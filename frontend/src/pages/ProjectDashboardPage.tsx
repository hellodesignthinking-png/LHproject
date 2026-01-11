import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, AnalysisStatus } from '../services/analysisAPI';
import { ModuleStatusBar } from '../components/ModuleStatusBar';
import './ProjectDashboardPage.css';

export const ProjectDashboardPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<AnalysisStatus | null>(null);
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
        if (data.m1_status.status === 'not_started' || 
            data.m1_status.status === 'in_progress') {
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

    const moduleKey = `${module.toLowerCase()}_status` as keyof AnalysisStatus;
    const moduleInfo = status[moduleKey] as any;
    const moduleStatus = moduleInfo?.status || 'not_started';
    
    if (module === 'M1') {
      navigate(`/projects/${projectId}/modules/m1/verify`);
    } else if (moduleStatus === 'verified' || moduleStatus === 'completed') {
      navigate(`/projects/${projectId}/modules/${module.toLowerCase()}/results`);
    } else if (moduleStatus === 'not_started') {
      alert(`이전 모듈을 먼저 완료해주세요`);
    } else if (moduleStatus === 'invalid') {
      alert(`${module} 결과가 유효하지 않습니다. 다시 실행해주세요.`);
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
      <ModuleStatusBar 
        m1={status.m1_status}
        m2={status.m2_status}
        m3={status.m3_status}
        m4={status.m4_status}
        m5={status.m5_status}
        m6={status.m6_status}
        projectId={projectId!}
        onModuleClick={handleNavigateToModule}
      />

      {/* Project Header */}
      <div className="project-header">
        <button 
          className="back-button"
          onClick={() => navigate('/projects')}
        >
          ← All Projects
        </button>
        <h1>📂 {status.project_name || '프로젝트 대시보드'}</h1>
        <p className="project-address">📍 {status.address || '주소 미지정'}</p>
      </div>

      {/* Context Metadata */}
      {status.current_context_id && (
        <div className="context-info">
          <h3>🔍 Context Information</h3>
          <div className="context-grid">
            <div className="context-item">
              <span className="label">Project ID:</span>
              <code>{projectId}</code>
            </div>
            <div className="context-item">
              <span className="label">Context ID:</span>
              <code>{status.current_context_id.substring(0, 16)}...</code>
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
      {status.m1_status.status !== 'verified' && status.m1_status.status !== 'completed' && (
        <div className="verification-required-banner">
          <div className="banner-icon">🔒</div>
          <div className="banner-content">
            <h3>M1 인간 검증 필요</h3>
            <p>
              M1 토지 데이터가 수집되었지만 계속 진행하려면 인간 검증이 필요합니다.
              데이터를 검토하고 승인해주세요.
            </p>
            <button 
              className="btn-verify"
              onClick={() => navigate(`/projects/${projectId}/modules/m1/verify`)}
            >
              🔍 M1 데이터 검토 및 검증
            </button>
          </div>
        </div>
      )}

      {/* Module Progress */}
      <div className="module-progress">
        <h3>📊 분석 진행 상황</h3>
        <div className="progress-cards">
          {['M1', 'M2', 'M3', 'M4', 'M5', 'M6'].map((module) => {
            const moduleKey = `${module.toLowerCase()}_status` as keyof AnalysisStatus;
            const moduleInfo = status[moduleKey] as any;
            const moduleStatus = moduleInfo?.status || 'not_started';
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
                {moduleStatus === 'verified' || moduleStatus === 'completed' ? (
                  <button className="btn-view">결과 보기 →</button>
                ) : moduleStatus === 'not_started' && module === 'M1' ? (
                  <button className="btn-verify">지금 검증 →</button>
                ) : null}
              </div>
            );
          })}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>⚡ 빠른 작업</h3>
        <div className="action-buttons">
          <button 
            className="action-btn"
            onClick={() => navigate(`/projects/${projectId}/modules/m1/verify`)}
          >
            🔍 M1 데이터 검토
          </button>
          {status.m6_status.status === 'completed' && (
            <button 
              className="action-btn"
              onClick={() => navigate(`/projects/${projectId}/report`)}
            >
              📄 최종 보고서 생성
            </button>
          )}
          <button 
            className="action-btn secondary"
            onClick={() => {
              if (confirm('정말로 이 프로젝트를 삭제하시겠습니까?')) {
                analysisAPI.deleteProject(projectId!).then(() => {
                  navigate('/projects');
                });
              }
            }}
          >
            🗑️ 프로젝트 삭제
          </button>
        </div>
      </div>
    </div>
  );
};

// Helper functions
function getStatusClass(status: string): string {
  switch (status) {
    case 'verified':
    case 'completed': return 'status-completed';
    case 'in_progress': return 'status-in-progress';
    case 'not_started': return 'status-pending';
    case 'invalid': return 'status-invalid';
    case 'error': return 'status-failed';
    default: return 'status-locked';
  }
}

function getStatusIcon(status: string): string {
  switch (status) {
    case 'verified':
    case 'completed': return '✅';
    case 'in_progress': return '🔄';
    case 'not_started': return '⏸️';
    case 'invalid': return '⚠️';
    case 'error': return '❌';
    default: return '🔒';
  }
}

function getModuleName(module: string): string {
  const names: Record<string, string> = {
    M1: '토지 정보',
    M2: '토지 가치',
    M3: '주택 유형',
    M4: '건축 규모',
    M5: '타당성 분석',
    M6: 'LH 판정'
  };
  return names[module] || module;
}

function formatStatus(status: string): string {
  const formatted: Record<string, string> = {
    verified: '검증됨 ✓',
    completed: '완료됨 ✓',
    in_progress: '진행 중...',
    not_started: '시작 안 됨',
    invalid: '유효하지 않음 - 재실행 필요',
    error: '실패',
    locked: '잠김'
  };
  return formatted[status] || status;
}
