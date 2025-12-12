"""
Test Suite for Multi-Parcel Optimizer v24.1
Tests combination search, Pareto optimal, synergy calculation
"""

import pytest
from app.engines.multi_parcel_optimizer import (
    MultiParcelOptimizer,
    ParcelData,
    ParcelCombination,
    CombinationScore
)


class TestMultiParcelOptimizer:
    """Multi-Parcel Optimizer Test Suite"""
    
    def setup_method(self):
        """Setup before each test"""
        self.optimizer = MultiParcelOptimizer()
        
        # Test parcels
        self.test_parcels = [
            {
                'id': 'P001', 
                'area_sqm': 400, 
                'max_far': 200, 
                'price_per_sqm': 10000000,
                'latitude': 37.5000, 
                'longitude': 127.0000,
                'shape_regularity': 0.8,
                'accessibility': 0.9,
                'development_difficulty': 0.2
            },
            {
                'id': 'P002', 
                'area_sqm': 600, 
                'max_far': 220, 
                'price_per_sqm': 10500000,
                'latitude': 37.5002, 
                'longitude': 127.0002,
                'shape_regularity': 0.7,
                'accessibility': 0.85,
                'development_difficulty': 0.3
            },
            {
                'id': 'P003', 
                'area_sqm': 800, 
                'max_far': 200, 
                'price_per_sqm': 9800000,
                'latitude': 37.5004, 
                'longitude': 127.0004,
                'shape_regularity': 0.9,
                'accessibility': 0.8,
                'development_difficulty': 0.25
            },
            {
                'id': 'P004', 
                'area_sqm': 500, 
                'max_far': 250, 
                'price_per_sqm': 11000000,
                'latitude': 37.5006, 
                'longitude': 127.0006,
                'shape_regularity': 0.6,
                'accessibility': 0.75,
                'development_difficulty': 0.4
            },
            {
                'id': 'P005', 
                'area_sqm': 700, 
                'max_far': 230, 
                'price_per_sqm': 10200000,
                'latitude': 37.5008, 
                'longitude': 127.0008,
                'shape_regularity': 0.75,
                'accessibility': 0.88,
                'development_difficulty': 0.28
            }
        ]
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        assert self.optimizer.min_parcels == 1
        assert self.optimizer.max_parcels == 5
        assert self.optimizer.target_area_min == 500
        assert self.optimizer.target_area_max == 3000
        assert self.optimizer.max_distance_km == 0.5
    
    def test_convert_parcels(self):
        """Test parcel data conversion"""
        converted = self.optimizer._convert_parcels(self.test_parcels)
        
        assert len(converted) == 5
        assert all(isinstance(p, ParcelData) for p in converted)
        assert converted[0].id == 'P001'
        assert converted[0].area_sqm == 400
        assert converted[0].max_far == 200
    
    def test_generate_combinations(self):
        """Test combination generation"""
        parcel_objects = self.optimizer._convert_parcels(self.test_parcels)
        
        combinations = self.optimizer._generate_combinations(
            parcel_objects,
            target_area_range=(1000, 2000),
            max_combinations=100
        )
        
        assert len(combinations) > 0
        assert all(isinstance(c, ParcelCombination) for c in combinations)
        
        # Check area constraints
        for combo in combinations:
            assert 1000 <= combo.total_area <= 2000
    
    def test_distance_constraint(self):
        """Test distance constraint check"""
        parcel_objects = self.optimizer._convert_parcels(self.test_parcels)
        
        # Close parcels (should pass)
        close_parcels = (parcel_objects[0], parcel_objects[1])
        assert self.optimizer._check_distance_constraint(close_parcels) == True
        
        # All 5 parcels (should still pass given test coordinates)
        all_parcels = tuple(parcel_objects)
        result = self.optimizer._check_distance_constraint(all_parcels)
        assert isinstance(result, bool)
    
    def test_calculate_distance(self):
        """Test Haversine distance calculation"""
        # Seoul City Hall to Gangnam Station (~9km)
        distance = self.optimizer._calculate_distance(
            37.5665, 126.9780,  # City Hall
            37.4979, 127.0276   # Gangnam
        )
        
        assert 8.0 < distance < 10.0  # Approximate distance
    
    def test_evaluate_combination(self):
        """Test combination evaluation"""
        parcel_objects = self.optimizer._convert_parcels(self.test_parcels)
        
        # Create 2-parcel combination
        combo = ParcelCombination(
            id="P001_P002",
            parcels=[parcel_objects[0], parcel_objects[1]]
        )
        
        evaluated = self.optimizer._evaluate_combination(combo)
        
        assert evaluated.scores is not None
        assert isinstance(evaluated.scores, CombinationScore)
        assert 0 <= evaluated.scores.total_score <= 100
        assert 0 <= evaluated.scores.area_score <= 100
        assert 0 <= evaluated.scores.far_score <= 100
        assert 0 <= evaluated.scores.cost_score <= 100
        assert 0 <= evaluated.scores.shape_score <= 100
        assert 0 <= evaluated.scores.synergy_score <= 100
        
        # Check calculated properties
        assert evaluated.total_area == 1000  # 400 + 600
        assert evaluated.combined_far > evaluated.avg_far  # FAR bonus applied
        assert evaluated.total_cost > 0
        
        # Check advantages/disadvantages
        assert isinstance(evaluated.advantages, list)
        assert isinstance(evaluated.disadvantages, list)
        assert len(evaluated.recommendation) > 0
    
    def test_rank_combinations(self):
        """Test combination ranking"""
        parcel_objects = self.optimizer._convert_parcels(self.test_parcels)
        
        combinations = self.optimizer._generate_combinations(
            parcel_objects,
            target_area_range=(1000, 2000),
            max_combinations=20
        )
        
        evaluated = [self.optimizer._evaluate_combination(c) for c in combinations]
        ranked = self.optimizer._rank_combinations(evaluated)
        
        assert len(ranked) == len(evaluated)
        assert ranked[0].rank == 1
        assert ranked[-1].rank == len(ranked)
        
        # Check descending order
        for i in range(len(ranked) - 1):
            assert ranked[i].scores.total_score >= ranked[i+1].scores.total_score
    
    def test_pareto_dominance(self):
        """Test Pareto dominance check"""
        parcel_objects = self.optimizer._convert_parcels(self.test_parcels)
        
        # Create two combinations
        combo_a = ParcelCombination(
            id="A",
            parcels=[parcel_objects[0], parcel_objects[1]]
        )
        combo_b = ParcelCombination(
            id="B",
            parcels=[parcel_objects[0], parcel_objects[2]]
        )
        
        combo_a = self.optimizer._evaluate_combination(combo_a)
        combo_b = self.optimizer._evaluate_combination(combo_b)
        
        # Check dominance
        result = self.optimizer._dominates(combo_a, combo_b)
        assert isinstance(result, bool)
    
    def test_find_pareto_optimal(self):
        """Test Pareto optimal set identification"""
        parcel_objects = self.optimizer._convert_parcels(self.test_parcels)
        
        combinations = self.optimizer._generate_combinations(
            parcel_objects,
            target_area_range=(1000, 2000),
            max_combinations=20
        )
        
        evaluated = [self.optimizer._evaluate_combination(c) for c in combinations]
        pareto_optimal = self.optimizer._find_pareto_optimal(evaluated)
        
        assert len(pareto_optimal) > 0
        assert len(pareto_optimal) <= len(evaluated)
        assert all(c.is_pareto_optimal for c in pareto_optimal)
    
    def test_full_optimization(self):
        """Test full optimization workflow"""
        result = self.optimizer.optimize(
            parcels=self.test_parcels,
            target_area_range=(1000, 2000),
            max_combinations=50
        )
        
        # Check result structure
        assert result['success'] == True
        assert result['total_parcels'] == 5
        assert result['total_combinations_evaluated'] > 0
        
        assert 'top_10_combinations' in result
        assert 'pareto_optimal_set' in result
        assert 'best_combination' in result
        assert 'recommendation' in result
        assert 'optimization_summary' in result
        
        # Check best combination
        best = result['best_combination']
        assert best is not None
        assert best['rank'] == 1
        assert best['parcel_count'] >= 1
        assert best['total_area_sqm'] > 0
        assert 0 <= best['scores']['total'] <= 100
        
        # Check Pareto optimal
        pareto = result['pareto_optimal_set']
        assert len(pareto) > 0
        assert all(c['is_pareto_optimal'] for c in pareto)
        
        # Check summary
        summary = result['optimization_summary']
        assert summary['total_evaluated'] > 0
        assert summary['pareto_optimal_count'] == len(pareto)
        assert 0 <= summary['pareto_optimal_ratio'] <= 100
        assert summary['best_score'] >= summary['average_score']
    
    def test_synergy_calculation(self):
        """Test synergy score calculation"""
        parcel_objects = self.optimizer._convert_parcels(self.test_parcels)
        
        # 3-parcel combination (should have high synergy)
        combo_3 = ParcelCombination(
            id="P001_P002_P003",
            parcels=[parcel_objects[0], parcel_objects[1], parcel_objects[2]]
        )
        
        evaluated_3 = self.optimizer._evaluate_combination(combo_3)
        
        # Check synergy factors
        assert evaluated_3.scores.synergy_score > 0
        assert evaluated_3.combined_far == evaluated_3.avg_far + 20.0  # 3+ parcels: +20%
        
        # Compare with 1-parcel
        combo_1 = ParcelCombination(
            id="P001",
            parcels=[parcel_objects[0]]
        )
        
        evaluated_1 = self.optimizer._evaluate_combination(combo_1)
        
        # 3-parcel should have higher synergy
        assert evaluated_3.scores.synergy_score > evaluated_1.scores.synergy_score
    
    def test_cost_score_calculation(self):
        """Test cost score calculation"""
        # Low-cost parcel
        low_cost = [{
            'id': 'LOW',
            'area_sqm': 1000,
            'max_far': 200,
            'price_per_sqm': 8000000,  # Low price
            'latitude': 37.5,
            'longitude': 127.0
        }]
        
        # High-cost parcel
        high_cost = [{
            'id': 'HIGH',
            'area_sqm': 1000,
            'max_far': 200,
            'price_per_sqm': 20000000,  # High price
            'latitude': 37.5,
            'longitude': 127.0
        }]
        
        result_low = self.optimizer.optimize(low_cost, (800, 1200), 10)
        result_high = self.optimizer.optimize(high_cost, (800, 1200), 10)
        
        # Low-cost should have better cost score
        low_cost_score = result_low['best_combination']['scores']['cost']
        high_cost_score = result_high['best_combination']['scores']['cost']
        
        assert low_cost_score > high_cost_score
    
    def test_area_score_calculation(self):
        """Test area score calculation"""
        # Optimal area (1000-2000㎡)
        optimal = [{
            'id': 'OPT',
            'area_sqm': 1500,  # Optimal
            'max_far': 200,
            'price_per_sqm': 10000000
        }]
        
        # Too small area
        too_small = [{
            'id': 'SMALL',
            'area_sqm': 300,  # Too small
            'max_far': 200,
            'price_per_sqm': 10000000
        }]
        
        result_opt = self.optimizer.optimize(optimal, (1400, 1600), 10)
        result_small = self.optimizer.optimize(too_small, (250, 350), 10)
        
        # Optimal should have perfect area score
        opt_area_score = result_opt['best_combination']['scores']['area']
        small_area_score = result_small['best_combination']['scores']['area']
        
        assert opt_area_score >= 95  # Near perfect
        assert opt_area_score > small_area_score
    
    def test_recommendation_generation(self):
        """Test recommendation message generation"""
        result = self.optimizer.optimize(
            parcels=self.test_parcels,
            target_area_range=(1000, 2000),
            max_combinations=30
        )
        
        recommendation = result['recommendation']
        
        # Check content
        assert '최적 조합 추천' in recommendation
        assert '종합 점수' in recommendation
        assert '조합 특성' in recommendation
        assert '강점' in recommendation or '약점' in recommendation
        assert '✅' in recommendation or '⭐' in recommendation or '⚠️' in recommendation
    
    def test_empty_parcels(self):
        """Test with empty parcel list"""
        result = self.optimizer.optimize(
            parcels=[],
            target_area_range=(1000, 2000),
            max_combinations=10
        )
        
        assert result['success'] == True
        assert result['total_parcels'] == 0
        assert result['total_combinations_evaluated'] == 0
    
    def test_single_parcel(self):
        """Test with single parcel"""
        single = [self.test_parcels[0]]
        
        result = self.optimizer.optimize(
            parcels=single,
            target_area_range=(300, 500),
            max_combinations=10
        )
        
        assert result['success'] == True
        assert result['total_parcels'] == 1
        assert result['best_combination']['parcel_count'] == 1
    
    def test_large_target_area(self):
        """Test with large target area requiring multiple parcels"""
        result = self.optimizer.optimize(
            parcels=self.test_parcels,
            target_area_range=(2500, 3000),  # Requires 4-5 parcels
            max_combinations=50
        )
        
        assert result['success'] == True
        
        if result['total_combinations_evaluated'] > 0:
            best = result['best_combination']
            assert best['total_area_sqm'] >= 2500
            assert best['parcel_count'] >= 4


