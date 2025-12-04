"""
ZeroSite v9.0 - GIS Engine
===========================

GIS 엔진 v9.0 - POI 거리 계산, 접근성 평가, 시간 계산

주요 기능:
1. Kakao Maps API 연동 POI 검색 (8개 카테고리)
2. Haversine 거리 계산 + Infinity/NaN 방어
3. 도보 시간 (4km/h) / 차량 시간 (30km/h) 계산
4. 인간 친화적 거리 표시 ("1.2km", "350m")
5. 접근성 점수 계산 (0-100)
6. 개별 POI 점수 (0-10) + 해석

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import asyncio
import logging
import math
import httpx

from app.models_v9.standard_schema_v9_0 import (
    GISResult,
    POIDistance
)
from app.schemas import Coordinates

logger = logging.getLogger(__name__)


@dataclass
class POICategoryConfig:
    """POI 카테고리 설정"""
    category_id: str
    display_name: str
    search_keywords: List[str]
    search_radius: int  # meters
    ideal_distance: int  # meters (이상적 거리)
    max_distance: int    # meters (최대 허용 거리)
    weight: float        # 가중치 (0.0 ~ 1.0)


class GISEngineV90:
    """
    GIS Engine v9.0
    
    주요 개선사항:
    - Infinity/NaN 완벽 방어
    - 도보/차량 시간 계산
    - 정확한 거리 표시
    - 접근성 점수 (0-100)
    - KeyError 제로
    """
    
    # POI 카테고리 정의 (v8.1 기반 + v9.0 확장)
    POI_CATEGORIES: Dict[str, POICategoryConfig] = {
        "elementary_schools": POICategoryConfig(
            category_id="elementary_schools",
            display_name="초등학교",
            search_keywords=["초등학교"],
            search_radius=1500,
            ideal_distance=500,
            max_distance=1000,
            weight=0.15
        ),
        "middle_schools": POICategoryConfig(
            category_id="middle_schools",
            display_name="중학교",
            search_keywords=["중학교"],
            search_radius=2000,
            ideal_distance=800,
            max_distance=1500,
            weight=0.12
        ),
        "high_schools": POICategoryConfig(
            category_id="high_schools",
            display_name="고등학교",
            search_keywords=["고등학교"],
            search_radius=2500,
            ideal_distance=1000,
            max_distance=2000,
            weight=0.10
        ),
        "subway_stations": POICategoryConfig(
            category_id="subway_stations",
            display_name="지하철역",
            search_keywords=["지하철역", "전철역"],
            search_radius=2000,
            ideal_distance=500,
            max_distance=1500,
            weight=0.20
        ),
        "bus_stops": POICategoryConfig(
            category_id="bus_stops",
            display_name="버스정류장",
            search_keywords=["버스정류장"],
            search_radius=500,
            ideal_distance=200,
            max_distance=400,
            weight=0.08
        ),
        "hospitals": POICategoryConfig(
            category_id="hospitals",
            display_name="병원",
            search_keywords=["종합병원", "병원"],
            search_radius=3000,
            ideal_distance=1000,
            max_distance=2500,
            weight=0.15
        ),
        "supermarkets": POICategoryConfig(
            category_id="supermarkets",
            display_name="대형마트",
            search_keywords=["이마트", "롯데마트", "홈플러스", "대형마트"],
            search_radius=2000,
            ideal_distance=800,
            max_distance=1500,
            weight=0.12
        ),
        "parks": POICategoryConfig(
            category_id="parks",
            display_name="공원",
            search_keywords=["공원"],
            search_radius=2000,
            ideal_distance=500,
            max_distance=1500,
            weight=0.08
        )
    }
    
    def __init__(self, kakao_api_key: str):
        """
        GIS Engine 초기화
        
        Args:
            kakao_api_key: Kakao REST API Key
        """
        self.kakao_api_key = kakao_api_key
        logger.info("🌍 GIS Engine v9.0 초기화 완료")
    
    async def analyze_comprehensive_gis(
        self,
        coordinates: Coordinates,
        address: str
    ) -> GISResult:
        """
        종합 GIS 분석 수행
        
        Args:
            coordinates: 대상지 좌표
            address: 대상지 주소
            
        Returns:
            GISResult (정규화된 v9.0 스키마)
        """
        logger.info(f"🌍 GIS 분석 시작: {address}")
        
        # 1. 모든 POI 카테고리 검색
        poi_data = {}
        for category_id, config in self.POI_CATEGORIES.items():
            logger.info(f"  🔍 POI 검색: {config.display_name}")
            pois = await self._search_poi_category(coordinates, config)
            poi_data[category_id] = pois
        
        # 2. 접근성 점수 계산
        accessibility_score = self._calculate_overall_accessibility(poi_data)
        accessibility_grade = self._get_accessibility_grade(accessibility_score)
        
        # 3. GISResult 생성
        result = GISResult(
            elementary_schools=poi_data.get("elementary_schools", []),
            middle_schools=poi_data.get("middle_schools", []),
            high_schools=poi_data.get("high_schools", []),
            subway_stations=poi_data.get("subway_stations", []),
            bus_stops=poi_data.get("bus_stops", []),
            hospitals=poi_data.get("hospitals", []),
            supermarkets=poi_data.get("supermarkets", []),
            parks=poi_data.get("parks", []),
            overall_accessibility_score=accessibility_score,
            accessibility_grade=accessibility_grade
        )
        
        logger.info(f"✅ GIS 분석 완료: 접근성 {accessibility_score:.1f}/100 (등급: {accessibility_grade})")
        return result
    
    async def _search_poi_category(
        self,
        coordinates: Coordinates,
        config: POICategoryConfig
    ) -> List[POIDistance]:
        """
        특정 카테고리 POI 검색 + 정규화
        
        Args:
            coordinates: 중심 좌표
            config: POI 카테고리 설정
            
        Returns:
            List[POIDistance] (최대 3개)
        """
        all_pois = []
        
        for keyword in config.search_keywords:
            try:
                pois = await self._search_kakao_api(
                    coordinates,
                    keyword,
                    config.search_radius
                )
                
                # 중복 제거 (이름 기준)
                for poi in pois:
                    if not any(p["name"] == poi["name"] for p in all_pois):
                        all_pois.append(poi)
            
            except Exception as e:
                logger.warning(f"⚠️ Kakao API 검색 오류 ({keyword}): {e}")
        
        # 거리순 정렬
        all_pois.sort(key=lambda x: x["distance"])
        
        # 상위 3개 + POIDistance로 변환
        result = []
        for poi in all_pois[:3]:
            distance_m = self._safe_float(poi["distance"], 9999.0)
            
            # 거리 표시 + 시간 계산
            distance_display = self._format_distance(distance_m)
            walk_time = self._calculate_walk_time(distance_m)
            drive_time = self._calculate_drive_time(distance_m)
            
            # 접근성 점수 (0-10) + 해석
            acc_score = self._calculate_poi_score(distance_m, config)
            interpretation = self._get_poi_interpretation(acc_score)
            
            poi_distance = POIDistance(
                category=config.category_id,
                name=poi["name"],
                distance_m=distance_m,
                distance_display=distance_display,
                walk_time_min=walk_time,
                drive_time_min=drive_time,
                accessibility_score=acc_score,
                interpretation=interpretation
            )
            result.append(poi_distance)
        
        # 없으면 기본값 추가 (KeyError 방지)
        if not result:
            result.append(POIDistance(
                category=config.category_id,
                name=f"{config.display_name} 없음",
                distance_m=9999.0,
                distance_display="정보 없음",
                walk_time_min=None,
                drive_time_min=None,
                accessibility_score=0.0,
                interpretation="정보 없음"
            ))
        
        return result
    
    async def _search_kakao_api(
        self,
        coordinates: Coordinates,
        keyword: str,
        radius: int
    ) -> List[Dict]:
        """
        Kakao Local API POI 검색
        
        Args:
            coordinates: 중심 좌표
            keyword: 검색 키워드
            radius: 검색 반경 (m)
            
        Returns:
            List[Dict]: POI 목록 (최대 15개)
        """
        try:
            async with httpx.AsyncClient() as client:
                url = "https://dapi.kakao.com/v2/local/search/keyword.json"
                headers = {"Authorization": f"KakaoAK {self.kakao_api_key}"}
                params = {
                    "query": keyword,
                    "x": coordinates.longitude,
                    "y": coordinates.latitude,
                    "radius": radius,
                    "sort": "distance",
                    "size": 15
                }
                
                response = await client.get(url, headers=headers, params=params, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                documents = data.get("documents", [])
                
                # POI 정보 추출
                pois = []
                for doc in documents:
                    pois.append({
                        "name": doc.get("place_name", "Unknown"),
                        "distance": float(doc.get("distance", 9999.0)),
                        "address": doc.get("address_name", ""),
                        "latitude": float(doc.get("y", 0.0)),
                        "longitude": float(doc.get("x", 0.0))
                    })
                
                return pois
        
        except Exception as e:
            logger.error(f"❌ Kakao API 오류: {e}")
            return []
    
    def _calculate_poi_score(
        self,
        distance: float,
        config: POICategoryConfig
    ) -> float:
        """
        POI 접근성 점수 계산 (0-10)
        
        거리 기반 점수:
        - 이상적 거리 이내: 10점
        - 최대 거리 이내: 선형 감소
        - 최대 거리 초과: 0점
        
        Args:
            distance: 거리 (m)
            config: POI 카테고리 설정
            
        Returns:
            float (0.0 ~ 10.0)
        """
        if distance <= config.ideal_distance:
            return 10.0
        elif distance <= config.max_distance:
            # 선형 감소
            ratio = (config.max_distance - distance) / (config.max_distance - config.ideal_distance)
            return round(10.0 * ratio, 1)
        else:
            return 0.0
    
    def _get_poi_interpretation(self, score: float) -> str:
        """POI 점수 해석"""
        if score >= 9.0:
            return "매우 우수"
        elif score >= 7.0:
            return "우수"
        elif score >= 5.0:
            return "보통"
        elif score >= 3.0:
            return "미흡"
        else:
            return "불량"
    
    def _calculate_overall_accessibility(self, poi_data: Dict[str, List[POIDistance]]) -> float:
        """
        전체 접근성 점수 계산 (0-100)
        
        각 카테고리의 대표 POI (첫 번째)를 기준으로 가중 평균
        
        Args:
            poi_data: 카테고리별 POI 목록
            
        Returns:
            float (0-100)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for category_id, pois in poi_data.items():
            if not pois:
                continue
            
            # 첫 번째 POI의 점수 사용
            poi_score = pois[0].accessibility_score  # 0-10
            config = self.POI_CATEGORIES.get(category_id)
            
            if config:
                weighted_score = poi_score * config.weight * 10  # 0-100 변환
                total_score += weighted_score
                total_weight += config.weight
        
        # 가중 평균
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0.0
        
        return round(final_score, 1)
    
    def _get_accessibility_grade(self, score: float) -> str:
        """접근성 등급 산출"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _format_distance(self, distance: float) -> str:
        """
        거리 포맷팅 (인간 친화적)
        
        예: 350m, 1.2km
        """
        if math.isnan(distance) or math.isinf(distance):
            return "정보 없음"
        
        if distance < 1000:
            return f"{int(distance)}m"
        else:
            km = distance / 1000
            return f"{km:.1f}km"
    
    def _calculate_walk_time(self, distance: float) -> Optional[int]:
        """
        도보 시간 계산 (분)
        
        가정: 도보 속도 4km/h
        """
        if math.isnan(distance) or math.isinf(distance) or distance >= 9000:
            return None
        
        # 4km/h = 66.67m/min
        walk_time = distance / 66.67
        return max(1, int(round(walk_time)))
    
    def _calculate_drive_time(self, distance: float) -> Optional[int]:
        """
        차량 시간 계산 (분)
        
        가정: 시내 평균 속도 30km/h
        """
        if math.isnan(distance) or math.isinf(distance) or distance >= 9000:
            return None
        
        # 30km/h = 500m/min
        drive_time = distance / 500
        return max(1, int(round(drive_time)))
    
    def _safe_float(self, value: any, default: float = 0.0) -> float:
        """
        안전한 float 변환 (Infinity/NaN 방어)
        
        Args:
            value: 변환할 값
            default: 기본값
            
        Returns:
            float (정상 값 또는 기본값)
        """
        try:
            f = float(value)
            if math.isnan(f) or math.isinf(f):
                return default
            return f
        except:
            return default
