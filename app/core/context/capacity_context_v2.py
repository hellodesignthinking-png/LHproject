"""
M4: Capacity Context V2 (건축규모검토 모듈)
==========================================

ZeroSite M4 모듈 - 물리적 건축 규모 산출 전용
절대 수행하지 않는 것: 판단(합격/불합격), 사업성, 감정평가, LH 의사결정

M4의 핵심 질문:
"이 토지(M1)와 이 지역의 LH 선호 주거유형(M3)을 기준으로,
 용적률을 최대한 활용한 안과,
 주차가 물리적으로 가능한 현실적인 안을
 동시에 제시할 수 있는가?"

Author: ZeroSite Architecture Team
Date: 2025-12-17
Version: 2.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from enum import Enum


class RampFeasibility(str, Enum):
    """램프 물리적 가능성"""
    FEASIBLE = "feasible"              # 가능
    MARGINAL = "marginal"              # 한계
    NOT_FEASIBLE = "not_feasible"      # 불가능


class ParkingType(str, Enum):
    """주차 방식"""
    SELF_PARKING = "self_parking"          # 자주식 (기본)
    MECHANICAL = "mechanical"              # 기계식 (가능성만 제시)
    HYBRID = "hybrid"                      # 혼용


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. GFA 상세 분해 (Gross Floor Area Breakdown)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class GFABreakdown:
    """
    연면적(GFA) 상세 분해
    
    총연면적 = NIA + 공용면적 + 기계실/손실면적
    """
    total_gfa_sqm: float                # 총 연면적 (㎡)
    
    # NIA (Net Internal Area) - 세대 전용면적
    nia_sqm: float                      # 순수 세대 전용면적
    nia_ratio: float                    # NIA 비율 (%)
    
    # 공용면적
    common_core_sqm: float              # 코어(계단, 엘리베이터)
    common_corridor_sqm: float          # 복도
    common_shared_sqm: float            # 공용공간(커뮤니티 등)
    common_total_sqm: float             # 공용 합계
    common_ratio: float                 # 공용 비율 (%)
    
    # 기계실/손실
    mechanical_sqm: float               # 기계실, 전기실 등
    loss_sqm: float                     # 벽체, 기타 손실
    mechanical_loss_ratio: float        # 기계/손실 비율 (%)
    
    def __post_init__(self):
        """검증: 합계 = 총연면적"""
        calc_total = (
            self.nia_sqm + 
            self.common_total_sqm + 
            self.mechanical_sqm + 
            self.loss_sqm
        )
        assert abs(calc_total - self.total_gfa_sqm) < 1.0, \
            f"GFA 분해 오류: {calc_total:.1f} ≠ {self.total_gfa_sqm:.1f}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. 법정 및 인센티브 용적률 기준 규모
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class CapacityScale:
    """
    용적률 기준 건축 규모
    (법정 용적률 vs 인센티브 용적률)
    """
    # 용적률/건폐율
    applied_far: float                  # 적용 용적률 (%)
    applied_bcr: float                  # 적용 건폐율 (%)
    
    # 기본 규모
    max_footprint_sqm: float            # 최대 건축면적 (대지면적 × BCR)
    target_gfa_sqm: float               # 목표 연면적 (대지면적 × FAR)
    
    # GFA 분해
    gfa_breakdown: GFABreakdown         # 연면적 상세 분해
    
    # 세대수 산정
    total_units: int                    # 총 세대수
    unit_type_distribution: Dict[str, int]  # 유형별 세대수 {'30㎡': 50, '45㎡': 30}
    average_unit_area_sqm: float        # 평균 세대 면적 (전용)
    
    # 주차대수 산정
    required_parking_spaces: int        # 법정 필수 주차대수
    parking_ratio: float                # 주차 비율 (대/세대)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. 물리적 매싱 대안 (3~5개 생성)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class MassingOption:
    """
    물리적 배치 대안
    
    예시:
    - Option 1: 2개동 × 15층 = 30호/층 → 900세대
    - Option 2: 3개동 × 10층 = 30호/층 → 900세대
    - Option 3: 1개동 × 20층 = 45호/층 → 900세대
    """
    option_id: str                      # 대안 ID (A, B, C...)
    option_name: str                    # 대안명
    
    # 건물 배치
    building_count: int                 # 건물 동수
    floors_per_building: int            # 동당 층수
    
    # 층별 계획
    standard_floor_area_sqm: float      # 기준층 면적 (㎡)
    units_per_floor: int                # 층당 세대수
    
    # 달성 지표
    achieved_gfa_sqm: float             # 달성 연면적
    achieved_far: float                 # 달성 용적률 (%)
    far_achievement_rate: float         # 용적률 달성률 (0-1)
    
    # 부지 활용
    site_coverage_ratio: float          # 부지 점유율 (%)
    open_space_ratio: float             # 오픈스페이스 비율 (%)
    
    # 평가
    buildability_score: float           # 시공성 점수 (0-100)
    efficiency_score: float             # 효율성 점수 (0-100)
    remarks: List[str] = field(default_factory=list)  # 비고


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 주차 해결안 (핵심: FAR vs 주차 트레이드오프)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class RampCondition:
    """
    램프 물리적 조건 검토
    
    자주식 지하주차장 진입로 최소 기준:
    - 폭: 3.3m 이상 (일방향), 5.5m 이상 (양방향)
    - 길이: 직선구간 6m 이상
    - 회전반경: 최소 6m
    - 비주거 면적: 램프 + 진입부 필요
    """
    ramp_width_m: float                 # 램프 폭 (m)
    ramp_length_m: float                # 램프 길이 (m)
    turning_radius_m: float             # 회전 반경 (m)
    non_residential_area_sqm: float     # 비주거 소요 면적 (㎡)
    
    # 판정 (상태만, 판단 아님)
    feasibility: RampFeasibility        # 가능성
    constraint_issues: List[str] = field(default_factory=list)  # 제약사항


@dataclass(frozen=True)
class ParkingSolution:
    """
    주차 해결안
    
    Alternative A: 용적률 최대화 → 주차 대응
    Alternative B: 주차 우선 → 용적률 조정
    """
    solution_type: Literal["alternative_A", "alternative_B"]
    solution_name: str                  # 대안명
    
    # 주차 계획
    parking_type: ParkingType           # 주차 방식
    total_parking_spaces: int           # 총 주차대수
    
    # 자주식 주차
    self_parking_spaces: int            # 자주식 대수
    basement_floors: int                # 지하 층수
    ramp_condition: RampCondition       # 램프 조건
    
    # 기계식 주차 (가능성만 제시)
    mechanical_parking_spaces: int      # 기계식 대수 (있다면)
    mechanical_type: Optional[str]      # 기계식 종류
    
    # 규모 조정 (Alternative B용)
    adjusted_total_units: Optional[int]         # 조정된 총 세대수
    adjusted_floors: Optional[int]              # 조정된 층수
    adjusted_gfa_sqm: Optional[float]           # 조정된 연면적
    far_sacrifice_ratio: Optional[float]        # 용적률 희생 비율
    
    # 평가
    parking_achievability_score: float  # 주차 실현가능성 (0-100)
    remarks: List[str] = field(default_factory=list)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. 세대 구성 요약
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class UnitSummary:
    """
    세대 구성 요약
    
    M3에서 받은 preferred_unit_type과 unit_mix_ratio 기반
    """
    total_units: int                    # 총 세대수
    
    # M3 입력
    preferred_unit_type: str            # LH 선호 유형 (예: '청년형 30㎡')
    unit_mix_ratio: Dict[str, float]    # 혼합 비율 {'30㎡': 0.7, '45㎡': 0.3}
    
    # 산출 결과
    unit_count_by_type: Dict[str, int]  # 유형별 세대수
    unit_area_by_type: Dict[str, float] # 유형별 면적 (㎡)
    
    # 통계
    min_unit_area_sqm: float            # 최소 세대 면적
    max_unit_area_sqm: float            # 최대 세대 면적
    average_unit_area_sqm: float        # 평균 세대 면적


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. 최종 CapacityContext V2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass(frozen=True)
class CapacityContextV2:
    """
    M4 건축규모검토 모듈 출력 Context V2
    
    ✅ 6가지 필수 산출물:
    1. legal_capacity: 법정 용적률 규모
    2. incentive_capacity: 인센티브 용적률 규모
    3. massing_options: 3~5개 물리적 배치 대안
    4. unit_summary: 세대 구성 요약
    5. parking_solutions: 주차 해결안 (A: 용적률 MAX, B: 주차 우선)
    6. (출력 항목 자체가 6번째)
    
    🚫 절대 포함되지 않는 것:
    - 사업성 판단 (M5)
    - LH 합격/불합격 판단 (M6)
    - 감정평가액 (M2)
    - 판단적 진술
    
    frozen=True: 생성 후 수정 불가
    """
    
    # ═══════════════════════════════════════════════════
    # 필수 산출물 1, 2: 법정 vs 인센티브 규모
    # ═══════════════════════════════════════════════════
    legal_capacity: CapacityScale       # 법정 용적률 기준 규모
    incentive_capacity: CapacityScale   # 인센티브 용적률 기준 규모
    
    # ═══════════════════════════════════════════════════
    # 필수 산출물 3: 물리적 매싱 대안 (3~5개)
    # ═══════════════════════════════════════════════════
    massing_options: List[MassingOption]
    
    # ═══════════════════════════════════════════════════
    # 필수 산출물 4: 세대 구성 요약
    # ═══════════════════════════════════════════════════
    unit_summary: UnitSummary
    
    # ═══════════════════════════════════════════════════
    # 필수 산출물 5: 주차 해결안 (A & B)
    # ═══════════════════════════════════════════════════
    parking_solutions: Dict[str, ParkingSolution]  # {'alternative_A': ..., 'alternative_B': ...}
    
    # ═══════════════════════════════════════════════════
    # 메타데이터 (required fields, no defaults)
    # ═══════════════════════════════════════════════════
    calculation_date: str               # 계산 일시
    
    # 입력 참조 (READ-ONLY, 원본 수정 절대 금지)
    input_land_area_sqm: float          # 입력 대지면적
    input_legal_far: float              # 입력 법정 용적률
    input_incentive_far: float          # 입력 인센티브 용적률
    input_housing_type: str             # 입력 LH 주거유형
    
    # ═══════════════════════════════════════════════════
    # 필수 산출물 6: 도면 생성 정보 (with defaults)
    # ═══════════════════════════════════════════════════
    schematic_drawing_paths: Dict[str, str] = field(default_factory=dict)
    # {'ground_layout': 'path/to/ground.svg',
    #  'standard_floor': 'path/to/floor.svg',
    #  'basement_parking': 'path/to/parking.svg',
    #  'massing_comparison': 'path/to/massing.png'}
    
    module_version: str = "2.0"         # 모듈 버전
    
    # 가정사항 및 제약조건
    assumptions: Dict[str, any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    calculation_notes: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """검증"""
        # 주차 해결안 2개 필수
        assert "alternative_A" in self.parking_solutions, "Alternative A 필수"
        assert "alternative_B" in self.parking_solutions, "Alternative B 필수"
        
        # 매싱 대안 3~5개
        assert 3 <= len(self.massing_options) <= 5, "매싱 대안 3~5개"
        
        # 인센티브 >= 법정
        assert self.incentive_capacity.applied_far >= self.legal_capacity.applied_far
    
    @property
    def far_max_alternative(self) -> ParkingSolution:
        """용적률 최대화 대안 (Alternative A)"""
        return self.parking_solutions["alternative_A"]
    
    @property
    def parking_priority_alternative(self) -> ParkingSolution:
        """주차 우선 대안 (Alternative B)"""
        return self.parking_solutions["alternative_B"]
    
    @property
    def recommended_massing(self) -> MassingOption:
        """권장 매싱 (효율성 최고)"""
        return max(self.massing_options, key=lambda x: x.efficiency_score)
    
    @property
    def capacity_summary(self) -> str:
        """규모 요약"""
        legal_units = self.legal_capacity.total_units
        incentive_units = self.incentive_capacity.total_units
        
        alt_a_parking = self.far_max_alternative.total_parking_spaces
        alt_b_parking = self.parking_priority_alternative.total_parking_spaces
        alt_b_units = self.parking_priority_alternative.adjusted_total_units or incentive_units
        
        return f"""
