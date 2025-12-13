"""
ZeroSite v24.1 - Integration Tests
Tests for Phase 1 + Phase 1.5 features

Author: ZeroSite Development Team
Version: v24.1.0
Created: 2025-12-12
"""

import pytest
from datetime import datetime
from app.engines.capacity_engine_v241 import CapacityEngineV241
from app.engines.scenario_engine_v241 import ScenarioEngineV241
from app.engines.multi_parcel_optimizer_v241 import MultiParcelOptimizerV241
from app.engines.market_engine_v241 import MarketEngineV241
from app.engines.risk_engine_v241 import RiskEngineV241
from app.engines.alias_engine_v241 import AliasEngineV241
from app.engines.narrative_engine_v241 import NarrativeEngineV241
from app.services.report_generator_v241 import ReportGeneratorV241
from app.visualization.waterfall_chart_v241 import generate_financial_waterfall
from app.visualization.mass_sketch_v241 import MassSketchGenerator


class TestPhase1Integration:
    """Integration tests for Phase 1 (7 core engines)"""
    
    @pytest.fixture
    def sample_project_data(self):
        """Sample project data for testing"""
        return {
            "address": "서울시 강남구 테헤란로 1",
            "land_area": 1000.0,
            "zone_type": "제2종일반주거지역",
            "far_legal": 200.0,
            "bcr_legal": 60.0,
            "height_limit": 35.0,
            "unit_count": 50,
            "avg_unit_size": 85.0,
            "construction_cost_per_sqm": 3000000,
            "land_price_per_sqm": 5000000,
            "sale_price_per_sqm": 12000000
        }
    
    def test_capacity_to_scenario_workflow(self, sample_project_data):
        """Test workflow from Capacity Engine to Scenario Engine"""
        # Step 1: Run capacity analysis
        capacity_engine = CapacityEngineV241()
        capacity_result = capacity_engine.analyze_capacity(
            land_area=sample_project_data["land_area"],
            far_legal=sample_project_data["far_legal"],
            bcr_legal=sample_project_data["bcr_legal"],
            height_limit=sample_project_data["height_limit"]
        )
        
        assert capacity_result is not None
        assert "total_gfa" in capacity_result
        
        # Step 2: Use capacity results in scenario analysis
        scenario_engine = ScenarioEngineV241()
        scenario_a = scenario_engine.analyze_scenario_a(
            gfa=capacity_result["total_gfa"],
            unit_count=sample_project_data["unit_count"],
            avg_unit_size=sample_project_data["avg_unit_size"]
        )
        
        assert scenario_a is not None
        assert scenario_a["scenario_type"] == "A"
        assert "financial_metrics" in scenario_a
    
    def test_scenario_to_report_workflow(self, sample_project_data):
        """Test workflow from Scenario Engine to Report Generator"""
        # Step 1: Generate scenario analysis
        scenario_engine = ScenarioEngineV241()
        comparison = scenario_engine.compare_scenarios_abc(
            land_area=sample_project_data["land_area"],
            far_legal=sample_project_data["far_legal"],
            construction_cost=sample_project_data["construction_cost_per_sqm"],
            sale_price=sample_project_data["sale_price_per_sqm"]
        )
        
        assert comparison is not None
        assert "scenario_a" in comparison
        assert "scenario_b" in comparison
        assert "scenario_c" in comparison
        
        # Step 2: Generate report from scenarios
        report_gen = ReportGeneratorV241()
        report = report_gen.generate_comprehensive_report(
            project_data=sample_project_data,
            scenario_comparison=comparison,
            include_advanced=True
        )
        
        assert report is not None
        assert len(report.sections) > 0
        assert report.metadata.version == "24.1.0"
    
    def test_market_to_risk_workflow(self, sample_project_data):
        """Test workflow from Market Engine to Risk Engine"""
        # Step 1: Market analysis
        market_engine = MarketEngineV241()
        market_analysis = market_engine.analyze_market(
            address=sample_project_data["address"],
            price_history=[5000000, 5200000, 5100000, 5300000, 5250000]
        )
        
        assert market_analysis is not None
        assert "volatility" in market_analysis
        assert "risk_score" in market_analysis
        
        # Step 2: Use market data in risk assessment
        risk_engine = RiskEngineV241()
        risk_profile = risk_engine.generate_comprehensive_profile(
            project_data=sample_project_data,
            market_volatility=market_analysis["volatility"],
            price_trend=market_analysis.get("trend", 0.0)
        )
        
        assert risk_profile is not None
        assert "overall_risk_level" in risk_profile
        assert "design_risk" in risk_profile
        assert "legal_risk" in risk_profile


