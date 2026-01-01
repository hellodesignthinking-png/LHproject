"""
v1.6.0: Download Limit Dependencies
PDF 다운로드 횟수 제한 체크
"""

from fastapi import HTTPException, Request
from typing import Optional
import functools

from app.models.access_log import get_access_log_storage


def check_download_limit(
    run_id: str,
    report_type: str,
    user_email: Optional[str] = None,
    share_token: Optional[str] = None,
    request: Optional[Request] = None
):
    """
    다운로드 제한 체크 및 증가
    
    Args:
        run_id: RUN_ID
        report_type: 보고서 타입
        user_email: 사용자 이메일 (인증된 경우)
        share_token: 공유 토큰 (비인증 경우)
        request: FastAPI Request 객체
    
    Raises:
        HTTPException: 다운로드 제한 초과 시
    """
    storage = get_access_log_storage()
    
    # Get current limit
    limit = storage.get_download_limit(
        run_id=run_id,
        report_type=report_type,
        user_email=user_email,
        share_token=share_token
    )
    
    # Check if exceeded
    if limit.is_exceeded():
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Download limit exceeded",
                "message": f"You have reached the maximum download limit ({limit.max_downloads}) for this report.",
                "run_id": run_id,
                "report_type": report_type,
                "download_count": limit.download_count,
                "max_downloads": limit.max_downloads
            }
        )
    
    # Increment download count
    storage.increment_download(
        run_id=run_id,
        report_type=report_type,
        user_email=user_email,
        share_token=share_token
    )
    
    # Log the action
    if request:
        # Access logging will be handled by middleware
        pass
    
    return limit


def require_download_limit_check(func):
    """
    PDF 다운로드 엔드포인트에 적용하는 데코레이터
    
    Usage:
        @require_download_limit_check
        async def download_pdf(...):
            ...
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract parameters
        context_id = kwargs.get("context_id")
        current_user = kwargs.get("current_user")
        request = kwargs.get("request")
        
        # Determine report type from function name or path
        report_type = _infer_report_type(func.__name__)
        
        # Extract user info
        user_email = current_user.email if current_user else None
        share_token = request.query_params.get("token") if request else None
        
        # Check download limit
        if context_id and report_type:
            check_download_limit(
                run_id=context_id,
                report_type=report_type,
                user_email=user_email,
                share_token=share_token,
                request=request
            )
        
        # Call original function
        return await func(*args, **kwargs)
    
    return wrapper


def _infer_report_type(func_name: str) -> str:
    """함수 이름에서 보고서 타입 추론"""
    mapping = {
        "master": "master",
        "landowner": "landowner",
        "lh_technical": "lh-technical",
        "market_analysis": "market-analysis",
        "lh_submission": "lh-submission",
        "investor": "investment"
    }
    
    for key, value in mapping.items():
        if key in func_name.lower():
            return value
    
    return "unknown"
