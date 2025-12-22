/**
 * STEP 5: Road & Access Information
 */

import React, { useState, useEffect } from 'react';
import { m1ApiService } from '../../services/m1.service';
import { RoadInfoResponse } from '../../types/m1.types';
import DataSourceBadge from '../shared/DataSourceBadge';

interface Step5Props {
  coordinates: { lat: number; lon: number };
  onNext: (data: RoadInfoResponse) => void;
  onBack: () => void;
}

export const Step5RoadAccess: React.FC<Step5Props> = ({ coordinates, onNext, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    road_width: 8.0,
    road_type: '도로',
    road_contact: 'yes'
  });

  useEffect(() => {
    fetchRoadInfo();
  }, []);

  const fetchRoadInfo = async () => {
    setLoading(true);
    const result = await m1ApiService.getRoadInfo(coordinates);
    setLoading(false);
    if (result.success) {
      setFormData({
        road_width: result.data.road_width,
        road_type: result.data.road_type,
        road_contact: result.data.road_contact
      });
    }
  };

  const handleSubmit = () => {
    onNext({
      nearby_roads: [],
      road_contact: formData.road_contact,
      road_width: formData.road_width,
      road_type: formData.road_type,
      success: true
    });
  };

  return (
    <div className="step-container">
      <h2>도로 접면 확인</h2>
      <DataSourceBadge source="api" apiName="도로정보" />
      
      <div className="form-section">
        <div className="form-row">
          <label>접도 여부:</label>
          <select value={formData.road_contact} onChange={(e) => setFormData(prev => ({ ...prev, road_contact: e.target.value }))}>
            <option value="yes">접도 O</option>
            <option value="no">접도 X</option>
            <option value="partial">일부 접도</option>
          </select>
        </div>
        <div className="form-row">
          <label>도로 폭 (m):</label>
          <input type="number" value={formData.road_width} onChange={(e) => setFormData(prev => ({ ...prev, road_width: parseFloat(e.target.value) }))} />
        </div>
        <div className="form-row">
          <label>도로 위치:</label>
          <input type="text" value={formData.road_type} onChange={(e) => setFormData(prev => ({ ...prev, road_type: e.target.value }))} />
        </div>
      </div>

      <div className="button-group">
        <button className="btn-secondary" onClick={onBack}>이전</button>
        <button className="btn-primary" onClick={handleSubmit}>다음</button>
      </div>
    </div>
  );
};

export default Step5RoadAccess;
