"""
행정안전부 공공데이터 API 서비스
"""

import httpx
from typing import Optional, Dict, Any
from app.config import get_settings
from app.schemas import Coordinates, DemographicInfo


class MOISService:
    """행정안전부 주민등록 인구통계 API 서비스"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.mois_api_base_url
        self.api_key = self.settings.mois_api_key
    
    async def get_administrative_code(self, address: str) -> Optional[str]:
        """
        주소로부터 행정구역코드 추출
        
        Args:
            address: 주소
            
        Returns:
            행정구역코드 (시군구 코드)
        """
        # 주소에서 시군구 추출 (간단한 파싱)
        # 예: "서울특별시 강남구 역삼동" -> "11680" (강남구 코드)
        
        # 주요 행정구역 코드 매핑 (실제로는 더 정교한 매핑 필요)
        code_mapping = {
            "강남구": "11680",
            "서초구": "11650",
            "송파구": "11710",
            "강동구": "11740",
            "마포구": "11440",
            "용산구": "11170",
            "성동구": "11200",
            "광진구": "11215",
            "동대문구": "11230",
            "성북구": "11290",
            "도봉구": "11320",
            "노원구": "11350",
            "은평구": "11380",
            "서대문구": "11410",
            "종로구": "11110",
            "중구": "11140",
            "양천구": "11470",
            "강서구": "11500",
            "구로구": "11530",
            "금천구": "11545",
            "영등포구": "11560",
            "동작구": "11590",
            "관악구": "11620",
        }
        
        for district, code in code_mapping.items():
            if district in address:
                return code
        
        # 기본값: 강남구
        return "11680"
    
    async def get_population_by_age(self, admin_code: str) -> Optional[DemographicInfo]:
        """
        행정구역별 연령대별 인구 조회
        
        Args:
            admin_code: 행정구역코드
            
        Returns:
            DemographicInfo 객체
        """
        # 실제 API 엔드포인트
        url = f"{self.base_url}/getPopulationByAge"
        params = {
            "serviceKey": self.api_key,
            "admCode": admin_code,
            "numOfRows": 100,
            "pageNo": 1,
            "format": "json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                
                data = response.json()
                
                # API 응답 구조에 따라 파싱
                if "response" in data and "body" in data["response"]:
                    items = data["response"]["body"].get("items", {}).get("item", [])
                    
                    if not isinstance(items, list):
                        items = [items]
                    
                    total_pop = 0
                    youth_pop = 0  # 20-39세
                    
                    for item in items:
                        age = item.get("age", "")
                        population = int(item.get("population", 0))
                        
                        total_pop += population
                        
                        # 청년 인구 집계 (20-39세)
                        try:
                            age_num = int(age)
                            if 20 <= age_num <= 39:
                                youth_pop += population
                        except:
                            pass
                    
                    if total_pop > 0:
                        return DemographicInfo(
                            total_population=total_pop,
                            youth_population=youth_pop,
                            youth_ratio=round((youth_pop / total_pop) * 100, 2),
                            single_households=int(total_pop * 0.31),  # 평균 1인가구 비율
                            single_household_ratio=31.0
                        )
                
        except Exception as e:
            print(f"⚠️ 인구통계 API 조회 실패, 기본값 사용: {e}")
        
        # API 실패 시 기본값 반환 (서울시 평균 기준)
        return DemographicInfo(
            total_population=500000,
            youth_population=150000,
            youth_ratio=30.0,
            single_households=155000,
            single_household_ratio=31.0
        )
    
    async def get_household_info(self, admin_code: str) -> Dict[str, Any]:
        """
        가구 정보 조회
        
        Args:
            admin_code: 행정구역코드
            
        Returns:
            가구 정보 딕셔너리
        """
        url = f"{self.base_url}/getHouseholdInfo"
        params = {
            "serviceKey": self.api_key,
            "admCode": admin_code,
            "numOfRows": 10,
            "pageNo": 1,
            "format": "json"
        }
        
        household_info = {
            "total_households": 200000,
            "single_households": 62000,
            "two_person_households": 50000,
            "three_person_households": 45000,
            "four_plus_households": 43000
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
                        household_type = item.get("householdType", "")
                        count = int(item.get("count", 0))
                        
                        if "1인" in household_type:
                            household_info["single_households"] = count
                        elif "2인" in household_type:
                            household_info["two_person_households"] = count
                        elif "3인" in household_type:
                            household_info["three_person_households"] = count
                
        except Exception as e:
            print(f"⚠️ 가구정보 API 조회 실패, 기본값 사용: {e}")
        
        return household_info
    
    async def analyze_demographics(self, address: str, coordinates: Coordinates) -> DemographicInfo:
        """
        인구통계 종합 분석
        
        Args:
            address: 주소
            coordinates: 좌표
            
        Returns:
            DemographicInfo 객체
        """
        # 행정구역코드 추출
        admin_code = await self.get_administrative_code(address)
        
        # 인구 정보 조회
        demographic_info = await self.get_population_by_age(admin_code)
        
        # 가구 정보 조회 및 보강
        household_info = await self.get_household_info(admin_code)
        
        if demographic_info:
            # 가구 정보로 1인가구 수 업데이트
            demographic_info.single_households = household_info["single_households"]
            demographic_info.single_household_ratio = round(
                (household_info["single_households"] / household_info["total_households"]) * 100,
                2
            )
        
        return demographic_info
    
    async def calculate_demand_indicators(
        self,
        demographic_info: DemographicInfo,
        unit_type: str
    ) -> Dict[str, Any]:
        """
        수요 지표 계산
        
        Args:
            demographic_info: 인구통계 정보
            unit_type: 세대 유형
            
        Returns:
            수요 지표 딕셔너리
        """
        demand_indicators = {
            "target_population": 0,
            "market_size_score": 0,
            "demographic_fit_score": 0
        }
        
        # 세대 유형별 타겟 인구 계산
        if unit_type == "청년형":
            demand_indicators["target_population"] = demographic_info.youth_population
            demand_indicators["demographic_fit_score"] = min(demographic_info.youth_ratio * 2, 100)
        
        elif unit_type == "신혼부부형":
            # 25-35세 인구 추정 (청년 인구의 60%)
            demand_indicators["target_population"] = int(demographic_info.youth_population * 0.6)
            demand_indicators["demographic_fit_score"] = min(demographic_info.youth_ratio * 1.8, 100)
        
        elif unit_type == "고령자형":
            # 65세 이상 추정 (전체 인구의 15%)
            demand_indicators["target_population"] = int(demographic_info.total_population * 0.15)
            demand_indicators["demographic_fit_score"] = 50
        
        # 시장 규모 점수 (타겟 인구에 비례)
        if demand_indicators["target_population"] > 100000:
            demand_indicators["market_size_score"] = 100
        elif demand_indicators["target_population"] > 50000:
            demand_indicators["market_size_score"] = 80
        elif demand_indicators["target_population"] > 20000:
            demand_indicators["market_size_score"] = 60
        else:
            demand_indicators["market_size_score"] = 40
        
        return demand_indicators
