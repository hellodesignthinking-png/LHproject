"""
프로젝트 관리 데이터 모델
"""

from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field
import uuid


class ProjectStatus(str, Enum):
    """프로젝트 상태"""
    PLANNING = "기획"
    LAND_ANALYSIS = "토지분석"
    APPROVAL_PENDING = "인허가진행"
    DESIGN = "설계"
    PRE_AGREEMENT = "사전약정"
    CONSTRUCTION = "시공"
    INSPECTION = "준공검사"
    PURCHASE_PENDING = "매입심사"
    COMPLETED = "완료"
    CANCELLED = "취소"


class MilestoneStatus(str, Enum):
    """마일스톤 상태"""
    NOT_STARTED = "미시작"
    IN_PROGRESS = "진행중"
    COMPLETED = "완료"
    DELAYED = "지연"
    BLOCKED = "차단"


class RiskLevel(str, Enum):
    """리스크 레벨"""
    LOW = "낮음"
    MEDIUM = "보통"
    HIGH = "높음"
    CRITICAL = "심각"


class Project(BaseModel):
    """프로젝트 모델"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="프로젝트 ID")
    name: str = Field(..., description="프로젝트명")
    address: str = Field(..., description="사업지 주소")
    land_area: float = Field(..., gt=0, description="토지 면적(㎡)")
    unit_type: str = Field(..., description="세대 유형 (청년형/신혼부부형/고령자형)")
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING, description="프로젝트 상태")
    
    # 사업 기본정보
    estimated_units: Optional[int] = Field(None, description="예상 세대수")
    estimated_cost: Optional[float] = Field(None, description="예상 사업비(원)")
    target_purchase_price: Optional[float] = Field(None, description="목표 매입가(원)")
    
    # 일정
    start_date: datetime = Field(default_factory=datetime.now, description="시작일")
    target_completion_date: Optional[datetime] = Field(None, description="목표 완료일")
    actual_completion_date: Optional[datetime] = Field(None, description="실제 완료일")
    
    # 분석 결과 참조
    analysis_id: Optional[str] = Field(None, description="토지분석 결과 ID")
    
    # 담당자 및 협력사
    project_manager: Optional[str] = Field(None, description="프로젝트 매니저")
    contractor: Optional[str] = Field(None, description="시공사")
    architect: Optional[str] = Field(None, description="설계사")
    
    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일시")
    created_by: Optional[str] = Field(None, description="생성자")
    
    # 추가 정보
    notes: Optional[str] = Field(None, description="비고")
    tags: List[str] = Field(default_factory=list, description="태그")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "서울 강남 역삼동 신축매입임대 프로젝트",
                "address": "서울특별시 강남구 역삼동 679",
                "land_area": 500.0,
                "unit_type": "청년형",
                "estimated_units": 34,
                "estimated_cost": 2500000000,
                "project_manager": "김철수"
            }
        }


class ProjectMilestone(BaseModel):
    """프로젝트 마일스톤"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="마일스톤 ID")
    project_id: str = Field(..., description="프로젝트 ID")
    name: str = Field(..., description="마일스톤명")
    description: Optional[str] = Field(None, description="설명")
    status: MilestoneStatus = Field(default=MilestoneStatus.NOT_STARTED, description="상태")
    
    # 일정
    planned_start_date: Optional[datetime] = Field(None, description="계획 시작일")
    planned_end_date: Optional[datetime] = Field(None, description="계획 완료일")
    actual_start_date: Optional[datetime] = Field(None, description="실제 시작일")
    actual_end_date: Optional[datetime] = Field(None, description="실제 완료일")
    
    # 진행률
    progress_percentage: int = Field(default=0, ge=0, le=100, description="진행률(%)")
    
    # 담당자 및 관련 정보
    assignee: Optional[str] = Field(None, description="담당자")
    dependencies: List[str] = Field(default_factory=list, description="선행 마일스톤 ID 목록")
    
    # 체크리스트
    checklist: List[Dict[str, bool]] = Field(default_factory=list, description="체크리스트")
    
    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now, description="생성일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일시")
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "abc-123",
                "name": "토지 입지분석",
                "description": "LH 매입 적합성 검토 및 리스크 분석",
                "status": "진행중",
                "progress_percentage": 75,
                "checklist": [
                    {"유해시설 검토": True},
                    {"접근성 분석": True},
                    {"인구통계 분석": False}
                ]
            }
        }


