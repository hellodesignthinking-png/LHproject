"""
Project Management API
======================

ZeroSite Decision OS - 프로젝트 관리 API
목적: 프로젝트 CRUD, 진행률 추적, 이력 조회

Author: ZeroSite Team
Date: 2026-01-12
"""

from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.project import (
    Project,
    ProjectStore,
    get_project_store,
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectListResponse,
    ProjectProgressResponse,
    ProjectStatus,
    ModuleStatus,
    ModuleProgress
)

# ========================================
# Router 초기화
# ========================================
router = APIRouter(
    prefix="/api/projects",
    tags=["Project Management"]
)

# ========================================
# Dependency
# ========================================

def get_current_user_id() -> str:
    """현재 사용자 ID 조회 (Demo: 고정값)"""
    # TODO: 실제 인증 시스템 연동
    return "demo_user_001"


# ========================================
# API Endpoints
# ========================================

@router.post(
    "",
    response_model=Project,
    summary="프로젝트 생성",
    description="새로운 분석 프로젝트를 생성합니다."
)
async def create_project(
    request: CreateProjectRequest,
    user_id: str = Depends(get_current_user_id)
):
    """프로젝트 생성"""
    
    store = get_project_store()
    
    # 프로젝트 ID 생성
    project_id = f"proj_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    
    # 프로젝트 객체 생성
    project = Project(
        project_id=project_id,
        project_name=request.project_name,
        land_address=request.land_address,
        created_by=user_id,
        modules=[
            ModuleProgress(module_name="M1", status=ModuleStatus.NOT_STARTED),
            ModuleProgress(module_name="M2", status=ModuleStatus.NOT_STARTED),
            ModuleProgress(module_name="M3", status=ModuleStatus.NOT_STARTED),
            ModuleProgress(module_name="M4", status=ModuleStatus.NOT_STARTED),
            ModuleProgress(module_name="M5", status=ModuleStatus.NOT_STARTED),
            ModuleProgress(module_name="M6", status=ModuleStatus.NOT_STARTED),
            ModuleProgress(module_name="M7", status=ModuleStatus.NOT_STARTED),
        ]
    )
    
    # 저장
    created_project = store.create_project(project)
    
    return created_project


@router.get(
    "",
    response_model=ProjectListResponse,
    summary="프로젝트 목록 조회",
    description="사용자의 프로젝트 목록을 조회합니다."
)
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    status: Optional[ProjectStatus] = Query(None, description="필터: 프로젝트 상태"),
    limit: int = Query(50, ge=1, le=100, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋")
):
    """프로젝트 목록 조회"""
    
    store = get_project_store()
    
    # 전체 프로젝트 조회
    all_projects = store.list_projects(user_id=user_id)
    
    # 상태 필터
    if status:
        all_projects = [p for p in all_projects if p.status == status]
    
    # 정렬 (최신순)
    all_projects.sort(key=lambda x: x.updated_at, reverse=True)
    
    # 페이징
    paginated_projects = all_projects[offset:offset + limit]
    
    return ProjectListResponse(
        total=len(all_projects),
        projects=paginated_projects
    )


@router.get(
    "/{project_id}",
    response_model=Project,
    summary="프로젝트 상세 조회",
    description="특정 프로젝트의 상세 정보를 조회합니다."
)
async def get_project(
    project_id: str = Path(..., description="프로젝트 ID"),
    user_id: str = Depends(get_current_user_id)
):
    """프로젝트 상세 조회"""
    
    store = get_project_store()
    project = store.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 권한 확인 (자신의 프로젝트만 조회 가능)
    if project.created_by != user_id:
        raise HTTPException(status_code=403, detail="프로젝트 조회 권한이 없습니다.")
    
    return project


@router.put(
    "/{project_id}",
    response_model=Project,
    summary="프로젝트 업데이트",
    description="프로젝트 정보를 업데이트합니다."
)
async def update_project(
    project_id: str = Path(..., description="프로젝트 ID"),
    request: UpdateProjectRequest = ...,
    user_id: str = Depends(get_current_user_id)
):
    """프로젝트 업데이트"""
    
    store = get_project_store()
    project = store.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 권한 확인
    if project.created_by != user_id:
        raise HTTPException(status_code=403, detail="프로젝트 수정 권한이 없습니다.")
    
    # 업데이트 데이터 준비
    updates = {}
    if request.project_name:
        updates["project_name"] = request.project_name
    if request.land_address:
        updates["land_address"] = request.land_address
    if request.status:
        updates["status"] = request.status
    
    # 업데이트 실행
    updated_project = store.update_project(project_id, updates)
    
    return updated_project


