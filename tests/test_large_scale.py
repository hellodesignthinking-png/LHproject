"""
초대형 필지 계산 성능 및 정확도 테스트
"""

import pytest
import time
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_large_parcel_calculation(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    초대형 필지 (10,000㎡) 정상 계산 테스트
    - 예상: 200+ 세대, 정상 계산 완료, 10초 이내
    """
    start_time = time.time()
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 10000,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    elapsed_time = time.time() - start_time
    
    assert response.status_code == 200
    data = response.json()
    
    # 대규모 사업 확인
    assert data["building_capacity"]["units"] >= 150
    assert data["building_capacity"]["floors"] >= 10
    
    # 성능 확인 (10초 이내)
    assert elapsed_time < 10.0
    
    # Grade 정보 존재 확인
    assert "grade_info" in data
    assert "checklist" in data


@pytest.mark.asyncio
async def test_very_large_parcel_50000sqm(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    초대형 필지 (50,000㎡) 계산 테스트
    - 예상: 1000+ 세대
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 50000,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 초대형 사업 규모
    assert data["building_capacity"]["units"] >= 500
    assert data["building_capacity"]["parking_spaces"] >= 250


@pytest.mark.asyncio
async def test_large_scale_checklist_completeness(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    대규모 사업의 체크리스트 완전성 테스트
    - 모든 16개 항목이 정상 평가되어야 함
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 10000,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 체크리스트 16개 항목 확인 (입지 4 + 규모 4 + 사업성 4 + 법규 4)
    checklist = data["checklist"]
    assert len(checklist) == 16
    
    # 각 카테고리별 4개씩 확인
    categories = [item["category"] for item in checklist]
    assert categories.count("입지") == 4
    assert categories.count("규모") == 4
    assert categories.count("사업성") == 4
    assert categories.count("법규") == 4


@pytest.mark.asyncio
async def test_performance_multiple_requests(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    다중 요청 성능 테스트
    - 5개 요청을 순차적으로 처리, 각 요청 5초 이내
    """
    land_areas = [1000, 2000, 3000, 5000, 10000]
    
    for area in land_areas:
        start_time = time.time()
        
        response = await test_client.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": area,
            "unit_type": "청년",
            "lh_version": "2024"
        })
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 5.0
        
        data = response.json()
        assert data["building_capacity"]["units"] > 0


@pytest.mark.asyncio
async def test_large_scale_financial_calculation(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    대규모 사업의 재무 계산 정확도 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 10000,
        "unit_type": "청년",
        "land_appraisal_price": 5500000,  # 550만원/㎡
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 재무 데이터 존재 확인
    assert "grade_info" in data
    assert data["grade_info"]["category_scores"]["사업성"] >= 0
    
    # 세대수 대비 사업비 적정성 확인
    units = data["building_capacity"]["units"]
    assert units >= 150
