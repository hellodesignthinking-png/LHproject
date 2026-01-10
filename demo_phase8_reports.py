#!/usr/bin/env python3
"""
Phase 8 보고서 데모 스크립트
실제 파이프라인 결과로 풍부한 보고서 생성 데모
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:49999"

def demo_phase8_reports():
    """Phase 8 보고서 생성 데모"""
    
    print("=" * 70)
    print("Phase 8 보고서 생성 데모")
    print("=" * 70)
    
    # Step 1: 주소 검색
    print("\n1️⃣ 주소 검색...")
    address_response = requests.post(
        f"{BASE_URL}/api/m1/address/search",
        json={"query": "서울특별시 강남구 역삼동 123-45"}
    )
    
    if address_response.status_code != 200:
        print(f"❌ 주소 검색 실패: {address_response.status_code}")
        return
    
    address_data = address_response.json()
    print(f"✅ 주소 검색 완료")
    print(f"   - PNU: {address_data.get('pnu', 'N/A')}")
    
    # Step 2: Context 생성 (Freeze)
    print("\n2️⃣ Context 생성...")
    freeze_response = requests.post(
        f"{BASE_URL}/api/m1/freeze-context-v2",
        json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "pnu": address_data.get('pnu'),
            "coordinates": address_data.get('coordinates', [127.0, 37.5])
        }
    )
    
    if freeze_response.status_code != 200:
        print(f"❌ Context 생성 실패: {freeze_response.status_code}")
        return
    
    freeze_data = freeze_response.json()
    context_id = freeze_data.get('context_id')
    print(f"✅ Context 생성 완료: {context_id}")
    
    # Step 3: 파이프라인 실행 (M1-M6)
    print("\n3️⃣ 파이프라인 실행 (M1-M6)...")
    pipeline_response = requests.post(
        f"{BASE_URL}/api/v4/pipeline/analyze",
        json={
            "context_id": context_id,
            "modules": ["M2", "M3", "M4", "M5", "M6"]
        }
    )
    
    if pipeline_response.status_code != 200:
        print(f"❌ 파이프라인 실행 실패: {pipeline_response.status_code}")
        return
    
    print(f"✅ 파이프라인 실행 완료")
    
    # Wait for pipeline to complete
    time.sleep(2)
    
    # Step 4: 모듈별 보고서 생성 테스트
    print("\n4️⃣ Phase 8 보고서 생성 테스트")
    print("=" * 70)
    
    modules = ["M2", "M3", "M4", "M5", "M6"]
    results = {}
    
    for module in modules:
        print(f"\n📄 {module} 보고서 생성 중...")
        
        # Test HTML endpoint
        html_response = requests.get(
            f"{BASE_URL}/api/v4/reports/{module}/html",
            params={"context_id": context_id}
        )
        
        if html_response.status_code == 200:
            html_content = html_response.text
            
            # Check for Phase 8 enhancements
            checks = {
                "M2": ["CASE_001", "CASE_002", "거래사례", "가격 형성"],
                "M3": ["역세권", "생활편의", "라이프스타일"],
                "M4": ["주차", "대안", "비용"],
                "M5": ["IRR", "NPV", "민감도"],
                "M6": ["종합 판단", "추천", "A등급"]
            }
            
            found_items = []
            for check in checks.get(module, []):
                if check in html_content:
                    found_items.append(check)
            
            results[module] = {
                "status": "✅ SUCCESS",
                "size": len(html_content),
                "found": found_items
            }
            
            print(f"   ✅ 성공: {len(html_content)} chars")
            print(f"   발견된 항목: {', '.join(found_items)}")
            
        else:
            results[module] = {
                "status": f"❌ FAILED ({html_response.status_code})",
                "error": html_response.text[:200]
            }
            print(f"   ❌ 실패: {html_response.status_code}")
            print(f"   오류: {html_response.text[:200]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 결과 요약")
    print("=" * 70)
    
    for module, result in results.items():
        print(f"\n{module}: {result['status']}")
        if 'found' in result:
            print(f"  - 데이터 크기: {result['size']:,} chars")
            print(f"  - Phase 8 항목: {len(result['found'])}개")
    
    print("\n" + "=" * 70)
    print(f"✅ Context ID: {context_id}")
    print(f"🌐 브라우저에서 확인:")
    for module in modules:
        print(f"   - {module}: {BASE_URL}/api/v4/reports/{module}/html?context_id={context_id}")
    print("=" * 70)

if __name__ == "__main__":
    try:
        demo_phase8_reports()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
