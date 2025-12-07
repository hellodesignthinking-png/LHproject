"""
ZeroSite Phase 11: Report Generation API v11

RESTful API endpoints for 5-type report system.

Features:
    - Single report generation
    - Bulk report generation (all 5 types)
    - Async background processing
    - PDF/HTML/JSON format support
    - Community auto-injection
    - Phase 8 verified cost integration

Endpoints:
    POST /api/v11/report - Generate single report
    POST /api/v11/report/all - Generate all 5 reports
    GET /api/v11/report/{report_id}/status - Check generation status
    GET /api/v11/report/{report_id}/download - Download generated report
"""

from typing import Optional, List, Dict, Any, Literal
from pathlib import Path
from datetime import datetime
import asyncio
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.report_types_v11.base_report_engine import (
    ZeroSiteDecision,
    ParcelData,
    CapexData,
    ROIData,
    LHScoreData,
    ComparableValuation,
    VerifiedCostData,
    BuildingScaleData
)
from app.report_types_v11.community_injector import inject_community_auto
from app.report_types_v11.export_engine import (
    export_single_report,
    export_all_reports,
    ExportEngine
)


# Router
router = APIRouter(prefix="/api/v11", tags=["Report Generation v11"])


# Request Models
class ReportGenerationRequest(BaseModel):
    """Request for report generation"""
    
    # Basic info
    address: str = Field(..., description="Target address")
    
    # Strategy
    strategy: Literal["single", "merged"] = Field("single", description="Development strategy")
    
    # Parcel data (simplified for API)
    land_area: float = Field(..., description="Land area in m²")
    building_coverage_ratio: float = Field(..., description="Building coverage ratio (%)")
    floor_area_ratio: float = Field(..., description="Floor area ratio (%)")
    land_use_zone: str = Field(..., description="Land use zone")
    
    # Optional preferences
    recommended_type: Optional[str] = Field(None, description="Housing type (Youth, Newlyweds_TypeI, etc.)")
    community_preference: Optional[str] = Field(None, description="Community module preference")
    
    # Format options
    formats: List[Literal["pdf", "html", "json"]] = Field(["pdf", "html"], description="Output formats")


class SingleReportRequest(ReportGenerationRequest):
    """Request for single report generation"""
    report_type: Literal["lh_submission", "investor", "construction", "executive", "comparative"] = Field(
        ..., 
        description="Type of report to generate"
    )


class AllReportsRequest(ReportGenerationRequest):
    """Request for all reports generation"""
    pass


# Response Models
class ReportGenerationResponse(BaseModel):
    """Response for report generation"""
    job_id: str = Field(..., description="Job ID for tracking")
    status: Literal["queued", "processing", "completed", "failed"] = Field(..., description="Job status")
    report_type: Optional[str] = None
    message: str = Field(..., description="Status message")
    
    # Results (when completed)
    pdf_url: Optional[str] = None
    html_url: Optional[str] = None
    json_url: Optional[str] = None
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    generation_time_seconds: Optional[float] = None


class AllReportsResponse(BaseModel):
    """Response for all reports generation"""
    job_id: str = Field(..., description="Job ID for tracking")
    status: Literal["queued", "processing", "completed", "failed"] = Field(..., description="Job status")
    message: str = Field(..., description="Status message")
    
    # Results (when completed)
    reports: Optional[Dict[str, Dict[str, str]]] = None  # {report_type: {format: url}}
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    total_generation_time_seconds: Optional[float] = None


# In-memory job storage (for demo - replace with Redis in production)
job_storage: Dict[str, Dict[str, Any]] = {}


