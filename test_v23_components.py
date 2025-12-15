#!/usr/bin/env python3
"""
ZeroSite v23 - Component Test Script
=====================================
Tests all v23 components independently
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.scenario_engine import ABScenarioEngine
from app.visualization.far_chart import FARChartGenerator
from app.visualization.market_histogram import MarketHistogramGenerator

print("=" * 80)
print("ZeroSite v23 - Component Test Suite")
print("=" * 80)

# Test data
test_cases = [
    ("서울특별시 강남구 역삼동 123-45", 1650.0),
    ("서울특별시 송파구 잠실동 456-78", 1800.0),
    ("서울특별시 노원구 상계동 789-12", 2000.0),
]

# Initialize engines
engine = ABScenarioEngine()
far_generator = FARChartGenerator()
market_generator = MarketHistogramGenerator()

test_results = []

for idx, (address, land_area) in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST CASE {idx}: {address} ({land_area}㎡)")
    print(f"{'='*80}")
    
    try:
        # 1. Generate scenarios
        print("\n🔵 Generating Scenario A (청년)...")
        scenario_a = engine.generate_scenario_A(address, land_area)
        print(f"   ✅ Scenario A generated")
        print(f"      - FAR: {scenario_a.far_legal}% → {scenario_a.far_final}%")
        print(f"      - Units: {scenario_a.unit_count}")
        print(f"      - CAPEX: {scenario_a.total_capex/1e8:.2f}억원")
        print(f"      - ROI: {scenario_a.roi:.2f}%")
        print(f"      - Decision: {scenario_a.decision}")
        
        print("\n🟠 Generating Scenario B (신혼부부)...")
        scenario_b = engine.generate_scenario_B(address, land_area)
        print(f"   ✅ Scenario B generated")
        print(f"      - FAR: {scenario_b.far_legal}% → {scenario_b.far_final}%")
        print(f"      - Units: {scenario_b.unit_count}")
        print(f"      - CAPEX: {scenario_b.total_capex/1e8:.2f}억원")
        print(f"      - ROI: {scenario_b.roi:.2f}%")
        print(f"      - Decision: {scenario_b.decision}")
        
        # 2. Compare scenarios
        print("\n📊 Comparing scenarios...")
        comparison = engine.compare_scenarios(scenario_a, scenario_b)
        print(f"   ✅ Comparison completed")
        print(f"      - FAR Winner: {comparison['far_final']['winner']}")
        print(f"      - Profit Winner: {comparison['profit']['winner']}")
        print(f"      - ROI Winner: {comparison['roi']['winner']}")
        print(f"      - Decision Winner: {comparison['decision']['winner']}")
        
        # 3. Generate summary
        print("\n📝 Generating comparison summary...")
        summary = engine.generate_comparison_summary(scenario_a, scenario_b, comparison)
        print(f"   ✅ Summary generated ({len(summary)} chars)")
        
        # 4. Generate recommendation
        print("\n💡 Generating recommendation...")
        recommendation = engine.generate_recommendation(scenario_a, scenario_b, comparison)
        print(f"   ✅ Recommendation generated")
        print(f"      Conclusion: {recommendation['conclusion']}")
        
        # 5. Generate visualizations
        print("\n📈 Generating visualizations...")
        
        # FAR chart
        far_base64, _ = far_generator.generate_far_comparison_chart(
            scenario_a.far_legal,
            scenario_a.far_final,
            scenario_b.far_legal,
            scenario_b.far_final
        )
        print(f"   ✅ FAR chart generated ({len(far_base64)} chars base64)")
        
        # Market histogram
        market_base64, _, stats = market_generator.generate_price_distribution_histogram(address)
        print(f"   ✅ Market histogram generated ({len(market_base64)} chars base64)")
        print(f"      - Mean: {stats['mean']:.2f}M/㎡")
        print(f"      - Std: {stats['std']:.2f}M/㎡")
        print(f"      - CV: {stats['cv']:.1f}%")
        
        test_results.append({
            "address": address,
            "status": "SUCCESS",
            "scenario_a_decision": scenario_a.decision,
            "scenario_b_decision": scenario_b.decision,
            "winner": comparison['decision']['winner']
        })
        
        print(f"\n✅ TEST CASE {idx} PASSED")
        
    except Exception as e:
        print(f"\n❌ TEST CASE {idx} FAILED: {str(e)}")
        test_results.append({
            "address": address,
            "status": "FAILED",
            "error": str(e)
        })

# Summary
print(f"\n{'='*80}")
print("TEST SUMMARY")
print(f"{'='*80}")

passed = sum(1 for r in test_results if r['status'] == 'SUCCESS')
failed = sum(1 for r in test_results if r['status'] == 'FAILED')

print(f"\nTotal Tests: {len(test_results)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Success Rate: {passed/len(test_results)*100:.1f}%")

print(f"\n{'='*80}")
print("DETAILED RESULTS")
print(f"{'='*80}")

for idx, result in enumerate(test_results, 1):
    print(f"\n{idx}. {result['address']}")
    print(f"   Status: {result['status']}")
    if result['status'] == 'SUCCESS':
        print(f"   Scenario A: {result['scenario_a_decision']}")
        print(f"   Scenario B: {result['scenario_b_decision']}")
        print(f"   Winner: Scenario {result['winner']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")

print(f"\n{'='*80}")
if passed == len(test_results):
    print("🎉 ALL TESTS PASSED - ZeroSite v23 PRODUCTION READY!")
else:
    print(f"⚠️  {failed} TEST(S) FAILED - REVIEW REQUIRED")
print(f"{'='*80}")
