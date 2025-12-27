"""
ZeroSite v4.0 - GraphQL Schema
Strawberry GraphQL 스키마 정의
"""

import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

@strawberry.enum
class AnalysisStatus(Enum):
    """분석 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@strawberry.enum
class Verdict(Enum):
    """사업 타당성 판정"""
    GO = "GO"
    CONDITIONAL_GO = "CONDITIONAL_GO"
    NO_GO = "NO_GO"


@strawberry.enum
class UserRole(Enum):
    """사용자 역할"""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


# ============================================================================
# Types
# ============================================================================

@strawberry.type
class LandInfo:
    """부지 정보"""
    parcel_id: str
    address: str
    area_pyeong: float
    area_sqm: float
    zone: str
    far_percent: float
    bcr_percent: float
    asking_price_million: float


@strawberry.type
class AppraisalResult:
    """감정평가 결과"""
    official_land_price_per_sqm: float
    market_price_per_sqm: float
    acquisition_cost_million: float
    total_project_cost_million: float
    discount_rate: float


@strawberry.type
class CapacityResult:
    """용적률 검토 결과"""
    max_floor_area_ratio: float
    max_building_coverage_ratio: float
    total_floor_area_sqm: float
    buildable_units: int
    parking_spaces_required: int


@strawberry.type
class FeasibilityResult:
    """재무 타당성 결과"""
    total_revenue_million: float
    net_profit_million: float
    profit_margin_percent: float
    roi_percent: float
    irr_percent: float
    npv_million: float
    payback_period_years: float


@strawberry.type
class LHReview:
    """LH 평가 결과"""
    lh_score: float
    location_score: float
    development_score: float
    financial_score: float
    risk_score: float
    final_verdict: Verdict
    recommendation: str


@strawberry.type
class AnalysisResult:
    """분석 결과 (전체)"""
    job_id: str
    status: AnalysisStatus
    progress: int
    land_info: LandInfo
    appraisal: Optional[AppraisalResult]
    capacity: Optional[CapacityResult]
    feasibility: Optional[FeasibilityResult]
    lh_review: Optional[LHReview]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]


@strawberry.type
class User:
    """사용자"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime


@strawberry.type
class APIKey:
    """API 키"""
    id: int
    name: str
    key_prefix: str
    usage_count: int
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime


@strawberry.type
class Chart:
    """차트 데이터"""
    job_id: str
    chart_type: str
    image_url: str
    created_at: datetime


# ============================================================================
# Input Types
# ============================================================================

@strawberry.input
class LandInfoInput:
    """부지 정보 입력"""
    parcel_id: str
    address: str
    area_pyeong: float
    area_sqm: float
    zone: str
    far_percent: float
    bcr_percent: float
    asking_price_million: float


