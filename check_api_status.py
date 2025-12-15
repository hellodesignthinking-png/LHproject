#!/usr/bin/env python3
"""API 연동 상태 확인"""

import requests
import json

# API 설정
APIS = {
    '카카오': {
        'url': 'https://dapi.kakao.com/v2/local/search/address.json',
        'params': {'query': '서울 강남구 역삼동 680-11'},
        'headers': {'Authorization': 'KakaoAK 1b172a21a17b8b51dd47884b45228483'}
    },
    'V-World': {
        'url': 'https://api.vworld.kr/req/data',
        'params': {
            'service': 'data',
            'version': '2.0',
            'request': 'GetFeature',
            'key': 'B6B0B6F1-E572-304A-9742-384510D86FE4',
            'data': 'LP_PA_CBND_BONBUN',
            'format': 'json',
            'geomFilter': 'POINT(127.0358887 37.4948853)'
        }
    },
    '국토부': {
        'url': 'http://apis.data.go.kr/1611000/nsdi/LandUseService/attr/getLandUseAttr',
        'params': {
            'ServiceKey': '702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d',
            'pnu': '1168010100106800011',
            'format': 'xml'
        }
    }
}

def test_api(name, config):
    """API 테스트"""
    print(f"\n📡 {name} API 테스트...")
    
    try:
        response = requests.get(
            config['url'],
            params=config.get('params', {}),
            headers=config.get('headers', {}),
            timeout=10
        )
        
        print(f"   HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ 성공")
            
            # 응답 미리보기
            content = response.text[:200]
            print(f"   응답: {content}...")
            
            return True
        else:
            print(f"   ❌ 실패 (HTTP {response.status_code})")
            print(f"   응답: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔍 ZeroSite API 연동 상태 확인")
    print("="*60)
    
    results = {}
    
    for name, config in APIS.items():
        results[name] = test_api(name, config)
    
    print("\n" + "="*60)
    print("📊 결과 요약")
    print("="*60)
    
    for name, success in results.items():
        status = "✅ 작동" if success else "❌ 실패"
        print(f"{name:10s}: {status}")
    
    total = len(results)
    success_count = sum(results.values())
    
    print(f"\n총 {total}개 중 {success_count}개 성공 ({success_count/total*100:.0f}%)")
    print("\n💡 외부 API 실패 시 자동으로 Fallback 시스템이 작동합니다.")
