"""
M3 LH Demand Service
====================

LH 선호유형 선택 서비스

이 서비스는 M1 토지정보를 기반으로
LH가 선호하는 주택유형을 선택합니다.

평가 요소:
- 역세권/대학 proximity
- 지역 인구 통계
- 용도지역 적합성
- LH 정책 우선순위

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import logging
from datetime import datetime

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.housing_type_context import (
    HousingTypeContext,
    TypeScore,
    POIAnalysis
)

logger = logging.getLogger(__name__)


class LHDemandService:
    """
    LH 선호유형 선택 서비스 (M3)
    
    입력: CanonicalLandContext (M1)
    출력: HousingTypeContext (선택된 유형)
    """
    
    def __init__(self):
        """서비스 초기화"""
        logger.info("✅ M3 LH Demand Service initialized")
    
    def run(self, land_ctx: CanonicalLandContext) -> HousingTypeContext:
        """
        LH 선호유형 선택 실행
        
        Args:
            land_ctx: M1에서 생성된 토지정보
        
        Returns:
            HousingTypeContext (frozen=True)
        """
        
        logger.info("="*80)
        logger.info("🏘️ M3 LH DEMAND MODULE - Determining Preferred Housing Type")
        logger.info(f"   Zone: {land_ctx.zone_type}")
        logger.info(f"   Location: {land_ctx.location_summary}")
        logger.info("="*80)
        
        # TODO: 실제 로직 구현
        # Step 1: 역세권 proximity 계산
        # Step 2: 대학 proximity 계산
        # Step 3: 인구 밀도 및 청년층 비율
        # Step 4: LH 정책 가중치 적용
        # Step 5: 유형별 수요 점수 계산
        # Step 6: 최적 유형 선택
        
        # Mock 데이터
        housing_type_ctx = self._create_mock_context(land_ctx)
        
        logger.info(f"✅ Housing Type Selected: {housing_type_ctx.selected_type_name}")
        logger.info(f"   Demand Prediction: {housing_type_ctx.demand_prediction:.1f}/100")
        logger.info("="*80)
        
        return housing_type_ctx
    
    def _create_mock_context(self, land_ctx: CanonicalLandContext) -> HousingTypeContext:
        """Mock 유형 선택 (테스트용)"""
        # TODO: 실제 로직으로 교체
        
        # POI Analysis Mock
        poi_analysis = POIAnalysis(
            subway_distance=800.0,
            school_distance=500.0,
            hospital_distance=1200.0,
            commercial_distance=300.0,
            subway_score=15.0,
            school_score=10.0,
            hospital_score=8.0,
            commercial_score=7.0,
            total_poi_count=25,
            radius_500m_count=8,
            radius_1km_count=15,
            radius_2km_count=25
        )
        
        # Type Scores Mock
        type_scores = {
            "youth": TypeScore(
                type_name="청년형",
                type_code="youth",
                total_score=85.0,
                location_score=30.0,
                accessibility_score=28.0,
                poi_score=27.0,
                demand_prediction=85.0
            ),
            "newlywed_1": TypeScore(
                type_name="신혼희망타운 I",
                type_code="newlywed_1",
                total_score=75.0,
                location_score=28.0,
                accessibility_score=25.0,
                poi_score=22.0,
                demand_prediction=75.0
            ),
            "newlywed_2": TypeScore(
                type_name="신혼희망타운 II",
                type_code="newlywed_2",
                total_score=70.0,
                location_score=26.0,
                accessibility_score=24.0,
                poi_score=20.0,
                demand_prediction=70.0
            ),
            "multi_child": TypeScore(
                type_name="다자녀형",
                type_code="multi_child",
                total_score=65.0,
                location_score=24.0,
                accessibility_score=22.0,
                poi_score=19.0,
                demand_prediction=65.0
            ),
            "senior": TypeScore(
                type_name="고령자형",
                type_code="senior",
                total_score=60.0,
                location_score=22.0,
                accessibility_score=20.0,
                poi_score=18.0,
                demand_prediction=60.0
            )
        }
        
        # Tie Detection: Sort by score and check if top 2 are within 5 points (threshold)
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1].total_score, reverse=True)
        top_type_code, top_score_obj = sorted_types[0]
        second_type_code, second_score_obj = sorted_types[1]
        
        score_diff = top_score_obj.total_score - second_score_obj.total_score
        TIE_THRESHOLD = 5.0  # 점수 차이 5점 이내면 동점으로 간주
        
        is_tie = score_diff < TIE_THRESHOLD
        
        # Tie handling parameters
        tie_params = {}
        if is_tie:
            tie_params = {
                "is_tie": True,
                "secondary_type": second_type_code,
                "secondary_type_name": second_score_obj.type_name,
                "secondary_score": second_score_obj.total_score,
                "score_difference": score_diff
            }
            logger.info(f"⚠️  Tie Detected: {top_score_obj.type_name} ({top_score_obj.total_score:.1f}) "
                       f"vs {second_score_obj.type_name} ({second_score_obj.total_score:.1f}), "
                       f"차이: {score_diff:.1f}점")
        
        return HousingTypeContext(
            selected_type=top_type_code,
            selected_type_name=top_score_obj.type_name,
            selection_confidence=0.85,
            type_scores=type_scores,
            **tie_params,  # Unpack tie parameters if present
            location_score=30.0,
            poi_analysis=poi_analysis,
            demand_prediction=85.0,
            demand_trend="HIGH",
            target_population=50000,
            competitor_count=3,
            competitor_analysis="MODERATE",
            strengths=["역세권 우수", "청년 인구 밀집", "LH 정책 우선순위"],
            weaknesses=["경쟁 단지 3개 존재"],
            recommendations=["청년형으로 진행 권장", "역세권 입지 강점 활용"],
            analysis_date=datetime.now().strftime("%Y-%m-%d"),
            data_sources=["POI DB", "인구통계 API", "LH 정책"]
        )


__all__ = ["LHDemandService"]
