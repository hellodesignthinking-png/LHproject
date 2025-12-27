#!/usr/bin/env python3
"""
ZeroSite v4.0 Chart Generator Test
===================================

차트 생성 테스트

Author: ZeroSite Visualization Team
Date: 2025-12-26
"""

import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.context.canonical_land import CanonicalLandContext
from app.modules.m2_appraisal.service import AppraisalService
from app.modules.m3_lh_demand.service import LHDemandService
from app.modules.m4_capacity.service_v2 import CapacityServiceV2
from app.modules.m5_feasibility.service import FeasibilityService
from app.modules.m6_lh_review.service_v3 import LHReviewServiceV3
from app.modules.visualization.chart_generator import ChartGenerator


def main():
    """차트 생성 테스트"""
    
    print("\n" + "="*80)
    print("  ZeroSite v4.0 Chart Generator Test")
    print("  차트 자동 생성")
    print("="*80 + "\n")
    
    # 테스트 부지
    land_ctx = CanonicalLandContext(
        parcel_id="1168010100106480023",
        address="서울특별시 강남구 역삼동 648-23",
        road_address="서울특별시 강남구 테헤란로 123",
        coordinates=(37.4995539438207, 127.031393491745),
        sido="서울특별시",
        sigungu="강남구",
        dong="역삼동",
        area_sqm=500.0,
        area_pyeong=151.25,
        land_category="대",
        land_use="주거용",
        zone_type="제2종일반주거지역",
        zone_detail="7층 이하",
        far=200.0,
        bcr=60.0,
        road_width=6.0,
        road_type="중로",
        terrain_height="평지",
        terrain_shape="정형",
        regulations={},
        restrictions=[],
        data_source="Test Data",
        retrieval_date="2025-12-26"
    )
    
    # M2-M6 파이프라인
    print("[STEP 1] M2→M6 파이프라인 실행...\n")
    
    m2_service = AppraisalService(use_enhanced_services=True)
    m2_result = m2_service.run(land_ctx, asking_price=None)
    print(f"  ✓ M2 완료: ₩{m2_result.land_value:,}")
    
    m3_service = LHDemandService()
    m3_result = m3_service.run(land_ctx)
    print(f"  ✓ M3 완료: {m3_result.selected_type_name}")
    
    m4_service = CapacityServiceV2()
    m4_result = m4_service.run(land_ctx, m3_result)
    print(f"  ✓ M4 완료: {m4_result.incentive_capacity.total_units}세대")
    
    m5_service = FeasibilityService()
    m5_result = m5_service.run(m2_result, m4_result)
    print(f"  ✓ M5 완료: NPV ₩{m5_result.financial_metrics.npv_public:,}")
    
    m6_service = LHReviewServiceV3()
    m6_result = m6_service.run(
        land_ctx=land_ctx,
        appraisal_ctx=m2_result,
        housing_type_ctx=m3_result,
        capacity_ctx=m4_result,
        feasibility_ctx=m5_result
    )
    print(f"  ✓ M6 완료: {m6_result.judgement.value} ({m6_result.lh_score_total:.1f}/100)\n")
    
    # 차트 생성
    print("[STEP 2] 차트 생성 시작...\n")
    
    chart_gen = ChartGenerator(output_dir="output/charts")
    
    # 1. LH 점수표 차트
    print("  [1/3] LH 점수표 차트...")
    section_scores = {
        "A": m6_result.section_a_policy.weighted_score,
        "B": m6_result.section_b_location.weighted_score,
        "C": m6_result.section_c_construction.weighted_score,
        "D": m6_result.section_d_price.weighted_score,
        "E": m6_result.section_e_business.weighted_score
    }
    
    lh_chart = chart_gen.generate_lh_scorecard_chart(
        section_scores=section_scores,
        total_score=m6_result.lh_score_total,
        file_name="test_lh_scorecard.png"
    )
    
    # 2. 재무 분석 차트
    print("  [2/3] 재무 분석 차트...")
    cost_breakdown = {
        "토지매입": m5_result.cost_breakdown.land_acquisition_cost,
        "건축": m5_result.cost_breakdown.construction_cost,
        "설계": m5_result.cost_breakdown.design_cost,
        "간접": m5_result.cost_breakdown.indirect_cost,
        "금융": m5_result.cost_breakdown.financing_cost,
        "예비": m5_result.cost_breakdown.contingency
    }
    
    revenue_projection = {
        "LH매입": m5_result.revenue_projection.lh_purchase_price,
        "민간분양": m5_result.revenue_projection.private_sale_revenue,
        "임대수익": m5_result.revenue_projection.rental_income_annual
    }
    
    financial_chart = chart_gen.generate_financial_chart(
        cost_breakdown=cost_breakdown,
        revenue_projection=revenue_projection,
        npv=m5_result.financial_metrics.npv_public,
        irr=m5_result.financial_metrics.irr_public,
        file_name="test_financial.png"
    )
    
    # 3. 건축 규모 비교 차트
    print("  [3/3] 건축 규모 비교 차트...")
    legal_capacity = {
        "applied_far": m4_result.input_legal_far,
        "applied_bcr": m4_result.legal_capacity.applied_bcr,
        "total_units": m4_result.legal_capacity.total_units,
        "required_parking_spaces": m4_result.legal_capacity.required_parking_spaces
    }
    
    incentive_capacity = {
        "applied_far": m4_result.input_incentive_far,
        "applied_bcr": m4_result.incentive_capacity.applied_bcr,
        "total_units": m4_result.incentive_capacity.total_units,
        "required_parking_spaces": m4_result.incentive_capacity.required_parking_spaces
    }
    
    capacity_chart = chart_gen.generate_capacity_comparison_chart(
        legal_capacity=legal_capacity,
        incentive_capacity=incentive_capacity,
        file_name="test_capacity.png"
    )
    
    print("\n" + "="*80)
    print("  차트 생성 완료")
    print("="*80)
    print(f"\n📊 생성된 차트:")
    print(f"   1. LH 점수표: {lh_chart}")
    print(f"   2. 재무 분석: {financial_chart}")
    print(f"   3. 건축 규모: {capacity_chart}")
    print("\n" + "="*80 + "\n")
    
    print("✓ Chart Generator Test COMPLETED\n")


if __name__ == "__main__":
    main()