class TestPhase15Integration:
    """Integration tests for Phase 1.5 features"""
    
    @pytest.fixture
    def sample_financial_data(self):
        """Sample financial data for testing"""
        return {
            "land_cost": 5000,  # 억원
            "construction_cost": 3000,
            "financing_cost": 500,
            "sales_revenue": 10000,
            "operating_expense": 400,
            "net_profit": 1100
        }
    
    def test_alias_engine_integration(self):
        """Test Alias Engine with various data types"""
        alias_engine = AliasEngineV241()
        
        # Test currency formatting
        value_1 = alias_engine.format_value(500000000, "currency")
        assert "억" in value_1 or "만" in value_1
        
        # Test area conversion
        value_2 = alias_engine.convert_unit(1000, "sqm_to_pyeong")
        assert value_2 > 0
        assert value_2 != 1000  # Should be converted
        
        # Test alias lookup
        alias = alias_engine.get("total_gfa")
        assert alias is not None
    
    def test_narrative_engine_integration(self, sample_financial_data):
        """Test Narrative Engine generation"""
        narrative_engine = NarrativeEngineV241()
        
        # Test financial narrative
        narrative = narrative_engine.generate_financial_narrative(
            sample_financial_data
        )
        
        assert narrative is not None
        assert narrative.title is not None
        assert len(narrative.content) > 100  # Should be substantial
        assert len(narrative.key_points) > 0
    
    def test_waterfall_chart_generation(self, sample_financial_data):
        """Test Financial Waterfall Chart generation"""
        # Generate waterfall chart
        chart_base64 = generate_financial_waterfall(
            land_cost=sample_financial_data["land_cost"],
            construction_cost=sample_financial_data["construction_cost"],
            financing_cost=sample_financial_data["financing_cost"],
            sales_revenue=sample_financial_data["sales_revenue"],
            operating_expense=sample_financial_data["operating_expense"],
            net_profit=sample_financial_data["net_profit"]
        )
        
        assert chart_base64 is not None
        assert len(chart_base64) > 1000  # Base64 PNG should be substantial
        assert chart_base64.startswith("data:image/png;base64,")
    
    def test_mass_sketch_generation(self):
        """Test Mass Sketch 2D/3D generation"""
        sketch_gen = MassSketchGenerator()
        
        # Test 2D plan generation
        plan_base64 = sketch_gen.generate_2d_plan(
            length=50.0,
            width=30.0,
            height=35.0,
            floors=10,
            setback=3.0
        )
        
        assert plan_base64 is not None
        assert len(plan_base64) > 1000
        assert plan_base64.startswith("data:image/png;base64,")
        
        # Test isometric 3D generation
        iso_base64 = sketch_gen.generate_isometric_3d(
            length=50.0,
            width=30.0,
            height=35.0,
            floors=10
        )
        
        assert iso_base64 is not None
        assert len(iso_base64) > 1000
    
    def test_multi_parcel_integration(self):
        """Test Multi-Parcel Optimizer integration"""
        optimizer = MultiParcelOptimizerV241()
        
        # Create sample parcels
        parcels = [
            {
                "id": f"P{i:03d}",
                "area_sqm": 500.0 + i * 50,
                "price_per_sqm": 3000000,
                "max_far": 200.0,
                "shape_regularity": 0.8,
                "road_access": 1 if i % 2 == 0 else 0
            }
            for i in range(5)
        ]
        
        # Run optimization
        result = optimizer.optimize_genetic_algorithm(
            parcels=parcels,
            target_area_min=1000.0,
            population_size=20,
            generations=10
        )
        
        assert result is not None
        assert "best_combinations" in result
        assert len(result["best_combinations"]) > 0


