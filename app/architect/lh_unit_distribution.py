"""
ZeroSite Phase 11: LH Unit Distribution Engine

Distributes units according to LH housing supply standards:
- 22/30/42/50/58㎡ unit sizes
- Y/N/A/S/M supply types
- Official LH ratio guidelines

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

import logging
from typing import List, Dict
from .models import (
    UnitType, 
    SupplyType, 
    LH_UNIT_SIZES, 
    LH_DISTRIBUTION_RATIOS
)

logger = logging.getLogger(__name__)


class LHUnitDistributor:
    """
    LH 매입임대 기준 세대 배분 엔진
    
    Features:
    - 공급유형별 평형 구성 (Y/N/A/S/M)
    - 22/30/42/50/58㎡ 표준 평형
    - LH 권장 비율 적용
    """
    
    def __init__(self, supply_type: SupplyType):
        """
        Initialize distributor
        
        Args:
            supply_type: LH 공급유형 (Y/N/A/S/M)
        """
        self.supply_type = supply_type
        self.ratios = LH_DISTRIBUTION_RATIOS[supply_type]
        
        logger.info(f"📊 LH Unit Distributor initialized: {supply_type.value}")
    
    def distribute(self, total_units: int) -> List[UnitType]:
        """
        세대수 배분
        
        Args:
            total_units: 총 세대수
            
        Returns:
            List of UnitType with distribution
        """
        logger.info(f"🏗️ Distributing {total_units} units for type {self.supply_type.value}")
        
        unit_mix = []
        allocated_count = 0
        
        # 비율에 따라 배분
        for unit_name, ratio in self.ratios.items():
            if ratio == 0:
                continue
            
            count = int(total_units * ratio)
            
            if count > 0:
                unit_type = UnitType(
                    size_sqm=LH_UNIT_SIZES[unit_name],
                    count=count,
                    name=unit_name
                )
                unit_mix.append(unit_type)
                allocated_count += count
        
        # 나머지 세대는 가장 많은 비율을 가진 평형에 배정
        remaining = total_units - allocated_count
        if remaining > 0 and unit_mix:
            # 비율이 가장 높은 평형 찾기
            max_ratio_unit = max(self.ratios.items(), key=lambda x: x[1])
            max_unit_name = max_ratio_unit[0]
            
            # 해당 평형에 나머지 추가
            for unit in unit_mix:
                if unit.name == max_unit_name:
                    unit.count += remaining
                    logger.info(f"  ➕ Added {remaining} remaining units to {max_unit_name}")
                    break
        
        # 결과 로깅
        for unit in unit_mix:
            logger.info(
                f"  ✅ {unit.name} ({unit.size_sqm}㎡): {unit.count}세대 "
                f"({unit.count/total_units*100:.1f}%)"
            )
        
        return unit_mix
    
    def get_distribution_summary(self, total_units: int) -> Dict:
        """
        배분 요약 정보
        
        Args:
            total_units: 총 세대수
            
        Returns:
            Summary dictionary
        """
        unit_mix = self.distribute(total_units)
        
        return {
            "supply_type": self.supply_type.value,
            "total_units": total_units,
            "unit_mix": [
                {
                    "name": u.name,
                    "size_sqm": u.size_sqm,
                    "count": u.count,
                    "ratio": u.count / total_units,
                    "total_area": u.total_area
                }
                for u in unit_mix
            ],
            "total_exclusive_area": sum(u.total_area for u in unit_mix),
            "average_unit_size": sum(u.total_area for u in unit_mix) / total_units
        }
    
    @staticmethod
    def recommend_supply_type(address: str, context: Dict = None) -> SupplyType:
        """
        입지 기반 공급유형 추천
        
        Args:
            address: 주소
            context: 추가 컨텍스트 (역세권, POI 등)
            
        Returns:
            Recommended SupplyType
        """
        # Simple heuristics (Phase 6 Demand Engine과 연계 예정)
        
        if context is None:
            context = {}
        
        # 대학가 키워드
        university_keywords = ["대학", "학교", "캠퍼스"]
        if any(kw in address for kw in university_keywords):
            logger.info("🎓 University area detected → YOUTH type")
            return SupplyType.YOUTH
        
        # 역세권
        station_keywords = ["역", "지하철"]
        if any(kw in address for kw in station_keywords):
            if context.get("has_school", False):
                logger.info("👨‍👩‍👧 Station + School → NEWLYWED type")
                return SupplyType.NEWLYWED
            else:
                logger.info("🚇 Station area → MIXED type")
                return SupplyType.MIXED
        
        # 고령자 밀집 지역
        senior_keywords = ["요양", "노인", "실버"]
        if any(kw in address for kw in senior_keywords):
            logger.info("👴 Senior area detected → SENIOR type")
            return SupplyType.SENIOR
        
        # 기본값: 일반형
        logger.info("🏘️ Default → GENERAL type")
        return SupplyType.GENERAL
    
    def validate_mix(self, unit_mix: List[UnitType]) -> Dict:
        """
        평형 구성 검증
        
        Args:
            unit_mix: 세대 구성
            
        Returns:
            Validation result
        """
        issues = []
        warnings = []
        
        total_units = sum(u.count for u in unit_mix)
        
        # 1. 최소 세대수 검증 (LH 기준: 최소 20세대)
        if total_units < 20:
            issues.append(f"총 세대수 부족: {total_units}세대 (최소 20세대 필요)")
        
        # 2. 평형별 비율 검증
        for unit in unit_mix:
            ratio = unit.count / total_units
            expected_ratio = self.ratios.get(unit.name, 0)
            
            if abs(ratio - expected_ratio) > 0.05:  # 5% 이상 차이
                warnings.append(
                    f"{unit.name}: 실제 {ratio*100:.1f}%, "
                    f"권장 {expected_ratio*100:.1f}% (차이 {abs(ratio-expected_ratio)*100:.1f}%p)"
                )
        
        # 3. 대형 평형 과다 검증 (58㎡)
        large_units = sum(u.count for u in unit_mix if u.size_sqm >= 55)
        if large_units / total_units > 0.30:
            warnings.append(
                f"대형 평형(55㎡ 이상) 비중 높음: {large_units/total_units*100:.1f}% "
                f"(권장 30% 이하)"
            )
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_units": total_units,
            "summary": f"{'✅ 검증 통과' if len(issues) == 0 else '❌ 검증 실패'}"
        }


# Convenience functions

def create_distributor(supply_type: SupplyType) -> LHUnitDistributor:
    """Create distributor instance"""
    return LHUnitDistributor(supply_type)


def quick_distribute(supply_type: SupplyType, total_units: int) -> List[UnitType]:
    """Quick distribution"""
    distributor = create_distributor(supply_type)
    return distributor.distribute(total_units)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "="*80)
    print("🏗️ LH Unit Distribution Test")
    print("="*80)
    
    # Test all supply types
    test_cases = [
        (SupplyType.YOUTH, 100, "청년형 100세대"),
        (SupplyType.NEWLYWED, 120, "신혼형 120세대"),
        (SupplyType.GENERAL, 150, "일반형 150세대"),
        (SupplyType.SENIOR, 80, "고령형 80세대"),
        (SupplyType.MIXED, 110, "혼합형 110세대"),
    ]
    
    for supply_type, units, desc in test_cases:
        print(f"\n📊 Test: {desc}")
        print("-" * 80)
        
        distributor = create_distributor(supply_type)
        unit_mix = distributor.distribute(units)
        
        # Validation
        validation = distributor.validate_mix(unit_mix)
        print(f"\n{validation['summary']}")
        if validation['warnings']:
            for warning in validation['warnings']:
                print(f"  ⚠️ {warning}")
    
    print("\n" + "="*80)
    print("✅ All tests completed")
    print("="*80)
