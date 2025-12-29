/**
 * STEP 8: Context Freeze & Pipeline Start
 * ========================================
 * 
 * - V2 API로 업그레이드 (6-category structure)
 * - 파이프라인 다이어그램 추가
 * - "분석 시작 (M1 Lock)" 개념 명확화
 */

import React, { useState } from 'react';
import { M1FormData } from '../../types/m1.types';
import { BACKEND_URL } from '../../config';

interface Step8Props {
  formData: M1FormData;
  onComplete: (frozenContext: { context_id: string; parcel_id: string }) => void;
  onBack: () => void;
}

export const Step8ContextFreeze: React.FC<Step8Props> = ({ formData, onComplete, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 🔒 VALIDATION: M1 Lock 최소 조건 체크
  const canLock = (): boolean => {
    const checks = {
      // 필수: 주소
      hasAddress: !!formData.selectedAddress?.jibun_address,
      
      // 필수: 좌표
      hasCoordinates: !!(formData.geocodeData?.coordinates.lat && 
                         formData.geocodeData?.coordinates.lon),
      
      // 필수: 지번 (본번은 필수, 부번은 선택)
      hasJibun: !!formData.cadastralData?.bonbun && formData.cadastralData.bonbun !== '',
      
      // 필수: 면적 (> 0)
      hasArea: (formData.cadastralData?.area || 0) > 0,
      
      // 필수: 지목 (비어있지 않음)
      hasJimok: !!formData.cadastralData?.jimok && formData.cadastralData.jimok !== '',
      
      // 필수: 용도지역
      hasZoning: !!formData.landUseData?.zone_type && formData.landUseData.zone_type !== '',
      
      // 필수: FAR/BCR (> 0)
      hasFAR: (formData.landUseData?.far || 0) > 0,
      hasBCR: (formData.landUseData?.bcr || 0) > 0,
      
      // 필수: 도로 폭 (> 0)
      hasRoadWidth: (formData.roadInfoData?.road_width || 0) > 0,
      
      // 필수: 공시지가 (> 0) - M2 감정평가를 위해 필수
      hasOfficialPrice: (formData.marketData?.official_land_price || 0) > 0,
    };
    
    return Object.values(checks).every(v => v === true);
  };

  const getMissingFields = (): string[] => {
    const missing: string[] = [];
    
    if (!formData.selectedAddress?.jibun_address) missing.push('주소');
    if (!formData.geocodeData?.coordinates.lat) missing.push('좌표');
    if (!formData.cadastralData?.bonbun) missing.push('본번');
    if ((formData.cadastralData?.area || 0) <= 0) missing.push('토지면적');
    if (!formData.cadastralData?.jimok) missing.push('지목');
    if (!formData.landUseData?.zone_type) missing.push('용도지역');
    if ((formData.landUseData?.far || 0) <= 0) missing.push('용적률(FAR)');
    if ((formData.landUseData?.bcr || 0) <= 0) missing.push('건폐율(BCR)');
    if ((formData.roadInfoData?.road_width || 0) <= 0) missing.push('도로 폭');
    if ((formData.marketData?.official_land_price || 0) <= 0) missing.push('공시지가');
    
    return missing;
  };

  const getDataQualityWarnings = (): string[] => {
    const warnings: string[] = [];
    
    // 공시지가 OR 거래사례 권장
    if (!formData.marketData?.official_land_price && 
        (!formData.marketData?.transactions || formData.marketData.transactions.length === 0)) {
      warnings.push('공시지가 또는 거래사례를 입력하면 더 정확한 감정평가가 가능합니다.');
    }
    
    // 거래사례 < 3건 경고
    if (formData.marketData?.transactions && formData.marketData.transactions.length > 0 && 
        formData.marketData.transactions.length < 3) {
      warnings.push(`거래사례가 ${formData.marketData.transactions.length}건으로 적습니다. 3건 이상 권장합니다.`);
    }
    
    return warnings;
  };

  // Helper function to normalize data source to uppercase
  const normalizeDataSource = (source?: string): string => {
    if (!source) return 'MANUAL';
    const normalized = source.toUpperCase();
    // Map 'MOCK' to 'MANUAL' as backend only accepts 'API' or 'MANUAL'
    if (normalized === 'MOCK' || normalized === 'PDF') return 'MANUAL';
    return normalized === 'API' ? 'API' : 'MANUAL';
  };

  const startAnalysis = async () => {
    try {
      setLoading(true);
      
      // V2 API 호출 (6-category structure)
      // CRITICAL FIX: Use coordinates from geocodeData first, fallback to selectedAddress
      const lat = formData.geocodeData?.coordinates?.lat 
        || formData.selectedAddress?.coordinates?.lat 
        || 0;
      const lon = formData.geocodeData?.coordinates?.lon 
        || formData.selectedAddress?.coordinates?.lon 
        || 0;
      
      const freezeRequestV2 = {
        // STEP 1-2: Address & Coordinates
        address: formData.selectedAddress?.jibun_address || '',
        road_address: formData.selectedAddress?.road_address || '',
        sido: formData.geocodeData?.sido || formData.selectedAddress?.sido || '',
        sigungu: formData.geocodeData?.sigungu || formData.selectedAddress?.sigungu || '',
        dong: formData.geocodeData?.dong || formData.selectedAddress?.dong || '',
        beopjeong_dong: formData.geocodeData?.beopjeong_dong || formData.selectedAddress?.dong,
        coordinates: {
          lat: lat,
          lon: lon
        },
        coordinates_verified: true,
        address_source: normalizeDataSource(formData.dataSources['address']?.source),
        coordinates_source: normalizeDataSource(formData.dataSources['geocode']?.source),
        
        // STEP 3: Cadastral
        bonbun: formData.cadastralData?.bonbun || '',
        bubun: formData.cadastralData?.bubun || '',
        jimok: formData.cadastralData?.jimok || '',  // ✅ NO DEFAULT - require explicit input
        area: formData.cadastralData?.area || 0,
        cadastral_source: normalizeDataSource(formData.dataSources['cadastral']?.source),
        cadastral_confidence: formData.dataSources['cadastral']?.confidence,
        
        // STEP 4: Zoning & Legal
        zone_type: formData.landUseData?.zone_type || '',
        zone_detail: formData.landUseData?.zone_detail,
        land_use: formData.landUseData?.land_use || '',  // ✅ NO DEFAULT - require explicit input
        far: formData.landUseData?.far || 0,
        bcr: formData.landUseData?.bcr || 0,
        height_limit: null,
        regulations: formData.landUseData?.regulations || [],
        restrictions: formData.landUseData?.restrictions || [],
        zoning_source: normalizeDataSource(formData.dataSources['land_use']?.source),
        
        // STEP 5: Road Access
        road_contact: formData.roadInfoData?.road_contact || '접도',  // TODO: Make this a required input field
        road_width: formData.roadInfoData?.road_width || 0,
        road_type: formData.roadInfoData?.road_type || '',  // ✅ NO DEFAULT - require explicit input
        nearby_roads: formData.roadInfoData?.nearby_roads?.map(r => ({
          name: r.name || '',
          width: r.width || 0,
          distance: r.distance || 0
        })) || [],
        road_source: normalizeDataSource(formData.dataSources['road_info']?.source),
        
        // STEP 6: Market Data (거래사례 분리)
        official_land_price: formData.marketData?.official_land_price,
        official_land_price_date: formData.marketData?.official_land_price_date,
        official_price_source: normalizeDataSource(formData.dataSources['market_data']?.source),
        
        // 거래사례 - appraisal용 (M2 계산용, 최대 5건)
        transaction_cases_appraisal: formData.marketData?.transactions
          ?.slice(0, 5)
          .map(tx => ({
            date: tx.date,
            area: tx.area,
            amount: tx.amount,
            distance: tx.distance,
            address: tx.address,
            use_in_calculation: true
          })) || [],
        
        // 거래사례 - reference용 (보고서 참고, 무제한)
        transaction_cases_reference: formData.marketData?.transactions || [],
        
        // Premium factors (M2 보정용)
        corner_lot: false,
        wide_road: false,
        subway_proximity: null,
        school_district: null,
        development_plan: null,
        
        // Optional: Demand inputs (M3)
        population_density: null,
        age_distribution: null,
        income_level: null,
        preferred_lh_types: [],
        
        // Optional: Financial inputs (M5)
        construction_unit_cost: null,
        linkage_available: false,
        linkage_loan_amount: null,
        linkage_interest_rate: null,
        
        // Metadata
        created_by: 'm1_user',
        data_sources: formData.dataSources
      };

      // 🔥 CRITICAL FIX: Use centralized config
      const apiUrl = `${BACKEND_URL}/api/m1/freeze-context-v2`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(freezeRequestV2)
      });
      
      if (!response.ok) {
        throw new Error('Context freeze failed');
      }

      const data = await response.json();
      console.log('📥 [Step8] Backend response:', data);
      
      // 🔥 CRITICAL FIX: Call onComplete callback BEFORE setting result
      // This ensures PipelineOrchestrator receives notification immediately
      if (onComplete && data.context_id && data.parcel_id) {
        console.log('✅ [Step8] Context frozen, calling onComplete callback');
        console.log('📦 [Step8] Context ID:', data.context_id);
        console.log('📦 [Step8] Parcel ID:', data.parcel_id);
        console.log('📞 [Step8] Calling onComplete...');
        
        // Call onComplete first to trigger pipeline
        onComplete({
          context_id: data.context_id,
          parcel_id: data.parcel_id
        });
        
        console.log('✅ [Step8] onComplete called successfully');
      } else {
        console.warn('⚠️ [Step8] onComplete callback not provided or data incomplete');
        console.log('🔍 [Step8] Debug - onComplete:', !!onComplete);
        console.log('🔍 [Step8] Debug - context_id:', data.context_id);
        console.log('🔍 [Step8] Debug - parcel_id:', data.parcel_id);
      }
      
      // Set result AFTER calling onComplete
      // This prevents the success screen from blocking the pipeline
      setResult(data);
      setError(null);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Context freeze failed');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="step-container loading">
        <div className="spinner"></div>
        <h3>🔒 분석용 컨텍스트 생성 중...</h3>
        <p>데이터를 6개 카테고리로 재정렬하고 있습니다.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="step-container error">
        <h2>⚠️ 오류 발생</h2>
        <p>{error}</p>
        <div className="button-group">
          <button onClick={onBack}>이전</button>
          <button onClick={startAnalysis}>다시 시도</button>
        </div>
      </div>
    );
  }

  if (result) {
    // 🔥 CRITICAL: Don't show success screen if onComplete was called
    // Let PipelineOrchestrator take over immediately
    if (onComplete && result.context_id && result.parcel_id) {
      console.log('🚀 [Step8] Context frozen, transitioning to pipeline...');
      return (
        <div className="step-container loading">
          <div className="spinner"></div>
          <h3>🚀 파이프라인으로 전환 중...</h3>
          <p>M2→M6 분석이 자동으로 시작됩니다.</p>
        </div>
      );
    }
    
    // Fallback: Show success screen only if no onComplete callback
    return (
      <div className="step-container step8-success">
        <div className="success-icon" style={{ fontSize: '64px', marginBottom: '20px' }}>✅</div>
        <h2>🔒 분석용 컨텍스트 확정 완료</h2>
        <p className="success-message" style={{ fontSize: '16px', color: '#4CAF50' }}>
          {result.message}
        </p>

        <div className="context-info" style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '15px',
          margin: '30px 0'
        }}>
          <div className="info-card" style={{ padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
            <h4 style={{ marginTop: 0, fontSize: '14px', color: '#666' }}>Context ID</h4>
            <p style={{ fontFamily: 'monospace', fontSize: '12px', wordBreak: 'break-all' }}>
              {result.context_id}
            </p>
          </div>
          <div className="info-card" style={{ padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
            <h4 style={{ marginTop: 0, fontSize: '14px', color: '#666' }}>Parcel ID</h4>
            <p style={{ fontFamily: 'monospace', fontSize: '12px' }}>
              {result.parcel_id}
            </p>
          </div>
          <div className="info-card" style={{ padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
            <h4 style={{ marginTop: 0, fontSize: '14px', color: '#666' }}>신뢰도 점수</h4>
            <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#4CAF50' }}>
              {(result.confidence_score * 100).toFixed(0)}%
            </p>
          </div>
          <div className="info-card" style={{ padding: '15px', background: '#e8f5e9', borderRadius: '8px' }}>
            <h4 style={{ marginTop: 0, fontSize: '14px', color: '#2e7d32' }}>상태</h4>
            <p style={{ fontSize: '18px', fontWeight: 'bold', color: '#2e7d32' }}>
              🔒 Frozen (불변)
            </p>
          </div>
        </div>

        {/* 파이프라인 다이어그램 */}
        <div style={{ 
          margin: '30px 0', 
          padding: '20px', 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '12px',
          color: 'white'
        }}>
          <h3 style={{ marginTop: 0, color: 'white' }}>📊 분석 파이프라인</h3>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '10px'
          }}>
            <div style={{ textAlign: 'center', flex: '1 1 100px' }}>
              <div style={{ fontSize: '32px' }}>✅</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>M1</div>
              <div style={{ fontSize: '11px', opacity: 0.9 }}>토지정보</div>
            </div>
            <div style={{ fontSize: '24px', opacity: 0.7 }}>→</div>
            <div style={{ textAlign: 'center', flex: '1 1 100px' }}>
              <div style={{ fontSize: '32px' }}>📈</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>M2</div>
              <div style={{ fontSize: '11px', opacity: 0.9 }}>감정평가</div>
            </div>
            <div style={{ fontSize: '24px', opacity: 0.7 }}>→</div>
            <div style={{ textAlign: 'center', flex: '1 1 100px' }}>
              <div style={{ fontSize: '32px' }}>🏠</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>M3</div>
              <div style={{ fontSize: '11px', opacity: 0.9 }}>주택유형</div>
            </div>
            <div style={{ fontSize: '24px', opacity: 0.7 }}>→</div>
            <div style={{ textAlign: 'center', flex: '1 1 100px' }}>
              <div style={{ fontSize: '32px' }}>📐</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>M4</div>
              <div style={{ fontSize: '11px', opacity: 0.9 }}>규모분석</div>
            </div>
            <div style={{ fontSize: '24px', opacity: 0.7 }}>→</div>
            <div style={{ textAlign: 'center', flex: '1 1 100px' }}>
              <div style={{ fontSize: '32px' }}>💰</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>M5</div>
              <div style={{ fontSize: '11px', opacity: 0.9 }}>사업성</div>
            </div>
            <div style={{ fontSize: '24px', opacity: 0.7 }}>→</div>
            <div style={{ textAlign: 'center', flex: '1 1 100px' }}>
              <div style={{ fontSize: '32px' }}>📄</div>
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>M6</div>
              <div style={{ fontSize: '11px', opacity: 0.9 }}>보고서</div>
            </div>
          </div>
        </div>

        {/* 불변성 안내 */}
        <div style={{ 
          padding: '20px', 
          background: '#fff3cd', 
          border: '2px solid #ffc107',
          borderRadius: '8px',
          marginBottom: '30px'
        }}>
          <h4 style={{ marginTop: 0, color: '#856404' }}>⚠️ 중요: 컨텍스트 불변성</h4>
          <ul style={{ marginBottom: 0, paddingLeft: '20px', color: '#856404' }}>
            <li>이 시점부터 M1 데이터는 <strong>변경 불가</strong>입니다.</li>
            <li>M2-M6 분석은 이 <strong>frozen context</strong>를 사용합니다.</li>
            <li>M1 화면에서 수정해도 분석 결과는 변하지 않습니다.</li>
            <li>새로운 분석이 필요하면 <strong>새로운 context</strong>를 생성하세요.</li>
          </ul>
        </div>

        {result.missing_fields && result.missing_fields.length > 0 && (
          <div style={{ 
            padding: '15px', 
            background: '#fff3cd', 
            borderRadius: '8px',
            marginBottom: '20px'
          }}>
            <h4 style={{ marginTop: 0, color: '#856404' }}>⚠️ 권장 필드 누락</h4>
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#856404' }}>
              {result.missing_fields.map((field: string, idx: number) => (
                <li key={idx}>{field}</li>
              ))}
            </ul>
            <p style={{ fontSize: '13px', marginBottom: 0, marginTop: '10px' }}>
              분석은 진행되지만, 누락된 필드를 채우면 더 정확한 결과를 얻을 수 있습니다.
            </p>
          </div>
        )}

        <div className="button-group" style={{ marginTop: '30px' }}>
          <button 
            className="btn-secondary" 
            onClick={() => window.location.reload()}
            style={{ padding: '12px 24px', fontSize: '14px' }}
          >
            다른 토지 분석
          </button>
          <button 
            className="btn-primary" 
            onClick={() => onComplete(result)}
            style={{ padding: '12px 32px', fontSize: '16px', fontWeight: 'bold' }}
          >
            M2 감정평가 시작 →
          </button>
        </div>
      </div>
    );
  }

  // Initial state - show review & confirm
  const lockEnabled = canLock();
  const missingFields = getMissingFields();
  const qualityWarnings = getDataQualityWarnings();

  return (
    <div className="step-container step8-confirm">
      <h2>📋 최종 검토 및 분석 시작</h2>
      <p>모든 데이터를 확인하셨나요? 아래 버튼을 누르면 <strong>분석용 불변 컨텍스트</strong>가 생성됩니다.</p>

      {/* 🔴 MISSING FIELDS ERROR */}
      {!lockEnabled && missingFields.length > 0 && (
        <div style={{ 
          margin: '20px 0', 
          padding: '20px', 
          background: '#fff3e0', 
          borderRadius: '8px',
          border: '2px solid #ff9800'
        }}>
          <h4 style={{ marginTop: 0, color: '#e65100' }}>❌ 필수 항목 누락</h4>
          <p style={{ marginBottom: '10px', color: '#e65100' }}>
            다음 필수 항목을 입력해야 분석을 시작할 수 있습니다:
          </p>
          <ul style={{ marginBottom: 0, paddingLeft: '20px', color: '#e65100', fontWeight: 'bold' }}>
            {missingFields.map((field, idx) => (
              <li key={idx}>{field}</li>
            ))}
          </ul>
        </div>
      )}

      {/* ⚠️ QUALITY WARNINGS */}
      {lockEnabled && qualityWarnings.length > 0 && (
        <div style={{ 
          margin: '20px 0', 
          padding: '15px', 
          background: '#fff3cd', 
          borderRadius: '8px',
          border: '1px solid #ffc107'
        }}>
          <h4 style={{ marginTop: 0, color: '#856404' }}>⚠️ 데이터 품질 권장사항</h4>
          <ul style={{ marginBottom: 0, paddingLeft: '20px', color: '#856404' }}>
            {qualityWarnings.map((warning, idx) => (
              <li key={idx}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ 
        margin: '30px 0', 
        padding: '20px', 
        background: '#f8f9fa', 
        borderRadius: '8px',
        border: '1px solid #dee2e6'
      }}>
        <h3 style={{ marginTop: 0 }}>✅ 수집된 데이터 요약</h3>
        <ul style={{ paddingLeft: '20px' }}>
          <li>주소: {formData.selectedAddress?.road_address || '(미입력)'}</li>
          <li>본번-부번: {formData.cadastralData?.bonbun || '(미입력)'}-{formData.cadastralData?.bubun || '0'}</li>
          <li>지목: {formData.cadastralData?.jimok || '(미입력)'}</li>
          <li>면적: {formData.cadastralData?.area ? `${formData.cadastralData.area}㎡ (${(formData.cadastralData.area / 3.3058).toFixed(1)}평)` : '(미입력)'}</li>
          <li>용도지역: {formData.landUseData?.zone_type || '(미입력)'}</li>
          <li>토지이용: {formData.landUseData?.land_use || '(미입력)'}</li>
          <li>용적률/건폐율: {formData.landUseData?.far || 0}% / {formData.landUseData?.bcr || 0}%</li>
          <li>도로폭: {formData.roadInfoData?.road_width || 0}m ({formData.roadInfoData?.road_type || '(미입력)'})</li>
          {formData.marketData?.official_land_price && (
            <li>공시지가: {formData.marketData.official_land_price.toLocaleString()}원/㎡</li>
          )}
          {formData.marketData?.transactions && formData.marketData.transactions.length > 0 && (
            <li>거래사례: {formData.marketData.transactions.length}건</li>
          )}
        </ul>
      </div>

      <div style={{ 
        padding: '20px', 
        background: '#e3f2fd', 
        borderRadius: '8px',
        marginBottom: '30px'
      }}>
        <h4 style={{ marginTop: 0, color: '#1976d2' }}>💡 다음 단계</h4>
        <p style={{ marginBottom: 0, color: '#1976d2' }}>
          "분석 시작" 버튼을 누르면 M2(감정평가) → M3(주택유형) → M4(규모분석) → 
          M5(사업성) → M6(보고서) 파이프라인이 순차적으로 실행됩니다.
        </p>
      </div>

      <div className="button-group">
        <button onClick={onBack} style={{ padding: '12px 24px' }}>
          이전 (재검토)
        </button>
        <button 
          onClick={startAnalysis}
          disabled={!lockEnabled}
          style={{ 
            padding: '15px 40px', 
            fontSize: '18px', 
            fontWeight: 'bold',
            background: lockEnabled 
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : '#cccccc',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: lockEnabled ? 'pointer' : 'not-allowed',
            opacity: lockEnabled ? 1 : 0.6
          }}
          title={!lockEnabled ? `필수 항목 누락: ${missingFields.join(', ')}` : ''}
        >
          {lockEnabled ? '🔒 분석 시작 (M1 Lock)' : '❌ 입력 완료 필요'}
        </button>
      </div>
    </div>
  );
};

export default Step8ContextFreeze;
