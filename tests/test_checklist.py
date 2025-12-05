"""
체크리스트 상세 정보 테스트
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_checklist_details_included(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    체크리스트 상세 정보 포함 테스트
    - checklist_details 필드 존재
    - 16개 항목 (입지 4 + 규모 4 + 사업성 4 + 법규 4)
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # checklist_details 필드 존재
    assert "checklist_details" in data
    checklist_details = data["checklist_details"]
    
    # 기본 구조 확인
    assert "total_items" in checklist_details
    assert "passed_items" in checklist_details
    assert "failed_items" in checklist_details
    assert "warning_items" in checklist_details
    assert "category_summary" in checklist_details
    
    # 총 16개 항목
    assert checklist_details["total_items"] == 16
    
    # 카테고리별 요약 (4개 카테고리)
    assert len(checklist_details["category_summary"]) == 4
    assert "입지" in checklist_details["category_summary"]
    assert "규모" in checklist_details["category_summary"]
    assert "사업성" in checklist_details["category_summary"]
    assert "법규" in checklist_details["category_summary"]


@pytest.mark.asyncio
async def test_checklist_category_summary_structure(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    카테고리별 요약 구조 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    category_summary = data["checklist_details"]["category_summary"]
    
    # 각 카테고리별 구조 확인
    for category in ["입지", "규모", "사업성", "법규"]:
        assert category in category_summary
        cat_info = category_summary[category]
        
        # 필수 필드
        assert "total" in cat_info
        assert "passed" in cat_info
        assert "failed" in cat_info
        assert "warning" in cat_info
        assert "info" in cat_info
        assert "score" in cat_info
        
        # 각 카테고리 4개 항목
        assert cat_info["total"] == 4
        
        # 통과+실패+경고+정보 = 총 항목
        assert (cat_info["passed"] + cat_info["failed"] + 
                cat_info["warning"] + cat_info["info"]) == cat_info["total"]


@pytest.mark.asyncio
async def test_checklist_items_detail(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    개별 체크리스트 항목 상세 정보 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    items = data["checklist_details"]["items"]
    
    # 16개 항목 상세 정보
    assert len(items) == 16
    
    # 각 항목 구조 확인
    for item in items:
        assert "category" in item
        assert "item" in item
        assert "status" in item
        assert "value" in item
        assert "standard" in item
        assert "description" in item
        assert "score" in item
        
        # 상태 값 검증
        assert item["status"] in ["통과", "부적합", "주의", "참고"]
        
        # 점수 범위 검증
        assert 0 <= item["score"] <= 100


@pytest.mark.asyncio
async def test_checklist_pass_rate_calculation(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    체크리스트 통과율 계산 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    checklist_details = data["checklist_details"]
    
    total = checklist_details["total_items"]
    passed = checklist_details["passed_items"]
    failed = checklist_details["failed_items"]
    warning = checklist_details["warning_items"]
    info = checklist_details["info_items"]
    
    # 합계 일치
    assert total == passed + failed + warning + info
    
    # 통과율 계산 (통과 + 참고)
    pass_rate = (passed + info) / total * 100
    assert 0 <= pass_rate <= 100


@pytest.mark.asyncio
async def test_checklist_version_specific_criteria(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    LH 버전별 체크리스트 기준 적용 테스트
    """
    # 2024 버전
    response_2024 = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    # 2025 버전
    response_2025 = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2025"
    })
    
    assert response_2024.status_code == 200
    assert response_2025.status_code == 200
    
    data_2024 = response_2024.json()
    data_2025 = response_2025.json()
    
    # 둘 다 16개 항목
    assert data_2024["checklist_details"]["total_items"] == 16
    assert data_2025["checklist_details"]["total_items"] == 16
    
    # 2025년은 기준 완화로 통과율이 더 높을 수 있음
    pass_rate_2024 = data_2024["checklist_details"]["passed_items"]
    pass_rate_2025 = data_2025["checklist_details"]["passed_items"]
    
    # 세대수 기준 완화로 2025년이 유리
    assert pass_rate_2025 >= pass_rate_2024 - 2  # 오차 허용


@pytest.mark.asyncio
async def test_checklist_integration_with_grade(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    체크리스트와 등급 정보 통합 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 1000,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 체크리스트와 등급 정보 모두 존재
    assert "checklist" in data
    assert "checklist_details" in data
    assert "grade_info" in data
    
    # 카테고리별 점수 일치
    checklist_category_scores = {
        cat: info["score"]
        for cat, info in data["checklist_details"]["category_summary"].items()
    }
    
    grade_category_scores = data["grade_info"]["category_scores"]
    
    # 각 카테고리 점수가 일치해야 함
    for category in ["입지", "규모", "사업성", "법규"]:
        assert abs(checklist_category_scores[category] - 
                   grade_category_scores[category]) < 0.1
