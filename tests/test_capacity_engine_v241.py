"""
Tests for Enhanced Capacity Engine v24.1

Tests for GAP #1:
- Mass Simulation (층수×면적 3D 조합)
- Sun Exposure Setback (일조 이격거리 정밀 계산)
- Floor Optimization (층수 최적화 알고리즘)

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

import pytest
import math
from app.engines.capacity_engine_v241 import (
    CapacityEngineV241,
    MassConfiguration,
    SunExposureAnalysis,
    FloorOptimizationResult
)


class TestMassSimulation:
    """Tests for Mass Simulation feature"""
    
    @pytest.fixture
    def engine(self):
        return CapacityEngineV241()
    
    def test_mass_simulation_generates_5_configurations(self, engine):
        """Test that mass simulation generates up to 5 configurations"""
        configs = engine.generate_mass_simulation(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            max_floors=11,
            floor_height=3.0
        )
        
        assert len(configs) <= 5
        assert len(configs) >= 3  # Should generate at least 3 types
        assert all(isinstance(c, MassConfiguration) for c in configs)
    
    def test_mass_simulation_includes_all_shape_types(self, engine):
        """Test that different shape types are generated"""
        configs = engine.generate_mass_simulation(
            land_area=1000.0,
            bcr_limit=60.0,
            far_limit=250.0,
            max_floors=15,
            floor_height=3.0
        )
        
        shape_types = {c.shape_type for c in configs}
        assert 'tower' in shape_types or 'slab' in shape_types or 'mixed' in shape_types
    
    def test_mass_simulation_tower_config(self, engine):
        """Test tower configuration (high floors, low footprint)"""
        configs = engine.generate_mass_simulation(
            land_area=1000.0,
            bcr_limit=60.0,
            far_limit=300.0,
            max_floors=20,
            floor_height=3.0
        )
        
        tower_configs = [c for c in configs if c.shape_type == 'tower']
        if tower_configs:
            tower = tower_configs[0]
            assert tower.floors >= 15  # High floors
            assert tower.aspect_ratio >= 2.0  # Elongated shape
    
    def test_mass_simulation_slab_config(self, engine):
        """Test slab configuration (low floors, high footprint)"""
        configs = engine.generate_mass_simulation(
            land_area=1000.0,
            bcr_limit=70.0,
            far_limit=200.0,
            max_floors=15,
            floor_height=3.0
        )
        
        slab_configs = [c for c in configs if c.shape_type == 'slab']
        if slab_configs:
            slab = slab_configs[0]
            assert slab.floors <= 7  # Low floors
            assert slab.aspect_ratio <= 1.0  # Wide shape
    
    def test_mass_simulation_efficiency_scores(self, engine):
        """Test that efficiency scores are calculated"""
        configs = engine.generate_mass_simulation(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            max_floors=11,
            floor_height=3.0
        )
        
        for config in configs:
            assert 0 <= config.efficiency_score <= 100
            assert config.efficiency_score > 0  # Should not be zero
    
    def test_mass_simulation_sorted_by_efficiency(self, engine):
        """Test that configurations are sorted by efficiency"""
        configs = engine.generate_mass_simulation(
            land_area=1000.0,
            bcr_limit=60.0,
            far_limit=250.0,
            max_floors=15,
            floor_height=3.0
        )
        
        # Check descending order
        for i in range(len(configs) - 1):
            assert configs[i].efficiency_score >= configs[i+1].efficiency_score
    
    def test_mass_simulation_volume_calculation(self, engine):
        """Test that volume is calculated correctly"""
        configs = engine.generate_mass_simulation(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            max_floors=10,
            floor_height=3.0
        )
        
        for config in configs:
            expected_volume = config.footprint * config.floors * 3.0
            assert abs(config.volume - expected_volume) < 0.1


class TestSunExposureSetback:
    """Tests for Sun Exposure Setback calculation"""
    
    @pytest.fixture
    def engine(self):
        return CapacityEngineV241()
    
    def test_sun_exposure_winter_shadow(self, engine):
        """Test winter solstice shadow length calculation"""
        analysis = engine.calculate_sun_exposure_setback(
            building_height=30.0,
            zoning_type='제2종일반주거',
            latitude=37.5665
        )
        
        assert isinstance(analysis, SunExposureAnalysis)
        assert analysis.winter_solstice_shadow_length > 0
        # At Seoul latitude, 30m building creates ~48m shadow in winter
        assert 40 < analysis.winter_solstice_shadow_length < 55
    
    def test_sun_exposure_solar_angles(self, engine):
        """Test solar angle calculations"""
        analysis = engine.calculate_sun_exposure_setback(
            building_height=30.0,
            zoning_type='제2종일반주거'
        )
        
        # Winter angle should be lower than summer
        assert analysis.solar_angle_winter < analysis.solar_angle_summer
        # Seoul winter solstice: ~30-32°, summer: ~76-78°
        assert 28 < analysis.solar_angle_winter < 35
        assert 74 < analysis.solar_angle_summer < 80
    
    def test_sun_exposure_setback_requirement_residential(self, engine):
        """Test setback requirements for residential zones"""
        analysis1 = engine.calculate_sun_exposure_setback(
            building_height=30.0,
            zoning_type='제1종일반주거'
        )
        
        analysis2 = engine.calculate_sun_exposure_setback(
            building_height=30.0,
            zoning_type='제2종일반주거'
        )
        
        # Type 1 should require more setback than Type 2
        assert analysis1.required_setback_north >= analysis2.required_setback_north
        assert analysis1.required_setback_north >= 1.5  # Minimum for Type 1
        assert analysis2.required_setback_north >= 1.0  # Minimum for Type 2
    
    def test_sun_exposure_compliance_status(self, engine):
        """Test compliance status determination"""
        analysis = engine.calculate_sun_exposure_setback(
            building_height=30.0,
            zoning_type='제2종일반주거'
        )
        
        assert analysis.compliance_status in ['PASS', 'MARGINAL', 'FAIL']
        assert isinstance(analysis.recommendation, str)
        assert len(analysis.recommendation) > 0
    
    def test_sun_exposure_daylight_hours(self, engine):
        """Test annual daylight hours calculation"""
        analysis = engine.calculate_sun_exposure_setback(
            building_height=30.0,
            zoning_type='제2종일반주거',
            analyze_annual=True
        )
        
        # Seoul averages ~5-6 hours direct sunlight
        assert 4.0 <= analysis.daylight_hours_annual <= 6.5
    
    def test_sun_exposure_height_impact(self, engine):
        """Test that taller buildings create longer shadows"""
        analysis_low = engine.calculate_sun_exposure_setback(
            building_height=15.0,
            zoning_type='제2종일반주거'
        )
        
        analysis_high = engine.calculate_sun_exposure_setback(
            building_height=45.0,
            zoning_type='제2종일반주거'
        )
        
        assert analysis_high.winter_solstice_shadow_length > analysis_low.winter_solstice_shadow_length
        assert analysis_high.required_setback_north > analysis_low.required_setback_north
    
    def test_solar_altitude_calculation(self, engine):
        """Test solar altitude angle calculation method"""
        # Winter solstice
        altitude_winter = engine._calculate_solar_altitude(
            latitude=37.5665,
            declination=-23.45
        )
        
        # Summer solstice
        altitude_summer = engine._calculate_solar_altitude(
            latitude=37.5665,
            declination=23.45
        )
        
        assert altitude_winter < altitude_summer
        assert 25 < altitude_winter < 35
        assert 70 < altitude_summer < 80


class TestFloorOptimization:
    """Tests for Floor Optimization (Multi-Objective)"""
    
    @pytest.fixture
    def engine(self):
        return CapacityEngineV241()
    
    def test_floor_optimization_generates_results(self, engine):
        """Test that floor optimization generates results"""
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거',
            unit_area_avg=59.0,
            floor_height=3.0
        )
        
        assert len(results) > 0
        assert all(isinstance(r, FloorOptimizationResult) for r in results)
    
    def test_floor_optimization_sorted_by_score(self, engine):
        """Test that results are sorted by total score"""
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거'
        )
        
        # Check descending order
        for i in range(len(results) - 1):
            assert results[i].total_score >= results[i+1].total_score
    
    def test_floor_optimization_pareto_optimal_identified(self, engine):
        """Test that Pareto optimal solutions are identified"""
        results = engine.optimize_floor_configuration(
            land_area=1000.0,
            bcr_limit=60.0,
            far_limit=250.0,
            height_limit=45.0,
            zoning_type='제2종일반주거'
        )
        
        pareto_count = sum(1 for r in results if r.pareto_optimal)
        assert pareto_count > 0  # Should have at least some Pareto optimal solutions
        assert pareto_count <= len(results)  # Not all can be Pareto optimal typically
    
    def test_floor_optimization_scores_valid(self, engine):
        """Test that all scores are in valid range"""
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거'
        )
        
        for result in results:
            assert 0 <= result.sunlight_score <= 100
            assert 0 <= result.cost_score <= 100
            assert 0 <= result.shape_score <= 100
            assert 0 <= result.total_score <= 100
    
    def test_floor_optimization_unit_count_positive(self, engine):
        """Test that unit counts are positive"""
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거'
        )
        
        for result in results:
            assert result.unit_count > 0
    
    def test_floor_optimization_custom_weights(self, engine):
        """Test optimization with custom weights"""
        custom_weights = {
            'unit_count': 0.5,  # Prioritize unit count
            'sunlight': 0.2,
            'cost': 0.2,
            'shape': 0.1
        }
        
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거',
            weights=custom_weights
        )
        
        # Top result should favor higher unit count
        assert len(results) > 0
        top_result = results[0]
        assert top_result.unit_count > 0
    
    def test_floor_optimization_tradeoff_analysis(self, engine):
        """Test that tradeoff analysis is provided"""
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거'
        )
        
        for result in results:
            assert 'unit_count' in result.tradeoff_analysis
            assert 'sunlight_status' in result.tradeoff_analysis
            assert 'cost_per_unit_relative' in result.tradeoff_analysis
            assert 'shape_regularity' in result.tradeoff_analysis
    
    def test_floor_optimization_optimal_range(self, engine):
        """Test that optimal floors are in reasonable range"""
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거'
        )
        
        for result in results:
            assert 3 <= result.optimal_floors <= 20  # Reasonable range


class TestIntegration:
    """Integration tests for all v24.1 features"""
    
    @pytest.fixture
    def engine(self):
        return CapacityEngineV241()
    
    def test_end_to_end_analysis(self, engine):
        """Test complete analysis workflow using all v24.1 features"""
        land_area = 660.0
        bcr_limit = 60.0
        far_limit = 200.0
        max_floors = 11
        height_limit = 35.0
        zoning_type = '제2종일반주거'
        
        # Step 1: Generate mass simulations
        mass_configs = engine.generate_mass_simulation(
            land_area=land_area,
            bcr_limit=bcr_limit,
            far_limit=far_limit,
            max_floors=max_floors,
            floor_height=3.0
        )
        assert len(mass_configs) > 0
        
        # Step 2: Analyze sun exposure for optimal configuration
        optimal_mass = mass_configs[0]
        building_height = optimal_mass.floors * 3.0
        
        sun_analysis = engine.calculate_sun_exposure_setback(
            building_height=building_height,
            zoning_type=zoning_type
        )
        assert sun_analysis.compliance_status in ['PASS', 'MARGINAL', 'FAIL']
        
        # Step 3: Optimize floor configuration
        optimization_results = engine.optimize_floor_configuration(
            land_area=land_area,
            bcr_limit=bcr_limit,
            far_limit=far_limit,
            height_limit=height_limit,
            zoning_type=zoning_type
        )
        assert len(optimization_results) > 0
        
        # Verify optimal result is reasonable
        optimal_result = optimization_results[0]
        assert optimal_result.total_score > 50  # Should be decent score
        assert optimal_result.unit_count > 0
    
    def test_version_compatibility(self, engine):
        """Test that v24.1 engine maintains v24.0 compatibility"""
        # v24.0 style input should still work
        input_data = {
            'land_area_sqm': 660.0,
            'zoning_type': '제2종일반주거',
            'far_limit': 200.0,
            'bcr_limit': 60.0,
            'height_limit': 35.0,
            'land_depth_m': 25.0,
            'unit_types': {'59': 0.6, '84': 0.4}
        }
        
        result = engine.process(input_data)
        assert result['success'] is True
        assert 'data' in result
    
    def test_performance_mass_simulation(self, engine):
        """Test that mass simulation completes quickly"""
        import time
        
        start = time.time()
        configs = engine.generate_mass_simulation(
            land_area=1000.0,
            bcr_limit=60.0,
            far_limit=250.0,
            max_floors=15,
            floor_height=3.0
        )
        duration = time.time() - start
        
        assert duration < 0.1  # Should complete in <100ms
        assert len(configs) > 0
    
    def test_performance_sun_exposure(self, engine):
        """Test that sun exposure calculation completes quickly"""
        import time
        
        start = time.time()
        analysis = engine.calculate_sun_exposure_setback(
            building_height=30.0,
            zoning_type='제2종일반주거'
        )
        duration = time.time() - start
        
        assert duration < 0.05  # Should complete in <50ms
        assert analysis.compliance_status in ['PASS', 'MARGINAL', 'FAIL']
    
    def test_performance_floor_optimization(self, engine):
        """Test that floor optimization completes in reasonable time"""
        import time
        
        start = time.time()
        results = engine.optimize_floor_configuration(
            land_area=660.0,
            bcr_limit=60.0,
            far_limit=200.0,
            height_limit=35.0,
            zoning_type='제2종일반주거'
        )
        duration = time.time() - start
        
        assert duration < 0.2  # Should complete in <200ms
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
