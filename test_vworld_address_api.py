#!/usr/bin/env python3
"""
V-World API Alternative Test - Address Search
주소 검색 API로 PNU 및 좌표 확인
"""
import requests
import json
import sys
sys.path.insert(0, '/home/user/webapp')

from app.config_v30 import config_v30

def test_address_search(address):
    """V-World 주소 검색 API 테스트"""
    print("\n" + "="*80)
    print(f"📍 주소 검색: {address}")
    print("="*80)
    
    # V-World 주소 검색 API
    params = {
        'service': 'address',
        'request': 'GetAddress',
        'version': '2.0',
        'crs': 'epsg:4326',
        'address': address,
        'format': 'json',
        'type': 'PARCEL',  # 지번 주소
        'key': config_v30.VWORLD_API_KEY
    }
    
    print(f"\nAPI URL: {config_v30.VWORLD_ADDRESS_URL}")
    print(f"API Key: {config_v30.VWORLD_API_KEY}")
    print(f"Address: {address}")
    
    try:
        print("\n요청 중...")
        response = requests.get(
            config_v30.VWORLD_ADDRESS_URL,
            params=params,
            timeout=15
        )
        
        print(f"응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 전체 응답 출력
            print("\n📥 전체 응답:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 데이터 파싱
            response_data = data.get('response', {})
            status = response_data.get('status')
            
            print(f"\n✅ API 상태: {status}")
            
            if status == 'OK':
                result = response_data.get('result', {})
                items = result.get('items', [])
                
                if items:
                    print(f"\n✅ 결과 개수: {len(items)}개")
                    
                    for idx, item in enumerate(items[:3], 1):
                        print(f"\n📊 결과 #{idx}:")
                        print(f"   전체 주소: {item.get('address', {}).get('road', 'N/A')}")
                        print(f"   지번 주소: {item.get('address', {}).get('parcel', 'N/A')}")
                        print(f"   PNU: {item.get('address', {}).get('zipcode', 'N/A')}")
                        
                        point = item.get('point', {})
                        print(f"   좌표: {point.get('x', 'N/A')}, {point.get('y', 'N/A')}")
                        
                        # 전체 속성 출력
                        print(f"\n   전체 속성:")
                        print(json.dumps(item, indent=6, ensure_ascii=False))
                else:
                    print("\n⚠️  해당 주소에 대한 결과가 없습니다.")
            else:
                print(f"\n❌ API 오류: {status}")
                error_text = response_data.get('error', {}).get('text', 'N/A')
                error_code = response_data.get('error', {}).get('code', 'N/A')
                print(f"   오류 코드: {error_code}")
                print(f"   오류 메시지: {error_text}")
        else:
            print(f"\n❌ HTTP 오류: {response.status_code}")
            print(f"   응답: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n❌ 타임아웃 오류 (15초 초과)")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 연결 오류: {e}")
    except Exception as e:
        print(f"\n❌ 예외 발생: {type(e).__name__}: {e}")

def test_wms_service():
    """V-World WMS 서비스 테스트 (GetCapabilities)"""
    print("\n" + "="*80)
    print("🗺️  V-World WMS 서비스 테스트")
    print("="*80)
    
    wms_url = "https://api.vworld.kr/req/wms"
    
    params = {
        'service': 'WMS',
        'request': 'GetCapabilities',
        'key': config_v30.VWORLD_API_KEY,
        'version': '1.3.0'
    }
    
    print(f"\nWMS URL: {wms_url}")
    print(f"API Key: {config_v30.VWORLD_API_KEY}")
    
    try:
        print("\n요청 중...")
        response = requests.get(wms_url, params=params, timeout=15)
        
        print(f"응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text[:1000]
            print(f"\n✅ WMS 서비스 응답 (첫 1000자):")
            print(content)
            
            if 'ServiceException' in content:
                print("\n❌ WMS 서비스 예외 발생")
            elif 'WMS_Capabilities' in content or 'Capabilities' in content:
                print("\n✅ WMS 서비스 정상 작동")
        else:
            print(f"\n❌ HTTP 오류: {response.status_code}")
            print(f"   응답: {response.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ 예외 발생: {type(e).__name__}: {e}")

def test_simple_get():
    """단순 GET 요청으로 API 키 유효성 확인"""
    print("\n" + "="*80)
    print("🔑 API 키 유효성 간단 테스트")
    print("="*80)
    
    # 단순한 주소 검색으로 API 키 테스트
    url = "https://api.vworld.kr/req/address"
    
    params = {
        'service': 'address',
        'request': 'getAddress',
        'version': '2.0',
        'crs': 'epsg:4326',
        'address': '서울특별시 종로구',
        'format': 'json',
        'type': 'PARCEL',
        'key': config_v30.VWORLD_API_KEY
    }
    
    print(f"\nURL: {url}")
    print(f"API Key: {config_v30.VWORLD_API_KEY}")
    print(f"Simple Test Address: 서울특별시 종로구")
    
    try:
        print("\n요청 중...")
        response = requests.get(url, params=params, timeout=15)
        
        print(f"응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                status = data.get('response', {}).get('status', 'UNKNOWN')
                print(f"\n✅ API 응답 상태: {status}")
                
                if status == 'OK':
                    print("✅ API 키가 유효합니다!")
                elif status == 'NOT_FOUND':
                    print("⚠️  결과를 찾을 수 없지만 API 키는 유효합니다.")
                else:
                    error = data.get('response', {}).get('error', {})
                    print(f"❌ API 오류: {error}")
            except:
                print(f"응답 (텍스트): {response.text[:500]}")
        else:
            print(f"\n❌ HTTP 오류: {response.status_code}")
            print(f"   응답: {response.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ 예외 발생: {type(e).__name__}: {e}")

def main():
    """메인 테스트 함수"""
    print("\n" + "🔍 " * 20)
    print("V-World API 종합 테스트")
    print("🔍 " * 20)
    
    # 1. API 키 유효성 단순 테스트
    test_simple_get()
    
    # 2. WMS 서비스 테스트
    test_wms_service()
    
    # 3. 주소 검색 테스트
    test_addresses = [
        '서울특별시 관악구 신림동 1524-8',
        '서울특별시 강남구 역삼동 680-11',
        '부산광역시 해운대구 우동 1500-1'
    ]
    
    for address in test_addresses:
        test_address_search(address)
    
    print("\n" + "="*80)
    print("테스트 완료")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
