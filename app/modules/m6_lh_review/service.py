"""
M6 LH Review Service
====================

LH 심사예측 서비스

이 서비스는 M3 주택유형, M4 건축규모, M5 사업성을 종합하여
LH 심사 결과를 예측합니다.

⚠️ 중요: 이 모듈은 계산 결과만 사용하며, 어떤 Context도 수정하지 않습니다!

평가 기준 (110점):
- 입지 (35점): 역세권, 대학, 편의시설
- 규모 (20점): 세대수, 층수
- 사업성 (40점): NPV, IRR, 재무안정성
- 법적적합성 (15점): 용도지역, 규제

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import logging
from datetime import datetime

from typing import Union

from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context import CapacityContext  # V1 (legacy)
from app.core.context.capacity_context_v2 import CapacityContextV2  # V2 (new)
from app.core.context.feasibility_context import FeasibilityContext
from app.core.context.lh_review_context import (
    LHReviewContext,
    ScoreBreakdown,
    ApprovalPrediction,
    DecisionType,
    ProjectGrade
)

logger = logging.getLogger(__name__)


class LHReviewService:
    """
    LH 심사예측 서비스 (M6)
    
    입력: HousingTypeContext (M3), CapacityContext (M4), FeasibilityContext (M5)
    출력: LHReviewContext (최종 심사 예측)
    
    ⚠️ 모든 입력 Context는 READ-ONLY
    """
    
    def __init__(self):
        """서비스 초기화"""
        logger.info("✅ M6 LH Review Service initialized")
        logger.info("   ⚠️ All input contexts are READ-ONLY!")
    
    def run(
        self,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: Union[CapacityContext, CapacityContextV2],
        feasibility_ctx: FeasibilityContext
    ) -> LHReviewContext:
        """
        LH 심사예측 실행
        
        Args:
            housing_type_ctx: M3 주택유형
            capacity_ctx: M4 건축규모 (V1 or V2)
            feasibility_ctx: M5 사업성
        
        Returns:
            LHReviewContext (frozen=True, 최종 심사 결과)
        """
        
        # Detect V1 or V2 and extract units
        if isinstance(capacity_ctx, CapacityContextV2):
            recommended_units = capacity_ctx.incentive_capacity.total_units
            logger.info("="*80)
            logger.info("⚖️ M6 LH REVIEW MODULE - Predicting LH Review Decision")
            logger.info(f"   Housing Type: {housing_type_ctx.selected_type}")
            logger.info(f"   Capacity V2: Incentive {recommended_units}세대")
            logger.info(f"   NPV: ₩{feasibility_ctx.financial_metrics.npv_public:,.0f}")
            logger.info("="*80)
        else:
            recommended_units = capacity_ctx.unit_plan.recommended_units
            logger.info("="*80)
            logger.info("⚖️ M6 LH REVIEW MODULE - Predicting LH Review Decision")
            logger.info(f"   Housing Type: {housing_type_ctx.selected_type}")
            logger.info(f"   Recommended Units: {recommended_units}")
            logger.info(f"   NPV: ₩{feasibility_ctx.financial_metrics.npv_public:,.0f}")
            logger.info("="*80)
        
        # TODO: 실제 로직 구현
        # Step 1: 입지 점수 (35점) - M3 데이터
        # Step 2: 규모 점수 (20점) - M4 데이터
        # Step 3: 사업성 점수 (40점) - M5 데이터
        # Step 4: 법적적합성 점수 (15점) - M1+M4 데이터
        # Step 5: 총점 계산 및 등급 부여
        # Step 6: GO/NO-GO 판단
        
        # Mock 데이터
        lh_review_ctx = self._create_mock_context(
            housing_type_ctx, capacity_ctx, feasibility_ctx
        )
        
        logger.info(f"✅ LH Review Complete")
        logger.info(f"   Decision: {lh_review_ctx.decision}")
        logger.info(f"   Total Score: {lh_review_ctx.total_score:.1f}/110")
        logger.info(f"   Grade: {lh_review_ctx.grade}")
        logger.info("="*80)
        
        return lh_review_ctx
    
    def _create_mock_context(
        self,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: Union[CapacityContext, CapacityContextV2],
        feasibility_ctx: FeasibilityContext
    ) -> LHReviewContext:
        """Mock LH 심사 예측 (테스트용)"""
        # TODO: 실제 로직으로 교체
        
        # === 110점 체계 계산 ===
        
        # 1. 입지 점수 (35점 만점)
        location_score = housing_type_ctx.location_score  # 30.0/35
        
        # 2. 규모 점수 (20점 만점)
        # Extract units from V1 or V2
        if isinstance(capacity_ctx, CapacityContextV2):
            recommended_units = capacity_ctx.incentive_capacity.total_units
        else:
            recommended_units = capacity_ctx.unit_plan.recommended_units
        
        if recommended_units >= 100:
            scale_score = 20.0
        elif recommended_units >= 70:
            scale_score = 17.0
        elif recommended_units >= 50:
            scale_score = 15.0
        else:
            scale_score = 10.0
        
        # 3. 사업성 점수 (40점 만점) - M5에서 계산됨
        feasibility_score = feasibility_ctx.profitability_score  # 40점 만점
        
        # 4. 법규 적합성 (15점 만점)
        compliance_score = 15.0  # 간단히 만점
        
        # 총점
        total_score = location_score + scale_score + feasibility_score + compliance_score
        
        # ScoreBreakdown 객체
        score_breakdown = ScoreBreakdown(
            location_score=location_score,
            scale_score=scale_score,
            feasibility_score=feasibility_score,
            compliance_score=compliance_score,
            total_score=total_score
        )
        
        # 등급
        if total_score >= 90:
            grade = ProjectGrade.S
        elif total_score >= 80:
            grade = ProjectGrade.A
        elif total_score >= 70:
            grade = ProjectGrade.B
        elif total_score >= 60:
            grade = ProjectGrade.C
        elif total_score >= 50:
            grade = ProjectGrade.D
        else:
            grade = ProjectGrade.F
        
        # 의사결정
        if total_score >= 80:
            decision = DecisionType.GO
        elif total_score >= 70:
            decision = DecisionType.CONDITIONAL
        else:
            decision = DecisionType.NO_GO
        
        # 승인 확률
        approval_probability = min(total_score / 110, 1.0)
        if approval_probability > 0.8:
            approval_likelihood = "HIGH"
        elif approval_probability > 0.6:
            approval_likelihood = "MEDIUM"
        else:
            approval_likelihood = "LOW"
        
        approval_prediction = ApprovalPrediction(
            approval_probability=approval_probability,
            approval_likelihood=approval_likelihood,
            expected_conditions=[
                "LH 혐의 필요",
                "토지비 감정평가 확인"
            ] if decision == DecisionType.CONDITIONAL else [],
            critical_factors=[
                f"입지 점수: {location_score:.1f}/35",
                f"사업성 점수: {feasibility_score:.1f}/40"
            ]
        )
        
        # SWOT 분석
        strengths = [
            f"입지 우수 ({housing_type_ctx.selected_type_name})",
            f"사업성 {feasibility_ctx.profitability_grade}등급",
            f"ROI {feasibility_ctx.financial_metrics.roi:.1f}%"
        ]
        
        weaknesses = []
        if location_score < 30:
            weaknesses.append("입지 점수 개선 필요")
        if scale_score < 15:
            weaknesses.append("규모 부족 (최소 50세대 권장)")
        if feasibility_score < 30:
            weaknesses.append("사업성 개선 필요")
        if not weaknesses:
            weaknesses.append("주요 약점 없음")
        
        opportunities = [
            "LH 신축매입임대 정책 확대",
            "지역 수요 증가 추세"
        ]
        
        threats = [
            "경쟁 단지 증가",
            "공사비 상승 리스크"
        ]
        
        # 권장사항
        if decision == DecisionType.GO:
            recommendations = [
                "LH 협의 즉시 진행 권장",
                "토지비 감정평가 접수",
                "사업계획서 작성 착수"
            ]
            action_items = [
                "1단계: LH 사업부서 문의",
                "2단계: 감정평가 의뢰",
                "3단계: 사업계획서 제출"
            ]
        elif decision == DecisionType.CONDITIONAL:
            recommendations = [
                "조건 충족 후 LH 협의 진행",
                "입지 또는 규모 개선 검토"
            ]
            action_items = [
                "조건 충족 여부 확인",
                "개선 방안 도출"
            ]
        else:
            recommendations = [
                "현재 상태로는 진행 불가",
                "입지 재검토 또는 대체 부지 탐색 권장"
            ]
            action_items = [
                "대체 부지 물색",
                "지역 변경 검토"
            ]
        
        # 개선 영역
        improvement_areas = {}
        if location_score < 30:
            improvement_areas["입지"] = "역세권 또는 대학 근처 부지 탐색"
        if scale_score < 15:
            improvement_areas["규모"] = "최소 50세대 이상 확보 권장"
        if feasibility_score < 30:
            improvement_areas["사업성"] = "토지비 절감 또는 공사비 최적화"
        
        # 정책 가중치
        policy_weights = {
            "역세권_청년형": 1.2,
            "대학근처_청년형": 1.15,
            "신혼희망타운_우선": 1.1
        }
        
        return LHReviewContext(
            score_breakdown=score_breakdown,
            total_score=total_score,
            grade=grade,
            decision=decision,
            decision_rationale=f"{grade.value}등급, {total_score:.1f}/110점. {decision.value} 결정.",
            approval_prediction=approval_prediction,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            recommendations=recommendations,
            action_items=action_items,
            improvement_areas=improvement_areas,
            policy_weights=policy_weights,
            review_date=datetime.now().strftime("%Y-%m-%d"),
            reviewer="ZeroSite AI LH Review Engine v9.1 (Refactored M6)",
            review_version="2025 LH 기준 (110점 체계)"
        )


__all__ = ["LHReviewService"]
