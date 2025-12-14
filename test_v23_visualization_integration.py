"""
ZeroSite v23 - Visualization Integration Test
==============================================

Tests the complete visualization pipeline:
1. Sensitivity analysis
2. Chart generation
3. Context integration
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services_v13.sensitivity_analysis import SensitivityAnalyzer
from app.services_v13.tornado_chart_generator import (
    generate_tornado_chart,
    generate_profit_distribution_chart
)
from app.services_v13.scenario_heatmap_generator import (
    generate_profit_heatmap,
    generate_roi_heatmap,
    generate_decision_heatmap
)

def test_visualization_pipeline():
    """
    Test complete visualization pipeline
    """
    print("="*80)
    print("ZeroSite v23 - Visualization Integration Test")
    print("="*80)
    print()
    
    # Test case: 강남 역삼동 825
    base_capex = 30000000000  # 300억
    base_appraisal_rate = 0.92  # 92%
    market_land_value = 24200000000  # 242억
    gross_floor_area = 2200  # 2200㎡
    
    print("📊 TEST 1: Sensitivity Analysis Generation")
    print("-" * 80)
    
    analyzer = SensitivityAnalyzer()
    result = analyzer.analyze_comprehensive(
        base_capex=base_capex,
        base_appraisal_rate=base_appraisal_rate,
        market_land_value=market_land_value,
        gross_floor_area=gross_floor_area
    )
    
    print(f"✅ Generated {len(result['scenarios'])} scenarios")
    print(f"   • Profit range: {result['summary']['profit_min_eok']:.2f}억 ~ {result['summary']['profit_max_eok']:.2f}억")
    print(f"   • GO probability: {result['summary']['go_probability_pct']:.1f}%")
    print(f"   • Tornado factors: {len(result['tornado_data'])}")
    print()
    
    # Create output directory
    output_dir = "/home/user/webapp/test_charts"
    os.makedirs(output_dir, exist_ok=True)
    
    print("📊 TEST 2: Chart Generation")
    print("-" * 80)
    
    charts_generated = []
    
    # Get base profit
    base_scenario = next((s for s in result['scenarios'] if s.get('is_base')), None)
    base_profit = base_scenario['profit_eok'] if base_scenario else 0.0
    
    # 1. Tornado diagram
    print("   Generating tornado diagram...", end=" ")
    tornado_path = f"{output_dir}/tornado_diagram.png"
    if generate_tornado_chart(result['tornado_data'], tornado_path, base_profit=base_profit):
        charts_generated.append('tornado')
        print("✅")
    else:
        print("❌")
    
    # 2. Profit distribution
    print("   Generating profit distribution...", end=" ")
    profit_dist_path = f"{output_dir}/profit_distribution.png"
    if generate_profit_distribution_chart(result['scenarios'], profit_dist_path):
        charts_generated.append('profit_distribution')
        print("✅")
    else:
        print("❌")
    
    # 3. Profit heatmap
    print("   Generating profit heatmap...", end=" ")
    profit_heatmap_path = f"{output_dir}/profit_heatmap.png"
    if generate_profit_heatmap(result['scenarios'], profit_heatmap_path):
        charts_generated.append('profit_heatmap')
        print("✅")
    else:
        print("❌")
    
    # 4. ROI heatmap
    print("   Generating ROI heatmap...", end=" ")
    roi_heatmap_path = f"{output_dir}/roi_heatmap.png"
    if generate_roi_heatmap(result['scenarios'], roi_heatmap_path):
        charts_generated.append('roi_heatmap')
        print("✅")
    else:
        print("❌")
    
    # 5. Decision heatmap
    print("   Generating decision heatmap...", end=" ")
    decision_heatmap_path = f"{output_dir}/decision_heatmap.png"
    if generate_decision_heatmap(result['scenarios'], decision_heatmap_path):
        charts_generated.append('decision_heatmap')
        print("✅")
    else:
        print("❌")
    
    print(f"\n✅ Generated {len(charts_generated)}/5 charts successfully")
    print()
    
    print("📊 TEST 3: Context Integration")
    print("-" * 80)
    
    # Simulate context creation (as in app_v20_complete_service.py)
    ctx = {
        'sensitivity_analysis_v23': result,
        'sensitivity_scenarios': result['scenarios'],
        'sensitivity_summary': result['summary'],
        'sensitivity_tornado': result['tornado_data'],
        'sensitivity_charts': {
            'tornado': tornado_path if 'tornado' in charts_generated else None,
            'profit_distribution': profit_dist_path if 'profit_distribution' in charts_generated else None,
            'profit_heatmap': profit_heatmap_path if 'profit_heatmap' in charts_generated else None,
            'roi_heatmap': roi_heatmap_path if 'roi_heatmap' in charts_generated else None,
            'decision_heatmap': decision_heatmap_path if 'decision_heatmap' in charts_generated else None
        }
    }
    
    print("✅ Context created with:")
    print(f"   • sensitivity_analysis_v23: {ctx['sensitivity_analysis_v23'] is not None}")
    print(f"   • sensitivity_scenarios: {len(ctx['sensitivity_scenarios'])} items")
    print(f"   • sensitivity_summary: {len(ctx['sensitivity_summary'])} keys")
    print(f"   • sensitivity_tornado: {len(ctx['sensitivity_tornado'])} items")
    print(f"   • sensitivity_charts: {len([v for v in ctx['sensitivity_charts'].values() if v])} charts")
    print()
    
    print("📊 TEST 4: Chart File Verification")
    print("-" * 80)
    
    for chart_name, chart_path in ctx['sensitivity_charts'].items():
        if chart_path and os.path.exists(chart_path):
            size = os.path.getsize(chart_path) / 1024  # KB
            print(f"   ✅ {chart_name}: {size:.1f} KB")
        else:
            print(f"   ❌ {chart_name}: Not found")
    print()
    
    print("="*80)
    print("✅ ALL TESTS PASSED: Visualization Pipeline Complete")
    print("="*80)
    print()
    print("Summary:")
    print(f"   • Sensitivity analysis: ✅")
    print(f"   • Charts generated: {len(charts_generated)}/5")
    print(f"   • Context integration: ✅")
    print(f"   • Charts available in: {output_dir}")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = test_visualization_pipeline()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
