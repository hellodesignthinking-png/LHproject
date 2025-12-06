"""
ZeroSite Phase 2.5: Financial Parameters Loader

Loads financial parameters from JSON configuration file.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

import json
from pathlib import Path
from typing import Dict, Any

# Configuration file path
CONFIG_FILE = Path(__file__).parent / "financial_parameters.json"


def load_financial_parameters() -> Dict[str, Any]:
    """
    Load financial parameters from JSON configuration
    
    Returns:
        Dictionary with financial parameters:
        - discount_rate_public: Public sector discount rate (default: 0.02)
        - discount_rate_private: Private sector discount rate (default: 0.055)
        - discount_rates: Detailed rate information
    
    Example:
        >>> params = load_financial_parameters()
        >>> print(params['discount_rate_public'])
        0.02
    """
    default_params = {
        'discount_rate_public': 0.02,
        'discount_rate_private': 0.055,
        'discount_rates': {
            'public': {
                'rate': 0.02,
                'description': 'Public sector discount rate (2%)'
            },
            'private': {
                'rate': 0.055,
                'description': 'Private sector discount rate (5.5%)'
            }
        }
    }
    
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                params = json.load(f)
                return params
        else:
            print(f"Warning: {CONFIG_FILE} not found, using defaults")
            return default_params
    except Exception as e:
        print(f"Error loading financial parameters: {e}, using defaults")
        return default_params


def get_discount_rate(sector: str = 'public') -> float:
    """
    Get discount rate for specific sector
    
    Args:
        sector: 'public' or 'private'
    
    Returns:
        Discount rate as float (e.g., 0.02 for 2%)
    
    Example:
        >>> rate = get_discount_rate('public')
        >>> print(rate)
        0.02
    """
    params = load_financial_parameters()
    
    if sector == 'public':
        return params.get('discount_rate_public', 0.02)
    elif sector == 'private':
        return params.get('discount_rate_private', 0.055)
    else:
        raise ValueError(f"Unknown sector: {sector}. Use 'public' or 'private'")


# Convenience constants
DISCOUNT_RATE_PUBLIC = 0.02
DISCOUNT_RATE_PRIVATE = 0.055
