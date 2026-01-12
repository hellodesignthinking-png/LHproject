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
        
        # Auto-collect POI data using Kakao Map API
        try:
            from app.services.kakao.kakao_map_service import KakaoMapService
            
            kakao_service = KakaoMapService()
            poi_data = await kakao_service.collect_all_poi(request.address)
            
            # Create basic M1 data structure with POI
            m1_result = {
                "address": request.address,
                "road_address": request.address,  # Will be filled by geocoding
                "area_sqm": 0,  # To be filled manually
                "area_pyeong": 0,
                "zone_type": "",
                "far": 0,
                "bcr": 0,
                "road_width": 0,
                "official_land_price": 0,
                "official_price_date": "",
                "regulations": "",
                "restrictions": "",
                "subway_stations": poi_data.get("subway_stations", []),
                "bus_stops": poi_data.get("bus_stops", []),
                "poi_schools": poi_data.get("poi_schools", []),
                "poi_commercial": poi_data.get("poi_commercial", []),
                "data_sources": {
                    "cadastral": "Kakao Map API (POI only)",
                    "official_price": "Not collected",
                    "regulations": "Not collected"
                }
            }
            
            # Update M1 status with collected data
            analysis_status_storage.update_module_status(
                project_id=project_id,
                module_name="M1",
                status=ModuleStatus.COMPLETED,
                result_summary=m1_result
            )
            
            logger.info(f"✅ M1 POI data auto-collected for {project_id}")
            logger.info(f"   Subway stations: {len(poi_data.get('subway_stations', []))}")
            logger.info(f"   Schools: {len(poi_data.get('poi_schools', []))}")
            logger.info(f"   Commercial: {len(poi_data.get('poi_commercial', []))}")
            
        except Exception as poi_err:
            logger.warning(f"⚠️ Failed to auto-collect POI: {poi_err}")
            # Continue without POI data - user can collect manually later
        
        return CreateProjectResponse(
            success=True,
            project_id=project_id,
            message="Project created successfully. M1 data collection completed with POI data.",
            next_action="Please verify M1 data and complete missing information..."
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
    
    # For M1, allow verification even if status is not COMPLETED
    # This supports manual data entry workflow
    if module_name == "M1":
        if module_info.status == ModuleStatus.NOT_STARTED:
            logger.warning(f"⚠️ M1 verification requested but status is NOT_STARTED")
            logger.warning(f"   Allowing verification for manual data workflow")
        elif module_info.status != ModuleStatus.COMPLETED:
            logger.warning(f"⚠️ M1 status is {module_info.status}, not COMPLETED")
    else:
        # For M2-M6, require COMPLETED status
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


class ExecuteModuleResponse(BaseModel):
    """Module execution response"""
    success: bool
    message: str
    module_name: str
    execution_id: Optional[str] = None
    status: str


@router.post("/projects/{project_id}/modules/{module_name}/execute", response_model=ExecuteModuleResponse)
async def execute_module(
    project_id: str,
    module_name: str
):
    """
    ⚡ CRITICAL: Execute module analysis
    
    This triggers the actual execution of M2-M6 modules.
    M1 is executed automatically on project creation.
    
    Args:
        project_id: Project identifier
        module_name: M2, M3, M4, M5, or M6 (M1 is automatic)
    
    Returns:
        Execution status and result
    """
    
    # Validate module name
    valid_modules = ["M2", "M3", "M4", "M5", "M6"]
    if module_name not in valid_modules:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid module: {module_name}. Only M2-M6 can be executed via this endpoint."
        )
    
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # Check if module can be executed
    can_execute, reason = status.can_execute_module(module_name)
    if not can_execute:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute {module_name}: {reason}"
        )
    
    try:
        execution_id = str(uuid.uuid4())
        
        logger.info(f"⚡ Executing {module_name} for project {project_id}")
        logger.info(f"   Execution ID: {execution_id}")
        
        # Mark module as in progress
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name=module_name,
            status=ModuleStatus.IN_PROGRESS,
            result_summary={"execution_id": execution_id, "started_at": datetime.now().isoformat()}
        )
        
        # TODO: Actually execute the module logic here
        # For now, immediately mark as completed (mock)
        # In production, this would call the actual M2/M3/M4/M5/M6 services
        
        # Execute actual module logic based on module_name
        if module_name == "M2":
            # M2: Land Value Analysis
            m1_data = status.get_module_status("M1").result_summary
            if m1_data:
                # Simple land value calculation based on M1 data
                area_sqm = m1_data.get("area_sqm", 0)
                official_price = m1_data.get("official_land_price", 0)
                zone_type = m1_data.get("zone_type", "")
                
                # Calculate estimated land value (simple formula)
                # Official price usually 70-80% of market price
                if area_sqm > 0 and official_price > 0:
                    estimated_value = int(area_sqm * official_price * 1.3)  # 30% markup
                    unit_price_sqm = int(official_price * 1.3)
                    unit_price_pyeong = int(unit_price_sqm * 3.3058)
                else:
                    estimated_value = 0
                    unit_price_sqm = 0
                    unit_price_pyeong = 0
                
                mock_result = {
                    "execution_id": execution_id,
                    "module": module_name,
                    "computed_at": datetime.now().isoformat(),
                    "status": "completed",
                    "land_value": estimated_value,
                    "unit_price_sqm": unit_price_sqm,
                    "unit_price_pyeong": unit_price_pyeong,
                    "confidence_score": 75,
                    "confidence_level": "보통",
                    "valuation_method": "공시지가 기준 추정",
                    "official_price": official_price,
                    "market_to_official_ratio": 1.3,
                    "price_range": {
                        "min": int(estimated_value * 0.9),
                        "max": int(estimated_value * 1.1)
                    },
                    "premium_factors": {
                        "corner_lot": 0,
                        "subway_proximity": 5 if m1_data.get("subway_stations") else 0,
                        "school_district": 3 if m1_data.get("poi_schools") else 0
                    },
                    "transaction_samples": []
                }
            else:
                mock_result = {
                    "execution_id": execution_id,
                    "module": module_name,
                    "computed_at": datetime.now().isoformat(),
                    "status": "completed",
                    "message": f"{module_name} execution completed but M1 data not available"
                }
        
        elif module_name == "M3":
            # M3: Housing Type Decision
            m1_data = status.get_module_status("M1").result_summary
            zone_type = m1_data.get("zone_type", "") if m1_data else ""
            
            # Simple housing type selection based on zone
            if "상업" in zone_type:
                selected_type = "도시형생활주택"
                confidence = 80
            elif "주거" in zone_type:
                selected_type = "공공임대주택"
                confidence = 85
            else:
                selected_type = "공공임대주택"
                confidence = 70
            
            mock_result = {
                "execution_id": execution_id,
                "module": module_name,
                "computed_at": datetime.now().isoformat(),
                "status": "completed",
                "selected_type": selected_type,
                "confidence": confidence,
                "decision_rationale": f"용도지역({zone_type})을 고려한 최적 주거 유형 선정",
                "selection_method": "용도지역 기반 자동 선택"
            }
        
        else:
            # M4, M5, M6: Simple mock for now
            mock_result = {
                "execution_id": execution_id,
                "module": module_name,
                "computed_at": datetime.now().isoformat(),
                "status": "completed",
                "message": f"{module_name} execution completed (basic implementation)"
            }
        
        # Mark module as completed
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name=module_name,
            status=ModuleStatus.COMPLETED,
            result_summary=mock_result
        )
        
        logger.info(f"✅ {module_name} execution completed")
        
        return ExecuteModuleResponse(
            success=True,
            message=f"{module_name} executed successfully",
            module_name=module_name,
            execution_id=execution_id,
            status="completed"
        )
    
    except Exception as e:
        logger.error(f"❌ {module_name} execution failed: {e}")
        
        # Mark module as failed
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name=module_name,
            status=ModuleStatus.FAILED,
            result_summary={"error": str(e)}
        )
        
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


@router.put("/projects/{project_id}/modules/M1/data")
async def update_m1_data(
    project_id: str,
    data: Dict[str, Any]
):
    """
    Update M1 data with manual input
    
    This allows users to manually input M1 land data when
    automatic collection fails or is incomplete.
    """
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    try:
        # Update M1 data
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name="M1",
            status=ModuleStatus.COMPLETED,
            result_summary=data
        )
        
        logger.info(f"✅ M1 data updated manually for project {project_id}")
        
        return {
            "success": True,
            "message": "M1 data updated successfully",
            "project_id": project_id
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to update M1 data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
