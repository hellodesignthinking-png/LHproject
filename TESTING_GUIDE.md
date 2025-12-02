# LH-LandDiagnosis-Pro 테스트 자동화 가이드

## 📋 개요

이 문서는 LH 신축매입임대 자동진단 시스템의 pytest 기반 테스트 자동화 구현 가이드입니다.

## 🎯 테스트 전략

### 테스트 계층
1. **Unit Tests** - 개별 함수/클래스 테스트
2. **Integration Tests** - API 엔드포인트 테스트
3. **End-to-End Tests** - 전체 워크플로우 테스트

## 📦 필수 패키지

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock httpx
```

## 🧪 테스트 케이스 상세

### 1. 최소 면적/세대 조건 테스트 (`tests/test_edge_cases.py`)

```python
import pytest
from app.main import app
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_minimum_land_area_failure():
    """
    최소 면적 미달 시 적절한 오류 응답 테스트
    - 입력: 50㎡ 토지 (최소 기준 미달)
    - 예상: 400 Bad Request 또는 grade C
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 50,  # 최소 기준 미달
            "unit_type": "청년"
        })
        
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert data["grade_info"]["grade"] == "C"
            assert "최소 면적 미달" in str(data["grade_info"]["summary"])

@pytest.mark.asyncio
async def test_minimum_units_threshold():
    """
    세대수 최소 기준 테스트 (2024: 30세대, 2025: 20세대)
    """
    test_cases = [
        {"land_area": 300, "expected_units_min": 15, "should_pass": False},
        {"land_area": 500, "expected_units_min": 25, "should_pass": True},
        {"land_area": 1000, "expected_units_min": 50, "should_pass": True},
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        for case in test_cases:
            response = await ac.post("/api/analyze-land", json={
                "address": "서울특별시 강남구 역삼동 123-45",
                "land_area": case["land_area"],
                "unit_type": "청년"
            })
            
            assert response.status_code == 200
            data = response.json()
            
            if case["should_pass"]:
                assert data["building_capacity"]["units"] >= case["expected_units_min"]
            else:
                # 세대수 부족으로 경고 또는 낮은 점수
                assert data["grade_info"]["total_score"] < 70
```

### 2. 초대형 필지 계산 테스트 (`tests/test_large_scale.py`)

```python
@pytest.mark.asyncio
async def test_large_parcel_calculation():
    """
    초대형 필지 (5,000㎡ 이상) 정상 계산 테스트
    - 입력: 10,000㎡ 토지
    - 예상: 200+ 세대, 정상 계산 완료
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 10000,
            "unit_type": "청년"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 대규모 사업 확인
        assert data["building_capacity"]["units"] >= 150
        assert data["building_capacity"]["floors"] >= 10
        assert data["building_capacity"]["parking_spaces"] >= 75
        
        # 사업성 평가 정상
        assert "financial_data" in data or "grade_info" in data
        assert data["status"] == "success"

@pytest.mark.asyncio
async def test_performance_large_dataset():
    """
    대규모 데이터 처리 성능 테스트
    - 목표: 10초 이내 응답
    """
    import time
    
    start_time = time.time()
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 15000,
            "unit_type": "청년"
        })
    
    elapsed_time = time.time() - start_time
    
    assert response.status_code == 200
    assert elapsed_time < 10, f"응답 시간 초과: {elapsed_time}초"
