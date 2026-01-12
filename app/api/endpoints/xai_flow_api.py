"""
XAI Score Flow API
===================

M1~M6 점수 흐름 시각화 API

Author: ZeroSite Decision OS Team
Date: 2026-01-12
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.api.endpoints.m2_scoring_api import m2_results
from app.api.endpoints.m3_selection_api import m3_results
from app.core.xai_score_flow import flow_generator, SankeyDiagram
from app.core.m1_state_machine import get_m1_state

router = APIRouter(
    prefix="/api/projects/{project_id}/xai",
    tags=["XAI - Explainable AI"]
)

@router.get("/score-flow", response_model=SankeyDiagram)
async def get_score_flow(project_id: str):
    """
    M1~M6 점수 흐름 조회 (Sankey Diagram용)
    
    Returns:
        SankeyDiagram: 전체 점수 흐름 데이터
    """
    # M1 FACT 조회
    m1_context = get_m1_state(project_id)
    if not m1_context or not m1_context.result_data:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "M1_NOT_FOUND",
                "message": "M1 FACT가 없습니다"
            }
        )
    
    m1_fact_dict = m1_context.result_data.model_dump() if hasattr(m1_context.result_data, 'model_dump') else dict(m1_context.result_data)
    
    # M2 점수 조회
    if project_id not in m2_results:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "M2_NOT_FOUND",
                "message": "M2 점수가 없습니다"
            }
        )
    
    m2_score = m2_results[project_id]
    m2_dict = {
        "total_score": m2_score.total_score,
        "score_breakdown": {
            "road": m2_score.score_breakdown.road,
            "shape": m2_score.score_breakdown.shape,
            "orientation": m2_score.score_breakdown.orientation,
            "market": m2_score.score_breakdown.market,
            "building": m2_score.score_breakdown.building,
            "road_detail": m2_score.score_breakdown.road_detail,
            "shape_detail": m2_score.score_breakdown.shape_detail,
            "orientation_detail": m2_score.score_breakdown.orientation_detail,
            "market_detail": m2_score.score_breakdown.market_detail,
            "building_detail": m2_score.score_breakdown.building_detail
        },
        "recommendation": m2_score.recommendation
    }
    
    # M3 선택 조회 (optional)
    m3_dict = None
    if project_id in m3_results:
        m3_result = m3_results[project_id]
        m3_dict = {
            "recommended_type": m3_result.recommended_type.value,
            "confidence": m3_result.confidence,
            "alternative_types": [t.value for t in m3_result.alternative_types]
        }
    
    # M6 최종 판단 (미래 - 현재는 M2 권고 사용)
    m6_dict = {
        "decision": m2_score.recommendation.split()[0]  # "GO (권장)" -> "GO"
    }
    
    # 흐름 생성
    diagram = flow_generator.generate(
        m1_fact=m1_fact_dict,
        m2_score=m2_dict,
        m3_selection=m3_dict,
        m6_decision=m6_dict
    )
    
    return diagram
