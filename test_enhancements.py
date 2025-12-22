#!/usr/bin/env python3
"""
Test for v8.5 enhancements:
1. CH.9-10 restructuring
2. Location score consistency (CH.3 vs CH.9)
3. Location map placeholder
4. Evaluation matrix visualization
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_enhancements():
    """Test all enhancements"""
    
    payload = {
        "address": "서울특별시 강남구 테헤란로 152",
        "land_area": 1500.0,
        "unit_type": "청년",
        "zone_type": "제2종일반주거지역",
        "land_appraisal_price": 5500000,
        "report_mode": "ultra_v8_5",
        "expected_units": 60
    }
    
    print("=" * 80)
    print("V8.5 ENHANCEMENTS VERIFICATION TEST")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nTest Scope:")
    print("1. CH.3: Location map placeholder + Evaluation matrix visualization")
    print("2. CH.9: Enhanced decision framework with matrix")
    print("3. CH.10: 6-month action plan + preconditions")
    print("4. Location score consistency (CH.3 == CH.9)")
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
    
    # Get chapters
    chapters = data.get('report_data', {}).get('chapters', [])
    ch3 = next((ch for ch in chapters if ch.get('chapter_number') == 3), None)
    ch9 = next((ch for ch in chapters if ch.get('chapter_number') == 9), None)
    ch10 = next((ch for ch in chapters if ch.get('chapter_number') == 10), None)
    
    print("\n[STEP 2] Chapter 3 Verification:")
    print("-" * 80)
    
    if ch3:
        content3 = ch3.get('content', '')
        
        # Check location map placeholder
        has_map = '📍 대상지 주소' in content3 or '🗺️ 위치 지도' in content3 or 'Kakao Map' in content3
        print(f"  Location Map Placeholder:    {'✅ YES' if has_map else '❌ NO'}")
        
        # Check evaluation matrix visualization
        has_radar = '📈 시각화' in content3 or 'Radar Chart' in content3 or '레이더 차트' in content3
        has_heatmap = 'Heatmap' in content3 or '히트맵' in content3
        print(f"  Radar Chart Placeholder:     {'✅ YES' if has_radar else '❌ NO'}")
        print(f"  Heatmap Placeholder:         {'✅ YES' if has_heatmap else '❌ NO'}")
        
        # Extract location score from CH.3
        ch3_score = None
        for line in content3.split('\n'):
            if '종합 등급' in line and '점' in line:
                # Try to extract score
                import re
                match = re.search(r'(\d+)점', line)
                if match:
                    ch3_score = int(match.group(1))
                    break
        
        print(f"  CH.3 Location Score:         {ch3_score if ch3_score else 'N/A'}점")
    
    print("\n[STEP 3] Chapter 9 Verification:")
    print("-" * 80)
    
    if ch9:
        content9 = ch9.get('content', '')
        
        # Check enhanced decision framework
        has_process_diagram = '의사결정 프로세스 개요' in content9 or 'STEP 1' in content9
        has_matrix = '의사결정 매트릭스' in content9
        has_final_decision = '최종 의사결정' in content9 and '╔' in content9
        
        print(f"  Decision Process Diagram:    {'✅ YES' if has_process_diagram else '❌ NO'}")
        print(f"  Decision Matrix:             {'✅ YES' if has_matrix else '❌ NO'}")
        print(f"  Enhanced Final Decision Box: {'✅ YES' if has_final_decision else '❌ NO'}")
        
        # Extract location score from CH.9
        ch9_score = None
        for line in content9.split('\n'):
            if '종합 점수' in line and '점' in line:
                # Try to extract score
                import re
                match = re.search(r'(\d+\.?\d*)점', line)
                if match:
                    ch9_score = float(match.group(1))
                    break
        
        print(f"  CH.9 Location Score:         {ch9_score if ch9_score else 'N/A'}점")
        
        # Check consistency
        if ch3_score and ch9_score:
            consistent = abs(ch3_score - ch9_score) < 1.0
            print(f"  Score Consistency (CH.3==CH.9): {'✅ YES' if consistent else '❌ NO'}")
    
    print("\n[STEP 4] Chapter 10 Verification:")
    print("-" * 80)
    
    if ch10:
        content10 = ch10.get('content', '')
        
        # Check 6-month action plan
        has_timeline = '📅 Timeline Overview' in content10 or 'Month 1-2' in content10
        has_month_table = '| 주차 |' in content10 or 'Week 1-2' in content10
        has_preconditions = '전제조건' in content10 or '조건 1' in content10
        has_milestones = 'Milestone' in content10
        
        print(f"  6-Month Timeline:            {'✅ YES' if has_timeline else '❌ NO'}")
        print(f"  Monthly Task Tables:         {'✅ YES' if has_month_table else '❌ NO'}")
        print(f"  Preconditions Section:       {'✅ YES' if has_preconditions else '❌ NO'}")
        print(f"  Milestone Markers:           {'✅ YES' if has_milestones else '❌ NO'}")
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY:")
    print("=" * 80)
    
    all_checks = [
        has_map if ch3 else False,
        has_radar if ch3 else False,
        has_heatmap if ch3 else False,
        has_process_diagram if ch9 else False,
        has_matrix if ch9 else False,
        has_final_decision if ch9 else False,
        has_timeline if ch10 else False,
        has_month_table if ch10 else False,
        has_preconditions if ch10 else False,
        has_milestones if ch10 else False
    ]
    
    pass_count = sum(1 for check in all_checks if check)
    total_count = len(all_checks)
    
    if pass_count == total_count:
        print("🎉 ALL ENHANCEMENTS VERIFIED SUCCESSFULLY!")
        print(f"  ✅ CH.3: Location map + Evaluation matrix")
        print(f"  ✅ CH.9: Enhanced decision framework")
        print(f"  ✅ CH.10: 6-month action plan")
        if ch3_score and ch9_score and abs(ch3_score - ch9_score) < 1.0:
            print(f"  ✅ Location score consistency: {ch3_score}점 (CH.3) == {ch9_score}점 (CH.9)")
    else:
        print(f"⚠️ PARTIAL SUCCESS: {pass_count}/{total_count} checks passed")
    
    print("\n" + "=" * 80)
    
    return analysis_id

if __name__ == "__main__":
    test_enhancements()
