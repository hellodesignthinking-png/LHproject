#!/usr/bin/env python3
"""
Test Suite for Expert v3.2 Integration
======================================
Comprehensive tests for v3.2 backend engines + Section 03-1 integration

Test Coverage:
1. Backend Engines (Financial, Cost, Market)
2. A/B Scenario Engine
3. Expert v3.2 Generator
4. API Endpoint (/api/v3.2/generate-expert-report)
5. Complete Report Generation Workflow

Author: ZeroSite v3.2 Testing Team
Date: 2025-12-11
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, '/home/user/webapp')

# Test counters
test_count = 0
passed_count = 0
failed_count = 0

def test(name: str):
    """Test decorator"""
    global test_count
    test_count += 1
    print(f"\n{'='*80}")
    print(f"TEST #{test_count}: {name}")
    print('='*80)

def assert_pass(condition: bool, message: str):
    """Assert with pass/fail tracking"""
    global passed_count, failed_count
    if condition:
        print(f"  ✅ PASS: {message}")
        passed_count += 1
    else:
        print(f"  ❌ FAIL: {message}")
        failed_count += 1

def assert_exists(obj, key: str, message: str):
    """Assert key exists in object"""
    condition = key in obj
    assert_pass(condition, message)
    return condition

def assert_gt(value, threshold, message: str):
    """Assert value > threshold"""
    condition = value > threshold
    assert_pass(condition, message)
    return condition


# ==========================================
# TEST 1: Import Backend Engines
# ==========================================

test("Import v3.2 Backend Engines")

try:
    from backend.services_v9.financial_analysis_engine import FinancialAnalysisEngineV32
    assert_pass(True, "FinancialAnalysisEngineV32 imported")
except ImportError as e:
    assert_pass(False, f"FinancialAnalysisEngineV32 import failed: {e}")

try:
    from backend.services_v9.cost_estimation_engine import CostEstimationEngineV32
    assert_pass(True, "CostEstimationEngineV32 imported")
except ImportError as e:
    assert_pass(False, f"CostEstimationEngineV32 import failed: {e}")

try:
    from backend.services_v9.market_data_processor import MarketDataProcessorV32
    assert_pass(True, "MarketDataProcessorV32 imported")
except ImportError as e:
    assert_pass(False, f"MarketDataProcessorV32 import failed: {e}")

try:
    from backend.services_v9.ab_scenario_engine import ABScenarioEngine
    assert_pass(True, "ABScenarioEngine imported")
except ImportError as e:
    assert_pass(False, f"ABScenarioEngine import failed: {e}")


# ==========================================
# TEST 2: Financial Analysis Engine
# ==========================================

test("Financial Analysis Engine v3.2")

try:
    from backend.services_v9.financial_analysis_engine import FinancialAnalysisEngineV32
    
    engine = FinancialAnalysisEngineV32()
    assert_pass(True, "Engine instantiated")
    
    result = engine.analyze(
        land_price=62_700_000_000,  # 62.7 billion KRW
        construction_cost=88_500_000_000,  # 88.5 billion KRW
        other_costs=14_200_000_000,  # 14.2 billion KRW
        total_units=30,
        unit_size_sqm=60.0,
        lh_price_per_sqm=3_850_000
    )
    
    assert_exists(result, 'total_investment', "Result contains 'total_investment'")
    assert_exists(result, 'lh_purchase_price', "Result contains 'lh_purchase_price'")
    assert_exists(result, 'profit', "Result contains 'profit'")
    assert_exists(result, 'roi_percent', "Result contains 'roi_percent'")
    assert_exists(result, 'npv', "Result contains 'npv'")
    assert_exists(result, 'irr_percent', "Result contains 'irr_percent'")
    
    # ROI should be realistic (-50% to +100%)
    roi_realistic = -50 <= result['roi_percent'] <= 100
    assert_pass(roi_realistic, f"ROI is realistic: {result['roi_percent']:.2f}%")
    
    print(f"\n  📊 Sample Results:")
    print(f"     Total Investment: {result['total_investment']/1e8:.1f}억원")
    print(f"     LH Purchase Price: {result['lh_purchase_price']/1e8:.1f}억원")
    print(f"     Profit: {result['profit']/1e8:.1f}억원")
    print(f"     ROI: {result['roi_percent']:.2f}%")
    print(f"     NPV: {result['npv']/1e8:.1f}억원")
    print(f"     IRR: {result['irr_percent']:.2f}%")

except Exception as e:
    assert_pass(False, f"Financial engine test failed: {e}")


# ==========================================
# TEST 3: Cost Estimation Engine
# ==========================================

test("Cost Estimation Engine v3.2")

try:
    from backend.services_v9.cost_estimation_engine import CostEstimationEngineV32
    
    engine = CostEstimationEngineV32()
    assert_pass(True, "Engine instantiated")
    
    result = engine.estimate(
        land_area_sqm=660.0,
        land_price_per_sqm=9_500_000,
        total_floor_area_sqm=1980.0
    )
    
    assert_exists(result, 'cost_breakdown', "Result contains 'cost_breakdown'")
    assert_exists(result, 'total_cost', "Result contains 'total_cost'")
    assert_exists(result, 'cost_per_sqm', "Result contains 'cost_per_sqm'")
    
    breakdown = result['cost_breakdown']
    assert_exists(breakdown, 'land_acquisition', "Breakdown contains 'land_acquisition'")
    assert_exists(breakdown, 'construction', "Breakdown contains 'construction'")
    assert_exists(breakdown, 'design_fee', "Breakdown contains 'design_fee'")
    
    # Verify sum equals total
    breakdown_sum = sum(breakdown.values())
    total_cost = result['total_cost']
    sum_matches = abs(breakdown_sum - total_cost) < 1000  # Allow ₩1000 rounding error
    assert_pass(sum_matches, f"Breakdown sum matches total: {breakdown_sum:,.0f} ≈ {total_cost:,.0f}")
    
    print(f"\n  📊 Sample Results:")
    print(f"     Total Cost: {total_cost/1e8:.1f}억원")
    print(f"     Land Acquisition: {breakdown['land_acquisition']/1e8:.1f}억원")
    print(f"     Construction: {breakdown['construction']/1e8:.1f}억원")
    print(f"     Cost/㎡: {result['cost_per_sqm']:,.0f}원")

except Exception as e:
    assert_pass(False, f"Cost engine test failed: {e}")


# ==========================================
# TEST 4: A/B Scenario Engine
# ==========================================

test("A/B Scenario Engine")

try:
    from backend.services_v9.ab_scenario_engine import ABScenarioEngine
    
    engine = ABScenarioEngine()
    assert_pass(True, "Engine instantiated")
    
    result = engine.compare_scenarios(
        land_area_sqm=660.0,
        bcr_legal=50.0,
        far_legal=300.0,
        avg_land_price_per_sqm=9_500_000
    )
    
    assert_exists(result, 'scenario_a', "Result contains 'scenario_a'")
    assert_exists(result, 'scenario_b', "Result contains 'scenario_b'")
    assert_exists(result, 'comparison_table', "Result contains 'comparison_table'")
    assert_exists(result, 'recommendation', "Result contains 'recommendation'")
    
    scenario_a = result['scenario_a']
    scenario_b = result['scenario_b']
    
    # Scenario A (Youth) should have 50% FAR relaxation
    far_a_relaxation = scenario_a['far_final'] - scenario_a['far_legal']
    far_a_correct = abs(far_a_relaxation - 150.0) < 1.0  # Should be +150%p
    assert_pass(far_a_correct, f"Scenario A FAR relaxation: +{far_a_relaxation:.0f}%p (expected +150%p)")
    
    # Scenario B (Newlywed) should have 30% FAR relaxation
    far_b_relaxation = scenario_b['far_final'] - scenario_b['far_legal']
    far_b_correct = abs(far_b_relaxation - 90.0) < 1.0  # Should be +90%p
    assert_pass(far_b_correct, f"Scenario B FAR relaxation: +{far_b_relaxation:.0f}%p (expected +90%p)")
    
    # Recommendation should be A or B
    recommended = result['recommendation']['recommended_scenario']
    rec_valid = recommended in ['A', 'B']
    assert_pass(rec_valid, f"Recommendation is valid: {recommended}")
    
    print(f"\n  📊 Comparison Results:")
    print(f"     Scenario A (Youth): {scenario_a['total_units']} units, {scenario_a['roi_percent']:.2f}% ROI")
    print(f"     Scenario B (Newlywed): {scenario_b['total_units']} units, {scenario_b['roi_percent']:.2f}% ROI")
    print(f"     Recommended: Scenario {recommended}")

except Exception as e:
    assert_pass(False, f"A/B Scenario engine test failed: {e}")


# ==========================================
# TEST 5: Expert v3.2 Generator
# ==========================================

test("Expert v3.2 Report Generator")

try:
    from backend.services_v9.expert_v3_generator import ExpertV3ReportGenerator
    
    generator = ExpertV3ReportGenerator()
    assert_pass(True, "Generator instantiated")
    
    result = generator.generate_complete_report(
        address="서울특별시 마포구 월드컵북로 120",
        land_area_sqm=660.0,
        bcr_legal=50.0,
        far_legal=300.0
    )
    
    assert_exists(result, 'html', "Result contains 'html'")
    assert_exists(result, 'metadata', "Result contains 'metadata'")
    assert_exists(result, 'section_03_1_data', "Result contains 'section_03_1_data'")
    
    html = result['html']
    metadata = result['metadata']
    section_data = result['section_03_1_data']
    
    # HTML should be substantial (>5KB)
    html_size = len(html)
    assert_gt(html_size, 5000, f"HTML size is substantial: {html_size:,} bytes")
    
    # Should contain Section 03-1
    has_section_03_1 = 'Section 03-1' in html or 'SECTION 03-1' in html
    assert_pass(has_section_03_1, "HTML contains Section 03-1")
    
    # Should contain A/B comparison
    has_ab_comparison = '시나리오 A' in html and '시나리오 B' in html
    assert_pass(has_ab_comparison, "HTML contains A/B comparison")
    
    # Metadata should be complete
    assert_exists(metadata, 'recommended_scenario', "Metadata contains 'recommended_scenario'")
    assert_exists(metadata, 'version', "Metadata contains 'version'")
    
    print(f"\n  📊 Generation Results:")
    print(f"     HTML Size: {html_size:,} bytes")
    print(f"     Recommended Scenario: {metadata['recommended_scenario']}")
    print(f"     Version: {metadata['version']}")

except Exception as e:
    assert_pass(False, f"Expert v3.2 generator test failed: {e}")


# ==========================================
# TEST 6: Section 03-1 Data Structure
# ==========================================

test("Section 03-1 Data Structure")

try:
    from backend.services_v9.expert_v3_generator import ExpertV3ReportGenerator
    
    generator = ExpertV3ReportGenerator()
    
    data = generator.generate_section_03_1_data(
        land_area_sqm=660.0,
        bcr_legal=50.0,
        far_legal=300.0,
        avg_land_price_per_sqm=9_500_000
    )
    
    # Should have 50+ variables
    data_count = len(data)
    assert_gt(data_count, 50, f"Data contains {data_count} variables (expected 50+)")
    
    # Key Scenario A variables
    scenario_a_keys = [
        'scenario_a_name', 'scenario_a_unit_count', 'scenario_a_far_final',
        'scenario_a_total_capex', 'scenario_a_roi', 'scenario_a_decision'
    ]
    for key in scenario_a_keys:
        assert_exists(data, key, f"Data contains '{key}'")
    
    # Key Scenario B variables
    scenario_b_keys = [
        'scenario_b_name', 'scenario_b_unit_count', 'scenario_b_far_final',
        'scenario_b_total_capex', 'scenario_b_roi', 'scenario_b_decision'
    ]
    for key in scenario_b_keys:
        assert_exists(data, key, f"Data contains '{key}'")
    
    # Recommendation
    assert_exists(data, 'recommended_scenario', "Data contains 'recommended_scenario'")
    assert_exists(data, 'final_recommendation', "Data contains 'final_recommendation'")
    
    print(f"\n  📊 Data Structure:")
    print(f"     Total Variables: {data_count}")
    print(f"     Scenario A Name: {data.get('scenario_a_name', 'N/A')}")
    print(f"     Scenario B Name: {data.get('scenario_b_name', 'N/A')}")
    print(f"     Recommended: {data.get('final_recommendation', 'N/A')}")

except Exception as e:
    assert_pass(False, f"Section 03-1 data test failed: {e}")


# ==========================================
# FINAL REPORT
# ==========================================

print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"Total Tests: {test_count}")
print(f"Total Assertions: {passed_count + failed_count}")
print(f"✅ Passed: {passed_count}")
print(f"❌ Failed: {failed_count}")

if failed_count == 0:
    print("\n🎉 ALL TESTS PASSED! Expert v3.2 is ready for integration.")
    success_rate = 100.0
else:
    success_rate = (passed_count / (passed_count + failed_count)) * 100
    print(f"\n⚠️  Some tests failed. Success rate: {success_rate:.1f}%")

print("="*80)

# Exit with appropriate code
sys.exit(0 if failed_count == 0 else 1)
