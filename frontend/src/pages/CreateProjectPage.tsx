import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI } from '../services/analysisAPI';
import './CreateProjectPage.css';

export const CreateProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    project_name: '',
    address: '',
    reference_info: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.project_name.trim()) {
      setError('프로젝트 이름을 입력해주세요');
      return;
    }

    if (!formData.address.trim()) {
      setError('주소를 입력해주세요');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Create project with correct API format
      const response = await analysisAPI.createProject({
        project_name: formData.project_name.trim(),
        address: formData.address.trim(),
        reference_info: formData.reference_info.trim() || undefined
      });

      // Navigate to project dashboard
      navigate(`/projects/${response.project_id}`);
    } catch (err: any) {
      setError(err.message || '프로젝트 생성에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/projects');
  };

  return (
    <div className="create-project-page">
      <div className="create-project-container">
        <div className="page-header">
          <h1>🏗️ 새 프로젝트 생성</h1>
          <p className="subtitle">
            토지 주소를 입력하여 종합 분석을 시작하세요
          </p>
        </div>

        <form onSubmit={handleSubmit} className="create-project-form">
          {/* Required: Project Name */}
          <div className="form-group">
            <label htmlFor="project_name" className="form-label required">
              프로젝트 이름 <span className="required-mark">*</span>
            </label>
            <input
              type="text"
              id="project_name"
              name="project_name"
              value={formData.project_name}
              onChange={handleInputChange}
              placeholder="예: 강남 대치동 토지 분석"
              className="form-input"
              required
              disabled={loading}
              autoFocus
            />
            <p className="form-hint">
              프로젝트를 식별할 수 있는 이름을 입력하세요
            </p>
          </div>

          {/* Required: Address */}
          <div className="form-group">
            <label htmlFor="address" className="form-label required">
              토지 주소 <span className="required-mark">*</span>
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              placeholder="예: 서울특별시 강남구 테헤란로 518"
              className="form-input"
              required
              disabled={loading}
            />
            <p className="form-hint">
              도로명 주소 또는 지번 주소를 입력하세요
            </p>
          </div>

          {/* Optional: Reference Info */}
          <div className="form-group">
            <label htmlFor="reference_info" className="form-label">
              참고 정보 (선택사항)
            </label>
            <textarea
              id="reference_info"
              name="reference_info"
              value={formData.reference_info}
              onChange={handleInputChange}
              placeholder="예: 매매가 50억, 면적 500㎡, 현재 용도 등"
              className="form-input form-textarea"
              rows={3}
              disabled={loading}
            />
            <p className="form-hint">
              토지 관련 추가 정보나 메모 (선택사항)
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-alert">
              <span className="error-icon">⚠️</span>
              <span className="error-text">{error}</span>
            </div>
          )}

          {/* Form Actions */}
          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={handleCancel}
              disabled={loading}
            >
              취소
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !formData.project_name.trim() || !formData.address.trim()}
            >
              {loading ? '생성 중...' : '프로젝트 생성 및 분석 시작'}
            </button>
          </div>
        </form>

        {/* Info Box */}
        <div className="info-box">
          <h3>📌 다음 단계 안내</h3>
          <ol>
            <li>
              <strong>M1 데이터 수집:</strong> 시스템이 자동으로 정부 API에서 
              토지 데이터를 수집합니다
            </li>
            <li>
              <strong>인간 검증 (필수):</strong> 수집된 모든 데이터를 확인하고 
              승인해야 다음 단계로 진행됩니다
            </li>
            <li>
              <strong>M2-M6 자동 분석:</strong> 검증 후 시스템이 자동으로 
              토지가치, 주택유형, 건축규모, 재무분석, LH판정을 수행합니다
            </li>
          </ol>
        </div>

        {/* Phase 2 Declaration */}
        <div className="phase-declaration">
          <p className="declaration-text">
            ⚡ <strong>Phase 2 원칙:</strong> 모든 분석은 M1 검증 이후에만 실행됩니다
          </p>
          <p className="declaration-subtext">
            ZeroSite는 데이터 우선(DATA-FIRST) · 인간 검증(HUMAN-VERIFIED) · 
            컨텍스트 기반(CONTEXT-AWARE) 시스템입니다
          </p>
        </div>
      </div>
    </div>
  );
};
