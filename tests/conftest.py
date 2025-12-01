"""
pytest 공통 fixtures 및 설정
"""

import pytest
from httpx import AsyncClient
from app.main import app


@pytest.fixture
def mock_kakao_service(monkeypatch):
    """카카오 API 모킹"""
    from app.services.kakao_service import KakaoService
    from app.schemas import Coordinates
    
    async def mock_address_to_coordinates(self, address: str):
        return Coordinates(latitude=37.5665, longitude=126.9780)
    
    async def mock_search_nearby_facilities(self, coords, category, radius=2000):
        return [
            {"name": "지하철역", "category": "지하철", "distance": 500},
            {"name": "버스정류장", "category": "버스", "distance": 100},
            {"name": "편의점", "category": "편의점", "distance": 200}
        ]
    
    async def mock_search_hazardous_facilities(self, coords, unit_type=None):
        return []
    
    async def mock_analyze_location_accessibility(self, coords):
        return {
            "nearest_subway_distance": 500,
            "nearest_school_distance": 800,
            "accessibility_score": 75,
            "subway_stations": []
        }
    
    monkeypatch.setattr(KakaoService, "address_to_coordinates", mock_address_to_coordinates)
    monkeypatch.setattr(KakaoService, "search_nearby_facilities", mock_search_nearby_facilities)
    monkeypatch.setattr(KakaoService, "search_hazardous_facilities", mock_search_hazardous_facilities)
    monkeypatch.setattr(KakaoService, "analyze_location_accessibility", mock_analyze_location_accessibility)


@pytest.fixture
def mock_mois_service(monkeypatch):
    """행정안전부 API 모킹"""
    from app.services.mois_service import MOISService
    from app.schemas import DemographicInfo
    
    async def mock_analyze_demographics(self, address, coords):
        return DemographicInfo(
            total_population=100000,
            youth_population=30000,
            youth_ratio=30.0,
            single_households=25000,
            single_household_ratio=25.0
        )
    
    async def mock_calculate_demand_indicators(self, demographic_info, unit_type):
        return {
            "demographic_fit_score": 70,
            "market_size_score": 65
        }
    
    monkeypatch.setattr(MOISService, "analyze_demographics", mock_analyze_demographics)
    monkeypatch.setattr(MOISService, "calculate_demand_indicators", mock_calculate_demand_indicators)


@pytest.fixture
def mock_land_regulation_service(monkeypatch):
    """국토교통부 API 모킹"""
    from app.services.land_regulation_service import LandRegulationService
    from app.schemas import ZoneInfo
    
    async def mock_get_zone_info(self, coords):
        return ZoneInfo(
            zone_type="제2종일반주거지역",
            building_coverage_ratio=60.0,
            floor_area_ratio=200.0,
            height_limit=None
        )
    
    async def mock_check_development_restrictions(self, coords):
        return []
    
    monkeypatch.setattr(LandRegulationService, "get_zone_info", mock_get_zone_info)
    monkeypatch.setattr(LandRegulationService, "check_development_restrictions", mock_check_development_restrictions)


@pytest.fixture
async def test_client():
    """테스트용 AsyncClient"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_analysis_request():
    """샘플 분석 요청 데이터"""
    return {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500.0,
        "unit_type": "청년",
        "lh_version": "2024"
    }


@pytest.fixture
def sample_large_analysis_request():
    """대규모 필지 샘플 요청"""
    return {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 10000.0,
        "unit_type": "청년",
        "lh_version": "2024"
    }
