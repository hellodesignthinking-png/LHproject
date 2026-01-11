#!/usr/bin/env python3
"""
ZeroSite DATA SUFFICIENT Test
==============================
실제 데이터가 입력되었을 때 정상 분석 흐름으로 전환되는지 테스트

Author: ZeroSite Development Team
Date: 2026-01-11
"""

import requests
import json
import sys

BASE_URL = "http://localhost:49999"

def test_data_sufficient():
    """실제 데이터 입력 시나리오 테스트"""
    
    print("=" * 80)
    print("🧪 ZeroSite DATA SUFFICIENT Test")
    print("=" * 80)
    
    # Test Case 1: 기존 PNU (실제 데이터 있음)
    test_cases = [
        {
            "name": "서울 강남 역삼동 (실제 데이터)",
            "parcel_id": "1168010100005200012",
            "address": "서울특별시 강남구 역삼동 123-45",
            "expected": "ANALYSIS_SUCCESS"
        },
        {
            "name": "서울 송파 잠실동 (Mock 데이터)",
            "parcel_id": "1171010100001234567",
            "address": "서울시 송파구 잠실동 123-45",
            "expected": "ANALYSIS_SUCCESS"
        }
    ]
    
    for idx, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {idx}: {case['name']}")
        print(f"   PNU: {case['parcel_id']}")
        print(f"   주소: {case['address']}")
        print(f"   기대 결과: {case['expected']}")
        print("-" * 80)
        
        # 1) Run pipeline
        print("   ▶ Pipeline 실행 중...")
        pipeline_url = f"{BASE_URL}/api/v4/pipeline/analyze"
        pipeline_payload = {
            "parcel_id": case["parcel_id"],
            "address": case["address"]
        }
        
        response = requests.post(pipeline_url, json=pipeline_payload)
        print(f"   Pipeline 상태: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Pipeline 실행 실패: {response.text}")
            continue
        
        pipeline_result = response.json()
        context_id = pipeline_result.get("analysis_id") or pipeline_result.get("context_id")
        
        if not context_id:
            print(f"   ❌ Context ID를 가져올 수 없습니다: {pipeline_result}")
            continue
        
        print(f"   Context ID: {context_id}")
        
        # 2) Get M4 report
        print(f"   ▶ M4 보고서 조회 중...")
        report_url = f"{BASE_URL}/api/v4/reports/M4/html?context_id={context_id}"
        
        response = requests.get(report_url)
        print(f"   M4 보고서 상태: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ M4 보고서 조회 실패")
            continue
        
        html_content = response.text
        
        # 3) Check report type
        if "DATA INSUFFICIENT" in html_content or "데이터 부족" in html_content:
            print(f"   ⚠️  결과: DATA INSUFFICIENT 템플릿 사용")
            print(f"   📊 MDS 상태 확인:")
            
            # Extract MDS requirements if available
            if "mds_requirements" in html_content or "필수 입력 항목" in html_content:
                print(f"      - 사업지 주소: ✅/❌")
                print(f"      - 토지면적: ✅/❌")
                print(f"      - 용도지역: ✅/❌")
                print(f"      - M3 공급유형: ✅/❌")
        else:
            print(f"   ✅ 결과: 정상 분석 보고서 생성")
            
            # Check key sections
            key_sections = [
                ("법적 건축 가능 범위", "legal_framework"),
                ("시나리오 분석", "scenario"),
                ("최종 판단", "final_decision"),
                ("M3 공급유형 연계", "m3_linkage")
            ]
            
            print(f"   📊 보고서 섹션 체크:")
            for section_name, section_key in key_sections:
                if section_key in html_content or section_name in html_content:
                    print(f"      ✅ {section_name}")
                else:
                    print(f"      ❌ {section_name} (누락)")
        
        print(f"   🔗 보고서 URL: {report_url}")
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_data_sufficient()
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {e}")
        sys.exit(1)
