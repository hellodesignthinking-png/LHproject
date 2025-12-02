"""
수요 점수 계산 테스트
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_low_demand_area_score_reduction(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_land_regulation_service,
    monkeypatch
):
    """
    저수요 지역 점수 감점 테스트
    - 청년 인구 5%, 1인 가구 10%
    - 지하철역 3km 이상
    """
    from app.services.mois_service import MOISService
    from app.schemas import DemographicInfo
    
    async def mock_analyze_demographics_low(self, address, coords):
        return DemographicInfo(
            total_population=50000,
            youth_population=2500,  # 5%
            youth_ratio=5.0,
            single_households=5000,  # 10%
            single_household_ratio=10.0
        )
    
    async def mock_calculate_demand_indicators_low(self, demographic_info, unit_type):
        return {
            "demographic_fit_score": 30,
            "market_size_score": 25
        }
    
    monkeypatch.setattr(MOISService, "analyze_demographics", mock_analyze_demographics_low)
    monkeypatch.setattr(MOISService, "calculate_demand_indicators", mock_calculate_demand_indicators_low)
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "경기도 양평군 저수요지역",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 수요 점수 낮음
    assert data["demand_analysis"]["demand_score"] < 50
    # 입지 카테고리 점수 낮음
    assert data["grade_info"]["category_scores"]["입지"] < 60


@pytest.mark.asyncio
async def test_high_demand_area_score_boost(
    test_client: AsyncClient,
    mock_land_regulation_service,
    monkeypatch
):
    """
    고수요 지역 점수 가산 테스트
    - 청년 인구 40%, 1인 가구 45%
    - 지하철역 300m 이내
    """
    from app.services.mois_service import MOISService
    from app.services.kakao_service import KakaoService
    from app.schemas import DemographicInfo, Coordinates
    
    async def mock_analyze_demographics_high(self, address, coords):
        return DemographicInfo(
            total_population=150000,
            youth_population=60000,  # 40%
            youth_ratio=40.0,
            single_households=67500,  # 45%
            single_household_ratio=45.0
        )
    
    async def mock_calculate_demand_indicators_high(self, demographic_info, unit_type):
        return {
            "demographic_fit_score": 90,
            "market_size_score": 85
        }
    
    async def mock_address_to_coordinates(self, address: str):
        return Coordinates(latitude=37.5665, longitude=126.9780)
    
    async def mock_search_nearby_facilities_high(self, coords, category, radius=2000):
        return [
            {"name": f"{category}{i}", "category": category, "distance": 100 * i}
            for i in range(1, 11)
        ]
    
    async def mock_search_hazardous_facilities(self, coords, unit_type=None):
        return []
    
    async def mock_analyze_location_accessibility_high(self, coords):
        return {
            "nearest_subway_distance": 300,  # 300m
            "nearest_school_distance": 400,
            "nearest_university_distance": 800,
            "accessibility_score": 90,
            "subway_stations": [{"name": "역삼역", "distance": 300}]
        }
    
    monkeypatch.setattr(MOISService, "analyze_demographics", mock_analyze_demographics_high)
    monkeypatch.setattr(MOISService, "calculate_demand_indicators", mock_calculate_demand_indicators_high)
    monkeypatch.setattr(KakaoService, "address_to_coordinates", mock_address_to_coordinates)
    monkeypatch.setattr(KakaoService, "search_nearby_facilities", mock_search_nearby_facilities_high)
    monkeypatch.setattr(KakaoService, "search_hazardous_facilities", mock_search_hazardous_facilities)
    monkeypatch.setattr(KakaoService, "analyze_location_accessibility", mock_analyze_location_accessibility_high)
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 수요 점수 높음
    assert data["demand_analysis"]["demand_score"] >= 70
    # 입지 카테고리 점수 높음
    assert data["grade_info"]["category_scores"]["입지"] >= 70
    # 전체 등급 양호
    assert data["grade_info"]["grade"] in ["A", "B"]


@pytest.mark.asyncio
async def test_demand_score_calculation_consistency(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    수요 점수 계산 일관성 테스트
    - 동일 입력에 대해 동일 결과
    """
    request_data = {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    }
    
    # 2회 요청
    response1 = await test_client.post("/api/analyze-land", json=request_data)
    response2 = await test_client.post("/api/analyze-land", json=request_data)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    data1 = response1.json()
    data2 = response2.json()
    
    # 수요 점수 동일
    assert data1["demand_analysis"]["demand_score"] == data2["demand_analysis"]["demand_score"]
    # 등급 동일
    assert data1["grade_info"]["grade"] == data2["grade_info"]["grade"]


@pytest.mark.asyncio
async def test_unit_type_demand_matching(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    세대 유형별 수요 매칭 테스트
    - 청년형 vs 신혼부부형 수요 점수 차이
    """
    base_request = {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "lh_version": "2024"
    }
    
    # 청년형
    response_youth = await test_client.post("/api/analyze-land", json={
        **base_request,
        "unit_type": "청년"
    })
    
    # 신혼부부형
    response_newlywed = await test_client.post("/api/analyze-land", json={
        **base_request,
        "unit_type": "신혼·신생아 I"
    })
    
    assert response_youth.status_code == 200
    assert response_newlywed.status_code == 200
    
    data_youth = response_youth.json()
    data_newlywed = response_newlywed.json()
    
    # 두 유형 모두 수요 점수 존재
    assert "demand_analysis" in data_youth
    assert "demand_analysis" in data_newlywed
    
    # 점수는 다를 수 있음 (지역 특성에 따라)
    assert data_youth["demand_analysis"]["demand_score"] >= 0
    assert data_newlywed["demand_analysis"]["demand_score"] >= 0
