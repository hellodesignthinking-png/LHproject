#!/usr/bin/env python3
"""
V-World API 직접 테스트 스크립트
개별공시지가 및 용도지역 API 테스트
"""
import requests
import json
import sys
sys.path.insert(0, '/home/user/webapp')

from app.config_v30 import config_v30

def test_vworld_landprice(lat, lng, address_name):
    """개별공시지가 API 테스트"""
    print("\n" + "="*80)
    print(f"📍 {address_name}")
    print(f"   좌표: {lat}, {lng}")
    print("="*80)
    
    print("\n1️⃣ 개별공시지가 API 테스트")
    print("-" * 80)
    
    # V-World 개별공시지가 API
    params = {
        'service': 'data',
        'request': 'GetFeature',
        'data': 'LP_PA_CBND_BUBUN',  # 개별공시지가 레이어
        'key': config_v30.VWORLD_API_KEY,
        'domain': 'localhost',
        'geomFilter': f'POINT({lng} {lat})',
        'format': 'json',
        'size': '1',
        'page': '1'
    }
    
    print(f"API URL: {config_v30.VWORLD_LANDPRICE_URL}")
    print(f"API Key: {config_v30.VWORLD_API_KEY}")
    print(f"Layer: {params['data']}")
    print(f"Point: POINT({lng} {lat})")
    
    try:
        print("\n요청 중...")
        response = requests.get(
            config_v30.VWORLD_LANDPRICE_URL,
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
            status = data.get('response', {}).get('status')
            print(f"\n✅ API 상태: {status}")
            
            if status == 'OK':
                features = data.get('response', {}).get('result', {}).get('featureCollection', {}).get('features', [])
                
                if features:
                    print(f"\n✅ 결과 개수: {len(features)}개")
                    
                    for idx, feature in enumerate(features[:3], 1):
                        props = feature.get('properties', {})
                        
                        print(f"\n📊 결과 #{idx}:")
                        print(f"   PNU: {props.get('PNU', 'N/A')}")
                        print(f"   공시지가 (PBLNTF_PC): ₩{props.get('PBLNTF_PC', 0):,}/㎡")
                        print(f"   기준년월 (STDMT): {props.get('STDMT', 'N/A')}")
                        print(f"   지번 (LNBR): {props.get('LNBR', 'N/A')}")
                        print(f"   지목 (LNDCGR_NM): {props.get('LNDCGR_NM', 'N/A')}")
                        print(f"   면적 (AR): {props.get('AR', 'N/A')}㎡")
                        
                        # 전체 속성 출력
                        print(f"\n   전체 속성:")
                        for key, value in props.items():
                            if key not in ['geometry', 'geom']:
                                print(f"      {key}: {value}")
                else:
                    print("\n⚠️  해당 좌표에 데이터가 없습니다.")
            else:
                print(f"\n❌ API 오류: {status}")
                print(f"   메시지: {data.get('response', {}).get('error', {}).get('text', 'N/A')}")
        else:
            print(f"\n❌ HTTP 오류: {response.status_code}")
            print(f"   응답: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n❌ 타임아웃 오류 (15초 초과)")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 연결 오류: {e}")
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")

def test_vworld_zoning(lat, lng, address_name):
    """용도지역 API 테스트"""
    print("\n\n2️⃣ 용도지역 API 테스트")
    print("-" * 80)
    
    # V-World 용도지역 API
    params = {
        'service': 'data',
        'request': 'GetFeature',
        'data': 'LT_C_UQ111',  # 용도지역 레이어
        'key': config_v30.VWORLD_API_KEY,
        'domain': 'localhost',
        'geomFilter': f'POINT({lng} {lat})',
        'format': 'json',
        'size': '1',
        'page': '1'
    }
    
    print(f"API URL: {config_v30.VWORLD_ZONING_URL}")
    print(f"API Key: {config_v30.VWORLD_API_KEY}")
    print(f"Layer: {params['data']}")
    print(f"Point: POINT({lng} {lat})")
    
    try:
        print("\n요청 중...")
        response = requests.get(
            config_v30.VWORLD_ZONING_URL,
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
            status = data.get('response', {}).get('status')
            print(f"\n✅ API 상태: {status}")
            
            if status == 'OK':
                features = data.get('response', {}).get('result', {}).get('featureCollection', {}).get('features', [])
                
                if features:
                    print(f"\n✅ 결과 개수: {len(features)}개")
                    
                    for idx, feature in enumerate(features[:3], 1):
                        props = feature.get('properties', {})
                        
                        print(f"\n📊 결과 #{idx}:")
                        print(f"   용도지역명 (UQ_NM): {props.get('UQ_NM', 'N/A')}")
                        print(f"   용도지역코드 (UQ_CD): {props.get('UQ_CD', 'N/A')}")
                        print(f"   PNU: {props.get('PNU', 'N/A')}")
                        
                        # 전체 속성 출력
                        print(f"\n   전체 속성:")
                        for key, value in props.items():
                            if key not in ['geometry', 'geom']:
                                print(f"      {key}: {value}")
                else:
                    print("\n⚠️  해당 좌표에 데이터가 없습니다.")
            else:
                print(f"\n❌ API 오류: {status}")
                print(f"   메시지: {data.get('response', {}).get('error', {}).get('text', 'N/A')}")
        else:
            print(f"\n❌ HTTP 오류: {response.status_code}")
            print(f"   응답: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("\n❌ 타임아웃 오류 (15초 초과)")
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 연결 오류: {e}")
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")

def main():
    """메인 테스트 함수"""
    print("\n" + "🔍 " * 20)
    print("V-World API 직접 테스트")
    print("🔍 " * 20)
    
    # 테스트할 주소들
    test_locations = [
        {
            'name': '서울특별시 관악구 신림동 1524-8',
            'lat': 37.4847,
            'lng': 126.9295
        },
        {
            'name': '서울특별시 강남구 역삼동 680-11',
            'lat': 37.5172,
            'lng': 127.0473
        },
        {
            'name': '부산광역시 해운대구 우동 1500-1',
            'lat': 35.1631,
            'lng': 129.1635
        }
    ]
    
    for location in test_locations:
        # 개별공시지가 API 테스트
        test_vworld_landprice(location['lat'], location['lng'], location['name'])
        
        # 용도지역 API 테스트
        test_vworld_zoning(location['lat'], location['lng'], location['name'])
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
