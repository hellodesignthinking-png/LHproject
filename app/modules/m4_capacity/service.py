"""
M4 Capacity Service
===================

건축규모 검토 서비스

이 서비스는 M1 토지정보와 M3 주택유형을 기반으로
건축 가능한 규모(세대수, 연면적 등)를 계산합니다.

계산 요소:
- FAR/BCR 기반 규모 산정
- 주차대수 산정
- 세대수 계산
- 층수 산정

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

import logging
from datetime import datetime

from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.housing_type_context import HousingTypeContext
from app.core.context.capacity_context import CapacityContext

logger = logging.getLogger(__name__)


class CapacityService:
    """
    건축규모 검토 서비스 (M4)
    
    입력: CanonicalLandContext (M1), HousingTypeContext (M3)
    출력: CapacityContext (건축 규모)
    """
    
    def __init__(self):
        """서비스 초기화"""
        logger.info("✅ M4 Capacity Service initialized")
    
    def run(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext
    ) -> CapacityContext:
        """
        건축규모 검토 실행
        
        Args:
            land_ctx: M1 토지정보
            housing_type_ctx: M3 주택유형
        
        Returns:
            CapacityContext (frozen=True)
        """
        
        logger.info("="*80)
        logger.info("🏗️ M4 CAPACITY MODULE - Calculating Building Capacity")
        logger.info(f"   Land Area: {land_ctx.area_sqm:,.1f}㎡")
        logger.info(f"   Housing Type: {housing_type_ctx.selected_type}")
        logger.info(f"   FAR: {land_ctx.far}%, BCR: {land_ctx.bcr}%")
        logger.info("="*80)
        
        # TODO: 실제 로직 구현
        # Step 1: 건축면적 = 대지면적 × BCR
        # Step 2: 연면적 = 대지면적 × FAR
        # Step 3: 세대수 = 연면적 / 세대당 전용면적
        # Step 4: 주차대수 = 세대수 × 주차비율
        # Step 5: 층수 = 연면적 / 건축면적
        
        # Mock 데이터
        capacity_ctx = self._create_mock_context(land_ctx, housing_type_ctx)
        
        logger.info(f"✅ Capacity Calculated")
        logger.info(f"   Recommended Units: {capacity_ctx.unit_summary.total_units if hasattr(capacity_ctx, 'unit_summary') else 'N/A'}")
        logger.info(f"   GFA: {capacity_ctx.building_specs.total_gfa_sqm:,.1f}㎡")
        logger.info(f"   Parking: {capacity_ctx.parking_plan.planned_spaces}")
        logger.info("="*80)
        
        return capacity_ctx
    
    def _create_mock_context(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext
    ) -> CapacityContext:
        """Mock 규모 계산 (테스트용)"""
        # TODO: 실제 로직으로 교체
        
        # 간단한 계산
        bcr = land_ctx.bcr / 100
        far = land_ctx.far / 100
        
        building_coverage = land_ctx.area_sqm * bcr
        total_gfa = land_ctx.area_sqm * far
        
        # 세대당 전용면적 (청년형 기준 30㎡)
        unit_area = 30.0
        total_units = int(total_gfa / (unit_area * 1.5))  # 공용면적 포함
        
        # 주차대수 (세대당 0.5대)
        parking_spaces = int(total_units * 0.5)
        
        # 층수
        floors = int(total_gfa / building_coverage)
        
        # BuildingSpecs, UnitPlan, ParkingPlan 생성
        from app.core.context.capacity_context import BuildingSpecs, UnitPlan, ParkingPlan
        
        building_specs = BuildingSpecs(
            max_floors=floors + 2,
            recommended_floors=floors,
            total_gfa_sqm=total_gfa,
            building_coverage_sqm=building_coverage,
            unit_area_avg=unit_area
        )
        
        unit_plan = UnitPlan(
            max_units=int(total_units * 1.2),
            recommended_units=total_units,
            unit_type_distribution={
                "소형(30㎡)": total_units
            }
        )
        
        parking_plan = ParkingPlan(
            required_spaces=int(parking_spaces * 0.9),
            planned_spaces=parking_spaces,
            parking_ratio=0.5
        )
        
        return CapacityContext(
            far_available=land_ctx.far,
            bcr_available=land_ctx.bcr,
            far_utilization=0.8,  # Mock 80% 활용
            bcr_utilization=0.7,  # Mock 70% 활용
            building_specs=building_specs,
            unit_plan=unit_plan,
            parking_plan=parking_plan,
            building_type="아파트",
            structure_type="철근콘크리트",
            compliance_score=13.5,  # Mock score
            calculation_date=datetime.now().strftime("%Y-%m-%d"),
            compliance_issues=[],
            design_constraints=[]
        )


__all__ = ["CapacityService"]
