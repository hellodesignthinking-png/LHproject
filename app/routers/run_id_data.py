"""
v1.6.0: RUN_ID Data API Router
실제 RUN_ID 조회 및 검색 API
"""

from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from pydantic import BaseModel

from app.services.run_id_data import (
    RunIdInfo,
    get_run_id_service
)
from app.security.dependencies import CurrentUser, get_current_user


router = APIRouter(prefix="/api/v4/run-ids", tags=["RUN_ID Data v1.6"])


# ========== Response Models ==========

class RunIdListResponse(BaseModel):
    """RUN_ID 목록 응답"""
    run_ids: List[RunIdInfo]
    total_count: int
    page: int
    page_size: int


class RunIdStatisticsResponse(BaseModel):
    """RUN_ID 통계 응답"""
    total_count: int
    active_count: int
    by_status: dict
    by_region: dict
    recent: List[str]


# ========== API Endpoints ==========

@router.get("/list", response_model=RunIdListResponse)
async def get_run_id_list(
    status: Optional[str] = Query(None, description="상태 필터"),
    page: int = Query(1, description="페이지 번호", ge=1),
    page_size: int = Query(20, description="페이지 크기", ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    RUN_ID 목록 조회
    
    - 인증된 사용자만 접근 가능
    - 페이지네이션 지원
    - 상태 필터링 가능
    """
    service = get_run_id_service()
    
    # Get all matching RUN_IDs
    all_run_ids = service.get_all_run_ids(
        status=status,
        limit=page_size * page
    )
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated = all_run_ids[start_idx:end_idx]
    
    return RunIdListResponse(
        run_ids=paginated,
        total_count=len(all_run_ids),
        page=page,
        page_size=page_size
    )


@router.get("/search", response_model=RunIdListResponse)
async def search_run_ids(
    q: str = Query(..., description="검색어 (RUN_ID, 주소, PNU)"),
    limit: int = Query(20, description="최대 결과 개수", ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    RUN_ID 검색
    
    - RUN_ID, 주소, PNU로 검색
    - 부분 매칭 지원
    - 인증된 사용자만 접근 가능
    """
    service = get_run_id_service()
    results = service.search_run_ids(query=q, limit=limit)
    
    return RunIdListResponse(
        run_ids=results,
        total_count=len(results),
        page=1,
        page_size=limit
    )


@router.get("/statistics", response_model=RunIdStatisticsResponse)
async def get_run_id_statistics(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    RUN_ID 통계 조회
    
    - 총 개수, 상태별 분포
    - 지역별 분포
    - 최근 생성된 RUN_ID
    - 인증된 사용자만 접근 가능
    """
    service = get_run_id_service()
    stats = service.get_run_id_statistics()
    
    return RunIdStatisticsResponse(**stats)


@router.get("/{run_id}", response_model=RunIdInfo)
async def get_run_id_info(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    특정 RUN_ID 정보 조회
    
    - RUN_ID로 상세 정보 조회
    - 인증된 사용자만 접근 가능
    """
    service = get_run_id_service()
    info = service.get_run_id_info(run_id)
    
    if not info:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"RUN_ID '{run_id}' not found"
        )
    
    return info
