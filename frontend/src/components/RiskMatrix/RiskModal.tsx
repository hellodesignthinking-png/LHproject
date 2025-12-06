/**
 * Risk Modal Component
 * Phase 4: Frontend Visualization - Task 2
 * 
 * Modal dialog showing detailed risk information:
 * - Risk ID, name, category
 * - Probability and impact scores
 * - Risk level with visual indicator
 * - Detailed description
 * - 3+ response strategies
 */

import React, { useEffect } from 'react';
import { RiskModalProps } from './types';
import { getRiskLevelConfig } from './utils';
import './RiskMatrix.css';

const RiskModal: React.FC<RiskModalProps> = ({ risk, isOpen, onClose }) => {
  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !risk) return null;

  const config = getRiskLevelConfig(risk.risk_level);

  /**
   * Get category display name in Korean
   */
  const getCategoryName = (category: string): string => {
    const categoryMap: Record<string, string> = {
      financial: '재무',
      construction: '공사',
      legal: '법률/인허가',
      market: '시장',
      operational: '운영'
    };
    return categoryMap[category] || category;
  };

  /**
   * Render probability and impact scores
   */
  const renderScores = () => {
    return (
      <div className="risk-modal-scores">
        <div className="risk-score-item">
          <div className="score-label">발생확률</div>
          <div className="score-value">
            <div className="score-bar">
              <div 
                className="score-bar-fill"
                style={{ 
                  width: `${(risk.probability / 5) * 100}%`,
                  backgroundColor: config.color
                }}
              />
            </div>
            <span className="score-number">{risk.probability}/5</span>
          </div>
        </div>

        <div className="risk-score-item">
          <div className="score-label">영향도</div>
          <div className="score-value">
            <div className="score-bar">
              <div 
                className="score-bar-fill"
                style={{ 
                  width: `${(risk.impact / 5) * 100}%`,
                  backgroundColor: config.color
                }}
              />
            </div>
            <span className="score-number">{risk.impact}/5</span>
          </div>
        </div>

        <div className="risk-score-item risk-score-total">
          <div className="score-label">위험도 점수</div>
          <div className="score-value">
            <span className="score-number-large" style={{ color: config.color }}>
              {risk.risk_score}
            </span>
            <span className="score-max">/ 25</span>
          </div>
        </div>
      </div>
    );
  };

  /**
   * Render response strategies
   */
  const renderStrategies = () => {
    if (!risk.response_strategies || risk.response_strategies.length === 0) {
      return (
        <div className="no-strategies">
          대응 전략이 정의되지 않았습니다.
        </div>
      );
    }

    return (
      <div className="risk-strategies-list">
        {risk.response_strategies.map((strategy, index) => (
          <div key={`strategy-${index}`} className="strategy-item">
            <div className="strategy-number">{index + 1}</div>
            <div className="strategy-text">{strategy}</div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <>
      {/* Modal overlay */}
      <div className="risk-modal-overlay" onClick={onClose}>
        {/* Modal content */}
        <div className="risk-modal" onClick={(e) => e.stopPropagation()}>
          {/* Header */}
          <div className="risk-modal-header">
            <div className="risk-modal-header-top">
              <div className="risk-id-badge">{risk.id}</div>
              <button 
                className="risk-modal-close"
                onClick={onClose}
                aria-label="닫기"
              >
                ✕
              </button>
            </div>
            <h2 className="risk-modal-title">{risk.name}</h2>
            <div className="risk-modal-meta">
              <span className="risk-category-badge">
                {getCategoryName(risk.category)}
              </span>
              <span 
                className="risk-level-badge"
                style={{ 
                  backgroundColor: config.backgroundColor,
                  color: config.color,
                  borderColor: config.borderColor
                }}
              >
                {config.emoji} {config.label}
              </span>
            </div>
          </div>

          {/* Body */}
          <div className="risk-modal-body">
            {/* Scores section */}
            <div className="risk-modal-section">
              <h3 className="risk-modal-section-title">위험도 평가</h3>
              {renderScores()}
            </div>

            {/* Description section */}
            <div className="risk-modal-section">
              <h3 className="risk-modal-section-title">상세 설명</h3>
              <p className="risk-description">{risk.description}</p>
            </div>

            {/* Strategies section */}
            <div className="risk-modal-section">
              <h3 className="risk-modal-section-title">
                대응 전략 
                <span className="strategy-count">
                  ({risk.response_strategies?.length || 0}개)
                </span>
              </h3>
              {renderStrategies()}
            </div>
          </div>

          {/* Footer */}
          <div className="risk-modal-footer">
            <button 
              className="risk-modal-btn risk-modal-btn-close"
              onClick={onClose}
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default RiskModal;
