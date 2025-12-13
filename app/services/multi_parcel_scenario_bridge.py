"""
ZeroSite v24.1 - Multi-Parcel Scenario Bridge
Automatically reflect parcel merger results into Scenario A/B/C analysis

Author: ZeroSite Development Team
Version: 24.1.0
Created: 2025-12-12
"""

from typing import Dict, Any, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class MultiParcelScenarioBridge:
    """
    Bridge between Multi-Parcel Optimizer and Scenario Engine
    
    Automatically converts multi-parcel merger results into
    Scenario A/B/C inputs with proper FAR, unit count, and economics.
    """
    
    def __init__(self):
        """Initialize bridge"""
        self.version = "24.1.0"
        logger.info("Multi-Parcel Scenario Bridge v24.1.0 initialized")
    
    def merge_to_scenario_inputs(
        self,
        multi_parcel_result: Dict[str, Any],
        base_scenario_config: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Convert multi-parcel merger results to Scenario A/B/C inputs
        
        Args:
            multi_parcel_result: Output from MultiParcelOptimizerV241
                - 'solutions': List of optimized combinations
                - 'metrics': Optimization metrics
            base_scenario_config: Base configuration
                - 'price_per_sqm': Land price per square meter
                - 'construction_cost_per_unit': Construction cost
                - 'target_roi': Target return on investment
        
        Returns:
            Tuple of (scenario_a_data, scenario_b_data, scenario_c_data)
        """
        logger.info("Converting multi-parcel results to scenario inputs")
        
        # Extract best solution
        solutions = multi_parcel_result.get('solutions', [])
        if not solutions:
            logger.warning("No solutions found in multi-parcel result")
            return self._generate_default_scenarios(base_scenario_config)
        
        best_solution = solutions[0]  # Top solution from genetic algorithm
        
        # Calculate merged parcel metrics
        merged_metrics = self._calculate_merged_metrics(
            best_solution, 
            base_scenario_config
        )
        
        # Generate synergy bonus from parcel combination
        synergy_bonus = self._calculate_synergy_bonus(
            best_solution,
            multi_parcel_result.get('metrics', {})
        )
        
        # Generate 3 scenarios based on merged metrics
        scenario_a = self._generate_scenario_a_conservative(
            merged_metrics, 
            synergy_bonus,
            base_scenario_config
        )
        
        scenario_b = self._generate_scenario_b_standard(
            merged_metrics, 
            synergy_bonus,
            base_scenario_config
        )
        
        scenario_c = self._generate_scenario_c_aggressive(
            merged_metrics, 
            synergy_bonus,
            base_scenario_config
        )
        
        logger.info(f"Generated scenarios - A: {scenario_a['units']} units, "
                   f"B: {scenario_b['units']} units, C: {scenario_c['units']} units")
        
        return scenario_a, scenario_b, scenario_c
    
    def _calculate_merged_metrics(
        self,
        solution: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate metrics for merged parcels
        
        Args:
            solution: Optimized parcel combination
            config: Base configuration
        
        Returns:
            Dictionary with merged metrics:
                - total_area: Total land area (㎡)
                - weighted_far: Weighted average FAR
                - max_units: Maximum buildable units
                - total_investment: Total investment required
                - accessibility_score: Average accessibility
        """
        # Extract parcel data from solution
        parcels = solution.get('parcels', [])
        if not parcels:
            return self._default_merged_metrics(config)
        
        # Calculate total area
        total_area = sum(p.get('area_sqm', 0) for p in parcels)
        
        # Calculate weighted average FAR
        total_far_weight = sum(
            p.get('area_sqm', 0) * p.get('max_far', 0) 
            for p in parcels
        )
        weighted_far = total_far_weight / total_area if total_area > 0 else 200.0
        
        # Calculate maximum units (assuming 80㎡ per unit)
        total_gfa = total_area * (weighted_far / 100)
        max_units = int(total_gfa / 80)
        
        # Calculate total investment
        price_per_sqm = config.get('price_per_sqm', 5000000)
        total_investment = total_area * price_per_sqm
        
        # Calculate average accessibility score
        accessibility_scores = [p.get('accessibility_score', 5.0) for p in parcels]
        avg_accessibility = sum(accessibility_scores) / len(accessibility_scores)
        
        # Calculate development difficulty (lower is better)
        difficulty_scores = [p.get('development_difficulty', 5.0) for p in parcels]
        avg_difficulty = sum(difficulty_scores) / len(difficulty_scores)
        
        return {
            'total_area': total_area,
            'weighted_far': weighted_far,
            'max_units': max_units,
            'total_investment': total_investment,
            'accessibility_score': avg_accessibility,
            'development_difficulty': avg_difficulty,
            'parcel_count': len(parcels)
        }
    
    def _calculate_synergy_bonus(
        self,
        solution: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> float:
        """
        Calculate synergy bonus from parcel combination
        
        Synergy factors:
        - Shape regularity improvement
        - Adjacency benefits
        - Combined accessibility
        - Scale economies
        
        Args:
            solution: Optimized solution
            metrics: Optimization metrics
        
        Returns:
            Synergy multiplier (1.0 = no bonus, >1.0 = positive synergy)
        """
        base_synergy = 1.0
        
        # Factor 1: Number of parcels (more parcels = more complexity, less synergy)
        parcel_count = len(solution.get('parcels', []))
        if parcel_count == 2:
            parcel_synergy = 1.10  # 10% bonus for 2 parcels
        elif parcel_count == 3:
            parcel_synergy = 1.15  # 15% bonus for 3 parcels
        elif parcel_count >= 4:
            parcel_synergy = 1.20  # 20% bonus for 4+ parcels
        else:
            parcel_synergy = 1.0
        
        # Factor 2: Shape regularity (from solution fitness)
        fitness = solution.get('fitness', 0.5)
        shape_synergy = 1.0 + (fitness * 0.1)  # Up to 10% bonus
        
        # Factor 3: Accessibility (from metrics)
        avg_accessibility = metrics.get('average_accessibility', 5.0)
        accessibility_synergy = 1.0 + ((avg_accessibility - 5.0) / 50)  # Scale 5-10 → 0-10%
        
        # Combine synergies (multiplicative)
        total_synergy = base_synergy * parcel_synergy * shape_synergy * accessibility_synergy
        
        # Cap at 1.3 (30% max bonus)
        total_synergy = min(total_synergy, 1.3)
        
        logger.info(f"Synergy calculation: parcel={parcel_synergy:.2f}, "
                   f"shape={shape_synergy:.2f}, access={accessibility_synergy:.2f}, "
                   f"total={total_synergy:.2f}")
        
        return total_synergy
    
    def _generate_scenario_a_conservative(
        self,
        merged_metrics: Dict[str, Any],
        synergy_bonus: float,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Scenario A: Conservative (80% of potential)
        
        Target: Low risk, quick approval, stable returns
        """
        max_units = merged_metrics['max_units']
        total_area = merged_metrics['total_area']
        weighted_far = merged_metrics['weighted_far']
        
        # Conservative: 80% utilization
        utilization = 0.8
        
        scenario_a = {
            'name': 'Scenario A: Conservative',
            'description': '안정적 개발 시나리오 (토지 잠재력의 80% 활용)',
            
            # Capacity
            'units': int(max_units * utilization),
            'far': weighted_far * utilization,
            'total_area': total_area,
            'gfa': total_area * (weighted_far * utilization / 100),
            
            # Investment
            'land_cost': merged_metrics['total_investment'],
            'construction_cost': int(max_units * utilization) * config.get('construction_cost_per_unit', 150000000),
            'total_investment': merged_metrics['total_investment'] + 
                              (int(max_units * utilization) * config.get('construction_cost_per_unit', 150000000)),
            
            # Returns (with synergy bonus)
            'expected_roi': config.get('target_roi', 0.12) * synergy_bonus * 0.95,  # Slightly lower for safety
            'expected_irr': 0.15 * synergy_bonus * 0.95,
            'payback_years': 7.5,
            
            # Risk
            'risk_level': 'LOW',
            'approval_probability': 0.90,
            
            # Synergy
            'synergy_bonus': synergy_bonus,
            'synergy_description': f'{(synergy_bonus - 1.0) * 100:.1f}% 시너지 효과'
        }
        
        return scenario_a
    
    def _generate_scenario_b_standard(
        self,
        merged_metrics: Dict[str, Any],
        synergy_bonus: float,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Scenario B: Standard (100% of potential)
        
        Target: Balanced risk/return, full utilization
        """
        max_units = merged_metrics['max_units']
        total_area = merged_metrics['total_area']
        weighted_far = merged_metrics['weighted_far']
        
        # Standard: 100% utilization
        utilization = 1.0
        
        scenario_b = {
            'name': 'Scenario B: Standard',
            'description': '표준 개발 시나리오 (토지 잠재력의 100% 활용)',
            
            # Capacity
            'units': max_units,
            'far': weighted_far,
            'total_area': total_area,
            'gfa': total_area * (weighted_far / 100),
            
            # Investment
            'land_cost': merged_metrics['total_investment'],
            'construction_cost': max_units * config.get('construction_cost_per_unit', 150000000),
            'total_investment': merged_metrics['total_investment'] + 
                              (max_units * config.get('construction_cost_per_unit', 150000000)),
            
            # Returns (with full synergy bonus)
            'expected_roi': config.get('target_roi', 0.12) * synergy_bonus,
            'expected_irr': 0.15 * synergy_bonus,
            'payback_years': 6.5,
            
            # Risk
            'risk_level': 'MEDIUM',
            'approval_probability': 0.80,
            
            # Synergy
            'synergy_bonus': synergy_bonus,
            'synergy_description': f'{(synergy_bonus - 1.0) * 100:.1f}% 시너지 효과 (완전 활용)'
        }
        
        return scenario_b
    
    def _generate_scenario_c_aggressive(
        self,
        merged_metrics: Dict[str, Any],
        synergy_bonus: float,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate Scenario C: Aggressive (120% with relaxation)
        
        Target: Maximum returns, requires policy incentives
        """
        max_units = merged_metrics['max_units']
        total_area = merged_metrics['total_area']
        weighted_far = merged_metrics['weighted_far']
        
        # Aggressive: 120% with FAR relaxation
        utilization = 1.2
        
        scenario_c = {
            'name': 'Scenario C: Aggressive',
            'description': '적극적 개발 시나리오 (용적률 완화 활용, 120% 달성)',
            
            # Capacity
            'units': int(max_units * utilization),
            'far': weighted_far * utilization,
            'total_area': total_area,
            'gfa': total_area * (weighted_far * utilization / 100),
            
            # Investment (10% premium for premium construction)
            'land_cost': merged_metrics['total_investment'],
            'construction_cost': int(max_units * utilization) * config.get('construction_cost_per_unit', 150000000) * 1.1,
            'total_investment': merged_metrics['total_investment'] + 
                              (int(max_units * utilization) * config.get('construction_cost_per_unit', 150000000) * 1.1),
            
            # Returns (highest with synergy, but requires incentives)
            'expected_roi': config.get('target_roi', 0.12) * synergy_bonus * 1.15,  # 15% boost
            'expected_irr': 0.15 * synergy_bonus * 1.15,
            'payback_years': 5.5,
            
            # Risk
            'risk_level': 'MEDIUM_HIGH',
            'approval_probability': 0.65,  # Requires policy approval
            
            # Requirements
            'requires_far_relaxation': True,
            'required_incentives': ['공공기여', '기반시설 기부채납', '임대주택 제공'],
            
            # Synergy
            'synergy_bonus': synergy_bonus * 1.1,  # Extra boost from scale
            'synergy_description': f'{(synergy_bonus * 1.1 - 1.0) * 100:.1f}% 시너지 효과 (규모의 경제)'
        }
        
        return scenario_c
    
    def _generate_default_scenarios(
        self,
        config: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """Generate default scenarios when no multi-parcel data available"""
        logger.warning("Generating default scenarios (no multi-parcel data)")
        
        default_area = config.get('default_area', 1000.0)
        default_far = config.get('default_far', 200.0)
        default_units = int(default_area * (default_far / 100) / 80)
        
        scenario_a = {
            'name': 'Scenario A: Conservative (Default)',
            'units': int(default_units * 0.8),
            'far': default_far * 0.8,
            'total_area': default_area,
            'expected_roi': 0.10,
            'synergy_bonus': 1.0
        }
        
        scenario_b = {
            'name': 'Scenario B: Standard (Default)',
            'units': default_units,
            'far': default_far,
            'total_area': default_area,
            'expected_roi': 0.12,
            'synergy_bonus': 1.0
        }
        
        scenario_c = {
            'name': 'Scenario C: Aggressive (Default)',
            'units': int(default_units * 1.2),
            'far': default_far * 1.2,
            'total_area': default_area,
            'expected_roi': 0.15,
            'synergy_bonus': 1.0
        }
        
        return scenario_a, scenario_b, scenario_c
    
    def _default_merged_metrics(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Return default merged metrics"""
        return {
            'total_area': config.get('default_area', 1000.0),
            'weighted_far': config.get('default_far', 200.0),
            'max_units': 100,
            'total_investment': 5000000000,
            'accessibility_score': 5.0,
            'development_difficulty': 5.0,
            'parcel_count': 1
        }
    
    def generate_merger_impact_narrative(
        self,
        original_metrics: Dict[str, Any],
        merged_metrics: Dict[str, Any],
        synergy_bonus: float
    ) -> str:
        """
        Generate Korean narrative explaining merger impact
        
        Args:
            original_metrics: Single parcel metrics
            merged_metrics: Merged parcel metrics
            synergy_bonus: Calculated synergy multiplier
        
        Returns:
            Professional Korean narrative
        """
        original_units = original_metrics.get('units', 0)
        merged_units = merged_metrics.get('max_units', 0)
        unit_increase = merged_units - original_units
        increase_pct = (unit_increase / original_units * 100) if original_units > 0 else 0
        
        synergy_pct = (synergy_bonus - 1.0) * 100
        
        narrative = f"""
**필지 통합 효과 분석**

{merged_metrics['parcel_count']}개 필지를 통합한 결과, 다음과 같은 개발 효과를 확인할 수 있습니다.

**규모 증대**:
- 개별 개발 시: 약 {original_units}세대
- 통합 개발 시: 약 {merged_units}세대
- 증가량: +{unit_increase}세대 ({increase_pct:.1f}% 증가)

**시너지 효과**:
- 통합 시너지: {synergy_pct:.1f}%
- 형상 정형화로 인한 설계 효율 개선
- 통합 접근성 향상
- 규모의 경제 효과

**경제성 개선**:
- 투자수익률(ROI) {synergy_pct:.1f}% 추가 상승 효과
- 사업 리스크 분산
- 인허가 효율성 증대

**추천사항**:
필지 통합을 통한 개발이 개별 개발 대비 {increase_pct:.1f}% 이상의 
세대수 증가와 {synergy_pct:.1f}%의 시너지 효과를 제공하므로, 
통합 개발을 적극 권장합니다.
        """.strip()
        
        return narrative


# Module exports
__all__ = ["MultiParcelScenarioBridge"]
