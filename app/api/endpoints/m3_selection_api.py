"""
M3 Supply Type Selection API
==============================

M2 점수 기반 공급유형 선택 API

Author: ZeroSite Decision OS Team
Date: 2026-01-12
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

from app.api.endpoints.m2_scoring_api import m2_results
from app.core.m3_selection_engine import (
    M2ScoreInput, M3SelectionResult, selection_engine
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/projects/{project_id}/modules/M3",
    tags=["M3 - Supply Type Selection"]
)

# ============================================================
# In-Memory Storage
# ============================================================

m3_results: dict[str, M3SelectionResult] = {}

# ============================================================
# Request/Response Models
# ============================================================

class M3SelectRequest(BaseModel):
    """M3 공급유형 선택 요청"""
    force_recalculate: bool = False

class M3SelectResponse(BaseModel):
    """M3 공급유형 선택 응답"""
    status: str
    message: str
    result: Optional[M3SelectionResult] = None
    errors: Optional[list[str]] = None

# ============================================================
# API Endpoints
# ============================================================

@router.post("/select", response_model=M3SelectResponse)
async def select_supply_type(
    project_id: str,
    request: M3SelectRequest
):
    """
    M3 공급유형 선택 실행
    
    실행 전제:
    - M2 점수 계산 완료
    
    반환:
    - recommended_type (YOUTH/NEWLYWED/SENIOR/GENERAL)
    - confidence (0~1)
    - reason_summary (설명)
    """
    logger.info(f"🚀 M3 SELECTION START - Project: {project_id}")
    
    try:
        # ① M2 결과 조회 (차단 조건)
        if project_id not in m2_results:
            return M3SelectResponse(
                status="BLOCKED",
                message="M2 점수 계산이 완료되지 않았습니다",
                errors=[
                    "M2 상태 ≠ COMPLETED",
                    "POST /api/projects/{project_id}/modules/M2/calculate를 먼저 실행하세요"
                ]
            )
        
        m2_result = m2_results[project_id]
        logger.info(f"✅ M2 결과 로드 완료: {m2_result.total_score}점")
        
        # ② M2 → M3 Data Contract 변환
        m2_input = M2ScoreInput(
            m2_total_score=m2_result.total_score,
            m2_risk_flags=[flag.value for flag in m2_result.risk_flags],
            m2_score_breakdown={
                "road": m2_result.score_breakdown.road,
                "shape": m2_result.score_breakdown.shape,
                "orientation": m2_result.score_breakdown.orientation,
                "market": m2_result.score_breakdown.market,
                "building": m2_result.score_breakdown.building
            },
            m2_recommendation=m2_result.recommendation
        )
        
        # ③ M3 공급유형 선택 (핵심 엔진 호출)
        result = selection_engine.select(m2_input)
        
        # ④ 결과 저장
        m3_results[project_id] = result
        
        logger.info(f"✅ M3 선택 완료: {result.recommended_type.value} ({result.confidence:.0%})")
        
        return M3SelectResponse(
            status="SUCCESS",
            message=f"공급유형 선택 완료: {result.recommended_type.value}",
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M3 선택 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "SELECTION_FAILED",
                "message": str(e)
            }
        )


@router.get("/result", response_model=M3SelectionResult)
async def get_m3_result(project_id: str):
    """M3 공급유형 선택 결과 조회"""
    if project_id not in m3_results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "RESULT_NOT_FOUND",
                "message": f"M3 결과가 없습니다: {project_id}",
                "action": "POST /api/projects/{project_id}/modules/M3/select를 먼저 실행하세요"
            }
        )
    
    return m3_results[project_id]


@router.get("/status")
async def get_m3_status(project_id: str):
    """M3 상태 조회"""
    m2_exists = project_id in m2_results
    m3_exists = project_id in m3_results
    
    return {
        "project_id": project_id,
        "m2_calculated": m2_exists,
        "m3_ready": m2_exists,
        "m3_selected": m3_exists,
        "recommended_type": m3_results[project_id].recommended_type.value if m3_exists else None
    }
