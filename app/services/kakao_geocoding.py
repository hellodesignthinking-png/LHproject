"""
Kakao Map API - Geocoding Service
카카오 지도 API 연동

REST API Key: 1b172a21a17b8b51dd47884b45228483
"""

import requests
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class KakaoGeocoding:
    """
    카카오 맵 API - 주소 → 좌표 변환
    
    주요 기능:
    1. 주소 검색 (address.json)
    2. 좌표 변환 (lat, lon)
    3. 도로명 추출
    """
    
    BASE_URL = "https://dapi.kakao.com/v2/local"
    API_KEY = "1b172a21a17b8b51dd47884b45228483"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            api_key: 카카오 REST API 키 (없으면 기본값 사용)
        """
        self.api_key = api_key or self.API_KEY
        logger.info(f"✅ Kakao Geocoding initialized")
    
    
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float]]:
        """
        주소 → 좌표 변환
        
        Args:
            address: 도로명 또는 지번 주소
            
        Returns:
            (위도, 경도) 또는 None
        """
        
        url = f"{self.BASE_URL}/search/address.json"
        
        headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
        
        params = {
            "query": address
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code != 200:
                logger.error(f"❌ 카카오 API 오류: {response.status_code}")
                return None
            
            data = response.json()
            
            if not data.get('documents'):
                logger.debug(f"주소 못 찾음: {address}")
                return None
            
            doc = data['documents'][0]
            
            # 좌표 추출
            lat = float(doc['y'])
            lon = float(doc['x'])
            
            logger.debug(f"📍 {address} → ({lat}, {lon})")
            
            return (lat, lon)
            
        except Exception as e:
            logger.error(f"❌ 지오코딩 오류: {e}")
            return None
    
    
    def get_road_name(self, address: str) -> str:
        """
        도로명 추출
        
        Args:
            address: 주소
            
        Returns:
            도로명 (예: "테헤란로") 또는 빈 문자열
        """
        
        url = f"{self.BASE_URL}/search/address.json"
        
        headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
        
        params = {
            "query": address
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('documents'):
                    doc = data['documents'][0]
                    
                    # 도로명 주소
                    road_address = doc.get('road_address')
                    
                    if road_address:
                        road_name = road_address.get('road_name', '')
                        return road_name
            
            return ""
            
        except Exception as e:
            logger.debug(f"도로명 추출 실패: {e}")
            return ""
    
    
    def get_full_address_info(self, address: str) -> dict:
        """
        주소 상세 정보 조회
        
        Args:
            address: 주소
            
        Returns:
            주소 정보 딕셔너리
        """
        
        url = f"{self.BASE_URL}/search/address.json"
        
        headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
        
        params = {
            "query": address
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code != 200:
                return {}
            
            data = response.json()
            
            if not data.get('documents'):
                return {}
            
            doc = data['documents'][0]
            
            # 기본 정보
            result = {
                'lat': float(doc['y']),
                'lon': float(doc['x']),
                'address_name': doc.get('address_name', ''),
                'address_type': doc.get('address_type', '')
            }
            
            # 도로명 주소 정보
            road_address = doc.get('road_address')
            if road_address:
                result.update({
                    'road_name': road_address.get('road_name', ''),
                    'building_name': road_address.get('building_name', ''),
                    'zone_no': road_address.get('zone_no', '')
                })
            
            # 지번 주소 정보
            address = doc.get('address')
            if address:
                result.update({
                    'region_1depth': address.get('region_1depth_name', ''),
                    'region_2depth': address.get('region_2depth_name', ''),
                    'region_3depth': address.get('region_3depth_name', ''),
                    'mountain_yn': address.get('mountain_yn', 'N'),
                    'main_address_no': address.get('main_address_no', ''),
                    'sub_address_no': address.get('sub_address_no', '')
                })
            
            return result
            
        except Exception as e:
            logger.error(f"주소 정보 조회 실패: {e}")
            return {}
    
    
    def classify_road_grade(self, road_name: str) -> str:
        """
        도로 등급 분류
        
        Args:
            road_name: 도로명
            
        Returns:
            도로 등급 ('대로', '중로', '소로')
        """
        
        if not road_name:
            return '소로'
        
        # 대로 (넓은 도로)
        if '대로' in road_name:
            return '대로'
        
        # 중로 (중간 도로)
        elif '로' in road_name and '길' not in road_name:
            return '중로'
        
        # 소로 (좁은 도로, 길)
        else:
            return '소로'


# Singleton instance
_kakao_geocoding = None


def get_kakao_geocoding() -> KakaoGeocoding:
    """Kakao Geocoding 싱글톤 인스턴스 반환"""
    global _kakao_geocoding
    if _kakao_geocoding is None:
        _kakao_geocoding = KakaoGeocoding()
    return _kakao_geocoding
