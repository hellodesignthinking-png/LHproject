/**
 * STEP 3: Cadastral Data (지적 정보)
 * =================================
 * Fetch parcel information: bonbun, bubun, jimok, area
 * Support: API fetch, PDF upload, manual input
 */

import React, { useState, useEffect } from 'react';
import { m1ApiService } from '../../services/m1.service';
import { CadastralResponse, PDFParseResponse, DataSourceInfo } from '../../types/m1.types';
import { DataSourceBadge } from '../shared/DataSourceBadge';

interface Step3Props {
  onNext: (data: CadastralResponse, source: DataSourceInfo) => void;
  onBack: () => void;
  coordinates: { lat: number; lon: number };
  autoFetch?: boolean;
}

export const Step3CadastralData: React.FC<Step3Props> = ({
  onNext,
  onBack,
  coordinates,
  autoFetch = true,
}) => {
  const [loading, setLoading] = useState(false);
  const [cadastralData, setCadastralData] = useState<CadastralResponse | null>(null);
  const [manualMode, setManualMode] = useState(false);
  const [uploadMode, setUploadMode] = useState(false);
  const [dataSource, setDataSource] = useState<DataSourceInfo | null>(null);

  // Manual input fields
  const [bonbun, setBonbun] = useState('');
  const [bubun, setBubun] = useState('');
  const [jimok, setJimok] = useState('대지');
  const [area, setArea] = useState('');

  // Auto-fetch on mount
  useEffect(() => {
    if (autoFetch && coordinates) {
      fetchCadastralData();
    }
  }, [autoFetch, coordinates]);

  const [apiError, setApiError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  const fetchCadastralData = async (isRetry: boolean = false) => {
    setLoading(true);
    setApiError(null);
    
    const result = await m1ApiService.getCadastralData(coordinates);
    setLoading(false);

    if (result.success) {
      setCadastralData(result.data);
      setDataSource({
        source: 'api',
        apiName: '국토교통부 토지대장 API',
        timestamp: new Date().toISOString(),
      });
      setBonbun(result.data.bonbun);
      setBubun(result.data.bubun);
      setJimok(result.data.jimok);
      setArea(result.data.area.toString());
      setApiError(null);
      setRetryCount(0);
    } else {
      const errorMsg = result.error.detail;
      setApiError(errorMsg);
      
      // ✅ Auto-retry once (if not already retrying)
      if (!isRetry && retryCount < 1) {
        console.log('🔄 API failed, auto-retrying once...');
        setRetryCount(1);
        setTimeout(() => fetchCadastralData(true), 1000);
      } else {
        // ❌ Auto-retry failed, show bypass options
        console.error('❌ API failed after retry:', errorMsg);
      }
    }
  };

  const handlePDFUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    const result = await m1ApiService.parsePDF(file);
    setLoading(false);

    if (result.success) {
      const extracted = result.data.extracted;
      const confidence = result.data.confidence;

      if (extracted.bonbun) setBonbun(extracted.bonbun);
      if (extracted.bubun) setBubun(extracted.bubun);
      if (extracted.jimok) setJimok(extracted.jimok);
      if (extracted.area) setArea(extracted.area.toString());

      setDataSource({
        source: 'pdf',
        apiName: 'PDF OCR',
        timestamp: new Date().toISOString(),
        confidence: Object.values(confidence).reduce((a, b) => (a || 0) + (b || 0), 0) / Object.keys(confidence).length,
      });

      alert('PDF에서 지적 정보를 추출했습니다. 확인 후 진행하세요.');
    } else {
      alert('PDF 파싱 실패: ' + result.error.detail);
    }
  };

  const handleManualSubmit = () => {
    const data: CadastralResponse = {
      bonbun,
      bubun,
      jimok,
      area: parseFloat(area),
      success: true,
    };

    const source: DataSourceInfo = {
      source: 'manual',
      timestamp: new Date().toISOString(),
    };

    onNext(data, source);
  };

  const handleAutoSubmit = () => {
    if (cadastralData && dataSource) {
      const data: CadastralResponse = {
        bonbun,
        bubun,
        jimok,
        area: parseFloat(area),
        success: true,
      };
      onNext(data, dataSource);
    }
  };

  return (
    <div className="step-container">
      <h2>지적 정보 (STEP 3)</h2>
      <p>토지 지번, 지목, 면적 정보를 확인합니다.</p>

      {dataSource && <DataSourceBadge {...dataSource} />}

      {/* ❌ API FAILURE - BYPASS OPTIONS */}
      {apiError && !cadastralData && (
        <div style={{ 
          margin: '20px 0', 
          padding: '20px', 
          background: '#fff3e0', 
          borderRadius: '8px',
          border: '2px solid #ff9800'
        }}>
          <h4 style={{ marginTop: 0, color: '#e65100' }}>⚠️ API 조회 실패</h4>
          <p style={{ color: '#e65100' }}>{apiError}</p>
          <p style={{ color: '#e65100', fontWeight: 'bold' }}>
            다음 중 하나를 선택하여 진행하세요:
          </p>
          <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
            <button 
              onClick={() => fetchCadastralData()}
              style={{ 
                padding: '10px 20px', 
                background: '#2196F3', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🔄 재시도
            </button>
            <button 
              onClick={() => { setUploadMode(true); setApiError(null); }}
              style={{ 
                padding: '10px 20px', 
                background: '#FF9800', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              📄 PDF 업로드
            </button>
            <button 
              onClick={() => { setManualMode(true); setApiError(null); }}
              style={{ 
                padding: '10px 20px', 
                background: '#9C27B0', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              ✏️ 수동 입력
            </button>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setManualMode(!manualMode)}>
          {manualMode ? 'API 조회 모드' : '수동 입력 모드'}
        </button>
        <button onClick={() => setUploadMode(!uploadMode)} style={{ marginLeft: '10px' }}>
          {uploadMode ? 'PDF 업로드 취소' : 'PDF 업로드'}
        </button>
      </div>

      {uploadMode && (
        <div style={{ marginBottom: '20px', padding: '10px', border: '1px dashed #ccc' }}>
          <label>토지대장 PDF 업로드:</label>
          <input type="file" accept=".pdf" onChange={handlePDFUpload} />
        </div>
      )}

      <div className="form-group">
        <label>본번 (Bonbun)</label>
        <input
          type="text"
          value={bonbun}
          onChange={(e) => setBonbun(e.target.value)}
          placeholder="예: 10"
          disabled={!manualMode && loading}
        />
      </div>

      <div className="form-group">
        <label>부번 (Bubun)</label>
        <input
          type="text"
          value={bubun}
          onChange={(e) => setBubun(e.target.value)}
          placeholder="예: 1"
          disabled={!manualMode && loading}
        />
      </div>

      <div className="form-group">
        <label>지목 (Jimok)</label>
        <select value={jimok} onChange={(e) => setJimok(e.target.value)} disabled={!manualMode && loading}>
          <option value="대지">대지</option>
          <option value="전">전</option>
          <option value="답">답</option>
          <option value="임야">임야</option>
          <option value="기타">기타</option>
        </select>
      </div>

      <div className="form-group">
        <label>면적 (㎡)</label>
        <input
          type="number"
          value={area}
          onChange={(e) => setArea(e.target.value)}
          placeholder="예: 500.5"
          disabled={!manualMode && loading}
        />
        {area && (
          <small style={{ color: '#666' }}>
            약 {(parseFloat(area) / 3.3058).toFixed(1)}평
          </small>
        )}
      </div>

      <div className="button-group">
        <button onClick={onBack}>이전</button>
        {manualMode ? (
          <button onClick={handleManualSubmit} disabled={!bonbun || !jimok || !area}>
            다음 (수동 입력)
          </button>
        ) : (
          <button onClick={handleAutoSubmit} disabled={!cadastralData || !bonbun || !area}>
            {loading ? '조회 중...' : '다음'}
          </button>
        )}
        {!manualMode && (
          <button onClick={() => fetchCadastralData()} disabled={loading} style={{ marginLeft: '10px' }}>
            재조회
          </button>
        )}
      </div>
    </div>
  );
};

export default Step3CadastralData;
