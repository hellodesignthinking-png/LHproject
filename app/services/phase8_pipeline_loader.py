"""
Phase 8: 파이프라인 결과 조회 헬퍼
====================================

context_id 또는 parcel_id로 파이프라인 결과를 가져오는 유틸리티

작성일: 2026-01-10
"""

import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.core.pipeline.zer0site_pipeline import PipelineResult
from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.appraisal_context import AppraisalContext
from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context_v2 import CapacityContextV2
from app.core.context.feasibility_context import FeasibilityContext
from app.core.context.lh_review_context import LHReviewContext

logger = logging.getLogger(__name__)

CACHE_DIR = Path("/home/user/webapp/.cache/pipeline")


async def get_pipeline_result(identifier: str) -> Optional[PipelineResult]:
    """
    파이프라인 결과 조회 (context_id 또는 parcel_id)
    
    Args:
        identifier: context_id 또는 parcel_id
        
    Returns:
        PipelineResult 또는 None
    """
    try:
        # 파일 기반 캐시에서 로드
        cache_file = CACHE_DIR / f"{identifier}.json"
        
        if not cache_file.exists():
            logger.warning(f"Pipeline result not found for identifier: {identifier}")
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Context 객체로 재구성
        result = PipelineResult(
            land=CanonicalLandContext(**data['land']) if data.get('land') else None,
            appraisal=AppraisalContext(**data['appraisal']) if data.get('appraisal') else None,
            housing_type=HousingTypeContext(**data['housing_type']) if data.get('housing_type') else None,
            capacity=CapacityContextV2(**data['capacity']) if data.get('capacity') else None,
            feasibility=FeasibilityContext(**data['feasibility']) if data.get('feasibility') else None,
            lh_review=LHReviewContext(**data['lh_review']) if data.get('lh_review') else None,
        )
        
        logger.info(f"✅ Pipeline result loaded for: {identifier}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to load pipeline result: {e}")
        return None


async def get_address_from_result(result: PipelineResult) -> str:
    """
    파이프라인 결과에서 주소 추출
    
    Args:
        result: PipelineResult
        
    Returns:
        주소 문자열
    """
    if result and result.land:
        return result.land.address
    return "주소 정보 없음"


async def create_mock_pipeline_result(context_id: str) -> PipelineResult:
    """
    테스트용 Mock 파이프라인 결과 생성
    
    Args:
        context_id: 컨텍스트 ID
        
    Returns:
        Mock PipelineResult
    """
    logger.warning(f"Creating MOCK pipeline result for: {context_id}")
    
    # Mock Context 생성 (실제 데이터 구조 유지)
    from app.core.context.canonical_land import CanonicalLandContext
    from app.core.context.appraisal_context import AppraisalContext
    from app.core.context.housing_type_context import HousingTypeContext, TypeScore
    from app.core.context.capacity_context_v2 import CapacityContextV2, Scenario
    from app.core.context.feasibility_context import FeasibilityContext
    from app.core.context.lh_review_context import LHReviewContext
    
    # M1: Land
    land_ctx = CanonicalLandContext(
        parcel_id="1168010100100010001",
        address="서울특별시 강남구 역삼동 123-45",
        area_sqm=1000.0,
        area_pyeong=302.5,
        zone_type="제2종일반주거지역",
        zone_district="제2종일반주거지역",
        legal_far=250.0,
        legal_bcr=60.0,
        road_condition="12m 도로 접함",
        is_corner_lot=False,
    )
    
    # M2: Appraisal
    appraisal_ctx = AppraisalContext(
        land_value=3000000000.0,  # 30억
        unit_price=3000000.0,     # 300만원/㎡
        confidence_level="HIGH",
        confidence_score=0.85,
        method_used="거래사례비교법",
        evaluation_date=datetime.now().strftime("%Y-%m-%d"),
    )
    
    # M3: Housing Type
    from app.core.context.housing_type_context import TypeScore
    
    youth_score = TypeScore(
        type_name="청년형",
        type_code="YOUTH",
        total_score=85.0,
        location_score=30.0,
        accessibility_score=28.0,
        poi_score=27.0,
        demand_prediction=85.0,
    )
    
    housing_ctx = HousingTypeContext(
        selected_type="청년형",
        demand_prediction="수요 높음",
        preferred_type=youth_score,
        candidate_types=[youth_score],
    )
    
    # M4: Capacity (V2)
    scenario_a = Scenario(
        name="법정 최대",
        total_units=100,
        total_gfa=25000.0,
        applied_far=250.0,
        parking_spaces=120,
    )
    scenario_b = Scenario(
        name="추천 시나리오",
        total_units=80,
        total_gfa=20000.0,
        applied_far=200.0,
        parking_spaces=100,
    )
    scenario_c = Scenario(
        name="보수적",
        total_units=60,
        total_gfa=15000.0,
        applied_far=150.0,
        parking_spaces=80,
    )
    
    capacity_ctx = CapacityContextV2(
        scenario_a=scenario_a,
        scenario_b=scenario_b,
        scenario_c=scenario_c,
        recommended_scenario="B",
    )
    
    # M5: Feasibility
    feasibility_ctx = FeasibilityContext(
        total_cost=15000000000.0,    # 150억
        total_revenue=18000000000.0,  # 180억
        irr_pct=12.5,
        npv=2500000000.0,             # 25억
        roi_pct=20.0,
        payback_years=7.5,
    )
    
    # M6: LH Review
    lh_review_ctx = LHReviewContext(
        total_score=82.5,
        grade="A",
        approval_probability=75.0,
        decision="추진 권장",
        final_decision="추진 권장",
    )
    
    return PipelineResult(
        land=land_ctx,
        appraisal=appraisal_ctx,
        housing_type=housing_ctx,
        capacity=capacity_ctx,
        feasibility=feasibility_ctx,
        lh_review=lh_review_ctx,
    )
