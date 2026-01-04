/**
 * ValidationErrorModal Component
 * ================================
 * 🔒 Display validation errors when Hard Check fails
 * 
 * RULE 4: Hard Check Validation Error Display
 * 
 * Version: REAL APPRAISAL STANDARD v6.5 FINAL - EXECUTION LOCK
 * Date: 2025-12-29
 */

import React from 'react';
import './ValidationErrorModal.css';

export interface ValidationError {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

interface ValidationErrorModalProps {
  validation: ValidationError | null;
  onRetry: () => void;
  onClose: () => void;
}

export const ValidationErrorModal: React.FC<ValidationErrorModalProps> = ({
  validation,
  onRetry,
  onClose,
}) => {
  if (!validation || validation.isValid) return null;

  return (
    <div className="validation-error-overlay">
      <div className="validation-error-modal">
        {/* Header */}
        <div className="modal-header">
          <div className="error-icon">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <h2 className="modal-title">데이터 검증 실패</h2>
          <p className="modal-subtitle">
            M2~M6 모듈 간 데이터 일관성 검증에 실패했습니다.
          </p>
        </div>

        {/* Errors Section */}
        {validation.errors.length > 0 && (
          <div className="errors-section">
            <div className="section-title">
              <i className="fas fa-times-circle"></i>
              <span>오류 ({validation.errors.length})</span>
            </div>
            <ul className="error-list">
              {validation.errors.map((error, idx) => (
                <li key={idx} className="error-item">
                  <i className="fas fa-exclamation-circle"></i>
                  <span>{error}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Warnings Section */}
        {validation.warnings.length > 0 && (
          <div className="warnings-section">
            <div className="section-title">
              <i className="fas fa-exclamation-triangle"></i>
              <span>경고 ({validation.warnings.length})</span>
            </div>
            <ul className="warning-list">
              {validation.warnings.map((warning, idx) => (
                <li key={idx} className="warning-item">
                  <i className="fas fa-info-circle"></i>
                  <span>{warning}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Explanation */}
        <div className="explanation-section">
          <p className="explanation-text">
            <strong>📋 검증 항목:</strong>
          </p>
          <ul className="check-list">
            <li>✓ Context ID 일관성</li>
            <li>✓ Timestamp 일관성</li>
            <li>✓ 주소 일치</li>
            <li>✓ 데이터 논리적 연결 (M3→M4→M5)</li>
          </ul>
          <p className="explanation-note">
            위 항목 중 하나 이상이 실패하여 결과를 표시할 수 없습니다.
          </p>
        </div>

        {/* Actions */}
        <div className="modal-actions">
          <button className="btn-retry" onClick={onRetry}>
            <i className="fas fa-redo"></i>
            다시 시도
          </button>
          <button className="btn-close" onClick={onClose}>
            <i className="fas fa-times"></i>
            닫기
          </button>
        </div>

        {/* Support Info */}
        <div className="support-info">
          <i className="fas fa-question-circle"></i>
          <span>
            문제가 계속되면 관리자에게 문의해주세요.
          </span>
        </div>
      </div>
    </div>
  );
};
