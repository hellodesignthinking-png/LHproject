/**
 * STEP 3: Parcel Number & Area Confirmation
 * ==========================================
 * Cadastral data with PDF upload option
 */

import React, { useState, useEffect } from 'react';
import { m1ApiService } from '../../services/m1.service';
import { CadastralResponse, PDFParseResponse } from '../../types/m1.types';
import DataSourceBadge from '../shared/DataSourceBadge';

interface Step3Props {
  coordinates: { lat: number; lon: number };
  onNext: (data: CadastralResponse, pdfData?: any) => void;
  onBack: () => void;
  initialData?: CadastralResponse;
}

export const Step3ParcelArea: React.FC<Step3Props> = ({ coordinates, onNext, onBack, initialData }) => {
  const [loading, setLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [dataSource, setDataSource] = useState<'api' | 'manual' | 'pdf'>('api');
  const [formData, setFormData] = useState({
    bonbun: initialData?.bonbun || '',
    bubun: initialData?.bubun || '',
    jimok: initialData?.jimok || '대',
    area: initialData?.area || 0
  });
  const [pdfConfidence, setPdfConfidence] = useState<any>(null);

  useEffect(() => {
    if (!initialData) {
      fetchCadastralData();
    }
  }, []);

  const fetchCadastralData = async () => {
    setLoading(true);
    const result = await m1ApiService.getCadastralData(coordinates);
    setLoading(false);
    
    if (result.success && result.data.success) {
      setFormData({
        bonbun: result.data.bonbun,
        bubun: result.data.bubun,
        jimok: result.data.jimok,
        area: result.data.area
      });
      setDataSource('api');
    } else {
      setDataSource('manual');
    }
  };

  const handlePDFUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setPdfLoading(true);
    const result = await m1ApiService.parsePDF(file);
    setPdfLoading(false);

    if (result.success) {
      const extracted = result.data.extracted;
      setFormData({
        bonbun: extracted.bonbun || formData.bonbun,
        bubun: extracted.bubun || formData.bubun,
        jimok: extracted.jimok || formData.jimok,
        area: parseFloat(extracted.area || String(formData.area))
      });
      setPdfConfidence(result.data.confidence);
      setDataSource('pdf');
    }
  };

  const handleSubmit = () => {
    const result: CadastralResponse = {
      bonbun: formData.bonbun,
      bubun: formData.bubun,
      jimok: formData.jimok,
      area: formData.area,
      success: true
    };
    onNext(result, pdfConfidence);
  };

  return (
    <div className="step-container step3">
      <h2>지번·면적 확인</h2>
      <p className="step-description">대지의 지번과 면적을 확인하세요.</p>

      <DataSourceBadge source={dataSource} />

      {loading && <div className="loading-spinner">조회 중...</div>}

      <div className="pdf-upload-section">
        <label className="pdf-upload-btn">
          📄 토지대장 PDF 업로드
          <input type="file" accept=".pdf" onChange={handlePDFUpload} style={{ display: 'none' }} />
        </label>
        {pdfLoading && <span>PDF 분석 중...</span>}
      </div>

      <div className="form-section">
        <div className="form-row">
          <label>본번:</label>
          <input
            type="text"
            value={formData.bonbun}
            onChange={(e) => setFormData(prev => ({ ...prev, bonbun: e.target.value }))}
            placeholder="123"
          />
          {pdfConfidence?.bonbun && (
            <span className="confidence">신뢰도: {(pdfConfidence.bonbun * 100).toFixed(0)}%</span>
          )}
        </div>
        <div className="form-row">
          <label>부번:</label>
          <input
            type="text"
            value={formData.bubun}
            onChange={(e) => setFormData(prev => ({ ...prev, bubun: e.target.value }))}
            placeholder="45"
          />
        </div>
        <div className="form-row">
          <label>지목:</label>
          <select
            value={formData.jimok}
            onChange={(e) => setFormData(prev => ({ ...prev, jimok: e.target.value }))}
          >
            <option value="대">대 (垈)</option>
            <option value="전">전 (田)</option>
            <option value="답">답 (畓)</option>
            <option value="임야">임야 (林野)</option>
            <option value="잡종지">잡종지</option>
            <option value="공장용지">공장용지</option>
          </select>
        </div>
        <div className="form-row">
          <label>면적 (㎡):</label>
          <input
            type="number"
            value={formData.area}
            onChange={(e) => setFormData(prev => ({ ...prev, area: parseFloat(e.target.value) }))}
            placeholder="1000.00"
          />
          <span className="area-pyeong">≈ {(formData.area / 3.3058).toFixed(1)} 평</span>
        </div>
      </div>

      {formData.area === 0 && (
        <div className="warning-box">
          ⚠️ 면적 정보가 없습니다. 토지대장 PDF를 업로드하거나 직접 입력하세요.
        </div>
      )}

      <div className="button-group">
        <button className="btn-secondary" onClick={onBack}>이전</button>
        <button className="btn-primary" onClick={handleSubmit} disabled={!formData.bonbun || formData.area <= 0}>
          다음
        </button>
      </div>
    </div>
  );
};

export default Step3ParcelArea;
