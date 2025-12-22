"""
Test Comprehensive Report Composer v3.3

목적:
- Comprehensive Report (15-20 pages) 생성 검증
- 7개 섹션 모두 생성 확인
- target_audience별 강조점 차이 확인
- LH Decision 통합 정확성 확인
- Financial Engine 통합 정확성 확인
- 15-20장 분량 검증
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.report_composers.comprehensive_report_composer import ComprehensiveReportComposer
from app.services.appraisal_context import AppraisalContextLock
from app.services.canonical_schema import (
    CanonicalAppraisalResult, ZoningInfo, OfficialLandPrice,
    PremiumInfo, PremiumDetail, CalculationInfo,
    ConfidenceInfo, ConfidenceFactors, MetadataInfo
)


def create_complete_mock_data():
    """Create complete mock data for comprehensive report test"""
    
    # 1. Appraisal Context (FACT - 절대 수정 불가)
    zoning = ZoningInfo(
        confirmed_type="제2종일반주거지역",
        floor_area_ratio=250.0,
        building_coverage_ratio=50.0
    )
    
    appraisal_result = CanonicalAppraisalResult(
        zoning=zoning,
        official_land_price=OfficialLandPrice(
            standard_price_per_sqm=5500000,
            reference_year=2024,
            reference_parcel="서울특별시 마포구 XX-XX",
            distance_to_standard=100.0
        ),
        premium=PremiumInfo(
            development_potential=PremiumDetail(rate=0.045, rationale="역세권 개발 가능성"),
            location_premium=PremiumDetail(rate=0.03, rationale="지하철 300m, 학교 400m"),
            policy_benefit=PremiumDetail(rate=0.015, rationale="LH 공공주택 정책 혜택"),
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
    
    appraisal_ctx = AppraisalContextLock()
    appraisal_ctx.lock(appraisal_result.model_dump())
    
    # 2. Land Diagnosis (INTERPRETATION)
    land_diagnosis = {
        'address': '서울특별시 마포구 월드컵북로 120',
        'development_potential': 'HIGH',
        'risk_level': 'MEDIUM',
        'architectural_efficiency': 80,
        'demand_suitability': 'A',
    }
    
    # 3. LH Analysis (JUDGMENT)
    lh_result = {
        'decision': 'GO',
        'roi': 27.44,
        'construction_cost': 8400000000,
        'verified_cost': 627387750,
        'total_cost': 13182261750,
        'lh_purchase_price': 16800000000,
        'estimated_revenue': 16800000000,
    }
    
    # 4. CH3 Scores
    ch3_scores = {
        'overall_score': 85.0,
        'financial_feasibility': 90.0,
        'market_feasibility': 82.0,
    }
    
    # 5. CH4 Scores
    ch4_scores = {
        'type_scores': {
            '행복주택': 15.2,
            '청년': 14.8,
            '신혼부부': 14.2,
            '일반': 13.5,
            '공공임대': 12.8,
        }
    }
    
    # 6. Risk Matrix (optional)
    risk_matrix = {
        'total_risk_score': 25,
        'risk_items': [
            {
                'risk_id': 'R001',
                'category': '접근성',
                'risk_item': '도로 접근',
                'level': 'LOW',
                'probability': 'LOW',
                'impact': 'MEDIUM',
                'mitigation_strategy': '도로 확장 계획 확인'
            }
        ]
    }
    
    # 7. Financial Analysis (optional)
    financial_analysis = {
        'irr': 27.44,
        'roi': 27.44,
        'npv': 3617738250,
        'payback_months': 18
    }
    
    return (appraisal_ctx, land_diagnosis, lh_result, ch3_scores, 
            ch4_scores, risk_matrix, financial_analysis)


def test_all_sections_generated():
    """Test: 7개 섹션 + appendix 모두 존재"""
    
    print("\n" + "="*100)
    print("TEST 1: All Sections Generated")
    print("="*100)
    
    # Given
    (appraisal_ctx, land_diagnosis, lh_result, ch3_scores, 
     ch4_scores, risk_matrix, financial_analysis) = create_complete_mock_data()
    
    composer = ComprehensiveReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result,
        ch3_scores=ch3_scores,
        ch4_scores=ch4_scores,
        risk_matrix=risk_matrix,
        financial_analysis=financial_analysis
    )
    
    # When
    report = composer.compose(target_audience="landowner")
    
    # Then
    required_sections = [
        'section_1_executive_summary',
        'section_2_land_overview',
        'section_3_lh_analysis',
        'section_4_development_feasibility',
        'section_5_financial_analysis',
        'section_6_risk_matrix',
        'section_7_conclusion',
        'appendix'
    ]
    
    for section in required_sections:
        assert section in report, f"Section '{section}' missing"
        print(f"   ✅ {section}: exists")
    
    print("\n✅ TEST 1 PASSED - All 7 sections + appendix generated")
    return report


def test_landowner_emphasis():
    """Test: target_audience='landowner'일 때 Section 3 (LH) 강조"""
    
    print("\n" + "="*100)
    print("TEST 2: Landowner Emphasis (Section 3 LH)")
    print("="*100)
    
    # Given
    (appraisal_ctx, land_diagnosis, lh_result, ch3_scores, 
     ch4_scores, risk_matrix, financial_analysis) = create_complete_mock_data()
    
    composer = ComprehensiveReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result,
        ch3_scores=ch3_scores,
        ch4_scores=ch4_scores
    )
    
    # When
    report = composer.compose(target_audience="landowner")
    
    # Then - Section 3 should have all LH analysis parts
    section_3 = report['section_3_lh_analysis']
    
    required_parts = [
        'part_1_pass_fail_prediction',
        'part_2_supply_type_analysis',
        'part_3_purchase_price_adequacy',
        'part_4_improvement_strategies'
    ]
    
    for part in required_parts:
        assert part in section_3, f"Part '{part}' missing in Section 3"
        print(f"   ✅ {part}: exists")
    
    # Verify LH prediction exists
    prediction = section_3['part_1_pass_fail_prediction']['prediction']
    assert prediction in ['PASS', 'CONDITIONAL', 'FAIL'], f"Invalid prediction: {prediction}"
    
    print(f"\n   LH Prediction: {section_3['part_1_pass_fail_prediction']['prediction_icon']} {prediction}")
    print(f"   Recommended Type: {section_3['part_2_supply_type_analysis']['recommended_type']}")
    print(f"   Price Adequacy: {section_3['part_3_purchase_price_adequacy']['adequacy']}")
    
    print("\n✅ TEST 2 PASSED - Landowner emphasis on LH analysis verified")
    return report


def test_investor_emphasis():
    """Test: target_audience='investor'일 때 Section 5 (Financial) 강조"""
    
    print("\n" + "="*100)
    print("TEST 3: Investor Emphasis (Section 5 Financial)")
    print("="*100)
    
    # Given
    (appraisal_ctx, land_diagnosis, lh_result, ch3_scores, 
     ch4_scores, risk_matrix, financial_analysis) = create_complete_mock_data()
    
    composer = ComprehensiveReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result,
        financial_analysis=financial_analysis
    )
    
    # When
    report = composer.compose(target_audience="investor")
    
    # Then - Section 5 should have all financial analysis parts
    section_5 = report['section_5_financial_analysis']
    
    required_parts = [
        'project_cost_estimation',
        'profitability_metrics',
        'scenario_analysis'
    ]
    
    for part in required_parts:
        assert part in section_5, f"Part '{part}' missing in Section 5"
        print(f"   ✅ {part}: exists")
    
    # Verify financial metrics
    metrics = section_5['profitability_metrics']
    assert 'irr' in metrics, "IRR missing"
    assert 'roi' in metrics, "ROI missing"
    assert 'npv' in metrics, "NPV missing"
    
    print(f"\n   IRR: {metrics['irr']['value']}%")
    print(f"   ROI: {metrics['roi']['value']}%")
    print(f"   NPV: {metrics['npv']['value']:,}원")
    print(f"   Payback: {metrics['payback_period']['value']}개월")
    
    # Verify scenarios
    scenarios = section_5['scenario_analysis']
    assert 'best_case' in scenarios, "Best case scenario missing"
    assert 'base_case' in scenarios, "Base case scenario missing"
    assert 'worst_case' in scenarios, "Worst case scenario missing"
    
    print(f"\n   Scenario Analysis:")
    print(f"      Best Case IRR: {scenarios['best_case']['irr']}%")
    print(f"      Base Case IRR: {scenarios['base_case']['irr']}%")
    print(f"      Worst Case IRR: {scenarios['worst_case']['irr']}%")
    
    print("\n✅ TEST 3 PASSED - Investor emphasis on financial analysis verified")
    return report


def test_lh_integration_accuracy():
    """Test: LH Decision Report와 동일한 판정 결과"""
    
    print("\n" + "="*100)
    print("TEST 4: LH Integration Accuracy")
    print("="*100)
    
    # Given
    (appraisal_ctx, land_diagnosis, lh_result, ch3_scores, 
     ch4_scores, risk_matrix, financial_analysis) = create_complete_mock_data()
    
    # Generate standalone LH Decision Report
    from app.services.report_composers.lh_decision_report_composer import LHDecisionReportComposer
    
    lh_composer = LHDecisionReportComposer(
        appraisal_ctx=appraisal_ctx,
        lh_result=lh_result,
        ch3_scores=ch3_scores,
        ch4_scores=ch4_scores
    )
    lh_standalone = lh_composer.generate()
    
    # Generate Comprehensive Report
    comprehensive_composer = ComprehensiveReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result,
        ch3_scores=ch3_scores,
        ch4_scores=ch4_scores
    )
    comprehensive_report = comprehensive_composer.compose()
    
    # Then - Compare predictions
    standalone_prediction = lh_standalone['part_3_pass_fail']['prediction']
    integrated_prediction = comprehensive_report['section_3_lh_analysis']['part_1_pass_fail_prediction']['prediction']
    
    assert standalone_prediction == integrated_prediction, \
        f"Prediction mismatch: standalone={standalone_prediction}, integrated={integrated_prediction}"
    
    print(f"   ✅ Prediction match: {standalone_prediction}")
    
    # Compare recommended types
    standalone_type = lh_standalone['part_1_supply_type']['recommended_type']
    integrated_type = comprehensive_report['section_3_lh_analysis']['part_2_supply_type_analysis']['recommended_type']
    
    assert standalone_type == integrated_type, \
        f"Recommended type mismatch: standalone={standalone_type}, integrated={integrated_type}"
    
    print(f"   ✅ Recommended type match: {standalone_type}")
    
    # Compare adequacy
    standalone_adequacy = lh_standalone['part_2_purchase_price']['adequacy']
    integrated_adequacy = comprehensive_report['section_3_lh_analysis']['part_3_purchase_price_adequacy']['adequacy']
    
    assert standalone_adequacy == integrated_adequacy, \
        f"Adequacy mismatch: standalone={standalone_adequacy}, integrated={integrated_adequacy}"
    
    print(f"   ✅ Adequacy match: {standalone_adequacy}")
    
    print("\n✅ TEST 4 PASSED - LH integration accuracy verified")
    return True


def test_page_count():
    """Test: 15-20장 범위 내"""
    
    print("\n" + "="*100)
    print("TEST 5: Page Count (15-20 pages)")
    print("="*100)
    
    # Given
    (appraisal_ctx, land_diagnosis, lh_result, ch3_scores, 
     ch4_scores, risk_matrix, financial_analysis) = create_complete_mock_data()
    
    composer = ComprehensiveReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result,
        ch3_scores=ch3_scores,
        ch4_scores=ch4_scores
    )
    
    # When
    report = composer.compose()
    
    # Then
    page_count = report.get('actual_pages', 0)
    
    assert 15 <= page_count <= 20, f"Page count {page_count} out of range (15-20)"
    
    print(f"   ✅ Page count: {page_count} (within 15-20 range)")
    print(f"   Estimated pages: {report.get('estimated_pages', 'N/A')}")
    
    print("\n✅ TEST 5 PASSED - Page count within acceptable range")
    return page_count


def test_appraisal_immutability():
    """Test: Appraisal Context 불변성 확인"""
    
    print("\n" + "="*100)
    print("TEST 6: Appraisal Context Immutability")
    print("="*100)
    
    # Given
    (appraisal_ctx, land_diagnosis, lh_result, ch3_scores, 
     ch4_scores, risk_matrix, financial_analysis) = create_complete_mock_data()
    
    # Record original hash
    original_hash = appraisal_ctx.get_hash_signature()
    original_value = appraisal_ctx.get('calculation.final_appraised_total')
    
    print(f"   Original Hash: {original_hash[:16]}...")
    print(f"   Original Value: {original_value:,}원")
    
    # When - Generate report
    composer = ComprehensiveReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result
    )
    report = composer.compose()
    
    # Then - Verify hash unchanged
    final_hash = appraisal_ctx.get_hash_signature()
    final_value = appraisal_ctx.get('calculation.final_appraised_total')
    
    assert original_hash == final_hash, "Hash changed! Appraisal context modified!"
    assert original_value == final_value, "Value changed! Appraisal context modified!"
    assert appraisal_ctx.verify_hash(), "Hash verification failed!"
    
    print(f"   Final Hash: {final_hash[:16]}...")
    print(f"   Final Value: {final_value:,}원")
    print(f"   ✅ Hash verified: UNCHANGED")
    print(f"   ✅ Value verified: UNCHANGED")
    
    print("\n✅ TEST 6 PASSED - Appraisal context remains immutable")
    return True


def run_all_tests():
    """Run all comprehensive report tests"""
    
    print("\n" + "="*100)
    print("🚀 ZeroSite v3.3 - COMPREHENSIVE REPORT COMPOSER TESTS")
    print("="*100)
    
    try:
        # Test 1: All sections generated
        report1 = test_all_sections_generated()
        
        # Test 2: Landowner emphasis
        report2 = test_landowner_emphasis()
        
        # Test 3: Investor emphasis
        report3 = test_investor_emphasis()
        
        # Test 4: LH integration accuracy
        test_lh_integration_accuracy()
        
        # Test 5: Page count
        page_count = test_page_count()
        
        # Test 6: Appraisal immutability
        test_appraisal_immutability()
        
        # Summary
        print("\n" + "="*100)
        print("📊 TEST SUMMARY")
        print("="*100)
        print(f"   ✅ TEST 1: All sections generated")
        print(f"   ✅ TEST 2: Landowner emphasis verified")
        print(f"   ✅ TEST 3: Investor emphasis verified")
        print(f"   ✅ TEST 4: LH integration accuracy verified")
        print(f"   ✅ TEST 5: Page count ({page_count} pages) verified")
        print(f"   ✅ TEST 6: Appraisal immutability verified")
        print("\n" + "="*100)
        print("✅ ALL TESTS PASSED - Comprehensive Report Composer v3.3 Working Correctly")
        print("="*100)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
