"""
M2 Scoring API (M1 FACT 기반 재설계)
=====================================

핵심 원칙:
1. M1 FROZEN 상태 필수
2. M1 FACT만 사용 (Single Source of Truth)
3. score_breakdown 100% 설명 가능
4. M6까지 추적 가능

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 3.0
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import logging

from app.core.m1_state_machine import get_m1_state, M1Status
from app.core.m2_scoring_engine import (
    M1FactContract, M2ScoringResult, scoring_engine
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M2",
    tags=["M2 - Land Scoring (LH Standard)"]
)

# ============================================================
# In-Memory Storage
# ============================================================

m2_results: dict[str, M2ScoringResult] = {}

# ============================================================
# Request/Response Models
# ============================================================

class M2CalculateRequest(BaseModel):
    """M2 점수 계산 요청"""
    force_recalculate: bool = Field(default=False, description="강제 재계산 여부")

class M2CalculateResponse(BaseModel):
    """M2 점수 계산 응답"""
    status: str = Field(..., description="상태 (SUCCESS/BLOCKED)")
    message: str = Field(..., description="메시지")
    result: Optional[M2ScoringResult] = None
    errors: Optional[list[str]] = None

# ============================================================
# API Endpoints
# ============================================================

@router.post("/score", response_model=M2CalculateResponse)
async def calculate_m2_score(
    project_id: str,
    request: M2CalculateRequest
):
    """
    M2 점수 계산 실행 (LH Standard - M1 FACT 기반)
    
    실행 전제:
    - M1.status == FROZEN
    - M1.result_data 존재
    
    반환:
    - total_score (0-100)
    - risk_flags
    - score_breakdown (도로/형상/방향/시세/건물)
    - recommendation (GO/NO-GO)
    """
    logger.info(f"🚀 M2 SCORING START - Project: {project_id}")
    
    try:
        # ① M1 상태 조회
        m1_context = get_m1_state(project_id)
        
        if not m1_context:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "M1_NOT_FOUND",
                    "message": f"M1 상태를 찾을 수 없습니다: {project_id}",
                    "action": "POST /api/projects/{project_id}/modules/M1/auto-fetch를 먼저 실행하세요"
                }
            )
        
        # ② M1 FROZEN 확인 (차단 조건)
        if m1_context.status != M1Status.FROZEN:
            return M2CalculateResponse(
                status="BLOCKED",
                message=f"M1 FACT가 FROZEN 상태가 아닙니다 (현재: {m1_context.status.value})",
                errors=[
                    "M1 상태 ≠ FROZEN",
                    "POST /api/projects/{project_id}/modules/M1/freeze를 먼저 실행하세요"
                ]
            )
        
        logger.info(f"✅ M1 FROZEN 확인 완료")
        
        # ③ M1 result_data 확인
        if not m1_context.result_data:
            return M2CalculateResponse(
                status="BLOCKED",
                message="M1 FACT 데이터가 없습니다",
                errors=["M1 result_data is None"]
            )
        
        # ④ M1 FACT → M1FactContract 변환
        m1_fact_dict = m1_context.result_data.model_dump() if hasattr(m1_context.result_data, 'model_dump') else dict(m1_context.result_data)
        
        logger.info(f"📊 M1 FACT 로드 완료: {len(m1_fact_dict)} 필드")
        
        try:
            m1_fact = M1FactContract(**m1_fact_dict)
        except Exception as e:
            logger.error(f"❌ M1 FACT 변환 실패: {e}")
            return M2CalculateResponse(
                status="BLOCKED",
                message="M1 FACT 데이터 구조가 올바르지 않습니다",
                errors=[str(e)]
            )
        
        # ⑤ M2 점수 계산 (핵심 엔진 호출)
        # Use context_id from result_data if available, otherwise use project_id
        context_id = m1_context.result_data.context_id if m1_context.result_data and hasattr(m1_context.result_data, 'context_id') else project_id
        result = scoring_engine.calculate(m1_fact, context_id)
        
        # ⑥ 결과 저장
        m2_results[project_id] = result
        
        logger.info(f"✅ M2 점수 계산 완료: {result.total_score}점")
        logger.info(f"   권고: {result.recommendation}")
        logger.info(f"   리스크: {len(result.risk_flags)}개")
        
        return M2CalculateResponse(
            status="SUCCESS",
            message=f"M2 점수 계산 완료: {result.total_score}점",
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M2 계산 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "CALCULATION_FAILED",
                "message": str(e)
            }
        )


@router.get("/result", response_model=M2ScoringResult)
async def get_m2_result(project_id: str):
    """
    M2 점수 결과 조회
    
    Returns:
        M2ScoringResult: 저장된 점수 결과
    """
    if project_id not in m2_results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "RESULT_NOT_FOUND",
                "message": f"M2 점수 결과가 없습니다: {project_id}",
                "action": "POST /api/projects/{project_id}/modules/M2/calculate를 먼저 실행하세요"
            }
        )
    
    return m2_results[project_id]


@router.get("/status")
async def get_m2_status(project_id: str):
    """
    M2 상태 조회 (간단한 요약)
    
    Returns:
        dict: 상태 정보
    """
    m1_context = get_m1_state(project_id)
    
    if not m1_context:
        return {
            "project_id": project_id,
            "m2_ready": False,
            "reason": "M1 상태 없음"
        }
    
    is_frozen = m1_context.status == M1Status.FROZEN
    has_result = project_id in m2_results
    
    return {
        "project_id": project_id,
        "m1_status": m1_context.status.value,
        "m1_frozen": is_frozen,
        "m2_ready": is_frozen,
        "m2_calculated": has_result,
        "m2_score": m2_results[project_id].total_score if has_result else None
    }
