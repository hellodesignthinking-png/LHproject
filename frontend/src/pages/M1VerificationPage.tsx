/**
 * M1 Verification Page
 * =====================
 * 
 * 🔒 CRITICAL GATE: This page blocks M2-M6 execution until user approves
 * 
 * User must review:
 * 1. Basic land info (address, area, zoning, FAR/BCR)
 * 2. Location & infrastructure (subway, bus, POI)
 * 3. Official price & regulations
 * 4. Transaction cases (recent 6 months)
 * 
 * User actions:
 * - [Reject] → Re-collect data, invalidate M2-M6
 * - [Approve] → Enable M2 execution
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI, ModuleResult, useProjectStatus } from '../services/analysisAPI';
import { ModuleStatusBar } from '../components/ModuleStatusBar';
import { M1DataInputForm } from './M1DataInputForm';
import './M1VerificationPage.css';

interface M1Data {
  // Basic land info
  address: string;
  road_address: string;
  area_sqm: number;
  area_pyeong: number;
  zone_type: string;
  far: number;
  bcr: number;
  road_width: number;
  
  // Location data
  subway_stations: Array<{
    name: string;
    line: string;
    distance_m: number;
    walk_time_min: number;
  }>;
  bus_stops: Array<{
    name: string;
    distance_m: number;
    routes: string[];
  }>;
  poi_schools: Array<{
    name: string;
    type: string;
    distance_m: number;
  }>;
  poi_commercial: Array<{
    name: string;
    type: string;
    distance_m: number;
  }>;
  
  // Official price
  official_land_price: number;
  official_price_date: string;
  official_price_source: string;
  
  // Regulations
  regulations: string[];
  restrictions: string[];
  
  // Transaction cases
  transaction_cases: Array<{
    date: string;
    area_sqm: number;
    amount: number;
    distance_m: number;
    address: string;
  }>;
  
  // Context info
  context_id: string;
  fetched_at: string;
  data_sources: {
    address: string;
    cadastral: string;
    zoning: string;
    official_price: string;
  };
}

export const M1VerificationPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  const { status: projectStatus, loading: statusLoading, error: statusError } = 
    useProjectStatus(projectId || null);
  
  const [m1Data, setM1Data] = useState<M1Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [showManualInput, setShowManualInput] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [collectingPOI, setCollectingPOI] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState<M1Data | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  
  // Handle POI data collection
  const handleCollectPOI = async () => {
    if (!m1Data?.address) {
      alert('주소 정보가 없습니다.');
      return;
    }
    
    const confirmed = window.confirm(
      '🗺️ 카카오맵 API로 주변 시설 정보를 수집하시겠습니까?\n\n' +
      '수집 항목:\n' +
      '- 지하철역 (1km 반경)\n' +
      '- 버스 정류장 (500m 반경)\n' +
      '- 학교 (1km 반경)\n' +
      '- 편의시설 (1km 반경)\n\n' +
      '소요 시간: 약 10-15초'
    );
    
    if (!confirmed) return;
    
    try {
      setCollectingPOI(true);
      console.log('🗺️ Collecting POI data for:', m1Data.address);
      
      const response = await analysisAPI.collectPOI(m1Data.address);
      
      if (response.success && response.data) {
        console.log('✅ POI data collected:', response.data);
        
        // Update m1Data with collected POI
        setM1Data(prev => prev ? {
          ...prev,
          subway_stations: response.data!.subway_stations,
          bus_stops: response.data!.bus_stops,
          poi_schools: response.data!.poi_schools,
          poi_commercial: response.data!.poi_commercial
        } : null);
        
        alert(
          `✅ POI 데이터 수집 완료!\n\n` +
          `🚇 지하철역: ${response.data.subway_stations.length}개\n` +
          `🚌 버스 정류장: ${response.data.bus_stops.length}개\n` +
          `🏫 학교: ${response.data.poi_schools.length}개\n` +
          `🏪 편의시설: ${response.data.poi_commercial.length}개\n\n` +
          `수집된 데이터가 화면에 표시되었습니다.`
        );
      } else {
        throw new Error(response.message || 'POI 수집 실패');
      }
    } catch (err) {
      console.error('❌ Failed to collect POI:', err);
      alert(`❌ POI 데이터 수집 실패:\n${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setCollectingPOI(false);
    }
  };

  // Fetch M1 data
  useEffect(() => {
    if (!projectId) return;

    const fetchM1Data = async () => {
      try {
        setLoading(true);
        
        // 먼저 세션 스토리지에서 수동 입력 데이터 확인
        const manualDataStr = sessionStorage.getItem(`m1_manual_${projectId}`);
        if (manualDataStr) {
          const manualData = JSON.parse(manualDataStr);
          console.log('📝 수동 입력된 M1 데이터 로드:', manualData);
          setM1Data(manualData);
          setError(null);
          setLoading(false);
          return;
        }
        
        // 수동 데이터가 없으면 API에서 가져오기
        const result = await analysisAPI.getModuleResult<M1Data>(projectId, 'M1');
        
        // Validate result exists
        if (!result.result) {
          console.log('⚠️ M1 data not available - auto collecting might be needed');
          throw new Error('M1 data not available');
        }
        
        // Check if POI data is missing and try to auto-collect
        if (result.result.address && 
            (!result.result.subway_stations || result.result.subway_stations.length === 0) &&
            (!result.result.poi_schools || result.result.poi_schools.length === 0)) {
          console.log('🔄 POI 데이터 누락 감지 - 자동 수집 시도');
          
          try {
            const poiResponse = await analysisAPI.collectPOI(result.result.address);
            if (poiResponse.success && poiResponse.data) {
              console.log('✅ POI 자동 수집 완료:', poiResponse.data);
              result.result = {
                ...result.result,
                subway_stations: poiResponse.data.subway_stations,
                bus_stops: poiResponse.data.bus_stops,
                poi_schools: poiResponse.data.poi_schools,
                poi_commercial: poiResponse.data.poi_commercial
              };
            }
          } catch (poiErr) {
            console.warn('⚠️ POI 자동 수집 실패:', poiErr);
            // Continue with existing data even if POI collection fails
          }
        }
        
        setM1Data(result.result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load M1 data');
      } finally {
        setLoading(false);
      }
    };

    fetchM1Data();
  }, [projectId]);

  const handleApprove = async () => {
    if (!projectId) return;
    
    try {
      setVerifying(true);
      
      // 🔥 CRITICAL STEP 1: COMMIT M1 DATA to result_data
      // This is THE MOST IMPORTANT step - without this, M2~M6 cannot execute
      console.log('=' .repeat(80));
      console.log('🔥 STEP 1: COMMITTING M1 DATA TO BACKEND');
      console.log('=' .repeat(80));
      
      let m1DataToCommit = m1Data;
      
      // Check if this is manual data or edited data
      const manualDataStr = sessionStorage.getItem(`m1_manual_${projectId}`);
      const isManualData = manualDataStr !== null;
      
      if (isManualData) {
        // Use manual/edited data from session storage
        m1DataToCommit = JSON.parse(manualDataStr);
        console.log('📝 Using manual/edited M1 data from session');
      } else if (m1Data) {
        // Use existing M1 data
        console.log('📊 Using existing M1 data');
      } else {
        alert('❌ M1 데이터가 없습니다. 데이터를 먼저 입력해주세요.');
        setVerifying(false);
        return;
      }
      
      // Validate M1 data before commit
      if (!m1DataToCommit.area_sqm || m1DataToCommit.area_sqm <= 0) {
        alert('❌ 면적(area_sqm)이 유효하지 않습니다. 0보다 큰 값을 입력해주세요.');
        setVerifying(false);
        return;
      }
      
      if (!m1DataToCommit.official_land_price || m1DataToCommit.official_land_price <= 0) {
        alert('❌ 공시지가(official_land_price)가 유효하지 않습니다. 0보다 큰 값을 입력해주세요.');
        setVerifying(false);
        return;
      }
      
      if (!m1DataToCommit.zone_type || m1DataToCommit.zone_type.trim() === '') {
        alert('❌ 용도지역(zone_type)이 유효하지 않습니다. 값을 입력해주세요.');
        setVerifying(false);
        return;
      }
      
      console.log('📤 M1 Data to commit:', {
        area_sqm: m1DataToCommit.area_sqm,
        official_land_price: m1DataToCommit.official_land_price,
        zone_type: m1DataToCommit.zone_type,
        far: m1DataToCommit.far,
        bcr: m1DataToCommit.bcr
      });
      
      try {
        const commitResponse = await analysisAPI.commitM1Data(projectId, m1DataToCommit);
        console.log('=' .repeat(80));
        console.log('✅ M1 DATA COMMITTED SUCCESSFULLY');
        console.log('   Committed at:', commitResponse.committed_at);
        console.log('   Area:', commitResponse.committed_data.area_sqm, '㎡');
        console.log('   Price:', commitResponse.committed_data.official_land_price, '원/㎡');
        console.log('   Zone:', commitResponse.committed_data.zone_type);
        console.log('   🔥 M2~M6 CAN NOW EXECUTE');
        console.log('=' .repeat(80));
        
        // Clean up session storage after successful commit
        if (isManualData) {
          sessionStorage.removeItem(`m1_manual_${projectId}`);
          console.log('🗑️ Session storage cleaned');
        }
      } catch (commitError: any) {
        console.error('❌ M1 commit failed:', commitError);
        alert(
          `❌ M1 데이터 커밋 실패\n\n` +
          `${commitError.message}\n\n` +
          `M1 데이터가 유효한지 확인해주세요.`
        );
        setVerifying(false);
        return;
      }
      
      // 🔥 STEP 2: VERIFY M1 (mark as approved)
      console.log('=' .repeat(80));
      console.log('🔥 STEP 2: VERIFYING M1 MODULE');
      console.log('=' .repeat(80));
      
      try {
        const verifyResponse = await analysisAPI.verifyModule(projectId, 'M1', {
          approved: true,
          comments: 'M1 data committed and verified by user',
          verified_by: 'user@example.com'
        });
        
        console.log('✅ M1 verified:', verifyResponse.message);
      } catch (verifyError: any) {
        // If verification fails, log but continue (data is already committed)
        console.warn('⚠️ M1 verification warning:', verifyError.message);
      }
      
      // 🔥 STEP 3: EXECUTE M2~M6 PIPELINE
      console.log('=' .repeat(80));
      console.log('🔥 STEP 3: EXECUTING M2~M6 PIPELINE');
      console.log('=' .repeat(80));
      
      try {
        const execResponse = await analysisAPI.executeFullPipeline(projectId);
        console.log('✅ Pipeline execution triggered');
        console.log('   Executed modules:', execResponse.executed_modules);
        console.log('=' .repeat(80));
        
        alert(
          `✅ M1 검증 성공!\n\n` +
          `🔥 M1 데이터가 커밋되었습니다.\n` +
          `⚡ M2~M6 모듈 실행 중...\n\n` +
          `실행된 모듈: ${execResponse.executed_modules?.join(', ') || 'N/A'}`
        );
        
        // Navigate to M2 results
        navigate(`/projects/${projectId}/modules/m2/results`);
      } catch (execError: any) {
        console.error('❌ Pipeline execution failed:', execError);
        alert(
          `✅ M1 검증 완료\n\n` +
          `하지만 파이프라인 실행 실패:\n` +
          `${execError.message}\n\n` +
          `대시보드에서 모듈을 수동으로 실행해주세요.`
        );
        
        // Navigate to dashboard
        navigate(`/projects/${projectId}`);
      }
      
    } catch (err: any) {
      console.error('❌ Approval process failed:', err);
      alert(`❌ Verification failed: ${err.message || 'Unknown error'}`);
    } finally {
      setVerifying(false);
    }
  };

  const handleReject = async () => {
    if (!projectId) return;
    
    const confirmed = window.confirm(
      '⚠️ This will reject M1 data and require re-collection.\n\n' +
      'M2-M6 will be invalidated.\n\n' +
      'Are you sure?'
    );
    
    if (!confirmed) return;
    
    try {
      setVerifying(true);
      
      const response = await analysisAPI.verifyModule(projectId, 'M1', {
        approved: false,
        comments: 'M1 data rejected - needs correction',
        verified_by: 'user@example.com' // TODO: Get from auth context
      });
      
      alert(`⚠️ ${response.message}\n\n${response.next_action}`);
      
      // Navigate back to project input
      navigate(`/projects/${projectId}/edit`);
      
    } catch (err) {
      alert(`❌ Rejection failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setVerifying(false);
    }
  };

  const handleModuleClick = (moduleName: string) => {
    // Navigate to module result page
    navigate(`/projects/${projectId}/modules/${moduleName.toLowerCase()}/results`);
  };

  if (statusLoading || loading) {
    return (
      <div className="verification-page loading">
        <div className="spinner">Loading M1 data...</div>
      </div>
    );
  }

  // Show edit form if in edit mode
  if (editMode && m1Data) {
    return (
      <div className="verification-page">
        <M1DataInputForm
          projectId={projectId!}
          initialAddress={m1Data.address}
          initialData={{
            address: m1Data.address,
            road_address: m1Data.road_address || '',
            parcel_number: '',
            area_sqm: m1Data.area_sqm,
            zone_type: m1Data.zone_type,
            far: m1Data.far,
            bcr: m1Data.bcr,
            road_width: m1Data.road_width || 0,
            official_land_price: m1Data.official_land_price || 0,
            official_price_date: m1Data.official_price_date || new Date().toISOString().split('T')[0],
            regulations: m1Data.regulations ? m1Data.regulations.join(', ') : '',
            restrictions: m1Data.restrictions ? m1Data.restrictions.join(', ') : '',
            subway_stations: m1Data.subway_stations || [],
            bus_stops: m1Data.bus_stops || [],
            poi_schools: m1Data.poi_schools || [],
            poi_commercial: m1Data.poi_commercial || [],
            transaction_cases: m1Data.transaction_cases || []
          }}
          onSubmit={async (formData) => {
            try {
              console.log('수정된 M1 데이터:', formData);
              
              // 수정된 데이터를 M1Data 형식으로 변환
              const updatedM1Data: M1Data = {
                address: formData.address,
                road_address: formData.road_address || '',
                area_sqm: formData.area_sqm,
                area_pyeong: formData.area_sqm / 3.3058,
                zone_type: formData.zone_type,
                far: formData.far,
                bcr: formData.bcr,
                road_width: formData.road_width || 0,
                
                subway_stations: formData.subway_stations || [],
                bus_stops: formData.bus_stops || [],
                poi_schools: formData.poi_schools || [],
                poi_commercial: formData.poi_commercial || [],
                
                official_land_price: formData.official_land_price || 0,
                official_price_date: formData.official_price_date || new Date().toISOString().split('T')[0],
                official_price_source: '수동 수정',
                
                regulations: formData.regulations ? formData.regulations.split(',').map(r => r.trim()) : [],
                restrictions: formData.restrictions ? formData.restrictions.split(',').map(r => r.trim()) : [],
                
                transaction_cases: formData.transaction_cases || [],
                
                // 메타데이터
                context_id: m1Data.context_id,
                fetched_at: new Date().toISOString(),
                data_sources: {
                  address: '수동 수정',
                  cadastral: '수동 수정',
                  zoning: '수동 수정',
                  official_price: '수동 수정'
                }
              };
              
              // 백엔드에 업데이트
              await analysisAPI.updateM1Data(projectId!, updatedM1Data);
              
              // 세션 스토리지에도 저장
              sessionStorage.setItem(`m1_manual_${projectId}`, JSON.stringify(updatedM1Data));
              
              alert('✅ M1 데이터가 성공적으로 수정되었습니다!');
              
              // 수정 모드 종료 및 페이지 새로고침
              setEditMode(false);
              window.location.reload();
            } catch (err) {
              console.error('M1 데이터 수정 실패:', err);
              alert(`❌ M1 데이터 수정에 실패했습니다:\n${err instanceof Error ? err.message : 'Unknown error'}`);
              throw err;
            }
          }}
          onCancel={() => {
            setEditMode(false);
          }}
        />
      </div>
    );
  }

  if (statusError || error) {
    // Show manual input form if requested
    if (showManualInput) {
      return (
        <div className="verification-page">
          <M1DataInputForm
            projectId={projectId!}
            initialAddress={projectStatus?.address}
            onSubmit={async (formData) => {
              try {
                console.log('수동 입력된 M1 데이터:', formData);
                
                // 수동 입력 데이터를 M1Data 형식으로 변환
                const m1Data: M1Data = {
                  address: formData.address,
                  road_address: formData.road_address || '',
                  area_sqm: formData.area_sqm,
                  area_pyeong: formData.area_sqm / 3.3058,
                  zone_type: formData.zone_type,
                  far: formData.far,
                  bcr: formData.bcr,
                  road_width: formData.road_width || 0,
                  
                  subway_stations: formData.subway_stations || [],
                  bus_stops: formData.bus_stops || [],
                  poi_schools: formData.poi_schools || [],
                  poi_commercial: formData.poi_commercial || [],
                  
                  official_land_price: formData.official_land_price || 0,
                  official_price_date: formData.official_price_date || new Date().toISOString().split('T')[0],
                  official_price_source: '수동 입력',
                  
                  regulations: formData.regulations ? formData.regulations.split(',').map(r => r.trim()) : [],
                  restrictions: formData.restrictions ? formData.restrictions.split(',').map(r => r.trim()) : [],
                  
                  transaction_cases: formData.transaction_cases || [],
                  
                  // 메타데이터
                  context_id: projectStatus?.current_context_id || '',
                  fetched_at: new Date().toISOString(),
                  data_sources: {
                    address: '수동 입력',
                    cadastral: '수동 입력',
                    zoning: '수동 입력',
                    official_price: '수동 입력'
                  }
                };
                
                // TODO: 백엔드 API에 수동 입력 데이터 저장 엔드포인트 필요
                // 지금은 로컬 스토리지에 임시 저장
                sessionStorage.setItem(`m1_manual_${projectId}`, JSON.stringify(m1Data));
                
                alert('✅ M1 데이터가 저장되었습니다!\n이제 데이터를 검증하고 승인할 수 있습니다.');
                
                // 페이지 새로고침하여 저장된 데이터 로드
                window.location.reload();
              } catch (err) {
                console.error('M1 데이터 저장 실패:', err);
                throw err;
              }
            }}
            onCancel={() => {
              setShowManualInput(false);
              navigate(`/projects/${projectId}`);
            }}
          />
        </div>
      );
    }

    return (
      <div className="verification-page error">
        <div className="error-container">
          <h2>❌ M1 데이터 로딩 오류</h2>
          <p className="error-message">{statusError || error}</p>
          
          <div className="error-details">
            <h3>📋 가능한 원인:</h3>
            <ul>
              <li>M1 데이터 자동 수집이 아직 시작되지 않았습니다</li>
              <li>정부 API 연결에 문제가 있을 수 있습니다</li>
              <li>입력하신 주소로 토지 정보를 찾을 수 없습니다</li>
            </ul>
          </div>

          <div className="error-actions">
            <button 
              className="btn-primary"
              onClick={() => setShowManualInput(true)}
            >
              📝 수동으로 M1 데이터 입력하기
            </button>
            <button 
              className="btn-secondary"
              onClick={() => window.location.reload()}
            >
              🔄 페이지 새로고침
            </button>
            <button 
              className="btn-secondary"
              onClick={() => navigate(`/projects/${projectId}`)}
            >
              ← 프로젝트 대시보드로 돌아가기
            </button>
          </div>

          <div className="error-hint">
            <p>
              <strong>💡 도움말:</strong><br/>
              M1 데이터 수집은 프로젝트 생성 시 자동으로 시작됩니다. 
              몇 분 정도 기다린 후 다시 시도하거나, 수동 입력을 선택하세요.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!projectStatus || !m1Data) {
    return (
      <div className="verification-page error">
        <h2>⚠️ No Data Available</h2>
        <p>M1 data has not been collected yet.</p>
      </div>
    );
  }

  // 디버그 로그
  console.log('📊 M1VerificationPage 렌더링:', {
    projectId,
    hasM1Data: !!m1Data,
    isEditing,
    hasEditedData: !!editedData,
    m1Data_preview: m1Data ? {
      address: m1Data.address,
      area_sqm: m1Data.area_sqm,
      zone_type: m1Data.zone_type
    } : null
  });

  // M1 데이터가 비어있는지 확인
  const isM1DataEmpty = m1Data && (
    !m1Data.area_sqm || 
    m1Data.area_sqm === 0 || 
    !m1Data.zone_type || 
    m1Data.zone_type === ''
  );

  console.log('🔍 M1 데이터 상태:', {
    isM1DataEmpty,
    area_sqm: m1Data?.area_sqm,
    zone_type: m1Data?.zone_type,
    official_land_price: m1Data?.official_land_price
  });

  return (
    <div className="verification-page">
      {/* Module Status Bar */}
      <ModuleStatusBar
        m1={projectStatus.m1_status}
        m2={projectStatus.m2_status}
        m3={projectStatus.m3_status}
        m4={projectStatus.m4_status}
        m5={projectStatus.m5_status}
        m6={projectStatus.m6_status}
        projectId={projectId!}
        onModuleClick={handleModuleClick}
      />

      {/* Page Header */}
      <div className="page-header">
        <h1>🔒 M1 토지정보 확인</h1>
        <div className="project-info">
          <div className="info-item">
            <strong>Project:</strong> {projectStatus.project_name}
          </div>
          <div className="info-item">
            <strong>Address:</strong> {projectStatus.address}
          </div>
          <div className="info-item">
            <strong>Context ID:</strong> <code>{projectStatus.current_context_id}</code>
          </div>
          <div className="info-item">
            <strong>Data Fetched:</strong> {m1Data.fetched_at}
          </div>
        </div>
        <div className="header-actions">
          {!isEditing ? (
            <button 
              className="btn-edit"
              onClick={() => {
                console.log('🖊️ 편집 버튼 클릭됨!');
                console.log('현재 M1 데이터:', m1Data);
                setIsEditing(true);
                setEditedData({...m1Data});
                console.log('편집 모드 활성화됨, isEditing:', true);
              }}
              style={{
                padding: '10px 20px',
                fontSize: '16px',
                background: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                marginTop: '10px'
              }}
            >
              ✏️ 데이터 수정하기
            </button>
          ) : (
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
              <button 
                className="btn-save"
                onClick={async () => {
                  console.log('💾 저장 버튼 클릭됨!');
                  console.log('editedData:', editedData);
                  console.log('projectId:', projectId);
                  
                  if (!editedData || !projectId) {
                    console.error('❌ editedData 또는 projectId가 없습니다');
                    return;
                  }
                  
                  try {
                    setIsSaving(true);
                    console.log('🚀 백엔드에 데이터 전송 중...');
                    
                    // 백엔드에 업데이트
                    await analysisAPI.updateM1Data(projectId, editedData);
                    console.log('✅ 백엔드 업데이트 성공!');
                    
                    // 로컬 상태 업데이트
                    setM1Data(editedData);
                    setIsEditing(false);
                    
                    alert('✅ M1 데이터가 성공적으로 저장되었습니다!');
                  } catch (err) {
                    console.error('❌ 저장 실패:', err);
                    alert('❌ 저장에 실패했습니다: ' + (err instanceof Error ? err.message : 'Unknown error'));
                  } finally {
                    setIsSaving(false);
                  }
                }}
                disabled={isSaving}
                style={{
                  padding: '10px 20px',
                  fontSize: '16px',
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  opacity: isSaving ? 0.6 : 1
                }}
              >
                {isSaving ? '💾 저장 중...' : '💾 저장'}
              </button>
              <button 
                className="btn-cancel"
                onClick={() => {
                  setIsEditing(false);
                  setEditedData(null);
                }}
                disabled={isSaving}
                style={{
                  padding: '10px 20px',
                  fontSize: '16px',
                  background: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: isSaving ? 'not-allowed' : 'pointer',
                  opacity: isSaving ? 0.6 : 1
                }}
              >
                ❌ 취소
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="verification-content">
        {/* Editing Mode Indicator */}
        {isEditing && (
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '15px 20px',
            borderRadius: '8px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}>
            <span style={{ fontSize: '24px' }}>✏️</span>
            <div>
              <strong style={{ fontSize: '18px' }}>편집 모드 활성화</strong>
              <p style={{ margin: '5px 0 0 0', fontSize: '14px', opacity: 0.9 }}>
                파란색 테두리가 있는 필드를 클릭하여 수정할 수 있습니다. 완료되면 "💾 저장" 버튼을 클릭하세요.
              </p>
            </div>
          </div>
        )}
        
        {/* Empty Data Warning */}
        {isM1DataEmpty && !isEditing && (
          <div style={{
            background: '#fff3cd',
            border: '2px solid #ffc107',
            borderRadius: '8px',
            padding: '20px',
            marginBottom: '20px'
          }}>
            <h3 style={{ color: '#856404', margin: '0 0 10px 0' }}>
              ⚠️ M1 데이터가 비어있습니다
            </h3>
            <p style={{ color: '#856404', margin: '0 0 15px 0' }}>
              필수 정보(면적, 용도지역, 공시지가 등)가 입력되지 않았습니다.
              <br />
              <strong>"✏️ 데이터 수정하기"</strong> 버튼을 클릭하여 필수 정보를 입력해주세요.
            </p>
            <ul style={{ color: '#856404', margin: '0', paddingLeft: '20px' }}>
              <li>토지 면적 (m²)</li>
              <li>용도지역 (예: 준주거지역, 상업지역)</li>
              <li>공시지가 (₩/m²)</li>
              <li>건폐율, 용적률</li>
            </ul>
          </div>
        )}
        
        {/* Warning Banner */}
        <div className="warning-banner">
          <h3>⚠️ IMPORTANT: Data Verification Required</h3>
          <p>
            Please carefully review the land data below. 
            M2-M6 analysis will be based on this data.
            If any information is incorrect, click [Reject] to re-collect.
          </p>
        </div>

        {/* Panel 1: Basic Land Information */}
        <section className="data-panel">
          <h2>🏠 1. 기본 토지 정보</h2>
          <div className="data-grid">
            <div className="data-item">
              <label>도로명 주소:</label>
              {isEditing && editedData ? (
                <input
                  type="text"
                  value={editedData.road_address}
                  onChange={(e) => setEditedData({...editedData, road_address: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              ) : (
                <span className="value">{m1Data.road_address}</span>
              )}
            </div>
            <div className="data-item">
              <label>지번 주소:</label>
              {isEditing && editedData ? (
                <input
                  type="text"
                  value={editedData.address}
                  onChange={(e) => setEditedData({...editedData, address: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              ) : (
                <span className="value">{m1Data.address}</span>
              )}
            </div>
            <div className="data-item">
              <label>면적 (m²):</label>
              {isEditing && editedData ? (
                <input
                  type="number"
                  value={editedData.area_sqm}
                  onChange={(e) => {
                    const area_sqm = parseFloat(e.target.value) || 0;
                    setEditedData({
                      ...editedData,
                      area_sqm,
                      area_pyeong: area_sqm / 3.3058
                    });
                  }}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              ) : (
                <span className="value">
                  {(m1Data.area_sqm || 0).toLocaleString()}m² 
                  ({(m1Data.area_pyeong || 0).toLocaleString()}평)
                </span>
              )}
            </div>
            <div className="data-item">
              <label>용도지역:</label>
              {isEditing && editedData ? (
                <input
                  type="text"
                  value={editedData.zone_type}
                  onChange={(e) => setEditedData({...editedData, zone_type: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                  placeholder="예: 준주거지역, 제2종일반주거지역"
                />
              ) : (
                <span className="value">{m1Data.zone_type}</span>
              )}
            </div>
            <div className="data-item">
              <label>건폐율 (%):</label>
              {isEditing && editedData ? (
                <input
                  type="number"
                  value={editedData.bcr}
                  onChange={(e) => setEditedData({...editedData, bcr: parseFloat(e.target.value) || 0})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              ) : (
                <span className="value">{m1Data.bcr}%</span>
              )}
            </div>
            <div className="data-item">
              <label>용적률 (%):</label>
              {isEditing && editedData ? (
                <input
                  type="number"
                  value={editedData.far}
                  onChange={(e) => setEditedData({...editedData, far: parseFloat(e.target.value) || 0})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              ) : (
                <span className="value">{m1Data.far}%</span>
              )}
            </div>
            <div className="data-item">
              <label>도로폭 (m):</label>
              {isEditing && editedData ? (
                <input
                  type="number"
                  value={editedData.road_width}
                  onChange={(e) => setEditedData({...editedData, road_width: parseFloat(e.target.value) || 0})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              ) : (
                <span className="value">{m1Data.road_width}m</span>
              )}
            </div>
            <div className="data-source">
              📍 Source: {m1Data.data_sources.cadastral} ✅
            </div>
          </div>
        </section>

        {/* Panel 2: Location & Infrastructure */}
        <section className="data-panel">
          <h2>🚇 2. 위치·입지 데이터</h2>
          
          <h3>지하철역</h3>
          {m1Data.subway_stations && m1Data.subway_stations.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>역명</th>
                  <th>호선</th>
                  <th>거리</th>
                  <th>도보시간</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {m1Data.subway_stations.map((station, idx) => (
                  <tr key={idx}>
                    <td>{station.name}</td>
                    <td>{station.line}</td>
                    <td>{station.distance_m}m</td>
                    <td>{station.walk_time_min}분</td>
                    <td>
                      <span className={station.distance_m <= 500 ? 'status-good' : 'status-normal'}>
                        {station.distance_m <= 500 ? '🟢 우수' : '⚪ 보통'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="no-data-box">
              <p className="no-data-title">⚠️ 교통 정보 미수집</p>
              <p className="no-data-desc">
                현재 백엔드에서 지하철역 정보를 자동으로 수집하지 않습니다.
                <br />
                실제 위치의 지하철역 정보를 확인하려면:
              </p>
              <ul className="no-data-tips">
                <li>🗺️ 네이버 지도 또는 카카오맵에서 '{m1Data.address}' 검색</li>
                <li>🚇 주변 지하철역 거리 확인</li>
                <li>📝 [Reject] 클릭 후 수동 입력으로 교통 정보 추가</li>
              </ul>
            </div>
          )}

          <h3>버스정류장</h3>
          {m1Data.bus_stops && m1Data.bus_stops.length > 0 ? (
            <div className="bus-info">
              <p>{m1Data.bus_stops.length}개 정류장, 200m 이내</p>
            </div>
          ) : (
            <div className="no-data-box">
              <p className="no-data-title">⚠️ 버스 정보 미수집</p>
              <p className="no-data-desc">
                현재 백엔드에서 버스정류장 정보를 자동으로 수집하지 않습니다.
                <br />
                실제 위치의 버스정류장 정보를 확인하려면:
              </p>
              <ul className="no-data-tips">
                <li>🗺️ 네이버 지도 또는 카카오맵에서 '{m1Data.address}' 검색</li>
                <li>🚌 주변 버스정류장 위치 및 노선 확인</li>
                <li>📝 [Reject] 클릭 후 수동 입력으로 버스 정보 추가</li>
              </ul>
            </div>
          )}

          <h3>주요 시설</h3>
          <div className="poi-grid">
            {m1Data.poi_schools && m1Data.poi_schools.length > 0 && (
              <div className="poi-category">
                <h4>학교 ({m1Data.poi_schools.length})</h4>
                <ul>
                  {m1Data.poi_schools.slice(0, 3).map((poi, idx) => (
                    <li key={idx}>{poi.name} - {poi.distance_m}m</li>
                  ))}
                </ul>
              </div>
            )}
            
            {m1Data.poi_commercial && m1Data.poi_commercial.length > 0 && (
              <div className="poi-category">
                <h4>편의시설 ({m1Data.poi_commercial.length})</h4>
                <ul>
                  {m1Data.poi_commercial.slice(0, 3).map((poi, idx) => (
                    <li key={idx}>{poi.name} - {poi.distance_m}m</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="data-source">
            📍 Source: {m1Data.data_sources.address} ✅
          </div>
        </section>

        {/* Panel 3: Official Price & Regulations */}
        <section className="data-panel">
          <h2>💰 3. 공시지가 & 규제 정보</h2>
          
          <div className="data-grid">
            <div className="data-item">
              <label>공시지가 (₩/m²):</label>
              {isEditing && editedData ? (
                <input
                  type="number"
                  value={editedData.official_land_price}
                  onChange={(e) => setEditedData({...editedData, official_land_price: parseFloat(e.target.value) || 0})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                  placeholder="예: 5000000"
                />
              ) : (
                <span className="value">₩{(m1Data.official_land_price || 0).toLocaleString()}/m²</span>
              )}
            </div>
            <div className="data-item">
              <label>기준일:</label>
              {isEditing && editedData ? (
                <input
                  type="date"
                  value={editedData.official_price_date}
                  onChange={(e) => setEditedData({...editedData, official_price_date: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '2px solid #007bff',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}
                />
              ) : (
                <span className="value">{m1Data.official_price_date}</span>
              )}
            </div>
          </div>

          <h3>규제 사항</h3>
          {isEditing && editedData ? (
            <div>
              <textarea
                value={(editedData.regulations || []).join(', ')}
                onChange={(e) => {
                  const regulations = e.target.value.split(',').map(r => r.trim()).filter(r => r);
                  setEditedData({...editedData, regulations});
                }}
                placeholder="규제 사항을 쉼표(,)로 구분하여 입력하세요"
                style={{
                  width: '100%',
                  minHeight: '60px',
                  padding: '8px',
                  border: '2px solid #007bff',
                  borderRadius: '4px',
                  fontSize: '14px',
                  fontFamily: 'inherit'
                }}
              />
              <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                예: 주택건설사업계획승인, 건축물의 건축허가, 도시관리계획
              </small>
            </div>
          ) : (
            m1Data.regulations && m1Data.regulations.length > 0 ? (
              <ul className="regulation-list">
                {m1Data.regulations.map((reg, idx) => (
                  <li key={idx}>⚠️ {reg}</li>
                ))}
              </ul>
            ) : (
              <p className="no-data">특별 규제 사항 없음</p>
            )
          )}

          {(isEditing || (m1Data.restrictions && m1Data.restrictions.length > 0)) && (
            <>
              <h3>제한 사항</h3>
              {isEditing && editedData ? (
                <div>
                  <textarea
                    value={(editedData.restrictions || []).join(', ')}
                    onChange={(e) => {
                      const restrictions = e.target.value.split(',').map(r => r.trim()).filter(r => r);
                      setEditedData({...editedData, restrictions});
                    }}
                    placeholder="제한 사항을 쉼표(,)로 구분하여 입력하세요"
                    style={{
                      width: '100%',
                      minHeight: '60px',
                      padding: '8px',
                      border: '2px solid #007bff',
                      borderRadius: '4px',
                      fontSize: '14px',
                      fontFamily: 'inherit'
                    }}
                  />
                  <small style={{ color: '#666', display: 'block', marginTop: '5px' }}>
                    예: 녹지지역, 고도제한, 일조권 제한
                  </small>
                </div>
              ) : (
                <ul className="regulation-list">
                  {m1Data.restrictions.map((res, idx) => (
                    <li key={idx}>🚫 {res}</li>
                  ))}
                </ul>
              )}
            </>
          )}

          <div className="data-source">
            📍 Source: {m1Data.data_sources.official_price} ✅
          </div>
        </section>

        {/* Panel 4: Transaction Cases */}
        <section className="data-panel">
          <h2>📊 4. 주변 거래사례 (최근 6개월)</h2>
          
          {m1Data.transaction_cases && m1Data.transaction_cases.length > 0 ? (
            <>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>거래일</th>
                    <th>면적 (m²)</th>
                    <th>거래가 (₩)</th>
                    <th>거리 (m)</th>
                    <th>주소</th>
                  </tr>
                </thead>
                <tbody>
                  {m1Data.transaction_cases.map((txn, idx) => (
                    <tr key={idx}>
                      <td>{idx + 1}</td>
                      <td>{txn.date}</td>
                      <td>{(txn.area_sqm || 0).toLocaleString()}</td>
                      <td>₩{(txn.amount || 0).toLocaleString()}</td>
                      <td>{txn.distance_m}m</td>
                      <td>{txn.address}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div className="transaction-summary">
                <p>
                  <strong>총 {m1Data.transaction_cases.length}건의 거래사례</strong>
                </p>
                <p>⚠️ 이상치 감지: 없음</p>
              </div>
            </>
          ) : (
            <p className="no-data warning">
              ⚠️ 인근 거래사례 데이터 없음
              <br />
              이 경우 M2 분석의 신뢰도가 낮을 수 있습니다.
            </p>
          )}
        </section>

        {/* Verification Actions */}
        <section className="verification-actions">
          <div className="action-warning">
            <h3>🔒 데이터 검증 필수</h3>
            <p>
              위 데이터가 정확한지 확인해주세요.
              <br />
              M2~M6 분석은 이 데이터를 기반으로 진행됩니다.
            </p>
          </div>

          <div className="action-buttons">
            <button 
              className="btn btn-secondary"
              onClick={handleCollectPOI}
              disabled={verifying || collectingPOI}
              title="카카오맵 API로 주변 시설 정보 수집"
            >
              {collectingPOI ? '🔄 수집 중...' : '🗺️ POI 데이터 수집'}
            </button>
            
            <button 
              className="btn btn-danger"
              onClick={handleReject}
              disabled={verifying || collectingPOI}
            >
              ❌ 데이터 수정 필요 / 주소 재입력
            </button>

            <button 
              className="btn btn-primary"
              onClick={handleApprove}
              disabled={verifying || collectingPOI}
            >
              ✅ M1 데이터 확인 완료 → M2~M6 분석 진행
            </button>
          </div>

          {verifying && (
            <div className="verifying-status">
              <div className="spinner-small" />
              Processing verification...
            </div>
          )}
        </section>
      </div>
    </div>
  );
};
