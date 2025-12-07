/**
 * Risk Modal Component
 * Displays detailed risk information including response strategies
 */

import React, { useEffect } from 'react';
import { RiskModalProps } from './types';
import { getRiskEmoji, getRiskColor } from './utils';
import './RiskMatrix.css';

export const RiskModal: React.FC<RiskModalProps> = ({ risk, isOpen, onClose }) => {
  // Handle ESC key press
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
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

  if (!isOpen || !risk) {
    return null;
  }

  const riskColor = getRiskColor(risk.risk_score);

  return (
    <div className="risk-modal-overlay" onClick={onClose}>
      <div 
        className="risk-modal-content" 
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="risk-modal-title"
      >
        {/* Close Button */}
        <button
          className="risk-modal-close"
          onClick={onClose}
          aria-label="Close modal"
        >
          ×
        </button>

        {/* Header */}
        <div className="risk-modal-header">
          <div className="risk-modal-title-row">
            <span className="risk-modal-emoji">
              {getRiskEmoji(risk.risk_level)}
            </span>
            <h2 id="risk-modal-title" className="risk-modal-title">
              {risk.name}
            </h2>
          </div>
          <p className="risk-modal-title-en">{risk.name_en}</p>
        </div>

        {/* Risk Metrics */}
        <div className="risk-modal-metrics">
          <div className="metric-card">
            <div className="metric-label">Risk ID</div>
            <div className="metric-value">{risk.id}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">Category</div>
            <div className="metric-value">{risk.category_kr}</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">발생확률</div>
            <div className="metric-value">{risk.probability}/5</div>
          </div>
          
          <div className="metric-card">
            <div className="metric-label">영향도</div>
            <div className="metric-value">{risk.impact}/5</div>
          </div>
          
          <div className="metric-card highlight">
            <div className="metric-label">Risk Score</div>
            <div 
              className="metric-value large" 
              style={{ color: riskColor }}
            >
              {risk.risk_score}
            </div>
          </div>
        </div>

        {/* Risk Level Badge */}
        <div className="risk-level-badge-container">
          <div 
            className={`risk-level-badge ${risk.risk_level.toLowerCase()}`}
            style={{ borderColor: riskColor }}
          >
            <span className="badge-emoji">{getRiskEmoji(risk.risk_level)}</span>
            <span className="badge-text">
              {risk.risk_level_kr} ({risk.risk_level})
            </span>
          </div>
        </div>

        {/* Description */}
        <div className="risk-modal-section">
          <h3 className="section-title">
            <span className="section-icon">📝</span>
            Risk Description
          </h3>
          <p className="risk-description">{risk.description}</p>
        </div>

        {/* Response Strategies */}
        <div className="risk-modal-section">
          <h3 className="section-title">
            <span className="section-icon">🛡️</span>
            Response Strategies (대응 전략)
          </h3>
          <div className="strategies-list">
            {risk.response_strategies.map((strategy, index) => (
              <div key={index} className="strategy-item">
                <div className="strategy-number">{index + 1}</div>
                <div className="strategy-text">{strategy}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="risk-modal-footer">
          <button 
            className="btn-secondary" 
            onClick={onClose}
          >
            닫기 (Close)
          </button>
          <button 
            className="btn-primary"
            onClick={() => {
              // In a real app, this might navigate to a detailed risk management page
              console.log('Export risk:', risk.id);
              alert(`Risk ${risk.id} exported to clipboard`);
            }}
          >
            Export
          </button>
        </div>
      </div>
    </div>
  );
};

export default RiskModal;
