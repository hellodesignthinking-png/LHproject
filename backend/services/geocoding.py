"""
Enhanced Geocoding Service for ZeroSite Expert v3

Mock geocoding with comprehensive Korean region coverage
"""

from dataclasses import dataclass
from typing import Optional
import random


@dataclass
class Coordinates:
    """Geographic coordinates with administrative info"""
    lat: float
    lng: float
    region: str      # e.g., "서울특별시"
    district: str    # e.g., "강남구"


class EnhancedGeocodingService:
    """
    Enhanced geocoding service with better region coverage
    
    Improvements over existing:
    - More regions and districts covered
    - Better address parsing
    - Consistent coordinate generation
    """
    
    # Comprehensive region/district coordinates
    REGION_COORDINATES = {
        "서울특별시": {
            "강남구": (37.5172, 127.0473),
            "서초구": (37.4837, 127.0324),
            "송파구": (37.5145, 127.1059),
            "강동구": (37.5301, 127.1238),
            "마포구": (37.5663, 126.9019),
            "용산구": (37.5326, 126.9900),
            "영등포구": (37.5264, 126.8962),
            "강서구": (37.5509, 126.8495),
            "구로구": (37.4954, 126.8874),
            "관악구": (37.4781, 126.9514),
            "default": (37.5665, 126.9780)
        },
        "경기도": {
            "성남시": (37.4201, 127.1262),
            "용인시": (37.2411, 127.1776),
            "화성시": (37.1990, 126.8312),
            "수원시": (37.2636, 127.0286),
            "고양시": (37.6584, 126.8320),
            "남양주시": (37.6361, 127.2168),
            "평택시": (36.9921, 127.1128),
            "default": (37.4138, 127.5183)
        },
        "인천광역시": {
            "연수구": (37.4104, 126.6784),
            "남동구": (37.4471, 126.7314),
            "서구": (37.5451, 126.6762),
            "default": (37.4563, 126.7052)
        },
        "부산광역시": {
            "해운대구": (35.1631, 129.1635),
            "수영구": (35.1454, 129.1136),
            "default": (35.1796, 129.0756)
        },
        "default": {
            "default": (37.5665, 126.9780)
        }
    }
    
    def geocode(self, address: str) -> Coordinates:
        """
        Convert Korean address to coordinates
        
        Args:
            address: Korean address string
        
        Returns:
            Coordinates object with lat/lng and admin info
        """
        region = self._extract_region(address)
        district = self._extract_district(address, region)
        
        # Get base coordinates
        base_lat, base_lng = self._get_base_coordinates(region, district)
        
        # Add small random offset for variation (±500m)
        lat = base_lat + random.uniform(-0.005, 0.005)
        lng = base_lng + random.uniform(-0.005, 0.005)
        
        return Coordinates(
            lat=round(lat, 6),
            lng=round(lng, 6),
            region=region,
            district=district if district != "default" else "중심지"
        )
    
    def _extract_region(self, address: str) -> str:
        """Extract region (시/도) from address"""
        for region in self.REGION_COORDINATES.keys():
            if region in address and region != "default":
                return region
        
        # Partial matches
        if "서울" in address: return "서울특별시"
        elif "부산" in address: return "부산광역시"
        elif "인천" in address: return "인천광역시"
        elif "경기" in address: return "경기도"
        
        return "서울특별시"  # Default
    
    def _extract_district(self, address: str, region: str) -> str:
        """Extract district (구/시) from address"""
        if region not in self.REGION_COORDINATES:
            return "default"
        
        district_map = self.REGION_COORDINATES[region]
        for district in district_map.keys():
            if district != "default" and district in address:
                return district
        
        return "default"
    
    def _get_base_coordinates(self, region: str, district: str) -> tuple:
        """Get base coordinates for region/district"""
        if region in self.REGION_COORDINATES:
            region_coords = self.REGION_COORDINATES[region]
            if district in region_coords:
                return region_coords[district]
            return region_coords["default"]
        
        return self.REGION_COORDINATES["default"]["default"]


# Test
if __name__ == "__main__":
    service = EnhancedGeocodingService()
    
    test_addresses = [
        "서울특별시 강남구 역삼동 123-45",
        "경기도 성남시 분당구 정자동 100-1",
        "인천광역시 연수구 송도동 50-3"
    ]
    
    print("Enhanced Geocoding Service Test\n" + "="*50)
    for addr in test_addresses:
        coords = service.geocode(addr)
        print(f"\n주소: {addr}")
        print(f"좌표: ({coords.lat}, {coords.lng})")
        print(f"지역: {coords.region} {coords.district}")
