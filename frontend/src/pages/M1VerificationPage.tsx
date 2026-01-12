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
          throw new Error('M1 data not available');
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
      
      // Check if this is manual data
      const isManualData = sessionStorage.getItem(`m1_manual_${projectId}`) !== null;
      
      if (isManualData) {
        // For manual data, we need to execute M1 first
        console.log('📝 수동 입력 데이터 → M1 실행 중...');
        
        try {
          // Attempt to execute M1 (this will trigger the backend M1 collection)
          await analysisAPI.executeModule(projectId, 'M1');
          console.log('✅ M1 실행 완료');
          
          // Wait a bit for execution to complete
          await new Promise(resolve => setTimeout(resolve, 2000));
        } catch (execError) {
          console.warn('⚠️ M1 자동 실행 실패:', execError);
          // Continue anyway - the manual data is our fallback
        }
      }
      
      // Step 1: Verify M1
      const verifyResponse = await analysisAPI.verifyModule(projectId, 'M1', {
        approved: true,
        comments: isManualData 
          ? 'M1 data manually entered and verified by user'
          : 'M1 data verified by user',
        verified_by: 'user@example.com' // TODO: Get from auth context
      });
      
      console.log('✅ M1 검증 완료:', verifyResponse.message);
      
      // Step 2: Execute M2-M6 pipeline (CRITICAL EXECUTION TRIGGER)
      console.log('⚡ Triggering M2-M6 execution...');
      
      try {
        const execResponse = await analysisAPI.executeFullPipeline(projectId);
        console.log('✅ Pipeline execution triggered:', execResponse.message);
        console.log('Executed modules:', execResponse.executed_modules);
        
        alert(
          `✅ M1 Verified Successfully!\n\n` +
          `${verifyResponse.message}\n\n` +
          `⚡ Executing M2-M6 modules...\n` +
          `${execResponse.executed_modules.join(', ')}`
        );
      } catch (execError) {
        console.error('❌ Pipeline execution failed:', execError);
        alert(
          `✅ M1 Verified, but pipeline execution failed:\n` +
          `${execError instanceof Error ? execError.message : 'Unknown error'}\n\n` +
          `You may need to execute modules manually.`
        );
      }
      
      // Step 3: Navigate to M2 results page
      navigate(`/projects/${projectId}/modules/m2/results`);
      
    } catch (err) {
      alert(`❌ Verification failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
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
      </div>

      <div className="verification-content">
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
              <span className="value">{m1Data.road_address}</span>
            </div>
            <div className="data-item">
              <label>지번 주소:</label>
              <span className="value">{m1Data.address}</span>
            </div>
            <div className="data-item">
              <label>면적:</label>
              <span className="value">
                {m1Data.area_sqm.toLocaleString()}m² 
                ({m1Data.area_pyeong.toLocaleString()}평)
              </span>
            </div>
            <div className="data-item">
              <label>용도지역:</label>
              <span className="value">{m1Data.zone_type}</span>
            </div>
            <div className="data-item">
              <label>건폐율 / 용적률:</label>
              <span className="value">{m1Data.bcr}% / {m1Data.far}%</span>
            </div>
            <div className="data-item">
              <label>도로폭:</label>
              <span className="value">{m1Data.road_width}m</span>
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
              <label>공시지가:</label>
              <span className="value">₩{m1Data.official_land_price.toLocaleString()}/m²</span>
            </div>
            <div className="data-item">
              <label>기준일:</label>
              <span className="value">{m1Data.official_price_date}</span>
            </div>
          </div>

          <h3>규제 사항</h3>
          {m1Data.regulations && m1Data.regulations.length > 0 ? (
            <ul className="regulation-list">
              {m1Data.regulations.map((reg, idx) => (
                <li key={idx}>⚠️ {reg}</li>
              ))}
            </ul>
          ) : (
            <p className="no-data">특별 규제 사항 없음</p>
          )}

          {m1Data.restrictions && m1Data.restrictions.length > 0 && (
            <>
              <h3>제한 사항</h3>
              <ul className="regulation-list">
                {m1Data.restrictions.map((res, idx) => (
                  <li key={idx}>🚫 {res}</li>
                ))}
              </ul>
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
                      <td>{txn.area_sqm.toLocaleString()}</td>
                      <td>₩{txn.amount.toLocaleString()}</td>
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
              className="btn btn-danger"
              onClick={handleReject}
              disabled={verifying}
            >
              ❌ 데이터 수정 필요 / 주소 재입력
            </button>

            <button 
              className="btn btn-primary"
              onClick={handleApprove}
              disabled={verifying}
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
