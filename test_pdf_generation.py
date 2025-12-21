#!/usr/bin/env python3
"""
PDF Generation Test Script
Tests all module PDF generators (M2-M6)
"""

import sys
import os
sys.path.insert(0, '/home/user/webapp')

from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator

def test_m2_pdf():
    """Test M2 PDF generation"""
    generator = ModulePDFGenerator()
    
    test_data = {
        "appraisal": {
            "land_value": 1621848717,
            "unit_price_sqm": 3243697,
            "unit_price_pyeong": 10723014
        },
        "official_price": {
            "total": 500000000,
            "per_sqm": 1000000
        },
        "transactions": {
            "count": 10,
            "avg_price_sqm": 3243697,
            "samples": [
                {
                    "address": "서울 마포구 논현동 482-54",
                    "date": "2024-01-23",
                    "price_sqm": 3400805,
                    "distance_km": 0.5
                }
            ]
        },
        "premium": {
            "scores": {"road": 4, "terrain": 10, "location": 7, "accessibility": 7},
            "premiums": {"distance": 0.05, "time": 0.03, "zone": 0.04, "size": 0.03, "total_rate": 15.0}
        },
        "confidence": {
            "score": 0.85,
            "level": "HIGH"
        }
    }
    
    pdf_bytes = generator.generate_m2_appraisal_pdf(test_data)
    
    with open('/home/user/webapp/temp/TEST_M2_토지감정평가.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ M2 PDF generated: {len(pdf_bytes)} bytes")
    return len(pdf_bytes) > 0

def test_m4_pdf():
    """Test M4 PDF generation"""
    generator = ModulePDFGenerator()
    
    test_data = {
        "legal_capacity": {
            "far_max": 200.0,
            "bcr_max": 60.0,
            "total_units": 20,
            "gross_floor_area": 1000.0
        },
        "incentive_capacity": {
            "far_max": 260.0,
            "total_units": 26
        },
        "parking": {
            "alt_a": 15,
            "alt_b": 18
        }
    }
    
    pdf_bytes = generator.generate_m4_capacity_pdf(test_data)
    
    with open('/home/user/webapp/temp/TEST_M4_건축규모분석.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ M4 PDF generated: {len(pdf_bytes)} bytes")
    return len(pdf_bytes) > 0

def test_m5_pdf():
    """Test M5 PDF generation"""
    generator = ModulePDFGenerator()
    
    test_data = {
        "financial": {
            "npv_public": 793000000,
            "irr": 12.8,
            "profitability_rate": 15.5
        },
        "costs": {
            "land": 500000000,
            "construction": 300000000,
            "other": 50000000,
            "total": 850000000
        },
        "revenues": {
            "sale": 1200000000,
            "rental": 100000000,
            "other": 50000000,
            "total": 1350000000
        }
    }
    
    pdf_bytes = generator.generate_m5_feasibility_pdf(test_data)
    
    with open('/home/user/webapp/temp/TEST_M5_사업성분석.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ M5 PDF generated: {len(pdf_bytes)} bytes")
    return len(pdf_bytes) > 0

def test_m6_pdf():
    """Test M6 PDF generation"""
    generator = ModulePDFGenerator()
    
    test_data = {
        "decision": {
            "type": "GO",
            "rationale": "입지 우수, 사업성 양호, LH 선호 유형 적합"
        },
        "grade": "A",
        "total_score": 85.0,
        "approval_probability": 0.77,
        "scores": {
            "location": 25.0,
            "feasibility": 20.0,
            "demand": 15.0,
            "capacity": 15.0,
            "other": 10.0
        }
    }
    
    pdf_bytes = generator.generate_m6_lh_review_pdf(test_data)
    
    with open('/home/user/webapp/temp/TEST_M6_LH심사예측.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ M6 PDF generated: {len(pdf_bytes)} bytes")
    return len(pdf_bytes) > 0

if __name__ == '__main__':
    print("🧪 Testing PDF Generation...")
    print()
    
    os.makedirs('/home/user/webapp/temp', exist_ok=True)
    
    results = []
    results.append(("M2 토지감정평가", test_m2_pdf()))
    results.append(("M4 건축규모분석", test_m4_pdf()))
    results.append(("M5 사업성분석", test_m5_pdf()))
    results.append(("M6 LH심사예측", test_m6_pdf()))
    
    print()
    print("=" * 50)
    print("📊 Test Results:")
    print("=" * 50)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print()
        print("🎉 All PDF generation tests passed!")
        print()
        print("Generated PDF files:")
        print("  - /home/user/webapp/temp/TEST_M2_토지감정평가.pdf")
        print("  - /home/user/webapp/temp/TEST_M4_건축규모분석.pdf")
        print("  - /home/user/webapp/temp/TEST_M5_사업성분석.pdf")
        print("  - /home/user/webapp/temp/TEST_M6_LH심사예측.pdf")
    else:
        print()
        print("⚠️ Some tests failed!")
        sys.exit(1)
