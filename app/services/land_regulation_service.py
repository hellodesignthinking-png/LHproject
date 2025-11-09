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
        용도지역 정보 조회
        
        Args:
            coordinates: 조회할 좌표
            
        Returns:
            ZoneInfo 객체 또는 None
        """
        # 실제 API 엔드포인트: /getZoneLandInfo
        url = f"{self.base_url}/getZoneLandInfo"
        params = {
            "serviceKey": self.api_key,
            "pnu": "",  # PNU 코드 (필요시 좌표→PNU 변환 필요)
            "ldCode": "",
            "ldCodeNm": "",
            "numOfRows": 10,
            "pageNo": 1,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                
                data = response.json()
                
                # API 응답 구조에 따라 파싱 (실제 응답 구조 확인 필요)
                if "response" in data and "body" in data["response"]:
                    items = data["response"]["body"].get("items", {}).get("item", [])
                    
                    if items:
                        item = items[0] if isinstance(items, list) else items
                        
                        return ZoneInfo(
                            zone_type=item.get("zoneNm", "제2종일반주거지역"),
                            building_coverage_ratio=float(item.get("bcRat", 60)),
                            floor_area_ratio=float(item.get("vlRat", 200)),
                            height_limit=item.get("htLmt")
                        )
                
        except Exception as e:
            print(f"⚠️ 용도지역 API 조회 실패, 기본값 사용: {e}")
        
        # API 실패 시 기본값 반환 (일반적인 제2종일반주거지역 기준)
        return ZoneInfo(
            zone_type="제2종일반주거지역",
            building_coverage_ratio=60.0,
            floor_area_ratio=200.0,
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
