"""
Dashboard Builder - ZeroSite Land Report v5.0
Chart.js, Leaflet, Mapbox GL JS용 대시보드 데이터 생성
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class DashboardData(BaseModel):
    """대시보드 데이터 모델"""
    chart_configs: Dict[str, Any]
    map_data: Dict[str, Any]
    statistics: Dict[str, Any]


class DashboardBuilder:
    """대시보드 데이터 빌더"""
    
    def __init__(self):
        """초기화"""
        self.default_colors = {
            "청년": "#3498db",
            "신혼·신생아 I": "#e91e63",
            "신혼·신생아 II": "#9c27b0",
            "다자녀": "#4caf50",
            "고령자": "#ff9800",
            "일반": "#607d8b",
            "든든전세": "#9e9e9e"
        }
    
    def build_dashboard(
        self,
        analysis_result: Dict[str, Any],
        include_charts: bool = True,
        include_maps: bool = True
    ) -> DashboardData:
        """
        전체 대시보드 데이터 생성
        
        Args:
            analysis_result: 분석 결과 데이터
            include_charts: 차트 포함 여부
            include_maps: 지도 포함 여부
            
        Returns:
            DashboardData: 대시보드 데이터
        """
        chart_configs = {}
        map_data = {}
        
        if include_charts:
            # 차트 생성
            if analysis_result.get("type_demand_scores"):
                chart_configs["type_demand_scores_radar"] = self.generate_radar_chart_config(
                    analysis_result["type_demand_scores"]
                )
            
            if analysis_result.get("grade_info"):
                chart_configs["category_scores_bar"] = self.generate_bar_chart_config(
                    analysis_result["grade_info"].get("category_scores", {})
                )
        
        if include_maps:
            # 지도 데이터 생성
            if analysis_result.get("geo_optimization"):
                map_data["geo_optimizer_points"] = self.generate_geo_optimizer_map_data(
                    analysis_result["geo_optimization"]
                )
            
            if analysis_result.get("coordinates"):
                map_data["main_location"] = {
                    "lat": analysis_result["coordinates"]["latitude"],
                    "lng": analysis_result["coordinates"]["longitude"]
                }
        
        # 통계 생성
        statistics = self._generate_statistics(analysis_result)
        
        return DashboardData(
            chart_configs=chart_configs,
            map_data=map_data,
            statistics=statistics
        )
    
    def generate_radar_chart_config(
        self, 
        type_demand_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        유형별 수요점수 Radar Chart 설정 생성 (Chart.js)
        
        Args:
            type_demand_scores: 유형별 점수 딕셔너리
            
        Returns:
            Chart.js radar chart configuration
        """
        labels = list(type_demand_scores.keys())
        data = list(type_demand_scores.values())
        
        return {
            "type": "radar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "유형별 수요 점수",
                    "data": data,
                    "backgroundColor": "rgba(102, 126, 234, 0.2)",
                    "borderColor": "rgb(102, 126, 234)",
                    "pointBackgroundColor": "rgb(102, 126, 234)",
                    "pointBorderColor": "#fff",
                    "pointHoverBackgroundColor": "#fff",
                    "pointHoverBorderColor": "rgb(102, 126, 234)",
                    "pointRadius": 5,
                    "pointHoverRadius": 7
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": True,
                "scales": {
                    "r": {
                        "beginAtZero": True,
                        "max": 100,
                        "ticks": {
                            "stepSize": 20
                        },
                        "pointLabels": {
                            "font": {
                                "size": 12,
                                "weight": "bold"
                            }
                        }
                    }
                },
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "top"
                    },
                    "title": {
                        "display": True,
                        "text": "유형별 수요 점수 비교",
                        "font": {
                            "size": 16,
                            "weight": "bold"
                        }
                    }
                }
            }
        }
    
    def generate_bar_chart_config(
        self, 
        category_scores: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        카테고리별 점수 Bar Chart 설정 생성 (Chart.js)
        
        Args:
            category_scores: 카테고리별 점수
            
        Returns:
            Chart.js bar chart configuration
        """
        labels = list(category_scores.keys())
        data = list(category_scores.values())
        
        # 점수에 따른 색상 배열 생성
        colors = [
            "#4caf50" if score >= 80 else "#ff9800" if score >= 60 else "#f44336"
            for score in data
        ]
        
        return {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "점수",
                    "data": data,
                    "backgroundColor": colors,
                    "borderColor": colors,
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "max": 100,
                        "ticks": {
                            "stepSize": 20
                        },
                        "title": {
                            "display": True,
                            "text": "점수"
                        }
                    },
                    "x": {
                        "title": {
                            "display": True,
                            "text": "카테고리"
                        }
                    }
                },
                "plugins": {
                    "legend": {
                        "display": False
                    },
                    "title": {
                        "display": True,
                        "text": "카테고리별 평가 점수",
                        "font": {
                            "size": 16,
                            "weight": "bold"
                        }
                    }
                }
            }
        }
    
    def generate_heatmap_data(
        self, 
        parcels: List[Dict[str, Any]]
    ) -> List[List[float]]:
        """
        Leaflet Heatmap 데이터 생성
        
        Args:
            parcels: 필지 목록 (lat, lng, demand_score 포함)
            
        Returns:
            Heatmap data [[lat, lng, intensity], ...]
        """
        heatmap_data = []
        
        for parcel in parcels:
            if parcel.get("latitude") and parcel.get("longitude"):
                intensity = parcel.get("demand_score", 50) / 100  # 0-1 정규화
                heatmap_data.append([
                    parcel["latitude"],
                    parcel["longitude"],
                    intensity
                ])
        
        return heatmap_data
    
    def generate_map_markers(
        self, 
        parcels: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Leaflet Map Markers 데이터 생성
        
        Args:
            parcels: 필지 목록
            
        Returns:
            Marker data [{lat, lng, popup, color}, ...]
        """
        markers = []
        
        for parcel in parcels:
            if parcel.get("latitude") and parcel.get("longitude"):
                demand_score = parcel.get("demand_score", 0)
                
                # 점수에 따른 색상
                color = self._get_marker_color(demand_score)
                
                # 팝업 내용
                popup = f"""
                    <b>{parcel.get('address', 'Unknown')}</b><br>
                    수요 점수: {demand_score:.1f}점<br>
                    세대수: {parcel.get('building_capacity', '-')}세대
                """
                
                markers.append({
                    "lat": parcel["latitude"],
                    "lng": parcel["longitude"],
                    "popup": popup,
                    "color": color,
                    "score": demand_score
                })
        
        return markers
    
    def generate_geo_optimizer_map_data(
        self, 
        geo_optimization: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Geo Optimizer 3D Map 데이터 생성 (Mapbox GL JS)
        
        Args:
            geo_optimization: Geo optimization 결과
            
        Returns:
            3D map data
        """
        points = []
        
        # 현재 위치
        current_loc = geo_optimization["analyzed_location"]
        points.append({
            "type": "current",
            "lat": current_loc["latitude"],
            "lng": current_loc["longitude"],
            "score": geo_optimization["optimization_score"],
            "label": "현재 위치",
            "color": "#2196f3"
        })
        
        # 추천 사이트
        for idx, site in enumerate(geo_optimization.get("recommended_sites", [])):
            color = self._get_marker_color(site["overall_score"])
            
            points.append({
                "type": "recommended",
                "lat": site["latitude"],
                "lng": site["longitude"],
                "score": site["overall_score"],
                "label": f"추천 #{idx + 1}",
                "color": color,
                "site_id": site.get("site_id")
            })
        
        return {
            "points": points,
            "center": {
                "lat": current_loc["latitude"],
                "lng": current_loc["longitude"]
            },
            "zoom": 14
        }
    
    def generate_cluster_map_data(
        self, 
        cluster_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        다필지 클러스터 Map 데이터 생성
        
        Args:
            cluster_analysis: 클러스터 분석 결과
            
        Returns:
            Cluster map data
        """
        clusters_data = []
        
        for cluster in cluster_analysis.get("clusters", []):
            cluster_data = {
                "cluster_id": cluster["cluster_id"],
                "center_lat": cluster["center_latitude"],
                "center_lng": cluster["center_longitude"],
                "total_area": cluster["total_area"],
                "cluster_score": cluster["cluster_score"],
                "synergy_score": cluster["synergy_score"],
                "parcels": [
                    {
                        "lat": p["latitude"],
                        "lng": p["longitude"],
                        "address": p["address"]
                    }
                    for p in cluster["parcels"]
                ]
            }
            clusters_data.append(cluster_data)
        
        return {
            "clusters": clusters_data,
            "total_clusters": len(clusters_data)
        }
    
    def _get_marker_color(self, score: float) -> str:
        """점수에 따른 마커 색상 반환"""
        if score >= 80:
            return "#4caf50"  # green
        elif score >= 60:
            return "#ff9800"  # orange
        else:
            return "#f44336"  # red
    
    def _generate_statistics(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """통계 생성"""
        stats = {
            "total_analyses": 1,
            "avg_demand_score": 0,
            "top_housing_type": None,
            "eligibility_rate": 0
        }
        
        # 평균 수요 점수
        type_scores = analysis_result.get("type_demand_scores", {})
        if type_scores:
            stats["avg_demand_score"] = round(
                sum(type_scores.values()) / len(type_scores), 1
            )
            stats["top_housing_type"] = max(
                type_scores.items(), 
                key=lambda x: x[1]
            )[0]
        
        # 적합성
        summary = analysis_result.get("summary", {})
        if summary:
            stats["eligibility_rate"] = 100 if summary.get("is_eligible") else 0
        
        return stats


# 전역 인스턴스
_dashboard_builder = None

def get_dashboard_builder() -> DashboardBuilder:
    """Dashboard Builder 싱글톤 인스턴스 반환"""
    global _dashboard_builder
    if _dashboard_builder is None:
        _dashboard_builder = DashboardBuilder()
    return _dashboard_builder
