/**
 * ZeroSite v4.0 Pipeline Orchestrator
 * =====================================
 * 
 * Unified component for complete M1→M6 pipeline flow
 * 
 * Flow:
 * 1. User inputs minimal data in M1 (8 steps)
 * 2. Click "분석 시작 (M1 Lock)" → Context freezes
 * 3. Automatically trigger M2→M3→M4→M5→M6 pipeline
 * 4. Display results from each module
 * 5. Generate 6 types of reports
 * 
 * Key Rules:
 * - No "next step selection" between M1-M6
 * - M4 shows BOTH alternatives (Legal/Incentive, Alt A/B) - comparison view only
 * - M6 is the FIRST decision point (GO/NO-GO)
 * - All contexts are immutable after creation
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 */

import React, { useState } from 'react';
import { M1LandingPage } from '../m1/M1LandingPage';
import { BACKEND_URL } from '../../config';
import './PipelineOrchestrator.css';

type PipelineStage = 
  | 'M1_INPUT'       // User inputs land data (8 steps)
  | 'M1_FROZEN'      // M1 context locked, ready for pipeline
  | 'PIPELINE_RUNNING'  // M2→M6 executing automatically
  | 'RESULTS_READY'     // All modules complete, show results
  | 'REPORTS_GENERATED'; // 6 reports ready for download

interface PipelineState {
  stage: PipelineStage;
  contextId: string | null;
  parcelId: string | null;
  
  // Module results
  m1Result: any | null;
  m2Result: any | null;
  m3Result: any | null;
  m4Result: any | null;
  m5Result: any | null;
  m6Result: any | null;
  
  // Pipeline execution metadata
  analysisId: string | null;
  executionTimeMs: number | null;
  
  // UI state
  loading: boolean;
  error: string | null;
}

