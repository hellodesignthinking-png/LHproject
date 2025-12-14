"""
ZeroSite v30.0 - Geocoding Engine
Real API: Kakao Local API + Fallback
Input: Address string
Output: {lat, lng, si, gu, dong, jibun}
"""
import requests
from typing import Dict, Optional
from app.config_v30 import config_v30


class GeocodingEngineV30:
    """Geocoding with real Kakao API"""
    
    def __init__(self):
        self.api_key = config_v30.KAKAO_REST_API_KEY
        self.use_real_api = config_v30.USE_REAL_API
        
    def geocode_address(self, address: str) -> Dict[str, any]:
        """
        Geocode address to coordinates and parsed components
        
        Args:
            address: Korean address string
            
        Returns:
            {
                'lat': float,
                'lng': float,
                'si': str (시/도),
                'gu': str (구/군),
                'dong': str (동/읍/면),
                'jibun': str (지번),
                'success': bool,
                'method': str  # 'kakao_api' or 'fallback'
            }
        """
        if self.use_real_api and self.api_key:
            result = self._geocode_with_kakao(address)
            if result['success']:
                return result
        
        # Fallback
        return self._geocode_fallback(address)
    
    def _geocode_with_kakao(self, address: str) -> Dict[str, any]:
        """Real Kakao API call"""
        try:
            headers = {"Authorization": f"KakaoAK {self.api_key}"}
            params = {"query": address}
            
            response = requests.get(
                config_v30.KAKAO_GEOCODE_URL,
                headers=headers,
                params=params,
                timeout=config_v30.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('documents'):
                    doc = data['documents'][0]
                    address_info = doc.get('address', {})
                    
                    return {
                        'lat': float(doc.get('y', 0)),
                        'lng': float(doc.get('x', 0)),
                        'si': address_info.get('region_1depth_name', ''),
                        'gu': address_info.get('region_2depth_name', ''),
                        'dong': address_info.get('region_3depth_name', ''),
                        'jibun': address_info.get('address_name', '').split()[-1] if address_info.get('address_name') else '',
                        'success': True,
                        'method': 'kakao_api'
                    }
        except Exception as e:
            print(f"Kakao API error: {e}")
        
        return {'success': False}
    
    def _geocode_fallback(self, address: str) -> Dict[str, any]:
        """Fallback geocoding using pattern matching"""
        # Parse address components
        parts = address.replace(',', ' ').split()
        
        si = parts[0] if len(parts) > 0 else ''
        gu = parts[1] if len(parts) > 1 else ''
        dong = parts[2] if len(parts) > 2 else ''
        jibun = parts[3] if len(parts) > 3 else ''
        
        # Approximate coordinates based on region
        lat, lng = self._estimate_coordinates(si, gu, dong)
        
        return {
            'lat': lat,
            'lng': lng,
            'si': si,
            'gu': gu,
            'dong': dong,
            'jibun': jibun,
            'success': True,
            'method': 'fallback'
        }
    
    def _estimate_coordinates(self, si: str, gu: str, dong: str) -> tuple:
        """Estimate coordinates based on known regions"""
        # Major city centers
        known_coords = {
            '서울특별시': {
                '강남구': {'역삼동': (37.5172, 127.0473), 'default': (37.5172, 127.0473)},
                '관악구': {'신림동': (37.4784, 126.9516), 'default': (37.4784, 126.9516)},
                '송파구': {'잠실동': (37.5133, 127.1000), 'default': (37.5133, 127.1000)},
                '마포구': {'상암동': (37.5794, 126.8895), 'default': (37.5794, 126.8895)},
                'default': (37.5665, 126.9780)  # Seoul City Hall
            },
            '부산광역시': {
                '해운대구': {'우동': (35.1631, 129.1635), 'default': (35.1631, 129.1635)},
                'default': (35.1796, 129.0756)  # Busan City Hall
            },
            '경기도': {
                '성남시': {'분당구': (37.3816, 127.1189), 'default': (37.4201, 127.1267)},
                'default': (37.2751, 127.0095)  # Suwon
            },
            '제주특별자치도': {
                '제주시': {'연동': (33.4841, 126.4935), 'default': (33.4996, 126.5312)},
                'default': (33.4996, 126.5312)
            }
        }
        
        if si in known_coords:
            if gu in known_coords[si]:
                if dong in known_coords[si][gu]:
                    return known_coords[si][gu][dong]
                return known_coords[si][gu].get('default', known_coords[si]['default'])
            return known_coords[si]['default']
        
        # Default: Seoul
        return (37.5665, 126.9780)


# Test function
if __name__ == "__main__":
    engine = GeocodingEngineV30()
    
    test_addresses = [
        "서울특별시 강남구 역삼동 680-11",
        "서울특별시 관악구 신림동 1524-8",
        "부산광역시 해운대구 우동 1234"
    ]
    
    for addr in test_addresses:
        result = engine.geocode_address(addr)
        print(f"{addr}:")
        print(f"  Lat/Lng: {result['lat']}, {result['lng']}")
        print(f"  Parsed: {result['si']} {result['gu']} {result['dong']} {result['jibun']}")
        print(f"  Method: {result['method']}\n")
