"""
Test Pre-Report Composer

목적:
- Pre-Report (2페이지) 생성 검증
- 데이터 구조 확인
- LH 가능성 판단 로직 검증
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.report_composers.pre_report_composer import PreReportComposer
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


def create_mock_land_diagnosis():
    """Mock Land Diagnosis 생성"""
    return {
        'address': '서울특별시 마포구 월드컵북로 120',
        'development_potential': 'HIGH',
        'risk_level': 'MEDIUM',
    }


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


def test_pre_report_generation():
    """Test Pre-Report (2p) generation"""
    
    print("\n" + "="*80)
    print("ZeroSite v8.9 - Pre-Report Composer Test")
    print("="*80)
    
    # Given
    print("\n📋 STEP 1: Creating mock data...")
    appraisal_ctx = create_mock_appraisal_context()
    land_diagnosis = create_mock_land_diagnosis()
    lh_result = create_mock_lh_result()
    ch4_scores = create_mock_ch4_scores()
    
    print("   ✅ Mock data created")
    print(f"   Appraisal Context: LOCKED")
    print(f"   Land Area: 660㎡")
    print(f"   LH Decision: {lh_result['decision']}")
    
    # When
    print("\n📋 STEP 2: Generating Pre-Report...")
    composer = PreReportComposer(appraisal_ctx, land_diagnosis, lh_result, ch4_scores)
    report = composer.generate()
    
    # Then
    print("\n📋 STEP 3: Verifying report structure...")
    
    assert 'report_id' in report, "Report ID missing"
    assert report['report_type'] == 'pre_report', "Wrong report type"
    assert report['total_pages'] == 2, "Wrong page count"
    assert 'page_1_executive_summary' in report, "Page 1 (Executive Summary) missing"
    assert 'page_2_quick_analysis' in report, "Page 2 (Quick Analysis) missing"
    
    print("   ✅ Report structure verified")
    
    # Verify Page 1 - Executive Summary (v3.3)
    print("\n📋 STEP 4: Verifying Page 1 (Executive Summary)...")
    page1 = report['page_1_executive_summary']
    
    assert 'land_basic_info' in page1, "Land basic info missing"
    assert 'lh_possibility_gauge' in page1, "LH possibility gauge missing"
    assert 'key_metrics' in page1, "Key metrics missing"
    assert 'key_strengths' in page1, "Key strengths missing"
    assert 'review_items' in page1, "Review items missing"
    assert page1['lh_possibility_gauge'] in ['HIGH', 'MEDIUM', 'LOW'], "Invalid LH possibility"
    
    print(f"   ✅ Page 1 (Executive Summary) verified")
    print(f"      Address: {page1['land_basic_info']['address']}")
    print(f"      Land Area: {page1['land_basic_info']['land_area_sqm']}㎡")
    print(f"      Zone Type: {page1['land_basic_info']['zone_type']}")
    print(f"      LH Possibility: {page1['lh_possibility_icon']} {page1['lh_possibility_gauge']}")
    print(f"      Key Metrics: {list(page1['key_metrics'].keys())}")
    print(f"      Key Strengths: {len(page1['key_strengths'])} items")
    
    # Verify Page 2 - Quick Analysis (v3.3)
    print("\n📋 STEP 5: Verifying Page 2 (Quick Analysis)...")
    page2 = report['page_2_quick_analysis']
    
    assert 'development_overview_table' in page2, "Development overview table missing"
    assert 'supply_type_visualization' in page2, "Supply type visualization missing"
    assert 'next_steps_cta' in page2, "Next steps CTA missing"
    
    print(f"   ✅ Page 2 (Quick Analysis) verified")
    print(f"      Development Overview: {len(page2['development_overview_table'])} items")
    print(f"      Supply Type Chart: {page2['supply_type_visualization']['chart_type']}")
    print(f"      CTA Title: {page2['next_steps_cta']['title']}")
    
    # Display development overview
    print("\n   📊 Development Overview:")
    for key, item in list(page2['development_overview_table'].items())[:3]:
        print(f"      • {item['item']}: {item['value']}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - Pre-Report Composer Working Correctly")
    print("="*80)
    
    return report


if __name__ == "__main__":
    test_pre_report_generation()
