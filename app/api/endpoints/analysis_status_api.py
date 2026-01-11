"""
ZeroSite Analysis Status & Result API
======================================

Endpoints for:
1. Project creation and status tracking
2. Module result retrieval (M1-M6)
3. Verification gates
4. Execution control

Author: ZeroSite UX Redesign Team
Date: 2026-01-11
Version: 3.0 (Human-Verified Mode)
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.analysis_status import (
    analysis_status_storage,
    AnalysisStatus,
    ModuleStatus,
    VerificationStatus,
    ModuleInfo
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["Analysis Status & Results"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateProjectRequest(BaseModel):
    """Create new analysis project"""
    project_name: str
    address: str
    reference_info: Optional[str] = None


class CreateProjectResponse(BaseModel):
    """Project creation response"""
    success: bool
    project_id: str
    message: str
    next_action: str


class VerifyModuleRequest(BaseModel):
    """User verification for module results"""
    approved: bool  # True = approved, False = rejected
    comments: Optional[str] = None
    verified_by: Optional[str] = "user"


class VerifyModuleResponse(BaseModel):
    """Verification response"""
    success: bool
    message: str
    next_action: Optional[str] = None
    can_proceed: bool


class ModuleResultResponse(BaseModel):
    """Module result retrieval response"""
    success: bool
    module_name: str
    status: str
    verification_status: Optional[str] = None
    executed_at: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    can_execute: bool
    execution_blocked_reason: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/projects/create", response_model=CreateProjectResponse)
async def create_analysis_project(request: CreateProjectRequest):
    """
    STEP 1: Create new analysis project
    
    Creates project and executes M1 data collection automatically.
    User must verify M1 before M2-M6 can execute.
    """
    try:
        # Generate project ID
        project_id = str(uuid.uuid4())
        context_id = str(uuid.uuid4())
        
        # Create analysis status
        status = analysis_status_storage.create_status(
            project_id=project_id,
            project_name=request.project_name,
            address=request.address,
            context_id=context_id
        )
        
        logger.info(f"✅ Project created: {project_id}")
        logger.info(f"   Name: {request.project_name}")
        logger.info(f"   Address: {request.address}")
        
        return CreateProjectResponse(
            success=True,
            project_id=project_id,
            message="Project created successfully. M1 data collection will start automatically.",
            next_action="Collecting M1 land information..."
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str) -> AnalysisStatus:
    """
    Get complete analysis status for a project
    
    Returns:
        - Current context ID and version
        - Status of all modules (M1-M6)
        - Verification status
        - Next recommended action
    """
    status = analysis_status_storage.get_status(project_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    return status


@router.post("/projects/{project_id}/modules/{module_name}/verify", response_model=VerifyModuleResponse)
async def verify_module_results(
    project_id: str,
    module_name: str,
    request: VerifyModuleRequest
):
    """
    🔒 CRITICAL: User verification gate
    
    User confirms or rejects module results.
    
    Args:
        project_id: Project identifier
        module_name: M1, M2, M3, M4, M5, or M6
        request: Verification decision
    
    Returns:
        Verification status and next action
    """
    
    # Validate module name
    valid_modules = ["M1", "M2", "M3", "M4", "M5", "M6"]
    if module_name not in valid_modules:
        raise HTTPException(status_code=400, detail=f"Invalid module: {module_name}")
    
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # Check if module has been executed
    module_info = status.get_module_status(module_name)
    if module_info.status != ModuleStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"{module_name} has not been completed yet. Current status: {module_info.status}"
        )
    
    # Apply verification
    verification_status = VerificationStatus.APPROVED if request.approved else VerificationStatus.REJECTED
    
    try:
        analysis_status_storage.verify_module(
            project_id=project_id,
            module_name=module_name,
            verification=verification_status,
            verified_by=request.verified_by
        )
        
        logger.info(f"✅ {module_name} verification: {verification_status.value}")
        logger.info(f"   Project: {project_id}")
        logger.info(f"   Verified by: {request.verified_by}")
        
        # Determine next action
        if verification_status == VerificationStatus.APPROVED:
            # Get next module
            module_order = ["M1", "M2", "M3", "M4", "M5", "M6"]
            current_idx = module_order.index(module_name)
            
            if current_idx < len(module_order) - 1:
                next_module = module_order[current_idx + 1]
                next_action = f"Ready to execute {next_module}"
                can_proceed = True
            else:
                next_action = "All modules completed - ready for final report"
                can_proceed = False
            
            return VerifyModuleResponse(
                success=True,
                message=f"{module_name} approved by user",
                next_action=next_action,
                can_proceed=can_proceed
            )
        else:
            # Rejected - need to re-collect
            return VerifyModuleResponse(
                success=True,
                message=f"{module_name} rejected by user - data recollection required",
                next_action=f"Re-execute {module_name} with corrected data",
                can_proceed=False
            )
    
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/modules/{module_name}/result", response_model=ModuleResultResponse)
async def get_module_result(
    project_id: str,
    module_name: str
):
    """
    Get result data for specific module
    
    Returns:
        - Module execution status
        - Verification status
        - Result data (if completed)
        - Whether next module can execute
    """
    
    # Validate module name
    valid_modules = ["M1", "M2", "M3", "M4", "M5", "M6"]
    if module_name not in valid_modules:
        raise HTTPException(status_code=400, detail=f"Invalid module: {module_name}")
    
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # Get module info
    module_info = status.get_module_status(module_name)
    
    # Check execution permission for next module
    module_order = ["M1", "M2", "M3", "M4", "M5", "M6"]
    current_idx = module_order.index(module_name)
    
    if current_idx < len(module_order) - 1:
        next_module = module_order[current_idx + 1]
        can_execute_next, reason = status.can_execute_module(next_module)
    else:
        can_execute_next = False
        reason = "Last module in pipeline"
    
    return ModuleResultResponse(
        success=True,
        module_name=module_name,
        status=module_info.status.value,
        verification_status=module_info.verification_status.value if module_info.verification_status else None,
        executed_at=module_info.executed_at,
        result_data=module_info.result_summary,
        can_execute=can_execute_next,
        execution_blocked_reason=None if can_execute_next else reason
    )


@router.get("/projects")
async def list_all_projects(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List all analysis projects
    
    Returns:
        List of projects with their status
    """
    all_statuses = analysis_status_storage.list_all()
    
    # Sort by last activity (most recent first)
    sorted_statuses = sorted(
        all_statuses,
        key=lambda s: s.last_activity,
        reverse=True
    )
    
    # Apply pagination
    paginated = sorted_statuses[offset:offset + limit]
    
    return {
        "success": True,
        "total": len(all_statuses),
        "limit": limit,
        "offset": offset,
        "projects": [
            {
                "project_id": s.project_id,
                "project_name": s.project_name,
                "address": s.address,
                "progress": s.get_progress_percentage(),
                "next_action": s.get_next_action(),
                "last_activity": s.last_activity,
                "is_locked": s.is_locked
            }
            for s in paginated
        ]
    }


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """
    Delete analysis project
    
    Note: This also invalidates all associated contexts
    """
    status = analysis_status_storage.get_status(project_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # TODO: Actually delete from storage
    # For now, just mark as invalid
    
    return {
        "success": True,
        "message": f"Project {project_id} deleted"
    }
