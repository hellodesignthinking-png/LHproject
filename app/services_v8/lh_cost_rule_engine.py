"""
ZeroSite Phase 8.7: LH Cost Rule Engine

Applies LH official construction cost rules and regulations to base construction costs.

Features:
    - Design fee calculation
    - Supervision fee calculation
    - General management cost
    - Site condition adjustments
    - Underground floor additions
    - Construction class differentials (A/B/C/D)
    - Regional labor cost adjustments
    - Seasonal adjustments
    - Special requirements (seismic, energy, barrier-free, smart home)
    - Contingency calculation
    - VAT application

Formula:
    LH Official Cost = (
        Base Construction Cost
        × Construction Class
        × Site Condition
        × Regional Labor
        × Seasonal
    ) + Design Fee + Supervision Fee + General Management
      + Underground Addition + Special Requirements
      + Contingency + VAT

Author: ZeroSite Development Team
Date: 2025-12-06
Version: 1.0
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class LHCostBreakdown:
    """LH cost calculation breakdown"""
    
    # Base costs
    base_construction_cost: float
    
    # Multipliers
    construction_class_coefficient: float
    site_condition_coefficient: float
    regional_labor_coefficient: float
    seasonal_coefficient: float
    
    # Adjusted construction cost
    adjusted_construction_cost: float
    
    # Additional costs
    design_fee: float
    supervision_fee: float
    general_management: float
    underground_addition: float
    special_requirements_cost: float
    
    # Subtotals
    subtotal_before_contingency: float
    contingency: float
    subtotal_before_vat: float
    vat: float
    
    # Final total
    total_lh_cost: float
    
    # Metadata
    construction_class: str
    site_condition_type: str
    region: str
    month: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "base_construction_cost": self.base_construction_cost,
            "multipliers": {
                "construction_class": self.construction_class_coefficient,
                "site_condition": self.site_condition_coefficient,
                "regional_labor": self.regional_labor_coefficient,
                "seasonal": self.seasonal_coefficient
            },
            "adjusted_construction_cost": self.adjusted_construction_cost,
            "additional_costs": {
                "design_fee": self.design_fee,
                "supervision_fee": self.supervision_fee,
                "general_management": self.general_management,
                "underground_addition": self.underground_addition,
                "special_requirements": self.special_requirements_cost
            },
            "subtotals": {
                "before_contingency": self.subtotal_before_contingency,
                "contingency": self.contingency,
                "before_vat": self.subtotal_before_vat,
                "vat": self.vat
            },
            "total_lh_cost": self.total_lh_cost,
            "metadata": {
                "construction_class": self.construction_class,
                "site_condition": self.site_condition_type,
                "region": self.region,
                "month": self.month
            }
        }


class LHCostRuleEngine:
    """
    LH Official Cost Rule Engine
    
    Applies LH construction cost rules and regulations to calculate
    official LH-compliant construction costs.
    
    Usage:
        engine = LHCostRuleEngine()
        lh_cost = engine.calculate_lh_cost(
            base_construction_cost=10_000_000_000,
            address="서울특별시 강남구",
            construction_class="B",
            underground_floors=2,
            site_condition="urban"
        )
    """
    
    def __init__(self, rules_path: Path = None):
        """
        Initialize LH Cost Rule Engine
        
        Args:
            rules_path: Path to LH cost rules JSON file
        """
        self.rules_path = rules_path or Path("./app/data/lh_cost_rules/lh_official_rules.json")
        self.rules = None
        self._load_rules()
    
    def _load_rules(self):
        """Load LH cost rules from JSON"""
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
        except FileNotFoundError:
            print(f"Warning: LH cost rules not found at {self.rules_path}")
            self.rules = None
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in LH cost rules: {e}")
            self.rules = None
    
    def _get_construction_class_coefficient(self, construction_class: str) -> float:
        """Get construction class coefficient"""
        if not self.rules:
            return 1.0
        
        classes = self.rules.get("construction_class", {}).get("classes", {})
        if construction_class not in classes:
            # Default to B (LH standard)
            construction_class = "B"
        
        return classes.get(construction_class, {}).get("coefficient", 1.0)
    
    def _get_site_condition_coefficient(self, site_condition: str) -> float:
        """Get site condition coefficient"""
        if not self.rules:
            return 1.0
        
        conditions = self.rules.get("site_conditions", {})
        return conditions.get(site_condition, {}).get("coefficient", 1.0)
    
    def _get_regional_labor_coefficient(self, address: str) -> float:
        """Get regional labor cost coefficient from address"""
        if not self.rules:
            return 1.0
        
        labor_costs = self.rules.get("regional_labor_cost", {})
        
        # Parse region from address
        if "서울" in address:
            return labor_costs.get("seoul", {}).get("coefficient", 1.08)
        elif "경기" in address:
            return labor_costs.get("gyeonggi", {}).get("coefficient", 1.03)
        elif any(city in address for city in ["인천", "부산", "대구", "광주", "대전", "울산"]):
            return labor_costs.get("metropolitan", {}).get("coefficient", 1.0)
        else:
            return labor_costs.get("provincial", {}).get("coefficient", 0.95)
    
    def _get_seasonal_coefficient(self, month: int = None) -> float:
        """Get seasonal construction cost coefficient"""
        if not self.rules:
            return 1.0
        
        if month is None:
            month = datetime.now().month
        
        seasonal = self.rules.get("seasonal_adjustment", {})
        
        if month in seasonal.get("winter", {}).get("months", []):
            return seasonal.get("winter", {}).get("coefficient", 1.05)
        elif month in seasonal.get("summer", {}).get("months", []):
            return seasonal.get("summer", {}).get("coefficient", 1.02)
        else:
            return seasonal.get("spring_fall", {}).get("coefficient", 1.0)
    
    def _calculate_design_fee(self, construction_cost: float, rate: str = "standard") -> float:
        """Calculate design fee"""
        if not self.rules:
            return construction_cost * 0.10
        
        design_rules = self.rules.get("base_rules", {}).get("design_fee", {})
        rate_value = design_rules.get("rate_range", {}).get(rate, 0.10)
        
        return construction_cost * rate_value
    
    def _calculate_supervision_fee(self, construction_cost: float, rate: str = "standard") -> float:
        """Calculate supervision fee"""
        if not self.rules:
            return construction_cost * 0.04
        
        supervision_rules = self.rules.get("base_rules", {}).get("supervision_fee", {})
        rate_value = supervision_rules.get("rate_range", {}).get(rate, 0.04)
        
        return construction_cost * rate_value
    
    def _calculate_general_management(self, construction_cost: float) -> float:
        """Calculate general management cost"""
        if not self.rules:
            return construction_cost * 0.05
        
        rate = self.rules.get("base_rules", {}).get("general_management", {}).get("rate", 0.05)
        return construction_cost * rate
    
    def _calculate_underground_addition(
        self,
        total_floor_area: float,
        underground_floors: int,
        underground_floor_area_per_floor: float = None
    ) -> float:
        """Calculate underground floor construction cost addition"""
        if underground_floors <= 0:
            return 0
        
        if not self.rules:
            return 0
        
        underground_rules = self.rules.get("underground_floors", {})
        
        # If no specific floor area provided, estimate as 70% of total floor area
        if underground_floor_area_per_floor is None:
            underground_floor_area_per_floor = total_floor_area * 0.7 / max(underground_floors, 1)
        
        # Calculate cost by depth
        by_depth = underground_rules.get("by_depth", {})
        total_cost = 0
        
        for floor_num in range(1, underground_floors + 1):
            if floor_num == 1:
                cost_per_m2 = by_depth.get("B1", 180000)
            elif floor_num == 2:
                cost_per_m2 = by_depth.get("B2", 220000)
            elif floor_num == 3:
                cost_per_m2 = by_depth.get("B3", 280000)
            else:
                cost_per_m2 = by_depth.get("B4_plus", 350000)
            
            total_cost += underground_floor_area_per_floor * cost_per_m2
        
        return total_cost
    
    def _calculate_special_requirements(
        self,
        construction_cost: float,
        requirements: List[str] = None
    ) -> float:
        """Calculate special requirements cost"""
        if not requirements:
            # Default requirements for LH public housing
            requirements = ["seismic_design", "energy_efficiency", "barrier_free"]
        
        if not self.rules:
            return construction_cost * 0.10
        
        special_rules = self.rules.get("special_requirements", {})
        total_addition = 0
        
        for req in requirements:
            if req in special_rules:
                rate = special_rules[req].get("cost_addition_rate", 0)
                total_addition += rate
        
        return construction_cost * total_addition
    
    def _calculate_contingency(self, total_cost: float, rate: str = "standard") -> float:
        """Calculate contingency"""
        if not self.rules:
            return total_cost * 0.10
        
        contingency_rules = self.rules.get("base_rules", {}).get("contingency", {})
        rate_value = contingency_rules.get("rate_range", {}).get(rate, 0.10)
        
        return total_cost * rate_value
    
    def _calculate_vat(self, total_cost: float) -> float:
        """Calculate VAT"""
        if not self.rules:
            return total_cost * 0.10
        
        vat_rate = self.rules.get("base_rules", {}).get("vat", {}).get("rate", 0.10)
        return total_cost * vat_rate
    
    def calculate_lh_cost(
        self,
        base_construction_cost: float,
        address: str,
        construction_class: str = "B",
        site_condition: str = "suburban",
        underground_floors: int = 0,
        total_floor_area: float = None,
        special_requirements: List[str] = None,
        month: int = None
    ) -> LHCostBreakdown:
        """
        Calculate LH official construction cost
        
        Args:
            base_construction_cost: Base construction cost (원)
            address: Project address (for regional labor cost)
            construction_class: A/B/C/D (default: B - LH standard)
            site_condition: urban/suburban/rural/island (default: suburban)
            underground_floors: Number of underground floors (default: 0)
            total_floor_area: Total floor area in ㎡ (for underground calculation)
            special_requirements: List of special requirements (default: LH standard)
            month: Month of construction (for seasonal adjustment)
        
        Returns:
            LHCostBreakdown with detailed cost breakdown
        """
        # Get multipliers
        construction_class_coef = self._get_construction_class_coefficient(construction_class)
        site_condition_coef = self._get_site_condition_coefficient(site_condition)
        regional_labor_coef = self._get_regional_labor_coefficient(address)
        seasonal_coef = self._get_seasonal_coefficient(month)
        
        # Adjusted construction cost
        adjusted_construction = (
            base_construction_cost
            * construction_class_coef
            * site_condition_coef
            * regional_labor_coef
            * seasonal_coef
        )
        
        # Additional costs
        design_fee = self._calculate_design_fee(adjusted_construction)
        supervision_fee = self._calculate_supervision_fee(adjusted_construction)
        general_management = self._calculate_general_management(adjusted_construction)
        
        underground_addition = 0
        if underground_floors > 0 and total_floor_area:
            underground_addition = self._calculate_underground_addition(
                total_floor_area, underground_floors
            )
        
        special_requirements_cost = self._calculate_special_requirements(
            adjusted_construction, special_requirements
        )
        
        # Subtotal before contingency
        subtotal = (
            adjusted_construction
            + design_fee
            + supervision_fee
            + general_management
            + underground_addition
            + special_requirements_cost
        )
        
        # Contingency
        contingency = self._calculate_contingency(subtotal)
        subtotal_before_vat = subtotal + contingency
        
        # VAT
        vat = self._calculate_vat(subtotal_before_vat)
        
        # Total LH cost
        total_lh_cost = subtotal_before_vat + vat
        
        # Create breakdown
        return LHCostBreakdown(
            base_construction_cost=base_construction_cost,
            construction_class_coefficient=construction_class_coef,
            site_condition_coefficient=site_condition_coef,
            regional_labor_coefficient=regional_labor_coef,
            seasonal_coefficient=seasonal_coef,
            adjusted_construction_cost=adjusted_construction,
            design_fee=design_fee,
            supervision_fee=supervision_fee,
            general_management=general_management,
            underground_addition=underground_addition,
            special_requirements_cost=special_requirements_cost,
            subtotal_before_contingency=subtotal,
            contingency=contingency,
            subtotal_before_vat=subtotal_before_vat,
            vat=vat,
            total_lh_cost=total_lh_cost,
            construction_class=construction_class,
            site_condition_type=site_condition,
            region=address,
            month=month or datetime.now().month
        )


# Convenience function
def calculate_lh_official_cost(
    base_construction_cost: float,
    address: str,
    **kwargs
) -> LHCostBreakdown:
    """
    Convenience function to calculate LH official cost
    
    Usage:
        lh_cost = calculate_lh_official_cost(
            base_construction_cost=10_000_000_000,
            address="서울특별시 강남구",
            construction_class="B"
        )
    """
    engine = LHCostRuleEngine()
    return engine.calculate_lh_cost(base_construction_cost, address, **kwargs)
