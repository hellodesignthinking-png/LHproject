"""
ZeroSite Phase 11: Parking Calculator

Calculates parking requirements based on LH standards and local regulations.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

import logging
from typing import List, Dict
from .models import UnitType, ParkingRequirement

logger = logging.getLogger(__name__)


class ParkingCalculator:
    """
    주차 계산 엔진
    
    Features:
    - LH 매입임대 주차 기준
    - 지역별 차등 적용 (서울/비서울)
    - 장애인 주차 자동 계산
    - 지상/지하 배분
    """
    
    # LH 주차 기준 (세대당 주차대수)
    LH_PARKING_RATIO = {
        "seoul": 0.5,  # 서울: 2세대당 1대
        "gyeonggi": 0.7,  # 경기: 1.5세대당 1대
        "metro": 0.6,  # 광역시: 1.7세대당 1대
        "other": 0.8,  # 기타: 1.3세대당 1대
    }
    
    # 장애인 주차 비율 (전체 주차의 %)
    DISABLED_PARKING_RATIO = 0.03  # 3%
    
    # 지하 주차 비율 (전체 주차의 %)
    UNDERGROUND_RATIO = 0.80  # 80%
    
    def __init__(self):
        """Initialize parking calculator"""
        logger.info("🚗 Parking Calculator initialized")
    
    def calculate(
        self, 
        unit_mix: List[UnitType], 
        address: str,
        region_type: str = None
    ) -> ParkingRequirement:
        """
        주차 계산
        
        Args:
            unit_mix: 세대 구성
            address: 주소
            region_type: 지역 구분 (seoul/gyeonggi/metro/other)
            
        Returns:
            ParkingRequirement
        """
        total_units = sum(u.count for u in unit_mix)
        
        # 지역 자동 판별
        if region_type is None:
            region_type = self._detect_region(address)
        
        logger.info(f"🚗 Calculating parking for {total_units} units in {region_type}")
        
        # 기본 주차대수 계산
        base_ratio = self.LH_PARKING_RATIO[region_type]
        required_spots = max(1, int(total_units * base_ratio))
        
        # LH 기준: 최소 확보율 100% + 여유분 5%
        provided_spots = int(required_spots * 1.05)
        
        # 장애인 주차
        disabled_spots = max(1, int(provided_spots * self.DISABLED_PARKING_RATIO))
        
        # 지상/지하 배분
        underground_spots = int(provided_spots * self.UNDERGROUND_RATIO)
        surface_spots = provided_spots - underground_spots
        
        logger.info(
            f"  ✅ Required: {required_spots}, "
            f"Provided: {provided_spots}, "
            f"Underground: {underground_spots}, "
            f"Surface: {surface_spots}, "
            f"Disabled: {disabled_spots}"
        )
        
        return ParkingRequirement(
            required_spots=required_spots,
            provided_spots=provided_spots,
            underground_spots=underground_spots,
            surface_spots=surface_spots,
            disabled_spots=disabled_spots
        )
    
    def _detect_region(self, address: str) -> str:
        """
        주소에서 지역 구분 자동 판별
        
        Args:
            address: 주소
            
        Returns:
            Region type (seoul/gyeonggi/metro/other)
        """
        if "서울" in address or "서울특별시" in address:
            return "seoul"
        elif "경기" in address or "경기도" in address:
            return "gyeonggi"
        elif any(city in address for city in ["부산", "대구", "인천", "광주", "대전", "울산"]):
            return "metro"
        else:
            return "other"
    
    def calculate_cost(
        self, 
        parking: ParkingRequirement,
        cost_per_underground: float = 30_000_000,  # 지하 주차 1대당 3천만원
        cost_per_surface: float = 5_000_000  # 지상 주차 1대당 500만원
    ) -> Dict:
        """
        주차 공사비 계산
        
        Args:
            parking: 주차 요구사항
            cost_per_underground: 지하 주차 단가
            cost_per_surface: 지상 주차 단가
            
        Returns:
            Cost breakdown
        """
        underground_cost = parking.underground_spots * cost_per_underground
        surface_cost = parking.surface_spots * cost_per_surface
        total_cost = underground_cost + surface_cost
        
        return {
            "underground_cost": underground_cost,
            "surface_cost": surface_cost,
            "total_cost": total_cost,
            "cost_per_spot": total_cost / parking.provided_spots if parking.provided_spots > 0 else 0,
            "breakdown": {
                "underground": {
                    "spots": parking.underground_spots,
                    "unit_cost": cost_per_underground,
                    "total": underground_cost
                },
                "surface": {
                    "spots": parking.surface_spots,
                    "unit_cost": cost_per_surface,
                    "total": surface_cost
                }
            }
        }
    
    def validate_compliance(
        self, 
        parking: ParkingRequirement,
        strict_mode: bool = True
    ) -> Dict:
        """
        주차 기준 적합성 검증
        
        Args:
            parking: 주차 요구사항
            strict_mode: 엄격 모드 (LH 제출용)
            
        Returns:
            Validation result
        """
        issues = []
        warnings = []
        
        # 1. 기본 확보율 검증
        if parking.compliance_rate < 1.0:
            issues.append(
                f"법정 주차대수 미달: {parking.provided_spots}/{parking.required_spots} "
                f"({parking.compliance_rate*100:.1f}%)"
            )
        elif parking.compliance_rate < 1.05 and strict_mode:
            warnings.append("여유분 부족: LH 기준 5% 이상 권장")
        
        # 2. 장애인 주차 검증
        min_disabled = max(1, int(parking.provided_spots * 0.02))
        if parking.disabled_spots < min_disabled:
            issues.append(
                f"장애인 주차 부족: {parking.disabled_spots}/{min_disabled} "
                f"(최소 2% 필요)"
            )
        
        # 3. 지하 주차 비율 검증
        if parking.provided_spots > 0:
            underground_ratio = parking.underground_spots / parking.provided_spots
            if underground_ratio < 0.70 and strict_mode:
                warnings.append(
                    f"지하 주차 비중 낮음: {underground_ratio*100:.1f}% "
                    f"(권장 70% 이상)"
                )
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "compliance_rate": parking.compliance_rate,
            "summary": f"{'✅ 기준 충족' if len(issues) == 0 else '❌ 기준 미달'}"
        }
    
    def get_recommendations(
        self, 
        parking: ParkingRequirement,
        unit_mix: List[UnitType]
    ) -> List[str]:
        """
        주차 개선 권장사항
        
        Args:
            parking: 현재 주차 계획
            unit_mix: 세대 구성
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # 확보율 체크
        if parking.compliance_rate < 1.0:
            shortfall = parking.required_spots - parking.provided_spots
            recommendations.append(
                f"⚠️ 주차대수 {shortfall}대 추가 필요"
            )
        
        # 지하 주차 비율 체크
        if parking.provided_spots > 0:
            underground_ratio = parking.underground_spots / parking.provided_spots
            if underground_ratio < 0.70:
                add_underground = int(parking.provided_spots * 0.70) - parking.underground_spots
                recommendations.append(
                    f"💡 지하 주차 {add_underground}대 추가 권장 (LH 평가 점수 향상)"
                )
        
        # 세대수 대비 주차 과다 체크
        total_units = sum(u.count for u in unit_mix)
        if parking.compliance_rate > 1.2:
            recommendations.append(
                "💡 주차 여유분 많음 → 공사비 절감 가능"
            )
        
        if not recommendations:
            recommendations.append("✅ 주차 계획 적정")
        
        return recommendations


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    from .lh_unit_distribution import quick_distribute
    from .models import SupplyType
    
    print("\n" + "="*80)
    print("🚗 Parking Calculator Test")
    print("="*80)
    
    # Test cases
    test_cases = [
        ("서울특별시 강남구 역삼동 123", SupplyType.YOUTH, 100),
        ("경기도 성남시 분당구 판교동", SupplyType.NEWLYWED, 120),
        ("부산광역시 해운대구 우동", SupplyType.SENIOR, 80),
    ]
    
    calculator = ParkingCalculator()
    
    for address, supply_type, units in test_cases:
        print(f"\n📍 Location: {address}")
        print(f"   Type: {supply_type.value}, Units: {units}")
        print("-" * 80)
        
        # Create unit mix
        unit_mix = quick_distribute(supply_type, units)
        
        # Calculate parking
        parking = calculator.calculate(unit_mix, address)
        print(f"  Required: {parking.required_spots}")
        print(f"  Provided: {parking.provided_spots}")
        print(f"  Compliance: {parking.compliance_rate*100:.1f}%")
        
        # Calculate cost
        cost = calculator.calculate_cost(parking)
        print(f"  Total Cost: ₩{cost['total_cost']:,.0f}")
        print(f"  Cost per Spot: ₩{cost['cost_per_spot']:,.0f}")
        
        # Validate
        validation = calculator.validate_compliance(parking)
        print(f"\n  {validation['summary']}")
        
        # Recommendations
        recommendations = calculator.get_recommendations(parking, unit_mix)
        for rec in recommendations:
            print(f"  {rec}")
    
    print("\n" + "="*80)
    print("✅ All parking tests completed")
    print("="*80)
