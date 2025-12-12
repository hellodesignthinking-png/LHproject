"""
ZeroSite v24 - Capacity Engine (규모검토 엔진)

Building capacity simulation engine for automatic calculation of:
- Maximum floors (층수)
- Unit count (세대수)
- Parking spaces (주차대수)
- Daylight regulation compliance (일조권)

Priority: 🔴 CRITICAL (v24 Core Feature)
Specification: docs/CAPACITY_ENGINE_SPEC.md

Author: ZeroSite Development Team
Version: 24.0.0
Date: 2025-12-12
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import math

from .base_engine import BaseEngine

logger = logging.getLogger(__name__)


@dataclass
class FloorCalculation:
    """Floor calculation result"""
    max_floors: int
    max_floors_by_height: int
    max_floors_by_far: int
    max_floors_by_daylight: int
    limiting_factor: str  # 'height', 'far', or 'daylight'
    building_height: float  # in meters


@dataclass
class UnitCalculation:
    """Unit count calculation result"""
    total_units: int
    units_by_type: Dict[str, int]
    residential_area: float
    common_area: float
    avg_unit_area: float


@dataclass
class ParkingCalculation:
    """Parking space calculation result"""
    required_spaces: int
    parking_ratio: float
    zoning_type: str
    calculation: str


@dataclass
class DaylightValidation:
    """Daylight regulation validation result"""
    compliant: bool
    required_setback: float
    actual_setback: float
    shortfall: float
    regulation: str
    status: str


class CapacityEngine(BaseEngine):
    """
    Capacity Engine for ZeroSite v24
    
    Automatically calculates building capacity based on:
    - Land area and zoning regulations
    - FAR (Floor Area Ratio) limits
    - BCR (Building Coverage Ratio) limits
    - Height restrictions
    - Daylight regulations
    """
    
    # Parking ratios by zoning type (Seoul standards)
    PARKING_RATIOS = {
        '제1종일반주거': 0.7,
        '제2종일반주거': 0.8,
        '제3종일반주거': 1.0,
        '준주거': 1.0,
    }
    
    def __init__(self):
        """Initialize Capacity Engine"""
        super().__init__(engine_name="CapacityEngine", version="24.0.0")
        self.logger.info("Capacity Engine v24.0.0 initialized (CRITICAL)")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process building capacity calculation request.
        
        Args:
            input_data: {
                'land_area_sqm': float - Land area in square meters
                'zoning_type': str - Zoning classification
                'far_limit': float - Floor Area Ratio limit (%)
                'bcr_limit': float - Building Coverage Ratio limit (%)
                'height_limit': float - Maximum building height (m)
                'land_depth_m': float - Land depth (north direction, m)
                'unit_types': Dict[str, float] - Unit type distribution
                'floor_height': float - Floor height (m, default: 3.0)
                'efficiency_ratio': float - Residential efficiency (default: 0.75)
                'common_area_ratio': float - Common area ratio (default: 0.25)
            }
            
        Returns:
            Standardized result with capacity analysis
        """
        self.log_processing(input_data)
        
        # Validate input
        required_fields = [
            'land_area_sqm', 'zoning_type', 'far_limit', 'bcr_limit',
            'height_limit', 'land_depth_m', 'unit_types'
        ]
        if not self.validate_input(input_data, required_fields):
            return self.create_result(
                success=False,
                error=f"Missing required fields: {required_fields}"
            )
        
        try:
            # Extract parameters with defaults
            land_area_sqm = float(input_data['land_area_sqm'])
            zoning_type = input_data['zoning_type']
            far_limit = float(input_data['far_limit'])
            bcr_limit = float(input_data['bcr_limit'])
            height_limit = float(input_data['height_limit'])
            land_depth_m = float(input_data['land_depth_m'])
            unit_types = input_data['unit_types']
            
            floor_height = float(input_data.get('floor_height', 3.0))
            efficiency_ratio = float(input_data.get('efficiency_ratio', 0.75))
            common_area_ratio = float(input_data.get('common_area_ratio', 0.25))
            
            # Calculate maximum floors
            floor_calc = self.calculate_max_floors(
                land_area_sqm=land_area_sqm,
                zoning_type=zoning_type,
                far_limit=far_limit,
                bcr_limit=bcr_limit,
                height_limit=height_limit,
                land_depth_m=land_depth_m,
                floor_height=floor_height
            )
            
            # Calculate total floor area
            building_footprint = land_area_sqm * (bcr_limit / 100)
            total_floor_area = building_footprint * floor_calc.max_floors
            
            # Calculate unit count
            unit_calc = self.calculate_unit_count(
                total_floor_area=total_floor_area,
                unit_types=unit_types,
                efficiency_ratio=efficiency_ratio,
                common_area_ratio=common_area_ratio
            )
            
            # Calculate parking spaces
            parking_calc = self.calculate_parking_spaces(
                total_units=unit_calc.total_units,
                zoning_type=zoning_type
            )
            
            # Validate daylight compliance
            daylight_val = self.validate_daylight_compliance(
                zoning_type=zoning_type,
                building_height=floor_calc.building_height,
                setback_distance=land_depth_m
            )
            
            # Build result
            capacity_data = {
                'floors': {
                    'max_floors': floor_calc.max_floors,
                    'max_floors_by_height': floor_calc.max_floors_by_height,
                    'max_floors_by_far': floor_calc.max_floors_by_far,
                    'max_floors_by_daylight': floor_calc.max_floors_by_daylight,
                    'limiting_factor': floor_calc.limiting_factor,
                    'building_height': round(floor_calc.building_height, 2)
                },
                'units': {
                    'total_units': unit_calc.total_units,
                    'units_by_type': unit_calc.units_by_type,
                    'residential_area': round(unit_calc.residential_area, 2),
                    'common_area': round(unit_calc.common_area, 2),
                    'avg_unit_area': round(unit_calc.avg_unit_area, 2)
                },
                'parking': {
                    'required_spaces': parking_calc.required_spaces,
                    'parking_ratio': parking_calc.parking_ratio,
                    'zoning_type': parking_calc.zoning_type,
                    'calculation': parking_calc.calculation
                },
                'daylight': {
                    'compliant': daylight_val.compliant,
                    'required_setback': round(daylight_val.required_setback, 2),
                    'actual_setback': round(daylight_val.actual_setback, 2),
                    'shortfall': round(daylight_val.shortfall, 2),
                    'regulation': daylight_val.regulation,
                    'status': daylight_val.status
                },
                'summary': {
                    'land_area': round(land_area_sqm, 2),
                    'building_footprint': round(building_footprint, 2),
                    'total_floor_area': round(total_floor_area, 2),
                    'far_actual': round((total_floor_area / land_area_sqm) * 100, 2),
                    'bcr_actual': round(bcr_limit, 2)
                }
            }
            
            return self.create_result(success=True, data=capacity_data)
            
        except Exception as e:
            self.logger.error(f"Capacity calculation error: {str(e)}")
            return self.create_result(
                success=False,
                error=f"Capacity calculation failed: {str(e)}"
            )
    
    def calculate_max_floors(
        self,
        land_area_sqm: float,
        zoning_type: str,
        far_limit: float,
        bcr_limit: float,
        height_limit: float,
        land_depth_m: float,
        floor_height: float = 3.0
    ) -> FloorCalculation:
        """
        Calculate maximum number of floors based on multiple constraints.
        
        Args:
            land_area_sqm: Land area in square meters
            zoning_type: Zoning classification
            far_limit: Floor Area Ratio limit (%)
            bcr_limit: Building Coverage Ratio limit (%)
            height_limit: Maximum building height (m)
            land_depth_m: Land depth in north direction (m)
            floor_height: Floor height (m)
            
        Returns:
            FloorCalculation object with detailed calculation
        """
        
        # A. Height limit constraint
        max_floors_by_height = int(height_limit / floor_height)
        
        # B. FAR limit constraint
        # Total floor area = land area × FAR
        # Building footprint = land area × BCR
        # Max floors = Total floor area / Building footprint
        building_footprint = land_area_sqm * (bcr_limit / 100)
        total_floor_area_limit = land_area_sqm * (far_limit / 100)
        
        if building_footprint > 0:
            max_floors_by_far = int(total_floor_area_limit / building_footprint)
        else:
            max_floors_by_far = 0
        
        # C. Daylight regulation constraint
        max_floors_by_daylight = self._calculate_daylight_limit(
            zoning_type=zoning_type,
            land_depth_m=land_depth_m,
            floor_height=floor_height
        )
        
        # D. Determine limiting factor
        constraints = {
            'height': max_floors_by_height,
            'far': max_floors_by_far,
            'daylight': max_floors_by_daylight
        }
        
        limiting_factor = min(constraints, key=constraints.get)
        max_floors = constraints[limiting_factor]
        
        # Calculate actual building height
        building_height = max_floors * floor_height
        
        self.logger.info(
            f"Floor calculation: height={max_floors_by_height}, "
            f"far={max_floors_by_far}, daylight={max_floors_by_daylight}, "
            f"limiting={limiting_factor} → {max_floors} floors"
        )
        
        return FloorCalculation(
            max_floors=max_floors,
            max_floors_by_height=max_floors_by_height,
            max_floors_by_far=max_floors_by_far,
            max_floors_by_daylight=max_floors_by_daylight,
            limiting_factor=limiting_factor,
            building_height=building_height
        )
    
    def _calculate_daylight_limit(
        self,
        zoning_type: str,
        land_depth_m: float,
        floor_height: float
    ) -> int:
        """
        Calculate maximum floors based on daylight regulations.
        
        Daylight Regulations (Seoul):
        - 제1종일반주거: Up to 9m: 1.5m setback, Above 9m: height × 0.5 setback
        - 제2종일반주거: Up to 9m: 1.0m setback, Above 9m: height × 0.5 setback
        - 제3종일반주거/준주거: Above 9m: height × 0.5 setback
        
        Args:
            zoning_type: Zoning classification
            land_depth_m: Land depth in north direction (m)
            floor_height: Floor height (m)
            
        Returns:
            Maximum number of floors
        """
        
        # Define setback requirements
        if zoning_type == '제1종일반주거':
            setback_base = 1.5  # Base setback for first 9m
            setback_ratio = 0.5  # Ratio for height above 9m
        elif zoning_type == '제2종일반주거':
            setback_base = 1.0
            setback_ratio = 0.5
        else:  # 제3종일반주거, 준주거
            setback_base = 0.0
            setback_ratio = 0.5
        
        # Calculate usable depth after base setback
        usable_depth = land_depth_m - setback_base
        
        if usable_depth <= 0:
            return 0
        
        # Calculate floors up to 9m (approximately 3 floors)
        max_height_9m = 9.0
        floors_9m = int(max_height_9m / floor_height)
        
        # If land depth allows more than 9m height
        if usable_depth > max_height_9m:
            # Additional height = (usable_depth - 9m) / (1 + setback_ratio)
            # This accounts for the setback requirement of height × 0.5
            additional_height = (usable_depth - max_height_9m) / (1 + setback_ratio)
            additional_floors = int(additional_height / floor_height)
            
            total_floors = floors_9m + additional_floors
        else:
            # Can only build up to what 9m constraint allows
            total_floors = min(floors_9m, int(usable_depth / floor_height))
        
        return total_floors
    
    def calculate_unit_count(
        self,
        total_floor_area: float,
        unit_types: Dict[str, float],
        efficiency_ratio: float = 0.75,
        common_area_ratio: float = 0.25
    ) -> UnitCalculation:
        """
        Calculate total unit count and distribution by type.
        
        Args:
            total_floor_area: Total floor area (㎡)
            unit_types: Unit type distribution (e.g., {"59": 0.6, "84": 0.4})
            efficiency_ratio: Residential efficiency ratio (default: 0.75)
            common_area_ratio: Common area ratio (default: 0.25)
            
        Returns:
            UnitCalculation object
        """
        
        # Calculate residential and common areas
        residential_area = total_floor_area * efficiency_ratio
        common_area = total_floor_area * common_area_ratio
        
        # Calculate average unit area
        avg_unit_area = sum(
            float(unit_type) * ratio
            for unit_type, ratio in unit_types.items()
        )
        
        # Calculate total units
        total_units = int(residential_area / avg_unit_area)
        
        # Distribute units by type
        units_by_type = {}
        for unit_type, ratio in unit_types.items():
            units_by_type[unit_type] = round(total_units * ratio)
        
        # Correct rounding errors
        actual_total = sum(units_by_type.values())
        if actual_total != total_units:
            # Adjust the largest type
            max_type = max(unit_types, key=unit_types.get)
            units_by_type[max_type] += (total_units - actual_total)
        
        self.logger.info(
            f"Unit calculation: {total_units} units total, "
            f"types={units_by_type}, avg_area={avg_unit_area:.1f}㎡"
        )
        
        return UnitCalculation(
            total_units=total_units,
            units_by_type=units_by_type,
            residential_area=residential_area,
            common_area=common_area,
            avg_unit_area=avg_unit_area
        )
    
    def calculate_parking_spaces(
        self,
        total_units: int,
        zoning_type: str
    ) -> ParkingCalculation:
        """
        Calculate required parking spaces based on zoning type.
        
        Args:
            total_units: Total number of units
            zoning_type: Zoning classification
            
        Returns:
            ParkingCalculation object
        """
        
        # Get parking ratio for zoning type
        parking_ratio = self.PARKING_RATIOS.get(zoning_type, 1.0)
        
        # Calculate required spaces (round up)
        required_spaces = math.ceil(total_units * parking_ratio)
        
        calculation = f"{total_units}세대 × {parking_ratio} = {required_spaces}대"
        
        self.logger.info(
            f"Parking calculation: {calculation} ({zoning_type})"
        )
        
        return ParkingCalculation(
            required_spaces=required_spaces,
            parking_ratio=parking_ratio,
            zoning_type=zoning_type,
            calculation=calculation
        )
    
    def validate_daylight_compliance(
        self,
        zoning_type: str,
        building_height: float,
        setback_distance: float
    ) -> DaylightValidation:
        """
        Validate daylight regulation compliance.
        
        Args:
            zoning_type: Zoning classification
            building_height: Actual building height (m)
            setback_distance: Actual setback distance (m)
            
        Returns:
            DaylightValidation object
        """
        
        # Calculate required setback
        if zoning_type == '제1종일반주거':
            if building_height <= 9.0:
                required_setback = 1.5
                regulation = "9m 이하: 1.5m 이격"
            else:
                required_setback = 1.5 + (building_height - 9.0) * 0.5
                regulation = "9m 초과: 1.5m + (H-9m)×0.5"
        
        elif zoning_type == '제2종일반주거':
            if building_height <= 9.0:
                required_setback = 1.0
                regulation = "9m 이하: 1.0m 이격"
            else:
                required_setback = 1.0 + (building_height - 9.0) * 0.5
                regulation = "9m 초과: 1.0m + (H-9m)×0.5"
        
        else:  # 제3종일반주거, 준주거
            if building_height <= 9.0:
                required_setback = 0.0
                regulation = "9m 이하: 이격거리 없음"
            else:
                required_setback = (building_height - 9.0) * 0.5
                regulation = "9m 초과: (H-9m)×0.5"
        
        # Check compliance
        compliant = setback_distance >= required_setback
        shortfall = max(0, required_setback - setback_distance)
        status = "✅ 준수" if compliant else "❌ 미준수"
        
        self.logger.info(
            f"Daylight validation: required={required_setback:.1f}m, "
            f"actual={setback_distance:.1f}m, {status}"
        )
        
        return DaylightValidation(
            compliant=compliant,
            required_setback=required_setback,
            actual_setback=setback_distance,
            shortfall=shortfall,
            regulation=regulation,
            status=status
        )


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    # Test the Capacity Engine with 3 test cases from specification
    engine = CapacityEngine()
    
    test_cases = [
        {
            "name": "Test 1: 제2종일반주거 (마포구 월드컵북로 120)",
            "input": {
                "land_area_sqm": 660.0,
                "zoning_type": "제2종일반주거",
                "far_limit": 200.0,
                "bcr_limit": 60.0,
                "height_limit": 35.0,
                "land_depth_m": 25.0,
                "unit_types": {"59": 0.6, "84": 0.4}
            },
            "expected": {
                "max_floors": 8,
                "total_units": 60,
                "parking_spaces": 48
            }
        },
        {
            "name": "Test 2: 제1종일반주거 (작은 필지)",
            "input": {
                "land_area_sqm": 300.0,
                "zoning_type": "제1종일반주거",
                "far_limit": 150.0,
                "bcr_limit": 50.0,
                "height_limit": 20.0,
                "land_depth_m": 15.0,
                "unit_types": {"59": 1.0}
            },
            "expected": {
                "max_floors": 4,
                "total_units": 17,
                "parking_spaces": 12
            }
        },
        {
            "name": "Test 3: 준주거지역 (고밀도)",
            "input": {
                "land_area_sqm": 1650.0,
                "zoning_type": "준주거",
                "far_limit": 500.0,
                "bcr_limit": 60.0,
                "height_limit": 50.0,
                "land_depth_m": 40.0,
                "unit_types": {"84": 0.5, "114": 0.5}
            },
            "expected": {
                "max_floors": 15,
                "total_units": 83,
                "parking_spaces": 83
            }
        }
    ]
    
    print("=" * 80)
    print("CAPACITY ENGINE v24.0.0 TEST")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        
        result = engine.process(test_case['input'])
        
        if result['success']:
            data = result['data']
            expected = test_case['expected']
            
            print(f"\n✅ Success!")
            print(f"\n📐 Floors:")
            print(f"   Max Floors: {data['floors']['max_floors']} "
                  f"(Expected: {expected['max_floors']}) "
                  f"{'✅' if data['floors']['max_floors'] == expected['max_floors'] else '❌'}")
            print(f"   By Height: {data['floors']['max_floors_by_height']}")
            print(f"   By FAR: {data['floors']['max_floors_by_far']}")
            print(f"   By Daylight: {data['floors']['max_floors_by_daylight']}")
            print(f"   Limiting Factor: {data['floors']['limiting_factor']}")
            print(f"   Building Height: {data['floors']['building_height']}m")
            
            print(f"\n🏠 Units:")
            print(f"   Total Units: {data['units']['total_units']} "
                  f"(Expected: {expected['total_units']}) "
                  f"{'✅' if abs(data['units']['total_units'] - expected['total_units']) <= 1 else '❌'}")
            print(f"   By Type: {data['units']['units_by_type']}")
            print(f"   Residential Area: {data['units']['residential_area']}㎡")
            print(f"   Avg Unit Area: {data['units']['avg_unit_area']}㎡")
            
            print(f"\n🚗 Parking:")
            print(f"   Required Spaces: {data['parking']['required_spaces']} "
                  f"(Expected: {expected['parking_spaces']}) "
                  f"{'✅' if data['parking']['required_spaces'] == expected['parking_spaces'] else '❌'}")
            print(f"   Ratio: {data['parking']['parking_ratio']}")
            print(f"   Calculation: {data['parking']['calculation']}")
            
            print(f"\n☀️ Daylight:")
            print(f"   Status: {data['daylight']['status']}")
            print(f"   Required Setback: {data['daylight']['required_setback']}m")
            print(f"   Actual Setback: {data['daylight']['actual_setback']}m")
            print(f"   Regulation: {data['daylight']['regulation']}")
            
            print(f"\n📊 Summary:")
            print(f"   Land Area: {data['summary']['land_area']}㎡")
            print(f"   Building Footprint: {data['summary']['building_footprint']}㎡")
            print(f"   Total Floor Area: {data['summary']['total_floor_area']}㎡")
            print(f"   FAR (Actual): {data['summary']['far_actual']}%")
        else:
            print(f"\n❌ Error: {result['error']}")
    
    print(f"\n{'='*80}")
    print("Test Complete!")
    print(f"{'='*80}")
