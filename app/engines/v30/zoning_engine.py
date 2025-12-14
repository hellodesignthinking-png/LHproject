"""
ZeroSite v30.0 - Zoning Engine
Real API: V-World Land Use Regulation API + Fallback
Input: lat, lng
Output: zone_type (용도지역)
"""
import requests
from typing import Dict, Optional
from app.config_v30 import config_v30


class ZoningEngineV30:
    """Land use zoning with real V-World API"""
    
    def __init__(self):
        self.api_key = config_v30.VWORLD_API_KEY
        self.use_real_api = config_v30.USE_REAL_API
        
    def get_zone_type(self, lat: float, lng: float, si: str = '', gu: str = '', dong: str = '') -> Dict[str, any]:
        """
        Get land use zone type for coordinates
        
        Args:
            lat: Latitude
            lng: Longitude
            si, gu, dong: Optional address components for fallback
            
        Returns:
            {
                'zone_type': str,  # 용도지역 (e.g., '제2종일반주거지역', '근린상업지역')
                'zone_code': str,
                'success': bool,
                'method': str
            }
        """
        if self.use_real_api and self.api_key:
            result = self._get_zone_from_vworld(lat, lng)
            if result['success']:
                return result
        
        # Fallback
        return self._get_zone_fallback(si, gu, dong)
    
    def _get_zone_from_vworld(self, lat: float, lng: float) -> Dict[str, any]:
        """Real V-World API call"""
        try:
            params = {
                'service': 'data',
                'request': 'GetFeature',
                'data': 'LT_C_UQ111',  # 용도지역 레이어
                'key': self.api_key,
                'domain': 'localhost',
                'geomFilter': f'POINT({lng} {lat})',
                'format': 'json',
                'size': '1',
                'page': '1'
            }
            
            response = requests.get(
                config_v30.VWORLD_ZONING_URL,
                params=params,
                timeout=config_v30.API_TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('response', {}).get('status') == 'OK':
                    features = data.get('response', {}).get('result', {}).get('featureCollection', {}).get('features', [])
                    if features:
                        props = features[0].get('properties', {})
                        zone_name = props.get('UQ_NM', '')  # 용도지역명
                        zone_code = props.get('UQ_CD', '')  # 용도지역코드
                        
                        if zone_name:
                            return {
                                'zone_type': zone_name,
                                'zone_code': zone_code,
                                'success': True,
                                'method': 'vworld_api'
                            }
        except Exception as e:
            print(f"V-World API error: {e}")
        
        return {'success': False}
    
    def _get_zone_fallback(self, si: str, gu: str, dong: str) -> Dict[str, any]:
        """Fallback zoning based on address patterns"""
        # Zoning patterns by region
        zone_map = {
            '서울특별시': {
                '강남구': {
                    '역삼동': '근린상업지역',
                    '삼성동': '일반상업지역',
                    'default': '근린상업지역'
                },
                '관악구': {
                    '신림동': '제2종일반주거지역',
                    'default': '제2종일반주거지역'
                },
                '송파구': {
                    '잠실동': '준주거지역',
                    'default': '제2종일반주거지역'
                },
                '마포구': {
                    '상암동': '준주거지역',
                    'default': '제2종일반주거지역'
                },
                'default': '제2종일반주거지역'
            },
            '부산광역시': {
                '해운대구': {
                    '우동': '근린상업지역',
                    'default': '근린상업지역'
                },
                'default': '제2종일반주거지역'
            },
            '경기도': {
                '성남시': {
                    'default': '제2종일반주거지역'
                },
                'default': '제2종일반주거지역'
            },
            '제주특별자치도': {
                '제주시': {
                    '연동': '계획관리지역',
                    'default': '계획관리지역'
                },
                'default': '계획관리지역'
            }
        }
        
        # Lookup zone
        zone_type = '제2종일반주거지역'  # default
        
        if si in zone_map:
            if gu in zone_map[si]:
                if dong in zone_map[si][gu]:
                    zone_type = zone_map[si][gu][dong]
                else:
                    zone_type = zone_map[si][gu].get('default', zone_map[si]['default'])
            else:
                zone_type = zone_map[si]['default']
        
        return {
            'zone_type': zone_type,
            'zone_code': '',
            'success': True,
            'method': 'fallback'
        }


# Test function
if __name__ == "__main__":
    engine = ZoningEngineV30()
    
    test_cases = [
        (37.5172, 127.0473, '서울특별시', '강남구', '역삼동'),  # Gangnam
        (37.4784, 126.9516, '서울특별시', '관악구', '신림동'),  # Gwanak
        (35.1631, 129.1635, '부산광역시', '해운대구', '우동'),  # Haeundae
    ]
    
    for lat, lng, si, gu, dong in test_cases:
        result = engine.get_zone_type(lat, lng, si, gu, dong)
        print(f"{si} {gu} {dong}:")
        print(f"  Zone: {result['zone_type']}")
        print(f"  Method: {result['method']}\n")
