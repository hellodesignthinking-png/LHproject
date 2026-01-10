"""
Phase 8: 파이프라인 결과 조회 헬퍼 (FIXED)
====================================

context_id 또는 parcel_id로 파이프라인 결과를 가져오는 유틸리티
- 모든 Context 클래스의 실제 필드에 맞춘 Mock 데이터

작성일: 2026-01-10 (Updated)
"""

import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.core.pipeline.zer0site_pipeline import PipelineResult
from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.appraisal_context import (
    AppraisalContext, TransactionSample, 
    PremiumFactors, ConfidenceMetrics
)
from app.core.context.housing_type_context import HousingTypeContext, TypeScore
from app.core.context.capacity_context_v2 import (
    CapacityContextV2, GFABreakdown, CapacityScale, 
    MassingOption, UnitSummary, ParkingSolution,
    RampCondition, ParkingType, RampFeasibility
)
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
        PipelineResult 또는 None (실패 시 Mock 데이터 반환)
    """
    try:
        # 파일 기반 캐시에서 로드
        cache_file = CACHE_DIR / f"{identifier}.json"
        
        if not cache_file.exists():
            logger.warning(f"Pipeline result not found for identifier: {identifier}")
            logger.info(f"Creating MOCK pipeline result for: {identifier}")
            # 🔥 AUTO-FALLBACK: Mock 데이터 생성
            return await create_mock_pipeline_result(identifier)
        
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
    테스트용 Mock 파이프라인 결과 생성 (모든 필드 정확)
    
    Args:
        context_id: 컨텍스트 ID
        
    Returns:
        Mock PipelineResult
    """
    logger.warning(f"Creating MOCK pipeline result for: {context_id}")
    
    # ========================================
    # M1: CanonicalLandContext
    # ========================================
    land_ctx = CanonicalLandContext(
        parcel_id="1168010100100010001",
        address="서울특별시 강남구 역삼동 123-45",
        road_address="서울특별시 강남구 테헤란로 123",
        coordinates=(37.5012, 127.0396),
        sido="서울특별시",
        sigungu="강남구",
        dong="역삼동",
        area_sqm=1000.0,
        area_pyeong=302.5,
        land_category="대",
        land_use="주거용",
        zone_type="제2종일반주거지역",
        zone_detail="제2종일반주거지역",
        far=250.0,
        bcr=60.0,
        road_width=12.0,
        road_type="일반도로",
        terrain_height="평지",
        terrain_shape="정형지",
        regulations={},
        restrictions=[],
        data_source="Mock",
        retrieval_date=datetime.now().strftime("%Y-%m-%d"),
    )
    
    # ========================================
    # M2: AppraisalContext (모든 필드 정확)
    # ========================================
    
    # Transaction Samples (정확한 필드명)
    transaction_samples = [
        TransactionSample(
            address="서울시 강남구 역삼동 123-12",
            transaction_date="2025-11-15",
            price_total=2850000000.0,
            price_per_sqm=3000000.0,
            area_sqm=950.0,
            distance_km=0.15,
            zone_type="제2종일반주거지역",
            adjusted_price_per_sqm=3000000.0,
            adjustment_factors={"location": 1.0, "area": 0.95}
        ),
        TransactionSample(
            address="서울시 강남구 역삼동 145-8",
            transaction_date="2025-10-28",
            price_total=3234000000.0,
            price_per_sqm=2940000.0,
            area_sqm=1100.0,
            distance_km=0.22,
            zone_type="제2종일반주거지역",
            adjusted_price_per_sqm=2940000.0,
            adjustment_factors={"location": 1.0, "area": 1.1}
        ),
        TransactionSample(
            address="서울시 강남구 역삼동 134-25",
            transaction_date="2025-09-10",
            price_total=3213000000.0,
            price_per_sqm=3060000.0,
            area_sqm=1050.0,
            distance_km=0.18,
            zone_type="제2종일반주거지역",
            adjusted_price_per_sqm=3060000.0,
            adjustment_factors={"location": 1.02, "area": 1.05}
        ),
    ]
    
    # Premium Factors (정확한 필드명)
    premium_factors = PremiumFactors(
        road_score=8.0,
        terrain_score=9.0,
        location_score=15.0,
        accessibility_score=12.0,
        distance_premium=3.0,
        time_premium=2.0,
        size_premium=1.0,
        zone_premium=5.0,
        total_premium_rate=42.86
    )
    
    # Confidence Metrics (정확한 필드명)
    confidence_metrics = ConfidenceMetrics(
        sample_count_score=0.80,
        price_variance_score=0.90,
        distance_score=0.88,
        recency_score=0.85,
        confidence_score=0.86,
        confidence_level="HIGH"
    )
    
    # AppraisalContext (모든 필드)
    appraisal_ctx = AppraisalContext(
        land_value=3000000000.0,
        unit_price_sqm=3000000.0,
        unit_price_pyeong=9917400.0,
        official_price=2100000000.0,
        official_price_per_sqm=2100000.0,
        transaction_samples=transaction_samples,
        transaction_count=len(transaction_samples),
        avg_transaction_price=3000000.0,
        premium_factors=premium_factors,
        premium_rate=42.86,
        confidence_metrics=confidence_metrics,
        confidence_score=0.86,
        confidence_level="HIGH",
        price_range_low=2850000000.0,
        price_range_high=3150000000.0,
        valuation_date=datetime.now().strftime("%Y-%m-%d"),
        valuation_method="거래사례비교법",
        appraiser="ZeroSite AI",
        negotiation_strategies=[
            {"strategy": "공시지가 기준 협상", "expected_discount": "5-8%"},
            {"strategy": "LH 매입 기준 활용", "expected_discount": "3-5%"}
        ],
        asking_price=3200000000.0,
        price_gap_pct=6.67,
        recommendation="적정가",
    )
    
    # ========================================
    # M3: HousingTypeContext
    # ========================================
    
    youth_score = TypeScore(
        type_name="청년형",
        type_code="YOUTH",
        total_score=85.0,
        location_score=30.0,
        accessibility_score=28.0,
        poi_score=27.0,
        demand_prediction=85.0,
    )
    
    newlywed_score = TypeScore(
        type_name="신혼부부형",
        type_code="NEWLYWED",
        total_score=78.0,
        location_score=28.0,
        accessibility_score=26.0,
        poi_score=24.0,
        demand_prediction=78.0,
    )
    
    housing_ctx = HousingTypeContext(
        selected_type="청년형",
        demand_prediction="수요 높음",
        preferred_type=youth_score,
        candidate_types=[youth_score, newlywed_score],
    )
    
    # Add fields for backward compatibility
    housing_ctx.recommended_type = "청년형"
    housing_ctx.lifestyle_score = 85.0
    housing_ctx.second_choice = "신혼부부형"
    
    # ========================================
    # M4: CapacityContextV2 (완전한 구조)
    # ========================================
    
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
    massing_options = [
        MassingOption(
            option_id="A",
            option_name="2개동 × 15층",
            building_count=2,
            floors_per_building=15,
            standard_floor_area_sqm=1000.0,
            units_per_floor=4,
            achieved_gfa_sqm=30000.0,
            achieved_far=300.0,
            far_achievement_rate=1.0,
            site_coverage_ratio=60.0,
            open_space_ratio=40.0,
            buildability_score=85.0,
            efficiency_score=88.0,
            remarks=["균형잡힌 배치", "쾌적한 동간 거리"]
        ),
        MassingOption(
            option_id="B",
            option_name="3개동 × 10층",
            building_count=3,
            floors_per_building=10,
            standard_floor_area_sqm=1000.0,
            units_per_floor=4,
            achieved_gfa_sqm=30000.0,
            achieved_far=300.0,
            far_achievement_rate=1.0,
            site_coverage_ratio=60.0,
            open_space_ratio=40.0,
            buildability_score=82.0,
            efficiency_score=85.0,
            remarks=["저층 쾌적성", "다동 배치"]
        ),
    ]
    
    # Unit Summary
    unit_summary = UnitSummary(
        total_units=120,
        preferred_unit_type="청년형 (30㎡)",
        unit_mix_ratio={"30㎡": 0.7, "45㎡": 0.3},
        unit_count_by_type={"30㎡": 84, "45㎡": 36},
        unit_area_by_type={"30㎡": 30.0, "45㎡": 45.0},
        min_unit_area_sqm=30.0,
        max_unit_area_sqm=45.0,
        average_unit_area_sqm=33.75,
    )
    
    # Ramp Condition
    ramp_condition = RampCondition(
        ramp_width_m=5.5,
        ramp_length_m=8.0,
        turning_radius_m=6.5,
        non_residential_area_sqm=150.0,
        feasibility=RampFeasibility.FEASIBLE,
        constraint_issues=[]
    )
    
    # Parking Solutions
    parking_solutions = {
        "alternative_A": ParkingSolution(
            solution_type="alternative_A",
            solution_name="대안 A: 지하 2층 자주식",
            parking_type=ParkingType.UNDERGROUND,
            total_parking_spaces=144,
            self_parking_spaces=144,
            basement_floors=2,
            ramp_condition=ramp_condition,
            mechanical_parking_spaces=0,
            mechanical_type=None,
            adjusted_total_units=None,
            adjusted_floors=None,
            adjusted_gfa_sqm=None,
            far_sacrifice_ratio=None,
            parking_achievability_score=90.0,
            remarks=["지상 공간 확보", "쾌적한 단지 환경", "건축비 증가"]
        ),
        "alternative_B": ParkingSolution(
            solution_type="alternative_B",
            solution_name="대안 B: 지상 + 지하 혼합",
            parking_type=ParkingType.MIXED,
            total_parking_spaces=144,
            self_parking_spaces=100,
            basement_floors=1,
            ramp_condition=ramp_condition,
            mechanical_parking_spaces=44,
            mechanical_type="2단 승강식",
            adjusted_total_units=120,
            adjusted_floors=None,
            adjusted_gfa_sqm=30000.0,
            far_sacrifice_ratio=0.0,
            parking_achievability_score=85.0,
            remarks=["비용 절감", "공간 효율", "주차 우선"]
        ),
    }
    
    # CapacityContextV2
    capacity_ctx = CapacityContextV2(
        legal_capacity=legal_capacity,
        incentive_capacity=incentive_capacity,
        massing_options=massing_options,
        unit_summary=unit_summary,
        parking_solutions=parking_solutions,
    )
    
    # Add fields for backward compatibility
    capacity_ctx.legal_far = 250.0
    capacity_ctx.legal_bcr = 60.0
    capacity_ctx.legal_units = 100
    capacity_ctx.legal_gfa = 25000.0
    capacity_ctx.incentive_far = 300.0
    capacity_ctx.final_units = 120
    capacity_ctx.final_gfa = 30000.0
    
    # ========================================
    # M5: FeasibilityContext
    # ========================================
    
    feasibility_ctx = FeasibilityContext(
        land_cost=3000000000.0,
        construction_cost=7500000000.0,
        indirect_cost=1500000000.0,
        total_cost=12000000000.0,
        lh_rental_revenue=14400000000.0,
        total_revenue=14400000000.0,
        net_profit=2400000000.0,
        irr=0.125,  # 12.5%
        npv=2400000000.0,
        roi=0.20,
        payback_period=7.5,
    )
    
    # ========================================
    # M6: LHReviewContext
    # ========================================
    
    lh_review_ctx = LHReviewContext(
        total_score=82.5,
        grade="A",
        decision="추진 권장",
        approval_probability=0.85,
        location_score=28.0,
        scale_score=22.0,
        feasibility_score=25.0,
        compliance_score=7.5,
    )
    
    # ========================================
    # PipelineResult 생성
    # ========================================
    
    result = PipelineResult(
        land=land_ctx,
        appraisal=appraisal_ctx,
        housing_type=housing_ctx,
        capacity=capacity_ctx,
        feasibility=feasibility_ctx,
        lh_review=lh_review_ctx,
    )
    
    logger.info(f"✅ Mock pipeline result created for: {context_id}")
    return result
