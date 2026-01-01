"""
외부 공유 토큰 모델

목적:
- 로그인 없이 특정 보고서 공유
- 토큰 기반 접근 제어
- 만료 시간 설정
- 접근 로그 기록

핵심 원칙:
"외부 공유는 편의가 아니라 '책임 있는 공개'다."
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import uuid


# ==============================================================================
# Pydantic Models
# ==============================================================================

class ShareTokenCreate(BaseModel):
    """공유 토큰 생성 요청"""
    run_id: str = Field(..., description="RUN_ID (예: TEST_6REPORT)")
    report_type: str = Field(..., description="보고서 타입 (A~F, 예: presentation)")
    expires_in_hours: int = Field(24, ge=1, le=168, description="만료 시간 (1~168시간, 기본 24h)")
    created_by_email: Optional[str] = Field(None, description="생성자 이메일 (선택)")


class ShareToken(BaseModel):
    """공유 토큰 응답"""
    token: str = Field(..., description="공유 토큰 UUID")
    run_id: str
    report_type: str
    expires_at: datetime
    is_active: bool = True
    created_at: datetime
    last_accessed_at: Optional[datetime] = None
    access_count: int = 0
    created_by_email: Optional[str] = None
    
    class Config:
        from_attributes = True


class ShareTokenResponse(BaseModel):
    """공유 링크 생성 응답"""
    share_url: str = Field(..., description="공유 링크 URL")
    token: str = Field(..., description="공유 토큰")
    expires_at: datetime = Field(..., description="만료 시각")
    expires_in_hours: int = Field(..., description="남은 시간 (시간)")


class ShareAccessLog(BaseModel):
    """공유 링크 접근 로그"""
    token: str
    accessed_at: datetime
    access_count: int
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


# ==============================================================================
# Token Generation
# ==============================================================================

def generate_share_token() -> str:
    """
    공유 토큰 생성
    
    Returns:
        UUID 형식의 토큰 문자열
    """
    return str(uuid.uuid4())


def calculate_expiry_time(hours: int) -> datetime:
    """
    만료 시간 계산
    
    Args:
        hours: 시간 (1~168)
    
    Returns:
        만료 시각 (UTC)
    """
    return datetime.utcnow() + timedelta(hours=hours)


# ==============================================================================
# In-Memory Storage (v1.3에서는 간단한 dict 사용)
# ==============================================================================

# 실제 운영에서는 DB 사용
SHARE_TOKENS_STORAGE = {}


class ShareTokenStorage:
    """공유 토큰 저장소 (In-Memory)"""
    
    @staticmethod
    def create_token(
        run_id: str,
        report_type: str,
        expires_in_hours: int,
        created_by_email: Optional[str] = None
    ) -> ShareToken:
        """
        공유 토큰 생성 및 저장
        
        Args:
            run_id: RUN_ID
            report_type: 보고서 타입
            expires_in_hours: 만료 시간 (시간)
            created_by_email: 생성자 이메일
        
        Returns:
            ShareToken
        """
        token = generate_share_token()
        expires_at = calculate_expiry_time(expires_in_hours)
        
        share_token = ShareToken(
            token=token,
            run_id=run_id,
            report_type=report_type,
            expires_at=expires_at,
            is_active=True,
            created_at=datetime.utcnow(),
            last_accessed_at=None,
            access_count=0,
            created_by_email=created_by_email,
        )
        
        SHARE_TOKENS_STORAGE[token] = share_token
        return share_token
    
    @staticmethod
    def get_token(token: str) -> Optional[ShareToken]:
        """
        토큰 조회
        
        Args:
            token: 토큰 UUID
        
        Returns:
            ShareToken or None
        """
        return SHARE_TOKENS_STORAGE.get(token)
    
    @staticmethod
    def update_access(token: str) -> bool:
        """
        접근 로그 업데이트
        
        Args:
            token: 토큰 UUID
        
        Returns:
            True if success, False if token not found
        """
        share_token = SHARE_TOKENS_STORAGE.get(token)
        if share_token:
            share_token.last_accessed_at = datetime.utcnow()
            share_token.access_count += 1
            return True
        return False
    
    @staticmethod
    def deactivate_token(token: str) -> bool:
        """
        토큰 비활성화
        
        Args:
            token: 토큰 UUID
        
        Returns:
            True if success, False if token not found
        """
        share_token = SHARE_TOKENS_STORAGE.get(token)
        if share_token:
            share_token.is_active = False
            return True
        return False
    
    @staticmethod
    def set_expiry(token: str, expires_at: datetime) -> bool:
        """
        토큰 만료 시각 설정 (테스트용)
        
        Args:
            token: 토큰 UUID
            expires_at: 새로운 만료 시각
        
        Returns:
            True if success, False if token not found
        """
        share_token = SHARE_TOKENS_STORAGE.get(token)
        if share_token:
            share_token.expires_at = expires_at
            return True
        return False
    
    @staticmethod
    def list_tokens(run_id: Optional[str] = None) -> list[ShareToken]:
        """
        토큰 목록 조회
        
        Args:
            run_id: RUN_ID (선택, None이면 모든 토큰)
        
        Returns:
            ShareToken 목록
        """
        if run_id:
            return [t for t in SHARE_TOKENS_STORAGE.values() if t.run_id == run_id]
        return list(SHARE_TOKENS_STORAGE.values())


# ==============================================================================
# Token Validation
# ==============================================================================

def is_token_valid(token: ShareToken) -> tuple[bool, Optional[str]]:
    """
    토큰 유효성 검증
    
    Args:
        token: ShareToken
    
    Returns:
        (valid: bool, reason: Optional[str])
    """
    # 1. 활성 상태 확인
    if not token.is_active:
        return False, "Token is inactive"
    
    # 2. 만료 시간 확인
    if token.expires_at < datetime.utcnow():
        return False, "Token expired"
    
    return True, None


def validate_token_scope(
    token: ShareToken,
    run_id: str,
    report_type: str
) -> tuple[bool, Optional[str]]:
    """
    토큰 범위(Scope) 검증
    
    Args:
        token: ShareToken
        run_id: 요청한 RUN_ID
        report_type: 요청한 보고서 타입
    
    Returns:
        (valid: bool, reason: Optional[str])
    """
    # RUN_ID 일치 확인
    if token.run_id != run_id:
        return False, f"Token is for RUN_ID '{token.run_id}', not '{run_id}'"
    
    # 보고서 타입 일치 확인
    if token.report_type != report_type:
        return False, f"Token is for report type '{token.report_type}', not '{report_type}'"
    
    return True, None
