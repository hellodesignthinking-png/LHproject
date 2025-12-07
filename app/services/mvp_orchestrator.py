"""
ZeroSite MVP Orchestrator
=========================

Single-parcel land analysis orchestrator:
1. Land Input → Zoning Rules
2. Building Scale Calculation (Flexity-style)
3. Unit Type Estimation (v11.0)
4. LH Evaluation (v11.0)
5. PDF Report Generation (v7.5 design + v11.0 data)

Author: ZeroSite Development Team
Date: 2025-12-06
Version: MVP 1.0
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from app.mvp_config_pkg.mvp_config import get_mvp_config
from app.services_v9.address_resolver_v9_0 import AddressResolverV9
from app.services_v9.zoning_auto_mapper_v9_0 import ZoningAutoMapperV9

logger = logging.getLogger(__name__)


@dataclass
class LandInput:
    """Land input data"""
    address: str
    land_area: float
    land_appraisal_price: Optional[float] = None
    zone_type: Optional[str] = None


@dataclass
class BuildingScale:
    """Building scale calculation result"""
    total_gross_area: float
    residential_gfa: float
    commercial_gfa: float
    building_footprint: float
    max_units: int
    floor_count: int
    units_per_floor: int
    parking_required: int
    
    # Regulatory info
    building_coverage_ratio: float
    floor_area_ratio: float
    zone_type: str
    
    # Calculation metadata
    unit_area_used: float
    residential_ratio: float
    parking_ratio: float


@dataclass
class MVPAnalysisResult:
    """Complete MVP analysis result"""
    # Input
    land_input: LandInput
    
    # Step 1: Land & Zoning
    coordinates: Dict[str, float]
    zoning_info: Dict[str, Any]
    
    # Step 2: Building Scale
    building_scale: BuildingScale
    
    # Step 3-5: v11.0 Engine Results (to be filled by report generator)
    unit_analysis: Optional[Dict[str, Any]] = None
    lh_evaluation: Optional[Dict[str, Any]] = None
    
    # Metadata
    timestamp: str = None
    calculation_time_ms: int = 0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class MVPOrchestrator:
    """
    MVP Orchestrator for single-parcel analysis
    
    Workflow:
        1. Resolve address → coordinates
        2. Get zoning rules → BCR/FAR
        3. Calculate building scale (Flexity-style)
        4. Return structured data for v11.0 engines
    
    Usage:
        orchestrator = MVPOrchestrator()
        result = await orchestrator.analyze(
            address="서울특별시 강남구 테헤란로 123",
            land_area=850.0,
            land_appraisal_price=4500000.0
        )
    """
    
    def __init__(self):
        """Initialize MVP orchestrator"""
        self.config = get_mvp_config()
        self.address_resolver = AddressResolverV9()
        self.zoning_mapper = ZoningAutoMapperV9()
        logger.info("✅ MVPOrchestrator initialized")
    
    async def analyze(
        self,
        address: str,
        land_area: float,
        land_appraisal_price: Optional[float] = None,
        zone_type: Optional[str] = None
    ) -> MVPAnalysisResult:
        """
        Execute complete MVP analysis flow
        
        Args:
            address: Property address
            land_area: Land area in m²
            land_appraisal_price: Optional land appraisal price
            zone_type: Optional zone type (auto-detected if not provided)
        
        Returns:
            MVPAnalysisResult: Complete analysis result
        
        Raises:
            ValueError: If required data is missing or invalid
        """
        start_time = datetime.utcnow()
        logger.info("="*80)
        logger.info(f"🚀 MVP Analysis Started: {address}")
        logger.info("="*80)
        
        # Create land input
        land_input = LandInput(
            address=address,
            land_area=land_area,
            land_appraisal_price=land_appraisal_price,
            zone_type=zone_type
        )
        
        # Step 1: Resolve address → coordinates
        logger.info("\n📍 Step 1: Address Resolution")
        coordinates = await self._resolve_address(address)
        logger.info(f"   ✅ Coordinates: {coordinates}")
        
        # Step 2: Get zoning information
        logger.info("\n🏗️ Step 2: Zoning Information")
        zoning_info = self._get_zoning_info(zone_type or "제2종일반주거지역")
        logger.info(f"   ✅ Zone Type: {zoning_info['zone_type']}")
        logger.info(f"   ✅ BCR: {zoning_info['building_coverage_ratio']}%")
        logger.info(f"   ✅ FAR: {zoning_info['floor_area_ratio']}%")
        
        # Update land input with detected zone type
        if not land_input.zone_type:
            land_input.zone_type = zoning_info['zone_type']
        
        # Step 3: Calculate building scale (Flexity-style)
        logger.info("\n📐 Step 3: Building Scale Calculation")
        building_scale = self._calculate_building_scale(
            land_area=land_area,
            bcr=zoning_info['building_coverage_ratio'],
            far=zoning_info['floor_area_ratio'],
            zone_type=zoning_info['zone_type']
        )
        logger.info(f"   ✅ Total GFA: {building_scale.total_gross_area:,.0f} m²")
        logger.info(f"   ✅ Max Units: {building_scale.max_units}")
        logger.info(f"   ✅ Floors: {building_scale.floor_count}")
        logger.info(f"   ✅ Parking: {building_scale.parking_required}")
        
        # Calculate execution time
        end_time = datetime.utcnow()
        calc_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Create result
        result = MVPAnalysisResult(
            land_input=land_input,
            coordinates=coordinates,
            zoning_info=zoning_info,
            building_scale=building_scale,
            calculation_time_ms=calc_time_ms
        )
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ MVP Analysis Complete ({calc_time_ms}ms)")
        logger.info("="*80)
        
        return result
    
    async def _resolve_address(self, address: str) -> Dict[str, float]:
        """
        Resolve address to coordinates
        
        Args:
            address: Property address
        
        Returns:
            Dict with latitude, longitude, legal_code
        """
        try:
            address_info = await self.address_resolver.resolve_address(address)
            
            if address_info:
                return {
                    "latitude": address_info.latitude,
                    "longitude": address_info.longitude,
                    "legal_code": address_info.legal_code
                }
            else:
                # Default to Seoul City Hall
                logger.warning("⚠️ Address resolution failed, using default coordinates")
                return {
                    "latitude": 37.5665,
                    "longitude": 126.9780,
                    "legal_code": "1111000000"
                }
        except Exception as e:
            logger.error(f"❌ Address resolution error: {str(e)}")
            return {
                "latitude": 37.5665,
                "longitude": 126.9780,
                "legal_code": "1111000000"
            }
    
    def _get_zoning_info(self, zone_type: str) -> Dict[str, Any]:
        """
        Get zoning information and building standards
        
        Args:
            zone_type: Zone type (e.g., "제2종일반주거지역")
        
        Returns:
            Dict with zone_type, BCR, FAR, parking_ratio, max_height
        """
        try:
            standards = self.zoning_mapper.get_zoning_standards(zone_type)
            
            if standards:
                return {
                    "zone_type": standards.zone_type,
                    "building_coverage_ratio": standards.building_coverage_ratio,
                    "floor_area_ratio": standards.floor_area_ratio,
                    "max_height": standards.max_height,
                    "parking_ratio": standards.parking_ratio,
                    "description": standards.description
                }
            else:
                # Default values
                logger.warning(f"⚠️ Zone type '{zone_type}' not found, using defaults")
                return {
                    "zone_type": "미지정",
                    "building_coverage_ratio": 50.0,
                    "floor_area_ratio": 200.0,
                    "max_height": None,
                    "parking_ratio": 1.0,
                    "description": "기본값"
                }
        except Exception as e:
            logger.error(f"❌ Zoning info error: {str(e)}")
            return {
                "zone_type": "미지정",
                "building_coverage_ratio": 50.0,
                "floor_area_ratio": 200.0,
                "max_height": None,
                "parking_ratio": 1.0,
                "description": "기본값"
            }
    
    def _calculate_building_scale(
        self,
        land_area: float,
        bcr: float,
        far: float,
        zone_type: str
    ) -> BuildingScale:
        """
        Calculate building scale (Flexity-style)
        
        Formula:
            max_floor_area = land_area × (FAR / 100)
            coverage_area = land_area × (BCR / 100)
            floor_count = max_floor_area / coverage_area
            residential_gfa = max_floor_area × residential_ratio
            max_units = residential_gfa / unit_area
            parking = max_units × parking_ratio
        
        Args:
            land_area: Land area in m²
            bcr: Building coverage ratio (%)
            far: Floor area ratio (%)
            zone_type: Zone type
        
        Returns:
            BuildingScale: Complete building scale calculation
        """
        config = self.config.building
        
        # Get externalized parameters
        unit_area = config.default_unit_area
        residential_ratio = config.residential_ratio
        commercial_ratio = config.commercial_ratio
        parking_ratio = config.parking_ratios.get(zone_type, config.parking_ratios["default"])
        max_floors_limit = config.max_floors_by_zone.get(zone_type, config.max_floors_by_zone["default"])
        
        # Calculate total GFA
        total_gross_area = land_area * (far / 100.0)
        
        # Calculate building footprint
        building_footprint = land_area * (bcr / 100.0)
        
        # Calculate residential vs commercial GFA
        residential_gfa = total_gross_area * residential_ratio
        commercial_gfa = total_gross_area * commercial_ratio
        
        # Calculate floor count
        if building_footprint > 0:
            calculated_floors = int(total_gross_area / building_footprint)
            floor_count = max(config.min_floors, calculated_floors)
            floor_count = min(floor_count, max_floors_limit)
        else:
            floor_count = config.min_floors
        
        # Calculate max units
        max_units = int(residential_gfa / unit_area)
        max_units = max(config.min_units, max_units)
        
        # Calculate units per floor
        units_per_floor = int(max_units / floor_count) if floor_count > 0 else 0
        units_per_floor = max(2, units_per_floor)
        
        # Calculate parking
        parking_required = int(max_units * parking_ratio)
        
        return BuildingScale(
            total_gross_area=total_gross_area,
            residential_gfa=residential_gfa,
            commercial_gfa=commercial_gfa,
            building_footprint=building_footprint,
            max_units=max_units,
            floor_count=floor_count,
            units_per_floor=units_per_floor,
            parking_required=parking_required,
            building_coverage_ratio=bcr,
            floor_area_ratio=far,
            zone_type=zone_type,
            unit_area_used=unit_area,
            residential_ratio=residential_ratio,
            parking_ratio=parking_ratio
        )
    
    def to_dict(self, result: MVPAnalysisResult) -> Dict[str, Any]:
        """Convert MVPAnalysisResult to dictionary"""
        return {
            "land_input": asdict(result.land_input),
            "coordinates": result.coordinates,
            "zoning_info": result.zoning_info,
            "building_scale": asdict(result.building_scale),
            "unit_analysis": result.unit_analysis,
            "lh_evaluation": result.lh_evaluation,
            "timestamp": result.timestamp,
            "calculation_time_ms": result.calculation_time_ms
        }


# Global singleton
_orchestrator: Optional[MVPOrchestrator] = None


def get_orchestrator() -> MVPOrchestrator:
    """Get or create MVP orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MVPOrchestrator()
    return _orchestrator
