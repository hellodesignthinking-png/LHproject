/**
 * M1 Data Input Form
 * ==================
 * 
 * Manual data entry form for M1 land information
 * Used when automatic data collection fails
 */

import React, { useState } from 'react';
import './M1DataInputForm.css';

interface M1FormData {
  // 기본 토지 정보
  address: string;
  road_address: string;
  parcel_number: string;
  area_sqm: number;
  zone_type: string;
  far: number;
  bcr: number;
  road_width: number;
  
  // 공시지가
  official_land_price: number;
  official_price_date: string;
  
  // 규제사항
  regulations: string;
  restrictions: string;
}

interface M1DataInputFormProps {
  projectId: string;
  initialAddress?: string;
  onSubmit: (data: M1FormData) => Promise<void>;
  onCancel: () => void;
}

export const M1DataInputForm: React.FC<M1DataInputFormProps> = ({
  projectId,
  initialAddress,
  onSubmit,
  onCancel
}) => {
  const [formData, setFormData] = useState<M1FormData>({
    address: initialAddress || '',
    road_address: '',
    parcel_number: '',
    area_sqm: 0,
    zone_type: '',
    far: 0,
    bcr: 0,
    road_width: 0,
    official_land_price: 0,
    official_price_date: new Date().toISOString().split('T')[0],
    regulations: '',
    restrictions: ''
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name.includes('sqm') || name.includes('far') || name.includes('bcr') || name.includes('width') || name.includes('price')
        ? parseFloat(value) || 0
        : value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.address.trim()) {
      newErrors.address = '주소를 입력해주세요';
    }
    
    if (formData.area_sqm <= 0) {
      newErrors.area_sqm = '토지 면적을 입력해주세요';
    }
    
    if (!formData.zone_type.trim()) {
      newErrors.zone_type = '용도지역을 선택해주세요';
    }
    
    if (formData.far <= 0) {
      newErrors.far = '용적률을 입력해주세요';
    }
    
    if (formData.bcr <= 0) {
      newErrors.bcr = '건폐율을 입력해주세요';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      alert('필수 항목을 모두 입력해주세요');
      return;
    }
    
    try {
      setLoading(true);
      await onSubmit(formData);
    } catch (err) {
      alert(err instanceof Error ? err.message : '데이터 저장에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="m1-data-input-form">
      <div className="form-header">
        <h2>📝 M1 토지 정보 수동 입력</h2>
        <p className="form-description">
          자동 수집이 불가능한 경우 아래 양식을 작성해주세요. 
          정확한 정보 입력이 분석 결과의 정확도를 높입니다.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="m1-form">
        {/* 기본 토지 정보 */}
        <section className="form-section">
          <h3>🏡 기본 토지 정보</h3>
          
          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="address" className="required">
                지번 주소 *
              </label>
              <input
                type="text"
                id="address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="예: 서울특별시 마포구 월드컵북로 120"
                className={errors.address ? 'error' : ''}
                disabled={loading}
              />
              {errors.address && <span className="error-text">{errors.address}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="road_address">
                도로명 주소
              </label>
              <input
                type="text"
                id="road_address"
                name="road_address"
                value={formData.road_address}
                onChange={handleChange}
                placeholder="예: 서울특별시 마포구 월드컵북로 240"
                disabled={loading}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="parcel_number">
                지번
              </label>
              <input
                type="text"
                id="parcel_number"
                name="parcel_number"
                value={formData.parcel_number}
                onChange={handleChange}
                placeholder="예: 120-5"
                disabled={loading}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="area_sqm" className="required">
                토지 면적 (㎡) *
              </label>
              <input
                type="number"
                id="area_sqm"
                name="area_sqm"
                value={formData.area_sqm || ''}
                onChange={handleChange}
                placeholder="예: 500"
                step="0.01"
                min="0"
                className={errors.area_sqm ? 'error' : ''}
                disabled={loading}
              />
              {formData.area_sqm > 0 && (
                <span className="help-text">
                  약 {(formData.area_sqm / 3.3058).toFixed(2)} 평
                </span>
              )}
              {errors.area_sqm && <span className="error-text">{errors.area_sqm}</span>}
            </div>
          </div>
        </section>

        {/* 용도지역 및 건축규제 */}
        <section className="form-section">
          <h3>🏗️ 용도지역 및 건축규제</h3>
          
          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="zone_type" className="required">
                용도지역 *
              </label>
              <select
                id="zone_type"
                name="zone_type"
                value={formData.zone_type}
                onChange={handleChange}
                className={errors.zone_type ? 'error' : ''}
                disabled={loading}
              >
                <option value="">선택하세요</option>
                <optgroup label="주거지역">
                  <option value="제1종전용주거지역">제1종전용주거지역</option>
                  <option value="제2종전용주거지역">제2종전용주거지역</option>
                  <option value="제1종일반주거지역">제1종일반주거지역</option>
                  <option value="제2종일반주거지역">제2종일반주거지역</option>
                  <option value="제3종일반주거지역">제3종일반주거지역</option>
                  <option value="준주거지역">준주거지역</option>
                </optgroup>
                <optgroup label="상업지역">
                  <option value="중심상업지역">중심상업지역</option>
                  <option value="일반상업지역">일반상업지역</option>
                  <option value="근린상업지역">근린상업지역</option>
                  <option value="유통상업지역">유통상업지역</option>
                </optgroup>
                <optgroup label="공업지역">
                  <option value="전용공업지역">전용공업지역</option>
                  <option value="일반공업지역">일반공업지역</option>
                  <option value="준공업지역">준공업지역</option>
                </optgroup>
                <optgroup label="녹지지역">
                  <option value="보전녹지지역">보전녹지지역</option>
                  <option value="생산녹지지역">생산녹지지역</option>
                  <option value="자연녹지지역">자연녹지지역</option>
                </optgroup>
              </select>
              {errors.zone_type && <span className="error-text">{errors.zone_type}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="far" className="required">
                용적률 (%) *
              </label>
              <input
                type="number"
                id="far"
                name="far"
                value={formData.far || ''}
                onChange={handleChange}
                placeholder="예: 250"
                step="1"
                min="0"
                max="1000"
                className={errors.far ? 'error' : ''}
                disabled={loading}
              />
              {errors.far && <span className="error-text">{errors.far}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="bcr" className="required">
                건폐율 (%) *
              </label>
              <input
                type="number"
                id="bcr"
                name="bcr"
                value={formData.bcr || ''}
                onChange={handleChange}
                placeholder="예: 60"
                step="1"
                min="0"
                max="100"
                className={errors.bcr ? 'error' : ''}
                disabled={loading}
              />
              {errors.bcr && <span className="error-text">{errors.bcr}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="road_width">
                전면도로 폭 (m)
              </label>
              <input
                type="number"
                id="road_width"
                name="road_width"
                value={formData.road_width || ''}
                onChange={handleChange}
                placeholder="예: 8"
                step="0.1"
                min="0"
                disabled={loading}
              />
            </div>
          </div>
        </section>

        {/* 공시지가 */}
        <section className="form-section">
          <h3>💰 공시지가</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="official_land_price">
                개별공시지가 (원/㎡)
              </label>
              <input
                type="number"
                id="official_land_price"
                name="official_land_price"
                value={formData.official_land_price || ''}
                onChange={handleChange}
                placeholder="예: 5000000"
                step="1000"
                min="0"
                disabled={loading}
              />
              {formData.official_land_price > 0 && formData.area_sqm > 0 && (
                <span className="help-text">
                  총 공시지가: {(formData.official_land_price * formData.area_sqm).toLocaleString()} 원
                </span>
              )}
            </div>
            
            <div className="form-group">
              <label htmlFor="official_price_date">
                기준일자
              </label>
              <input
                type="date"
                id="official_price_date"
                name="official_price_date"
                value={formData.official_price_date}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
          </div>
        </section>

        {/* 규제사항 */}
        <section className="form-section">
          <h3>📋 규제 및 제한사항</h3>
          
          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="regulations">
                규제사항
              </label>
              <textarea
                id="regulations"
                name="regulations"
                value={formData.regulations}
                onChange={handleChange}
                placeholder="예: 지구단위계획구역, 고도지구 등&#10;여러 규제사항을 쉼표(,)로 구분하여 입력하세요"
                rows={3}
                disabled={loading}
              />
              <span className="help-text">
                투기과열지구, 토지거래허가구역, 지구단위계획구역, 경관지구 등
              </span>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group full-width">
              <label htmlFor="restrictions">
                제한사항
              </label>
              <textarea
                id="restrictions"
                name="restrictions"
                value={formData.restrictions}
                onChange={handleChange}
                placeholder="예: 일조권 제한, 조망권 제한 등&#10;여러 제한사항을 쉼표(,)로 구분하여 입력하세요"
                rows={3}
                disabled={loading}
              />
              <span className="help-text">
                일조권 제한, 사선제한, 공원접촉면 제한, 층수 제한 등
              </span>
            </div>
          </div>
        </section>

        {/* 버튼 */}
        <div className="form-actions">
          <button
            type="button"
            className="btn-secondary"
            onClick={onCancel}
            disabled={loading}
          >
            취소
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
          >
            {loading ? '저장 중...' : '저장 및 검증하기'}
          </button>
        </div>

        {/* 안내사항 */}
        <div className="form-notice">
          <p>
            <strong>💡 입력 팁:</strong>
          </p>
          <ul>
            <li>토지 면적과 용적률/건폐율은 건축 규모 산정에 직접 영향을 미치므로 정확하게 입력해주세요</li>
            <li>공시지가는 실거래가 추정에 참고됩니다 (선택사항)</li>
            <li>규제사항은 LH 검토 시 고려되므로 가능한 상세히 입력해주세요</li>
            <li>불확실한 정보는 비워두시고, 확인 후 수정하실 수 있습니다</li>
          </ul>
        </div>
      </form>
    </div>
  );
};
