"""
ZeroSite Analysis Status Tracking
==================================

Tracks verification and execution status for M1-M6 modules.
Ensures human-verified workflow with proper gates.

Author: ZeroSite UX Redesign Team
Date: 2026-01-11
Version: 3.0 (Human-Verified Mode)
"""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ModuleStatus(str, Enum):
    """Module execution status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"  # 사용자 확인 완료
    ERROR = "error"
    INVALID = "invalid"  # Context 변경으로 무효화


class VerificationStatus(str, Enum):
    """User verification status"""
    PENDING = "pending"  # 확인 대기
    APPROVED = "approved"  # 사용자 승인
    REJECTED = "rejected"  # 사용자 거부 (재수집 필요)


class ModuleInfo(BaseModel):
    """Individual module status"""
    module_name: str  # M1, M2, M3, M4, M5, M6
    status: ModuleStatus = ModuleStatus.NOT_STARTED
    verification_status: Optional[VerificationStatus] = None
    executed_at: Optional[str] = None  # ISO 8601
    verified_at: Optional[str] = None  # ISO 8601
    verified_by: Optional[str] = None  # User ID
    error_message: Optional[str] = None
    context_id: Optional[str] = None  # 실행 시 사용된 Context ID
    
    # 실행 결과 메타데이터
    result_summary: Optional[Dict] = None  # 주요 결과 요약


class AnalysisStatus(BaseModel):
    """
    Complete analysis status for a project
    
    Tracks:
    - Each module's execution and verification status
    - Context version and validity
    - User confirmation flow
    - Gate control logic
    """
    
    # Project identification
    project_id: str
    project_name: str
    address: str
    parcel_id: Optional[str] = None
    
    # Context tracking
    current_context_id: str
    context_created_at: str
    context_version: str = "2.0"
    
    # Module statuses
    m1_status: ModuleInfo = Field(default_factory=lambda: ModuleInfo(module_name="M1"))
    m2_status: ModuleInfo = Field(default_factory=lambda: ModuleInfo(module_name="M2"))
    m3_status: ModuleInfo = Field(default_factory=lambda: ModuleInfo(module_name="M3"))
    m4_status: ModuleInfo = Field(default_factory=lambda: ModuleInfo(module_name="M4"))
    m5_status: ModuleInfo = Field(default_factory=lambda: ModuleInfo(module_name="M5"))
    m6_status: ModuleInfo = Field(default_factory=lambda: ModuleInfo(module_name="M6"))
    
    # Overall status
    created_at: str
    updated_at: str
    last_activity: str
    
    # Access control
    is_locked: bool = False  # True when analysis is finalized
    locked_at: Optional[str] = None
    locked_by: Optional[str] = None
    
    def get_module_status(self, module_name: str) -> ModuleInfo:
        """Get status for specific module"""
        module_map = {
            "M1": self.m1_status,
            "M2": self.m2_status,
            "M3": self.m3_status,
            "M4": self.m4_status,
            "M5": self.m5_status,
            "M6": self.m6_status,
        }
        return module_map.get(module_name)
    
    def can_execute_module(self, module_name: str) -> tuple[bool, str]:
        """
        Check if module can be executed
        
        Returns:
            (can_execute: bool, reason: str)
        """
        
        # M1은 항상 실행 가능
        if module_name == "M1":
            return True, "M1 can always execute"
        
        # M2는 M1 verified 필요
        if module_name == "M2":
            if self.m1_status.verification_status != VerificationStatus.APPROVED:
                return False, "M1 must be verified before M2"
            return True, "M1 verified, M2 can execute"
        
        # M3는 M2 completed 필요
        if module_name == "M3":
            if self.m2_status.status != ModuleStatus.COMPLETED:
                return False, "M2 must be completed before M3"
            return True, "M2 completed, M3 can execute"
        
        # M4는 M3 completed 필요
        if module_name == "M4":
            if self.m3_status.status != ModuleStatus.COMPLETED:
                return False, "M3 must be completed before M4"
            return True, "M3 completed, M4 can execute"
        
        # M5는 M4 completed 필요
        if module_name == "M5":
            if self.m4_status.status != ModuleStatus.COMPLETED:
                return False, "M4 must be completed before M5"
            return True, "M4 completed, M5 can execute"
        
        # M6는 M5 completed 필요
        if module_name == "M6":
            if self.m5_status.status != ModuleStatus.COMPLETED:
                return False, "M5 must be completed before M6"
            return True, "M5 completed, M6 can execute"
        
        return False, f"Unknown module: {module_name}"
    
    def invalidate_downstream_modules(self, from_module: str):
        """
        Invalidate all modules after the specified one
        
        Example: If M1 is re-executed, M2-M6 become invalid
        """
        module_order = ["M1", "M2", "M3", "M4", "M5", "M6"]
        
        if from_module not in module_order:
            return
        
        start_idx = module_order.index(from_module) + 1
        
        for module in module_order[start_idx:]:
            module_status = self.get_module_status(module)
            if module_status:
                module_status.status = ModuleStatus.INVALID
                module_status.verification_status = None
                module_status.error_message = f"Invalidated due to {from_module} change"
    
    def get_progress_percentage(self) -> int:
        """Calculate overall progress (0-100)"""
        modules = [self.m1_status, self.m2_status, self.m3_status, 
                   self.m4_status, self.m5_status, self.m6_status]
        
        completed = sum(1 for m in modules if m.status == ModuleStatus.COMPLETED)
        return int((completed / len(modules)) * 100)
    
    def get_next_action(self) -> str:
        """Get next recommended action"""
        
        if self.m1_status.status != ModuleStatus.COMPLETED:
            return "Execute M1: Collect land information"
        
        if self.m1_status.verification_status != VerificationStatus.APPROVED:
            return "Verify M1: Confirm land data before proceeding"
        
        if self.m2_status.status != ModuleStatus.COMPLETED:
            return "Execute M2: Land appraisal and market analysis"
        
        if self.m3_status.status != ModuleStatus.COMPLETED:
            return "Execute M3: Housing type selection"
        
        if self.m4_status.status != ModuleStatus.COMPLETED:
            return "Execute M4: Building capacity calculation"
        
        if self.m5_status.status != ModuleStatus.COMPLETED:
            return "Execute M5: Feasibility analysis"
        
        if self.m6_status.status != ModuleStatus.COMPLETED:
            return "Execute M6: LH comprehensive review"
        
        return "Analysis complete - ready for final report"


# ============================================================================
# Status Storage (In-Memory + Redis)
# ============================================================================

class AnalysisStatusStorage:
    """Storage for analysis status tracking"""
    
    def __init__(self):
        self._storage: Dict[str, AnalysisStatus] = {}
    
    def create_status(
        self,
        project_id: str,
        project_name: str,
        address: str,
        context_id: str,
        parcel_id: Optional[str] = None
    ) -> AnalysisStatus:
        """Create new analysis status"""
        now = datetime.now().isoformat()
        
        status = AnalysisStatus(
            project_id=project_id,
            project_name=project_name,
            address=address,
            parcel_id=parcel_id,
            current_context_id=context_id,
            context_created_at=now,
            created_at=now,
            updated_at=now,
            last_activity=now
        )
        
        self._storage[project_id] = status
        return status
    
    def get_status(self, project_id: str) -> Optional[AnalysisStatus]:
        """Get analysis status by project ID"""
        return self._storage.get(project_id)
    
    def update_module_status(
        self,
        project_id: str,
        module_name: str,
        status: ModuleStatus,
        context_id: Optional[str] = None,
        result_summary: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """Update individual module status"""
        analysis_status = self.get_status(project_id)
        if not analysis_status:
            raise ValueError(f"Analysis status not found: {project_id}")
        
        module_status = analysis_status.get_module_status(module_name)
        if not module_status:
            raise ValueError(f"Unknown module: {module_name}")
        
        module_status.status = status
        module_status.executed_at = datetime.now().isoformat()
        
        if context_id:
            module_status.context_id = context_id
        
        if result_summary:
            module_status.result_summary = result_summary
        
        if error_message:
            module_status.error_message = error_message
        
        analysis_status.updated_at = datetime.now().isoformat()
        analysis_status.last_activity = datetime.now().isoformat()
    
    def verify_module(
        self,
        project_id: str,
        module_name: str,
        verification: VerificationStatus,
        verified_by: Optional[str] = None
    ):
        """Mark module as verified by user"""
        analysis_status = self.get_status(project_id)
        if not analysis_status:
            raise ValueError(f"Analysis status not found: {project_id}")
        
        module_status = analysis_status.get_module_status(module_name)
        if not module_status:
            raise ValueError(f"Unknown module: {module_name}")
        
        module_status.verification_status = verification
        module_status.verified_at = datetime.now().isoformat()
        module_status.verified_by = verified_by
        
        analysis_status.updated_at = datetime.now().isoformat()
        analysis_status.last_activity = datetime.now().isoformat()
    
    def list_all(self) -> List[AnalysisStatus]:
        """List all analysis statuses"""
        return list(self._storage.values())


# Global instance
analysis_status_storage = AnalysisStatusStorage()
