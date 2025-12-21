/**
 * STEP 7: Review & Verify (검토 및 확인)
 * ======================================
 * Review all collected land information before freezing context
 */

import React from 'react';
import { M1FormData } from '../../types/m1.types';
import { DataSourceBadge } from '../shared/DataSourceBadge';

interface Step7Props {
  onNext: () => void;
  onBack: () => void;
  formData: M1FormData;
  onEdit: (step: number) => void;
}

export const Step7Review: React.FC<Step7Props> = ({ onNext, onBack, formData, onEdit }) => {
  const formatArea = (sqm: number): string => {
    const pyeong = sqm / 3.3058;
    return `${sqm.toLocaleString()}㎡ (${pyeong.toFixed(1)}평)`;
  };

  const formatPrice = (amount: number): string => {
    if (amount >= 100000000) {
      const eok = Math.floor(amount / 100000000);
      const man = Math.floor((amount % 100000000) / 10000);
      return man > 0 ? `${eok}억 ${man}만원` : `${eok}억원`;
    } else if (amount >= 10000) {
      return `${Math.floor(amount / 10000)}만원`;
    }
    return `${amount}원`;
  };

  return (
    <div className="step-container">
      <h2>정보 검토 (STEP 7)</h2>
      <p>수집된 모든 토지 정보를 확인하고 검토하세요.</p>

      {/* STEP 1: Address */}
      <div className="review-section" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0 }}>주소 정보</h3>
          <button onClick={() => onEdit(1)} style={{ fontSize: '12px' }}>수정</button>
        </div>
        {formData.selectedAddress && (
          <>
            <p><strong>도로명:</strong> {formData.selectedAddress.road_address}</p>
            <p><strong>지번:</strong> {formData.selectedAddress.jibun_address}</p>
            {formData.dataSources['address'] && <DataSourceBadge {...formData.dataSources['address']} />}
          </>
        )}
      </div>

      {/* STEP 2: Location */}
      <div className="review-section" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0 }}>위치 정보</h3>
          <button onClick={() => onEdit(2)} style={{ fontSize: '12px' }}>수정</button>
        </div>
        {formData.geocodeData && (
          <>
            <p><strong>좌표:</strong> ({formData.geocodeData.coordinates.lat.toFixed(6)}, {formData.geocodeData.coordinates.lon.toFixed(6)})</p>
            <p><strong>행정구역:</strong> {formData.geocodeData.sido} {formData.geocodeData.sigungu} {formData.geocodeData.dong}</p>
            {formData.dataSources['geocode'] && <DataSourceBadge {...formData.dataSources['geocode']} />}
          </>
        )}
      </div>

      {/* STEP 3: Cadastral */}
      <div className="review-section" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0 }}>지적 정보</h3>
          <button onClick={() => onEdit(3)} style={{ fontSize: '12px' }}>수정</button>
        </div>
        {formData.cadastralData && (
          <>
            <p><strong>지번:</strong> {formData.cadastralData.bonbun}-{formData.cadastralData.bubun}</p>
            <p><strong>지목:</strong> {formData.cadastralData.jimok}</p>
            <p><strong>면적:</strong> {formatArea(formData.cadastralData.area)}</p>
            {formData.dataSources['cadastral'] && <DataSourceBadge {...formData.dataSources['cadastral']} />}
          </>
        )}
      </div>

      {/* STEP 4: Land Use */}
      <div className="review-section" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0 }}>법적 정보</h3>
          <button onClick={() => onEdit(4)} style={{ fontSize: '12px' }}>수정</button>
        </div>
        {formData.landUseData && (
          <>
            <p><strong>용도지역:</strong> {formData.landUseData.zone_type}</p>
            <p><strong>용도지구:</strong> {formData.landUseData.zone_detail || 'N/A'}</p>
            <p><strong>건폐율:</strong> {formData.landUseData.bcr}%</p>
            <p><strong>용적률:</strong> {formData.landUseData.far}%</p>
            <p><strong>토지이용:</strong> {formData.landUseData.land_use}</p>
            {formData.landUseData.regulations.length > 0 && (
              <div>
                <strong>규제사항:</strong>
                <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
                  {formData.landUseData.regulations.map((reg, idx) => (
                    <li key={idx} style={{ fontSize: '14px' }}>{reg}</li>
                  ))}
                </ul>
              </div>
            )}
            {formData.dataSources['land_use'] && <DataSourceBadge {...formData.dataSources['land_use']} />}
          </>
        )}
      </div>

      {/* STEP 5: Road */}
      <div className="review-section" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0 }}>도로 정보</h3>
          <button onClick={() => onEdit(5)} style={{ fontSize: '12px' }}>수정</button>
        </div>
        {formData.roadInfoData && (
          <>
            <p><strong>접도:</strong> {formData.roadInfoData.road_contact}</p>
            <p><strong>도로폭:</strong> {formData.roadInfoData.road_width}m</p>
            <p><strong>도로유형:</strong> {formData.roadInfoData.road_type}</p>
            {formData.dataSources['road_info'] && <DataSourceBadge {...formData.dataSources['road_info']} />}
          </>
        )}
      </div>

      {/* STEP 6: Market */}
      <div className="review-section" style={{ marginBottom: '20px', padding: '15px', border: '1px solid #ddd', borderRadius: '8px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
          <h3 style={{ margin: 0 }}>시장 정보</h3>
          <button onClick={() => onEdit(6)} style={{ fontSize: '12px' }}>수정</button>
        </div>
        {formData.marketData && (
          <>
            {formData.marketData.official_land_price && (
              <p><strong>공시지가:</strong> {formatPrice(formData.marketData.official_land_price)}</p>
            )}
            <p><strong>실거래 건수:</strong> {formData.marketData.transactions.length}건</p>
            {formData.dataSources['market_data'] && <DataSourceBadge {...formData.dataSources['market_data']} />}
          </>
        )}
      </div>

      <div style={{ marginTop: '30px', padding: '15px', background: '#fff8dc', borderRadius: '8px' }}>
        <h4 style={{ marginTop: 0 }}>⚠️ 확인 사항</h4>
        <ul style={{ paddingLeft: '20px' }}>
          <li>모든 정보가 정확한지 확인하세요.</li>
          <li>다음 단계에서 데이터를 확정하면 수정할 수 없습니다.</li>
          <li>확정된 컨텍스트는 M2-M6 파이프라인에서 사용됩니다.</li>
        </ul>
      </div>

      <div className="button-group" style={{ marginTop: '20px' }}>
        <button onClick={onBack}>이전</button>
        <button onClick={onNext} style={{ background: '#28a745', color: 'white' }}>
          확정 및 다음 (STEP 8)
        </button>
      </div>
    </div>
  );
};

export default Step7Review;
