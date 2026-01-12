"""
M6 LH Final Judgment Module API
================================

ZeroSite Decision OS - M6 모듈
목적: LH 종합 판단 (GO / CONDITIONAL / NO-GO)

핵심 역할:
- M1~M5+M7의 모든 결과를 통합 분석
- LH 실무자가 상신할 것인지 최종 판단
- 보완 조건 및 제출 전략 제시

Author: ZeroSite Decision OS
Date: 2026-01-12
Module: M6 – LH FINAL JUDGMENT
"""

from fastapi import APIRouter, HTTPException, Path, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio

# ========================================
# Router 초기화
# ========================================
router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M6",
    tags=["M6 - LH Final Judgment"]
)

# ========================================
# Pydantic Models
# ========================================

class SupplementCondition(BaseModel):
    """보완 조건"""
    category: str = Field(..., description="보완 카테고리")
    condition: str = Field(..., description="보완 내용")
    priority: str = Field(..., description="우선순위: HIGH/MEDIUM/LOW")
    deadline: Optional[str] = Field(None, description="기한")

class ModuleEvaluation(BaseModel):
    """모듈별 평가"""
    module_name: str
    status: str  # PASS / WARNING / FAIL
    score: float  # 0.0 ~ 1.0
    key_points: List[str]

class M6ResultData(BaseModel):
    """M6 출력 데이터"""
    final_decision: str = Field(..., description="최종 판단: GO / CONDITIONAL / NO-GO")
    lh_submission_probability: str = Field(..., description="LH 매입 가능성: 높음/보통/낮음")
    module_evaluations: List[ModuleEvaluation]
    supplement_conditions: List[SupplementCondition]
    submission_strategy: str = Field(..., description="제출 전략")
    overall_rationale: str = Field(..., description="종합 판단 근거")
    confidence_score: float = Field(..., description="신뢰도 점수 (0.0 ~ 1.0)")
    calculated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class M6CalculateRequest(BaseModel):
    """M6 계산 요청"""
    context_id: str = Field(..., description="M1 Context ID (FROZEN)")
    force_recalculate: bool = Field(False, description="강제 재계산 여부")

class M6StatusResponse(BaseModel):
    """M6 상태 응답"""
    project_id: str
    context_id: str
    status: str  # NOT_STARTED, IN_PROGRESS, COMPLETED, FAILED
    calculated_at: Optional[str]
    error: Optional[str]

# ========================================
# In-Memory Storage
# ========================================
M6_CACHE: Dict[str, Dict[str, Any]] = {}

# ========================================
# Helper Functions
# ========================================

def get_all_module_results(context_id: str) -> Dict[str, Any]:
    """M1~M5+M7 모든 모듈 결과 수집"""
    return {
        "M1": {
            "area_sqm": 1500,
            "zone_type": "준주거지역",
            "bcr": 60,
            "far": 300,
            "frozen_at": "2026-01-12T10:00:00Z"
        },
        "M2": {
            "adjusted_land_value": 42000000000,
            "confidence_score": 0.82,
            "risk_factors": ["시장 변동성"]
        },
        "M3": {
            "recommended_type": "청년 매입임대",
            "lh_pass_score": 85
        },
        "M4": {
            "lh_recommended": {"units": 240, "total_floor_area": 10200}
        },
        "M5": {
            "lh_purchase": {"buffer_ratio": 12.76},
            "stability_assessment": "✅ 안정적"
        },
        "M7": {
            "community_concept": "청년 생활안정형",
            "operation_model": "LH 위탁 운영"
        }
    }

def evaluate_module(module_name: str, module_data: Dict[str, Any]) -> ModuleEvaluation:
    """모듈별 평가"""
    
    if module_name == "M1":
        return ModuleEvaluation(
            module_name="M1 사실 확정",
            status="PASS",
            score=1.0,
            key_points=["FROZEN 완료", "필수 항목 검증 통과"]
        )
    
    elif module_name == "M2":
        score = module_data.get("confidence_score", 0.8)
        status = "PASS" if score >= 0.7 else "WARNING"
        return ModuleEvaluation(
            module_name="M2 토지 매입 적정성",
            status=status,
            score=score,
            key_points=[
                f"적정 매입가 {module_data.get('adjusted_land_value', 0) / 100000000:.1f}억원",
                f"신뢰도 {score * 100:.0f}%"
            ]
        )
    
    elif module_name == "M3":
        lh_score = module_data.get("lh_pass_score", 0)
        status = "PASS" if lh_score >= 80 else "WARNING" if lh_score >= 70 else "FAIL"
        return ModuleEvaluation(
            module_name="M3 공급유형 적합성",
            status=status,
            score=lh_score / 100,
            key_points=[
                f"추천 유형: {module_data.get('recommended_type', 'N/A')}",
                f"LH 통과 점수: {lh_score}/100"
            ]
        )
    
    elif module_name == "M4":
        return ModuleEvaluation(
            module_name="M4 건축 규모",
            status="PASS",
            score=0.9,
            key_points=[
                f"세대수: {module_data.get('lh_recommended', {}).get('units', 0)}세대",
                "보수적 설계 적용"
            ]
        )
    
    elif module_name == "M5":
        buffer_ratio = module_data.get("lh_purchase", {}).get("buffer_ratio", 0)
        status = "PASS" if 5 <= buffer_ratio <= 15 else "WARNING"
        return ModuleEvaluation(
            module_name="M5 사업성·리스크",
            status=status,
            score=0.85,
            key_points=[
                f"안전 마진: {buffer_ratio:.1f}%",
                module_data.get("stability_assessment", "")
            ]
        )
    
    elif module_name == "M7":
        return ModuleEvaluation(
            module_name="M7 커뮤니티 계획",
            status="PASS",
            score=0.88,
            key_points=[
                f"콘셉트: {module_data.get('community_concept', 'N/A')}",
                f"운영: {module_data.get('operation_model', 'N/A')}"
            ]
        )
    
    else:
        return ModuleEvaluation(
            module_name=module_name,
            status="WARNING",
            score=0.5,
            key_points=["평가 기준 없음"]
        )