class TestCombinationScore:
    """Test CombinationScore dataclass"""
    
    def test_default_initialization(self):
        """Test default score initialization"""
        score = CombinationScore()
        
        assert score.area_score == 0.0
        assert score.far_score == 0.0
        assert score.cost_score == 0.0
        assert score.shape_score == 0.0
        assert score.synergy_score == 0.0
        assert score.total_score == 0.0
        
        # Check weights
        assert sum(score.weights.values()) == pytest.approx(1.0, abs=0.01)
    
    def test_custom_scores(self):
        """Test custom score values"""
        score = CombinationScore(
            area_score=85.0,
            far_score=90.0,
            cost_score=75.0,
            shape_score=80.0,
            synergy_score=88.0
        )
        
        assert score.area_score == 85.0
        assert score.far_score == 90.0


class TestParcelData:
    """Test ParcelData dataclass"""
    
    def test_parcel_initialization(self):
        """Test parcel data initialization"""
        parcel = ParcelData(
            id='TEST001',
            area_sqm=1000,
            max_far=200,
            price_per_sqm=10000000
        )
        
        assert parcel.id == 'TEST001'
        assert parcel.area_sqm == 1000
        assert parcel.max_far == 200
        assert parcel.price_per_sqm == 10000000
        
        # Check defaults
        assert parcel.zoning == "general_residential"
        assert parcel.shape_regularity == 0.7
        assert parcel.accessibility == 0.8
        assert parcel.development_difficulty == 0.3


