"""
Geo Optimizer - ZeroSite Land Report v5.0
지리적 최적 위치 분석 및 추천 서비스
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from dataclasses import dataclass


class OptimizedSite(BaseModel):
    """최적화된 입지 정보"""
    site_id: str
    latitude: float
    longitude: float
    address: str
    
    # 점수
    overall_score: float  # 종합 점수 (0-100)
    accessibility_score: float  # 접근성 점수
    demand_score: float  # 수요 점수
    infrastructure_score: float  # 인프라 점수
    environment_score: float  # 환경 점수
    
    # 거리 정보
    subway_distance: Optional[float] = None
    school_distance: Optional[float] = None
    hospital_distance: Optional[float] = None
    market_distance: Optional[float] = None
    
    # 특징
    strengths: List[str] = []
    weaknesses: List[str] = []
    
    # 추천 이유
    recommendation_reason: str = ""


class GeoOptimizationResult(BaseModel):
    """지리적 최적화 결과"""
    analyzed_location: Dict[str, Any]  # 원래 입력 위치 (lat, lng, address)
    optimization_score: float  # 최적화 점수 (0-100)
    
    recommended_sites: List[OptimizedSite] = []  # 추천 대안 위치 (최대 5개)
    
    # 분석 요약
    current_site_strengths: List[str] = []
    current_site_weaknesses: List[str] = []
    optimization_suggestions: List[str] = []


class GeoOptimizer:
    """지리적 최적화 분석 엔진"""
    
    def __init__(self):
        """초기화"""
        self.weights = {
            "accessibility": 0.35,  # 접근성 가중치
            "demand": 0.30,  # 수요 가중치
            "infrastructure": 0.20,  # 인프라 가중치
            "environment": 0.15,  # 환경 가중치
        }
        
        # 거리 기준 (미터)
        self.distance_thresholds = {
            "subway": {"excellent": 500, "good": 1000, "acceptable": 1500},
            "school": {"excellent": 400, "good": 800, "acceptable": 1200},
            "hospital": {"excellent": 500, "good": 1000, "acceptable": 2000},
            "market": {"excellent": 300, "good": 600, "acceptable": 1000},
        }
    
    def optimize(
        self,
        latitude: float,
        longitude: float,
        address: str,
        accessibility: Dict[str, Any],
        demographic_info: Optional[Any] = None,
        zone_info: Optional[Any] = None
    ) -> GeoOptimizationResult:
        """
        지리적 최적화 분석 수행
        
        Args:
            latitude: 위도
            longitude: 경도
            address: 주소
            accessibility: 접근성 정보
            demographic_info: 인구통계 정보
            zone_info: 용도지역 정보
            
        Returns:
            GeoOptimizationResult: 최적화 결과
        """
        # 1. 현재 위치 점수 계산
        current_scores = self._calculate_scores(
            accessibility, demographic_info, zone_info
        )
        
        overall_score = (
            current_scores["accessibility"] * self.weights["accessibility"] +
            current_scores["demand"] * self.weights["demand"] +
            current_scores["infrastructure"] * self.weights["infrastructure"] +
            current_scores["environment"] * self.weights["environment"]
        )
        
        # 2. 현재 위치 강약점 분석
        strengths, weaknesses = self._analyze_current_site(
            accessibility, current_scores
        )
        
        # 3. 최적화 제안 생성
        suggestions = self._generate_optimization_suggestions(
            current_scores, weaknesses, accessibility
        )
        
        # 4. 추천 대안 위치 생성 (반경 2km 내 가상 최적 지점)
        recommended_sites = self._generate_recommended_sites(
            latitude, longitude, address, accessibility, current_scores
        )
        
        return GeoOptimizationResult(
            analyzed_location={
                "latitude": latitude,
                "longitude": longitude,
                "address": address
            },
            optimization_score=round(overall_score, 1),
            recommended_sites=recommended_sites,
            current_site_strengths=strengths,
            current_site_weaknesses=weaknesses,
            optimization_suggestions=suggestions
        )
    
    def _calculate_scores(
        self,
        accessibility: Dict[str, Any],
        demographic_info: Optional[Any],
        zone_info: Optional[Any]
    ) -> Dict[str, float]:
        """각 항목별 점수 계산"""
        scores = {}
        
        # 접근성 점수 (0-100)
        base_accessibility = accessibility.get("accessibility_score", 50)
        scores["accessibility"] = min(base_accessibility, 100)
        
        # 수요 점수 (0-100)
        demand_score = 50.0
        if demographic_info:
            # 청년인구 비율 기반
            youth_ratio = getattr(demographic_info, "youth_ratio", 25.0)
            demand_score += min(youth_ratio * 1.5, 40)
        
        # 지하철 거리 보정
        subway_dist = accessibility.get("nearest_subway_distance", 9999)
        if subway_dist < 500:
            demand_score += 10
        elif subway_dist < 1000:
            demand_score += 5
        
        scores["demand"] = min(demand_score, 100)
        
        # 인프라 점수 (0-100)
        infrastructure_score = 50.0
        school_dist = accessibility.get("nearest_school_distance", 9999)
        hospital_dist = accessibility.get("nearest_hospital_distance", 9999)
        
        if school_dist < 500:
            infrastructure_score += 20
        elif school_dist < 1000:
            infrastructure_score += 10
        
        if hospital_dist < 500:
            infrastructure_score += 20
        elif hospital_dist < 1000:
            infrastructure_score += 10
        
        scores["infrastructure"] = min(infrastructure_score, 100)
        
        # 환경 점수 (0-100)
        environment_score = 70.0  # 기본값
        if zone_info and "주거" in getattr(zone_info, "zone_type", ""):
            environment_score += 15
        
        scores["environment"] = min(environment_score, 100)
        
        return scores
    
    def _analyze_current_site(
        self,
        accessibility: Dict[str, Any],
        scores: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """현재 위치의 강약점 분석"""
        strengths = []
        weaknesses = []
        
        # 접근성 분석
        subway_dist = accessibility.get("nearest_subway_distance", 9999)
        if subway_dist < 500:
            strengths.append(f"지하철역 {int(subway_dist)}m - 매우 우수한 대중교통 접근성")
        elif subway_dist < 1000:
            strengths.append(f"지하철역 {int(subway_dist)}m - 양호한 대중교통 접근성")
        elif subway_dist > 1500:
            weaknesses.append(f"지하철역 {int(subway_dist)}m - 대중교통 접근성 개선 필요")
        
        # 학교 거리
        school_dist = accessibility.get("nearest_school_distance", 9999)
        if school_dist < 500:
            strengths.append(f"학교 {int(school_dist)}m - 교육 인프라 우수")
        elif school_dist > 1200:
            weaknesses.append(f"학교 {int(school_dist)}m - 교육 시설 접근성 불리")
        
        # 병원 거리
        hospital_dist = accessibility.get("nearest_hospital_distance", 9999)
        if hospital_dist < 500:
            strengths.append(f"병원 {int(hospital_dist)}m - 의료 인프라 우수")
        elif hospital_dist > 2000:
            weaknesses.append(f"병원 {int(hospital_dist)}m - 의료 시설 접근성 불리")
        
        # 종합 점수 기반
        if scores["accessibility"] >= 80:
            strengths.append("전반적으로 우수한 입지 조건")
        elif scores["accessibility"] < 50:
            weaknesses.append("입지 조건 개선이 필요함")
        
        return strengths, weaknesses
    
    def _generate_optimization_suggestions(
        self,
        scores: Dict[str, float],
        weaknesses: List[str],
        accessibility: Dict[str, Any]
    ) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []
        
        # 접근성 개선
        if scores["accessibility"] < 70:
            subway_dist = accessibility.get("nearest_subway_distance", 9999)
            if subway_dist > 1000:
                suggestions.append(
                    f"지하철역 접근성 개선: 현재 {int(subway_dist)}m → 800m 이내 위치 권장"
                )
        
        # 수요 개선
        if scores["demand"] < 60:
            suggestions.append("청년/신혼부부 유입이 높은 지역으로 위치 조정 권장")
        
        # 인프라 개선
        if scores["infrastructure"] < 60:
            suggestions.append("학교, 병원 등 생활 인프라 밀집 지역 탐색 권장")
        
        # 종합 제안
        if len(weaknesses) >= 3:
            suggestions.append("현재 위치의 약점이 다수 발견됨. 대안 위치 검토를 강력히 권장합니다.")
        
        return suggestions
    
    def _generate_recommended_sites(
        self,
        latitude: float,
        longitude: float,
        address: str,
        accessibility: Dict[str, Any],
        current_scores: Dict[str, float]
    ) -> List[OptimizedSite]:
        """추천 대안 위치 생성"""
        recommended = []
        
        # 반경 1-2km 내 가상 최적 지점 생성 (실제로는 POI 기반으로 계산)
        # 여기서는 예시로 4방향 지점 생성
        directions = [
            {"name": "북측", "lat_offset": 0.01, "lng_offset": 0},
            {"name": "남측", "lat_offset": -0.01, "lng_offset": 0},
            {"name": "동측", "lat_offset": 0, "lng_offset": 0.015},
            {"name": "서측", "lat_offset": 0, "lng_offset": -0.015},
        ]
        
        for idx, direction in enumerate(directions):
            new_lat = latitude + direction["lat_offset"]
            new_lng = longitude + direction["lng_offset"]
            
            # 점수 시뮬레이션 (실제로는 해당 위치의 실제 데이터 기반)
            simulated_score = current_scores["accessibility"] + (idx + 1) * 2
            simulated_score = min(simulated_score, 95)
            
            site = OptimizedSite(
                site_id=f"ALT_{idx+1:02d}",
                latitude=new_lat,
                longitude=new_lng,
                address=f"{address} {direction['name']} 약 1km 지점",
                overall_score=round(simulated_score, 1),
                accessibility_score=round(simulated_score - 5, 1),
                demand_score=round(current_scores["demand"] + 3, 1),
                infrastructure_score=round(current_scores["infrastructure"] + 2, 1),
                environment_score=round(current_scores["environment"], 1),
                subway_distance=accessibility.get("nearest_subway_distance", 9999) - 200,
                school_distance=accessibility.get("nearest_school_distance", 9999) - 100,
                hospital_distance=accessibility.get("nearest_hospital_distance", 9999) - 150,
                strengths=[
                    f"{direction['name']} 방향으로 접근성 개선",
                    "대중교통 접근성 향상",
                    "생활 인프라 밀집 지역"
                ],
                weaknesses=["현장 실사 필요", "토지 매물 확인 필요"],
                recommendation_reason=f"{direction['name']} 방향으로 {idx+1}km 이동 시 입지 점수 {(idx+1)*2}점 향상 예상"
            )
            
            recommended.append(site)
        
        # 점수 순으로 정렬
        recommended.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 상위 3개만 반환
        return recommended[:3]


# 전역 인스턴스
_geo_optimizer = None

def get_geo_optimizer() -> GeoOptimizer:
    """Geo Optimizer 싱글톤 인스턴스 반환"""
    global _geo_optimizer
    if _geo_optimizer is None:
        _geo_optimizer = GeoOptimizer()
    return _geo_optimizer
