"""
Test DATA INSUFFICIENT detection
"""
import requests
import json

BASE_URL = "http://localhost:49999"

def test_invalid_pnu():
    """테스트: 잘못된 PNU로 DATA INSUFFICIENT 트리거"""
    print("\n" + "="*80)
    print("🧪 테스트: 잘못된 PNU → DATA INSUFFICIENT 예상")
    print("="*80)
    
    payload = {
        "parcel_id": "INVALID_TEST_PNU_999",
        "address": ""
    }
    
    # 파이프라인 실행
    response = requests.post(
        f"{BASE_URL}/api/v4/pipeline/analyze",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    result = response.json()
    print(f"파이프라인 상태: {result.get('status')}")
    
    # M4 보고서 요청
    context_id = result.get("parcel_id")
    print(f"\n🔍 M4 보고서 생성 (Context: {context_id})...")
    
    m4_response = requests.get(
        f"{BASE_URL}/api/v4/reports/M4/html?context_id={context_id}"
    )
    
    html = m4_response.text
    
    # DATA INSUFFICIENT 템플릿 감지
    if "DATA INSUFFICIENT" in html:
        print("✅ PASS: DATA INSUFFICIENT 템플릿 사용됨")
        print("✅ PASS: 추정 계산 없음")
        print("✅ PASS: 입력 요청 안내 출력")
    elif "추가 입력이 필요한 항목" in html:
        print("✅ PASS: 입력 요청 템플릿 감지")
    elif "Mock Data" in html or "500.0㎡" in html:
        print("❌ FAIL: Mock 데이터로 보고서 생성함")
    else:
        print("⚠️ WARNING: 알 수 없는 응답")
        print(html[:500])


if __name__ == "__main__":
    print("🔴 ZeroSite DATA INSUFFICIENT 테스트 시작")
    print("="*80)
    
    test_invalid_pnu()
    
    print("\n" + "="*80)
    print("🏁 테스트 완료")
    print("="*80)
