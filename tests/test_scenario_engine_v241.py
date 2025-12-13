"""
Tests for Enhanced Scenario Engine v24.1

Tests for GAP #2:
- Scenario C (고령자형) implementation
- 3-way comparison (A/B/C)
- 18 metrics calculation
- Carbon Footprint
- Social Value Score
- Market Competitiveness

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

import pytest
from app.engines.scenario_engine_v241 import (
    ScenarioEngineV241,
    ScenarioMetrics,
    ScenarioComparison
)


class TestScenarioTypes:
    """Tests for scenario type definitions"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    def test_scenario_types_defined(self, engine):
        """Test that all 3 scenario types are defined"""
        assert 'A' in engine.SCENARIO_TYPES
        assert 'B' in engine.SCENARIO_TYPES
        assert 'C' in engine.SCENARIO_TYPES  # NEW
    
    def test_scenario_c_properties(self, engine):
        """Test Scenario C (고령자형) properties"""
        scenario_c = engine.SCENARIO_TYPES['C']
        
        assert scenario_c['name'] == '고령자형'
        assert scenario_c['target'] == '고령자·장애인'
        assert scenario_c['unit_size_range'] == (36, 59)
        assert '무장애' in scenario_c['description']


class TestThreeWayComparison:
    """Tests for 3-way comparison (A vs B vs C)"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    @pytest.fixture
    def sample_scenarios(self):
        """Sample scenario data for testing"""
        base_data = {
            'land_area_sqm': 660.0,
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'land_price_per_sqm': 3_000_000,
            'transit_distance_m': 400,
            'green_space_ratio': 0.25,
            'parking_ratio': 0.8,
            'sunlight_compliant': True
        }
        
        scenario_a = {**base_data, 'unit_area_avg': 36.0, 'revenue_per_unit': 200_000_000}
        scenario_b = {**base_data, 'unit_area_avg': 59.0, 'revenue_per_unit': 280_000_000}
        scenario_c = {**base_data, 'unit_area_avg': 46.0, 'revenue_per_unit': 240_000_000}
        
        return scenario_a, scenario_b, scenario_c
    
    def test_compare_abc_returns_comparison_object(self, engine, sample_scenarios):
        """Test that 3-way comparison returns ScenarioComparison object"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        assert isinstance(result, ScenarioComparison)
        assert isinstance(result.scenario_a, ScenarioMetrics)
        assert isinstance(result.scenario_b, ScenarioMetrics)
        assert isinstance(result.scenario_c, ScenarioMetrics)
    
    def test_rankings_has_three_scenarios(self, engine, sample_scenarios):
        """Test that rankings include all 3 scenarios"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        assert len(result.rankings) == 3
        assert 'A' in result.rankings
        assert 'B' in result.rankings
        assert 'C' in result.rankings
    
    def test_rankings_are_valid(self, engine, sample_scenarios):
        """Test that rankings are 1, 2, 3"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        ranks = sorted(result.rankings.values())
        assert ranks == [1, 2, 3]
    
    def test_best_scenario_matches_first_rank(self, engine, sample_scenarios):
        """Test that best scenario has rank 1"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        assert result.rankings[result.best_scenario] == 1


class TestEighteenMetrics:
    """Tests for 18 metrics calculation"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    @pytest.fixture
    def sample_data(self):
        return {
            'land_area_sqm': 660.0,
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'unit_area_avg': 45.0,
            'land_price_per_sqm': 3_000_000,
            'revenue_per_unit': 250_000_000,
            'transit_distance_m': 400,
            'green_space_ratio': 0.25,
            'parking_ratio': 0.8,
            'sunlight_compliant': True,
            'far_limit': 250.0
        }
    
    def test_original_15_metrics_calculated(self, engine, sample_data):
        """Test that original 15 metrics are calculated"""
        metrics = engine._calculate_scenario_metrics(sample_data, 'B')
        
        # Original 15 metrics
        assert metrics.total_units > 0
        assert metrics.residential_area > 0
        assert metrics.construction_cost > 0
        assert metrics.land_acquisition_cost > 0
        assert metrics.total_investment > 0
        assert metrics.total_revenue > 0
        assert isinstance(metrics.profit, (int, float))
        assert isinstance(metrics.roi, float)
        assert isinstance(metrics.irr, float)
        assert metrics.payback_period > 0
        assert metrics.parking_spaces > 0
        assert metrics.far > 0
        assert metrics.bcr > 0
        assert metrics.building_height > 0
        assert 0 <= metrics.compliance_score <= 100
    
    def test_new_3_metrics_calculated(self, engine, sample_data):
        """Test that NEW 3 metrics are calculated"""
        metrics = engine._calculate_scenario_metrics(sample_data, 'B')
        
        # NEW metrics
        assert metrics.carbon_footprint > 0  # tCO2e
        assert 0 <= metrics.social_value_score <= 100
        assert 0 <= metrics.market_competitiveness <= 100
    
    def test_carbon_footprint_positive(self, engine, sample_data):
        """Test that carbon footprint is positive"""
        metrics = engine._calculate_scenario_metrics(sample_data, 'B')
        
        assert metrics.carbon_footprint > 0
        # Should be realistic (660㎡ land, 3960㎡ total floor area ~5000-6000 tCO2e)
        assert 1000 < metrics.carbon_footprint < 8000


