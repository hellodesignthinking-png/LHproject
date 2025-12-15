#!/usr/bin/env python3
"""
Test Financial Engine with Multiple Scenarios
Tests various land sizes, locations, and unit types
"""

import sys
import os
import importlib.util

# Direct import of financial engine
current_dir = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "financial_engine_v7_4",
    os.path.join(current_dir, "app/services/financial_engine_v7_4.py")
)
financial_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(financial_module)

run_full_financial_analysis = financial_module.run_full_financial_analysis


def format_krw(amount):
    """Format Korean Won"""
    if amount >= 100_000_000:
        return f"{amount / 100_000_000:.1f}억원"
    elif amount >= 10_000:
        return f"{amount / 10_000:.0f}만원"
    else:
        return f"{amount:,.0f}원"


# Test scenarios
SCENARIOS = [
    {
        'name': 'Scenario 1: Small Mapo Site (Suburban)',
        'land_area': 660.0,
        'address': '서울특별시 마포구 월드컵북로 120',
        'unit_type': '청년',
        'construction_type': 'standard'
    },
    {
        'name': 'Scenario 2: Medium Gangnam Site (Premium)',
        'land_area': 1200.0,
        'address': '서울특별시 강남구 역삼동 123',
        'unit_type': '신혼부부 I',
        'construction_type': 'standard'
    },
    {
        'name': 'Scenario 3: Large Gangbuk Site (Economy)',
        'land_area': 2000.0,
        'address': '서울특별시 종로구 혜화동 456',
        'unit_type': '다자녀',
        'construction_type': 'economy'
    },
    {
        'name': 'Scenario 4: Very Small Gangnam (High-end)',
        'land_area': 400.0,
        'address': '서울특별시 서초구 서초동 789',
        'unit_type': '청년',
        'construction_type': 'premium'
    },
    {
        'name': 'Scenario 5: Large Suburban Mixed',
        'land_area': 3000.0,
        'address': '서울특별시 양천구 목동 101',
        'unit_type': '고령자',
        'construction_type': 'standard'
    },
]


def test_scenario(scenario):
    """Test a single scenario"""
    print("\n" + "="*100)
    print(f"📊 {scenario['name']}")
    print("="*100)
    
    print(f"\n📍 Parameters:")
    print(f"   - Location: {scenario['address']}")
    print(f"   - Land Area: {scenario['land_area']}㎡")
    print(f"   - Unit Type: {scenario['unit_type']}")
    print(f"   - Construction: {scenario['construction_type']}")
    
    # Run analysis
    result = run_full_financial_analysis(
        scenario['land_area'],
        scenario['address'],
        scenario['unit_type'],
        scenario['construction_type']
    )
    
    # Extract results
    capex = result['capex']
    noi = result['noi']
    returns = result['returns']
    breakeven = result['breakeven']
    sensitivity = result['sensitivity']
    summary = result['summary']
    
    # Display key results
    print(f"\n💰 Financial Results:")
    print(f"   - Total Investment: {format_krw(capex['total_capex'])}")
    print(f"   - Unit Count: {capex['unit_count']}세대")
    print(f"   - Per Unit Cost: {format_krw(capex['capex_per_unit'])}")
    print(f"   - Land Zone: {capex['land_price_zone']}")
    
    print(f"\n📈 Performance Metrics:")
    print(f"   - Cap Rate: {returns['cap_rate_percent']:.2f}%")
    print(f"   - LH Target: {returns['lh_target_cap_rate_percent']:.2f}%")
    print(f"   - Meets LH Criteria: {'✅ YES' if returns['meets_lh_target'] else '❌ NO'}")
    print(f"   - NOI (Year 2): {format_krw(noi['noi'])}")
    print(f"   - NOI Margin: {noi['noi_margin_percent']:.1f}%")
    
    print(f"\n⚖️  Breakeven Analysis:")
    print(f"   - Breakeven Occupancy: {breakeven['breakeven_occupancy_percent']:.1f}%")
    print(f"   - Achievable: {'✅ YES' if breakeven['achievable'] else '❌ NO'}")
    print(f"   - Payback Period: {breakeven['payback_period_years']:.1f} years")
    
    irr_range = sensitivity['summary']['irr_range']
    print(f"\n📊 Sensitivity (IRR Range):")
    print(f"   - Pessimistic: {irr_range['pessimistic']:.2f}%")
    print(f"   - Base: {irr_range['base']:.2f}%")
    print(f"   - Optimistic: {irr_range['optimistic']:.2f}%")
    print(f"   - Spread: {irr_range['spread']:.2f}%")
    
    # Investment decision
    print(f"\n💡 Investment Decision:")
    if returns['meets_lh_target'] and breakeven['achievable']:
        print(f"   ✅ RECOMMEND: Strong project, meets all criteria")
        decision = "GO"
    elif returns['meets_lh_target']:
        print(f"   ⚠️  CONDITIONAL: Meets cap rate but breakeven challenging")
        decision = "CONDITIONAL"
    elif breakeven['achievable']:
        print(f"   ⚠️  CONDITIONAL: Good breakeven but cap rate low")
        decision = "CONDITIONAL"
    else:
        print(f"   ❌ NOT RECOMMEND: Requires optimization")
        decision = "NO-GO"
    
    return {
        'name': scenario['name'],
        'land_area': scenario['land_area'],
        'address': scenario['address'],
        'unit_type': scenario['unit_type'],
        'unit_count': capex['unit_count'],
        'investment': capex['total_capex'],
        'cap_rate': returns['cap_rate_percent'],
        'meets_lh': returns['meets_lh_target'],
        'achievable': breakeven['achievable'],
        'decision': decision,
        'irr_spread': irr_range['spread']
    }


