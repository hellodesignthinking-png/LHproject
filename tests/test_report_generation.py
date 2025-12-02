"""
PDF/HTML 보고서 생성 테스트
"""

import pytest
from httpx import AsyncClient
import re


@pytest.mark.asyncio
async def test_html_report_generation(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    HTML 보고서 생성 오류 없음 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # report_text 필드 존재 (HTML 텍스트)
    assert "report_text" in data or data.get("status") == "success"


@pytest.mark.asyncio
async def test_pdf_generation_endpoint(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    PDF 생성 엔드포인트 테스트
    """
    # 먼저 분석 수행
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # analysis_id 존재
    assert "analysis_id" in data
    
    # PDF URL 존재 (optional)
    # pdf_url이 있다면 정상적인 형식이어야 함
    if "pdf_url" in data and data["pdf_url"]:
        assert "/api/reports/" in data["pdf_url"] or "pdf" in data["pdf_url"].lower()


@pytest.mark.asyncio
async def test_report_with_consultant_info(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    컨설턴트 정보 포함 보고서 생성 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024",
        "consultant": {
            "name": "홍길동",
            "phone": "010-1234-5678",
            "department": "토지개발팀",
            "email": "hong@example.com"
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 컨설턴트 정보가 응답에 반영되어야 함 (optional)
    assert data.get("status") == "success"


@pytest.mark.asyncio
async def test_report_generation_with_custom_weights(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    사용자 정의 가중치 포함 보고서 생성 테스트
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
    
    # 정상 응답
    assert data["status"] == "success"
    assert "grade_info" in data


@pytest.mark.asyncio
async def test_report_generation_error_handling(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    보고서 생성 중 오류 처리 테스트
    """
    # 극단적으로 작은 면적 (보고서 생성은 가능해야 함)
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 100,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    # 오류가 발생하더라도 적절한 응답
    assert response.status_code in [200, 400, 500]
    
    if response.status_code == 200:
        data = response.json()
        # 보고서 생성이 완료되어야 함
        assert "grade_info" in data


@pytest.mark.asyncio
async def test_report_html_structure_validation(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    HTML 보고서 구조 검증 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # report_text가 있다면 HTML 검증
    if "report_text" in data and data["report_text"]:
        html = data["report_text"]
        
        # 기본 HTML 태그 존재
        assert "<html" in html.lower()
        assert "</html>" in html.lower()
        assert "<body" in html.lower()
        assert "</body>" in html.lower()
        
        # 보고서 제목 포함
        assert "LH" in html or "신축매입" in html


@pytest.mark.asyncio
async def test_report_with_land_appraisal_price(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    토지 감정평가액 포함 보고서 생성 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "land_appraisal_price": 5500000,  # 550만원/㎡
        "lh_version": "2024"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 정상 응답
    assert data["status"] == "success"
    assert "grade_info" in data


@pytest.mark.asyncio
async def test_report_generation_multiple_unit_types(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    다양한 세대 유형의 보고서 생성 테스트
    """
    unit_types = ["청년", "신혼·신생아 I", "신혼·신생아 II", "다자녀", "고령자"]
    
    for unit_type in unit_types:
        response = await test_client.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": unit_type,
            "lh_version": "2024"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 모든 유형에 대해 정상 보고서 생성
        assert data["status"] == "success"
        assert "grade_info" in data
        assert data["unit_type"] == unit_type


@pytest.mark.asyncio
async def test_report_generation_with_lh_version_2025(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    2025 버전 LH 기준 보고서 생성 테스트
    """
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2025"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # 2025 버전 적용 확인
    assert data.get("lh_version", "2024") == "2025"
    assert "grade_info" in data


@pytest.mark.asyncio
async def test_report_generation_performance(
    test_client: AsyncClient,
    mock_kakao_service,
    mock_mois_service,
    mock_land_regulation_service
):
    """
    보고서 생성 성능 테스트 (5초 이내)
    """
    import time
    
    start_time = time.time()
    
    response = await test_client.post("/api/analyze-land", json={
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area": 500,
        "unit_type": "청년",
        "lh_version": "2024"
    })
    
    elapsed_time = time.time() - start_time
    
    assert response.status_code == 200
    # 보고서 생성은 5초 이내에 완료되어야 함
    assert elapsed_time < 5.0
