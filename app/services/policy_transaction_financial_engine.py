"""
ZeroSite v17 - Policy Transaction Financial Engine
정책형 신축매입임대 사업성 평가 엔진 (거래형 모델)

핵심 개념:
- **거래형 수익 모델**: LH에게 "건물을 지어 판매"하는 구조
- **최종 감정평가 매입가**가 수익을 결정 (운영 수익이 아님)
- **거래 수익 = LH 매입가 - 총 CAPEX**
- LH 감정평가 메커니즘 시뮬레이션 (토지+건물 85-95% 인정)
- 공사비 연동제 반영 (건축비 리스크 최소화)

사업 구조:
1. 사업자가 토지 매입 + 건축
2. 완공 후 LH가 감정평가
3. LH가 감정평가액 기준으로 매입
4. 사업자는 매입가로 CAPEX 회수 + 수익 실현
5. 이후 LH가 30년 임대운영 (사업자 무관)

**중요**: 이 모델은 민간형 30년 임대운영 모델(PrivateRentalFinancialEngine)과 완전히 다릅니다.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AppraisalResult:
    """감정평가 결과"""
    land_appraisal: float  # 토지 감정가액
    building_appraisal: float  # 건물 감정가액
    total_appraisal: float  # 총 감정가액
    appraisal_rate: float  # 감정평가율 (CAPEX 대비)
    
    
@dataclass
class PolicyFinancialResult:
    """정책형 재무 분석 결과"""
    # CAPEX
    capex_total: float
    land_cost: float
    construction_cost: float
    
    # 감정평가
    appraisal: AppraisalResult
    
    # 최종 매입가
    final_purchase_price: float
    internal_adjustment_rate: float
    
    # 정책형 수익성
    policy_npv: float  # 매입가 - CAPEX
    policy_irr: float  # (매입가 - CAPEX) / CAPEX
    
    # 민간형 수익성 (비교용)
    private_npv: float
    private_irr: float
    
    # 판단
    decision: str  # GO / CONDITIONAL_GO / NO_GO
    decision_reason: str


class PolicyFinancialEngine:
    """
    정책형 거래 재무 평가 엔진 (LH 신축매입임대 전용)
    
    LH 신축매입임대 사업의 실제 메커니즘을 반영:
    1. **거래형 수익 모델**: 건물 매각이 수익원 (운영 수익 아님)
    2. **감정평가 기반 최종 매입가 결정**: LH 감정평가 85-95% 적용
    3. **공사비 연동제 적용**: 건축비 변동 리스크 최소화
    4. **거래 수익 = LH 매입가 - CAPEX**: 단순하고 명확한 구조
    5. **Policy NPV/IRR**: 30년 운영 IRR이 아닌 거래 수익률
    
    **사업자 입장**: 
    - "LH에게 건물을 지어 판매" → 매입가 수령 → 사업 종료
    - 이후 LH가 30년 임대운영 (사업자 무관)
    
    **민간형과의 차이**:
    - 민간형: 30년 임대운영 수익으로 회수 (PrivateRentalFinancialEngine)
    - 정책형: LH 매입가로 즉시 회수 (PolicyTransactionFinancialEngine)
    """
    
    def __init__(self):
        # LH 감정평가 파라미터
        self.land_appraisal_rate_range = (0.85, 0.95)  # 토지: 공시지가 대비 85-95%
        self.building_appraisal_rate_range = (0.85, 0.95)  # 건물: 표준건축비 대비 85-95%
        
        # LH 내부 조정 파라미터
        self.internal_adjustment_range = (0.95, 1.05)  # ±5% 범위
        
        # 공사비 연동제 파라미터
        self.construction_index_adjustment = 1.0  # 기본값 (시장 변동 없음)
        
    def calculate_appraisal_value(
        self,
        land_cost: float,
        construction_cost: float,
        appraisal_rate: float = 0.90
    ) -> AppraisalResult:
        """
        감정평가 금액 산정
        
        LH 감정평가 메커니즘:
        - 토지: 공시지가 기준 × 시가반영률 (85-95%)
        - 건물: 표준건축비 × 감정평가 조정률 (85-95%)
        
        Args:
            land_cost: 토지비
            construction_cost: 건축비
            appraisal_rate: 감정평가율 (기본값 90%)
            
        Returns:
            AppraisalResult 객체
        """
        # 토지 감정가액 (공시지가 기준이므로 시장가보다 낮게 평가)
        land_appraisal = land_cost * appraisal_rate
        
        # 건물 감정가액 (실제 공사비의 85-95% 인정)
        building_appraisal = construction_cost * appraisal_rate
        
        # 총 감정가액
        total_appraisal = land_appraisal + building_appraisal
        
        # 총 CAPEX 대비 감정평가율
        total_capex = land_cost + construction_cost
        appraisal_rate_actual = total_appraisal / total_capex if total_capex > 0 else 0
        
        logger.info(f"💰 감정평가: 토지 {land_appraisal/1e8:.1f}억 + 건물 {building_appraisal/1e8:.1f}억 = 총 {total_appraisal/1e8:.1f}억 (감정평가율 {appraisal_rate_actual*100:.1f}%)")
        
        return AppraisalResult(
            land_appraisal=land_appraisal,
            building_appraisal=building_appraisal,
            total_appraisal=total_appraisal,
            appraisal_rate=appraisal_rate_actual
        )
    
    def calculate_final_purchase_price(
        self,
        appraisal_value: float,
        internal_adjustment: float = 1.0
    ) -> float:
        """
        최종 매입가 결정
        
        LH 내부 심사 과정:
        - 감정평가액 기준
        - 내부 조정 ±5% (예산, 정책 우선순위 등)
        
        Args:
            appraisal_value: 감정평가액
            internal_adjustment: 내부 조정률 (0.95 ~ 1.05)
            
        Returns:
            최종 매입가
        """
        final_price = appraisal_value * internal_adjustment
        
        logger.info(f"🏢 최종 매입가: {final_price/1e8:.1f}억 (감정가 {appraisal_value/1e8:.1f}억 × 조정률 {internal_adjustment*100:.1f}%)")
        
        return final_price
    
    def apply_construction_indexing(
        self,
        construction_cost: float,
        market_index_change: float = 0.0
    ) -> float:
        """
        공사비 연동제 적용
        
        2024년 LH 신축매입임대는 건축비 연동제 적용:
        - 시장 건축비 변동 자동 반영
        - 사업자의 건축비 리스크 최소화
        
        Args:
            construction_cost: 기준 건축비
            market_index_change: 시장 건축비 변동률 (예: 0.05 = 5% 상승)
            
        Returns:
            조정된 건축비
        """
        adjusted_cost = construction_cost * (1 + market_index_change)
        
        if market_index_change != 0:
            logger.info(f"🏗️ 공사비 연동제: {construction_cost/1e8:.1f}억 → {adjusted_cost/1e8:.1f}억 (변동률 {market_index_change*100:+.1f}%)")
        
        return adjusted_cost
    
    def evaluate(
        self,
        capex_data: Dict[str, Any],
        appraisal_rate: float = 0.90,
        internal_adjustment: float = 1.0,
        construction_index_change: float = 0.0,
        private_npv: float = 0.0,
        private_irr: float = 0.0
    ) -> PolicyFinancialResult:
        """
        정책형 사업성 종합 평가
        
        Args:
            capex_data: CAPEX 데이터 (land, construction, total 등)
            appraisal_rate: 감정평가율 (0.85 ~ 0.95)
            internal_adjustment: 내부 조정률 (0.95 ~ 1.05)
            construction_index_change: 건축비 변동률
            private_npv: 민간형 NPV (비교용)
            private_irr: 민간형 IRR (비교용)
            
        Returns:
            PolicyFinancialResult 객체
        """
        logger.info("=" * 60)
        logger.info("🏛️ 정책형 재무 평가 시작 (LH 신축매입임대 메커니즘)")
        logger.info("=" * 60)
        
        # 1. CAPEX 추출
        land_cost = capex_data.get('land', 0)
        construction_cost = capex_data.get('construction', 0)
        capex_total = capex_data.get('total', land_cost + construction_cost)
        
        logger.info(f"📊 CAPEX: 토지 {land_cost/1e8:.1f}억 + 건축 {construction_cost/1e8:.1f}억 = 총 {capex_total/1e8:.1f}억")
        
        # 2. 공사비 연동제 적용
        adjusted_construction_cost = self.apply_construction_indexing(
            construction_cost,
            construction_index_change
        )
        
        # 3. 감정평가 금액 산정
        appraisal = self.calculate_appraisal_value(
            land_cost,
            adjusted_construction_cost,
            appraisal_rate
        )
        
        # 4. 최종 매입가 결정
        final_purchase_price = self.calculate_final_purchase_price(
            appraisal.total_appraisal,
            internal_adjustment
        )
        
        # 5. 정책형 수익성 계산
        policy_npv = final_purchase_price - capex_total
        policy_irr = (policy_npv / capex_total) if capex_total > 0 else 0
        
        logger.info(f"✅ 정책형 NPV: {policy_npv/1e8:.1f}억 (매입가 {final_purchase_price/1e8:.1f}억 - CAPEX {capex_total/1e8:.1f}억)")
        logger.info(f"✅ 정책형 IRR: {policy_irr*100:.2f}% (NPV / CAPEX)")
        
        # 6. 의사결정
        decision, reason = self._make_decision(
            policy_npv,
            policy_irr,
            appraisal_rate,
            private_npv,
            private_irr
        )
        
        logger.info(f"🎯 판단: {decision}")
        logger.info(f"📝 근거: {reason}")
        logger.info("=" * 60)
        
        return PolicyFinancialResult(
            capex_total=capex_total,
            land_cost=land_cost,
            construction_cost=construction_cost,
            appraisal=appraisal,
            final_purchase_price=final_purchase_price,
            internal_adjustment_rate=internal_adjustment,
            policy_npv=policy_npv,
            policy_irr=policy_irr,
            private_npv=private_npv,
            private_irr=private_irr,
            decision=decision,
            decision_reason=reason
        )
    
    def _make_decision(
        self,
        policy_npv: float,
        policy_irr: float,
        appraisal_rate: float,
        private_npv: float,
        private_irr: float
    ) -> Tuple[str, str]:
        """
        의사결정 판단
        
        Returns:
            (decision, reason) 튜플
        """
        # 정책형 기준
        if policy_npv >= 0 and policy_irr >= 0:
            decision = "GO"
            reason = f"정책형 수익성 양호 (NPV {policy_npv/1e8:.1f}억, IRR {policy_irr*100:.1f}%). LH 매입 가능성 높음."
            
        elif policy_npv >= -10e8 and policy_irr >= -0.10:  # -10억, -10% 이내
            decision = "CONDITIONAL_GO"
            reason = f"정책형 수익성 조건부 양호 (NPV {policy_npv/1e8:.1f}억, IRR {policy_irr*100:.1f}%). 감정평가율 {appraisal_rate*100:.0f}% 기준. 주거복지 정책 목적으로 LH 매입 가능."
            
        else:
            decision = "NO_GO"
            reason = f"정책형 수익성 부족 (NPV {policy_npv/1e8:.1f}억, IRR {policy_irr*100:.1f}%). 감정평가율 개선 또는 CAPEX 절감 필요."
        
        # 민간 vs 정책 비교
        if private_npv < 0 and policy_npv >= -10e8:
            reason += f" [참고: 민간형 NPV {private_npv/1e8:.1f}억 대비 정책형이 {abs(private_npv - policy_npv)/1e8:.1f}억 개선]"
        
        return decision, reason
    
    def sensitivity_analysis(
        self,
        capex_data: Dict[str, Any],
        private_npv: float = 0.0,
        private_irr: float = 0.0
    ) -> Dict[str, Any]:
        """
        민감도 분석 (감정평가율 변동)
        
        Args:
            capex_data: CAPEX 데이터
            private_npv: 민간형 NPV
            private_irr: 민간형 IRR
            
        Returns:
            시나리오별 결과
        """
        scenarios = {
            'pessimistic': {'appraisal_rate': 0.85, 'label': '비관적 (85%)'},
            'base': {'appraisal_rate': 0.90, 'label': '기준 (90%)'},
            'optimistic': {'appraisal_rate': 0.95, 'label': '낙관적 (95%)'}
        }
        
        results = {}
        
        for scenario_name, params in scenarios.items():
            result = self.evaluate(
                capex_data=capex_data,
                appraisal_rate=params['appraisal_rate'],
                internal_adjustment=1.0,
                construction_index_change=0.0,
                private_npv=private_npv,
                private_irr=private_irr
            )
            
            results[scenario_name] = {
                'label': params['label'],
                'appraisal_rate': params['appraisal_rate'],
                'appraisal_value': result.appraisal.total_appraisal,
                'purchase_price': result.final_purchase_price,
                'policy_npv': result.policy_npv,
                'policy_irr': result.policy_irr,
                'decision': result.decision,
                'decision_reason': result.decision_reason
            }
        
        return results
