"""
카카오맵 API 서비스
"""

import httpx
from typing import Optional, List, Dict, Any
from app.config import get_settings
from app.schemas import Coordinates, NearbyFacility


class KakaoService:
    """카카오맵 API 통합 서비스"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.kakao_api_base_url
        self.api_key = self.settings.kakao_rest_api_key
        self.headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
    
    async def address_to_coordinates(self, address: str) -> Optional[Coordinates]:
        """
        주소를 좌표로 변환
        
        Args:
            address: 변환할 주소
            
        Returns:
            Coordinates 객체 또는 None
        """
        url = f"{self.base_url}/v2/local/search/address.json"
        params = {"query": address}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("documents"):
                    doc = data["documents"][0]
                    return Coordinates(
                        latitude=float(doc["y"]),
                        longitude=float(doc["x"])
                    )
                
                return None
                
        except Exception as e:
            print(f"❌ 주소 변환 실패: {e}")
            return None
    
    async def search_nearby_facilities(
        self,
        coordinates: Coordinates,
        category: str,
        radius: int = 2000
    ) -> List[NearbyFacility]:
        """
        주변 시설 검색
        
        Args:
            coordinates: 중심 좌표
            category: 검색 카테고리 (예: "지하철역", "대학교", "편의점")
            radius: 검색 반경(m), 최대 20000
            
        Returns:
            주변 시설 리스트
        """
        url = f"{self.base_url}/v2/local/search/keyword.json"
        params = {
            "query": category,
            "x": coordinates.longitude,
            "y": coordinates.latitude,
            "radius": radius,
            "sort": "distance"
        }
        
        facilities = []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                for doc in data.get("documents", [])[:10]:  # 최대 10개
                    facilities.append(NearbyFacility(
                        name=doc["place_name"],
                        category=doc.get("category_name", category),
                        distance=float(doc["distance"]),
                        address=doc.get("address_name", "")
                    ))
                
        except Exception as e:
            print(f"❌ 주변 시설 검색 실패 ({category}): {e}")
        
        return facilities
    
    async def search_hazardous_facilities(self, coordinates: Coordinates) -> List[Dict[str, Any]]:
        """
        유해시설 검색 (주유소, 공장 등)
        
        Args:
            coordinates: 중심 좌표
            
        Returns:
            유해시설 리스트
        """
        hazardous_categories = [
            "주유소",
            "공장",
            "폐기물처리시설",
            "축사",
            "장례식장",
            "화장장"
        ]
        
        all_hazardous = []
        
        for category in hazardous_categories:
            facilities = await self.search_nearby_facilities(
                coordinates,
                category,
                radius=500  # 500m 이내
            )
            
            for facility in facilities:
                all_hazardous.append({
                    "name": facility.name,
                    "category": category,
                    "distance": facility.distance,
                    "address": facility.address
                })
        
        return all_hazardous
    
    async def get_road_info(self, coordinates: Coordinates) -> Optional[Dict[str, Any]]:
        """
        도로 정보 조회 (간접적으로 카테고리 검색 활용)
        
        Args:
            coordinates: 좌표
            
        Returns:
            도로 정보 딕셔너리
        """
        url = f"{self.base_url}/v2/local/geo/coord2address.json"
        params = {
            "x": coordinates.longitude,
            "y": coordinates.latitude
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("documents"):
                    doc = data["documents"][0]
                    road_info = doc.get("road_address", {})
                    
                    return {
                        "road_name": road_info.get("road_name", ""),
                        "zone_no": road_info.get("zone_no", ""),
                        "address": doc.get("address", {}).get("address_name", "")
                    }
                
        except Exception as e:
            print(f"❌ 도로 정보 조회 실패: {e}")
        
        return None
    
    async def analyze_location_accessibility(self, coordinates: Coordinates) -> Dict[str, Any]:
        """
        입지 접근성 종합 분석
        
        Args:
            coordinates: 분석할 좌표
            
        Returns:
            접근성 분석 결과
        """
        # 주요 시설별 검색
        subway_stations = await self.search_nearby_facilities(coordinates, "지하철역", 2000)
        universities = await self.search_nearby_facilities(coordinates, "대학교", 3000)
        bus_stops = await self.search_nearby_facilities(coordinates, "버스정류장", 500)
        convenience_stores = await self.search_nearby_facilities(coordinates, "편의점", 1000)
        
        # 최단 거리 계산
        nearest_subway = min([f.distance for f in subway_stations], default=9999)
        nearest_university = min([f.distance for f in universities], default=9999)
        nearest_bus = min([f.distance for f in bus_stops], default=9999)
        nearest_convenience = min([f.distance for f in convenience_stores], default=9999)
        
        # 접근성 점수 계산 (100점 만점)
        accessibility_score = 0
        
        if nearest_subway < 500:
            accessibility_score += 40
        elif nearest_subway < 1000:
            accessibility_score += 25
        elif nearest_subway < 2000:
            accessibility_score += 10
        
        if nearest_bus < 300:
            accessibility_score += 20
        
        if nearest_university < 3000:
            accessibility_score += 20
        
        if nearest_convenience < 500:
            accessibility_score += 20
        
        return {
            "accessibility_score": accessibility_score,
            "nearest_subway_distance": nearest_subway,
            "nearest_university_distance": nearest_university,
            "nearest_bus_distance": nearest_bus,
            "subway_stations": subway_stations[:5],
            "universities": universities[:3],
            "convenience_stores": convenience_stores[:5]
        }
    
    def generate_static_map_url(
        self,
        coordinates: Coordinates,
        width: int = 800,
        height: int = 600,
        zoom_level: int = 15,
        markers: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        카카오 정적 지도 이미지 URL 생성
        
        Args:
            coordinates: 중심 좌표
            width: 이미지 너비
            height: 이미지 높이
            zoom_level: 확대 레벨 (1-14)
            markers: 마커 정보 리스트 [{'lat': 37.5, 'lng': 127.0, 'text': '위치'}]
            
        Returns:
            정적 지도 이미지 URL
        """
        base_url = "https://dapi.kakao.com/v2/maps/staticmap"
        
        # 기본 파라미터
        params = {
            "center": f"{coordinates.longitude},{coordinates.latitude}",
            "level": zoom_level,
            "marker": f"color:red|{coordinates.longitude},{coordinates.latitude}"
        }
        
        # 추가 마커가 있는 경우
        if markers:
            marker_strings = []
            for m in markers[:10]:  # 최대 10개
                lng = m.get('lng', coordinates.longitude)
                lat = m.get('lat', coordinates.latitude)
                marker_strings.append(f"{lng},{lat}")
            if marker_strings:
                params["marker"] += "|" + "|".join(marker_strings)
        
        # URL 파라미터 구성
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    async def get_static_map_image(
        self,
        coordinates: Coordinates,
        width: int = 800,
        height: int = 600,
        zoom_level: int = 15
    ) -> Optional[str]:
        """
        카카오 정적 지도 이미지를 Base64로 인코딩하여 반환
        
        Args:
            coordinates: 중심 좌표
            width: 이미지 너비
            height: 이미지 높이  
            zoom_level: 확대 레벨
            
        Returns:
            Base64 인코딩된 이미지 문자열 또는 None
        """
        url = f"https://dapi.kakao.com/v2/maps/staticmap"
        params = {
            "center": f"{coordinates.longitude},{coordinates.latitude}",
            "level": zoom_level,
            "marker": f"color:red|{coordinates.longitude},{coordinates.latitude}"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=15.0
                )
                response.raise_for_status()
                
                # 이미지를 Base64로 인코딩
                import base64
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/png;base64,{image_base64}"
                
        except Exception as e:
            print(f"❌ 지도 이미지 생성 실패: {e}")
            return None