# Helper Functions
def create_mock_decision(request: ReportGenerationRequest) -> ZeroSiteDecision:
    """
    Create mock decision from API request
    
    In production, this would call Phase 0-7 engines.
    For now, we create a simplified mock.
    """
    
    # Create parcel
    parcel = ParcelData(
        address=request.address,
        land_area=request.land_area,
        building_coverage_ratio=request.building_coverage_ratio,
        floor_area_ratio=request.floor_area_ratio,
        land_use_zone=request.land_use_zone,
        current_land_price=2500000.0  # Mock price
    )
    
    # Mock building scale
    scale = BuildingScaleData(
        max_building_area=request.land_area * (request.building_coverage_ratio / 100),
        max_floor_area=request.land_area * (request.floor_area_ratio / 100),
        estimated_units=int(request.land_area * (request.floor_area_ratio / 100) / 60),
        avg_unit_size=60.0,
        total_floors=int(request.floor_area_ratio / 100 * 3)
    )
    
    # Mock CAPEX
    capex = CapexData(
        land_acquisition=request.land_area * 2500000,
        construction_cost=scale.max_floor_area * 2000000,
        design_supervision=scale.max_floor_area * 2000000 * 0.06,
        financing_cost=scale.max_floor_area * 2000000 * 0.03,
        contingency=scale.max_floor_area * 2000000 * 0.05,
        total_capex=(request.land_area * 2500000) + (scale.max_floor_area * 2000000 * 1.14)
    )
    
    # Mock ROI
    roi = ROIData(
        roi_percent=12.5,
        irr_percent=10.8,
        npv=capex.total_capex * 0.12,
        payback_period_months=96,
        annual_rental_income=capex.total_capex * 0.135,
        total_rental_income=capex.total_capex * 1.08
    )
    
    # Mock LH Score
    lh_score = LHScoreData(
        location_score=22.0,
        transportation_score=18.5,
        education_score=19.0,
        amenities_score=13.5,
        demand_score=17.0,
        total_score=90.0,
        grade="A"
    )
    
    # Mock Comparable Valuation
    comparable = ComparableValuation(
        estimated_price_per_m2=2650000,
        estimated_total_price=request.land_area * 2650000,
        confidence_level=0.92,
        comparable_transactions=15,
        valuation_method="Comparable Sales Analysis",
        price_range_min=2450000,
        price_range_max=2850000
    )
    
    # Verified Cost (Phase 8 placeholder)
    verified_cost = VerifiedCostData(
        cost_per_m2=None,
        year=2025,
        status="pending_phase8"
    )
    
    # Determine recommended type
    recommended_type = request.recommended_type or "Youth"
    
    # Create decision
    decision = ZeroSiteDecision(
        address=request.address,
        parcels=[parcel],
        strategy=request.strategy,
        recommended_type=recommended_type,
        scale=scale,
        capex=capex,
        roi=roi,
        lh_score=lh_score,
        comparable_valuation=comparable,
        verified_cost=verified_cost,
        final_grade="A",
        recommendation="GO",
        key_strengths=[
            "우수한 투자수익률 (ROI 12.5%)",
            "높은 LH 평가 점수 (90.0/100)",
            "양호한 입지 조건"
        ],
        key_weaknesses=[
            "초기 투자비 부담",
            "시장 경쟁 존재"
        ],
        next_steps=[
            "토지 매매 협상 진행",
            "건축 설계 용역 발주",
            "LH 사전 상담 신청"
        ]
    )
    
    return decision


