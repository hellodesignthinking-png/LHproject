/**
 * M1 Land Information Landing Page - v2.1 (Phase 2)
 * ===================================================
 * 
 * NEW: "Land Fact Confirmation" Architecture
 * 
 * Architecture (6 Steps):
 * - STEP 0: Start Screen
 * - STEP 1: Address Search
 * - STEP 2: Location Verification (Geocoding)
 * - STEP 2.5: ★ Data Collection Method Selection (NEW in Phase 2!)
 * - STEP 3: ★ Unified Review Screen (Auto Collection + Review)
 * - STEP 4: Context Freeze (불변 컨텍스트 생성)
 * 
 * Changes in v2.1 (Phase 2):
 * - Added Step 2.5: Data Collection Method Selection
 *   → User explicitly chooses: API / PDF / Manual
 * - Clearer data source tracking
 * - Explicit "confirmation" process
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 * Version: 2.1 (Phase 2)
 */

import React, { useState } from 'react';
import { M1State, M1FormData, AddressSuggestion, DataSourceInfo } from '../../types/m1.types';
import { m1ApiService } from '../../services/m1.service';
import { ProgressBar } from '../shared/ProgressBar';

// Import STEP components
import { QuickApiKeySetup, ApiKeys } from './QuickApiKeySetup'; // NEW: Quick API Key Setup (Step -1)
import Step0Start from './Step0Start';
import Step1AddressInput from './Step1AddressInput';
import Step2LocationVerification from './Step2LocationVerification';
import { Step2_5DataCollectionMethod, DataCollectionMethod } from './Step2_5DataCollectionMethod'; // NEW in Phase 2!
import { ReviewScreen } from './ReviewScreen'; // NEW: Unified review screen
import Step8ContextFreeze from './Step8ContextFreeze';

const STEP_LABELS = [
  'API 설정',      // STEP -1: API Key Setup
  '시작',          // STEP 0: Start
  '주소 입력',     // STEP 1: Address Search
  '위치 확인',     // STEP 2: Location Verification
  '수집 방법',     // STEP 2.5: Data Collection Method (NEW!)
  '데이터 검토',   // STEP 3: Unified Review
  'M1 확정',       // STEP 4: Context Freeze
];

interface M1LandingPageProps {
  onContextFreezeComplete?: (contextId: string, parcelId: string) => void;
}

