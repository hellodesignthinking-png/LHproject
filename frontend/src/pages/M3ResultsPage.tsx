import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, ModuleResult } from '../services/analysisAPI';
import './ModuleResultsPage.css';

type M3Result = ModuleResult<any>;

export const M3ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<M3Result | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notExecuted, setNotExecuted] = useState(false);
  const [executing, setExecuting] = useState(false);

  const loadResult = async () => {
    if (!projectId) return;

    try {
      setLoading(true);
      setError(null);
      setNotExecuted(false);
      
      const data = await analysisAPI.getModuleResult<any>(projectId, 'M3');
      
      // ✅ Validate M3 result schema
      const m3Data = data.result;
      
      if (!m3Data || typeof m3Data !== 'object') {
        throw new Error('M3 result data is missing or invalid');
      }
      
      if (!m3Data.selected_type) {
        throw new Error('M3 result missing required field: selected_type');
      }
      
      if (!m3Data.decision_rationale || m3Data.decision_rationale.length < 20) {
        throw new Error('M3 result has invalid decision_rationale (too short or missing)');
      }
      
      setResult(data);
    } catch (err: any) {
      console.error('Error loading M3 result:', err);
      
      // Check if it's a MODULE_NOT_EXECUTED error
      if (err.message?.includes('MODULE_NOT_EXECUTED') || 
          err.message?.includes('has not been executed')) {
        setNotExecuted(true);
        setError('M3 has not been executed yet. Click "Run M3" to execute.');
      } else {
        setError(err.message || 'Failed to load M3 results');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResult();
  }, [projectId]);

  const handleExecuteM3 = async () => {
    if (!projectId) return;
    
    try {
      setExecuting(true);
      setError(null);
      
      // Execute M3
      await analysisAPI.executeModule(projectId, 'M3');
      
      // Wait a moment for execution to complete
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Reload result
      await loadResult();
    } catch (err: any) {
      setError(err.message || 'Failed to execute M3');
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="module-results-page">
        <div className="loading-spinner">Loading M3 Results...</div>
      </div>
    );
  }

  if (notExecuted) {
    return (
      <div className="module-results-page">
        <div className="not-executed-message">
          <h2>⏳ M3 Not Executed</h2>
          <p>M3 Housing Type Decision has not been executed yet.</p>
          <p className="help-text">
            Make sure M2 is completed first, then click the button below to execute M3.
          </p>
          <div className="action-buttons">
            <button 
              className="btn-primary"
              onClick={handleExecuteM3}
              disabled={executing}
            >
              {executing ? 'Executing M3...' : '▶️ Run M3'}
            </button>
            <button 
              className="btn-secondary"
              onClick={() => navigate(`/projects/${projectId}`)}
            >
              ← Back to Project
            </button>
          </div>
          {error && (
            <div className="error-message" style={{ marginTop: '1rem' }}>
              {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-results-page">
        <div className="error-message">
          <h3>❌ Error Loading M3 Results</h3>
          <p>{error}</p>
          <div className="action-buttons">
            <button onClick={loadResult} className="btn-primary">
              🔄 Retry
            </button>
            <button onClick={() => navigate(`/projects/${projectId}`)} className="btn-secondary">
              ← Back to Project
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!result || !result.result) {
    return (
      <div className="module-results-page">
        <div className="no-data">
          <h3>No M3 results available</h3>
          <button onClick={handleExecuteM3} disabled={executing}>
            {executing ? 'Executing...' : '▶️ Run M3'}
          </button>
        </div>
      </div>
    );
  }

  // Safe access with defaults
  const m3Data = result.result;
  const selectedType = m3Data.selected_type || 'Unknown';
  const confidence = m3Data.confidence || 0;
  const rationale = m3Data.decision_rationale || m3Data.selection_reason || 'No rationale provided';
  const selectionMethod = m3Data.selection_method || 'N/A';

  return (
    <div className="module-results-page">
      {/* Context Metadata Header */}
      <div className="context-metadata">
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="label">Module:</span>
            <code>M3</code>
          </div>
          <div className="metadata-item">
            <span className="label">Execution ID:</span>
            <code>{m3Data.execution_id || 'N/A'}</code>
          </div>
          <div className="metadata-item">
            <span className="label">Computed At:</span>
            <span>{m3Data.computed_at ? new Date(m3Data.computed_at).toLocaleString('ko-KR') : 'N/A'}</span>
          </div>
          <div className="metadata-item">
            <span className="label">Status:</span>
            <span className="status-badge">{m3Data.status || 'completed'}</span>
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
            {selectedType}
          </div>
          <div className="confidence-score">
            Confidence: {confidence}%
          </div>
        </div>
      </section>

      {/* Decision Rationale */}
      <section className="result-section">
        <h2>📋 Decision Rationale</h2>
        <div className="rationale-box">
          <p className="rationale-text">
            {rationale}
          </p>
        </div>
        
        {selectionMethod && (
          <div className="method-info">
            <strong>Selection Method:</strong> {selectionMethod}
          </div>
        )}
      </section>

      {/* Strengths */}
      {m3Data.strengths && m3Data.strengths.length > 0 && (
        <section className="result-section">
          <h2>💪 Strengths</h2>
          <ul className="strength-list">
            {m3Data.strengths.map((strength: string, idx: number) => (
              <li key={idx} className="strength-item">
                ✓ {strength}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Weaknesses */}
      {m3Data.weaknesses && m3Data.weaknesses.length > 0 && (
        <section className="result-section">
          <h2>⚠️ Weaknesses</h2>
          <ul className="weakness-list">
            {m3Data.weaknesses.map((weakness: string, idx: number) => (
              <li key={idx} className="weakness-item">
                ⚠ {weakness}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Rejected Types */}
      {m3Data.rejected_types && m3Data.rejected_types.length > 0 && (
        <section className="result-section">
          <h2>❌ Rejected Types</h2>
          <div className="rejected-types">
            {m3Data.rejected_types.map((rejected: any, idx: number) => (
              <div key={idx} className="rejected-type-card">
                <div className="rejected-type-name">{rejected.type}</div>
                <div className="rejection-reason">{rejected.reason}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Demand Prediction */}
      {m3Data.demand_prediction && (
        <section className="result-section">
          <h2>📊 Demand Prediction</h2>
          <div className="demand-metrics">
            <div className="metric-card">
              <div className="metric-label">Demand Score</div>
              <div className="metric-value">
                {m3Data.demand_prediction.score || 'N/A'}%
              </div>
            </div>
            {m3Data.demand_prediction.competitors && (
              <div className="metric-card">
                <div className="metric-label">Nearby Competitors</div>
                <div className="metric-value">
                  {m3Data.demand_prediction.competitors} projects
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
