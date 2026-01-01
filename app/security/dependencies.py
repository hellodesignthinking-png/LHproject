"""
FastAPI Security Dependencies

목적:
- 사용자 인증 (Authentication)
- 권한 확인 (Authorization)
- 보고서 접근 제어

핵심:
"모든 엔드포인트에서 재사용 가능한 권한 체크"
"""

import logging
from typing import Optional, List
from fastapi import Depends, HTTPException, Header, status
from pydantic import BaseModel

from app.models.security import UserRole
from app.security.access_control import (
    check_role_access,
    check_full_access,
    is_admin_or_internal,
    log_access_attempt,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# Mock User (v1.2 단계에서는 간단한 Mock 사용)
# ==============================================================================

class CurrentUser(BaseModel):
    """현재 사용자 정보"""
    user_id: str
    email: str
    role: str
    allowed_run_ids: Optional[List[str]] = None  # None = unrestricted (ADMIN/INTERNAL)


# Mock 사용자 데이터 (실제 운영에서는 DB에서 조회)
MOCK_USERS = {
    "admin@zerosite.com": CurrentUser(
        user_id="admin-001",
        email="admin@zerosite.com",
        role="ADMIN",
        allowed_run_ids=None,  # 모든 RUN_ID 접근 가능
    ),
    "internal@zerosite.com": CurrentUser(
        user_id="internal-001",
        email="internal@zerosite.com",
        role="INTERNAL",
        allowed_run_ids=None,  # 모든 RUN_ID 접근 가능
    ),
    "landowner@example.com": CurrentUser(
        user_id="landowner-001",
        email="landowner@example.com",
        role="LANDOWNER",
        allowed_run_ids=["TEST_6REPORT", "RUN_20260101_001"],
    ),
    "lh@example.com": CurrentUser(
        user_id="lh-001",
        email="lh@example.com",
        role="LH",
        allowed_run_ids=["TEST_6REPORT"],
    ),
    "investor@example.com": CurrentUser(
        user_id="investor-001",
        email="investor@example.com",
        role="INVESTOR",
        allowed_run_ids=["TEST_6REPORT"],
    ),
}


# ==============================================================================
# Authentication
# ==============================================================================

async def get_current_user(
    x_user_email: Optional[str] = Header(None, description="사용자 이메일 (Mock 인증)")
) -> CurrentUser:
    """
    현재 사용자 정보 조회 (Mock 버전)
    
    v1.2에서는 Header로 이메일을 받아 Mock 사용자 반환
    실제 운영에서는 JWT 토큰 검증 + DB 조회
    
    Args:
        x_user_email: 요청 헤더에서 받은 사용자 이메일
    
    Returns:
        CurrentUser
    
    Raises:
        HTTPException 401: 인증 실패
    """
    if not x_user_email:
        logger.warning("❌ Authentication failed: missing X-User-Email header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide X-User-Email header.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Mock 사용자 조회
    user = MOCK_USERS.get(x_user_email)
    if not user:
        logger.warning(f"❌ Authentication failed: user not found: {x_user_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User not found: {x_user_email}",
        )
    
    logger.info(f"✅ User authenticated: {user.email} (role={user.role})")
    return user


# ==============================================================================
# Authorization: Report Access
# ==============================================================================

def require_report_access(report_type: str):
    """
    보고서 접근 권한 확인 (Role 기준)
    
    사용법:
        @router.get("/pdf")
        async def get_pdf(user=Depends(require_report_access("master"))):
            ...
    
    Args:
        report_type: 보고서 타입 (예: "master", "landowner")
    
    Returns:
        Dependency function
    """
    async def _check_access(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        # Role 기준 접근 권한 확인
        allowed, reason = check_role_access(user.role, report_type)
        
        if not allowed:
            logger.warning(
                f"❌ Access denied: user={user.email}, role={user.role}, report={report_type}, reason={reason}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {reason}",
            )
        
        logger.info(f"✅ Report access granted: user={user.email}, report={report_type}")
        return user
    
    return _check_access


# ==============================================================================
# Authorization: Full Access (Role + RUN_ID + Report)
# ==============================================================================

def require_full_access(report_type: str):
    """
    전체 접근 권한 확인 (Role + RUN_ID + Report Type)
    
    사용법:
        @router.get("/pdf")
        async def get_pdf(
            context_id: str,
            user=Depends(require_full_access("master"))
        ):
            ...
    
    Args:
        report_type: 보고서 타입
    
    Returns:
        Dependency function that checks full access
    """
    async def _check_full_access(
        context_id: str,
        user: CurrentUser = Depends(get_current_user)
    ) -> CurrentUser:
        # 전체 접근 권한 확인
        allowed, reason = check_full_access(
            user_id=user.user_id,
            user_role=user.role,
            run_id=context_id,
            report_type=report_type,
            allowed_run_ids=user.allowed_run_ids,
        )
        
        # 접근 로그 기록
        log_access_attempt(
            user_id=user.user_id,
            user_role=user.role,
            run_id=context_id,
            report_type=report_type,
            allowed=allowed,
            reason=reason,
        )
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {reason}",
            )
        
        return user
    
    return _check_full_access


# ==============================================================================
# Admin Only
# ==============================================================================

async def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    ADMIN 권한 확인
    
    사용법:
        @router.post("/admin/users")
        async def create_user(user=Depends(require_admin)):
            ...
    """
    if user.role != "ADMIN":
        logger.warning(f"❌ Admin access denied: user={user.email}, role={user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return user


# ==============================================================================
# Admin or Internal
# ==============================================================================

async def require_admin_or_internal(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    ADMIN 또는 INTERNAL 권한 확인
    """
    if not is_admin_or_internal(user.role):
        logger.warning(f"❌ Internal access denied: user={user.email}, role={user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Internal access required",
        )
    
    return user
