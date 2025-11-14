"""
프로젝트 관리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.modules.project_management import (
    Project, ProjectStatus, ProjectMilestone, 
    ProjectCreateRequest, ProjectUpdateRequest
)
from app.modules.project_management.models import (
    ProjectRisk, ProjectDocument, ProjectDashboardSummary,
    MilestoneStatus, RiskLevel
)
from app.modules.project_management.service import get_project_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["Project Management"])

# 서비스 인스턴스
project_service = get_project_service()


# ==================== 프로젝트 CRUD ====================

@router.post("", response_model=Project, status_code=201)
async def create_project(request: ProjectCreateRequest, created_by: Optional[str] = None):
    """
    새 프로젝트 생성
    
    - **name**: 프로젝트명
    - **address**: 사업지 주소
    - **land_area**: 토지 면적(㎡)
    - **unit_type**: 세대 유형 (청년형/신혼부부형/고령자형)
    """
    try:
        logger.info(f"프로젝트 생성 요청: {request.name}")
        project = project_service.create_project(request, created_by)
        return project
    except Exception as e:
        logger.error(f"프로젝트 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[Project])
async def list_projects(
    status: Optional[ProjectStatus] = None,
    unit_type: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = 100
):
    """
    프로젝트 목록 조회
    
    - **status**: 상태 필터
    - **unit_type**: 세대 유형 필터
    - **tags**: 태그 필터
    - **limit**: 최대 조회 개수
    """
    try:
        projects = project_service.list_projects(status, unit_type, tags, limit)
        logger.info(f"프로젝트 목록 조회: {len(projects)}건")
        return projects
    except Exception as e:
        logger.error(f"프로젝트 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """
    프로젝트 상세 조회
    
    - **project_id**: 프로젝트 ID
    """
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    updated_by: Optional[str] = None
):
    """
    프로젝트 수정
    
    - **project_id**: 프로젝트 ID
    - 수정 가능한 필드는 요청 body 참조
    """
    try:
        project = project_service.update_project(project_id, request, updated_by)
        if not project:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
        
        logger.info(f"프로젝트 수정 완료: {project_id}")
        return project
    except Exception as e:
        logger.error(f"프로젝트 수정 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    프로젝트 삭제
    
    - **project_id**: 프로젝트 ID
    """
    success = project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    return {"status": "success", "message": "프로젝트가 삭제되었습니다."}


# ==================== 마일스톤 관리 ====================

@router.get("/{project_id}/milestones", response_model=List[ProjectMilestone])
async def get_project_milestones(project_id: str):
    """
    프로젝트 마일스톤 목록 조회
    
    - **project_id**: 프로젝트 ID
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    milestones = project_service.get_project_milestones(project_id)
    return milestones


@router.post("/{project_id}/milestones", response_model=ProjectMilestone, status_code=201)
async def create_milestone(project_id: str, milestone: ProjectMilestone):
    """
    새 마일스톤 생성
    
    - **project_id**: 프로젝트 ID
    - 마일스톤 정보는 요청 body 참조
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # project_id 강제 설정
    milestone.project_id = project_id
    
    try:
        created = project_service.create_milestone(milestone)
        return created
    except Exception as e:
        logger.error(f"마일스톤 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{project_id}/milestones/{milestone_id}")
async def update_milestone_status(
    project_id: str,
    milestone_id: str,
    status: MilestoneStatus,
    progress: Optional[int] = None
):
    """
    마일스톤 상태 업데이트
    
    - **project_id**: 프로젝트 ID
    - **milestone_id**: 마일스톤 ID
    - **status**: 새로운 상태
    - **progress**: 진행률 (0-100)
    """
    milestone = project_service.update_milestone_status(
        milestone_id, project_id, status, progress
    )
    
    if not milestone:
        raise HTTPException(status_code=404, detail="마일스톤을 찾을 수 없습니다.")
    
    return {
        "status": "success",
        "milestone": milestone
    }


@router.get("/{project_id}/progress")
async def get_project_progress(project_id: str):
    """
    프로젝트 진행률 조회
    
    - **project_id**: 프로젝트 ID
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    progress = project_service.get_project_progress(project_id)
    return {
        "project_id": project_id,
        "project_name": project.name,
        **progress
    }


# ==================== 리스크 관리 ====================

@router.get("/{project_id}/risks", response_model=List[ProjectRisk])
async def get_project_risks(project_id: str, active_only: bool = True):
    """
    프로젝트 리스크 목록 조회
    
    - **project_id**: 프로젝트 ID
    - **active_only**: 활성 리스크만 조회 (기본값: True)
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    risks = project_service.get_project_risks(project_id, active_only)
    return risks


@router.post("/{project_id}/risks", response_model=ProjectRisk, status_code=201)
async def add_project_risk(project_id: str, risk: ProjectRisk):
    """
    프로젝트 리스크 추가
    
    - **project_id**: 프로젝트 ID
    - 리스크 정보는 요청 body 참조
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # project_id 강제 설정
    risk.project_id = project_id
    
    try:
        added = project_service.add_risk(risk)
        return added
    except Exception as e:
        logger.error(f"리스크 추가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 문서 관리 ====================

@router.get("/{project_id}/documents", response_model=List[ProjectDocument])
async def get_project_documents(
    project_id: str,
    document_type: Optional[str] = None
):
    """
    프로젝트 문서 목록 조회
    
    - **project_id**: 프로젝트 ID
    - **document_type**: 문서 유형 필터 (선택)
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    documents = project_service.get_project_documents(project_id, document_type)
    return documents


@router.post("/{project_id}/documents", response_model=ProjectDocument, status_code=201)
async def add_project_document(project_id: str, document: ProjectDocument):
    """
    프로젝트 문서 추가
    
    - **project_id**: 프로젝트 ID
    - 문서 정보는 요청 body 참조
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    # project_id 강제 설정
    document.project_id = project_id
    
    try:
        added = project_service.add_document(document)
        return added
    except Exception as e:
        logger.error(f"문서 추가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 타임라인 ====================

@router.get("/{project_id}/timeline")
async def get_project_timeline(project_id: str, limit: int = 50):
    """
    프로젝트 타임라인 조회
    
    - **project_id**: 프로젝트 ID
    - **limit**: 최대 조회 개수
    """
    # 프로젝트 존재 확인
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    timeline = project_service.get_project_timeline(project_id, limit)
    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_events": len(timeline),
        "events": timeline
    }


# ==================== 대시보드 ====================

@router.get("/dashboard/summary", response_model=ProjectDashboardSummary)
async def get_dashboard_summary():
    """
    대시보드 요약 정보 조회
    
    전체 프로젝트의 통계 및 현황 요약
    """
    try:
        summary = project_service.get_dashboard_summary()
        return summary
    except Exception as e:
        logger.error(f"대시보드 요약 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 유틸리티 ====================

@router.get("/statuses/list")
async def list_project_statuses():
    """
    사용 가능한 프로젝트 상태 목록
    """
    return {
        "statuses": [status.value for status in ProjectStatus]
    }


@router.get("/unit-types/list")
async def list_unit_types():
    """
    사용 가능한 세대 유형 목록
    """
    return {
        "unit_types": ["청년형", "신혼부부형", "고령자형", "혼합형"]
    }
