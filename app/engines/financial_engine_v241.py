"""
ZeroSite v24.1 - Enhanced Financial Engine

NEW FEATURES (v24.1 GAP #5):
- Payback Period calculation (simple & discounted)
- Externalized financial configuration
- Sensitivity analysis with tornado chart visualization

Priority: 🟡 MEDIUM (v24.1 GAP Closing)
Specification: docs/ZEROSITE_V24.1_GAP_CLOSING_PLAN.md

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass

# Financial configuration (inline for now)
FINANCIAL_CONFIG = {
    'discount_rate': 0.08,
    'irr_benchmark': 0.12,
    'roi_benchmark': 0.15,
    'payback_period': {
        'excellent_threshold': 5.0,
        'target_simple': 8.0,
        'max_acceptable': 12.0
    },
    'sensitivity_parameters': {
        'variables': ['total_investment', 'construction_cost', 'land_acquisition_cost', 'revenue_per_unit', 'total_units'],
        'variance_range': {
            'optimistic': -0.15,
            'pessimistic': 0.15
        }
    }
}

def get_discount_rate(scenario='default'):
    """Get discount rate for scenario"""
    return FINANCIAL_CONFIG['discount_rate']

def get_irr_benchmark(scenario='default'):
    """Get IRR benchmark for scenario"""
    return FINANCIAL_CONFIG['irr_benchmark']

def get_roi_benchmark(scenario='default'):
    """Get ROI benchmark for scenario"""
    return FINANCIAL_CONFIG['roi_benchmark']

logger = logging.getLogger(__name__)


@dataclass
class PaybackPeriodResult:
    """Payback period analysis result"""
    simple_payback_years: float
    discounted_payback_years: float
    cumulative_cashflow: List[float]
    assessment: str  # 'EXCELLENT', 'GOOD', 'ACCEPTABLE', 'POOR'
    recommendation: str


@dataclass
class SensitivityResult:
    """Sensitivity analysis result"""
    variable_name: str
    base_value: float
    optimistic_value: float
    pessimistic_value: float
    base_npv: float
    optimistic_npv: float
    pessimistic_npv: float
    npv_range: float
    sensitivity_index: float  # Higher = more sensitive


class FinancialEngineV241:
    """
    Enhanced Financial Engine for ZeroSite v24.1
    
    NEW FEATURES:
    1. Payback Period calculation (simple & discounted)
    2. Externalized configuration (FINANCIAL_CONFIG)
    3. Sensitivity analysis with tornado chart data
    """
    
    def __init__(self, discount_rate: Optional[float] = None):
        """
        Initialize Enhanced Financial Engine v24.1
        
        Args:
            discount_rate: Custom discount rate (overrides config default)
        """
        self.version = "24.1.0"
        self.config = FINANCIAL_CONFIG
        self.discount_rate = discount_rate or get_discount_rate('default')
        logger.info(f"Enhanced Financial Engine v24.1.0 initialized (discount rate: {self.discount_rate:.2%})")
    
    # ========================================================================
    # NEW FEATURE #1: PAYBACK PERIOD CALCULATION
    # ========================================================================
    
    def calculate_payback_period(
        self,
        initial_investment: float,
        annual_cashflows: List[float],
        discount_rate: Optional[float] = None
    ) -> PaybackPeriodResult:
        """
        Calculate both simple and discounted payback periods
        
        Payback Period: Time required to recover initial investment
        - Simple: Uses nominal cashflows (no discounting)
        - Discounted: Uses present value of cashflows
        
        Args:
            initial_investment: Initial capital outlay
            annual_cashflows: List of annual net cashflows
            discount_rate: Override default discount rate
            
        Returns:
            PaybackPeriodResult with both calculations
        """
        logger.info(f"Calculating payback period for investment: ₩{initial_investment:,.0f}")
        
        dr = discount_rate or self.discount_rate
        
        # Calculate simple payback
        simple_payback = self._calculate_simple_payback(
            initial_investment,
            annual_cashflows
        )
        
        # Calculate discounted payback
        discounted_payback = self._calculate_discounted_payback(
            initial_investment,
            annual_cashflows,
            dr
        )
        
        # Generate cumulative cashflow
        cumulative = self._calculate_cumulative_cashflow(
            initial_investment,
            annual_cashflows,
            dr
        )
        
        # Assess payback performance
        assessment = self._assess_payback_period(simple_payback, discounted_payback)
        
        # Generate recommendation
        recommendation = self._generate_payback_recommendation(
            simple_payback,
            discounted_payback,
            assessment
        )
        
        return PaybackPeriodResult(
            simple_payback_years=round(simple_payback, 2),
            discounted_payback_years=round(discounted_payback, 2),
            cumulative_cashflow=cumulative,
            assessment=assessment,
            recommendation=recommendation
        )
    
    def _calculate_simple_payback(
        self,
        initial_investment: float,
        annual_cashflows: List[float]
    ) -> float:
        """Calculate simple payback period (no discounting)"""
        cumulative = 0
        
        for year, cashflow in enumerate(annual_cashflows, start=1):
            cumulative += cashflow
            
            if cumulative >= initial_investment:
                # Interpolate to find exact payback time
                previous_cumulative = cumulative - cashflow
                remaining = initial_investment - previous_cumulative
                fraction = remaining / cashflow if cashflow > 0 else 0
                
                return (year - 1) + fraction
        
        # Not paid back within analysis period
        return float('inf') if cumulative < initial_investment else len(annual_cashflows)
    
    def _calculate_discounted_payback(
        self,
        initial_investment: float,
        annual_cashflows: List[float],
        discount_rate: float
    ) -> float:
        """Calculate discounted payback period"""
        cumulative_pv = 0
        
        for year, cashflow in enumerate(annual_cashflows, start=1):
            pv = cashflow / ((1 + discount_rate) ** year)
            cumulative_pv += pv
            
            if cumulative_pv >= initial_investment:
                # Interpolate to find exact payback time
                previous_cumulative = cumulative_pv - pv
                remaining = initial_investment - previous_cumulative
                fraction = remaining / pv if pv > 0 else 0
                
                return (year - 1) + fraction
        
        # Not paid back within analysis period
        return float('inf') if cumulative_pv < initial_investment else len(annual_cashflows)
    
    def _calculate_cumulative_cashflow(
        self,
        initial_investment: float,
        annual_cashflows: List[float],
        discount_rate: float
    ) -> List[float]:
        """Calculate cumulative cashflow over time"""
        cumulative = [-initial_investment]
        running_total = -initial_investment
        
        for year, cashflow in enumerate(annual_cashflows, start=1):
            pv = cashflow / ((1 + discount_rate) ** year)
            running_total += pv
            cumulative.append(running_total)
        
        return cumulative
    
    def _assess_payback_period(
        self,
        simple: float,
        discounted: float
    ) -> str:
        """Assess payback period performance"""
        thresholds = self.config['payback_period']
        
        # Use simple payback for assessment
        if simple == float('inf'):
            return 'POOR'
        elif simple <= thresholds['excellent_threshold']:
            return 'EXCELLENT'
        elif simple <= thresholds['target_simple']:
            return 'GOOD'
        elif simple <= thresholds['max_acceptable']:
            return 'ACCEPTABLE'
        else:
            return 'POOR'
    
    def _generate_payback_recommendation(
        self,
        simple: float,
        discounted: float,
        assessment: str
    ) -> str:
        """Generate payback recommendation"""
        if assessment == 'EXCELLENT':
            return f"Outstanding payback period ({simple:.1f} years). Strong investment candidate."
        elif assessment == 'GOOD':
            return f"Good payback period ({simple:.1f} years). Meets target criteria."
        elif assessment == 'ACCEPTABLE':
            return f"Acceptable payback period ({simple:.1f} years). Within acceptable range."
        else:
            return f"Payback period ({simple:.1f} years) exceeds target. Consider project optimization."
    
    # ========================================================================
    # NEW FEATURE #2: SENSITIVITY ANALYSIS
    # ========================================================================
    
    def perform_sensitivity_analysis(
        self,
        base_case: Dict[str, float],
        analysis_variables: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on key financial variables
        
        Tests how changes in input variables affect NPV
        
        Args:
            base_case: Base case financial parameters
            analysis_variables: Variables to analyze (defaults to config)
            
        Returns:
            Dict with sensitivity results and tornado chart data
        """
        logger.info("Performing sensitivity analysis")
        
        if analysis_variables is None:
            analysis_variables = self.config['sensitivity_parameters']['variables']
        
        variance_range = self.config['sensitivity_parameters']['variance_range']
        
        # Calculate base case NPV
        base_npv = self._calculate_npv(base_case)
        
        # Analyze each variable
        sensitivity_results = []
        
        for variable in analysis_variables:
            if variable not in base_case:
                continue
            
            result = self._analyze_variable_sensitivity(
                variable,
                base_case,
                variance_range,
                base_npv
            )
            sensitivity_results.append(result)
        
        # Sort by sensitivity index (most sensitive first)
        sensitivity_results.sort(key=lambda x: x.sensitivity_index, reverse=True)
        
        # Generate tornado chart data
        tornado_data = self._generate_tornado_chart_data(sensitivity_results[:5])
        
        return {
            'base_npv': base_npv,
            'sensitivity_results': sensitivity_results,
            'tornado_chart_data': tornado_data,
            'most_sensitive_variable': sensitivity_results[0].variable_name if sensitivity_results else None,
            'analysis_count': len(sensitivity_results)
        }
    
    def _analyze_variable_sensitivity(
        self,
        variable: str,
        base_case: Dict[str, float],
        variance_range: Dict[str, float],
        base_npv: float
    ) -> SensitivityResult:
        """Analyze sensitivity for a single variable"""
        base_value = base_case[variable]
        
        # Optimistic case (e.g., -15% cost or +15% revenue)
        optimistic_case = base_case.copy()
        if 'cost' in variable.lower():
            optimistic_case[variable] = base_value * (1 + variance_range['optimistic'])
        else:
            optimistic_case[variable] = base_value * (1 - variance_range['optimistic'])
        optimistic_npv = self._calculate_npv(optimistic_case)
        
        # Pessimistic case (e.g., +15% cost or -15% revenue)
        pessimistic_case = base_case.copy()
        if 'cost' in variable.lower():
            pessimistic_case[variable] = base_value * (1 + variance_range['pessimistic'])
        else:
            pessimistic_case[variable] = base_value * (1 - variance_range['pessimistic'])
        pessimistic_npv = self._calculate_npv(pessimistic_case)
        
        # Calculate sensitivity index
        npv_range = abs(optimistic_npv - pessimistic_npv)
        sensitivity_index = npv_range / abs(base_npv) if base_npv != 0 else 0
        
        return SensitivityResult(
            variable_name=variable,
            base_value=base_value,
            optimistic_value=optimistic_case[variable],
            pessimistic_value=pessimistic_case[variable],
            base_npv=base_npv,
            optimistic_npv=optimistic_npv,
            pessimistic_npv=pessimistic_npv,
            npv_range=npv_range,
            sensitivity_index=sensitivity_index
        )
    
    def _calculate_npv(self, params: Dict[str, float]) -> float:
        """Calculate NPV from parameters"""
        # Simplified NPV calculation
        investment = params.get('total_investment', params.get('construction_cost', 0) + 
                                params.get('land_acquisition_cost', 0))
        revenue = params.get('total_revenue', params.get('revenue_per_unit', 0) * 
                            params.get('total_units', 40))
        
        return revenue - investment
    
    def _generate_tornado_chart_data(
        self,
        top_results: List[SensitivityResult]
    ) -> Dict[str, Any]:
        """Generate data for tornado chart visualization"""
        chart_data = {
            'variables': [],
            'optimistic_delta': [],
            'pessimistic_delta': [],
            'base_npv': top_results[0].base_npv if top_results else 0
        }
        
        for result in top_results:
            chart_data['variables'].append(result.variable_name)
            chart_data['optimistic_delta'].append(
                result.optimistic_npv - result.base_npv
            )
            chart_data['pessimistic_delta'].append(
                result.pessimistic_npv - result.base_npv
            )
        
        return chart_data
    
    # ========================================================================
    # ENHANCED NPV/IRR CALCULATIONS
    # ========================================================================
    
    def calculate_npv(
        self,
        initial_investment: float,
        annual_cashflows: List[float],
        discount_rate: Optional[float] = None
    ) -> float:
        """
        Calculate Net Present Value
        
        Args:
            initial_investment: Initial capital outlay
            annual_cashflows: Annual net cashflows
            discount_rate: Override default discount rate
            
        Returns:
            NPV value
        """
        dr = discount_rate or self.discount_rate
        
        npv = -initial_investment
        
        for year, cashflow in enumerate(annual_cashflows, start=1):
            pv = cashflow / ((1 + dr) ** year)
            npv += pv
        
        return npv
    
    def calculate_irr(
        self,
        initial_investment: float,
        annual_cashflows: List[float],
        max_iterations: int = 100
    ) -> float:
        """
        Calculate Internal Rate of Return using Newton-Raphson method
        
        Args:
            initial_investment: Initial capital outlay
            annual_cashflows: Annual net cashflows
            max_iterations: Maximum iterations for convergence
            
        Returns:
            IRR (as decimal, e.g., 0.12 = 12%)
        """
        # Initial guess
        irr = 0.1
        
        for _ in range(max_iterations):
            npv = -initial_investment
            npv_derivative = 0
            
            for year, cashflow in enumerate(annual_cashflows, start=1):
                factor = (1 + irr) ** year
                npv += cashflow / factor
                npv_derivative -= year * cashflow / (factor * (1 + irr))
            
            if abs(npv) < 0.01:  # Converged
                return irr
            
            # Newton-Raphson update
            if npv_derivative != 0:
                irr = irr - npv / npv_derivative
            else:
                break
        
        return irr


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def assess_financial_performance(
    roi: float,
    irr: float,
    payback_years: float
) -> Dict[str, str]:
    """Assess overall financial performance"""
    roi_bench = get_roi_benchmark('target')
    irr_bench = get_irr_benchmark('target')
    payback_bench = FINANCIAL_CONFIG['payback_period']['target_simple']
    
    assessments = {
        'roi_assessment': 'EXCELLENT' if roi >= roi_bench * 1.5 else 'GOOD' if roi >= roi_bench else 'ACCEPTABLE' if roi >= roi_bench * 0.7 else 'POOR',
        'irr_assessment': 'EXCELLENT' if irr >= irr_bench * 1.5 else 'GOOD' if irr >= irr_bench else 'ACCEPTABLE' if irr >= irr_bench * 0.7 else 'POOR',
        'payback_assessment': 'EXCELLENT' if payback_years <= payback_bench * 0.7 else 'GOOD' if payback_years <= payback_bench else 'ACCEPTABLE' if payback_years <= payback_bench * 1.3 else 'POOR'
    }
    
    return assessments
