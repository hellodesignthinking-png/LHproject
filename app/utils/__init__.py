"""
ZeroSite v22 Utility Modules
=============================

Comprehensive utilities for report generation.
"""

from .market_data_processor import (
    MarketDataProcessor,
    normalize_region,
    get_market_data,
    estimate_price
)

from .zoning_classifier import (
    ZoningClassifier,
    classify_zoning,
    get_base_far
)

from .risk_matrix_formatter import (
    RiskMatrixFormatter,
    format_risk_matrix,
    calculate_total_risk,
    generate_risk_narrative,
    get_default_risks
)

from .alias_generator import (
    AliasGenerator,
    generate_aliases,
    safe_format
)

__all__ = [
    # Market Data
    'MarketDataProcessor',
    'normalize_region',
    'get_market_data',
    'estimate_price',
    
    # Zoning
    'ZoningClassifier',
    'classify_zoning',
    'get_base_far',
    
    # Risk
    'RiskMatrixFormatter',
    'format_risk_matrix',
    'calculate_total_risk',
    'generate_risk_narrative',
    'get_default_risks',
    
    # Aliases
    'AliasGenerator',
    'generate_aliases',
    'safe_format',
]
