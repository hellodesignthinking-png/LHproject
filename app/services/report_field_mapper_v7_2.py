"""
ZeroSite Report Engine v7.2 Field Mapper
Maps v7.2 analysis engine output to report template variables
Replaces ALL v6.x field mappings with v7.2 structure
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class ReportFieldMapperV72:
    """
    Complete field mapping for ZeroSite v7.2 Report Engine
    Handles all engine components: Type Demand, GeoOptimizer, Multi-Parcel, etc.
    """
    
    def __init__(self):
        self.version = "7.2.0"
        self.generated_at = datetime.now().isoformat()
    
    def map_analysis_output_to_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main mapping function: v7.2 engine output → report variables
        
        Args:
            analysis_result: Raw output from ZeroSite v7.2 analysis engine
            
        Returns:
            Complete report data dictionary with all v7.2 fields mapped
        """
        
        report_data = {
            # Meta information
            "report_version": "7.2.0",
            "generated_at": self.generated_at,
            "engine_version": "ZeroSite v7.2",
            
            # Core analysis info
            "basic_info": self._map_basic_info(analysis_result),
            
            # Type Demand v3.1
            "type_demand": self._map_type_demand_v3_1(analysis_result),
            
            # GeoOptimizer v3.1
            "geo_optimizer": self._map_geo_optimizer_v3_1(analysis_result),
            
            # Multi-Parcel v3.0 (if applicable)
            "multi_parcel": self._map_multi_parcel_v3_0(analysis_result),
            
            # LH scoring & assessment
            "lh_assessment": self._map_lh_assessment(analysis_result),
            
            # Building & development info
            "development": self._map_development_info(analysis_result),
            
            # Risk analysis
            "risks": self._map_risk_analysis(analysis_result),
            
            # Performance stats (Rate Limit, Cache)
            "performance": self._map_performance_stats(analysis_result),
            
            # LH Notice Loader v2.1 (if applicable)
            "lh_notice": self._map_lh_notice_loader(analysis_result),
            
            # Negotiation strategies
            "strategies": self._map_negotiation_strategies(analysis_result),
            
            # Fallback status
            "fallback_info": self._map_fallback_status(analysis_result)
        }
        
        return report_data
    
    def _map_basic_info(self, data: Dict) -> Dict[str, Any]:
        """Map basic analysis information"""
        return {
            "analysis_id": data.get("analysis_id", "N/A"),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "address": data.get("address", "주소 정보 없음"),
            "coordinates": {
                "lat": data.get("coordinates", {}).get("lat", 0.0),
                "lng": data.get("coordinates", {}).get("lng", 0.0)
            },
            "area_sqm": data.get("area", 0.0),
            "area_pyeong": round(data.get("area", 0.0) / 3.3058, 2),
            "zoning_type": data.get("zoning_type", "용도지역 미확인"),
            "unit_type": data.get("unit_type", "유형 미지정")
        }
    
    def _map_type_demand_v3_1(self, data: Dict) -> Dict[str, Any]:
        """Map Type Demand Score v3.1 fields"""
        return {
            # Main score
            "score": data.get("type_demand_score", 0.0),
            "grade": data.get("type_demand_grade", "미평가"),
            "lh_2025_applied": data.get("lh_2025_weights_applied", True),
            
            # Individual type scores
            "scores_by_type": {
                "청년": data.get("청년_score", 0.0),
                "신혼신생아I": data.get("신혼신생아I_score", 0.0),
                "신혼신생아II": data.get("신혼신생아II_score", 0.0),
                "다자녀": data.get("다자녀_score", 0.0),
                "고령자": data.get("고령자_score", 0.0),
                "일반": data.get("일반_score", 0.0),
                "든든전세": data.get("든든전세_score", 0.0)
            },
            
            # POI distances (v3.1 standard)
            "poi_distances": {
                "school": data.get("school_distance", 0.0),
                "hospital": data.get("hospital_distance", 0.0),
                "station": data.get("station_distance", 0.0),
                "market": data.get("market_distance", 0.0)
            },
            
            # Weights
            "poi_distance_weight": data.get("poi_distance_weight", 0.35),
            
            # Demographics
            "youth_population_ratio": data.get("youth_population_ratio", 0.0),
            "household_growth_rate": data.get("household_growth_rate", 0.0),
            
            # Accessibility
            "accessibility_score": data.get("accessibility_score", 0.0),
            
            # Drainage
            "drainage_score": data.get("drainage_optimization_score", 0.0),
            "drainage_quality": data.get("drainage_quality", "fair")
        }
    
    def _map_geo_optimizer_v3_1(self, data: Dict) -> Dict[str, Any]:
        """Map GeoOptimizer v3.1 fields"""
        
        # Parse alternative locations
        alt_locations = data.get("alternative_locations", [])
        alternatives = []
        
        for i, alt in enumerate(alt_locations[:3], 1):
            alternatives.append({
                "rank": i,
                "lat": alt.get("lat", 0.0),
                "lng": alt.get("lng", 0.0),
                "score": alt.get("score", 0.0),
                "distance_m": alt.get("distance", 0)
            })
        
        # Fill up to 3 alternatives
        while len(alternatives) < 3:
            alternatives.append({
                "rank": len(alternatives) + 1,
                "lat": 0.0,
                "lng": 0.0,
                "score": 0.0,
                "distance_m": 0
            })
        
        return {
            "score": data.get("geo_optimizer_score", 0.0),
            "grade": data.get("optimization_grade", "fair"),
            "alternatives": alternatives,
            "poi_density_score": data.get("poi_density_score", 0.0),
            "total_pois_nearby": data.get("total_pois_nearby", 0),
            "poi_diversity_index": data.get("poi_diversity_index", 0.0),
            "distance_penalty_factor": data.get("distance_penalty_factor", 1.0),
            "accessibility_bonus": data.get("accessibility_bonus", 0.0)
        }
    
    def _map_multi_parcel_v3_0(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Map Multi-Parcel v3.0 fields (if applicable)"""
        
        parcel_count = data.get("parcel_count", 1)
        
        if parcel_count < 2:
            return None  # Single parcel analysis
        
        return {
            "parcel_count": parcel_count,
            "total_area": data.get("total_area", 0.0),
            "center_point": {
                "lat": data.get("center_point_lat", 0.0),
                "lng": data.get("center_point_lng", 0.0),
                "method": data.get("center_point_method", "geometric_centroid")
            },
            "shape_analysis": {
                "compactness_ratio": data.get("shape_compactness_ratio", 0.0),
                "quality": data.get("shape_quality", "fair"),
                "penalty_factor": data.get("shape_penalty_factor", 1.0),
                "boundary_irregularity": data.get("boundary_irregularity", 0.0)
            },
            "zoning": {
                "dominant_type": data.get("dominant_zoning_type", "N/A"),
                "consistency": data.get("zoning_consistency", "unknown"),
                "mixed": data.get("mixed_zones", False),
                "dominant_ratio": data.get("dominant_zoning_ratio", 0.0)
            },
            "combined_scores": {
                "lh_score": data.get("combined_lh_score", 0.0),
                "lh_grade": data.get("combined_lh_grade", "C"),
                "weighted_base": data.get("weighted_base_score", 0.0),
                "penalty_applied": data.get("shape_penalty_applied", 0.0)
            },
            "individual_parcels": data.get("individual_parcels", []),
            "contribution_ratios": data.get("parcel_contribution_ratios", [])
        }
    
    def _map_lh_assessment(self, data: Dict) -> Dict[str, Any]:
        """Map LH scoring and assessment"""
        return {
            "score": data.get("lh_score", 0.0),
            "grade": data.get("lh_grade", "C"),
            "version": data.get("lh_version", "2024"),
            "overall_suitability": data.get("overall_suitability", "평가 필요"),
            "recommendation": data.get("recommendation", "상세 검토 권장")
        }
    
    def _map_development_info(self, data: Dict) -> Dict[str, Any]:
        """Map building and development information"""
        return {
            "estimated_units": data.get("estimated_units", 0),
            "estimated_floors": data.get("estimated_floors", 0),
            "building_coverage_ratio": data.get("building_coverage_ratio", 0.0),
            "floor_area_ratio": data.get("floor_area_ratio", 0.0)
        }
    
    def _map_risk_analysis(self, data: Dict) -> Dict[str, Any]:
        """Map risk factors and analysis"""
        risk_factors = data.get("risk_factors", [])
        
        return {
            "count": data.get("risk_count", len(risk_factors)),
            "factors": risk_factors,
            "has_risks": len(risk_factors) > 0,
            "risk_level": "high" if len(risk_factors) >= 3 else "medium" if len(risk_factors) >= 1 else "low"
        }
    
    def _map_performance_stats(self, data: Dict) -> Dict[str, Any]:
        """Map performance statistics (Rate Limit, Cache)"""
        return {
            # Rate limit stats
            "api_retry_count": data.get("api_retry_count", 0),
            "circuit_breaker_state": data.get("circuit_breaker_state", "CLOSED"),
            "provider_used": data.get("provider_used", "kakao"),
            "failover_occurred": data.get("failover_occurred", False),
            "total_api_calls": data.get("total_api_calls", 0),
            "failed_api_calls": data.get("failed_api_calls", 0),
            
            # Cache stats
            "cache_hit_rate": data.get("cache_hit_rate", 0.0),
            "cache_hits": data.get("cache_hits", 0),
            "cache_misses": data.get("cache_misses", 0),
            "cache_backend": data.get("cache_backend", "memory"),
            
            # Timing
            "analysis_duration": data.get("total_analysis_duration", 0.0),
            "avg_api_response_time": data.get("avg_api_response_time", 0.0)
        }
    
    def _map_lh_notice_loader(self, data: Dict) -> Optional[Dict[str, Any]]:
        """Map LH Notice Loader v2.1 fields (if applicable)"""
        
        if "notice_id" not in data and "lh_notice_summary" not in data:
            return None
        
        return {
            "notice_id": data.get("notice_id", "N/A"),
            "title": data.get("notice_title", "N/A"),
            "published_date": data.get("published_date", "N/A"),
            "category": data.get("category", "N/A"),
            "region": data.get("region", "N/A"),
            "extraction_method": data.get("extraction_method", "pdfplumber"),
            "extraction_confidence": data.get("extraction_confidence", 0.0),
            "summary": data.get("lh_notice_summary", "공고 정보 없음"),
            "risk_flags": data.get("lh_risk_flags", []),
            "compatibility_score": data.get("lh_compatibility_score", 0.0)
        }
    
    def _map_negotiation_strategies(self, data: Dict) -> Dict[str, Any]:
        """Map negotiation strategies"""
        strategies = data.get("negotiation_strategies", [])
        
        return {
            "strategies": strategies,
            "count": len(strategies),
            "final_score": data.get("final_score_after_strategy", 0.0)
        }
    
    def _map_fallback_status(self, data: Dict) -> Dict[str, Any]:
        """Map API fallback status for transparency"""
        return {
            "api_available": data.get("api_available", True),
            "using_cache": data.get("using_cache", False),
            "using_fallback": data.get("using_fallback", False),
            "data_quality": data.get("data_quality", "real")  # real/cached/fallback/mock
        }
    
    def get_safe_value(self, data: Dict, key: str, default: Any = "N/A") -> Any:
        """
        Safely get value with fallback chain
        Priority: real data → cached → default
        """
        value = data.get(key, default)
        
        # Handle None or empty values
        if value is None or value == "":
            return default
        
        return value
    
    def format_score(self, score: float, precision: int = 1) -> str:
        """Format score with fallback for missing data"""
        if score is None or score == 0.0:
            return "평가 중"
        return f"{score:.{precision}f}점"
    
    def format_distance(self, distance: float, unit: str = "m") -> str:
        """Format distance with proper units"""
        if distance is None or distance == 0.0:
            return "거리 정보 없음"
        
        if distance >= 1000:
            return f"{distance/1000:.1f}km"
        return f"{distance:.0f}m"


# Singleton instance
field_mapper = ReportFieldMapperV72()


def map_v7_2_output(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function for mapping v7.2 engine output to report format
    
    Usage:
        from app.services.report_field_mapper_v7_2 import map_v7_2_output
        report_data = map_v7_2_output(analysis_engine_output)
    """
    return field_mapper.map_analysis_output_to_report(analysis_result)
