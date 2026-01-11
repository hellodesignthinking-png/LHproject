/**
 * Module Status Bar Component
 * ============================
 * 
 * Shows real-time status of all 6 modules (M1-M6)
 * Fixed at top of all analysis pages
 * 
 * Status Icons:
 * ✅ VERIFIED (green) - Completed & user verified
 * 🔄 IN_PROGRESS (blue) - Currently executing
 * ⏸️ LOCKED (gray) - Cannot execute (prerequisite not met)
 * ❌ ERROR (red) - Execution failed
 * ⚠️ PENDING (yellow) - Awaiting verification
 * 🚫 INVALID (orange) - Context changed, re-execute required
 */

import React from 'react';
import { ModuleInfo } from '../services/analysisAPI';
import './ModuleStatusBar.css';

interface ModuleStatusBarProps {
  m1: ModuleInfo;
  m2: ModuleInfo;
  m3: ModuleInfo;
  m4: ModuleInfo;
  m5: ModuleInfo;
  m6: ModuleInfo;
  projectId: string;
  onModuleClick: (moduleName: string) => void;
}

interface ModuleDisplay {
  name: string;
  label: string;
  icon: string;
  color: string;
  clickable: boolean;
  tooltip: string;
}

export const ModuleStatusBar: React.FC<ModuleStatusBarProps> = ({
  m1, m2, m3, m4, m5, m6, projectId, onModuleClick
}) => {
  
  const getModuleDisplay = (module: ModuleInfo): ModuleDisplay => {
    const { status, verification_status } = module;
    
    // VERIFIED (green) - User approved
    if (verification_status === 'approved') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '✅',
        color: 'verified',
        clickable: true,
        tooltip: 'Verified - Click to view results'
      };
    }
    
    // IN_PROGRESS (blue)
    if (status === 'in_progress') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '🔄',
        color: 'in-progress',
        clickable: false,
        tooltip: 'Executing...'
      };
    }
    
    // COMPLETED but pending verification (yellow)
    if (status === 'completed' && verification_status === 'pending') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '⚠️',
        color: 'pending',
        clickable: true,
        tooltip: 'Awaiting verification - Click to verify'
      };
    }
    
    // COMPLETED (no verification needed for M2-M6)
    if (status === 'completed') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '✅',
        color: 'completed',
        clickable: true,
        tooltip: 'Completed - Click to view results'
      };
    }
    
    // INVALID (orange) - Context changed
    if (status === 'invalid') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '🚫',
        color: 'invalid',
        clickable: false,
        tooltip: 'INVALID - Data changed, re-execute required'
      };
    }
    
    // ERROR (red)
    if (status === 'error') {
      return {
        name: module.module_name,
        label: module.module_name,
        icon: '❌',
        color: 'error',
        clickable: true,
        tooltip: `Error: ${module.error_message || 'Unknown error'}`
      };
    }
    
    // NOT_STARTED / LOCKED (gray)
    return {
      name: module.module_name,
      label: module.module_name,
      icon: '⏸️',
      color: 'locked',
      clickable: false,
      tooltip: 'Locked - Complete previous module first'
    };
  };

  const modules = [
    getModuleDisplay(m1),
    getModuleDisplay(m2),
    getModuleDisplay(m3),
    getModuleDisplay(m4),
    getModuleDisplay(m5),
    getModuleDisplay(m6),
  ];

  const handleModuleClick = (module: ModuleDisplay) => {
    if (module.clickable) {
      onModuleClick(module.name);
    }
  };

  return (
    <div className="module-status-bar">
      <div className="status-bar-container">
        {modules.map((module) => (
          <div
            key={module.name}
            className={`
              module-badge 
              module-${module.color}
              ${module.clickable ? 'clickable' : 'disabled'}
            `}
            onClick={() => handleModuleClick(module)}
            title={module.tooltip}
          >
            <span className="module-icon">{module.icon}</span>
            <span className="module-label">{module.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ============================================================================
// Legend Component (Optional)
// ============================================================================

export const ModuleStatusLegend: React.FC = () => {
  return (
    <div className="status-legend">
      <div className="legend-title">Status Icons:</div>
      <div className="legend-items">
        <div className="legend-item">
          <span className="legend-icon">✅</span>
          <span className="legend-text">Verified/Completed</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">🔄</span>
          <span className="legend-text">In Progress</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">⏸️</span>
          <span className="legend-text">Locked</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">⚠️</span>
          <span className="legend-text">Awaiting Verification</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">🚫</span>
          <span className="legend-text">Invalid</span>
        </div>
        <div className="legend-item">
          <span className="legend-icon">❌</span>
          <span className="legend-text">Error</span>
        </div>
      </div>
    </div>
  );
};
