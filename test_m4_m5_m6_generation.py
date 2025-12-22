#!/usr/bin/env python3
"""
Enhanced M4-M5-M6 PDF Generation Test
Tests with complete data required by DataContract validation
"""

import sys
import os
sys.path.insert(0, '/home/user/webapp')

from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator

def test_m4_complete():
    """Test M4 PDF generation with complete data"""
    print("\n🧪 Testing M4 (Building Capacity Analysis)...")
    generator = ModulePDFGenerator()
    
    # Complete M4 data structure matching validation requirements
    test_data = {
        "selected_scenario_id": "scenario_A",
        "legal_capacity": {
            "far_max": 200.0,
            "bcr_max": 60.0,
            "total_units": 20,
            "gross_floor_area": 1500.0,
            "site_area": 750.0,
            "buildable_area": 450.0
        },
        "incentive_capacity": {
            "far_max": 260.0,
            "total_units": 26,
            "additional_far": 60.0,
            "public_contribution": "청년 주택"
        },
        "parking": {
            "required": 20,
            "alt_a": {
                "solution": "B3 + 기계식",
                "count": 18,
                "cost": 8100000000,
                "ramp_feasible": False
            },
            "alt_b": {
                "solution": "B2 자주식",
                "count": 20,
                "cost": 5100000000,
                "ramp_feasible": True
            }
        },
        "scenarios": [
            {
                "id": "scenario_A",
                "name": "Option A (FAR 최대화)",
                "units": 26,
                "far": 260.0,
                "gfa_m2": 1950.0,
                "parking_solution": "B3 + 기계식",
                "parking_cost": 8100000000,
                "description": "용적률 최대, 주차비 높음"
            },
            {
                "id": "scenario_B",
                "name": "Option B (주차 우선)",
                "units": 20,
                "far": 200.0,
                "gfa_m2": 1500.0,
                "parking_solution": "B2 자주식",
                "parking_cost": 5100000000,
                "description": "주차 편의 우선"
            }
        ],
        "gfa_breakdown": {
            "private_area": 1200.0,
            "common_area": 250.0,
            "mechanical_area": 50.0,
            "total": 1500.0
        }
    }
    
    try:
        pdf_bytes = generator.generate_m4_capacity_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M4_완전한_데이터.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M4 PDF generated: {len(pdf_bytes):,} bytes")
        print(f"  📄 Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ M4 generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_m5_complete():
    """Test M5 PDF generation with complete data"""
    print("\n🧪 Testing M5 (Feasibility Analysis)...")
    generator = ModulePDFGenerator()
    
    # Complete M5 data structure
    test_data = {
        "household_count": 20,
        "avg_unit_area_m2": 59.0,
        "lh_unit_price": 320000000,
        "regional_coefficient": 1.2,
        "costs": {
            "land": 50000000000,
            "construction": 30000000000,
            "design": 1200000000,  # 4% of construction
            "permit": 300000000,    # 1% of construction
            "finance": 2700000000,  # 6% * 18mo * (land+construction)
            "other": 1500000000,     # 5% of construction
            "total": 85700000000
        },
        "scenarios": [
            {
                "id": "scenario_A",
                "name": "Option A (FAR 최대)",
                "units": 26,
                "lh_price": 99840000000,  # 320M * 26 * 1.2
                "total_cost": 90000000000,
                "profit": 9840000000,
                "profit_margin": 10.9
            },
            {
                "id": "scenario_B",
                "name": "Option B (주차 우선)",
                "units": 20,
                "lh_price": 76800000000,  # 320M * 20 * 1.2
                "total_cost": 85700000000,
                "profit": -8900000000,
                "profit_margin": -10.4
            }
        ],
        "lh_purchase_price": 99840000000,
        "expected_profit": 9840000000,
        "profit_margin": 10.9,
        "m5_total_score": 75,
        "best_scenario": "scenario_A"
    }
    
    try:
        pdf_bytes = generator.generate_m5_feasibility_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M5_완전한_데이터.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M5 PDF generated: {len(pdf_bytes):,} bytes")
        print(f"  📄 Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ M5 generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_m6_complete():
    """Test M6 PDF generation with complete data"""
    print("\n🧪 Testing M6 (LH Review Prediction)...")
    generator = ModulePDFGenerator()
    
    # Complete M6 data structure with consistent values
    test_data = {
        "m5_score": 75,
        "m6_score": 85,
        "total_score": 85,  # Must be consistent with m6_score
        "approval_rate": 77.3,
        "grade": "A",
        "decision": "GO",
        "scores": {
            "location": 18,
            "scale": 14,
            "parking": 15,
            "facilities": 8,
            "community": 9,
            "eco_friendly": 7,
            "stability": 9,
            "other": 5
        },
        "hard_fail_items": [
            {"name": "용적률", "passed": True, "value": "240% (법정 250%)"},
            {"name": "주차", "passed": True, "value": "1.2대/세대"},
            {"name": "일조권", "passed": True, "value": "3시간"},
            {"name": "층수", "passed": True, "value": "20층"},
            {"name": "구조", "passed": True, "value": "내진 적용"}
        ],
        "conditional_scenarios": [
            {
                "issue": "주차 부족",
                "option_a": {
                    "action": "세대수 10% 감소",
                    "m5_impact": "수익 30억 감소",
                    "m6_impact": "Hard Fail 해결"
                },
                "option_b": {
                    "action": "지하 1개층 추가",
                    "m5_impact": "주차비용 20억 증가",
                    "m6_impact": "Hard Fail 해결, 주차 점수 유지"
                },
                "recommendation": "Option B (수익 손실 최소화)"
            }
        ]
    }
    
    try:
        pdf_bytes = generator.generate_m6_lh_review_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M6_완전한_데이터.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M6 PDF generated: {len(pdf_bytes):,} bytes")
        print(f"  📄 Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"  ❌ M6 generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_m4_partial_data():
    """Test M4 with partial data (should generate with warnings)"""
    print("\n🧪 Testing M4 with partial data (validation relaxed)...")
    generator = ModulePDFGenerator()
    
    test_data = {
        "selected_scenario_id": "default",
        "legal_capacity": {
            "far_max": 200.0,
            "bcr_max": 60.0,
            "total_units": 0,  # This should show as "N/A (검증 필요)"
            "gross_floor_area": 0
        },
        "scenarios": [
            {
                "id": "default",
                "name": "기본 시나리오",
                "units": 20,
                "far": 200.0
            }
        ]
    }
    
    try:
        pdf_bytes = generator.generate_m4_capacity_pdf(test_data)
        
        output_path = '/home/user/webapp/temp/TEST_M4_부분_데이터.pdf'
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"  ✅ M4 PDF generated with warnings: {len(pdf_bytes):,} bytes")
        print(f"  📄 Saved to: {output_path}")
        print(f"  ⚠️ Check PDF for 'N/A (검증 필요)' messages")
        return True
    except Exception as e:
        print(f"  ❌ M4 generation failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 70)
    print("  🧪 ZeroSite M4-M5-M6 Enhanced PDF Generation Test")
    print("  Testing with complete data and validation fixes")
    print("=" * 70)
    
    os.makedirs('/home/user/webapp/temp', exist_ok=True)
    
    results = []
    results.append(("M4 (완전한 데이터)", test_m4_complete()))
    results.append(("M5 (완전한 데이터)", test_m5_complete()))
    results.append(("M6 (완전한 데이터)", test_m6_complete()))
    results.append(("M4 (부분 데이터)", test_m4_partial_data()))
    
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
        print("  🎉 All tests passed successfully!")
        print()
        print("  Generated files:")
        print("    - TEST_M4_완전한_데이터.pdf")
        print("    - TEST_M5_완전한_데이터.pdf")
        print("    - TEST_M6_완전한_데이터.pdf")
        print("    - TEST_M4_부분_데이터.pdf (with warnings)")
    else:
        print()
        print("  ⚠️ Some tests failed. Check logs above for details.")
        sys.exit(1)
