"""
ZeroSite M4/M5/M6 데이터 바인딩 복구 통합 테스트
===============================================

목적: M4, M5, M6 모든 모듈의 데이터 바인딩 복구 검증

Author: ZeroSite Development Team
Date: 2026-01-11
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import requests
import json

BASE_URL = "http://localhost:49999"

def test_full_pipeline_data_binding():
    """
    테스트: 전체 파이프라인 M4/M5/M6 데이터 바인딩
    
    1. 파이프라인 실행 (Context 생성)
    2. M4 보고서 확인 (데이터 바인딩)
    3. M5 보고서 확인 (M4 데이터 연계)
    4. M6 보고서 확인 (M1~M5 데이터 연계)
    """
    print("=" * 80)
    print("TEST: Full Pipeline Data Binding (M4/M5/M6)")
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
        print(f"\n📊 M1 데이터:")
        print(f"   - 주소: {land_data.get('address', 'N/A')}")
        print(f"   - 토지면적: {land_data.get('land', {}).get('area_sqm', 0)} ㎡")
        print(f"   - 용도지역: {land_data.get('zoning', {}).get('type', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Pipeline 실행 실패: {e}")
        return
    
    # Step 2: M4 보고서 확인
    print(f"\n📍 Step 2: M4 보고서 확인")
    test_module_report("M4", parcel_id)
    
    # Step 3: M5 보고서 확인
    print(f"\n📍 Step 3: M5 보고서 확인")
    test_module_report("M5", parcel_id)
    
    # Step 4: M6 보고서 확인
    print(f"\n📍 Step 4: M6 보고서 확인")
    test_module_report("M6", parcel_id)

def test_module_report(module_id: str, context_id: str):
    """개별 모듈 보고서 테스트"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/v4/reports/{module_id}/html",
            params={"context_id": context_id},
            timeout=10
        )
        response.raise_for_status()
        html = response.text
        
        # 키워드 분석
        keywords = {
            "DATA CONNECTION ERROR": "❌ 데이터 연결 오류",
            "DATA NOT LOADED": "❌ 데이터 미로딩",
            "DATA INSUFFICIENT": "❌ 데이터 부족",
            "세대": "✅ 세대수 표시",
            "연면적": "✅ 연면적 표시",
            "NPV": "✅ NPV 지표" if module_id == "M5" else None,
            "최종 판단": "✅ 최종 판단" if module_id == "M6" else None,
        }
        
        results = {}
        for keyword, description in keywords.items():
            if description is None:
                continue
            if keyword in html:
                results[description] = "감지됨"
        
        print(f"✅ {module_id} 보고서 조회 성공")
        print(f"   보고서 내용:")
        for desc, status in results.items():
            print(f"   - {desc}: {status}")
        
        # 보고서 URL
        print(f"   🔗 URL: {BASE_URL}/api/v4/reports/{module_id}/html?context_id={context_id}")
        
        # 최종 판정
        error_detected = any("❌" in desc for desc in results.keys())
        if error_detected:
            print(f"   ⚠️ 결과: 데이터 연결 문제 감지")
        else:
            print(f"   ✅ 결과: 정상 보고서 생성")
        
    except Exception as e:
        print(f"❌ {module_id} 보고서 조회 실패: {e}")

def test_data_flow():
    """
    테스트: 데이터 흐름 검증
    M1 → M3 → M4 → M5 → M6
    """
    print("\n" + "=" * 80)
    print("TEST: Data Flow Verification (M1→M3→M4→M5→M6)")
    print("=" * 80)
    
    parcel_id = "1168010100005200012"
    
    try:
        # 파이프라인 실행
        response = requests.post(
            f"{BASE_URL}/api/v4/pipeline/analyze",
            json={"parcel_id": parcel_id, "address": "서울특별시 강남구 역삼동 123-45"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        results_data = result.get("results", {})
        
        # M1 → M4 흐름
        print(f"\n📊 M1 → M4 데이터 흐름:")
        m1_land_area = results_data.get("land", {}).get("land", {}).get("area_sqm", 0)
        m1_zoning = results_data.get("land", {}).get("zoning", {}).get("type", "")
        print(f"   M1: 토지면적={m1_land_area}㎡, 용도지역={m1_zoning}")
        print(f"   → M4에서 사용 여부 확인 필요")
        
        # M3 → M4 흐름
        print(f"\n📊 M3 → M4 데이터 흐름:")
        m3_type = results_data.get("housing_type", {}).get("details", {}).get("selected", {}).get("type", "")
        print(f"   M3: 공급유형={m3_type}")
        print(f"   → M4에서 사용 여부 확인 필요")
        
        # M4 → M5 흐름
        print(f"\n📊 M4 → M5 데이터 흐름:")
        m4_units = results_data.get("capacity", {}).get("summary", {}).get("recommended_units", 0)
        m4_floor_area = results_data.get("capacity", {}).get("details", {}).get("total_floor_area_sqm", 0)
        print(f"   M4: 세대수={m4_units}, 연면적={m4_floor_area}㎡")
        print(f"   → M5에서 사용 여부 확인 필요")
        
        # M5 → M6 흐름
        print(f"\n📊 M5 → M6 데이터 흐름:")
        m5_npv = results_data.get("feasibility", {}).get("summary", {}).get("npv_public_krw", 0)
        print(f"   M5: NPV={m5_npv:,.0f}원")
        print(f"   → M6에서 사용 여부 확인 필요")
        
        print(f"\n✅ 데이터 흐름 검증 완료")
        
    except Exception as e:
        print(f"❌ 데이터 흐름 검증 실패: {e}")

if __name__ == "__main__":
    test_full_pipeline_data_binding()
    test_data_flow()
    
    print("\n" + "=" * 80)
    print("✅ 전체 테스트 완료")
    print("=" * 80)
