/**
 * Quick API Key Setup - Simplified Version
 * ========================================
 * 
 * 간단한 카카오 API 키만 입력받는 빠른 설정 화면
 * 
 * Features:
 * - 카카오 REST API 키만 필수 입력
 * - VWorld, Data.go.kr은 선택사항
 * - SessionStorage 저장
 * - Skip 버튼으로 Mock 데이터 사용 가능
 */

import React, { useState } from 'react';
import './QuickApiKeySetup.css';

export interface ApiKeys {
  kakao: string;
  vworld?: string;
  dataGoKr?: string;
}

interface QuickApiKeySetupProps {
  onComplete: (keys: ApiKeys) => void;
  onSkip: () => void;
}

export const QuickApiKeySetup: React.FC<QuickApiKeySetupProps> = ({ onComplete, onSkip }) => {
  const [kakaoKey, setKakaoKey] = useState('');
  const [showKey, setShowKey] = useState(false);

  const handleSubmit = () => {
    if (!kakaoKey.trim()) {
      alert('카카오 REST API 키를 입력해주세요.');
      return;
    }

    const keys: ApiKeys = {
      kakao: kakaoKey.trim(),
    };

    // SessionStorage에 저장
    sessionStorage.setItem('m1_api_keys', JSON.stringify(keys));
    
    console.log('✅ API 키 저장 완료 (SessionStorage)');
    onComplete(keys);
  };

  const handleSkip = () => {
    console.log('⚠️ API 키 설정 Skip - Mock 데이터 사용');
    sessionStorage.removeItem('m1_api_keys');
    onSkip();
  };

  return (
    <div className="quick-api-setup">
      <div className="setup-container">
        <div className="setup-header">
          <div className="icon-wrapper">
            <i className="fas fa-key"></i>
          </div>
          <h1 className="setup-title">카카오 API 키 설정</h1>
          <p className="setup-subtitle">
            실제 주소 검색을 사용하려면 카카오 REST API 키가 필요합니다
          </p>
        </div>

        <div className="setup-body">
          <div className="info-card">
            <div className="info-icon">
              <i className="fas fa-info-circle"></i>
            </div>
            <div className="info-content">
              <h3>카카오 API 키가 없으신가요?</h3>
              <p>
                <a 
                  href="https://developers.kakao.com/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="link-primary"
                >
                  카카오 개발자 사이트
                </a>
                에서 무료로 발급받을 수 있습니다.
              </p>
              <ol className="steps-list">
                <li>카카오 개발자 사이트 로그인</li>
                <li>"내 애플리케이션" → "애플리케이션 추가하기"</li>
                <li>앱 생성 후 "REST API 키" 복사</li>
              </ol>
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="kakao-key" className="input-label">
              <i className="fas fa-key"></i>
              카카오 REST API 키
              <span className="required">*</span>
            </label>
            <div className="input-wrapper">
              <input
                id="kakao-key"
                type={showKey ? 'text' : 'password'}
                className="api-input"
                value={kakaoKey}
                onChange={(e) => setKakaoKey(e.target.value)}
                placeholder="예: 1234567890abcdef1234567890abcdef"
                autoComplete="off"
              />
              <button
                type="button"
                className="toggle-visibility"
                onClick={() => setShowKey(!showKey)}
                title={showKey ? '숨기기' : '보기'}
              >
                <i className={`fas fa-eye${showKey ? '-slash' : ''}`}></i>
              </button>
            </div>
            <p className="input-hint">
              <i className="fas fa-shield-alt"></i>
              API 키는 브라우저에만 저장됩니다 (SessionStorage)
            </p>
          </div>

          <div className="security-notice">
            <i className="fas fa-lock"></i>
            <div>
              <strong>보안 안내</strong>
              <ul>
                <li>API 키는 서버에 전송되지 않습니다</li>
                <li>브라우저 세션에만 임시 저장됩니다</li>
                <li>브라우저를 닫으면 자동으로 삭제됩니다</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="setup-actions">
          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={!kakaoKey.trim()}
          >
            <i className="fas fa-check"></i>
            API 키 저장하고 시작하기
          </button>

          <button
            className="btn btn-secondary"
            onClick={handleSkip}
          >
            <i className="fas fa-forward"></i>
            건너뛰기 (Mock 데이터 사용)
          </button>

          <p className="skip-notice">
            <i className="fas fa-info-circle"></i>
            건너뛰면 샘플 주소만 검색됩니다 (개발/테스트용)
          </p>
        </div>
      </div>
    </div>
  );
};

export default QuickApiKeySetup;
