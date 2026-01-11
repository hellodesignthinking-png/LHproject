import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI } from '../services/analysisAPI';
import './CreateProjectPage.css';

export const CreateProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    address: '',
    lot_number: '',
    area_sqm: '',
    zoning: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.address.trim()) {
      setError('Address is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Create project
      const project = await analysisAPI.createProject({
        address: formData.address,
        lot_number: formData.lot_number || undefined,
        metadata: {
          area_sqm: formData.area_sqm ? parseFloat(formData.area_sqm) : undefined,
          zoning: formData.zoning || undefined
        }
      });

      // Navigate to M1 verification page
      navigate(`/projects/${project.project_id}/modules/m1/verify`);
    } catch (err: any) {
      setError(err.message || 'Failed to create project');
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
          <h1>🏗️ Create New Project</h1>
          <p className="subtitle">
            Enter the property address to start a comprehensive land analysis
          </p>
        </div>

        <form onSubmit={handleSubmit} className="create-project-form">
          {/* Required: Address */}
          <div className="form-group">
            <label htmlFor="address" className="form-label required">
              Property Address <span className="required-mark">*</span>
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleInputChange}
              placeholder="e.g., 서울특별시 강남구 테헤란로 518"
              className="form-input"
              required
              disabled={loading}
            />
            <p className="form-hint">
              Full address including street name and number
            </p>
          </div>

          {/* Optional: Lot Number */}
          <div className="form-group">
            <label htmlFor="lot_number" className="form-label">
              Lot Number / 지번 (Optional)
            </label>
            <input
              type="text"
              id="lot_number"
              name="lot_number"
              value={formData.lot_number}
              onChange={handleInputChange}
              placeholder="e.g., 대치동 157-29"
              className="form-input"
              disabled={loading}
            />
            <p className="form-hint">
              Traditional Korean lot number system
            </p>
          </div>

          {/* Optional: Area */}
          <div className="form-group">
            <label htmlFor="area_sqm" className="form-label">
              Land Area (m²) (Optional)
            </label>
            <input
              type="number"
              id="area_sqm"
              name="area_sqm"
              value={formData.area_sqm}
              onChange={handleInputChange}
              placeholder="e.g., 500"
              className="form-input"
              step="0.01"
              min="0"
              disabled={loading}
            />
            <p className="form-hint">
              If known, provide the land area in square meters
            </p>
          </div>

          {/* Optional: Zoning */}
          <div className="form-group">
            <label htmlFor="zoning" className="form-label">
              Zoning / 용도지역 (Optional)
            </label>
            <input
              type="text"
              id="zoning"
              name="zoning"
              value={formData.zoning}
              onChange={handleInputChange}
              placeholder="e.g., 제2종일반주거지역"
              className="form-input"
              disabled={loading}
            />
            <p className="form-hint">
              Land use zoning classification
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
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading || !formData.address.trim()}
            >
              {loading ? 'Creating...' : 'Create Project & Start Analysis'}
            </button>
          </div>
        </form>

        {/* Info Box */}
        <div className="info-box">
          <h3>📌 What happens next?</h3>
          <ol>
            <li>
              <strong>M1 Data Collection:</strong> System will automatically collect 
              land data from government APIs
            </li>
            <li>
              <strong>Human Verification:</strong> You'll review and verify all 
              collected data before proceeding
            </li>
            <li>
              <strong>M2-M6 Analysis:</strong> Once verified, the system will execute 
              valuation, type selection, capacity, feasibility, and LH review
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
};
