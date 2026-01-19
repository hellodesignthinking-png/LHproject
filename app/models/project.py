"""
Project Management System
=========================

ZeroSite Decision OS - 프로젝트 관리 시스템
목적: 다중 프로젝트 관리, 진행률 추적, 이력 관리

Author: ZeroSite Team
Date: 2026-01-12
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


# ========================================
# Enums
# ========================================

class ProjectStatus(str, Enum):
    """프로젝트 상태"""
    DRAFT = "DRAFT"  # 작성 중
    M1_PENDING = "M1_PENDING"  # M1 진행 중
    M1_FROZEN = "M1_FROZEN"  # M1 동결 완료
    M2_PENDING = "M2_PENDING"  # M2 진행 중
    M3_PENDING = "M3_PENDING"  # M3 진행 중
    M4_PENDING = "M4_PENDING"  # M4 진행 중
    M5_PENDING = "M5_PENDING"  # M5 진행 중
    M7_PENDING = "M7_PENDING"  # M7 진행 중
    M6_PENDING = "M6_PENDING"  # M6 진행 중 (최종 판단)
    COMPLETED = "COMPLETED"  # 완료
    ARCHIVED = "ARCHIVED"  # 보관


class ModuleStatus(str, Enum):
    """모듈 상태"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FROZEN = "FROZEN"  # M1 전용
    FAILED = "FAILED"


class UserRole(str, Enum):
    """사용자 역할"""
    ADMIN = "ADMIN"  # 관리자
    USER = "USER"  # 일반 사용자
    VIEWER = "VIEWER"  # 열람자 (LH 실무자)


# ========================================
# Data Models
# ========================================

class ModuleProgress(BaseModel):
    """모듈 진행 상태"""
    module_name: str = Field(..., description="모듈명 (M1~M7)")
    status: ModuleStatus = Field(default=ModuleStatus.NOT_STARTED)
    progress_percent: int = Field(default=0, ge=0, le=100)
    context_id: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class Project(BaseModel):
    """프로젝트 모델"""
    project_id: str = Field(..., description="프로젝트 고유 ID")
    project_name: str = Field(..., description="프로젝트명")
    land_address: Optional[str] = Field(None, description="토지 지번")
    
    # 상태 관리
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT)
    overall_progress: int = Field(default=0, ge=0, le=100, description="전체 진행률 (%)")
    
    # 모듈 진행 상태
    modules: List[ModuleProgress] = Field(default_factory=list)
    
    # M1 Context ID (Single Source of Truth)
    m1_context_id: Optional[str] = None
    
    # M6 최종 판단
    final_decision: Optional[str] = None  # GO/CONDITIONAL/NO-GO
    lh_pass_probability: Optional[str] = None
    
    # 메타 정보
    created_by: str = Field(..., description="생성자 ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 보고서 URL
    report_pdf_url: Optional[str] = None
    report_html_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "proj_20260112_abc123",
                "project_name": "강남구 역삼동 신축매입임대 검토",
                "land_address": "서울특별시 강남구 역삼동 XXX-X",
                "status": "M1_FROZEN",
                "overall_progress": 35,
                "modules": [
                    {
                        "module_name": "M1",
                        "status": "FROZEN",
                        "progress_percent": 100,
                        "context_id": "ctx_abc123"
                    }
                ],
                "created_by": "user_001",
                "created_at": "2026-01-12T10:00:00Z"
            }
        }


class User(BaseModel):
    """사용자 모델"""
    user_id: str = Field(..., description="사용자 고유 ID")
    username: str = Field(..., description="사용자명")
    email: str = Field(..., description="이메일")
    role: UserRole = Field(default=UserRole.USER)
    
    # 프로젝트 제한
    max_projects: int = Field(default=10, description="최대 프로젝트 수")
    current_projects: int = Field(default=0, description="현재 프로젝트 수")
    
    # 메타 정보
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_001",
                "username": "김철수",
                "email": "kim@example.com",
                "role": "USER",
                "max_projects": 10,
                "current_projects": 3
            }
        }


# ========================================
# Request/Response Models
# ========================================

class CreateProjectRequest(BaseModel):
    """프로젝트 생성 요청"""
    project_name: str = Field(..., description="프로젝트명", min_length=1, max_length=200)
    land_address: Optional[str] = Field(None, description="토지 지번")


class UpdateProjectRequest(BaseModel):
    """프로젝트 업데이트 요청"""
    project_name: Optional[str] = None
    land_address: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectListResponse(BaseModel):
    """프로젝트 목록 응답"""
    total: int = Field(..., description="전체 프로젝트 수")
    projects: List[Project] = Field(..., description="프로젝트 목록")


