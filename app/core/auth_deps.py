"""
ZeroSite v4.0 Authentication Dependencies
==========================================

FastAPI 인증 의존성 함수들

Author: ZeroSite Security Team
Date: 2025-12-27
Version: 1.0
"""

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.core.security import (
    verify_token,
    get_current_user_from_token,
    verify_api_key_access,
    User,
    TokenData
)


# OAuth2 스키마
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "read": "Read access",
        "write": "Write access",
        "admin": "Admin access"
    }
)

# HTTP Bearer 스키마 (API Key용)
security = HTTPBearer()


# ==================== Dependencies ====================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    현재 사용자 가져오기 (JWT 토큰)
    
    Args:
        token: JWT 토큰
        
    Returns:
        User 객체
        
    Raises:
        HTTPException: 인증 실패 시
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user = get_current_user_from_token(token)
    
    if user is None:
        raise credentials_exception
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    활성 사용자 확인
    
    Args:
        current_user: 현재 사용자
        
    Returns:
        User 객체
        
    Raises:
        HTTPException: 비활성 사용자인 경우
    """
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    관리자 권한 확인
    
    Args:
        current_user: 현재 사용자
        
    Returns:
        User 객체
        
    Raises:
        HTTPException: 관리자 권한이 없는 경우
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """
    API 키 검증
    
    Args:
        credentials: HTTP Authorization 헤더
        
    Returns:
        User 객체
        
    Raises:
        HTTPException: API 키가 유효하지 않은 경우
    """
    api_key = credentials.credentials
    
    key_data = verify_api_key_access(api_key)
    
    if not key_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # API 키로 사용자 조회
    from app.core.security import get_user, fake_users_db
    
    # user_id로 사용자 찾기
    user = None
    for username, user_data in fake_users_db.items():
        if user_data.user_id == key_data.user_id:
            user = User(**user_data.dict())
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for API key"
        )
    
    return user


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    선택적 인증 (토큰이 있으면 사용자 반환, 없으면 None)
    
    Args:
        token: JWT 토큰 (선택)
        
    Returns:
        User 또는 None
    """
    if not token:
        return None
    
    try:
        user = await get_current_user(token)
        return user
    except HTTPException:
        return None
