/**
 * M1 Data Input Form
 * ==================
 * 
 * Manual data entry form for M1 land information
 * Used when automatic data collection fails
 */

import React, { useState } from 'react';
import './M1DataInputForm.css';

// 지하철역 정보
interface SubwayStation {
  name: string;
  line: string;
  distance_m: number;
  walk_time_min: number;
}

// 버스 정류장 정보
interface BusStop {
  name: string;
  distance_m: number;
  routes: string;
}

// 주변 학교 정보
interface School {
  name: string;
  type: string; // 초등학교, 중학교, 고등학교
  distance_m: number;
}

// 주변 상업시설 정보
interface Commercial {
  name: string;
  type: string; // 대형마트, 편의점, 병원 등
  distance_m: number;
}

// 거래 사례 정보
interface TransactionCase {
  date: string;
  area_sqm: number;
  amount: number;
  distance_m: number;
  address: string;
}

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
  
  // 교통 인프라
  subway_stations: SubwayStation[];
  bus_stops: BusStop[];
  
  // 주변 편의시설
  poi_schools: School[];
  poi_commercial: Commercial[];
  
  // 거래 사례
  transaction_cases: TransactionCase[];
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
    restrictions: '',
    subway_stations: [],
    bus_stops: [],
    poi_schools: [],
    poi_commercial: [],
    transaction_cases: []
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // 계산된 필드
  const area_pyeong = formData.area_sqm / 3.3058;
  const total_official_price = formData.official_land_price * formData.area_sqm;

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

        {/* 계산된 정보 요약 */}
        {formData.area_sqm > 0 && (
          <section className="form-section info-summary">
            <h3>📊 자동 계산 정보</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <span className="summary-label">토지 면적 (평)</span>
                <span className="summary-value">{area_pyeong.toFixed(2)} 평</span>
              </div>
              {formData.official_land_price > 0 && (
                <div className="summary-item">
                  <span className="summary-label">총 공시지가</span>
                  <span className="summary-value">{total_official_price.toLocaleString()} 원</span>
                </div>
              )}
              {formData.far > 0 && formData.area_sqm > 0 && (
                <div className="summary-item">
                  <span className="summary-label">최대 연면적 (용적률 기준)</span>
                  <span className="summary-value">
                    {(formData.area_sqm * formData.far / 100).toFixed(2)} ㎡
                    ({((formData.area_sqm * formData.far / 100) / 3.3058).toFixed(2)} 평)
                  </span>
                </div>
              )}
              {formData.bcr > 0 && formData.area_sqm > 0 && (
                <div className="summary-item">
                  <span className="summary-label">최대 건축면적 (건폐율 기준)</span>
                  <span className="summary-value">
                    {(formData.area_sqm * formData.bcr / 100).toFixed(2)} ㎡
                    ({((formData.area_sqm * formData.bcr / 100) / 3.3058).toFixed(2)} 평)
                  </span>
                </div>
              )}
            </div>
          </section>
        )}

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

        {/* 고급 정보 토글 버튼 */}
        <div className="advanced-toggle">
          <button
            type="button"
            className="toggle-btn"
            onClick={() => setShowAdvanced(!showAdvanced)}
            disabled={loading}
          >
            {showAdvanced ? '▼' : '▶'} 고급 정보 입력 (선택사항)
          </button>
          <p className="toggle-help">
            교통 인프라, 편의시설, 거래 사례 등 상세 정보를 입력하면 더 정확한 분석이 가능합니다.
          </p>
        </div>

        {/* 고급 정보 섹션 */}
        {showAdvanced && (
          <>
            {/* 교통 인프라 - 지하철 */}
            <section className="form-section">
              <h3>🚇 지하철역 정보</h3>
              <TransportInfoInput
                type="subway"
                items={formData.subway_stations}
                onChange={(items) => setFormData(prev => ({ ...prev, subway_stations: items }))}
                disabled={loading}
              />
            </section>

            {/* 교통 인프라 - 버스 */}
            <section className="form-section">
              <h3>🚌 버스 정류장 정보</h3>
              <TransportInfoInput
                type="bus"
                items={formData.bus_stops}
                onChange={(items) => setFormData(prev => ({ ...prev, bus_stops: items }))}
                disabled={loading}
              />
            </section>

            {/* 주변 학교 */}
            <section className="form-section">
              <h3>🏫 주변 학교</h3>
              <SchoolInfoInput
                items={formData.poi_schools}
                onChange={(items) => setFormData(prev => ({ ...prev, poi_schools: items }))}
                disabled={loading}
              />
            </section>

            {/* 주변 상업시설 */}
            <section className="form-section">
              <h3>🏪 주변 상업시설</h3>
              <CommercialInfoInput
                items={formData.poi_commercial}
                onChange={(items) => setFormData(prev => ({ ...prev, poi_commercial: items }))}
                disabled={loading}
              />
            </section>

            {/* 거래 사례 */}
            <section className="form-section">
              <h3>📈 최근 거래 사례</h3>
              <TransactionCaseInput
                items={formData.transaction_cases}
                onChange={(items) => setFormData(prev => ({ ...prev, transaction_cases: items }))}
                disabled={loading}
              />
            </section>
          </>
        )}

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

