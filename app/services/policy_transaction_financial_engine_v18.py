"""
ZeroSite v18 - Policy Transaction Financial Engine
===================================================
LH 신축형 매입임대 사업 전용 재무 분석 엔진

핵심 개념:
---------
1. **수익 모델**: LH 최종 매입가 (NOT 30년 임대운영)
2. **총사업비 수지표**: 토지비 + 건설비 + 부대비 + 금융비용 + 예비비
3. **LH 감정평가**: 토지가액(거래사례) + 건물가액(공사비 85-95% 인정)
4. **공사비 연동제**: 건축비 변동 자동 반영
5. **ROI 중심**: Profit / Total CAPEX
6. **IRR**: 2.5년 Cashflow IRR (NOT 30-year)

사업 구조:
---------
[사업자] 토지 매입 → 건축 → 완공
         ↓
[LH] 감정평가 → 매입 결정 → 매입가 지급
         ↓
[사업자] 매입가 수령 → CAPEX 회수 + 수익/손실 확정

거래 수익 = LH 매입가 - 총사업비
ROI = 거래 수익 / 총사업비
IRR = 2.5년 기준 내부수익률

이전 모델과의 차이:
------------------
v17 (PrivateRentalEngine):
- 수익 = 30년 임대료 합계
- NPV = PV(임대료) - CAPEX
- 결과: NPV -111.9억 (항상 음수)

v18 (PolicyTransactionEngine):
- 수익 = LH 매입가 (1회 거래)
- Profit = 매입가 - CAPEX
- 결과: Profit -7.6억 (현실적)
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


# ==========================================
# 1. 데이터 모델 정의
# ==========================================

@dataclass
class TransactionInputs:
    """거래형 사업 입력 데이터"""
    # 기본 정보
    land_area_m2: float                        # 대지면적 (㎡)
    building_area_m2: float                    # 연면적 (㎡)
    
    # 가격 정보 (거래사례 기반)
    land_price_per_m2: float                   # 토지 평균 거래단가 (원/㎡)
    construction_cost_per_m2: float            # 건설비 단가 (원/㎡)
    
    # 부대비용 비율
    design_cost_rate: float = 0.08             # 설계비 8%
    supervision_cost_rate: float = 0.03        # 감리비 3%
    permit_cost_rate: float = 0.02             # 인허가비 2%
    contingency_rate: float = 0.10             # 예비비 10%
    financing_rate: float = 0.03               # 금융비용 3% (PF 이자)
    misc_cost_rate: float = 0.04               # 기타비용 4%
    
    # LH 감정평가 파라미터
    land_appraisal_rate: float = 0.95          # 토지 감정평가 인정률 95%
    building_ack_rate: float = 0.90            # 건물 공사비 인정률 90%
    appraisal_safety_factor: float = 0.98      # 안전계수 98%
    
    # 공사비 연동제
    construction_index_rate: float = 1.05      # 연동지수 105% (5% 상승)
    
    # 기타
    construction_period_years: float = 2.5     # 공사기간 (IRR 계산용)


@dataclass
class CAPEXBreakdown:
    """총사업비 상세 내역"""
    # 토지 관련
    land_cost: float                           # 토지비
    land_acquisition_tax: float                # 취득세
    
    # 건설 관련
    base_construction_cost: float              # 기본 건설비
    indexed_construction_cost: float           # 연동제 적용 건설비
    design_cost: float                         # 설계비
    supervision_cost: float                    # 감리비
    permit_cost: float                         # 인허가비
    
    # 기타
    contingency_cost: float                    # 예비비
    financing_cost: float                      # 금융비용
    misc_cost: float                           # 기타비용
    
    # 합계
    total_capex: float                         # 총사업비


@dataclass
class AppraisalResult:
    """LH 감정평가 결과"""
    land_appraised_value: float                # 토지 감정가액
    building_appraised_value: float            # 건물 감정가액
    indexing_adjustment: float                 # 연동제 조정액
    subtotal: float                            # 소계
    safety_factor_adjustment: float            # 안전계수 조정
    final_appraisal_value: float               # 최종 감정평가액 (LH 매입가)


@dataclass
class TransactionResult:
    """거래형 사업 분석 결과"""
    # 입력
    inputs: TransactionInputs
    
    # CAPEX
    capex: CAPEXBreakdown
    
    # LH 매입가
    appraisal: AppraisalResult
    
    # 사업 수익성
    revenue: float                             # 수익 = LH 매입가
    cost: float                                # 비용 = 총사업비
    profit: float                              # 이익 = 수익 - 비용
    roi_pct: float                             # ROI (%)
    irr_pct: float                             # IRR (%) - 2.5년 기준
    payback_years: float                       # 회수기간
    
    # 의사결정
    decision: str                              # GO / CONDITIONAL-GO / NO-GO
    decision_reason: str                       # 판단 근거
    conditional_requirements: List[str]        # 조건부 GO 요구사항


# ==========================================
# 2. 핵심 엔진
# ==========================================

class PolicyTransactionFinancialEngineV18:
    """
    ZeroSite v18 - 정책형 거래 재무 평가 엔진
    
    LH 신축매입임대 사업의 실제 메커니즘 반영:
    1. 총사업비 수지표 작성
    2. LH 감정평가액 산정
    3. 거래 수익 = 매입가 - 총사업비
    4. ROI = 거래 수익 / 총사업비
    5. IRR = 2.5년 Cashflow IRR
    """
    
    def __init__(self, inputs: TransactionInputs):
        self.inputs = inputs
        logger.info("=" * 80)
        logger.info("🏛️ PolicyTransactionFinancialEngineV18 초기화")
        logger.info("=" * 80)
    
    # ========================================
    # STEP 1: 총사업비 계산 (CAPEX)
    # ========================================
    
    def calculate_total_capex(self) -> CAPEXBreakdown:
        """
        총사업비 산출표 생성
        
        구성:
        1. 토지비 (거래사례 기반 평균단가 × 면적)
        2. 취득세 (토지비 × 4.4%)
        3. 건설비 (표준건축비 × 연동지수)
        4. 설계비 (건설비 × 8%)
        5. 감리비 (건설비 × 3%)
        6. 인허가비 (건설비 × 2%)
        7. 예비비 (건설비 × 10%)
        8. 금융비용 (PF 대출 이자, 총비용 × 3%)
        9. 기타비용 (법무, 보험 등, 총비용 × 4%)
        """
        i = self.inputs
        
        logger.info("📊 STEP 1: 총사업비 계산")
        
        # 1. 토지비 (거래사례 기반)
        land_cost = i.land_area_m2 * i.land_price_per_m2
        land_acquisition_tax = land_cost * 0.044  # 취득세 4.4%
        
        logger.info(f"  🏞️  토지비: {land_cost/1e8:.2f}억 (거래단가 {i.land_price_per_m2/1e4:.0f}만/㎡ × {i.land_area_m2:.1f}㎡)")
        logger.info(f"  💳 취득세: {land_acquisition_tax/1e8:.2f}억 (4.4%)")
        
        # 2. 건설비 (공사비 연동제 적용)
        base_construction_cost = i.building_area_m2 * i.construction_cost_per_m2
        indexed_construction_cost = base_construction_cost * i.construction_index_rate
        
        logger.info(f"  🏗️  기본 건설비: {base_construction_cost/1e8:.2f}억")
        logger.info(f"  📈 연동제 적용: {indexed_construction_cost/1e8:.2f}억 (지수 {i.construction_index_rate*100:.1f}%)")
        
        # 3. 설계/감리/인허가
        design_cost = indexed_construction_cost * i.design_cost_rate
        supervision_cost = indexed_construction_cost * i.supervision_cost_rate
        permit_cost = indexed_construction_cost * i.permit_cost_rate
        
        logger.info(f"  📐 설계비: {design_cost/1e8:.2f}억 ({i.design_cost_rate*100:.0f}%)")
        logger.info(f"  👷 감리비: {supervision_cost/1e8:.2f}억 ({i.supervision_cost_rate*100:.0f}%)")
        logger.info(f"  📋 인허가비: {permit_cost/1e8:.2f}억 ({i.permit_cost_rate*100:.0f}%)")
        
        # 4. 예비비
        contingency_cost = indexed_construction_cost * i.contingency_rate
        logger.info(f"  🛡️  예비비: {contingency_cost/1e8:.2f}억 ({i.contingency_rate*100:.0f}%)")
        
        # 5. 소계
        subtotal = (land_cost + land_acquisition_tax + indexed_construction_cost + 
                   design_cost + supervision_cost + permit_cost + contingency_cost)
        
        # 6. 금융비용 (PF 이자)
        financing_cost = subtotal * i.financing_rate
        logger.info(f"  💰 금융비용: {financing_cost/1e8:.2f}억 ({i.financing_rate*100:.0f}%, PF 대출 이자)")
        
        # 7. 기타비용
        misc_cost = subtotal * i.misc_cost_rate
        logger.info(f"  📦 기타비용: {misc_cost/1e8:.2f}억 ({i.misc_cost_rate*100:.0f}%, 법무/보험 등)")
        
        # 8. 총사업비
        total_capex = subtotal + financing_cost + misc_cost
        
        logger.info(f"")
        logger.info(f"  ✅ 총사업비: {total_capex/1e8:.2f}억원")
        logger.info(f"")
        
        return CAPEXBreakdown(
            land_cost=land_cost,
            land_acquisition_tax=land_acquisition_tax,
            base_construction_cost=base_construction_cost,
            indexed_construction_cost=indexed_construction_cost,
            design_cost=design_cost,
            supervision_cost=supervision_cost,
            permit_cost=permit_cost,
            contingency_cost=contingency_cost,
            financing_cost=financing_cost,
            misc_cost=misc_cost,
            total_capex=total_capex
        )
    
    # ========================================
    # STEP 2: LH 감정평가액 산정
    # ========================================
    
    def calculate_lh_appraisal(self, capex: CAPEXBreakdown) -> AppraisalResult:
        """
        LH 감정평가 메커니즘 시뮬레이션
        
        LH 감정평가 방식:
        1. 토지가액 = 거래사례 기준 × 인정률 (95%)
        2. 건물가액 = 공사비 × 인정률 (85-95%, 기본 90%)
        3. 연동제 조정 = 건설비 증가분 인정
        4. 안전계수 = 최종 조정 (98%)
        5. 최종 매입가 = (토지 + 건물 + 연동제) × 안전계수
        """
        i = self.inputs
        
        logger.info("💎 STEP 2: LH 감정평가 계산")
        
        # 1. 토지 감정가액
        land_appraised_value = capex.land_cost * i.land_appraisal_rate
        logger.info(f"  🏞️  토지 감정가액: {land_appraised_value/1e8:.2f}억 (토지비 {capex.land_cost/1e8:.2f}억 × {i.land_appraisal_rate*100:.0f}%)")
        
        # 2. 건물 감정가액 (공사비 인정률 적용)
        building_appraised_value = capex.indexed_construction_cost * i.building_ack_rate
        logger.info(f"  🏢 건물 감정가액: {building_appraised_value/1e8:.2f}억 (건설비 {capex.indexed_construction_cost/1e8:.2f}억 × {i.building_ack_rate*100:.0f}%)")
        
        # 3. 연동제 조정액
        indexing_adjustment = (capex.indexed_construction_cost - capex.base_construction_cost) * 0.8  # 연동제 증가분의 80% 인정
        logger.info(f"  📈 연동제 조정: {indexing_adjustment/1e8:.2f}억")
        
        # 4. 소계
        subtotal = land_appraised_value + building_appraised_value + indexing_adjustment
        logger.info(f"  📊 소계: {subtotal/1e8:.2f}억")
        
        # 5. 안전계수 적용
        safety_factor_adjustment = subtotal * (1 - i.appraisal_safety_factor)
        final_appraisal_value = subtotal * i.appraisal_safety_factor
        
        logger.info(f"  🛡️  안전계수: {i.appraisal_safety_factor*100:.1f}% (조정 {safety_factor_adjustment/1e8:.2f}억)")
        logger.info(f"")
        logger.info(f"  ✅ 최종 감정평가액 (LH 매입가): {final_appraisal_value/1e8:.2f}억원")
        logger.info(f"")
        
        return AppraisalResult(
            land_appraised_value=land_appraised_value,
            building_appraised_value=building_appraised_value,
            indexing_adjustment=indexing_adjustment,
            subtotal=subtotal,
            safety_factor_adjustment=safety_factor_adjustment,
            final_appraisal_value=final_appraisal_value
        )
    
    # ========================================
    # STEP 3: 사업 수익성 분석
    # ========================================
    
    def calculate_roi_irr(self, capex: CAPEXBreakdown, appraisal: AppraisalResult) -> Tuple[float, float, float]:
        """
        ROI, IRR, 회수기간 계산
        
        ROI = (LH 매입가 - 총사업비) / 총사업비 × 100%
        IRR = 2.5년 Cashflow 기준 내부수익률
        Payback = 총사업비 / 연평균 수익
        """
        i = self.inputs
        
        logger.info("📈 STEP 3: 수익성 분석")
        
        revenue = appraisal.final_appraisal_value
        cost = capex.total_capex
        profit = revenue - cost
        
        # ROI
        roi_pct = (profit / cost) * 100
        logger.info(f"  💵 LH 매입가: {revenue/1e8:.2f}억원")
        logger.info(f"  💸 총사업비: {cost/1e8:.2f}억원")
        logger.info(f"  {'📗' if profit >= 0 else '📕'} 사업이익: {profit/1e8:+.2f}억원")
        logger.info(f"  {'✅' if roi_pct >= 0 else '❌'} ROI: {roi_pct:+.2f}%")
        
        # IRR (2.5년 Cashflow)
        irr_pct = self._calculate_cashflow_irr(cost, revenue, i.construction_period_years)
        logger.info(f"  📊 IRR (2.5년): {irr_pct:+.2f}%")
        
        # Payback
        if profit > 0:
            payback_years = i.construction_period_years
        else:
            payback_years = 999.0  # Never
        logger.info(f"  ⏱️  회수기간: {payback_years:.1f}년")
        logger.info(f"")
        
        return roi_pct, irr_pct, payback_years
    
    def _calculate_cashflow_irr(self, cost: float, revenue: float, years: float) -> float:
        """
        2.5년 Cashflow 기준 IRR 계산
        
        Cashflow:
        Year 0: -CAPEX (초기 투자)
        Year 1: 0 (건설 중)
        Year 2: 0 (건설 중)
        Year 2.5: +Revenue (LH 매입가 수령)
        """
        try:
            # Simplified: Year 0 = -cost, Year 2.5 = +revenue
            cashflows = [-cost, 0, 0, revenue]
            irr = np.irr(cashflows)
            
            if np.isnan(irr) or np.isinf(irr):
                # Fallback: simple calculation
                irr = ((revenue / cost) - 1) / years
            
            return irr * 100  # Convert to percentage
        except Exception as e:
            logger.warning(f"IRR calculation failed: {e}, using fallback")
            return ((revenue / cost) - 1) / years * 100
    
    # ========================================
    # STEP 4: 의사결정 규칙
    # ========================================
    
    def make_decision(self, profit: float, roi_pct: float, capex: CAPEXBreakdown) -> Tuple[str, str, List[str]]:
        """
        GO / CONDITIONAL-GO / NO-GO 판단
        
        판단 기준:
        - GO: Profit > 0 and ROI > 5%
        - CONDITIONAL-GO: -10% < ROI < 5% (토지비/공사비 절감 시 수익 가능)
        - NO-GO: ROI < -10% (구조적 문제)
        """
        logger.info("🎯 STEP 4: 의사결정")
        
        conditions = []
        
        if profit > 0 and roi_pct > 5:
            decision = "GO"
            reason = f"사업이익 {profit/1e8:+.2f}억원, ROI {roi_pct:+.2f}% 확보. LH 매입 가능성 높음."
            
        elif roi_pct > -10:
            decision = "CONDITIONAL-GO"
            
            # 개선 가능 영역 분석
            land_reduction_target = capex.land_cost * 0.10  # 토지비 10% 절감 목표
            construction_reduction_target = capex.indexed_construction_cost * 0.08  # 공사비 8% 절감 목표
            
            conditions.append(f"토지비 {land_reduction_target/1e8:.1f}억 절감 (현재 {capex.land_cost/1e8:.1f}억 → 목표 {(capex.land_cost-land_reduction_target)/1e8:.1f}억)")
            conditions.append(f"공사비 {construction_reduction_target/1e8:.1f}억 절감 (VE, 자재 단가 협상)")
            
            if abs(profit) < capex.land_cost * 0.05:
                conditions.append("토지 매입가 협상 우선 추진")
            
            reason = f"현재 ROI {roi_pct:+.2f}%. 토지비 또는 공사비 절감 시 수익성 확보 가능. 조건부 진행 권고."
            
        else:
            decision = "NO-GO"
            reason = f"ROI {roi_pct:+.2f}%로 구조적 수익성 미흡. 사업 재검토 필요."
            conditions.append("사업 구조 전면 재검토")
            conditions.append("대안 부지 검토")
        
        logger.info(f"  🎯 판단: {decision}")
        logger.info(f"  📝 근거: {reason}")
        if conditions:
            logger.info(f"  📌 조건:")
            for cond in conditions:
                logger.info(f"     - {cond}")
        logger.info("=" * 80)
        
        return decision, reason, conditions
    
    # ========================================
    # 종합 평가
    # ========================================
    
    def evaluate(self) -> TransactionResult:
        """
        전체 사업성 평가 실행
        
        Returns:
            TransactionResult: 종합 분석 결과
        """
        # Step 1: 총사업비
        capex = self.calculate_total_capex()
        
        # Step 2: LH 감정평가
        appraisal = self.calculate_lh_appraisal(capex)
        
        # Step 3: ROI/IRR
        roi_pct, irr_pct, payback_years = self.calculate_roi_irr(capex, appraisal)
        
        # Step 4: 의사결정
        profit = appraisal.final_appraisal_value - capex.total_capex
        decision, reason, conditions = self.make_decision(profit, roi_pct, capex)
        
        return TransactionResult(
            inputs=self.inputs,
            capex=capex,
            appraisal=appraisal,
            revenue=appraisal.final_appraisal_value,
            cost=capex.total_capex,
            profit=profit,
            roi_pct=roi_pct,
            irr_pct=irr_pct,
            payback_years=payback_years,
            decision=decision,
            decision_reason=reason,
            conditional_requirements=conditions
        )
    
    # ========================================
    # 민감도 분석
    # ========================================
    
    def sensitivity_analysis(self) -> Dict[str, Any]:
        """
        민감도 분석
        
        변수:
        - 토지비 ±10%
        - 공사비 ±15%
        - 감정평가율 85% / 90% / 95%
        """
        logger.info("📊 민감도 분석 시작...")
        
        base_result = self.evaluate()
        
        scenarios = {}
        
        # 1. 토지비 민감도
        for adj in [-0.10, 0, 0.10]:
            key = f"land_{adj:+.0%}"
            modified_inputs = TransactionInputs(**self.inputs.__dict__)
            modified_inputs.land_price_per_m2 *= (1 + adj)
            engine = PolicyTransactionFinancialEngineV18(modified_inputs)
            result = engine.evaluate()
            scenarios[key] = {
                'label': f'토지비 {adj:+.0%}',
                'profit': result.profit / 1e8,
                'roi': result.roi_pct,
                'decision': result.decision
            }
        
        # 2. 공사비 민감도
        for adj in [-0.15, 0, 0.15]:
            key = f"construction_{adj:+.0%}"
            modified_inputs = TransactionInputs(**self.inputs.__dict__)
            modified_inputs.construction_cost_per_m2 *= (1 + adj)
            engine = PolicyTransactionFinancialEngineV18(modified_inputs)
            result = engine.evaluate()
            scenarios[key] = {
                'label': f'공사비 {adj:+.0%}',
                'profit': result.profit / 1e8,
                'roi': result.roi_pct,
                'decision': result.decision
            }
        
        # 3. 감정평가율 민감도
        for rate in [0.85, 0.90, 0.95]:
            key = f"appraisal_{rate:.0%}"
            modified_inputs = TransactionInputs(**self.inputs.__dict__)
            modified_inputs.building_ack_rate = rate
            engine = PolicyTransactionFinancialEngineV18(modified_inputs)
            result = engine.evaluate()
            scenarios[key] = {
                'label': f'감정평가율 {rate:.0%}',
                'profit': result.profit / 1e8,
                'roi': result.roi_pct,
                'decision': result.decision
            }
        
        return {
            'base': {
                'profit': base_result.profit / 1e8,
                'roi': base_result.roi_pct,
                'decision': base_result.decision
            },
            'scenarios': scenarios
        }


# ==========================================
# 3. 헬퍼 함수
# ==========================================

def create_transaction_engine_from_context(context: Dict[str, Any]) -> PolicyTransactionFinancialEngineV18:
    """
    ReportContextBuilder에서 사용하기 쉽게 context dict로부터 엔진 생성
    
    Args:
        context: report_context_builder의 context dict
        
    Returns:
        PolicyTransactionFinancialEngineV18 인스턴스
    """
    site = context.get('site', {})
    cost = context.get('cost', {})
    market = context.get('market', {})
    
    # 기본값 설정
    land_area_m2 = site.get('land_area_sqm', 660.0)
    building_area_m2 = site.get('land_area_sqm', 660.0) * 2.5  # 용적률 250% 가정
    
    # 거래사례 기반 토지가격 (기존 공시지가 대신)
    # TODO: 실거래가 API 연동 시 교체
    land_price_per_m2 = market.get('land_price_per_m2', 10_000_000)  # 1000만원/㎡ (서울 평균)
    
    construction_cost_per_m2 = cost.get('construction', {}).get('per_sqm', 3_500_000)
    
    inputs = TransactionInputs(
        land_area_m2=land_area_m2,
        building_area_m2=building_area_m2,
        land_price_per_m2=land_price_per_m2,
        construction_cost_per_m2=construction_cost_per_m2
    )
    
    return PolicyTransactionFinancialEngineV18(inputs)
