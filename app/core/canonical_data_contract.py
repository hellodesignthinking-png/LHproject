"""
ZeroSite M2-M6 Canonical Data Contract
모든 모듈이 반환하는 표준 데이터 구조 정의

Version: 2.0
Date: 2025-12-19
Author: ZeroSite Backend Team

핵심 원칙:
1. 모든 모듈은 summary + details 구조를 가진다
2. 프론트엔드 카드는 summary만 읽는다 (details 접근 금지)
3. PDF는 details를 사용하되, 표지/요약은 summary를 사용한다
4. 0/None 값 처리 규칙을 명확히 한다
"""

from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================================
# M2: 토지감정평가 (Land Appraisal)
# ============================================================================

class M2Summary(BaseModel):
    """M2 요약 데이터 (프론트 카드용)
    
    ✅ Optional 필드: 데이터가 없으면 None (0이 아님!)
    프론트엔드가 None을 'N/A (검증 필요)'로 표시
    """
    
    land_value_total_krw: Optional[int] = Field(
        None,  # ✅ Changed from ... to None
        description="총 토지가치 (원 단위, 정수)",
        example=1621848717
    )
    pyeong_price_krw: Optional[int] = Field(
        None,  # ✅ Changed from ... to None
        description="평당 가격 (원 단위, 정수)",
        example=10723014
    )
    confidence_pct: Optional[int] = Field(
        None,  # ✅ Changed from ... to None (can be None if data quality is poor)
        ge=0, 
        le=100,
        description="신뢰도 (0-100 정수 퍼센트)",
        example=85
    )
    transaction_count: Optional[int] = Field(
        None,  # ✅ Changed from ... to None
        ge=0,
        description="거래사례 건수",
        example=10
    )


class M2Result(BaseModel):
    """M2 완전한 결과"""
    
    module: Literal["M2"] = "M2"
    context_id: str
    summary: M2Summary
    details: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# M3: LH 선호유형 분석 (Housing Type Preference)
# ============================================================================

class M3Summary(BaseModel):
    """M3 요약 데이터 (프론트 카드용)
    
    ✅ Optional 필드: 데이터가 없으면 None (0이 아님!)
    프론트엔드가 None을 'N/A (검증 필요)'로 표시
    """
    
    recommended_type: Optional[str] = Field(
        None,  # ✅ Changed from ... to None
        description="추천 주택 유형 (한글)",
        example="청년형"
    )
    total_score: Optional[int] = Field(
        None,  # ✅ Changed from ... to None
        ge=0, 
        le=100,
        description="종합 점수 (0-100 정수)",
        example=85
    )
    confidence_pct: Optional[int] = Field(
        None,  # ✅ Changed from ... to None
        ge=0, 
        le=100,
        description="신뢰도 (0-100 정수 퍼센트)",
        example=85
    )
    second_choice: Optional[str] = Field(
        None,
        description="차선책 유형 (옵션)",
        example="신혼부부형"
    )


class M3Result(BaseModel):
    """M3 완전한 결과"""
    
    module: Literal["M3"] = "M3"
    context_id: str
    summary: M3Summary
    details: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# M4: 건축규모 결정 (Building Capacity)
# ============================================================================

class M4Summary(BaseModel):
    """M4 요약 데이터 (프론트 카드용)"""
    
    legal_units: int = Field(
        ..., 
        ge=0,
        description="법정 용적률 기준 세대수",
        example=20
    )
    incentive_units: int = Field(
        ..., 
        ge=0,
        description="인센티브 용적률 기준 세대수",
        example=26
    )
    parking_alt_a: Optional[int] = Field(
        None,
        description="주차 대안 A 대수 (기계식 등)",
        example=18
    )
    parking_alt_b: Optional[int] = Field(
        None,
        description="주차 대안 B 대수 (자주식 등)",
        example=20
    )


class M4Result(BaseModel):
    """M4 완전한 결과"""
    
    module: Literal["M4"] = "M4"
    context_id: str
    summary: M4Summary
    details: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# M5: 사업성 분석 (Feasibility Analysis)
# ============================================================================

class M5Summary(BaseModel):
    """M5 요약 데이터 (프론트 카드용)"""
    
    npv_public_krw: int = Field(
        ..., 
        description="NPV (공공임대 기준, 원 단위)",
        example=793000000
    )
    irr_pct: float = Field(
        ..., 
        ge=0,
        description="IRR (퍼센트, 소수점 1자리)",
        example=12.8
    )
    roi_pct: float = Field(
        ..., 
        ge=0,
        description="ROI (퍼센트, 소수점 1자리)",
        example=15.5
    )
    grade: str = Field(
        ...,
        description="사업성 등급 (A/B/C/D)",
        example="A"
    )


