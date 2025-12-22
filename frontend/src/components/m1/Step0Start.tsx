/**
 * STEP 0: Start Screen
 * ====================
 * 
 * Introduction screen for M1 land information collection
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 */

import React from 'react';
import './Step0Start.css';

interface Step0StartProps {
  onStart: () => void;
}

export const Step0Start: React.FC<Step0StartProps> = ({ onStart }) => {
  return (
    <div className="step0-container">
      <div className="step0-content">
        <div className="step0-header">
          <h1 className="step0-title">토지 기본정보 입력 (M1)</h1>
          <p className="step0-subtitle">
            주소를 기준으로 토지의 사실관계를 단계적으로 확정합니다.
          </p>
          <p className="step0-description">
            모든 정보는 <strong>공공 API 자동 조회 + 사용자 검증</strong> 방식으로 수집됩니다.
          </p>
        </div>

        <div className="info-cards">
          <div className="info-card">
            <div className="card-icon">📍</div>
            <h3 className="card-title">8단계 단계별 입력</h3>
            <p className="card-description">
              주소부터 시장 데이터까지 단계적으로 정보를 수집합니다.
            </p>
          </div>

          <div className="info-card">
            <div className="card-icon">🔍</div>
            <h3 className="card-title">자동 조회 + 사용자 검증</h3>
            <p className="card-description">
              API로 자동 조회 후 사용자가 직접 확인하고 수정할 수 있습니다.
            </p>
          </div>

          <div className="info-card">
            <div className="card-icon">🔒</div>
            <h3 className="card-title">최종 확정 후 변경 불가</h3>
            <p className="card-description">
              모든 정보 확인 후 확정하면 분석에 사용되는 기준 데이터가 됩니다.
            </p>
          </div>
        </div>

        <div className="step0-steps">
          <h3 className="steps-title">진행 단계</h3>
          <ol className="steps-list">
            <li>주소 입력 (도로명/지번)</li>
            <li>위치 확인 (지도)</li>
            <li>지번·면적 확인</li>
            <li>법적 정보 확인 (용도지역, FAR, BCR)</li>
            <li>도로 접면 확인</li>
            <li>시장 데이터 확인 (공시지가, 실거래)</li>
            <li>종합 검증</li>
            <li>정보 확정</li>
          </ol>
        </div>

        <button className="btn-start" onClick={onStart}>
          주소 입력 시작
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M7.5 15L12.5 10L7.5 5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <p className="step0-note">
          💡 입력 중 언제든지 저장되며, 새로고침해도 진행 상황이 유지됩니다.
        </p>
      </div>
    </div>
  );
};

export default Step0Start;
