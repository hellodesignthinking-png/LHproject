"""
접근 제어 유틸리티

목적:
- Role 기반 접근 제어
- RUN_ID 단위 접근 제어
- 보고서 타입별 접근 제어

핵심:
"누가, 어떤 RUN_ID의, 어떤 보고서를 볼 수 있는지 통제"
"""

import logging
from typing import Optional, List
from app.models.security import (
    UserRole,
    ReportType,
    can_access_report_by_role,
    format_report_type,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# Role-Based Access Control
# ==============================================================================

def check_role_access(user_role: str, report_type: str) -> tuple[bool, Optional[str]]:
    """
    Role 기준 보고서 접근 권한 확인
    
    Args:
        user_role: 사용자 역할 (예: "ADMIN", "LANDOWNER")
        report_type: 보고서 타입 (예: "master", "landowner")
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    try:
        # Role Enum 변환
        role_enum = UserRole(user_role.upper())
    except ValueError:
        return False, f"Invalid role: {user_role}"
    
    # 보고서 타입 표준화
    formatted_report_type = format_report_type(report_type)
    
    # 권한 확인
    allowed = can_access_report_by_role(role_enum, formatted_report_type)
    
    if allowed:
        logger.info(f"✅ Access granted: role={user_role}, report={formatted_report_type}")
        return True, None
    else:
        reason = f"Role '{user_role}' cannot access report type '{formatted_report_type}'"
        logger.warning(f"❌ Access denied: {reason}")
        return False, reason


def check_run_id_access(
    user_id: str,
    run_id: str,
    allowed_run_ids: Optional[List[str]] = None
) -> tuple[bool, Optional[str]]:
    """
    RUN_ID 단위 접근 권한 확인
    
    Args:
        user_id: 사용자 ID
        run_id: 요청한 RUN_ID
        allowed_run_ids: 사용자가 접근 가능한 RUN_ID 목록 (None이면 모두 허용)
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    # allowed_run_ids가 None이면 모든 RUN_ID 허용 (ADMIN/INTERNAL)
    if allowed_run_ids is None:
        logger.info(f"✅ RUN_ID access granted (unrestricted): user={user_id}, run_id={run_id}")
        return True, None
    
    # RUN_ID 목록에 포함되어 있는지 확인
    if run_id in allowed_run_ids:
        logger.info(f"✅ RUN_ID access granted: user={user_id}, run_id={run_id}")
        return True, None
    else:
        reason = f"User '{user_id}' cannot access RUN_ID '{run_id}'"
        logger.warning(f"❌ RUN_ID access denied: {reason}")
        return False, reason


def check_full_access(
    user_id: str,
    user_role: str,
    run_id: str,
    report_type: str,
    allowed_run_ids: Optional[List[str]] = None
) -> tuple[bool, Optional[str]]:
    """
    전체 접근 권한 확인 (Role + RUN_ID + Report Type)
    
    Args:
        user_id: 사용자 ID
        user_role: 사용자 역할
        run_id: 요청한 RUN_ID
        report_type: 보고서 타입
        allowed_run_ids: 사용자가 접근 가능한 RUN_ID 목록
    
    Returns:
        (allowed: bool, reason: Optional[str])
    """
    # Step 1: Role 기준 보고서 접근 권한 확인
    role_allowed, role_reason = check_role_access(user_role, report_type)
    if not role_allowed:
        return False, role_reason
    
    # Step 2: RUN_ID 접근 권한 확인
    run_id_allowed, run_id_reason = check_run_id_access(user_id, run_id, allowed_run_ids)
    if not run_id_allowed:
        return False, run_id_reason
    
    # 모든 검사 통과
    logger.info(f"✅ Full access granted: user={user_id}, role={user_role}, run_id={run_id}, report={report_type}")
    return True, None


# ==============================================================================
# Convenience Functions
# ==============================================================================

def get_allowed_reports(user_role: str) -> List[str]:
    """
    사용자 Role에 따라 접근 가능한 보고서 목록 반환
    
    Args:
        user_role: 사용자 역할
    
    Returns:
        보고서 타입 문자열 목록 (예: ["master", "landowner"])
    """
    try:
        role_enum = UserRole(user_role.upper())
        from app.models.security import get_allowed_reports_for_role
        allowed_report_enums = get_allowed_reports_for_role(role_enum)
        return [report.value for report in allowed_report_enums]
    except ValueError:
        logger.error(f"Invalid role: {user_role}")
        return []


def is_admin_or_internal(user_role: str) -> bool:
    """
    ADMIN 또는 INTERNAL 역할인지 확인
    
    Args:
        user_role: 사용자 역할
    
    Returns:
        True if ADMIN or INTERNAL, False otherwise
    """
    try:
        role_enum = UserRole(user_role.upper())
        return role_enum in [UserRole.ADMIN, UserRole.INTERNAL]
    except ValueError:
        return False


# ==============================================================================
# Access Logging
# ==============================================================================

def log_access_attempt(
    user_id: str,
    user_role: str,
    run_id: str,
    report_type: str,
    allowed: bool,
    reason: Optional[str] = None
):
    """
    접근 시도 로그 기록 (추후 감사/모니터링용)
    
    Args:
        user_id: 사용자 ID
        user_role: 사용자 역할
        run_id: 요청한 RUN_ID
        report_type: 보고서 타입
        allowed: 접근 허용 여부
        reason: 거부 사유 (있는 경우)
    """
    status = "GRANTED" if allowed else "DENIED"
    log_msg = f"[ACCESS {status}] user={user_id}, role={user_role}, run_id={run_id}, report={report_type}"
    
    if reason:
        log_msg += f", reason={reason}"
    
    if allowed:
        logger.info(log_msg)
    else:
        logger.warning(log_msg)
