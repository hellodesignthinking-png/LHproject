"""
v1.6.0: Access Logging Middleware
모든 보고서 접근을 자동으로 로깅
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid
from typing import Optional

from app.models.access_log import (
    AccessLog,
    AccessAction,
    get_access_log_storage
)


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    """
    보고서 접근을 자동으로 로깅하는 미들웨어
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.storage = get_access_log_storage()
    
    async def dispatch(self, request: Request, call_next):
        # Start timing
        start_time = time.time()
        
        # Check if this is a report access request
        should_log = self._should_log_request(request)
        
        # Process request
        try:
            response = await call_next(request)
            success = response.status_code < 400
            error_message = None
        except Exception as e:
            success = False
            error_message = str(e)
            raise
        finally:
            # Log if needed
            if should_log:
                response_time_ms = int((time.time() - start_time) * 1000)
                self._log_access(request, response_time_ms, success, error_message)
        
        return response
    
    def _should_log_request(self, request: Request) -> bool:
        """로깅할 요청인지 확인"""
        path = request.url.path
        
        # Log report access requests
        if "/api/v4/reports/six-types/" in path:
            return True
        
        # Log dashboard access
        if path.startswith("/dashboard"):
            return True
        
        # Log share link creation
        if "/api/v4/share/create" in path:
            return True
        
        return False
    
    def _log_access(
        self,
        request: Request,
        response_time_ms: int,
        success: bool,
        error_message: Optional[str]
    ):
        """접근 로그 생성 및 저장"""
        try:
            # Extract action from path
            action = self._determine_action(request.url.path)
            
            # Extract RUN_ID and report type
            run_id, report_type = self._extract_resource_info(request)
            
            # Extract user information
            user_email = request.headers.get("X-User-Email")
            user_role = request.headers.get("X-User-Role")
            
            # Get IP address
            ip_address = self._get_client_ip(request)
            
            # Get share token if present
            share_token = request.query_params.get("token")
            
            # Create log entry
            log = AccessLog(
                log_id=str(uuid.uuid4()),
                user_email=user_email,
                user_role=user_role,
                ip_address=ip_address,
                user_agent=request.headers.get("User-Agent"),
                run_id=run_id or "UNKNOWN",
                report_type=report_type or "UNKNOWN",
                action=action,
                share_token=share_token,
                success=success,
                error_message=error_message,
                request_path=request.url.path,
                response_time_ms=response_time_ms
            )
            
            # Save log
            self.storage.log_access(log)
            
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"Error logging access: {e}")
    
    def _determine_action(self, path: str) -> AccessAction:
        """요청 경로에서 액션 추출"""
        if "/html" in path:
            return AccessAction.VIEW_HTML
        elif "/pdf" in path:
            return AccessAction.DOWNLOAD_PDF
        elif "/share/create" in path:
            return AccessAction.CREATE_SHARE
        elif "/share/" in path:
            return AccessAction.USE_SHARE_TOKEN
        elif "/dashboard" in path:
            return AccessAction.VIEW_DASHBOARD
        else:
            return AccessAction.VIEW_HTML  # Default
    
    def _extract_resource_info(self, request: Request) -> tuple[Optional[str], Optional[str]]:
        """요청에서 RUN_ID와 report_type 추출"""
        # From query params
        run_id = request.query_params.get("context_id")
        
        # From path params
        path_parts = request.url.path.split("/")
        report_type = None
        
        # Extract report type from path like /api/v4/reports/six-types/master/html
        if "six-types" in path_parts:
            try:
                idx = path_parts.index("six-types")
                if idx + 1 < len(path_parts):
                    report_type = path_parts[idx + 1]
            except (ValueError, IndexError):
                pass
        
        # Dashboard case
        if "/dashboard/" in request.url.path:
            try:
                idx = path_parts.index("dashboard")
                if idx + 1 < len(path_parts):
                    run_id = path_parts[idx + 1]
                    report_type = "dashboard"
            except (ValueError, IndexError):
                pass
        
        return run_id, report_type
    
    def _get_client_ip(self, request: Request) -> str:
        """클라이언트 IP 주소 추출 (프록시 고려)"""
        # Check X-Forwarded-For header first (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        if request.client:
            return request.client.host
        
        return "UNKNOWN"