class TestEndToEndWorkflow:
    """End-to-end integration tests"""
    
    def test_complete_project_analysis_workflow(self):
        """Test complete workflow from data input to report generation"""
        
        # Project data
        project_data = {
            "address": "서울시 강남구 테헤란로 1",
            "land_area": 1000.0,
            "zone_type": "제2종일반주거지역",
            "far_legal": 200.0,
            "bcr_legal": 60.0,
            "height_limit": 35.0,
            "land_price_per_sqm": 5000000,
            "construction_cost_per_sqm": 3000000,
            "sale_price_per_sqm": 12000000
        }
        
        # Step 1: Capacity Analysis
        capacity_engine = CapacityEngineV241()
        capacity = capacity_engine.analyze_capacity(
            land_area=project_data["land_area"],
            far_legal=project_data["far_legal"],
            bcr_legal=project_data["bcr_legal"],
            height_limit=project_data["height_limit"]
        )
        
        # Step 2: Scenario Comparison
        scenario_engine = ScenarioEngineV241()
        scenarios = scenario_engine.compare_scenarios_abc(
            land_area=project_data["land_area"],
            far_legal=project_data["far_legal"],
            construction_cost=project_data["construction_cost_per_sqm"],
            sale_price=project_data["sale_price_per_sqm"]
        )
        
        # Step 3: Market Analysis
        market_engine = MarketEngineV241()
        market = market_engine.analyze_market(
            address=project_data["address"],
            price_history=[5000000, 5200000, 5100000, 5300000, 5250000]
        )
        
        # Step 4: Risk Assessment
        risk_engine = RiskEngineV241()
        risk = risk_engine.generate_comprehensive_profile(
            project_data=project_data,
            market_volatility=market["volatility"],
            price_trend=market.get("trend", 0.0)
        )
        
        # Step 5: Generate Narratives
        narrative_engine = NarrativeEngineV241()
        financial_narrative = narrative_engine.generate_financial_narrative(
            {
                "land_cost": project_data["land_area"] * project_data["land_price_per_sqm"] / 100000000,
                "construction_cost": capacity["total_gfa"] * project_data["construction_cost_per_sqm"] / 100000000,
                "sales_revenue": capacity["total_gfa"] * project_data["sale_price_per_sqm"] / 100000000
            }
        )
        
        # Step 6: Generate Visualizations
        sketch_gen = MassSketchGenerator()
        mass_sketch = sketch_gen.generate_2d_plan(
            length=50.0,
            width=project_data["land_area"] / 50.0,
            height=project_data["height_limit"],
            floors=int(capacity["total_gfa"] / (project_data["land_area"] * project_data["bcr_legal"] / 100))
        )
        
        # Step 7: Generate Final Report
        report_gen = ReportGeneratorV241()
        report = report_gen.generate_comprehensive_report(
            project_data=project_data,
            scenario_comparison=scenarios,
            include_advanced=True
        )
        
        # Assertions
        assert capacity is not None
        assert scenarios is not None
        assert market is not None
        assert risk is not None
        assert financial_narrative is not None
        assert mass_sketch is not None
        assert report is not None
        
        # Verify report completeness
        assert len(report.sections) >= 5
        assert report.metadata.version == "24.1.0"
        assert report.total_pages >= 20
    
    def test_alias_formatting_in_report(self):
        """Test that Alias Engine properly formats values in reports"""
        
        alias_engine = AliasEngineV241()
        narrative_engine = NarrativeEngineV241()
        
        # Create financial data with large numbers
        financial_data = {
            "land_cost": 500000000000,  # 5천억원
            "construction_cost": 300000000000,  # 3천억원
            "sales_revenue": 1000000000000  # 1조원
        }
        
        # Format using alias engine
        formatted_land = alias_engine.format_value(
            financial_data["land_cost"],
            "currency"
        )
        
        # Generate narrative
        narrative = narrative_engine.generate_financial_narrative(
            {
                "land_cost": financial_data["land_cost"] / 100000000,
                "construction_cost": financial_data["construction_cost"] / 100000000,
                "sales_revenue": financial_data["sales_revenue"] / 100000000
            }
        )
        
        # Verify formatting
        assert formatted_land is not None
        assert "억" in formatted_land or "조" in formatted_land
        
        # Verify narrative uses proper formatting
        assert narrative.content is not None
        assert len(narrative.content) > 0


