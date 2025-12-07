"""
Risk Enhancement Engine
=======================

Phase 2, Tasks 2.3, 2.4, 2.5: Enhanced Risk Analysis

This module provides comprehensive risk analysis:
- Task 2.3: Risk Matrix Visualization (Impact vs Probability)
- Task 2.4: Top 10 Risks + 3 Response Strategies each
- Task 2.5: Exit Strategy Scenarios (3 scenarios)

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0 (Phase 2)
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Risk:
    """Data structure for a single risk"""
    id: str
    name: str
    name_en: str
    category: str  # 'legal', 'financial', 'market', 'construction', 'operational'
    probability: int  # 1-5 (1=Very Low, 5=Very High)
    impact: int  # 1-5 (1=Very Low, 5=Very High)
    description: str
    response_strategies: List[str]  # 3 strategies
    
    @property
    def risk_score(self) -> int:
        """Calculate risk score (Probability × Impact)"""
        return self.probability * self.impact
    
    @property
    def risk_level(self) -> str:
        """Determine risk level based on score"""
        if self.risk_score >= 20:
            return 'CRITICAL'
        elif self.risk_score >= 12:
            return 'HIGH'
        elif self.risk_score >= 6:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    @property
    def risk_level_kr(self) -> str:
        """Korean risk level"""
        level_map = {
            'CRITICAL': '심각',
            'HIGH': '높음',
            'MEDIUM': '보통',
            'LOW': '낮음'
        }
        return level_map.get(self.risk_level, '알 수 없음')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'category': self.category,
            'category_kr': self._translate_category(),
            'probability': self.probability,
            'impact': self.impact,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'risk_level_kr': self.risk_level_kr,
            'description': self.description,
            'response_strategies': self.response_strategies
        }
    
    def _translate_category(self) -> str:
        """Translate category to Korean"""
        cat_map = {
            'legal': '법률/규제',
            'financial': '재무/자금',
            'market': '시장/수요',
            'construction': '건설/공사',
            'operational': '운영/관리'
        }
        return cat_map.get(self.category, self.category)


class RiskEnhancer:
    """
    Enhanced Risk Analysis Engine
    
    Phase 2, Tasks 2.3-2.5:
    - Risk Matrix Visualization
    - Top 10 Risks with Response Strategies
    - Exit Strategy Scenarios
    """
    
    def __init__(self):
        """Initialize risk enhancer"""
        logger.info("✅ RiskEnhancer initialized")
    
    def enhance_risk_analysis(
        self,
        base_risk_analysis: Dict[str, Any],
        finance_data: Dict[str, Any],
        market_data: Dict[str, Any],
        demand_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance risk analysis with Phase 2 components
        
        Args:
            base_risk_analysis: Basic risk analysis from Phase 1
            finance_data: Financial metrics
            market_data: Market analysis results
            demand_data: Demand analysis results
        
        Returns:
            Enhanced risk analysis with matrix, top 10 risks, and exit strategies
        """
        logger.info("🔍 Enhancing risk analysis (Phase 2)")
        
        # Identify top 10 risks
        top_risks = self._identify_top_risks(
            base_risk_analysis,
            finance_data,
            market_data,
            demand_data
        )
        
        # Generate risk matrix data
        risk_matrix = self._generate_risk_matrix(top_risks)
        
        # Generate exit strategies
        exit_strategies = self._generate_exit_strategies(
            finance_data,
            market_data,
            base_risk_analysis
        )
        
        enhanced_analysis = {
            'top_10_risks': [risk.to_dict() for risk in top_risks],
            'risk_matrix': risk_matrix,
            'exit_strategies': exit_strategies,
            'overall_risk_summary': self._generate_risk_summary(top_risks)
        }
        
        logger.info(f"✅ Risk enhancement complete: {len(top_risks)} risks identified")
        return enhanced_analysis
    
    def _identify_top_risks(
        self,
        base_risks: Dict[str, Any],
        finance: Dict[str, Any],
        market: Dict[str, Any],
        demand: Dict[str, Any]
    ) -> List[Risk]:
        """
        Phase 2, Task 2.4: Identify Top 10 Risks with 3 Response Strategies each
        
        Risk categories:
        1. Legal/Regulatory (법률/규제)
        2. Financial/Funding (재무/자금)
        3. Market/Demand (시장/수요)
        4. Construction (건설/공사)
        5. Operational/Management (운영/관리)
        """
        risks = []
        
        # Extract key metrics
        npv = finance.get('npv', {}).get('public', 0)
        irr = finance.get('irr', {}).get('public', 0)
        market_signal = market.get('signal', 'FAIR')
        demand_score = demand.get('overall_score', 60.0)
        
        # Risk 1: Financial Viability Risk (재무 타당성 리스크)
        if npv < 0:
            prob = 5 if npv < -100_000_000_00 else 4  # More probable if deeply negative
            impact = 5
            risks.append(Risk(
                id='R01',
                name='재무 타당성 부족',
                name_en='Financial Viability Risk',
                category='financial',
                probability=prob,
                impact=impact,
                description=f'NPV {npv/1e8:.1f}억원으로 사업 수익성 확보 실패. 투자 회수 불가능 위험',
                response_strategies=[
                    '사업 규모 확대 (필지 추가 매입) 또는 건축 규모 증대로 수익성 개선',
                    '공사비 절감 방안 검토 (설계 최적화, VE 적용)',
                    '임대료 상향 조정 또는 부대사업 도입으로 수익원 다각화'
                ]
            ))
        else:
            prob = 2
            impact = 3
            risks.append(Risk(
                id='R01',
                name='수익성 변동 리스크',
                name_en='Profitability Volatility',
                category='financial',
                probability=prob,
                impact=impact,
                description='시장 여건 변화에 따른 수익성 변동 가능성',
                response_strategies=[
                    '정기적인 수익성 모니터링 및 조기 경보 시스템 구축',
                    '비용 절감 및 수익 증대 방안 지속 발굴',
                    '시나리오별 대응 계획 사전 수립'
                ]
            ))
        
        # Risk 2: Market Demand Risk (시장 수요 리스크)
        if demand_score < 60:
            prob = 4
            impact = 4
            risks.append(Risk(
                id='R02',
                name='낮은 수요 리스크',
                name_en='Low Demand Risk',
                category='market',
                probability=prob,
                impact=impact,
                description=f'수요 점수 {demand_score:.0f}점으로 낮은 입주 수요 예상. 공실 장기화 우려',
                response_strategies=[
                    '타겟층 확대 (복수 주거 유형 혼합 운영)',
                    '임대료 탄력적 조정 및 입주 인센티브 제공',
                    '적극적인 마케팅 및 입주 유치 활동 강화'
                ]
            ))
        else:
            prob = 2
            impact = 3
            risks.append(Risk(
                id='R02',
                name='수요 변동 리스크',
                name_en='Demand Fluctuation',
                category='market',
                probability=prob,
                impact=impact,
                description='계절적/경기적 수요 변동 가능성',
                response_strategies=[
                    '다양한 계층 대상 마케팅으로 수요 기반 확대',
                    '우수한 주거 품질로 입주민 만족도 제고',
                    '장기 거주 유도 프로그램 운영'
                ]
            ))
        
        # Risk 3: Market Price Risk (시장 가격 리스크)
        if market_signal == 'OVERVALUED':
            prob = 5
            impact = 4
            risks.append(Risk(
                id='R03',
                name='시장 고평가 리스크',
                name_en='Market Overvaluation Risk',
                category='market',
                probability=prob,
                impact=impact,
                description='현재 시장 가격이 고평가 상태. 가격 하락 시 사업성 악화 우려',
                response_strategies=[
                    '취득 가격 재협상 또는 사업 보류/재검토',
                    '가격 하락 대비 수익 구조 강화 (비용 절감, 부대수익)',
                    '보수적 재무 가정 적용 및 리스크 완충 자금 확보'
                ]
            ))
        else:
            prob = 2
            impact = 3
            risks.append(Risk(
                id='R03',
                name='시장 가격 변동성',
                name_en='Market Price Volatility',
                category='market',
                probability=prob,
                impact=impact,
                description='부동산 시장 가격 변동에 따른 사업 가치 변화',
                response_strategies=[
                    '시장 가격 모니터링 및 정기 재평가',
                    '장기 안정적 수익 구조 구축',
                    '시장 변동성 대비 재무 완충 장치 마련'
                ]
            ))
        
        # Risk 4: Construction Cost Overrun (공사비 증가 리스크)
        prob = 4
        impact = 4
        risks.append(Risk(
            id='R04',
            name='공사비 증가 리스크',
            name_en='Construction Cost Overrun',
            category='construction',
            probability=prob,
            impact=impact,
            description='자재비 상승, 인건비 증가 등으로 공사비 예산 초과 가능성',
            response_strategies=[
                '상세 설계를 통한 공사비 정밀 산출 및 예비비 확보',
                '자재 가격 고정 계약 또는 헤지 전략 활용',
                'CM/VE 적용으로 설계 최적화 및 비용 절감'
            ]
        ))
        
        # Risk 5: Construction Delay (공사 지연 리스크)
        prob = 3
        impact = 4
        risks.append(Risk(
            id='R05',
            name='공사 지연 리스크',
            name_en='Construction Delay Risk',
            category='construction',
            probability=prob,
            impact=impact,
            description='기상, 인력, 자재 수급 등 문제로 공사 기간 지연 가능성',
            response_strategies=[
                '상세 공정표 작성 및 주요 일정 버퍼 확보',
                '우수 시공사 선정 및 엄격한 공정 관리',
                '대체 자재/인력 공급망 사전 확보'
            ]
        ))
        
        # Risk 6: Regulatory/Permit Risk (인허가 리스크)
        prob = 3
        impact = 5
        risks.append(Risk(
            id='R06',
            name='인허가 지연/불허 리스크',
            name_en='Permit/Regulatory Risk',
            category='legal',
            probability=prob,
            impact=impact,
            description='건축허가, 용도변경 등 인허가 과정에서 지연 또는 불허 가능성',
            response_strategies=[
                '사전 인허가 컨설팅 및 관계 기관 협의 강화',
                '대안 설계 방안 사전 준비',
                '법률/규제 변화 모니터링 및 선제 대응'
            ]
        ))
        
        # Risk 7: Funding Risk (자금 조달 리스크)
        prob = 3
        impact = 4
        risks.append(Risk(
            id='R07',
            name='자금 조달 리스크',
            name_en='Funding/Financing Risk',
            category='financial',
            probability=prob,
            impact=impact,
            description='금리 상승, 대출 심사 강화 등으로 자금 조달 차질 가능성',
            response_strategies=[
                '복수 금융기관 대출 협의 및 자금 조달 계획 다변화',
                'LH 재원 활용 극대화 및 정책 자금 적극 활용',
                '단계별 자금 소요 계획 수립 및 조기 집행'
            ]
        ))
        
        # Risk 8: Occupancy Risk (입주율 리스크)
        prob = 3
        impact = 4
        risks.append(Risk(
            id='R08',
            name='낮은 입주율 리스크',
            name_en='Low Occupancy Risk',
            category='operational',
            probability=prob,
            impact=impact,
            description='완공 후 입주율 저조로 수익 감소 및 NOI 하락 우려',
            response_strategies=[
                '입주 전 사전 마케팅 및 예약 입주 유도',
                '초기 입주 인센티브 제공 (임대료 할인, 이사 비용 지원)',
                '우수한 주거 환경 및 서비스로 구전 효과 창출'
            ]
        ))
        
        # Risk 9: Operational Management Risk (운영 관리 리스크)
        prob = 2
        impact = 3
        risks.append(Risk(
            id='R09',
            name='운영 관리 리스크',
            name_en='Operational Management Risk',
            category='operational',
            probability=prob,
            impact=impact,
            description='시설 관리, 입주민 관리 등 운영 단계에서의 문제 발생 가능성',
            response_strategies=[
                '전문 운영 관리 업체 선정 및 체계적 관리 시스템 구축',
                '입주민 만족도 조사 및 피드백 반영 체계 마련',
                '시설 유지보수 계획 수립 및 예산 확보'
            ]
        ))
        
        # Risk 10: Exit Difficulty Risk (출구 전략 리스크)
        prob = 3
        impact = 3
        risks.append(Risk(
            id='R10',
            name='출구 전략 리스크',
            name_en='Exit Strategy Risk',
            category='financial',
            probability=prob,
            impact=impact,
            description='매각 또는 자산 처분 시 적절한 매수자 확보 어려움 또는 낮은 매각가',
            response_strategies=[
                '사업 초기부터 출구 전략 수립 및 정기 검토',
                '자산 가치 제고를 위한 지속적 관리 및 개선',
                '복수 출구 시나리오 (LH 장기 보유, 기관 매각, 리츠 편입 등) 준비'
            ]
        ))
        
        # Sort by risk score (highest first)
        risks_sorted = sorted(risks, key=lambda r: r.risk_score, reverse=True)
        
        return risks_sorted[:10]  # Top 10
    
    def _generate_risk_matrix(self, risks: List[Risk]) -> Dict[str, Any]:
        """
        Phase 2, Task 2.3: Risk Matrix Visualization Data
        
        Generate data for 5x5 risk matrix (Probability vs Impact)
        """
        # Create 5x5 matrix
        matrix = [[[] for _ in range(5)] for _ in range(5)]
        
        # Place risks in matrix
        for risk in risks:
            prob_idx = risk.probability - 1  # Convert 1-5 to 0-4
            impact_idx = risk.impact - 1
            matrix[prob_idx][impact_idx].append({
                'id': risk.id,
                'name': risk.name,
                'risk_score': risk.risk_score
            })
        
        # Count risks by level
        risk_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for risk in risks:
            risk_counts[risk.risk_level] += 1
        
        return {
            'matrix': matrix,
            'axis_labels': {
                'probability': ['매우 낮음', '낮음', '보통', '높음', '매우 높음'],
                'impact': ['매우 낮음', '낮음', '보통', '높음', '매우 높음']
            },
            'risk_counts': risk_counts,
            'total_risks': len(risks)
        }
    
    def _generate_exit_strategies(
        self,
        finance: Dict[str, Any],
        market: Dict[str, Any],
        base_risks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phase 2, Task 2.5: Exit Strategy Scenarios
        
        Generate 3 exit strategy scenarios:
        1. Planned Exit (계획된 출구)
        2. Early Exit (조기 출구)
        3. Distressed Exit (비상 출구)
        """
        npv = finance.get('npv', {}).get('public', 0)
        capex = finance.get('capex', {}).get('total', 1)
        
        strategies = []
        
        # Strategy 1: Planned Exit (10-year hold)
        strategies.append({
            'scenario': 'planned_exit',
            'scenario_kr': '계획된 출구 (10년 보유)',
            'timeline': '10년 후 (2035년)',
            'conditions': [
                '안정적인 운영 실적 (평균 입주율 95% 이상)',
                '자산 가치 유지 또는 증대',
                '시장 여건 양호 (임대시장 안정)'
            ],
            'exit_methods': [
                {
                    'method': 'LH 장기 보유',
                    'description': 'LH가 임대주택으로 계속 운영. 안정적 현금흐름 확보',
                    'pros': ['안정적 수익', '정책 목적 달성', '운영 리스크 최소화'],
                    'cons': ['자본 회수 지연', '기회비용 발생']
                },
                {
                    'method': '기관투자자 매각',
                    'description': '연기금, 보험사 등 기관투자자에게 매각',
                    'pros': ['자본 회수', '안정적 매수 주체', '공정한 가격 형성'],
                    'cons': ['매각 절차 소요', '시장 여건 영향']
                },
                {
                    'method': '리츠(REITs) 편입',
                    'description': '부동산 투자회사(리츠)에 편입하여 유동화',
                    'pros': ['유동성 확보', '분산 투자', '지속적 관리'],
                    'cons': ['리츠 시장 여건 의존', '가격 변동성']
                }
            ],
            'expected_value': capex * 1.1,  # 10% appreciation over 10 years
            'expected_value_kr': f"{capex * 1.1 / 1e8:.1f}억원"
        })
        
        # Strategy 2: Early Exit (3-5 year)
        strategies.append({
            'scenario': 'early_exit',
            'scenario_kr': '조기 출구 (3-5년 보유)',
            'timeline': '3-5년 후 (2028-2030년)',
            'conditions': [
                '예상보다 빠른 사업 안정화',
                '시장 호황으로 높은 매각가 기대',
                '자금 회전 필요성 발생'
            ],
            'exit_methods': [
                {
                    'method': '프로젝트 금융 상환 후 매각',
                    'description': '대출 조기 상환 후 자산 매각',
                    'pros': ['조기 자본 회수', '시장 호황기 활용', '높은 수익률 가능'],
                    'cons': ['조기 상환 수수료', '짧은 운영 실적']
                },
                {
                    'method': '프로젝트 인수 (Project Takeover)',
                    'description': '개발사 또는 운영사에 프로젝트 전체 이전',
                    'pros': ['신속한 거래', '일괄 처리', '협상 여지'],
                    'cons': ['가격 할인 가능성', '매수자 확보 어려움']
                }
            ],
            'expected_value': capex * 1.05,  # 5% appreciation
            'expected_value_kr': f"{capex * 1.05 / 1e8:.1f}억원"
        })
        
        # Strategy 3: Distressed Exit (Emergency)
        strategies.append({
            'scenario': 'distressed_exit',
            'scenario_kr': '비상 출구 (긴급 처분)',
            'timeline': '즉시 ~ 2년 내',
            'conditions': [
                '심각한 사업 부진 (입주율 70% 미만 지속)',
                '재무적 어려움 (자금 조달 실패, 부채 상환 곤란)',
                '정책 변경 또는 규제 강화로 사업 지속 불가'
            ],
            'exit_methods': [
                {
                    'method': '할인 매각 (Distressed Sale)',
                    'description': '시장가 이하로 신속히 매각',
                    'pros': ['신속한 자금 확보', '손실 확정 및 재기 기회'],
                    'cons': ['큰 손실 발생', '브랜드 이미지 타격']
                },
                {
                    'method': '공공 기관 인수',
                    'description': 'LH 또는 지자체가 공공 목적으로 인수',
                    'pros': ['사회적 목적 달성', '안정적 거래'],
                    'cons': ['낮은 매각가', '협상 제한']
                },
                {
                    'method': '자산 재구조화',
                    'description': '부채 조정, 지분 재배치 등 구조 개편',
                    'pros': ['사업 지속 가능성', '일부 자본 보존'],
                    'cons': ['복잡한 절차', '불확실성']
                }
            ],
            'expected_value': capex * 0.8,  # 20% loss
            'expected_value_kr': f"{capex * 0.8 / 1e8:.1f}억원"
        })
        
        return {
            'strategies': strategies,
            'recommendation': self._recommend_exit_strategy(npv, base_risks),
            'total_scenarios': len(strategies)
        }
    
    def _recommend_exit_strategy(self, npv: float, base_risks: Dict[str, Any]) -> str:
        """Recommend primary exit strategy based on project conditions"""
        overall_risk = base_risks.get('overall_level', 'MEDIUM')
        
        if npv > 0 and overall_risk == 'LOW':
            return "계획된 출구 전략 (10년 장기 보유) 권장. 안정적 수익 구조 확보 가능"
        elif npv > 0:
            return "계획된 출구 + 조기 출구 옵션 병행. 시장 여건 모니터링하며 최적 시점 포착"
        else:
            return "조기 출구 전략 수립 필수. 사업 개선 후 3-5년 내 매각 목표 설정"
    
    def _generate_risk_summary(self, risks: List[Risk]) -> Dict[str, Any]:
        """Generate overall risk summary"""
        if not risks:
            return {'total_risks': 0, 'average_score': 0, 'summary': '리스크 정보 없음'}
        
        total_score = sum(r.risk_score for r in risks)
        avg_score = total_score / len(risks)
        
        critical_risks = [r for r in risks if r.risk_level == 'CRITICAL']
        high_risks = [r for r in risks if r.risk_level == 'HIGH']
        
        if critical_risks:
            summary = f"심각 리스크 {len(critical_risks)}개 존재. 즉각적인 대응 조치 필요"
        elif high_risks:
            summary = f"높은 리스크 {len(high_risks)}개 존재. 적극적 리스크 관리 필요"
        else:
            summary = "관리 가능한 수준의 리스크. 정기적 모니터링 권장"
        
        return {
            'total_risks': len(risks),
            'average_score': round(avg_score, 1),
            'critical_count': len(critical_risks),
            'high_count': len(high_risks),
            'summary': summary
        }
