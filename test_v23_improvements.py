"""
ZeroSite v23 - Improvements Test Script
========================================

테스트 항목:
1. 민감도 분석 (CAPEX ±10%, 감정평가율 ±5%)
2. Dynamic CAPEX 토지비 계산
3. LH 인정 건축비 검증

Author: ZeroSite AI Analysis System
Date: 2025-12-10
"""

import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

logger = logging.getLogger(__name__)

def test_sensitivity_analysis():
    """Test Sensitivity Analysis Module"""
    logger.info("="*80)
    logger.info("TEST 1: 민감도 분석 (CAPEX ±10%, 감정평가율 ±5%)")
    logger.info("="*80)
    
    try:
        from app.services_v13.sensitivity_analysis import (
            SensitivityAnalyzer,
            format_sensitivity_report
        )
        
        analyzer = SensitivityAnalyzer()
        
        # Test case: 강남 역삼동 825
        result = analyzer.analyze_comprehensive(
            base_capex=30000000000,  # 300억
            base_appraisal_rate=0.92,
            market_land_value=24200000000,  # 242억
            gross_floor_area=2200
        )
        
        # Print formatted report
        report = format_sensitivity_report(result)
        print(report)
        
        # Summary
        summary = result['summary']
        logger.info(f"✅ 민감도 분석 완료")
        logger.info(f"   수익 범위: {summary['profit_min_eok']:.2f}억 ~ {summary['profit_max_eok']:.2f}억")
        logger.info(f"   GO 확률: {summary['go_probability_pct']:.1f}%")
        logger.info(f"   가장 민감한 요인: {result['tornado_data']['most_sensitive']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 민감도 분석 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_dynamic_capex():
    """Test Dynamic CAPEX Calculator"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Dynamic CAPEX 토지비 계산 + 건축비 검증")
    logger.info("="*80)
    
    try:
        from app.services_v13.dynamic_capex_calculator import (
            DynamicCapexCalculator,
            format_dynamic_capex_report
        )
        
        calculator = DynamicCapexCalculator()
        
        # Test case 1: Dynamic land cost
        logger.info("\n▶ Test 2-1: 시장가 기반 동적 토지비 계산")
        land_result = calculator.calculate_dynamic_land_cost(
            market_land_value=24200000000,  # 242억
            capex_total=30000000000,  # 300억
            use_dynamic=True
        )
        
        logger.info(f"   시장 토지가: 242.00억원")
        logger.info(f"   예상 토지비 (협상 5% 할인): {land_result['estimated_land_cost_eok']:.2f}억원")
        logger.info(f"   CAPEX 토지비: {land_result['land_cost_eok']:.2f}억원 ({land_result['land_cost_ratio_pct']:.1f}%)")
        logger.info(f"   조정 필요: {land_result['adjustment_needed']}")
        
        if land_result['adjustment_needed']:
            logger.info(f"   권장 CAPEX: {land_result['recommended_capex_eok']:.0f}억원")
        
        # Test case 2: Construction cost validation
        logger.info("\n▶ Test 2-2: LH 인정 건축비 검증")
        
        # Scenario A: 현재 CAPEX (750만원/㎡)
        validation_current = calculator.validate_construction_cost(
            capex_building_cost=16500000000,  # 165억 (55%)
            gross_floor_area=2200
        )
        
        logger.info(f"   현재 건축비: {validation_current['capex_cost_per_sqm_man']}만원/㎡")
        logger.info(f"   LH 표준: {validation_current['lh_standard_man']}만원/㎡")
        logger.info(f"   상태: {validation_current['status']}")
        logger.info(f"   초과액: {validation_current['excess_man']}만원/㎡ ({validation_current['excess_pct']:.1f}%)")
        
        # Scenario B: 조정 후 CAPEX (500만원/㎡)
        logger.info("\n▶ Test 2-3: 조정 후 건축비 검증")
        
        breakdown = calculator.adjust_capex_breakdown(
            capex_total=30000000000,
            land_cost=land_result['land_cost_won'],
            gross_floor_area=2200
        )
        
        logger.info(f"   조정 후 건축비: {breakdown['validation']['capex_cost_per_sqm_man']}만원/㎡")
        logger.info(f"   상태: {breakdown['validation']['status']}")
        logger.info(f"   초과액: {breakdown['validation']['excess_man']}만원/㎡ ({breakdown['validation']['excess_pct']:.1f}%)")
        
        # Print full report
        print("\n" + format_dynamic_capex_report(
            land_result,
            validation_current,
            breakdown
        ))
        
        logger.info("✅ Dynamic CAPEX 계산 완료")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dynamic CAPEX 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test Integration with Main Service"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: 메인 서비스 통합 테스트")
    logger.info("="*80)
    
    try:
        # Import main service
        from app_v20_complete_service import add_template_aliases
        
        # Create test context
        test_context = {
            'address': '서울특별시 강남구 역삼동 825',
            'land_area_sqm': 1100,
            'gross_floor_area': 2200,
            'capex_krw': 30000000000,  # 300억
            'appraisal_price': 22000000  # 2,200만원/㎡
        }
        
        logger.info("▶ Test Context:")
        logger.info(f"   주소: {test_context['address']}")
        logger.info(f"   토지 면적: {test_context['land_area_sqm']}㎡")
        logger.info(f"   연면적: {test_context['gross_floor_area']}㎡")
        logger.info(f"   CAPEX: {test_context['capex_krw']/1e8:.0f}억원")
        
        logger.info("\n▶ Running add_template_aliases...")
        
        # Run context builder
        result_context = add_template_aliases(test_context)
        
        # Check v23 improvements
        logger.info("\n▶ v23 Improvements Status:")
        
        # 1. Dynamic Land Cost
        if 'dynamic_land_cost_analysis' in result_context:
            land_analysis = result_context['dynamic_land_cost_analysis']
            logger.info(f"   ✅ Dynamic Land Cost: {land_analysis['land_cost_eok']:.2f}억 ({land_analysis['land_cost_ratio_pct']:.1f}%)")
            logger.info(f"      Method: {land_analysis['method']}")
        else:
            logger.warning("   ⚠️ Dynamic Land Cost: Not found")
        
        # 2. Construction Validation
        if 'construction_validation' in result_context:
            validation = result_context['construction_validation']
            logger.info(f"   ✅ Construction Validation: {validation['status']}")
            logger.info(f"      CAPEX: {validation['capex_cost_per_sqm_man']}만원/㎡")
            logger.info(f"      LH 표준: {validation['lh_standard_man']}만원/㎡")
        else:
            logger.warning("   ⚠️ Construction Validation: Not found")
        
        # 3. Sensitivity Analysis
        if 'sensitivity_analysis_v23' in result_context:
            sensitivity = result_context['sensitivity_analysis_v23']
            if sensitivity:
                summary = sensitivity['summary']
                logger.info(f"   ✅ Sensitivity Analysis: {len(sensitivity['scenarios'])}개 시나리오")
                logger.info(f"      수익 범위: {summary['profit_min_eok']:.2f}억 ~ {summary['profit_max_eok']:.2f}억")
                logger.info(f"      GO 확률: {summary['go_probability_pct']:.1f}%")
            else:
                logger.warning("   ⚠️ Sensitivity Analysis: Failed")
        else:
            logger.warning("   ⚠️ Sensitivity Analysis: Not found")
        
        logger.info("\n✅ 메인 서비스 통합 테스트 완료")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 통합 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("━"*80)
    logger.info("ZeroSite v23 - Improvements Test Suite")
    logger.info("━"*80)
    
    results = {
        'sensitivity_analysis': test_sensitivity_analysis(),
        'dynamic_capex': test_dynamic_capex(),
        'integration': test_integration()
    }
    
    # Summary
    logger.info("\n" + "━"*80)
    logger.info("TEST SUMMARY")
    logger.info("━"*80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"   {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n🎉 모든 테스트 통과!")
        return 0
    else:
        logger.error("\n❌ 일부 테스트 실패")
        return 1


if __name__ == '__main__':
    sys.exit(main())
