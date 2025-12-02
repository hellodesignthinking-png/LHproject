"""
ZeroSite v7.2 Complete Integration Test
Tests all 11 patches with real engine output
"""

import pytest
import sys
from pathlib import Path
import asyncio
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.analysis_engine import AnalysisEngine
from app.services.report_engine_v7_2 import ReportEngineV72
from app.schemas import LandAnalysisRequest


class TestV72Integration:
    """Complete v7.2 integration test suite"""
    
    @pytest.mark.asyncio
    async def test_complete_v7_2_workflow(self):
        """
        Test complete workflow: Analysis → Report → Validation
        Address: 월드컵북로 120
        Type: 청년
        """
        print("\n" + "="*80)
        print("V7.2 COMPLETE INTEGRATION TEST")
        print("="*80)
        
        # Step 1: Run analysis
        print("\n[1/4] Running land analysis...")
        engine = AnalysisEngine()
        request = LandAnalysisRequest(
            address="월드컵북로 120",
            land_area=660.0,
            unit_type="청년"
        )
        
        engine_output = await engine.analyze_land(request)
        assert engine_output is not None, "Engine output should not be None"
        print(f"  ✓ Analysis complete")
        
        # Step 2: Generate v7.2 report
        print("\n[2/4] Generating v7.2 report...")
        report_engine = ReportEngineV72()
        
        result = report_engine.generate_report(
            engine_output=engine_output,
            report_type="comprehensive",
            format="markdown"
        )
        
        assert result['success'], "Report generation should succeed"
        assert 'report_data' in result, "Result should include report_data"
        print(f"  ✓ Report generated: {result['statistics']['total_lines']} lines")
        
        # Step 3: Validate all 11 patches
        print("\n[3/4] Validating all 11 patches...")
        report_data = result['report_data']
        
        # PATCH 1: POI v3.1
        assert 'poi_analysis_v3_1' in report_data, "Missing POI v3.1"
        poi = report_data['poi_analysis_v3_1']
        assert 'final_distance_m' in poi, "Missing final_distance_m"
        assert 'lh_grade' in poi, "Missing lh_grade"
        assert 'weight_applied_distance' in poi, "Missing weight_applied_distance"
        assert 'total_score_v3_1' in poi, "Missing total_score_v3_1"
        assert poi['version'] == "3.1", "POI version should be 3.1"
        print(f"  ✓ PATCH 1: POI v3.1 (grade={poi['lh_grade']}, score={poi['total_score_v3_1']})")
        
        # PATCH 2: Type Demand v3.1
        assert 'type_demand_v3_1' in report_data, "Missing Type Demand v3.1"
        td = report_data['type_demand_v3_1']
        assert 'type_scores' in td, "Missing type_scores"
        assert len(td['type_scores']) >= 5, "Should have 5+ housing types"
        for type_name, scores in td['type_scores'].items():
            assert 'raw_score' in scores, f"{type_name}: Missing raw_score"
            assert 'poi_bonus' in scores, f"{type_name}: Missing poi_bonus"
            assert 'final_score' in scores, f"{type_name}: Missing final_score"
        print(f"  ✓ PATCH 2: Type Demand v3.1 ({len(td['type_scores'])} types)")
        
        # PATCH 3: Multi-Parcel v3.0
        assert 'multi_parcel_v3_0' in report_data, "Missing Multi-Parcel v3.0"
        mp = report_data['multi_parcel_v3_0']
        assert 'compactness_ratio' in mp, "Missing compactness_ratio"
        assert 'shape_penalty' in mp, "Missing shape_penalty"
        assert mp['version'] == "3.0", "Multi-Parcel version should be 3.0"
        print(f"  ✓ PATCH 3: Multi-Parcel v3.0 (multi={mp['is_multi_parcel']})")
        
        # PATCH 4: GeoOptimizer v3.1
        assert 'geo_optimizer_v3_1' in report_data, "Missing GeoOptimizer v3.1"
        geo = report_data['geo_optimizer_v3_1']
        assert 'final_score' in geo, "Missing final_score"
        assert 'slope_score' in geo, "Missing slope_score"
        assert 'noise_score' in geo, "Missing noise_score"
        assert 'sunlight_score' in geo, "Missing sunlight_score"
        assert geo['version'] == "3.1", "GeoOptimizer version should be 3.1"
        print(f"  ✓ PATCH 4: GeoOptimizer v3.1 (score={geo['final_score']})")
        
        # PATCH 5: API Performance
        assert 'api_performance' in report_data, "Missing API Performance"
        api = report_data['api_performance']
        assert 'last_provider_used' in api, "Missing last_provider_used"
        assert 'retry_count' in api, "Missing retry_count"
        assert 'cache_stats' in api, "Missing cache_stats"
        print(f"  ✓ PATCH 5: API Performance (provider={api['last_provider_used']})")
        
        # PATCH 6: LH Notice v2.1
        assert 'lh_notice_v2_1' in report_data, "Missing LH Notice v2.1"
        notice = report_data['lh_notice_v2_1']
        assert notice['version'] == "2.1", "LH Notice version should be 2.1"
        print(f"  ✓ PATCH 6: LH Notice v2.1")
        
        # PATCH 7: Coordinates
        assert 'coordinates' in report_data, "Missing coordinates"
        coords = report_data['coordinates']
        assert 'latitude' in coords, "Missing latitude"
        assert 'longitude' in coords, "Missing longitude"
        assert coords['latitude'] != 0.0, "Latitude should not be 0.0"
        print(f"  ✓ PATCH 7: GPS ({coords['latitude']:.4f}, {coords['longitude']:.4f})")
        
        # PATCH 8: Zoning v7.2 (20+ fields)
        assert 'zone_info' in report_data, "Missing zone_info"
        zone = report_data['zone_info']
        assert len(zone) >= 20, f"Should have 20+ zone fields, got {len(zone)}"
        print(f"  ✓ PATCH 8: Zoning v7.2 ({len(zone)} fields)")
        
        # PATCH 9: Basic Info
        assert 'basic_info' in report_data, "Missing basic_info"
        basic = report_data['basic_info']
        assert basic['unit_type'] == "청년", "Unit type should match"
        print(f"  ✓ PATCH 9: Real Engine Data")
        
        # PATCH 10: Risk 2025
        assert 'risk_analysis_2025' in report_data, "Missing risk_analysis_2025"
        risk = report_data['risk_analysis_2025']
        assert risk['criteria_version'] == "LH_2025", "Should use LH_2025 criteria"
        print(f"  ✓ PATCH 10: Risk LH 2025 (level={risk['risk_level']})")
        
        # PATCH 11: Metadata
        assert 'metadata' in report_data, "Missing metadata"
        meta = report_data['metadata']
        assert 'patches_applied' in meta, "Missing patches_applied"
        assert len(meta['patches_applied']) == 11, "Should have 11 patches"
        print(f"  ✓ PATCH 11: Validation (11/11 patches)")
        
        # Step 4: Verify data correctness
        print("\n[4/4] Verifying data correctness...")
        
        # Check POI accuracy
        assert poi['lh_grade'] in ['A', 'B', 'C', 'D'], "Invalid LH grade"
        assert poi['total_score_v3_1'] > 0, "POI score should be > 0"
        print(f"  ✓ POI accuracy: grade={poi['lh_grade']}, score={poi['total_score_v3_1']}")
        
        # Check Type Demand differentiation
        scores = [s['final_score'] for s in td['type_scores'].values()]
        assert len(set(scores)) > 1, "Type scores should be different"
        print(f"  ✓ Type Demand differentiation: {len(set(scores))} unique scores")
        
        # Check GeoOptimizer
        assert geo['final_score'] > 0, "GeoOptimizer score should be > 0"
        assert len(geo['alternatives']) >= 0, "Should have alternatives list"
        print(f"  ✓ GeoOptimizer: score={geo['final_score']}, alt={len(geo['alternatives'])}")
        
        # Check Zoning population
        non_empty_zones = sum(1 for v in zone.values() if v not in [None, 0, 0.0, "", []])
        assert non_empty_zones >= 10, f"At least 10 zone fields should be populated, got {non_empty_zones}"
        print(f"  ✓ Zoning populated: {non_empty_zones}/{len(zone)} fields")
        
        print("\n" + "="*80)
        print("✅ V7.2 INTEGRATION TEST PASSED")
        print("="*80)
        
        return True
    
    @pytest.mark.asyncio
    async def test_null_safe_fallback(self):
        """Test null-safe fallback for missing data"""
        print("\n" + "="*80)
        print("NULL-SAFE FALLBACK TEST")
        print("="*80)
        
        # Create mapper directly
        from app.services.report_field_mapper_v7_2_complete import ReportFieldMapperV72Complete
        mapper = ReportFieldMapperV72Complete()
        
        # Test with minimal data
        minimal_data = {
            "summary": {
                "address": "Test Address",
                "land_area": 100.0
            }
        }
        
        result = mapper.map_analysis_output_to_report(minimal_data)
        
        # Should not crash and should have fallback values
        assert 'coordinates' in result
        assert result['coordinates']['latitude'] == 0.0
        assert result['coordinates']['longitude'] == 0.0
        print("  ✓ GPS fallback working")
        
        assert 'poi_analysis_v3_1' in result
        print("  ✓ POI fallback working")
        
        assert 'type_demand_v3_1' in result
        print("  ✓ Type Demand fallback working")
        
        assert 'multi_parcel_v3_0' in result
        print("  ✓ Multi-Parcel fallback working")
        
        print("\n✅ NULL-SAFE FALLBACK TEST PASSED")
        
        return True
    
    @pytest.mark.asyncio
    async def test_multi_format_generation(self):
        """Test report generation in all formats"""
        print("\n" + "="*80)
        print("MULTI-FORMAT GENERATION TEST")
        print("="*80)
        
        engine = AnalysisEngine()
        request = LandAnalysisRequest(
            address="월드컵북로 120",
            land_area=660.0,
            unit_type="청년"
        )
        
        engine_output = await engine.analyze_land(request)
        report_engine = ReportEngineV72()
        
        # Test Markdown
        md_result = report_engine.generate_report(
            engine_output=engine_output,
            report_type="comprehensive",
            format="markdown"
        )
        assert md_result['success']
        assert md_result['format'] == "markdown"
        print("  ✓ Markdown format: OK")
        
        # Test JSON
        json_result = report_engine.generate_report(
            engine_output=engine_output,
            report_type="comprehensive",
            format="json"
        )
        assert json_result['success']
        assert json_result['format'] == "json"
        # Verify JSON is valid
        json.loads(json_result['content'])
        print("  ✓ JSON format: OK")
        
        print("\n✅ MULTI-FORMAT TEST PASSED")
        
        return True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
