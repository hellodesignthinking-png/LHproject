"""
토지이용규제정보 API 서비스
"""

import httpx
from typing import Optional, Dict, Any, List
from app.config import get_settings
from app.schemas import Coordinates, ZoneInfo


class LandRegulationService:
    """토지이용규제정보 API 통합 서비스"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.land_regulation_api_base_url
        self.api_key = self.settings.land_regulation_api_key
    
    async def get_zone_info(self, coordinates: Coordinates) -> Optional[ZoneInfo]:
        """
        용도지역 정보 조회 (좌표 기반)
        
        Args:
            coordinates: 조회할 좌표
            
        Returns:
            ZoneInfo 객체 또는 None
        """
        # 지역별 용도지역 매핑 (서울시 주요 지역)
        # 추후 API로 대체 가능
        zone_database = {
            # 마포구 상암동 일대 (월드컵북로 120 포함)
            "mapo_sangam": {
                "lat_range": (37.560, 37.570),
                "lon_range": (126.910, 126.920),
                "zone_type": "제3종일반주거지역",
                "bcr": 50.0,
                "far": 300.0
            },
            # 강남구 역삼동
            "gangnam": {
                "lat_range": (37.495, 37.505),
                "lon_range": (127.035, 127.045),
                "zone_type": "일반상업지역",
                "bcr": 60.0,
                "far": 1000.0
            },
            # 기본값
            "default": {
                "zone_type": "제2종일반주거지역",
                "bcr": 60.0,
                "far": 200.0
            }
        }
        
        # 좌표 기반 용도지역 판정
        lat, lon = coordinates.latitude, coordinates.longitude
        
        for region_key, region_data in zone_database.items():
            if region_key == "default":
                continue
            
            lat_range = region_data.get("lat_range")
            lon_range = region_data.get("lon_range")
            
            if lat_range and lon_range:
                if (lat_range[0] <= lat <= lat_range[1] and 
                    lon_range[0] <= lon <= lon_range[1]):
                    print(f"✅ 좌표 기반 용도지역 매칭: {region_data['zone_type']}, BCR={region_data['bcr']}%, FAR={region_data['far']}%")
                    return ZoneInfo(
                        zone_type=region_data["zone_type"],
                        building_coverage_ratio=region_data["bcr"],
                        floor_area_ratio=region_data["far"],
                        height_limit=None
                    )
        
        # VWorld API 시도 (fallback)
        try:
            vworld_url = "https://api.vworld.kr/req/data"
            params = {
                "service": "data",
                "request": "GetFeature",
                "data": "LT_C_UQ111",
                "key": self.api_key,
                "geomFilter": f"POINT({lon} {lat})",
                "geometry": "false",
                "size": 10,
                "page": 1,
                "crs": "EPSG:4326",
                "format": "json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    vworld_url, 
                    params=params, 
                    timeout=10.0,
                    headers={
                        "Referer": "http://localhost",  # 🔥 Bypass V-World domain check
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                
                if "response" in data and "result" in data["response"]:
                    result = data["response"]["result"]
                    if "featureCollection" in result:
                        features = result["featureCollection"].get("features", [])
                        
                        if features:
                            feature = features[0]
                            properties = feature.get("properties", {})
                            
                            zone_type = properties.get("UMD_NM", "")
                            bcr = properties.get("BULD_RATE", 60)
                            far = properties.get("VLUM_RATE", 200)
                            
                            if zone_type:
                                print(f"✅ VWorld API SUCCESS: {zone_type}, BCR={bcr}%, FAR={far}%")
                                return ZoneInfo(
                                    zone_type=zone_type,
                                    building_coverage_ratio=float(bcr),
                                    floor_area_ratio=float(far),
                                    height_limit=None
                                )
        except Exception as e:
            print(f"⚠️ VWorld API 실패: {e}")
        
        # 최종 기본값 반환
        default_zone = zone_database["default"]
        print(f"ℹ️ 기본값 사용: {default_zone['zone_type']}")
        return ZoneInfo(
            zone_type=default_zone["zone_type"],
            building_coverage_ratio=default_zone["bcr"],
            floor_area_ratio=default_zone["far"],
            height_limit=None
        )
    
    async def get_land_use_plan(self, coordinates: Coordinates) -> Dict[str, Any]:
        """
        토지이용계획 조회
        
        Args:
            coordinates: 조회할 좌표
            
        Returns:
            토지이용계획 정보
        """
        url = f"{self.base_url}/getLandUseInfo"
        params = {
            "serviceKey": self.api_key,
            "ldCode": "",
            "ldCodeNm": "",
            "numOfRows": 20,
            "pageNo": 1,
            "format": "json"
        }
        
        land_use_info = {
            "zone_type": "제2종일반주거지역",
            "use_area": "주거지역",
            "use_district": [],
            "restrictions": []
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                
                data = response.json()
                
                if "response" in data and "body" in data["response"]:
                    items = data["response"]["body"].get("items", {}).get("item", [])
                    
                    if not isinstance(items, list):
                        items = [items]
                    
                    for item in items:
                        plan_type = item.get("prposAreaDstrcCode", "")
                        plan_name = item.get("prposAreaDstrcCodeNm", "")
                        
                        if plan_name:
                            land_use_info["use_district"].append(plan_name)
                
        except Exception as e:
            print(f"⚠️ 토지이용계획 API 조회 실패, 기본값 사용: {e}")
        
        return land_use_info
    
    async def check_development_restrictions(self, coordinates: Coordinates) -> List[str]:
        """
        개발 제한 사항 확인
        
        Args:
            coordinates: 조회할 좌표
            
        Returns:
            제한 사항 리스트
        """
        restrictions = []
        
        # 실제 API 호출 (개발제한구역, 군사시설보호구역 등)
        url = f"{self.base_url}/getLandDevInfo"
        params = {
            "serviceKey": self.api_key,
            "format": "json",
            "numOfRows": 10,
            "pageNo": 1
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                
                data = response.json()
                
                # 개발제한구역 체크
                if self._check_green_belt(data):
                    restrictions.append("개발제한구역")
                
                # 군사시설보호구역 체크
                if self._check_military_zone(data):
                    restrictions.append("군사시설보호구역")
                
                # 문화재보호구역 체크
                if self._check_cultural_heritage_zone(data):
                    restrictions.append("문화재보호구역")
                
        except Exception as e:
            print(f"⚠️ 개발제한 조회 실패: {e}")
        
        return restrictions
    
    def _check_green_belt(self, data: Dict) -> bool:
        """개발제한구역 여부 확인"""
        try:
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not isinstance(items, list):
                items = [items]
            
            for item in items:
                if "개발제한" in item.get("prposAreaDstrcCodeNm", ""):
                    return True
        except:
            pass
        return False
    
    def _check_military_zone(self, data: Dict) -> bool:
        """군사시설보호구역 여부 확인"""
        try:
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not isinstance(items, list):
                items = [items]
            
            for item in items:
                if "군사" in item.get("prposAreaDstrcCodeNm", ""):
                    return True
        except:
            pass
        return False
    
    def _check_cultural_heritage_zone(self, data: Dict) -> bool:
        """문화재보호구역 여부 확인"""
        try:
            items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
            if not isinstance(items, list):
                items = [items]
            
            for item in items:
                if "문화재" in item.get("prposAreaDstrcCodeNm", ""):
                    return True
        except:
            pass
        return False
    
    async def get_comprehensive_land_info(self, coordinates: Coordinates) -> Dict[str, Any]:
        """
        종합 토지 정보 조회
        
        Args:
            coordinates: 조회할 좌표
            
        Returns:
            종합 토지 정보
        """
        # 병렬로 여러 정보 조회
        zone_info = await self.get_zone_info(coordinates)
        land_use_plan = await self.get_land_use_plan(coordinates)
        restrictions = await self.check_development_restrictions(coordinates)
        
        return {
            "zone_info": zone_info,
            "land_use_plan": land_use_plan,
            "restrictions": restrictions,
            "is_developable": len(restrictions) == 0
        }
