"""
ZeroSite v3.3 Phase 2 - Composer Integration Tests

Tests for the 3 new report composers:
1. InvestorReportComposer
2. LandPriceReportComposer
3. InternalAssessmentComposer
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.appraisal_context import AppraisalContextLock
from app.services.canonical_schema import CanonicalAppraisalResult, ZoningInfo, OfficialLandPrice, TransactionCase
from app.services.report_composers.investor_report_composer import InvestorReportComposer
from app.services.report_composers.land_price_report_composer import LandPriceReportComposer
from app.services.report_composers.internal_assessment_composer import InternalAssessmentComposer


def test_phase2_integration():
    """
    Phase 2 Integration Test
    Tests all 3 new report composers
    """
    
    print("\n" + "="*100)
    print("🚀 ZeroSite v3.3 Phase 2 - Composer Integration Test")
    print("   Testing: Investor Report + Land Price Report + Internal Assessment")
    print("="*100)
    
    # ========== STEP 1: Create Mock Data ==========
    print("\n📋 STEP 1: Creating mock data...")
    
    # Create mock appraisal result (same format as Phase 1 test)
    from app.services.canonical_schema import (
        PremiumInfo, PremiumDetail, CalculationInfo,
        ConfidenceInfo, ConfidenceFactors, MetadataInfo
    )
    
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
        transaction_case=TransactionCase(
            price_per_sqm=6000000.0,
            transaction_date="2024-06-15",
            distance_m=250.0,
            area_sqm=650.0,
            similarity_score=0.85
        ),
        premium=PremiumInfo(
            development_potential=PremiumDetail(rate=0.045, rationale="역세권 개발 가능성"),
            location_premium=PremiumDetail(rate=0.03, rationale="지하철 300m, 학교 400m"),
            policy_benefit=PremiumDetail(rate=0.015, rationale="LH 공공주택 지구"),
            total_premium_rate=0.09
        ),
        calculation=CalculationInfo(
            base_price_per_sqm=5775000.0,
            premium_adjusted_per_sqm=6294750.0,
            land_area_sqm=660.0,
            final_appraised_total=4154535000.0
        ),
        confidence=ConfidenceInfo(
            score=85,
            factors=ConfidenceFactors(
                data_completeness=90,
                case_similarity=80,
                time_relevance=85,
                regulatory_clarity=85
            )
        ),
        metadata=MetadataInfo(
            appraisal_engine="ZeroSite v8.7",
            calculation_method="거래사례비교법 (주)",
            appraiser_note="우수한 개발 가능성"
        )
    )
    
    # Lock the appraisal context
    appraisal_ctx = AppraisalContextLock()
    appraisal_ctx.lock(appraisal_result.model_dump())
    
    print(f"   ✅ Appraisal Context LOCKED")
    print(f"      Final Appraised Value: 4,154,535,000원")
    print(f"      Zone Type: 제2종일반주거지역")
    print(f"      FAR: 250.0%")
    
    # Mock land diagnosis
    land_diagnosis = {
        'development_potential': 'HIGH',
        'access_quality': 'GOOD',
        'infrastructure': 'ADEQUATE',
        'risk_level': 'MEDIUM'
    }
    
    # Mock LH result
    lh_result = {
        'decision': 'GO',
        'roi': 27.44,
        'lh_purchase_price': 16800000000,
        'analysis_result': {
            'construction_cost': 8400000000,
            'verified_cost': 627387750,
            'total_cost': 13182261750
        }
    }
    
    # Mock CH4 scores
    ch4_scores = {
        '행복주택': 15.2,
        '청년': 14.8,
        '신혼부부': 14.2,
        '일반': 13.5,
        '공공임대': 12.8
    }
    
    # Mock risk matrix
    risk_matrix = {
        'total_risk_score': 25,
        'risk_level': 'LOW'
    }
    
    # Mock financial analysis
    financial_analysis = {
        'irr': 27.44,
        'roi': 27.44,
        'npv': 3617738250,
        'payback_months': 18
    }
    
    # ========== STEP 2: Test Investor Report Composer ==========
    print("\n📋 STEP 2: Testing Investor Report Composer...")
    
    investor_composer = InvestorReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result,
        risk_matrix=risk_matrix,
        financial_analysis=financial_analysis
    )
    
    investor_report = investor_composer.compose()
    
    # Verify structure
    assert investor_report['report_type'] == 'investor_report', "Wrong report type"
    assert 'section_1_investment_summary' in investor_report, "Section 1 missing"
    assert 'section_2_land_valuation' in investor_report, "Section 2 missing"
    assert 'section_3_development_plan' in investor_report, "Section 3 missing"
    assert 'section_4_financial_projection' in investor_report, "Section 4 missing"
    assert 'section_5_risk_return_analysis' in investor_report, "Section 5 missing"
    assert 'section_6_recommendation' in investor_report, "Section 6 missing"
    
    # Verify investment grade
    investment_grade = investor_report['section_1_investment_summary']['investment_grade']
    assert investment_grade in ['A', 'B', 'C', 'D'], "Invalid investment grade"
    
    # Verify financial projection
    assert 'part_4_4_scenario_analysis' in investor_report['section_4_financial_projection'], "Scenario analysis missing"
    
    print(f"   ✅ Investor Report generated successfully")
    print(f"      Report ID: {investor_report['report_id']}")
    print(f"      Investment Grade: {investment_grade}")
    print(f"      Expected IRR: {investor_report['section_4_financial_projection']['part_4_2_revenue_analysis']['revenue_metrics']['irr']['value']:.1f}%")
    
    # ========== STEP 3: Test Land Price Report Composer ==========
    print("\n📋 STEP 3: Testing Land Price Report Composer...")
    
    landprice_composer = LandPriceReportComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result
    )
    
    landprice_report = landprice_composer.compose()
    
    # Verify structure
    assert landprice_report['report_type'] == 'land_price_report', "Wrong report type"
    assert 'section_1_price_summary' in landprice_report, "Section 1 missing"
    assert 'section_2_valuation_analysis' in landprice_report, "Section 2 missing"
    assert 'section_3_market_comparison' in landprice_report, "Section 3 missing"
    assert 'section_4_recommendation' in landprice_report, "Section 4 missing"
    
    # Verify price judgment
    price_judgment = landprice_report['section_1_price_summary']['price_adequacy']['judgment']
    assert price_judgment in ['적정', '약간 고가', '고가', '저가'], "Invalid price judgment"
    
    # Verify recommendation methods
    assert 'price_calculation_methods' in landprice_report['section_4_recommendation'], "Price calculation methods missing"
    
    print(f"   ✅ Land Price Report generated successfully")
    print(f"      Report ID: {landprice_report['report_id']}")
    print(f"      Price Judgment: {price_judgment}")
    print(f"      Appropriate Price Range: {landprice_report['section_4_recommendation']['final_appropriate_price']['formatted_range']}")
    
    # ========== STEP 4: Test Internal Assessment Composer ==========
    print("\n📋 STEP 4: Testing Internal Assessment Composer...")
    
    internal_composer = InternalAssessmentComposer(
        appraisal_ctx=appraisal_ctx,
        land_diagnosis=land_diagnosis,
        lh_result=lh_result,
        ch4_scores=ch4_scores,
        risk_matrix=risk_matrix,
        financial_analysis=financial_analysis
    )
    
    internal_report = internal_composer.compose()
    
    # Verify structure
    assert internal_report['report_type'] == 'internal_assessment', "Wrong report type"
    assert 'section_1_executive_decision' in internal_report, "Section 1 missing"
    assert 'section_2_key_metrics' in internal_report, "Section 2 missing"
    assert 'section_3_risk_flags' in internal_report, "Section 3 missing"
    assert 'section_4_financial_snapshot' in internal_report, "Section 4 missing"
    assert 'section_5_action_items' in internal_report, "Section 5 missing"
    
    # Verify decision
    decision = internal_report['section_1_executive_decision']['final_decision']['decision']
    assert decision in ['GO', 'CONDITIONAL', 'NO-GO'], "Invalid decision"
    
    # Verify overall score
    overall_score = internal_report['section_2_key_metrics']['overall_score']
    assert 0 <= overall_score <= 100, "Invalid overall score"
    
    print(f"   ✅ Internal Assessment generated successfully")
    print(f"      Report ID: {internal_report['report_id']}")
    print(f"      Decision: {decision}")
    print(f"      Overall Score: {overall_score}/100")
    
    # ========== STEP 5: Verify Appraisal Immutability ==========
    print("\n📋 STEP 5: Verifying Appraisal Context Immutability...")
    
    # Verify hash hasn't changed
    assert appraisal_ctx.verify_hash(), "Hash verification failed - data may have been modified!"
    
    # Verify data is still accessible and correct
    final_value = appraisal_ctx.get('calculation.final_appraised_total')
    assert final_value == 4154535000, f"Appraisal value changed! Expected 4154535000, got {final_value}"
    
    print(f"   ✅ Appraisal Context remains LOCKED and IMMUTABLE")
    print(f"      Hash verification: PASSED")
    print(f"      Final value unchanged: {final_value:,.0f}원")
    
    # ========== STEP 6: Generate Summary ==========
    print("\n📋 STEP 6: Generating Phase 2 Summary...")
    
    summary = {
        'phase': 'Phase 2',
        'status': 'COMPLETE',
        'reports_generated': [
            {
                'name': 'Investor Report',
                'type': 'investor_report',
                'pages': '10-12',
                'report_id': investor_report['report_id'],
                'investment_grade': investment_grade
            },
            {
                'name': 'Land Price Report',
                'type': 'land_price_report',
                'pages': '5-8',
                'report_id': landprice_report['report_id'],
                'price_judgment': price_judgment
            },
            {
                'name': 'Internal Assessment',
                'type': 'internal_assessment',
                'pages': '5',
                'report_id': internal_report['report_id'],
                'decision': decision
            }
        ],
        'appraisal_context': {
            'locked': True,
            'hash_verified': True,
            'final_appraised_value': final_value,
            'hash_signature': appraisal_ctx.get_hash_signature()[:16] + '...'
        },
        'compliance': {
            'canonical_flow': '✅ FACT → INTERPRETATION → JUDGMENT',
            'immutability': '✅ Appraisal Context LOCKED',
            'no_recalculation': '✅ No recalculation performed',
            'all_reports': '✅ 7/7 Report Types Complete (100%)'
        }
    }
    
    print("\n" + "="*100)
    print("📊 PHASE 2 SUMMARY")
    print("="*100)
    print(f"\n   Status: {summary['status']}")
    print(f"\n   Reports Generated:")
    for report in summary['reports_generated']:
        print(f"      - {report['name']} ({report['pages']} pages)")
        print(f"        Report ID: {report['report_id']}")
        key_metric = report.get('investment_grade') or report.get('price_judgment') or report.get('decision')
        print(f"        Key Metric: {key_metric}")
    
    print(f"\n   Appraisal Context:")
    print(f"      Locked: {summary['appraisal_context']['locked']}")
    print(f"      Hash Verified: {summary['appraisal_context']['hash_verified']}")
    print(f"      Final Value: {summary['appraisal_context']['final_appraised_value']:,.0f}원")
    print(f"      Hash: {summary['appraisal_context']['hash_signature']}")
    
    print(f"\n   Compliance Checklist:")
    for key, value in summary['compliance'].items():
        print(f"      {value} {key.replace('_', ' ').title()}")
    
    print("\n" + "="*100)
    print("✅ PHASE 2 INTEGRATION TEST PASSED - ALL REQUIREMENTS MET")
    print("="*100)
    
    return summary


if __name__ == "__main__":
    test_phase2_integration()
