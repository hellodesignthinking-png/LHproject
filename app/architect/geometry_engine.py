"""
ZeroSite Phase 11: Geometry Engine

Simple layout generation for building blocks.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

import logging
import math
from typing import List, Dict
from .models import UnitType, GeometryLayout

logger = logging.getLogger(__name__)


class GeometryEngine:
    """
    건축 형상 및 배치 엔진
    
    Features:
    - 단순 블록 레이아웃 생성
    - 세대 배치 최적화
    - SVG 출력
    """
    
    def __init__(self):
        """Initialize geometry engine"""
        logger.info("📐 Geometry Engine initialized")
    
    def solve_layout(
        self, 
        unit_mix: List[UnitType],
        building_coverage: float,
        floor_count: int
    ) -> GeometryLayout:
        """
        레이아웃 생성
        
        Args:
            unit_mix: 세대 구성
            building_coverage: 건축면적 (㎡)
            floor_count: 층수
            
        Returns:
            GeometryLayout
        """
        logger.info(
            f"📐 Solving layout for {sum(u.count for u in unit_mix)} units, "
            f"{building_coverage}㎡ footprint"
        )
        
        # 단순 직사각형 블록 배치
        # 가정: 각 세대는 대략 정사각형
        
        total_units = sum(u.count for u in unit_mix)
        units_per_floor = max(1, total_units // floor_count)
        
        # 각 층당 필요한 면적
        floor_area = building_coverage
        
        # 블록 크기 추정 (정사각형 가정)
        block_size = math.sqrt(floor_area)
        
        # 단순 배치: 1개의 큰 블록
        blocks = [
            {
                "x": 0,
                "y": 0,
                "width": block_size,
                "height": block_size,
                "floors": floor_count,
                "units_per_floor": units_per_floor
            }
        ]
        
        # 대지 면적 대비 건축면적 비율 (건폐율)
        # 가정: 대지면적 = 건축면적 / 0.6 (건폐율 60% 가정)
        estimated_site_area = building_coverage / 0.6
        site_coverage_ratio = building_coverage / estimated_site_area
        
        logger.info(
            f"  ✅ Layout: 1 block, {block_size:.1f}m × {block_size:.1f}m, "
            f"{floor_count} floors"
        )
        
        return GeometryLayout(
            blocks=blocks,
            total_footprint=building_coverage,
            site_coverage_ratio=site_coverage_ratio
        )
    
    def calculate_unit_positions(
        self, 
        unit_mix: List[UnitType],
        layout: GeometryLayout
    ) -> List[Dict]:
        """
        세대별 위치 계산
        
        Args:
            unit_mix: 세대 구성
            layout: 레이아웃
            
        Returns:
            List of unit positions
        """
        positions = []
        
        # 단순 구현: 층별로 균등 배분
        total_units = sum(u.count for u in unit_mix)
        
        if not layout.blocks:
            return positions
        
        block = layout.blocks[0]
        floors = block.get("floors", 1)
        units_per_floor = total_units // floors
        
        unit_index = 0
        for unit_type in unit_mix:
            for i in range(unit_type.count):
                floor = unit_index // units_per_floor
                position_in_floor = unit_index % units_per_floor
                
                positions.append({
                    "unit_index": unit_index,
                    "unit_type": unit_type.name,
                    "size": unit_type.size_sqm,
                    "floor": floor + 1,  # 1층부터 시작
                    "position": position_in_floor
                })
                
                unit_index += 1
        
        return positions
    
    def optimize_orientation(
        self, 
        layout: GeometryLayout,
        context: Dict = None
    ) -> Dict:
        """
        배치 방향 최적화
        
        Args:
            layout: 레이아웃
            context: 주변 환경 정보
            
        Returns:
            Optimization result
        """
        if context is None:
            context = {}
        
        recommendations = []
        
        # 일조권 고려
        if context.get("north_open", False):
            recommendations.append("💡 남향 배치 권장 (일조권 우수)")
        
        # 도로 접면
        road_direction = context.get("road_direction", "south")
        recommendations.append(f"🚗 도로 접면: {road_direction}")
        
        # 조망
        if context.get("has_view", False):
            recommendations.append("🌄 조망 고려 배치 가능")
        
        return {
            "recommendations": recommendations,
            "optimal_rotation": 0,  # 0도 (남향)
            "adjustments": []
        }
    
    def validate_layout(self, layout: GeometryLayout) -> Dict:
        """
        레이아웃 검증
        
        Args:
            layout: 레이아웃
            
        Returns:
            Validation result
        """
        issues = []
        warnings = []
        
        # 1. 건폐율 검증
        if layout.site_coverage_ratio > 0.7:
            warnings.append(
                f"건폐율 높음: {layout.site_coverage_ratio*100:.1f}% "
                f"(녹지 공간 부족 우려)"
            )
        
        # 2. 블록 개수
        if len(layout.blocks) == 0:
            issues.append("블록 없음")
        
        # 3. 비정상적 크기
        for i, block in enumerate(layout.blocks):
            width = block.get("width", 0)
            height = block.get("height", 0)
            
            if width < 10 or height < 10:
                issues.append(
                    f"블록 {i+1} 크기 비정상: {width}m × {height}m "
                    f"(최소 10m × 10m 필요)"
                )
            
            if width > 100 or height > 100:
                warnings.append(
                    f"블록 {i+1} 크기 과대: {width}m × {height}m "
                    f"(소방/피난 문제 발생 가능)"
                )
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "summary": f"{'✅ 레이아웃 적정' if len(issues) == 0 else '❌ 레이아웃 문제'}"
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from .lh_unit_distribution import quick_distribute
    from .models import SupplyType
    
    print("\n" + "="*80)
    print("📐 Geometry Engine Test")
    print("="*80)
    
    # Test case
    unit_mix = quick_distribute(SupplyType.NEWLYWED, 120)
    building_coverage = 600.0  # 600㎡
    floor_count = 10
    
    engine = GeometryEngine()
    
    # Solve layout
    layout = engine.solve_layout(unit_mix, building_coverage, floor_count)
    
    print(f"\n📊 Layout Result:")
    print(f"  Blocks: {len(layout.blocks)}")
    print(f"  Footprint: {layout.total_footprint:.0f}㎡")
    print(f"  Site Coverage: {layout.site_coverage_ratio*100:.1f}%")
    
    # Generate SVG
    svg = layout.to_svg()
    print(f"\n📄 SVG Generated: {len(svg)} characters")
    
    # Calculate positions
    positions = engine.calculate_unit_positions(unit_mix, layout)
    print(f"\n🏠 Unit Positions: {len(positions)} units")
    for pos in positions[:5]:  # First 5
        print(f"  Unit {pos['unit_index']}: {pos['unit_type']} on Floor {pos['floor']}")
    
    # Validate
    validation = engine.validate_layout(layout)
    print(f"\n{validation['summary']}")
    for warning in validation.get('warnings', []):
        print(f"  ⚠️ {warning}")
    
    # Optimize orientation
    context = {"north_open": True, "road_direction": "south"}
    optimization = engine.optimize_orientation(layout, context)
    print(f"\n🧭 Orientation Optimization:")
    for rec in optimization['recommendations']:
        print(f"  {rec}")
    
    print("\n" + "="*80)
    print("✅ Geometry tests completed")
    print("="*80)