@strawberry.input
class UserInput:
    """사용자 생성 입력"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER


@strawberry.input
class APIKeyInput:
    """API 키 생성 입력"""
    name: str
    expires_days: Optional[int] = 90


# ============================================================================
# Queries
# ============================================================================

@strawberry.type
class Query:
    """GraphQL 쿼리"""
    
    @strawberry.field
    def hello(self) -> str:
        """테스트 쿼리"""
        return "Hello from ZeroSite GraphQL API!"
    
    @strawberry.field
    async def analysis_result(self, job_id: str) -> Optional[AnalysisResult]:
        """
        분석 결과 조회
        
        Args:
            job_id: 작업 ID
        
        Returns:
            분석 결과 또는 None
        """
        # TODO: 실제 데이터베이스에서 조회
        return None
    
    @strawberry.field
    async def analysis_results(
        self,
        status: Optional[AnalysisStatus] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[AnalysisResult]:
        """
        분석 결과 목록 조회
        
        Args:
            status: 필터링할 상태 (선택)
            limit: 결과 개수 제한
            offset: 오프셋
        
        Returns:
            분석 결과 리스트
        """
        # TODO: 실제 데이터베이스에서 조회
        return []
    
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        """
        사용자 조회
        
        Args:
            id: 사용자 ID
        
        Returns:
            사용자 정보 또는 None
        """
        # TODO: 실제 데이터베이스에서 조회
        return None
    
    @strawberry.field
    async def users(
        self,
        role: Optional[UserRole] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[User]:
        """
        사용자 목록 조회
        
        Args:
            role: 필터링할 역할 (선택)
            limit: 결과 개수 제한
            offset: 오프셋
        
        Returns:
            사용자 리스트
        """
        # TODO: 실제 데이터베이스에서 조회
        return []
    
    @strawberry.field
    async def api_keys(self, user_id: int) -> List[APIKey]:
        """
        API 키 목록 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            API 키 리스트
        """
        # TODO: 실제 데이터베이스에서 조회
        return []
    
    @strawberry.field
    async def charts(self, job_id: str) -> List[Chart]:
        """
        차트 목록 조회
        
        Args:
            job_id: 작업 ID
        
        Returns:
            차트 리스트
        """
        # TODO: 실제 파일 시스템에서 조회
        return []


# ============================================================================
# Mutations
# ============================================================================

@strawberry.type
class Mutation:
    """GraphQL 뮤테이션"""
    
    @strawberry.mutation
    async def create_analysis(self, land_info: LandInfoInput) -> AnalysisResult:
        """
        분석 생성
        
        Args:
            land_info: 부지 정보
        
        Returns:
            생성된 분석 결과
        """
        # TODO: 실제 분석 작업 시작
        import uuid
        from datetime import datetime
        
        job_id = str(uuid.uuid4())
        
        return AnalysisResult(
            job_id=job_id,
            status=AnalysisStatus.PENDING,
            progress=0,
            land_info=LandInfo(**land_info.__dict__),
            appraisal=None,
            capacity=None,
            feasibility=None,
            lh_review=None,
            created_at=datetime.now(),
            completed_at=None,
            error_message=None
        )
    
    @strawberry.mutation
    async def delete_analysis(self, job_id: str) -> bool:
        """
        분석 삭제
        
        Args:
            job_id: 작업 ID
        
        Returns:
            성공 여부
        """
        # TODO: 실제 데이터베이스에서 삭제
        return True
    
    @strawberry.mutation
    async def create_user(self, user_input: UserInput) -> User:
        """
        사용자 생성
        
        Args:
            user_input: 사용자 입력
        
        Returns:
            생성된 사용자
        """
        # TODO: 실제 데이터베이스에 저장
        from datetime import datetime
        
        return User(
            id=1,
            username=user_input.username,
            email=user_input.email,
            full_name=user_input.full_name,
            role=user_input.role,
            is_active=True,
            created_at=datetime.now()
        )
    
    @strawberry.mutation
    async def create_api_key(self, api_key_input: APIKeyInput, user_id: int) -> APIKey:
        """
        API 키 생성
        
        Args:
            api_key_input: API 키 입력
            user_id: 사용자 ID
        
        Returns:
            생성된 API 키
        """
        # TODO: 실제 데이터베이스에 저장
        from datetime import datetime, timedelta
        
        expires_at = datetime.now() + timedelta(days=api_key_input.expires_days or 90)
        
        return APIKey(
            id=1,
            name=api_key_input.name,
            key_prefix="zerosite_",
            usage_count=0,
            last_used_at=None,
            expires_at=expires_at,
            is_active=True,
            created_at=datetime.now()
        )
    
    @strawberry.mutation
    async def revoke_api_key(self, api_key_id: int) -> bool:
        """
        API 키 비활성화
        
        Args:
            api_key_id: API 키 ID
        
        Returns:
            성공 여부
        """
        # TODO: 실제 데이터베이스에서 업데이트
        return True


# ============================================================================
# Subscriptions (WebSocket)
# ============================================================================

@strawberry.type
class Subscription:
    """GraphQL 구독 (실시간 업데이트)"""
    
    @strawberry.subscription
    async def analysis_progress(self, job_id: str) -> AnalysisResult:
        """
        분석 진행 상황 구독
        
        Args:
            job_id: 작업 ID
        
        Yields:
            실시간 분석 결과
        """
        # TODO: 실제 분석 진행 상황 스트리밍
        import asyncio
        from datetime import datetime
        
        for progress in range(0, 101, 10):
            await asyncio.sleep(1)
            
            yield AnalysisResult(
                job_id=job_id,
                status=AnalysisStatus.RUNNING if progress < 100 else AnalysisStatus.COMPLETED,
                progress=progress,
                land_info=LandInfo(
                    parcel_id="TEST-001",
                    address="테스트 주소",
                    area_pyeong=100,
                    area_sqm=330,
                    zone="제2종일반주거지역",
                    far_percent=200,
                    bcr_percent=60,
                    asking_price_million=10000
                ),
                appraisal=None,
                capacity=None,
                feasibility=None,
                lh_review=None,
                created_at=datetime.now(),
                completed_at=None,
                error_message=None
            )


# ============================================================================
# Schema
# ============================================================================

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)
