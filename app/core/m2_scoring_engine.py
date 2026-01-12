"""
M2 Land Valuation Scoring Engine (LH Standard)
M1 FACT → M2 Score 자동 연계 시스템

핵심 원칙:
1. M1 FROZEN FACT만 사용 (Single Source of Truth)
2. 모든 점수는 M1→Rule→Score 명확한 매핑
3. score_breakdown 100% 설명 가능
4. M6까지 추적 가능

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 3.0 (M1 FACT 기반 재설계)
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ============================================================
# 리스크 플래그 정의
# ============================================================

class RiskFlag(str, Enum):
    """M2 리스크 플래그 (치명도별)"""
    # 도로 관련
    ROAD_FATAL = "ROAD_FATAL"              # 도로 4m 미만 (치명적)
    ROAD_NARROW = "ROAD_NARROW"            # 도로 6m 미만
    FIRE_TRUCK_NO_ACCESS = "FIRE_TRUCK_NO_ACCESS"  # 소방차 진입 불가
    
    # 형상 관련
    SHAPE_IRREGULAR = "SHAPE_IRREGULAR"    # 부정형/자루형
    SHAPE_LOW_EFFICIENCY = "SHAPE_LOW_EFFICIENCY"  # 유효건축비율 70% 미만
    
    # 방향/일조 관련
    SUNLIGHT_RISK = "SUNLIGHT_RISK"        # 일조권 리스크 높음
    ADJACENT_HEIGHT_RISK = "ADJACENT_HEIGHT_RISK"  # 인접고층 리스크
    
    # 시세 관련
    PRICE_GAP_HIGH = "PRICE_GAP_HIGH"      # 시세 갭 비율 2.0 초과
    
    # 건물 관련
    DEMOLITION_REQUIRED = "DEMOLITION_REQUIRED"  # 철거 필요
    BUILDING_STRUCTURE_COMPLEX = "BUILDING_STRUCTURE_COMPLEX"  # 구조 복잡

# ============================================================
# M1 FACT Data Contract
# ============================================================

class M1FactContract(BaseModel):
    """M2가 사용 가능한 M1 FACT 필드 (허용 목록)"""
    
    # 기본 토지 정보
    address: str
    lat: float
    lng: float
    land_area: float  # ㎡
    zoning: str  # 용도지역
    bcr: float  # 건폐율
    far: float  # 용적률
    official_land_price: float  # 공시지가 (원/㎡)
    
    # 도로 조건 (5개 필수)
    road_access_type: str  # 접도 유형
    road_width_m: float  # 도로 폭 (m)
    road_count: int  # 접도 수
    fire_truck_access: bool  # 소방차 진입 가능 여부
    road_legal_status: str  # 도로 법적 지위
    
    # 대지 형상 (4개 필수)
    site_shape_type: str  # 형상 유형
    frontage_m: float  # 전면 폭 (m)
    depth_m: float  # 깊이 (m)
    effective_build_ratio: float  # 유효 건축 비율 (%)
    
    # 방향/일조 (3개)
    main_direction: str  # 주향
    sunlight_risk: str  # 일조권 리스크
    adjacent_height_risk: str  # 인접 고층 리스크
    
    # 시세 정보 (3개 중 최소 1개)
    nearby_transaction_price_py: Optional[float] = None  # 인근 거래가 (원/평)
    public_land_price_py: Optional[float] = None  # 공시지가 (원/평)
    price_gap_ratio: Optional[float] = None  # 가격 갭 비율
    
    # 기존 건물 (선택)
    existing_building_exists: bool = False
    existing_building_structure: Optional[str] = None
    existing_building_floors: Optional[int] = None
    existing_building_area_m2: Optional[float] = None
    demolition_required: Optional[bool] = None
    
    # 기타
    transaction_price: Optional[float] = None
    regulation_summary: Optional[str] = None
    lh_compatibility: Optional[str] = None

# ============================================================
# M2 점수 세부 항목
# ============================================================

class ScoreBreakdown(BaseModel):
    """M2 점수 세부 항목 (M6 대시보드 노출용)"""
    road: int = Field(..., description="도로 점수")
    shape: int = Field(..., description="대지 형상 점수")
    orientation: int = Field(..., description="방향/일조 점수")
    market: int = Field(..., description="시세 적정성 점수")
    building: int = Field(..., description="기존 건물 리스크 점수")
    total: int = Field(..., description="총점")
    
    # 각 항목별 설명 (M6 카드 노출)
    road_detail: str = ""
    shape_detail: str = ""
    orientation_detail: str = ""
    market_detail: str = ""
    building_detail: str = ""

# ============================================================
# M2 점수 계산 결과
# ============================================================

class M2ScoringResult(BaseModel):
    """M2 점수 계산 결과"""
    total_score: int = Field(..., ge=0, le=100, description="총점 (0-100)")
    risk_flags: List[RiskFlag] = Field(default_factory=list, description="리스크 플래그")
    score_breakdown: ScoreBreakdown = Field(..., description="점수 세부 항목")
    
    # 매입 권고
    recommendation: str = Field(..., description="GO/NO-GO 권고")
    confidence: int = Field(..., ge=0, le=100, description="신뢰도 (%)")
    
    # 추적성
    m1_context_id: str = Field(..., description="M1 Context ID")
    calculated_at: str = Field(..., description="계산 시각")

# ============================================================
# M2 점수 계산 엔진 (핵심)
# ============================================================

class M2ScoringEngine:
    """
    M2 점수 계산 엔진
    
    입력: M1FactContract (M1 FROZEN FACT만 허용)
    출력: M2ScoringResult (total_score + risk_flags + score_breakdown)
    
    원칙:
    - M1 외의 데이터 사용 금지
    - 모든 점수는 명확한 규칙 기반
    - Frontend 계산 금지
    - M2 내부 추정 금지
    """
    
    def __init__(self):
        self.logger = logger
    
    def calculate(self, m1_fact: M1FactContract, context_id: str) -> M2ScoringResult:
        """
        M2 점수 계산 메인 함수
        
        Args:
            m1_fact: M1 FROZEN FACT
            context_id: M1 Context ID
            
        Returns:
            M2ScoringResult: 점수 + 리스크 + 설명
        """
        self.logger.info("=" * 80)
        self.logger.info("🧮 M2 SCORING ENGINE START (M1 FACT 기반)")
        self.logger.info("=" * 80)
        
        risk_flags: List[RiskFlag] = []
        
        # (A) 도로 점수 계산
        road_score, road_detail, road_risks = self._calculate_road_score(m1_fact)
        risk_flags.extend(road_risks)
        
        # (B) 대지 형상 점수 계산
        shape_score, shape_detail, shape_risks = self._calculate_shape_score(m1_fact)
        risk_flags.extend(shape_risks)
        
        # (C) 방향/일조 점수 계산
        orientation_score, orientation_detail, orientation_risks = self._calculate_orientation_score(m1_fact)
        risk_flags.extend(orientation_risks)
        
        # (D) 시세 적정성 점수 계산
        market_score, market_detail, market_risks = self._calculate_market_score(m1_fact)
        risk_flags.extend(market_risks)
        
        # (E) 기존 건물 리스크 점수 계산
        building_score, building_detail, building_risks = self._calculate_building_score(m1_fact)
        risk_flags.extend(building_risks)
        
        # 총점 계산
        total_score = max(0, min(100, 50 + road_score + shape_score + orientation_score + market_score + building_score))
        
        # 권고 결정
        recommendation = self._determine_recommendation(total_score, risk_flags)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(m1_fact, risk_flags)
        
        # 결과 구성
        breakdown = ScoreBreakdown(
            road=road_score,
            shape=shape_score,
            orientation=orientation_score,
            market=market_score,
            building=building_score,
            total=total_score,
            road_detail=road_detail,
            shape_detail=shape_detail,
            orientation_detail=orientation_detail,
            market_detail=market_detail,
            building_detail=building_detail
        )
        
        from datetime import datetime
        result = M2ScoringResult(
            total_score=total_score,
            risk_flags=risk_flags,
            score_breakdown=breakdown,
            recommendation=recommendation,
            confidence=confidence,
            m1_context_id=context_id,
            calculated_at=datetime.utcnow().isoformat()
        )
        
        self.logger.info(f"✅ M2 점수 계산 완료: {total_score}점 / 신뢰도 {confidence}%")
        self.logger.info(f"   도로: {road_score:+d} | 형상: {shape_score:+d} | 방향: {orientation_score:+d} | 시세: {market_score:+d} | 건물: {building_score:+d}")
        self.logger.info(f"   리스크 플래그: {len(risk_flags)}개")
        self.logger.info(f"   권고: {recommendation}")
        self.logger.info("=" * 80)
        
        return result
    
    def _calculate_road_score(self, m1: M1FactContract) -> tuple[int, str, List[RiskFlag]]:
        """(A) 도로 점수 계산"""
        score = 0
        risks = []
        details = []
        
        # 도로 폭
        if m1.road_width_m >= 8:
            score += 10
            details.append(f"도로 폭 {m1.road_width_m}m (8m 이상) → +10점")
        elif m1.road_width_m >= 6:
            score += 5
            risks.append(RiskFlag.ROAD_NARROW)
            details.append(f"도로 폭 {m1.road_width_m}m (6-8m) → +5점 (협소 주의)")
        else:
            score -= 20
            risks.append(RiskFlag.ROAD_FATAL)
            details.append(f"도로 폭 {m1.road_width_m}m (6m 미만) → -20점 (치명적)")
        
        # 소방차 진입
        if not m1.fire_truck_access:
            score -= 30
            risks.append(RiskFlag.FIRE_TRUCK_NO_ACCESS)
            details.append("소방차 진입 불가 → -30점")
        
        detail = " | ".join(details)
        return score, detail, risks
    
    def _calculate_shape_score(self, m1: M1FactContract) -> tuple[int, str, List[RiskFlag]]:
        """(B) 대지 형상 점수 계산"""
        score = 0
        risks = []
        details = []
        
        # 형상 유형 (순서 중요: 부정형 먼저 체크)
        shape_type = m1.site_shape_type.lower()
        if "부정형" in shape_type or "자루" in shape_type:
            score -= 10
            risks.append(RiskFlag.SHAPE_IRREGULAR)
            details.append(f"형상: {m1.site_shape_type} → -10점 (부정형)")
        elif "장방형" in shape_type:
            score += 5
            details.append(f"형상: {m1.site_shape_type} → +5점")
        elif "정형" in shape_type:
            score += 10
            details.append(f"형상: {m1.site_shape_type} → +10점")
        else:
            # 기타 형상은 0점
            details.append(f"형상: {m1.site_shape_type} → 0점")
        
        # 유효 건축 비율
        if m1.effective_build_ratio < 70:
            score -= 10
            risks.append(RiskFlag.SHAPE_LOW_EFFICIENCY)
            details.append(f"유효 건축비율 {m1.effective_build_ratio}% (70% 미만) → -10점")
        
        detail = " | ".join(details)
        return score, detail, risks
    
    def _calculate_orientation_score(self, m1: M1FactContract) -> tuple[int, str, List[RiskFlag]]:
        """(C) 방향/일조 점수 계산"""
        score = 0
        risks = []
        details = []
        
        # 주향
        direction = m1.main_direction.lower()
        if any(d in direction for d in ["남", "south"]):
            score += 5
            details.append(f"주향: {m1.main_direction} → +5점")
        
        # 일조권 리스크
        if "높음" in m1.sunlight_risk.lower():
            score -= 10
            risks.append(RiskFlag.SUNLIGHT_RISK)
            details.append(f"일조권 리스크 높음 → -10점")
        
        # 인접 고층 리스크
        if "높음" in m1.adjacent_height_risk.lower():
            score -= 10
            risks.append(RiskFlag.ADJACENT_HEIGHT_RISK)
            details.append(f"인접 고층 리스크 높음 → -10점")
        
        detail = " | ".join(details) if details else f"주향: {m1.main_direction}"
        return score, detail, risks
    
    def _calculate_market_score(self, m1: M1FactContract) -> tuple[int, str, List[RiskFlag]]:
        """(D) 시세 적정성 점수 계산"""
        score = 0
        risks = []
        details = []
        
        # price_gap_ratio가 있으면 사용
        if m1.price_gap_ratio is not None:
            if m1.price_gap_ratio <= 1.5:
                score += 10
                details.append(f"시세 갭 비율 {m1.price_gap_ratio:.2f} (≤1.5) → +10점")
            elif m1.price_gap_ratio <= 2.0:
                details.append(f"시세 갭 비율 {m1.price_gap_ratio:.2f} (1.5~2.0) → 0점")
            else:
                score -= 20
                risks.append(RiskFlag.PRICE_GAP_HIGH)
                details.append(f"시세 갭 비율 {m1.price_gap_ratio:.2f} (>2.0) → -20점")
        else:
            details.append("시세 비교 데이터 없음")
        
        detail = " | ".join(details)
        return score, detail, risks
    
    def _calculate_building_score(self, m1: M1FactContract) -> tuple[int, str, List[RiskFlag]]:
        """(E) 기존 건물 리스크 점수 계산"""
        score = 0
        risks = []
        details = []
        
        if m1.existing_building_exists:
            # 철거 필요
            if m1.demolition_required:
                score -= 10
                risks.append(RiskFlag.DEMOLITION_REQUIRED)
                details.append("철거 필요 → -10점")
            
            # 구조
            if m1.existing_building_structure and m1.existing_building_structure.upper() in ["RC", "SRC"]:
                score -= 5
                risks.append(RiskFlag.BUILDING_STRUCTURE_COMPLEX)
                details.append(f"구조 {m1.existing_building_structure} → -5점")
        
        detail = " | ".join(details) if details else "기존 건물 없음"
        return score, detail, risks
    
    def _determine_recommendation(self, total_score: int, risk_flags: List[RiskFlag]) -> str:
        """GO/NO-GO 권고 결정"""
        fatal_risks = [RiskFlag.ROAD_FATAL, RiskFlag.FIRE_TRUCK_NO_ACCESS]
        
        has_fatal = any(risk in risk_flags for risk in fatal_risks)
        
        if has_fatal:
            return "NO-GO (치명적 리스크)"
        elif total_score >= 70:
            return "GO (권장)"
        elif total_score >= 50:
            return "CONDITIONAL-GO (조건부 진행)"
        else:
            return "NO-GO (점수 미달)"
    
    def _calculate_confidence(self, m1: M1FactContract, risk_flags: List[RiskFlag]) -> int:
        """신뢰도 계산"""
        confidence = 70  # 기본값
        
        # 시세 데이터 있으면 +10
        if m1.price_gap_ratio is not None:
            confidence += 10
        
        # 거래가 정보 있으면 +10
        if m1.transaction_price is not None and m1.transaction_price > 0:
            confidence += 10
        
        # 리스크 많으면 -5 * 개수
        confidence -= len(risk_flags) * 5
        
        return max(0, min(100, confidence))


# ============================================================
# 전역 인스턴스
# ============================================================

scoring_engine = M2ScoringEngine()
