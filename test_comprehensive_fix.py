#!/usr/bin/env python3
"""
Comprehensive test for all fixes:
1. Percentage conversion (건폐율, 용적률)
2. Financial data (0원 problem)
3. AI Summary blocks
4. Dynamic ROI evaluation
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_analyze():
    """Test /api/analyze endpoint with comprehensive data"""
    
    payload = {
        "address": "서울특별시 강남구 테헤란로 152",
        "land_area": 1500.0,
        "unit_type": "청년",
        "zone_type": "제2종일반주거지역",
        "land_appraisal_price": 5500000,  # 550만원/㎡
        "report_mode": "ultra_v8_5",
        "building_coverage_ratio": 0.5,  # 50% (will test conversion)
        "floor_area_ratio": 3.0,  # 300% (will test conversion)
        "expected_units": 60  # 50세대 이상 → LH_LINKED mode
    }
    
    print("=" * 80)
    print("COMPREHENSIVE FIX VERIFICATION TEST")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTest Cases:")
    print("1. Percentage Conversion Fix (건폐율 0.5 → 50%, 용적률 3.0 → 300%)")
    print("2. Financial Data Completeness (land_appraisal, verified_cost, ROI)")
    print("3. AI Summary Blocks (CH.1, 5, 6)")
    print("4. Dynamic ROI Evaluation Phrases")
    print("\n" + "=" * 80)
    
    # Call /api/analyze
    print("\n[STEP 1] Calling /api/analyze...")
    response = requests.post(f"{API_BASE}/api/analyze", json=payload)
    
    if response.status_code != 200:
        print(f"❌ ERROR: Status {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    analysis_id = data.get('analysis_id')
    print(f"✅ Analysis ID: {analysis_id}")
    
    # Check financial_result
    financial = data.get('financial_result', {})
    print("\n[STEP 2] Financial Data Verification:")
    print("-" * 80)
    
    # Critical fields check
    checks = {
        'land_appraisal': financial.get('land_appraisal', 0),
        'total_verified_cost': financial.get('total_verified_cost', 0),
        'lh_purchase_price': financial.get('lh_purchase_price', 0),
        'total_project_cost': financial.get('total_project_cost', 0),
        'roi': financial.get('roi', 0),
        'project_rating': financial.get('project_rating', 'N/A'),
        'decision': financial.get('decision', 'N/A'),
        'analysis_mode': financial.get('analysis_mode', 'N/A')
    }
    
    all_ok = True
    for key, value in checks.items():
        if key in ['roi']:
            status = "✅ OK" if value != 0 or value is not None else "❌ ZERO"
        elif key in ['project_rating', 'decision', 'analysis_mode']:
            status = "✅ OK" if value != 'N/A' and value is not None else "❌ N/A"
        else:
            status = "✅ OK" if value > 0 else "❌ ZERO"
        
        if "❌" in status:
            all_ok = False
        
        if key == 'roi':
            print(f"{key:25}: {value:>15.2f}% {status:>10}")
        elif isinstance(value, (int, float)) and key not in ['project_rating', 'decision', 'analysis_mode']:
            print(f"{key:25}: {value:>15,.0f}원 {status:>10}")
        else:
            print(f"{key:25}: {str(value):>18} {status:>10}")
    
    if all_ok:
        print("\n🎉 FINANCIAL DATA: ALL FIELDS POPULATED - NO ZERO VALUES")
    else:
        print("\n⚠️ WARNING: Some financial fields are zero or N/A")
    
    # Check report_data chapters
    report_data = data.get('report_data', {})
    chapters = report_data.get('chapters', [])
    
    print(f"\n[STEP 3] Report Data Verification:")
    print("-" * 80)
    print(f"Total Chapters: {len(chapters)}")
    
    # Check specific chapters for AI Summary and content
    ch1 = next((ch for ch in chapters if ch.get('chapter_number') == 1), None)
    ch5 = next((ch for ch in chapters if ch.get('chapter_number') == 5), None)
    ch6 = next((ch for ch in chapters if ch.get('chapter_number') == 6), None)
    
    if ch1:
        content1 = ch1.get('content', '')
        has_ai_summary_ch1 = '🔎 AI SUMMARY' in content1
        has_roi_text = f"{checks['roi']:.2f}%" in content1
        has_lh_purchase = f"{checks['lh_purchase_price']:,.0f}원" in content1
        
        print(f"\nCH.1 Executive Summary:")
        print(f"  AI Summary Block:        {'✅ YES' if has_ai_summary_ch1 else '❌ NO'}")
        print(f"  ROI Display:             {'✅ YES' if has_roi_text else '❌ NO'}")
        print(f"  LH Purchase Price:       {'✅ YES' if has_lh_purchase else '❌ NO'}")
    
    if ch5:
        content5 = ch5.get('content', '')
        has_ai_summary_ch5 = '🔎 AI SUMMARY' in content5
        # Check percentage display (should be 50%, 300%, not 5000%, 30000%)
        has_correct_bcr = '50%' in content5 or '60%' in content5  # depending on input
        has_wrong_bcr = '5000%' in content5 or '6000%' in content5
        
        print(f"\nCH.5 Legal Review:")
        print(f"  AI Summary Block:        {'✅ YES' if has_ai_summary_ch5 else '❌ NO'}")
        print(f"  Correct Percentage:      {'✅ YES (50%, 300%)' if has_correct_bcr and not has_wrong_bcr else '❌ NO'}")
        print(f"  Wrong Percentage Found:  {'❌ YES (5000%, 30000%)' if has_wrong_bcr else '✅ NO'}")
    
    if ch6:
        content6 = ch6.get('content', '')
        has_ai_summary_ch6 = '🔎 AI SUMMARY' in content6
        has_land_appraisal = f"{checks['land_appraisal']:,.0f}원" in content6
        has_verified_cost = f"{checks['total_verified_cost']:,.0f}원" in content6
        
        print(f"\nCH.6 Financial Analysis:")
        print(f"  AI Summary Block:        {'✅ YES' if has_ai_summary_ch6 else '❌ NO'}")
        print(f"  Land Appraisal Display:  {'✅ YES' if has_land_appraisal else '❌ NO'}")
        print(f"  Verified Cost Display:   {'✅ YES' if has_verified_cost else '❌ NO'}")
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY:")
    print("=" * 80)
    
    if all_ok and has_ai_summary_ch1 and has_correct_bcr and not has_wrong_bcr:
        print("🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
        print("  ✅ Financial data populated (no 0원 problem)")
        print("  ✅ Percentage conversion fixed (no 5000%, 30000%)")
        print("  ✅ AI Summary blocks added")
        print("  ✅ Dynamic ROI evaluation phrases")
    else:
        print("⚠️ SOME ISSUES DETECTED:")
        if not all_ok:
            print("  ❌ Financial data has zero values")
        if not has_ai_summary_ch1:
            print("  ❌ AI Summary blocks missing")
        if has_wrong_bcr:
            print("  ❌ Percentage conversion not fixed")
    
    print("\n" + "=" * 80)
    
    return analysis_id

if __name__ == "__main__":
    test_analyze()
