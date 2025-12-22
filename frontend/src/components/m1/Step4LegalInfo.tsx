/**
 * STEP 4: Legal/Usage Information
 * ================================
 * Zoning, FAR, BCR information
 */

import React, { useState, useEffect } from 'react';
import { m1ApiService } from '../../services/m1.service';
import { LandUseResponse } from '../../types/m1.types';
import DataSourceBadge from '../shared/DataSourceBadge';

interface Step4Props {
  coordinates: { lat: number; lon: number };
  jimok: string;
  onNext: (data: LandUseResponse) => void;
  onBack: () => void;
  initialData?: LandUseResponse;
}

export const Step4LegalInfo: React.FC<Step4Props> = ({ coordinates, jimok, onNext, onBack, initialData }) => {
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState<'api' | 'manual'>('api');
  const [formData, setFormData] = useState({
    zone_type: initialData?.zone_type || 'general_residential',
    zone_detail: initialData?.zone_detail || '제2종일반주거지역',
    bcr: initialData?.bcr || 60,
    far: initialData?.far || 200,
    land_use: initialData?.land_use || '주거용',
    regulations: initialData?.regulations || [],
    restrictions: initialData?.restrictions || []
  });

  useEffect(() => {
    if (!initialData) {
      fetchLandUseData();
    }
  }, []);

  const fetchLandUseData = async () => {
    setLoading(true);
    const result = await m1ApiService.getLandUse(coordinates, jimok);
    setLoading(false);
    
    if (result.success) {
      setFormData({
        zone_type: result.data.zone_type,
        zone_detail: result.data.zone_detail,
        bcr: result.data.bcr,
        far: result.data.far,
        land_use: result.data.land_use,
        regulations: result.data.regulations,
        restrictions: result.data.restrictions
      });
      setDataSource('api');
    } else {
      setDataSource('manual');
    }
  };

  const handleSubmit = () => {
    const result: LandUseResponse = {
      ...formData,
      success: true
    };
    onNext(result);
  };

  return (
    <div className="step-container step4">
      <h2>법적 정보 확인</h2>
      <p className="step-description">용도지역, FAR, BCR 등을 확인하세요.</p>

      <DataSourceBadge source={dataSource} />

      <div className="form-section">
        <div className="form-row">
          <label>용도지역:</label>
          <select
            value={formData.zone_type}
            onChange={(e) => setFormData(prev => ({ ...prev, zone_type: e.target.value }))}
          >
            <option value="general_residential">일반주거지역</option>
            <option value="exclusive_residential">전용주거지역</option>
            <option value="commercial">상업지역</option>
            <option value="industrial">공업지역</option>
            <option value="green">녹지지역</option>
          </select>
        </div>
        <div className="form-row">
          <label>용도지역 상세:</label>
          <input
            type="text"
            value={formData.zone_detail}
            onChange={(e) => setFormData(prev => ({ ...prev, zone_detail: e.target.value }))}
            placeholder="제2종일반주거지역"
          />
        </div>
        <div className="form-row">
          <label>법정 건폐율 (%):</label>
          <input
            type="number"
            value={formData.bcr}
            onChange={(e) => setFormData(prev => ({ ...prev, bcr: parseFloat(e.target.value) }))}
            min="0"
            max="100"
          />
        </div>
        <div className="form-row">
          <label>법정 용적률 (%):</label>
          <input
            type="number"
            value={formData.far}
            onChange={(e) => setFormData(prev => ({ ...prev, far: parseFloat(e.target.value) }))}
            min="0"
            max="1000"
          />
        </div>
        <div className="form-row">
          <label>이용 상황:</label>
          <input
            type="text"
            value={formData.land_use}
            onChange={(e) => setFormData(prev => ({ ...prev, land_use: e.target.value }))}
            placeholder="주거용"
          />
        </div>
      </div>

      <div className="info-note">
        💡 법적 정보는 분석의 기준이 되며, 유리/불리 판단은 하지 않습니다.
      </div>

      <div className="button-group">
        <button className="btn-secondary" onClick={onBack}>이전</button>
        <button className="btn-primary" onClick={handleSubmit}>다음</button>
      </div>
    </div>
  );
};

export default Step4LegalInfo;
