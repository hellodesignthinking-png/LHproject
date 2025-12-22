"""
M6: LH Review Context
======================

LH 심사 예측 모듈(M6) 출력 Context

LH 신축매입임대 공식 평가 기준 (110점 체계):
1. 입지 평가 (35점)
2. 사업 규모 (20점)
3. 사업성 평가 (40점)
4. 법규 적합성 (15점)

최종 판단: GO / NO-GO / CONDITIONAL

⚠️ 절대 규칙:
- M1-M5 Context를 READ-ONLY로만 참조
- 어떤 Context도 수정 금지
- 계산 결과만 출력

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class DecisionType(str, Enum):
    """의사결정 유형"""
    GO = "GO"                           # 진행 권장
    NO_GO = "NO_GO"                     # 진행 불가
    CONDITIONAL = "CONDITIONAL"         # 조건부 진행


class ProjectGrade(str, Enum):
    """프로젝트 등급"""
    S = "S"  # 90점 이상
    A = "A"  # 80-89점
    B = "B"  # 70-79점
    C = "C"  # 60-69점
    D = "D"  # 50-59점
    F = "F"  # 50점 미만


@dataclass(frozen=True)
class ScoreBreakdown:
    """점수 세부 분석"""
    location_score: float               # 입지 (35점)
    scale_score: float                  # 규모 (20점)
    feasibility_score: float            # 사업성 (40점)
    compliance_score: float             # 법규 (15점)
    total_score: float                  # 총점 (110점)
    
    def __post_init__(self):
        assert 0 <= self.location_score <= 35
        assert 0 <= self.scale_score <= 20
        assert 0 <= self.feasibility_score <= 40
        assert 0 <= self.compliance_score <= 15
        assert 0 <= self.total_score <= 110


@dataclass(frozen=True)
class ApprovalPrediction:
    """승인 예측"""
    approval_probability: float         # 승인 확률 (0-1)
    approval_likelihood: str            # 승인 가능성 (HIGH/MEDIUM/LOW)
    expected_conditions: List[str]      # 예상 조건사항
    critical_factors: List[str]         # 핵심 요인


@dataclass(frozen=True)
class LHReviewContext:
    """
    LH 심사 예측 Context (M6 출력)
    
    frozen=True: 생성 후 수정 불가
    
    최종 판단 모듈로, 모든 Context를 READ-ONLY로 참조
    """
    
    # === 종합 점수 ===
    score_breakdown: ScoreBreakdown     # 세부 점수
    total_score: float                  # 총점 (110점)
    grade: ProjectGrade                 # 등급 (S/A/B/C/D/F)
    
    # === 최종 의사결정 ===
    decision: DecisionType              # GO / NO-GO / CONDITIONAL
    decision_rationale: str             # 판단 근거
    
    # === 승인 예측 ===
    approval_prediction: ApprovalPrediction  # 승인 예측
    
    # === 메타데이터 ===
    review_date: str                    # 심사 일시
    reviewer: str                       # 리뷰어
    review_version: str                 # 리뷰 버전
    
    # === 강점 & 약점 ===
    strengths: List[str] = field(default_factory=list)       # 강점
    weaknesses: List[str] = field(default_factory=list)      # 약점
    opportunities: List[str] = field(default_factory=list)   # 기회
    threats: List[str] = field(default_factory=list)         # 위협
    
    # === 권장사항 ===
    recommendations: List[str] = field(default_factory=list)  # 권장사항
    action_items: List[str] = field(default_factory=list)    # 실행 항목
    
    # === 개선 포인트 ===
    improvement_areas: Dict[str, str] = field(default_factory=dict)  # 개선 영역
    
    # === 정책 가중치 (참고용) ===
    policy_weights: Dict[str, float] = field(default_factory=dict)   # 정책 가중치
    
    def __post_init__(self):
        """유효성 검증"""
        assert 0 <= self.total_score <= 110, "총점은 0-110 범위"
        assert self.decision in DecisionType, "올바른 의사결정 유형"
        assert self.grade in ProjectGrade, "올바른 프로젝트 등급"
        assert 0 <= self.approval_prediction.approval_probability <= 1, \
            "승인 확률은 0-1 범위"
    
    @property
    def is_go_decision(self) -> bool:
        """진행 권장 여부"""
        return self.decision == DecisionType.GO
    
    @property
    def is_high_grade(self) -> bool:
        """높은 등급 여부 (S or A)"""
        return self.grade in [ProjectGrade.S, ProjectGrade.A]
    
    @property
    def is_likely_approved(self) -> bool:
        """승인 가능성 높음"""
        return self.approval_prediction.approval_probability > 0.7
    
    @property
    def passing_score(self) -> bool:
        """합격 점수 여부 (80점 이상)"""
        return self.total_score >= 80
    
    @property
    def review_summary(self) -> str:
        """심사 요약"""
        return (
            f"등급: {self.grade.value} ({self.total_score:.1f}/110점)\n"
            f"의사결정: {self.decision.value}\n"
            f"승인 확률: {self.approval_prediction.approval_probability:.0%}\n"
            f"강점: {len(self.strengths)}개 / 약점: {len(self.weaknesses)}개"
        )
    
    @property
    def detailed_scores(self) -> str:
        """상세 점수"""
        return (
            f"입지: {self.score_breakdown.location_score:.1f}/35점\n"
            f"규모: {self.score_breakdown.scale_score:.1f}/20점\n"
            f"사업성: {self.score_breakdown.feasibility_score:.1f}/40점\n"
            f"법규: {self.score_breakdown.compliance_score:.1f}/15점"
        )
    
    def to_dict(self) -> Dict[str, any]:
        """딕셔너리 변환"""
        return {
            "scores": {
                "location": self.score_breakdown.location_score,
                "scale": self.score_breakdown.scale_score,
                "feasibility": self.score_breakdown.feasibility_score,
                "compliance": self.score_breakdown.compliance_score,
                "total": self.total_score
            },
            "grade": self.grade.value,
            "decision": {
                "type": self.decision.value,
                "rationale": self.decision_rationale
            },
            "approval": {
                "probability": self.approval_prediction.approval_probability,
                "likelihood": self.approval_prediction.approval_likelihood,
                "expected_conditions": self.approval_prediction.expected_conditions,
                "critical_factors": self.approval_prediction.critical_factors
            },
            "swot": {
                "strengths": self.strengths,
                "weaknesses": self.weaknesses,
                "opportunities": self.opportunities,
                "threats": self.threats
            },
            "recommendations": {
                "general": self.recommendations,
                "actions": self.action_items,
                "improvements": self.improvement_areas
            },
            "metadata": {
                "date": self.review_date,
                "reviewer": self.reviewer,
                "version": self.review_version
            }
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return self.review_summary
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return (
            f"LHReviewContext("
            f"grade={self.grade.value}, "
            f"score={self.total_score:.1f}, "
            f"decision={self.decision.value})"
        )