class ProjectRisk(BaseModel):
    """프로젝트 리스크"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="리스크 ID")
    project_id: str = Field(..., description="프로젝트 ID")
    title: str = Field(..., description="리스크 제목")
    description: str = Field(..., description="리스크 설명")
    category: str = Field(..., description="카테고리 (입지/인허가/시공/재무 등)")
    level: RiskLevel = Field(..., description="리스크 레벨")
    
    # 대응 계획
    mitigation_plan: Optional[str] = Field(None, description="완화 계획")
    contingency_plan: Optional[str] = Field(None, description="비상 계획")
    
    # 상태
    status: str = Field(default="활성", description="상태 (활성/해결/무시)")
    resolved_at: Optional[datetime] = Field(None, description="해결일시")
    
    # 메타데이터
    identified_by: Optional[str] = Field(None, description="식별자")
    identified_at: datetime = Field(default_factory=datetime.now, description="식별일시")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정일시")


class ProjectDocument(BaseModel):
    """프로젝트 문서"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="문서 ID")
    project_id: str = Field(..., description="프로젝트 ID")
    name: str = Field(..., description="문서명")
    document_type: str = Field(..., description="문서 유형 (계약서/설계도/보고서 등)")
    file_path: Optional[str] = Field(None, description="파일 경로")
    file_url: Optional[str] = Field(None, description="파일 URL")
    file_size: Optional[int] = Field(None, description="파일 크기(bytes)")
    mime_type: Optional[str] = Field(None, description="MIME 타입")
    
    # 버전 관리
    version: str = Field(default="1.0", description="버전")
    is_latest: bool = Field(default=True, description="최신 버전 여부")
    
    # 메타데이터
    uploaded_by: Optional[str] = Field(None, description="업로드자")
    uploaded_at: datetime = Field(default_factory=datetime.now, description="업로드일시")
    description: Optional[str] = Field(None, description="설명")
    tags: List[str] = Field(default_factory=list, description="태그")


class ProjectTimeline(BaseModel):
    """프로젝트 타임라인 이벤트"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="이벤트 ID")
    project_id: str = Field(..., description="프로젝트 ID")
    event_type: str = Field(..., description="이벤트 유형")
    title: str = Field(..., description="제목")
    description: Optional[str] = Field(None, description="설명")
    occurred_at: datetime = Field(default_factory=datetime.now, description="발생일시")
    created_by: Optional[str] = Field(None, description="생성자")
    metadata: Dict = Field(default_factory=dict, description="추가 메타데이터")


class ProjectDashboardSummary(BaseModel):
    """프로젝트 대시보드 요약"""
    total_projects: int = Field(..., description="총 프로젝트 수")
    active_projects: int = Field(..., description="진행중 프로젝트 수")
    completed_projects: int = Field(..., description="완료 프로젝트 수")
    
    by_status: Dict[str, int] = Field(..., description="상태별 프로젝트 수")
    by_unit_type: Dict[str, int] = Field(..., description="유형별 프로젝트 수")
    
    total_estimated_cost: float = Field(..., description="총 예상 사업비")
    total_units: int = Field(..., description="총 세대수")
    
    high_risk_count: int = Field(..., description="고위험 프로젝트 수")
    delayed_milestones: int = Field(..., description="지연된 마일스톤 수")
    
    recent_activities: List[ProjectTimeline] = Field(..., description="최근 활동")


# 프로젝트 생성/수정 요청 모델
class ProjectCreateRequest(BaseModel):
    """프로젝트 생성 요청"""
    name: str = Field(..., description="프로젝트명")
    address: str = Field(..., description="사업지 주소")
    land_area: float = Field(..., gt=0, description="토지 면적(㎡)")
    unit_type: str = Field(..., description="세대 유형")
    estimated_units: Optional[int] = Field(None, description="예상 세대수")
    estimated_cost: Optional[float] = Field(None, description="예상 사업비")
    project_manager: Optional[str] = Field(None, description="프로젝트 매니저")
    target_completion_date: Optional[datetime] = Field(None, description="목표 완료일")
    notes: Optional[str] = Field(None, description="비고")
    tags: List[str] = Field(default_factory=list, description="태그")


class ProjectUpdateRequest(BaseModel):
    """프로젝트 수정 요청"""
    name: Optional[str] = Field(None, description="프로젝트명")
    status: Optional[ProjectStatus] = Field(None, description="상태")
    estimated_units: Optional[int] = Field(None, description="예상 세대수")
    estimated_cost: Optional[float] = Field(None, description="예상 사업비")
    target_purchase_price: Optional[float] = Field(None, description="목표 매입가")
    project_manager: Optional[str] = Field(None, description="프로젝트 매니저")
    contractor: Optional[str] = Field(None, description="시공사")
    architect: Optional[str] = Field(None, description="설계사")
    target_completion_date: Optional[datetime] = Field(None, description="목표 완료일")
    notes: Optional[str] = Field(None, description="비고")
    tags: Optional[List[str]] = Field(None, description="태그")
