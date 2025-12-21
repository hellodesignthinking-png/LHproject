"""
M4: Capacity Context
====================

건축물 규모 검토 모듈(M4) 출력 Context

이 모듈은 건축법, 용적률, 건폐율을 고려하여:
- 최대 세대수
- 권장 세대수
- 주차 대수
- 층수
- 총 연면적

을 계산합니다.

⚠️ 중요:
- land_value는 참조하지 않음 (M2 결과만 사용)
- 사업성 ROI는 계산하지 않음 (M5로 이동)
- LH 매입가는 계산하지 않음 (M5로 이동)

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BuildingSpecs:
    """건축물 사양"""
    max_floors: int                     # 최고 층수
    recommended_floors: int             # 권장 층수
    total_gfa_sqm: float               # 총 연면적 (㎡)
    building_coverage_sqm: float        # 건축면적 (㎡)
    unit_area_avg: float                # 평균 세대 면적 (㎡)


@dataclass(frozen=True)
class UnitPlan:
    """세대 계획"""
    max_units: int                      # 최대 세대수
    recommended_units: int              # 권장 세대수
    unit_type_distribution: Dict[str, int]  # 유형별 세대수 (59A: 10, 59B: 15, ...)
    
    
@dataclass(frozen=True)
class ParkingPlan:
    """주차 계획"""
    required_spaces: int                # 법적 필수 주차 대수
    planned_spaces: int                 # 계획 주차 대수
    parking_ratio: float                # 주차 비율 (대/세대)


@dataclass(frozen=True)
class CapacityContext:
    """
    건축 규모 Context (M4 출력)
    
    frozen=True: 생성 후 수정 불가
    """
    
    # === 용적률/건폐율 ===
    far_available: float                # 사용 가능 용적률 (%)
    bcr_available: float                # 사용 가능 건폐율 (%)
    far_utilization: float              # 용적률 활용률 (%)
    bcr_utilization: float              # 건폐율 활용률 (%)
    
    # === 건축물 사양 ===
    building_specs: BuildingSpecs       # 건축물 상세 사양
    
    # === 세대 계획 ===
    unit_plan: UnitPlan                 # 세대 계획
    
    # === 주차 계획 ===
    parking_plan: ParkingPlan           # 주차 계획
    
    # === 건축물 유형 ===
    building_type: str                  # 건축물 유형 (아파트/다세대/도시형생활주택)
    structure_type: str                 # 구조 유형 (철근콘크리트/철골)
    
    # === 법규 적합성 ===
    compliance_score: float             # 법규 적합성 점수 (15점 만점)
    
    # === 메타데이터 ===
    calculation_date: str               # 계산 일시
    
    # === 설계 제약 & 이슈 ===
    compliance_issues: List[str] = field(default_factory=list)  # 법규 이슈
    design_constraints: List[str] = field(default_factory=list)  # 설계 제약사항
    assumptions: Dict[str, any] = field(default_factory=dict)  # 가정 사항
    
    def __post_init__(self):
        """유효성 검증"""
        assert 0 <= self.far_available <= 1000, "용적률은 0-1000% 범위"
        assert 0 <= self.bcr_available <= 100, "건폐율은 0-100% 범위"
        assert self.unit_plan.max_units >= self.unit_plan.recommended_units
        assert self.parking_plan.planned_spaces >= self.parking_plan.required_spaces
    
    @property
    def is_high_density(self) -> bool:
        """고밀도 개발 여부"""
        return self.far_utilization > 0.8
    
    @property
    def capacity_summary(self) -> str:
        """규모 요약"""
        return (
            f"권장 세대수: {self.unit_plan.recommended_units}세대\n"
            f"층수: {self.building_specs.recommended_floors}층\n"
            f"주차: {self.parking_plan.planned_spaces}대\n"
            f"용적률: {self.far_utilization:.0%}"
        )
    
    def to_dict(self) -> Dict[str, any]:
        return {
            "utilization": {
                "far": self.far_available,
                "bcr": self.bcr_available,
                "far_util": self.far_utilization,
                "bcr_util": self.bcr_utilization
            },
            "building": {
                "type": self.building_type,
                "floors": self.building_specs.recommended_floors,
                "gfa_sqm": self.building_specs.total_gfa_sqm
            },
            "units": {
                "recommended": self.unit_plan.recommended_units,
                "max": self.unit_plan.max_units,
                "distribution": self.unit_plan.unit_type_distribution
            },
            "parking": {
                "required": self.parking_plan.required_spaces,
                "planned": self.parking_plan.planned_spaces,
                "ratio": self.parking_plan.parking_ratio
            },
            "compliance": {
                "score": self.compliance_score,
                "issues": self.compliance_issues
            }
        }