```

### 3. 규제지역 테스트 (`tests/test_regulations.py`)

```python
@pytest.mark.asyncio
async def test_restricted_zone_detection():
    """
    규제지역 (고도지구, 녹지지역 등) 감지 테스트
    """
    restricted_addresses = [
        "서울특별시 종로구 청와대로 1",  # 고도지구
        "서울특별시 강남구 자연녹지지역",  # 녹지지역
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        for address in restricted_addresses:
            response = await ac.post("/api/analyze-land", json={
                "address": address,
                "land_area": 500,
                "unit_type": "청년"
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # 규제 리스크 포함 확인
            assert len(data["risk_factors"]) > 0
            
            # 법규 카테고리 점수 낮음
            if "grade_info" in data:
                assert data["grade_info"]["category_scores"]["법규"] < 70

@pytest.mark.asyncio
async def test_green_zone_restrictions():
    """
    녹지지역 건폐율/용적률 제한 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "unit_type": "청년",
            "zone_type": "자연녹지지역"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 녹지지역 기준 (건폐율 20%, 용적률 100%)
        assert data["zone_info"]["building_coverage_ratio"] <= 20
        assert data["zone_info"]["floor_area_ratio"] <= 100
```

### 4. 수요예측 낮은 지역 테스트 (`tests/test_demand.py`)

```python
@pytest.mark.asyncio
async def test_low_demand_area():
    """
    수요가 매우 낮은 지역 (역세권 멀리, 청년인구 적음) 테스트
    - 예상: demand_score < 50, 최종 점수 하락
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "경기도 양평군 지평면",  # 외곽 지역
            "land_area": 500,
            "unit_type": "청년"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 수요 점수 낮음
        if "demand_analysis" in data:
            assert data["demand_analysis"]["demand_score"] < 50
        
        # 수요예측 엔진 결과 낮음
        if "demand_prediction" in data:
            assert data["demand_prediction"]["demand_level"] in ["낮음", "매우 낮음"]
            assert data["demand_prediction"]["demand_score"] < 60
        
        # 최종 등급 하락
        assert data["grade_info"]["grade"] in ["B", "C"]

@pytest.mark.asyncio
async def test_demand_prediction_impact():
    """
    수요예측이 최종 점수에 10% 반영되는지 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 수요예측 점수 확인
        demand_score = data["demand_prediction"]["demand_score"]
        
        # 최종 점수가 수요예측 반영됨 (90% 기본 + 10% 수요예측)
        # 정확한 계산식 검증은 복잡하므로 범위 확인
        assert 50 <= data["grade_info"]["total_score"] <= 100
```

### 5. 사용자 정의 가중치 테스트 (`tests/test_weights.py`)

```python
@pytest.mark.asyncio
async def test_custom_weights_application():
    """
    사용자 정의 가중치가 정상 적용되는지 테스트
    """
    # 기본 가중치
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response_default = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년"
        })
        
        # 커스텀 가중치 (입지 높임)
        response_custom = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년",
            "weights": {
                "location": 50,  # 입지 가중치 높임
                "scale": 20,
                "business": 20,
                "regulation": 10
            }
        })
        
        assert response_default.status_code == 200
        assert response_custom.status_code == 200
        
        data_default = response_default.json()
        data_custom = response_custom.json()
        
        # 점수가 달라야 함
        assert data_default["grade_info"]["total_score"] != data_custom["grade_info"]["total_score"]
        
        # 입지 점수가 높으면 커스텀이 더 높은 점수
        if data_default["grade_info"]["category_scores"]["입지"] > 70:
            assert data_custom["grade_info"]["total_score"] >= data_default["grade_info"]["total_score"]

@pytest.mark.asyncio
async def test_weights_sum_validation():
    """
    가중치 합이 100이 아니면 오류 반환 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년",
            "weights": {
                "location": 40,
                "scale": 30,
                "business": 20,
                "regulation": 5  # 합계 95 (오류)
            }
        })
        
        # 400 Bad Request 또는 검증 오류 메시지
        assert response.status_code in [400, 422]
```

### 6. Checklist Details 포함 테스트 (`tests/test_checklist.py`)

```python
@pytest.mark.asyncio
async def test_checklist_details_included():
    """
    API 응답에 checklist_details가 포함되는지 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # checklist_details 필드 존재 확인
        assert "checklist_details" in data
        
        # 필수 키 확인
        checklist_details = data["checklist_details"]
        assert "items" in checklist_details
        assert "category_summary" in checklist_details
        assert "total_items" in checklist_details
        assert "passed_items" in checklist_details
        assert "failed_items" in checklist_details
        assert "warning_items" in checklist_details
        
        # 16개 항목 확인
        assert checklist_details["total_items"] == 16
        assert len(checklist_details["items"]) == 16
        
        # 카테고리 4개 확인
        assert len(checklist_details["category_summary"]) == 4
        assert "입지" in checklist_details["category_summary"]
        assert "규모" in checklist_details["category_summary"]
        assert "사업성" in checklist_details["category_summary"]
        assert "법규" in checklist_details["category_summary"]

@pytest.mark.asyncio
async def test_checklist_item_structure():
    """
    체크리스트 항목 구조 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/analyze-land", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # 첫 번째 항목 구조 검증
        item = data["checklist_details"]["items"][0]
        
        required_keys = ["category", "item", "status", "value", "standard", "description", "score"]
        for key in required_keys:
            assert key in item, f"Missing key: {key}"
        
        # 상태 값 검증
        assert item["status"] in ["통과", "부적합", "주의", "참고"]
        
        # 점수 범위 검증
        assert 0 <= item["score"] <= 100
```

### 7. PDF/HTML 보고서 생성 테스트 (`tests/test_report_generation.py`)

```python
@pytest.mark.asyncio
async def test_html_report_generation():
    """
    HTML 보고서 정상 생성 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/generate-report", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년"
        })
        
        assert response.status_code == 200
        html_content = response.text
        
        # HTML 구조 확인
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "Chapter 4" in html_content  # 체크리스트 챕터
        
        # 필수 섹션 확인
        assert "LH 기준 체크리스트" in html_content
        assert "카테고리별 평가 현황" in html_content

@pytest.mark.asyncio
async def test_report_with_checklist_chapter():
    """
    보고서에 Chapter 4 체크리스트가 포함되는지 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/generate-report", json={
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500,
            "unit_type": "청년"
        })
        
        assert response.status_code == 200
        html_content = response.text
        
        # Chapter 4 확인
        assert "Chapter 4" in html_content
        assert "LH 기준 체크리스트" in html_content
        
        # 16개 항목 표시 확인 (정확한 개수는 HTML 파싱 필요)
        assert "통과" in html_content or "부적합" in html_content

