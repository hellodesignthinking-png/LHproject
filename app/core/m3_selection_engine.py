"""
M3 Supply Type Selection Engine (M2 Score 기반)
=================================================

핵심 원칙:
1. M3 = M2 점수 해석기 (독립 판단 금지)
2. M2 결과를 공급유형별로 번역하는 역할
3. 모든 판단은 M2 점수에서 추적 가능

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 1.0 (M2 기반 재설계)
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ============================================================
# 공급유형 정의 (LH 실무 기준)
# ============================================================

class SupplyType(str, Enum):
    """LH 신축매입임대 공급유형"""
    YOUTH = "YOUTH"              # 청년 매입임대
    NEWLYWED = "NEWLYWED"        # 신혼부부 매입임대
    SENIOR = "SENIOR"            # 고령자 매입임대
    GENERAL = "GENERAL"          # 일반 매입임대

class SupplyTypeFitness(str, Enum):
    """공급유형 적합도"""
    HIGH = "HIGH"                # 높음 (80% 이상)
    MEDIUM_HIGH = "MEDIUM_HIGH"  # 중상 (60~80%)
    MEDIUM = "MEDIUM"            # 중간 (40~60%)
    LOW = "LOW"                  # 낮음 (40% 미만)
    BLOCKED = "BLOCKED"          # 차단됨 (치명 리스크)

# ============================================================
# M2 → M3 Data Contract
# ============================================================

class M2ScoreInput(BaseModel):
    """M3가 사용 가능한 M2 데이터 (허용 목록)"""
    m2_total_score: int = Field(..., ge=0, le=100, description="M2 총점")
    m2_risk_flags: List[str] = Field(default_factory=list, description="M2 리스크 플래그")
    m2_score_breakdown: Dict[str, int] = Field(..., description="M2 점수 세부")
    m2_recommendation: str = Field(..., description="M2 권고 (GO/CONDITIONAL-GO/NO-GO)")

class SupplyTypeCandidate(BaseModel):
    """공급유형 후보"""
    type: SupplyType
    fitness: SupplyTypeFitness
    confidence: float = Field(..., ge=0, le=1, description="신뢰도 (0~1)")
    reasons: List[str] = Field(default_factory=list, description="선정 이유")
    blocking_reasons: List[str] = Field(default_factory=list, description="차단 이유")

class M3SelectionResult(BaseModel):
    """M3 공급유형 선택 결과"""
    recommended_type: SupplyType
    confidence: float = Field(..., ge=0, le=1, description="추천 신뢰도")
    alternative_types: List[SupplyType] = Field(default_factory=list, description="대안 유형")
    
    # 설명 책임
    reason_summary: List[str] = Field(..., min_length=1, description="선정 이유 요약")
    all_candidates: List[SupplyTypeCandidate] = Field(..., description="전체 후보군 평가")
    
    # M2 추적성
    m2_total_score: int
    m2_breakdown: Dict[str, int]
    
    # 메타데이터
    calculated_at: str

# ============================================================
# M3 Selection Engine
# ============================================================

class M3SelectionEngine:
    """
    M3 공급유형 선택 엔진
    
    입력: M2ScoreInput (M2 점수만 허용)
    출력: M3SelectionResult (공급유형 + 설명)
    
    원칙:
    - M1 직접 참조 금지
    - 정책 DB 재조회 금지
    - Frontend 추론 금지
    - M2 점수가 유일한 입력
    """
    
    def __init__(self):
        self.logger = logger
    
    def select(self, m2_input: M2ScoreInput) -> M3SelectionResult:
        """
        M3 공급유형 선택 메인 함수
        
        Args:
            m2_input: M2 점수 및 세부 정보
            
        Returns:
            M3SelectionResult: 추천 유형 + 설명
        """
        self.logger.info("=" * 80)
        self.logger.info("🏘️  M3 SUPPLY TYPE SELECTION START (M2 점수 기반)")
        self.logger.info("=" * 80)
        self.logger.info(f"📊 M2 입력: 총점 {m2_input.m2_total_score}점, 리스크 {len(m2_input.m2_risk_flags)}개")
        
        # 모든 공급유형 후보 평가
        candidates = []
        
        # (A) 청년 매입임대
        youth_candidate = self._evaluate_youth(m2_input)
        candidates.append(youth_candidate)
        
        # (B) 신혼부부 매입임대
        newlywed_candidate = self._evaluate_newlywed(m2_input)
        candidates.append(newlywed_candidate)
        
        # (C) 고령자 매입임대
        senior_candidate = self._evaluate_senior(m2_input)
        candidates.append(senior_candidate)
        
        # (D) 일반 매입임대
        general_candidate = self._evaluate_general(m2_input)
        candidates.append(general_candidate)
        
        # 최적 후보 선택 (fitness 높은 순)
        viable_candidates = [c for c in candidates if c.fitness != SupplyTypeFitness.BLOCKED]
        
        if not viable_candidates:
            self.logger.warning("⚠️  모든 공급유형이 차단됨")
            # 가장 차단 이유가 적은 것 선택
            recommended = min(candidates, key=lambda c: len(c.blocking_reasons))
        else:
            # fitness 점수로 정렬
            fitness_score_map = {
                SupplyTypeFitness.HIGH: 4,
                SupplyTypeFitness.MEDIUM_HIGH: 3,
                SupplyTypeFitness.MEDIUM: 2,
                SupplyTypeFitness.LOW: 1,
                SupplyTypeFitness.BLOCKED: 0
            }
            viable_candidates.sort(key=lambda c: (fitness_score_map[c.fitness], c.confidence), reverse=True)
            recommended = viable_candidates[0]
        
        # 대안 유형 (상위 3개)
        alternative_types = [c.type for c in viable_candidates[1:4] if c.type != recommended.type]
        
        # 이유 요약 생성
        reason_summary = self._generate_reason_summary(m2_input, recommended)
        
        from datetime import datetime
        result = M3SelectionResult(
            recommended_type=recommended.type,
            confidence=recommended.confidence,
            alternative_types=alternative_types,
            reason_summary=reason_summary,
            all_candidates=candidates,
            m2_total_score=m2_input.m2_total_score,
            m2_breakdown=m2_input.m2_score_breakdown,
            calculated_at=datetime.utcnow().isoformat()
        )
        
        self.logger.info(f"✅ M3 선택 완료: {recommended.type.value} ({recommended.fitness.value}, {recommended.confidence:.0%})")
        self.logger.info(f"   대안 유형: {[t.value for t in alternative_types]}")
        self.logger.info("=" * 80)
        
        return result
    
    def _evaluate_youth(self, m2: M2ScoreInput) -> SupplyTypeCandidate:
        """(A) 청년 매입임대 적합성 평가"""
        reasons = []
        blocking = []
        
        # 조건 1: M2 총점 ≥ 70
        if m2.m2_total_score >= 70:
            reasons.append(f"M2 총점 {m2.m2_total_score}점으로 기준 충족 (≥70)")
        else:
            blocking.append(f"M2 총점 {m2.m2_total_score}점으로 기준 미달 (<70)")
        
        # 조건 2: 도로 점수 ≥ 0
        road_score = m2.m2_score_breakdown.get("road", 0)
        if road_score >= 0:
            reasons.append(f"도로 점수 {road_score:+d}점으로 양호")
        else:
            blocking.append(f"도로 점수 {road_score:+d}점으로 리스크")
        
        # 조건 3: 방향 점수 ≥ 0
        orientation_score = m2.m2_score_breakdown.get("orientation", 0)
        if orientation_score >= 0:
            reasons.append("방향/일조 조건 양호")
        else:
            blocking.append("방향/일조 리스크 존재")
        
        # 조건 4: ROAD_NARROW 리스크 없음
        if "ROAD_NARROW" not in m2.m2_risk_flags:
            reasons.append("도로 협소 리스크 없음")
        else:
            blocking.append("도로 협소로 접근성 우려")
        
        # 적합도 결정
        if blocking:
            fitness = SupplyTypeFitness.BLOCKED
            confidence = 0.0
        elif m2.m2_total_score >= 80:
            fitness = SupplyTypeFitness.HIGH
            confidence = 0.9
        elif m2.m2_total_score >= 70:
            fitness = SupplyTypeFitness.MEDIUM_HIGH
            confidence = 0.75
        else:
            fitness = SupplyTypeFitness.LOW
            confidence = 0.4
        
        return SupplyTypeCandidate(
            type=SupplyType.YOUTH,
            fitness=fitness,
            confidence=confidence,
            reasons=reasons,
            blocking_reasons=blocking
        )
    
    def _evaluate_newlywed(self, m2: M2ScoreInput) -> SupplyTypeCandidate:
        """(B) 신혼부부 매입임대 적합성 평가"""
        reasons = []
        blocking = []
        
        # 조건 1: 60 ≤ M2 총점 < 75
        if 60 <= m2.m2_total_score < 75:
            reasons.append(f"M2 총점 {m2.m2_total_score}점으로 신혼부부 대상 적정")
        elif m2.m2_total_score >= 75:
            reasons.append(f"M2 총점 {m2.m2_total_score}점으로 우수 (청년 대상 더 적합)")
        else:
            blocking.append(f"M2 총점 {m2.m2_total_score}점으로 기준 미달 (<60)")
        
        # 조건 2: 형상 점수 ≥ 0
        shape_score = m2.m2_score_breakdown.get("shape", 0)
        if shape_score >= 0:
            reasons.append(f"대지 형상 양호 ({shape_score:+d}점)")
        else:
            blocking.append(f"대지 형상 부적합 ({shape_score:+d}점)")
        
        # 조건 3: 시세 점수 ≥ 0
        market_score = m2.m2_score_breakdown.get("market", 0)
        if market_score >= 0:
            reasons.append("시세 적정")
        else:
            blocking.append("시세 과대평가 우려")
        
        # 적합도 결정
        if blocking:
            fitness = SupplyTypeFitness.BLOCKED
            confidence = 0.0
        elif 65 <= m2.m2_total_score < 75:
            fitness = SupplyTypeFitness.HIGH
            confidence = 0.85
        elif 60 <= m2.m2_total_score < 65:
            fitness = SupplyTypeFitness.MEDIUM_HIGH
            confidence = 0.7
        else:
            fitness = SupplyTypeFitness.LOW
            confidence = 0.3
        
        return SupplyTypeCandidate(
            type=SupplyType.NEWLYWED,
            fitness=fitness,
            confidence=confidence,
            reasons=reasons,
            blocking_reasons=blocking
        )
    
    def _evaluate_senior(self, m2: M2ScoreInput) -> SupplyTypeCandidate:
        """(C) 고령자 매입임대 적합성 평가"""
        reasons = []
        blocking = []
        
        # 조건 1: M2 총점 ≥ 55
        if m2.m2_total_score >= 55:
            reasons.append(f"M2 총점 {m2.m2_total_score}점으로 기준 충족 (≥55)")
        else:
            blocking.append(f"M2 총점 {m2.m2_total_score}점으로 기준 미달 (<55)")
        
        # 조건 2: 도로 점수 (협소하지 않아야 함)
        if "ROAD_FATAL" not in m2.m2_risk_flags:
            reasons.append("도로 조건 고령자 접근 가능")
        else:
            blocking.append("도로 협소로 고령자 접근 어려움")
        
        # 추가: 방향 점수는 무관하지만 언급
        orientation_score = m2.m2_score_breakdown.get("orientation", 0)
        if orientation_score >= 0:
            reasons.append("일조 조건 양호 (고령자 선호)")
        
        # 적합도 결정
        if blocking:
            fitness = SupplyTypeFitness.BLOCKED
            confidence = 0.0
        elif m2.m2_total_score >= 65:
            fitness = SupplyTypeFitness.MEDIUM_HIGH
            confidence = 0.7
        elif m2.m2_total_score >= 55:
            fitness = SupplyTypeFitness.MEDIUM
            confidence = 0.6
        else:
            fitness = SupplyTypeFitness.LOW
            confidence = 0.3
        
        return SupplyTypeCandidate(
            type=SupplyType.SENIOR,
            fitness=fitness,
            confidence=confidence,
            reasons=reasons,
            blocking_reasons=blocking
        )
    
    def _evaluate_general(self, m2: M2ScoreInput) -> SupplyTypeCandidate:
        """(D) 일반 매입임대 적합성 평가"""
        reasons = []
        blocking = []
        
        # 조건 1: M2 총점 ≥ 50
        if m2.m2_total_score >= 50:
            reasons.append(f"M2 총점 {m2.m2_total_score}점으로 최소 기준 충족")
        else:
            blocking.append(f"M2 총점 {m2.m2_total_score}점으로 기준 미달 (<50)")
        
        # 조건 2: 치명 리스크 없음
        fatal_risks = ["ROAD_FATAL", "FIRE_TRUCK_NO_ACCESS"]
        has_fatal = any(risk in m2.m2_risk_flags for risk in fatal_risks)
        
        if not has_fatal:
            reasons.append("치명적 리스크 없음")
        else:
            blocking.append("치명적 리스크 존재 (도로/소방)")
        
        # 적합도 결정 (일반은 최후 보루)
        if blocking:
            fitness = SupplyTypeFitness.BLOCKED
            confidence = 0.0
        elif m2.m2_total_score >= 60:
            fitness = SupplyTypeFitness.MEDIUM
            confidence = 0.6
        elif m2.m2_total_score >= 50:
            fitness = SupplyTypeFitness.LOW
            confidence = 0.5
        else:
            fitness = SupplyTypeFitness.LOW
            confidence = 0.2
        
        return SupplyTypeCandidate(
            type=SupplyType.GENERAL,
            fitness=fitness,
            confidence=confidence,
            reasons=reasons,
            blocking_reasons=blocking
        )
    
    def _generate_reason_summary(self, m2: M2ScoreInput, recommended: SupplyTypeCandidate) -> List[str]:
        """이유 요약 생성"""
        summary = []
        
        # M2 점수 언급
        if m2.m2_total_score >= 70:
            summary.append(f"M2 총점 {m2.m2_total_score}점으로 상위권")
        elif m2.m2_total_score >= 50:
            summary.append(f"M2 총점 {m2.m2_total_score}점으로 중위권")
        else:
            summary.append(f"M2 총점 {m2.m2_total_score}점으로 하위권")
        
        # 리스크 언급
        if len(m2.m2_risk_flags) == 0:
            summary.append("리스크 플래그 없음")
        elif len(m2.m2_risk_flags) <= 2:
            summary.append(f"경미한 리스크 {len(m2.m2_risk_flags)}개")
        else:
            summary.append(f"주의 리스크 {len(m2.m2_risk_flags)}개")
        
        # 추천 유형 이유
        summary.append(f"{recommended.type.value} 기준 충족")
        
        return summary


# ============================================================
# 전역 인스턴스
# ============================================================

selection_engine = M3SelectionEngine()
