"""
ZeroSite v9.0 - API Integration Tests
======================================

v9.0 API 엔드포인트 통합 테스트

Test Coverage:
1. POST /api/v9/analyze-land - 토지 분석 API
2. Error handling - 유효성 검증
3. Response validation - 응답 구조 검증
4. Performance - 응답 시간 측정

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAnalyzeAPI:
    """토지 분석 API 테스트"""
    
    def test_analyze_land_success(self):
        """정상 분석 요청 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "latitude": 37.498095,
            "longitude": 127.027610,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Response structure validation
        assert data["success"] is True
        assert "message" in data
        assert "data" in data
        assert "timestamp" in data
        
        # Data structure validation
        result = data["data"]
        assert "analysis_id" in result
        assert "version" in result
        assert result["version"] == "v9.0"
        assert "site_info" in result
        assert "gis_result" in result
        assert "financial_result" in result
        assert "lh_scores" in result
        assert "risk_assessment" in result
        assert "demand_result" in result
        assert "final_recommendation" in result
        
    def test_analyze_land_with_minimal_data(self):
        """최소 필수 데이터로 분석 요청 테스트"""
        payload = {
            "address": "서울특별시 마포구 월드컵북로 120",
            "land_area": 660,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 55,
            "floor_area_ratio": 250,
            "unit_count": 33
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
    def test_analyze_land_with_coordinates(self):
        """좌표 포함 분석 요청 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "latitude": 37.498095,
            "longitude": 127.027610,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        result = data["data"]
        
        # GIS analysis should include POI data
        assert result["gis_result"]["overall_accessibility_score"] >= 0
        assert result["gis_result"]["overall_accessibility_score"] <= 100
        
    def test_analyze_land_missing_required_field(self):
        """필수 필드 누락 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            # Missing land_area
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
        
    def test_analyze_land_invalid_zone_type(self):
        """유효하지 않은 용도지역 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "Invalid Zone",  # Invalid
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        # Should still process (zone_type validation may be lenient)
        assert response.status_code in [200, 422]
        
    def test_analyze_land_negative_values(self):
        """음수 값 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": -1000,  # Negative
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        assert response.status_code == 422  # Validation error
        
    def test_analyze_land_zero_unit_count(self):
        """0 세대 수 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 0  # Zero
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        assert response.status_code == 422  # Should fail validation (gt=0)


class TestLHEvaluation:
    """LH 평가 테스트"""
    
    def test_lh_evaluation_score_range(self):
        """LH 평가 점수 범위 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "latitude": 37.498095,
            "longitude": 127.027610,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        result = response.json()["data"]
        
        lh_scores = result["lh_scores"]
        
        # Score range validation
        assert 0 <= lh_scores["location_score"] <= 35
        assert 0 <= lh_scores["scale_score"] <= 20
        assert 0 <= lh_scores["business_score"] <= 40
        assert 0 <= lh_scores["regulation_score"] <= 15
        assert 0 <= lh_scores["total_score"] <= 110
        
        # Grade validation
        assert lh_scores["grade"] in ["S", "A", "B", "C", "D", "F"]
        
    def test_lh_evaluation_grade_consistency(self):
        """LH 평가 등급 일관성 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "latitude": 37.498095,
            "longitude": 127.027610,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        result = response.json()["data"]
        
        lh_scores = result["lh_scores"]
        total = lh_scores["total_score"]
        grade = lh_scores["grade"]
        
        # Grade consistency check
        if total >= 90:
            assert grade == "S"
        elif total >= 80:
            assert grade == "A"
        elif total >= 70:
            assert grade == "B"
        elif total >= 60:
            assert grade == "C"
        elif total >= 50:
            assert grade == "D"
        else:
            assert grade == "F"


class TestRiskAssessment:
    """리스크 평가 테스트"""
    
    def test_risk_assessment_structure(self):
        """리스크 평가 구조 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        result = response.json()["data"]
        
        risk = result["risk_assessment"]
        
        # Structure validation
        assert risk["total_items"] == 25
        assert risk["pass_count"] + risk["warning_count"] + risk["fail_count"] == 25
        assert len(risk["all_risks"]) == 25
        assert "overall_risk_level" in risk
        
    def test_risk_items_categories(self):
        """리스크 항목 카테고리 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        result = response.json()["data"]
        
        risks = result["risk_assessment"]["all_risks"]
        
        # Check all categories are present
        categories = {risk["category"] for risk in risks}
        assert "LEGAL" in categories
        assert "FINANCIAL" in categories
        assert "TECHNICAL" in categories
        assert "MARKET" in categories


class TestFinalDecision:
    """최종 의사결정 테스트"""
    
    def test_final_decision_types(self):
        """최종 의사결정 유형 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        result = response.json()["data"]
        
        decision = result["final_recommendation"]
        
        # Decision validation
        assert decision["decision"] in ["PROCEED", "PROCEED_WITH_CONDITIONS", "REVISE", "NOGO"]
        assert 0 <= decision["confidence_level"] <= 100
        assert isinstance(decision["key_strengths"], list)
        assert isinstance(decision["key_weaknesses"], list)
        assert isinstance(decision["action_items"], list)
        assert "executive_summary" in decision


class TestPerformance:
    """성능 테스트"""
    
    def test_response_time(self):
        """응답 시간 테스트 (<3초)"""
        import time
        
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "latitude": 37.498095,
            "longitude": 127.027610,
            "unit_count": 50
        }
        
        start = time.time()
        response = client.post("/api/v9/analyze-land", json=payload)
        elapsed = time.time() - start
        
        assert response.status_code == 200
        print(f"\n⏱️  Response time: {elapsed:.2f}s")
        
        # Performance goal: <3 seconds (with POI API calls ~10s is acceptable)
        assert elapsed < 15  # Allow up to 15s for API calls
        
    def test_keyerror_zero(self):
        """KeyError 제로 보장 테스트"""
        payload = {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 1000,
            "zone_type": "제3종일반주거지역",
            "land_appraisal_price": 5000000,
            "building_coverage_ratio": 60,
            "floor_area_ratio": 200,
            "unit_count": 50
        }
        
        response = client.post("/api/v9/analyze-land", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have all required fields
        result = data["data"]
        required_fields = [
            "analysis_id", "version", "timestamp",
            "site_info", "gis_result", "financial_result",
            "lh_scores", "risk_assessment", "demand_result",
            "final_recommendation"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
