import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI, ProjectListItem } from '../services/analysisAPI';
import './ProjectListPage.css';

export const ProjectListPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await analysisAPI.listProjects();
      setProjects(data);
    } catch (err: any) {
      setError(err.message || '프로젝트 목록을 불러올 수 없습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = () => {
    navigate('/projects/create');
  };

  const handleProjectClick = (projectId: string) => {
    navigate(`/projects/${projectId}`);
  };

  const handleDeleteProject = async (projectId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!confirm('정말로 이 프로젝트를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await analysisAPI.deleteProject(projectId);
      await loadProjects(); // Reload list
    } catch (err: any) {
      alert(`프로젝트 삭제 실패: ${err.message}`);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'VERIFIED': return 'status-verified';
      case 'COMPLETED': return 'status-completed';
      case 'IN_PROGRESS': return 'status-in-progress';
      case 'PENDING': return 'status-pending';
      case 'FAILED': return 'status-failed';
      case 'INVALID': return 'status-invalid';
      default: return 'status-unknown';
    }
  };

  if (loading) {
    return (
      <div className="project-list-page">
        <div className="loading-spinner">프로젝트 목록을 불러오는 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="project-list-page">
        <div className="error-message">
          <h3>❌ 프로젝트 로딩 오류</h3>
          <p>{error}</p>
          <button onClick={loadProjects}>다시 시도</button>
        </div>
      </div>
    );
  }

  return (
    <div className="project-list-page">
      <div className="page-header">
        <h1>📂 내 프로젝트</h1>
        <button className="btn-create" onClick={handleCreateProject}>
          + 새 프로젝트
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h2>아직 프로젝트가 없습니다</h2>
          <p>첫 번째 프로젝트를 생성하여 토지 분석을 시작하세요</p>
          <button className="btn-primary" onClick={handleCreateProject}>
            첫 프로젝트 생성하기
          </button>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div 
              key={project.project_id}
              className="project-card"
              onClick={() => handleProjectClick(project.project_id)}
            >
              <div className="project-card-header">
                <h3 className="project-name">{project.name || '이름 없는 프로젝트'}</h3>
                <button 
                  className="btn-delete"
                  onClick={(e) => handleDeleteProject(project.project_id, e)}
                  title="Delete project"
                >
                  🗑️
                </button>
              </div>

              <div className="project-address">
                📍 {project.address || '주소 미지정'}
              </div>

              <div className="project-meta">
                <div className="meta-item">
                  <span className="label">생성일:</span>
                  <span className="value">
                    {new Date(project.created_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
                <div className="meta-item">
                  <span className="label">수정일:</span>
                  <span className="value">
                    {new Date(project.updated_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
              </div>

              <div className="module-status-summary">
                {['M1', 'M2', 'M3', 'M4', 'M5', 'M6'].map((module) => {
                  const status = project.module_statuses?.[module] || 'PENDING';
                  return (
                    <div 
                      key={module}
                      className={`module-badge ${getStatusBadgeClass(status)}`}
                      title={`${module}: ${status}`}
                    >
                      {module}
                    </div>
                  );
                })}
              </div>

              {project.context_id && (
                <div className="project-context">
                  <span className="label">컨텍스트:</span>
                  <code className="context-id">{project.context_id.substring(0, 8)}...</code>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
