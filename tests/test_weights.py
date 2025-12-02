"""
사용자 정의 가중치 조합 테스트
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_custom_weights_application(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    사용자 정의 가중치 적용 테스트
    - 입지 40%, 규모 20%, 사업성 25%, 법규 15%
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024",
        "weights": {
            "location": 40,
            "scale": 20,
            "business": 25,
            "regulation": 15
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Grade 정보 존재
    assert "grade_info" in data
    assert "category_scores" in data["grade_info"]
    
    # 총점이 100점 만점으로 계산됨
    assert 0 <= data["grade_info"]["total_score"] <= 100


@pytest.mark.asyncio
async def test_extreme_weights_location_focus(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    극단적 가중치 테스트 - 입지 중시 (입지 70%)
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024",
        "weights": {
            "location": 70,
            "scale": 10,
            "business": 10,
            "regulation": 10
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 입지 점수가 전체 점수에 큰 영향
    location_score = data["grade_info"]["category_scores"]["입지"]
    total_score = data["grade_info"]["total_score"]
    
    # 입지 점수가 낮으면 전체 점수도 낮아야 함
    if location_score < 50:
        assert total_score < 60


@pytest.mark.asyncio
async def test_extreme_weights_business_focus(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    극단적 가중치 테스트 - 사업성 중시 (사업성 70%)
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "land_appraisal_price": 5500000,  # 550만원/㎡
        "lh_version": "2024",
        "weights": {
            "location": 10,
            "scale": 10,
            "business": 70,
            "regulation": 10
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 사업성 점수가 전체 점수에 큰 영향
    business_score = data["grade_info"]["category_scores"]["사업성"]
    total_score = data["grade_info"]["total_score"]
    
    # 사업성 점수와 전체 점수의 상관관계
    assert abs(total_score - business_score * 0.7) < 30  # 오차 범위 30점


@pytest.mark.asyncio
async def test_invalid_weights_sum_not_100(
    test_client: AsyncClient
):
    """
    잘못된 가중치 합계 테스트 (합계가 100이 아님)
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024",
        "weights": {
            "location": 50,
            "scale": 30,
            "business": 30,  # 합계 110
            "regulation": 0
        }
    })
    
    # Validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_weights_comparison_default_vs_custom(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    기본 가중치 vs 사용자 정의 가중치 비교
    """
    base_request = {
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    }
    
    # 기본 가중치
    response_default = await test_client.post("/api/analyze-land", json=base_request)
    
    # 사용자 정의 가중치 (입지 중시)
    response_custom = await test_client.post("/api/analyze-land", json={
        **base_request,
        "weights": {
            "location": 50,
            "scale": 20,
            "business": 20,
            "regulation": 10
        }
    })
    
    assert response_default.status_code == 200
    assert response_custom.status_code == 200
    
    data_default = response_default.json()
    data_custom = response_custom.json()
    
    # 카테고리 점수는 동일해야 함
    assert data_default["grade_info"]["category_scores"]["입지"] == \
           data_custom["grade_info"]["category_scores"]["입지"]
    
    # 총점은 다를 수 있음 (가중치가 다르므로)
    # 입지 점수가 높으면 사용자 정의(입지 중시)가 더 높아야 함
    location_score = data_default["grade_info"]["category_scores"]["입지"]
    if location_score > 70:
        assert data_custom["grade_info"]["total_score"] >= data_default["grade_info"]["total_score"]


@pytest.mark.asyncio
async def test_weights_with_different_lh_versions(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    LH 버전별 가중치 적용 테스트
    """
    custom_weights = {
        "location": 35,
        "scale": 25,
        "business": 25,
        "regulation": 15
    }
    
    # 2024 버전
    response_2024 = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024",
        "weights": custom_weights
    })
    
    # 2025 버전
    response_2025 = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2025",
        "weights": custom_weights
    })
    
    assert response_2024.status_code == 200
    assert response_2025.status_code == 200
    
    data_2024 = response_2024.json()
    data_2025 = response_2025.json()
    
    # 가중치는 동일하게 적용되지만, 버전별 기준이 달라 점수는 다를 수 있음
    assert "grade_info" in data_2024
    assert "grade_info" in data_2025