class M5Result(BaseModel):
    """M5 완전한 결과"""
    
    module: Literal["M5"] = "M5"
    context_id: str
    summary: M5Summary
    details: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# M6: LH 심사예측 (LH Review Prediction)
# ============================================================================

class M6Summary(BaseModel):
    """M6 요약 데이터 (프론트 카드용)
    
    중요: 이 필드들이 PDF의 모든 곳(표지/요약/본문)에서 동일하게 사용되어야 함
    """
    
    decision: Literal["GO", "NO-GO", "CONDITIONAL"] = Field(
        ...,
        description="최종 판정",
        example="GO"
    )
    total_score: float = Field(
        ..., 
        ge=0,
        description="총점 (소수점 1자리)",
        example=85.0
    )
    max_score: int = Field(
        default=110,
        description="만점 기준",
        example=110
    )
    grade: Literal["A", "B", "C", "D"] = Field(
        ...,
        description="등급",
        example="A"
    )
    approval_probability_pct: int = Field(
        ..., 
        ge=0, 
        le=100,
        description="승인 가능성 (0-100 정수 퍼센트)",
        example=77
    )


class M6Result(BaseModel):
    """M6 완전한 결과"""
    
    module: Literal["M6"] = "M6"
    context_id: str
    summary: M6Summary
    details: Dict[str, Any] = Field(default_factory=dict)
    meta: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 변환 헬퍼 함수 (기존 데이터 → 표준 포맷)
# ============================================================================

def convert_m2_to_standard(raw_data: Dict[str, Any], context_id: str) -> M2Result:
    """기존 M2 데이터를 표준 포맷으로 변환
    
    처리:
    - confidence.score → confidence_pct (0-1 → 0-100)
    - reliability.score → confidence_pct
    - trust_score → confidence_pct
    
    ✅ CRITICAL: 값이 없으면 None 유지 (0 fallback 금지!)
    """
    
    # 신뢰도 필드 찾기 (여러 가능한 키 시도)
    confidence_raw = (
        raw_data.get('confidence', {}).get('score') or
        raw_data.get('reliability', {}).get('score') or
        raw_data.get('trust_score') or
        raw_data.get('confidence_score')
    )
    
    # 0-1 범위면 100 곱하기, None이면 None 유지
    if confidence_raw is not None:
        if 0 <= confidence_raw <= 1:
            confidence_pct = int(confidence_raw * 100)
        else:
            confidence_pct = int(confidence_raw)
    else:
        confidence_pct = None
    
    # ✅ FIX: None을 유지, 0으로 변환하지 않음
    land_value = raw_data.get('appraisal', {}).get('land_value')
    pyeong_price = raw_data.get('appraisal', {}).get('unit_price_pyeong')
    trans_count = raw_data.get('transactions', {}).get('count')
    
    summary = M2Summary(
        land_value_total_krw=int(land_value) if land_value is not None else None,
        pyeong_price_krw=int(pyeong_price) if pyeong_price is not None else None,
        confidence_pct=confidence_pct,
        transaction_count=int(trans_count) if trans_count is not None else None
    )
    
    return M2Result(
        module="M2",
        context_id=context_id,
        summary=summary,
        details=raw_data,
        meta={
            "generated_at": datetime.now().isoformat(),
            "data_quality": {
                "is_mock": False,
                "warnings": []
            }
        }
    )


