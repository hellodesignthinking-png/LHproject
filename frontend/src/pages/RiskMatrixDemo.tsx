/**
 * Risk Matrix Demo Page
 * Phase 4: Frontend Visualization - Task 2
 * 
 * Demo page showing Risk Matrix component with sample data
 */

import React, { useState, useEffect } from 'react';
import RiskMatrixGrid from '../components/RiskMatrix/RiskMatrixGrid';
import { RiskMatrixData, Risk } from '../components/RiskMatrix/types';
import { calculateRiskLevel } from '../components/RiskMatrix/utils';

/**
 * Sample risk data for testing
 * Based on actual Phase 2 test output
 */
const SAMPLE_RISKS: Risk[] = [
  {
    id: 'R01',
    name: '재무 타당성 부족',
    category: 'financial',
    probability: 5,
    impact: 5,
    risk_score: 25,
    risk_level: 'CRITICAL',
    description: 'NPV -131.7억원으로 사업 수익성 확보 실패. 투자 회수 불가능 위험',
    response_strategies: [
      '사업 규모 확대 (600㎡ → 800㎡+) 통한 수익성 개선',
      '공사비 절감 방안 검토 (VE, 자재 선정 최적화)',
      '임대료 상향 조정 또는 부대사업 도입 (편의점, 카페 등)'
    ]
  },
  {
    id: 'R02',
    name: '공사비 증가 리스크',
    category: 'construction',
    probability: 4,
    impact: 4,
    risk_score: 16,
    risk_level: 'HIGH',
    description: '자재비·인건비 상승, 설계 변경으로 공사비 10~20% 증가 가능',
    response_strategies: [
      '정밀 공사비 산정 및 예비비 15% 확보',
      '주요 자재 고정가 계약 체결',
      'CM/VE 적용으로 설계 최적화'
    ]
  },
  {
    id: 'R03',
    name: '인허가 지연/불허 리스크',
    category: 'legal',
    probability: 3,
    impact: 5,
    risk_score: 15,
    risk_level: 'HIGH',
    description: '건축 심의, 용도 변경 지연 또는 불허 시 사업 일정 6개월+ 지연',
    response_strategies: [
      '건축 전 사전협의 철저 진행',
      '대체 설계안 2개 이상 준비',
      '지자체 조례 개정 동향 지속 모니터링'
    ]
  },
  {
    id: 'R04',
    name: '공사 지연 리스크',
    category: 'construction',
    probability: 3,
    impact: 4,
    risk_score: 12,
    risk_level: 'HIGH',
    description: '공정 지연, 날씨, 민원으로 준공 3~6개월 지연 가능',
    response_strategies: [
      '세부 공정표 작성 및 주간 점검',
      '우수 시공사 선정 (유사 실적 확인)',
      '대체 자재 공급망 확보'
    ]
  },
  {
    id: 'R05',
    name: '자금 조달 리스크',
    category: 'financial',
    probability: 3,
    impact: 4,
    risk_score: 12,
    risk_level: 'HIGH',
    description: 'PF 금리 상승 또는 대출 조건 악화로 자금 조달 실패 가능',
    response_strategies: [
      '복수 금융기관과 사전 협의',
      'LH 정책자금 활용 (저금리 2.87%)',
      '단계별 자금 조달 계획 수립'
    ]
  },
  {
    id: 'R06',
    name: '시장 수요 부족',
    category: 'market',
    probability: 4,
    impact: 3,
    risk_score: 12,
    risk_level: 'HIGH',
    description: '청년 인구 감소, 경쟁 심화로 입주율 목표(92.5%) 미달 가능',
    response_strategies: [
      '타겟 확대 (청년 → 신혼부부, 1인 가구)',
      '유연한 가격 정책 (초기 할인, 장기 계약 우대)',
      '차별화된 편의시설 제공 (공유 오피스, 피트니스)'
    ]
  },
  {
    id: 'R07',
    name: '운영 관리 리스크',
    category: 'operational',
    probability: 3,
    impact: 3,
    risk_score: 9,
    risk_level: 'MEDIUM',
    description: '시설 노후화, 입주자 민원, 관리비 증가로 운영 효율 저하',
    response_strategies: [
      '전문 PM(Property Management) 업체 위탁',
      '정기 점검 및 예방 정비 시스템 구축',
      '입주자 커뮤니티 활성화'
    ]
  },
  {
    id: 'R08',
    name: '정책 변경 리스크',
    category: 'legal',
    probability: 2,
    impact: 4,
    risk_score: 8,
    risk_level: 'MEDIUM',
    description: 'LH 신축매입임대 정책 축소, 지원 조건 변경 가능',
    response_strategies: [
      '정책 변경 시나리오별 대응 계획 수립',
      '민간 임대로 전환 가능한 설계 반영',
      'LH 외 SH, 지방 공기업과 협력 다각화'
    ]
  },
  {
    id: 'R09',
    name: '경쟁 심화 리스크',
    category: 'market',
    probability: 3,
    impact: 2,
    risk_score: 6,
    risk_level: 'MEDIUM',
    description: '인근 신규 청년주택 공급으로 경쟁 심화',
    response_strategies: [
      '차별화된 브랜딩 (프리미엄 청년주택)',
      '특화 서비스 제공 (생활 편의, IT 인프라)',
      '조기 입주자 유치 마케팅 강화'
    ]
  },
  {
    id: 'R10',
    name: '환경·안전 리스크',
    category: 'construction',
    probability: 2,
    impact: 3,
    risk_score: 6,
    risk_level: 'MEDIUM',
    description: '공사 중 안전사고, 환경 민원 발생 가능',
    response_strategies: [
      '안전관리 계획 수립 및 일일 점검',
      '소음·분진 저감 공법 적용',
      '인근 주민 사전 설명회 개최'
    ]
  }
];