export const M1LandingPage: React.FC<M1LandingPageProps> = ({ onContextFreezeComplete }) => {
  // API Keys state (stored in SessionStorage)
  const [apiKeys, setApiKeys] = useState<ApiKeys | null>(null);
  const [apiKeysConfigured, setApiKeysConfigured] = useState<boolean>(false);
  
  // NEW Phase 2: Data collection method
  const [collectionMethod, setCollectionMethod] = useState<DataCollectionMethod>(null);

  // Auto-configure Kakao API key on component mount
  React.useEffect(() => {
    const autoConfiguredKeys: ApiKeys = {
      kakao: '6ff4cfada4e33ec48b782f78858f0c39', // Pre-configured Kakao API key
    };
    sessionStorage.setItem('m1_api_keys', JSON.stringify(autoConfiguredKeys));
    setApiKeys(autoConfiguredKeys);
    setApiKeysConfigured(true);
  }, []);

  const [state, setState] = useState<M1State>({
    currentStep: 0, // Start directly at Step 0 (skip API key setup)
    formData: {
      dataSources: {},
    },
    loading: false,
    error: null,
  });

  const updateFormData = (updates: Partial<M1FormData>) => {
    setState((prev) => ({
      ...prev,
      formData: {
        ...prev.formData,
        ...updates,
      },
    }));
  };

  const goToStep = (step: number) => {
    setState((prev) => ({ ...prev, currentStep: step }));
  };

  // Handle API Key Setup (Step -1)
  const handleApiKeySetup = (keys: ApiKeys) => {
    setApiKeys(keys);
    setApiKeysConfigured(true);
    // Store in SessionStorage for use in API calls
    sessionStorage.setItem('m1_api_keys', JSON.stringify(keys));
    goToStep(0); // Go to Start screen
  };

  const handleApiKeySkip = () => {
    // Skip API setup and use mock data
    setApiKeysConfigured(false);
    sessionStorage.removeItem('m1_api_keys');
    goToStep(0); // Go to Start screen
  };

  const handleStep0Next = () => {
    goToStep(1);
  };

  const handleStep1Next = (address: AddressSuggestion) => {
    updateFormData({
      selectedAddress: address,
      dataSources: {
        ...state.formData.dataSources,
        address: {
          source: 'api',
          apiName: '행정안전부 주소정보 API',
          timestamp: new Date().toISOString(),
        },
      },
    });
    goToStep(2);
  };

  const handleStep2Next = (geocodeData: any) => {
    updateFormData({
      geocodeData,
      dataSources: {
        ...state.formData.dataSources,
        geocode: {
          source: 'api',
          apiName: 'Kakao Geocoding API',
          timestamp: new Date().toISOString(),
        },
      },
    });
    goToStep(2.5); // NEW Phase 2: Go to Data Collection Method Selection
  };

  // NEW Phase 2: Handle Data Collection Method Selection
  const handleStep2_5Next = (method: DataCollectionMethod) => {
    setCollectionMethod(method);
    console.log('🎯 Data Collection Method Selected:', method);
    goToStep(3); // Go to ReviewScreen with selected method
  };

  // NEW v2.0: Handle ReviewScreen completion with unified collected data
  const handleReviewComplete = (landBundle: any) => {
    console.log('✅ M1 v2.0: Review complete, unified data collected:', landBundle);
    
    // Store all collected data in formData
    // Map backend field names to frontend expected names
    updateFormData({
      geocodeData: {
        coordinates: landBundle.coordinates,
        sido: landBundle.sido,
        sigungu: landBundle.sigungu,
        dong: landBundle.dong,
        beopjeong_dong: landBundle.beopjeong_dong,
      } as any,
      cadastralData: {
        bonbun: landBundle.cadastral?.bonbun,
        bubun: landBundle.cadastral?.bubun,
        area: landBundle.cadastral?.area,
        jimok: landBundle.cadastral?.jimok,
      } as any,
      landUseData: {
        zone_type: landBundle.legal?.use_zone || '',  // Map use_zone to zone_type
        land_use: landBundle.cadastral?.jimok || '',  // Use jimok as land_use
        far: landBundle.legal?.floor_area_ratio || 0,  // Map floor_area_ratio to far
        bcr: landBundle.legal?.building_coverage_ratio || 0,  // Map building_coverage_ratio to bcr
        regulations: landBundle.legal?.regulations || [],
      } as any,
      roadInfoData: {
        road_contact: landBundle.road?.road_contact || '',
        road_width: landBundle.road?.road_width || 0,
        road_type: landBundle.road?.road_type || '',
      } as any,
      marketData: {
        official_land_price: landBundle.market?.official_land_price,
        official_land_price_date: landBundle.market?.official_land_price_date,
        transactions: landBundle.market?.transactions || [],
      } as any,
      // landBundle: landBundle, // Store complete bundle (not in type, skip)
      dataSources: {
        ...state.formData.dataSources,
        address: {
          source: 'mock',
          apiName: 'Mock Address Data',
          timestamp: landBundle.collection_timestamp,
        },
        geocode: {
          source: 'mock',
          apiName: 'Mock Geocode Data',
          timestamp: landBundle.collection_timestamp,
        },
        cadastral: {
          source: landBundle.cadastral?.api_result?.success ? 'api' : 'mock',
          apiName: landBundle.cadastral?.api_result?.api_name || 'Mock Data',
          timestamp: landBundle.collection_timestamp,
        },
        land_use: {
          source: landBundle.legal?.api_result?.success ? 'api' : 'mock',
          apiName: landBundle.legal?.api_result?.api_name || 'Mock Data',
          timestamp: landBundle.collection_timestamp,
        },
        road_info: {
          source: landBundle.road?.api_result?.success ? 'api' : 'mock',
          apiName: landBundle.road?.api_result?.api_name || 'Mock Data',
          timestamp: landBundle.collection_timestamp,
        },
        market_data: {
          source: landBundle.market?.api_result?.success ? 'api' : 'mock',
          apiName: landBundle.market?.api_result?.api_name || 'Mock Data',
          timestamp: landBundle.collection_timestamp,
        },
        unified_collection: {
          source: 'api',
          apiName: 'M1 Unified Data Collection API v2.0',
          timestamp: landBundle.collection_timestamp,
        },
      },
    });
    
    goToStep(4); // Go to Context Freeze (was Step 8)
  };

  const handleStep8Complete = (frozenContext: any) => {
    console.log('🎯 [M1Landing] handleStep8Complete called:', frozenContext);
    
    // 🔥 CRITICAL FIX: If pipeline callback is provided, call it immediately
    // Don't store frozenContext in state as it will render success screen
    if (onContextFreezeComplete && frozenContext.context_id && frozenContext.parcel_id) {
      console.log('✅ [M1Landing] Calling onContextFreezeComplete callback');
      console.log('📦 [M1Landing] Context ID:', frozenContext.context_id);
      console.log('📦 [M1Landing] Parcel ID:', frozenContext.parcel_id);
      
      // Call pipeline callback immediately - DO NOT update local state
      onContextFreezeComplete(frozenContext.context_id, frozenContext.parcel_id);
      
      console.log('✅ [M1Landing] Callback invoked, control passed to PipelineOrchestrator');
    } else {
      // Fallback: standalone M1 usage - store state and show success screen
      console.log('ℹ️ [M1Landing] No pipeline callback, showing standalone success');
      setState((prev) => ({
        ...prev,
        frozenContext,
      }));
      alert(`컨텍스트 확정 완료!\n컨텍스트 ID: ${frozenContext.context_id}\n\n이제 M2-M6 파이프라인으로 이동합니다.`);
    }
  };

  const renderCurrentStep = () => {
    switch (state.currentStep) {
      case -1:
        // NEW: Quick API Key Setup (Step -1)
        return (
          <QuickApiKeySetup 
            onComplete={handleApiKeySetup} 
            onSkip={handleApiKeySkip}
          />
        );

      case 0:
        return <Step0Start onStart={handleStep0Next} />;

      case 1:
        return (
          <Step1AddressInput
            onNext={handleStep1Next}
            onBack={() => goToStep(0)}
          />
        );

      case 2:
        return (
          <Step2LocationVerification
            onNext={handleStep2Next}
            onBack={() => goToStep(1)}
            address={state.formData.selectedAddress?.jibun_address || state.formData.selectedAddress?.road_address || ''}
            initialData={state.formData.selectedAddress ? {
              coordinates: {
                lat: state.formData.selectedAddress.coordinates.lat,
                lon: state.formData.selectedAddress.coordinates.lon
              },
              sido: state.formData.selectedAddress.sido,
              sigungu: state.formData.selectedAddress.sigungu,
              dong: state.formData.selectedAddress.dong,
              beopjeong_dong: state.formData.selectedAddress.dong,
              success: true
            } : undefined}
          />
        );

      case 2.5:
        // NEW Phase 2: Data Collection Method Selection
        return (
          <Step2_5DataCollectionMethod
            onNext={handleStep2_5Next}
            onBack={() => goToStep(2)}
          />
        );

      case 3:
        // NEW v2.1: Unified ReviewScreen with collection method
        // CRITICAL FIX: Use coordinates from geocodeData first, fallback to selectedAddress
        const lat = state.formData.geocodeData?.coordinates?.lat 
          || state.formData.selectedAddress?.coordinates?.lat 
          || 0;
        const lon = state.formData.geocodeData?.coordinates?.lon 
          || state.formData.selectedAddress?.coordinates?.lon 
          || 0;
        
        return (
          <ReviewScreen
            address={state.formData.selectedAddress?.jibun_address || state.formData.selectedAddress?.road_address || ''}
            lat={lat}
            lon={lon}
            collectionMethod={collectionMethod} // NEW Phase 2: Pass selected method
            onBack={() => goToStep(2.5)} // Go back to method selection
            onNext={handleReviewComplete}
          />
        );

      case 4:
        // Context Freeze (was Step 8 in v1.0)
        return (
          <Step8ContextFreeze
            formData={state.formData}
            onComplete={handleStep8Complete}
            onBack={() => goToStep(3)}
          />
        );

      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <div className="m1-landing-page" style={{ maxWidth: '900px', margin: '0 auto', padding: '20px' }}>
      <header style={{ marginBottom: '30px', textAlign: 'center' }}>
        <h1>ZeroSite M1: 토지 정보 수집</h1>
        <p style={{ color: '#666' }}>8단계 프로세스로 정확한 토지 정보를 수집합니다.</p>
      </header>

      {state.currentStep > 0 && (
        <ProgressBar
          currentStep={state.currentStep}
          totalSteps={STEP_LABELS.length}
          stepLabels={STEP_LABELS}
        />
      )}

      {state.error && (
        <div
          style={{
            padding: '15px',
            marginBottom: '20px',
            background: '#fee',
            border: '1px solid #fcc',
            borderRadius: '8px',
            color: '#c33',
          }}
        >
          <strong>오류:</strong> {state.error}
        </div>
      )}

      <main>{renderCurrentStep()}</main>

      {/* 🔥 CRITICAL: Only show success box in standalone mode (no pipeline callback) */}
      {state.frozenContext && !onContextFreezeComplete && (
        <div
          style={{
            marginTop: '30px',
            padding: '20px',
            background: '#e8f5e9',
            border: '2px solid #4caf50',
            borderRadius: '8px',
          }}
        >
          <h3 style={{ marginTop: 0, color: '#2e7d32' }}>✅ 컨텍스트 확정 완료</h3>
          <p>
            <strong>컨텍스트 ID:</strong> {state.frozenContext.context_id}
          </p>
          <p>
            <strong>생성 시간:</strong>{' '}
            {new Date(state.frozenContext.created_at).toLocaleString('ko-KR')}
          </p>
          <p style={{ fontSize: '14px', color: '#555' }}>
            이 컨텍스트는 M2(용도 추천), M3(주택 유형), M4(용적 산출), M5(사업성 분석), M6(리포트 생성) 모듈에서 사용됩니다.
          </p>
        </div>
      )}
    </div>
  );
};

export default M1LandingPage;
