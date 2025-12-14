"""
ZeroSite v40.6 Quick Validation Test
감정평가 기준축 정합성 검증

Purpose: Verify that all modules correctly use Appraisal as the single source of truth

Created: 2025-12-14
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_v40_6_integrity():
    """Run v40.6 integrity tests"""
    
    print_header("ZeroSite v40.6 Quick Validation Test")
    
    # Step 1: Create context
    print("\n[1/5] Creating analysis context...")
    response = requests.post(
        f"{BASE_URL}/api/v40.2/run-analysis",
        json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area_sqm": 991.74
        },
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"❌ Context creation failed: {response.status_code}")
        return False
    
    context_id = response.json()["context_id"]
    print(f"✅ Context created: {context_id[:16]}...")
    
    # Step 2: Verify Appraisal Context Structure
    print("\n[2/5] Verifying Appraisal Context Structure...")
    appr_resp = requests.get(f"{BASE_URL}/api/v40.2/context/{context_id}/appraisal")
    appraisal = appr_resp.json()["data"]
    
    required_fields = ["adjustment_logic", "transaction_summary_text", "premium_explanation"]
    has_all_fields = all(f in appraisal for f in required_fields)
    
    if has_all_fields:
        print("✅ All v40.6 appraisal fields present:")
        print(f"   - adjustment_logic: {list(appraisal['adjustment_logic'].keys())}")
        print(f"   - transaction_summary_text: {len(appraisal['transaction_summary_text'])} chars")
        print(f"   - premium_explanation: {len(appraisal['premium_explanation'])} chars")
    else:
        print("❌ Missing appraisal fields")
        return False
    
    # Step 3: Run LH Review
    print("\n[3/5] Running LH Review...")
    lh_resp = requests.post(
        f"{BASE_URL}/api/v40/lh-review/predict",
        json={
            "context_id": context_id,
            "housing_type": "청년",
            "target_units": 100
        },
        timeout=30
    )
    
    if lh_resp.status_code != 200:
        print(f"❌ LH Review failed: {lh_resp.status_code}")
        return False
    
    lh_result = lh_resp.json()
    print(f"✅ LH Review completed:")
    print(f"   - Score: {lh_result['predicted_score']}/100")
    print(f"   - Pass Probability: {lh_result['pass_probability']}%")
    print(f"   - Risk Level: {lh_result['risk_level']}")
    
    # Step 4: Test Report Generation (Landowner Brief)
    print("\n[4/5] Testing Report Generation...")
    report_resp = requests.get(
        f"{BASE_URL}/api/v40.2/reports/{context_id}/landowner_brief",
        timeout=30
    )
    
    if report_resp.status_code != 200:
        print(f"❌ Report generation failed: {report_resp.status_code}")
        return False
    
    pdf_size = len(report_resp.content)
    print(f"✅ Report generated successfully:")
    print(f"   - PDF Size: {pdf_size/1024:.1f} KB")
    
    # Step 5: Verify Data Consistency
    print("\n[5/5] Verifying Data Consistency...")
    
    # Get diagnosis and capacity to verify they use appraisal data
    diagnosis_resp = requests.get(f"{BASE_URL}/api/v40.2/context/{context_id}/diagnosis")
    diagnosis = diagnosis_resp.json()["data"]
    
    # Check that diagnosis uses appraisal's official_price
    appr_official_price = appraisal.get("official_price", 0)
    diag_official_price = diagnosis.get("official_price", 0)
    
    if appr_official_price == diag_official_price:
        print(f"✅ Diagnosis uses Appraisal official_price: {appr_official_price:,.0f}")
    else:
        print(f"❌ Data inconsistency:")
        print(f"   Appraisal: {appr_official_price:,.0f}")
        print(f"   Diagnosis: {diag_official_price:,.0f}")
        return False
    
    # Check zoning consistency
    appr_zone = appraisal.get("zoning", {}).get("zone_type", "")
    diag_zone = diagnosis.get("zone_type", "")
    
    if appr_zone == diag_zone:
        print(f"✅ Zoning consistent: {appr_zone}")
    else:
        print(f"❌ Zoning inconsistency:")
        print(f"   Appraisal: {appr_zone}")
        print(f"   Diagnosis: {diag_zone}")
        return False
    
    # Final Summary
    print_header("✅ v40.6 VALIDATION COMPLETE")
    print("""
All integrity checks passed:
1. ✅ Appraisal Context Structure (3 new fields)
2. ✅ LH Review Execution
3. ✅ Report Generation
4. ✅ Data Consistency (official_price, zoning)

v40.6 Status: PASS
감정평가 기준축: 정상 작동
""")
    
    return True

if __name__ == "__main__":
    try:
        success = test_v40_6_integrity()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        exit(1)
