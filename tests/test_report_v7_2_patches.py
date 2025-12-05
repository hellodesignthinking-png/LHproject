"""
PATCH 11: Unit Tests for Report Engine v7.2
Validates that engine JSON → report output is correct for all 11 critical patches
"""

import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.report_field_mapper_v7_2_complete import ReportFieldMapperV72Complete


class TestReportV72Patches:
    """Test suite for all 11 critical patches"""
    
    @pytest.fixture
    def mapper(self):
        """Create mapper instance"""
        return ReportFieldMapperV72Complete()
    
    @pytest.fixture
    def sample_engine_output(self):
        """Sample v7.2 engine output"""
        return {
            "coordinates": "latitude=37.5639 longitude=126.9133",
            "zone_info": {
                "land_use_zone": "제2종일반주거지역",
                "building_coverage_ratio": 60.0,
                "floor_area_ratio": 200.0,
                "height_limit": 35.0,
                "overlay_zones": ["경관지구"],
                "district_unit_plan": False,
                "development_restrictions": [],
                "road_width": 8.0,
                "water_supply": True,
            },
            "demand_analysis": {
                "demand_score": 66.5,
                "key_factors": [
                    "초등학교 288m",
                    "병원 179m",
                    "가좌역 548m",
                    "대학교 372m",
                ],
            },
            "grade_info": {
                "grade": "A",
                "total_score": 86.27,
                "category_scores": {
                    "입지": 92.5,
                    "규모": 86.25,
                    "사업성": 85.0,
                    "법규": 75.0,
                },
            },
            "type_demand_scores": {
                "청년": 74.0,
                "신혼·신생아 I": 84.0,
                "신혼·신생아 II": 70.0,
                "다자녀": 76.0,
                "고령자": 94.0,
            },
            "geo_optimization": {
                "optimization_score": 82.0,
                "recommended_sites": [
                    {"location": "Alternative 1", "distance": 500, "score": 85.0, "reason": "Better access"},
                    {"location": "Alternative 2", "distance": 800, "score": 80.0, "reason": "Lower price"},
                ],
                "current_site_strengths": ["교통 편의", "학교 접근성"],
                "current_site_weaknesses": ["주차 공간 부족"],
            },
            "demand_prediction": {
                "predicted_demand_score": 88.2,
                "demand_level": "높음",
            },
            "building_capacity": {
                "estimated_units": 44,
                "estimated_floors": 4,
                "building_coverage_ratio": 60.0,
                "floor_area_ratio": 200.0,
                "parking_spaces": 22,
            },
            "risk_factors": [],
            "summary": {
                "address": "월드컵북로 120",
                "land_area": 660.0,
                "is_eligible": True,
                "estimated_units": 44,
                "demand_score": 66.5,
                "recommendation": "검토 필요 - 조건부 적합",
                "risk_count": 0,
                "grade": "A",
                "total_score": 86.27,
            },
            "financial_data": {
                "total_project_cost": 2479641841,
                "profit": 4120358159,
                "profit_rate": 166.17,
                "roi": 166.17,
            },
            "negotiation_strategy": {
                "strategies": ["가격 협상", "단계적 매입"],
                "priority_factors": ["입지", "가격"],
                "recommended_approach": "적극 협상",
            },
            "lh_version": "2024",
        }
    
    def test_patch_1_poi_v3_1_fields(self, mapper, sample_engine_output):
        """
        PATCH 1: POI v3.1 fields
        - final_distance_m
        - lh_grade
        - weight_applied_distance
        - total_score_v3_1
        """
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        poi = result["poi_analysis_v3_1"]
        
        assert "final_distance_m" in poi, "Missing final_distance_m"
        assert "lh_grade" in poi, "Missing lh_grade"
        assert "weight_applied_distance" in poi, "Missing weight_applied_distance"
        assert "total_score_v3_1" in poi, "Missing total_score_v3_1"
        assert poi["version"] == "3.1", "Version should be 3.1"
        assert poi["lh_grade"] == "A", f"Expected grade A, got {poi['lh_grade']}"
        assert poi["total_score_v3_1"] > 0, "Score should be > 0"
    
    def test_patch_2_type_demand_v3_1_scoring(self, mapper, sample_engine_output):
        """
        PATCH 2: Type Demand v3.1 scoring
        - final_score
        - raw_score
        - poi_bonus
        - user_type_weight
        """
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        type_demand = result["type_demand_v3_1"]
        
        assert "type_scores" in type_demand, "Missing type_scores"
        assert "version" in type_demand, "Missing version"
        assert type_demand["version"] == "3.1", "Version should be 3.1"
        
        # Check each type has required fields
        for type_name, scores in type_demand["type_scores"].items():
            assert "raw_score" in scores, f"{type_name}: Missing raw_score"
            assert "poi_bonus" in scores, f"{type_name}: Missing poi_bonus"
            assert "user_type_weight" in scores, f"{type_name}: Missing user_type_weight"
            assert "final_score" in scores, f"{type_name}: Missing final_score"
            assert scores["final_score"] > scores["raw_score"], "Final score should include bonus"
    
    def test_patch_3_multi_parcel_v3_0(self, mapper, sample_engine_output):
        """
        PATCH 3: Multi-Parcel v3.0
        - combined_center
        - compactness_ratio
        - shape_penalty
        - recommendation_level
        """
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        mp = result["multi_parcel_v3_0"]
        
        assert "combined_center" in mp, "Missing combined_center"
        assert "compactness_ratio" in mp, "Missing compactness_ratio"
        assert "shape_penalty" in mp, "Missing shape_penalty"
        assert "recommendation_level" in mp, "Missing recommendation_level"
        assert mp["version"] == "3.0", "Version should be 3.0"
    
    def test_patch_4_geo_optimizer_v3_1(self, mapper, sample_engine_output):
        """
        PATCH 4: GeoOptimizer v3.1
        - final_score
        - weighted_total
        - slope_score
        - noise_score
        - sunlight_score
        """
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        geo = result["geo_optimizer_v3_1"]
        
        assert "final_score" in geo, "Missing final_score"
        assert "weighted_total" in geo, "Missing weighted_total"
        assert "slope_score" in geo, "Missing slope_score"
        assert "noise_score" in geo, "Missing noise_score"
        assert "sunlight_score" in geo, "Missing sunlight_score"
        assert geo["version"] == "3.1", "Version should be 3.1"
        assert geo["final_score"] == 82.0, f"Expected 82.0, got {geo['final_score']}"
        assert len(geo["alternatives"]) == 2, "Should have 2 alternatives"
    
    def test_patch_5_api_failover_stats(self, mapper, sample_engine_output):
        """
        PATCH 5: API Failover and Rate Limit
        - last_provider_used
        - retry_count
        - failover_sequence
        - cache_stats.hit_rate
        """
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        api = result["api_performance"]
        
        assert "last_provider_used" in api, "Missing last_provider_used"
        assert "retry_count" in api, "Missing retry_count"
        assert "failover_sequence" in api, "Missing failover_sequence"
        assert "cache_stats" in api, "Missing cache_stats"
        assert "hit_rate" in api["cache_stats"], "Missing cache hit_rate"
    
    def test_patch_6_lh_notice_v2_1(self, mapper, sample_engine_output):
        """PATCH 6: LH Notice v2.1 structure"""
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        notice = result["lh_notice_v2_1"]
        
        assert "version" in notice, "Missing version"
        assert notice["version"] == "2.1", "Version should be 2.1"
        assert "has_recent_notice" in notice, "Missing has_recent_notice"
        assert "notice_count" in notice, "Missing notice_count"
    
    def test_patch_7_null_safe_gps_poi(self, mapper):
        """PATCH 7: Null-safe fallback for missing GPS/POI"""
        # Test with missing coordinates
        data_no_coords = {"summary": {"address": "Test"}}
        result = mapper.map_analysis_output_to_report(data_no_coords)
        
        assert result["coordinates"]["latitude"] == 0.0, "Should fallback to 0.0"
        assert result["coordinates"]["longitude"] == 0.0, "Should fallback to 0.0"
        
        # Test with string coordinates
        data_str_coords = {"coordinates": "latitude=37.5 longitude=126.9"}
        result2 = mapper.map_analysis_output_to_report(data_str_coords)
        
        assert result2["coordinates"]["latitude"] == 37.5, "Should parse string"
        assert result2["coordinates"]["longitude"] == 126.9, "Should parse string"
    
    def test_patch_8_zoning_v7_2_20_plus_fields(self, mapper, sample_engine_output):
        """PATCH 8: Zoning with 20+ v7.2 fields"""
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        zone = result["zone_info"]
        
        # Basic fields
        assert "land_use_zone" in zone, "Missing land_use_zone"
        assert "building_coverage_ratio" in zone, "Missing building_coverage_ratio"
        assert "floor_area_ratio" in zone, "Missing floor_area_ratio"
        assert "height_limit" in zone, "Missing height_limit"
        
        # NEW v7.2 fields
        assert "overlay_zones" in zone, "Missing overlay_zones"
        assert "district_unit_plan" in zone, "Missing district_unit_plan"
        assert "development_restrictions" in zone, "Missing development_restrictions"
        assert "environmental_restrictions" in zone, "Missing environmental_restrictions"
        assert "road_width" in zone, "Missing road_width"
        assert "water_supply" in zone, "Missing water_supply"
        assert "sewage_system" in zone, "Missing sewage_system"
        assert "electricity" in zone, "Missing electricity"
        assert "gas_supply" in zone, "Missing gas_supply"
        assert "urban_planning_area" in zone, "Missing urban_planning_area"
        assert "parking_requirements" in zone, "Missing parking_requirements"
        assert "green_space_ratio" in zone, "Missing green_space_ratio"
        
        # Count total fields
        assert len(zone) >= 20, f"Should have 20+ fields, got {len(zone)}"
    
    def test_patch_9_real_engine_no_mock(self, mapper, sample_engine_output):
        """PATCH 9: Real engine output (no mock data)"""
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        
        # Verify all data comes from input, not mocked
        assert result["basic_info"]["address"] == "월드컵북로 120", "Should use real address"
        assert result["lh_assessment"]["grade"] == "A", "Should use real grade"
        assert result["lh_assessment"]["total_score"] == 86.27, "Should use real score"
    
    def test_patch_10_risk_table_lh_2025(self, mapper, sample_engine_output):
        """PATCH 10: Risk Table (LH 2025 criteria)"""
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        risk = result["risk_analysis_2025"]
        
        assert "criteria_version" in risk, "Missing criteria_version"
        assert risk["criteria_version"] == "LH_2025", "Should use 2025 criteria"
        assert "risk_level" in risk, "Missing risk_level"
        assert "risk_score" in risk, "Missing risk_score"
        assert "risk_categories" in risk, "Missing risk_categories"
        
        # With 0 risks, should be low risk
        assert risk["risk_level"] == "저위험", "0 risks should be low"
        assert risk["risk_score"] >= 80.0, "Low risk should have high score"
    
    def test_patch_11_field_validation(self, mapper, sample_engine_output):
        """PATCH 11: Complete field validation"""
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        
        # Check all major sections exist
        required_sections = [
            "metadata",
            "basic_info",
            "coordinates",
            "zone_info",
            "poi_analysis_v3_1",
            "type_demand_v3_1",
            "multi_parcel_v3_0",
            "geo_optimizer_v3_1",
            "api_performance",
            "lh_notice_v2_1",
            "risk_analysis_2025",
            "lh_assessment",
            "development_info",
            "demand_analysis",
            "financial_data",
            "negotiation_strategy",
            "summary",
        ]
        
        for section in required_sections:
            assert section in result, f"Missing section: {section}"
    
    def test_metadata_patches_applied(self, mapper, sample_engine_output):
        """Verify metadata lists all applied patches"""
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        metadata = result["metadata"]
        
        expected_patches = [
            "POI_v3.1", "TypeDemand_v3.1", "MultiParcel_v3.0",
            "GeoOptimizer_v3.1", "APIFailover", "LHNotice_v2.1",
            "NullSafeGPS", "Zoning_v7.2", "RealEngineOnly",
            "RiskTable_2025", "FieldValidation"
        ]
        
        for patch in expected_patches:
            assert patch in metadata["patches_applied"], f"Missing patch: {patch}"
    
    def test_integration_full_mapping(self, mapper, sample_engine_output):
        """Integration test: Full engine output → report mapping"""
        result = mapper.map_analysis_output_to_report(sample_engine_output)
        
        # Verify no major errors
        assert result is not None, "Result should not be None"
        assert isinstance(result, dict), "Result should be dict"
        
        # Verify key values propagate correctly
        assert result["lh_assessment"]["grade"] == "A"
        assert result["basic_info"]["address"] == "월드컵북로 120"
        assert result["development_info"]["estimated_units"] == 44
        assert result["geo_optimizer_v3_1"]["final_score"] == 82.0
        
        print("\n✅ ALL 11 CRITICAL PATCHES VALIDATED")
        print(f"   Patches applied: {', '.join(result['metadata']['patches_applied'])}")
        print(f"   Report version: {result['metadata']['report_version']}")
        print(f"   Engine version: {result['metadata']['engine_version']}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