/**
 * Generate risk matrix data from sample risks
 */
const generateMatrixData = (risks: Risk[]): RiskMatrixData => {
  // Initialize 5x5 matrix (impact 5 to 1, probability 1 to 5)
  const matrix = [];
  for (let impact = 5; impact >= 1; impact--) {
    const row = [];
    for (let probability = 1; probability <= 5; probability++) {
      const cellRisks = risks.filter(
        r => r.probability === probability && r.impact === impact
      );
      const level = calculateRiskLevel(probability, impact);
      
      row.push({
        probability,
        impact,
        risks: cellRisks,
        count: cellRisks.length,
        level
      });
    }
    matrix.push(row);
  }

  // Calculate risk counts by level
  const risk_counts = {
    CRITICAL: risks.filter(r => r.risk_level === 'CRITICAL').length,
    HIGH: risks.filter(r => r.risk_level === 'HIGH').length,
    MEDIUM: risks.filter(r => r.risk_level === 'MEDIUM').length,
    LOW: risks.filter(r => r.risk_level === 'LOW').length
  };

  return {
    matrix,
    axis_labels: {
      x_label: '발생확률',
      y_label: '영향도',
      x_values: ['1', '2', '3', '4', '5'],
      y_values: ['5', '4', '3', '2', '1']
    },
    risk_counts,
    total_risks: risks.length
  };
};

