import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, ProjectStatus } from '../services/analysisAPI';
import { ModuleStatusBar } from '../components/ModuleStatusBar';
import './ProjectDashboardPage.css';

export const ProjectDashboardPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<ProjectStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const loadStatus = async () => {
      try {
        setLoading(true);
        const data = await analysisAPI.getProjectStatus(projectId);
        setStatus(data);

        // Auto-navigate to M1 verification if not yet verified
        if (data.module_statuses.M1 === 'PENDING' || 
            data.module_statuses.M1 === 'IN_PROGRESS') {
          navigate(`/projects/${projectId}/modules/m1/verify`, { replace: true });
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load project status');
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
    
    // Poll status every 5 seconds
    const interval = setInterval(loadStatus, 5000);
    return () => clearInterval(interval);
  }, [projectId, navigate]);

  const handleNavigateToModule = (module: string) => {
    if (!projectId || !status) return;

    const moduleStatus = status.module_statuses[module];
    
    if (module === 'M1') {
      if (moduleStatus === 'VERIFIED' || moduleStatus === 'COMPLETED') {
        navigate(`/projects/${projectId}/modules/m1/verify`);
      } else {
        navigate(`/projects/${projectId}/modules/m1/verify`);
      }
    } else if (moduleStatus === 'VERIFIED' || moduleStatus === 'COMPLETED') {
      navigate(`/projects/${projectId}/modules/${module.toLowerCase()}/results`);
    } else if (moduleStatus === 'LOCKED') {
      alert(`Please complete previous modules before accessing ${module}`);
    } else if (moduleStatus === 'INVALID') {
      alert(`${module} results are invalid. Please re-execute the module.`);
    }
  };

  if (loading) {
    return (
      <div className="project-dashboard-page">
        <div className="loading-spinner">Loading project...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="project-dashboard-page">
        <div className="error-message">
          <h3>❌ Error Loading Project</h3>
          <p>{error}</p>
          <button onClick={() => navigate('/projects')}>
            ← Back to Projects
          </button>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="project-dashboard-page">
        <div className="no-data">No project data available</div>
      </div>
    );
  }

  return (
    <div className="project-dashboard-page">
      {/* Module Status Bar */}
      <ModuleStatusBar projectId={projectId!} />

      {/* Project Header */}
      <div className="project-header">
        <button 
          className="back-button"
          onClick={() => navigate('/projects')}
        >
          ← All Projects
        </button>
        <h1>📂 {status.name || 'Project Dashboard'}</h1>
        <p className="project-address">📍 {status.address || 'Address not specified'}</p>
      </div>

      {/* Context Metadata */}
      {status.context_id && (
        <div className="context-info">
          <h3>🔍 Context Information</h3>
          <div className="context-grid">
            <div className="context-item">
              <span className="label">Project ID:</span>
              <code>{projectId}</code>
            </div>
            <div className="context-item">
              <span className="label">Context ID:</span>
              <code>{status.context_id.substring(0, 16)}...</code>
            </div>
            <div className="context-item">
              <span className="label">Created:</span>
              <span>{new Date(status.created_at).toLocaleString('ko-KR')}</span>
            </div>
            <div className="context-item">
              <span className="label">Last Updated:</span>
              <span>{new Date(status.updated_at).toLocaleString('ko-KR')}</span>
            </div>
          </div>
        </div>
      )}

      {/* M1 Verification Required Banner */}
      {status.module_statuses.M1 !== 'VERIFIED' && status.module_statuses.M1 !== 'COMPLETED' && (
        <div className="verification-required-banner">
          <div className="banner-icon">🔒</div>
          <div className="banner-content">
            <h3>M1 Human Verification Required</h3>
            <p>
              M1 land data has been collected but requires human verification before proceeding.
              Please review and approve the data to continue.
            </p>
            <button 
              className="btn-verify"
              onClick={() => navigate(`/projects/${projectId}/modules/m1/verify`)}
            >
              🔍 Review & Verify M1 Data
            </button>
          </div>
        </div>
      )}

      {/* Module Progress */}
      <div className="module-progress">
        <h3>📊 Analysis Progress</h3>
        <div className="progress-cards">
          {['M1', 'M2', 'M3', 'M4', 'M5', 'M6'].map((module) => {
            const moduleStatus = status.module_statuses[module];
            const statusClass = getStatusClass(moduleStatus);
            const statusIcon = getStatusIcon(moduleStatus);
            const moduleName = getModuleName(module);

            return (
              <div 
                key={module}
                className={`progress-card ${statusClass}`}
                onClick={() => handleNavigateToModule(module)}
              >
                <div className="card-header">
                  <span className="module-label">{module}</span>
                  <span className="status-icon">{statusIcon}</span>
                </div>
                <div className="card-title">{moduleName}</div>
                <div className="card-status">{formatStatus(moduleStatus)}</div>
                {moduleStatus === 'VERIFIED' || moduleStatus === 'COMPLETED' ? (
                  <button className="btn-view">View Results →</button>
                ) : moduleStatus === 'PENDING' && module === 'M1' ? (
                  <button className="btn-verify">Verify Now →</button>
                ) : null}
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>⚡ Quick Actions</h3>
        <div className="action-buttons">
          <button 
            className="action-btn"
            onClick={() => navigate(`/projects/${projectId}/modules/m1/verify`)}
            disabled={status.module_statuses.M1 !== 'PENDING' && 
                     status.module_statuses.M1 !== 'VERIFIED' &&
                     status.module_statuses.M1 !== 'COMPLETED'}
          >
            🔍 Review M1 Data
          </button>
          {status.module_statuses.M6 === 'COMPLETED' && (
            <button 
              className="action-btn"
              onClick={() => navigate(`/projects/${projectId}/report`)}
            >
              📄 Generate Final Report
            </button>
          )}
          <button 
            className="action-btn secondary"
            onClick={() => {
              if (confirm('Are you sure you want to delete this project?')) {
                analysisAPI.deleteProject(projectId!).then(() => {
                  navigate('/projects');
                });
              }
            }}
          >
            🗑️ Delete Project
          </button>
        </div>
      </div>
    </div>
  );
};

// Helper functions
function getStatusClass(status: string): string {
  switch (status) {
    case 'VERIFIED':
    case 'COMPLETED': return 'status-completed';
    case 'IN_PROGRESS': return 'status-in-progress';
    case 'PENDING': return 'status-pending';
    case 'INVALID': return 'status-invalid';
    case 'FAILED': return 'status-failed';
    default: return 'status-locked';
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'VERIFIED':
    case 'COMPLETED': return '✅';
    case 'IN_PROGRESS': return '🔄';
    case 'PENDING': return '⏸️';
    case 'INVALID': return '⚠️';
    case 'FAILED': return '❌';
    default: return '🔒';
  }
}

function getModuleName(module: string): string {
  const names: Record<string, string> = {
    M1: 'Land Information',
    M2: 'Land Valuation',
    M3: 'Housing Type',
    M4: 'Building Scale',
    M5: 'Feasibility Analysis',
    M6: 'LH Review'
  };
  return names[module] || module;
}

function formatStatus(status: string): string {
  const formatted: Record<string, string> = {
    VERIFIED: 'Verified ✓',
    COMPLETED: 'Completed ✓',
    IN_PROGRESS: 'In Progress...',
    PENDING: 'Pending',
    INVALID: 'Invalid - Re-run Required',
    FAILED: 'Failed',
    LOCKED: 'Locked'
  };
  return formatted[status] || status;
}
