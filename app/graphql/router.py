"""
ZeroSite v4.0 - GraphQL Router
FastAPI에 GraphQL 엔드포인트 추가
"""

from fastapi import APIRouter, Depends
from strawberry.fastapi import GraphQLRouter
from app.graphql.schema import schema
from app.core.auth_deps import get_current_user  # JWT 인증


# GraphQL Router 생성
graphql_router = GraphQLRouter(
    schema,
    graphiql=True,  # GraphiQL IDE 활성화
    path="/graphql"
)

# FastAPI Router 생성
router = APIRouter(
    prefix="/graphql",
    tags=["GraphQL"]
)

# GraphQL 엔드포인트
# Note: 인증이 필요한 경우 아래 주석 해제
# @router.get("")
# @router.post("")
# async def graphql_endpoint(current_user = Depends(get_current_user)):
#     """GraphQL 엔드포인트 (인증 필요)"""
#     return graphql_router


# 인증 없이 사용 (개발/테스트용)
def get_graphql_router():
    """GraphQL Router 반환"""
    return graphql_router
