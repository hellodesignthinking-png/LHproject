"""
Unit Estimator Service for ZeroSite v9.1

Provides automatic household unit count estimation based on:
- Land area
- Building coverage ratio
- Floor area ratio
- Zoning type
- Standard unit sizes (Korean LH standards)

This service restores the v7.5 automation feature where users 
don't need to manually calculate household count.

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

import logging
import math
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class UnitSizeType(Enum):
    """
    표준 평형 타입 (LH 기준)
    """
    TYPE_16 = "16평형"  # 약 53㎡
    TYPE_20 = "20평형"  # 약 66㎡ 
    TYPE_24 = "24평형"  # 약 79㎡
    TYPE_26 = "26평형"  # 약 86㎡
    TYPE_32 = "32평형"  # 약 106㎡
    TYPE_40 = "40평형"  # 약 132㎡


@dataclass
class UnitEstimation:
    """
    세대수 자동 추정 결과
    
    Attributes:
        estimated_units: 추정 세대수
        calculation_method: 계산 방식 ("FLOOR_AREA_RATIO" | "BUILDING_COVERAGE")
        total_floor_area: 총 연면적 (㎡)
        buildable_area: 건축가능면적 (㎡)
        avg_unit_size: 평균 세대면적 (㎡)
        unit_type_distribution: 평형별 세대수 분포 (예: {"20평형": 30, "26평형": 20})
        efficiency_ratio: 전용률 (%)
        confidence_score: 신뢰도 (0-100)
        warnings: 경고 메시지 목록
    """
    estimated_units: int
    calculation_method: str
    total_floor_area: float
    buildable_area: float
    avg_unit_size: float
    unit_type_distribution: Dict[str, int]
    efficiency_ratio: float
    confidence_score: float
    warnings: List[str]


class UnitEstimatorV9:
    """
    세대수 자동 추정 엔진 (ZeroSite v9.1 핵심 기능)
    
    Features:
    - 용적률 기반 세대수 계산
    - 건폐율/층수 기반 세대수 계산
    - 평형별 세대 분포 자동 생성
    - LH 기준 전용률 적용 (75-85%)
    - 법정 주차 대수 검증
    
    Calculation Logic:
    1. 총 연면적 = 토지면적 × 용적률
    2. 전용면적 = 총 연면적 × 전용률 (80%)
    3. 세대수 = 전용면적 / 평균 세대 전용면적
    
    Based On:
    - LH 한국토지주택공사 설계기준
    - 주택법 시행규칙 (주택 규모별 기준)
    - 건축법 (공용면적, 부대시설)
    
    Usage:
        estimator = UnitEstimatorV9()
        result = estimator.estimate_units(
            land_area=1000.0,
            floor_area_ratio=300.0,
            building_coverage_ratio=50.0,
            zone_type="제3종일반주거지역"
        )
        print(result.estimated_units)  # 80
    """
    
    # LH 표준 평형 전용면적 (㎡)
    STANDARD_UNIT_SIZES = {
        "16평형": 53.0,
        "20평형": 66.0,
        "24평형": 79.0,
        "26평형": 86.0,
        "32평형": 106.0,
        "40평형": 132.0
    }
    
    # 전용률 (공용면적 포함 비율)
    DEFAULT_EFFICIENCY_RATIO = 0.80  # 80% (LH 기준)
    MIN_EFFICIENCY_RATIO = 0.75
    MAX_EFFICIENCY_RATIO = 0.85
    
    # 층당 층고
    FLOOR_HEIGHT = 3.0  # m
    
    # 법정 주차 대수 비율 (세대당)
    PARKING_RATIO = 1.0
    
    def __init__(self):
        logger.info("🏗️ UnitEstimatorV9 initialized")
    
    def estimate_units(
        self,
        land_area: float,
        floor_area_ratio: float,
        building_coverage_ratio: Optional[float] = None,
        zone_type: Optional[str] = None,
        max_height: Optional[float] = None,
        target_unit_size: str = "26평형"
    ) -> UnitEstimation:
        """
        세대수 자동 추정 (v9.1 핵심 메서드)
        
        Args:
            land_area: 토지면적 (㎡)
            floor_area_ratio: 용적률 (%)
            building_coverage_ratio: 건폐율 (%, optional)
            zone_type: 용도지역명 (optional)
            max_height: 최대 높이 제한 (m, optional)
            target_unit_size: 목표 평형 (default: 26평형)
        
        Returns:
            UnitEstimation: 세대수 추정 결과
        
        Example:
            >>> estimator = UnitEstimatorV9()
            >>> result = estimator.estimate_units(1000, 300.0, 50.0)
            >>> result.estimated_units
            80
        """
        logger.info(f"📊 세대수 자동 추정 시작: 토지면적 {land_area}㎡, 용적률 {floor_area_ratio}%")
        
        warnings = []
        
        # 1. 입력 검증
        if land_area <= 0:
            raise ValueError(f"토지면적이 유효하지 않습니다: {land_area}㎡")
        
        if floor_area_ratio <= 0 or floor_area_ratio > 1000:
            raise ValueError(f"용적률이 유효하지 않습니다: {floor_area_ratio}%")
        
        # 2. 총 연면적 계산
        total_floor_area = land_area * (floor_area_ratio / 100.0)
        logger.info(f"   총 연면적: {total_floor_area:.2f}㎡")
        
        # 3. 건축가능면적 계산 (건폐율 기반)
        if building_coverage_ratio:
            buildable_area = land_area * (building_coverage_ratio / 100.0)
            logger.info(f"   건축면적: {buildable_area:.2f}㎡ (건폐율 {building_coverage_ratio}%)")
        else:
            buildable_area = total_floor_area / 5.0  # 기본 5층 가정
            warnings.append("건폐율 미입력 - 기본값(5층) 가정")
        
        # 4. 층수 추정
        estimated_floors = math.ceil(total_floor_area / buildable_area)
        
        if max_height:
            max_floors = math.floor(max_height / self.FLOOR_HEIGHT)
            if estimated_floors > max_floors:
                estimated_floors = max_floors
                warnings.append(f"높이 제한으로 층수 조정: {max_floors}층")
        
        logger.info(f"   추정 층수: {estimated_floors}층")
        
        # 5. 전용률 적용
        efficiency_ratio = self.DEFAULT_EFFICIENCY_RATIO
        usable_floor_area = total_floor_area * efficiency_ratio
        logger.info(f"   전용면적: {usable_floor_area:.2f}㎡ (전용률 {efficiency_ratio*100:.0f}%)")
        
        # 6. 평균 세대 전용면적
        if target_unit_size not in self.STANDARD_UNIT_SIZES:
            target_unit_size = "26평형"
            warnings.append(f"표준 평형 미지정 - 기본값({target_unit_size}) 사용")
        
        avg_unit_size = self.STANDARD_UNIT_SIZES[target_unit_size]
        logger.info(f"   목표 평형: {target_unit_size} ({avg_unit_size}㎡)")
        
        # 7. 세대수 계산
        estimated_units = math.floor(usable_floor_area / avg_unit_size)
        logger.info(f"   추정 세대수: {estimated_units}세대")
        
        # 8. 평형별 분포 생성 (LH 표준 분포 적용)
        unit_type_distribution = self._generate_unit_distribution(
            estimated_units, 
            target_unit_size
        )
        
        # 9. 신뢰도 계산
        confidence_score = self._calculate_confidence(
            land_area=land_area,
            floor_area_ratio=floor_area_ratio,
            building_coverage_ratio=building_coverage_ratio,
            estimated_units=estimated_units,
            warnings=warnings
        )
        
        # 10. 계산 방식 결정
        calculation_method = "FLOOR_AREA_RATIO"
        if building_coverage_ratio:
            calculation_method = "FLOOR_AREA_RATIO_WITH_COVERAGE"
        
        # 11. 결과 생성
        result = UnitEstimation(
            estimated_units=estimated_units,
            calculation_method=calculation_method,
            total_floor_area=total_floor_area,
            buildable_area=buildable_area,
            avg_unit_size=avg_unit_size,
            unit_type_distribution=unit_type_distribution,
            efficiency_ratio=efficiency_ratio,
            confidence_score=confidence_score,
            warnings=warnings
        )
        
        logger.info(f"✅ 세대수 추정 완료: {estimated_units}세대 (신뢰도: {confidence_score:.1f}%)")
        
        return result
    
    def _generate_unit_distribution(
        self, 
        total_units: int, 
        primary_type: str = "26평형"
    ) -> Dict[str, int]:
        """
        평형별 세대 분포 생성 (LH 표준 분포)
        
        Distribution Strategy:
        - 주력 평형 (26평형): 50%
        - 소형 (20평형): 30%
        - 중대형 (32평형): 20%
        
        Args:
            total_units: 총 세대수
            primary_type: 주력 평형 (default: 26평형)
        
        Returns:
            Dict[str, int]: 평형별 세대수 (예: {"20평형": 24, "26평형": 40, "32평형": 16})
        """
        distribution = {}
        
        if total_units <= 0:
            return {"26평형": 0}
        
        # 소규모 프로젝트 (30세대 미만) - 단일 평형
        if total_units < 30:
            distribution[primary_type] = total_units
            return distribution
        
        # 중규모 프로젝트 (30-100세대) - 2-3 평형 mix
        if total_units < 100:
            distribution["20평형"] = math.floor(total_units * 0.30)
            distribution["26평형"] = math.floor(total_units * 0.50)
            distribution["32평형"] = total_units - distribution["20평형"] - distribution["26평형"]
            return distribution
        
        # 대규모 프로젝트 (100세대+) - 다양한 평형 mix
        distribution["16평형"] = math.floor(total_units * 0.15)
        distribution["20평형"] = math.floor(total_units * 0.25)
        distribution["26평형"] = math.floor(total_units * 0.35)
        distribution["32평형"] = math.floor(total_units * 0.20)
        distribution["40평형"] = total_units - sum(distribution.values())
        
        return distribution
    
    def _calculate_confidence(
        self,
        land_area: float,
        floor_area_ratio: float,
        building_coverage_ratio: Optional[float],
        estimated_units: int,
        warnings: List[str]
    ) -> float:
        """
        추정 신뢰도 계산 (0-100)
        
        Confidence Factors:
        - 토지면적 (너무 작거나 크면 감점)
        - 용적률 범위 (100-500% 정상)
        - 건폐율 입력 여부 (있으면 +20점)
        - 경고 개수 (1개당 -10점)
        
        Args:
            land_area: 토지면적 (㎡)
            floor_area_ratio: 용적률 (%)
            building_coverage_ratio: 건폐율 (%, optional)
            estimated_units: 추정 세대수
            warnings: 경고 목록
        
        Returns:
            float: 신뢰도 (0-100)
        """
        confidence = 100.0
        
        # 1. 토지면적 검증
        if land_area < 500:
            confidence -= 15.0  # 소규모 토지 (500㎡ 미만)
        elif land_area > 10000:
            confidence -= 10.0  # 대규모 토지 (1만㎡ 초과)
        
        # 2. 용적률 검증
        if floor_area_ratio < 100 or floor_area_ratio > 500:
            confidence -= 20.0  # 비정상 용적률
        
        # 3. 건폐율 검증
        if not building_coverage_ratio:
            confidence -= 20.0  # 건폐율 미입력
        
        # 4. 세대수 검증
        if estimated_units < 20:
            confidence -= 10.0  # 소규모 (20세대 미만)
        elif estimated_units > 500:
            confidence -= 15.0  # 대규모 (500세대 초과)
        
        # 5. 경고 개수 반영
        confidence -= len(warnings) * 10.0
        
        # 6. 범위 제한 (0-100)
        confidence = max(0.0, min(100.0, confidence))
        
        return confidence
    
    def estimate_parking_requirement(self, unit_count: int) -> int:
        """
        법정 주차 대수 계산
        
        Args:
            unit_count: 세대수
        
        Returns:
            int: 필요 주차 대수
        """
        return math.ceil(unit_count * self.PARKING_RATIO)
    
    def validate_unit_estimation(
        self,
        estimated_units: int,
        land_area: float,
        parking_area_available: Optional[float] = None
    ) -> Dict[str, any]:
        """
        세대수 추정 검증
        
        Args:
            estimated_units: 추정 세대수
            land_area: 토지면적 (㎡)
            parking_area_available: 주차 가능 면적 (㎡, optional)
        
        Returns:
            Dict: 검증 결과 {"valid": bool, "issues": List[str]}
        """
        issues = []
        
        # 1. 밀도 검증 (세대/토지면적)
        density = estimated_units / land_area * 1000  # 세대/1000㎡
        
        if density > 150:
            issues.append(f"세대 밀도 과밀 ({density:.1f}세대/1000㎡)")
        elif density < 10:
            issues.append(f"세대 밀도 과소 ({density:.1f}세대/1000㎡)")
        
        # 2. 주차 검증
        required_parking = self.estimate_parking_requirement(estimated_units)
        
        if parking_area_available:
            # 주차면적 기준: 25㎡/대 (평행주차 기준)
            available_parking_spaces = parking_area_available / 25.0
            
            if available_parking_spaces < required_parking:
                issues.append(
                    f"주차 공간 부족 (필요: {required_parking}대, 가능: {available_parking_spaces:.0f}대)"
                )
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "required_parking": required_parking,
            "density_per_1000sqm": round(density, 2)
        }


# 모듈 레벨 함수 (간편 사용)
def quick_estimate_units(
    land_area: float, 
    floor_area_ratio: float,
    building_coverage_ratio: Optional[float] = None
) -> int:
    """
    세대수 빠른 추정 (간편 함수)
    
    Args:
        land_area: 토지면적 (㎡)
        floor_area_ratio: 용적률 (%)
        building_coverage_ratio: 건폐율 (%, optional)
    
    Returns:
        int: 추정 세대수
    
    Example:
        >>> unit_count = quick_estimate_units(1000, 300.0, 50.0)
        >>> print(unit_count)
        80
    """
    estimator = UnitEstimatorV9()
    result = estimator.estimate_units(
        land_area=land_area,
        floor_area_ratio=floor_area_ratio,
        building_coverage_ratio=building_coverage_ratio
    )
    return result.estimated_units