def convert_m3_to_standard(raw_data: Dict[str, Any], context_id: str) -> M3Result:
    """기존 M3 데이터를 표준 포맷으로 변환
    
    처리:
    - score → total_score (0-1 → 0-100)
    - recommendation_score → total_score
    
    ✅ CRITICAL FIX: details.selected에서 실제 데이터 추출
    """
    
    # 🔥 FIX: details 내부에서 실제 데이터 추출
    selected = raw_data.get('selected', {})
    scores = raw_data.get('scores', {})
    
    # recommended_type 추출 (selected.name 또는 selected.display_string)
    recommended_type = (
        selected.get('name') or 
        selected.get('display_string') or
        raw_data.get('recommended_type')
    )
    
    # total_score 추출 (선택된 타입의 점수)
    selected_type_key = selected.get('type', 'youth')  # 'youth', 'newlywed_1', etc.
    score_raw = None
    
    if selected_type_key and scores.get(selected_type_key):
        score_raw = scores[selected_type_key].get('total')
    
    if score_raw is None:
        score_raw = (
            raw_data.get('total_score') or
            raw_data.get('score') or
            raw_data.get('recommendation_score')
        )
    
    # 0-1 범위면 100 곱하기, None이면 None 유지
    if score_raw is not None:
        if 0 <= score_raw <= 1:
            total_score = int(score_raw * 100)
        else:
            total_score = int(score_raw)
    else:
        total_score = None
    
    # 신뢰도 (selected.confidence)
    confidence_raw = selected.get('confidence') or raw_data.get('confidence', {}).get('score')
    if confidence_raw is not None:
        if 0 <= confidence_raw <= 1:
            confidence_pct = int(confidence_raw * 100)
        else:
            confidence_pct = int(confidence_raw)
    else:
        confidence_pct = None
    
    # second_choice 추출 (두 번째로 높은 점수의 타입)
    second_choice = raw_data.get('second_choice')
    if not second_choice and scores:
        sorted_scores = sorted(
            [(k, v.get('total', 0), v.get('name', k)) for k, v in scores.items() if k != selected_type_key],
            key=lambda x: x[1],
            reverse=True
        )
        if sorted_scores:
            second_choice = sorted_scores[0][2]  # name of second place
    
    summary = M3Summary(
        recommended_type=recommended_type,
        total_score=total_score,
        confidence_pct=confidence_pct,
        second_choice=second_choice
    )
    
    return M3Result(
        module="M3",
        context_id=context_id,
        summary=summary,
        details=raw_data,
        meta={
            "generated_at": datetime.now().isoformat(),
            "data_quality": {
                "is_mock": False,
                "warnings": []
            }
        }
    )


def convert_m6_to_standard(raw_data: Dict[str, Any], context_id: str) -> M6Result:
    """기존 M6 데이터를 표준 포맷으로 변환
    
    중요: 단일 소스에서 total_score를 가져와 모든 곳에 사용
    
    처리:
    - 여러 total_score 키를 통합
    - approval_rate (0-1) → approval_probability_pct (0-100)
    
    ✅ CRITICAL FIX: details 내부에서 실제 데이터 추출
    """
    
    # 🔥 FIX: total_score 찾기 (우선순위: details.scores.total > top level)
    scores_dict = raw_data.get('scores', {})
    total_score = (
        scores_dict.get('total') or
        raw_data.get('total_score') or
        raw_data.get('m6_score') or
        0.0
    )
    
    # 🔥 FIX: approval_probability 처리 (details.approval.probability)
    approval_dict = raw_data.get('approval', {})
    approval_rate = (
        approval_dict.get('probability') or
        raw_data.get('approval_rate', 0) or 
        raw_data.get('approval_probability', 0)
    )
    if approval_rate is not None and 0 <= approval_rate <= 1:
        approval_probability_pct = int(approval_rate * 100)
    elif approval_rate is not None:
        approval_probability_pct = int(approval_rate)
    else:
        approval_probability_pct = 0
    
    # 🔥 FIX: grade 추출 (details.grade 우선, 없으면 계산)
    grade_from_details = raw_data.get('grade')
    if grade_from_details:
        grade = grade_from_details
    else:
        # grade 계산 (total_score 기반)
        if total_score >= 90:
            grade = "A"
        elif total_score >= 75:
            grade = "B"
        elif total_score >= 60:
            grade = "C"
        else:
            grade = "D"
    
    # 🔥 FIX: decision 추출 (details.decision.type)
    decision_dict = raw_data.get('decision', {})
    if isinstance(decision_dict, dict):
        decision = decision_dict.get('type', 'NO-GO')
    else:
        decision = decision_dict if decision_dict else 'NO-GO'
    
    summary = M6Summary(
        decision=decision,
        total_score=float(total_score),
        max_score=110,
        grade=grade,
        approval_probability_pct=approval_probability_pct
    )
    
    return M6Result(
        module="M6",
        context_id=context_id,
        summary=summary,
        details=raw_data,
        meta={
            "generated_at": datetime.now().isoformat(),
            "data_quality": {
                "is_mock": False,
                "warnings": []
            }
        }
    )


# ============================================================================
# 검증 함수
# ============================================================================

def validate_summary_consistency(module_result: Dict[str, Any]) -> bool:
    """요약과 상세 데이터 일관성 검증
    
    Returns:
        True if consistent, raises ValueError if not
    """
    
    module = module_result.get('module')
    summary = module_result.get('summary', {})
    details = module_result.get('details', {})
    
    if module == "M6":
        # M6의 경우 total_score가 모든 곳에서 동일해야 함
        summary_score = summary.get('total_score')
        details_score = details.get('total_score')
        
        if details_score and summary_score != details_score:
            raise ValueError(
                f"M6 total_score inconsistency: "
                f"summary={summary_score}, details={details_score}"
            )
    
    return True
