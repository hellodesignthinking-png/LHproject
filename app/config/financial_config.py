"""
ZeroSite v24.1 - Financial Configuration

NEW FEATURES (v24.1 GAP #5):
- Externalized financial parameters (discount rate, escalation rates, etc.)
- Configurable assumptions for sensitivity analysis
- Industry-standard benchmarks

Priority: 🟡 MEDIUM (v24.1 GAP Closing)
Specification: docs/ZEROSITE_V24.1_GAP_CLOSING_PLAN.md

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, Any

# ============================================================================
# DISCOUNT RATE CONFIGURATION
# ============================================================================

DISCOUNT_RATE = {
    'default': 0.05,  # 5% (standard commercial real estate)
    'conservative': 0.07,  # 7% (risk-averse investors)
    'aggressive': 0.03,  # 3% (patient capital, long-term)
    'government': 0.045,  # 4.5% (public housing projects)
    'description': 'Annual discount rate for NPV calculations'
}

# ============================================================================
# ESCALATION RATES
# ============================================================================

ESCALATION_RATES = {
    'construction_cost': 0.03,  # 3% annual construction cost inflation
    'land_price': 0.04,  # 4% annual land price appreciation
    'revenue': 0.025,  # 2.5% annual revenue growth
    'operating_cost': 0.028,  # 2.8% annual operating cost inflation
    'description': 'Annual escalation rates for various cost/revenue categories'
}

# ============================================================================
# PAYBACK PERIOD PARAMETERS
# ============================================================================

PAYBACK_PERIOD = {
    'target_simple': 7.0,  # Target simple payback: 7 years
    'target_discounted': 10.0,  # Target discounted payback: 10 years
    'max_acceptable': 15.0,  # Maximum acceptable: 15 years
    'excellent_threshold': 5.0,  # Excellent: < 5 years
    'description': 'Payback period thresholds (years)'
}

# ============================================================================
# IRR BENCHMARKS
# ============================================================================

IRR_BENCHMARKS = {
    'minimum_acceptable': 8.0,  # Minimum acceptable IRR: 8%
    'target': 12.0,  # Target IRR: 12%
    'excellent': 18.0,  # Excellent IRR: 18%
    'world_class': 25.0,  # World-class IRR: 25%
    'description': 'IRR performance benchmarks (%)'
}

# ============================================================================
# ROI BENCHMARKS
# ============================================================================

ROI_BENCHMARKS = {
    'minimum_acceptable': 10.0,  # Minimum acceptable ROI: 10%
    'target': 15.0,  # Target ROI: 15%
    'excellent': 25.0,  # Excellent ROI: 25%
    'world_class': 40.0,  # World-class ROI: 40%
    'description': 'ROI performance benchmarks (%)'
}

# ============================================================================
# SENSITIVITY ANALYSIS PARAMETERS
# ============================================================================

SENSITIVITY_PARAMETERS = {
    'variables': [
        'construction_cost',
        'land_acquisition_cost',
        'revenue_per_unit',
        'absorption_rate',
        'interest_rate'
    ],
    'variance_range': {
        'optimistic': -0.15,  # -15% (best case)
        'base': 0.0,  # 0% (base case)
        'pessimistic': 0.15  # +15% (worst case)
    },
    'tornado_chart_variables': 5,  # Show top 5 most sensitive variables
    'description': 'Parameters for sensitivity analysis'
}

# ============================================================================
# FINANCING PARAMETERS
# ============================================================================

FINANCING = {
    'debt_equity_ratio': {
        'conservative': 0.5,  # 50% debt, 50% equity
        'moderate': 0.7,  # 70% debt, 30% equity
        'aggressive': 0.8  # 80% debt, 20% equity
    },
    'interest_rate': {
        'low': 0.035,  # 3.5% (favorable market)
        'medium': 0.045,  # 4.5% (typical market)
        'high': 0.065  # 6.5% (tight market)
    },
    'loan_term_years': {
        'short': 5,
        'medium': 10,
        'long': 15
    },
    'description': 'Debt financing parameters'
}

# ============================================================================
# COST ASSUMPTIONS
# ============================================================================

COST_ASSUMPTIONS = {
    'construction_cost_per_sqm': {
        'low': 1_500_000,  # ₩1.5M/㎡ (basic quality)
        'medium': 1_850_000,  # ₩1.85M/㎡ (standard quality)
        'high': 2_300_000  # ₩2.3M/㎡ (premium quality)
    },
    'land_price_per_sqm': {
        'low': 2_000_000,  # ₩2M/㎡ (suburban)
        'medium': 3_000_000,  # ₩3M/㎡ (urban)
        'high': 5_000_000  # ₩5M/㎡ (premium location)
    },
    'soft_costs_percentage': 0.15,  # 15% of hard costs
    'contingency_percentage': 0.08,  # 8% contingency
    'description': 'Construction and land cost assumptions'
}

# ============================================================================
# REVENUE ASSUMPTIONS
# ============================================================================

REVENUE_ASSUMPTIONS = {
    'revenue_per_unit': {
        'small': 200_000_000,  # ₩200M (< 50㎡)
        'medium': 300_000_000,  # ₩300M (50-80㎡)
        'large': 450_000_000  # ₩450M (> 80㎡)
    },
    'absorption_rate': {
        'slow': 0.05,  # 5% per month
        'normal': 0.10,  # 10% per month
        'fast': 0.15  # 15% per month
    },
    'pricing_premium': {
        'none': 1.0,  # No premium
        'location': 1.05,  # +5% for location
        'design': 1.03,  # +3% for design
        'sustainability': 1.04  # +4% for green features
    },
    'description': 'Revenue and sales assumptions'
}

# ============================================================================
# OPERATING PARAMETERS
# ============================================================================

OPERATING_PARAMETERS = {
    'holding_period_years': 5,  # Typical holding period
    'exit_cap_rate': 0.055,  # 5.5% exit cap rate
    'annual_operating_cost_per_sqm': 50_000,  # ₩50K/㎡/year
    'vacancy_rate': 0.05,  # 5% vacancy assumption
    'management_fee_percentage': 0.03,  # 3% of revenue
    'description': 'Operating and exit assumptions'
}

# ============================================================================
# CONSOLIDATED CONFIGURATION
# ============================================================================

FINANCIAL_CONFIG = {
    'discount_rate': DISCOUNT_RATE,
    'escalation_rates': ESCALATION_RATES,
    'payback_period': PAYBACK_PERIOD,
    'irr_benchmarks': IRR_BENCHMARKS,
    'roi_benchmarks': ROI_BENCHMARKS,
    'sensitivity_parameters': SENSITIVITY_PARAMETERS,
    'financing': FINANCING,
    'cost_assumptions': COST_ASSUMPTIONS,
    'revenue_assumptions': REVENUE_ASSUMPTIONS,
    'operating_parameters': OPERATING_PARAMETERS,
    'version': '24.1.0',
    'last_updated': '2025-12-12'
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_discount_rate(scenario: str = 'default') -> float:
    """Get discount rate for specified scenario"""
    return DISCOUNT_RATE.get(scenario, DISCOUNT_RATE['default'])


def get_irr_benchmark(level: str = 'target') -> float:
    """Get IRR benchmark for specified level"""
    return IRR_BENCHMARKS.get(level, IRR_BENCHMARKS['target'])


def get_roi_benchmark(level: str = 'target') -> float:
    """Get ROI benchmark for specified level"""
    return ROI_BENCHMARKS.get(level, ROI_BENCHMARKS['target'])


def get_sensitivity_range(scenario: str = 'base') -> float:
    """Get sensitivity variance for scenario"""
    return SENSITIVITY_PARAMETERS['variance_range'].get(scenario, 0.0)


def get_config_summary() -> Dict[str, Any]:
    """Get summary of financial configuration"""
    return {
        'discount_rate_default': DISCOUNT_RATE['default'],
        'target_irr': IRR_BENCHMARKS['target'],
        'target_roi': ROI_BENCHMARKS['target'],
        'target_payback': PAYBACK_PERIOD['target_simple'],
        'construction_cost_medium': COST_ASSUMPTIONS['construction_cost_per_sqm']['medium'],
        'sensitivity_variables': len(SENSITIVITY_PARAMETERS['variables'])
    }
