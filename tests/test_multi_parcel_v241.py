"""
Tests for ZeroSite v24.1 Enhanced Multi-Parcel Optimization

Test Coverage:
- Pareto Front Visualization (2D/3D)
- Genetic Algorithm Optimization
- Synergy Heatmap Generation

Author: ZeroSite Test Team
Version: 24.1.0
Date: 2025-12-12
"""

import pytest
from app.engines.multi_parcel_optimizer_v241 import (
    MultiParcelOptimizerV241,
    check_matplotlib_available
)


class TestMultiParcelOptimizerV241:
    """Tests for MultiParcelOptimizerV241 initialization"""
    
    @pytest.fixture
    def optimizer(self):
        return MultiParcelOptimizerV241()
    
    def test_initialization(self, optimizer):
        """Test that optimizer initializes correctly"""
        assert optimizer.version == "24.1.0"
        assert optimizer.ga_population_size == 100
        assert optimizer.ga_generations == 50
    
    def test_ga_parameters(self, optimizer):
        """Test GA parameters"""
        assert optimizer.ga_crossover_rate == 0.8
        assert optimizer.ga_mutation_rate == 0.1


class TestGeneticAlgorithm:
    """Tests for Genetic Algorithm optimization"""
    
    @pytest.fixture
    def optimizer(self):
        return MultiParcelOptimizerV241()
    
    @pytest.fixture
    def sample_parcels(self):
        """Generate sample parcels for testing"""
        return [
            {
                'id': f'P{i+1}',
                'area_sqm': 300 + i * 50,
                'max_far': 200 + i * 10,
                'price_per_sqm': 3_000_000 + i * 100_000,
                'latitude': 37.5 + i * 0.001,
                'longitude': 127.0 + i * 0.001,
                'shape_regularity': 0.7 + i * 0.05
            }
            for i in range(10)
        ]
    
    def test_ga_with_small_dataset(self, optimizer, sample_parcels):
        """Test GA with 10 parcels"""
        result = optimizer.optimize_with_genetic_algorithm(
            sample_parcels,
            population_size=20,
            generations=10
        )
        
        assert result is not None
        assert 'algorithm' in result
        assert result['algorithm'] == 'genetic_algorithm'
        assert 'top_solutions' in result
        assert len(result['top_solutions']) > 0
    
    def test_ga_returns_top_10_solutions(self, optimizer, sample_parcels):
        """Test that GA returns up to 10 solutions"""
        result = optimizer.optimize_with_genetic_algorithm(
            sample_parcels,
            population_size=50,
            generations=20
        )
        
        assert len(result['top_solutions']) <= 10
    
    def test_ga_solution_structure(self, optimizer, sample_parcels):
        """Test GA solution structure"""
        result = optimizer.optimize_with_genetic_algorithm(
            sample_parcels,
            population_size=20,
            generations=5
        )
        
        solution = result['top_solutions'][0]
        assert 'parcel_ids' in solution
        assert 'parcel_count' in solution
        assert 'total_area' in solution
        assert 'fitness_score' in solution
    
    def test_ga_convergence_tracking(self, optimizer, sample_parcels):
        """Test that GA tracks convergence"""
        result = optimizer.optimize_with_genetic_algorithm(
            sample_parcels,
            population_size=20,
            generations=10
        )
        
        assert 'convergence' in result
        assert 'best_fitness_history' in result['convergence']
        assert len(result['convergence']['best_fitness_history']) > 0


class TestParetoVisualization:
    """Tests for Pareto Front visualization"""
    
    @pytest.fixture
    def optimizer(self):
        return MultiParcelOptimizerV241()
    
    @pytest.fixture
    def sample_combinations(self):
        """Generate sample combinations for visualization"""
        return [
            {
                'total_cost': 1_000_000_000 + i * 100_000_000,
                'combined_far': 180 + i * 5,
                'scores': {'synergy_score': 50 + i * 5},
                'is_pareto_optimal': i % 3 == 0
            }
            for i in range(20)
        ]
    
    @pytest.mark.skipif(not check_matplotlib_available(), reason="matplotlib not available")
    def test_visualize_pareto_2d(self, optimizer, sample_combinations):
        """Test 2D Pareto visualization"""
        result = optimizer.visualize_pareto_front(sample_combinations, mode='2d')
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0  # Base64 string should not be empty
    
    @pytest.mark.skipif(not check_matplotlib_available(), reason="matplotlib not available")
    def test_visualize_pareto_3d(self, optimizer, sample_combinations):
        """Test 3D Pareto visualization"""
        result = optimizer.visualize_pareto_front(sample_combinations, mode='3d')
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_visualize_without_matplotlib(self, optimizer, sample_combinations):
        """Test visualization gracefully handles missing matplotlib"""
        # This test will pass regardless of matplotlib availability
        result = optimizer.visualize_pareto_front(sample_combinations)
        assert isinstance(result, str)