M4 건축규모 검토 결과:

[법정 기준]
- 용적률: {self.legal_capacity.applied_far}%
- 총 세대수: {legal_units}세대
- 연면적: {self.legal_capacity.target_gfa_sqm:,.0f}㎡

[인센티브 기준]
- 용적률: {self.incentive_capacity.applied_far}%
- 총 세대수: {incentive_units}세대
- 연면적: {self.incentive_capacity.target_gfa_sqm:,.0f}㎡

[주차 해결안]
- Alternative A (용적률 MAX): {incentive_units}세대, 주차 {alt_a_parking}대
- Alternative B (주차 우선): {alt_b_units}세대, 주차 {alt_b_parking}대

[권장 매싱]
- {self.recommended_massing.option_name}
- {self.recommended_massing.building_count}개동 × {self.recommended_massing.floors_per_building}층
        """.strip()
    
    def to_dict(self) -> Dict[str, any]:
        """딕셔너리 변환 (API/보고서용)"""
        return {
            "module_version": self.module_version,
            "calculation_date": self.calculation_date,
            
            "legal_capacity": {
                "applied_far": self.legal_capacity.applied_far,
                "applied_bcr": self.legal_capacity.applied_bcr,
                "target_gfa_sqm": self.legal_capacity.target_gfa_sqm,
                "total_units": self.legal_capacity.total_units,
                "required_parking": self.legal_capacity.required_parking_spaces,
                "gfa_breakdown": {
                    "nia_sqm": self.legal_capacity.gfa_breakdown.nia_sqm,
                    "common_sqm": self.legal_capacity.gfa_breakdown.common_total_sqm,
                    "mechanical_loss_sqm": (
                        self.legal_capacity.gfa_breakdown.mechanical_sqm +
                        self.legal_capacity.gfa_breakdown.loss_sqm
                    )
                }
            },
            
            "incentive_capacity": {
                "applied_far": self.incentive_capacity.applied_far,
                "applied_bcr": self.incentive_capacity.applied_bcr,
                "target_gfa_sqm": self.incentive_capacity.target_gfa_sqm,
                "total_units": self.incentive_capacity.total_units,
                "required_parking": self.incentive_capacity.required_parking_spaces,
                "gfa_breakdown": {
                    "nia_sqm": self.incentive_capacity.gfa_breakdown.nia_sqm,
                    "common_sqm": self.incentive_capacity.gfa_breakdown.common_total_sqm,
                    "mechanical_loss_sqm": (
                        self.incentive_capacity.gfa_breakdown.mechanical_sqm +
                        self.incentive_capacity.gfa_breakdown.loss_sqm
                    )
                }
            },
            
            "massing_options": [
                {
                    "option_id": opt.option_id,
                    "option_name": opt.option_name,
                    "building_count": opt.building_count,
                    "floors": opt.floors_per_building,
                    "units_per_floor": opt.units_per_floor,
                    "achieved_far": opt.achieved_far,
                    "buildability_score": opt.buildability_score,
                    "efficiency_score": opt.efficiency_score
                }
                for opt in self.massing_options
            ],
            
            "unit_summary": {
                "total_units": self.unit_summary.total_units,
                "preferred_type": self.unit_summary.preferred_unit_type,
                "unit_count_by_type": self.unit_summary.unit_count_by_type,
                "average_area_sqm": self.unit_summary.average_unit_area_sqm
            },
            
            "parking_solutions": {
                "alternative_A": {
                    "solution_type": "far_maximization",
                    "total_parking": self.far_max_alternative.total_parking_spaces,
                    "basement_floors": self.far_max_alternative.basement_floors,
                    "ramp_feasibility": self.far_max_alternative.ramp_condition.feasibility.value,
                    "achievability_score": self.far_max_alternative.parking_achievability_score
                },
                "alternative_B": {
                    "solution_type": "parking_priority",
                    "total_parking": self.parking_priority_alternative.total_parking_spaces,
                    "adjusted_units": self.parking_priority_alternative.adjusted_total_units,
                    "far_sacrifice": self.parking_priority_alternative.far_sacrifice_ratio,
                    "achievability_score": self.parking_priority_alternative.parking_achievability_score
                }
            },
            
            "schematic_drawings": self.schematic_drawing_paths,
            
            "inputs": {
                "land_area_sqm": self.input_land_area_sqm,
                "legal_far": self.input_legal_far,
                "incentive_far": self.input_incentive_far,
                "housing_type": self.input_housing_type
            },
            
            "metadata": {
                "assumptions": self.assumptions,
                "constraints": self.constraints,
                "notes": self.calculation_notes
            }
        }


__all__ = [
    "CapacityContextV2",
    "CapacityScale",
    "GFABreakdown",
    "MassingOption",
    "ParkingSolution",
    "RampCondition",
    "UnitSummary",
    "RampFeasibility",
    "ParkingType"
]
