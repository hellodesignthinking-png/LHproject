#!/usr/bin/env python3
"""
Phase 2 Implementation Test Script
Tests all Phase 2 tasks (2.1-2.5):
- Task 2.1: Competitive Analysis
- Task 2.2: Price Comparison & Differentiation Strategy
- Task 2.3: Risk Matrix Visualization
- Task 2.4: Top 10 Risks + Response Strategies
- Task 2.5: Exit Strategy Scenarios
"""
import os
import sys
import json

# Set working directory
os.chdir('/home/user/webapp')
sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_context_builder import ReportContextBuilder

def print_separator(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_phase2():
    """Test all Phase 2 tasks comprehensively"""
    
    print_separator("Phase 2 Implementation Test - Tasks 2.1 to 2.5")
    
    # Test data
    test_address = "서울시 강남구 역삼동 123"
    test_land_area = 500.0
    test_housing_type = "youth"
    
    print(f"Test Parameters:")
    print(f"  Address: {test_address}")
    print(f"  Land Area: {test_land_area}㎡")
    print(f"  Housing Type: {test_housing_type}")
    print()
    
    # Build context
    print("Building Expert Edition v3 Context...")
    builder = ReportContextBuilder()
    context = builder.build_expert_context(
        address=test_address,
        land_area_sqm=test_land_area,
        coordinates=None
    )
    
    print(f"✓ Context built successfully with {len(context)} sections")
    print()
    
    # ========================================================================
    # TASK 2.1: COMPETITIVE ANALYSIS
    # ========================================================================
    print_separator("TASK 2.1: Competitive Analysis")
    
    if 'competitive_analysis' in context:
        comp_analysis = context['competitive_analysis']
        
        print(f"Competitors Found: {comp_analysis.get('competitor_count', 0)}")
        print()
        
        if 'competitors' in comp_analysis:
            print("Competitor Details:")
            for i, comp in enumerate(comp_analysis['competitors'][:3], 1):
                print(f"  {i}. {comp.get('name', 'N/A')}")
                print(f"     거리: {comp.get('distance', 0):.1f}km")
                print(f"     임대료: {comp.get('rent_per_sqm', 0):,}원/㎡")
                print(f"     입주율: {comp.get('occupancy_rate', 0):.1f}%")
                print()
        
        if 'market_statistics' in comp_analysis:
            market = comp_analysis['market_statistics']
            print("Market Statistics:")
            print(f"  평균 임대료: {market.get('avg_rent', 0):,}원/㎡")
            print(f"  평균 입주율: {market.get('avg_occupancy', 0):.1f}%")
            print(f"  총 세대수: {market.get('total_units', 0):,}세대")
            print(f"  시장 포화도: {market.get('market_saturation', 'N/A')}")
            print(f"  경쟁 강도: {market.get('competitive_intensity', 'N/A')} ({market.get('intensity_score', 0):.1f}/100)")
            print()
        
        if 'positioning' in comp_analysis:
            pos = comp_analysis['positioning']
            print("Competitive Positioning:")
            print(f"  우리 임대료: {pos.get('our_rent', 0):,}원/㎡")
            print(f"  시장 대비: {pos.get('vs_market_avg', 0):+.1f}%")
            print(f"  포지셔닝: {pos.get('position', 'N/A')}")
            print(f"  백분위: {pos.get('percentile', 0)}th")
            print()
        
        if 'recommendations' in comp_analysis:
            print("Strategic Recommendations:")
            for i, rec in enumerate(comp_analysis['recommendations'], 1):
                print(f"  {i}. {rec}")
            print()
    else:
        print("⚠ No competitive_analysis found in context")
    
    # ========================================================================
    # TASK 2.2: PRICE COMPARISON & DIFFERENTIATION STRATEGY
    # ========================================================================
    print_separator("TASK 2.2: Price Comparison & Differentiation Strategy")
    
    if 'competitive_analysis' in context and 'price_comparison' in context['competitive_analysis']:
        price_comp = context['competitive_analysis']['price_comparison']
        
        if 'comparison_table' in price_comp:
            print("Price Comparison Table:")
            print(f"{'프로젝트명':<30} {'월임대료/㎡':>15} {'월임대료(25㎡)':>18} {'순위':>8}")
            print("-" * 80)
            
            for row in price_comp['comparison_table']:
                print(f"{row.get('name', 'N/A'):<30} {row.get('rent_per_sqm', 0):>13,}원/㎡ {row.get('monthly_rent_25sqm', 0):>15,}원 {row.get('rank', '-'):>8}")
            print()
            
            if 'summary' in price_comp:
                print(f"가격 포지셔닝: {price_comp['summary']}")
                print()
        
        if 'differentiation_strategy' in context['competitive_analysis']:
            diff_strat = context['competitive_analysis']['differentiation_strategy']
            
            print("Differentiation Strategies:")
            for i, strategy in enumerate(diff_strat.get('strategies', []), 1):
                print(f"\n  Strategy {i}: {strategy.get('title', 'N/A')}")
                print(f"  {strategy.get('description', 'N/A')}")
                if 'key_actions' in strategy:
                    print(f"  Key Actions:")
                    for action in strategy['key_actions']:
                        print(f"    • {action}")
            print()
    else:
        print("⚠ No price_comparison or differentiation_strategy found")
    
    # ========================================================================
    # TASK 2.3: RISK MATRIX VISUALIZATION
    # ========================================================================
    print_separator("TASK 2.3: Risk Matrix Visualization")
    
    # Check both possible locations
    risk_data = None
    if 'risk_enhancement' in context:
        risk_data = context['risk_enhancement']
    elif 'risk_analysis' in context and 'enhanced' in context['risk_analysis']:
        risk_data = context['risk_analysis']['enhanced']
    
    if risk_data and 'risk_matrix' in risk_data:
        risk_matrix = risk_data['risk_matrix']
        
        print("5x5 Risk Matrix:")
        print(f"  Matrix Size: {risk_matrix.get('matrix_size', 'N/A')}")
        print(f"  X-Axis (Probability): {risk_matrix.get('x_axis_label', 'N/A')}")
        print(f"  Y-Axis (Impact): {risk_matrix.get('y_axis_label', 'N/A')}")
        print()
        
        if 'matrix_data' in risk_matrix:
            print("Matrix Data (Probability x Impact):")
            matrix = risk_matrix['matrix_data']
            
            # Display matrix
            print("\n  Impact ↑")
            for i in range(5, 0, -1):
                row_str = f"    {i} │ "
                for j in range(1, 6):
                    cell = matrix.get(f"P{j}I{i}", {})
                    count = cell.get('count', 0)
                    level = cell.get('level', 'LOW')
                    color_code = {
                        'CRITICAL': '🔴',
                        'HIGH': '🟠',
                        'MEDIUM': '🟡',
                        'LOW': '🟢'
                    }.get(level, '⚪')
                    row_str += f"{color_code}({count:2d}) "
                print(row_str)
            print("      └─────────────────────→ Probability")
            print("        1    2    3    4    5")
            print()
        
        if 'risk_counts' in risk_matrix:
            counts = risk_matrix['risk_counts']
            print("Risk Level Distribution:")
            print(f"  🔴 CRITICAL: {counts.get('critical', 0)} risks")
            print(f"  🟠 HIGH: {counts.get('high', 0)} risks")
            print(f"  🟡 MEDIUM: {counts.get('medium', 0)} risks")
            print(f"  🟢 LOW: {counts.get('low', 0)} risks")
            print()
    else:
        print("⚠ No risk_matrix found in context")
    
    # ========================================================================
    # TASK 2.4: TOP 10 RISKS + RESPONSE STRATEGIES
    # ========================================================================
    print_separator("TASK 2.4: Top 10 Risks + Response Strategies")
    
    # Check both possible locations
    risk_data = None
    if 'risk_enhancement' in context:
        risk_data = context['risk_enhancement']
    elif 'risk_analysis' in context and 'enhanced' in context['risk_analysis']:
        risk_data = context['risk_analysis']['enhanced']
    
    if risk_data and 'top_10_risks' in risk_data:
        top_risks = risk_data['top_10_risks']
        
        print(f"Total Risks Identified: {len(top_risks)}")
        print()
        
        for risk in top_risks[:5]:  # Show first 5 for brevity
            print(f"Risk {risk.get('risk_id', 'N/A')}: {risk.get('name', 'N/A')}")
            print(f"  Category: {risk.get('category', 'N/A')}")
            print(f"  Probability: {risk.get('probability', 0)}/5")
            print(f"  Impact: {risk.get('impact', 0)}/5")
            print(f"  Risk Score: {risk.get('risk_score', 0)}")
            print(f"  Level: {risk.get('level', 'N/A')}")
            print()
            
            if 'response_strategies' in risk:
                print("  Response Strategies:")
                for i, strategy in enumerate(risk['response_strategies'], 1):
                    if isinstance(strategy, dict):
                        print(f"    {i}. {strategy.get('title', 'N/A')}")
                        print(f"       {strategy.get('description', 'N/A')}")
                    else:
                        # String format
                        print(f"    {i}. {strategy}")
                print()
        
        if len(top_risks) > 5:
            print(f"... and {len(top_risks) - 5} more risks")
            print()
    else:
        print("⚠ No top_10_risks found in context")
    
    # ========================================================================
    # TASK 2.5: EXIT STRATEGY SCENARIOS
    # ========================================================================
    print_separator("TASK 2.5: Exit Strategy Scenarios")
    
    # Check both possible locations
    risk_data = None
    if 'risk_enhancement' in context:
        risk_data = context['risk_enhancement']
    elif 'risk_analysis' in context and 'enhanced' in context['risk_analysis']:
        risk_data = context['risk_analysis']['enhanced']
    
    if risk_data and 'exit_strategies' in risk_data:
        exit_strat = risk_data['exit_strategies']
        
        print(f"Exit Scenarios Defined: {len(exit_strat.get('strategies', []))}")
        print()
        
        for scenario in exit_strat.get('strategies', []):
            print(f"Scenario: {scenario.get('scenario_kr', scenario.get('scenario', 'N/A'))}")
            print(f"  Timeline: {scenario.get('timeline', 'N/A')}")
            print()
            
            if 'conditions' in scenario:
                print("  Trigger Conditions:")
                for condition in scenario['conditions']:
                    print(f"    • {condition}")
                print()
            
            if 'exit_methods' in scenario:
                print("  Exit Methods:")
                for method in scenario['exit_methods']:
                    print(f"    • {method.get('method', 'N/A')}: {method.get('description', 'N/A')}")
                print()
            
            if 'expected_value_kr' in scenario:
                print(f"  Expected Value: {scenario['expected_value_kr']}")
                print()
    else:
        print("⚠ No exit_strategies found in context")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print_separator("Phase 2 Test Summary")
    
    # Check for risk data in both possible locations
    risk_data = None
    if 'risk_enhancement' in context:
        risk_data = context['risk_enhancement']
    elif 'risk_analysis' in context and 'enhanced' in context['risk_analysis']:
        risk_data = context['risk_analysis']['enhanced']
    
    tasks_status = {
        '2.1 Competitive Analysis': 'competitive_analysis' in context,
        '2.2 Price Comparison': 'competitive_analysis' in context and 'price_comparison' in context.get('competitive_analysis', {}),
        '2.3 Risk Matrix': risk_data is not None and 'risk_matrix' in risk_data,
        '2.4 Top 10 Risks': risk_data is not None and 'top_10_risks' in risk_data,
        '2.5 Exit Strategy': risk_data is not None and 'exit_strategies' in risk_data and len(risk_data.get('exit_strategies', {}).get('strategies', [])) > 0
    }
    
    print("Task Completion Status:")
    for task, status in tasks_status.items():
        status_icon = "✓" if status else "✗"
        print(f"  {status_icon} {task}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(tasks_status.values())
    print()
    print(f"Overall Phase 2 Status: {'✓ ALL TASKS PASS' if all_passed else '✗ SOME TASKS FAILED'}")
    print()
    
    return all_passed

if __name__ == "__main__":
    try:
        success = test_phase2()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
