"""
ZeroSite Phase 11: Zoning Rules Engine

Calculates buildable volume based on zoning regulations.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

import logging
from typing import Dict, List
from .models import BuildableVolume, DesignStrategy

logger = logging.getLogger(__name__)


class ZoningRuleEngine:
    """
    법규 기반 건축 규모 산정 엔진
    
    Features:
    - 건폐율/용적률 기반 규모 계산
    - 전략별 multiplier 적용
    - 층수/높이 제한 반영
    """
    
    # 전략별 적용률
    STRATEGY_MULTIPLIERS = {
        DesignStrategy.STABLE: 0.85,  # 안정형: 85% 사용
        DesignStrategy.STANDARD: 0.95,  # 표준형: 95% 사용
        DesignStrategy.PROFIT: 1.00,  # 수익형: 100% 사용
    }
    
    # 평균 세대 면적 (전용면적 기준, 전용률 75% 가정)
    AVG_UNIT_SIZE = 35  # 35㎡ 전용면적
    EFFICIENCY_RATIO = 0.75  # 전용률 75%
    
    def __init__(self, land_params: Dict):
        """
        Initialize zoning engine
        
        Args:
            land_params: {
                "area": 대지면적 (㎡),
                "bcr": 건폐율 (%),
                "far": 용적률 (%),
                "max_floors": 최고층수 (선택),
                "max_height": 최고높이 (m, 선택)
            }
        """
        self.land_area = land_params["area"]
        self.bcr = land_params["bcr"] / 100  # % -> 소수
        self.far = land_params["far"] / 100  # % -> 소수
        self.max_floors = land_params.get("max_floors", 15)  # 기본 15층
        self.max_height = land_params.get("max_height", 45.0)  # 기본 45m
        
        logger.info(
            f"🏗️ Zoning Engine initialized: "
            f"{self.land_area}㎡, BCR:{self.bcr*100}%, FAR:{self.far*100}%"
        )
    
    def calculate_volume(self, strategy: DesignStrategy) -> BuildableVolume:
        """
        건축 가능 규모 계산
        
        Args:
            strategy: 설계 전략
            
        Returns:
            BuildableVolume
        """
        logger.info(f"📐 Calculating volume for strategy: {strategy.value}")
        
        # 1. 건축면적 (건폐율 기준)
        building_coverage = self.land_area * self.bcr
        
        # 2. 연면적 (용적률 기준)
        max_gfa = self.land_area * self.far
        
        # 3. 전략별 적용률
        multiplier = self.STRATEGY_MULTIPLIERS[strategy]
        target_gfa = max_gfa * multiplier
        
        # 4. 층수 계산
        floor_count = min(
            int(target_gfa / building_coverage),
            self.max_floors
        )
        
        # 실제 연면적 조정
        actual_gfa = building_coverage * floor_count
        
        # 5. 세대수 추정
        # 전용면적 = 연면적 × 전용률
        total_exclusive_area = actual_gfa * self.EFFICIENCY_RATIO
        max_units = int(total_exclusive_area / self.AVG_UNIT_SIZE)
        
        logger.info(
            f"  ✅ GFA: {actual_gfa:,.0f}㎡, "
            f"Units: {max_units}, "
            f"Floors: {floor_count}, "
            f"Multiplier: {multiplier}"
        )
        
        return BuildableVolume(
            total_gfa=actual_gfa,
            max_units=max_units,
            building_coverage=building_coverage,
            floor_count=floor_count,
            strategy=strategy
        )
    
    def calculate_all_scenarios(self) -> Dict[DesignStrategy, BuildableVolume]:
        """
        모든 전략에 대한 규모 계산
        
        Returns:
            Dict of strategy -> BuildableVolume
        """
        results = {}
        
        for strategy in DesignStrategy:
            results[strategy] = self.calculate_volume(strategy)
        
        return results
    
    def validate_volume(self, volume: BuildableVolume) -> Dict:
        """
        규모 적법성 검증
        
        Args:
            volume: 건축 규모
            
        Returns:
            Validation result
        """
        issues = []
        warnings = []
        
        # 1. 용적률 검증
        actual_far = volume.total_gfa / self.land_area
        if actual_far > self.far * 1.01:  # 1% 여유
            issues.append(
                f"용적률 초과: {actual_far*100:.1f}% > {self.far*100:.0f}%"
            )
        
        # 2. 건폐율 검증
        actual_bcr = volume.building_coverage / self.land_area
        if actual_bcr > self.bcr * 1.01:
            issues.append(
                f"건폐율 초과: {actual_bcr*100:.1f}% > {self.bcr*100:.0f}%"
            )
        
        # 3. 층수 검증
        if volume.floor_count > self.max_floors:
            issues.append(
                f"층수 초과: {volume.floor_count}층 > {self.max_floors}층"
            )
        
        # 4. 효율성 경고
        efficiency = volume.total_gfa / (self.land_area * self.far)
        if efficiency < 0.80:
            warnings.append(
                f"용적률 활용 낮음: {efficiency*100:.1f}% (80% 미만)"
            )
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "summary": f"{'✅ 법규 적합' if len(issues) == 0 else '❌ 법규 위반'}"
        }
    
    def get_recommendations(self, strategy: DesignStrategy) -> List[str]:
        """
        규모 최적화 권장사항
        
        Args:
            strategy: 설계 전략
            
        Returns:
            List of recommendations
        """
        volume = self.calculate_volume(strategy)
        recommendations = []
        
        # 용적률 활용도
        efficiency = volume.total_gfa / (self.land_area * self.far)
        
        if efficiency < 0.85 and strategy == DesignStrategy.PROFIT:
            recommendations.append(
                f"💡 용적률 {(1-efficiency)*100:.1f}% 추가 활용 가능 "
                f"(약 {int((self.land_area * self.far * (1-efficiency))/100)}세대 증가)"
            )
        
        if efficiency > 0.95 and strategy == DesignStrategy.STABLE:
            recommendations.append(
                "💡 안정형 전략에서 용적률 95% 이상 사용 → 점수 하락 우려"
            )
        
        # 층수 최적화
        if volume.floor_count < 5:
            recommendations.append(
                "⚠️ 저층 건물 → 엘리베이터 비용 효율 낮음"
            )
        elif volume.floor_count > 12:
            recommendations.append(
                "💡 12층 이상 → 피난 설비 추가 비용 발생"
            )
        
        if not recommendations:
            recommendations.append("✅ 최적 규모")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*80)
    print("🏗️ Zoning Rules Engine Test")
    print("="*80)
    
    # Test case
    land_params = {
        "area": 1000.0,  # 1000㎡
        "bcr": 60,  # 60%
        "far": 200,  # 200%
        "max_floors": 15,
    }
    
    engine = ZoningRuleEngine(land_params)
    
    # Calculate all scenarios
    print("\n📊 All Scenarios:")
    print("-" * 80)
    
    for strategy in DesignStrategy:
        volume = engine.calculate_volume(strategy)
        
        print(f"\n{strategy.value.upper()} Strategy:")
        print(f"  GFA: {volume.total_gfa:,.0f}㎡")
        print(f"  Max Units: {volume.max_units}")
        print(f"  Floors: {volume.floor_count}")
        print(f"  Building Coverage: {volume.building_coverage:,.0f}㎡")
        
        # Validate
        validation = engine.validate_volume(volume)
        print(f"  {validation['summary']}")
        
        # Recommendations
        recommendations = engine.get_recommendations(strategy)
        for rec in recommendations:
            print(f"  {rec}")
    
    print("\n" + "="*80)
    print("✅ Zoning tests completed")
    print("="*80)
