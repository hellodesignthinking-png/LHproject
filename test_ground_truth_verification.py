"""
ZeroSite v23 - Ground Truth Verification
=========================================

이 스크립트는 "강남 역삼동 825 프로젝트"의 실제 계산값을 검증합니다.

테스트 케이스 입력값:
- 주소: 서울특별시 강남구 역삼동 825
- 토지 면적: 1,100㎡
- 연면적: 2,200㎡
- CAPEX: 300억원
- 시장 토지가: 242억원 (예상)
- 감정평가율: 92%
- LH 표준건축비: 350만원/㎡

목표:
1. Financial Engine 실제 계산 결과 확보
2. 민감도 분석 9개 시나리오 검증
3. Dynamic CAPEX 계산 검증
4. 문서 vs 코드 불일치 발견
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

logger = logging.getLogger(__name__)

# Test case parameters (from v23_implementation_summary.md)
TEST_CASE = {
    'name': '강남 역삼동 825 프로젝트',
    'address': '서울특별시 강남구 역삼동 825',
    'land_area_sqm': 1100,
    'gross_floor_area': 2200,
    'base_capex_won': 30000000000,  # 300억원
    'base_capex_eok': 300,
    'market_land_value_won': 24200000000,  # 242억원
    'market_land_value_eok': 242,
    'base_appraisal_rate': 0.92,  # 92%
    'lh_standard_cost_per_sqm': 3500000,  # 350만원/㎡
    'lh_approved_limit_per_sqm': 4200000,  # 420만원/㎡ (표준 +20%)
}


def test_sensitivity_analysis():
    """
    Task 1 & 2: 민감도 분석 Ground Truth 계산
    """
    logger.info("="*80)
    logger.info("TEST 1: 민감도 분석 Ground Truth 검증")
    logger.info("="*80)
    
    try:
        from app.services_v13.sensitivity_analysis import (
            SensitivityAnalyzer,
            format_sensitivity_report
        )
        
        analyzer = SensitivityAnalyzer()
        
        # Run sensitivity analysis
        result = analyzer.analyze_comprehensive(
            base_capex=TEST_CASE['base_capex_won'],
            base_appraisal_rate=TEST_CASE['base_appraisal_rate'],
            market_land_value=TEST_CASE['market_land_value_won'],
            gross_floor_area=TEST_CASE['gross_floor_area'],
            lh_standard_cost_per_sqm=TEST_CASE['lh_standard_cost_per_sqm']
        )
        
        # Print detailed results
        logger.info(f"\n{'='*80}")
        logger.info("민감도 분석 실제 계산 결과 (Ground Truth)")
        logger.info(f"{'='*80}\n")
        
        # Print all 9 scenarios in table format
        logger.info("┌─────────────────────────────┬────────┬────────┬────────┬────────┬────────────────┐")
        logger.info("│         시나리오             │ CAPEX  │ 평가율 │ 수익   │  ROI   │   의사결정     │")
        logger.info("│                             │ (억원) │  (%)   │ (억원) │  (%)   │                │")
        logger.info("├─────────────────────────────┼────────┼────────┼────────┼────────┼────────────────┤")
        
        for scenario in result['scenarios']:
            logger.info(
                f"│ {scenario['scenario_name']:<27} │ {scenario['adjusted_capex_eok']:>6.0f} │ "
                f"{scenario['adjusted_appraisal_rate_pct']:>6.2f} │ {scenario['profit_eok']:>6.2f} │ "
                f"{scenario['roi_pct']:>6.2f} │ {scenario['decision']:<14} │"
            )
        
        logger.info("└─────────────────────────────┴────────┴────────┴────────┴────────┴────────────────┘")
        
        # Print summary
        summary = result['summary']
        logger.info(f"\n{'='*80}")
        logger.info("요약 통계")
        logger.info(f"{'='*80}")
        logger.info(f"수익 범위: {summary['profit_min_eok']:.2f}억 ~ {summary['profit_max_eok']:.2f}억")
        logger.info(f"수익 변동폭: {summary['profit_range_eok']:.2f}억")
        logger.info(f"ROI 범위: {summary['roi_min_pct']:.2f}% ~ {summary['roi_max_pct']:.2f}%")
        logger.info(f"ROI 변동폭: {summary['roi_range_pct']:.2f}%p")
        logger.info(f"GO 시나리오: {summary['go_count']}개 ({summary['go_probability_pct']:.1f}%)")
        logger.info(f"NO-GO 시나리오: {summary['no_go_count']}개")
        
        # Print tornado data
        tornado = result['tornado_data']
        logger.info(f"\n{'='*80}")
        logger.info("Tornado 다이어그램 (민감도 순위)")
        logger.info(f"{'='*80}")
        
        for i, factor in enumerate(tornado['factors'], 1):
            logger.info(f"\n{i}위. {factor['factor']} ({factor['variation']})")
            logger.info(f"  • 변동폭: {factor['total_range']:.2f}억원")
            logger.info(f"  • 음의 영향: {factor['impact_negative']:.2f}억원")
            logger.info(f"  • 양의 영향: {factor['impact_positive']:.2f}억원")
        
        logger.info(f"\n가장 민감한 요인: {tornado['most_sensitive']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ 민감도 분석 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_dynamic_capex():
    """
    Task 3: Dynamic CAPEX 계산 Ground Truth 검증
    """
    logger.info(f"\n{'='*80}")
    logger.info("TEST 2: Dynamic CAPEX 계산 Ground Truth 검증")
    logger.info(f"{'='*80}\n")
    
    try:
        from app.services_v13.dynamic_capex_calculator import (
            DynamicCapexCalculator,
            format_dynamic_capex_report
        )
        
        calculator = DynamicCapexCalculator()
        
        # Test 1: Dynamic land cost calculation
        logger.info("▶ Test 2-1: 시장가 기반 동적 토지비 계산")
        logger.info("-" * 80)
        
        land_result = calculator.calculate_dynamic_land_cost(
            market_land_value=TEST_CASE['market_land_value_won'],
            capex_total=TEST_CASE['base_capex_won'],
            use_dynamic=True
        )
        
        logger.info(f"입력:")
        logger.info(f"  • 시장 토지가: {TEST_CASE['market_land_value_eok']:.2f}억원")
        logger.info(f"  • 총 CAPEX: {TEST_CASE['base_capex_eok']:.0f}억원")
        logger.info(f"\n계산 결과:")
        logger.info(f"  • 예상 토지비 (협상 후): {land_result['estimated_land_cost_eok']:.2f}억원")
        logger.info(f"  • CAPEX 토지비: {land_result['land_cost_eok']:.2f}억원")
        logger.info(f"  • 토지비 비율: {land_result['land_cost_ratio_pct']:.1f}%")
        logger.info(f"  • 계산 방법: {land_result['method']}")
        logger.info(f"  • 조정 필요: {land_result['adjustment_needed']}")
        
        if land_result['adjustment_needed']:
            logger.info(f"  • 권장 CAPEX: {land_result['recommended_capex_eok']:.0f}억원")
        
        # Test 2: Construction cost validation
        logger.info(f"\n▶ Test 2-2: LH 인정 건축비 검증")
        logger.info("-" * 80)
        
        # Current CAPEX building cost (55% of 300억 = 165억)
        current_building_cost = TEST_CASE['base_capex_won'] * 0.55
        
        validation = calculator.validate_construction_cost(
            capex_building_cost=current_building_cost,
            gross_floor_area=TEST_CASE['gross_floor_area']
        )
        
        logger.info(f"입력:")
        logger.info(f"  • CAPEX 건축비: {current_building_cost/1e8:.2f}억원 (CAPEX의 55%)")
        logger.info(f"  • 연면적: {TEST_CASE['gross_floor_area']:.0f}㎡")
        logger.info(f"\n검증 결과:")
        logger.info(f"  • CAPEX 건축비 단가: {validation['capex_cost_per_sqm_man']:.1f}만원/㎡")
        logger.info(f"  • LH 표준건축비: {validation['lh_standard_man']:.1f}만원/㎡")
        logger.info(f"  • LH 인정 한도: {validation['lh_approved_limit_man']:.1f}만원/㎡ (표준 +20%)")
        logger.info(f"  • 초과액: {validation['excess_man']:.1f}만원/㎡ ({validation['excess_pct']:.1f}%)")
        logger.info(f"  • 상태: {validation['status']}")
        
        if validation['status'] == 'ERROR':
            logger.warning(f"  ⚠️ 경고: {validation['message']}")
        
        # Test 3: CAPEX breakdown adjustment
        logger.info(f"\n▶ Test 2-3: CAPEX 세부 항목 조정")
        logger.info("-" * 80)
        
        breakdown = calculator.adjust_capex_breakdown(
            capex_total=TEST_CASE['base_capex_won'],
            land_cost=land_result['land_cost_won'],
            gross_floor_area=TEST_CASE['gross_floor_area']
        )
        
        logger.info(f"조정 후 CAPEX 구조:")
        logger.info(f"\n┌──────────────┬────────┬───────────┬──────────────┐")
        logger.info(f"│   항목       │  비율  │   금액    │     상태     │")
        logger.info(f"├──────────────┼────────┼───────────┼──────────────┤")
        
        items = [
            ('토지비', breakdown['land_cost_eok'], breakdown['land_cost_ratio_pct'], '✅ 시장가 기반'),
            ('직접 건축비', breakdown['direct_cost_eok'], breakdown['direct_cost_ratio_pct'], 
             '✅ OK' if breakdown['validation']['status'] == 'OK' else '❌ ERROR'),
            ('간접비', breakdown['indirect_cost_eok'], breakdown['indirect_cost_ratio_pct'], ''),
            ('설계비', breakdown['design_cost_eok'], breakdown['design_cost_ratio_pct'], ''),
            ('기타비용', breakdown['other_cost_eok'], breakdown['other_cost_ratio_pct'], ''),
        ]
        
        for item_name, amount, ratio, status in items:
            logger.info(f"│ {item_name:<12} │ {ratio:>5.1f}% │ {amount:>9.2f}억│ {status:<12} │")
        
        logger.info(f"└──────────────┴────────┴───────────┴──────────────┘")
        
        logger.info(f"\n조정 후 건축비 검증:")
        logger.info(f"  • 건축비 단가: {breakdown['validation']['capex_cost_per_sqm_man']:.1f}만원/㎡")
        logger.info(f"  • 상태: {breakdown['validation']['status']}")
        
        return {
            'land_result': land_result,
            'validation': validation,
            'breakdown': breakdown
        }
        
    except Exception as e:
        logger.error(f"❌ Dynamic CAPEX 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_land_value_3layer():
    """
    Task 4: Land Value 3-Layer 검증
    """
    logger.info(f"\n{'='*80}")
    logger.info("TEST 3: Land Value 3-Layer 구조 검증")
    logger.info(f"{'='*80}\n")
    
    try:
        from app.services_v13.land_trade_api import LandValueCalculator
        
        # Note: This would require actual API integration
        # For now, we'll use test values
        
        logger.info("Layer 1: Market Land Value (국토부 실거래가 기반)")
        logger.info(f"  • 시장 토지가: {TEST_CASE['market_land_value_eok']:.2f}억원")
        logger.info(f"  • 평균 단가: {TEST_CASE['market_land_value_won']/TEST_CASE['land_area_sqm']/10000:.2f}만원/㎡")
        
        logger.info(f"\nLayer 2: LH Appraisal Value (감정평가)")
        lh_land_appraisal = TEST_CASE['market_land_value_won'] * TEST_CASE['base_appraisal_rate']
        lh_building_appraisal = TEST_CASE['lh_standard_cost_per_sqm'] * TEST_CASE['gross_floor_area']
        lh_total = lh_land_appraisal + lh_building_appraisal
        
        logger.info(f"  • 토지 감정가: {lh_land_appraisal/1e8:.2f}억원 (시장가 × {TEST_CASE['base_appraisal_rate']*100:.0f}%)")
        logger.info(f"  • 건물 감정가: {lh_building_appraisal/1e8:.2f}억원 (표준단가 × 연면적)")
        logger.info(f"  • 총 LH 매입가: {lh_total/1e8:.2f}억원")
        
        logger.info(f"\nLayer 3: CAPEX Land Cost (동적 계산)")
        # This would come from dynamic calculator
        logger.info(f"  • 기존 고정 토지비: {TEST_CASE['base_capex_eok']*0.25:.2f}억원 (CAPEX의 25%)")
        logger.info(f"  • 개선 후 동적 토지비: (상기 Test 2 결과 참조)")
        
        return {
            'market_land_value_eok': TEST_CASE['market_land_value_eok'],
            'lh_land_appraisal_eok': round(lh_land_appraisal/1e8, 2),
            'lh_building_appraisal_eok': round(lh_building_appraisal/1e8, 2),
            'lh_total_appraisal_eok': round(lh_total/1e8, 2),
        }
        
    except Exception as e:
        logger.error(f"❌ 3-Layer 검증 실패: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def compare_with_documentation():
    """
    Task 6: 문서와 코드 간 차이 발견
    """
    logger.info(f"\n{'='*80}")
    logger.info("TEST 4: 문서 vs 코드 불일치 검증")
    logger.info(f"{'='*80}\n")
    
    # Values from v23_implementation_summary.md
    documented_values = {
        'best_profit_eok': 40.77,
        'base_profit_eok': -0.36,
        'worst_profit_eok': -41.49,
        'best_roi_pct': 15.10,
        'base_roi_pct': -0.12,
        'worst_roi_pct': -12.57,
        'capex_sensitivity_eok': 60.00,
        'appraisal_sensitivity_eok': 22.26,
    }
    
    logger.info("문서에 기록된 값 (v23_implementation_summary.md):")
    logger.info(f"  • 최적 시나리오 수익: {documented_values['best_profit_eok']:.2f}억원")
    logger.info(f"  • 기준 시나리오 수익: {documented_values['base_profit_eok']:.2f}억원")
    logger.info(f"  • 최악 시나리오 수익: {documented_values['worst_profit_eok']:.2f}억원")
    logger.info(f"  • CAPEX 민감도: {documented_values['capex_sensitivity_eok']:.2f}억원")
    logger.info(f"  • 감정평가율 민감도: {documented_values['appraisal_sensitivity_eok']:.2f}억원")
    
    logger.info(f"\n코드 계산 결과와 비교를 위해 상기 TEST 1 결과를 참조하세요.")
    
    return documented_values


def main():
    """Run all ground truth verification tests"""
    logger.info("━"*80)
    logger.info("ZeroSite v23 - Ground Truth Verification Suite")
    logger.info(f"테스트 케이스: {TEST_CASE['name']}")
    logger.info("━"*80)
    
    results = {}
    
    # Test 1 & 2: Sensitivity Analysis
    sensitivity_result = test_sensitivity_analysis()
    if sensitivity_result:
        results['sensitivity'] = sensitivity_result
    
    # Test 3: Dynamic CAPEX
    capex_result = test_dynamic_capex()
    if capex_result:
        results['capex'] = capex_result
    
    # Test 4: 3-Layer validation
    layer_result = test_land_value_3layer()
    if layer_result:
        results['layers'] = layer_result
    
    # Test 5: Documentation comparison
    doc_values = compare_with_documentation()
    if doc_values:
        results['documentation'] = doc_values
    
    # Final summary
    logger.info(f"\n{'='*80}")
    logger.info("Ground Truth 검증 완료")
    logger.info(f"{'='*80}")
    
    if results.get('sensitivity'):
        base_scenario = next(
            s for s in results['sensitivity']['scenarios'] 
            if s['scenario_name'] == "Base (기준)"
        )
        logger.info(f"\n✅ 기준 시나리오 (CAPEX 300억, 평가율 92%):")
        logger.info(f"   수익: {base_scenario['profit_eok']:.2f}억원")
        logger.info(f"   ROI: {base_scenario['roi_pct']:.2f}%")
        logger.info(f"   IRR: {base_scenario['irr_pct']:.2f}%")
        logger.info(f"   의사결정: {base_scenario['decision']}")
    
    if results.get('layers'):
        logger.info(f"\n✅ 3-Layer Land Valuation:")
        logger.info(f"   Market: {results['layers']['market_land_value_eok']:.2f}억원")
        logger.info(f"   LH Land: {results['layers']['lh_land_appraisal_eok']:.2f}억원")
        logger.info(f"   LH Total: {results['layers']['lh_total_appraisal_eok']:.2f}억원")
    
    logger.info(f"\n이제 이 Ground Truth 값을 기준으로 문서와 비교하여 불일치를 수정합니다.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
