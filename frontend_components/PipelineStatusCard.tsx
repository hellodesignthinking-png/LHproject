/**
 * ZeroSite v40.4 - Pipeline Status Card Component
 * 
 * Purpose: Display v40.3 Pipeline Lock status in UI
 * Features:
 * - 5-stage pipeline visualization
 * - Real-time status updates
 * - Data consistency indicators
 * - Context protection status
 * 
 * @author ZeroSite AI Development Team
 * @date 2025-12-14
 */

import React, { useState, useEffect } from 'react';
import './PipelineStatusCard.css';

interface PipelineStage {
  id: string;
  name: string;
  nameEn: string;
  completed: boolean;
  status: string;
  requiredBy: string[];
}

interface PipelineStatus {
  context_id: string;
  version: string;
  overall_status: string;
  pipeline: {
    [key: string]: PipelineStage;
  };
  consistency: {
    status: string;
    checks: Array<{
      name: string;
      status: string;
      details: any;
    }>;
  };
  protection: {
    protected: boolean;
    lock_timestamp: string;
  };
}

interface PipelineStatusCardProps {
  contextId: string;
  autoRefresh?: boolean;
  refreshInterval?: number; // milliseconds
}

const PipelineStatusCard: React.FC<PipelineStatusCardProps> = ({
  contextId,
  autoRefresh = false,
  refreshInterval = 5000,
}) => {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPipelineStatus = async () => {
    try {
      const response = await fetch(
        `/api/v40.2/context/${contextId}/pipeline-status`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch pipeline status');
      }
      
      const data = await response.json();
      setStatus(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPipelineStatus();

    if (autoRefresh) {
      const interval = setInterval(fetchPipelineStatus, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [contextId, autoRefresh, refreshInterval]);

  if (loading) {
    return (
      <div className="pipeline-status-card loading">
        <div className="spinner"></div>
        <p>Loading pipeline status...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="pipeline-status-card error">
        <h3>❌ Error</h3>
        <p>{error}</p>
        <button onClick={fetchPipelineStatus}>Retry</button>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  const getStageIcon = (stage: PipelineStage) => {
    if (stage.completed) return '✅';
    if (stage.status.includes('Missing')) return '❌';
    return '⏳';
  };

  const getOverallStatusColor = (overallStatus: string) => {
    if (overallStatus.includes('Complete')) return 'success';
    if (overallStatus.includes('Progress')) return 'warning';
    return 'danger';
  };

  const stageNames: { [key: string]: string } = {
    '1_appraisal': '감정평가 (Appraisal)',
    '2_diagnosis': '토지진단 (Diagnosis)',
    '3_capacity': '규모검토 (Capacity)',
    '4_scenario': '시나리오 (Scenarios)',
    '5_lh_review': 'LH 심사예측 (AI Judge)',
  };

  return (
    <div className="pipeline-status-card">
      {/* Header */}
      <div className="card-header">
        <h2>🔄 Pipeline 상태</h2>
        <span className="version-badge">v{status.version}</span>
      </div>

      {/* Overall Status */}
      <div className={`overall-status ${getOverallStatusColor(status.overall_status)}`}>
        <strong>{status.overall_status}</strong>
      </div>

      {/* Pipeline Stages */}
      <div className="pipeline-stages">
        {Object.keys(status.pipeline)
          .sort()
          .map((stageKey) => {
            const stage = status.pipeline[stageKey];
            return (
              <div
                key={stageKey}
                className={`pipeline-stage ${stage.completed ? 'completed' : 'pending'}`}
              >
                <div className="stage-icon">{getStageIcon(stage)}</div>
                <div className="stage-info">
                  <div className="stage-name">{stageNames[stageKey]}</div>
                  <div className="stage-status">{stage.status}</div>
                </div>
              </div>
            );
          })}
      </div>

      {/* Data Consistency */}
      <div className="consistency-section">
        <h3>📊 데이터 일관성</h3>
        <div className={`consistency-status ${status.consistency.status.includes('CONSISTENT') ? 'pass' : 'fail'}`}>
          {status.consistency.status}
        </div>
        
        {status.consistency.checks && status.consistency.checks.length > 0 && (
          <div className="consistency-checks">
            {status.consistency.checks.map((check, index) => (
              <div key={index} className="check-item">
                <span className="check-status">{check.status}</span>
                <span className="check-name">{check.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Context Protection */}
      <div className="protection-section">
        <h3>🔒 Context 보호</h3>
        <div className="protection-info">
          <div className="protection-row">
            <span>보호 상태:</span>
            <strong className={status.protection.protected ? 'protected' : 'unprotected'}>
              {status.protection.protected ? '✅ Protected' : '❌ Unprotected'}
            </strong>
          </div>
          {status.protection.lock_timestamp && (
            <div className="protection-row">
              <span>잠금 시각:</span>
              <span className="timestamp">{status.protection.lock_timestamp}</span>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="card-footer">
        <button onClick={fetchPipelineStatus} className="refresh-button">
          🔄 새로고침
        </button>
        <span className="context-id">Context: {contextId.substring(0, 8)}...</span>
      </div>
    </div>
  );
};

export default PipelineStatusCard;