class TestPerformanceIntegration:
    """Performance integration tests"""
    
    def test_full_analysis_performance(self):
        """Test that complete analysis completes within acceptable time"""
        import time
        
        start_time = time.time()
        
        # Run complete analysis
        project_data = {
            "land_area": 1000.0,
            "far_legal": 200.0,
            "bcr_legal": 60.0,
            "height_limit": 35.0
        }
        
        # Capacity
        capacity_engine = CapacityEngineV241()
        capacity = capacity_engine.analyze_capacity(
            land_area=project_data["land_area"],
            far_legal=project_data["far_legal"],
            bcr_legal=project_data["bcr_legal"],
            height_limit=project_data["height_limit"]
        )
        
        # Scenario
        scenario_engine = ScenarioEngineV241()
        scenarios = scenario_engine.compare_scenarios_abc(
            land_area=project_data["land_area"],
            far_legal=project_data["far_legal"],
            construction_cost=3000000,
            sale_price=12000000
        )
        
        # Market
        market_engine = MarketEngineV241()
        market = market_engine.analyze_market(
            address="서울시 강남구",
            price_history=[5000000] * 12
        )
        
        # Risk
        risk_engine = RiskEngineV241()
        risk = risk_engine.generate_comprehensive_profile(
            project_data=project_data,
            market_volatility=market["volatility"],
            price_trend=0.0
        )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete in under 5 seconds
        assert elapsed < 5.0, f"Full analysis took {elapsed:.2f}s (target: <5s)"
    
    def test_visualization_generation_performance(self):
        """Test visualization generation performance"""
        import time
        
        sketch_gen = MassSketchGenerator()
        
        start_time = time.time()
        
        # Generate multiple visualizations
        plan = sketch_gen.generate_2d_plan(50, 30, 35, 10)
        iso = sketch_gen.generate_isometric_3d(50, 30, 35, 10)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete in under 3 seconds
        assert elapsed < 3.0, f"Visualization generation took {elapsed:.2f}s (target: <3s)"


class TestErrorHandling:
    """Integration tests for error handling"""
    
    def test_invalid_data_handling(self):
        """Test that engines handle invalid data gracefully"""
        
        capacity_engine = CapacityEngineV241()
        
        # Test with negative values
        with pytest.raises(ValueError):
            capacity_engine.analyze_capacity(
                land_area=-1000.0,  # Invalid
                far_legal=200.0,
                bcr_legal=60.0,
                height_limit=35.0
            )
    
    def test_missing_data_handling(self):
        """Test handling of missing required data"""
        
        scenario_engine = ScenarioEngineV241()
        
        # Test with missing data
        with pytest.raises((ValueError, TypeError)):
            scenario_engine.analyze_scenario_a(
                gfa=None,  # Missing
                unit_count=50,
                avg_unit_size=85
            )


class TestBackwardCompatibility:
    """Tests for backward compatibility with v24.0"""
    
    def test_v240_data_format_support(self):
        """Test that v24.1 engines support v24.0 data formats"""
        
        # v24.0 format data
        v240_data = {
            "land_area": 1000.0,
            "far": 200.0,  # Old key name
            "bcr": 60.0,   # Old key name
            "height": 35.0  # Old key name
        }
        
        # Should work with v24.1 engines (with mapping)
        capacity_engine = CapacityEngineV241()
        
        # Map old keys to new keys
        mapped_data = {
            "land_area": v240_data["land_area"],
            "far_legal": v240_data["far"],
            "bcr_legal": v240_data["bcr"],
            "height_limit": v240_data["height"]
        }
        
        result = capacity_engine.analyze_capacity(**mapped_data)
        
        assert result is not None
        assert "total_gfa" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
