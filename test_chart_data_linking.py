#!/usr/bin/env python3
"""
Chart Data Linking Test
Verifies image page data is correctly linked and displayed
"""

import sys
import os
sys.path.insert(0, '/home/user/webapp')

from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator

def test_m4_chart_labels():
    """Test M4 bar chart delta labels are correct"""
    print("\n🧪 Testing M4 Chart Labels...")
    generator = ModulePDFGenerator()
    
    test_data = {
        "selected_scenario_id": "scenario_A",
        "legal_capacity": {
            "far_max": 200.0,
            "bcr_max": 60.0,
            "total_units": 20,  # First bar
            "gross_floor_area": 1500.0,
            "site_area": 750.0,
            "buildable_area": 450.0
        },
        "incentive_capacity": {
            "far_max": 260.0,
            "total_units": 26,  # Second bar (should show +6)
            "additional_far": 60.0
        },
        "parking": {
            "required": 20,
            "alt_a": {"solution": "B3", "count": 18},
            "alt_b": {"solution": "B2", "count": 20}
        },
        "scenarios": [
            {"id": "scenario_A", "name": "Option A", "units": 26}
        ]
    }
    
    try:
        pdf_bytes = generator.generate_m4_capacity_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M4_CHART_LABELS.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M4 chart generated: {len(pdf_bytes):,} bytes")
        print(f"  📊 Expected labels:")
        print(f"     - First bar: 20세대 (법정 기준)")
        print(f"     - Second bar: 26세대 (법정 대비 +6)")
        print(f"  📄 Verify in: {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
        return False

def test_m5_zero_value_charts():
    """Test M5 charts handle zero values properly"""
    print("\n🧪 Testing M5 Zero Value Handling...")
    generator = ModulePDFGenerator()
    
    # Test with all zero values
    test_data = {
        "household_count": 20,
        "avg_unit_area_m2": 59.0,
        "lh_unit_price": 320000000,
        "costs": {
            "land": 0,           # Zero
            "construction": 0,   # Zero
            "design": 0,
            "permit": 0,
            "finance": 0,
            "other": 0,
            "total": 0           # Zero
        },
        "revenues": {
            "sale": 0,
            "rental": 0,
            "other": 0,
            "total": 0           # Zero
        },
        "scenarios": [
            {
                "id": "scenario_A",
                "name": "Test Scenario",
                "units": 20,
                "lh_price": 76800000000,
                "total_cost": 0,     # Zero
                "profit": 0,
                "profit_margin": 0
            }
        ]
    }
    
    try:
        pdf_bytes = generator.generate_m5_feasibility_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M5_ZERO_VALUES.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M5 chart with zeros generated: {len(pdf_bytes):,} bytes")
        print(f"  📊 Expected behavior:")
        print(f"     - Pie chart: Shows '비용 데이터 불충분 (N/A)'")
        print(f"     - Bar chart: Shows 'N/A (데이터 없음)' labels")
        print(f"  📄 Verify in: {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_m6_radar_chart_correct_keys():
    """Test M6 radar chart uses correct data keys"""
    print("\n🧪 Testing M6 Radar Chart Data Keys...")
    generator = ModulePDFGenerator()
    
    test_data = {
        "m5_score": 75,
        "m6_score": 85,
        "total_score": 85,
        "approval_rate": 77.3,
        "grade": "A",
        "decision": "GO",
        "scores": {
            # Correct M6 scoring keys (110 total)
            "location": 30,      # Out of 35
            "scale": 12,         # Out of 15
            "feasibility": 35,   # Out of 40
            "compliance": 18,    # Out of 20
            # OLD WRONG KEYS (should NOT be used):
            # "demand": 0,       # Doesn't exist in M6
            # "capacity": 0,     # Wrong key
            # "other": 0         # Not part of 110 system
        },
        "hard_fail_items": [
            {"name": "용적률", "passed": True},
            {"name": "주차", "passed": True}
        ]
    }
    
    try:
        pdf_bytes = generator.generate_m6_lh_review_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M6_RADAR_CORRECT.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M6 radar chart generated: {len(pdf_bytes):,} bytes")
        print(f"  📊 Expected behavior:")
        print(f"     - 4 categories (not 5): 입지, 규모, 사업성, 준수성")
        print(f"     - Max scores: [35, 15, 40, 20]")
        print(f"     - Values: [30, 12, 35, 18] = 95/110 total")
        print(f"  📄 Verify in: {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_m5_normal_data_charts():
    """Test M5 charts with normal non-zero data"""
    print("\n🧪 Testing M5 Charts with Normal Data...")
    generator = ModulePDFGenerator()
    
    test_data = {
        "household_count": 20,
        "avg_unit_area_m2": 59.0,
        "lh_unit_price": 320000000,
        "costs": {
            "land": 50000000000,
            "construction": 30000000000,
            "design": 1200000000,
            "permit": 300000000,
            "finance": 2700000000,
            "other": 1500000000,
            "total": 85700000000
        },
        "revenues": {
            "sale": 95000000000,
            "rental": 5000000000,
            "other": 2000000000,
            "total": 102000000000
        },
        "scenarios": [
            {
                "id": "scenario_A",
                "name": "Best Case",
                "units": 20,
                "lh_price": 76800000000,
                "total_cost": 85700000000,
                "profit": 16300000000,
                "profit_margin": 16.0
            }
        ]
    }
    
    try:
        pdf_bytes = generator.generate_m5_feasibility_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M5_NORMAL_DATA.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M5 chart with normal data: {len(pdf_bytes):,} bytes")
        print(f"  📊 Expected behavior:")
        print(f"     - Pie chart: Shows 3 segments with percentages")
        print(f"     - Bar chart: Shows two bars with values")
        print(f"  📄 Verify in: {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ Failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("  🧪 ZeroSite Image Page Data Linking Test")
    print("  Testing chart data is correctly linked and displayed")
    print("=" * 70)
    
    os.makedirs('/home/user/webapp/temp', exist_ok=True)
    
    results = []
    results.append(("M4 Chart Labels (Delta Fix)", test_m4_chart_labels()))
    results.append(("M5 Zero Value Handling", test_m5_zero_value_charts()))
    results.append(("M5 Normal Data Charts", test_m5_normal_data_charts()))
    results.append(("M6 Radar Chart Keys", test_m6_radar_chart_correct_keys()))
    
    print()
    print("=" * 70)
    print("  📊 Test Summary")
    print("=" * 70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print()
    print(f"  Result: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print()
        print("  🎉 All chart data linking tests passed!")
        print()
        print("  Generated files:")
        print("    - TEST_M4_CHART_LABELS.pdf (verify bar chart labels)")
        print("    - TEST_M5_ZERO_VALUES.pdf (verify N/A handling)")
        print("    - TEST_M5_NORMAL_DATA.pdf (verify normal charts)")
        print("    - TEST_M6_RADAR_CORRECT.pdf (verify 4 categories)")
        print()
        print("  🔍 Manual Verification Required:")
        print("    1. Open each PDF and check the charts")
        print("    2. Verify M4 shows '법정 기준' and '법정 대비 +X'")
        print("    3. Verify M5 zero-value charts show 'N/A' messages")
        print("    4. Verify M6 radar has 4 spokes (not 5)")
    else:
        print()
        print("  ⚠️ Some tests failed. Check logs above for details.")
        sys.exit(1)
