"""
ZeroSite Phase 11: Design Generator

Automated building design generator that creates 3 design alternatives (A/B/C)
based on LH housing standards.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from .models import (
    BuildingDesign,
    DesignStrategy,
    SupplyType,
    DesignMetrics,
    DesignComparisonResult
)
from .zoning_rules import ZoningRuleEngine
from .lh_unit_distribution import LHUnitDistributor
from .parking_calculator import ParkingCalculator
from .geometry_engine import GeometryEngine

logger = logging.getLogger(__name__)


class DesignGenerator:
    """
    3가지 설계안 자동 생성 엔진
    
    Generates:
    - A안 (안정형): LH 점수 최대화
    - B안 (표준형): 균형 설계
    - C안 (수익형): ROI 최대화
    
    Features:
    - LH 매입임대 기준 평형 구성
    - 법규 기반 규모 산정
    - 자동 주차 계산
    - 배치도 생성
    """
    
    def __init__(
        self,
        address: str,
        land_params: Dict,
        supply_type: Optional[SupplyType] = None
    ):
        """
        Initialize design generator
        
        Args:
            address: 대지 주소
            land_params: {
                "area": 대지면적 (㎡),
                "bcr": 건폐율 (%),
                "far": 용적률 (%),
                "max_floors": 최고층수 (선택),
                "zone_type": 용도지역 (선택)
            }
            supply_type: LH 공급유형 (선택, 자동 추천 가능)
        """
        self.address = address
        self.land_params = land_params
        
        # 공급유형 자동 추천 또는 사용자 지정
        if supply_type is None:
            self.supply_type = LHUnitDistributor.recommend_supply_type(address)
            logger.info(f"🤖 Auto-recommended supply type: {self.supply_type.value}")
        else:
            self.supply_type = supply_type
            logger.info(f"👤 User-specified supply type: {self.supply_type.value}")
        
        # Initialize engines
        self.zoning_engine = ZoningRuleEngine(land_params)
        self.unit_distributor = LHUnitDistributor(self.supply_type)
        self.parking_calculator = ParkingCalculator()
        self.geometry_engine = GeometryEngine()
        
        logger.info(f"🏗️ Design Generator initialized for: {address}")
    
    def generate(self) -> List[BuildingDesign]:
        """
        3가지 설계안 생성 (A/B/C)
        
        Returns:
            List of BuildingDesign (A안, B안, C안)
        """
        logger.info("🎨 Generating 3 design alternatives...")
        
        designs = []
        
        # Generate for each strategy
        for strategy in DesignStrategy:
            logger.info(f"\n{'='*80}")
            logger.info(f"🔨 Generating {strategy.value.upper()} design...")
            logger.info(f"{'='*80}")
            
            design = self._generate_single_design(strategy)
            designs.append(design)
            
            logger.info(f"✅ {strategy.value.upper()} design completed:")
            logger.info(f"   Units: {design.total_units}")
            logger.info(f"   GFA: {design.volume.total_gfa:,.0f}㎡")
            logger.info(f"   Parking: {design.parking.provided_spots}")
        
        logger.info(f"\n{'='*80}")
        logger.info("🎉 All 3 designs generated successfully!")
        logger.info(f"{'='*80}\n")
        
        return designs
    
    def _generate_single_design(self, strategy: DesignStrategy) -> BuildingDesign:
        """
        단일 설계안 생성
        
        Args:
            strategy: 설계 전략
            
        Returns:
            BuildingDesign
        """
        # 1. Calculate buildable volume
        volume = self.zoning_engine.calculate_volume(strategy)
        logger.info(f"  📐 Volume: {volume.total_gfa:,.0f}㎡, {volume.max_units} units")
        
        # 2. Distribute units by LH standards
        unit_mix = self.unit_distributor.distribute(volume.max_units)
        logger.info(f"  🏠 Unit mix: {len(unit_mix)} types, {sum(u.count for u in unit_mix)} units")
        
        # 3. Calculate parking
        parking = self.parking_calculator.calculate(unit_mix, self.address)
        logger.info(f"  🚗 Parking: {parking.provided_spots} spots")
        
        # 4. Generate layout
        layout = self.geometry_engine.solve_layout(
            unit_mix, 
            volume.building_coverage,
            volume.floor_count
        )
        logger.info(f"  📐 Layout: {len(layout.blocks)} blocks")
        
        # 5. Calculate metrics
        metrics = self._calculate_metrics(volume, unit_mix, parking)
        logger.info(f"  📊 Metrics calculated")
        
        # 6. Create design object
        design_id = f"design_{strategy.value}_{uuid.uuid4().hex[:8]}"
        
        design = BuildingDesign(
            design_id=design_id,
            strategy=strategy,
            supply_type=self.supply_type,
            volume=volume,
            unit_mix=unit_mix,
            parking=parking,
            layout=layout,
            metrics=metrics
        )
        
        return design
    
    def _calculate_metrics(self, volume, unit_mix, parking) -> DesignMetrics:
        """
        설계 지표 계산
        
        Args:
            volume: BuildableVolume
            unit_mix: List[UnitType]
            parking: ParkingRequirement
            
        Returns:
            DesignMetrics
        """
        # 전용면적 합계
        total_exclusive = sum(u.total_area for u in unit_mix)
        
        # 전용률
        efficiency_ratio = total_exclusive / volume.total_gfa if volume.total_gfa > 0 else 0
        
        # E/S 비율 (서비스면적 / 전용면적)
        # 가정: 1층 상가 = 전체 건축면적의 5%
        service_area = volume.building_coverage * 0.05
        es_ratio = service_area / total_exclusive if total_exclusive > 0 else 0
        
        # 공용면적 비율
        common_area = volume.total_gfa - total_exclusive - service_area
        common_area_ratio = common_area / volume.total_gfa if volume.total_gfa > 0 else 0
        
        # 녹지율 (가정: 대지면적 - 건축면적의 30%를 녹지로)
        # 대지면적 추정 (건축면적 / 건폐율)
        estimated_site_area = volume.building_coverage / 0.6  # 건폐율 60% 가정
        green_area = (estimated_site_area - volume.building_coverage) * 0.3
        green_ratio = green_area / estimated_site_area if estimated_site_area > 0 else 0
        
        return DesignMetrics(
            efficiency_ratio=efficiency_ratio,
            es_ratio=es_ratio,
            common_area_ratio=common_area_ratio,
            green_ratio=green_ratio
        )
    
    def compare_designs(self, designs: List[BuildingDesign]) -> DesignComparisonResult:
        """
        설계안 비교
        
        Args:
            designs: List of BuildingDesign
            
        Returns:
            DesignComparisonResult
        """
        logger.info("📊 Comparing designs...")
        
        # Create comparison table
        comparison_table = {
            "strategies": [d.strategy.value for d in designs],
            "total_units": [d.total_units for d in designs],
            "total_gfa": [d.volume.total_gfa for d in designs],
            "parking_spots": [d.parking.provided_spots for d in designs],
            "efficiency_ratio": [d.metrics.efficiency_ratio for d in designs],
            "es_ratio": [d.metrics.es_ratio for d in designs],
            "green_ratio": [d.metrics.green_ratio for d in designs],
        }
        
        # Recommend based on balance
        # 표준형을 기본 추천
        recommended = DesignStrategy.STANDARD
        
        # If LH scores available, recommend highest
        scored_designs = [d for d in designs if d.lh_score is not None]
        if scored_designs:
            best_lh = max(scored_designs, key=lambda d: d.lh_score)
            recommended = best_lh.strategy
            logger.info(f"  💡 Recommended: {recommended.value} (Best LH score: {best_lh.lh_score})")
        else:
            logger.info(f"  💡 Recommended: {recommended.value} (Default)")
        
        return DesignComparisonResult(
            designs=designs,
            recommended=recommended,
            comparison_table=comparison_table
        )
    
    def generate_and_compare(self) -> DesignComparisonResult:
        """
        설계안 생성 및 비교 (원스톱)
        
        Returns:
            DesignComparisonResult
        """
        designs = self.generate()
        comparison = self.compare_designs(designs)
        return comparison
    
    def to_dict(self, designs: List[BuildingDesign]) -> Dict:
        """
        딕셔너리 변환 (API 응답용)
        
        Args:
            designs: List of BuildingDesign
            
        Returns:
            Dictionary
        """
        return {
            "address": self.address,
            "supply_type": self.supply_type.value,
            "land_area": self.land_params["area"],
            "generated_at": datetime.now().isoformat(),
            "designs": [d.to_dict() for d in designs],
            "design_count": len(designs)
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*80)
    print("🏗️ ZeroSite Phase 11: Design Generator Demo")
    print("="*80)
    
    # Test case: 서울 강남구 1000㎡ 대지
    address = "서울특별시 강남구 역삼동 123-45"
    land_params = {
        "area": 1000.0,  # 1000㎡
        "bcr": 60,  # 60%
        "far": 200,  # 200%
        "max_floors": 15,
        "zone_type": "제2종일반주거지역"
    }
    
    # Initialize generator
    generator = DesignGenerator(
        address=address,
        land_params=land_params,
        supply_type=SupplyType.NEWLYWED  # 신혼형
    )
    
    # Generate and compare
    comparison = generator.generate_and_compare()
    
    # Print results
    print("\n" + "="*80)
    print("📊 DESIGN COMPARISON RESULTS")
    print("="*80)
    
    print(f"\n🏠 Supply Type: {generator.supply_type.value}")
    print(f"📍 Address: {address}")
    print(f"📐 Land Area: {land_params['area']:,.0f}㎡")
    print(f"💡 Recommended: {comparison.recommended.value.upper()}")
    
    print("\n" + "-"*80)
    print("Comparison Table:")
    print("-"*80)
    
    table = comparison.comparison_table
    headers = ["Strategy", "Units", "GFA(㎡)", "Parking", "효율", "E/S", "녹지"]
    
    print(f"{'Strategy':<10} {'Units':<8} {'GFA(㎡)':<12} {'Parking':<8} {'효율':<8} {'E/S':<8} {'녹지':<8}")
    print("-"*80)
    
    for i, strategy in enumerate(table["strategies"]):
        print(
            f"{strategy:<10} "
            f"{table['total_units'][i]:<8} "
            f"{table['total_gfa'][i]:<12,.0f} "
            f"{table['parking_spots'][i]:<8} "
            f"{table['efficiency_ratio'][i]:<8.1%} "
            f"{table['es_ratio'][i]:<8.1%} "
            f"{table['green_ratio'][i]:<8.1%}"
        )
    
    print("\n" + "="*80)
    print("✅ Design generation completed successfully!")
    print("="*80)
    
    # Export to dict
    result_dict = generator.to_dict(comparison.designs)
    print(f"\n📄 Result exported: {len(str(result_dict))} characters")
