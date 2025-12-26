"""
M6 LH Comprehensive Judgement Service V3 (ZeroSite 4.0 FIX)
============================================================

LH 실제 심사 흐름을 완전히 재현한 최종 고정판

⚠️ 절대 원칙:
- 결론은 M6에서만 나온다
- M1~M5는 가능/불가능 언급 금지
- 보고서 문장으로 판단하지 않음
- LH 실제 평가 구조를 코드로 복제

Author: ZeroSite M6 Team
Date: 2025-12-26
Version: 3.0 (LH Standard FIX)
"""

import logging
from typing import Union
from datetime import datetime

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context import CapacityContext
from app.core.context.capacity_context_v2 import CapacityContextV2
from app.core.context.appraisal_context import AppraisalContext
from app.core.context.feasibility_context import FeasibilityContext

from .comprehensive_judgement import (
    M6ComprehensiveResult,
    SectionScore,
    RegionWeights,
    RegionWeightType,
    determine_grade,
    determine_judgement,
    determine_confidence_level
)

from .section_calculators import (
    calculate_section_a_policy,
    calculate_section_b_location,
    calculate_section_c_construction,
    calculate_section_d_price,
    calculate_section_e_business
)

logger = logging.getLogger(__name__)


class LHReviewServiceV3:
    """
    LH 종합 판단 서비스 V3 (ZeroSite 4.0 FIX)
    
    입력:
    - CanonicalLandContext (M1)
    - AppraisalContext (M2)
    - HousingTypeContext (M3)
    - CapacityContext (M4)
    - FeasibilityContext (M5)
    
    출력:
    - M6ComprehensiveResult
    """
    
    def __init__(self):
        """서비스 초기화"""
        logger.info("=" * 80)
        logger.info("🏢 M6 LH Comprehensive Judgement Service V3 Initialized")
        logger.info("   📋 LH 100-Point Evaluation (5 Sections)")
        logger.info("   🌍 Region-Specific Weighting (CAPITAL/LOCAL)")
        logger.info("   ⚠️  Fatal Reject Conditions Active")
        logger.info("   ✅ ZeroSite 4.0 FIX Standard")
        logger.info("=" * 80)
    
    def run(
        self,
        land_ctx: CanonicalLandContext,
        appraisal_ctx: AppraisalContext,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: Union[CapacityContext, CapacityContextV2],
        feasibility_ctx: FeasibilityContext
    ) -> M6ComprehensiveResult:
        """
        LH 종합 판단 실행
        
        Args:
            land_ctx: M1 토지 정보
            appraisal_ctx: M2 감정 평가
            housing_type_ctx: M3 주거 유형
            capacity_ctx: M4 건축 규모
            feasibility_ctx: M5 사업성
        
        Returns:
            M6ComprehensiveResult
        """
        logger.info("\n" + "=" * 80)
        logger.info("⚖️  M6 LH COMPREHENSIVE JUDGEMENT")
        logger.info("=" * 80)
        logger.info(f"📍 Address: {land_ctx.address}")
        logger.info(f"📍 Region: {land_ctx.sido}")
        
        # Determine region weight type
        capital_regions = ["서울특별시", "경기도", "인천광역시"]
        region_type = RegionWeightType.CAPITAL if land_ctx.sido in capital_regions else RegionWeightType.LOCAL
        logger.info(f"📍 Region Weight: {region_type.value}")
        logger.info("=" * 80)
        
        # Get region weights
        if region_type == RegionWeightType.CAPITAL:
            weights = RegionWeights.get_capital_weights()
        else:
            weights = RegionWeights.get_local_weights()
        
        # ====================================================================
        # STEP 1: 섹션별 원점수 계산
        # ====================================================================
        
        logger.info("\n[STEP 1] 📊 섹션별 원점수 계산")
        logger.info("-" * 80)
        
        # [A] 정책·유형 적합성 (25점)
        a_score, a_items, a_fatal, a_rejects = calculate_section_a_policy(
            housing_type_ctx, land_ctx
        )
        logger.info(f"[A] 정책·유형: {a_score:.1f}/25")
        
        # [B] 입지·환경 평가 (20점)
        b_score, b_items, b_fatal, b_rejects = calculate_section_b_location(
            land_ctx, housing_type_ctx
        )
        logger.info(f"[B] 입지·환경: {b_score:.1f}/20")
        
        # [C] 건축 가능성 (20점)
        c_score, c_items, c_fatal, c_rejects = calculate_section_c_construction(
            capacity_ctx, land_ctx
        )
        logger.info(f"[C] 건축: {c_score:.1f}/20")
        
        # [D] 가격·매입 적정성 (15점)
        d_score, d_items, d_deductions = calculate_section_d_price(
            appraisal_ctx, land_ctx
        )
        logger.info(f"[D] 가격: {d_score:.1f}/15")
        
        # [E] 사업성 (20점)
        e_score, e_items, e_fatal, e_rejects = calculate_section_e_business(
            feasibility_ctx
        )
        logger.info(f"[E] 사업성: {e_score:.1f}/20")
        
        # 원점수 합계
        raw_total = a_score + b_score + c_score + d_score + e_score
        logger.info("-" * 80)
        logger.info(f"📊 원점수 합계: {raw_total:.1f}/100")
        
        # ====================================================================
        # STEP 2: 지역별 가중치 적용
        # ====================================================================
        
        logger.info("\n[STEP 2] ⚖️  지역별 가중치 적용")
        logger.info("-" * 80)
        logger.info(f"가중치 ({region_type.value}):")
        logger.info(f"  정책·유형: ×{weights.policy:.1f}")
        logger.info(f"  입지·환경: ×{weights.location:.1f}")
        logger.info(f"  건축: ×{weights.construction:.1f}")
        logger.info(f"  가격: ×{weights.price:.1f}")
        logger.info(f"  사업성: ×{weights.business:.1f}")
        
        # 가중치 적용
        a_weighted = a_score * weights.policy
        b_weighted = b_score * weights.location
        c_weighted = c_score * weights.construction
        d_weighted = d_score * weights.price
        e_weighted = e_score * weights.business
        
        weighted_sum = a_weighted + b_weighted + c_weighted + d_weighted + e_weighted
        
        # 정규화 (원점수 총점 유지)
        scale_factor = raw_total / weighted_sum if weighted_sum > 0 else 1.0
        
        a_final = a_weighted * scale_factor
        b_final = b_weighted * scale_factor
        c_final = c_weighted * scale_factor
        d_final = d_weighted * scale_factor
        e_final = e_weighted * scale_factor
        
        final_total = a_final + b_final + c_final + d_final + e_final
        
        logger.info("-" * 80)
        logger.info(f"[A] 정책·유형: {a_final:.1f}")
        logger.info(f"[B] 입지·환경: {b_final:.1f}")
        logger.info(f"[C] 건축: {c_final:.1f}")
        logger.info(f"[D] 가격: {d_final:.1f}")
        logger.info(f"[E] 사업성: {e_final:.1f}")
        logger.info("-" * 80)
        logger.info(f"📊 가중치 적용 총점: {final_total:.1f}/100")
        
        # ====================================================================
        # STEP 3: 즉시 탈락 여부 확인
        # ====================================================================
        
        logger.info("\n[STEP 3] 🚨 즉시 탈락 여부 확인")
        logger.info("-" * 80)
        
        fatal_reject = a_fatal or b_fatal or c_fatal or e_fatal
        reject_reasons = a_rejects + b_rejects + c_rejects + e_rejects
        
        if fatal_reject:
            logger.info("❌ 즉시 탈락 조건 감지")
            for reason in reject_reasons:
                logger.info(f"   • {reason}")
        else:
            logger.info("✅ 즉시 탈락 조건 없음")
        
        # ====================================================================
        # STEP 4: 최종 판정
        # ====================================================================
        
        logger.info("\n[STEP 4] 🎯 최종 판정")
        logger.info("-" * 80)
        
        judgement = determine_judgement(final_total, fatal_reject)
        grade = determine_grade(final_total)
        
        logger.info(f"Total Score: {final_total:.1f}/100")
        logger.info(f"Grade: {grade.value}")
        logger.info(f"Judgement: {judgement.value}")
        
        # ====================================================================
        # STEP 5: 개선 방안 생성
        # ====================================================================
        
        improvement_points = self._generate_improvements(
            a_score, b_score, c_score, d_score, e_score,
            housing_type_ctx, capacity_ctx, feasibility_ctx
        )
        
        # ====================================================================
        # STEP 6: 신뢰도 평가
        # ====================================================================
        
        # 데이터 완전성 평가
        completeness = 0.9  # 기본 높음 (실제로는 각 Context의 필드 완성도 체크)
        confidence_level = determine_confidence_level(fatal_reject, completeness)
        
        # ====================================================================
        # 최종 결과 생성
        # ====================================================================
        
        result = M6ComprehensiveResult(
            lh_score_total=final_total,
            judgement=judgement,
            grade=grade,
            fatal_reject=fatal_reject,
            reject_reasons=reject_reasons,
            deduction_reasons=d_deductions,
            improvement_points=improvement_points,
            region_weight=region_type,
            confidence_level=confidence_level,
            section_a_policy=SectionScore(
                raw_score=a_score,
                weight=weights.policy,
                weighted_score=a_final,
                max_score=25.0,
                items=a_items
            ),
            section_b_location=SectionScore(
                raw_score=b_score,
                weight=weights.location,
                weighted_score=b_final,
                max_score=20.0,
                items=b_items
            ),
            section_c_construction=SectionScore(
                raw_score=c_score,
                weight=weights.construction,
                weighted_score=c_final,
                max_score=20.0,
                items=c_items
            ),
            section_d_price=SectionScore(
                raw_score=d_score,
                weight=weights.price,
                weighted_score=d_final,
                max_score=15.0,
                items=d_items
            ),
            section_e_business=SectionScore(
                raw_score=e_score,
                weight=weights.business,
                weighted_score=e_final,
                max_score=20.0,
                items=e_items
            ),
            applied_weights={
                "policy": weights.policy,
                "location": weights.location,
                "construction": weights.construction,
                "price": weights.price,
                "business": weights.business
            }
        )
        
        logger.info("=" * 80)
        logger.info("✅ M6 LH COMPREHENSIVE JUDGEMENT COMPLETED")
        logger.info(f"   Judgement: {judgement.value}")
        logger.info(f"   Score: {final_total:.1f}/100")
        logger.info(f"   Grade: {grade.value}")
        logger.info(f"   Confidence: {confidence_level}")
        logger.info("=" * 80 + "\n")
        
        return result
    
    def _generate_improvements(
        self,
        a_score, b_score, c_score, d_score, e_score,
        housing_type_ctx, capacity_ctx, feasibility_ctx
    ) -> list:
        """개선 방안 생성"""
        improvements = []
        
        # 정책·유형 개선
        if a_score < 20:
            improvements.append("세대 유형을 신혼형으로 전환 시 +5 가능")
        
        # 입지 개선
        if b_score < 15:
            improvements.append("역세권 접근성 개선 시 +3 가능")
        
        # 건축 개선
        if c_score < 15:
            if hasattr(capacity_ctx, 'incentive_capacity'):
                units = capacity_ctx.incentive_capacity.total_units
                if units < 50:
                    improvements.append(f"세대수 {50-units}세대 증가 시 +4 가능")
        
        # 가격 개선
        if d_score < 12:
            improvements.append("매입 단가 조정 협상 시 +3 가능")
        
        # 사업성 개선
        if e_score < 15:
            irr = feasibility_ctx.financial_metrics.irr_public
            if irr < 12:
                improvements.append("공사비 절감 시 IRR 개선 가능 (+5)")
        
        return improvements


__all__ = ["LHReviewServiceV3"]