def main():
    """Run all scenarios and compare"""
    print("="*100)
    print("🧪 ZeroSite v7.4 Financial Engine - Multi-Scenario Testing")
    print("="*100)
    print(f"\nTesting {len(SCENARIOS)} different scenarios...")
    
    results = []
    for scenario in SCENARIOS:
        result = test_scenario(scenario)
        results.append(result)
    
    # Summary comparison
    print("\n" + "="*100)
    print("📊 SCENARIO COMPARISON SUMMARY")
    print("="*100)
    
    print(f"\n{'Scenario':<40} {'Land(㎡)':<10} {'Units':<8} {'Investment':<15} {'Cap Rate':<12} {'Decision':<15}")
    print("-"*100)
    
    for r in results:
        scenario_name = r['name'].replace('Scenario ', 'S')[:38]
        print(f"{scenario_name:<40} "
              f"{r['land_area']:<10.0f} "
              f"{r['unit_count']:<8} "
              f"{format_krw(r['investment']):<15} "
              f"{r['cap_rate']:>6.2f}% {'✓' if r['meets_lh'] else '✗':<5} "
              f"{r['decision']:<15}")
    
    # Statistics
    go_count = sum(1 for r in results if r['decision'] == 'GO')
    conditional_count = sum(1 for r in results if r['decision'] == 'CONDITIONAL')
    no_go_count = sum(1 for r in results if r['decision'] == 'NO-GO')
    
    avg_cap_rate = sum(r['cap_rate'] for r in results) / len(results)
    
    print(f"\n📈 Statistics:")
    print(f"   - Total Scenarios: {len(results)}")
    print(f"   - GO: {go_count} ({go_count/len(results)*100:.0f}%)")
    print(f"   - CONDITIONAL: {conditional_count} ({conditional_count/len(results)*100:.0f}%)")
    print(f"   - NO-GO: {no_go_count} ({no_go_count/len(results)*100:.0f}%)")
    print(f"   - Average Cap Rate: {avg_cap_rate:.2f}%")
    
    # Best and worst
    best = max(results, key=lambda x: x['cap_rate'])
    worst = min(results, key=lambda x: x['cap_rate'])
    
    print(f"\n🏆 Best Scenario:")
    print(f"   - {best['name']}")
    print(f"   - Cap Rate: {best['cap_rate']:.2f}%")
    print(f"   - Investment: {format_krw(best['investment'])}")
    
    print(f"\n⚠️  Worst Scenario:")
    print(f"   - {worst['name']}")
    print(f"   - Cap Rate: {worst['cap_rate']:.2f}%")
    print(f"   - Investment: {format_krw(worst['investment'])}")
    
    # Key insights
    print(f"\n💡 Key Insights:")
    
    # Land price zone impact
    gangnam_scenarios = [r for r in results if 'gangnam' in r['address'].lower() or '강남' in r['address'] or '서초' in r['address']]
    suburban_scenarios = [r for r in results if r not in gangnam_scenarios and '종로' not in r['address'] and '중구' not in r['address']]
    
    if gangnam_scenarios:
        gangnam_avg = sum(r['cap_rate'] for r in gangnam_scenarios) / len(gangnam_scenarios)
        print(f"   1. Gangnam Zone Average Cap Rate: {gangnam_avg:.2f}% (typically lower due to high land costs)")
    
    if suburban_scenarios:
        suburban_avg = sum(r['cap_rate'] for r in suburban_scenarios) / len(suburban_scenarios)
        print(f"   2. Suburban Zone Average Cap Rate: {suburban_avg:.2f}% (typically higher due to lower land costs)")
    
    # Size impact
    large_sites = [r for r in results if r['land_area'] >= 1500]
    small_sites = [r for r in results if r['land_area'] < 1000]
    
    if large_sites:
        large_avg = sum(r['cap_rate'] for r in large_sites) / len(large_sites)
        print(f"   3. Large Sites (≥1500㎡) Average Cap Rate: {large_avg:.2f}% (economies of scale)")
    
    if small_sites:
        small_avg = sum(r['cap_rate'] for r in small_sites) / len(small_sites)
        print(f"   4. Small Sites (<1000㎡) Average Cap Rate: {small_avg:.2f}% (higher per-unit costs)")
    
    print(f"\n✅ Multi-scenario testing complete!")
    print("="*100)


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
