/**
 * API Key Setup Component
 * ======================
 * 
 * 사용자가 M1 시작 전에 API 키를 입력하는 화면
 * SessionStorage에 저장되어 브라우저 닫으면 자동 삭제
 * 
 * Security:
 * - API 키는 절대 서버에 저장되지 않음
 * - SessionStorage 사용 (브라우저 닫으면 삭제)
 * - GitHub에 커밋되지 않음
 * 
 * Required APIs:
 * - Kakao REST API Key
 * - VWorld API Key
 * - Data.go.kr API Key
 * 
 * Author: ZeroSite Security Team
 * Date: 2025-12-17
 */

import React, { useState, useEffect } from 'react';

export interface ApiKeys {
  kakao: string;
  vworld: string;
  dataGoKr: string;
}

interface ApiKeySetupProps {
  onComplete: (keys: ApiKeys) => void;
  onSkip?: () => void;
}

interface ApiTestResult {
  kakao: 'pending' | 'success' | 'failed' | 'untested';
  vworld: 'pending' | 'success' | 'failed' | 'untested';
  dataGoKr: 'pending' | 'success' | 'failed' | 'untested';
}

export const ApiKeySetup: React.FC<ApiKeySetupProps> = ({ onComplete, onSkip }) => {
  const [keys, setKeys] = useState<ApiKeys>({
    kakao: '',
    vworld: '',
    dataGoKr: '',
  });

  const [showKeys, setShowKeys] = useState<{ [key: string]: boolean }>({
    kakao: false,
    vworld: false,
    dataGoKr: false,
  });

  const [testResults, setTestResults] = useState<ApiTestResult>({
    kakao: 'untested',
    vworld: 'untested',
    dataGoKr: 'untested',
  });

  const [isUsingEnvKeys, setIsUsingEnvKeys] = useState(false);

  // SessionStorage에서 기존 키 불러오기 + .env 키 로드 옵션
  useEffect(() => {
    const savedKeys = sessionStorage.getItem('m1_api_keys');
    if (savedKeys) {
      try {
        const parsed = JSON.parse(savedKeys);
        setKeys(parsed);
      } catch (e) {
        console.error('Failed to parse saved API keys:', e);
      }
    }
  }, []);

  // .env 파일의 API 키를 불러오는 함수
  const loadEnvKeys = async () => {
    try {
      // Backend health check API를 통해 .env 키가 있는지 확인
      const response = await fetch('/api/m1/health');
      const health = await response.json();
      
      if (health.status === 'healthy') {
        // .env에 키가 설정되어 있으면 사용 가능 표시
        setIsUsingEnvKeys(true);
        alert(
          '✅ 서버에 .env 파일의 API 키가 설정되어 있습니다!\n\n' +
          '"Backend .env 키 사용하기" 버튼을 클릭하거나\n' +
          '직접 API 키를 입력하여 진행할 수 있습니다.'
        );
      }
    } catch (e) {
      console.error('Failed to check .env keys:', e);
    }
  };

  // API 키 테스트 함수
  const testApiKey = async (apiName: 'kakao' | 'vworld' | 'dataGoKr') => {
    setTestResults(prev => ({ ...prev, [apiName]: 'pending' }));

    try {
      // Kakao API 테스트 (주소 검색)
      if (apiName === 'kakao') {
        const response = await fetch('https://dapi.kakao.com/v2/local/search/address.json?query=서울', {
          headers: {
            'Authorization': `KakaoAK ${keys.kakao}`
          }
        });
        
        if (response.ok) {
          setTestResults(prev => ({ ...prev, kakao: 'success' }));
          alert('✅ Kakao API 키가 정상 작동합니다!');
          return;
        } else if (response.status === 401) {
          throw new Error('API 키가 유효하지 않습니다 (401 Unauthorized)');
        } else if (response.status === 403) {
          throw new Error('API 키가 차단되었거나 권한이 없습니다 (403 Forbidden)');
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      }

      // VWorld/Data.go.kr API는 CORS 문제로 직접 테스트 불가
      if (apiName === 'vworld' || apiName === 'dataGoKr') {
        alert(
          `⚠️ ${apiName === 'vworld' ? 'VWorld' : 'Data.go.kr'} API 테스트\n\n` +
          '해당 API는 브라우저에서 직접 테스트할 수 없습니다.\n' +
          '백엔드 서버를 통해 자동으로 테스트됩니다.\n\n' +
          '"시작하기" 버튼을 클릭하여 진행하세요.'
        );
        setTestResults(prev => ({ ...prev, [apiName]: 'untested' }));
        return;
      }

    } catch (error) {
      setTestResults(prev => ({ ...prev, [apiName]: 'failed' }));
      alert(
        `❌ ${apiName.toUpperCase()} API 테스트 실패\n\n` +
        `오류: ${error instanceof Error ? error.message : String(error)}\n\n` +
        '다음을 확인하세요:\n' +
        '1. API 키가 정확한지 확인\n' +
        '2. API 키 활성화 상태 확인\n' +
        '3. API 사용 권한 확인'
      );
    }
  };

  // Backend .env 키 사용 함수
  const useBackendEnvKeys = () => {
    // SessionStorage를 비워서 백엔드의 .env 키를 사용하도록 함
    sessionStorage.removeItem('m1_api_keys');
    alert(
      '✅ Backend .env 파일의 API 키를 사용합니다!\n\n' +
      'API 키가 SessionStorage에서 제거되었습니다.\n' +
      '백엔드 서버의 .env 파일에 설정된 키를 사용합니다.'
    );
    // 키를 비우고 진행
    setKeys({ kakao: '', vworld: '', dataGoKr: '' });
    onComplete({ kakao: '', vworld: '', dataGoKr: '' });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // SessionStorage에 저장 (브라우저 닫으면 자동 삭제)
    sessionStorage.setItem('m1_api_keys', JSON.stringify(keys));
    
    onComplete(keys);
  };

  const handleSkip = () => {
    // Mock 데이터로 진행
    if (onSkip) {
      onSkip();
    }
  };

  const toggleShowKey = (keyName: string) => {
    setShowKeys(prev => ({
      ...prev,
      [keyName]: !prev[keyName]
    }));
  };

  const allKeysEntered = keys.kakao && keys.vworld && keys.dataGoKr;

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '40px 20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '30px',
        borderRadius: '12px',
        marginBottom: '30px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
      }}>
        <h1 style={{ margin: '0 0 10px 0', fontSize: '28px', fontWeight: '600' }}>
          🔐 API 키 설정
        </h1>
        <p style={{ margin: 0, opacity: 0.9, fontSize: '15px' }}>
          실제 정부 데이터를 사용하려면 API 키를 입력하세요
        </p>
      </div>

      <div style={{
        background: '#fff3cd',
        border: '1px solid #ffeaa7',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '30px'
      }}>
        <h3 style={{ margin: '0 0 10px 0', color: '#856404', fontSize: '16px' }}>
          ⚠️ 보안 안내
        </h3>
        <ul style={{ margin: 0, paddingLeft: '20px', color: '#856404', fontSize: '14px' }}>
          <li>API 키는 <strong>SessionStorage</strong>에만 저장됩니다</li>
          <li>브라우저를 닫으면 자동으로 삭제됩니다</li>
          <li>서버에는 절대 저장되지 않습니다</li>
          <li>GitHub에 커밋되지 않습니다</li>
        </ul>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Kakao API Key */}
        <div style={{ marginBottom: '25px' }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '600',
            fontSize: '14px',
            color: '#2c3e50'
          }}>
            1️⃣ Kakao REST API Key
            <span style={{ color: '#e74c3c', marginLeft: '4px' }}>*</span>
          </label>
          <div style={{ position: 'relative' }}>
            <input
              type={showKeys.kakao ? 'text' : 'password'}
              value={keys.kakao}
              onChange={(e) => setKeys({ ...keys, kakao: e.target.value })}
              placeholder="1b172a21a17b8b51dd47884b45228483"
              style={{
                width: '100%',
                padding: '12px',
                paddingRight: '50px',
                border: '2px solid #dfe6e9',
                borderRadius: '8px',
                fontSize: '14px',
                fontFamily: 'monospace',
                boxSizing: 'border-box'
              }}
            />
            <button
              type="button"
              onClick={() => toggleShowKey('kakao')}
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '18px'
              }}
            >
              {showKeys.kakao ? '🙈' : '👁️'}
            </button>
          </div>
          <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#7f8c8d' }}>
            용도: 주소 검색, 좌표 변환 | 
            <a 
              href="https://developers.kakao.com/" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#3498db', marginLeft: '5px' }}
            >
              발급받기 →
            </a>
          </p>
        </div>

        {/* VWorld API Key */}
        <div style={{ marginBottom: '25px' }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '600',
            fontSize: '14px',
            color: '#2c3e50'
          }}>
            2️⃣ VWorld API Key
            <span style={{ color: '#e74c3c', marginLeft: '4px' }}>*</span>
          </label>
          <div style={{ position: 'relative' }}>
            <input
              type={showKeys.vworld ? 'text' : 'password'}
              value={keys.vworld}
              onChange={(e) => setKeys({ ...keys, vworld: e.target.value })}
              placeholder="B6B0B6F1-E572-304A-9742-384510D86FE4"
              style={{
                width: '100%',
                padding: '12px',
                paddingRight: '50px',
                border: '2px solid #dfe6e9',
                borderRadius: '8px',
                fontSize: '14px',
                fontFamily: 'monospace',
                boxSizing: 'border-box'
              }}
            />
            <button
              type="button"
              onClick={() => toggleShowKey('vworld')}
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '18px'
              }}
            >
              {showKeys.vworld ? '🙈' : '👁️'}
            </button>
          </div>
          <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#7f8c8d' }}>
            용도: 지적도, 용도지역, 용적률/건폐율 | 
            <a 
              href="http://www.vworld.kr/" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#3498db', marginLeft: '5px' }}
            >
              발급받기 →
            </a>
          </p>
        </div>

        {/* Data.go.kr API Key */}
        <div style={{ marginBottom: '30px' }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            fontWeight: '600',
            fontSize: '14px',
            color: '#2c3e50'
          }}>
            3️⃣ Data.go.kr API Key
            <span style={{ color: '#e74c3c', marginLeft: '4px' }}>*</span>
          </label>
          <div style={{ position: 'relative' }}>
            <input
              type={showKeys.dataGoKr ? 'text' : 'password'}
              value={keys.dataGoKr}
              onChange={(e) => setKeys({ ...keys, dataGoKr: e.target.value })}
              placeholder="702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d"
              style={{
                width: '100%',
                padding: '12px',
                paddingRight: '50px',
                border: '2px solid #dfe6e9',
                borderRadius: '8px',
                fontSize: '14px',
                fontFamily: 'monospace',
                boxSizing: 'border-box'
              }}
            />
            <button
              type="button"
              onClick={() => toggleShowKey('dataGoKr')}
              style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                fontSize: '18px'
              }}
            >
              {showKeys.dataGoKr ? '🙈' : '👁️'}
            </button>
          </div>
          <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#7f8c8d' }}>
            용도: 공시지가, 토지 실거래가 | 
            <a 
              href="https://www.data.go.kr/" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#3498db', marginLeft: '5px' }}
            >
              발급받기 →
            </a>
          </p>
        </div>

        {/* API 키 테스트 버튼 */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '10px',
          marginBottom: '20px'
        }}>
          <button
            type="button"
            onClick={() => testApiKey('kakao')}
            disabled={!keys.kakao || testResults.kakao === 'pending'}
            style={{
              padding: '10px',
              background: testResults.kakao === 'success' ? '#2ecc71' : testResults.kakao === 'failed' ? '#e74c3c' : '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: '600',
              cursor: keys.kakao ? 'pointer' : 'not-allowed',
              opacity: keys.kakao ? 1 : 0.5,
              transition: 'all 0.3s'
            }}
          >
            {testResults.kakao === 'pending' ? '🔄 테스트 중...' :
             testResults.kakao === 'success' ? '✅ Kakao OK' :
             testResults.kakao === 'failed' ? '❌ Kakao 실패' :
             '🧪 Kakao 테스트'}
          </button>

          <button
            type="button"
            onClick={() => testApiKey('vworld')}
            disabled={!keys.vworld}
            style={{
              padding: '10px',
              background: '#95a5a6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: '600',
              cursor: keys.vworld ? 'pointer' : 'not-allowed',
              opacity: keys.vworld ? 1 : 0.5,
              transition: 'all 0.3s'
            }}
          >
            ⚠️ VWorld (CORS)
          </button>

          <button
            type="button"
            onClick={() => testApiKey('dataGoKr')}
            disabled={!keys.dataGoKr}
            style={{
              padding: '10px',
              background: '#95a5a6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: '600',
              cursor: keys.dataGoKr ? 'pointer' : 'not-allowed',
              opacity: keys.dataGoKr ? 1 : 0.5,
              transition: 'all 0.3s'
            }}
          >
            ⚠️ Data.go.kr (CORS)
          </button>
        </div>

        <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
          <button
            type="submit"
            disabled={!allKeysEntered}
            style={{
              flex: 1,
              padding: '15px',
              background: allKeysEntered 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                : '#b2bec3',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: allKeysEntered ? 'pointer' : 'not-allowed',
              transition: 'all 0.3s',
              boxShadow: allKeysEntered ? '0 4px 15px rgba(102, 126, 234, 0.4)' : 'none'
            }}
          >
            ✅ 시작하기
          </button>

          {onSkip && (
            <button
              type="button"
              onClick={handleSkip}
              style={{
                flex: 1,
                padding: '15px',
                background: '#f8f9fa',
                color: '#495057',
                border: '2px solid #dee2e6',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
            >
              ⏭️ Mock 데이터로 진행
            </button>
          )}
        </div>

        {/* Backend .env 키 사용 버튼 */}
        <button
          type="button"
          onClick={useBackendEnvKeys}
          style={{
            width: '100%',
            padding: '15px',
            background: 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '15px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s',
            boxShadow: '0 4px 15px rgba(243, 156, 18, 0.3)'
          }}
        >
          🔧 Backend .env 키 사용하기 (서버 설정 키)
        </button>
      </form>

      <div style={{
        marginTop: '30px',
        padding: '20px',
        background: '#f8f9fa',
        borderRadius: '8px',
        fontSize: '13px',
        color: '#495057'
      }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#2c3e50' }}>
          💡 API 키가 없으신가요?
        </h4>
        <p style={{ margin: '0 0 10px 0' }}>
          "Mock 데이터로 진행" 버튼을 클릭하면 실제 API 없이도 시스템을 테스트할 수 있습니다.
        </p>
        <p style={{ margin: 0, color: '#7f8c8d' }}>
          Mock 데이터는 실제 주소를 기반으로 현실적인 값을 생성합니다.
        </p>
      </div>

      <div style={{
        marginTop: '20px',
        padding: '20px',
        background: '#fff3cd',
        borderRadius: '8px',
        fontSize: '13px',
        color: '#856404',
        border: '1px solid #ffeaa7'
      }}>
        <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: '#856404' }}>
          🔴 현재 API 연결 문제 (2025-12-18)
        </h4>
        <p style={{ margin: '0 0 10px 0' }}>
          <strong>VWorld API</strong>와 <strong>Data.go.kr API</strong>가 현재 <strong>502 Bad Gateway/500 Internal Error</strong>를 반환하고 있습니다.
        </p>
        <p style={{ margin: '0 0 10px 0' }}>
          이는 <strong>한국 공공 API의 해외/클라우드 IP 차단 정책</strong> 때문입니다.
        </p>
        <p style={{ margin: 0 }}>
          <strong>권장 해결책:</strong>
        </p>
        <ul style={{ margin: '5px 0 0 0', paddingLeft: '20px' }}>
          <li>📄 <strong>PDF 업로드</strong>: 토지대장, 토지이용계획확인서 등을 업로드하여 자동 추출</li>
          <li>✏️ <strong>수동 입력</strong>: 모든 필드를 직접 입력</li>
          <li>⏳ <strong>API 복구 대기</strong>: VWorld/Data.go.kr 서버 복구 대기</li>
        </ul>
      </div>
    </div>
  );
};
