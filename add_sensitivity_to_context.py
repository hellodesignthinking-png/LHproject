"""
Add Sensitivity Analysis to Report Context
===========================================

이 스크립트는 report context에 민감도 분석 결과를 추가합니다.
"""

def add_sensitivity_analysis_to_context(context):
    """
    Context에 민감도 분석 결과 추가
    
    Args:
        context: 기존 report context dict
    
    Returns:
        Updated context with sensitivity analysis
    """
    from app.services_v13.sensitivity_analysis import SensitivityAnalyzer
    
    # Extract required parameters
    capex_won = context.get('capex_won', context.get('capex_krw', 30000000000))
    market_land_value_won = context.get('market_land_value_won', 24200000000)
    gross_floor_area = context.get('gross_floor_area', 2200)
    appraisal_rate = context.get('land_appraisal_rate', 0.92)
    lh_standard_cost = context.get('lh_standard_cost_per_sqm', 3500000)
    
    # Run sensitivity analysis
    try:
        analyzer = SensitivityAnalyzer()
        result = analyzer.analyze_comprehensive(
            base_capex=capex_won,
            base_appraisal_rate=appraisal_rate,
            market_land_value=market_land_value_won,
            gross_floor_area=gross_floor_area,
            lh_standard_cost_per_sqm=lh_standard_cost
        )
        
        context['sensitivity_analysis_v23'] = result
        context['has_sensitivity_analysis'] = True
        
        print(f"✅ Sensitivity analysis added to context:")
        print(f"   - Scenarios: {len(result['scenarios'])}")
        print(f"   - GO scenarios: {result['summary']['go_count']}")
        print(f"   - Most sensitive factor: {result['tornado_data']['most_sensitive']}")
        
    except Exception as e:
        print(f"❌ Failed to add sensitivity analysis: {str(e)}")
        context['sensitivity_analysis_v23'] = None
        context['has_sensitivity_analysis'] = False
    
    return context


if __name__ == '__main__':
    # Test with sample context
    test_context = {
        'capex_won': 30000000000,
        'market_land_value_won': 24200000000,
        'gross_floor_area': 2200,
        'land_appraisal_rate': 0.92
    }
    
    result_context = add_sensitivity_analysis_to_context(test_context)
    
    if result_context.get('has_sensitivity_analysis'):
        print("\n" + "="*80)
        print("민감도 분석 결과:")
        print("="*80)
        
        summary = result_context['sensitivity_analysis_v23']['summary']
        print(f"수익 범위: {summary['profit_min_eok']:.2f}억 ~ {summary['profit_max_eok']:.2f}억")
        print(f"GO 시나리오: {summary['go_count']}개 ({summary['go_probability_pct']:.1f}%)")
        print(f"가장 민감한 요인: {result_context['sensitivity_analysis_v23']['tornado_data']['most_sensitive']}")
    else:
        print("\n❌ 민감도 분석 실패")