class ProjectProgressResponse(BaseModel):
    """프로젝트 진행률 응답"""
    project_id: str
    overall_progress: int
    modules: List[ModuleProgress]
    next_module: Optional[str] = None
    is_completed: bool = False


# ========================================
# In-Memory Storage (Demo)
# ========================================

class ProjectStore:
    """프로젝트 저장소 (In-Memory)"""
    
    def __init__(self):
        self.projects: dict[str, Project] = {}
        self.users: dict[str, User] = {}
        
        # Demo 사용자 추가
        demo_user = User(
            user_id="demo_user_001",
            username="데모 사용자",
            email="demo@zerosite.ai",
            role=UserRole.USER,
            max_projects=10,
            current_projects=0
        )
        self.users[demo_user.user_id] = demo_user
    
    def create_project(self, project: Project) -> Project:
        """프로젝트 생성"""
        self.projects[project.project_id] = project
        
        # 사용자 프로젝트 수 증가
        if project.created_by in self.users:
            self.users[project.created_by].current_projects += 1
        
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """프로젝트 조회"""
        return self.projects.get(project_id)
    
    def list_projects(self, user_id: Optional[str] = None) -> List[Project]:
        """프로젝트 목록 조회"""
        if user_id:
            return [p for p in self.projects.values() if p.created_by == user_id]
        return list(self.projects.values())
    
    def update_project(self, project_id: str, updates: dict) -> Optional[Project]:
        """프로젝트 업데이트"""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        # 업데이트
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.updated_at = datetime.utcnow()
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """프로젝트 삭제"""
        project = self.projects.get(project_id)
        if not project:
            return False
        
        # 사용자 프로젝트 수 감소
        if project.created_by in self.users:
            self.users[project.created_by].current_projects -= 1
        
        del self.projects[project_id]
        return True
    
    def update_module_progress(
        self,
        project_id: str,
        module_name: str,
        status: ModuleStatus,
        progress: int,
        context_id: Optional[str] = None
    ) -> Optional[Project]:
        """모듈 진행 상태 업데이트"""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        # 모듈 찾기 또는 생성
        module = next((m for m in project.modules if m.module_name == module_name), None)
        if not module:
            module = ModuleProgress(module_name=module_name)
            project.modules.append(module)
        
        # 상태 업데이트
        module.status = status
        module.progress_percent = progress
        if context_id:
            module.context_id = context_id
        
        if status == ModuleStatus.COMPLETED or status == ModuleStatus.FROZEN:
            module.completed_at = datetime.utcnow()
        
        # M1 Context ID 저장
        if module_name == "M1" and context_id:
            project.m1_context_id = context_id
        
        # 전체 진행률 계산
        project.overall_progress = self._calculate_overall_progress(project)
        
        # 프로젝트 상태 업데이트
        project.status = self._determine_project_status(project)
        
        project.updated_at = datetime.utcnow()
        return project
    
    def _calculate_overall_progress(self, project: Project) -> int:
        """전체 진행률 계산"""
        if not project.modules:
            return 0
        
        # M1~M7 각각 가중치 (M1: 15%, M2~M5: 각 12.5%, M6: 20%, M7: 15%)
        weights = {
            "M1": 15,
            "M2": 12.5,
            "M3": 12.5,
            "M4": 12.5,
            "M5": 12.5,
            "M6": 20,
            "M7": 15
        }
        
        total_progress = 0
        for module in project.modules:
            weight = weights.get(module.module_name, 0)
            total_progress += (module.progress_percent / 100) * weight
        
        return int(total_progress)
    
    def _determine_project_status(self, project: Project) -> ProjectStatus:
        """프로젝트 상태 결정"""
        module_statuses = {m.module_name: m.status for m in project.modules}
        
        # M1 FROZEN 확인
        if module_statuses.get("M1") == ModuleStatus.FROZEN:
            # M6 완료 확인
            if module_statuses.get("M6") == ModuleStatus.COMPLETED:
                return ProjectStatus.COMPLETED
            
            # 진행 중인 모듈 확인
            for module_name in ["M7", "M6", "M5", "M4", "M3", "M2"]:
                if module_statuses.get(module_name) == ModuleStatus.IN_PROGRESS:
                    return ProjectStatus[f"{module_name}_PENDING"]
            
            # M2부터 시작 (M1 완료 후)
            return ProjectStatus.M2_PENDING
        
        # M1 진행 중
        if module_statuses.get("M1") == ModuleStatus.IN_PROGRESS:
            return ProjectStatus.M1_PENDING
        
        return ProjectStatus.DRAFT


# Singleton instance
_project_store = None


def get_project_store() -> ProjectStore:
    """ProjectStore 싱글톤 인스턴스"""
    global _project_store
    if _project_store is None:
        _project_store = ProjectStore()
    return _project_store
