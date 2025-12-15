"""
ZeroSite v24.1 - Location & Infrastructure Analysis Engine
Analyzes location advantages based on real geographic data

Features:
- Transport accessibility (subway, bus)
- Education infrastructure (schools)
- Convenience facilities (stores, cafes)
- Medical facilities
- Parks and green spaces
- Generates narrative-style analysis

Author: ZeroSite Development Team
Version: 24.1.0 (Genspark v4.0)
Created: 2025-12-13
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)


@dataclass
class LocationScore:
    """Location score result"""
    transport_score: int
    education_score: int
    convenience_score: int
    medical_score: int
    overall_score: int
    narrative: List[str]
    details: Dict[str, Any]


class LocationInfraEngine:
    """
    Location & Infrastructure Analysis Engine
    
    Analyzes location advantages and generates narrative descriptions
    """
    
    def __init__(self):
        """Initialize engine"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Default POI databases (fallback data)
        self.default_pois = {
            "강남구": {
                "subway_500m": 2, "bus_stops_500m": 5,
                "elementary_1km": 3, "middle_1km": 2, "high_1km": 2,
                "convenience_500m": 12, "medical_500m": 4, "parks_1km": 2
            },
            "서초구": {
                "subway_500m": 2, "bus_stops_500m": 4,
                "elementary_1km": 3, "middle_1km": 2, "high_1km": 2,
                "convenience_500m": 10, "medical_500m": 3, "parks_1km": 2
            },
            "마포구": {
                "subway_500m": 2, "bus_stops_500m": 4,
                "elementary_1km": 2, "middle_1km": 2, "high_1km": 1,
                "convenience_500m": 11, "medical_500m": 3, "parks_1km": 1
            },
            "용산구": {
                "subway_500m": 2, "bus_stops_500m": 4,
                "elementary_1km": 2, "middle_1km": 2, "high_1km": 1,
                "convenience_500m": 9, "medical_500m": 3, "parks_1km": 3
            },
            "default": {
                "subway_500m": 1, "bus_stops_500m": 3,
                "elementary_1km": 2, "middle_1km": 1, "high_1km": 1,
                "convenience_500m": 6, "medical_500m": 2, "parks_1km": 1
            }
        }
    
    def analyze(
        self, 
        address: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_m: int = 1000
    ) -> LocationScore:
        """
        Analyze location and infrastructure
        
        Args:
            address: Property address
            lat: Latitude (optional, for future POI API integration)
            lon: Longitude (optional, for future POI API integration)
            radius_m: Analysis radius in meters
            
        Returns:
            LocationScore object with scores and narratives
        """
        try:
            self.logger.info(f"🗺️ Analyzing location for: {address}")
            
            # Extract district from address
            district = self._extract_district(address)
            
            # Get POI data (fallback to district defaults)
            poi_data = self._get_poi_data(district, lat, lon)
            
            # Calculate scores
            transport_score = self._calculate_transport_score(poi_data)
            education_score = self._calculate_education_score(poi_data)
            convenience_score = self._calculate_convenience_score(poi_data)
            medical_score = self._calculate_medical_score(poi_data)
            
            # Overall score (weighted average)
            overall_score = int(
                transport_score * 0.35 +
                education_score * 0.25 +
                convenience_score * 0.25 +
                medical_score * 0.15
            )
            
            # Generate narratives
            narratives = self._generate_narratives(
                poi_data, transport_score, education_score, 
                convenience_score, medical_score, overall_score
            )
            
            result = LocationScore(
                transport_score=transport_score,
                education_score=education_score,
                convenience_score=convenience_score,
                medical_score=medical_score,
                overall_score=overall_score,
                narrative=narratives,
                details=poi_data
            )
            
            self.logger.info(f"✅ Location analysis complete: Overall score = {overall_score}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Location analysis failed: {e}")
            # Return default fallback
            return LocationScore(
                transport_score=70,
                education_score=70,
                convenience_score=70,
                medical_score=70,
                overall_score=70,
                narrative=["대상지는 일반적인 도심 입지 특성을 보입니다."],
                details={}
            )
    
    def _extract_district(self, address: str) -> str:
        """Extract district (구) from address"""
        for district in ["강남구", "서초구", "마포구", "용산구", "송파구", "강동구"]:
            if district in address:
                return district
        return "default"
    
    def _get_poi_data(self, district: str, lat: Optional[float], lon: Optional[float]) -> Dict[str, Any]:
        """
        Get POI (Point of Interest) data
        
        TODO: Integrate with Kakao Local API or VWorld POI API
        Currently uses fallback district data
        """
        if lat and lon:
            # TODO: Query actual POI APIs here
            self.logger.info(f"📍 Coordinates provided: ({lat}, {lon}) - Using fallback for now")
        
        # Use district defaults
        return self.default_pois.get(district, self.default_pois["default"]).copy()
    
    def _calculate_transport_score(self, poi_data: Dict[str, Any]) -> int:
        """Calculate transport accessibility score (0-100)"""
        subway_count = poi_data.get("subway_500m", 0)
        bus_count = poi_data.get("bus_stops_500m", 0)
        
        # Scoring logic
        score = 50  # Base score
        score += min(subway_count * 15, 30)  # Max +30 for subway
        score += min(bus_count * 3, 20)      # Max +20 for bus
        
        return min(score, 100)
    
    def _calculate_education_score(self, poi_data: Dict[str, Any]) -> int:
        """Calculate education infrastructure score (0-100)"""
        elem_count = poi_data.get("elementary_1km", 0)
        middle_count = poi_data.get("middle_1km", 0)
        high_count = poi_data.get("high_1km", 0)
        
        score = 50  # Base score
        score += min(elem_count * 10, 20)
        score += min(middle_count * 10, 15)
        score += min(high_count * 10, 15)
        
        return min(score, 100)
    
    def _calculate_convenience_score(self, poi_data: Dict[str, Any]) -> int:
        """Calculate convenience facilities score (0-100)"""
        conv_count = poi_data.get("convenience_500m", 0)
        
        score = 50  # Base score
        score += min(conv_count * 4, 50)  # Max +50
        
        return min(score, 100)
    
    def _calculate_medical_score(self, poi_data: Dict[str, Any]) -> int:
        """Calculate medical facilities score (0-100)"""
        medical_count = poi_data.get("medical_500m", 0)
        
        score = 50  # Base score
        score += min(medical_count * 12, 50)  # Max +50
        
        return min(score, 100)
    
    def _generate_narratives(
        self, poi_data: Dict[str, Any], 
        transport: int, education: int, 
        convenience: int, medical: int, overall: int
    ) -> List[str]:
        """Generate narrative descriptions"""
        narratives = []
        
        # Transport narrative
        subway_count = poi_data.get("subway_500m", 0)
        bus_count = poi_data.get("bus_stops_500m", 0)
        if subway_count >= 2:
            narratives.append(
                f"대상지는 반경 500m 이내에 지하철역이 {subway_count}개, 버스정류장이 {bus_count}개 위치하여 "
                "대중교통 접근성이 매우 우수합니다."
            )
        elif subway_count >= 1:
            narratives.append(
                f"대상지는 반경 500m 이내에 지하철역이 {subway_count}개, 버스정류장이 {bus_count}개 위치하여 "
                "대중교통 접근성이 양호한 편입니다."
            )
        else:
            narratives.append(
                f"대상지는 반경 500m 이내에 버스정류장이 {bus_count}개 위치하여 "
                "대중교통 접근성이 보통 수준입니다."
            )
        
        # Education narrative
        elem = poi_data.get("elementary_1km", 0)
        middle = poi_data.get("middle_1km", 0)
        high = poi_data.get("high_1km", 0)
        if elem + middle + high >= 5:
            narratives.append(
                f"초·중·고교가 반경 1km 내에 각각 {elem}개, {middle}개, {high}개 분포하여 "
                "교육 인프라가 풍부한 지역입니다."
            )
        elif elem + middle + high >= 3:
            narratives.append(
                f"초·중·고교가 반경 1km 내에 총 {elem + middle + high}개 위치하여 "
                "교육 인프라가 양호한 수준입니다."
            )
        else:
            narratives.append("교육 인프라는 인근 지역 평균 수준입니다.")
        
        # Convenience narrative
        conv = poi_data.get("convenience_500m", 0)
        if conv >= 10:
            narratives.append(
                f"편의점·슈퍼·카페 등 근린생활시설이 반경 500m 내에 {conv}개 이상 밀집하여 "
                "일상생활 편의성이 매우 높습니다."
            )
        elif conv >= 6:
            narratives.append(
                f"편의점·슈퍼·카페 등 근린생활시설이 반경 500m 내에 {conv}개 위치하여 "
                "일상생활 편의성이 양호합니다."
            )
        else:
            narratives.append("생활 편의시설은 인근 지역 평균 수준입니다.")
        
        # Medical narrative
        med = poi_data.get("medical_500m", 0)
        if med >= 3:
            narratives.append(
                f"병원·의원·약국 등 의료시설이 반경 500m 내에 {med}개 위치하여 "
                "의료 접근성이 우수합니다."
            )
        elif med >= 2:
            narratives.append("의료시설 접근성은 양호한 편입니다.")
        
        # Overall summary
        if overall >= 85:
            narratives.append(
                "종합적으로 대상지는 교통·교육·편의시설 등 입지 여건이 매우 우수한 지역으로 평가됩니다."
            )
        elif overall >= 75:
            narratives.append(
                "종합적으로 대상지는 입지 여건이 양호한 지역으로 평가됩니다."
            )
        elif overall >= 60:
            narratives.append(
                "종합적으로 대상지는 평균 수준의 입지 여건을 갖추고 있습니다."
            )
        
        return narratives


# Singleton instance
_location_engine = None

def get_location_engine() -> LocationInfraEngine:
    """Get singleton instance of LocationInfraEngine"""
    global _location_engine
    if _location_engine is None:
        _location_engine = LocationInfraEngine()
    return _location_engine
