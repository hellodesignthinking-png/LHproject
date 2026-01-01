"""
보안 및 권한 관리 모델

목적:
- Role 기반 접근 제어 (RBAC)
- RUN_ID 단위 접근 제한
- 보고서 타입별 접근 제한

핵심 원칙:
"권한은 UX가 아니라 신뢰의 최소 단위다."
"""

from sqlalchemy import Column, String, ARRAY, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum
import uuid


# ==============================================================================
# Enums
# ==============================================================================

class UserRole(str, Enum):
    """사용자 역할"""
    ADMIN = "ADMIN"
    INTERNAL = "INTERNAL"
    LANDOWNER = "LANDOWNER"
    LH = "LH"
    INVESTOR = "INVESTOR"


class ReportType(str, Enum):
    """보고서 타입"""
    MASTER = "master"                  # A: 종합 최종 보고서 60p
    LANDOWNER = "landowner"            # B: 토지주 제출용 보고서
    LH_TECHNICAL = "lh-technical"      # C: LH 기술검증 보고서
    INVESTMENT = "investment"          # D: 사업성·투자 검토 보고서
    QUICK_REVIEW = "quick-review"      # E: 사전 검토 리포트
    PRESENTATION = "presentation"      # F: 설명용 프레젠테이션


# ==============================================================================
# Pydantic Models
# ==============================================================================

class UserBase(BaseModel):
    """사용자 기본 모델"""
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    """사용자 생성 모델"""
    password: str


class User(UserBase):
    """사용자 응답 모델"""
    id: uuid.UUID
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class RunIdAclBase(BaseModel):
    """RUN_ID 접근 제어 기본 모델"""
    run_id: str
    user_id: uuid.UUID
    allowed_reports: List[str]


class RunIdAclCreate(RunIdAclBase):
    """RUN_ID 접근 제어 생성 모델"""
    pass


class RunIdAcl(RunIdAclBase):
    """RUN_ID 접근 제어 응답 모델"""
    id: uuid.UUID
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """JWT 토큰 데이터"""
    user_id: Optional[uuid.UUID] = None
    email: Optional[str] = None
    role: Optional[str] = None


class AccessCheckRequest(BaseModel):
    """접근 권한 체크 요청"""
    user_id: uuid.UUID
    run_id: str
    report_type: str


class AccessCheckResponse(BaseModel):
    """접근 권한 체크 응답"""
    allowed: bool
    reason: Optional[str] = None


# ==============================================================================
# Role-Report Access Matrix (변경 금지)
# ==============================================================================

ROLE_REPORT_ACCESS_MATRIX = {
    UserRole.ADMIN: [
        ReportType.MASTER,
        ReportType.LANDOWNER,
        ReportType.LH_TECHNICAL,
        ReportType.INVESTMENT,
        ReportType.QUICK_REVIEW,
        ReportType.PRESENTATION,
    ],
    UserRole.INTERNAL: [
        ReportType.MASTER,
        ReportType.LANDOWNER,
        ReportType.LH_TECHNICAL,
        ReportType.INVESTMENT,
        ReportType.QUICK_REVIEW,
        ReportType.PRESENTATION,
    ],
    UserRole.LANDOWNER: [
        ReportType.LANDOWNER,
        ReportType.PRESENTATION,
    ],
    UserRole.LH: [
        ReportType.LH_TECHNICAL,
        ReportType.PRESENTATION,
    ],
    UserRole.INVESTOR: [
        ReportType.INVESTMENT,
        ReportType.PRESENTATION,
    ],
}


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_allowed_reports_for_role(role: UserRole) -> List[ReportType]:
    """
    Role에 따라 접근 가능한 보고서 목록 반환
    
    Args:
        role: 사용자 역할
    
    Returns:
        접근 가능한 보고서 타입 목록
    """
    return ROLE_REPORT_ACCESS_MATRIX.get(role, [])


def can_access_report_by_role(role: UserRole, report_type: str) -> bool:
    """
    Role 기준으로 보고서 접근 가능 여부 확인
    
    Args:
        role: 사용자 역할
        report_type: 보고서 타입 (예: "master", "landowner")
    
    Returns:
        True if allowed, False otherwise
    """
    allowed_reports = get_allowed_reports_for_role(role)
    
    # report_type을 ReportType Enum으로 변환
    try:
        report_enum = ReportType(report_type)
        return report_enum in allowed_reports
    except ValueError:
        return False


def format_report_type(report_type: str) -> str:
    """
    보고서 타입을 표준 형식으로 변환
    
    예: "quick_review" → "quick-review"
    """
    return report_type.replace("_", "-").lower()
