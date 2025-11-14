"""
프로젝트 관리 서비스
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime
from .models import (
    Project, ProjectStatus, ProjectMilestone, ProjectRisk,
    ProjectDocument, ProjectTimeline, ProjectDashboardSummary,
    ProjectCreateRequest, ProjectUpdateRequest, MilestoneStatus
)

logger = logging.getLogger(__name__)


class ProjectService:
    """프로젝트 관리 서비스 클래스"""
    
    def __init__(self):
        # 메모리 저장소 (실제로는 데이터베이스 사용)
        self.projects: Dict[str, Project] = {}
        self.milestones: Dict[str, List[ProjectMilestone]] = {}
        self.risks: Dict[str, List[ProjectRisk]] = {}
        self.documents: Dict[str, List[ProjectDocument]] = {}
        self.timeline: Dict[str, List[ProjectTimeline]] = {}
        
        logger.info("ProjectService 초기화 완료")
    
    # ==================== 프로젝트 CRUD ====================
    
    def create_project(self, request: ProjectCreateRequest, created_by: Optional[str] = None) -> Project:
        """프로젝트 생성"""
        project = Project(
            name=request.name,
            address=request.address,
            land_area=request.land_area,
            unit_type=request.unit_type,
            estimated_units=request.estimated_units,
            estimated_cost=request.estimated_cost,
            project_manager=request.project_manager,
            target_completion_date=request.target_completion_date,
            notes=request.notes,
            tags=request.tags,
            created_by=created_by
        )
        
        self.projects[project.id] = project
        
        # 타임라인 이벤트 생성
        self._add_timeline_event(
            project.id,
            "project_created",
            "프로젝트 생성",
            f"'{project.name}' 프로젝트가 생성되었습니다.",
            created_by
        )
        
        # 기본 마일스톤 생성
        self._create_default_milestones(project.id)
        
        logger.info(f"프로젝트 생성 완료: {project.id} - {project.name}")
        return project
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """프로젝트 조회"""
        return self.projects.get(project_id)
    
    def list_projects(
        self,
        status: Optional[ProjectStatus] = None,
        unit_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Project]:
        """프로젝트 목록 조회"""
        projects = list(self.projects.values())
        
        # 필터링
        if status:
            projects = [p for p in projects if p.status == status]
        
        if unit_type:
            projects = [p for p in projects if p.unit_type == unit_type]
        
        if tags:
            projects = [p for p in projects if any(tag in p.tags for tag in tags)]
        
        # 최신순 정렬
        projects.sort(key=lambda x: x.created_at, reverse=True)
        
        return projects[:limit]
    
    def update_project(
        self,
        project_id: str,
        request: ProjectUpdateRequest,
        updated_by: Optional[str] = None
    ) -> Optional[Project]:
        """프로젝트 수정"""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        # 변경사항 추적
        changes = []
        
        # 수정 가능한 필드 업데이트
        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                old_value = getattr(project, field, None)
                if old_value != value:
                    setattr(project, field, value)
                    changes.append(f"{field}: {old_value} → {value}")
        
        project.updated_at = datetime.now()
        
        # 타임라인 이벤트 생성
        if changes:
            self._add_timeline_event(
                project_id,
                "project_updated",
                "프로젝트 수정",
                f"프로젝트 정보가 수정되었습니다: {', '.join(changes[:3])}",
                updated_by
            )
        
        logger.info(f"프로젝트 수정 완료: {project_id} - {len(changes)}개 필드")
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """프로젝트 삭제"""
        if project_id in self.projects:
            del self.projects[project_id]
            
            # 관련 데이터 삭제
            self.milestones.pop(project_id, None)
            self.risks.pop(project_id, None)
            self.documents.pop(project_id, None)
            self.timeline.pop(project_id, None)
            
            logger.info(f"프로젝트 삭제 완료: {project_id}")
            return True
        return False
    
    # ==================== 마일스톤 관리 ====================
    
    def create_milestone(self, milestone: ProjectMilestone) -> ProjectMilestone:
        """마일스톤 생성"""
        if milestone.project_id not in self.milestones:
            self.milestones[milestone.project_id] = []
        
        self.milestones[milestone.project_id].append(milestone)
        
        logger.info(f"마일스톤 생성: {milestone.name} (프로젝트: {milestone.project_id})")
        return milestone
    
    def get_project_milestones(self, project_id: str) -> List[ProjectMilestone]:
        """프로젝트 마일스톤 목록 조회"""
        return self.milestones.get(project_id, [])
    
    def update_milestone_status(
        self,
        milestone_id: str,
        project_id: str,
        status: MilestoneStatus,
        progress: Optional[int] = None
    ) -> Optional[ProjectMilestone]:
        """마일스톤 상태 업데이트"""
        milestones = self.milestones.get(project_id, [])
        
        for milestone in milestones:
            if milestone.id == milestone_id:
                milestone.status = status
                if progress is not None:
                    milestone.progress_percentage = progress
                milestone.updated_at = datetime.now()
                
                # 시작/완료 시간 자동 설정
                if status == MilestoneStatus.IN_PROGRESS and not milestone.actual_start_date:
                    milestone.actual_start_date = datetime.now()
                elif status == MilestoneStatus.COMPLETED:
                    milestone.actual_end_date = datetime.now()
                    milestone.progress_percentage = 100
                
                # 타임라인 이벤트
                self._add_timeline_event(
                    project_id,
                    "milestone_updated",
                    f"마일스톤 진행: {milestone.name}",
                    f"상태: {status.value}, 진행률: {milestone.progress_percentage}%"
                )
                
                logger.info(f"마일스톤 업데이트: {milestone.name} - {status.value}")
                return milestone
        
        return None
    
    def _create_default_milestones(self, project_id: str):
        """기본 마일스톤 생성"""
        default_milestones = [
            ("토지 입지분석", "LH 매입 적합성 검토 및 리스크 분석"),
            ("사업성 분석", "건축비, 매입가, 수익성 시뮬레이션"),
            ("인허가 신청", "건축 인허가 및 관련 서류 준비"),
            ("설계 진행", "건축 설계 및 LH 기준 검토"),
            ("LH 사전약정", "LH와 사전약정 체결"),
            ("착공", "건축 공사 시작"),
            ("중간 검수", "공정 진행 점검"),
            ("준공검사", "LH 준공검사 준비 및 진행"),
            ("매입 심사", "LH 최종 매입 심사"),
            ("프로젝트 완료", "매입 완료 및 정산")
        ]
        
        for i, (name, description) in enumerate(default_milestones):
            milestone = ProjectMilestone(
                project_id=project_id,
                name=name,
                description=description,
                status=MilestoneStatus.NOT_STARTED if i > 0 else MilestoneStatus.IN_PROGRESS
            )
            self.create_milestone(milestone)
    
    # ==================== 리스크 관리 ====================
    
    def add_risk(self, risk: ProjectRisk) -> ProjectRisk:
        """리스크 추가"""
        if risk.project_id not in self.risks:
            self.risks[risk.project_id] = []
        
        self.risks[risk.project_id].append(risk)
        
        # 타임라인 이벤트
        self._add_timeline_event(
            risk.project_id,
            "risk_identified",
            f"리스크 식별: {risk.title}",
            f"{risk.level.value} - {risk.description[:50]}...",
            risk.identified_by
        )
        
        logger.info(f"리스크 추가: {risk.title} ({risk.level.value})")
        return risk
    
    def get_project_risks(self, project_id: str, active_only: bool = True) -> List[ProjectRisk]:
        """프로젝트 리스크 목록 조회"""
        risks = self.risks.get(project_id, [])
        
        if active_only:
            risks = [r for r in risks if r.status == "활성"]
        
        # 레벨별 정렬 (높은 순)
        risk_order = {"심각": 0, "높음": 1, "보통": 2, "낮음": 3}
        risks.sort(key=lambda x: risk_order.get(x.level.value, 999))
        
        return risks
    
    # ==================== 문서 관리 ====================
    
    def add_document(self, document: ProjectDocument) -> ProjectDocument:
        """문서 추가"""
        if document.project_id not in self.documents:
            self.documents[document.project_id] = []
        
        self.documents[document.project_id].append(document)
        
        # 타임라인 이벤트
        self._add_timeline_event(
            document.project_id,
            "document_uploaded",
            f"문서 업로드: {document.name}",
            f"{document.document_type} - {document.version}",
            document.uploaded_by
        )
        
        logger.info(f"문서 추가: {document.name}")
        return document
    
    def get_project_documents(self, project_id: str, document_type: Optional[str] = None) -> List[ProjectDocument]:
        """프로젝트 문서 목록 조회"""
        documents = self.documents.get(project_id, [])
        
        if document_type:
            documents = [d for d in documents if d.document_type == document_type]
        
        # 최신순 정렬
        documents.sort(key=lambda x: x.uploaded_at, reverse=True)
        
        return documents
    
    # ==================== 타임라인 ====================
    
    def _add_timeline_event(
        self,
        project_id: str,
        event_type: str,
        title: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """타임라인 이벤트 추가"""
        if project_id not in self.timeline:
            self.timeline[project_id] = []
        
        event = ProjectTimeline(
            project_id=project_id,
            event_type=event_type,
            title=title,
            description=description,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        self.timeline[project_id].append(event)
    
    def get_project_timeline(self, project_id: str, limit: int = 50) -> List[ProjectTimeline]:
        """프로젝트 타임라인 조회"""
        events = self.timeline.get(project_id, [])
        
        # 최신순 정렬
        events.sort(key=lambda x: x.occurred_at, reverse=True)
        
        return events[:limit]
    
    # ==================== 대시보드 및 통계 ====================
    
    def get_dashboard_summary(self) -> ProjectDashboardSummary:
        """대시보드 요약 정보"""
        all_projects = list(self.projects.values())
        
        # 기본 통계
        total = len(all_projects)
        active = len([p for p in all_projects if p.status not in [ProjectStatus.COMPLETED, ProjectStatus.CANCELLED]])
        completed = len([p for p in all_projects if p.status == ProjectStatus.COMPLETED])
        
        # 상태별 통계
        by_status = {}
        for status in ProjectStatus:
            count = len([p for p in all_projects if p.status == status])
            if count > 0:
                by_status[status.value] = count
        
        # 유형별 통계
        by_unit_type = {}
        for project in all_projects:
            by_unit_type[project.unit_type] = by_unit_type.get(project.unit_type, 0) + 1
        
        # 재무 통계
        total_cost = sum(p.estimated_cost for p in all_projects if p.estimated_cost)
        total_units = sum(p.estimated_units for p in all_projects if p.estimated_units)
        
        # 리스크 통계
        high_risk_count = 0
        for project in all_projects:
            project_risks = self.get_project_risks(project.id)
            if any(r.level.value in ["높음", "심각"] for r in project_risks):
                high_risk_count += 1
        
        # 지연된 마일스톤
        delayed_count = 0
        for project_milestones in self.milestones.values():
            delayed_count += len([m for m in project_milestones if m.status == MilestoneStatus.DELAYED])
        
        # 최근 활동
        all_events = []
        for events in self.timeline.values():
            all_events.extend(events)
        all_events.sort(key=lambda x: x.occurred_at, reverse=True)
        recent_activities = all_events[:10]
        
        return ProjectDashboardSummary(
            total_projects=total,
            active_projects=active,
            completed_projects=completed,
            by_status=by_status,
            by_unit_type=by_unit_type,
            total_estimated_cost=total_cost,
            total_units=total_units,
            high_risk_count=high_risk_count,
            delayed_milestones=delayed_count,
            recent_activities=recent_activities
        )
    
    def get_project_progress(self, project_id: str) -> Dict:
        """프로젝트 진행률 계산"""
        milestones = self.get_project_milestones(project_id)
        
        if not milestones:
            return {"progress": 0, "total_milestones": 0}
        
        total = len(milestones)
        completed = len([m for m in milestones if m.status == MilestoneStatus.COMPLETED])
        in_progress = len([m for m in milestones if m.status == MilestoneStatus.IN_PROGRESS])
        delayed = len([m for m in milestones if m.status == MilestoneStatus.DELAYED])
        
        # 가중 진행률
        progress = (completed * 100 + in_progress * 50) / (total * 100) * 100
        
        return {
            "progress": round(progress, 1),
            "total_milestones": total,
            "completed": completed,
            "in_progress": in_progress,
            "delayed": delayed,
            "not_started": total - completed - in_progress - delayed
        }


# 전역 서비스 인스턴스
_project_service = None

def get_project_service() -> ProjectService:
    """프로젝트 서비스 싱글톤"""
    global _project_service
    if _project_service is None:
        _project_service = ProjectService()
    return _project_service