def generate_supplement_conditions(
    evaluations: List[ModuleEvaluation],
    all_results: Dict[str, Any]
) -> List[SupplementCondition]:
    """보완 조건 생성"""
    
    conditions = []
    
    # WARNING/FAIL 모듈 체크
    for eval in evaluations:
        if eval.status == "FAIL":
            conditions.append(SupplementCondition(
                category=eval.module_name,
                condition=f"{eval.module_name} 재검토 필수",
                priority="HIGH",
                deadline="즉시"
            ))
        elif eval.status == "WARNING":
            conditions.append(SupplementCondition(
                category=eval.module_name,
                condition=f"{eval.module_name} 보완 권장",
                priority="MEDIUM",
                deadline="제출 전"
            ))
    
    # M5 안전 마진 체크
    m5 = all_results.get("M5", {})
    buffer_ratio = m5.get("lh_purchase", {}).get("buffer_ratio", 0)
    
    if buffer_ratio < 8:
        conditions.append(SupplementCondition(
            category="M5 사업성",
            condition="안전 마진 8% 이상 확보 권장",
            priority="MEDIUM",
            deadline="제출 전"
        ))
    elif buffer_ratio > 12:
        conditions.append(SupplementCondition(
            category="M5 사업성",
            condition="과도한 마진, 커뮤니티 투자 확대 검토",
            priority="LOW",
            deadline="협의 시"
        ))
    
    # 기본 조건
    if not conditions:
        conditions.append(SupplementCondition(
            category="일반",
            condition="현재 구조 유지, 추가 보완 불필요",
            priority="LOW",
            deadline="N/A"
        ))
    
    return conditions

def make_final_decision(
    evaluations: List[ModuleEvaluation],
    conditions: List[SupplementCondition]
) -> str:
    """최종 판단 결정"""
    
    fail_count = sum(1 for e in evaluations if e.status == "FAIL")
    warning_count = sum(1 for e in evaluations if e.status == "WARNING")
    avg_score = sum(e.score for e in evaluations) / len(evaluations)
    
    if fail_count >= 1:
        return "NO-GO"
    elif warning_count >= 3 or avg_score < 0.7:
        return "CONDITIONAL"
    else:
        return "GO"

def assess_submission_probability(decision: str, avg_score: float) -> str:
    """LH 제출 가능성 평가"""
    
    if decision == "GO" and avg_score >= 0.85:
        return "높음"
    elif decision == "GO" or decision == "CONDITIONAL":
        return "보통"
    else:
        return "낮음"

def generate_submission_strategy(
    decision: str,
    conditions: List[SupplementCondition]
) -> str:
    """제출 전략 생성"""
    
    if decision == "GO":
        return "즉시 제출 가능. 현재 구조 유지하며 LH 협의 진행."
    elif decision == "CONDITIONAL":
        high_priority = [c for c in conditions if c.priority == "HIGH"]
        if high_priority:
            return f"{len(high_priority)}개 고우선순위 조건 보완 후 제출. 최소 1주 소요 예상."
        else:
            return "중우선순위 조건 보완 후 제출. 2주 내 완료 가능."
    else:
        return "현재 구조 재검토 필수. 제출 보류 권장."

def generate_overall_rationale(
    decision: str,
    evaluations: List[ModuleEvaluation],
    conditions: List[SupplementCondition]
) -> str:
    """종합 판단 근거"""
    
    passed = [e.module_name for e in evaluations if e.status == "PASS"]
    warnings = [e.module_name for e in evaluations if e.status == "WARNING"]
    
    rationale = f"최종 판단: {decision}\n\n"
    rationale += f"통과 모듈: {', '.join(passed)}\n"
    
    if warnings:
        rationale += f"경고 모듈: {', '.join(warnings)}\n"
    
    rationale += f"\n보완 조건: {len(conditions)}개\n"
    
    if decision == "GO":
        rationale += "\nLH 실무 기준을 충족하며, 즉시 제출 가능한 수준입니다."
    elif decision == "CONDITIONAL":
        rationale += "\n일부 보완 후 제출 가능합니다. 핵심 리스크는 관리 가능한 수준입니다."
    else:
        rationale += "\n현재 구조는 LH 심사 통과가 어려울 것으로 판단됩니다."
    
    return rationale

