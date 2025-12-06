"""
ZeroSite Configuration Module

Loads configuration parameters from JSON files.
"""

import json
import os
from pathlib import Path


class FinancialParameters:
    """Financial parameters loader"""
    
    def __init__(self):
        config_dir = Path(__file__).parent
        config_path = config_dir / "financial_parameters.json"
        
        with open(config_path, "r", encoding="utf-8") as f:
            self._params = json.load(f)
    
    @property
    def discount_rate_public(self) -> float:
        """Public sector discount rate"""
        return self._params.get("discount_rate_public", 0.02)
    
    @property
    def discount_rate_private(self) -> float:
        """Private sector discount rate"""
        return self._params.get("discount_rate_private", 0.055)
    
    def get(self, key: str, default=None):
        """Get parameter by key"""
        return self._params.get(key, default)


# Global instance
financial_params = FinancialParameters()
