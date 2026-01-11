#!/usr/bin/env python3
"""
ZeroSite M5 DATA NOT LOADED Test
==================================
M5 사업성 분석 모듈의 데이터 로딩 검증 테스트

Author: ZeroSite Development Team
Date: 2026-01-11
"""

import requests
import json
import sys

BASE_URL = "http://localhost:49999"

def test_m5_data_not_loaded():
    """M5 DATA NOT LOADED 시나리오 테스트"""
    
    print("=" * 80)
    print("🧪 ZeroSite M5 DATA NOT LOADED Test")
    print("=" * 80)
    
    # Test Case 1: 정상 데이터 (M4 연계 성공)
    print("\n📝 Test Case 1: 정상 데이터 (M4 연계)")
    print("-" * 80)
    
    context_id_success = "1168010100005200012"
    
    print(f"   ▶ M5 보고서 조회 중... (Context: {context_id_success})")
    report_url = f"{BASE_URL}/api/v4/reports/M5/html?context_id={context_id_success}"
    
    response = requests.get(report_url)
    print(f"   M5 보고서 상태: {response.status_code}")
    
    if response.status_code == 200:
        html_content = response.text
        
        if "DATA NOT LOADED" in html_content:
            print(f"   ⚠️  결과: DATA NOT LOADED 템플릿 사용")
            print(f"   ❌ 예상과 다름: 정상 데이터임에도 DATA NOT LOADED")
        else:
            print(f"   ✅ 결과: 정상 분석 보고서 생성")
            
            # Check key sections
            key_sections = [
                "NPV",
                "IRR",
                "ROI",
                "사업성 등급"
            ]
            
            print(f"   📊 보고서 섹션 체크:")
            for section in key_sections:
                if section in html_content:
                    print(f"      ✅ {section}")
                else:
                    print(f"      ❌ {section} (누락)")
    else:
        print(f"   ❌ M5 보고서 조회 실패")
    
    print(f"   🔗 보고서 URL: {report_url}")
    
    # Test Case 2: DATA NOT LOADED (M4 연계 실패)
    print("\n📝 Test Case 2: DATA NOT LOADED (M4 데이터 없음)")
    print("-" * 80)
    
    context_id_fail = "TEST_M5_NO_M4_DATA"
    
    print(f"   ▶ 테스트 Context 생성 중... (Context: {context_id_fail})")
    
    # 파이프라인 없이 직접 M5 보고서 요청
    report_url_fail = f"{BASE_URL}/api/v4/reports/M5/html?context_id={context_id_fail}"
    
    response = requests.get(report_url_fail)
    print(f"   M5 보고서 상태: {response.status_code}")
    
    if response.status_code == 200:
        html_content = response.text
        
        if "DATA NOT LOADED" in html_content:
            print(f"   ✅ 결과: DATA NOT LOADED 템플릿 정상 작동")
            
            # Check required elements
            required_elements = [
                "필수 사업성 데이터가 수집되지 않아",
                "총 세대수 (M4 결과)",
                "총 연면적 (M4 결과)",
                "LH 매입 단가",
                "총 사업비"
            ]
            
            print(f"   📊 필수 요소 체크:")
            for element in required_elements:
                if element in html_content:
                    print(f"      ✅ {element}")
                else:
                    print(f"      ❌ {element} (누락)")
            
            # Check prohibited outputs
            prohibited_outputs = [
                "NPV:",
                "IRR:",
                "ROI:",
                "사업성 등급: A",
                "사업성 등급: B",
                "사업성 등급: C",
                "사업성 등급: D"
            ]
            
            print(f"   🚫 금지 출력 체크:")
            prohibited_found = False
            for output in prohibited_outputs:
                if output in html_content:
                    print(f"      ❌ {output} (발견됨 - 금지)")
                    prohibited_found = True
            
            if not prohibited_found:
                print(f"      ✅ 금지 출력 없음 (정상)")
                
        else:
            print(f"   ❌ 결과: 정상 보고서 생성됨 (예상과 다름)")
            print(f"   ⚠️  M4 데이터 없음에도 사업성 분석 수행")
    else:
        print(f"   ⚠️  M5 보고서 조회 실패 (상태 코드: {response.status_code})")
    
    print(f"   🔗 보고서 URL: {report_url_fail}")
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_m5_data_not_loaded()
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
