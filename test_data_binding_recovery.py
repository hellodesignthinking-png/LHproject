"""
ZeroSite Data Binding Recovery 테스트
====================================

목적: M4/M5 데이터 바인딩 복구 로직 검증

Author: ZeroSite Development Team
Date: 2026-01-11
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import requests
import json

BASE_URL = "http://localhost:49999"

def test_data_binding_recovery():
    """
    테스트: M4 데이터 바인딩 복구
    
    1. 파이프라인 실행 (Context 생성)
    2. M4 보고서 조회 (데이터 바인딩 복구 확인)
    """
    print("=" * 80)
    print("TEST: M4 Data Binding Recovery")
    print("=" * 80)
    
    # Step 1: 파이프라인 실행
    print("\n📍 Step 1: Pipeline 실행")
    parcel_id = "1168010100005200012"
    address = "서울특별시 강남구 역삼동 123-45"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v4/pipeline/analyze",
            json={"parcel_id": parcel_id, "address": address},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"✅ Pipeline 실행 성공")
        print(f"   - Context ID: {result.get('analysis_id')}")
        print(f"   - Status: {result.get('status')}")
        print(f"   - Modules: {result.get('modules_executed')}")
        
        # M1 데이터 확인
        land_data = result.get("results", {}).get("land", {})
        print(f"\n📊 M1 데이터 확인:")
        print(f"   - 주소: {land_data.get('address', 'N/A')}")
        print(f"   - 토지면적: {land_data.get('land', {}).get('area_sqm', 0)} ㎡")
        print(f"   - 용도지역: {land_data.get('zoning', {}).get('type', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Pipeline 실행 실패: {e}")
        return
    
    # Step 2: M4 보고서 조회
    print(f"\n📍 Step 2: M4 보고서 조회 (데이터 바인딩 복구 확인)")
    
    try:
        m4_response = requests.get(
            f"{BASE_URL}/api/v4/reports/M4/html",
            params={"context_id": parcel_id},
            timeout=10
        )
        m4_response.raise_for_status()
        m4_html = m4_response.text
        
        # HTML 분석
        keywords = {
            "DATA CONNECTION ERROR": "데이터 연결 오류",
            "상위 모듈(M1~M3) 데이터가 연결되지 않아": "바인딩 실패 메시지",
            "법적 건축 가능 범위": "정상 분석 내용",
            "시나리오 분석": "정상 분석 내용",
        }
        
        detection_results = {}
        for keyword, description in keywords.items():
            if keyword in m4_html:
                detection_results[description] = "✅ 감지됨"
            else:
                detection_results[description] = "❌ 없음"
        
        print(f"✅ M4 보고서 조회 성공")
        print(f"\n📊 보고서 내용 분석:")
        for desc, status in detection_results.items():
            print(f"   - {desc}: {status}")
        
        # 최종 판정
        if detection_results["데이터 연결 오류"] == "✅ 감지됨":
            print(f"\n⚠️ 결과: DATA CONNECTION ERROR 템플릿 사용 중")
            print(f"   → 데이터 바인딩 복구 실패 또는 데이터 부족")
        elif detection_results["정상 분석 내용"] == "✅ 감지됨":
            print(f"\n✅ 결과: 정상 분석 보고서 생성")
            print(f"   → 데이터 바인딩 복구 성공")
        else:
            print(f"\n❓ 결과: 판정 불가 (예상치 못한 출력)")
        
        # 보고서 URL 출력
        print(f"\n🔗 M4 보고서 URL:")
        print(f"   {BASE_URL}/api/v4/reports/M4/html?context_id={parcel_id}")
        
    except Exception as e:
        print(f"❌ M4 보고서 조회 실패: {e}")

def test_data_connection_error_template():
    """
    테스트: DATA CONNECTION ERROR 템플릿 직접 확인
    """
    print("\n" + "=" * 80)
    print("TEST: DATA CONNECTION ERROR Template")
    print("=" * 80)
    
    # 빈 Context ID로 M4 보고서 요청 (데이터 없음)
    test_context_id = "INVALID_CONTEXT_12345"
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v4/reports/M4/html",
            params={"context_id": test_context_id},
            timeout=10
        )
        
        print(f"\n📍 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # 키워드 확인
            if "DATA CONNECTION ERROR" in html:
                print(f"✅ DATA CONNECTION ERROR 템플릿 감지됨")
            elif "DATA INSUFFICIENT" in html:
                print(f"✅ DATA INSUFFICIENT 템플릿 사용 중")
            else:
                print(f"❓ 예상치 못한 템플릿 사용")
                
        elif response.status_code == 404:
            print(f"⚠️ Context not found (예상된 동작)")
        
        print(f"\n🔗 테스트 URL:")
        print(f"   {BASE_URL}/api/v4/reports/M4/html?context_id={test_context_id}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    test_data_binding_recovery()
    test_data_connection_error_template()
    
    print("\n" + "=" * 80)
    print("✅ 테스트 완료")
    print("=" * 80)