const RiskMatrixDemo: React.FC = () => {
  const [matrixData, setMatrixData] = useState<RiskMatrixData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const data = generateMatrixData(SAMPLE_RISKS);
      setMatrixData(data);
      setLoading(false);
    }, 500);
  }, []);

  const handleRiskClick = (risk: Risk) => {
    console.log('Risk clicked:', risk);
    // In real app, could navigate to risk detail page or trigger other actions
  };

  if (loading) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center',
        fontSize: '18px',
        color: '#6b7280'
      }}>
        <div style={{ marginBottom: '16px' }}>⏳ 리스크 매트릭스 로딩 중...</div>
        <div style={{ fontSize: '14px' }}>잠시만 기다려주세요</div>
      </div>
    );
  }

  if (!matrixData) {
    return (
      <div style={{ 
        padding: '40px', 
        textAlign: 'center',
        fontSize: '18px',
        color: '#dc2626'
      }}>
        ❌ 데이터를 불러올 수 없습니다
      </div>
    );
  }

  return (
    <div style={{ 
      padding: '40px',
      background: '#f3f4f6',
      minHeight: '100vh'
    }}>
      <div style={{ 
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        {/* Page header */}
        <div style={{ 
          marginBottom: '32px',
          textAlign: 'center'
        }}>
          <h1 style={{ 
            fontSize: '36px',
            fontWeight: 'bold',
            color: '#1f2937',
            margin: '0 0 12px 0'
          }}>
            🎯 리스크 매트릭스 데모
          </h1>
          <p style={{ 
            fontSize: '16px',
            color: '#6b7280',
            margin: 0
          }}>
            Phase 4: Frontend Visualization - Interactive 5×5 Risk Matrix Grid
          </p>
        </div>

        {/* Risk Matrix Component */}
        <RiskMatrixGrid
          data={matrixData}
          onRiskClick={handleRiskClick}
          showLegend={true}
        />

        {/* Statistics section */}
        <div style={{ 
          marginTop: '32px',
          padding: '24px',
          background: 'white',
          borderRadius: '12px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ 
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#1f2937',
            marginBottom: '16px'
          }}>
            📊 리스크 통계
          </h3>
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            <StatCard 
              label="총 리스크" 
              value={matrixData.total_risks}
              color="#3b82f6"
            />
            <StatCard 
              label="매우 높음" 
              value={matrixData.risk_counts.CRITICAL}
              color="#dc2626"
            />
            <StatCard 
              label="높음" 
              value={matrixData.risk_counts.HIGH}
              color="#ea580c"
            />
            <StatCard 
              label="보통" 
              value={matrixData.risk_counts.MEDIUM}
              color="#ca8a04"
            />
            <StatCard 
              label="낮음" 
              value={matrixData.risk_counts.LOW}
              color="#16a34a"
            />
          </div>
        </div>

        {/* Instructions */}
        <div style={{ 
          marginTop: '32px',
          padding: '20px',
          background: '#eff6ff',
          border: '2px solid #3b82f6',
          borderRadius: '8px'
        }}>
          <h4 style={{ 
            fontSize: '16px',
            fontWeight: 'bold',
            color: '#1e40af',
            marginBottom: '12px'
          }}>
            💡 사용 방법
          </h4>
          <ul style={{ 
            margin: 0,
            paddingLeft: '20px',
            color: '#1e40af',
            fontSize: '14px',
            lineHeight: '1.8'
          }}>
            <li>매트릭스 셀 위에 마우스를 올리면 해당 셀의 상세 정보를 볼 수 있습니다</li>
            <li>리스크가 있는 셀을 클릭하면 해당 리스크의 상세 정보를 확인할 수 있습니다</li>
            <li>한 셀에 여러 리스크가 있는 경우, 리스크 목록이 먼저 표시됩니다</li>
            <li>리스크 상세 모달에서 대응 전략을 확인할 수 있습니다</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

/**
 * Stat card component
 */
const StatCard: React.FC<{ label: string; value: number; color: string }> = ({ 
  label, 
  value, 
  color 
}) => {
  return (
    <div style={{ 
      padding: '16px',
      background: '#f9fafb',
      border: '2px solid #e5e7eb',
      borderRadius: '8px',
      textAlign: 'center'
    }}>
      <div style={{ 
        fontSize: '32px',
        fontWeight: 'bold',
        color,
        marginBottom: '8px'
      }}>
        {value}
      </div>
      <div style={{ 
        fontSize: '14px',
        color: '#6b7280',
        fontWeight: '600'
      }}>
        {label}
      </div>
    </div>
  );
};

export default RiskMatrixDemo;
