/**
 * STEP 7: Comprehensive Verification
 */

import React from 'react';
import { M1FormData } from '../../types/m1.types';
import DataSourceBadge from '../shared/DataSourceBadge';

interface Step7Props {
  formData: M1FormData;
  onNext: () => void;
  onBack: () => void;
  onEdit: (step: number) => void;
}

export const Step7Verification: React.FC<Step7Props> = ({ formData, onNext, onBack, onEdit }) => {
  return (
    <div className="step-container step7">
      <h2>종합 검증</h2>
      <p className="step-description">모든 정보를 최종 확인하세요. 확정 후에는 수정할 수 없습니다.</p>

      <div className="verification-table">
        <div className="verification-section">
          <h3>주소 정보</h3>
          <div className="data-row">
            <span className="label">도로명:</span>
            <span className="value">{formData.selectedAddress?.road_address}</span>
            <DataSourceBadge source={formData.dataSources?.address?.source || 'api'} />
            <button onClick={() => onEdit(1)}>수정</button>
          </div>
        </div>

        <div className="verification-section">
          <h3>위치 정보</h3>
          <div className="data-row">
            <span className="label">좌표:</span>
            <span className="value">
              {formData.geocodeData?.coordinates.lat.toFixed(6)}, {formData.geocodeData?.coordinates.lon.toFixed(6)}
            </span>
            <DataSourceBadge source={formData.dataSources?.location?.source || 'api'} />
            <button onClick={() => onEdit(2)}>수정</button>
          </div>
          <div className="data-row">
            <span className="label">행정구역:</span>
            <span className="value">
              {formData.geocodeData?.sido} {formData.geocodeData?.sigungu} {formData.geocodeData?.dong}
            </span>
          </div>
        </div>

        <div className="verification-section">
          <h3>지번·면적</h3>
          <div className="data-row">
            <span className="label">지번:</span>
            <span className="value">{formData.cadastralData?.bonbun}-{formData.cadastralData?.bubun}</span>
            <DataSourceBadge source={formData.dataSources?.cadastral?.source || 'api'} />
            <button onClick={() => onEdit(3)}>수정</button>
          </div>
          <div className="data-row">
            <span className="label">지목:</span>
            <span className="value">{formData.cadastralData?.jimok}</span>
          </div>
          <div className="data-row">
            <span className="label">면적:</span>
            <span className="value">
              {formData.cadastralData?.area.toLocaleString()}㎡ 
              ({(formData.cadastralData?.area ? formData.cadastralData.area / 3.3058 : 0).toFixed(1)}평)
            </span>
          </div>
        </div>

        <div className="verification-section">
          <h3>법적 정보</h3>
          <div className="data-row">
            <span className="label">용도지역:</span>
            <span className="value">{formData.landUseData?.zone_detail}</span>
            <DataSourceBadge source={formData.dataSources?.landUse?.source || 'api'} />
            <button onClick={() => onEdit(4)}>수정</button>
          </div>
          <div className="data-row">
            <span className="label">건폐율:</span>
            <span className="value">{formData.landUseData?.bcr}%</span>
          </div>
          <div className="data-row">
            <span className="label">용적률:</span>
            <span className="value">{formData.landUseData?.far}%</span>
          </div>
        </div>

        <div className="verification-section">
          <h3>도로 정보</h3>
          <div className="data-row">
            <span className="label">접도:</span>
            <span className="value">{formData.roadInfoData?.road_contact === 'yes' ? 'O' : 'X'}</span>
            <DataSourceBadge source={formData.dataSources?.road?.source || 'api'} />
            <button onClick={() => onEdit(5)}>수정</button>
          </div>
          <div className="data-row">
            <span className="label">도로 폭:</span>
            <span className="value">{formData.roadInfoData?.road_width}m</span>
          </div>
        </div>
      </div>

      <div className="warning-box">
        ⚠️ 확정 후에는 정보를 수정할 수 없습니다. 모든 정보를 신중히 확인하세요.
      </div>

      <div className="button-group">
        <button className="btn-secondary" onClick={onBack}>이전</button>
        <button className="btn-primary btn-confirm" onClick={onNext}>
          모든 정보 확정
        </button>
      </div>
    </div>
  );
};

export default Step7Verification;
