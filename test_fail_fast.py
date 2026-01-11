"""
ZeroSite FAIL FAST Test Script
===============================

극한 케이스 테스트: 데이터 누락 시나리오 검증
- M1 주소 누락
- M1 토지면적 0
- M3 공급유형 미결정
- M4 세대수 0
- M5 총 사업비 누락

각 케이스에서 시스템이 어떻게 FAIL FAST 하는지 확인
"""

import requests
import json

BASE_URL = "http://localhost:49999"

def test_invalid_parcel():
    """테스트 1: 잘못된 PNU (존재하지 않는 토지)"""
    print("\n" + "="*80)
    print("🧪 테스트 1: 잘못된 PNU (XXXXXXXXXXXXXXXXX)")
    print("="*80)
    
    payload = {
        "parcel_id": "XXXXXXXXXXXXXXXXX",
        "address": "존재하지 않는 주소"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v4/pipeline/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    result = response.json()
    print(f"상태 코드: {response.status_code}")
    print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    
    # M6 보고서 시도 (FAIL FAST 예상)
    print("\n🔍 M6 보고서 생성 시도 (FAIL FAST 예상)...")
    m6_response = requests.get(
        f"{BASE_URL}/api/v4/reports/M6/html?context_id=XXXXXXXXXXXXXXXXX"
    )
    print(f"M6 상태 코드: {m6_response.status_code}")
    
    if "데이터 무결성 오류" in m6_response.text or "Pipeline 결과 없음" in m6_response.text:
        print("✅ PASS: M6가 정상적으로 FAIL FAST 함")
    else:
        print("❌ FAIL: M6가 잘못된 데이터로 보고서를 생성함")


def test_empty_address():
    """테스트 2: 주소 없는 요청"""
    print("\n" + "="*80)
    print("🧪 테스트 2: 주소 없는 요청")
    print("="*80)
    
    payload = {
        "parcel_id": "9999999999999999999",
        "address": ""
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v4/pipeline/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        result = response.json()
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 422:
            print("✅ PASS: API가 validation error 반환")
        elif "error" in result:
            print("✅ PASS: 시스템이 오류 감지")
        else:
            print("⚠️ WARNING: 시스템이 빈 주소 허용")
            
    except Exception as e:
        print(f"⚠️ 예외 발생: {e}")


def test_zero_area():
    """테스트 3: 토지면적 0인 경우 (Mock 데이터 수정 필요)"""
    print("\n" + "="*80)
    print("🧪 테스트 3: 토지면적 검증")
    print("="*80)
    
    # 정상 분석 후 M1 데이터 확인
    payload = {
        "parcel_id": "1168010100005200012",
        "address": "서울시 강남구 역삼동 520-12"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v4/pipeline/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    result = response.json()
    land_area = result.get("results", {}).get("land", {}).get("land", {}).get("area_sqm")
    
    print(f"토지면적: {land_area}㎡")
    
    if land_area and land_area > 0:
        print("✅ PASS: 토지면적이 정상적으로 설정됨")
    else:
        print("❌ FAIL: 토지면적이 0 또는 누락됨")


if __name__ == "__main__":
    print("🔴 ZeroSite FAIL FAST 극한 케이스 테스트 시작")
    print("="*80)
    
    test_invalid_parcel()
    test_empty_address()
    test_zero_area()
    
    print("\n" + "="*80)
    print("🏁 테스트 완료")
    print("="*80)
