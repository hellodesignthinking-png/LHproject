/**
 * ExecutionLockOverlay Component
 * ================================
 * 🔒 Blocks UI when analysis is in progress
 * 
 * RULE 2: Prevent new address input until current analysis completes
 * 
 * Version: REAL APPRAISAL STANDARD v6.5 FINAL - EXECUTION LOCK
 * Date: 2025-12-29
 */

import React from 'react';
import './ExecutionLockOverlay.css';

interface ExecutionLockOverlayProps {
  isLocked: boolean;
  progress: number;
  contextId: string | null;
  elapsedTime: number;
}

export const ExecutionLockOverlay: React.FC<ExecutionLockOverlayProps> = ({
  isLocked,
  progress,
  contextId,
  elapsedTime,
}) => {
  if (!isLocked) return null;

  const formatTime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="execution-lock-overlay">
      <div className="execution-lock-content">
        <div className="lock-icon-container">
          <i className="fas fa-lock lock-icon"></i>
        </div>
        
        <h2 className="lock-title">🔄 분석이 진행 중입니다</h2>
        
        <p className="lock-message">
          잠시만 기다려 주세요.<br />
          M2~M6 전체 모듈이 완료될 때까지 새로운 주소 입력이 차단됩니다.
        </p>

        <div className="progress-section">
          <div className="progress-bar-container">
            <div 
              className="progress-bar-fill" 
              style={{ width: `${progress}%` }}
            >
              <span className="progress-text">{progress}%</span>
            </div>
          </div>
          
          <div className="progress-details">
            <div className="detail-item">
              <i className="fas fa-fingerprint"></i>
              <span>Context ID: {contextId?.substring(0, 20)}...</span>
            </div>
            <div className="detail-item">
              <i className="fas fa-clock"></i>
              <span>경과 시간: {formatTime(elapsedTime)}</span>
            </div>
          </div>
        </div>

        <div className="lock-warning">
          <i className="fas fa-info-circle"></i>
          <span>
            이 화면은 모든 모듈이 완료되면 자동으로 사라집니다.
          </span>
        </div>
      </div>
    </div>
  );
};
