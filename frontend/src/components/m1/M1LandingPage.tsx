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

// 🔒 EXECUTION LOCK & ATOMIC RELEASE
import { useExecutionLock } from '../../hooks/useExecutionLock';
import { useAtomicRelease } from '../../hooks/useAtomicRelease';
import { ExecutionLockOverlay } from '../shared/ExecutionLockOverlay';

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
  onContextFreezeComplete?: (contextId: string, parcelId: string, formData?: M1FormData) => void;
}

export const M1LandingPage: React.FC<M1LandingPageProps> = ({ onContextFreezeComplete }) => {
  // 🔒 EXECUTION LOCK & ATOMIC RELEASE Hooks
  const executionLock = useExecutionLock();
  const atomicRelease = useAtomicRelease();
  
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
    console.log('➡️ [M1Landing] goToStep called:', step);
    console.log('📍 [M1Landing] Current step:', state.currentStep);
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
    // 🔒 EXECUTION LOCK: Only apply if pipeline callback exists
    // Standalone M1 doesn't need execution lock
    const isPipelineMode = !!onContextFreezeComplete;
    
    if (isPipelineMode) {
      // 🔒 RULE 1: Check if execution is already locked
      if (executionLock.isLocked) {
        alert('⚠️ 분석이 이미 진행 중입니다.\n현재 분석이 완료될 때까지 기다려주세요.');
        console.warn('⚠️ EXECUTION BLOCKED: Analysis already in progress');
        return;
      }

      // Generate context_id for this new analysis
      const contextId = `CTX_${Date.now()}_${Math.random().toString(36).substring(2, 10)}`;
      
      // 🔒 RULE 1: Lock execution for new analysis
      const locked = executionLock.lockExecution(contextId);
      if (!locked) {
        alert('⚠️ 실행 잠금 실패. 다시 시도해주세요.');
        return;
      }

      console.log('🔒 EXECUTION LOCKED (Pipeline Mode):', contextId);
    } else {
      console.log('ℹ️ Standalone M1 mode - Execution lock skipped');
    }
    
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
    
    // 🔥 CRITICAL FIX: In Pipeline mode, skip Step2 (auto-populate geocode)
    if (isPipelineMode && address.coordinates) {
      console.log('🚀 [M1Landing] Pipeline mode - auto-populating geocode data');
      const autoGeocodeData = {
        coordinates: address.coordinates,
        sido: address.sido,
        sigungu: address.sigungu,
        dong: address.dong,
        beopjeong_dong: address.dong,
        success: true
      };
      
      updateFormData({
        geocodeData: autoGeocodeData,
        dataSources: {
          ...state.formData.dataSources,
          geocode: {
            source: 'api',
            apiName: 'Kakao Geocoding API (auto)',
            timestamp: new Date().toISOString(),
          },
        },
      });
      
      console.log('✅ [M1Landing] Auto geocode complete, jumping to Step 2.5');
      
      // 🔥 CRITICAL FIX: In Pipeline mode, also auto-select API collection method
      setCollectionMethod('api');
      console.log('🚀 [M1Landing] Pipeline mode - auto-selecting API collection method');
      console.log('✅ [M1Landing] Collection method set to API, jumping to Step 3');
      
      // 🔥 ULTRA FIX: In Pipeline mode, skip ReviewScreen (Step3) entirely
      // Go directly to Step4 (Context Freeze) with minimal required data
      console.log('🚀 [M1Landing] Pipeline mode - skipping ReviewScreen, jumping to Step 4');
      
      // Prepare minimal formData for Step4
      updateFormData({
        geocodeData: autoGeocodeData,
        cadastralData: {
          bonbun: address.bonbun || '',
          bubun: address.bubun || '0',
          area: 0, // Will be filled in Step4 or use mock
          jimok: '대', // Default
        } as any,
        landUseData: {
          zone_type: '제2종일반주거지역', // Default
          land_use: '주거용',
          far: 200,
          bcr: 60,
        } as any,
        roadInfoData: {
          road_width: 12,
          road_type: '일반도로',
        } as any,
        marketData: {
          official_land_price: null,
          transactions: [],
        } as any,
      });
      
      console.log('✅ [M1Landing] Minimal formData prepared, jumping to Step 4');
      goToStep(4); // Skip Step3, go directly to Context Freeze
    } else {
      goToStep(2); // Normal flow for standalone mode
    }
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
    console.log('🔍 [M1Landing] onContextFreezeComplete exists?', !!onContextFreezeComplete);
    console.log('🔍 [M1Landing] frozenContext.context_id:', frozenContext.context_id);
    console.log('🔍 [M1Landing] frozenContext.parcel_id:', frozenContext.parcel_id);
    console.log('🔍 [M1Landing] state.formData:', state.formData);
    
    const isPipelineMode = !!onContextFreezeComplete;
    
    // 🔒 Mark M1 as complete (only in pipeline mode)
    if (isPipelineMode) {
      executionLock.markModuleComplete('M1');
      console.log('✅ M1 Complete - Module marked');
    }
    
    // 🔥 CRITICAL FIX: If pipeline callback is provided, call it immediately
    // Don't store frozenContext in state as it will render success screen
    if (onContextFreezeComplete && frozenContext.context_id && frozenContext.parcel_id) {
      console.log('✅ [M1Landing] Calling onContextFreezeComplete callback (Pipeline Mode)');
      console.log('📦 [M1Landing] Context ID:', frozenContext.context_id);
      console.log('📦 [M1Landing] Parcel ID:', frozenContext.parcel_id);
      console.log('📦 [M1Landing] FormData keys:', Object.keys(state.formData || {}));
      console.log('📦 [M1Landing] FormData full:', JSON.stringify(state.formData, null, 2));
      
      // 🔥 CRITICAL: Call callback immediately - DO NOT wait or delay
      try {
        onContextFreezeComplete(frozenContext.context_id, frozenContext.parcel_id, state.formData);
        console.log('✅ [M1Landing] Callback invoked successfully');
      } catch (error) {
        console.error('❌ [M1Landing] Callback invocation failed:', error);
      }
      
      console.log('🚀 M2~M6 pipeline should now execute...');
      
      // 🔒 Safety: If pipeline doesn't respond in 5 seconds, show warning
      setTimeout(() => {
        if (executionLock.progress <= 16) { // M1 only = 16%
          console.warn('⚠️ Pipeline not responding after 5 seconds - auto unlocking');
          executionLock.unlockExecution();
          alert('⚠️ 파이프라인 연결 실패\n\nM2~M6 분석이 시작되지 않았습니다.\n페이지를 새로고침 해주세요.');
          window.location.reload();
        }
      }, 5000);
    } else {
      // Fallback: standalone M1 usage - store state and show success screen
      console.log('ℹ️ [M1Landing] Standalone M1 mode - No pipeline callback');
      setState((prev) => ({
        ...prev,
        frozenContext,
      }));
      alert(`컨텍스트 확정 완료!\n컨텍스트 ID: ${frozenContext.context_id}\n\n이제 M2-M6 파이프라인으로 이동합니다.`);
      
      // 🔒 No execution lock in standalone mode, nothing to unlock
      console.log('ℹ️ Standalone mode - No execution lock was applied');
    }
  };

  const renderCurrentStep = () => {
    console.log('🎬 [M1Landing] Rendering step:', state.currentStep);
    console.log('🎬 [M1Landing] Pipeline mode?', !!onContextFreezeComplete);
    
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
        console.log('🔒 [M1Landing] Rendering Step8ContextFreeze');
        console.log('🔒 [M1Landing] handleStep8Complete exists?', !!handleStep8Complete);
        console.log('🔒 [M1Landing] formData:', state.formData);
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
      {/* 🔒 EXECUTION LOCK OVERLAY */}
      <ExecutionLockOverlay
        isLocked={executionLock.isLocked}
        progress={executionLock.progress}
        contextId={executionLock.currentContextId}
        elapsedTime={executionLock.getElapsedTime()}
      />

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
