/**
 * ZeroSite Analysis API Service
 * ===============================
 * 
 * Context-Aware API Client
 * - Every result is tied to a specific context_id
 * - No caching of results across contexts
 * - Every request fetches fresh data from backend
 * 
 * CRITICAL: Results are NOT saved state - they are COMPUTED FACTS
 * from a specific context at a specific time.
 */

import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '../config';

// ============================================================================
// Type Definitions
// ============================================================================

export interface AnalysisStatus {
  project_id: string;
  project_name: string;
  address: string;
  parcel_id: string | null;
  current_context_id: string;
  context_created_at: string;
  context_version: string;
  
  m1_status: ModuleInfo;
  m2_status: ModuleInfo;
  m3_status: ModuleInfo;
  m4_status: ModuleInfo;
  m5_status: ModuleInfo;
  m6_status: ModuleInfo;
  
  created_at: string;
  updated_at: string;
  last_activity: string;
  
  is_locked: boolean;
  locked_at: string | null;
  locked_by: string | null;
}

export interface ModuleInfo {
  module_name: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'verified' | 'error' | 'invalid';
  verification_status: 'pending' | 'approved' | 'rejected' | null;
  executed_at: string | null;
  verified_at: string | null;
  verified_by: string | null;
  error_message: string | null;
  context_id: string | null;
  result_summary: any | null;
}

export interface ModuleResult<T = any> {
  success: boolean;
  project_id: string;
  context_id: string;
  execution_id: string | null;
  module: string;
  computed_at: string;
  inputs_hash: string | null;
  result: T;
  status: string;
  verification_status: string | null;
  executed_at: string | null;
  can_execute: boolean;
  execution_blocked_reason: string | null;
}

export interface CreateProjectRequest {
  project_name: string;
  address: string;
  reference_info?: string;
}

export interface CreateProjectResponse {
  success: boolean;
  project_id: string;
  message: string;
  next_action: string;
}

export interface ProjectListItem {
  project_id: string;
  name: string;
  address: string;
  progress: number;
  next_action: string;
  last_activity: string;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
  context_id?: string;
  module_statuses?: {
    [key: string]: string;
  };
}

export interface VerifyModuleRequest {
  approved: boolean;
  comments?: string;
  verified_by?: string;
}

export interface VerifyModuleResponse {
  success: boolean;
  message: string;
  next_action: string | null;
  can_proceed: boolean;
}

// ============================================================================
// API Service Class
// ============================================================================

