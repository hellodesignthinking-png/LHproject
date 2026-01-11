/**
 * M2 Results Page
 * ===============
 * 
 * Shows land valuation and market analysis results
 * 
 * Key data:
 * - Land value (₩)
 * - Unit prices (per m², per 평)
 * - Transaction samples with adjustments
 * - Confidence score
 * - Premium factors
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, ModuleResult, useProjectStatus } from '../../services/analysisAPI';
import { ModuleStatusBar } from '../../components/ModuleStatusBar';
import './ModuleResultsPage.css';

interface M2Data {
  land_value: number;
  unit_price_sqm: number;
  unit_price_pyeong: number;
  confidence_score: number;
  confidence_level: string;
  valuation_method: string;
  transaction_samples: Array<{
    date: string;
    area: number;
    amount: number;
    distance: number;
    adjustment_rate: number;
    adjusted_amount: number;
  }>;
  official_price: number;
  market_to_official_ratio: number;
  premium_factors: {
    corner_lot?: number;
    subway_proximity?: number;
    school_district?: number;
  };
  price_range: {
    min: number;
    max: number;
  };
}

export const M2ResultsPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const { status: projectStatus, loading: statusLoading } = 
    useProjectStatus(projectId || null);
  
  const [m2Data, setM2Data] = useState<M2Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const fetchM2Data = async () => {
      try {
        setLoading(true);
        const result = await analysisAPI.getModuleResult<M2Data>(projectId, 'M2');
        setM2Data(result.result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load M2 data');
      } finally {
        setLoading(false);
      }
    };

    fetchM2Data();
  }, [projectId]);

  const handleModuleClick = (moduleName: string) => {
    navigate(`/projects/${projectId}/modules/${moduleName.toLowerCase()}/results`);
  };

  if (statusLoading || loading) {
    return <div className="results-page loading"><div className="spinner">Loading...</div></div>;
  }

  if (error || !m2Data) {
    return (
      <div className="results-page error">
        <h2>❌ Error</h2>
        <p>{error || 'No data available'}</p>
      </div>
    );
  }

  if (!projectStatus) return null;

  return (
    <div className="results-page">
      <ModuleStatusBar
        m1={projectStatus.m1_status}
        m2={projectStatus.m2_status}
        m3={projectStatus.m3_status}
        m4={projectStatus.m4_status}
        m5={projectStatus.m5_status}
        m6={projectStatus.m6_status}
        projectId={projectId!}
        onModuleClick={handleModuleClick}
      />

      <div className="page-header">
        <h1>📈 M2 토지가치 · 시장 분석</h1>
        <div className="project-info">
          <span><strong>Project:</strong> {projectStatus.project_name}</span>
          <span><strong>Address:</strong> {projectStatus.address}</span>
        </div>
      </div>

      <div className="results-content">
        {/* Land Value Summary */}
        <section className="result-panel">
          <h2>💰 토지가치 산출 결과</h2>
          <div className="value-display">
            <div className="primary-value">
              <label>토지가치</label>
              <value className="large">₩{m2Data.land_value.toLocaleString()}</value>
            </div>
            <div className="secondary-values">
              <div>
                <label>단위면적당 (m²)</label>
                <value>₩{m2Data.unit_price_sqm.toLocaleString()}</value>
              </div>
              <div>
                <label>단위면적당 (평)</label>
                <value>₩{m2Data.unit_price_pyeong.toLocaleString()}</value>
              </div>
            </div>
          </div>
          
          <div className="method-info">
            <p><strong>산출방법:</strong> {m2Data.valuation_method}</p>
            <p><strong>신뢰도:</strong> {m2Data.confidence_score}% ({m2Data.confidence_level})</p>
          </div>
        </section>

        {/* Transaction Samples */}
        <section className="result-panel">
          <h2>📊 거래사례 분석</h2>
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>거래일</th>
                <th>면적</th>
                <th>거래가</th>
                <th>거리</th>
                <th>조정률</th>
                <th>조정가</th>
              </tr>
            </thead>
            <tbody>
              {m2Data.transaction_samples.map((sample, idx) => (
                <tr key={idx}>
                  <td>{idx + 1}</td>
                  <td>{sample.date}</td>
                  <td>{sample.area.toLocaleString()}m²</td>
                  <td>₩{sample.amount.toLocaleString()}</td>
                  <td>{sample.distance}m</td>
                  <td className={sample.adjustment_rate > 0 ? 'positive' : 'negative'}>
                    {sample.adjustment_rate > 0 ? '+' : ''}{sample.adjustment_rate.toFixed(1)}%
                  </td>
                  <td>₩{sample.adjusted_amount.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* Navigation */}
        <div className="navigation-buttons">
          <button className="btn" onClick={() => navigate(`/projects/${projectId}/modules/m1/verify`)}>
            ◀ M1으로 돌아가기
          </button>
          <button className="btn btn-primary" onClick={() => navigate(`/projects/${projectId}/modules/m3/results`)}>
            M3 진행 ▶
          </button>
        </div>
      </div>
    </div>
  );
};
