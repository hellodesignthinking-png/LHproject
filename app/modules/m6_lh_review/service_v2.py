"""
M6 LH Review Service V2
========================

LH 실제 평가표 (100점 체계) 기반 심사 예측 서비스

평가 항목 (총 100점):
① 입지 적합성: 20점
② 토지 확보 용이성: 15점
③ 건축·기술 적합성: 15점
④ 사업성(재무): 25점
⑤ 정책 부합성: 15점
⑥ 사업 리스크: 10점

⚠️ LH 지점별 가중치 적용 (수도권/지방)
⚠️ 가중 후 자동 정규화 (총점 100 유지)

Author: ZeroSite M6 Team
Date: 2025-12-26
Version: 2.0 (LH Standard)
"""

import logging
from datetime import datetime
from typing import Union

from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context import CapacityContext
from app.core.context.capacity_context_v2 import CapacityContextV2
from app.core.context.feasibility_context import FeasibilityContext
from app.core.context.canonical_land import CanonicalLandContext

from .lh_scorecard import (
    LHBranchType,
    RawScores,
    LHScorecardResult,
    apply_branch_weights,
    determine_decision,
    get_branch_weights
)

from .score_calculator import (
    calculate_location_score,
    calculate_land_score,
    calculate_technical_score,
    calculate_financial_score,
    calculate_policy_score,
    calculate_risk_score
)

logger = logging.getLogger(__name__)


