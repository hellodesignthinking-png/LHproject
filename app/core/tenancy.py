"""
ZeroSite v4.0 - Multi-tenancy Middleware
조직별 데이터 격리 미들웨어
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Multi-tenancy 미들웨어
    
    요청마다 조직 컨텍스트를 설정하고 데이터 격리를 보장합니다.
    """
    
    async def dispatch(self, request: Request, call_next):
        # 조직 ID 추출 (여러 방법 지원)
        organization_id = await self.extract_organization_id(request)
        
        # 요청 상태에 조직 ID 저장
        request.state.organization_id = organization_id
        
        # 로깅
        if organization_id:
            logger.info(f"Request from organization_id={organization_id}: {request.method} {request.url.path}")
        
        # 다음 미들웨어/핸들러 호출
        response = await call_next(request)
        
        # 응답 헤더에 조직 정보 추가 (선택사항)
        if organization_id:
            response.headers["X-Organization-Id"] = str(organization_id)
        
        return response
    
    async def extract_organization_id(self, request: Request) -> Optional[int]:
        """
        요청에서 조직 ID 추출
        
        우선순위:
        1. 헤더: X-Organization-Id
        2. 쿼리 파라미터: org_id
        3. JWT 토큰의 organization_id 클레임
        4. 서브도메인: {org_slug}.zerosite.com
        """
        
        # 1. HTTP 헤더에서 추출
        org_id_header = request.headers.get("X-Organization-Id")
        if org_id_header:
            try:
                return int(org_id_header)
            except ValueError:
                logger.warning(f"Invalid X-Organization-Id header: {org_id_header}")
        
        # 2. 쿼리 파라미터에서 추출
        org_id_query = request.query_params.get("org_id")
        if org_id_query:
            try:
                return int(org_id_query)
            except ValueError:
                logger.warning(f"Invalid org_id query parameter: {org_id_query}")
        
        # 3. JWT 토큰에서 추출 (request.state.user가 설정된 경우)
        if hasattr(request.state, "user"):
            user = request.state.user
            if hasattr(user, "organization_id"):
                return user.organization_id
        
        # 4. 서브도메인에서 추출
        host = request.headers.get("host", "")
        if host:
            subdomain = host.split(".")[0]
            # TODO: 서브도메인으로 조직 조회
            # org = await get_organization_by_slug(subdomain)
            # return org.id if org else None
        
        # 조직 ID를 찾을 수 없는 경우
        return None


def get_current_organization_id(request: Request) -> int:
    """
    현재 요청의 조직 ID 반환
    
    FastAPI 의존성 주입에서 사용:
    
    @app.get("/api/v1/data")
    async def get_data(
        request: Request,
        org_id: int = Depends(get_current_organization_id)
    ):
        # org_id를 사용하여 데이터 조회
        ...
    """
    if not hasattr(request.state, "organization_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID not found in request"
        )
    
    organization_id = request.state.organization_id
    if organization_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID is required"
        )
    
    return organization_id


async def verify_organization_access(
    request: Request,
    target_organization_id: int
) -> bool:
    """
    사용자가 특정 조직에 접근 권한이 있는지 확인
    
    Args:
        request: FastAPI Request 객체
        target_organization_id: 접근하려는 조직 ID
    
    Returns:
        접근 권한 여부
    
    Raises:
        HTTPException: 권한이 없는 경우
    """
    current_org_id = get_current_organization_id(request)
    
    # 조직 ID 불일치 시 접근 거부
    if current_org_id != target_organization_id:
        logger.warning(
            f"Organization access denied: current_org={current_org_id}, "
            f"target_org={target_organization_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization's data"
        )
    
    return True


# SQLAlchemy 쿼리 필터 헬퍼
def add_organization_filter(query, model, organization_id: int):
    """
    SQLAlchemy 쿼리에 조직 필터 추가
    
    사용 예시:
    query = session.query(AnalysisJob)
    query = add_organization_filter(query, AnalysisJob, organization_id)
    results = query.all()
    """
    return query.filter(model.organization_id == organization_id)