async def generate_report_async(
    job_id: str,
    request: ReportGenerationRequest,
    report_type: str,
    formats: List[str]
):
    """
    Background task for report generation
    
    This runs asynchronously and updates job_storage.
    """
    try:
        # Update status
        job_storage[job_id]["status"] = "processing"
        
        # Create decision
        decision = create_mock_decision(request)
        
        # Inject community
        inject_community_auto(decision, preference=request.community_preference)
        
        # Generate report
        results = {}
        for format_type in formats:
            result = export_single_report(
                decision,
                report_type,
                format_type,
                output_dir=Path("./reports")
            )
            
            if result.success:
                if format_type == "pdf":
                    results["pdf_url"] = f"/downloads/{Path(result.file_path).name}"
                elif format_type == "html":
                    results["html_url"] = f"/downloads/{Path(result.html_path).name}"
                elif format_type == "json":
                    results["json_url"] = f"/downloads/{Path(result.json_path).name}"
        
        # Update job storage
        job_storage[job_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "generation_time_seconds": 0.5,  # Mock time
            **results
        })
        
    except Exception as e:
        job_storage[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


async def generate_all_reports_async(
    job_id: str,
    request: ReportGenerationRequest,
    formats: List[str]
):
    """
    Background task for all reports generation
    """
    try:
        # Update status
        job_storage[job_id]["status"] = "processing"
        
        # Create decision
        decision = create_mock_decision(request)
        
        # Inject community
        inject_community_auto(decision, preference=request.community_preference)
        
        # Generate all reports
        results_dict = export_all_reports(
            decision,
            formats=formats,
            output_dir=Path("./reports")
        )
        
        # Format results
        reports = {}
        for report_type, format_results in results_dict.items():
            reports[report_type] = {}
            for format_type, result in format_results.items():
                if result.success:
                    if format_type == "pdf" and result.file_path:
                        reports[report_type]["pdf"] = f"/downloads/{Path(result.file_path).name}"
                    elif format_type == "html" and result.html_path:
                        reports[report_type]["html"] = f"/downloads/{Path(result.html_path).name}"
                    elif format_type == "json" and result.json_path:
                        reports[report_type]["json"] = f"/downloads/{Path(result.json_path).name}"
        
        # Update job storage
        job_storage[job_id].update({
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "total_generation_time_seconds": 1.0,  # Mock time
            "reports": reports
        })
        
    except Exception as e:
        job_storage[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


# API Endpoints
@router.post("/report", response_model=ReportGenerationResponse)
async def generate_single_report(
    request: SingleReportRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a single report
    
    This endpoint queues a report generation job and returns immediately.
    Use the job_id to check status and download results.
    
    Example:
        POST /api/v11/report
        {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500.0,
            "building_coverage_ratio": 60.0,
            "floor_area_ratio": 300.0,
            "land_use_zone": "제2종일반주거지역",
            "report_type": "executive",
            "formats": ["pdf", "html"]
        }
    """
    # Generate job ID
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    
    # Initialize job storage
    job_storage[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "report_type": request.report_type,
        "created_at": datetime.now().isoformat()
    }
    
    # Queue background task
    background_tasks.add_task(
        generate_report_async,
        job_id,
        request,
        request.report_type,
        request.formats
    )
    
    return ReportGenerationResponse(
        job_id=job_id,
        status="queued",
        report_type=request.report_type,
        message="Report generation queued. Use job_id to check status."
    )


@router.post("/report/all", response_model=AllReportsResponse)
async def generate_all_reports_endpoint(
    request: AllReportsRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate all 5 report types
    
    This endpoint generates all report types (LH, Investor, Construction, Executive, Comparative)
    and returns job_id for tracking.
    
    Example:
        POST /api/v11/report/all
        {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500.0,
            "building_coverage_ratio": 60.0,
            "floor_area_ratio": 300.0,
            "land_use_zone": "제2종일반주거지역",
            "formats": ["pdf", "html"]
        }
    """
    # Generate job ID
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    
    # Initialize job storage
    job_storage[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "created_at": datetime.now().isoformat()
    }
    
    # Queue background task
    background_tasks.add_task(
        generate_all_reports_async,
        job_id,
        request,
        request.formats
    )
    
    return AllReportsResponse(
        job_id=job_id,
        status="queued",
        message="All reports generation queued. Use job_id to check status."
    )


@router.get("/report/{job_id}/status")
async def get_report_status(job_id: str):
    """
    Check report generation status
    
    Example:
        GET /api/v11/report/job_abc123/status
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_storage[job_id]


@router.get("/report/{job_id}/download/{format}")
async def download_report(
    job_id: str,
    format: Literal["pdf", "html", "json"]
):
    """
    Download generated report
    
    Example:
        GET /api/v11/report/job_abc123/download/pdf
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_storage[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Job status: {job['status']}")
    
    # Get file URL
    url_key = f"{format}_url"
    if url_key not in job:
        raise HTTPException(status_code=404, detail=f"{format.upper()} file not found")
    
    file_url = job[url_key]
    file_path = Path("./reports") / Path(file_url).name
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type="application/octet-stream"
    )


# Health check
@router.get("/health")
async def health_check():
    """API health check"""
    return {
        "status": "healthy",
        "version": "11.0",
        "timestamp": datetime.now().isoformat()
    }