class TestSynergyHeatmap:
    """Tests for Synergy Heatmap generation"""
    
    @pytest.fixture
    def optimizer(self):
        return MultiParcelOptimizerV241()
    
    @pytest.fixture
    def sample_parcels(self):
        """Generate sample parcels"""
        return [
            {
                'id': f'P{i+1}',
                'area_sqm': 500 + i * 100,
                'max_far': 200 + i * 10,
                'latitude': 37.5 + i * 0.0005,
                'longitude': 127.0 + i * 0.0005,
                'shape_regularity': 0.8
            }
            for i in range(5)
        ]
    
    @pytest.mark.skipif(not check_matplotlib_available(), reason="matplotlib not available")
    def test_generate_synergy_heatmap(self, optimizer, sample_parcels):
        """Test synergy heatmap generation"""
        result = optimizer.generate_synergy_heatmap(sample_parcels)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_calculate_pairwise_synergy(self, optimizer, sample_parcels):
        """Test pairwise synergy calculation"""
        synergy = optimizer._calculate_pairwise_synergy(
            sample_parcels[0],
            sample_parcels[1]
        )
        
        assert 0 <= synergy <= 100
    
    def test_synergy_symmetric(self, optimizer, sample_parcels):
        """Test that synergy is symmetric"""
        synergy_12 = optimizer._calculate_pairwise_synergy(
            sample_parcels[0],
            sample_parcels[1]
        )
        synergy_21 = optimizer._calculate_pairwise_synergy(
            sample_parcels[1],
            sample_parcels[0]
        )
        
        assert abs(synergy_12 - synergy_21) < 0.01


class TestGAHelperFunctions:
    """Tests for GA helper functions"""
    
    @pytest.fixture
    def optimizer(self):
        return MultiParcelOptimizerV241()
    
    @pytest.fixture
    def sample_parcels(self):
        return [
            {'area_sqm': 500, 'max_far': 200, 'price_per_sqm': 3_000_000}
            for _ in range(5)
        ]
    
    def test_ga_initialize_population(self, optimizer, sample_parcels):
        """Test population initialization"""
        population = optimizer._ga_initialize_population(
            sample_parcels,
            population_size=10,
            target_area_range=(500, 2000)
        )
        
        assert len(population) == 10
        assert all(len(chromosome) == 5 for chromosome in population)
        assert all(sum(chromosome) > 0 for chromosome in population)  # At least one selected
    
    def test_ga_evaluate_fitness(self, optimizer, sample_parcels):
        """Test fitness evaluation"""
        chromosome = [1, 1, 0, 0, 0]
        fitness = optimizer._ga_evaluate_fitness(
            chromosome,
            sample_parcels,
            target_area_range=(500, 2000)
        )
        
        assert fitness >= 0
        assert fitness <= 100
    
    def test_ga_crossover(self, optimizer):
        """Test crossover operation"""
        parent1 = [1, 1, 0, 0, 1]
        parent2 = [0, 1, 1, 1, 0]
        
        child1, child2 = optimizer._ga_crossover(parent1, parent2)
        
        assert len(child1) == len(parent1)
        assert len(child2) == len(parent2)
    
    def test_ga_mutate(self, optimizer):
        """Test mutation operation"""
        chromosome = [1, 1, 0, 0, 0]
        mutated = optimizer._ga_mutate(chromosome, len(chromosome))
        
        assert len(mutated) == len(chromosome)
        assert sum(mutated) > 0  # At least one selected
        
        # Check that mutation changed at least one gene (might not always happen)
        # So we just verify structure is maintained


class TestIntegration:
    """Integration tests"""
    
    @pytest.fixture
    def optimizer(self):
        return MultiParcelOptimizerV241()
    
    @pytest.fixture
    def complete_parcels(self):
        """Generate complete parcel dataset"""
        return [
            {
                'id': f'Parcel_{i+1}',
                'area_sqm': 400 + i * 80,
                'max_far': 190 + i * 15,
                'price_per_sqm': 2_800_000 + i * 150_000,
                'latitude': 37.55 + i * 0.002,
                'longitude': 127.02 + i * 0.002,
                'shape_regularity': 0.65 + i * 0.05,
                'zoning': '제2종일반주거'
            }
            for i in range(12)
        ]
    
    def test_full_optimization_workflow(self, optimizer, complete_parcels):
        """Test complete optimization workflow"""
        # Run GA optimization
        ga_result = optimizer.optimize_with_genetic_algorithm(
            complete_parcels,
            population_size=30,
            generations=15
        )
        
        assert ga_result is not None
        assert len(ga_result['top_solutions']) > 0
        
        # Verify solutions are valid
        for solution in ga_result['top_solutions']:
            assert solution['parcel_count'] > 0
            assert solution['total_area'] > 0
            assert solution['fitness_score'] >= 0
