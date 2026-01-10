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
    from app.core.context.capacity_context_v2 import (
        CapacityContextV2, GFABreakdown, CapacityScale, 
        MassingOption, UnitSummary, ParkingSolution
    )
    from app.core.context.feasibility_context import FeasibilityContext
    from app.core.context.lh_review_context import LHReviewContext
    
    # M1: Land
    land_ctx = CanonicalLandContext(
        parcel_id="1168010100100010001",
        address="서울특별시 강남구 역삼동 123-45",
        area_sqm=1000.0,
        area_pyeong=302.5,
        zone_type="제2종일반주거지역",
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
    
    # M4: Capacity (V2) - 실제 구조에 맞춘 Mock 데이터
    from app.core.context.capacity_context_v2 import (
        GFABreakdown, CapacityScale, MassingOption, 
        UnitSummary, ParkingSolution, RampCondition,
        ParkingType, RampFeasibility
    )
    
    # GFA Breakdown
    gfa_breakdown_legal = GFABreakdown(
        total_gfa_sqm=25000.0,
        nia_sqm=18750.0,
        nia_ratio=75.0,
        common_core_sqm=3750.0,
        common_corridor_sqm=1250.0,
        common_shared_sqm=625.0,
        common_total_sqm=5625.0,
        common_ratio=22.5,
        mechanical_sqm=500.0,
        loss_sqm=125.0,
        mechanical_loss_ratio=2.5,
    )
    
    gfa_breakdown_incentive = GFABreakdown(
        total_gfa_sqm=30000.0,
        nia_sqm=22500.0,
        nia_ratio=75.0,
        common_core_sqm=4500.0,
        common_corridor_sqm=1500.0,
        common_shared_sqm=750.0,
        common_total_sqm=6750.0,
        common_ratio=22.5,
        mechanical_sqm=600.0,
        loss_sqm=150.0,
        mechanical_loss_ratio=2.5,
    )
    
    # Capacity Scales
    legal_capacity = CapacityScale(
        applied_far=250.0,
        applied_bcr=60.0,
        max_footprint_sqm=600.0,
        target_gfa_sqm=25000.0,
        gfa_breakdown=gfa_breakdown_legal,
        total_units=100,
        unit_type_distribution={"30㎡": 70, "45㎡": 30},
        average_unit_area_sqm=33.75,
        required_parking_spaces=120,
        parking_ratio=1.2,
    )
    
    incentive_capacity = CapacityScale(
        applied_far=300.0,
        applied_bcr=60.0,
        max_footprint_sqm=600.0,
        target_gfa_sqm=30000.0,
        gfa_breakdown=gfa_breakdown_incentive,
        total_units=120,
        unit_type_distribution={"30㎡": 84, "45㎡": 36},
        average_unit_area_sqm=33.75,
        required_parking_spaces=144,
        parking_ratio=1.2,
    )
    
    # Massing Options
    massing_option_a = MassingOption(
        option_id="A",
        option_name="2개동 × 15층",
        building_count=2,
        floors_per_building=15,
        standard_floor_area_sqm=400.0,
        units_per_floor=4,
        achieved_gfa_sqm=30000.0,
        achieved_far=300.0,
        far_achievement_rate=1.0,
        site_coverage_ratio=60.0,
        open_space_ratio=40.0,
        buildability_score=85.0,
        efficiency_score=90.0,
        remarks=["효율적 배치", "엘리베이터 2개동"],
    )
    
    # Unit Summary
    unit_summary = UnitSummary(
        total_units=100,
        preferred_unit_type="청년형 30㎡",
        unit_mix_ratio={"30㎡": 0.7, "45㎡": 0.3},
        unit_count_by_type={"30㎡": 70, "45㎡": 30},
        unit_area_by_type={"30㎡": 30.0, "45㎡": 45.0},
        min_unit_area_sqm=30.0,
        max_unit_area_sqm=45.0,
        average_unit_area_sqm=33.75,
    )
    
    # Ramp Condition
    ramp_condition = RampCondition(
        ramp_width_m=5.5,
        ramp_length_m=45.0,
        turning_radius_m=6.0,
        non_residential_area_sqm=150.0,
        feasibility=RampFeasibility.FEASIBLE,
        constraint_issues=[],
    )
    
    # Parking Solution (주차 우선)
    parking_solution = ParkingSolution(
        solution_type="alternative_B",
        solution_name="주차 우선 시나리오",
        parking_type=ParkingType.SELF_PARKING,
        total_parking_spaces=120,
        self_parking_spaces=120,
        basement_floors=3,
        ramp_condition=ramp_condition,
        mechanical_parking_spaces=0,
        mechanical_type=None,
        adjusted_total_units=100,
        adjusted_floors=None,
        adjusted_gfa_sqm=None,
        far_sacrifice_ratio=0.0,
        parking_achievability_score=95.0,
        remarks=["법정 주차대수 확보", "지하 3층 자주식"],
    )
    
    capacity_ctx = CapacityContextV2(
        legal_capacity=legal_capacity,
        incentive_capacity=incentive_capacity,
        massing_options=[massing_option_a],
        unit_summary=unit_summary,
        parking_solutions={"alternative_B": parking_solution},
        calculation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
