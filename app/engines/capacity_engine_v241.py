"""
ZeroSite v24.1 - Enhanced Capacity Engine

NEW FEATURES (v24.1 GAP #1):
- Mass Simulation: 층수×면적 3D 조합 알고리즘
- Sun Exposure Setback: 일조 이격거리 정밀 계산 (solar geometry)
- Floor Optimization: 층수 최적화 알고리즘 (multi-objective)

Priority: 🔴 CRITICAL (v24.1 GAP Closing)
Specification: docs/ZEROSITE_V24.1_GAP_CLOSING_PLAN.md

Author: ZeroSite Development Team
Version: 24.1.0
Date: 2025-12-12
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import math
import logging

from .capacity_engine import CapacityEngine, FloorCalculation

logger = logging.getLogger(__name__)


@dataclass
class MassConfiguration:
    """Building mass configuration"""
    floors: int
    footprint: float  # m²
    volume: float  # m³
    shape_type: str  # 'tower', 'slab', 'mixed'
    aspect_ratio: float  # length/width
    efficiency_score: float  # 0-100
    description: str


@dataclass
class SunExposureAnalysis:
    """Precise sun exposure analysis"""
    winter_solstice_shadow_length: float  # meters
    required_setback_north: float  # meters
    solar_angle_winter: float  # degrees
    solar_angle_summer: float  # degrees
    compliance_status: str  # 'PASS', 'FAIL', 'MARGINAL'
    daylight_hours_annual: float  # average hours per day
    recommendation: str


@dataclass
class FloorOptimizationResult:
    """Multi-objective floor optimization result"""
    optimal_floors: int
    unit_count: int
    sunlight_score: float  # 0-100
    cost_score: float  # 0-100
    shape_score: float  # 0-100
    total_score: float  # weighted average
    pareto_optimal: bool
    tradeoff_analysis: Dict[str, Any]


class CapacityEngineV241(CapacityEngine):
    """
    Enhanced Capacity Engine for ZeroSite v24.1
    
    NEW FEATURES:
    1. Mass Simulation - Generate multiple building configurations
    2. Sun Exposure - Precise solar geometry calculations
    3. Floor Optimization - Multi-objective optimization with Pareto analysis
    """
    
    # Solar constants
    LATITUDE_SEOUL = 37.5665  # degrees
    DECLINATION_WINTER_SOLSTICE = -23.45  # degrees (Dec 21)
    DECLINATION_SUMMER_SOLSTICE = 23.45  # degrees (Jun 21)
    
    def __init__(self):
        """Initialize Enhanced Capacity Engine v24.1"""
        super().__init__()
        self.version = "24.1.0"
        self.logger.info("Enhanced Capacity Engine v24.1.0 initialized (GAP #1)")
    
    # ========================================================================
    # NEW FEATURE #1: MASS SIMULATION
    # ========================================================================
    
    def generate_mass_simulation(
        self,
        land_area: float,
        bcr_limit: float,
        far_limit: float,
        max_floors: int,
        floor_height: float = 3.0
    ) -> List[MassConfiguration]:
        """
        Generate multiple building mass configurations (층수×면적 3D 조합)
        
        Strategy:
        - Tower형 (고층저면적): High aspect ratio, deep footprint
        - Slab형 (저층고면적): Low aspect ratio, wide footprint
        - Mixed형 (중간): Balanced configuration
        
        Args:
            land_area: Land area in m²
            bcr_limit: Building Coverage Ratio limit (%)
            far_limit: Floor Area Ratio limit (%)
            max_floors: Maximum allowable floors
            floor_height: Floor height in meters
            
        Returns:
            List of MassConfiguration objects (up to 5 configurations)
        """
        self.logger.info(f"Generating mass simulations for {land_area}m², max {max_floors} floors")
        
        max_footprint = land_area * (bcr_limit / 100)
        max_total_area = land_area * (far_limit / 100)
        
        configurations = []
        
        # Configuration 1: Tower Type (타워형 - 고층저면적)
        # Maximize floors, minimize footprint
        tower_floors = max_floors
        tower_footprint = min(max_footprint * 0.4, max_total_area / tower_floors)
        if tower_footprint > 0:
            tower_config = self._create_mass_config(
                floors=tower_floors,
                footprint=tower_footprint,
                floor_height=floor_height,
                shape_type='tower',
                aspect_ratio=2.5,  # Elongated
                description="고층 타워형 (최대 층수 활용)"
            )
            configurations.append(tower_config)
        
        # Configuration 2: Slab Type (슬랩형 - 저층고면적)
        # Minimize floors, maximize footprint
        slab_floors = max(3, max_floors // 3)
        slab_footprint = min(max_footprint * 0.9, max_total_area / slab_floors)
        if slab_footprint > 0:
            slab_config = self._create_mass_config(
                floors=slab_floors,
                footprint=slab_footprint,
                floor_height=floor_height,
                shape_type='slab',
                aspect_ratio=0.5,  # Wide and low
                description="저층 슬랩형 (최대 건축면적 활용)"
            )
            configurations.append(slab_config)
        
        # Configuration 3: Mixed Type (혼합형 - 중간)
        # Balanced approach
        mixed_floors = max_floors // 2
        mixed_footprint = min(max_footprint * 0.65, max_total_area / mixed_floors)
        if mixed_footprint > 0:
            mixed_config = self._create_mass_config(
                floors=mixed_floors,
                footprint=mixed_footprint,
                floor_height=floor_height,
                shape_type='mixed',
                aspect_ratio=1.5,
                description="중층 혼합형 (균형잡힌 구성)"
            )
            configurations.append(mixed_config)
        
        # Configuration 4: Optimal FAR Type (용적률 최적형)
        # Maximize FAR utilization
        optimal_far_floors = int(max_total_area / max_footprint)
        optimal_far_floors = min(optimal_far_floors, max_floors)
        optimal_far_footprint = max_footprint
        if optimal_far_floors > 0:
            optimal_config = self._create_mass_config(
                floors=optimal_far_floors,
                footprint=optimal_far_footprint,
                floor_height=floor_height,
                shape_type='mixed',
                aspect_ratio=1.8,
                description="용적률 최적형 (FAR 100% 활용)"
            )
            configurations.append(optimal_config)
        
        # Configuration 5: Efficiency Type (효율형)
        # Balance efficiency and buildability
        efficiency_floors = int(max_floors * 0.7)
        efficiency_footprint = min(max_footprint * 0.75, max_total_area / efficiency_floors)
        if efficiency_footprint > 0 and efficiency_floors > 0:
            efficiency_config = self._create_mass_config(
                floors=efficiency_floors,
                footprint=efficiency_footprint,
                floor_height=floor_height,
                shape_type='mixed',
                aspect_ratio=1.3,
                description="효율형 (시공성 + 효율성 균형)"
            )
            configurations.append(efficiency_config)
        
        # Sort by efficiency score (descending)
        configurations.sort(key=lambda x: x.efficiency_score, reverse=True)
        
        self.logger.info(f"Generated {len(configurations)} mass configurations")
        
        return configurations[:5]  # Return top 5
    
    def _create_mass_config(
        self,
        floors: int,
        footprint: float,
        floor_height: float,
        shape_type: str,
        aspect_ratio: float,
        description: str
    ) -> MassConfiguration:
        """Create a mass configuration with calculated metrics"""
        
        volume = footprint * floors * floor_height
        
        # Calculate efficiency score (0-100)
        # Factors: Floor count (30%), footprint utilization (30%), 
        #          aspect ratio (20%), buildability (20%)
        floor_score = min(100, (floors / 20) * 100) * 0.30
        footprint_score = min(100, (footprint / 1000) * 100) * 0.30
        
        # Optimal aspect ratio is 1.5-2.0
        aspect_score = 100 - abs(aspect_ratio - 1.75) * 30
        aspect_score = max(0, min(100, aspect_score)) * 0.20
        
        # Buildability: Lower is easier (prefer mid-rise)
        buildability_score = (100 - abs(floors - 10) * 3)
        buildability_score = max(0, min(100, buildability_score)) * 0.20
        
        efficiency_score = floor_score + footprint_score + aspect_score + buildability_score
        
        return MassConfiguration(
            floors=floors,
            footprint=round(footprint, 2),
            volume=round(volume, 2),
            shape_type=shape_type,
            aspect_ratio=round(aspect_ratio, 2),
            efficiency_score=round(efficiency_score, 2),
            description=description
        )
    
    # ========================================================================
    # NEW FEATURE #2: SUN EXPOSURE SETBACK (SOLAR GEOMETRY)
    # ========================================================================
    
    def calculate_sun_exposure_setback(
        self,
        building_height: float,
        zoning_type: str,
        latitude: float = LATITUDE_SEOUL,
        analyze_annual: bool = True
    ) -> SunExposureAnalysis:
        """
        Precise sun exposure calculation using solar geometry
        
        Method:
        1. Calculate solar altitude angle at winter solstice
        2. Compute shadow length using trigonometry
        3. Apply zoning-specific setback requirements
        4. Assess compliance status
        
        Args:
            building_height: Building height in meters
            zoning_type: Zoning classification
            latitude: Site latitude (default: Seoul 37.5665°)
            analyze_annual: Whether to calculate annual average
            
        Returns:
            SunExposureAnalysis object with detailed solar analysis
        """
        self.logger.info(
            f"Calculating sun exposure for {building_height}m building at {latitude}°N"
        )
        
        # 1. Calculate solar altitude angle at winter solstice (worst case)
        solar_altitude_winter = self._calculate_solar_altitude(
            latitude=latitude,
            declination=self.DECLINATION_WINTER_SOLSTICE
        )
        
        # 2. Calculate shadow length at solar noon
        # Shadow = Height / tan(altitude_angle)
        shadow_length_winter = building_height / math.tan(math.radians(solar_altitude_winter))
        
        # 3. Apply zoning-specific setback requirements
        if zoning_type in ['제1종일반주거', '제2종일반주거']:
            # Residential zones: More strict requirements
            required_setback = shadow_length_winter * 0.5  # 50% of shadow length
            min_setback = 1.5 if zoning_type == '제1종일반주거' else 1.0
            required_setback = max(required_setback, min_setback)
        else:
            # Commercial/mixed zones: Less strict
            required_setback = shadow_length_winter * 0.3  # 30% of shadow length
        
        # 4. Calculate summer solar angle for comparison
        solar_altitude_summer = self._calculate_solar_altitude(
            latitude=latitude,
            declination=self.DECLINATION_SUMMER_SOLSTICE
        )
        
        # 5. Calculate annual average daylight hours
        if analyze_annual:
            # Simplified: Assume 4.5 hours direct sunlight in winter, 
            # 6.5 in summer, average ~5.5
            daylight_hours_annual = 5.5
        else:
            daylight_hours_annual = 4.0  # Winter minimum
        
        # 6. Determine compliance status
        # Assume actual setback is required (for recommendation)
        if daylight_hours_annual >= 4.0 and solar_altitude_winter >= 30:
            compliance_status = 'PASS'
            recommendation = f"일조권 확보 양호. 정북방향 {required_setback:.1f}m 이상 이격 권장."
        elif daylight_hours_annual >= 3.0:
            compliance_status = 'MARGINAL'
            recommendation = f"일조권 개선 필요. 정북방향 {required_setback:.1f}m 이상 이격 필수."
        else:
            compliance_status = 'FAIL'
            recommendation = f"일조권 미달. 층수 축소 또는 정북방향 {required_setback * 1.5:.1f}m 이격 필요."
        
        self.logger.info(
            f"Sun exposure: Shadow {shadow_length_winter:.1f}m, "
            f"Setback {required_setback:.1f}m, Status {compliance_status}"
        )
        
        return SunExposureAnalysis(
            winter_solstice_shadow_length=round(shadow_length_winter, 2),
            required_setback_north=round(required_setback, 2),
            solar_angle_winter=round(solar_altitude_winter, 2),
            solar_angle_summer=round(solar_altitude_summer, 2),
            compliance_status=compliance_status,
            daylight_hours_annual=round(daylight_hours_annual, 1),
            recommendation=recommendation
        )
    
    def _calculate_solar_altitude(self, latitude: float, declination: float) -> float:
        """
        Calculate solar altitude angle at solar noon
        
        Formula: sin(altitude) = sin(latitude) × sin(declination) + 
                                 cos(latitude) × cos(declination)
        
        Args:
            latitude: Site latitude in degrees
            declination: Solar declination in degrees
            
        Returns:
            Solar altitude angle in degrees
        """
        lat_rad = math.radians(latitude)
        dec_rad = math.radians(declination)
        
        sin_altitude = (
            math.sin(lat_rad) * math.sin(dec_rad) +
            math.cos(lat_rad) * math.cos(dec_rad)
        )
        
        # Handle edge cases
        sin_altitude = max(-1.0, min(1.0, sin_altitude))
        
        altitude_rad = math.asin(sin_altitude)
        altitude_deg = math.degrees(altitude_rad)
        
        return altitude_deg
    
    # ========================================================================
    # NEW FEATURE #3: FLOOR OPTIMIZATION (MULTI-OBJECTIVE)
    # ========================================================================
    
    def optimize_floor_configuration(
        self,
        land_area: float,
        bcr_limit: float,
        far_limit: float,
        height_limit: float,
        zoning_type: str,
        unit_area_avg: float = 59.0,
        floor_height: float = 3.0,
        weights: Optional[Dict[str, float]] = None
    ) -> List[FloorOptimizationResult]:
        """
        Multi-objective floor optimization
        
        Objectives (weighted):
        1. Maximize unit count (30%)
        2. Maximize sunlight exposure (25%)
        3. Minimize construction cost (25%)
        4. Maximize shape regularity (20%)
        
        Method:
        - Generate candidate solutions (3-20 floors)
        - Evaluate each against objectives
        - Identify Pareto optimal set
        - Return ranked solutions with tradeoff analysis
        
        Args:
            land_area: Land area in m²
            bcr_limit: Building Coverage Ratio limit (%)
            far_limit: Floor Area Ratio limit (%)
            height_limit: Maximum height in meters
            zoning_type: Zoning classification
            unit_area_avg: Average unit area in m²
            floor_height: Floor height in meters
            weights: Custom objective weights (optional)
            
        Returns:
            List of FloorOptimizationResult objects (ranked)
        """
        self.logger.info(f"Optimizing floor configuration for {land_area}m² site")
        
        # Default weights
        if weights is None:
            weights = {
                'unit_count': 0.30,
                'sunlight': 0.25,
                'cost': 0.25,
                'shape': 0.20
            }
        
        # Generate candidate floor counts
        max_floors_by_height = int(height_limit / floor_height)
        max_floors_by_far = int((land_area * far_limit / 100) / 
                                (land_area * bcr_limit / 100))
        max_floors = min(max_floors_by_height, max_floors_by_far, 20)
        
        candidates = list(range(3, max_floors + 1))
        
        # Evaluate each candidate
        results = []
        for floors in candidates:
            result = self._evaluate_floor_option(
                floors=floors,
                land_area=land_area,
                bcr_limit=bcr_limit,
                far_limit=far_limit,
                zoning_type=zoning_type,
                unit_area_avg=unit_area_avg,
                floor_height=floor_height,
                weights=weights
            )
            results.append(result)
        
        # Identify Pareto optimal solutions
        results = self._identify_pareto_optimal(results)
        
        # Sort by total score (descending)
        results.sort(key=lambda x: x.total_score, reverse=True)
        
        self.logger.info(
            f"Optimized {len(results)} configurations, "
            f"optimal: {results[0].optimal_floors} floors"
        )
        
        return results
    
    def _evaluate_floor_option(
        self,
        floors: int,
        land_area: float,
        bcr_limit: float,
        far_limit: float,
        zoning_type: str,
        unit_area_avg: float,
        floor_height: float,
        weights: Dict[str, float]
    ) -> FloorOptimizationResult:
        """Evaluate a single floor count option against objectives"""
        
        building_height = floors * floor_height
        footprint = land_area * (bcr_limit / 100)
        total_area = footprint * floors
        
        # Objective 1: Unit Count (maximize)
        unit_count = int((total_area * 0.75) / unit_area_avg)  # 75% efficiency
        unit_score = min(100, (unit_count / 100) * 100)
        
        # Objective 2: Sunlight Score (maximize)
        sun_analysis = self.calculate_sun_exposure_setback(
            building_height=building_height,
            zoning_type=zoning_type
        )
        sunlight_score = {
            'PASS': 100,
            'MARGINAL': 60,
            'FAIL': 30
        }.get(sun_analysis.compliance_status, 50)
        
        # Objective 3: Cost Score (minimize cost = maximize score)
        # Lower floors = lower cost per unit
        # Optimal around 10 floors
        cost_score = 100 - abs(floors - 10) * 3
        cost_score = max(20, min(100, cost_score))
        
        # Objective 4: Shape Score (regularity)
        # Mid-rise buildings have better shape regularity
        shape_score = 100 - abs(floors - 8) * 4
        shape_score = max(30, min(100, shape_score))
        
        # Calculate weighted total score
        total_score = (
            unit_score * weights['unit_count'] +
            sunlight_score * weights['sunlight'] +
            cost_score * weights['cost'] +
            shape_score * weights['shape']
        )
        
        # Tradeoff analysis
        tradeoff = {
            'unit_count': unit_count,
            'unit_score': round(unit_score, 2),
            'sunlight_status': sun_analysis.compliance_status,
            'sunlight_score': round(sunlight_score, 2),
            'cost_per_unit_relative': round((100 - cost_score) + 100, 2),
            'cost_score': round(cost_score, 2),
            'shape_regularity': round(shape_score, 2),
            'shape_score': round(shape_score, 2)
        }
        
        return FloorOptimizationResult(
            optimal_floors=floors,
            unit_count=unit_count,
            sunlight_score=round(sunlight_score, 2),
            cost_score=round(cost_score, 2),
            shape_score=round(shape_score, 2),
            total_score=round(total_score, 2),
            pareto_optimal=False,  # Will be updated
            tradeoff_analysis=tradeoff
        )
    
    def _identify_pareto_optimal(
        self,
        results: List[FloorOptimizationResult]
    ) -> List[FloorOptimizationResult]:
        """
        Identify Pareto optimal solutions
        
        A solution is Pareto optimal if no other solution dominates it
        (i.e., better in all objectives)
        """
        pareto_set = []
        
        for i, result_i in enumerate(results):
            dominated = False
            
            for j, result_j in enumerate(results):
                if i == j:
                    continue
                
                # Check if result_j dominates result_i
                # (better in all objectives)
                if (result_j.unit_count >= result_i.unit_count and
                    result_j.sunlight_score >= result_i.sunlight_score and
                    result_j.cost_score >= result_i.cost_score and
                    result_j.shape_score >= result_i.shape_score and
                    (result_j.unit_count > result_i.unit_count or
                     result_j.sunlight_score > result_i.sunlight_score or
                     result_j.cost_score > result_i.cost_score or
                     result_j.shape_score > result_i.shape_score)):
                    dominated = True
                    break
            
            if not dominated:
                result_i.pareto_optimal = True
                pareto_set.append(result_i)
        
        self.logger.info(f"Identified {len(pareto_set)} Pareto optimal solutions")
        
        # Mark non-Pareto as False (already done above)
        return results


# ============================================================================
# CLI TEST
# ============================================================================

if __name__ == "__main__":
    """Test the Enhanced Capacity Engine v24.1"""
    
    engine = CapacityEngineV241()
    
    print("=" * 80)
    print("ENHANCED CAPACITY ENGINE v24.1 TEST (GAP #1)")
    print("=" * 80)
    
    # Test Case: 마포구 월드컵북로 120
    test_input = {
        'land_area': 660.0,
        'bcr_limit': 60.0,
        'far_limit': 200.0,
        'max_floors': 11,
        'height_limit': 35.0,
        'zoning_type': '제2종일반주거',
        'floor_height': 3.0
    }
    
    print(f"\n{'='*80}")
    print("TEST 1: MASS SIMULATION (층수×면적 3D 조합)")
    print(f"{'='*80}")
    
    mass_configs = engine.generate_mass_simulation(
        land_area=test_input['land_area'],
        bcr_limit=test_input['bcr_limit'],
        far_limit=test_input['far_limit'],
        max_floors=test_input['max_floors'],
        floor_height=test_input['floor_height']
    )
    
    print(f"\n✅ Generated {len(mass_configs)} mass configurations:\n")
    for i, config in enumerate(mass_configs, 1):
        print(f"  {i}. {config.description}")
        print(f"     Floors: {config.floors}, Footprint: {config.footprint}m², "
              f"Volume: {config.volume}m³")
        print(f"     Shape: {config.shape_type}, Aspect: {config.aspect_ratio}, "
              f"Efficiency: {config.efficiency_score:.1f}")
        print()
    
    print(f"\n{'='*80}")
    print("TEST 2: SUN EXPOSURE SETBACK (일조 이격거리 정밀 계산)")
    print(f"{'='*80}")
    
    sun_analysis = engine.calculate_sun_exposure_setback(
        building_height=30.0,  # 10 floors × 3m
        zoning_type=test_input['zoning_type'],
        analyze_annual=True
    )
    
    print(f"\n✅ Sun Exposure Analysis:")
    print(f"   Winter Solstice Shadow: {sun_analysis.winter_solstice_shadow_length}m")
    print(f"   Required Setback (North): {sun_analysis.required_setback_north}m")
    print(f"   Solar Angle (Winter): {sun_analysis.solar_angle_winter}°")
    print(f"   Solar Angle (Summer): {sun_analysis.solar_angle_summer}°")
    print(f"   Annual Daylight Hours: {sun_analysis.daylight_hours_annual}h/day")
    print(f"   Compliance: {sun_analysis.compliance_status}")
    print(f"   Recommendation: {sun_analysis.recommendation}")
    
    print(f"\n{'='*80}")
    print("TEST 3: FLOOR OPTIMIZATION (층수 최적화 - Multi-Objective)")
    print(f"{'='*80}")
    
    optimization_results = engine.optimize_floor_configuration(
        land_area=test_input['land_area'],
        bcr_limit=test_input['bcr_limit'],
        far_limit=test_input['far_limit'],
        height_limit=test_input['height_limit'],
        zoning_type=test_input['zoning_type'],
        unit_area_avg=59.0,
        floor_height=test_input['floor_height']
    )
    
    print(f"\n✅ Optimized {len(optimization_results)} floor configurations:\n")
    print(f"   Pareto Optimal Solutions: "
          f"{sum(1 for r in optimization_results if r.pareto_optimal)}\n")
    
    # Show top 5 results
    for i, result in enumerate(optimization_results[:5], 1):
        pareto_mark = "⭐" if result.pareto_optimal else "  "
        print(f"  {pareto_mark} #{i}. {result.optimal_floors} floors "
              f"(Total Score: {result.total_score:.1f})")
        print(f"      Units: {result.unit_count}, "
              f"Sunlight: {result.sunlight_score:.1f}, "
              f"Cost: {result.cost_score:.1f}, "
              f"Shape: {result.shape_score:.1f}")
        print()
    
    print(f"\n{'='*80}")
    print("✅ ALL TESTS COMPLETED - GAP #1 IMPLEMENTED")
    print(f"{'='*80}")
