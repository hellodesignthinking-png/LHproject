"""
M6 LH Comprehensive Judgement Engine V3 (ZeroSite 4.0 FIX)
===========================================================

LH 실제 심사 흐름을 코드로 복제한 최종 고정판

평가 구조 (총 100점):
- [A] 정책·유형 적합성: 25점
- [B] 입지·환경 평가: 20점
- [C] 건축 가능성: 20점
- [D] 가격·매입 적정성: 15점
- [E] 사업성: 20점

⚠️ FIX 규칙:
- 항목 추가/삭제 금지
- 배점 변경 금지
- 즉시 탈락 조건 변경 금지
- 가중치 임의 변경 금지

Author: ZeroSite M6 Team
Date: 2025-12-26
Version: 3.0 (LH Standard FIX)
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class JudgementType(Enum):
    """최종 판정 유형"""
    GO = "GO"                    # 즉시 진행 가능
    CONDITIONAL = "CONDITIONAL"  # 보완 시 가능
    NO_GO = "NO_GO"             # 진행 불가


class GradeType(Enum):
    """등급"""
    S = "S"      # 95~100
    A_PLUS = "A+"  # 90~94
    A = "A"      # 85~89
    B_PLUS = "B+"  # 80~84
    B = "B"      # 75~79
    C_PLUS = "C+"  # 70~74
    C = "C"      # 65~69
    D = "D"      # 60~64
    F = "F"      # <60


class RegionWeightType(Enum):
    """지역 가중치 유형"""
    CAPITAL = "수도권"  # 서울·경기·인천
    LOCAL = "지방"     # 광역시·중소도시


@dataclass(frozen=True)
class SectionScore:
    """섹션별 점수"""
    raw_score: float          # 원점수
    weight: float             # 가중치
    weighted_score: float     # 가중 점수
    max_score: float          # 만점
    items: Dict[str, float]   # 세부 항목 점수


@dataclass(frozen=True)
class RegionWeights:
    """지역별 가중치"""
    policy: float      # 정책·유형
    location: float    # 입지
    construction: float  # 건축
    price: float       # 가격
    business: float    # 사업성
    
    @staticmethod
    def get_capital_weights():
        """수도권 가중치: 입지·정책 우선 / 수익성은 관대"""
        return RegionWeights(
            policy=1.2,
            location=1.2,
            construction=1.0,
            price=1.1,
            business=0.9
        )
    
    @staticmethod
    def get_local_weights():
        """지방 가중치: 가격·사업성 우선 / 입지는 관대"""
        return RegionWeights(
            policy=1.0,
            location=0.9,
            construction=1.0,
            price=1.2,
            business=1.3
        )


@dataclass(frozen=True)
class M6ComprehensiveResult:
    """
    M6 최종 종합 판단 결과
    
    이것이 ZeroSite 4.0의 최종 결과물
    """
    # 기본 점수
    lh_score_total: float           # 총점 (0~100)
    judgement: JudgementType        # 최종 판정
    grade: GradeType                # 등급
    
    # 탈락 여부
    fatal_reject: bool              # 즉시 탈락 여부
    reject_reasons: List[str]       # 탈락 사유
    
    # 감점 및 개선
    deduction_reasons: List[str]    # 감점 사유
    improvement_points: List[str]   # 개선 방안
    
    # 메타 정보
    region_weight: RegionWeightType  # 지역 가중치
    confidence_level: str           # 신뢰도 (HIGH/MEDIUM/LOW)
    
    # 섹션별 상세 점수
    section_a_policy: SectionScore      # [A] 정책·유형 (25점)
    section_b_location: SectionScore    # [B] 입지·환경 (20점)
    section_c_construction: SectionScore  # [C] 건축 가능성 (20점)
    section_d_price: SectionScore       # [D] 가격·매입 (15점)
    section_e_business: SectionScore    # [E] 사업성 (20점)
    
    # 가중치 정보
    applied_weights: Dict[str, float]  # 적용된 가중치
    
    def to_dict(self) -> Dict:
        """결과를 딕셔너리로 변환"""
        return {
            "lh_score_total": round(self.lh_score_total, 1),
            "judgement": self.judgement.value,
            "grade": self.grade.value,
            "fatal_reject": self.fatal_reject,
            "reject_reasons": self.reject_reasons,
            "deduction_reasons": self.deduction_reasons,
            "improvement_points": self.improvement_points,
            "region_weight": self.region_weight.value,
            "confidence_level": self.confidence_level,
            "section_scores": {
                "policy": {
                    "raw": round(self.section_a_policy.raw_score, 1),
                    "weighted": round(self.section_a_policy.weighted_score, 1),
                    "max": self.section_a_policy.max_score,
                    "items": self.section_a_policy.items
                },
                "location": {
                    "raw": round(self.section_b_location.raw_score, 1),
                    "weighted": round(self.section_b_location.weighted_score, 1),
                    "max": self.section_b_location.max_score,
                    "items": self.section_b_location.items
                },
                "construction": {
                    "raw": round(self.section_c_construction.raw_score, 1),
                    "weighted": round(self.section_c_construction.weighted_score, 1),
                    "max": self.section_c_construction.max_score,
                    "items": self.section_c_construction.items
                },
                "price": {
                    "raw": round(self.section_d_price.raw_score, 1),
                    "weighted": round(self.section_d_price.weighted_score, 1),
                    "max": self.section_d_price.max_score,
                    "items": self.section_d_price.items
                },
                "business": {
                    "raw": round(self.section_e_business.raw_score, 1),
                    "weighted": round(self.section_e_business.weighted_score, 1),
                    "max": self.section_e_business.max_score,
                    "items": self.section_e_business.items
                }
            },
            "applied_weights": self.applied_weights
        }


def determine_grade(score: float) -> GradeType:
    """점수 기반 등급 결정"""
    if score >= 95:
        return GradeType.S
    elif score >= 90:
        return GradeType.A_PLUS
    elif score >= 85:
        return GradeType.A
    elif score >= 80:
        return GradeType.B_PLUS
    elif score >= 75:
        return GradeType.B
    elif score >= 70:
        return GradeType.C_PLUS
    elif score >= 65:
        return GradeType.C
    elif score >= 60:
        return GradeType.D
    else:
        return GradeType.F


def determine_judgement(score: float, fatal_reject: bool) -> JudgementType:
    """
    최종 판정 결정
    
    IF fatal_reject = TRUE
        → NO-GO (즉시 탈락)
    
    ELSE IF lh_score >= 85
        → GO
    
    ELSE IF 70 <= lh_score < 85
        → CONDITIONAL (보완 시 가능)
    
    ELSE
        → NO-GO
    """
    if fatal_reject:
        return JudgementType.NO_GO
    
    if score >= 85:
        return JudgementType.GO
    elif score >= 70:
        return JudgementType.CONDITIONAL
    else:
        return JudgementType.NO_GO


def determine_confidence_level(
    fatal_reject: bool,
    data_completeness: float
) -> str:
    """신뢰도 결정"""
    if fatal_reject:
        return "HIGH"  # 탈락 판정은 확실
    
    if data_completeness >= 0.9:
        return "HIGH"
    elif data_completeness >= 0.7:
        return "MEDIUM"
    else:
        return "LOW"


__all__ = [
    "JudgementType",
    "GradeType",
    "RegionWeightType",
    "SectionScore",
    "RegionWeights",
    "M6ComprehensiveResult",
    "determine_grade",
    "determine_judgement",
    "determine_confidence_level"
]
