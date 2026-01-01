"""
v1.6.0: Access Log Dashboard Router
접근 로그 조회 및 통계 API
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.models.access_log import (
    AccessLog,
    AccessAction,
    DownloadLimit,
    IPWhitelist,
    get_access_log_storage
)
from app.models.security import UserRole
from app.security.dependencies import CurrentUser, get_current_user


router = APIRouter(prefix="/api/v4/access-logs", tags=["Access Logs v1.6"])


# ========== Response Models ==========

class AccessLogResponse(BaseModel):
    """접근 로그 응답"""
    logs: List[AccessLog]
    total_count: int
    page: int
    page_size: int


class AccessLogStatistics(BaseModel):
    """접근 로그 통계"""
    total_accesses: int
    by_action: dict
    by_report_type: dict
    unique_users: int
    unique_ips: int
    failed_requests: int
    period: str


class DownloadLimitResponse(BaseModel):
    """다운로드 제한 응답"""
    limit: DownloadLimit
    remaining: int
    is_exceeded: bool


class IPWhitelistResponse(BaseModel):
    """IP 화이트리스트 응답"""
    whitelist: List[IPWhitelist]
    total_count: int


# ========== API Endpoints ==========

@router.get("/logs", response_model=AccessLogResponse)
async def get_access_logs(
    run_id: Optional[str] = Query(None, description="RUN_ID로 필터링"),
    user_email: Optional[str] = Query(None, description="사용자 이메일로 필터링"),
    action: Optional[AccessAction] = Query(None, description="액션 타입으로 필터링"),
    hours: int = Query(24, description="최근 N시간 로그 조회", ge=1, le=168),
    page: int = Query(1, description="페이지 번호", ge=1),
    page_size: int = Query(50, description="페이지 크기", ge=1, le=500),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    접근 로그 조회
    
    - ADMIN만 접근 가능
    - 시간 범위, RUN_ID, 사용자, 액션 타입으로 필터링 가능
    """
    # 🔐 ADMIN만 접근 가능
    if UserRole(current_user.role) != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Access logs are only accessible to ADMIN users"
        )
    
    storage = get_access_log_storage()
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    # Get logs
    logs = storage.get_logs(
        run_id=run_id,
        user_email=user_email,
        action=action,
        start_time=start_time,
        end_time=end_time,
        limit=page_size * page
    )
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_logs = logs[start_idx:end_idx]
    
    return AccessLogResponse(
        logs=paginated_logs,
        total_count=len(logs),
        page=page,
        page_size=page_size
    )


@router.get("/statistics", response_model=AccessLogStatistics)
async def get_access_statistics(
    run_id: Optional[str] = Query(None, description="RUN_ID로 필터링"),
    hours: int = Query(24, description="최근 N시간 통계", ge=1, le=168),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    접근 로그 통계
    
    - ADMIN만 접근 가능
    - 액션별, 보고서별 집계
    - 고유 사용자/IP 수
    """
    # 🔐 ADMIN만 접근 가능
    if UserRole(current_user.role) != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Access statistics are only accessible to ADMIN users"
        )
    
    storage = get_access_log_storage()
    stats = storage.get_log_statistics(run_id=run_id)
    
    return AccessLogStatistics(
        total_accesses=stats["total_accesses"],
        by_action=stats["by_action"],
        by_report_type=stats["by_report_type"],
        unique_users=stats["unique_users"],
        unique_ips=stats["unique_ips"],
        failed_requests=stats["failed_requests"],
        period=f"Last {hours} hours"
    )


@router.get("/download-limit", response_model=DownloadLimitResponse)
async def check_download_limit(
    run_id: str = Query(..., description="RUN_ID"),
    report_type: str = Query(..., description="보고서 타입"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    다운로드 제한 확인
    
    - 인증된 사용자: 본인의 다운로드 제한만 조회 가능
    - ADMIN: 모든 다운로드 제한 조회 가능
    """
    storage = get_access_log_storage()
    
    limit = storage.get_download_limit(
        run_id=run_id,
        report_type=report_type,
        user_email=current_user.email
    )
    
    return DownloadLimitResponse(
        limit=limit,
        remaining=max(0, limit.max_downloads - limit.download_count),
        is_exceeded=limit.is_exceeded()
    )


@router.get("/whitelist", response_model=IPWhitelistResponse)
async def get_ip_whitelist(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    IP 화이트리스트 조회
    
    - ADMIN만 접근 가능
    """
    # 🔐 ADMIN만 접근 가능
    if UserRole(current_user.role) != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="IP whitelist is only accessible to ADMIN users"
        )
    
    storage = get_access_log_storage()
    whitelist = storage.get_whitelist()
    
    return IPWhitelistResponse(
        whitelist=whitelist,
        total_count=len(whitelist)
    )


@router.post("/whitelist/add")
async def add_ip_to_whitelist(
    ip_address: str = Query(..., description="IP 주소 또는 CIDR"),
    description: str = Query(..., description="IP 설명"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    IP 화이트리스트에 추가
    
    - ADMIN만 접근 가능
    """
    # 🔐 ADMIN만 접근 가능
    if UserRole(current_user.role) != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN users can modify IP whitelist"
        )
    
    storage = get_access_log_storage()
    
    import uuid
    whitelist = IPWhitelist(
        whitelist_id=str(uuid.uuid4()),
        ip_address=ip_address,
        description=description,
        created_by=current_user.email
    )
    
    storage.add_to_whitelist(whitelist)
    
    return {
        "success": True,
        "message": f"IP {ip_address} added to whitelist",
        "whitelist": whitelist
    }


@router.delete("/whitelist/{whitelist_id}")
async def remove_ip_from_whitelist(
    whitelist_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    IP 화이트리스트에서 제거
    
    - ADMIN만 접근 가능
    """
    # 🔐 ADMIN만 접근 가능
    if UserRole(current_user.role) != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN users can modify IP whitelist"
        )
    
    storage = get_access_log_storage()
    storage.remove_from_whitelist(whitelist_id)
    
    return {
        "success": True,
        "message": f"IP whitelist entry {whitelist_id} removed"
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(20, description="최근 활동 개수", ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    최근 활동 조회 (간단 버전)
    
    - 인증된 사용자: 본인의 활동만 조회
    - ADMIN: 모든 활동 조회
    """
    storage = get_access_log_storage()
    
    # ADMIN은 모든 로그, 일반 사용자는 본인 로그만
    if UserRole(current_user.role) == UserRole.ADMIN:
        logs = storage.get_logs(limit=limit)
    else:
        logs = storage.get_logs(user_email=current_user.email, limit=limit)
    
    return {
        "recent_activity": [
            {
                "timestamp": log.timestamp.isoformat(),
                "action": log.action.value,
                "report_type": log.report_type,
                "run_id": log.run_id,
                "success": log.success
            }
            for log in logs
        ]
    }