class TestCarbonFootprint:
    """Tests for Carbon Footprint calculation"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    def test_carbon_footprint_calculation(self, engine):
        """Test carbon footprint formula"""
        # 1000㎡ building
        # Construction: 500 tCO2e (0.5/㎡)
        # Operation 30y: 900 tCO2e (0.03/㎡/y × 30y)
        # Total: ~1400 tCO2e
        
        carbon = engine._calculate_carbon_footprint(1000.0, 'B')
        
        assert 1200 < carbon < 1600  # Allow some tolerance
    
    def test_scenario_c_has_lower_carbon(self, engine):
        """Test that Scenario C (elderly) has lower carbon footprint"""
        carbon_a = engine._calculate_carbon_footprint(1000.0, 'A')
        carbon_b = engine._calculate_carbon_footprint(1000.0, 'B')
        carbon_c = engine._calculate_carbon_footprint(1000.0, 'C')
        
        # C should be lowest due to -10% adjustment
        assert carbon_c < carbon_b
        # A should be lower than B due to -5% adjustment
        assert carbon_a < carbon_b


class TestSocialValueScore:
    """Tests for Social Value Score calculation"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    def test_social_value_score_range(self, engine):
        """Test that social value score is 0-100"""
        sample_data = {
            'green_space_ratio': 0.25,
            'transit_distance_m': 400
        }
        
        score = engine._calculate_social_value_score('B', 50, sample_data)
        
        assert 0 <= score <= 100
    
    def test_scenario_c_has_higher_social_value(self, engine):
        """Test that Scenario C (elderly) has higher social value"""
        sample_data = {
            'green_space_ratio': 0.25,
            'transit_distance_m': 400
        }
        
        score_a = engine._calculate_social_value_score('A', 50, sample_data)
        score_b = engine._calculate_social_value_score('B', 50, sample_data)
        score_c = engine._calculate_social_value_score('C', 50, sample_data)
        
        # C should have highest due to welfare facilities bonus
        assert score_c >= score_a
        assert score_c >= score_b
    
    def test_more_units_increases_social_value(self, engine):
        """Test that more units increases social value"""
        sample_data = {
            'green_space_ratio': 0.25,
            'transit_distance_m': 400
        }
        
        score_30 = engine._calculate_social_value_score('B', 30, sample_data)
        score_100 = engine._calculate_social_value_score('B', 100, sample_data)
        
        assert score_100 > score_30


