/**
 * Risk Matrix Grid Component
 * Phase 4 - Day 1-2: Interactive 5×5 Risk Matrix Visualization
 */

import React, { useState, useMemo } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Cell,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend
} from 'recharts';
import { Risk, RiskMatrixProps } from './types';
import { transformRisksToChartData, getRiskEmoji, getRiskColor } from './utils';
import { RiskModal } from './RiskModal';
import './RiskMatrix.css';

export const RiskMatrixGrid: React.FC<RiskMatrixProps> = ({
  risks,
  onRiskClick,
  loading = false,
  error = null
}) => {
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Transform data for chart
  const chartData = useMemo(() => transformRisksToChartData(risks), [risks]);

  // Handle risk cell click
  const handleCellClick = (data: any) => {
    if (data && data.risk) {
      setSelectedRisk(data.risk);
      setIsModalOpen(true);
      if (onRiskClick) {
        onRiskClick(data.risk);
      }
    }
  };

  // Handle modal close
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedRisk(null), 300); // Delay clearing to allow animation
  };

  // Custom tooltip content
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length > 0) {
      const data = payload[0].payload;
      const risk = data.risk;

      return (
        <div className="risk-tooltip">
          <div className="risk-tooltip-header">
            <span className="risk-emoji">{getRiskEmoji(risk.risk_level)}</span>
            <strong>{risk.name}</strong>
          </div>
          <div className="risk-tooltip-body">
            <p className="risk-tooltip-category">{risk.category_kr}</p>
            <p className="risk-tooltip-score">
              Score: <strong>{risk.risk_score}</strong> ({risk.risk_level_kr})
            </p>
            <p className="risk-tooltip-metrics">
              발생확률: {risk.probability}/5 | 영향도: {risk.impact}/5
            </p>
          </div>
          <div className="risk-tooltip-footer">
            클릭하여 상세 정보 보기
          </div>
        </div>
      );
    }
    return null;
  };

  // Loading state
  if (loading) {
    return (
      <div className="risk-matrix-container">
        <div className="risk-matrix-loading">
          <div className="spinner"></div>
          <p>위험 매트릭스 로딩 중...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="risk-matrix-container">
        <div className="risk-matrix-error">
          <p>⚠️ 오류가 발생했습니다</p>
          <p className="error-message">{error}</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (!risks || risks.length === 0) {
    return (
      <div className="risk-matrix-container">
        <div className="risk-matrix-empty">
          <p>📊 표시할 위험이 없습니다</p>
        </div>
      </div>
    );
  }

  return (
    <div className="risk-matrix-container">
      <div className="risk-matrix-header">
        <h2 className="risk-matrix-title">
          위험 매트릭스 (Risk Matrix 5×5)
        </h2>
        <p className="risk-matrix-subtitle">
          총 {risks.length}개의 위험 요소 | 발생확률 × 영향도
        </p>
      </div>

      {/* Legend */}
      <div className="risk-legend">
        <div className="legend-item">
          <span className="legend-dot critical"></span>
          <span className="legend-text">심각 (CRITICAL ≥20)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot high"></span>
          <span className="legend-text">높음 (HIGH 12-19)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot medium"></span>
          <span className="legend-text">보통 (MEDIUM 6-11)</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot low"></span>
          <span className="legend-text">낮음 (LOW &lt;6)</span>
        </div>
      </div>

      {/* Chart */}
      <div className="risk-matrix-chart">
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 40, left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            
            <XAxis
              type="number"
              dataKey="x"
              name="발생확률"
              domain={[0, 6]}
              ticks={[1, 2, 3, 4, 5]}
              label={{
                value: '발생확률 (Probability)',
                position: 'bottom',
                offset: 20,
                style: { fontSize: 14, fontWeight: 600 }
              }}
              tickLine={{ stroke: '#9ca3af' }}
              axisLine={{ stroke: '#9ca3af' }}
            />
            
            <YAxis
              type="number"
              dataKey="y"
              name="영향도"
              domain={[0, 6]}
              ticks={[1, 2, 3, 4, 5]}
              label={{
                value: '영향도 (Impact)',
                angle: -90,
                position: 'left',
                offset: 40,
                style: { fontSize: 14, fontWeight: 600 }
              }}
              tickLine={{ stroke: '#9ca3af' }}
              axisLine={{ stroke: '#9ca3af' }}
            />
            
            <ZAxis
              type="number"
              dataKey="z"
              range={[200, 600]}
              name="Risk Score"
            />
            
            <Tooltip content={<CustomTooltip />} />
            
            <Scatter
              data={chartData}
              onClick={handleCellClick}
              style={{ cursor: 'pointer' }}
              shape="circle"
            >
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.fill}
                  stroke="#fff"
                  strokeWidth={2}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Risk Summary */}
      <div className="risk-summary">
        <div className="summary-card">
          <div className="summary-icon">🎯</div>
          <div className="summary-content">
            <div className="summary-label">총 위험 요소</div>
            <div className="summary-value">{risks.length}개</div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">🔴</div>
          <div className="summary-content">
            <div className="summary-label">심각 위험</div>
            <div className="summary-value">
              {risks.filter(r => r.risk_level === 'CRITICAL').length}개
            </div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">🟠</div>
          <div className="summary-content">
            <div className="summary-label">높은 위험</div>
            <div className="summary-value">
              {risks.filter(r => r.risk_level === 'HIGH').length}개
            </div>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">📊</div>
          <div className="summary-content">
            <div className="summary-label">평균 점수</div>
            <div className="summary-value">
              {(risks.reduce((sum, r) => sum + r.risk_score, 0) / risks.length).toFixed(1)}
            </div>
          </div>
        </div>
      </div>

      {/* Risk Modal */}
      <RiskModal
        risk={selectedRisk}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default RiskMatrixGrid;
