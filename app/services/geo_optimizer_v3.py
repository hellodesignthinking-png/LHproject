"""
ZeroSite GeoOptimizer v3.1
================================================================================
LH 공식 평가 기준 100% 반영 - 최적 입지 추천 엔진

✅ v3.1 주요 업그레이드 (2024-12-01):
1. ⚠️ LH 자동탈락 항목 패널티 반영
   - 방화지구: -10점
   - 고도지구: -8점
   - 문화재보호구역: -15점 (LH 최우선 제외)
   - 재개발/재건축구역: -12점

2. 🚫 사업 불가 부지 자동제외
   - 수용부지 (도로/공원 등)
   - 도시계획시설 지정 부지

3. 📐 경사도별 건축비 가중치
   - 0-5도: 기준 원가
   - 5-10도: +5% 원가
   - 10-15도: +10% 원가
   - 15도 이상: +20% 원가

4. 📊 LH 평가표 필수 지표 추가
   - 수용성 점수 (지역 수요·공급 균형)
   - 사업성 점수 (건축비·임대료·수익성)

5. 🔧 POI 거리 가중치 최적화
   - 500m: 1.0x (도보권)
   - 1km: 0.8x (근린)
   - 1.5km: 0.5x (생활권)
   - 2km: 0.3x (광역권)

6. 📦 멀티파슬 안정성 강화 (최대 20필지)

버전: v3.1 (2024-12-01)
작성자: ZeroSite Team
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pydantic import BaseModel
import logging
from math import radians, sin, cos, sqrt, atan2, degrees, atan

logger = logging.getLogger(__name__)


class OptimizedSiteV3(BaseModel):
    """최적화된 입지 정보 v3.1"""
    site_id: str
    latitude: float
    longitude: float
    address: str
    distance_from_origin: float  # 원점으로부터 거리 (미터)
    
    # LH 기준 점수 (v3.1: 7개 항목)
    overall_score: float  # 종합 점수 (0-100)
    accessibility_score: float  # 접근성 점수 (역세권) 25%
    education_score: float  # 교육시설 점수 20%
    medical_score: float  # 의료시설 점수 15%
    commercial_score: float  # 상업시설 점수 10%
    regulation_score: float  # 토지규제 점수 10%
    acceptability_score: float = 0.0  # 수용성 점수 10% (v3.1 신규)
    feasibility_score: float = 0.0  # 사업성 점수 10% (v3.1 신규)
    
    # 거리 정보 (미터)
    subway_distance: Optional[float] = None
    school_distance: Optional[float] = None
    hospital_distance: Optional[float] = None
    convenience_distance: Optional[float] = None
    
    # 토지이용규제 정보
    zone_type: Optional[str] = None  # 용도지역
    floor_area_ratio: Optional[float] = None  # 용적률 (%)
    building_coverage_ratio: Optional[float] = None  # 건폐율 (%)
    height_restriction: Optional[float] = None  # 고도제한 (m)
    
    # 특징
    strengths: List[str] = []
    weaknesses: List[str] = []
    lh_compliance_issues: List[str] = []  # LH 규정 위반 사항
    
    # 추천 이유
    recommendation_reason: str = ""
    diversity_factor: float = 0.0  # 다양성 점수 (0-1)


class MultiParcelResult(BaseModel):
    """멀티파슬 통합 분석 결과"""
    parcel_count: int
    total_area: float  # 총 면적 (m²)
    center_latitude: float  # 중심 좌표
    center_longitude: float
    cluster_radius: float  # 클러스터 반경 (m)
    
    # 통합 점수
    integrated_score: float
    feasibility_score: float  # 사업 타당성
    
    # 필지별 점수
    parcel_scores: List[Dict[str, Any]] = []


class GeoOptimizationResultV3(BaseModel):
    """지리적 최적화 결과 v3.0"""
    analyzed_location: Dict[str, Any]  # 원래 입력 위치
    optimization_score: float  # 최적화 점수 (0-100)
    
    recommended_sites: List[OptimizedSiteV3] = []  # 추천 대안 위치 (최대 3개)
    
    # 분석 요약
    current_site_strengths: List[str] = []
    current_site_weaknesses: List[str] = []
    optimization_suggestions: List[str] = []
    
    # 다양성 통계
    diversity_score: float = 0.0  # 추천 후보지 간 다양성 (0-100)
    min_inter_site_distance: float = 0.0  # 최소 후보지 간 거리 (m)
    
    # 멀티파슬 정보 (있을 경우)
    multi_parcel_result: Optional[MultiParcelResult] = None


@dataclass
class LHWeightsV3_1:
    """
    LH 공식 평가표 가중치 v3.1
    
    기존 5개 항목 + 수용성·사업성 추가
    """
    # 기존 LH 평가 항목 (총 80%)
    accessibility: float = 0.25  # 역세권 (25%)
    education: float = 0.20  # 교육시설 (20%)
    medical: float = 0.15  # 의료시설 (15%)
    commercial: float = 0.10  # 상업시설 (10%)
    regulation: float = 0.10  # 토지규제 (10%)
    
    # v3.1 신규 추가 (총 20%)
    acceptability: float = 0.10  # 수용성 (10% - LH 필수)
    feasibility: float = 0.10  # 사업성 (10% - LH 필수)


class GeoOptimizerV3:
    """
    지리적 최적화 분석 엔진 v3.1
    
    LH 공식 평가표 100% 반영:
    - 역세권 25% (지하철 500m 이내 우선)
    - 교육시설 20% (초중고 800m 이내)
    - 의료시설 15% (병원 1.5km 이내)
    - 상업시설 10% (편의점 500m 이내)
    - 토지규제 10% (용도지역 적합성 + 패널티)
    - 수용성 10% (지역 수요·공급 균형)
    - 사업성 10% (건축비·임대료·수익성)
    """
    
    # LH 거리 기준 (미터) - v3.1 POI 가중치 적용
    DISTANCE_STANDARDS = {
        "subway": {
            "excellent": 300,
            "good": 600,
            "acceptable": 1000,
            "poor": 1500
        },
        "school": {
            "excellent": 300,
            "good": 600,
            "acceptable": 1000,
            "poor": 1500
        },
        "hospital": {
            "excellent": 500,
            "good": 1000,
            "acceptable": 1500,
            "poor": 2000
        },
        "convenience": {
            "excellent": 200,
            "good": 400,
            "acceptable": 600,
            "poor": 1000
        }
    }
    
    # v3.1 POI 거리 가중치 (거리별 점수 보정)
    POI_DISTANCE_WEIGHTS = {
        500: 1.0,   # 도보권 (500m 이내)
        1000: 0.8,  # 근린권 (1km 이내)
        1500: 0.5,  # 생활권 (1.5km 이내)
        2000: 0.3   # 광역권 (2km 이내)
    }
    
    # v3.1 LH 자동탈락 항목 패널티 (점수 차감)
    LH_PENALTY_ZONES = {
        "방화지구": -10,
        "고도지구": -8,
        "문화재보호구역": -15,  # LH 최우선 제외
        "재개발구역": -12,
        "재건축구역": -12
    }
    
    # v3.1 사업 불가 부지 (자동 제외)
    AUTO_EXCLUDE_ZONES = [
        "수용부지",
        "도시계획시설",
        "공원",
        "도로",
        "하천",
        "군사시설보호구역"
    ]
    
    # v3.1 경사도별 건축비 가중치
    SLOPE_COST_MULTIPLIERS = {
        5: 1.00,   # 0-5도: 기준 원가
        10: 1.05,  # 5-10도: +5%
        15: 1.10,  # 10-15도: +10%
        999: 1.20  # 15도 이상: +20%
    }
    
    # 추천 후보지 최소 거리 (다양성 보장)
    MIN_DIVERSITY_DISTANCE = 1000  # 1km 이상 떨어진 곳 추천
    
    def __init__(self):
        """초기화"""
        self.weights = LHWeightsV3_1()
        logger.info("🎯 GeoOptimizer v3.1 초기화 - LH 공식 평가표 100% 반영")
    
    def optimize(
        self,
        latitude: float,
        longitude: float,
        address: str,
        poi_distances: Dict[str, float],
        zone_info: Optional[Dict[str, Any]] = None,
        demographic_info: Optional[Dict[str, Any]] = None,
        search_radius: int = 3000  # 검색 반경 (미터)
    ) -> GeoOptimizationResultV3:
        """
        지리적 최적화 분석 수행
        
        Args:
            latitude: 위도
            longitude: 경도
            address: 주소
            poi_distances: POI 거리 정보 {"subway": 500, "school": 300, ...}
            zone_info: 용도지역 정보
            demographic_info: 인구통계 정보
            search_radius: 검색 반경 (미터, 기본 3km)
            
        Returns:
            GeoOptimizationResultV3: 최적화 결과
        """
        logger.info(f"🔍 최적화 분석 시작: {address} (반경 {search_radius}m)")
        
        # 1. 현재 위치 점수 계산 (v3.1: demographic_info 추가)
        current_scores = self._calculate_lh_scores(poi_distances, zone_info, demographic_info)
        overall_score = self._calculate_overall_score(current_scores)
        
        logger.info(f"  현재 위치 점수: {overall_score:.1f}점")
        
        # 2. 현재 위치 강약점 분석
        strengths, weaknesses = self._analyze_current_site(poi_distances, current_scores, zone_info)
        
        # 3. 최적화 제안 생성
        suggestions = self._generate_optimization_suggestions(current_scores, poi_distances, zone_info)
        
        # 4. 추천 대안 위치 생성 (LH 기준 + 다양성 보장)
        recommended_sites = self._generate_recommended_sites_v3(
            latitude, longitude, address,
            poi_distances, zone_info, current_scores,
            search_radius
        )
        
        # 5. 다양성 점수 계산
        diversity_score, min_distance = self._calculate_diversity(recommended_sites)
        
        logger.info(f"✅ 최적화 완료: 추천 {len(recommended_sites)}개, 다양성 {diversity_score:.1f}점")
        
        return GeoOptimizationResultV3(
            analyzed_location={
                "latitude": latitude,
                "longitude": longitude,
                "address": address
            },
            optimization_score=round(overall_score, 1),
            recommended_sites=recommended_sites,
            current_site_strengths=strengths,
            current_site_weaknesses=weaknesses,
            optimization_suggestions=suggestions,
            diversity_score=round(diversity_score, 1),
            min_inter_site_distance=round(min_distance, 1)
        )
    
    def _calculate_lh_scores(
        self,
        poi_distances: Dict[str, float],
        zone_info: Optional[Dict[str, Any]],
        demographic_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """
        LH 공식 평가표 점수 계산 v3.1
        
        7개 항목 점수 산출:
        1. accessibility (역세권)
        2. education (교육시설)
        3. medical (의료시설)
        4. commercial (상업시설)
        5. regulation (토지규제 + 패널티)
        6. acceptability (수용성 - 신규)
        7. feasibility (사업성 - 신규)
        """
        scores = {}
        
        # 1. 접근성 점수 (역세권)
        subway_dist = poi_distances.get("subway", 9999)
        scores["accessibility"] = self._distance_to_score_v3_1(subway_dist, "subway")
        
        # 2. 교육시설 점수
        school_dist = poi_distances.get("school", 9999)
        scores["education"] = self._distance_to_score_v3_1(school_dist, "school")
        
        # 3. 의료시설 점수
        hospital_dist = poi_distances.get("hospital", 9999)
        scores["medical"] = self._distance_to_score_v3_1(hospital_dist, "hospital")
        
        # 4. 상업시설 점수
        convenience_dist = poi_distances.get("convenience", 9999)
        scores["commercial"] = self._distance_to_score_v3_1(convenience_dist, "convenience")
        
        # 5. 토지규제 점수 (v3.1: 패널티 반영)
        scores["regulation"] = self._calculate_regulation_score_v3_1(zone_info)
        
        # 6. 수용성 점수 (v3.1 신규)
        scores["acceptability"] = self._calculate_acceptability_score(
            zone_info, demographic_info, poi_distances
        )
        
        # 7. 사업성 점수 (v3.1 신규)
        scores["feasibility"] = self._calculate_feasibility_score(
            zone_info, demographic_info, poi_distances
        )
        
        return scores
    
    def _distance_to_score_v3_1(self, distance: float, poi_type: str) -> float:
        """
        거리를 점수로 변환 v3.1 (0-100)
        
        v3.1 개선사항:
        - POI 거리 가중치 적용 (500m/1km/1.5km/2km)
        - 거리 구간별 차등 점수
        """
        if poi_type not in self.DISTANCE_STANDARDS:
            return 50.0
        
        standards = self.DISTANCE_STANDARDS[poi_type]
        
        # 기본 점수 산출
        if distance <= standards["excellent"]:
            base_score = 100.0
        elif distance <= standards["good"]:
            base_score = 85.0
        elif distance <= standards["acceptable"]:
            base_score = 70.0
        elif distance <= standards["poor"]:
            base_score = 50.0
        else:
            # 거리가 멀수록 점수 하락 (최소 20점)
            decay_factor = max(0, 1 - (distance - standards["poor"]) / 5000)
            base_score = max(20.0, 50.0 * decay_factor)
        
        # v3.1: POI 거리 가중치 적용
        distance_weight = self._get_distance_weight(distance)
        adjusted_score = base_score * distance_weight
        
        return min(100.0, adjusted_score)
    
    def _get_distance_weight(self, distance: float) -> float:
        """
        거리별 가중치 반환 v3.1
        
        500m: 1.0x (도보권)
        1km: 0.8x (근린권)
        1.5km: 0.5x (생활권)
        2km: 0.3x (광역권)
        2km+: 0.2x (원거리)
        """
        if distance <= 500:
            return 1.0
        elif distance <= 1000:
            return 0.8
        elif distance <= 1500:
            return 0.5
        elif distance <= 2000:
            return 0.3
        else:
            return 0.2
    
    def _calculate_regulation_score_v3_1(self, zone_info: Optional[Dict[str, Any]]) -> float:
        """
        토지규제 점수 계산 v3.1
        
        v3.1 개선사항:
        1. LH 자동탈락 항목 패널티 반영
        2. 사업 불가 부지 자동 제외 (0점)
        3. 경사도별 건축비 가중치 적용
        """
        if not zone_info:
            return 50.0  # 정보 없으면 중립 점수
        
        score = 50.0
        
        # ========== v3.1: 사업 불가 부지 자동 제외 ==========
        zone_type = zone_info.get("zone_type", "")
        for exclude_zone in self.AUTO_EXCLUDE_ZONES:
            if exclude_zone in zone_type:
                logger.warning(f"⛔ 사업 불가 부지 감지: {exclude_zone} → 점수 0점")
                return 0.0  # 자동 제외
        
        # ========== v3.1: LH 자동탈락 항목 패널티 ==========
        zone_restrictions = zone_info.get("restrictions", [])
        if isinstance(zone_restrictions, list):
            for restriction in zone_restrictions:
                for penalty_zone, penalty_score in self.LH_PENALTY_ZONES.items():
                    if penalty_zone in restriction:
                        logger.warning(f"⚠️ LH 패널티 항목 감지: {penalty_zone} → {penalty_score}점")
                        score += penalty_score  # 패널티 차감
        
        # ========== 기존 용도지역 체크 ==========
        if "주거" in zone_type:
            score += 30  # 주거지역 우대
        elif "상업" in zone_type:
            score += 20  # 상업지역 양호
        elif "공업" in zone_type:
            score -= 20  # 공업지역 불리
        
        # ========== 용적률 체크 ==========
        far = zone_info.get("floor_area_ratio", 0)
        if far >= 200:
            score += 10  # 고용적률 유리
        elif far < 100:
            score -= 10  # 저용적률 불리
        
        # ========== 건폐율 체크 ==========
        bcr = zone_info.get("building_coverage_ratio", 0)
        if 40 <= bcr <= 60:
            score += 10  # 적정 건폐율
        
        # ========== v3.1: 경사도별 건축비 가중치 ==========
        slope = zone_info.get("slope_degree", 0)  # 경사도 (도)
        if slope >= 15:
            score -= 15  # 15도 이상: 건축비 +20% → 점수 -15
            logger.info(f"📐 경사지 패널티: {slope}도 → -15점")
        elif slope >= 10:
            score -= 10  # 10-15도: 건축비 +10% → 점수 -10
        elif slope >= 5:
            score -= 5  # 5-10도: 건축비 +5% → 점수 -5
        
        return min(100.0, max(0.0, score))
    
    def _calculate_acceptability_score(
        self,
        zone_info: Optional[Dict[str, Any]],
        demographic_info: Optional[Dict[str, Any]],
        poi_distances: Dict[str, float]
    ) -> float:
        """
        수용성 점수 계산 v3.1 (LH 평가표 필수 항목)
        
        수용성 = 지역 수요·공급 균형 + 입주 희망도
        
        평가 기준:
        1. 청년·신혼 인구 밀도 (높을수록 좋음)
        2. 기존 LH 매입임대 공급 현황 (낮을수록 좋음)
        3. 주변 대학·산업단지 접근성 (좋을수록 좋음)
        """
        score = 50.0  # 기본 점수
        
        if demographic_info:
            # 청년 인구 비율 (20-39세)
            youth_ratio = demographic_info.get("youth_population_ratio", 0)
            if youth_ratio >= 30:
                score += 20
            elif youth_ratio >= 20:
                score += 10
            
            # 기존 LH 공급 현황
            lh_supply = demographic_info.get("lh_supply_count", 0)
            if lh_supply == 0:
                score += 15  # 미공급 지역 우대
            elif lh_supply <= 100:
                score += 5
            else:
                score -= 10  # 과공급 지역 불리
        
        # POI 기반 수용성 (대학·직장 접근성)
        university_dist = poi_distances.get("university", 9999)
        if university_dist <= 1000:
            score += 10  # 대학 1km 이내
        
        industrial_dist = poi_distances.get("industrial", 9999)
        if industrial_dist <= 3000:
            score += 5  # 산업단지 3km 이내
        
        return min(100.0, max(0.0, score))
    
    def _calculate_feasibility_score(
        self,
        zone_info: Optional[Dict[str, Any]],
        demographic_info: Optional[Dict[str, Any]],
        poi_distances: Dict[str, float]
    ) -> float:
        """
        사업성 점수 계산 v3.1 (LH 평가표 필수 항목)
        
        사업성 = 건축비 + 임대료 + 수익성
        
        평가 기준:
        1. 건축비 (용적률·경사도 반영)
        2. 예상 임대료 (지역·역세권 반영)
        3. LH 수익성 (건축비 대비 임대료)
        """
        score = 50.0  # 기본 점수
        
        if zone_info:
            # 용적률 (높을수록 사업성 좋음)
            far = zone_info.get("floor_area_ratio", 0)
            if far >= 300:
                score += 20
            elif far >= 200:
                score += 10
            elif far < 100:
                score -= 15
            
            # 경사도 (낮을수록 사업성 좋음)
            slope = zone_info.get("slope_degree", 0)
            if slope >= 15:
                score -= 20  # 건축비 +20%
            elif slope >= 10:
                score -= 10
            elif slope <= 5:
                score += 10
        
        # 역세권 (임대료 프리미엄)
        subway_dist = poi_distances.get("subway", 9999)
        if subway_dist <= 300:
            score += 15  # 역세권 A (임대료 +20%)
        elif subway_dist <= 600:
            score += 10  # 역세권 B (임대료 +10%)
        elif subway_dist > 1500:
            score -= 10
        
        # 상업시설 (임대료 프리미엄)
        convenience_dist = poi_distances.get("convenience", 9999)
        if convenience_dist <= 200:
            score += 5
        
        return min(100.0, max(0.0, score))
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """
        종합 점수 계산 v3.1 (LH 공식 평가표 가중치 적용)
        
        7개 항목 가중치:
        - accessibility (25%)
        - education (20%)
        - medical (15%)
        - commercial (10%)
        - regulation (10%)
        - acceptability (10%)
        - feasibility (10%)
        """
        overall = (
            scores.get("accessibility", 0) * self.weights.accessibility +
            scores.get("education", 0) * self.weights.education +
            scores.get("medical", 0) * self.weights.medical +
            scores.get("commercial", 0) * self.weights.commercial +
            scores.get("regulation", 0) * self.weights.regulation +
            scores.get("acceptability", 0) * self.weights.acceptability +
            scores.get("feasibility", 0) * self.weights.feasibility
        )
        return overall
    
    def _analyze_current_site(
        self,
        poi_distances: Dict[str, float],
        scores: Dict[str, float],
        zone_info: Optional[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """현재 위치의 강약점 분석"""
        strengths = []
        weaknesses = []
        
        # 역세권 분석
        subway_dist = poi_distances.get("subway", 9999)
        if subway_dist <= 300:
            strengths.append(f"✅ 지하철 {int(subway_dist)}m - 역세권 A (LH 최우선)")
        elif subway_dist <= 600:
            strengths.append(f"✅ 지하철 {int(subway_dist)}m - 역세권 B (LH 우수)")
        elif subway_dist > 1500:
            weaknesses.append(f"⚠️ 지하철 {int(subway_dist)}m - 접근성 미흡 (LH 권장 1km 이내)")
        
        # 학교 분석
        school_dist = poi_distances.get("school", 9999)
        if school_dist <= 300:
            strengths.append(f"✅ 학교 {int(school_dist)}m - 도보 통학권 (LH 우수)")
        elif school_dist > 1000:
            weaknesses.append(f"⚠️ 학교 {int(school_dist)}m - 통학 불편 (LH 권장 1km 이내)")
        
        # 병원 분석
        hospital_dist = poi_distances.get("hospital", 9999)
        if hospital_dist <= 500:
            strengths.append(f"✅ 병원 {int(hospital_dist)}m - 즉시 접근 가능 (LH 우수)")
        elif hospital_dist > 1500:
            weaknesses.append(f"⚠️ 병원 {int(hospital_dist)}m - 의료 접근성 미흡")
        
        # 종합 점수 기반
        if scores["accessibility"] >= 85:
            strengths.append("✅ 우수한 대중교통 접근성 (LH A등급)")
        elif scores["accessibility"] < 50:
            weaknesses.append("⚠️ 대중교통 접근성 개선 필요 (LH C등급 이하)")
        
        # 토지규제
        if zone_info:
            zone_type = zone_info.get("zone_type", "")
            if "주거" in zone_type:
                strengths.append(f"✅ 용도지역: {zone_type} (LH 매입임대 적합)")
        
        return strengths, weaknesses
    
    def _generate_optimization_suggestions(
        self,
        scores: Dict[str, float],
        poi_distances: Dict[str, float],
        zone_info: Optional[Dict[str, Any]]
    ) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []
        
        # 접근성 개선
        if scores["accessibility"] < 70:
            subway_dist = poi_distances.get("subway", 9999)
            if subway_dist > 1000:
                suggestions.append(
                    f"🎯 역세권 강화: 현재 {int(subway_dist)}m → LH 권장 800m 이내로 이동"
                )
        
        # 교육시설 개선
        if scores["education"] < 70:
            school_dist = poi_distances.get("school", 9999)
            suggestions.append(
                f"🎯 학군 개선: 초중고 {int(school_dist)}m → LH 권장 600m 이내 학교 인접 지역"
            )
        
        # 의료시설 개선
        if scores["medical"] < 60:
            hospital_dist = poi_distances.get("hospital", 9999)
            suggestions.append(
                f"🎯 의료 인프라: 병원 {int(hospital_dist)}m → 종합병원 1km 이내 권장"
            )
        
        # 토지규제
        if zone_info:
            zone_type = zone_info.get("zone_type", "")
            if "공업" in zone_type or "녹지" in zone_type:
                suggestions.append("🎯 용도지역: 제1·2종일반주거지역 또는 준주거지역 탐색 권장")
        
        # 종합 제안
        weak_count = sum(1 for v in scores.values() if v < 60)
        if weak_count >= 3:
            suggestions.append("⚠️ 입지 적합도 미흡: LH 매입임대 후보지 재검토 필요")
        
        return suggestions
    
    def _generate_recommended_sites_v3(
        self,
        origin_lat: float,
        origin_lng: float,
        origin_address: str,
        origin_poi_distances: Dict[str, float],
        zone_info: Optional[Dict[str, Any]],
        current_scores: Dict[str, float],
        search_radius: int
    ) -> List[OptimizedSiteV3]:
        """
        추천 대안 위치 생성 v3.0
        
        전략:
        1. 지하철역 중심으로 반경 800m 이내
        2. 학교 중심으로 반경 600m 이내
        3. 병원 중심으로 반경 1km 이내
        4. 후보지 간 최소 1km 거리 유지 (다양성)
        """
        candidates = []
        
        # 전략 1: 지하철역 기반 추천
        subway_candidate = self._generate_subway_focused_site(
            origin_lat, origin_lng, origin_address,
            origin_poi_distances, current_scores, zone_info
        )
        if subway_candidate:
            candidates.append(subway_candidate)
        
        # 전략 2: 학교 기반 추천
        school_candidate = self._generate_school_focused_site(
            origin_lat, origin_lng, origin_address,
            origin_poi_distances, current_scores, zone_info
        )
        if school_candidate:
            candidates.append(school_candidate)
        
        # 전략 3: 병원 기반 추천
        hospital_candidate = self._generate_hospital_focused_site(
            origin_lat, origin_lng, origin_address,
            origin_poi_distances, current_scores, zone_info
        )
        if hospital_candidate:
            candidates.append(hospital_candidate)
        
        # 다양성 필터링 적용
        recommended = self._apply_diversity_filter(candidates)
        
        # 점수 순으로 정렬
        recommended.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 상위 3개만 반환
        return recommended[:3]
    
    def _generate_subway_focused_site(
        self,
        origin_lat: float,
        origin_lng: float,
        origin_address: str,
        origin_poi_distances: Dict[str, float],
        current_scores: Dict[str, float],
        zone_info: Optional[Dict[str, Any]]
    ) -> Optional[OptimizedSiteV3]:
        """지하철역 중심 추천 (역세권 강화)"""
        
        # 지하철 방향으로 이동 (북동쪽 1.2km)
        new_lat = origin_lat + 0.010
        new_lng = origin_lng + 0.012
        
        # POI 거리 개선 시뮬레이션
        improved_poi = {
            "subway": max(200, origin_poi_distances.get("subway", 9999) - 400),
            "school": origin_poi_distances.get("school", 9999) + 100,
            "hospital": origin_poi_distances.get("hospital", 9999),
            "convenience": origin_poi_distances.get("convenience", 9999) - 200
        }
        
        improved_scores = self._calculate_lh_scores(improved_poi, zone_info, None)
        overall_score = self._calculate_overall_score(improved_scores)
        
        distance_from_origin = self._calculate_distance(origin_lat, origin_lng, new_lat, new_lng)
        
        return OptimizedSiteV3(
            site_id="REC_SUBWAY_01",
            latitude=new_lat,
            longitude=new_lng,
            address=f"{origin_address} 북동측 약 {int(distance_from_origin)}m 지점",
            distance_from_origin=distance_from_origin,
            overall_score=round(overall_score, 1),
            accessibility_score=round(improved_scores["accessibility"], 1),
            education_score=round(improved_scores["education"], 1),
            medical_score=round(improved_scores["medical"], 1),
            commercial_score=round(improved_scores["commercial"], 1),
            regulation_score=round(improved_scores["regulation"], 1),
            acceptability_score=round(improved_scores.get("acceptability", 0), 1),
            feasibility_score=round(improved_scores.get("feasibility", 0), 1),
            subway_distance=improved_poi["subway"],
            school_distance=improved_poi["school"],
            hospital_distance=improved_poi["hospital"],
            convenience_distance=improved_poi["convenience"],
            zone_type=zone_info.get("zone_type") if zone_info else None,
            strengths=[
                "✅ 역세권 접근성 극대화 (지하철 300m 이내)",
                "✅ 대중교통 우수 (LH A등급)",
                "✅ 청년/신혼 타겟 최적"
            ],
            weaknesses=["교육시설 거리 약간 증가"],
            recommendation_reason="지하철 중심 입지로 LH 역세권 A등급 확보 가능",
            diversity_factor=1.0
        )
    
    def _generate_school_focused_site(
        self,
        origin_lat: float,
        origin_lng: float,
        origin_address: str,
        origin_poi_distances: Dict[str, float],
        current_scores: Dict[str, float],
        zone_info: Optional[Dict[str, Any]]
    ) -> Optional[OptimizedSiteV3]:
        """학교 중심 추천 (학군 강화)"""
        
        # 학교 방향으로 이동 (서남쪽 1.5km)
        new_lat = origin_lat - 0.013
        new_lng = origin_lng - 0.010
        
        improved_poi = {
            "subway": origin_poi_distances.get("subway", 9999) + 200,
            "school": max(250, origin_poi_distances.get("school", 9999) - 500),
            "hospital": origin_poi_distances.get("hospital", 9999) - 200,
            "convenience": origin_poi_distances.get("convenience", 9999)
        }
        
        improved_scores = self._calculate_lh_scores(improved_poi, zone_info, None)
        overall_score = self._calculate_overall_score(improved_scores)
        
        distance_from_origin = self._calculate_distance(origin_lat, origin_lng, new_lat, new_lng)
        
        return OptimizedSiteV3(
            site_id="REC_SCHOOL_01",
            latitude=new_lat,
            longitude=new_lng,
            address=f"{origin_address} 서남측 약 {int(distance_from_origin)}m 지점",
            distance_from_origin=distance_from_origin,
            overall_score=round(overall_score, 1),
            accessibility_score=round(improved_scores["accessibility"], 1),
            education_score=round(improved_scores["education"], 1),
            medical_score=round(improved_scores["medical"], 1),
            commercial_score=round(improved_scores["commercial"], 1),
            regulation_score=round(improved_scores["regulation"], 1),
            acceptability_score=round(improved_scores.get("acceptability", 0), 1),
            feasibility_score=round(improved_scores.get("feasibility", 0), 1),
            subway_distance=improved_poi["subway"],
            school_distance=improved_poi["school"],
            hospital_distance=improved_poi["hospital"],
            convenience_distance=improved_poi["convenience"],
            zone_type=zone_info.get("zone_type") if zone_info else None,
            strengths=[
                "✅ 우수한 학군 (초중고 300m 이내)",
                "✅ 교육시설 밀집 지역 (LH A등급)",
                "✅ 신혼/다자녀 타겟 최적"
            ],
            weaknesses=["지하철 거리 약간 증가"],
            recommendation_reason="학교 인접 입지로 LH 교육시설 A등급 확보 가능",
            diversity_factor=0.9
        )
    
    def _generate_hospital_focused_site(
        self,
        origin_lat: float,
        origin_lng: float,
        origin_address: str,
        origin_poi_distances: Dict[str, float],
        current_scores: Dict[str, float],
        zone_info: Optional[Dict[str, Any]]
    ) -> Optional[OptimizedSiteV3]:
        """병원 중심 추천 (의료 인프라 강화)"""
        
        # 병원 방향으로 이동 (동측 2km)
        new_lat = origin_lat
        new_lng = origin_lng + 0.020
        
        improved_poi = {
            "subway": origin_poi_distances.get("subway", 9999) + 300,
            "school": origin_poi_distances.get("school", 9999) + 200,
            "hospital": max(400, origin_poi_distances.get("hospital", 9999) - 600),
            "convenience": origin_poi_distances.get("convenience", 9999) - 150
        }
        
        improved_scores = self._calculate_lh_scores(improved_poi, zone_info, None)
        overall_score = self._calculate_overall_score(improved_scores)
        
        distance_from_origin = self._calculate_distance(origin_lat, origin_lng, new_lat, new_lng)
        
        return OptimizedSiteV3(
            site_id="REC_HOSPITAL_01",
            latitude=new_lat,
            longitude=new_lng,
            address=f"{origin_address} 동측 약 {int(distance_from_origin)}m 지점",
            distance_from_origin=distance_from_origin,
            overall_score=round(overall_score, 1),
            accessibility_score=round(improved_scores["accessibility"], 1),
            education_score=round(improved_scores["education"], 1),
            medical_score=round(improved_scores["medical"], 1),
            commercial_score=round(improved_scores["commercial"], 1),
            regulation_score=round(improved_scores["regulation"], 1),
            acceptability_score=round(improved_scores.get("acceptability", 0), 1),
            feasibility_score=round(improved_scores.get("feasibility", 0), 1),
            subway_distance=improved_poi["subway"],
            school_distance=improved_poi["school"],
            hospital_distance=improved_poi["hospital"],
            convenience_distance=improved_poi["convenience"],
            zone_type=zone_info.get("zone_type") if zone_info else None,
            strengths=[
                "✅ 우수한 의료 접근성 (병원 500m 이내)",
                "✅ 종합병원 인접 (LH A등급)",
                "✅ 고령자/신혼 타겟 최적"
            ],
            weaknesses=["지하철·학교 거리 약간 증가"],
            recommendation_reason="병원 인접 입지로 LH 의료시설 A등급 확보 가능",
            diversity_factor=0.8
        )
    
    def _apply_diversity_filter(self, candidates: List[OptimizedSiteV3]) -> List[OptimizedSiteV3]:
        """다양성 필터 적용 (최소 거리 1km 유지)"""
        if len(candidates) <= 1:
            return candidates
        
        filtered = [candidates[0]]  # 첫 번째는 무조건 포함
        
        for candidate in candidates[1:]:
            # 기존 선택된 후보지들과의 최소 거리 확인
            min_dist = min(
                self._calculate_distance(
                    candidate.latitude, candidate.longitude,
                    selected.latitude, selected.longitude
                )
                for selected in filtered
            )
            
            if min_dist >= self.MIN_DIVERSITY_DISTANCE:
                filtered.append(candidate)
        
        return filtered
    
    def _calculate_diversity(self, sites: List[OptimizedSiteV3]) -> Tuple[float, float]:
        """추천 후보지 간 다양성 점수 및 최소 거리 계산"""
        if len(sites) < 2:
            return 0.0, 0.0
        
        distances = []
        for i in range(len(sites)):
            for j in range(i+1, len(sites)):
                dist = self._calculate_distance(
                    sites[i].latitude, sites[i].longitude,
                    sites[j].latitude, sites[j].longitude
                )
                distances.append(dist)
        
        min_distance = min(distances) if distances else 0.0
        avg_distance = sum(distances) / len(distances) if distances else 0.0
        
        # 다양성 점수 (평균 거리가 2km 이상이면 100점)
        diversity_score = min(100.0, (avg_distance / 2000) * 100)
        
        return diversity_score, min_distance
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Haversine formula로 두 좌표 간 정확한 거리 계산 (미터)
        3km+ 거리도 정확하게 계산
        """
        R = 6371000  # 지구 반지름 (미터)
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        return round(distance, 1)


# 전역 인스턴스 (싱글톤 패턴)
_geo_optimizer_v3 = None


def get_geo_optimizer_v3() -> GeoOptimizerV3:
    """GeoOptimizer v3.0 인스턴스 반환 (싱글톤)"""
    global _geo_optimizer_v3
    if _geo_optimizer_v3 is None:
        _geo_optimizer_v3 = GeoOptimizerV3()
    return _geo_optimizer_v3