export const PipelineOrchestrator: React.FC = () => {
  const [state, setState] = useState<PipelineState>({
    stage: 'M1_INPUT',
    contextId: null,
    parcelId: null,
    m1Result: null,
    m2Result: null,
    m3Result: null,
    m4Result: null,
    m5Result: null,
    m6Result: null,
    analysisId: null,
    executionTimeMs: null,
    loading: false,
    error: null
  });

  /**
   * Handler: M1 Context Freeze Complete
   * 
   * Triggered when user clicks "분석 시작 (M1 Lock)" in Step 8
   * 
   * Actions:
   * 1. Store frozen context_id and parcel_id
   * 2. Convert M1 formData to mock_land_data format
   * 3. Automatically trigger M2→M6 pipeline with land data
   * 4. No user interaction required until M6 decision
   */
  const handleM1FreezeComplete = async (contextId: string, parcelId: string, formData?: any) => {
    console.log('═══════════════════════════════════════════════════════');
    console.log('🚀 [PipelineOrchestrator] handleM1FreezeComplete CALLED!');
    console.log('═══════════════════════════════════════════════════════');
    console.log('🔒 M1 Context Frozen:', { contextId, parcelId });
    console.log('📦 M1 FormData received:', !!formData);
    console.log('📦 M1 FormData keys:', formData ? Object.keys(formData) : 'null');
    console.log('📦 M1 FormData full:', formData);
    console.log('⏰ Time:', new Date().toLocaleTimeString());
    
    setState(prev => ({
      ...prev,
      stage: 'M1_FROZEN',
      contextId,
      parcelId,
      loading: true,
      error: null
    }));
    
    console.log('✅ State updated to M1_FROZEN, loading=true');

    try {
      // Automatically trigger M2→M6 pipeline
      console.log('🚀 Starting automatic M2→M6 pipeline execution...');
      console.log('⏰ Time:', new Date().toLocaleTimeString());
      
      // 🔥 CRITICAL FIX: Use centralized config
      const apiUrl = `${BACKEND_URL}/api/v4/pipeline/analyze`;
      
      // 🆕 Convert M1 formData to mock_land_data format if provided
      let mock_land_data = null;
      if (formData) {
        console.log('📝 Converting M1 formData to mock_land_data...');
        mock_land_data = {
          // STEP 1-2: Address & Coordinates
          address: formData.selectedAddress?.jibun_address || '',
          road_address: formData.selectedAddress?.road_address || '',
          sido: formData.geocodeData?.sido || formData.selectedAddress?.sido || '',
          sigungu: formData.geocodeData?.sigungu || formData.selectedAddress?.sigungu || '',
          dong: formData.geocodeData?.dong || formData.selectedAddress?.dong || '',
          coordinates: {
            lat: formData.geocodeData?.coordinates?.lat || 0,
            lon: formData.geocodeData?.coordinates?.lon || 0
          },
          coordinates_verified: true,
          address_source: formData.dataSources?.address || 'API',
          coordinates_source: formData.dataSources?.geocode || 'API',
          
          // STEP 3: Cadastral
          bonbun: formData.cadastralData?.bonbun || '',
          bubun: formData.cadastralData?.bubun || '0',
          jimok: formData.cadastralData?.jimok || '',
          area: formData.cadastralData?.area || 0,
          cadastral_source: formData.dataSources?.cadastral || 'API',
          
          // STEP 4: Zoning & Legal (🔥 CRITICAL: All required fields)
          zone_type: formData.landUseData?.zone_type || '',
          zone_detail: formData.landUseData?.zone_detail || null,
          land_use: formData.landUseData?.land_use || '주거용',  // ← 필수!
          far: formData.landUseData?.far || 0,
          bcr: formData.landUseData?.bcr || 0,
          height_limit: formData.landUseData?.height_limit || null,  // ← null (not 0!)
          regulations: formData.landUseData?.regulations || [],
          restrictions: formData.landUseData?.restrictions || [],
          zoning_source: formData.dataSources?.landUse || 'API',
          
          // STEP 5: Road Access
          road_contact: '접도',
          road_width: formData.roadInfoData?.road_width || 0,
          road_type: formData.roadInfoData?.road_type || '',
          nearby_roads: formData.roadInfoData?.nearby_roads || [],
          road_source: formData.dataSources?.roadInfo || 'API',
          
          // STEP 6: Market Data
          official_land_price: formData.marketData?.official_land_price || null,
          official_land_price_date: formData.marketData?.official_land_price_date || null,
          official_price_source: formData.dataSources?.marketData || 'API',
          transaction_cases_appraisal: formData.marketData?.transactions?.slice(0, 5) || [],
          transaction_cases_reference: formData.marketData?.transactions || [],
          
          // Premium factors
          corner_lot: false,
          wide_road: false,
          
          // Metadata
          created_by: 'pipeline_user'
        };
        console.log('✅ mock_land_data prepared:', mock_land_data);
      }
      
      const requestBody = {
        parcel_id: parcelId,
        use_cache: false,
        ...(mock_land_data && { mock_land_data })
      };
      
      console.log(`📡 Calling pipeline API: ${apiUrl}`);
      console.log('📦 Request body:', requestBody);
      
      const fetchStartTime = Date.now();
      
      // 🆕 Add timeout to prevent infinite waiting (increase to 120s for full pipeline)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        console.error('⏰ REQUEST TIMEOUT after 120 seconds');
        controller.abort();
      }, 120000); // 120 second timeout for full pipeline
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId); // Clear timeout if request completes
      
      const fetchEndTime = Date.now();
      console.log(`⏱️ Fetch completed in ${fetchEndTime - fetchStartTime}ms`);
      console.log(`📥 Response status: ${response.status} ${response.statusText}`);

      if (!response.ok) {
        console.error('❌ Response not OK:', response.status, response.statusText);
        // Parse detailed error from backend
        try {
          const errorData = await response.json();
          console.error('❌ Error data from backend:', errorData);
          const errorDetail = errorData.detail || {};
          
          let errorMessage = `Pipeline execution failed: ${response.statusText}`;
          
          if (typeof errorDetail === 'object') {
            errorMessage = `❌ ${errorDetail.error || 'Unknown error'}`;
            
            if (errorDetail.missing_field) {
              errorMessage += `\n\n🔴 Missing Field: ${errorDetail.missing_field}`;
            }
            
            if (errorDetail.hint) {
              errorMessage += `\n\n💡 Hint: ${errorDetail.hint}`;
            }
          } else if (typeof errorDetail === 'string') {
            errorMessage = errorDetail;
          }
          
          console.error('❌ Final error message:', errorMessage);
          throw new Error(errorMessage);
        } catch (jsonError) {
          console.error('❌ Failed to parse error JSON:', jsonError);
          throw new Error(`Pipeline execution failed: ${response.statusText}`);
        }
      }

      console.log('📥 Parsing response JSON...');
      const parseStartTime = Date.now();
      const pipelineResult = await response.json();
      const parseEndTime = Date.now();
      console.log(`⏱️ JSON parsed in ${parseEndTime - parseStartTime}ms`);
      console.log('✅ Pipeline execution complete:', pipelineResult);

      // Extract module results
      console.log('🔍 Extracting module results...');
      const results = pipelineResult.results || {};
      console.log('📊 Results extracted:', {
        land: !!results.land,
        appraisal: !!results.appraisal,
        housing_type: !!results.housing_type,
        capacity: !!results.capacity,
        feasibility: !!results.feasibility,
        lh_review: !!results.lh_review
      });
      
      console.log('🔄 Updating state to RESULTS_READY...');
      setState(prev => ({
        ...prev,
        stage: 'RESULTS_READY',
        analysisId: pipelineResult.analysis_id,
        executionTimeMs: pipelineResult.execution_time_ms,
        m1Result: results.land,
        m2Result: results.appraisal,
        m3Result: results.housing_type,
        m4Result: results.capacity,
        m5Result: results.feasibility,
        m6Result: results.lh_review,
        loading: false
      }));
      
      console.log('✅ State updated successfully!');
      console.log('⏰ Total time:', new Date().toLocaleTimeString());

    } catch (error) {
      console.error('❌ Pipeline execution failed:', error);
      console.error('❌ Error type:', error instanceof Error ? error.constructor.name : typeof error);
      console.error('❌ Error message:', error instanceof Error ? error.message : String(error));
      
      let errorMessage = 'Pipeline execution failed';
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorMessage = '⏰ 요청 시간 초과 (30초). 네트워크 연결을 확인하거나 다시 시도해주세요.';
        } else {
          errorMessage = error.message;
        }
      }
      
      setState(prev => ({
        ...prev,
        error: errorMessage,
        stage: 'M1_FROZEN', // Stay at frozen state for retry
        loading: false // 🆕 CRITICAL: Stop loading immediately on error
      }));
    } finally {
      // ⚠️ CRITICAL: Always stop loading, even if error occurred
      console.log('🔚 Finally block: Setting loading=false');
      setState(prev => ({ ...prev, loading: false }));
    }
  };

  /**
   * Handler: Generate Reports
   * 
   * Triggered when user is satisfied with M1-M6 results
   * Generates 6 types of reports from pipeline results
   */
  const handleGenerateReports = async () => {
    if (!state.parcelId) return;

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      // 🔥 CRITICAL FIX: Use centralized config
      const apiUrl = `${BACKEND_URL}/api/v4/pipeline/reports/comprehensive`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parcel_id: state.parcelId,
          report_type: 'comprehensive',
          output_format: 'json'
        })
      });

      if (!response.ok) {
        throw new Error('Report generation failed');
      }

      const reportResult = await response.json();
      console.log('✅ Reports generated:', reportResult);

      setState(prev => ({
        ...prev,
        stage: 'REPORTS_GENERATED',
        loading: false
      }));

    } catch (error) {
      console.error('❌ Report generation failed:', error);
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Report generation failed',
        loading: false
      }));
    }
  };

  /**
   * Handler: Retry Pipeline
   */
  const handleRetryPipeline = () => {
    if (state.contextId && state.parcelId) {
      handleM1FreezeComplete(state.contextId, state.parcelId);
    }
  };

  /**
   * Handler: Start New Analysis
   */
  const handleStartNew = () => {
    setState({
      stage: 'M1_INPUT',
      contextId: null,
      parcelId: null,
      m1Result: null,
      m2Result: null,
      m3Result: null,
      m4Result: null,
      m5Result: null,
      m6Result: null,
      analysisId: null,
      executionTimeMs: null,
      loading: false,
      error: null
    });
  };

  // ========================================================================
  // RENDER: Stage-based component switching
  // ========================================================================

  return (
    <div className="pipeline-orchestrator" style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Pipeline Status Header */}
      <div style={{ 
        background: 'white', 
        padding: '20px', 
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ margin: 0, fontSize: '24px', color: '#333' }}>
            ZeroSite v4.0 - 토지 분석 파이프라인
          </h1>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '20px', 
            marginTop: '15px',
            fontSize: '14px'
          }}>
            <StageIndicator label="M1 입력" active={state.stage === 'M1_INPUT'} completed={state.stage !== 'M1_INPUT'} />
            <Arrow />
            <StageIndicator label="M1 확정" active={state.stage === 'M1_FROZEN'} completed={state.stage !== 'M1_INPUT' && state.stage !== 'M1_FROZEN'} />
            <Arrow />
            <StageIndicator label="M2-M6 분석" active={state.stage === 'PIPELINE_RUNNING'} completed={state.stage === 'RESULTS_READY' || state.stage === 'REPORTS_GENERATED'} />
            <Arrow />
            <StageIndicator label="결과 검토" active={state.stage === 'RESULTS_READY'} completed={state.stage === 'REPORTS_GENERATED'} />
            <Arrow />
            <StageIndicator label="보고서" active={state.stage === 'REPORTS_GENERATED'} />
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 20px' }}>
        
        {/* Stage 1: M1 Input (8 steps) */}
        {state.stage === 'M1_INPUT' && (
          <M1LandingPage 
            onContextFreezeComplete={(contextId: string, parcelId: string, formData?: any) => {
              handleM1FreezeComplete(contextId, parcelId, formData);
            }}
          />
        )}

        {/* Stage 2: M1 Frozen - Auto-triggering Pipeline */}
        {state.stage === 'M1_FROZEN' && (
          <div style={{ 
            padding: '60px 20px', 
            textAlign: 'center',
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            {state.loading ? (
              <>
                <div className="spinner" style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
                <h2>🚀 M2→M6 파이프라인 실행 중...</h2>
                <p style={{ fontSize: '16px', color: '#666', marginTop: '10px' }}>
                  자동으로 감정평가 → 주택유형 → 규모분석 → 사업성 → LH심사를 수행하고 있습니다.
                </p>
                <p style={{ fontSize: '14px', color: '#999', marginTop: '20px' }}>
                  Context ID: <code>{state.contextId}</code>
                </p>
              </>
            ) : state.error ? (
              <>
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
                <h2 style={{ color: '#d32f2f', marginBottom: '20px' }}>파이프라인 실행 실패</h2>
                <div style={{ 
                  background: '#fef2f2', 
                  border: '2px solid #fca5a5',
                  borderRadius: '8px',
                  padding: '20px',
                  textAlign: 'left',
                  maxWidth: '600px',
                  margin: '0 auto 30px',
                  whiteSpace: 'pre-wrap',
                  fontSize: '14px',
                  lineHeight: '1.6'
                }}>
                  {state.error}
                </div>
                <div style={{ marginTop: '30px', display: 'flex', gap: '15px', justifyContent: 'center' }}>
                  <button 
                    onClick={handleRetryPipeline} 
                    style={{ 
                      padding: '12px 24px',
                      background: '#6366f1',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                  >
                    🔄 다시 시도
                  </button>
                  <button 
                    onClick={handleStartNew} 
                    style={{ 
                      padding: '12px 24px',
                      background: '#e5e7eb',
                      color: '#374151',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                  >
                    🆕 새로운 분석 시작
                  </button>
                </div>
              </>
            ) : null}
          </div>
        )}

        {/* Stage 3: Results Ready - Display M2-M6 results */}
        {state.stage === 'RESULTS_READY' && (
          <div>
            <div style={{ 
              background: 'white', 
              padding: '30px', 
              borderRadius: '12px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              marginBottom: '20px'
            }}>
              <div style={{ textAlign: 'center', marginBottom: '30px' }}>
                <div style={{ fontSize: '64px', marginBottom: '10px' }}>✅</div>
                <h2 style={{ margin: 0, color: '#4CAF50' }}>분석 완료!</h2>
                <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>
                  실행 시간: {state.executionTimeMs ? `${(state.executionTimeMs / 1000).toFixed(1)}초` : 'N/A'}
                </p>
              </div>

              {/* Module Results Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
                
                {/* M2: Appraisal */}
                {state.m2Result && (
                  <ModuleResultCard 
                    moduleId="M2"
                    title="토지감정평가"
                    icon="💰"
                    data={state.m2Result}
                    contextId={state.contextId} 
                    keyMetrics={[
                      { 
                        label: '토지가치', 
                        value: (state.m2Result.summary?.land_value_total_krw !== undefined && state.m2Result.summary?.land_value_total_krw !== null)
                          ? `₩${state.m2Result.summary.land_value_total_krw.toLocaleString()}` 
                          : (state.m2Result.details?.appraisal?.land_value)
                          ? `₩${state.m2Result.details.appraisal.land_value.toLocaleString()}`
                          : '감정평가 필요'
                      },
                      { 
                        label: '신뢰도', 
                        value: (state.m2Result.summary?.confidence_pct !== undefined && state.m2Result.summary?.confidence_pct !== null)
                          ? `${state.m2Result.summary.confidence_pct}%` 
                          : (state.m2Result.details?.confidence?.score)
                          ? `${Math.round(state.m2Result.details.confidence.score * 100)}%`
                          : '평가 기준 적용'
                      },
                      {
                        label: '평당가격',
                        value: (state.m2Result.summary?.pyeong_price_krw !== undefined && state.m2Result.summary?.pyeong_price_krw !== null)
                          ? `₩${state.m2Result.summary.pyeong_price_krw.toLocaleString()}`
                          : (state.m2Result.details?.appraisal?.unit_price_pyeong)
                          ? `₩${state.m2Result.details.appraisal.unit_price_pyeong.toLocaleString()}`
                          : '산정 중'
                      },
                      {
                        label: '거래사례',
                        value: (state.m2Result.summary?.transaction_count !== undefined && state.m2Result.summary?.transaction_count !== null)
                          ? `${state.m2Result.summary.transaction_count}건`
                          : (state.m2Result.details?.transactions?.count !== undefined && state.m2Result.details?.transactions?.count !== null)
                          ? `${state.m2Result.details.transactions.count}건`
                          : state.m2Result.details?.transactions?.count === 0 ? '0건 (신규지역)' : '조회 중'
                      }
                    ]}
                  />
                )}

                {/* M3: Housing Type */}
                {state.m3Result && (
                  <ModuleResultCard 
                    moduleId="M3"
                    title="LH 선호유형"
                    icon="🏠"
                    data={state.m3Result}
                    contextId={state.contextId} 
                    keyMetrics={[
                      { 
                        label: '선호 구조', 
                        value: state.m3Result.summary?.recommended_type 
                          || state.m3Result.details?.recommended_type 
                          || '구조 분석 결과'
                      },
                      {
                        label: '참고 점수',
                        value: (state.m3Result.summary?.total_score !== undefined && state.m3Result.summary?.total_score !== null)
                          ? `${state.m3Result.summary.total_score}점`
                          : (state.m3Result.details?.total_score !== undefined && state.m3Result.details?.total_score !== null)
                          ? `${state.m3Result.details.total_score}점`
                          : '생활 패턴 기반'
                      },
                      {
                        label: '패턴 일치도',
                        value: (state.m3Result.summary?.confidence_pct !== undefined && state.m3Result.summary?.confidence_pct !== null)
                          ? `${state.m3Result.summary.confidence_pct}%`
                          : (state.m3Result.details?.confidence?.score !== undefined)
                          ? `${Math.round(state.m3Result.details.confidence.score * 100)}%`
                          : '구조 분석 완료'
                      }
                    ]}
                  />
                )}

                {/* M4: Capacity (V2 - Both alternatives) */}
                {state.m4Result && (
                  <ModuleResultCard 
                    moduleId="M4"
                    title="건축규모 분석"
                    icon="📐"
                    data={state.m4Result}
                    contextId={state.contextId} 
                    keyMetrics={[
                      { label: '법정 세대수', value: (state.m4Result.summary?.legal_units !== undefined && state.m4Result.summary?.legal_units !== null) ? `${state.m4Result.summary.legal_units}세대` : (state.m4Result.details?.legal_capacity?.total_units !== undefined) ? `${state.m4Result.details.legal_capacity.total_units}세대` : '분석 필요' },
                      { label: '인센티브 세대수', value: (state.m4Result.summary?.incentive_units !== undefined && state.m4Result.summary?.incentive_units !== null) ? `${state.m4Result.summary.incentive_units}세대` : (state.m4Result.details?.incentive_capacity?.total_units !== undefined) ? `${state.m4Result.details.incentive_capacity.total_units}세대` : '분석 필요' },
                      { label: 'Alt A 주차', value: (state.m4Result.summary?.parking_alt_a !== undefined && state.m4Result.summary?.parking_alt_a !== null) ? `${state.m4Result.summary.parking_alt_a}대` : (state.m4Result.details?.parking?.alt_a?.count !== undefined) ? `${state.m4Result.details.parking.alt_a.count}대` : '설계 필요' },
                      { label: 'Alt B 주차', value: (state.m4Result.summary?.parking_alt_b !== undefined && state.m4Result.summary?.parking_alt_b !== null) ? `${state.m4Result.summary.parking_alt_b}대` : (state.m4Result.details?.parking?.alt_b?.count !== undefined) ? `${state.m4Result.details.parking.alt_b.count}대` : '설계 필요' }
                    ]}
                  />
                )}

                {/* M5: Feasibility */}
                {state.m5Result && (
                  <ModuleResultCard 
                    moduleId="M5"
                    title="사업성 분석"
                    icon="💼"
                    data={state.m5Result}
                    contextId={state.contextId} 
                    keyMetrics={[
                      { 
                        label: 'NPV (Public)', 
                        value: (state.m5Result.summary?.npv_public_krw !== undefined && state.m5Result.summary?.npv_public_krw !== null) 
                          ? `₩${state.m5Result.summary.npv_public_krw.toLocaleString()}` 
                          : 'LH 매입 구조 분석'
                      },
                      { 
                        label: 'IRR', 
                        value: (state.m5Result.summary?.irr_pct !== undefined && state.m5Result.summary?.irr_pct !== null) 
                          ? `${state.m5Result.summary.irr_pct.toFixed(1)}%` 
                          : 'LH 매입 구조 분석'
                      },
                      {
                        label: '등급',
                        value: state.m5Result.summary?.grade || (state.m5Result.details?.grade) || '사업성 평가 분석'
                      },
                      {
                        label: 'ROI',
                        value: (state.m5Result.summary?.roi_pct !== undefined && state.m5Result.summary?.roi_pct !== null) 
                          ? `${state.m5Result.summary.roi_pct.toFixed(1)}%` 
                          : 'LH 매입 구조 분석'
                      }
                    ]}
                  />
                )}

                {/* M6: LH Review (FIRST DECISION POINT) */}
                {state.m6Result && (
                  <ModuleResultCard 
                    moduleId="M6"
                    title="LH 심사예측"
                    icon="⚖️"
                    data={state.m6Result}
                    contextId={state.contextId} 
                    keyMetrics={[
                      { 
                        label: '최종 결정', 
                        value: state.m6Result.summary?.decision 
                          || (state.m6Result.details?.decision) 
                          || 'LH 심사 분석 결과', 
                        highlight: true 
                      },
                      { 
                        label: '종합 점수', 
                        value: (state.m6Result.summary?.total_score !== undefined && state.m6Result.summary?.total_score !== null)
                          ? `${state.m6Result.summary.total_score.toFixed(1)}/${state.m6Result.summary.max_score || 110}` 
                          : (state.m6Result.details?.total_score !== undefined)
                          ? `${state.m6Result.details.total_score}/110`
                          : 'LH 평가 기준 적용'
                      },
                      {
                        label: '등급',
                        value: state.m6Result.summary?.grade 
                          || (state.m6Result.details?.grade) 
                          || 'LH 등급 평가'
                      },
                      {
                        label: '승인 가능성',
                        value: (state.m6Result.summary?.approval_probability_pct !== undefined && state.m6Result.summary?.approval_probability_pct !== null) 
                          ? `${state.m6Result.summary.approval_probability_pct}%` 
                          : (state.m6Result.details?.approval_probability !== undefined)
                          ? `${Math.round(state.m6Result.details.approval_probability * 100)}%`
                          : '과거 사례 기반 분석'
                      }
                    ]}
                  />
                )}
              </div>

              {/* Latest REAL APPRAISAL STANDARD Reports - NEW */}
              <div style={{ 
                marginTop: '40px', 
                padding: '30px', 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
              }}>
                <div style={{ textAlign: 'center', marginBottom: '25px' }}>
                  <h3 style={{ margin: 0, fontSize: '22px', color: 'white', fontWeight: 'bold' }}>
                    ⭐ 최신 REAL APPRAISAL STANDARD 보고서
                  </h3>
                  <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.9)', marginTop: '8px' }}>
                    전문 감정평가 문서 형식 | M2-M6 전체 포함 | 실시간 데이터 생성
                  </p>
                </div>
                
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                  gap: '15px',
                  marginBottom: '20px'
                }}>
                  <a
                    href={`https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/pipeline/reports/module/M2/html?context_id=${state.contextId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '18px',
                      background: 'white',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      color: '#333',
                      textAlign: 'center',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      display: 'block'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                    }}
                  >
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>💰</div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>M2 토지감정평가</div>
                    <div style={{ fontSize: '11px', color: '#666' }}>거래사례 중심</div>
                  </a>
                  
                  <a
                    href={`https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/pipeline/reports/module/M3/html?context_id=${state.contextId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '18px',
                      background: 'white',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      color: '#333',
                      textAlign: 'center',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      display: 'block'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                    }}
                  >
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>🏘️</div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>M3 공급 유형</div>
                    <div style={{ fontSize: '11px', color: '#666' }}>단일 결정</div>
                  </a>
                  
                  <a
                    href={`https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/pipeline/reports/module/M4/html?context_id=${state.contextId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '18px',
                      background: 'white',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      color: '#333',
                      textAlign: 'center',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      display: 'block'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                    }}
                  >
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>🏗️</div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>M4 건축 규모</div>
                    <div style={{ fontSize: '11px', color: '#666' }}>최적 규모</div>
                  </a>
                  
                  <a
                    href={`https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/pipeline/reports/module/M5/html?context_id=${state.contextId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '18px',
                      background: 'white',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      color: '#333',
                      textAlign: 'center',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      display: 'block'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                    }}
                  >
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>📊</div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>M5 사업성 분석</div>
                    <div style={{ fontSize: '11px', color: '#666' }}>LH 매입 모델</div>
                  </a>
                  
                  <a
                    href={`https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai/api/v4/pipeline/reports/module/M6/html?context_id=${state.contextId}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '18px',
                      background: 'white',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      color: '#333',
                      textAlign: 'center',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      display: 'block'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                    }}
                  >
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>✅</div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '4px' }}>M6 종합 판단</div>
                    <div style={{ fontSize: '11px', color: '#666' }}>LH 심사</div>
                  </a>
                </div>
                
                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                  <div style={{ 
                    display: 'inline-block',
                    padding: '12px 24px',
                    background: 'rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    fontSize: '13px',
                    color: 'white'
                  }}>
                    💡 Tip: 브라우저에서 Ctrl+P → "PDF로 저장" → "배경 그래픽 켜기"
                  </div>
                </div>
              </div>

              {/* Final Report 6 Types Buttons - Original */}
              <div style={{ 
                marginTop: '20px', 
                padding: '30px', 
                background: '#f8f9fa', 
                borderRadius: '12px',
                border: '2px solid #e0e0e0'
              }}>
                <div style={{ textAlign: 'center', marginBottom: '25px' }}>
                  <h3 style={{ margin: 0, fontSize: '20px', color: '#1976d2' }}>📊 실시간 생성 보고서</h3>
                  <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
                    현재 분석 데이터 기반 (새 탭에서 열림)
                  </p>
                  {!state.contextId && (
                    <div style={{ 
                      marginTop: '12px', 
                      padding: '10px', 
                      background: '#fff3cd', 
                      border: '1px solid #ffc107',
                      borderRadius: '6px',
                      fontSize: '13px',
                      color: '#856404'
                    }}>
                      ⚠️ 최종보고서를 생성하려면 먼저 M1 분석을 완료하세요.
                    </div>
                  )}
                </div>
                
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
                  gap: '15px' 
                }}>
                  {/* 1. 종합 최종보고서 */}
                  <button
                    onClick={() => {
                      if (!state.contextId) {
                        alert('⚠️ M1 분석을 먼저 완료해주세요.');
                        return;
                      }
                      const url = `${BACKEND_URL}/api/v4/reports/final/all_in_one/html?context_id=${state.contextId}`;
                      window.open(url, '_blank');
                    }}
                    disabled={!state.contextId}
                    style={{
                      padding: '20px',
                      background: state.contextId ? 'white' : '#f0f0f0',
                      border: `2px solid ${state.contextId ? '#2563eb' : '#d0d0d0'}`,
                      borderRadius: '8px',
                      cursor: state.contextId ? 'pointer' : 'not-allowed',
                      transition: 'all 0.2s',
                      textAlign: 'left',
                      opacity: state.contextId ? 1 : 0.6
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ fontSize: '28px', marginBottom: '8px' }}>📋</div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
                      종합 최종보고서
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>
                      M2-M6 모든 분석 포함
                    </div>
                  </button>

                  {/* 2. 토지주 제출용 요약보고서 */}
                  <button
                    onClick={() => {
                      if (!state.contextId) {
                        alert('⚠️ M1 분석을 먼저 완료해주세요.');
                        return;
                      }
                      const url = `${BACKEND_URL}/api/v4/reports/final/landowner_summary/html?context_id=${state.contextId}`;
                      window.open(url, '_blank');
                    }}
                    disabled={!state.contextId}
                    style={{
                      padding: '20px',
                      background: state.contextId ? 'white' : '#f0f0f0',
                      border: `2px solid ${state.contextId ? '#10b981' : '#d0d0d0'}`,
                      borderRadius: '8px',
                      cursor: state.contextId ? 'pointer' : 'not-allowed',
                      transition: 'all 0.2s',
                      textAlign: 'left',
                      opacity: state.contextId ? 1 : 0.6
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ fontSize: '28px', marginBottom: '8px' }}>🤝</div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
                      토지주 제출용 보고서
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>
                      설득용, 긍정적 측면 강조
                    </div>
                  </button>

                  {/* 3. LH 제출용 기술검증 보고서 */}
                  <button
                    onClick={() => {
                      if (!state.contextId) {
                        alert('⚠️ M1 분석을 먼저 완료해주세요.');
                        return;
                      }
                      const url = `${BACKEND_URL}/api/v4/reports/final/lh_technical/html?context_id=${state.contextId}`;
                      window.open(url, '_blank');
                    }}
                    disabled={!state.contextId}
                    style={{
                      padding: '20px',
                      background: state.contextId ? 'white' : '#f0f0f0',
                      border: `2px solid ${state.contextId ? '#8b5cf6' : '#d0d0d0'}`,
                      borderRadius: '8px',
                      cursor: state.contextId ? 'pointer' : 'not-allowed',
                      transition: 'all 0.2s',
                      textAlign: 'left',
                      opacity: state.contextId ? 1 : 0.6
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ fontSize: '28px', marginBottom: '8px' }}>🏛️</div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
                      LH 제출용 기술검증 보고서
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>
                      LH 기준 중심, 객관적 사실
                    </div>
                  </button>

                  {/* 4. 사업성·투자 검토 보고서 */}
                  <button
                    onClick={() => {
                      const url = `${BACKEND_URL}/api/v4/reports/final/financial_feasibility/html?context_id=${state.contextId}`;
                      window.open(url, '_blank');
                    }}
                    style={{
                      padding: '20px',
                      background: 'white',
                      border: '2px solid #f59e0b',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      textAlign: 'left'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ fontSize: '28px', marginBottom: '8px' }}>💼</div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
                      사업성·투자 검토 보고서
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>
                      투자자용, M4/M5/M6 중심
                    </div>
                  </button>

                  {/* 5. 사전 검토 리포트 */}
                  <button
                    onClick={() => {
                      const url = `${BACKEND_URL}/api/v4/reports/final/quick_check/html?context_id=${state.contextId}`;
                      window.open(url, '_blank');
                    }}
                    style={{
                      padding: '20px',
                      background: 'white',
                      border: '2px solid #06b6d4',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      textAlign: 'left'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ fontSize: '28px', marginBottom: '8px' }}>⚡</div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
                      사전 검토 리포트
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>
                      빠른 검토용, 5-8 페이지
                    </div>
                  </button>

                  {/* 6. 설명용 프레젠테이션 보고서 */}
                  <button
                    onClick={() => {
                      if (!state.contextId) {
                        alert('⚠️ M1 분석을 먼저 완료해주세요.');
                        return;
                      }
                      const url = `${BACKEND_URL}/api/v4/reports/final/presentation/html?context_id=${state.contextId}`;
                      window.open(url, '_blank');
                    }}
                    disabled={!state.contextId}
                    style={{
                      padding: '20px',
                      background: state.contextId ? 'white' : '#f0f0f0',
                      border: `2px solid ${state.contextId ? '#ec4899' : '#d0d0d0'}`,
                      borderRadius: '8px',
                      cursor: state.contextId ? 'pointer' : 'not-allowed',
                      transition: 'all 0.2s',
                      textAlign: 'left',
                      opacity: state.contextId ? 1 : 0.6
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    <div style={{ fontSize: '28px', marginBottom: '8px' }}>📊</div>
                    <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
                      설명용 프레젠테이션 보고서
                    </div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>
                      화면 공유용, 시각 자료 중심
                    </div>
                  </button>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ 
                marginTop: '40px', 
                padding: '20px', 
                background: '#f5f5f5', 
                borderRadius: '8px',
                textAlign: 'center'
              }}>
                <h3 style={{ marginTop: 0 }}>다음 단계</h3>
                <p style={{ fontSize: '14px', color: '#666' }}>
                  M6 심사 결과를 바탕으로 의사결정을 진행하세요.
                </p>
                <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '20px' }}>
                  <button onClick={handleStartNew} style={{ padding: '12px 24px' }}>
                    새로운 분석 시작
                  </button>
                  <button 
                    onClick={handleGenerateReports}
                    style={{ 
                      padding: '12px 32px',
                      background: '#4CAF50',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontWeight: 'bold',
                      cursor: 'pointer'
                    }}
                  >
                    📄 6종 보고서 생성
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stage 4: Reports Generated */}
        {state.stage === 'REPORTS_GENERATED' && (
          <div style={{ 
            background: 'white', 
            padding: '60px 20px', 
            borderRadius: '12px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>📚</div>
            <h2>보고서 생성 완료!</h2>
            <p style={{ fontSize: '16px', color: '#666', marginTop: '10px' }}>
              6종 보고서가 준비되었습니다. 다운로드하여 활용하세요.
            </p>
            
            {/* Report download links (placeholder) */}
            <div style={{ 
              marginTop: '30px',
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '15px',
              maxWidth: '800px',
              margin: '30px auto'
            }}>
              {['사전검토보고서', '감정평가서', 'LH심사예측', '사업성분석', '종합보고서', '요약보고서'].map((reportName, idx) => (
                <div 
                  key={idx}
                  style={{ 
                    padding: '15px', 
                    background: '#f5f5f5', 
                    borderRadius: '8px',
                    cursor: 'pointer'
                  }}
                >
                  <div style={{ fontSize: '32px', marginBottom: '5px' }}>📄</div>
                  <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{reportName}</div>
                  <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>PDF 다운로드</div>
                </div>
              ))}
            </div>

            <button onClick={handleStartNew} style={{ marginTop: '30px', padding: '12px 32px' }}>
              새로운 분석 시작
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================================================
// Helper Components
// ============================================================================

const StageIndicator: React.FC<{ label: string; active?: boolean; completed?: boolean }> = ({ 
  label, 
  active = false, 
  completed = false 
}) => {
  const bgColor = completed ? '#4CAF50' : active ? '#2196F3' : '#e0e0e0';
  const textColor = completed || active ? 'white' : '#999';

  return (
    <div style={{ 
      padding: '8px 16px', 
      background: bgColor, 
      color: textColor,
      borderRadius: '20px',
      fontWeight: active ? 'bold' : 'normal',
      fontSize: '14px'
    }}>
      {completed && '✓ '}{label}
    </div>
  );
};

const Arrow: React.FC = () => (
  <div style={{ fontSize: '18px', color: '#ccc' }}>→</div>
);

interface ModuleResultCardProps {
  moduleId: string;
  title: string;
  icon: string;
  data: any;
  contextId: string; // ✅ ADD: Pass contextId from parent
  keyMetrics: { label: string; value: string; highlight?: boolean }[];
}

const ModuleResultCard: React.FC<ModuleResultCardProps> = ({ 
  moduleId, 
  title, 
  icon, 
  data,
  contextId, // ✅ ADD
  keyMetrics 
}) => {
  const [expanded, setExpanded] = React.useState(false);
  const handleDownloadPDF = async () => {
    try {
      console.log(`📄 [PDF DOWNLOAD] Starting download for ${moduleId}...`);
      
      // 🔥 FIX: Use pdf_download_url from data if available
      const pdfUrl = data?.pdf_download_url;
      const backendUrl = BACKEND_URL || 'https://8005-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai';
      
      // ✅ USE: contextId from props (passed from parent state)
      const finalUrl = pdfUrl 
        ? `${backendUrl}${pdfUrl}`
        : `${backendUrl}/api/v4/reports/${moduleId}/pdf?context_id=${contextId}`;
      
      console.log(`📄 [PDF DOWNLOAD] Using context_id: ${contextId}`);
      console.log(`📄 [PDF DOWNLOAD] Fetching from: ${finalUrl}`);
      
      // ✅ GET request with context_id query parameter (standardized)
      const response = await fetch(finalUrl, {
        method: 'GET',
      });
      
      console.log(`📄 [PDF DOWNLOAD] Response status: ${response.status}`);
      console.log(`📄 [PDF DOWNLOAD] Response headers:`, {
        contentType: response.headers.get('Content-Type'),
        contentDisposition: response.headers.get('Content-Disposition'),
        contentLength: response.headers.get('Content-Length')
      });
      
      if (!response.ok) {
        const contentType = response.headers.get('Content-Type');
        let errorMessage = `HTTP ${response.status}`;
        
        // Try to parse error from response body
        if (contentType?.includes('application/json')) {
          const errorData = await response.json().catch(() => null);
          if (errorData?.detail) {
            errorMessage = errorData.detail;
          }
        } else {
          const errorText = await response.text().catch(() => '');
          if (errorText) {
            errorMessage = errorText.substring(0, 200);
          }
        }
        
        console.error(`❌ [PDF DOWNLOAD] Failed:`, errorMessage);
        throw new Error(errorMessage);
      }
      
      // ✅ Extract filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `${moduleId}_${title}_보고서_${new Date().toISOString().split('T')[0]}.pdf`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      console.log(`📄 [PDF DOWNLOAD] Using filename: ${filename}`);
      
      // ✅ Download blob with proper cleanup
      const blob = await response.blob();
      console.log(`📄 [PDF DOWNLOAD] Blob size: ${blob.size} bytes, type: ${blob.type}`);
      
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup after download
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        console.log(`✅ [PDF DOWNLOAD] ${moduleId} PDF downloaded successfully, cleanup complete`);
      }, 100);
      
    } catch (error) {
      console.error(`❌ [PDF DOWNLOAD] Failed to download ${moduleId} report:`, error);
      alert(`보고서 다운로드 실패: ${error instanceof Error ? error.message : String(error)}\n\n자세한 내용은 브라우저 콘솔을 확인하세요.`);
    }
  };
  
  // 🔥 FIX: HTML Preview Handler with URL from data
  const handleHTMLPreview = () => {
    try {
      const htmlUrl = data?.html_preview_url;
      const backendUrl = BACKEND_URL || 'https://8005-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai';
      
      const finalUrl = htmlUrl 
        ? `${backendUrl}${htmlUrl}`
        : `${backendUrl}/api/v4/reports/${moduleId}/html?context_id=${contextId}`;
      
      console.log(`👁️ [HTML PREVIEW] Opening: ${finalUrl}`);
      window.open(finalUrl, '_blank', 'noopener,noreferrer');
    } catch (error) {
      console.error(`❌ [HTML PREVIEW] Failed:`, error);
      alert(`HTML 미리보기 실패: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    }
  };
  
  // Check if HTML preview is available
  const htmlPreviewAvailable = data?.html_preview_url || contextId;

  return (
    <div style={{ 
      padding: '20px', 
      background: '#f9f9f9', 
      border: '2px solid #e0e0e0',
      borderRadius: '8px',
      position: 'relative'
    }}>
      <div style={{ fontSize: '32px', marginBottom: '10px' }}>{icon}</div>
      <h3 style={{ margin: '0 0 5px 0', fontSize: '18px' }}>{moduleId}</h3>
      <p style={{ margin: '0 0 15px 0', fontSize: '14px', color: '#666' }}>{title}</p>
      
      {/* M3 전용 설명 문구 */}
      {moduleId === 'M3' && (
        <div style={{
          background: '#e3f2fd',
          border: '1px solid #90caf9',
          borderRadius: '6px',
          padding: '10px',
          marginBottom: '15px',
          fontSize: '12px',
          color: '#1565c0',
          lineHeight: '1.5'
        }}>
          <strong>ℹ️ M3는 점수 평가가 아닌</strong>, 입지에서 형성되는 <strong>실제 생활 패턴 구조</strong>를 분석합니다.
          <br/>
          "추천"이 아닌 "입지 특성 기반 선호 구조 해석" 결과입니다.
        </div>
      )}
      
      {/* M6 전용 다음 단계 문구 */}
      {moduleId === 'M6' && (
        <div style={{
          background: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '6px',
          padding: '10px',
          marginBottom: '15px',
          fontSize: '13px',
          color: '#856404',
          lineHeight: '1.5',
          fontWeight: '600'
        }}>
          <strong>📋 다음 단계:</strong> M6 심사 결과를 바탕으로 의사결정을 진행하세요.
        </div>
      )}
      
      <div style={{ borderTop: '1px solid #ddd', paddingTop: '15px', marginBottom: '15px' }}>
        {keyMetrics.map((metric, idx) => (
          <div key={idx} style={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            marginBottom: '8px',
            fontSize: '14px'
          }}>
            <span style={{ color: '#666' }}>{metric.label}:</span>
            <span style={{ 
              fontWeight: metric.highlight ? 'bold' : 'normal',
              color: metric.highlight ? '#4CAF50' : '#333'
            }}>
              {metric.value}
            </span>
          </div>
        ))}
      </div>
      
      {/* Detailed Report Section (Expandable) */}
      {expanded && data && (
        <div style={{
          marginTop: '20px',
          padding: '20px',
          background: 'white',
          border: '1px solid #ddd',
          borderRadius: '8px',
          maxHeight: '600px',
          overflowY: 'auto'
        }}>
          <h4 style={{ marginTop: 0, marginBottom: '15px', color: '#333' }}>📊 상세 분석 결과</h4>
          
          {/* Summary Section */}
          {data.summary && (
            <div style={{ marginBottom: '20px' }}>
              <h5 style={{ color: '#555', marginBottom: '10px' }}>📋 요약</h5>
              <div style={{ background: '#f5f5f5', padding: '15px', borderRadius: '6px' }}>
                {Object.entries(data.summary).map(([key, value]: [string, any]) => (
                  <div key={key} style={{ marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#666', fontSize: '13px' }}>{key}:</span>
                    <span style={{ fontWeight: 'bold', fontSize: '13px' }}>
                      {typeof value === 'number' ? value.toLocaleString() : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Details Section */}
          {data.details && (
            <div style={{ marginBottom: '20px' }}>
              <h5 style={{ color: '#555', marginBottom: '10px' }}>🔍 세부 정보</h5>
              <div style={{ background: '#f9f9f9', padding: '15px', borderRadius: '6px' }}>
                {Object.entries(data.details).map(([category, content]: [string, any]) => (
                  <div key={category} style={{ marginBottom: '15px' }}>
                    <div style={{ fontWeight: 'bold', color: '#333', marginBottom: '8px', fontSize: '14px' }}>
                      {category}
                    </div>
                    {typeof content === 'object' && content !== null ? (
                      <div style={{ paddingLeft: '15px', fontSize: '13px' }}>
                        {Object.entries(content).map(([key, value]: [string, any]) => (
                          <div key={key} style={{ marginBottom: '5px', color: '#666' }}>
                            <span style={{ color: '#888' }}>{key}:</span>{' '}
                            <span style={{ color: '#333' }}>
                              {typeof value === 'number' ? value.toLocaleString() : 
                               typeof value === 'object' ? JSON.stringify(value, null, 2) : 
                               String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div style={{ paddingLeft: '15px', color: '#666', fontSize: '13px' }}>
                        {String(content)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Raw Data (for debugging) */}
          {process.env.NODE_ENV === 'development' && (
            <details style={{ marginTop: '15px' }}>
              <summary style={{ cursor: 'pointer', color: '#999', fontSize: '12px' }}>🔧 디버그: Raw Data</summary>
              <pre style={{ 
                background: '#f0f0f0', 
                padding: '10px', 
                borderRadius: '4px', 
                fontSize: '11px',
                maxHeight: '300px',
                overflowY: 'auto'
              }}>
                {JSON.stringify(data, null, 2)}
              </pre>
            </details>
          )}
        </div>
      )}
      
      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '8px', marginTop: '15px' }}>
        {/* Toggle Detailed View Button */}
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            flex: 1,
            padding: '10px',
            background: expanded ? '#FF9800' : '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = expanded ? '#F57C00' : '#388E3C'}
          onMouseOut={(e) => e.currentTarget.style.background = expanded ? '#FF9800' : '#4CAF50'}
        >
          <span>{expanded ? '🔼' : '🔽'}</span>
          <span>{expanded ? '상세 보고서 닫기' : '상세 보고서 보기'}</span>
        </button>
        
        {/* Open HTML Report in New Tab */}
        <button
          onClick={() => {
            const backendUrl = BACKEND_URL || 'https://8091-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai';
            const htmlUrl = `${backendUrl}/api/v4/pipeline/reports/module/${moduleId}/html?context_id=${contextId}`;
            console.log(`📄 [HTML REPORT] Opening: ${htmlUrl}`);
            window.open(htmlUrl, '_blank');
          }}
          style={{
            flex: 1,
            padding: '10px',
            background: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px'
          }}
          onMouseOver={(e) => e.currentTarget.style.background = '#1976D2'}
          onMouseOut={(e) => e.currentTarget.style.background = '#2196F3'}
        >
          <span>📄</span>
          <span>새 탭에서 열기</span>
        </button>
      </div>
      
      <div style={{ fontSize: '11px', color: '#999', marginTop: '8px', textAlign: 'center' }}>
        💡 Tip: 새 탭 보고서에서 Ctrl+P → "PDF로 저장" → "배경 그래픽 켜기"
      </div>
    </div>
  );
};

export default PipelineOrchestrator;
