"""
ZeroSite v24.1 - Enhanced Multi-Parcel Optimization Engine

NEW FEATURES (v24.1 GAP #4):
- Pareto Front 2D/3D visualization (matplotlib)
- Genetic Algorithm for large-scale optimization (20+ parcels)
- Synergy effect heatmap matrix

Priority: 🟡 MEDIUM (v24.1 GAP Closing)
Specification: docs/ZEROSITE_V24.1_GAP_CLOSING_PLAN.md

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, List, Tuple, Optional, Any
import logging
import base64
import io
import random
import numpy as np

# Import base optimizer
from .multi_parcel_optimizer import (
    MultiParcelOptimizer,
    ParcelData,
    ParcelCombination,
    CombinationScore
)

logger = logging.getLogger(__name__)

# Try to import visualization libraries
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("matplotlib not available - visualization features disabled")


class MultiParcelOptimizerV241(MultiParcelOptimizer):
    """
    Enhanced Multi-Parcel Optimizer for ZeroSite v24.1
    
    NEW FEATURES:
    1. Pareto Front Visualization (2D/3D scatter plots)
    2. Genetic Algorithm for 20+ parcels
    3. Synergy Effect Heatmap
    """
    
    def __init__(self):
        """Initialize Enhanced Multi-Parcel Optimizer v24.1"""
        super().__init__()
        self.version = "24.1.0"
        logger.info("Enhanced Multi-Parcel Optimizer v24.1.0 initialized (GAP #4)")
        
        # GA parameters
        self.ga_population_size = 100
        self.ga_generations = 50
        self.ga_crossover_rate = 0.8
        self.ga_mutation_rate = 0.1
    
    # ========================================================================
    # NEW FEATURE #1: PARETO FRONT VISUALIZATION
    # ========================================================================
    
    def visualize_pareto_front(
        self,
        combinations: List[Dict],
        mode: str = '2d'
    ) -> str:
        """
        Generate Pareto Front visualization
        
        Args:
            combinations: List of evaluated combinations
            mode: '2d' or '3d' visualization
            
        Returns:
            Base64-encoded PNG image
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available - returning empty visualization")
            return ""
        
        logger.info(f"Generating Pareto Front visualization ({mode} mode)")
        
        # Extract data
        costs = [c.get('total_cost', 0) / 1e9 for c in combinations]  # Billions
        fars = [c.get('combined_far', 0) for c in combinations]
        synergies = [c.get('scores', {}).get('synergy_score', 0) for c in combinations]
        is_pareto = [c.get('is_pareto_optimal', False) for c in combinations]
        
        if mode == '2d':
            return self._visualize_pareto_2d(costs, fars, is_pareto)
        else:
            return self._visualize_pareto_3d(costs, fars, synergies, is_pareto)
    
    def _visualize_pareto_2d(
        self,
        costs: List[float],
        fars: List[float],
        is_pareto: List[bool]
    ) -> str:
        """Generate 2D Pareto Front scatter plot"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot non-Pareto points
        non_pareto_costs = [c for c, p in zip(costs, is_pareto) if not p]
        non_pareto_fars = [f for f, p in zip(fars, is_pareto) if not p]
        ax.scatter(non_pareto_costs, non_pareto_fars, 
                  alpha=0.5, s=50, c='gray', label='Other Solutions')
        
        # Plot Pareto optimal points
        pareto_costs = [c for c, p in zip(costs, is_pareto) if p]
        pareto_fars = [f for f, p in zip(fars, is_pareto) if p]
        ax.scatter(pareto_costs, pareto_fars, 
                  alpha=0.8, s=100, c='red', marker='*', label='Pareto Optimal')
        
        # Connect Pareto front
        if len(pareto_costs) > 1:
            sorted_pairs = sorted(zip(pareto_costs, pareto_fars))
            sorted_costs, sorted_fars = zip(*sorted_pairs)
            ax.plot(sorted_costs, sorted_fars, 'r--', alpha=0.5, linewidth=2)
        
        ax.set_xlabel('Total Cost (₩B)', fontsize=12)
        ax.set_ylabel('Combined FAR (%)', fontsize=12)
        ax.set_title('Multi-Parcel Optimization: Pareto Front (Cost vs FAR)', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def _visualize_pareto_3d(
        self,
        costs: List[float],
        fars: List[float],
        synergies: List[float],
        is_pareto: List[bool]
    ) -> str:
        """Generate 3D Pareto Front scatter plot"""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot non-Pareto points
        non_pareto_idx = [i for i, p in enumerate(is_pareto) if not p]
        if non_pareto_idx:
            ax.scatter(
                [costs[i] for i in non_pareto_idx],
                [fars[i] for i in non_pareto_idx],
                [synergies[i] for i in non_pareto_idx],
                alpha=0.4, s=30, c='gray', label='Other Solutions'
            )
        
        # Plot Pareto optimal points
        pareto_idx = [i for i, p in enumerate(is_pareto) if p]
        if pareto_idx:
            ax.scatter(
                [costs[i] for i in pareto_idx],
                [fars[i] for i in pareto_idx],
                [synergies[i] for i in pareto_idx],
                alpha=0.9, s=150, c='red', marker='*', label='Pareto Optimal'
            )
        
        ax.set_xlabel('Total Cost (₩B)', fontsize=10)
        ax.set_ylabel('Combined FAR (%)', fontsize=10)
        ax.set_zlabel('Synergy Score', fontsize=10)
        ax.set_title('3D Pareto Front: Cost vs FAR vs Synergy', 
                    fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    # ========================================================================
    # NEW FEATURE #2: GENETIC ALGORITHM OPTIMIZATION
    # ========================================================================
    
    def optimize_with_genetic_algorithm(
        self,
        parcels: List[Dict],
        population_size: int = 100,
        generations: int = 50,
        target_area_range: Tuple[float, float] = (500, 2000)
    ) -> Dict:
        """
        Genetic Algorithm for large-scale parcel optimization (20+ parcels)
        
        Designed for scenarios where combinatorial explosion makes
        exhaustive search infeasible.
        
        GA Parameters:
        - Population: 100 chromosomes (parcel combinations)
        - Crossover rate: 0.8 (80% of offspring via crossover)
        - Mutation rate: 0.1 (10% genes mutated)
        - Selection: Tournament selection (size=3)
        - Termination: 50 generations or convergence
        
        Args:
            parcels: List of parcels to optimize
            population_size: GA population size
            generations: Number of generations
            target_area_range: Desired total area range
            
        Returns:
            Dict with top 10 solutions and optimization metrics
        """
        logger.info(f"Starting GA optimization with {len(parcels)} parcels")
        
        if len(parcels) < 2:
            logger.warning("Need at least 2 parcels for GA optimization")
            return {'error': 'Insufficient parcels', 'solutions': []}
        
        # Initialize population
        population = self._ga_initialize_population(
            parcels, population_size, target_area_range
        )
        
        best_fitness_history = []
        avg_fitness_history = []
        
        # Evolutionary loop
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = [
                self._ga_evaluate_fitness(chromosome, parcels, target_area_range)
                for chromosome in population
            ]
            
            # Track statistics
            best_fitness = max(fitness_scores)
            avg_fitness = sum(fitness_scores) / len(fitness_scores)
            best_fitness_history.append(best_fitness)
            avg_fitness_history.append(avg_fitness)
            
            if generation % 10 == 0:
                logger.info(
                    f"Generation {generation}/{generations}: "
                    f"Best={best_fitness:.2f}, Avg={avg_fitness:.2f}"
                )
            
            # Check convergence (no improvement in last 10 generations)
            if generation > 10 and len(set(best_fitness_history[-10:])) == 1:
                logger.info(f"Converged at generation {generation}")
                break
            
            # Selection
            selected = self._ga_tournament_selection(
                population, fitness_scores, population_size
            )
            
            # Crossover & Mutation
            offspring = []
            for i in range(0, len(selected), 2):
                parent1 = selected[i]
                parent2 = selected[i+1] if i+1 < len(selected) else selected[0]
                
                if random.random() < self.ga_crossover_rate:
                    child1, child2 = self._ga_crossover(parent1, parent2)
                else:
                    child1, child2 = parent1[:], parent2[:]
                
                if random.random() < self.ga_mutation_rate:
                    child1 = self._ga_mutate(child1, len(parcels))
                if random.random() < self.ga_mutation_rate:
                    child2 = self._ga_mutate(child2, len(parcels))
                
                offspring.extend([child1, child2])
            
            population = offspring[:population_size]
        
        # Extract top 10 solutions
        final_fitness = [
            self._ga_evaluate_fitness(chromosome, parcels, target_area_range)
            for chromosome in population
        ]
        
        sorted_solutions = sorted(
            zip(population, final_fitness),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Convert to readable format
        top_solutions = []
        for chromosome, fitness in sorted_solutions:
            selected_parcels = [
                parcels[i] for i, gene in enumerate(chromosome) if gene == 1
            ]
            
            solution = {
                'parcel_ids': [p.get('id', i) for i, p in enumerate(selected_parcels)],
                'parcel_count': len(selected_parcels),
                'total_area': sum(p.get('area_sqm', 0) for p in selected_parcels),
                'fitness_score': round(fitness, 2),
                'estimated_far': sum(p.get('max_far', 200) for p in selected_parcels) / len(selected_parcels) if selected_parcels else 0,
                'estimated_cost': sum(
                    p.get('area_sqm', 0) * p.get('price_per_sqm', 3_000_000)
                    for p in selected_parcels
                )
            }
            top_solutions.append(solution)
        
        return {
            'algorithm': 'genetic_algorithm',
            'version': '24.1.0',
            'parameters': {
                'population_size': population_size,
                'generations': generations,
                'crossover_rate': self.ga_crossover_rate,
                'mutation_rate': self.ga_mutation_rate
            },
            'convergence': {
                'generations_run': len(best_fitness_history),
                'best_fitness_history': best_fitness_history,
                'avg_fitness_history': avg_fitness_history
            },
            'top_solutions': top_solutions,
            'solution_count': len(top_solutions)
        }
    
    def _ga_initialize_population(
        self,
        parcels: List[Dict],
        population_size: int,
        target_area_range: Tuple[float, float]
    ) -> List[List[int]]:
        """Initialize GA population with random valid chromosomes"""
        population = []
        min_area, max_area = target_area_range
        
        for _ in range(population_size):
            # Random binary chromosome (1=selected, 0=not selected)
            chromosome = [random.randint(0, 1) for _ in range(len(parcels))]
            
            # Ensure at least one parcel selected
            if sum(chromosome) == 0:
                chromosome[random.randint(0, len(parcels)-1)] = 1
            
            # Check area constraint (repair if needed)
            total_area = sum(
                parcels[i].get('area_sqm', 0)
                for i, gene in enumerate(chromosome) if gene == 1
            )
            
            # If too large, remove parcels
            while total_area > max_area and sum(chromosome) > 1:
                selected_idx = [i for i, g in enumerate(chromosome) if g == 1]
                if selected_idx:
                    chromosome[random.choice(selected_idx)] = 0
                    total_area = sum(
                        parcels[i].get('area_sqm', 0)
                        for i, gene in enumerate(chromosome) if gene == 1
                    )
            
            population.append(chromosome)
        
        return population
    
    def _ga_evaluate_fitness(
        self,
        chromosome: List[int],
        parcels: List[Dict],
        target_area_range: Tuple[float, float]
    ) -> float:
        """Evaluate fitness of a chromosome (parcel combination)"""
        selected_indices = [i for i, gene in enumerate(chromosome) if gene == 1]
        
        if not selected_indices:
            return 0.0
        
        selected_parcels = [parcels[i] for i in selected_indices]
        
        # Calculate metrics
        total_area = sum(p.get('area_sqm', 0) for p in selected_parcels)
        avg_far = sum(p.get('max_far', 200) for p in selected_parcels) / len(selected_parcels)
        total_cost = sum(
            p.get('area_sqm', 0) * p.get('price_per_sqm', 3_000_000)
            for p in selected_parcels
        )
        
        # Fitness components
        min_area, max_area = target_area_range
        
        # 1. Area fitness (prefer within range)
        if min_area <= total_area <= max_area:
            area_fitness = 100
        elif total_area < min_area:
            area_fitness = (total_area / min_area) * 50
        else:
            area_fitness = max(0, 100 - (total_area - max_area) / max_area * 50)
        
        # 2. FAR fitness (prefer higher FAR)
        far_fitness = min(100, (avg_far / 250) * 100)
        
        # 3. Cost efficiency (prefer lower cost per sqm)
        cost_per_sqm = total_cost / total_area if total_area > 0 else 1e10
        cost_fitness = max(0, 100 - (cost_per_sqm / 5_000_000) * 50)
        
        # 4. Parcel count penalty (prefer fewer parcels)
        parcel_penalty = len(selected_parcels) * 5
        
        # Weighted fitness
        fitness = (
            area_fitness * 0.35 +
            far_fitness * 0.30 +
            cost_fitness * 0.25 +
            (100 - parcel_penalty) * 0.10
        )
        
        return max(0, fitness)
    
    def _ga_tournament_selection(
        self,
        population: List[List[int]],
        fitness_scores: List[float],
        selection_size: int,
        tournament_size: int = 3
    ) -> List[List[int]]:
        """Tournament selection for GA"""
        selected = []
        
        for _ in range(selection_size):
            # Random tournament
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            
            # Select winner
            winner_idx = tournament_indices[tournament_fitness.index(max(tournament_fitness))]
            selected.append(population[winner_idx][:])
        
        return selected
    
    def _ga_crossover(
        self,
        parent1: List[int],
        parent2: List[int]
    ) -> Tuple[List[int], List[int]]:
        """Single-point crossover"""
        if len(parent1) < 2:
            return parent1[:], parent2[:]
        
        crossover_point = random.randint(1, len(parent1) - 1)
        
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2
    
    def _ga_mutate(
        self,
        chromosome: List[int],
        parcel_count: int
    ) -> List[int]:
        """Bit-flip mutation"""
        mutated = chromosome[:]
        mutation_point = random.randint(0, len(mutated) - 1)
        mutated[mutation_point] = 1 - mutated[mutation_point]  # Flip bit
        
        # Ensure at least one parcel selected
        if sum(mutated) == 0:
            mutated[random.randint(0, len(mutated) - 1)] = 1
        
        return mutated
    
    # ========================================================================
    # NEW FEATURE #3: SYNERGY HEATMAP
    # ========================================================================
    
    def generate_synergy_heatmap(
        self,
        parcels: List[Dict]
    ) -> str:
        """
        Generate parcel-to-parcel synergy heatmap
        
        Shows synergy score between each parcel pair (0-100 scale)
        
        Args:
            parcels: List of parcels
            
        Returns:
            Base64-encoded PNG heatmap
        """
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("matplotlib not available - returning empty heatmap")
            return ""
        
        logger.info(f"Generating synergy heatmap for {len(parcels)} parcels")
        
        n = len(parcels)
        synergy_matrix = np.zeros((n, n))
        
        # Calculate pairwise synergy scores
        for i in range(n):
            for j in range(n):
                if i == j:
                    synergy_matrix[i][j] = 100  # Self-synergy = 100
                else:
                    synergy_matrix[i][j] = self._calculate_pairwise_synergy(
                        parcels[i], parcels[j]
                    )
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(synergy_matrix, cmap='RdYlGn', vmin=0, vmax=100, aspect='auto')
        
        # Set ticks and labels
        parcel_ids = [p.get('id', f'P{i+1}') for i, p in enumerate(parcels)]
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(parcel_ids, rotation=45, ha='right')
        ax.set_yticklabels(parcel_ids)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Synergy Score (0-100)', rotation=270, labelpad=20)
        
        # Add text annotations
        for i in range(n):
            for j in range(n):
                text = ax.text(j, i, f'{synergy_matrix[i][j]:.0f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        ax.set_title('Parcel Synergy Heatmap', fontsize=14, fontweight='bold')
        ax.set_xlabel('Parcel ID', fontsize=12)
        ax.set_ylabel('Parcel ID', fontsize=12)
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()
        
        return image_base64
    
    def _calculate_pairwise_synergy(
        self,
        parcel1: Dict,
        parcel2: Dict
    ) -> float:
        """
        Calculate synergy score between two parcels (0-100)
        
        Factors:
        1. Proximity (closer = better)
        2. FAR compatibility (similar = better)
        3. Size compatibility (similar = better)
        4. Shape regularity (both regular = better)
        """
        score = 0
        
        # 1. Proximity score (30 points)
        lat1, lon1 = parcel1.get('latitude', 0), parcel1.get('longitude', 0)
        lat2, lon2 = parcel2.get('latitude', 0), parcel2.get('longitude', 0)
        
        distance_km = self._calculate_distance(lat1, lon1, lat2, lon2)
        
        if distance_km < 0.1:  # <100m
            proximity_score = 30
        elif distance_km < 0.3:  # <300m
            proximity_score = 20
        elif distance_km < 0.5:  # <500m
            proximity_score = 10
        else:
            proximity_score = 0
        
        score += proximity_score
        
        # 2. FAR compatibility (25 points)
        far1 = parcel1.get('max_far', 200)
        far2 = parcel2.get('max_far', 200)
        far_diff = abs(far1 - far2)
        
        if far_diff < 20:
            score += 25
        elif far_diff < 50:
            score += 15
        else:
            score += 5
        
        # 3. Size compatibility (25 points)
        area1 = parcel1.get('area_sqm', 500)
        area2 = parcel2.get('area_sqm', 500)
        size_ratio = min(area1, area2) / max(area1, area2)
        
        if size_ratio > 0.7:
            score += 25
        elif size_ratio > 0.5:
            score += 15
        else:
            score += 5
        
        # 4. Shape regularity (20 points)
        shape1 = parcel1.get('shape_regularity', 0.7)
        shape2 = parcel2.get('shape_regularity', 0.7)
        avg_shape = (shape1 + shape2) / 2
        
        score += avg_shape * 20
        
        return min(100, score)
    
    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points (km) using Haversine formula"""
        if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
            return 0.5  # Default distance if coordinates missing
        
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c


# ========================================================================
# HELPER FUNCTIONS
# ========================================================================

def check_matplotlib_available() -> bool:
    """Check if matplotlib is available for visualization"""
    return MATPLOTLIB_AVAILABLE
