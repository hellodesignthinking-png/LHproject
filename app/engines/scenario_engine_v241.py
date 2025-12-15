"""
ZeroSite v24.1 - Enhanced Scenario Engine

NEW FEATURES (v24.1 GAP #2):
- Scenario C (고령자형) implementation
- 3-way comparison (A/B/C)
- 18 metrics (15 existing + 3 new)
- Carbon Footprint calculation
- Social Value Score calculation
- Market Competitiveness Score calculation

Priority: 🔴 CRITICAL (v24.1 GAP Closing)
Specification: docs/ZEROSITE_V24.1_GAP_CLOSING_PLAN.md

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

from .scenario_engine import ScenarioEngine

logger = logging.getLogger(__name__)


@dataclass
class ScenarioMetrics:
    """Complete scenario metrics (18 total)"""
    # Original 15 metrics
    total_units: int
    residential_area: float
    construction_cost: float
    land_acquisition_cost: float
    total_investment: float
    total_revenue: float
    profit: float
    roi: float  # %
    irr: float  # %
    payback_period: float  # years
    parking_spaces: int
    far: float  # %
    bcr: float  # %
    building_height: float  # meters
    compliance_score: int  # 0-100
    
    # NEW 3 metrics (v24.1)
    carbon_footprint: float  # tCO2e
    social_value_score: int  # 0-100
    market_competitiveness: int  # 0-100


@dataclass
class ScenarioComparison:
    """3-way scenario comparison result"""
    scenario_a: ScenarioMetrics
    scenario_b: ScenarioMetrics
    scenario_c: ScenarioMetrics
    
    comparison_matrix: Dict[str, Dict[str, Any]]
    rankings: Dict[str, int]  # scenario_name -> rank (1/2/3)
    
    best_scenario: str  # 'A', 'B', or 'C'
    recommendation: str
    tradeoff_analysis: Dict[str, Any]


class ScenarioEngineV241(ScenarioEngine):
    """
    Enhanced Scenario Engine for ZeroSite v24.1
    
    NEW FEATURES:
    1. Scenario C (고령자형) - Elderly housing type
    2. 3-way comparison (A vs B vs C)
    3. 18 metrics (15 existing + 3 new)
       - Carbon Footprint
       - Social Value Score
       - Market Competitiveness
    """
    
    # Scenario type definitions
    SCENARIO_TYPES = {
        'A': {
            'name': '청년형',
            'target': '청년·신혼부부',
            'unit_size_range': (26, 46),  # m²
            'unit_mix': {'1인형': 0.6, '2인형': 0.4},
            'description': '소형 평형 중심, 역세권 입지'
        },
        'B': {
            'name': '일반형',
            'target': '일반 가구',
            'unit_size_range': (46, 85),  # m²
            'unit_mix': {'2인형': 0.5, '3인형': 0.5},
            'description': '중형 평형, 일반 임대주택'
        },
        'C': {
            'name': '고령자형',
            'target': '고령자·장애인',
            'unit_size_range': (36, 59),  # m²
            'unit_mix': {'1인형': 0.4, '2인형': 0.6},
            'description': '무장애 설계, 복지시설 연계'
        }
    }
    
    def __init__(self):
        """Initialize Enhanced Scenario Engine v24.1"""
        super().__init__()
        self.version = "24.1.0"
        self.logger.info("Enhanced Scenario Engine v24.1.0 initialized (GAP #2)")
    
    # ========================================================================
    # NEW FEATURE: 3-WAY COMPARISON (A/B/C)
    # ========================================================================
    
    def compare_abc_scenarios(
        self,
        scenario_a_data: Dict,
        scenario_b_data: Dict,
        scenario_c_data: Dict,
        weights: Optional[Dict[str, float]] = None
    ) -> ScenarioComparison:
        """
        3-way scenario comparison with 18 metrics
        
        Args:
            scenario_a_data: Scenario A input data
            scenario_b_data: Scenario B input data
            scenario_c_data: Scenario C input data (NEW)
            weights: Custom metric weights (optional)
            
        Returns:
            ScenarioComparison object with complete analysis
        """
        self.logger.info("Starting 3-way scenario comparison (A/B/C)")
        
        # Default weights for 18 metrics
        if weights is None:
            weights = self._get_default_weights()
        
        # Calculate metrics for each scenario
        metrics_a = self._calculate_scenario_metrics(scenario_a_data, 'A')
        metrics_b = self._calculate_scenario_metrics(scenario_b_data, 'B')
        metrics_c = self._calculate_scenario_metrics(scenario_c_data, 'C')
        
        # Create comparison matrix
        comparison_matrix = self._create_comparison_matrix(
            metrics_a, metrics_b, metrics_c
        )
        
        # Calculate rankings
        rankings = self._calculate_rankings(
            metrics_a, metrics_b, metrics_c, weights
        )
        
        # Determine best scenario
        best_scenario = min(rankings, key=rankings.get)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            best_scenario, rankings, metrics_a, metrics_b, metrics_c
        )
        
        # Perform tradeoff analysis
        tradeoff_analysis = self._perform_tradeoff_analysis(
            metrics_a, metrics_b, metrics_c
        )
        
        self.logger.info(
            f"3-way comparison complete: Best = {best_scenario}, "
            f"Rankings = {rankings}"
        )
        
        return ScenarioComparison(
            scenario_a=metrics_a,
            scenario_b=metrics_b,
            scenario_c=metrics_c,
            comparison_matrix=comparison_matrix,
            rankings=rankings,
            best_scenario=best_scenario,
            recommendation=recommendation,
            tradeoff_analysis=tradeoff_analysis
        )
    
    # ========================================================================
    # NEW FEATURE: 18 METRICS CALCULATION
    # ========================================================================
    
    def _calculate_scenario_metrics(
        self,
        scenario_data: Dict,
        scenario_type: str
    ) -> ScenarioMetrics:
        """
        Calculate all 18 metrics for a scenario
        
        15 existing metrics + 3 new metrics:
        - Carbon Footprint (NEW)
        - Social Value Score (NEW)
        - Market Competitiveness (NEW)
        """
        
        # Extract base data
        land_area = scenario_data.get('land_area_sqm', 660.0)
        far = scenario_data.get('far', 200.0)
        bcr = scenario_data.get('bcr', 60.0)
        floors = scenario_data.get('floors', 10)
        unit_area_avg = scenario_data.get('unit_area_avg', 45.0)
        
        # Calculate building metrics
        building_footprint = land_area * (bcr / 100)
        total_floor_area = building_footprint * floors
        residential_area = total_floor_area * 0.75  # 75% efficiency
        
        # Original 15 metrics
        total_units = int(residential_area / unit_area_avg)
        
        construction_cost_per_sqm = 1_850_000  # 원/㎡
        construction_cost = total_floor_area * construction_cost_per_sqm
        
        land_cost_per_sqm = scenario_data.get('land_price_per_sqm', 3_000_000)
        land_acquisition_cost = land_area * land_cost_per_sqm
        
        total_investment = construction_cost + land_acquisition_cost
        
        revenue_per_unit = scenario_data.get('revenue_per_unit', 250_000_000)
        total_revenue = total_units * revenue_per_unit
        
        profit = total_revenue - total_investment
        roi = (profit / total_investment) * 100 if total_investment > 0 else 0
        
        # Simplified IRR (assume 5-year project)
        irr = self._calculate_simple_irr(profit, total_investment)
        
        # Payback period (years)
        annual_cashflow = profit / 5  # Assume 5-year distribution
        payback_period = total_investment / annual_cashflow if annual_cashflow > 0 else 999
        
        parking_spaces = int(total_units * 0.8)  # 0.8 spaces per unit
        building_height = floors * 3.0  # 3m per floor
        
        compliance_score = self._calculate_compliance_score(scenario_data)
        
        # NEW METRIC #1: Carbon Footprint (tCO2e)
        carbon_footprint = self._calculate_carbon_footprint(
            total_floor_area, scenario_type
        )
        
        # NEW METRIC #2: Social Value Score (0-100)
        social_value_score = self._calculate_social_value_score(
            scenario_type, total_units, scenario_data
        )
        
        # NEW METRIC #3: Market Competitiveness (0-100)
        market_competitiveness = self._calculate_market_competitiveness(
            scenario_type, unit_area_avg, land_area, scenario_data
        )
        
        return ScenarioMetrics(
            total_units=total_units,
            residential_area=round(residential_area, 2),
            construction_cost=round(construction_cost, 0),
            land_acquisition_cost=round(land_acquisition_cost, 0),
            total_investment=round(total_investment, 0),
            total_revenue=round(total_revenue, 0),
            profit=round(profit, 0),
            roi=round(roi, 2),
            irr=round(irr, 2),
            payback_period=round(payback_period, 1),
            parking_spaces=parking_spaces,
            far=round(far, 2),
            bcr=round(bcr, 2),
            building_height=round(building_height, 2),
            compliance_score=compliance_score,
            carbon_footprint=round(carbon_footprint, 2),
            social_value_score=social_value_score,
            market_competitiveness=market_competitiveness
        )
    
    # ========================================================================
    # NEW METRIC CALCULATIONS
    # ========================================================================
    
    def _calculate_carbon_footprint(
        self,
        total_floor_area: float,
        scenario_type: str
    ) -> float:
        """
        Calculate building lifecycle carbon footprint (tCO2e)
        
        Components:
        1. Construction emissions: 0.5 tCO2e/㎡
        2. Operational emissions: 0.03 tCO2e/㎡/year
        3. Lifecycle: 30 years
        
        Adjustments:
        - Scenario C (고령자형): -10% (smaller units, less consumption)
        """
        # Construction phase
        construction_co2 = total_floor_area * 0.5  # 0.5 tCO2e/㎡
        
        # Operational phase (30 years)
        annual_operation_co2 = total_floor_area * 0.03  # 0.03 tCO2e/㎡/year
        operation_co2_30years = annual_operation_co2 * 30
        
        # Total lifecycle
        total_co2 = construction_co2 + operation_co2_30years
        
        # Scenario-specific adjustments
        if scenario_type == 'C':
            # Elderly housing: smaller units, lower energy consumption
            total_co2 *= 0.90  # -10%
        elif scenario_type == 'A':
            # Youth housing: smaller units
            total_co2 *= 0.95  # -5%
        
        return total_co2
    
    def _calculate_social_value_score(
        self,
        scenario_type: str,
        total_units: int,
        scenario_data: Dict
    ) -> int:
        """
        Calculate social value score (0-100)
        
        Components (weighted):
        - Affordable housing provision (30 points)
        - Public facility integration (25 points)
        - Green space provision (20 points)
        - Accessibility (15 points)
        - Community impact (10 points)
        """
        score = 0
        
        # 1. Affordable housing (30 points)
        # More units = higher social value
        if total_units >= 100:
            score += 30
        elif total_units >= 50:
            score += 25
        elif total_units >= 30:
            score += 20
        else:
            score += 15
        
        # 2. Public facility integration (25 points)
        # Scenario C (elderly) gets bonus for welfare facilities
        if scenario_type == 'C':
            score += 25  # Mandatory welfare facilities
        elif scenario_type == 'A':
            score += 20  # Community facilities
        else:
            score += 15  # Basic facilities
        
        # 3. Green space provision (20 points)
        green_space_ratio = scenario_data.get('green_space_ratio', 0.20)
        if green_space_ratio >= 0.30:
            score += 20
        elif green_space_ratio >= 0.20:
            score += 15
        else:
            score += 10
        
        # 4. Accessibility (15 points)
        # Scenario C gets bonus for barrier-free design
        if scenario_type == 'C':
            score += 15  # Full accessibility
        else:
            transit_distance = scenario_data.get('transit_distance_m', 500)
            if transit_distance <= 300:
                score += 15
            elif transit_distance <= 500:
                score += 12
            else:
                score += 8
        
        # 5. Community impact (10 points)
        # All scenarios contribute positively
        score += 10
        
        return min(score, 100)
    
    def _calculate_market_competitiveness(
        self,
        scenario_type: str,
        unit_area_avg: float,
        land_area: float,
        scenario_data: Dict
    ) -> int:
        """
        Calculate market competitiveness score (0-100)
        
        Components (weighted):
        - Location score (30 points)
        - Unit size appropriateness (25 points)
        - Price competitiveness (25 points)
        - Amenities (20 points)
        """
        score = 0
        
        # 1. Location score (30 points)
        transit_distance = scenario_data.get('transit_distance_m', 500)
        if transit_distance <= 300:
            score += 30
        elif transit_distance <= 500:
            score += 25
        elif transit_distance <= 1000:
            score += 20
        else:
            score += 15
        
        # 2. Unit size appropriateness (25 points)
        optimal_ranges = {
            'A': (26, 46),  # Youth
            'B': (46, 85),  # General
            'C': (36, 59)   # Elderly
        }
        min_size, max_size = optimal_ranges.get(scenario_type, (40, 60))
        
        if min_size <= unit_area_avg <= max_size:
            score += 25
        elif min_size * 0.9 <= unit_area_avg <= max_size * 1.1:
            score += 20
        else:
            score += 15
        
        # 3. Price competitiveness (25 points)
        # Lower price = higher competitiveness
        revenue_per_unit = scenario_data.get('revenue_per_unit', 250_000_000)
        market_avg = 250_000_000  # 2.5억 원
        
        price_ratio = revenue_per_unit / market_avg
        if price_ratio <= 0.80:
            score += 25
        elif price_ratio <= 0.90:
            score += 22
        elif price_ratio <= 1.00:
            score += 20
        else:
            score += 15
        
        # 4. Amenities (20 points)
        # Scenario-specific bonuses
        if scenario_type == 'C':
            score += 20  # Healthcare, welfare facilities
        elif scenario_type == 'A':
            score += 18  # Community spaces, cafes
        else:
            score += 16  # Standard amenities
        
        return min(score, 100)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _calculate_simple_irr(self, profit: float, investment: float) -> float:
        """Calculate simplified IRR for 5-year project"""
        if investment <= 0:
            return 0.0
        
        # Simplified: assume profit distributed over 5 years
        annual_return = profit / 5
        irr = (annual_return / investment) * 100
        
        return max(0.0, min(irr, 50.0))  # Cap at 50%
    
    def _calculate_compliance_score(self, scenario_data: Dict) -> int:
        """Calculate regulatory compliance score (0-100)"""
        score = 100
        
        # Check FAR compliance
        far = scenario_data.get('far', 200)
        far_limit = scenario_data.get('far_limit', 250)
        if far > far_limit:
            score -= 30
        
        # Check parking compliance
        parking_ratio = scenario_data.get('parking_ratio', 0.8)
        if parking_ratio < 0.7:
            score -= 20
        
        # Check sunlight compliance
        sunlight_compliant = scenario_data.get('sunlight_compliant', True)
        if not sunlight_compliant:
            score -= 25
        
        return max(score, 0)
    
    def _get_default_weights(self) -> Dict[str, float]:
        """Get default weights for 18 metrics"""
        return {
            'roi': 0.15,
            'irr': 0.12,
            'profit': 0.10,
            'total_units': 0.08,
            'payback_period': 0.08,
            'social_value_score': 0.10,  # NEW
            'market_competitiveness': 0.10,  # NEW
            'carbon_footprint': 0.08,  # NEW (negative)
            'compliance_score': 0.07,
            'far': 0.05,
            'parking_spaces': 0.03,
            'building_height': 0.02,
            'bcr': 0.02
        }
    
    def _create_comparison_matrix(
        self,
        metrics_a: ScenarioMetrics,
        metrics_b: ScenarioMetrics,
        metrics_c: ScenarioMetrics
    ) -> Dict[str, Dict[str, Any]]:
        """Create comparison matrix for all 18 metrics"""
        
        matrix = {}
        
        # Get all metric fields
        for field in metrics_a.__dataclass_fields__:
            value_a = getattr(metrics_a, field)
            value_b = getattr(metrics_b, field)
            value_c = getattr(metrics_c, field)
            
            # Determine best value (higher is better, except carbon_footprint)
            if field == 'carbon_footprint':
                best_value = min(value_a, value_b, value_c)
                winner = 'A' if value_a == best_value else ('B' if value_b == best_value else 'C')
            else:
                best_value = max(value_a, value_b, value_c)
                winner = 'A' if value_a == best_value else ('B' if value_b == best_value else 'C')
            
            matrix[field] = {
                'A': value_a,
                'B': value_b,
                'C': value_c,
                'best': winner,
                'best_value': best_value
            }
        
        return matrix
    
    def _calculate_rankings(
        self,
        metrics_a: ScenarioMetrics,
        metrics_b: ScenarioMetrics,
        metrics_c: ScenarioMetrics,
        weights: Dict[str, float]
    ) -> Dict[str, int]:
        """Calculate rankings (1st/2nd/3rd) for each scenario"""
        
        scores = {
            'A': self._calculate_weighted_score(metrics_a, weights),
            'B': self._calculate_weighted_score(metrics_b, weights),
            'C': self._calculate_weighted_score(metrics_c, weights)
        }
        
        # Sort by score (descending)
        sorted_scenarios = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Assign rankings
        rankings = {}
        for rank, (scenario, score) in enumerate(sorted_scenarios, 1):
            rankings[scenario] = rank
        
        return rankings
    
    def _calculate_weighted_score(
        self,
        metrics: ScenarioMetrics,
        weights: Dict[str, float]
    ) -> float:
        """Calculate weighted total score for a scenario"""
        
        score = 0.0
        
        # Normalize and weight each metric
        score += (metrics.roi / 20) * 100 * weights.get('roi', 0.15)
        score += (metrics.irr / 15) * 100 * weights.get('irr', 0.12)
        score += (metrics.profit / 50_000_000_000) * 100 * weights.get('profit', 0.10)
        score += (metrics.total_units / 100) * 100 * weights.get('total_units', 0.08)
        score += (10 / max(metrics.payback_period, 1)) * 100 * weights.get('payback_period', 0.08)
        
        # NEW metrics
        score += metrics.social_value_score * weights.get('social_value_score', 0.10)
        score += metrics.market_competitiveness * weights.get('market_competitiveness', 0.10)
        score += (1 - metrics.carbon_footprint / 10000) * 100 * weights.get('carbon_footprint', 0.08)
        
        score += metrics.compliance_score * weights.get('compliance_score', 0.07)
        
        return score
    
    def _generate_recommendation(
        self,
        best_scenario: str,
        rankings: Dict[str, int],
        metrics_a: ScenarioMetrics,
        metrics_b: ScenarioMetrics,
        metrics_c: ScenarioMetrics
    ) -> str:
        """Generate detailed recommendation text"""
        
        scenario_names = {
            'A': '청년형 (Scenario A)',
            'B': '일반형 (Scenario B)',
            'C': '고령자형 (Scenario C)'
        }
        
        best_metrics = {
            'A': metrics_a,
            'B': metrics_b,
            'C': metrics_c
        }[best_scenario]
        
        recommendation = f"""
