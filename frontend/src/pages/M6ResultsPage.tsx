import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, ModuleResult } from '../services/analysisAPI';

type M6Result = ModuleResult<any>;
import './ModuleResultsPage.css';

export const M6ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<M6Result | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const loadResult = async () => {
      try {
        setLoading(true);
        const data = await analysisAPI.getModuleResult<any>(projectId, 'M6');
        
        // Check if we got real data or just mock metadata
        const hasRealData = data.result && 
                           typeof data.result === 'object' && 
                           Object.keys(data.result).length > 5;
        
        if (!hasRealData) {
          throw new Error('M6 분석이 완료되었지만 상세 데이터가 아직 생성되지 않았습니다. (Mock execution)');
        }
        
        if (!data.context_id || !data.execution_id) {
          throw new Error('Invalid context: Missing context_id or execution_id');
        }
        
        setResult(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load M6 results');
      } finally {
        setLoading(false);
      }
    };

    loadResult();
  }, [projectId]);

  if (loading) {
    return (
      <div className="module-results-page">
        <div className="loading-spinner">Loading M6 Results...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="module-results-page">
        <div className="error-message">
          <h3>❌ Error Loading M6 Results</h3>
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
        <div className="no-data">No M6 results available</div>
      </div>
    );
  }

  const getDecisionClass = (decision: string) => {
    if (decision === 'GO') return 'decision-go';
    if (decision === 'CONDITIONAL') return 'decision-conditional';
    return 'decision-no-go';
  };

  const getGradeClass = (grade: string) => {
    if (grade === 'A' || grade === 'B') return 'grade-excellent';
    if (grade === 'C') return 'grade-good';
    return 'grade-fair';
  };

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

      {/* M6 Header */}
      <div className="module-header">
        <h1>M6: LH Comprehensive Review</h1>
        <p className="subtitle">LH 종합 심사 및 의사결정</p>
      </div>

      {/* Final Decision */}
      <section className="result-section decision-section">
        <h2>🎯 Final Decision</h2>
        <div className={`decision-badge ${getDecisionClass(result.result.decision)}`}>
          {result.result.decision}
        </div>
        <div className="score-display">
          <span className="score-label">Total Score:</span>
          <span className="score-value">
            {result.result.total_score?.toFixed(1) || '0.0'} / 110
          </span>
          <span className={`grade-badge ${getGradeClass(result.result.grade || 'N/A')}`}>
            Grade {result.result.grade || 'N/A'}
          </span>
        </div>
      </section>

      {/* Decision Rationale */}
      <section className="result-section">
        <h2>📋 Decision Rationale</h2>
        <div className="rationale-box">
          <p>{result.result.decision_rationale || 'No rationale provided'}</p>
        </div>
      </section>

      {/* Score Breakdown */}
      {result.result.score_breakdown && (
        <section className="result-section">
          <h2>📊 Score Breakdown</h2>
          <div className="score-breakdown">
            {result.result.score_breakdown.location_score !== undefined && (
              <div className="score-item">
                <span className="category">Location (M1)</span>
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{ width: `${(result.result.score_breakdown.location_score / 35) * 100}%` }}
                  />
                </div>
                <span className="score-text">
                  {result.result.score_breakdown.location_score} / 35
                </span>
              </div>
            )}
            {result.result.score_breakdown.scale_score !== undefined && (
              <div className="score-item">
                <span className="category">Building Scale (M4)</span>
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{ width: `${(result.result.score_breakdown.scale_score / 20) * 100}%` }}
                  />
                </div>
                <span className="score-text">
                  {result.result.score_breakdown.scale_score} / 20
                </span>
              </div>
            )}
            {result.result.score_breakdown.feasibility_score !== undefined && (
              <div className="score-item">
                <span className="category">Feasibility (M5)</span>
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{ width: `${(result.result.score_breakdown.feasibility_score / 40) * 100}%` }}
                  />
                </div>
                <span className="score-text">
                  {result.result.score_breakdown.feasibility_score} / 40
                </span>
              </div>
            )}
            {result.result.score_breakdown.legal_compliance_score !== undefined && (
              <div className="score-item">
                <span className="category">Legal Compliance</span>
                <div className="score-bar">
                  <div 
                    className="score-fill" 
                    style={{ width: `${(result.result.score_breakdown.legal_compliance_score / 15) * 100}%` }}
                  />
                </div>
                <span className="score-text">
                  {result.result.score_breakdown.legal_compliance_score} / 15
                </span>
              </div>
            )}
          </div>
        </section>
      )}

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

      {/* Recommendations */}
      {result.result.recommendations && result.result.recommendations.length > 0 && (
        <section className="result-section">
          <h2>💡 Recommendations</h2>
          <ul className="recommendation-list">
            {result.result.recommendations.map((rec, idx) => (
              <li key={idx} className="recommendation-item">
                → {rec}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Conditions (for CONDITIONAL decision) */}
      {result.result.decision === 'CONDITIONAL' && result.result.conditions && (
        <section className="result-section conditions-section">
          <h2>📌 Conditions for Approval</h2>
          <ul className="conditions-list">
            {result.result.conditions.map((condition, idx) => (
              <li key={idx} className="condition-item">
                {idx + 1}. {condition}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Risk Mitigation */}
      {result.result.risk_mitigation && result.result.risk_mitigation.length > 0 && (
        <section className="result-section">
          <h2>🛡️ Risk Mitigation Strategies</h2>
          <ul className="mitigation-list">
            {result.result.risk_mitigation.map((strategy, idx) => (
              <li key={idx} className="mitigation-item">
                {strategy}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Navigation */}
      <div className="navigation-buttons">
        <button 
          className="btn-secondary"
          onClick={() => navigate(`/projects/${projectId}/modules/m5/results`)}
        >
          ← M5 Results
        </button>
        <button 
          className="btn-primary"
          onClick={() => navigate(`/projects/${projectId}/report`)}
        >
          Final Report →
        </button>
      </div>
    </div>
  );
};
