"""
Premium Factor Auto-Detector
Antenna Holdings Co., Ltd.

Automatically detects and populates premium factors based on:
- Address analysis
- Kakao Map API (subway stations, amenities)
- Public data APIs (redevelopment zones, school districts)

Version: 1.0
Date: 2025-12-13
"""

from typing import Dict, Optional, Tuple
import logging
import requests
import re

logger = logging.getLogger(__name__)


class PremiumAutoDetector:
    """프리미엄 요인 자동 감지기"""
    
    def __init__(self):
        """초기화"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 8학군 목록 (서울)
        self.school_district_8_areas = [
            '강남구 대치동', '강남구 도곡동', '강남구 개포동',
            '서초구 서초동', '서초구 반포동', '서초구 잠원동',
            '송파구 잠실동', '송파구 방이동'
        ]
        
        # 재개발/재건축 지역 (샘플 데이터)
        self.redevelopment_areas = {
            '강남구 역삼동': 60,  # 사업승인
            '강남구 개포동': 40,  # 조합설립인가
            '서초구 반포동': 60,
            '송파구 잠실동': 40,
            '마포구 공덕동': 20,  # 정비구역지정
        }
        
        # GTX역 (계획 포함)
        self.gtx_stations = {
            '삼성역': (37.5088, 127.0633),
            '수서역': (37.4873, 127.1022),
            '양재역': (37.4844, 127.0344),
            '강남역': (37.4979, 127.0276),
        }
        
        self.logger.info("✅ PremiumAutoDetector initialized")
    
    def auto_detect_premium_factors(
        self,
        address: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Dict[str, float]:
        """
        자동으로 프리미엄 요인 감지
        
        Args:
            address: 주소
            latitude: 위도 (선택)
            longitude: 경도 (선택)
        
        Returns:
            프리미엄 요인 딕셔너리
        """
        
        premium_factors = {}
        
        self.logger.info(f"🔍 Auto-detecting premium factors for: {address}")
        
        # Get coordinates if not provided
        if not latitude or not longitude:
            latitude, longitude = self._geocode_address(address)
        
        # 1. 지하철역 거리
        subway_premium = self._detect_subway_distance(latitude, longitude)
        if subway_premium > 0:
            premium_factors['subway_distance'] = subway_premium
            self.logger.info(f"  ✅ Subway: +{subway_premium}%")
        
        # 2. 8학군
        if self._is_school_district_8(address):
            premium_factors['school_district_8'] = 25
            self.logger.info(f"  ✅ School District 8: +25%")
        
        # 3. 대형공원
        park_premium = self._detect_large_park(latitude, longitude)
        if park_premium > 0:
            premium_factors['large_park'] = park_premium
            self.logger.info(f"  ✅ Large Park: +{park_premium}%")
        
        # 4. 백화점/쇼핑몰
        shopping_premium = self._detect_shopping_mall(latitude, longitude)
        if shopping_premium > 0:
            premium_factors['department_store'] = shopping_premium
            self.logger.info(f"  ✅ Shopping Mall: +{shopping_premium}%")
        
        # 5. 대형병원
        hospital_premium = self._detect_large_hospital(latitude, longitude)
        if hospital_premium > 0:
            premium_factors['large_hospital'] = hospital_premium
            self.logger.info(f"  ✅ Large Hospital: +{hospital_premium}%")
        
        # 6. 재개발 상황
        redevelopment_premium = self._detect_redevelopment_status(address)
        if redevelopment_premium > 0:
            premium_factors['redevelopment_status'] = redevelopment_premium
            self.logger.info(f"  ✅ Redevelopment: +{redevelopment_premium}%")
        
        # 7. GTX역 거리
        gtx_premium = self._detect_gtx_station(latitude, longitude)
        if gtx_premium > 0:
            premium_factors['gtx_station'] = gtx_premium
            self.logger.info(f"  ✅ GTX Station: +{gtx_premium}%")
        
        # 8. 한강 조망 (간단한 거리 기반 판단)
        if self._has_han_river_view(latitude, longitude):
            premium_factors['han_river_view'] = 25
            self.logger.info(f"  ✅ Han River View: +25%")
        
        total_factors = len(premium_factors)
        self.logger.info(f"✅ Detected {total_factors} premium factors")
        
        return premium_factors
    
    def _geocode_address(self, address: str) -> Tuple[float, float]:
        """카카오 API로 주소 → 좌표 변환"""
        try:
            from config.api_keys import APIKeys
            kakao_key = APIKeys.get_kakao_key('rest')
            
            url = "https://dapi.kakao.com/v2/local/search/address.json"
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            params = {"query": address}
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('documents'):
                    doc = result['documents'][0]
                    return (float(doc['y']), float(doc['x']))
        except Exception as e:
            self.logger.warning(f"⚠️ Geocoding failed: {e}")
        
        return (37.5665, 126.9780)  # Fallback: Seoul City Hall
    
    def _detect_subway_distance(self, lat: float, lon: float) -> float:
        """지하철역까지 거리 감지"""
        try:
            from config.api_keys import APIKeys
            kakao_key = APIKeys.get_kakao_key('rest')
            
            url = "https://dapi.kakao.com/v2/local/search/category.json"
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            params = {
                "category_group_code": "SW8",  # 지하철역
                "x": lon,
                "y": lat,
                "radius": 1000,  # 1km 반경
                "sort": "distance"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('documents'):
                    nearest = result['documents'][0]
                    distance = int(nearest.get('distance', 99999))
                    
                    if distance <= 300:
                        return 30  # 300m 이내 +30%
                    elif distance <= 500:
                        return 20  # 500m 이내 +20%
                    elif distance <= 800:
                        return 10  # 800m 이내 +10%
        except Exception as e:
            self.logger.warning(f"⚠️ Subway detection failed: {e}")
        
        return 0
    
    def _is_school_district_8(self, address: str) -> bool:
        """8학군 여부 확인"""
        for area in self.school_district_8_areas:
            if area in address:
                return True
        return False
    
    def _detect_large_park(self, lat: float, lon: float) -> float:
        """대형공원 거리 감지"""
        try:
            from config.api_keys import APIKeys
            kakao_key = APIKeys.get_kakao_key('rest')
            
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            params = {
                "query": "공원",
                "x": lon,
                "y": lat,
                "radius": 1500,  # 1.5km 반경
                "sort": "distance"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('documents'):
                    # 첫 번째 결과가 대형공원인지 확인
                    nearest = result['documents'][0]
                    distance = int(nearest.get('distance', 99999))
                    
                    if distance <= 500:
                        return 15  # 500m 이내 +15%
                    elif distance <= 1000:
                        return 8   # 1km 이내 +8%
        except Exception as e:
            self.logger.warning(f"⚠️ Park detection failed: {e}")
        
        return 0
    
    def _detect_shopping_mall(self, lat: float, lon: float) -> float:
        """백화점/쇼핑몰 거리 감지"""
        try:
            from config.api_keys import APIKeys
            kakao_key = APIKeys.get_kakao_key('rest')
            
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            params = {
                "query": "백화점",
                "x": lon,
                "y": lat,
                "radius": 2000,  # 2km 반경
                "sort": "distance"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('documents'):
                    nearest = result['documents'][0]
                    distance = int(nearest.get('distance', 99999))
                    
                    if distance <= 500:
                        return 20  # 500m 이내 +20%
                    elif distance <= 1000:
                        return 12  # 1km 이내 +12%
        except Exception as e:
            self.logger.warning(f"⚠️ Shopping mall detection failed: {e}")
        
        return 0
    
    def _detect_large_hospital(self, lat: float, lon: float) -> float:
        """대형병원 거리 감지"""
        try:
            from config.api_keys import APIKeys
            kakao_key = APIKeys.get_kakao_key('rest')
            
            url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            headers = {"Authorization": f"KakaoAK {kakao_key}"}
            params = {
                "query": "대학병원",
                "x": lon,
                "y": lat,
                "radius": 5000,  # 5km 반경
                "sort": "distance"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('documents'):
                    nearest = result['documents'][0]
                    distance = int(nearest.get('distance', 99999))
                    
                    if distance <= 2000:
                        return 12  # 2km 이내 +12%
                    elif distance <= 5000:
                        return 5   # 5km 이내 +5%
        except Exception as e:
            self.logger.warning(f"⚠️ Hospital detection failed: {e}")
        
        return 0
    
    def _detect_redevelopment_status(self, address: str) -> float:
        """재개발 상황 감지"""
        for area, premium in self.redevelopment_areas.items():
            if area in address:
                return premium
        return 0
    
    def _detect_gtx_station(self, lat: float, lon: float) -> float:
        """GTX역 거리 감지"""
        from math import radians, sin, cos, sqrt, atan2
        
        min_distance = float('inf')
        
        for station_name, (station_lat, station_lon) in self.gtx_stations.items():
            # Haversine formula
            R = 6371  # Earth radius in km
            
            dlat = radians(lat - station_lat)
            dlon = radians(lon - station_lon)
            
            a = sin(dlat/2)**2 + cos(radians(station_lat)) * cos(radians(lat)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            min_distance = min(min_distance, distance)
        
        if min_distance <= 0.5:  # 500m
            return 50  # +50%
        elif min_distance <= 1.0:  # 1km
            return 35  # +35%
        elif min_distance <= 2.0:  # 2km
            return 20  # +20%
        
        return 0
    
    def _has_han_river_view(self, lat: float, lon: float) -> bool:
        """한강 조망권 여부 (간이 판단)"""
        # 한강 남쪽 인근 지역 (위도 기준)
        if 37.500 <= lat <= 37.540:
            # 한강변 근처 (±500m)
            han_river_lat = 37.520  # 대략적인 한강 위도
            distance_from_river = abs(lat - han_river_lat) * 111  # km
            
            if distance_from_river <= 0.5:  # 500m 이내
                return True
        
        return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    detector = PremiumAutoDetector()
    
    # Test case 1: 강남역 인근
    print("=" * 60)
    print("Test 1: 강남역 인근")
    print("=" * 60)
    
    factors1 = detector.auto_detect_premium_factors(
        "서울시 강남구 역삼동 123",
        latitude=37.4979,
        longitude=127.0276
    )
    
    print(f"\n감지된 프리미엄 요인: {len(factors1)}개")
    for key, value in factors1.items():
        print(f"  • {key}: {value:+.0f}%")
    
    # Test case 2: 한강변 잠실
    print("\n" + "=" * 60)
    print("Test 2: 한강변 잠실")
    print("=" * 60)
    
    factors2 = detector.auto_detect_premium_factors(
        "서울시 송파구 잠실동 456",
        latitude=37.5133,
        longitude=127.1000
    )
    
    print(f"\n감지된 프리미엄 요인: {len(factors2)}개")
    for key, value in factors2.items():
        print(f"  • {key}: {value:+.0f}%")
    
    print("\n✅ Auto-detection test completed")