✅ **최종 권장안: {scenario_names[best_scenario]}**

**종합 순위:**
1위: {scenario_names[[k for k, v in rankings.items() if v == 1][0]]}
2위: {scenario_names[[k for k, v in rankings.items() if v == 2][0]]}
3위: {scenario_names[[k for k, v in rankings.items() if v == 3][0]]}

**권장 사유:**
- ROI: {best_metrics.roi:.1f}%
- IRR: {best_metrics.irr:.1f}%
- 세대수: {best_metrics.total_units}세대
- 사회적 가치: {best_metrics.social_value_score}/100
- 시장 경쟁력: {best_metrics.market_competitiveness}/100
- 탄소배출: {best_metrics.carbon_footprint:.0f} tCO2e

**권장 타입:** {self.SCENARIO_TYPES[best_scenario]['description']}
"""
        
        return recommendation.strip()
    
    def _perform_tradeoff_analysis(
        self,
        metrics_a: ScenarioMetrics,
        metrics_b: ScenarioMetrics,
        metrics_c: ScenarioMetrics
    ) -> Dict[str, Any]:
        """Perform tradeoff analysis between scenarios"""
        
        return {
            'roi_comparison': {
                'A': metrics_a.roi,
                'B': metrics_b.roi,
                'C': metrics_c.roi,
                'spread': max(metrics_a.roi, metrics_b.roi, metrics_c.roi) - 
                         min(metrics_a.roi, metrics_b.roi, metrics_c.roi)
            },
            'social_value_comparison': {
                'A': metrics_a.social_value_score,
                'B': metrics_b.social_value_score,
                'C': metrics_c.social_value_score,
                'best': 'C' if metrics_c.social_value_score == max(
                    metrics_a.social_value_score,
                    metrics_b.social_value_score,
                    metrics_c.social_value_score
                ) else ('A' if metrics_a.social_value_score > metrics_b.social_value_score else 'B')
            },
            'carbon_comparison': {
                'A': metrics_a.carbon_footprint,
                'B': metrics_b.carbon_footprint,
                'C': metrics_c.carbon_footprint,
                'best': 'C' if metrics_c.carbon_footprint == min(
                    metrics_a.carbon_footprint,
                    metrics_b.carbon_footprint,
                    metrics_c.carbon_footprint
                ) else ('A' if metrics_a.carbon_footprint < metrics_b.carbon_footprint else 'B')
            }
        }


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    """Test the Enhanced Scenario Engine v24.1"""
    
    engine = ScenarioEngineV241()
    
    print("=" * 80)
    print("ENHANCED SCENARIO ENGINE v24.1 TEST (GAP #2)")
    print("=" * 80)
    
    # Test data for 3 scenarios
    scenario_a = {
        'land_area_sqm': 660.0,
        'far': 200.0,
        'bcr': 60.0,
        'floors': 10,
        'unit_area_avg': 36.0,  # Small units for youth
        'land_price_per_sqm': 3_000_000,
        'revenue_per_unit': 200_000_000,  # 2억
        'transit_distance_m': 350,
        'green_space_ratio': 0.25,
        'parking_ratio': 0.8,
        'sunlight_compliant': True
    }
    
    scenario_b = {
        'land_area_sqm': 660.0,
        'far': 220.0,
        'bcr': 60.0,
        'floors': 11,
        'unit_area_avg': 59.0,  # Medium units for general
        'land_price_per_sqm': 3_000_000,
        'revenue_per_unit': 280_000_000,  # 2.8억
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
        'unit_area_avg': 46.0,  # Small-medium for elderly
        'land_price_per_sqm': 3_000_000,
        'revenue_per_unit': 240_000_000,  # 2.4억
        'transit_distance_m': 300,
        'green_space_ratio': 0.30,
        'parking_ratio': 0.7,
        'sunlight_compliant': True
    }
    
    # Perform 3-way comparison
    comparison = engine.compare_abc_scenarios(scenario_a, scenario_b, scenario_c)
    
    print(f"\n{'='*80}")
    print("3-WAY SCENARIO COMPARISON (A vs B vs C)")
    print(f"{'='*80}")
    
    print(f"\n✅ Rankings:")
    for scenario, rank in sorted(comparison.rankings.items(), key=lambda x: x[1]):
        print(f"   {rank}위: Scenario {scenario} ({engine.SCENARIO_TYPES[scenario]['name']})")
    
    print(f"\n✅ Best Scenario: {comparison.best_scenario}")
    print(comparison.recommendation)
    
    print(f"\n{'='*80}")
    print("18 METRICS COMPARISON")
    print(f"{'='*80}")
    
    # Show key metrics
    key_metrics = [
        'total_units', 'roi', 'irr', 'profit',
        'carbon_footprint', 'social_value_score', 'market_competitiveness'
    ]
    
    print(f"\n{'Metric':<30} {'A':>12} {'B':>12} {'C':>12} {'Best':>8}")
    print("-" * 80)
    
    for metric in key_metrics:
        values = comparison.comparison_matrix[metric]
        print(f"{metric:<30} {values['A']:>12} {values['B']:>12} {values['C']:>12} {values['best']:>8}")
    
    print(f"\n{'='*80}")
    print("✅ ALL TESTS COMPLETED - GAP #2 IMPLEMENTED")
    print(f"{'='*80}")
