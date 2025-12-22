#!/usr/bin/env python3
"""
Diagnose data flow issue causing 0원 problem
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_data_flow():
    """Test complete data flow from frontend to report"""
    
    # Test payload with ALL required fields
    payload = {
        "address": "서울특별시 강남구 테헤란로 152",
        "land_area": 1500.0,
        "unit_type": "청년",
        "zone_type": "제2종일반주거지역",
        "land_appraisal_price": 5500000,  # 550만원/㎡
        "report_mode": "ultra_v8_5",
        "building_coverage_ratio": 0.6,  # 60%
        "floor_area_ratio": 2.0,  # 200%
        "expected_units": 78  # 50+ → LH_LINKED
    }
    
    print("=" * 80)
    print("DATA FLOW DIAGNOSIS")
    print("=" * 80)
    
    # Call analyze
    print("\n[TEST] Calling /api/analyze with 78 households...")
    response = requests.post(f"{API_BASE}/api/analyze", json=payload)
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        print(response.text[:500])
        return
    
    data = response.json()
    
    # Check financial_result
    financial = data.get('financial_result', {})
    
    print("\n[FINANCIAL ENGINE OUTPUT]")
    print("-" * 80)
    print(f"Analysis Mode: {financial.get('analysis_mode')}")
    print(f"Expected Units: {financial.get('expected_units')}")
    print(f"Land Appraisal: {financial.get('land_appraisal', 0):,.0f}원")
    print(f"Verified Cost: {financial.get('total_verified_cost', 0):,.0f}원")
    print(f"LH Purchase Price: {financial.get('lh_purchase_price', 0):,.0f}원")
    print(f"Total Project Cost: {financial.get('total_project_cost', 0):,.0f}원")
    print(f"ROI: {financial.get('roi', 0):.2f}%")
    print(f"Rating: {financial.get('project_rating')}")
    print(f"Decision: {financial.get('decision')}")
    
    # Check if mode is correct
    mode_correct = financial.get('analysis_mode') == 'LH_LINKED' and financial.get('expected_units', 0) >= 50
    
    # Check if values are zero
    values_zero = (
        financial.get('land_appraisal', 0) == 0 or
        financial.get('total_verified_cost', 0) == 0 or
        financial.get('lh_purchase_price', 0) == 0
    )
    
    print("\n[DIAGNOSIS]")
    print("-" * 80)
    print(f"Mode Correct (78 ≥ 50 → LH_LINKED): {'✅ YES' if mode_correct else '❌ NO'}")
    print(f"Zero Values Found: {'❌ YES - PROBLEM!' if values_zero else '✅ NO - OK'}")
    
    # Check report chapters
    chapters = data.get('report_data', {}).get('chapters', [])
    ch1 = next((ch for ch in chapters if ch.get('chapter_number') == 1), None)
    ch6 = next((ch for ch in chapters if ch.get('chapter_number') == 6), None)
    
    if ch1:
        content1 = ch1.get('content', '')
        has_zero_in_ch1 = '0원' in content1 or '0.00%' in content1
        print(f"CH.1 Contains '0원': {'❌ YES - PROBLEM!' if has_zero_in_ch1 else '✅ NO - OK'}")
        
        # Extract actual values from CH.1
        if 'ROI:' in content1:
            import re
            roi_match = re.search(r'ROI:\s*\*\*(-?\d+\.?\d*)%', content1)
            if roi_match:
                ch1_roi = float(roi_match.group(1))
                print(f"CH.1 ROI Display: {ch1_roi:.2f}%")
    
    if ch6:
        content6 = ch6.get('content', '')
        has_zero_in_ch6 = '0원' in content6
        print(f"CH.6 Contains '0원': {'❌ YES - PROBLEM!' if has_zero_in_ch6 else '✅ NO - OK'}")
    
    print("\n" + "=" * 80)
    
    if values_zero:
        print("❌ CRITICAL: Financial engine returning ZERO values")
        print("   → Check: gross_floor_area, official_land_price calculation")
    elif not mode_correct:
        print("❌ ERROR: Mode determination logic broken (78 units → should be LH_LINKED)")
    else:
        print("✅ Data flow appears correct")
    
    return data

if __name__ == "__main__":
    test_data_flow()