class TestPerformance:
    """Performance tests"""
    
    def test_optimization_speed(self):
        """Test optimization completes within reasonable time"""
        import time
        
        optimizer = MultiParcelOptimizer()
        
        parcels = [
            {'id': f'P{i:03d}', 'area_sqm': 500 + i*50, 'max_far': 200 + i*10, 
             'price_per_sqm': 10000000, 'latitude': 37.5 + i*0.001, 
             'longitude': 127.0 + i*0.001}
            for i in range(10)
        ]
        
        start = time.time()
        result = optimizer.optimize(
            parcels=parcels,
            target_area_range=(1000, 3000),
            max_combinations=100
        )
        elapsed = time.time() - start
        
        assert result['success'] == True
        assert elapsed < 5.0  # Should complete in < 5 seconds
    
    def test_memory_efficiency(self):
        """Test memory efficiency with many parcels"""
        optimizer = MultiParcelOptimizer()
        
        # 20 parcels
        parcels = [
            {'id': f'P{i:03d}', 'area_sqm': 400 + i*20, 'max_far': 200, 
             'price_per_sqm': 10000000}
            for i in range(20)
        ]
        
        result = optimizer.optimize(
            parcels=parcels,
            target_area_range=(1500, 2500),
            max_combinations=100  # Limit combinations
        )
        
        assert result['success'] == True
        assert result['total_combinations_evaluated'] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
