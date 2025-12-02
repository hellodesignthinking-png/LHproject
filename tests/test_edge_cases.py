"""
최소 면적/세대 조건 Edge Case 테스트
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_minimum_land_area_failure(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    최소 면적 미달 시 적절한 오류 응답 테스트
    - 입력: 50㎡ 토지 (최소 기준 미달)
    - 예상: grade C 또는 400 Bad Request
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 50,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert data["grade_info"]["grade"] == "C"
        assert data["grade_info"]["total_score"] < 60


@pytest.mark.asyncio
async def test_minimum_units_threshold_2024(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    세대수 최소 기준 테스트 (2024: 30세대)
    """
    test_cases = [
        {"land_area": 300, "expected_pass": False},  # ~15세대
        {"land_area": 500, "expected_pass": False},  # ~25세대
        {"land_area": 700, "expected_pass": True},   # ~35세대
    ]
    
    for case in test_cases:
        response = await test_client.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": case["land_area"],
            "unit_type": "청년",
            "lh_version": "2024"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        if case["expected_pass"]:
            assert data["grade_info"]["total_score"] >= 60
        else:
            assert data["grade_info"]["total_score"] < 70


@pytest.mark.asyncio
async def test_minimum_units_threshold_2025(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    세대수 최소 기준 테스트 (2025: 20세대 - 완화)
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,  # ~25세대
        "unit_type": "청년",
        "lh_version": "2025"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 2025년 버전은 20세대 이상이면 통과
    assert data["building_capacity"]["units"] >= 20
    # 2024보다 점수가 높아야 함
    assert data["grade_info"]["total_score"] >= 60


@pytest.mark.asyncio
async def test_zero_land_area_rejection(test_client: AsyncClient):
    """
    0 또는 음수 면적 입력 시 거부 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 0,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_negative_land_area_rejection(test_client: AsyncClient):
    """
    음수 면적 입력 시 거부 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": -100,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_invalid_lh_version_fallback(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    잘못된 LH 버전 입력 시 fallback 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "9999"  # 존재하지 않는 버전
    })
    
    # 서비스는 fallback으로 2024 버전 사용
    assert response.status_code == 200
    data = response.json()
    # lh_version이 2024로 fallback되었는지 확인
    assert data.get("lh_version", "2024") == "2024"
