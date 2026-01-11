import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, M5Result } from '../services/analysisAPI';
import './ModuleResultsPage.css';

export const M5ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<M5Result | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const loadResult = async () => {
      try {
        setLoading(true);
        const data = await analysisAPI.getModuleResult<M5Result>(projectId, 'M5');
        
        if (!data.context_id || !data.execution_id) {
          throw new Error('Invalid context: Missing context_id or execution_id');
        }
        
        setResult(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load M5 results');
      } finally {
        setLoading(false);
      }
    };

    loadResult();
  }, [projectId]);

  if (loading) {
    return (
      <div className="module-results-page">
        <div className="loading-spinner">Loading M5 Results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-results-page">
        <div className="error-message">
          <h3>❌ Error Loading M5 Results</h3>
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
        <div className="no-data">No M5 results available</div>
      </div>
    );
  }

  const financial = result.result.financial_metrics;
  const profitability = result.result.profitability;

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

      {/* M5 Header */}
      <div className="module-header">
        <h1>M5: Feasibility Analysis</h1>
        <p className="subtitle">사업 타당성 분석 결과</p>
      </div>

      {/* Financial Metrics */}
      <section className="result-section">
        <h2>💰 Financial Metrics</h2>
        <div className="financial-grid">
          <div className="financial-card">
            <div className="metric-label">NPV (Public)</div>
            <div className="metric-value npv">
              ₩{financial?.npv_public?.toLocaleString() || '0'}
            </div>
          </div>
          <div className="financial-card">
            <div className="metric-label">NPV (Market)</div>
            <div className="metric-value npv">
              ₩{financial?.npv_market?.toLocaleString() || '0'}
            </div>
          </div>
          <div className="financial-card">
            <div className="metric-label">IRR</div>
            <div className="metric-value irr">
              {financial?.irr_public?.toFixed(2) || '0'}%
            </div>
          </div>
          <div className="financial-card">
            <div className="metric-label">ROI</div>
            <div className="metric-value roi">
              {result.result.roi?.toFixed(2) || '0'}%
            </div>
          </div>
        </div>
      </section>

      {/* Profitability */}
      <section className="result-section">
        <h2>📊 Profitability Assessment</h2>
        <div className="profitability-summary">
          <div className="profit-grade">
            <span className="label">Grade:</span>
            <span className={`grade grade-${profitability?.grade?.toLowerCase() || 'unknown'}`}>
              {profitability?.grade || 'N/A'}
            </span>
          </div>
          <div className="profit-status">
            <span className="label">Profitable:</span>
            <span className={`status ${profitability?.profitable ? 'yes' : 'no'}`}>
              {profitability?.profitable ? '✓ YES' : '✗ NO'}
            </span>
          </div>
        </div>
        {profitability?.assessment_rationale && (
          <div className="rationale-box">
            <strong>Assessment Rationale:</strong>
            <p>{profitability.assessment_rationale}</p>
          </div>
        )}
      </section>

      {/* Cost Structure */}
      {result.result.cost_structure && (
        <section className="result-section">
          <h2>💸 Cost Structure</h2>
          <div className="cost-breakdown">
            {result.result.cost_structure.land_acquisition && (
              <div className="cost-item">
                <span className="label">Land Acquisition:</span>
                <span className="value">
                  ₩{result.result.cost_structure.land_acquisition.toLocaleString()}
                </span>
              </div>
            )}
            {result.result.cost_structure.construction && (
              <div className="cost-item">
                <span className="label">Construction:</span>
                <span className="value">
                  ₩{result.result.cost_structure.construction.toLocaleString()}
                </span>
              </div>
            )}
            {result.result.cost_structure.total_cost && (
              <div className="cost-item total">
                <span className="label">Total Project Cost:</span>
                <span className="value">
                  ₩{result.result.cost_structure.total_cost.toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Revenue Projection */}
      {result.result.revenue_projection && (
        <section className="result-section">
          <h2>📈 Revenue Projection</h2>
          <div className="revenue-metrics">
            {result.result.revenue_projection.total_revenue && (
              <div className="metric-item">
                <span className="label">Total Revenue:</span>
                <span className="value">
                  ₩{result.result.revenue_projection.total_revenue.toLocaleString()}
                </span>
              </div>
            )}
            {result.result.revenue_projection.avg_unit_price && (
              <div className="metric-item">
                <span className="label">Average Unit Price:</span>
                <span className="value">
                  ₩{result.result.revenue_projection.avg_unit_price.toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Risk Factors */}
      {result.result.risk_factors && result.result.risk_factors.length > 0 && (
        <section className="result-section">
          <h2>⚠️ Risk Factors</h2>
          <ul className="risk-list">
            {result.result.risk_factors.map((risk, idx) => (
              <li key={idx} className="risk-item">
                <span className="risk-severity">{risk.severity || 'Medium'}</span>
                <span className="risk-description">{risk.description || risk}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Key Assumptions */}
      {result.result.assumptions && (
        <section className="result-section">
          <h2>📝 Key Assumptions</h2>
          <div className="assumptions-box">
            <pre>{JSON.stringify(result.result.assumptions, null, 2)}</pre>
          </div>
        </section>
      )}

      {/* Navigation */}
      <div className="navigation-buttons">
        <button 
          className="btn-secondary"
          onClick={() => navigate(`/projects/${projectId}/modules/m4/results`)}
        >
          ← M4 Results
        </button>
        <button 
          className="btn-primary"
          onClick={() => navigate(`/projects/${projectId}/modules/m6/results`)}
        >
          M6 Results →
        </button>
      </div>
    </div>
  );
};