class AnalysisAPIService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Create new analysis project
   */
  async createProject(request: CreateProjectRequest): Promise<CreateProjectResponse> {
    const response = await fetch(`${this.baseUrl}/analysis/projects/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create project');
    }

    return response.json();
  }

  /**
   * Get complete analysis status for a project
   * 
   * CRITICAL: This returns the CURRENT context_id
   * All module results must match this context_id
   */
  async getProjectStatus(projectId: string): Promise<AnalysisStatus> {
    const response = await fetch(
      `${this.baseUrl}/analysis/projects/${projectId}/status`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get project status');
    }

    return response.json();
  }

  /**
   * Get module result (Context-Scoped)
   * 
   * CRITICAL: 
   * - Always fetches fresh from backend
   * - Never returns cached results
   * - Validates context_id matches current context
   */
  async getModuleResult<T = any>(
    projectId: string,
    moduleName: string,
    expectedContextId?: string
  ): Promise<ModuleResult<T>> {
    const response = await fetch(
      `${this.baseUrl}/analysis/projects/${projectId}/modules/${moduleName}/result`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to get ${moduleName} result`);
    }

    const rawResult: any = await response.json();
    
    // Handle both old format (result) and new format (result_data)
    const result: ModuleResult<T> = {
      ...rawResult,
      result: rawResult.result || rawResult.result_data,
    };

    // Validate context if provided
    if (expectedContextId && result.context_id !== expectedContextId) {
      throw new Error(
        `Context mismatch: Expected ${expectedContextId}, got ${result.context_id}. ` +
        `Results may be INVALID. Please refresh.`
      );
    }

    return result;
  }

  /**
   * Verify module results (🔒 CRITICAL GATE)
   * 
   * This is the human verification checkpoint.
   * Without this, downstream modules cannot execute.
   */
  async verifyModule(
    projectId: string,
    moduleName: string,
    request: VerifyModuleRequest
  ): Promise<VerifyModuleResponse> {
    const response = await fetch(
      `${this.baseUrl}/analysis/projects/${projectId}/modules/${moduleName}/verify`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to verify ${moduleName}`);
    }

    return response.json();
  }

  /**
   * Execute module analysis (⚡ EXECUTION TRIGGER)
   * 
   * CRITICAL: This is the execution trigger that actually runs M2-M6
   * Call this after M1 verification is approved to start the pipeline
   */
  async executeModule(
    projectId: string,
    moduleName: string
  ): Promise<{ success: boolean; message: string; execution_id?: string }> {
    const response = await fetch(
      `${this.baseUrl}/analysis/projects/${projectId}/modules/${moduleName}/execute`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to execute ${moduleName}`);
    }

    return response.json();
  }

  /**
   * Execute M1 → M6 full pipeline
   * 
   * This is a convenience method that triggers all modules in sequence
   * Use after M1 verification is approved
   */
  async executeFullPipeline(projectId: string): Promise<{
    success: boolean;
    executed_modules: string[];
    message: string;
  }> {
    const executedModules: string[] = [];
    
    // Execute M2-M6 in sequence
    const modules = ['M2', 'M3', 'M4', 'M5', 'M6'];
    
    for (const module of modules) {
      try {
        await this.executeModule(projectId, module);
        executedModules.push(module);
      } catch (error) {
        console.error(`Failed to execute ${module}:`, error);
        // Continue to next module even if one fails
      }
    }
    
    return {
      success: executedModules.length > 0,
      executed_modules: executedModules,
      message: `Executed ${executedModules.length}/${modules.length} modules`
    };
  }

  /**
   * List all projects
   */
  async listProjects(limit: number = 50, offset: number = 0) {
    const response = await fetch(
      `${this.baseUrl}/analysis/projects?limit=${limit}&offset=${offset}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to list projects');
    }

    const data = await response.json();
    return data.projects || [];
  }

  /**
   * Delete project
   */
  async deleteProject(projectId: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/analysis/projects/${projectId}`,
      {
        method: 'DELETE',
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete project');
    }
  }
  /**
   * Collect POI (Point of Interest) data using Kakao Map API
   * 
   * @param address - Address to collect POI data for
   * @returns POI data including subway, bus, schools, and commercial facilities
   */
  async collectPOI(address: string): Promise<{
    success: boolean;
    message: string;
    data?: {
      subway_stations: any[];
      bus_stops: any[];
      poi_schools: any[];
      poi_commercial: any[];
    };
  }> {
    const response = await fetch(
      `${this.baseUrl}/m1/collect-poi`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ address })
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to collect POI data');
    }

    return response.json();
  }
}

// ============================================================================
// Singleton Export
// ============================================================================

export const analysisAPI = new AnalysisAPIService();

// ============================================================================
// React Hook for Status Polling
// ============================================================================

/**
 * Custom hook to poll project status
 * 
 * Returns latest status and automatically refreshes every 5 seconds
 */
export function useProjectStatus(projectId: string | null, interval: number = 5000) {
  const [status, setStatus] = React.useState<AnalysisStatus | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!projectId) {
      setLoading(false);
      return;
    }

    let mounted = true;

    const fetchStatus = async () => {
      try {
        const data = await analysisAPI.getProjectStatus(projectId);
        if (mounted) {
          setStatus(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Unknown error');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    // Initial fetch
    fetchStatus();

    // Set up polling
    const intervalId = setInterval(fetchStatus, interval);

    return () => {
      mounted = false;
      clearInterval(intervalId);
    };
  }, [projectId, interval]);

  return { status, loading, error };
}

// Default export for easier imports
export default analysisAPI;
