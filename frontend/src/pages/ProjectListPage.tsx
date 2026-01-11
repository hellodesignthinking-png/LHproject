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
      setError(err.message || 'Failed to load projects');
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
    
    if (!confirm('Are you sure you want to delete this project?')) {
      return;
    }

    try {
      await analysisAPI.deleteProject(projectId);
      await loadProjects(); // Reload list
    } catch (err: any) {
      alert(`Failed to delete project: ${err.message}`);
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
        <div className="loading-spinner">Loading projects...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="project-list-page">
        <div className="error-message">
          <h3>❌ Error Loading Projects</h3>
          <p>{error}</p>
          <button onClick={loadProjects}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="project-list-page">
      <div className="page-header">
        <h1>📂 My Projects</h1>
        <button className="btn-create" onClick={handleCreateProject}>
          + New Project
        </button>
      </div>

      {projects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h2>No Projects Yet</h2>
          <p>Create your first project to start land analysis</p>
          <button className="btn-primary" onClick={handleCreateProject}>
            Create First Project
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
                <h3 className="project-name">{project.name || 'Unnamed Project'}</h3>
                <button 
                  className="btn-delete"
                  onClick={(e) => handleDeleteProject(project.project_id, e)}
                  title="Delete project"
                >
                  🗑️
                </button>
              </div>

              <div className="project-address">
                📍 {project.address || 'Address not specified'}
              </div>

              <div className="project-meta">
                <div className="meta-item">
                  <span className="label">Created:</span>
                  <span className="value">
                    {new Date(project.created_at).toLocaleDateString('ko-KR')}
                  </span>
                </div>
                <div className="meta-item">
                  <span className="label">Updated:</span>
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
                  <span className="label">Context:</span>
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
