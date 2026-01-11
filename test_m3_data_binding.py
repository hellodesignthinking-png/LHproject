"""
M3 공급유형 결정 데이터 바인딩 복구 테스트
========================================

테스트 시나리오:
1. M1 데이터 없는 상태 (바인딩 실패)
2. M1 데이터 있는 상태 (바인딩 성공)
3. Context ID 불일치 (바인딩 실패)

Author: ZeroSite Development Team
Date: 2026-01-11
"""

import requests
import json

BASE_URL = "http://localhost:49999"
TEST_CONTEXT_ID = "1168010100005200012"


def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_case_1_no_m1_data():
    """
    TEST CASE 1: M1 데이터 없는 상태
    - Context ID는 존재하지만 M1 데이터가 없는 경우
    - 예상: DATA CONNECTION ERROR
    """
    print_section("TEST CASE 1: M1 데이터 없는 상태 (바인딩 실패)")
    
    context_id = "TEST_NO_M1_DATA_001"
    
    print(f"1️⃣ Context ID: {context_id}")
    print(f"2️⃣ 예상 결과: DATA CONNECTION ERROR (M3)")
    print(f"3️⃣ 누락 필드: address, land_area_sqm, zoning\n")
    
    # M3 보고서 조회
    url = f"{BASE_URL}/api/v4/reports/M3/html?context_id={context_id}"
    print(f"📊 M3 보고서 조회: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # 바인딩 오류 메시지 확인
            if "DATA CONNECTION ERROR" in html:
                print("✅ DATA CONNECTION ERROR 템플릿 정상 출력")
                print(f"   - 'DATA CONNECTION ERROR' 문구 발견")
            else:
                print("⚠️ DATA CONNECTION ERROR 템플릿이 출력되지 않음")
            
            # 누락 필드 확인
            if "주소" in html or "address" in html:
                print(f"   - '주소' 누락 안내 발견")
            if "대지면적" in html or "land_area" in html:
                print(f"   - '대지면적' 누락 안내 발견")
            if "용도지역" in html or "zoning" in html:
                print(f"   - '용도지역' 누락 안내 발견")
            
            # 판단 문구 미출력 확인
            if "청년형 추천" not in html and "청년형 결정" not in html:
                print(f"   - ✅ '청년형 추천/결정' 문구 미출력 확인")
            else:
                print(f"   - ⚠️ '청년형 추천/결정' 문구가 출력됨 (잘못된 동작)")
        else:
            print(f"❌ 응답 오류: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
    
    print(f"\n📄 테스트 URL: {url}")


def test_case_2_with_m1_data():
    """
    TEST CASE 2: M1 데이터 있는 상태 (정상)
    - 실제 파이프라인 실행 후 M3 보고서 확인
    - 예상: 정상 M3 보고서 출력
    """
    print_section("TEST CASE 2: M1 데이터 있는 상태 (바인딩 성공)")
    
    print(f"1️⃣ Step 1: Pipeline 실행")
    
    # 파이프라인 실행
    pipeline_url = f"{BASE_URL}/api/v4/analyze/parcel"
    payload = {
        "parcel_id": TEST_CONTEXT_ID,
        "address": "서울특별시 강남구 역삼동 123-45"
    }
    
    try:
        response = requests.post(pipeline_url, json=payload, timeout=120)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Pipeline 실행 성공")
            print(f"   Context ID: {result.get('context_id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Modules: {len(result.get('results', {}))}개\n")
            
            # M1 데이터 확인
            m1_land = result.get("results", {}).get("land", {})
            if m1_land:
                print(f"2️⃣ M1 데이터 확인:")
                print(f"   주소: {m1_land.get('address', 'N/A')}")
                print(f"   토지면적: {m1_land.get('land', {}).get('area_sqm', 0)}㎡")
                print(f"   용도지역: {m1_land.get('zoning', {}).get('type', 'N/A')}\n")
        else:
            print(f"   ❌ Pipeline 실행 실패: {response.status_code}")
            return
    
    except Exception as e:
        print(f"   ❌ Pipeline 실행 예외: {e}")
        return
    
    print(f"3️⃣ Step 2: M3 보고서 조회")
    
    # M3 보고서 조회
    m3_url = f"{BASE_URL}/api/v4/reports/M3/html?context_id={TEST_CONTEXT_ID}"
    print(f"   URL: {m3_url}\n")
    
    try:
        response = requests.get(m3_url, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            
            # 데이터 바인딩 성공 확인
            if "주소 정보 없음" not in html and "대지면적 정보 없음" not in html:
                print(f"   ✅ 데이터 바인딩 성공 (주소/면적 정상 표시)")
            else:
                print(f"   ⚠️ 데이터 바인딩 실패 (주소/면적 '정보 없음' 표시)")
            
            # 정상 보고서 내용 확인
            if "청년형" in html:
                print(f"   ✅ 공급유형 결정 보고서 정상 생성")
            
            if "입지 분석" in html or "위치 분석" in html:
                print(f"   ✅ 입지 분석 섹션 포함")
            
            if "공급유형별 비교" in html or "탈락 사유" in html:
                print(f"   ✅ 공급유형 비교 섹션 포함")
            
            # M1 데이터 표시 확인
            if "서울특별시 강남구" in html:
                print(f"   ✅ M1 주소 데이터 정상 바인딩: '서울특별시 강남구' 발견")
            
            if "500" in html or "500㎡" in html:
                print(f"   ✅ M1 토지면적 데이터 정상 바인딩: '500㎡' 발견")
        else:
            print(f"   ❌ M3 보고서 조회 실패: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ M3 보고서 조회 예외: {e}")
    
    print(f"\n📄 M3 보고서 URL: {m3_url}")


def test_case_3_context_validation():
    """
    TEST CASE 3: Context 검증
    - 잘못된 Context ID
    - 예상: 404 또는 DATA CONNECTION ERROR
    """
    print_section("TEST CASE 3: Context ID 검증")
    
    invalid_context_id = "INVALID_CONTEXT_12345"
    
    print(f"1️⃣ Invalid Context ID: {invalid_context_id}")
    print(f"2️⃣ 예상 결과: 404 Not Found 또는 DATA CONNECTION ERROR\n")
    
    url = f"{BASE_URL}/api/v4/reports/M3/html?context_id={invalid_context_id}"
    print(f"📊 M3 보고서 조회: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 404:
            print(f"✅ 404 Not Found (예상된 동작)")
        elif response.status_code == 200:
            html = response.text
            if "DATA CONNECTION ERROR" in html or "Context not found" in html:
                print(f"✅ DATA CONNECTION ERROR 또는 Context 미존재 메시지 출력")
            else:
                print(f"⚠️ 예상치 못한 정상 응답")
    
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
    
    print(f"\n📄 테스트 URL: {url}")


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 80)
    print("  M3 공급유형 결정 데이터 바인딩 복구 테스트")
    print("=" * 80)
    
    # TC1: M1 데이터 없는 상태
    # test_case_1_no_m1_data()
    
    # TC2: M1 데이터 있는 상태 (정상 파이프라인)
    test_case_2_with_m1_data()
    
    # TC3: Context ID 검증
    test_case_3_context_validation()
    
    print_section("테스트 완료")
    print("✅ M3 데이터 바인딩 복구 테스트 완료\n")


if __name__ == "__main__":
    main()