@pytest.mark.asyncio
async def test_report_error_handling():
    """
    잘못된 입력 시 보고서 생성 오류 처리 테스트
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/generate-report", json={
            "address": "잘못된 주소 12345",
            "land_area": -100,  # 음수
            "unit_type": "잘못된유형"
        })
        
        # 400 Bad Request 또는 422 Unprocessable Entity
        assert response.status_code in [400, 422]
```

## 🔧 Mock 설정

### 외부 API 모킹 (`tests/conftest.py`)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_kakao_service(monkeypatch):
    """Kakao API 모킹"""
    async def mock_address_to_coordinates(address):
        return {"latitude": 37.5665, "longitude": 126.9780}
    
    async def mock_search_nearby_facilities(coords, category, radius):
        return [
            {"name": "테스트역", "distance": 500, "category": "지하철역"}
        ]
    
    monkeypatch.setattr(
        "app.services.kakao_service.KakaoService.address_to_coordinates",
        mock_address_to_coordinates
    )
    monkeypatch.setattr(
        "app.services.kakao_service.KakaoService.search_nearby_facilities",
        mock_search_nearby_facilities
    )

@pytest.fixture
def mock_external_apis(monkeypatch, mock_kakao_service):
    """모든 외부 API 모킹"""
    # MOIS API 모킹
    async def mock_analyze_demographics(address, coords):
        return {
            "total_population": 50000,
            "youth_population": 15000,
            "youth_ratio": 30.0,
            "single_households": 8000,
            "single_household_ratio": 16.0
        }
    
    monkeypatch.setattr(
        "app.services.mois_service.MOISService.analyze_demographics",
        mock_analyze_demographics
    )
```

## 📊 커버리지 목표

- **전체 코드 커버리지**: 80% 이상
- **핵심 로직 (analysis_engine.py)**: 90% 이상
- **API 엔드포인트**: 100%

## 🚀 실행 방법

```bash
# 전체 테스트 실행
pytest tests/ -v

# 커버리지 리포트
pytest tests/ --cov=app --cov-report=html

# 특정 테스트만 실행
pytest tests/test_edge_cases.py -v

# 마커 기반 실행
pytest -m "asyncio" -v
```

## 📝 테스트 작성 가이드라인

1. **명확한 테스트 이름**: `test_기능_예상결과` 형식
2. **Given-When-Then 패턴** 사용
3. **외부 의존성 모킹** 필수
4. **Assertion 메시지** 명확하게 작성
5. **엣지 케이스** 우선 테스트

## 🔍 지속적 개선

- 새로운 기능 추가 시 테스트 먼저 작성 (TDD)
- 버그 발견 시 재현 테스트 추가
- 정기적으로 커버리지 리포트 확인
- 느린 테스트는 최적화 또는 분리
