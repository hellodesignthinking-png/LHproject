"""
외부 공유 API Router

목적:
- 토큰 기반 공유 링크 생성 (내부용)
- 외부 공유 엔드포인트 (공개)
- 접근 로그 기록

핵심 원칙:
"외부 공유는 편의가 아니라 '책임 있는 공개'다."
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, Response
import logging
from typing import Optional

from app.models.share_token import (
    ShareTokenCreate,
    ShareTokenResponse,
    ShareTokenStorage,
    is_token_valid,
    validate_token_scope,
    ShareToken,
)
from app.security.dependencies import CurrentUser, require_admin_or_internal
from app.models.security import format_report_type

logger = logging.getLogger(__name__)

router = APIRouter(tags=["External Sharing"])


# ==============================================================================
# 내부용: 토큰 생성 API
# ==============================================================================

@router.post("/api/v4/share/create", response_model=ShareTokenResponse)
async def create_share_token(
    request: ShareTokenCreate,
    user: CurrentUser = Depends(require_admin_or_internal)
):
    """
    공유 토큰 생성 (내부용)
    
    🔒 권한: ADMIN 또는 INTERNAL만 생성 가능
    
    Args:
        request: ShareTokenCreate
        user: 현재 사용자
    
    Returns:
        ShareTokenResponse (share_url, token, expires_at)
    """
    try:
        logger.info(
            f"🔗 [Share Token Create] Requested by {user.email}: "
            f"run_id={request.run_id}, report_type={request.report_type}, "
            f"expires_in_hours={request.expires_in_hours}"
        )
        
        # 보고서 타입 표준화
        formatted_report_type = format_report_type(request.report_type)
        
        # 토큰 생성
        share_token = ShareTokenStorage.create_token(
            run_id=request.run_id,
            report_type=formatted_report_type,
            expires_in_hours=request.expires_in_hours,
            created_by_email=user.email,
        )
        
        # 공유 URL 생성
        # 실제 운영에서는 BASE_URL 설정 필요
        base_url = "http://localhost:8091"
        share_url = f"{base_url}/shared/{share_token.token}/{formatted_report_type}/html?context_id={request.run_id}"
        
        logger.info(
            f"✅ [Share Token Created] token={share_token.token}, "
            f"expires_at={share_token.expires_at}, share_url={share_url}"
        )
        
        return ShareTokenResponse(
            share_url=share_url,
            token=share_token.token,
            expires_at=share_token.expires_at,
            expires_in_hours=request.expires_in_hours,
        )
    
    except Exception as e:
        logger.error(f"❌ [Share Token Create] Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create share token: {str(e)}")


@router.get("/api/v4/share/list")
async def list_share_tokens(
    run_id: Optional[str] = Query(None, description="RUN_ID 필터 (선택)"),
    user: CurrentUser = Depends(require_admin_or_internal)
):
    """
    공유 토큰 목록 조회 (내부용)
    
    🔒 권한: ADMIN 또는 INTERNAL만 조회 가능
    """
    try:
        tokens = ShareTokenStorage.list_tokens(run_id=run_id)
        
        logger.info(f"📋 [Share Token List] Requested by {user.email}: run_id={run_id}, count={len(tokens)}")
        
        return {
            "tokens": [token.dict() for token in tokens],
            "count": len(tokens),
        }
    
    except Exception as e:
        logger.error(f"❌ [Share Token List] Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list share tokens: {str(e)}")


@router.delete("/api/v4/share/revoke/{token}")
async def revoke_share_token(
    token: str,
    user: CurrentUser = Depends(require_admin_or_internal)
):
    """
    공유 토큰 비활성화 (내부용)
    
    🔒 권한: ADMIN 또는 INTERNAL만 비활성화 가능
    """
    try:
        success = ShareTokenStorage.deactivate_token(token)
        
        if not success:
            raise HTTPException(status_code=404, detail="Token not found")
        
        logger.info(f"🚫 [Share Token Revoked] token={token}, by={user.email}")
        
        return {
            "message": "Token revoked successfully",
            "token": token,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [Share Token Revoke] Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to revoke token: {str(e)}")


# ==============================================================================
# 외부용: 공유 링크 엔드포인트
# ==============================================================================

def verify_share_token_access(
    token: str,
    report_type: str,
    context_id: str
) -> ShareToken:
    """
    공유 토큰 검증 (외부 접근용)
    
    Args:
        token: 공유 토큰
        report_type: 보고서 타입
        context_id: RUN_ID
    
    Returns:
        ShareToken
    
    Raises:
        HTTPException 403: 토큰 검증 실패
    """
    # 1. 토큰 조회
    share_token = ShareTokenStorage.get_token(token)
    if not share_token:
        logger.warning(f"❌ [Share Access] Token not found: {token}")
        raise HTTPException(status_code=403, detail="Invalid share token")
    
    # 2. 토큰 유효성 검증
    valid, reason = is_token_valid(share_token)
    if not valid:
        logger.warning(f"❌ [Share Access] Token invalid: {token}, reason={reason}")
        raise HTTPException(status_code=403, detail=reason)
    
    # 3. 토큰 범위 검증
    formatted_report_type = format_report_type(report_type)
    scope_valid, scope_reason = validate_token_scope(
        share_token,
        run_id=context_id,
        report_type=formatted_report_type
    )
    if not scope_valid:
        logger.warning(
            f"❌ [Share Access] Token scope mismatch: {token}, "
            f"requested=({context_id}, {formatted_report_type}), "
            f"token=({share_token.run_id}, {share_token.report_type}), "
            f"reason={scope_reason}"
        )
        raise HTTPException(status_code=403, detail=scope_reason)
    
    # 4. 접근 로그 업데이트
    ShareTokenStorage.update_access(token)
    
    logger.info(
        f"✅ [Share Access] Token verified: {token}, "
        f"run_id={context_id}, report_type={formatted_report_type}, "
        f"access_count={share_token.access_count + 1}"
    )
    
    return share_token


@router.get("/shared/{token}/{report_type}/html", response_class=HTMLResponse)
async def shared_report_html(
    token: str,
    report_type: str,
    context_id: str = Query(..., description="RUN_ID")
):
    """
    외부 공유 링크 - HTML 보기
    
    🌐 공개 엔드포인트 (로그인 불필요)
    🔒 토큰 검증만 수행
    
    Args:
        token: 공유 토큰
        report_type: 보고서 타입 (예: presentation, quick-review)
        context_id: RUN_ID
    
    Returns:
        HTML 보고서
    """
    # 토큰 검증
    share_token = verify_share_token_access(token, report_type, context_id)
    
    # HTML 생성 로직 (기존 엔드포인트 재사용)
    # 실제로는 final_reports.py의 해당 보고서 생성 로직 호출
    from app.routers.final_reports import (
        quick_review_report_html,
        presentation_report_html,
    )
    
    try:
        if report_type == "quick-review":
            # E. Quick Review HTML 생성 (권한 체크 우회)
            from app.routers.final_reports import _build_common_template_data, number_format, currency_format
            from jinja2 import Environment, FileSystemLoader
            from pathlib import Path
            
            template_data = _build_common_template_data(context_id)
            templates_path = Path(__file__).parent.parent / "templates_v13"
            env = Environment(loader=FileSystemLoader(str(templates_path)))
            env.filters['number_format'] = number_format
            env.filters['currency_format'] = currency_format
            
            template = env.get_template("quick_review_report.html")
            html_content = template.render(**template_data)
            
            logger.info(f"✅ [Shared HTML] Generated: token={token}, report={report_type}")
            return HTMLResponse(content=html_content)
        
        elif report_type == "presentation":
            # F. Presentation HTML 생성 (권한 체크 우회)
            from app.routers.final_reports import _build_common_template_data, number_format, currency_format
            from jinja2 import Environment, FileSystemLoader
            from pathlib import Path
            
            template_data = _build_common_template_data(context_id)
            templates_path = Path(__file__).parent.parent / "templates_v13"
            env = Environment(loader=FileSystemLoader(str(templates_path)))
            env.filters['number_format'] = number_format
            env.filters['currency_format'] = currency_format
            
            template = env.get_template("presentation_report.html")
            html_content = template.render(**template_data)
            
            logger.info(f"✅ [Shared HTML] Generated: token={token}, report={report_type}")
            return HTMLResponse(content=html_content)
        
        else:
            raise HTTPException(status_code=404, detail=f"Report type '{report_type}' not supported for sharing")
    
    except Exception as e:
        logger.error(f"❌ [Shared HTML] Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate shared report: {str(e)}")


@router.get("/shared/{token}/{report_type}/pdf")
async def shared_report_pdf(
    token: str,
    report_type: str,
    context_id: str = Query(..., description="RUN_ID")
):
    """
    외부 공유 링크 - PDF 다운로드
    
    🌐 공개 엔드포인트 (로그인 불필요)
    🔒 토큰 검증만 수행
    
    Args:
        token: 공유 토큰
        report_type: 보고서 타입
        context_id: RUN_ID
    
    Returns:
        PDF 파일
    """
    # 토큰 검증
    share_token = verify_share_token_access(token, report_type, context_id)
    
    # PDF 생성 (캐시 활용)
    from app.services.pdf_cache import get_cached_pdf, set_cached_pdf
    from app.services.pdf_generator_playwright import generate_pdf_from_url
    from urllib.parse import quote
    
    try:
        # Step 1: 캐시 조회
        cached_pdf = get_cached_pdf(run_id=context_id, report_type=report_type)
        if cached_pdf:
            logger.info(f"⚡ [Shared PDF] Cache HIT: token={token}, report={report_type}")
            
            filename = f"{report_type}_{context_id}.pdf"
            
            return Response(
                content=cached_pdf,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{quote(filename.encode("utf-8"))}"',
                    "Access-Control-Expose-Headers": "Content-Disposition",
                    "X-Cache-Status": "HIT",
                    "X-Shared-Token": "true",
                }
            )
        
        # Step 2: Cache MISS - PDF 생성
        logger.info(f"🔄 [Shared PDF] Cache MISS: generating PDF via Playwright")
        
        # HTML 엔드포인트 URL 생성 (공유 링크 사용)
        html_url = f"http://localhost:8091/shared/{token}/{report_type}/html?context_id={context_id}"
        
        # PDF 생성
        pdf_bytes = await generate_pdf_from_url(
            url=html_url,
            run_id=context_id,
            report_type=report_type.upper(),
            timeout_ms=60000
        )
        
        # Step 3: 캐시에 저장
        set_cached_pdf(run_id=context_id, report_type=report_type, pdf_bytes=pdf_bytes)
        
        filename = f"{report_type}_{context_id}.pdf"
        
        logger.info(f"✅ [Shared PDF] Generated: token={token}, report={report_type}, size={len(pdf_bytes)} bytes")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{quote(filename.encode("utf-8"))}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
                "X-Cache-Status": "MISS",
                "X-Shared-Token": "true",
            }
        )
    
    except Exception as e:
        logger.error(f"❌ [Shared PDF] Failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate shared PDF: {str(e)}")
