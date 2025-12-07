"""
ZeroSite MVP Configuration
==========================

Externalized configuration for building scale and unit calculations.
All values can be adjusted without modifying core logic.

Author: ZeroSite Development Team
Date: 2025-12-06
Version: MVP 1.0
"""

from typing import Dict
from pydantic import BaseModel, Field


class BuildingCalculationConfig(BaseModel):
    """Building scale calculation parameters"""
    
    # Unit Area Settings
    default_unit_area: float = Field(
        default=60.0,
        description="Default unit area in m² (평균 세대 면적)"
    )
    min_unit_area: float = Field(
        default=45.0,
        description="Minimum unit area in m²"
    )
    max_unit_area: float = Field(
        default=85.0,
        description="Maximum unit area in m²"
    )
    
    # GFA Distribution
    residential_ratio: float = Field(
        default=0.85,
        description="Residential area ratio (주거 비율)"
    )
    commercial_ratio: float = Field(
        default=0.15,
        description="Commercial/common area ratio (부대시설 비율)"
    )
    
    # Parking Standards
    parking_ratios: Dict[str, float] = Field(
        default={
            "제1종일반주거지역": 0.8,
            "제2종일반주거지역": 1.0,
            "제3종일반주거지역": 1.0,
            "준주거지역": 1.2,
            "중심상업지역": 1.5,
            "일반상업지역": 1.3,
            "근린상업지역": 1.2,
            "준공업지역": 1.1,
            "default": 1.0
        },
        description="Parking spaces per unit by zone type"
    )
    
    # Floor Limits
    max_floors_by_zone: Dict[str, int] = Field(
        default={
            "제1종일반주거지역": 4,
            "제2종일반주거지역": 7,
            "제3종일반주거지역": 15,
            "준주거지역": 20,
            "중심상업지역": 30,
            "일반상업지역": 20,
            "근린상업지역": 15,
            "준공업지역": 15,
            "default": 20
        },
        description="Maximum floors by zone type"
    )
    
    # Minimum Requirements
    min_units: int = Field(
        default=10,
        description="Minimum number of units for LH eligibility"
    )
    min_floors: int = Field(
        default=2,
        description="Minimum number of floors"
    )
    
    # Unit Type Mix
    unit_type_distribution: Dict[str, float] = Field(
        default={
            "59㎡": 0.6,  # 60%
            "74㎡": 0.3,  # 30%
            "84㎡": 0.1   # 10%
        },
        description="Default unit type distribution"
    )


class MVPConfig(BaseModel):
    """Complete MVP configuration"""
    
    building: BuildingCalculationConfig = Field(
        default_factory=BuildingCalculationConfig,
        description="Building calculation settings"
    )
    
    # API Settings
    kakao_api_timeout: int = Field(
        default=5,
        description="Kakao API timeout in seconds"
    )
    nsdi_api_timeout: int = Field(
        default=10,
        description="NSDI API timeout in seconds"
    )
    
    # Report Settings
    report_generation_timeout: int = Field(
        default=300,
        description="Report generation timeout in seconds (5 minutes)"
    )
    default_report_pages: int = Field(
        default=50,
        description="Default number of pages in report"
    )
    
    # Performance Settings
    enable_caching: bool = Field(
        default=True,
        description="Enable result caching"
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds"
    )


# Global configuration instance
_mvp_config: MVPConfig = None


def get_mvp_config() -> MVPConfig:
    """Get or create MVP configuration singleton"""
    global _mvp_config
    if _mvp_config is None:
        _mvp_config = MVPConfig()
    return _mvp_config


def update_mvp_config(**kwargs) -> MVPConfig:
    """
    Update MVP configuration
    
    Example:
        >>> config = update_mvp_config(
        ...     building__default_unit_area=50.0,
        ...     building__residential_ratio=0.80
        ... )
    """
    global _mvp_config
    if _mvp_config is None:
        _mvp_config = MVPConfig()
    
    # Update nested fields
    for key, value in kwargs.items():
        if '__' in key:
            # Handle nested updates (e.g., building__default_unit_area)
            parts = key.split('__')
            obj = _mvp_config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
        else:
            setattr(_mvp_config, key, value)
    
    return _mvp_config


# Convenience functions
def get_default_unit_area() -> float:
    """Get default unit area"""
    return get_mvp_config().building.default_unit_area


def get_parking_ratio(zone_type: str) -> float:
    """Get parking ratio for zone type"""
    config = get_mvp_config()
    return config.building.parking_ratios.get(
        zone_type,
        config.building.parking_ratios["default"]
    )


def get_max_floors(zone_type: str) -> int:
    """Get maximum floors for zone type"""
    config = get_mvp_config()
    return config.building.max_floors_by_zone.get(
        zone_type,
        config.building.max_floors_by_zone["default"]
    )


def get_residential_ratio() -> float:
    """Get residential area ratio"""
    return get_mvp_config().building.residential_ratio