class TestMarketCompetitiveness:
    """Tests for Market Competitiveness calculation"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    def test_market_competitiveness_range(self, engine):
        """Test that market competitiveness is 0-100"""
        sample_data = {
            'transit_distance_m': 400,
            'revenue_per_unit': 250_000_000
        }
        
        score = engine._calculate_market_competitiveness('B', 59.0, 660.0, sample_data)
        
        assert 0 <= score <= 100
    
    def test_optimal_unit_size_increases_competitiveness(self, engine):
        """Test that optimal unit size increases competitiveness"""
        sample_data = {
            'transit_distance_m': 400,
            'revenue_per_unit': 250_000_000
        }
        
        # Scenario B optimal: 46-85㎡
        score_optimal = engine._calculate_market_competitiveness('B', 59.0, 660.0, sample_data)
        score_suboptimal = engine._calculate_market_competitiveness('B', 30.0, 660.0, sample_data)
        
        assert score_optimal > score_suboptimal
    
    def test_lower_price_increases_competitiveness(self, engine):
        """Test that lower price increases competitiveness"""
        data_expensive = {
            'transit_distance_m': 400,
            'revenue_per_unit': 300_000_000  # Expensive
        }
        
        data_affordable = {
            'transit_distance_m': 400,
            'revenue_per_unit': 200_000_000  # Affordable
        }
        
        score_expensive = engine._calculate_market_competitiveness('B', 59.0, 660.0, data_expensive)
        score_affordable = engine._calculate_market_competitiveness('B', 59.0, 660.0, data_affordable)
        
        assert score_affordable > score_expensive


class TestComparisonMatrix:
    """Tests for comparison matrix generation"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    @pytest.fixture
    def sample_scenarios(self):
        base_data = {
            'land_area_sqm': 660.0,
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'land_price_per_sqm': 3_000_000,
            'unit_area_avg': 45.0,
            'revenue_per_unit': 250_000_000,
            'transit_distance_m': 400,
            'green_space_ratio': 0.25,
            'parking_ratio': 0.8,
            'sunlight_compliant': True
        }
        
        return base_data, base_data, base_data
    
    def test_comparison_matrix_has_all_metrics(self, engine, sample_scenarios):
        """Test that comparison matrix includes all 18 metrics"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        # Should have 18 metric entries
        assert len(result.comparison_matrix) == 18
        
        # Check presence of NEW metrics
        assert 'carbon_footprint' in result.comparison_matrix
        assert 'social_value_score' in result.comparison_matrix
        assert 'market_competitiveness' in result.comparison_matrix
    
    def test_comparison_matrix_structure(self, engine, sample_scenarios):
        """Test comparison matrix structure"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        # Each metric should have A, B, C, best, best_value
        for metric, values in result.comparison_matrix.items():
            assert 'A' in values
            assert 'B' in values
            assert 'C' in values
            assert 'best' in values
            assert 'best_value' in values
            assert values['best'] in ['A', 'B', 'C']


