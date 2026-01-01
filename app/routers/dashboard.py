"""
ZeroSite v1.4: RUN_ID Dashboard API
====================================

RUN_ID 기반 보고서 대시보드 API
- 6종 보고서 목록 조회
- 권한 기반 접근 가능 여부 확인
- 공유 링크 관리
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from app.models.security import UserRole
from app.security.dependencies import get_current_user, CurrentUser
from app.models.security import ROLE_REPORT_ACCESS_MATRIX
from app.models.share_token import ShareTokenStorage

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v4/dashboard",
    tags=["Dashboard"]
)


# ============================================================================
# Response Models
# ============================================================================

class ReportInfo(BaseModel):
    """보고서 정보"""
    code: str  # A, B, C, D, E, F
    name: str  # 종합 최종, 토지주 제출, ...
    name_en: str  # master, landowner, ...
    has_html_access: bool
    has_pdf_access: bool
    can_share: bool  # 외부 공유 가능 여부
    description: str


class RunIdInfo(BaseModel):
    """RUN_ID 프로젝트 정보"""
    run_id: str
    address: Optional[str] = None
    pnu: Optional[str] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = None


class DashboardResponse(BaseModel):
    """대시보드 응답"""
    run_id_info: RunIdInfo
    reports: List[ReportInfo]
    user_role: str


class ShareLinkInfo(BaseModel):
    """공유 링크 정보"""
    token: str
    report_type: str
    run_id: str
    expires_at: datetime
    access_count: int
    last_accessed_at: Optional[datetime]
    is_active: bool
    created_at: datetime


# ============================================================================
# 보고서 메타데이터
# ============================================================================

REPORT_METADATA = {
    "A": {
        "name": "종합 최종 보고서",
        "name_en": "master",
        "description": "전체 분석 결과 종합 보고서",
        "can_share": False
    },
    "B": {
        "name": "토지주 제출용 보고서",
        "name_en": "landowner",
        "description": "토지주에게 제출하는 요약 보고서",
        "can_share": True
    },
    "C": {
        "name": "LH 기술검증 보고서",
        "name_en": "lh-technical",
        "description": "LH 기술검증을 위한 상세 보고서",
        "can_share": False
    },
    "D": {
        "name": "투자 검토 보고서",
        "name_en": "investment",
        "description": "투자자를 위한 재무 분석 보고서",
        "can_share": True
    },
    "E": {
        "name": "사전 검토 보고서",
        "name_en": "quick-review",
        "description": "빠른 사전 검토용 요약 보고서",
        "can_share": False
    },
    "F": {
        "name": "설명 프레젠테이션",
        "name_en": "presentation",
        "description": "고객 설명용 프레젠테이션 보고서",
        "can_share": True
    }
}


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/{run_id}", response_model=DashboardResponse)
async def get_run_id_dashboard(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    RUN_ID 대시보드 조회
    
    - RUN_ID 정보
    - 6종 보고서 목록
    - 권한 기반 접근 가능 여부
    """
    logger.info(f"📊 [Dashboard] RUN_ID={run_id}, User={current_user.email}, Role={current_user.role}")
    
    user_role = current_user.role
    
    # RUN_ID 정보 (실제로는 context_storage에서 조회)
    run_id_info = RunIdInfo(
        run_id=run_id,
        address="서울시 강남구 역삼동 123-45",  # 추후 context_storage에서 조회
        pnu="1168010100101230045",
        created_at=datetime.now(),
        status="분석 완료"
    )
    
    # 6종 보고서 정보 생성
    reports = []
    for code in ["A", "B", "C", "D", "E", "F"]:
        meta = REPORT_METADATA[code]
        
        # 권한 체크 (ROLE_REPORT_ACCESS_MATRIX 사용)
        from app.models.security import ReportType
        report_type_map = {
            "A": ReportType.MASTER,
            "B": ReportType.LANDOWNER,
            "C": ReportType.LH_TECHNICAL,
            "D": ReportType.INVESTMENT,
            "E": ReportType.QUICK_REVIEW,
            "F": ReportType.PRESENTATION
        }
        
        user_role_enum = UserRole(user_role)
        has_access = report_type_map[code] in ROLE_REPORT_ACCESS_MATRIX.get(user_role_enum, [])
        
        report_info = ReportInfo(
            code=code,
            name=meta["name"],
            name_en=meta["name_en"],
            has_html_access=has_access,
            has_pdf_access=has_access,
            can_share=meta["can_share"] and has_access,  # 공유는 접근 권한이 있어야 가능
            description=meta["description"]
        )
        reports.append(report_info)
    
    return DashboardResponse(
        run_id_info=run_id_info,
        reports=reports,
        user_role=user_role
    )


@router.get("/{run_id}/shares", response_model=List[ShareLinkInfo])
async def get_share_links(
    run_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    RUN_ID의 공유 링크 목록 조회
    
    - 생성된 토큰 목록
    - 접근 로그
    - 만료 상태
    """
    logger.info(f"🔗 [Share Links] RUN_ID={run_id}, User={current_user.email}")
    
    storage = ShareTokenStorage()
    all_tokens = storage.get_all_tokens()
    
    # RUN_ID에 해당하는 토큰만 필터링
    run_id_tokens = [
        token for token in all_tokens
        if token.run_id == run_id
    ]
    
    # ShareLinkInfo로 변환
    share_links = [
        ShareLinkInfo(
            token=token.token,
            report_type=token.report_type,
            run_id=token.run_id,
            expires_at=token.expires_at,
            access_count=token.access_count,
            last_accessed_at=token.last_accessed_at,
            is_active=token.is_active,
            created_at=token.created_at
        )
        for token in run_id_tokens
    ]
    
    return share_links


@router.delete("/{run_id}/shares/{token}")
async def revoke_share_link(
    run_id: str,
    token: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    공유 링크 비활성화 (취소)
    
    - 토큰을 비활성화하여 더 이상 접근 불가능하게 함
    """
    logger.info(f"🚫 [Revoke Share] Token={token}, RUN_ID={run_id}, User={current_user.email}")
    
    storage = ShareTokenStorage()
    token_obj = storage.get_token(token)
    
    if not token_obj:
        raise HTTPException(status_code=404, detail="Share token not found")
    
    if token_obj.run_id != run_id:
        raise HTTPException(status_code=403, detail="Token does not belong to this RUN_ID")
    
    # 토큰 비활성화
    storage.deactivate_token(token)
    
    return {"message": "Share link revoked successfully", "token": token}


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def dashboard_health():
    """대시보드 API 헬스 체크"""
    return {
        "status": "healthy",
        "service": "dashboard",
        "version": "v1.4"
    }
