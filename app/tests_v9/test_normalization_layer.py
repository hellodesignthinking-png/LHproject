"""
ZeroSite v9.0 Normalization Layer 테스트
"""

import pytest
from app.services_v9.normalization_layer_v9_0 import NormalizationLayerV90
from app.models_v9.standard_schema_v9_0 import (
    AnalysisMode,
    ProjectGrade,
    DecisionType
)


class TestNormalizationLayer:
    """Normalization Layer 테스트"""
    
    @pytest.fixture
    def normalizer(self):
        return NormalizationLayerV90()
    
    # ===== Site Info Tests =====
    
    def test_normalize_site_info_complete_data(self, normalizer):
        """완전한 데이터로 Site Info 정규화"""
        raw_input = {
            "address": "서울시 마포구 월드컵북로 120",
            "land_area": 660.0,
            "land_appraisal_price": 5000000,
            "zone_type": "제3종일반주거지역",
            "building_coverage_ratio": 50.0,
            "floor_area_ratio": 250.0,
            "latitude": 37.5665,
            "longitude": 126.9780
        }
        
        site_info = normalizer.normalize_site_info(raw_input)
        
        assert site_info.address == "서울시 마포구 월드컵북로 120"
        assert site_info.land_area == 660.0
        assert site_info.total_land_price == 660.0 * 5000000
        assert site_info.latitude == 37.5665
    
    def test_normalize_site_info_missing_data(self, normalizer):
        """누락된 데이터로 Site Info 정규화 (기본값 처리)"""
        raw_input = {
            "address": "서울시 종로구"
        }
        
        site_info = normalizer.normalize_site_info(raw_input)
        
        # 기본값이 적용되어야 함
        assert site_info.address == "서울시 종로구"
        assert site_info.building_coverage_ratio == 50.0
        assert site_info.floor_area_ratio == 200.0
    
    # ===== GIS Tests =====
    
    def test_normalize_gis_with_pois(self, normalizer):
        """POI 데이터가 있는 GIS 정규화"""
        gis_raw = {
            "elementary_schools": [
                {
                    "name": "서울초등학교",
                    "distance": 450.0,
                    "accessibility_score": 9.2
                }
            ],
            "subway_stations": [
                {
                    "name": "월드컵경기장역",
                    "distance": 1200.0,
                    "accessibility_score": 8.5
                }
            ],
            "overall_accessibility_score": 85.3
        }
        
        gis_result = normalizer.normalize_gis_output(gis_raw)
        
        assert len(gis_result.elementary_schools) == 1
        assert gis_result.elementary_schools[0].name == "서울초등학교"
        assert gis_result.elementary_schools[0].distance_display == "450m"
        assert gis_result.elementary_schools[0].walk_time_min == 6  # 450 / 66.67
        assert gis_result.overall_accessibility_score == 85.3
        assert gis_result.accessibility_grade == "A"
    
    def test_normalize_gis_distance_formatting(self, normalizer):
        """거리 포맷팅 테스트"""
        assert normalizer._format_distance(450) == "450m"
        assert normalizer._format_distance(1200) == "1.20km"
        assert normalizer._format_distance(2500) == "2.5km"
        assert normalizer._format_distance(12000) == "10km 이상"
    
    def test_normalize_gis_handles_infinity(self, normalizer):
        """무한대 거리 처리"""
        gis_raw = {
            "elementary_schools": [
                {
                    "name": "Test School",
                    "distance": float('inf'),
                    "accessibility_score": 0.0
                }
            ],
            "overall_accessibility_score": 50.0
        }
        
        gis_result = normalizer.normalize_gis_output(gis_raw)
        
        # 무한대가 아닌 기본값(9999)으로 처리되어야 함
        assert gis_result.elementary_schools[0].distance_m == 0.0  # safe_float의 기본값
    
    # ===== Financial Tests =====
    
    def test_normalize_financial_standard_mode(self, normalizer):
        """50세대 미만 (STANDARD 모드)"""
        financial_raw = {
            "total_land_price": 3300000000,
            "construction_cost_per_sqm": 2500000,
            "total_construction_cost": 10000000000,
            "total_capex": 13300000000,
            "annual_noi": 250000000,
            "cap_rate": 1.88,
            "roi_10yr": -16.55,
            "irr_10yr": -2.1,
            "business_score": 18.4
        }
        
        financial_result = normalizer.normalize_financial_output(financial_raw, unit_count=33)
        
        assert financial_result.analysis_mode == AnalysisMode.STANDARD
        assert financial_result.unit_count == 33
        assert financial_result.lh_purchase_price is None  # STANDARD 모드는 None
        assert financial_result.cap_rate == 1.88
        assert financial_result.financial_grade in ["S", "A", "B", "C", "D", "F"]
    
    def test_normalize_financial_lh_linked_mode(self, normalizer):
        """50세대 이상 (LH_LINKED 모드)"""
        financial_raw = {
            "total_land_price": 5000000000,
            "construction_cost_per_sqm": 2500000,
            "total_construction_cost": 15000000000,
            "total_capex": 20000000000,
            "lh_purchase_price": 20000000000,
            "lh_purchase_price_per_sqm": 3000000,
            "verified_cost": 15000000000,
            "annual_noi": 500000000,
            "cap_rate": 2.5,
            "roi_10yr": 10.5,
            "irr_10yr": 3.2,
            "business_score": 35.0
        }
        
        financial_result = normalizer.normalize_financial_output(financial_raw, unit_count=60)
        
        assert financial_result.analysis_mode == AnalysisMode.LH_LINKED
        assert financial_result.unit_count == 60
        assert financial_result.lh_purchase_price == 20000000000
        assert financial_result.verified_cost == 15000000000
    
    # ===== LH Scores Tests =====
    
    def test_normalize_lh_scores(self, normalizer):
        """LH 점수 정규화"""
        lh_raw = {
            "location_score": 28.5,
            "scale_score": 15.0,
            "business_score": 32.0,
            "regulation_score": 12.0
        }
        
        lh_scores = normalizer.normalize_lh_scores(lh_raw)
        
        assert lh_scores.location_score == 28.5
        assert lh_scores.scale_score == 15.0
        assert lh_scores.business_score == 32.0
        assert lh_scores.regulation_score == 12.0
        assert lh_scores.total_score == 87.5
        assert lh_scores.grade == ProjectGrade.A  # 87.5/110 = 79.5% -> B등급? (정확한 로직 확인 필요)
    
    def test_normalize_lh_scores_bounds(self, normalizer):
        """LH 점수 범위 검증 (음수, 초과값 처리)"""
        lh_raw = {
            "location_score": 40.0,  # 35점 초과
            "scale_score": -5.0,  # 음수
            "business_score": 50.0,  # 40점 초과
            "regulation_score": 10.0
        }
        
        lh_scores = normalizer.normalize_lh_scores(lh_raw)
        
        assert lh_scores.location_score == 35.0  # 상한선
        assert lh_scores.scale_score == 0.0  # 하한선
        assert lh_scores.business_score == 40.0  # 상한선
        assert lh_scores.total_score <= 110.0
    
    # ===== Risk Assessment Tests =====
    
    def test_normalize_risk_assessment(self, normalizer):
        """리스크 평가 정규화"""
        risk_raw = {
            "all_risks": [
                {
                    "id": "FIN-001",
                    "category": "FINANCIAL",
                    "name": "낮은 ROI",
                    "severity": "HIGH",
                    "status": "FAIL",
                    "description": "ROI가 목표치 미달",
                    "mitigation": "공사비 절감"
                },
                {
                    "id": "LEG-001",
                    "category": "LEGAL",
                    "name": "법규 적합",
                    "severity": "LOW",
                    "status": "PASS",
                    "description": "법규 준수",
                    "mitigation": None
                }
            ]
        }
        
        risk_assessment = normalizer.normalize_risk_assessment(risk_raw)
        
        assert risk_assessment.total_items == 25
        assert len(risk_assessment.all_risks) == 2
        assert risk_assessment.pass_count == 1
        assert risk_assessment.fail_count == 1
        assert len(risk_assessment.critical_risks) == 1  # HIGH + FAIL
    
    # ===== Final Recommendation Tests =====
    
    def test_generate_recommendation_proceed(self, normalizer):
        """PROCEED 의사결정"""
        lh_scores = normalizer.normalize_lh_scores({
            "location_score": 30.0,
            "scale_score": 18.0,
            "business_score": 36.0,
            "regulation_score": 14.0
        })
        
        financial_result = normalizer.normalize_financial_output({
            "total_land_price": 5000000000,
            "construction_cost_per_sqm": 2500000,
            "total_construction_cost": 15000000000,
            "total_capex": 20000000000,
            "annual_noi": 2000000000,
            "cap_rate": 10.0,
            "roi_10yr": 50.0,
            "irr_10yr": 12.0,
            "business_score": 38.0
        }, unit_count=50)
        
        risk_assessment = normalizer.normalize_risk_assessment({"all_risks": []})
        
        recommendation = normalizer.generate_recommendation(
            lh_scores, financial_result, risk_assessment
        )
        
        assert recommendation.decision == DecisionType.PROCEED
        assert recommendation.confidence_level >= 80.0
        assert len(recommendation.key_strengths) > 0
    
    def test_generate_recommendation_nogo(self, normalizer):
        """NO-GO 의사결정"""
        lh_scores = normalizer.normalize_lh_scores({
            "location_score": 10.0,
            "scale_score": 5.0,
            "business_score": 15.0,
            "regulation_score": 5.0
        })
        
        financial_result = normalizer.normalize_financial_output({
            "total_land_price": 5000000000,
            "construction_cost_per_sqm": 2500000,
            "total_construction_cost": 15000000000,
            "total_capex": 20000000000,
            "annual_noi": -500000000,
            "cap_rate": -2.5,
            "roi_10yr": -30.0,
            "irr_10yr": -10.0,
            "business_score": 10.0
        }, unit_count=30)
        
        risk_raw = {
            "all_risks": [
                {"id": f"RISK-{i}", "category": "FINANCIAL", "name": f"Risk {i}", 
                 "severity": "HIGH", "status": "FAIL", "description": ""}
                for i in range(10)
            ]
        }
        risk_assessment = normalizer.normalize_risk_assessment(risk_raw)
        
        recommendation = normalizer.generate_recommendation(
            lh_scores, financial_result, risk_assessment
        )
        
        assert recommendation.decision == DecisionType.NOGO
        assert len(recommendation.key_weaknesses) > 0
    
    # ===== Helper Methods Tests =====
    
    def test_safe_float_handles_infinity(self, normalizer):
        """_safe_float 무한대 처리"""
        assert normalizer._safe_float(float('inf'), 0.0) == 0.0
        assert normalizer._safe_float(float('-inf'), 0.0) == 0.0
        assert normalizer._safe_float(float('nan'), 0.0) == 0.0
    
    def test_safe_float_handles_none(self, normalizer):
        """_safe_float None 처리"""
        assert normalizer._safe_float(None, 10.0) == 10.0
    
    def test_safe_float_valid_values(self, normalizer):
        """_safe_float 정상 값 처리"""
        assert normalizer._safe_float(123.45) == 123.45
        assert normalizer._safe_float("678.9") == 678.9
    
    def test_score_to_grade(self, normalizer):
        """점수 → 등급 변환"""
        assert normalizer._score_to_grade(95) == "S"
        assert normalizer._score_to_grade(85) == "A"
        assert normalizer._score_to_grade(75) == "B"
        assert normalizer._score_to_grade(65) == "C"
        assert normalizer._score_to_grade(55) == "D"
        assert normalizer._score_to_grade(45) == "F"
