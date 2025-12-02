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
            # Real API only - No fallback to mock data
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
            # Real API only - Return empty list on error
        
        return facilities
    
    async def search_hazardous_facilities(self, coordinates: Coordinates, unit_type: str = None) -> List[Dict[str, Any]]:
        """
        유해시설 검색 (LH 매입 제외 기준)
        
        Args:
            coordinates: 중심 좌표
            unit_type: 세대 유형 (다자녀형일 경우 2순위 시설도 체크)
            
        Returns:
            유해시설 리스트 (distance, is_critical 포함)
        """
        # LH 유해시설 기준 (절대 제외 기준만 적용)
        # 1순위: 절대 제외 (25m 이내 무조건 탈락)
        # 2순위: 제외 가능 (다자녀 유형 주택의 경우)
        hazardous_categories = {
            # 1순위: 절대 제외 시설 (25m 기준)
            "주유소": {"radius": 50, "critical_distance": 25, "priority": 1},
            "석유판매취급소": {"radius": 50, "critical_distance": 25, "priority": 1},
            "충전소": {"radius": 50, "critical_distance": 25, "priority": 1},  # 천연가스충전소 포함
            "LPG충전소": {"radius": 50, "critical_distance": 25, "priority": 1},
            "위험물저장소": {"radius": 50, "critical_distance": 25, "priority": 1},
            "위험물제조소": {"radius": 50, "critical_distance": 25, "priority": 1},
            
            # 2순위: 제외 가능 시설 (다자녀 유형만 해당)
            "숙박시설": {"radius": 50, "critical_distance": 25, "priority": 2},
            "모텔": {"radius": 50, "critical_distance": 25, "priority": 2},
            "위락시설": {"radius": 50, "critical_distance": 25, "priority": 2}
        }
        
        all_hazardous = []
        
        for category, config in hazardous_categories.items():
            # 2순위 시설은 다자녀형일 때만 체크
            if config.get("priority") == 2 and unit_type != "다자녀":
                continue  # 다자녀형이 아니면 2순위 시설은 체크 안함
            
            facilities = await self.search_nearby_facilities(
                coordinates,
                category,
                radius=config["radius"]
            )
            
            for facility in facilities:
                # 제외 키워드: 일반 상업시설 등은 유해시설이 아님
                exclude_keywords = [
                    "재활용", "자원회수", "재활용센터", "자원순환",  # 재활용 시설
                    "정육점", "고기", "육류", "축산물",  # 정육점/정육 판매
                    "정肉", "肉",  # 정육점 한자 표기
                    "식품", "마트", "슈퍼"  # 일반 식품 판매점
                ]
                is_excluded = any(keyword in facility.name for keyword in exclude_keywords)
                if is_excluded:
                    continue  # 제외 대상
                
                is_critical = facility.distance <= config["critical_distance"]
                priority = config.get("priority", 1)
                
                all_hazardous.append({
                    "name": facility.name,
                    "category": category,
                    "distance": facility.distance,
                    "address": facility.address,
                    "is_critical": is_critical,  # LH 탈락 사유 여부
                    "critical_distance": config["critical_distance"],
                    "priority": priority  # 1=절대제외, 2=다자녀만
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
        # 주요 시설별 검색 (ZeroSite v6.1 - 학교/병원 추가)
        subway_stations = await self.search_nearby_facilities(coordinates, "지하철역", 2000)
        universities = await self.search_nearby_facilities(coordinates, "대학교", 3000)
        bus_stops = await self.search_nearby_facilities(coordinates, "버스정류장", 500)
        convenience_stores = await self.search_nearby_facilities(coordinates, "편의점", 1000)
        
        # v6.1 추가: 학교 (초등/중학교) 및 병원 검색
        elementary_schools = await self.search_nearby_facilities(coordinates, "초등학교", 1500)
        middle_schools = await self.search_nearby_facilities(coordinates, "중학교", 1500)
        hospitals = await self.search_nearby_facilities(coordinates, "병원", 2000)
        
        # 최단 거리 계산
        nearest_subway = min([f.distance for f in subway_stations], default=9999)
        nearest_university = min([f.distance for f in universities], default=9999)
        nearest_bus = min([f.distance for f in bus_stops], default=9999)
        nearest_convenience = min([f.distance for f in convenience_stores], default=9999)
        
        # v6.1 추가: 학교/병원 최단 거리 계산
        nearest_elementary_school = min([f.distance for f in elementary_schools], default=9999)
        nearest_middle_school = min([f.distance for f in middle_schools], default=9999)
        nearest_school = min(nearest_elementary_school, nearest_middle_school)
        nearest_hospital = min([f.distance for f in hospitals], default=9999)
        
        # 디버그 로깅 (v6.1 - 거리 계산 검증용)
        print(f"    🔍 [POI Distance Debug] 초등학교: {nearest_elementary_school}m, 중학교: {nearest_middle_school}m → 최종 학교: {nearest_school}m")
        print(f"    🔍 [POI Distance Debug] 병원: {nearest_hospital}m")
        
        # 접근성 점수 계산 (100점 만점)
        accessibility_score = 0
        
        # 지하철역 점수 (최대 40점)
        if nearest_subway < 500:
            accessibility_score += 40
        elif nearest_subway < 1000:
            accessibility_score += 25
        elif nearest_subway < 2000:
            accessibility_score += 10
        
        # 버스정류장 점수 (최대 20점)
        if nearest_bus < 300:
            accessibility_score += 20
        
        # 대학교 점수 (최대 20점)
        if nearest_university < 3000:
            accessibility_score += 20
        
        # 편의점 점수 (최대 20점)
        if nearest_convenience < 500:
            accessibility_score += 20
        
        return {
            "accessibility_score": accessibility_score,
            "nearest_subway_distance": nearest_subway,
            "nearest_university_distance": nearest_university,
            "nearest_bus_distance": nearest_bus,
            "nearest_convenience_distance": nearest_convenience,
            # v6.1 추가: 학교 및 병원 거리
            "nearest_school_distance": nearest_school,
            "nearest_elementary_school_distance": nearest_elementary_school,
            "nearest_middle_school_distance": nearest_middle_school,
            "nearest_hospital_distance": nearest_hospital,
            # 시설 리스트
            "subway_stations": subway_stations[:5],
            "universities": universities[:3],
            "convenience_stores": convenience_stores[:5],
            "schools": (elementary_schools + middle_schools)[:5],
            "hospitals": hospitals[:3]
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
        zoom_level: int = 3,
        markers: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """
        카카오 정적 지도 이미지를 Base64로 인코딩하여 반환 (마커 포함)
        
        Args:
            coordinates: 중심 좌표 (대상지)
            width: 이미지 너비
            height: 이미지 높이  
            zoom_level: 확대 레벨 (1~14, 작을수록 확대)
            markers: 추가 마커 리스트 [{"lat": 37.5, "lng": 127.0, "color": "blue"}]
            
        Returns:
            Base64 인코딩된 이미지 문자열 또는 None
        """
        url = "https://dapi.kakao.com/v2/maps/staticmap"
        
        # 기본 파라미터
        params = {
            "center": f"{coordinates.longitude},{coordinates.latitude}",
            "level": zoom_level
        }
        
        # 마커 구성: 대상지는 빨간색 큰 마커
        marker_param = f"color:red|{coordinates.longitude},{coordinates.latitude}"
        
        # 추가 마커 (주요 시설 등 - 파란색)
        if markers:
            for marker in markers[:10]:  # 최대 10개
                lng = marker.get("lng")
                lat = marker.get("lat")
                color = marker.get("color", "blue")
                if lng and lat:
                    marker_param += f"|color:{color}|{lng},{lat}"
        
        params["marker"] = marker_param
        
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
    
    async def get_multiple_maps(
        self,
        coordinates: Coordinates,
        nearby_facilities: List[Dict[str, Any]] = None
    ) -> Dict[str, Optional[str]]:
        """
        여러 스케일의 지도 이미지를 생성
        
        Args:
            coordinates: 중심 좌표
            nearby_facilities: 주변 시설 리스트 (마커 표시용)
            
        Returns:
            Dict with 'overview', 'detail', 'facilities' 지도 이미지
        """
        maps = {}
        
        # 광역 지도 (큰 범위)
        maps['overview'] = await self.get_static_map_image(
            coordinates, zoom_level=6
        )
        
        # 상세 지도 (중간 범위)
        maps['detail'] = await self.get_static_map_image(
            coordinates, zoom_level=3
        )
        
        # 근접 지도 (작은 범위)
        maps['close'] = await self.get_static_map_image(
            coordinates, zoom_level=1
        )
        
        return maps
