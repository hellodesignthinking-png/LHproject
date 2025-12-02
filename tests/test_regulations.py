"""
규제 지역 및 제한 사항 테스트
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_green_zone_restriction(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    monkeypatch
):
    """
    녹지지역 제한 테스트
    - 건폐율 20%, 용적률 100%
    """
    from app.services.land_regulation_service import LandRegulationService
    from app.schemas import ZoneInfo
    
    async def mock_get_zone_info_green(self, coords):
        return ZoneInfo(
            zone_type="자연녹지지역",
            building_coverage_ratio=20.0,
            floor_area_ratio=100.0,
            height_limit=None
        )
    
    monkeypatch.setattr(LandRegulationService, "get_zone_info", mock_get_zone_info_green)
    monkeypatch.setattr(LandRegulationService, "check_development_restrictions", lambda self, coords: [])
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "경기도 용인시 녹지구역",
        "land_area": 1000,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 녹지지역은 낮은 용적률로 인해 세대수 적음
    assert data["building_capacity"]["units"] < 50
    # 법규 카테고리 점수 확인
    assert "grade_info" in data


@pytest.mark.asyncio
async def test_height_limit_restriction(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    monkeypatch
):
    """
    고도제한 지역 테스트
    - 높이제한 15m
    """
    from app.services.land_regulation_service import LandRegulationService
    from app.schemas import ZoneInfo
    
    async def mock_get_zone_info_height(self, coords):
        return ZoneInfo(
            zone_type="제2종일반주거지역",
            building_coverage_ratio=60.0,
            floor_area_ratio=200.0,
            height_limit=15.0  # 15m 높이제한 (약 5층)
        )
    
    monkeypatch.setattr(LandRegulationService, "get_zone_info", mock_get_zone_info_height)
    monkeypatch.setattr(LandRegulationService, "check_development_restrictions", lambda self, coords: [])
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 1000,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 높이제한으로 층수 제한
    assert data["building_capacity"]["floors"] <= 5


@pytest.mark.asyncio
async def test_hazardous_facility_critical(
    test_client: AsyncClient,
    mock_mois_service,
    mock_land_regulation_service,
    monkeypatch
):
    """
    주유소 25m 이내 절대 탈락 테스트
    """
    from app.services.kakao_service import KakaoService
    from app.schemas import Coordinates
    
    async def mock_address_to_coordinates(self, address: str):
        return Coordinates(latitude=37.5665, longitude=126.9780)
    
    async def mock_search_hazardous_facilities_critical(self, coords, unit_type=None):
        return [
            {
                "name": "주유소A",
                "category": "주유소",
                "distance": 20,  # 25m 이내
                "address": "서울특별시 강남구"
            }
        ]
    
    async def mock_analyze_location_accessibility(self, coords):
        return {
            "nearest_subway_distance": 500,
            "nearest_school_distance": 800,
            "accessibility_score": 75,
            "subway_stations": []
        }
    
    async def mock_search_nearby_facilities(self, coords, category, radius=2000):
        return []
    
    monkeypatch.setattr(KakaoService, "address_to_coordinates", mock_address_to_coordinates)
    monkeypatch.setattr(KakaoService, "search_hazardous_facilities", mock_search_hazardous_facilities_critical)
    monkeypatch.setattr(KakaoService, "analyze_location_accessibility", mock_analyze_location_accessibility)
    monkeypatch.setattr(KakaoService, "search_nearby_facilities", mock_search_nearby_facilities)
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 절대 탈락 사유로 인해 매입 부적격
    assert data["summary"]["is_eligible"] == False
    # Risk factor에 critical 존재
    assert any(risk["severity"] == "critical" for risk in data["risk_factors"])


@pytest.mark.asyncio
async def test_development_restriction_area(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    monkeypatch
):
    """
    개발제한구역 테스트
    """
    from app.services.land_regulation_service import LandRegulationService
    from app.schemas import ZoneInfo
    
    async def mock_get_zone_info(self, coords):
        return ZoneInfo(
            zone_type="자연환경보전지역",
            building_coverage_ratio=20.0,
            floor_area_ratio=80.0,
            height_limit=None
        )
    
    async def mock_check_development_restrictions(self, coords):
        return ["개발제한구역", "수질보전구역"]
    
    monkeypatch.setattr(LandRegulationService, "get_zone_info", mock_get_zone_info)
    monkeypatch.setattr(LandRegulationService, "check_development_restrictions", mock_check_development_restrictions)
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "경기도 양평군 개발제한구역",
        "land_area": 1000,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 개발제한구역으로 인한 리스크
    assert len(data["risk_factors"]) > 0
    # 매입 부적격
    assert data["summary"]["is_eligible"] == False


@pytest.mark.asyncio
async def test_commercial_zone_conditional(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    monkeypatch
):
    """
    상업지역 조건부 적격 테스트
    """
    from app.services.land_regulation_service import LandRegulationService
    from app.schemas import ZoneInfo
    
    async def mock_get_zone_info_commercial(self, coords):
        return ZoneInfo(
            zone_type="일반상업지역",
            building_coverage_ratio=80.0,
            floor_area_ratio=1300.0,
            height_limit=None
        )
    
    monkeypatch.setattr(LandRegulationService, "get_zone_info", mock_get_zone_info_commercial)
    monkeypatch.setattr(LandRegulationService, "check_development_restrictions", lambda self, coords: [])
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 상업지역은 조건부 통과 (법규 점수가 주거지역보다 낮음)
    assert data["grade_info"]["category_scores"]["법규"] < 100
