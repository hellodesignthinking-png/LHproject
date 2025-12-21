/**
 * STEP 2.5: Data Collection Method Selection
 * ===========================================
 * 
 * Critical step for M1 "Land Fact Confirmation" architecture
 * User explicitly chooses HOW to collect land data
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 * Version: M1 v2.1 (Phase 2)
 */

import React, { useState } from 'react';
import './Step2_5DataCollectionMethod.css';

export type DataCollectionMethod = 'api' | 'pdf' | 'manual' | null;

interface Step2_5Props {
  onNext: (method: DataCollectionMethod) => void;
  onBack: () => void;
}

export const Step2_5DataCollectionMethod: React.FC<Step2_5Props> = ({
  onNext,
  onBack,
}) => {
  const [selectedMethod, setSelectedMethod] = useState<DataCollectionMethod>(null);
  const [showApiKeyInfo, setShowApiKeyInfo] = useState(false);

  const handleMethodSelect = (method: DataCollectionMethod) => {
    setSelectedMethod(method);
  };

  const handleConfirm = () => {
    if (selectedMethod) {
      onNext(selectedMethod);
    }
  };

  return (
    <div className="step-container step2-5-data-collection-method">
      <div className="method-selection-header">
        <h2>🎯 토지 데이터 수집 방법 선택</h2>
        <p className="method-selection-subtitle">
          토지 정보를 어떻게 수집할지 선택해주세요
        </p>
        <div className="important-notice">
          <strong>⚠️ 중요:</strong> M1은 "토지 사실 확정 단계"입니다.
          <br />
          선택한 방법으로 수집한 데이터를 확인·수정 후 확정합니다.
        </div>
      </div>

      <div className="method-cards">
        {/* Method 1: Public API */}
        <div
          className={`method-card ${selectedMethod === 'api' ? 'selected' : ''}`}
          onClick={() => handleMethodSelect('api')}
        >
          <div className="method-icon">🌐</div>
          <h3>공공 API로 자동 수집</h3>
          <p className="method-description">
            VWorld, Data.go.kr 등 공공 API를 사용하여
            <br />
            지적, 법적, 도로, 시장 데이터를 자동 수집합니다.
          </p>
          
          <div className="method-pros">
            <h4>✅ 장점</h4>
            <ul>
              <li>가장 빠른 방법 (자동)</li>
              <li>최신 공공 데이터</li>
              <li>좌표 기반 정확한 매칭</li>
            </ul>
          </div>

          <div className="method-cons">
            <h4>⚠️ 주의사항</h4>
            <ul>
              <li>API 키 필요 (이미 입력했다면 사용)</li>
              <li>API 서버 오류 시 Mock 데이터 사용</li>
              <li>수집 후 반드시 확인 필요</li>
            </ul>
          </div>

          {selectedMethod === 'api' && (
            <div className="method-extra-info">
              <button
                className="btn-link"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowApiKeyInfo(!showApiKeyInfo);
                }}
              >
                {showApiKeyInfo ? '▼ API 키 정보 숨기기' : '▶ API 키 정보 보기'}
              </button>
              
              {showApiKeyInfo && (
                <div className="api-key-info">
                  <p><strong>필요한 API 키:</strong></p>
                  <ul>
                    <li>Kakao REST API (주소 검색)</li>
                    <li>VWorld API (지적 정보)</li>
                    <li>Data.go.kr API (법적, 시장 정보)</li>
                  </ul>
                  <p className="info-note">
                    💡 이미 Step 0에서 입력했다면 자동으로 사용됩니다.
                  </p>
                </div>
              )}
            </div>
          )}

          {selectedMethod === 'api' && (
            <div className="selection-indicator">✓ 선택됨</div>
          )}
        </div>

        {/* Method 2: PDF Upload */}
        <div
          className={`method-card ${selectedMethod === 'pdf' ? 'selected' : ''}`}
          onClick={() => handleMethodSelect('pdf')}
        >
          <div className="method-icon">📄</div>
          <h3>PDF 문서 업로드</h3>
          <p className="method-description">
            지적도, 토지이용계획확인서 등
            <br />
            PDF 문서를 업로드하여 데이터를 추출합니다.
          </p>

          <div className="method-pros">
            <h4>✅ 장점</h4>
            <ul>
              <li>기존 발급 문서 활용</li>
              <li>공식 문서 기반 (신뢰도 높음)</li>
              <li>API 키 불필요</li>
            </ul>
          </div>

          <div className="method-cons">
            <h4>⚠️ 주의사항</h4>
            <ul>
              <li>PDF 파일 준비 필요</li>
              <li>자동 인식 정확도 제한</li>
              <li>추출 후 수동 확인·수정 권장</li>
            </ul>
          </div>

          {selectedMethod === 'pdf' && (
            <div className="method-extra-info">
              <p><strong>지원 문서:</strong></p>
              <ul>
                <li>지적도 (토지대장)</li>
                <li>토지이용계획확인서</li>
                <li>부동산 거래 계약서</li>
              </ul>
            </div>
          )}

          {selectedMethod === 'pdf' && (
            <div className="selection-indicator">✓ 선택됨</div>
          )}
        </div>

        {/* Method 3: Manual Input */}
        <div
          className={`method-card ${selectedMethod === 'manual' ? 'selected' : ''}`}
          onClick={() => handleMethodSelect('manual')}
        >
          <div className="method-icon">✍️</div>
          <h3>직접 입력</h3>
          <p className="method-description">
            모든 토지 정보를
            <br />
            직접 입력합니다.
          </p>

          <div className="method-pros">
            <h4>✅ 장점</h4>
            <ul>
              <li>가장 정확한 방법 (직접 확인)</li>
              <li>외부 의존성 없음</li>
              <li>모든 필드 완전 제어</li>
            </ul>
          </div>

          <div className="method-cons">
            <h4>⚠️ 주의사항</h4>
            <ul>
              <li>시간이 가장 오래 걸림</li>
              <li>모든 필드 수동 입력 필요</li>
              <li>입력 오류 가능성</li>
            </ul>
          </div>

          {selectedMethod === 'manual' && (
            <div className="method-extra-info">
              <p><strong>입력 필요 항목 (8개):</strong></p>
              <ul>
                <li>토지 면적, 지목</li>
                <li>용도지역, 용적률, 건폐율</li>
                <li>도로 접면, 도로 폭</li>
                <li>공시지가</li>
              </ul>
            </div>
          )}

          {selectedMethod === 'manual' && (
            <div className="selection-indicator">✓ 선택됨</div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="method-selection-actions">
        <button onClick={onBack} className="btn-secondary">
          ← 뒤로 가기
        </button>
        <button
          onClick={handleConfirm}
          className="btn-primary"
          disabled={!selectedMethod}
        >
          {selectedMethod
            ? `✓ ${
                selectedMethod === 'api'
                  ? 'API 자동 수집'
                  : selectedMethod === 'pdf'
                  ? 'PDF 업로드'
                  : '직접 입력'
              } 진행`
            : '방법을 선택하세요'}
        </button>
      </div>
    </div>
  );
};
