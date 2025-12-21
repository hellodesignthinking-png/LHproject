/**
 * STEP 2: Location Verification
 * ==============================
 * Display coordinates on map and verify location
 */

import React, { useState, useEffect } from 'react';
import { m1ApiService } from '../../services/m1.service';
import { GeocodeResponse } from '../../types/m1.types';
import MapViewer from '../shared/MapViewer';
import DataSourceBadge from '../shared/DataSourceBadge';
import './Step2LocationVerification.css';

interface Step2Props {
  address: string;
  onNext: (data: GeocodeResponse) => void;
  onBack: () => void;
  initialData?: GeocodeResponse;
}

export const Step2LocationVerification: React.FC<Step2Props> = ({
  address,
  onNext,
  onBack,
  initialData
}) => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<GeocodeResponse | null>(initialData || null);
  const [manualMode, setManualMode] = useState(false);
  const [formData, setFormData] = useState({
    lat: initialData?.coordinates.lat || 37.5665,
    lon: initialData?.coordinates.lon || 126.9780,
    sido: initialData?.sido || '',
    sigungu: initialData?.sigungu || '',
    dong: initialData?.dong || ''
  });

  useEffect(() => {
    if (!initialData && address) {
      fetchGeocodeData();
    }
  }, [address]);

  const fetchGeocodeData = async () => {
    setLoading(true);
    const result = await m1ApiService.geocodeAddress(address);
    setLoading(false);
    
    if (result.success) {
      setData(result.data);
      setFormData({
        lat: result.data.coordinates.lat,
        lon: result.data.coordinates.lon,
        sido: result.data.sido,
        sigungu: result.data.sigungu,
        dong: result.data.dong
      });
    } else {
      setManualMode(true);
    }
  };

  const handleCoordinatesChange = (coords: { lat: number; lon: number }) => {
    setFormData(prev => ({ ...prev, ...coords }));
  };

  const handleSubmit = () => {
    const finalData: GeocodeResponse = {
      coordinates: { lat: formData.lat, lon: formData.lon },
      sido: formData.sido,
      sigungu: formData.sigungu,
      dong: formData.dong,
      beopjeong_dong: formData.dong,
      success: true
    };
    onNext(finalData);
  };

  if (loading) {
    return (
      <div className="step-container loading">
        <div className="spinner"></div>
        <p>위치 정보를 조회하는 중...</p>
      </div>
    );
  }

  return (
    <div className="step-container step2">
      <h2>위치 확인</h2>
      <p className="step-description">지도에서 위치를 확인하고 필요시 수정하세요.</p>

      {data && !manualMode && (
        <DataSourceBadge source="api" apiName="Kakao Geocoding" />
      )}
      {manualMode && (
        <DataSourceBadge source="manual" />
      )}

      <div className="map-section">
        <MapViewer
          coordinates={{ lat: formData.lat, lon: formData.lon }}
          layers={['roads', 'parcels']}
          markers={[{ lat: formData.lat, lon: formData.lon, label: '대상 필지' }]}
          onCoordinatesChange={handleCoordinatesChange}
        />
      </div>

      <div className="form-section">
        <div className="form-row">
          <label>위도 (Latitude):</label>
          <input
            type="number"
            step="0.000001"
            value={formData.lat}
            onChange={(e) => setFormData(prev => ({ ...prev, lat: parseFloat(e.target.value) }))}
          />
        </div>
        <div className="form-row">
          <label>경도 (Longitude):</label>
          <input
            type="number"
            step="0.000001"
            value={formData.lon}
            onChange={(e) => setFormData(prev => ({ ...prev, lon: parseFloat(e.target.value) }))}
          />
        </div>
        <div className="form-row">
          <label>시/도:</label>
          <input
            type="text"
            value={formData.sido}
            onChange={(e) => setFormData(prev => ({ ...prev, sido: e.target.value }))}
          />
        </div>
        <div className="form-row">
          <label>시/군/구:</label>
          <input
            type="text"
            value={formData.sigungu}
            onChange={(e) => setFormData(prev => ({ ...prev, sigungu: e.target.value }))}
          />
        </div>
        <div className="form-row">
          <label>읍/면/동:</label>
          <input
            type="text"
            value={formData.dong}
            onChange={(e) => setFormData(prev => ({ ...prev, dong: e.target.value }))}
          />
        </div>
      </div>

      <div className="button-group">
        <button className="btn-secondary" onClick={onBack}>이전</button>
        <button className="btn-primary" onClick={handleSubmit}>다음</button>
      </div>
    </div>
  );
};

export default Step2LocationVerification;