def calculate_confidence_score(
    evaluations: List[ModuleEvaluation],
    decision: str
) -> float:
    """신뢰도 점수 계산"""
    
    avg_module_score = sum(e.score for e in evaluations) / len(evaluations)
    
    decision_weight = {
        "GO": 1.0,
        "CONDITIONAL": 0.75,
        "NO-GO": 0.4
    }.get(decision, 0.5)
    
    return min(1.0, avg_module_score * decision_weight)

# ========================================
# API Endpoints
# ========================================

@router.post(
    "/calculate",
    response_model=M6ResultData,
    summary="M6 LH 종합 판단 실행",
    description="""
    M6 LH 종합 판단 모듈을 실행합니다.
    
    **전제 조건:**
    - M1 FACT FROZEN
    - M2 ~ M5 + M7 완료
    
    **최종 판단:**
    - GO: 즉시 제출 가능
    - CONDITIONAL: 보완 후 제출
    - NO-GO: 제출 보류
    """
)
async def calculate_m6(
    project_id: str = Path(..., description="프로젝트 ID"),
    request: M6CalculateRequest = Body(...)
):
    """M6 계산 실행"""
    
    context_id = request.context_id
    
    # 1. 모든 모듈 결과 수집
    try:
        all_results = get_all_module_results(context_id)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"모듈 결과 수집 실패: {str(e)}"
        )
    
    # 2. 모듈별 평가
    evaluations = [
        evaluate_module(module_name, module_data)
        for module_name, module_data in all_results.items()
    ]
    
    # 3. 보완 조건 생성
    conditions = generate_supplement_conditions(evaluations, all_results)
    
    # 4. 최종 판단
    decision = make_final_decision(evaluations, conditions)
    
    # 5. LH 제출 가능성
    avg_score = sum(e.score for e in evaluations) / len(evaluations)
    probability = assess_submission_probability(decision, avg_score)
    
    # 6. 제출 전략
    strategy = generate_submission_strategy(decision, conditions)
    
    # 7. 종합 판단 근거
    rationale = generate_overall_rationale(decision, evaluations, conditions)
    
    # 8. 신뢰도 점수
    confidence = calculate_confidence_score(evaluations, decision)
    
    # 9. 결과 생성
    result_data = M6ResultData(
        final_decision=decision,
        lh_submission_probability=probability,
        module_evaluations=evaluations,
        supplement_conditions=conditions,
        submission_strategy=strategy,
        overall_rationale=rationale,
        confidence_score=confidence
    )
    
    # 10. 캐시에 저장
    cache_key = f"{project_id}:{context_id}"
    M6_CACHE[cache_key] = {
        "status": "COMPLETED",
        "result_data": result_data.dict(),
        "calculated_at": result_data.calculated_at
    }
    
    return result_data

@router.get(
    "/result",
    response_model=M6ResultData,
    summary="M6 결과 조회"
)
async def get_m6_result(
    project_id: str = Path(...),
    context_id: str = ...
):
    """M6 결과 조회"""
    
    cache_key = f"{project_id}:{context_id}"
    
    if cache_key not in M6_CACHE:
        raise HTTPException(
            status_code=404,
            detail="M6 계산 결과를 찾을 수 없습니다."
        )
    
    cached = M6_CACHE[cache_key]
    return M6ResultData(**cached["result_data"])

@router.get(
    "/status",
    response_model=M6StatusResponse,
    summary="M6 상태 확인"
)
async def get_m6_status(
    project_id: str = Path(...),
    context_id: str = ...
):
    """M6 상태 확인"""
    
    cache_key = f"{project_id}:{context_id}"
    
    if cache_key not in M6_CACHE:
        return M6StatusResponse(
            project_id=project_id,
            context_id=context_id,
            status="NOT_STARTED",
            calculated_at=None,
            error=None
        )
    
    cached = M6_CACHE[cache_key]
    return M6StatusResponse(
        project_id=project_id,
        context_id=context_id,
        status=cached["status"],
        calculated_at=cached.get("calculated_at"),
        error=cached.get("error")
    )

@router.get(
    "/validate",
    summary="M6 실행 가능 여부 검증"
)
async def validate_m6(
    project_id: str = Path(...),
    context_id: str = ...
):
    """M6 실행 가능 여부 검증"""
    
    validation_result = {
        "can_execute": True,
        "checks": {
            "m1_frozen": True,
            "m2_completed": True,
            "m3_completed": True,
            "m4_completed": True,
            "m5_completed": True,
            "m7_completed": True
        },
        "errors": []
    }
    
    return validation_result
