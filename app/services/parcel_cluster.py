"""
Parcel Cluster - ZeroSite Land Report v5.0
다필지 클러스터링 및 최적 조합 분석 서비스
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from dataclasses import dataclass
import math


class Parcel(BaseModel):
    """필지 정보"""
    parcel_id: str
    address: str
    latitude: float
    longitude: float
    area: float  # 면적 (㎡)
    
    # 분석 결과
    demand_score: Optional[float] = None
    building_capacity: Optional[int] = None  # 세대수
    risk_level: Optional[str] = None  # high, medium, low


class ParcelCluster(BaseModel):
    """필지 클러스터"""
    cluster_id: str
    parcels: List[Parcel]
    
    # 클러스터 특성
    total_area: float
    total_capacity: int  # 총 세대수
    center_latitude: float
    center_longitude: float
    
    # 점수
    cluster_score: float  # 클러스터 종합 점수 (0-100)
    synergy_score: float  # 시너지 점수 (0-100)
    
    # 분석
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendation: str = ""


class ClusteringResult(BaseModel):
    """클러스터링 결과"""
    total_parcels: int
    clusters: List[ParcelCluster]
    
    # 추천
    recommended_cluster_id: Optional[str] = None
    optimization_suggestions: List[str] = []
    
    # 통계
    avg_parcel_area: float
    total_area: float
    total_capacity: int


class ParcelClusterAnalyzer:
    """다필지 클러스터링 분석기"""
    
    def __init__(self):
        """초기화"""
        self.min_cluster_area = 500  # 최소 클러스터 면적 (㎡)
        self.max_cluster_area = 3000  # 최대 클러스터 면적 (㎡)
        self.max_distance_km = 0.5  # 최대 클러스터링 거리 (km)
    
    def analyze_parcels(
        self,
        parcels: List[Dict[str, Any]],
        target_area_min: float = 500,
        target_area_max: float = 2000
    ) -> ClusteringResult:
        """
        다필지 클러스터링 분석
        
        Args:
            parcels: 필지 정보 리스트
            target_area_min: 목표 최소 면적
            target_area_max: 목표 최대 면적
            
        Returns:
            ClusteringResult: 클러스터링 결과
        """
        # 1. 필지 객체 생성
        parcel_objects = []
        for idx, p in enumerate(parcels):
            parcel = Parcel(
                parcel_id=p.get("parcel_id", f"P{idx+1:03d}"),
                address=p["address"],
                latitude=p.get("latitude", 0),
                longitude=p.get("longitude", 0),
                area=p["area"],
                demand_score=p.get("demand_score"),
                building_capacity=p.get("building_capacity"),
                risk_level=p.get("risk_level", "low")
            )
            parcel_objects.append(parcel)
        
        # 2. 클러스터 생성
        clusters = self._create_clusters(
            parcel_objects, target_area_min, target_area_max
        )
        
        # 3. 클러스터 평가
        evaluated_clusters = []
        for cluster in clusters:
            evaluated = self._evaluate_cluster(cluster)
            evaluated_clusters.append(evaluated)
        
        # 4. 최적 클러스터 선정
        best_cluster = None
        if evaluated_clusters:
            evaluated_clusters.sort(key=lambda c: c.cluster_score, reverse=True)
            best_cluster = evaluated_clusters[0]
        
        # 5. 통계 계산
        total_area = sum(p.area for p in parcel_objects)
        avg_area = total_area / len(parcel_objects) if parcel_objects else 0
        total_capacity = sum(
            p.building_capacity for p in parcel_objects 
            if p.building_capacity
        ) or 0
        
        # 6. 최적화 제안
        suggestions = self._generate_suggestions(
            parcel_objects, evaluated_clusters, target_area_min, target_area_max
        )
        
        return ClusteringResult(
            total_parcels=len(parcel_objects),
            clusters=evaluated_clusters,
            recommended_cluster_id=best_cluster.cluster_id if best_cluster else None,
            optimization_suggestions=suggestions,
            avg_parcel_area=round(avg_area, 2),
            total_area=round(total_area, 2),
            total_capacity=total_capacity
        )
    
    def _create_clusters(
        self,
        parcels: List[Parcel],
        target_min: float,
        target_max: float
    ) -> List[ParcelCluster]:
        """클러스터 생성"""
        clusters = []
        used_parcels = set()
        
        # 단일 필지가 목표 범위에 있는 경우
        for parcel in parcels:
            if parcel.parcel_id in used_parcels:
                continue
            
            if target_min <= parcel.area <= target_max:
                cluster = ParcelCluster(
                    cluster_id=f"C_{parcel.parcel_id}",
                    parcels=[parcel],
                    total_area=parcel.area,
                    total_capacity=parcel.building_capacity or 0,
                    center_latitude=parcel.latitude,
                    center_longitude=parcel.longitude,
                    cluster_score=0,  # 나중에 계산
                    synergy_score=0
                )
                clusters.append(cluster)
                used_parcels.add(parcel.parcel_id)
        
        # 인접 필지 조합 (2개 조합)
        for i, p1 in enumerate(parcels):
            if p1.parcel_id in used_parcels:
                continue
            
            for j, p2 in enumerate(parcels[i+1:], start=i+1):
                if p2.parcel_id in used_parcels:
                    continue
                
                # 거리 계산
                distance = self._calculate_distance(
                    p1.latitude, p1.longitude,
                    p2.latitude, p2.longitude
                )
                
                # 인접 필지이고 합산 면적이 목표 범위인 경우
                if distance <= self.max_distance_km:
                    combined_area = p1.area + p2.area
                    if target_min <= combined_area <= target_max:
                        center_lat = (p1.latitude + p2.latitude) / 2
                        center_lng = (p1.longitude + p2.longitude) / 2
                        
                        cluster = ParcelCluster(
                            cluster_id=f"C_{p1.parcel_id}_{p2.parcel_id}",
                            parcels=[p1, p2],
                            total_area=combined_area,
                            total_capacity=(p1.building_capacity or 0) + (p2.building_capacity or 0),
                            center_latitude=center_lat,
                            center_longitude=center_lng,
                            cluster_score=0,
                            synergy_score=0
                        )
                        clusters.append(cluster)
        
        return clusters
    
    def _evaluate_cluster(self, cluster: ParcelCluster) -> ParcelCluster:
        """클러스터 평가"""
        # 기본 점수 (면적 기반)
        area_score = min(cluster.total_area / 1000 * 30, 30)
        
        # 수요 점수 (평균)
        demand_scores = [
            p.demand_score for p in cluster.parcels 
            if p.demand_score is not None
        ]
        avg_demand = sum(demand_scores) / len(demand_scores) if demand_scores else 50
        demand_score = avg_demand * 0.4
        
        # 리스크 점수
        risk_score = 30
        high_risk_count = sum(1 for p in cluster.parcels if p.risk_level == "high")
        risk_score -= high_risk_count * 10
        risk_score = max(risk_score, 0)
        
        # 시너지 점수 (다필지인 경우 보너스)
        synergy_score = 0
        if len(cluster.parcels) > 1:
            synergy_score = 15  # 다필지 조합 보너스
            cluster.synergy_score = 70
        else:
            cluster.synergy_score = 50
        
        # 종합 점수
        cluster.cluster_score = round(
            area_score + demand_score + risk_score + synergy_score, 1
        )
        
        # 강약점 분석
        cluster.strengths = self._analyze_strengths(cluster)
        cluster.weaknesses = self._analyze_weaknesses(cluster)
        
        # 추천 메시지
        if cluster.cluster_score >= 80:
            cluster.recommendation = "✅ 매우 적합 - 우선 검토 추천"
        elif cluster.cluster_score >= 60:
            cluster.recommendation = "⚠️ 적합 - 조건부 검토"
        else:
            cluster.recommendation = "❌ 부적합 - 대안 검토 필요"
        
        return cluster
    
    def _analyze_strengths(self, cluster: ParcelCluster) -> List[str]:
        """강점 분석"""
        strengths = []
        
        if cluster.total_area >= 800:
            strengths.append(f"충분한 면적 ({cluster.total_area:.0f}㎡)")
        
        if len(cluster.parcels) > 1:
            strengths.append(f"다필지 조합으로 규모의 경제 실현 ({len(cluster.parcels)}필지)")
        
        if cluster.total_capacity >= 20:
            strengths.append(f"적정 세대수 확보 ({cluster.total_capacity}세대)")
        
        # 수요 점수 기반
        demand_scores = [p.demand_score for p in cluster.parcels if p.demand_score]
        if demand_scores and sum(demand_scores) / len(demand_scores) >= 70:
            strengths.append("높은 수요 점수")
        
        return strengths
    
    def _analyze_weaknesses(self, cluster: ParcelCluster) -> List[str]:
        """약점 분석"""
        weaknesses = []
        
        if cluster.total_area < 500:
            weaknesses.append(f"면적 부족 ({cluster.total_area:.0f}㎡)")
        
        # 리스크 체크
        high_risk = [p for p in cluster.parcels if p.risk_level == "high"]
        if high_risk:
            weaknesses.append(f"고위험 필지 포함 ({len(high_risk)}개)")
        
        if len(cluster.parcels) > 1:
            weaknesses.append("다필지 조합으로 소유자 협의 복잡")
        
        return weaknesses
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """두 지점 간 거리 계산 (km)"""
        # Haversine 공식
        R = 6371  # 지구 반지름 (km)
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _generate_suggestions(
        self,
        parcels: List[Parcel],
        clusters: List[ParcelCluster],
        target_min: float,
        target_max: float
    ) -> List[str]:
        """최적화 제안 생성"""
        suggestions = []
        
        # 클러스터 분석
        if not clusters:
            suggestions.append("목표 면적 범위에 적합한 클러스터를 찾을 수 없습니다. 면적 범위 조정을 권장합니다.")
        
        # 다필지 조합 제안
        multi_parcel_clusters = [c for c in clusters if len(c.parcels) > 1]
        if multi_parcel_clusters:
            best_multi = max(multi_parcel_clusters, key=lambda c: c.cluster_score)
            suggestions.append(
                f"다필지 조합 '{best_multi.cluster_id}'가 단일 필지 대비 {best_multi.synergy_score:.0f}점의 시너지 효과"
            )
        
        # 면적 제안
        avg_area = sum(p.area for p in parcels) / len(parcels) if parcels else 0
        if avg_area < target_min:
            suggestions.append(f"평균 필지 면적({avg_area:.0f}㎡)이 목표치({target_min}㎡) 미만입니다. 더 큰 필지 탐색 권장")
        
        return suggestions


# 전역 인스턴스
_parcel_analyzer = None

def get_parcel_analyzer() -> ParcelClusterAnalyzer:
    """Parcel Analyzer 싱글톤 인스턴스 반환"""
    global _parcel_analyzer
    if _parcel_analyzer is None:
        _parcel_analyzer = ParcelClusterAnalyzer()
    return _parcel_analyzer
