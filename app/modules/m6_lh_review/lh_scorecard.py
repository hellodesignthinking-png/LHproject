"""
LH 실제 평가표 (100점 체계)
==========================

이 모듈은 LH 실제 내부 평가표를 1:1로 코드화한 것입니다.

평가 항목 (총 100점):
① 입지 적합성: 20점
② 토지 확보 용이성: 15점
③ 건축·기술 적합성: 15점
④ 사업성(재무): 25점
⑤ 정책 부합성: 15점
⑥ 사업 리스크: 10점

❌ 항목 추가/삭제 불가
❌ 배점 변경 불가
❌ 가상의 평가 항목 생성 불가

Author: ZeroSite M6 Team
Date: 2025-12-26
Version: 1.0 (LH Standard)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class LHBranchType(Enum):
    """LH 지점 유형"""
    CAPITAL = "CAPITAL"  # 수도권 (서울·경기·인천)
    LOCAL = "LOCAL"      # 지방 (광역시·중소도시)


@dataclass(frozen=True)
class LHScorecardWeights:
    """
    LH 지점별 가중치 테이블
    
    ⚠️ 가중 후 자동 정규화하여 총점 100 유지
    """
    location: float       # 입지 적합성
    land: float          # 토지 확보 용이성
    technical: float     # 건축·기술 적합성
    financial: float     # 사업성(재무)
    policy: float        # 정책 부합성
    risk: float          # 사업 리스크
    
    def to_dict(self) -> Dict[str, float]:
        """가중치를 딕셔너리로 변환"""
        return {
            "location": self.location,
            "land": self.land,
            "technical": self.technical,
            "financial": self.financial,
            "policy": self.policy,
            "risk": self.risk
        }


# ============================================================================
# LH 지점별 가중치 정의
# ============================================================================

# 수도권 LH 가중치
# - 입지·사업성·리스크에 매우 민감
# - 정책 유형은 기본 충족 여부만 확인
CAPITAL_WEIGHTS = LHScorecardWeights(
    location=1.15,   # 입지 중시
    land=1.00,       # 표준
    technical=1.00,  # 표준
    financial=1.15,  # 사업성 중시
    policy=0.85,     # 정책은 기본만
    risk=1.20        # 리스크 매우 민감
)

# 지방 LH 가중치
# - 정책 부합성·공급 필요성 중시
# - 재무성은 최소 기준 충족 여부 위주
# - 리스크는 상대적으로 관대
LOCAL_WEIGHTS = LHScorecardWeights(
    location=0.90,   # 입지는 상대적으로 덜 중요
    land=1.05,       # 토지 확보 가능성 중시
    technical=1.00,  # 표준
    financial=0.90,  # 사업성은 최소 기준만
    policy=1.30,     # 정책 부합성 매우 중시
    risk=0.85        # 리스크에 관대
)


def get_branch_weights(branch_type: LHBranchType) -> LHScorecardWeights:
    """
    지점 유형에 따른 가중치 반환
    
    Args:
        branch_type: LH 지점 유형 (CAPITAL or LOCAL)
    
    Returns:
        LHScorecardWeights
    """
    if branch_type == LHBranchType.CAPITAL:
        return CAPITAL_WEIGHTS
    elif branch_type == LHBranchType.LOCAL:
        return LOCAL_WEIGHTS
    else:
        raise ValueError(f"Unknown branch type: {branch_type}")


@dataclass(frozen=True)
class RawScores:
    """
    원점수 (가중치 적용 전)
    
    각 항목의 최대 점수:
    - location: 20점
    - land: 15점
    - technical: 15점
    - financial: 25점
    - policy: 15점
    - risk: 10점
    """
    location: float     # 입지 적합성 (20점 만점)
    land: float        # 토지 확보 용이성 (15점 만점)
    technical: float   # 건축·기술 적합성 (15점 만점)
    financial: float   # 사업성(재무) (25점 만점)
    policy: float      # 정책 부합성 (15점 만점)
    risk: float        # 사업 리스크 (10점 만점)
    
    @property
    def total(self) -> float:
        """총점 (100점 만점)"""
        return (
            self.location +
            self.land +
            self.technical +
            self.financial +
            self.policy +
            self.risk
        )
    
    def to_dict(self) -> Dict[str, float]:
        """점수를 딕셔너리로 변환"""
        return {
            "location": self.location,
            "land": self.land,
            "technical": self.technical,
            "financial": self.financial,
            "policy": self.policy,
            "risk": self.risk,
            "total": self.total
        }


@dataclass(frozen=True)
class WeightedScores:
    """
    가중치 적용 후 점수 (정규화 완료)
    
    ⚠️ 총점은 항상 100점 기준으로 정규화됨
    """
    location: float
    land: float
    technical: float
    financial: float
    policy: float
    risk: float
    
    @property
    def total(self) -> float:
        """총점 (100점)"""
        return (
            self.location +
            self.land +
            self.technical +
            self.financial +
            self.policy +
            self.risk
        )
    
    def to_dict(self) -> Dict[str, float]:
        """점수를 딕셔너리로 변환"""
        return {
            "location": round(self.location, 1),
            "land": round(self.land, 1),
            "technical": round(self.technical, 1),
            "financial": round(self.financial, 1),
            "policy": round(self.policy, 1),
            "risk": round(self.risk, 1),
            "total": round(self.total, 1)
        }


def apply_branch_weights(
    raw_scores: RawScores,
    branch_type: LHBranchType
) -> WeightedScores:
    """
    지점별 가중치 적용 (총점 유지)
    
    Args:
        raw_scores: 원점수
        branch_type: LH 지점 유형
    
    Returns:
        WeightedScores (가중치 적용, 총점은 raw_scores.total과 동일)
    
    Process:
        1. 각 항목에 가중치 적용
        2. 가중 합계 계산
        3. 원점수 총점을 유지하도록 정규화
    
    Example:
        - Raw: location=17, financial=5 (total=22 + others)
        - CAPITAL weights: location×1.15, financial×1.15
        - After weighting: location=19.55, financial=5.75
        - Normalize to maintain raw total
    """
    weights = get_branch_weights(branch_type)
    
    # 1. 가중치 적용
    weighted = {
        "location": raw_scores.location * weights.location,
        "land": raw_scores.land * weights.land,
        "technical": raw_scores.technical * weights.technical,
        "financial": raw_scores.financial * weights.financial,
        "policy": raw_scores.policy * weights.policy,
        "risk": raw_scores.risk * weights.risk
    }
    
    # 2. 가중 합계
    weighted_sum = sum(weighted.values())
    
    # 3. 원점수 총점을 유지하도록 정규화
    # scale_factor = 원점수 총점 / 가중 합계
    raw_total = raw_scores.total
    scale_factor = raw_total / weighted_sum if weighted_sum > 0 else 1.0
    
    normalized = {
        key: value * scale_factor
        for key, value in weighted.items()
    }
    
    logger.debug(f"Branch Type: {branch_type.value}")
    logger.debug(f"Raw Total: {raw_total:.1f}")
    logger.debug(f"Weighted Sum: {weighted_sum:.1f}")
    logger.debug(f"Scale Factor: {scale_factor:.4f}")
    logger.debug(f"Normalized Total: {sum(normalized.values()):.1f}")
    
    return WeightedScores(
        location=normalized["location"],
        land=normalized["land"],
        technical=normalized["technical"],
        financial=normalized["financial"],
        policy=normalized["policy"],
        risk=normalized["risk"]
    )


class LHDecision(Enum):
    """LH 최종 판단"""
    GO = "GO"                    # ≥ 80점
    CONDITIONAL = "CONDITIONAL"  # 70~79점
    HOLD = "HOLD"                # < 70점


def determine_decision(total_score: float) -> LHDecision:
    """
    총점 기반 LH 최종 판단
    
    ⚠️ 지점 유형과 무관하게 동일한 기준 적용
    
    Args:
        total_score: 총점 (0~100)
    
    Returns:
        LHDecision
    """
    if total_score >= 80:
        return LHDecision.GO
    elif total_score >= 70:
        return LHDecision.CONDITIONAL
    else:
        return LHDecision.HOLD


@dataclass(frozen=True)
class LHScorecardResult:
    """
    LH 평가표 최종 결과
    
    이 구조는 보고서·API·PDF 모두에서 동일하게 사용
    """
    branch_type: LHBranchType
    raw_scores: RawScores
    weighted_scores: WeightedScores
    weights_applied: Dict[str, float]
    total_score: float
    decision: LHDecision
    decision_reasons: List[str]
    
    def to_dict(self) -> Dict:
        """결과를 딕셔너리로 변환"""
        return {
            "branch_type": self.branch_type.value,
            "raw_scores": self.raw_scores.to_dict(),
            "weighted_scores": self.weighted_scores.to_dict(),
            "weights_applied": self.weights_applied,
            "total_score": round(self.total_score, 1),
            "decision": self.decision.value,
            "decision_reasons": self.decision_reasons
        }


__all__ = [
    "LHBranchType",
    "LHScorecardWeights",
    "RawScores",
    "WeightedScores",
    "LHDecision",
    "LHScorecardResult",
    "CAPITAL_WEIGHTS",
    "LOCAL_WEIGHTS",
    "get_branch_weights",
    "apply_branch_weights",
    "determine_decision"
]
