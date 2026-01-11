import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, M4Result } from '../services/analysisAPI';
import './ModuleResultsPage.css';

export const M4ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<M4Result | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const loadResult = async () => {
      try {
        setLoading(true);
        const data = await analysisAPI.getModuleResult<M4Result>(projectId, 'M4');
        
        if (!data.context_id || !data.execution_id) {
          throw new Error('Invalid context: Missing context_id or execution_id');
        }
        
        setResult(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load M4 results');
      } finally {
        setLoading(false);
      }
    };

    loadResult();
  }, [projectId]);

  if (loading) {
    return (
      <div className="module-results-page">
        <div className="loading-spinner">Loading M4 Results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-results-page">
        <div className="error-message">
          <h3>❌ Error Loading M4 Results</h3>
          <p>{error}</p>
          <button onClick={() => navigate(`/projects/${projectId}`)}>
            ← Back to Project
          </button>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="module-results-page">
        <div className="no-data">No M4 results available</div>
      </div>
    );
  }

  return (
    <div className="module-results-page">
      {/* Context Metadata */}
      <div className="context-metadata">
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="label">Context ID:</span>
            <code>{result.context_id}</code>
          </div>
          <div className="metadata-item">
            <span className="label">Execution ID:</span>
            <code>{result.execution_id}</code>
          </div>
          <div className="metadata-item">
            <span className="label">Computed At:</span>
            <span>{new Date(result.computed_at).toLocaleString('ko-KR')}</span>
          </div>
          <div className="metadata-item">
            <span className="label">Input Hash:</span>
            <code className="hash">{result.inputs_hash?.substring(0, 16)}...</code>
          </div>
        </div>
      </div>

      {/* M4 Header */}
      <div className="module-header">
        <h1>M4: Building Scale Analysis</h1>
        <p className="subtitle">건축 규모 및 용량 산정 결과</p>
      </div>

      {/* Legal Capacity */}
      <section className="result-section">
        <h2>📏 Legal Capacity (법정 용량)</h2>
        <div className="capacity-grid">
          <div className="capacity-card">
            <div className="capacity-label">Total Units</div>
            <div className="capacity-value">
              {result.result.legal_capacity?.total_units || 0} 세대
            </div>
          </div>
          <div className="capacity-card">
            <div className="capacity-label">Total GFA</div>
            <div className="capacity-value">
              {result.result.legal_capacity?.total_gfa_sqm?.toLocaleString() || 0} m²
            </div>
          </div>
          <div className="capacity-card">
            <div className="capacity-label">Applied FAR</div>
            <div className="capacity-value">
              {result.result.legal_capacity?.applied_far || 0}%
            </div>
          </div>
        </div>
        {result.result.legal_capacity?.calculation_rationale && (
          <div className="rationale-box">
            <strong>Calculation Rationale:</strong>
            <p>{result.result.legal_capacity.calculation_rationale}</p>
          </div>
        )}
      </section>

      {/* Incentive Capacity */}
      {result.result.incentive_capacity && (
        <section className="result-section">
          <h2>🎁 Incentive Capacity (인센티브 용량)</h2>
          <div className="capacity-grid">
            <div className="capacity-card incentive">
              <div className="capacity-label">Total Units</div>
              <div className="capacity-value">
                {result.result.incentive_capacity.total_units || 0} 세대
              </div>
              <div className="capacity-diff">
                +{(result.result.incentive_capacity.total_units || 0) - 
                  (result.result.legal_capacity?.total_units || 0)} units
              </div>
            </div>
            <div className="capacity-card incentive">
              <div className="capacity-label">Total GFA</div>
              <div className="capacity-value">
                {result.result.incentive_capacity.total_gfa_sqm?.toLocaleString() || 0} m²
              </div>
            </div>
            <div className="capacity-card incentive">
              <div className="capacity-label">Applied FAR</div>
              <div className="capacity-value">
                {result.result.incentive_capacity.applied_far || 0}%
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Parking Solutions */}
      {result.result.parking_solutions && (
        <section className="result-section">
          <h2>🚗 Parking Solutions</h2>
          
          {result.result.parking_solutions.alternative_A && (
            <div className="parking-alternative">
              <h3>Alternative A (법정 기준)</h3>
              <div className="parking-metrics">
                <div className="metric-item">
                  <span className="label">Total Parking Spaces:</span>
                  <span className="value">
                    {result.result.parking_solutions.alternative_A.total_parking_spaces} 대
                  </span>
                </div>
                <div className="metric-item">
                  <span className="label">Parking Ratio:</span>
                  <span className="value">
                    {result.result.parking_solutions.alternative_A.parking_ratio || 'N/A'}
                  </span>
                </div>
              </div>
              {result.result.parking_solutions.alternative_A.notes && (
                <p className="parking-notes">
                  {result.result.parking_solutions.alternative_A.notes}
                </p>
              )}
            </div>
          )}

          {result.result.parking_solutions.alternative_B && (
            <div className="parking-alternative">
              <h3>Alternative B (최적화)</h3>
              <div className="parking-metrics">
                <div className="metric-item">
                  <span className="label">Total Parking Spaces:</span>
                  <span className="value">
                    {result.result.parking_solutions.alternative_B.total_parking_spaces} 대
                  </span>
                </div>
                <div className="metric-item">
                  <span className="label">Parking Ratio:</span>
                  <span className="value">
                    {result.result.parking_solutions.alternative_B.parking_ratio || 'N/A'}
                  </span>
                </div>
              </div>
              {result.result.parking_solutions.alternative_B.notes && (
                <p className="parking-notes">
                  {result.result.parking_solutions.alternative_B.notes}
                </p>
              )}
            </div>
          )}
        </section>
      )}

      {/* Calculation Details */}
      {result.result.calculation_details && (
        <section className="result-section">
          <h2>🔍 Calculation Details</h2>
          <div className="details-box">
            <pre>{JSON.stringify(result.result.calculation_details, null, 2)}</pre>
          </div>
        </section>
      )}

      {/* Navigation */}
      <div className="navigation-buttons">
        <button 
          className="btn-secondary"
          onClick={() => navigate(`/projects/${projectId}/modules/m3/results`)}
        >
          ← M3 Results
        </button>
        <button 
          className="btn-primary"
          onClick={() => navigate(`/projects/${projectId}/modules/m5/results`)}
        >
          M5 Results →
        </button>
      </div>
    </div>
  );
};
