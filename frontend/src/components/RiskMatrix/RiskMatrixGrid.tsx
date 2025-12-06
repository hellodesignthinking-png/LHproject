/**
 * Risk Matrix Grid Component
 * Phase 4: Frontend Visualization - Task 2
 * 
 * Interactive 5×5 Risk Matrix with:
 * - Color-coded cells based on risk level
 * - Hover tooltips showing cell details
 * - Click to view risks in modal
 * - Responsive design
 * - Legend showing risk levels
 */

import React, { useState, useMemo } from 'react';
import { RiskMatrixProps, Risk, RiskMatrixCell } from './types';
import { 
  getRiskLevelConfig, 
  getCellBackgroundColor, 
  getCellBorderColor,
  getCellTextColor,
  formatRiskCount,
  getCellTooltip 
} from './utils';
import RiskModal from './RiskModal';
import './RiskMatrix.css';

const RiskMatrixGrid: React.FC<RiskMatrixProps> = ({
  data,
  width,
  height,
  onRiskClick,
  showLegend = true,
  className = ''
}) => {
  const [selectedCell, setSelectedCell] = useState<RiskMatrixCell | null>(null);
  const [selectedRisk, setSelectedRisk] = useState<Risk | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [hoveredCell, setHoveredCell] = useState<{ x: number; y: number } | null>(null);

  /**
   * Handle cell click
   * Opens modal showing risks in the cell
   */
  const handleCellClick = (cell: RiskMatrixCell) => {
    if (cell.count > 0) {
      setSelectedCell(cell);
      if (cell.risks.length === 1) {
        // If only one risk, show it directly
        setSelectedRisk(cell.risks[0]);
        setIsModalOpen(true);
      } else {
        // Multiple risks - show list modal
        setSelectedRisk(null);
        setIsModalOpen(true);
      }
    }
  };

  /**
   * Handle risk selection from list
   */
  const handleRiskSelect = (risk: Risk) => {
    setSelectedRisk(risk);
    if (onRiskClick) {
      onRiskClick(risk);
    }
  };

  /**
   * Close modal
   */
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedCell(null);
    setSelectedRisk(null);
  };

  /**
   * Render matrix legend
   */
  const renderLegend = () => {
    const levels: Array<'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'> = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
    
    return (
      <div className="risk-matrix-legend">
        <div className="legend-title">위험도 수준</div>
        <div className="legend-items">
          {levels.map(level => {
            const config = getRiskLevelConfig(level);
            const count = data.risk_counts[level];
            
            return (
              <div key={level} className="legend-item">
                <div 
                  className="legend-color-box"
                  style={{
                    backgroundColor: config.backgroundColor,
                    borderColor: config.borderColor
                  }}
                >
                  <span className="legend-emoji">{config.emoji}</span>
                </div>
                <div className="legend-label">
                  <span className="legend-level-name">{config.label}</span>
                  <span className="legend-count">({count}개)</span>
                </div>
              </div>
            );
          })}
        </div>
        <div className="legend-total">
          총 리스크: <strong>{data.total_risks}개</strong>
        </div>
      </div>
    );
  };

  /**
   * Render single matrix cell
   */
  const renderCell = (cell: RiskMatrixCell, rowIndex: number, colIndex: number) => {
    const isHovered = hoveredCell?.x === colIndex && hoveredCell?.y === rowIndex;
    const hasRisks = cell.count > 0;
    
    const cellStyle = {
      backgroundColor: getCellBackgroundColor(cell.level),
      borderColor: getCellBorderColor(cell.level),
      cursor: hasRisks ? 'pointer' : 'default',
      opacity: hasRisks ? 1 : 0.6,
      transform: isHovered && hasRisks ? 'scale(1.05)' : 'scale(1)',
      transition: 'all 0.2s ease'
    };

    const textColor = getCellTextColor(cell.level);
    const tooltip = getCellTooltip(cell.probability, cell.impact, cell.count, cell.level);

    return (
      <div
        key={`cell-${rowIndex}-${colIndex}`}
        className={`risk-matrix-cell ${hasRisks ? 'has-risks' : 'empty'} ${isHovered ? 'hovered' : ''}`}
        style={cellStyle}
        onClick={() => handleCellClick(cell)}
        onMouseEnter={() => setHoveredCell({ x: colIndex, y: rowIndex })}
        onMouseLeave={() => setHoveredCell(null)}
        title={tooltip}
      >
        {hasRisks && (
          <>
            <div className="cell-count" style={{ color: textColor }}>
              {formatRiskCount(cell.count)}
            </div>
            {cell.count > 1 && (
              <div className="cell-multiple-indicator">
                <span className="multiple-icon">📋</span>
              </div>
            )}
          </>
        )}
        {!hasRisks && (
          <div className="cell-empty-indicator">—</div>
        )}
      </div>
    );
  };

  /**
   * Render axis labels
   */
  const renderAxisLabels = () => {
    return (
      <>
        {/* X-axis label (bottom) */}
        <div className="axis-label axis-label-x">
          {data.axis_labels.x_label}
          <div className="axis-arrow">→</div>
        </div>

        {/* Y-axis label (left) */}
        <div className="axis-label axis-label-y">
          <div className="axis-arrow axis-arrow-vertical">↑</div>
          {data.axis_labels.y_label}
        </div>

        {/* X-axis tick labels */}
        <div className="axis-ticks axis-ticks-x">
          {data.axis_labels.x_values.map((value, index) => (
            <div key={`x-tick-${index}`} className="axis-tick">
              {value}
            </div>
          ))}
        </div>

        {/* Y-axis tick labels */}
        <div className="axis-ticks axis-ticks-y">
          {data.axis_labels.y_values.map((value, index) => (
            <div key={`y-tick-${index}`} className="axis-tick">
              {value}
            </div>
          ))}
        </div>
      </>
    );
  };

  /**
   * Render risk list modal (when multiple risks in cell)
   */
  const renderRiskListModal = () => {
    if (!selectedCell || selectedRisk !== null) return null;

    return (
      <div className="risk-list-modal-overlay" onClick={handleCloseModal}>
        <div className="risk-list-modal" onClick={(e) => e.stopPropagation()}>
          <div className="risk-list-modal-header">
            <h3>
              리스크 목록 
              <span className="risk-list-count">({selectedCell.count}개)</span>
            </h3>
            <button className="modal-close-btn" onClick={handleCloseModal}>
              ✕
            </button>
          </div>
          <div className="risk-list-modal-subtitle">
            발생확률: {selectedCell.probability} | 영향도: {selectedCell.impact}
          </div>
          <div className="risk-list-modal-body">
            {selectedCell.risks.map((risk, index) => {
              const config = getRiskLevelConfig(risk.risk_level);
              return (
                <div 
                  key={risk.id} 
                  className="risk-list-item"
                  onClick={() => handleRiskSelect(risk)}
                  style={{ borderLeftColor: config.color }}
                >
                  <div className="risk-list-item-header">
                    <span className="risk-list-item-emoji">{config.emoji}</span>
                    <span className="risk-list-item-id">{risk.id}</span>
                    <span className="risk-list-item-level" style={{ color: config.color }}>
                      {config.label}
                    </span>
                    <span className="risk-list-item-score">
                      {risk.risk_score}점
                    </span>
                  </div>
                  <div className="risk-list-item-name">{risk.name}</div>
                  <div className="risk-list-item-category">
                    카테고리: {risk.category}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className={`risk-matrix-container ${className}`} style={{ width, height }}>
      <div className="risk-matrix-header">
        <h2 className="risk-matrix-title">리스크 매트릭스 (5×5)</h2>
        <p className="risk-matrix-subtitle">
          발생확률과 영향도에 따른 위험 분포 | 총 {data.total_risks}개 리스크
        </p>
      </div>

      <div className="risk-matrix-content">
        <div className="risk-matrix-grid-wrapper">
          {renderAxisLabels()}
          
          <div className="risk-matrix-grid">
            {data.matrix.map((row, rowIndex) => (
              <div key={`row-${rowIndex}`} className="risk-matrix-row">
                {row.map((cell, colIndex) => renderCell(cell, rowIndex, colIndex))}
              </div>
            ))}
          </div>
        </div>

        {showLegend && renderLegend()}
      </div>

      {/* Risk detail modal */}
      <RiskModal
        risk={selectedRisk}
        isOpen={isModalOpen && selectedRisk !== null}
        onClose={handleCloseModal}
      />

      {/* Risk list modal (multiple risks in cell) */}
      {renderRiskListModal()}
    </div>
  );
};

export default RiskMatrixGrid;