// 교통 인프라 입력 컴포넌트
interface TransportInfoInputProps {
  type: 'subway' | 'bus';
  items: SubwayStation[] | BusStop[];
  onChange: (items: any[]) => void;
  disabled: boolean;
}

const TransportInfoInput: React.FC<TransportInfoInputProps> = ({ type, items, onChange, disabled }) => {
  const addItem = () => {
    if (type === 'subway') {
      onChange([...items, { name: '', line: '', distance_m: 0, walk_time_min: 0 }]);
    } else {
      onChange([...items, { name: '', distance_m: 0, routes: '' }]);
    }
  };

  const removeItem = (index: number) => {
    onChange(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const updated = [...items];
    (updated[index] as any)[field] = value;
    onChange(updated);
  };

  return (
    <div className="dynamic-list">
      {items.map((item: any, index) => (
        <div key={index} className="dynamic-item">
          {type === 'subway' ? (
            <>
              <input
                type="text"
                placeholder="역명 (예: 홍대입구역)"
                value={item.name}
                onChange={(e) => updateItem(index, 'name', e.target.value)}
                disabled={disabled}
              />
              <input
                type="text"
                placeholder="호선 (예: 2호선)"
                value={item.line}
                onChange={(e) => updateItem(index, 'line', e.target.value)}
                disabled={disabled}
              />
              <input
                type="number"
                placeholder="거리 (m)"
                value={item.distance_m || ''}
                onChange={(e) => updateItem(index, 'distance_m', parseFloat(e.target.value) || 0)}
                disabled={disabled}
              />
              <input
                type="number"
                placeholder="도보시간 (분)"
                value={item.walk_time_min || ''}
                onChange={(e) => updateItem(index, 'walk_time_min', parseFloat(e.target.value) || 0)}
                disabled={disabled}
              />
            </>
          ) : (
            <>
              <input
                type="text"
                placeholder="정류장명"
                value={item.name}
                onChange={(e) => updateItem(index, 'name', e.target.value)}
                disabled={disabled}
              />
              <input
                type="number"
                placeholder="거리 (m)"
                value={item.distance_m || ''}
                onChange={(e) => updateItem(index, 'distance_m', parseFloat(e.target.value) || 0)}
                disabled={disabled}
              />
              <input
                type="text"
                placeholder="노선 (예: 7011, 7013)"
                value={item.routes}
                onChange={(e) => updateItem(index, 'routes', e.target.value)}
                disabled={disabled}
              />
            </>
          )}
          <button
            type="button"
            className="btn-remove"
            onClick={() => removeItem(index)}
            disabled={disabled}
          >
            ❌
          </button>
        </div>
      ))}
      <button
        type="button"
        className="btn-add"
        onClick={addItem}
        disabled={disabled}
      >
        + {type === 'subway' ? '지하철역 추가' : '버스 정류장 추가'}
      </button>
    </div>
  );
};

// 학교 정보 입력 컴포넌트
interface SchoolInfoInputProps {
  items: School[];
  onChange: (items: School[]) => void;
  disabled: boolean;
}

const SchoolInfoInput: React.FC<SchoolInfoInputProps> = ({ items, onChange, disabled }) => {
  const addItem = () => {
    onChange([...items, { name: '', type: '', distance_m: 0 }]);
  };

  const removeItem = (index: number) => {
    onChange(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const updated = [...items];
    (updated[index] as any)[field] = value;
    onChange(updated);
  };

  return (
    <div className="dynamic-list">
      {items.map((item, index) => (
        <div key={index} className="dynamic-item">
          <input
            type="text"
            placeholder="학교명"
            value={item.name}
            onChange={(e) => updateItem(index, 'name', e.target.value)}
            disabled={disabled}
          />
          <select
            value={item.type}
            onChange={(e) => updateItem(index, 'type', e.target.value)}
            disabled={disabled}
          >
            <option value="">종류 선택</option>
            <option value="초등학교">초등학교</option>
            <option value="중학교">중학교</option>
            <option value="고등학교">고등학교</option>
            <option value="대학교">대학교</option>
          </select>
          <input
            type="number"
            placeholder="거리 (m)"
            value={item.distance_m || ''}
            onChange={(e) => updateItem(index, 'distance_m', parseFloat(e.target.value) || 0)}
            disabled={disabled}
          />
          <button
            type="button"
            className="btn-remove"
            onClick={() => removeItem(index)}
            disabled={disabled}
          >
            ❌
          </button>
        </div>
      ))}
      <button
        type="button"
        className="btn-add"
        onClick={addItem}
        disabled={disabled}
      >
        + 학교 추가
      </button>
    </div>
  );
};

// 상업시설 정보 입력 컴포넌트
interface CommercialInfoInputProps {
  items: Commercial[];
  onChange: (items: Commercial[]) => void;
  disabled: boolean;
}

const CommercialInfoInput: React.FC<CommercialInfoInputProps> = ({ items, onChange, disabled }) => {
  const addItem = () => {
    onChange([...items, { name: '', type: '', distance_m: 0 }]);
  };

  const removeItem = (index: number) => {
    onChange(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const updated = [...items];
    (updated[index] as any)[field] = value;
    onChange(updated);
  };

  return (
    <div className="dynamic-list">
      {items.map((item, index) => (
        <div key={index} className="dynamic-item">
          <input
            type="text"
            placeholder="시설명"
            value={item.name}
            onChange={(e) => updateItem(index, 'name', e.target.value)}
            disabled={disabled}
          />
          <select
            value={item.type}
            onChange={(e) => updateItem(index, 'type', e.target.value)}
            disabled={disabled}
          >
            <option value="">종류 선택</option>
            <option value="대형마트">대형마트</option>
            <option value="편의점">편의점</option>
            <option value="병원">병원</option>
            <option value="약국">약국</option>
            <option value="은행">은행</option>
            <option value="우체국">우체국</option>
            <option value="공원">공원</option>
            <option value="도서관">도서관</option>
          </select>
          <input
            type="number"
            placeholder="거리 (m)"
            value={item.distance_m || ''}
            onChange={(e) => updateItem(index, 'distance_m', parseFloat(e.target.value) || 0)}
            disabled={disabled}
          />
          <button
            type="button"
            className="btn-remove"
            onClick={() => removeItem(index)}
            disabled={disabled}
          >
            ❌
          </button>
        </div>
      ))}
      <button
        type="button"
        className="btn-add"
        onClick={addItem}
        disabled={disabled}
      >
        + 상업시설 추가
      </button>
    </div>
  );
};

// 거래 사례 입력 컴포넌트
interface TransactionCaseInputProps {
  items: TransactionCase[];
  onChange: (items: TransactionCase[]) => void;
  disabled: boolean;
}

const TransactionCaseInput: React.FC<TransactionCaseInputProps> = ({ items, onChange, disabled }) => {
  const addItem = () => {
    onChange([...items, { date: new Date().toISOString().split('T')[0], area_sqm: 0, amount: 0, distance_m: 0, address: '' }]);
  };

  const removeItem = (index: number) => {
    onChange(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const updated = [...items];
    (updated[index] as any)[field] = value;
    onChange(updated);
  };

  return (
    <div className="dynamic-list transaction-list">
      {items.map((item, index) => (
        <div key={index} className="transaction-item">
          <div className="transaction-row">
            <div className="form-group">
              <label>거래일자</label>
              <input
                type="date"
                value={item.date}
                onChange={(e) => updateItem(index, 'date', e.target.value)}
                disabled={disabled}
              />
            </div>
            <div className="form-group">
              <label>면적 (㎡)</label>
              <input
                type="number"
                placeholder="예: 500"
                value={item.area_sqm || ''}
                onChange={(e) => updateItem(index, 'area_sqm', parseFloat(e.target.value) || 0)}
                disabled={disabled}
              />
            </div>
            <div className="form-group">
              <label>거래금액 (원)</label>
              <input
                type="number"
                placeholder="예: 500000000"
                value={item.amount || ''}
                onChange={(e) => updateItem(index, 'amount', parseFloat(e.target.value) || 0)}
                disabled={disabled}
              />
            </div>
          </div>
          <div className="transaction-row">
            <div className="form-group">
              <label>거리 (m)</label>
              <input
                type="number"
                placeholder="대상 토지로부터 거리"
                value={item.distance_m || ''}
                onChange={(e) => updateItem(index, 'distance_m', parseFloat(e.target.value) || 0)}
                disabled={disabled}
              />
            </div>
            <div className="form-group" style={{ flex: 2 }}>
              <label>주소</label>
              <input
                type="text"
                placeholder="거래 사례 주소"
                value={item.address}
                onChange={(e) => updateItem(index, 'address', e.target.value)}
                disabled={disabled}
              />
            </div>
            <div className="form-group" style={{ flex: 0, alignItems: 'flex-end' }}>
              <button
                type="button"
                className="btn-remove"
                onClick={() => removeItem(index)}
                disabled={disabled}
              >
                ❌ 삭제
              </button>
            </div>
          </div>
          {item.amount > 0 && item.area_sqm > 0 && (
            <div className="transaction-calc">
              평당 가격: <strong>{(item.amount / (item.area_sqm / 3.3058)).toLocaleString()}</strong> 원/평
              | ㎡당 가격: <strong>{(item.amount / item.area_sqm).toLocaleString()}</strong> 원/㎡
            </div>
          )}
        </div>
      ))}
      <button
        type="button"
        className="btn-add"
        onClick={addItem}
        disabled={disabled}
      >
        + 거래 사례 추가
      </button>
      {items.length > 0 && (
        <p className="help-text" style={{ marginTop: '1rem' }}>
          💡 최근 6개월 이내의 거래 사례를 입력하면 더 정확한 토지 가치 평가가 가능합니다.
        </p>
      )}
    </div>
  );
};