class LHReviewServiceV2:
    """
    LH 심사예측 서비스 V2 (100점 체계)
    
    입력:
    - CanonicalLandContext (M1): 토지 정보
    - HousingTypeContext (M3): 주거 유형
    - CapacityContext (M4): 건축 규모
    - FeasibilityContext (M5): 사업성
    
    출력:
    - LHScorecardResult: LH 평가표 기반 최종 심사 결과
    """
    
    def __init__(self):
        """서비스 초기화"""
        logger.info("=" * 80)
        logger.info("🏢 M6 LH Review Service V2 Initialized")
        logger.info("   📋 100-Point Scorecard System")
        logger.info("   🌍 Branch-Specific Weighting (CAPITAL/LOCAL)")
        logger.info("   ✅ LH Standard Compliance")
        logger.info("=" * 80)
    
    def run(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: Union[CapacityContext, CapacityContextV2],
        feasibility_ctx: FeasibilityContext,
        branch_type: LHBranchType = LHBranchType.CAPITAL
    ) -> LHScorecardResult:
        """
        LH 심사예측 실행
        
        Args:
            land_ctx: M1 토지 정보
            housing_type_ctx: M3 주거 유형
            capacity_ctx: M4 건축 규모 (V1 or V2)
            feasibility_ctx: M5 사업성
            branch_type: LH 지점 유형 (CAPITAL or LOCAL)
        
        Returns:
            LHScorecardResult
        """
        logger.info("\n" + "=" * 80)
        logger.info("⚖️  M6 LH REVIEW - SCORECARD CALCULATION")
        logger.info("=" * 80)
        logger.info(f"📍 Branch Type: {branch_type.value}")
        logger.info(f"📍 Address: {land_ctx.address}")
        logger.info(f"📍 Housing Type: {housing_type_ctx.selected_type_name}")
        
        # Extract units from V1 or V2
        if isinstance(capacity_ctx, CapacityContextV2):
            total_units = capacity_ctx.incentive_capacity.total_units
            legal_far = capacity_ctx.input_legal_far
            incentive_far = capacity_ctx.input_incentive_far
            logger.info(f"📍 Capacity: {total_units}세대 (Incentive)")
        else:
            total_units = capacity_ctx.unit_plan.recommended_units
            legal_far = 200.0  # Default
            incentive_far = 260.0  # Default
            logger.info(f"📍 Capacity: {total_units}세대")
        
        logger.info(f"📍 NPV: ₩{feasibility_ctx.financial_metrics.npv_public:,.0f}")
        logger.info(f"📍 IRR: {feasibility_ctx.financial_metrics.irr_public:.2f}%")
        logger.info("=" * 80)
        
        # ============================================================
        # STEP 1: 원점수 계산 (가중치 적용 전)
        # ============================================================
        
        logger.info("\n[STEP 1] 📊 RAW SCORE CALCULATION (Before Weighting)")
        logger.info("-" * 80)
        
        # ① 입지 적합성 (20점)
        location_score = calculate_location_score(
            poi_analysis=housing_type_ctx.poi_analysis.__dict__ if housing_type_ctx.poi_analysis else {},
            demand_prediction=housing_type_ctx.demand_prediction,
            location_score_m3=housing_type_ctx.location_score
        )
        logger.info(f"① 입지 적합성: {location_score:.1f}/20")
        
        # ② 토지 확보 용이성 (15점)
        land_score = calculate_land_score(
            parcel_id=land_ctx.parcel_id,
            b_code="",  # Not available in CanonicalLandContext
            zone_type=land_ctx.zone_type
        )
        logger.info(f"② 토지 확보 용이성: {land_score:.1f}/15")
        
        # ③ 건축·기술 적합성 (15점)
        technical_score = calculate_technical_score(
            legal_far=legal_far,
            legal_bcr=land_ctx.bcr,
            incentive_far=incentive_far,
            parking_feasible=True,  # Assume feasible if units calculated
            total_units=total_units
        )
        logger.info(f"③ 건축·기술 적합성: {technical_score:.1f}/15")
        
        # ④ 사업성(재무) (25점)
        financial_score = calculate_financial_score(
            npv_public=feasibility_ctx.financial_metrics.npv_public,
            irr_public=feasibility_ctx.financial_metrics.irr_public,
            total_cost=feasibility_ctx.cost_breakdown.total_cost,
            total_revenue=feasibility_ctx.revenue_projection.total_revenue
        )
        logger.info(f"④ 사업성(재무): {financial_score:.1f}/25")
        
        # ⑤ 정책 부합성 (15점)
        policy_score = calculate_policy_score(
            selected_type=housing_type_ctx.selected_type,
            selection_confidence=housing_type_ctx.selection_confidence,
            housing_demand=housing_type_ctx.demand_prediction
        )
        logger.info(f"⑤ 정책 부합성: {policy_score:.1f}/15")
        
        # ⑥ 사업 리스크 (10점)
        risk_score = calculate_risk_score(
            zone_type=land_ctx.zone_type,
            restrictions=land_ctx.restrictions if land_ctx.restrictions else [],
            total_units=total_units
        )
        logger.info(f"⑥ 사업 리스크: {risk_score:.1f}/10")
        
        # 원점수 객체 생성
        raw_scores = RawScores(
            location=location_score,
            land=land_score,
            technical=technical_score,
            financial=financial_score,
            policy=policy_score,
            risk=risk_score
        )
        
        logger.info("-" * 80)
        logger.info(f"📊 RAW TOTAL: {raw_scores.total:.1f}/100")
        logger.info("=" * 80)
        
        # ============================================================
        # STEP 2: 지점별 가중치 적용
        # ============================================================
        
        logger.info("\n[STEP 2] ⚖️  BRANCH WEIGHT APPLICATION")
        logger.info("-" * 80)
        
        weights = get_branch_weights(branch_type)
        logger.info(f"가중치 (Branch: {branch_type.value}):")
        logger.info(f"  - 입지 적합성: ×{weights.location:.2f}")
        logger.info(f"  - 토지 확보: ×{weights.land:.2f}")
        logger.info(f"  - 건축·기술: ×{weights.technical:.2f}")
        logger.info(f"  - 사업성: ×{weights.financial:.2f}")
        logger.info(f"  - 정책 부합성: ×{weights.policy:.2f}")
        logger.info(f"  - 사업 리스크: ×{weights.risk:.2f}")
        
        # 가중치 적용 및 정규화
        weighted_scores = apply_branch_weights(raw_scores, branch_type)
        
        logger.info("-" * 80)
        logger.info(f"① 입지 적합성: {weighted_scores.location:.1f}")
        logger.info(f"② 토지 확보 용이성: {weighted_scores.land:.1f}")
        logger.info(f"③ 건축·기술 적합성: {weighted_scores.technical:.1f}")
        logger.info(f"④ 사업성(재무): {weighted_scores.financial:.1f}")
        logger.info(f"⑤ 정책 부합성: {weighted_scores.policy:.1f}")
        logger.info(f"⑥ 사업 리스크: {weighted_scores.risk:.1f}")
        logger.info("-" * 80)
        logger.info(f"📊 WEIGHTED TOTAL: {weighted_scores.total:.1f}/100")
        logger.info("=" * 80)
        
        # ============================================================
        # STEP 3: 최종 판단
        # ============================================================
        
        logger.info("\n[STEP 3] 🎯 FINAL DECISION")
        logger.info("-" * 80)
        
        total_score = weighted_scores.total
        decision = determine_decision(total_score)
        
        logger.info(f"Total Score: {total_score:.1f}/100")
        logger.info(f"Decision: {decision.value}")
        logger.info("-" * 80)
        
        # 판단 근거 생성
        decision_reasons = self._generate_decision_reasons(
            decision=decision,
            raw_scores=raw_scores,
            weighted_scores=weighted_scores,
            branch_type=branch_type,
            irr=feasibility_ctx.financial_metrics.irr_public,
            npv=feasibility_ctx.financial_metrics.npv_public,
            units=total_units
        )
        
        for reason in decision_reasons:
            logger.info(f"  • {reason}")
        
        logger.info("=" * 80)
        
        # 최종 결과 생성
        result = LHScorecardResult(
            branch_type=branch_type,
            raw_scores=raw_scores,
            weighted_scores=weighted_scores,
            weights_applied=weights.to_dict(),
            total_score=total_score,
            decision=decision,
            decision_reasons=decision_reasons
        )
        
        logger.info("\n✅ M6 LH REVIEW COMPLETED")
        logger.info(f"   Decision: {decision.value}")
        logger.info(f"   Score: {total_score:.1f}/100")
        logger.info(f"   Branch: {branch_type.value}")
        logger.info("=" * 80 + "\n")
        
        return result
    
    def _generate_decision_reasons(
        self,
        decision,
        raw_scores: RawScores,
        weighted_scores,
        branch_type: LHBranchType,
        irr: float,
        npv: float,
        units: int
    ) -> list:
        """판단 근거 생성"""
        reasons = []
        
        # 결정 유형별 기본 메시지
        if decision.value == "GO":
            reasons.append(f"총점 {weighted_scores.total:.1f}/100으로 GO 기준 충족")
        elif decision.value == "CONDITIONAL":
            reasons.append(f"총점 {weighted_scores.total:.1f}/100으로 CONDITIONAL 판정")
        else:
            reasons.append(f"총점 {weighted_scores.total:.1f}/100으로 HOLD 판정")
        
        # IRR 기반 판단
        if irr >= 15.0:
            reasons.append(f"IRR {irr:.1f}%로 우수 (LH 기준 15% 초과)")
        elif irr >= 12.0:
            reasons.append(f"IRR {irr:.1f}%로 양호 (LH 기준 12% 충족)")
        else:
            reasons.append(f"IRR {irr:.1f}%로 LH 기준 12% 미달")
        
        # NPV 기반 판단
        if npv > 0:
            reasons.append(f"NPV ₩{npv:,.0f} 양호 (수익성 확보)")
        else:
            reasons.append(f"NPV ₩{npv:,.0f} 손실 (수익성 개선 필요)")
        
        # 규모 기반 판단
        if units >= 50:
            reasons.append(f"{units}세대로 적정 규모 확보")
        else:
            reasons.append(f"{units}세대로 소규모 (최소 50세대 권장)")
        
        # 지점별 특화 메시지
        if branch_type == LHBranchType.CAPITAL:
            if weighted_scores.location >= 18:
                reasons.append("수도권 기준 입지 경쟁력 우수")
            if weighted_scores.financial >= 20:
                reasons.append("수도권 기준 사업성 우수")
            if weighted_scores.risk <= 5:
                reasons.append("수도권 기준 리스크 관리 필요")
        else:  # LOCAL
            if weighted_scores.policy >= 12:
                reasons.append("지방 기준 정책 부합성 우수")
            if weighted_scores.land >= 12:
                reasons.append("지방 기준 토지 확보 용이")
        
        return reasons


__all__ = ["LHReviewServiceV2"]
