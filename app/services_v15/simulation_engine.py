"""
ZeroSite v15 Phase 2 - Simulation Engine
=========================================

3-Scenario Monte Carlo Analysis for LH Project Viability

Scenarios:
1. BASE: Expected case with current market conditions
2. OPTIMISTIC: Best-case with favorable conditions (+15% revenue, -10% costs)
3. PESSIMISTIC: Worst-case with adverse conditions (-15% revenue, +10% costs)

Purpose: Provide range-based decision support instead of single-point estimates
Output: 3 complete financial models with probability-weighted outcomes
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScenarioParameters:
    """Parameters for a single scenario simulation"""
    name: str
    name_kr: str
    probability: float  # 0.0 to 1.0
    
    # Revenue adjustments
    revenue_multiplier: float  # 1.0 = base, 1.15 = +15%
    rent_escalation_rate: float  # Annual rent increase rate
    
    # Cost adjustments
    capex_multiplier: float  # 1.0 = base, 0.90 = -10%
    opex_multiplier: float  # Operating expense adjustment
    
    # Market adjustments
    vacancy_rate: float  # Expected vacancy rate
    discount_rate: float  # WACC or required return
    
    # Construction adjustments
    construction_delay_months: int  # Additional months
    contingency_rate: float  # Additional contingency %


class SimulationEngine:
    """
    v15 Phase 2 - Scenario-based Financial Simulation
    
    Generates 3 comprehensive scenarios:
    - BASE: Most likely outcome
    - OPTIMISTIC: Favorable market conditions
    - PESSIMISTIC: Adverse market conditions
    """
    
    def __init__(self):
        """Initialize simulation engine with default scenario parameters"""
        self.scenarios = {
            'base': ScenarioParameters(
                name='BASE',
                name_kr='기본 시나리오',
                probability=0.60,  # 60% probability
                revenue_multiplier=1.00,
                rent_escalation_rate=0.02,  # 2% annual
                capex_multiplier=1.00,
                opex_multiplier=1.00,
                vacancy_rate=0.05,  # 5%
                discount_rate=0.045,  # 4.5%
                construction_delay_months=0,
                contingency_rate=0.10  # 10%
            ),
            'optimistic': ScenarioParameters(
                name='OPTIMISTIC',
                name_kr='낙관 시나리오',
                probability=0.25,  # 25% probability
                revenue_multiplier=1.15,  # +15% revenue
                rent_escalation_rate=0.03,  # 3% annual
                capex_multiplier=0.90,  # -10% costs (VE success)
                opex_multiplier=0.95,  # -5% opex
                vacancy_rate=0.02,  # 2% (low vacancy)
                discount_rate=0.040,  # 4.0% (favorable financing)
                construction_delay_months=-2,  # 2 months early
                contingency_rate=0.08  # 8%
            ),
            'pessimistic': ScenarioParameters(
                name='PESSIMISTIC',
                name_kr='비관 시나리오',
                probability=0.15,  # 15% probability
                revenue_multiplier=0.85,  # -15% revenue
                rent_escalation_rate=0.01,  # 1% annual
                capex_multiplier=1.10,  # +10% costs (overruns)
                opex_multiplier=1.10,  # +10% opex
                vacancy_rate=0.10,  # 10% (high vacancy)
                discount_rate=0.055,  # 5.5% (higher risk premium)
                construction_delay_months=3,  # 3 months delay
                contingency_rate=0.15  # 15%
            )
        }
    
    def simulate_scenarios(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run 3-scenario simulation and return comprehensive results
        
        Args:
            context: Base project context from report_context_builder
            
        Returns:
            Dictionary with scenario results and probability-weighted metrics
        """
        logger.info("🎲 Running 3-scenario simulation...")
        
        # Extract base financial data
        finance = context.get('finance', {})
        base_capex = finance.get('capex', {}).get('total', 0)
        base_annual_revenue = finance.get('revenue', {}).get('annual_rental', 0)
        base_npv = finance.get('npv_public', 0)
        base_irr = finance.get('irr_public_pct', 0)
        
        # Run simulations for all 3 scenarios
        results = {}
        for scenario_key, params in self.scenarios.items():
            results[scenario_key] = self._simulate_scenario(
                params, base_capex, base_annual_revenue, base_npv, base_irr
            )
        
        # Calculate probability-weighted expected values
        expected_values = self._calculate_expected_values(results)
        
        # Generate comparison table
        comparison = self._generate_comparison_table(results)
        
        # Calculate decision metrics
        decision_metrics = self._calculate_decision_metrics(results, expected_values)
        
        return {
            'scenarios': results,
            'expected_values': expected_values,
            'comparison_table': comparison,
            'decision_metrics': decision_metrics,
            'recommendation': self._generate_recommendation(decision_metrics)
        }
    
    def _simulate_scenario(
        self,
        params: ScenarioParameters,
        base_capex: float,
        base_revenue: float,
        base_npv: float,
        base_irr: float
    ) -> Dict[str, Any]:
        """Run simulation for a single scenario"""
        
        # Adjusted CAPEX
        adjusted_capex = base_capex * params.capex_multiplier
        contingency = adjusted_capex * params.contingency_rate
        total_capex = adjusted_capex + contingency
        
        # Adjusted Revenue
        adjusted_annual_revenue = base_revenue * params.revenue_multiplier
        revenue_30yr = self._calculate_30year_revenue(
            adjusted_annual_revenue,
            params.rent_escalation_rate,
            params.vacancy_rate
        )
        
        # Calculate NPV for this scenario
        npv = self._calculate_scenario_npv(
            total_capex,
            revenue_30yr,
            params.discount_rate
        )
        
        # Estimate IRR (simplified calculation)
        irr = self._estimate_scenario_irr(
            total_capex,
            revenue_30yr
        )
        
        # Calculate payback period
        payback = self._calculate_payback_period(
            total_capex,
            adjusted_annual_revenue * (1 - params.vacancy_rate)
        )
        
        return {
            'name': params.name,
            'name_kr': params.name_kr,
            'probability': params.probability,
            'parameters': {
                'revenue_adjustment': f"{(params.revenue_multiplier - 1) * 100:+.0f}%",
                'cost_adjustment': f"{(params.capex_multiplier - 1) * 100:+.0f}%",
                'vacancy_rate': f"{params.vacancy_rate * 100:.1f}%",
                'discount_rate': f"{params.discount_rate * 100:.2f}%",
                'construction_delay': f"{params.construction_delay_months:+d} months"
            },
            'capex': {
                'base': adjusted_capex,
                'contingency': contingency,
                'total': total_capex,
                'total_krw': total_capex / 100_000_000  # Convert to 억원
            },
            'revenue': {
                'annual': adjusted_annual_revenue,
                'total_30yr': revenue_30yr,
                'annual_krw': adjusted_annual_revenue / 100_000_000
            },
            'npv': {
                'value': npv,
                'value_krw': npv / 100_000_000
            },
            'irr': {
                'percentage': irr,
                'status': 'positive' if irr > params.discount_rate else 'negative'
            },
            'payback': {
                'years': payback,
                'status': 'achievable' if payback < 20 else 'long_term'
            }
        }
    
    def _calculate_30year_revenue(
        self,
        annual_revenue: float,
        escalation_rate: float,
        vacancy_rate: float
    ) -> float:
        """Calculate total 30-year revenue with escalation and vacancy"""
        total = 0.0
        current_revenue = annual_revenue * (1 - vacancy_rate)
        
        for year in range(30):
            total += current_revenue
            current_revenue *= (1 + escalation_rate)
        
        return total
    
    def _calculate_scenario_npv(
        self,
        capex: float,
        total_revenue: float,
        discount_rate: float
    ) -> float:
        """Calculate NPV for scenario"""
        # Simplified NPV calculation
        annual_avg_revenue = total_revenue / 30
        annual_opex = annual_avg_revenue * 0.15  # 15% operating costs
        annual_net_cf = annual_avg_revenue - annual_opex
        
        # Present value of 30-year annuity
        if discount_rate > 0:
            pv_factor = (1 - (1 + discount_rate) ** -30) / discount_rate
            pv_cashflows = annual_net_cf * pv_factor
        else:
            pv_cashflows = annual_net_cf * 30
        
        return pv_cashflows - capex
    
    def _estimate_scenario_irr(self, capex: float, total_revenue: float) -> float:
        """Estimate IRR for scenario (simplified)"""
        if capex <= 0:
            return 0.0
        
        annual_avg_revenue = total_revenue / 30
        annual_opex = annual_avg_revenue * 0.15
        annual_net_cf = annual_avg_revenue - annual_opex
        
        # Simple IRR estimation: (Annual CF / CAPEX) as approximation
        return (annual_net_cf / capex) * 100 if capex > 0 else 0.0
    
    def _calculate_payback_period(self, capex: float, annual_cf: float) -> float:
        """Calculate simple payback period"""
        if annual_cf <= 0:
            return 999.0
        return capex / annual_cf
    
    def _calculate_expected_values(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate probability-weighted expected values"""
        expected_npv = sum(
            results[key]['npv']['value'] * results[key]['probability']
            for key in results
        )
        
        expected_irr = sum(
            results[key]['irr']['percentage'] * results[key]['probability']
            for key in results
        )
        
        expected_payback = sum(
            results[key]['payback']['years'] * results[key]['probability']
            for key in results
        )
        
        return {
            'npv': expected_npv,
            'npv_krw': expected_npv / 100_000_000,
            'irr': expected_irr,
            'payback': expected_payback,
            'interpretation': self._interpret_expected_values(expected_npv, expected_irr)
        }
    
    def _interpret_expected_values(self, npv: float, irr: float) -> str:
        """Interpret expected values for decision-making"""
        if npv > 0 and irr > 4.5:
            return "기대값 기준 사업 타당성 우수 (Highly Viable)"
        elif npv > 0 and irr > 3.0:
            return "기대값 기준 사업 타당성 양호 (Viable)"
        elif npv > 0:
            return "기대값 기준 신중한 검토 필요 (Cautious)"
        else:
            return "기대값 기준 재검토 권고 (Review Required)"
    
    def _generate_comparison_table(self, results: Dict[str, Dict]) -> List[Dict]:
        """Generate side-by-side comparison table"""
        return [
            {
                'metric': 'CAPEX (억원)',
                'base': f"{results['base']['capex']['total_krw']:.1f}",
                'optimistic': f"{results['optimistic']['capex']['total_krw']:.1f}",
                'pessimistic': f"{results['pessimistic']['capex']['total_krw']:.1f}"
            },
            {
                'metric': 'NPV (억원)',
                'base': f"{results['base']['npv']['value_krw']:.1f}",
                'optimistic': f"{results['optimistic']['npv']['value_krw']:.1f}",
                'pessimistic': f"{results['pessimistic']['npv']['value_krw']:.1f}"
            },
            {
                'metric': 'IRR (%)',
                'base': f"{results['base']['irr']['percentage']:.2f}",
                'optimistic': f"{results['optimistic']['irr']['percentage']:.2f}",
                'pessimistic': f"{results['pessimistic']['irr']['percentage']:.2f}"
            },
            {
                'metric': '회수기간 (년)',
                'base': f"{results['base']['payback']['years']:.1f}",
                'optimistic': f"{results['optimistic']['payback']['years']:.1f}",
                'pessimistic': f"{results['pessimistic']['payback']['years']:.1f}"
            }
        ]
    
    def _calculate_decision_metrics(
        self,
        results: Dict[str, Dict],
        expected: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate decision support metrics"""
        # Downside risk: Probability of negative outcome
        downside_risk = results['pessimistic']['probability'] if results['pessimistic']['npv']['value'] < 0 else 0.0
        
        # Upside potential: Optimistic NPV vs Base NPV
        upside_potential_krw = (
            results['optimistic']['npv']['value_krw'] - 
            results['base']['npv']['value_krw']
        )
        
        # Risk-adjusted return
        risk_adjusted_npv = (
            results['base']['npv']['value'] * results['base']['probability'] +
            results['optimistic']['npv']['value'] * results['optimistic']['probability'] * 0.8 +  # Discount optimistic
            results['pessimistic']['npv']['value'] * results['pessimistic']['probability'] * 1.2   # Weight pessimistic
        )
        
        return {
            'downside_risk': downside_risk,
            'downside_risk_pct': f"{downside_risk * 100:.1f}%",
            'upside_potential_krw': upside_potential_krw,
            'risk_adjusted_npv': risk_adjusted_npv,
            'risk_adjusted_npv_krw': risk_adjusted_npv / 100_000_000,
            'confidence_level': self._assess_confidence_level(downside_risk, expected['npv'])
        }
    
    def _assess_confidence_level(self, downside_risk: float, expected_npv: float) -> str:
        """Assess overall confidence level"""
        if downside_risk == 0 and expected_npv > 0:
            return "HIGH (높음)"
        elif downside_risk < 0.20 and expected_npv > 0:
            return "MEDIUM-HIGH (중상)"
        elif downside_risk < 0.30:
            return "MEDIUM (중)"
        else:
            return "LOW (낮음)"
    
    def _generate_recommendation(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final recommendation based on simulation"""
        confidence = metrics['confidence_level']
        downside_risk = metrics['downside_risk']
        
        if 'HIGH' in confidence:
            decision = 'GO'
            reason = '모든 시나리오에서 양호한 수익성 예상'
        elif 'MEDIUM-HIGH' in confidence:
            decision = 'CONDITIONAL'
            reason = '기본 및 낙관 시나리오에서 타당성 확보, 위험 관리 필요'
        elif downside_risk > 0.20:
            decision = 'REVISE'
            reason = '비관 시나리오 리스크 높음, 구조 개선 필요'
        else:
            decision = 'NO-GO'
            reason = '기대값 기준 수익성 미흡'
        
        return {
            'decision': decision,
            'reason': reason,
            'confidence': confidence,
            'key_actions': self._get_key_actions(decision)
        }
    
    def _get_key_actions(self, decision: str) -> List[str]:
        """Get recommended actions based on decision"""
        actions_map = {
            'GO': [
                '즉시 사업 추진',
                'LH 협의 개시',
                '금융 조달 시작'
            ],
            'CONDITIONAL': [
                'VE를 통한 CAPEX 10% 절감 추진',
                'LH 정책자금 2.87% 금리 확보',
                '공실률 최소화 전략 수립'
            ],
            'REVISE': [
                '설계 변경을 통한 비용 절감',
                '임대료 수준 재검토',
                '단계별 개발 검토'
            ],
            'NO-GO': [
                '대안 입지 검토',
                '사업 구조 전면 재설계',
                '시장 환경 개선 대기'
            ]
        }
        return actions_map.get(decision, [])


# Singleton instance
_simulation_engine = None

def get_simulation_engine() -> SimulationEngine:
    """Get singleton instance of simulation engine"""
    global _simulation_engine
    if _simulation_engine is None:
        _simulation_engine = SimulationEngine()
    return _simulation_engine
