"""
Unit Estimator Service for ZeroSite v9.1

Provides automatic household unit calculation:
- Total unit count estimation
- Floor count calculation
- Parking space calculation
- Unit type distribution
- GFA (Gross Floor Area) breakdown

Based on Korean building standards and LH construction guidelines.

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

import logging
from typing import Optional, Dict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class UnitEstimate:
    """
    세대수 산정 결과
    
    Attributes:
        total_units: 총 세대수
        total_gfa: 연면적 (m²)
        residential_gfa: 주거 전용 면적 (m²)
        commercial_gfa: 부대시설 면적 (m²)
        building_footprint: 건축 면적 (m²)
        floors: 층수
        units_per_floor: 층별 세대수
        parking_spaces: 법정 주차 대수
        unit_type_distribution: 세대 유형별 배분
        avg_unit_area: 세대당 평균 면적 (m²)
        calculation_method: 계산 방법
    """
    total_units: int
    total_gfa: float
    residential_gfa: float
    commercial_gfa: float
    building_footprint: float
    floors: int
    units_per_floor: int
    parking_spaces: int
    unit_type_distribution: Dict[str, int] = field(default_factory=dict)
    avg_unit_area: float = 60.0
    calculation_method: str = "auto"


class UnitEstimatorV9:
    """
    자동 세대수 산정 엔진
    
    Features:
    - 용적률 기반 연면적 계산
    - 세대 유형별 면적 배분
    - 층수 및 층별 세대수 계산
    - 주차 대수 자동 계산
    - 건축 가능성 검증
    
    Based On:
    - 건축법 (건축물의 건폐율, 용적률)
    - 주차장법 (주차 기준)
    - LH 신축매입임대 기준 (세대수, 면적)
    
    Usage:
        estimator = UnitEstimatorV9()
        estimate = estimator.estimate_units(
            land_area=1000.0,
            floor_area_ratio=300.0,
            building_coverage_ratio=50.0
        )
        
        print(estimate.total_units)    # 28
        print(estimate.floors)          # 6
        print(estimate.parking_spaces)  # 28
    """
    
    # LH 신축매입임대 기준
    DEFAULT_UNIT_AREA = 60.0  # m² (약 18평)
    MIN_UNIT_AREA = 45.0      # m² (최소 전용면적)
    MAX_UNIT_AREA = 85.0      # m² (최대 전용면적)
    
    # 부대시설 비율 (상가, 관리사무소, 주민공동시설 등)
    COMMERCIAL_RATIO = 0.15   # 15%
    RESIDENTIAL_RATIO = 0.85  # 85%
    
    # 세대 유형별 면적 (m²)
    UNIT_TYPES = {
        "59㎡": 59.0,  # 약 18평
        "74㎡": 74.0,  # 약 22평
        "84㎡": 84.0   # 약 25평
    }
    
    # 세대 유형별 기본 배분 비율
    DEFAULT_UNIT_MIX = {
        "59㎡": 0.6,   # 60%
        "74㎡": 0.3,   # 30%
        "84㎡": 0.1    # 10%
    }
    
    def __init__(self):
        """Initialize UnitEstimatorV9"""
        logger.info("✅ UnitEstimatorV9 initialized")
    
    def estimate_units(
        self,
        land_area: float,
        floor_area_ratio: float,
        building_coverage_ratio: float,
        unit_type_mix: Optional[Dict[str, float]] = None,
        parking_ratio: float = 1.0
    ) -> UnitEstimate:
        """
        자동 세대수 산정
        
        Process:
        1. 연면적 계산 = 대지면적 × 용적률
        2. 주거 전용 면적 계산 = 연면적 × 85% (부대시설 15% 제외)
        3. 세대수 산정 = 주거 전용 면적 ÷ 세대당 평균 면적
        4. 층수 계산 = 연면적 ÷ 건축 면적
        5. 주차 대수 = 세대수 × 주차 비율
        
        Args:
            land_area: 대지 면적 (m²)
            floor_area_ratio: 용적률 (%)
            building_coverage_ratio: 건폐율 (%)
            unit_type_mix: 세대 유형 비율 (선택)
                {
                    "59㎡": 0.6,  # 60%
                    "74㎡": 0.3,  # 30%
                    "84㎡": 0.1   # 10%
                }
            parking_ratio: 주차 비율 (세대당 대수, 기본 1.0)
        
        Returns:
            UnitEstimate: 세대수 산정 결과
                - total_units: 총 세대수
                - total_gfa: 연면적
                - residential_gfa: 주거 전용 면적
                - commercial_gfa: 부대시설 면적
                - building_footprint: 건축 면적
                - floors: 층수
                - units_per_floor: 층별 세대수
                - parking_spaces: 주차 대수
                - unit_type_distribution: 세대 유형별 배분
        
        Example:
            >>> estimator = UnitEstimatorV9()
            >>> result = estimator.estimate_units(
            ...     land_area=1000.0,
            ...     floor_area_ratio=300.0,
            ...     building_coverage_ratio=50.0
            ... )
            >>> print(result.total_units)
            42
            >>> print(result.floors)
            6
        """
        logger.info(
            f"📊 세대수 자동 산정 시작\n"
            f"   대지면적: {land_area:.2f} m²\n"
            f"   용적률: {floor_area_ratio:.1f}%\n"
            f"   건폐율: {building_coverage_ratio:.1f}%"
        )
        
        # 1. 연면적 계산
        total_gfa = land_area * (floor_area_ratio / 100.0)
        logger.info(f"   연면적: {total_gfa:.2f} m²")
        
        # 2. 건축 면적 계산
        building_footprint = land_area * (building_coverage_ratio / 100.0)
        logger.info(f"   건축면적: {building_footprint:.2f} m²")
        
        # 3. 주거 전용 면적 (부대시설 15% 제외)
        residential_gfa = total_gfa * self.RESIDENTIAL_RATIO
        commercial_gfa = total_gfa * self.COMMERCIAL_RATIO
        logger.info(f"   주거 전용 면적: {residential_gfa:.2f} m²")
        logger.info(f"   부대시설 면적: {commercial_gfa:.2f} m²")
        
        # 4. 세대당 평균 면적 계산
        if unit_type_mix:
            avg_unit_area = self._calculate_avg_unit_area(unit_type_mix)
        else:
            avg_unit_area = self.DEFAULT_UNIT_AREA
        
        logger.info(f"   세대당 평균 면적: {avg_unit_area:.2f} m²")
        
        # 5. 추정 세대수
        estimated_units = int(residential_gfa / avg_unit_area)
        
        # 최소값 검증 (최소 10세대)
        if estimated_units < 10:
            logger.warning(f"⚠️ 세대수가 너무 적음: {estimated_units}세대 → 최소 10세대로 조정")
            estimated_units = 10
        
        logger.info(f"   ✅ 추정 세대수: {estimated_units}세대")
        
        # 6. 층수 계산
        if building_footprint > 0:
            floors = int(total_gfa / building_footprint)
            # 최소 2층, 최대 20층
            floors = max(2, min(floors, 20))
        else:
            floors = 5  # 기본값
        
        logger.info(f"   층수: {floors}층")
        
        # 7. 층별 세대수
        units_per_floor = int(estimated_units / floors) if floors > 0 else 0
        
        # 최소값 검증 (층별 최소 2세대)
        if units_per_floor < 2:
            units_per_floor = 2
        
        logger.info(f"   층별 세대수: {units_per_floor}세대/층")
        
        # 8. 주차 대수 (세대당 1대)
        parking_spaces = int(estimated_units * parking_ratio)
        logger.info(f"   주차 대수: {parking_spaces}대")
        
        # 9. 세대 유형별 배분
        if not unit_type_mix:
            unit_type_mix = self.DEFAULT_UNIT_MIX
        
        unit_type_distribution = self._distribute_units(estimated_units, unit_type_mix)
        logger.info(f"   세대 유형 배분: {unit_type_distribution}")
        
        # UnitEstimate 생성
        estimate = UnitEstimate(
            total_units=estimated_units,
            total_gfa=total_gfa,
            residential_gfa=residential_gfa,
            commercial_gfa=commercial_gfa,
            building_footprint=building_footprint,
            floors=floors,
            units_per_floor=units_per_floor,
            parking_spaces=parking_spaces,
            unit_type_distribution=unit_type_distribution,
            avg_unit_area=avg_unit_area,
            calculation_method="auto"
        )
        
        logger.info(
            f"✅ 세대수 산정 완료\n"
            f"   총 세대수: {estimate.total_units}세대\n"
            f"   층수: {estimate.floors}층\n"
            f"   층별 세대수: {estimate.units_per_floor}세대/층\n"
            f"   주차 대수: {estimate.parking_spaces}대"
        )
        
        return estimate
    
    def _calculate_avg_unit_area(self, unit_type_mix: Dict[str, float]) -> float:
        """
        세대 유형별 평균 면적 계산
        
        Args:
            unit_type_mix: 세대 유형 비율
                {"59㎡": 0.6, "74㎡": 0.3, "84㎡": 0.1}
        
        Returns:
            float: 평균 면적 (m²)
        
        Example:
            >>> estimator = UnitEstimatorV9()
            >>> avg = estimator._calculate_avg_unit_area({"59㎡": 0.6, "74㎡": 0.4})
            >>> print(avg)
            65.0  # 59*0.6 + 74*0.4 = 65.0
        """
        total_area = 0.0
        total_ratio = 0.0
        
        for unit_type, ratio in unit_type_mix.items():
            if unit_type in self.UNIT_TYPES:
                area = self.UNIT_TYPES[unit_type]
                total_area += area * ratio
                total_ratio += ratio
        
        if total_ratio > 0:
            avg_area = total_area / total_ratio
        else:
            avg_area = self.DEFAULT_UNIT_AREA
        
        return avg_area
    
    def _distribute_units(
        self,
        total_units: int,
        unit_type_mix: Dict[str, float]
    ) -> Dict[str, int]:
        """
        세대수를 유형별로 배분
        
        Args:
            total_units: 총 세대수
            unit_type_mix: 세대 유형 비율
        
        Returns:
            Dict[str, int]: 세대 유형별 배분
                {"59㎡": 25, "74㎡": 15, "84㎡": 5}
        
        Example:
            >>> estimator = UnitEstimatorV9()
            >>> dist = estimator._distribute_units(45, {"59㎡": 0.6, "74㎡": 0.4})
            >>> print(dist)
            {"59㎡": 27, "74㎡": 18}
        """
        distribution = {}
        remaining_units = total_units
        
        # 비율 정규화 (합이 1.0이 되도록)
        total_ratio = sum(unit_type_mix.values())
        if total_ratio == 0:
            total_ratio = 1.0
        
        # 각 유형별 배분 (마지막 유형 제외)
        unit_types = list(unit_type_mix.items())
        for i, (unit_type, ratio) in enumerate(unit_types[:-1]):
            normalized_ratio = ratio / total_ratio
            count = int(total_units * normalized_ratio)
            distribution[unit_type] = count
            remaining_units -= count
        
        # 마지막 유형은 남은 세대수 전부
        if unit_types:
            last_type = unit_types[-1][0]
            distribution[last_type] = remaining_units
        
        return distribution
    
    def validate_estimate(self, estimate: UnitEstimate) -> Dict[str, bool]:
        """
        세대수 산정 결과 검증
        
        Args:
            estimate: 세대수 산정 결과
        
        Returns:
            Dict[str, bool]: 검증 결과
                {
                    "is_valid": True,
                    "has_min_units": True,
                    "has_feasible_floors": True,
                    "has_parking": True
                }
        
        Example:
            >>> estimator = UnitEstimatorV9()
            >>> estimate = estimator.estimate_units(1000, 300, 50)
            >>> validation = estimator.validate_estimate(estimate)
            >>> print(validation["is_valid"])
            True
        """
        validation = {
            "is_valid": True,
            "has_min_units": estimate.total_units >= 10,
            "has_feasible_floors": 2 <= estimate.floors <= 20,
            "has_parking": estimate.parking_spaces >= estimate.total_units * 0.5,
            "has_reasonable_gfa": estimate.total_gfa > 0
        }
        
        # 전체 유효성
        validation["is_valid"] = all([
            validation["has_min_units"],
            validation["has_feasible_floors"],
            validation["has_parking"],
            validation["has_reasonable_gfa"]
        ])
        
        if not validation["is_valid"]:
            logger.warning(f"⚠️ 세대수 산정 결과 검증 실패: {validation}")
        
        return validation
    
    def estimate_with_unit_count(
        self,
        land_area: float,
        floor_area_ratio: float,
        building_coverage_ratio: float,
        target_unit_count: int,
        parking_ratio: float = 1.0
    ) -> UnitEstimate:
        """
        목표 세대수를 기반으로 역산 (사용자가 세대수를 직접 입력한 경우)
        
        Args:
            land_area: 대지 면적 (m²)
            floor_area_ratio: 용적률 (%)
            building_coverage_ratio: 건폐율 (%)
            target_unit_count: 목표 세대수
            parking_ratio: 주차 비율
        
        Returns:
            UnitEstimate: 세대수 산정 결과 (target_unit_count 기반)
        
        Example:
            >>> estimator = UnitEstimatorV9()
            >>> result = estimator.estimate_with_unit_count(
            ...     land_area=1000.0,
            ...     floor_area_ratio=300.0,
            ...     building_coverage_ratio=50.0,
            ...     target_unit_count=80
            ... )
            >>> print(result.total_units)
            80
        """
        logger.info(f"📊 목표 세대수 기반 역산: {target_unit_count}세대")
        
        # 기본 계산 수행
        estimate = self.estimate_units(
            land_area=land_area,
            floor_area_ratio=floor_area_ratio,
            building_coverage_ratio=building_coverage_ratio,
            parking_ratio=parking_ratio
        )
        
        # 세대수만 사용자 입력값으로 덮어쓰기
        estimate.total_units = target_unit_count
        estimate.calculation_method = "manual"
        
        # 주차 대수 재계산
        estimate.parking_spaces = int(target_unit_count * parking_ratio)
        
        # 층별 세대수 재계산
        if estimate.floors > 0:
            estimate.units_per_floor = int(target_unit_count / estimate.floors)
            if estimate.units_per_floor < 2:
                estimate.units_per_floor = 2
        
        # 세대 유형별 배분 재계산
        estimate.unit_type_distribution = self._distribute_units(
            target_unit_count,
            self.DEFAULT_UNIT_MIX
        )
        
        logger.info(f"✅ 목표 세대수 기반 역산 완료: {target_unit_count}세대")
        
        return estimate


# 전역 인스턴스 (싱글톤)
_unit_estimator: Optional[UnitEstimatorV9] = None


def get_unit_estimator() -> UnitEstimatorV9:
    """
    UnitEstimatorV9 싱글톤 인스턴스 획득
    
    Returns:
        UnitEstimatorV9: 전역 인스턴스
    
    Usage:
        estimator = get_unit_estimator()
        result = estimator.estimate_units(1000.0, 300.0, 50.0)
    """
    global _unit_estimator
    
    if _unit_estimator is None:
        _unit_estimator = UnitEstimatorV9()
    
    return _unit_estimator
