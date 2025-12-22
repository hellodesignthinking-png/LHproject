/**
 * M4 Capacity Results Display
 * ============================
 * 
 * CRITICAL: M4 shows BOTH alternatives side-by-side for COMPARISON ONLY
 * 
 * This is NOT a selection UI. User does NOT choose between alternatives.
 * Both alternatives are shown simultaneously:
 * - Legal FAR vs Incentive FAR capacity
 * - Alternative A (FAR MAX) vs Alternative B (Parking Priority)
 * 
 * M5 (Feasibility) uses BOTH alternatives automatically.
 * M6 (LH Review) is the FIRST decision point (GO/NO-GO).
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 */

import React from 'react';

interface M4ResultsDisplayProps {
  m4Result: any;
}

export const M4ResultsDisplay: React.FC<M4ResultsDisplayProps> = ({ m4Result }) => {
  if (!m4Result) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
        M4 결과 없음
      </div>
    );
  }

  // 🔥 CRITICAL: summary 필드만 사용 (canonical data contract)
  const summary = m4Result.summary || {};
  const details = m4Result.details || {};
  
  // Summary 데이터 (카드 표시용)
  const legalUnits = summary.legal_units ?? 0;
  const incentiveUnits = summary.incentive_units ?? 0;
  const parkingAltA = summary.parking_alt_a ?? 0;
  const parkingAltB = summary.parking_alt_b ?? 0;
  
  // Details 데이터 (상세 정보용 - 옵션)
  const legalCapacity = details.legal_capacity || {};
  const incentiveCapacity = details.incentive_capacity || {};
  const parkingSolutions = details.parking_solutions || {};
  const altA = parkingSolutions.alternative_A || {};
  const altB = parkingSolutions.alternative_B || {};

  return (
    <div className="m4-results-display" style={{ padding: '30px' }}>
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <div style={{ fontSize: '48px', marginBottom: '10px' }}>📐</div>
        <h2 style={{ margin: 0 }}>M4: 건축규모 분석 결과</h2>
        <p style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
          법정/인센티브 용적률 및 주차 대안 비교
        </p>
      </div>

      {/* FAR Capacity Comparison */}
      <div style={{ marginBottom: '40px' }}>
        <h3 style={{ 
          padding: '10px 15px', 
          background: '#f5f5f5', 
          borderRadius: '6px',
          marginBottom: '20px'
        }}>
          ① 용적률 기준 규모 비교
        </h3>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {/* Legal FAR */}
          <div style={{ 
            padding: '20px', 
            background: '#e3f2fd', 
            borderRadius: '8px',
            border: '2px solid #2196F3'
          }}>
            <h4 style={{ marginTop: 0, color: '#1976d2' }}>
              📘 법정 세대수
            </h4>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1976d2', margin: '15px 0' }}>
              {legalUnits > 0 ? `${legalUnits}세대` : 'N/A (검증 필요)'}
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>적용 용적률:</strong> {legalCapacity.applied_far || 'N/A'}%
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>적용 건폐율:</strong> {legalCapacity.applied_bcr || 'N/A'}%
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>목표 연면적:</strong> {legalCapacity.target_gfa_sqm ? (legalCapacity.target_gfa_sqm).toLocaleString() + '㎡' : 'N/A'}
              </div>
              <div>
                <strong>평균 세대면적:</strong> {legalCapacity.average_unit_area_sqm ? (legalCapacity.average_unit_area_sqm).toFixed(1) + '㎡' : 'N/A'}
              </div>
            </div>
          </div>

          {/* Incentive FAR */}
          <div style={{ 
            padding: '20px', 
            background: '#e8f5e9', 
            borderRadius: '8px',
            border: '2px solid #4CAF50'
          }}>
            <h4 style={{ marginTop: 0, color: '#2e7d32' }}>
              📗 인센티브 세대수
            </h4>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2e7d32', margin: '15px 0' }}>
              {incentiveUnits > 0 ? `${incentiveUnits}세대` : 'N/A (검증 필요)'}
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>적용 용적률:</strong> {incentiveCapacity.applied_far || 'N/A'}%
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>적용 건폐율:</strong> {incentiveCapacity.applied_bcr || 'N/A'}%
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>목표 연면적:</strong> {incentiveCapacity.target_gfa_sqm ? (incentiveCapacity.target_gfa_sqm).toLocaleString() + '㎡' : 'N/A'}
              </div>
              <div>
                <strong>평균 세대면적:</strong> {incentiveCapacity.average_unit_area_sqm ? (incentiveCapacity.average_unit_area_sqm).toFixed(1) + '㎡' : 'N/A'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Parking Solutions Comparison */}
      <div style={{ marginBottom: '40px' }}>
        <h3 style={{ 
          padding: '10px 15px', 
          background: '#f5f5f5', 
          borderRadius: '6px',
          marginBottom: '20px'
        }}>
          ② 주차 해결안 비교
        </h3>
        
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px'
        }}>
          {/* Alternative A: FAR MAX */}
          <div style={{ 
            padding: '20px', 
            background: '#fff3e0', 
            borderRadius: '8px',
            border: '2px solid #FF9800'
          }}>
            <h4 style={{ marginTop: 0, color: '#e65100' }}>
              🅰️ Alternative A: 용적률 최대화
            </h4>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#e65100', margin: '15px 0' }}>
              {parkingAltA > 0 ? `${parkingAltA}대` : 'N/A (검증 필요)'}
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>주차 방식:</strong> {altA.parking_type || 'N/A'}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>자주식:</strong> {altA.self_parking_spaces || 0}대
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>기계식:</strong> {altA.mechanical_parking_spaces || 0}대
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>지하층:</strong> {altA.basement_floors || 0}개층
              </div>
              <div>
                <strong>실현가능성:</strong> {altA.parking_achievability_score ? (altA.parking_achievability_score).toFixed(0) + '/100' : 'N/A'}
              </div>
            </div>
          </div>

          {/* Alternative B: Parking Priority */}
          <div style={{ 
            padding: '20px', 
            background: '#f3e5f5', 
            borderRadius: '8px',
            border: '2px solid #9C27B0'
          }}>
            <h4 style={{ marginTop: 0, color: '#6a1b9a' }}>
              🅱️ Alternative B: 주차 우선
            </h4>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#6a1b9a', margin: '15px 0' }}>
              {parkingAltB > 0 ? `${parkingAltB}대` : 'N/A (검증 필요)'}
            </div>
            <div style={{ fontSize: '14px', color: '#666' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>주차 방식:</strong> {altB.parking_type || 'N/A'}
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>자주식:</strong> {altB.self_parking_spaces || 0}대
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>기계식:</strong> {altB.mechanical_parking_spaces || 0}대
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>지하층:</strong> {altB.basement_floors || 0}개층
              </div>
              <div style={{ marginBottom: '8px' }}>
                <strong>실현가능성:</strong> {altB.parking_achievability_score ? (altB.parking_achievability_score).toFixed(0) + '/100' : 'N/A'}
              </div>
              {altB.far_sacrifice_ratio && (
                <div style={{ marginTop: '10px', padding: '8px', background: '#fff9c4', borderRadius: '4px' }}>
                  <strong>용적률 희생:</strong> {(altB.far_sacrifice_ratio * 100).toFixed(1)}%
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Schematic Drawings */}
      {details.schematic_drawing_paths && Object.keys(details.schematic_drawing_paths).length > 0 && (
        <div style={{ marginBottom: '40px' }}>
          <h3 style={{ 
            padding: '10px 15px', 
            background: '#f5f5f5', 
            borderRadius: '6px',
            marginBottom: '20px'
          }}>
            ③ 개략 도면 (4종)
          </h3>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '15px'
          }}>
            {Object.entries(details.schematic_drawing_paths).map(([drawingType, path]) => (
              <div 
                key={drawingType}
                style={{ 
                  padding: '15px', 
                  background: '#f9f9f9', 
                  borderRadius: '6px',
                  textAlign: 'center',
                  cursor: 'pointer',
                  border: '1px solid #ddd'
                }}
                onClick={() => window.open(path as string, '_blank')}
              >
                <div style={{ fontSize: '32px', marginBottom: '5px' }}>📄</div>
                <div style={{ fontSize: '12px', fontWeight: 'bold' }}>
                  {drawingType.replace(/_/g, ' ').toUpperCase()}
                </div>
                <div style={{ fontSize: '10px', color: '#999', marginTop: '3px' }}>
                  클릭하여 보기
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Important Note */}
      <div style={{ 
        padding: '20px', 
        background: '#fff3cd', 
        border: '2px solid #ffc107',
        borderRadius: '8px',
        marginTop: '30px'
      }}>
        <h4 style={{ marginTop: 0, color: '#856404' }}>⚠️ 중요: 대안 비교 화면입니다</h4>
        <ul style={{ marginBottom: 0, paddingLeft: '20px', color: '#856404', fontSize: '14px' }}>
          <li>이 화면은 <strong>비교 목적</strong>이며, 사용자가 대안을 선택하지 않습니다.</li>
          <li>M5 (사업성 분석)는 <strong>두 대안 모두</strong> 자동으로 사용합니다.</li>
          <li>M6 (LH 심사예측)에서 <strong>최초로 GO/NO-GO 결정</strong>이 이루어집니다.</li>
        </ul>
      </div>
    </div>
  );
};

export default M4ResultsDisplay;