@router.delete(
    "/{project_id}",
    summary="프로젝트 삭제",
    description="프로젝트를 삭제합니다."
)
async def delete_project(
    project_id: str = Path(..., description="프로젝트 ID"),
    user_id: str = Depends(get_current_user_id)
):
    """프로젝트 삭제"""
    
    store = get_project_store()
    project = store.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 권한 확인
    if project.created_by != user_id:
        raise HTTPException(status_code=403, detail="프로젝트 삭제 권한이 없습니다.")
    
    # 삭제
    success = store.delete_project(project_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="프로젝트 삭제 실패")
    
    return {"message": "프로젝트가 삭제되었습니다.", "project_id": project_id}


@router.get(
    "/{project_id}/progress",
    response_model=ProjectProgressResponse,
    summary="프로젝트 진행률 조회",
    description="프로젝트의 현재 진행률과 모듈별 상태를 조회합니다."
)
async def get_project_progress(
    project_id: str = Path(..., description="프로젝트 ID"),
    user_id: str = Depends(get_current_user_id)
):
    """프로젝트 진행률 조회"""
    
    store = get_project_store()
    project = store.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 권한 확인
    if project.created_by != user_id:
        raise HTTPException(status_code=403, detail="프로젝트 조회 권한이 없습니다.")
    
    # 다음 진행 모듈 결정
    next_module = None
    module_order = ["M1", "M2", "M3", "M4", "M5", "M7", "M6"]
    
    for module_name in module_order:
        module = next((m for m in project.modules if m.module_name == module_name), None)
        if module and module.status in [ModuleStatus.NOT_STARTED, ModuleStatus.IN_PROGRESS]:
            next_module = module_name
            break
    
    # 완료 여부
    is_completed = all(
        m.status in [ModuleStatus.COMPLETED, ModuleStatus.FROZEN]
        for m in project.modules
    )
    
    return ProjectProgressResponse(
        project_id=project.project_id,
        overall_progress=project.overall_progress,
        modules=project.modules,
        next_module=next_module,
        is_completed=is_completed
    )


@router.post(
    "/{project_id}/modules/{module_name}/progress",
    response_model=Project,
    summary="모듈 진행 상태 업데이트",
    description="특정 모듈의 진행 상태를 업데이트합니다."
)
async def update_module_progress(
    project_id: str = Path(..., description="프로젝트 ID"),
    module_name: str = Path(..., description="모듈명 (M1~M7)"),
    status: ModuleStatus = Query(..., description="모듈 상태"),
    progress: int = Query(..., ge=0, le=100, description="진행률 (%)"),
    context_id: Optional[str] = Query(None, description="Context ID"),
    user_id: str = Depends(get_current_user_id)
):
    """모듈 진행 상태 업데이트"""
    
    store = get_project_store()
    project = store.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 권한 확인
    if project.created_by != user_id:
        raise HTTPException(status_code=403, detail="프로젝트 수정 권한이 없습니다.")
    
    # 모듈명 검증
    if module_name not in ["M1", "M2", "M3", "M4", "M5", "M6", "M7"]:
        raise HTTPException(status_code=400, detail="유효하지 않은 모듈명입니다.")
    
    # 업데이트
    updated_project = store.update_module_progress(
        project_id=project_id,
        module_name=module_name,
        status=status,
        progress=progress,
        context_id=context_id
    )
    
    if not updated_project:
        raise HTTPException(status_code=500, detail="모듈 진행 상태 업데이트 실패")
    
    return updated_project


@router.get(
    "/{project_id}/reports",
    summary="프로젝트 보고서 URL 조회",
    description="프로젝트의 통합 보고서 URL을 조회합니다."
)
async def get_project_reports(
    project_id: str = Path(..., description="프로젝트 ID"),
    user_id: str = Depends(get_current_user_id)
):
    """프로젝트 보고서 URL 조회"""
    
    store = get_project_store()
    project = store.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # 권한 확인
    if project.created_by != user_id:
        raise HTTPException(status_code=403, detail="프로젝트 조회 권한이 없습니다.")
    
    # M1 Context ID 필요
    if not project.m1_context_id:
        raise HTTPException(
            status_code=400,
            detail="M1 모듈이 완료되지 않아 보고서를 생성할 수 없습니다."
        )
    
    context_id = project.m1_context_id
    
    return {
        "project_id": project.project_id,
        "m1_context_id": context_id,
        "reports": {
            "integrated_json": f"/api/reports/integrated/{context_id}",
            "integrated_html": f"/api/reports/integrated/{context_id}/html",
            "integrated_pdf": f"/api/reports/integrated/{context_id}/pdf",
            "m6_dashboard": f"/static/m6_dashboard.html?project_id={project_id}&context_id={context_id}"
        }
    }
