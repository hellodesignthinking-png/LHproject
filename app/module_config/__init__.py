"""
ZeroSite Module Configuration Package
Defines modular architecture for v3.3
"""

# Import module configuration
from .module_config import (
    MODULE_LAYER,
    REPORT_TYPE,
    MODULE_DEPENDENCIES,
    LAYER_PRINCIPLES,
    get_module_layer,
    get_report_dependencies,
    validate_module_interaction
)

__all__ = [
    'MODULE_LAYER',
    'REPORT_TYPE',
    'MODULE_DEPENDENCIES',
    'LAYER_PRINCIPLES',
    'get_module_layer',
    'get_report_dependencies',
    'validate_module_interaction'
]
