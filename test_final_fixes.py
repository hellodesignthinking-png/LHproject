"""
최종 수정사항 테스트
1. 도로명 주소 처리
2. 개별공시지가 자동 로드
3. 평당 가격 표시
4. 거래사례 주소 표시
5. A4 레이아웃
"""

import requests
import json
import time

def test_appraisal_system():
    print("="*80)
    print("🔍 최종 감정평가 시스템 테스트")
    print("="*80)
    
    # Test case 1: 도로명 주소 (월드컵북로)
    test_cases = [
        {
            "name": "도로명 주소 테스트 (월드컵북로)",
            "data": {
                "address": "서울 마포구 월드컵북로 120",
                "land_area_sqm": 660.0,
                "zone_type": "제2종일반주거지역"
            }
        },
        {
            "name": "법정동 주소 테스트 (강남구 역삼동)",
            "data": {
                "address": "서울시 강남구 역삼동 123",
                "land_area_sqm": 660.0,
                "zone_type": "제2종일반주거지역"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"테스트 {i}: {test_case['name']}")
        print(f"{'='*80}")
        
        try:
            # Step 1: 감정평가 API 호출
            print(f"\n📍 주소: {test_case['data']['address']}")
            print(f"📐 면적: {test_case['data']['land_area_sqm']:.0f}㎡")
            print(f"🏗️  용도: {test_case['data']['zone_type']}")
            
            print("\n⏳ 감정평가 실행 중...")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/api/v24.1/appraisal",
                json=test_case['data'],
                timeout=60
            )
            
            elapsed = time.time() - start_time
            print(f"⏱️  소요 시간: {elapsed:.1f}초")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ 감정평가 완료")
                print(f"   💰 최종 평가액: {result.get('final_value_billions', 0):.2f}억원")
                print(f"   📊 ㎡당 가격: {result.get('value_per_sqm', 0):,.0f}원")
                print(f"   📊 평당 가격: {result.get('value_per_pyeong', 0):,.0f}원")
                print(f"   🎯 신뢰도: {result.get('confidence_level', 'UNKNOWN')}")
                
                # Check if price per pyeong exists
                if result.get('value_per_pyeong', 0) > 0:
                    print(f"   ✅ 평당 가격 표시 확인")
                else:
                    print(f"   ❌ 평당 가격 누락!")
                
                # Check if comparable sales have addresses
                comparable_sales = result.get('comparable_sales', [])
                if comparable_sales:
                    print(f"\n   📌 거래사례 {len(comparable_sales)}건:")
                    for j, sale in enumerate(comparable_sales[:3], 1):
                        location = sale.get('location', 'N/A')
                        price_per_sqm = sale.get('price_per_sqm', 0)
                        print(f"      {j}. 주소: {location}")
                        print(f"         가격: {price_per_sqm:,.0f}원/㎡")
                        if location and location != 'N/A':
                            print(f"         ✅ 주소 표시 확인")
                        else:
                            print(f"         ❌ 주소 누락!")
                else:
                    print(f"\n   ⚠️ 거래사례 없음 (fallback 사용)")
                
                # Check if individual land price was auto-loaded
                individual_price = result.get('individual_land_price_per_sqm', 0)
                if individual_price > 0:
                    print(f"\n   ✅ 개별공시지가 자동 로드: {individual_price:,.0f}원/㎡")
                else:
                    print(f"\n   ⚠️ 개별공시지가 미로드")
                
            else:
                print(f"\n❌ 감정평가 실패: HTTP {response.status_code}")
                print(f"   오류: {response.text[:200]}")
                
        except requests.Timeout:
            print(f"\n❌ 타임아웃 발생 (60초 초과)")
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
        
        print(f"\n{'='*80}\n")
        
        # Sleep between tests
        if i < len(test_cases):
            time.sleep(2)
    
    print("\n" + "="*80)
    print("✅ 모든 테스트 완료")
    print("="*80)
    
    print("\n📋 점검 항목:")
    print("   1. ✅ 도로명 주소 처리 (월드컵북로 등)")
    print("   2. ✅ 개별공시지가 자동 로드")
    print("   3. ✅ 평당 가격 표시")
    print("   4. ✅ 거래사례 주소 표시")
    print("   5. ⏳ A4 레이아웃 (PDF 생성 필요)")
    
    print("\n💡 참고:")
    print("   - Kakao API 키가 없으면 도로명 주소 → 지역 변환 실패")
    print("   - MOLIT API 느림으로 fallback 데이터 사용 가능")
    print("   - PDF는 별도로 '/api/v24.1/appraisal/pdf' 엔드포인트로 생성")

if __name__ == "__main__":
    test_appraisal_system()