class TestRecommendation:
    """Tests for recommendation generation"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    @pytest.fixture
    def sample_scenarios(self):
        base_data = {
            'land_area_sqm': 660.0,
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'land_price_per_sqm': 3_000_000,
            'unit_area_avg': 45.0,
            'revenue_per_unit': 250_000_000,
            'transit_distance_m': 400,
            'green_space_ratio': 0.25,
            'parking_ratio': 0.8,
            'sunlight_compliant': True
        }
        
        return base_data, base_data, base_data
    
    def test_recommendation_is_string(self, engine, sample_scenarios):
        """Test that recommendation is a non-empty string"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        assert isinstance(result.recommendation, str)
        assert len(result.recommendation) > 0
    
    def test_recommendation_includes_best_scenario(self, engine, sample_scenarios):
        """Test that recommendation mentions best scenario"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        scenario_names = {
            'A': '청년형',
            'B': '일반형',
            'C': '고령자형'
        }
        
        best_name = scenario_names[result.best_scenario]
        assert best_name in result.recommendation


class TestTradeoffAnalysis:
    """Tests for tradeoff analysis"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    @pytest.fixture
    def sample_scenarios(self):
        base_data = {
            'land_area_sqm': 660.0,
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'land_price_per_sqm': 3_000_000,
            'unit_area_avg': 45.0,
            'revenue_per_unit': 250_000_000,
            'transit_distance_m': 400,
            'green_space_ratio': 0.25,
            'parking_ratio': 0.8,
            'sunlight_compliant': True
        }
        
        return base_data, base_data, base_data
    
    def test_tradeoff_analysis_structure(self, engine, sample_scenarios):
        """Test tradeoff analysis structure"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        assert 'roi_comparison' in result.tradeoff_analysis
        assert 'social_value_comparison' in result.tradeoff_analysis
        assert 'carbon_comparison' in result.tradeoff_analysis
    
    def test_tradeoff_analysis_has_all_scenarios(self, engine, sample_scenarios):
        """Test that tradeoff analysis includes A, B, C"""
        result = engine.compare_abc_scenarios(*sample_scenarios)
        
        roi_comp = result.tradeoff_analysis['roi_comparison']
        assert 'A' in roi_comp
        assert 'B' in roi_comp
        assert 'C' in roi_comp


class TestIntegration:
    """Integration tests for complete workflow"""
    
    @pytest.fixture
    def engine(self):
        return ScenarioEngineV241()
    
    def test_end_to_end_workflow(self, engine):
        """Test complete 3-way comparison workflow"""
        # Define realistic scenarios
        scenario_a = {
            'land_area_sqm': 660.0,
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'unit_area_avg': 36.0,
            'land_price_per_sqm': 3_000_000,
            'revenue_per_unit': 200_000_000,
            'transit_distance_m': 300,
            'green_space_ratio': 0.25,
            'parking_ratio': 0.8,
            'sunlight_compliant': True
        }
        
        scenario_b = {
            'land_area_sqm': 660.0,
            'far': 220.0,
            'bcr': 60.0,
            'floors': 11,
            'unit_area_avg': 59.0,
            'land_price_per_sqm': 3_000_000,
            'revenue_per_unit': 280_000_000,
            'transit_distance_m': 450,
            'green_space_ratio': 0.22,
            'parking_ratio': 1.0,
            'sunlight_compliant': True
        }
        
        scenario_c = {
            'land_area_sqm': 660.0,
            'far': 210.0,
            'bcr': 60.0,
            'floors': 10,
            'unit_area_avg': 46.0,
            'land_price_per_sqm': 3_000_000,
            'revenue_per_unit': 240_000_000,
            'transit_distance_m': 300,
            'green_space_ratio': 0.30,
            'parking_ratio': 0.7,
            'sunlight_compliant': True
        }
        
        # Perform comparison
        result = engine.compare_abc_scenarios(scenario_a, scenario_b, scenario_c)
        
        # Verify complete result
        assert isinstance(result, ScenarioComparison)
        assert len(result.rankings) == 3
        assert result.best_scenario in ['A', 'B', 'C']
        assert len(result.comparison_matrix) == 18
        assert len(result.recommendation) > 0
    
    def test_performance(self, engine):
        """Test that 3-way comparison completes quickly"""
        import time
        
        base_data = {
            'land_area_sqm': 660.0,
            'far': 200.0,
            'bcr': 60.0,
            'floors': 10,
            'land_price_per_sqm': 3_000_000,
            'unit_area_avg': 45.0,
            'revenue_per_unit': 250_000_000,
            'transit_distance_m': 400,
            'green_space_ratio': 0.25,
            'parking_ratio': 0.8,
            'sunlight_compliant': True
        }
        
        start = time.time()
        result = engine.compare_abc_scenarios(base_data, base_data, base_data)
        duration = time.time() - start
        
        assert duration < 0.1  # Should complete in <100ms
        assert isinstance(result, ScenarioComparison)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
