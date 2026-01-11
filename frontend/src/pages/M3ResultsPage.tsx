import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, M3Result } from '../services/analysisAPI';
import './ModuleResultsPage.css';

export const M3ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<M3Result | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const loadResult = async () => {
      try {
        setLoading(true);
        const data = await analysisAPI.getModuleResult<M3Result>(projectId, 'M3');
        
        // Context validation
        if (!data.context_id || !data.execution_id) {
          throw new Error('Invalid context: Missing context_id or execution_id');
        }
        
        setResult(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load M3 results');
      } finally {
        setLoading(false);
      }
    };

    loadResult();
  }, [projectId]);

  if (loading) {
    return (
      <div className="module-results-page">
        <div className="loading-spinner">Loading M3 Results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-results-page">
        <div className="error-message">
          <h3>❌ Error Loading M3 Results</h3>
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
        <div className="no-data">No M3 results available</div>
      </div>
    );
  }

  return (
    <div className="module-results-page">
      {/* Context Metadata Header */}
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

      {/* M3 Header */}
      <div className="module-header">
        <h1>M3: Housing Type Decision</h1>
        <p className="subtitle">주거 공급 유형 결정 결과</p>
      </div>

      {/* Selected Housing Type */}
      <section className="result-section">
        <h2>✅ Selected Housing Type</h2>
        <div className="housing-type-card selected">
          <div className="type-name">
            {result.result.selected_type || 'Unknown'}
          </div>
          <div className="confidence-score">
            Confidence: {result.result.confidence || 0}%
          </div>
        </div>
      </section>

      {/* Decision Rationale */}
      <section className="result-section">
        <h2>📋 Decision Rationale</h2>
        <div className="rationale-box">
          <p className="rationale-text">
            {result.result.decision_rationale || 
             result.result.selection_reason || 
             'No rationale provided'}
          </p>
        </div>
        
        {result.result.selection_method && (
          <div className="method-info">
            <strong>Selection Method:</strong> {result.result.selection_method}
          </div>
        )}
      </section>

      {/* Strengths */}
      {result.result.strengths && result.result.strengths.length > 0 && (
        <section className="result-section">
          <h2>💪 Strengths</h2>
          <ul className="strength-list">
            {result.result.strengths.map((strength, idx) => (
              <li key={idx} className="strength-item">
                ✓ {strength}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Weaknesses */}
      {result.result.weaknesses && result.result.weaknesses.length > 0 && (
        <section className="result-section">
          <h2>⚠️ Weaknesses</h2>
          <ul className="weakness-list">
            {result.result.weaknesses.map((weakness, idx) => (
              <li key={idx} className="weakness-item">
                ⚠ {weakness}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Rejected Types */}
      {result.result.rejected_types && result.result.rejected_types.length > 0 && (
        <section className="result-section">
          <h2>❌ Rejected Types</h2>
          <div className="rejected-types">
            {result.result.rejected_types.map((rejected: any, idx: number) => (
              <div key={idx} className="rejected-type-card">
                <div className="rejected-type-name">{rejected.type}</div>
                <div className="rejection-reason">{rejected.reason}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Demand Prediction */}
      {result.result.demand_prediction && (
        <section className="result-section">
          <h2>📊 Demand Prediction</h2>
          <div className="demand-metrics">
            <div className="metric-card">
              <div className="metric-label">Demand Score</div>
              <div className="metric-value">
                {result.result.demand_prediction.score || 'N/A'}%
              </div>
            </div>
            {result.result.demand_prediction.competitors && (
              <div className="metric-card">
                <div className="metric-label">Nearby Competitors</div>
                <div className="metric-value">
                  {result.result.demand_prediction.competitors} projects
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Navigation */}
      <div className="navigation-buttons">
        <button 
          className="btn-secondary"
          onClick={() => navigate(`/projects/${projectId}/modules/m2/results`)}
        >
          ← M2 Results
        </button>
        <button 
          className="btn-primary"
          onClick={() => navigate(`/projects/${projectId}/modules/m4/results`)}
        >
          M4 Results →
        </button>
      </div>
    </div>
  );
};
