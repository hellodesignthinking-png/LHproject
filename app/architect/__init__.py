"""
ZeroSite Phase 11: Architecture Design Automation Module

Automated building design system for LH public housing projects.

Features:
- 3 design alternatives (Stable/Standard/Profit)
- LH housing standards (22/30/42/50/58㎡)
- Y/N/A/S/M supply types
- Automatic parking calculation
- Layout generation
- Design comparison

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

from .models import (
    BuildingDesign,
    DesignStrategy,
    SupplyType,
    UnitType,
    BuildableVolume,
    ParkingRequirement,
    GeometryLayout,
    DesignMetrics,
    DesignComparisonResult,
    LH_UNIT_SIZES,
    LH_DISTRIBUTION_RATIOS,
)

from .design_generator import DesignGenerator
from .zoning_rules import ZoningRuleEngine
from .lh_unit_distribution import LHUnitDistributor, quick_distribute
from .parking_calculator import ParkingCalculator
from .geometry_engine import GeometryEngine

__version__ = "11.0.0"
__author__ = "ZeroSite Development Team + GenSpark AI"

__all__ = [
    # Main generator
    "DesignGenerator",
    
    # Engines
    "ZoningRuleEngine",
    "LHUnitDistributor",
    "ParkingCalculator",
    "GeometryEngine",
    
    # Models
    "BuildingDesign",
    "DesignStrategy",
    "SupplyType",
    "UnitType",
    "BuildableVolume",
    "ParkingRequirement",
    "GeometryLayout",
    "DesignMetrics",
    "DesignComparisonResult",
    
    # Constants
    "LH_UNIT_SIZES",
    "LH_DISTRIBUTION_RATIOS",
    
    # Utilities
    "quick_distribute",
]
