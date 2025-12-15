"""
Test LH Decision Report Composer

목적:
- LH Decision Report 생성 검증
- Pass/Fail 예측 로직 확인
- 개선 방안 생성 검증
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.report_composers.lh_decision_report_composer import LHDecisionReportComposer
from app.services.appraisal_context import AppraisalContextLock
from app.services.canonical_schema import CanonicalAppraisalResult, ZoningInfo


def create_mock_appraisal_context():
    """Mock AppraisalContextLock 생성"""
    
    from app.services.canonical_schema import (
        OfficialLandPrice, PremiumInfo, PremiumDetail,
        CalculationInfo, ConfidenceInfo, ConfidenceFactors,
        MetadataInfo
    )
    
    # Mock zoning info
    zoning = ZoningInfo(
        confirmed_type="제2종일반주거지역",
        floor_area_ratio=250.0,
        building_coverage_ratio=50.0
    )
    
    # Create mock appraisal result directly
    result = CanonicalAppraisalResult(
        zoning=zoning,
        official_land_price=OfficialLandPrice(
            standard_price_per_sqm=5500000,
            reference_year=2024,
            reference_parcel="서울특별시 마포구 XX-XX",
            distance_to_standard=100.0
        ),
        premium=PremiumInfo(
            development_potential=PremiumDetail(rate=0.045, rationale="개발 잠재력"),
            location_premium=PremiumDetail(rate=0.03, rationale="입지 우수"),
            policy_benefit=PremiumDetail(rate=0.015, rationale="정책 혜택"),
            total_premium_rate=0.09
        ),
        calculation=CalculationInfo(
            base_price_per_sqm=5775000,
            premium_adjusted_per_sqm=6294750,
            land_area_sqm=660.0,
            final_appraised_total=4154535000
        ),
        confidence=ConfidenceInfo(
            score=0.80,
            factors=ConfidenceFactors(
                data_completeness=0.85,
                case_similarity=0.78,
                time_relevance=0.77
            )
        ),
        metadata=MetadataInfo()
    )
    
    # Create and lock context
    ctx = AppraisalContextLock()
    # Convert Pydantic model to dict for lock method
    ctx.lock(result.model_dump())
    
    return ctx


def create_mock_lh_result():
    """Mock LH Result 생성"""
    return {
        'decision': 'GO',
        'roi': 27.44,
        'construction_cost': 8400000000,
        'verified_cost': 627387750,
        'total_cost': 13182261750,
        'lh_purchase_price': 16800000000,
    }


def create_mock_ch3_scores():
    """Mock CH3 Scores 생성"""
    return {
        'overall_score': 85.0,
        'financial_feasibility': 90.0,
        'market_feasibility': 82.0,
    }


def create_mock_ch4_scores():
    """Mock CH4 Scores 생성"""
    return {
        'type_scores': {
            '행복주택': 15.2,
            '청년': 14.8,
            '신혼부부': 14.2,
            '일반': 13.5,
            '공공임대': 12.8,
        }
    }


def test_lh_decision_report_generation():
    """Test LH Decision Report generation"""
    
    print("\n" + "="*80)
    print("ZeroSite v8.9 - LH Decision Report Composer Test")
    print("="*80)
    
    # Given
    print("\n📋 STEP 1: Creating mock data...")
    appraisal_ctx = create_mock_appraisal_context()
    lh_result = create_mock_lh_result()
    ch3_scores = create_mock_ch3_scores()
    ch4_scores = create_mock_ch4_scores()
    
    print("   ✅ Mock data created")
    print(f"   Appraisal Context: LOCKED")
    print(f"   LH Decision: {lh_result['decision']}")
    print(f"   ROI: {lh_result['roi']:.2f}%")
    
    # When
    print("\n📋 STEP 2: Generating LH Decision Report...")
    composer = LHDecisionReportComposer(appraisal_ctx, lh_result, ch3_scores, ch4_scores)
    report = composer.generate()
    
    # Then
    print("\n📋 STEP 3: Verifying report structure...")
    
    assert 'report_id' in report, "Report ID missing"
    assert report['report_type'] == 'lh_decision_report', "Wrong report type"
    assert 'part_1_supply_type' in report, "Part 1 missing"
    assert 'part_2_purchase_price' in report, "Part 2 missing"
    assert 'part_3_pass_fail' in report, "Part 3 missing"
    assert 'part_4_improvements' in report, "Part 4 missing"
    
    print("   ✅ Report structure verified")
    
    # Verify Part 1: Supply Type Analysis
    print("\n📋 STEP 4: Verifying Part 1 (공급유형 적정성)...")
    part1 = report['part_1_supply_type']
    
    assert 'recommended_type' in part1, "Recommended type missing"
    assert 'demand_score' in part1, "Demand score missing"
    assert 'suitability' in part1, "Suitability missing"
    
    print(f"   ✅ Part 1 verified")
    print(f"      Recommended Type: {part1['recommended_type']}")
    print(f"      Demand Score: {part1['normalized_score']:.1f}/100")
    print(f"      Suitability: {part1['suitability']} ({part1['suitability_text']})")
    
    # Verify Part 2: Purchase Price Analysis
    print("\n📋 STEP 5: Verifying Part 2 (매입가 적정성)...")
    part2 = report['part_2_purchase_price']
    
    assert 'land_appraisal' in part2, "Land appraisal missing"
    assert 'construction_cost' in part2, "Construction cost missing"
    assert 'lh_purchase_price' in part2, "LH purchase price missing"
    assert 'adequacy' in part2, "Adequacy missing"
    
    print(f"   ✅ Part 2 verified")
    print(f"      Land Appraisal: {part2['land_appraisal_formatted']}")
    print(f"      Construction Cost: {part2['construction_cost_formatted']}")
    print(f"      Total Cost: {part2['total_cost_formatted']}")
    print(f"      LH Purchase Price: {part2['lh_purchase_price_formatted']}")
    print(f"      Price Ratio: {part2['price_ratio']:.1f}%")
    print(f"      Adequacy: {part2['adequacy']} ({part2['adequacy_text']})")
    
    # Verify Part 3: Pass/Fail Prediction
    print("\n📋 STEP 6: Verifying Part 3 (Pass/Fail 예측)...")
    part3 = report['part_3_pass_fail']
    
    assert 'prediction' in part3, "Prediction missing"
    assert part3['prediction'] in ['PASS', 'CONDITIONAL', 'FAIL'], "Invalid prediction"
    assert 'pass_factors' in part3, "Pass factors missing"
    assert 'fail_risks' in part3, "Fail risks missing"
    
    print(f"   ✅ Part 3 verified")
    print(f"      Prediction: {part3['prediction_icon']} {part3['prediction']} ({part3['prediction_text']})")
    print(f"      Confidence: {part3['confidence_percentage']}%")
    print(f"      Overall Score: {part3['overall_score']}/100")
    
    print(f"\n      Pass Factors ({part3['pass_factors_count']}):")
    for factor in part3['pass_factors']:
        print(f"         {factor}")
    
    if part3['fail_risks']:
        print(f"\n      Fail Risks ({part3['fail_risks_count']}):")
        for risk in part3['fail_risks']:
            print(f"         {risk}")
    
    # Verify Part 4: Improvement Strategies
    print("\n📋 STEP 7: Verifying Part 4 (개선 방안)...")
    part4 = report['part_4_improvements']
    
    assert 'improvement_strategies' in part4, "Improvement strategies missing"
    assert 'alternative_scenarios' in part4, "Alternative scenarios missing"
    assert 'recommendation' in part4, "Recommendation missing"
    
    print(f"   ✅ Part 4 verified")
    print(f"      Improvement Strategies: {part4['improvement_count']}")
    print(f"      Alternative Scenarios: {len(part4['alternative_scenarios'])}")
    print(f"      Estimated Timeline: {part4['estimated_timeline']}")
    print(f"      Final Recommendation: {part4['recommendation']}")
    
    if part4['improvement_strategies']:
        print(f"\n      Strategies:")
        for strategy in part4['improvement_strategies']:
            print(f"         [{strategy['priority']}] {strategy['strategy']}")
            print(f"            Impact: {strategy['estimated_impact']}")
            print(f"            Timeline: {strategy['timeline']}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - LH Decision Report Composer Working Correctly")
    print("="*80)
    
    return report


if __name__ == "__main__":
    test_lh_decision_report_generation()
