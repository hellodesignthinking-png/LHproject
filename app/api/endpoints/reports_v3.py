"""
ZeroSite v3.3 Report API Endpoints
===================================

RESTful API endpoints for all 7 ZeroSite v3.3 Report Composers

Features:
- 6 Report Types (Pre-Report, Comprehensive, LH Decision, Investor, Land Price, Internal Assessment)
- Unified AppraisalContext integration
- PDF/HTML/JSON format support
- Async background processing support
- Standardized response format

Endpoints:
    POST /api/v3/reports/pre-report - Generate Pre-Report (2 pages)
    POST /api/v3/reports/comprehensive - Generate Comprehensive Report (15-20 pages)
    POST /api/v3/reports/lh-decision - Generate LH Decision Report
    POST /api/v3/reports/investor - Generate Investor Report (10-12 pages)
    POST /api/v3/reports/land-price - Generate Land Price Report (5-8 pages)
    POST /api/v3/reports/internal - Generate Internal Assessment (5 pages)
    GET /api/v3/reports/{report_id}/pdf - Download report as PDF
    GET /api/v3/reports/{report_id}/status - Check report generation status

Author: ZeroSite Development Team
Date: 2025-12-15
Version: v3.3
"""

from typing import Optional, List, Dict, Any, Literal
from pathlib import Path
from datetime import datetime
import uuid
import logging

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from app.services.report_composers import (
    PreReportComposer,
    ComprehensiveReportComposer,
    LHDecisionReportComposer,
    InvestorReportComposer,
    LandPriceReportComposer,
    InternalAssessmentComposer
)
from app.services.appraisal_context import AppraisalContextLock
from app.services.composer_adapter import ComposerDataAdapter
from app.services.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v3/reports", tags=["ZeroSite v3.3 Reports"])

# Initialize services
pdf_generator = PDFGenerator()

# In-memory storage for demo (replace with DB in production)
report_storage: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Request/Response Models
# ============================================================================

class ReportGenerationRequest(BaseModel):
    """Base request for report generation"""
    
    # Required: Appraisal Context Data
    appraisal_context: Dict[str, Any] = Field(
        ..., 
        description="AppraisalContext data (from analysis engine)"
    )
    
    # Optional: Target audience
    target_audience: Optional[Literal["landowner", "investor", "developer", "lh_evaluator"]] = Field(
        "landowner",
        description="Target audience for report"
    )
    
    # Optional: Output format
    output_format: Optional[Literal["json", "html", "pdf"]] = Field(
        "json",
        description="Output format (json returns structured data, html/pdf requires templates)"
    )
    
    # Optional: Metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata for report"
    )


class ReportGenerationResponse(BaseModel):
    """Response for report generation"""
    
    report_id: str = Field(..., description="Unique report ID")
    report_type: str = Field(..., description="Type of report generated")
    version: str = Field(default="v3.3", description="Report version")
    status: Literal["success", "processing", "failed"] = Field(..., description="Generation status")
    
    # Report data (JSON format)
    data: Optional[Dict[str, Any]] = Field(None, description="Report data (if output_format=json)")
    
    # File URLs (HTML/PDF format)
    html_url: Optional[str] = Field(None, description="HTML download URL")
    pdf_url: Optional[str] = Field(None, description="PDF download URL")
    
    # Metadata
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    generation_time_ms: Optional[float] = Field(None, description="Generation time in milliseconds")
    
    # Errors (if any)
    error: Optional[str] = Field(None, description="Error message if failed")


class BulkReportRequest(BaseModel):
    """Request for generating multiple reports"""
    
    appraisal_context: Dict[str, Any] = Field(..., description="AppraisalContext data")
    report_types: List[str] = Field(
        default=["pre_report", "comprehensive", "lh_decision"],
        description="List of report types to generate"
    )
    target_audience: Optional[str] = Field("landowner", description="Target audience")
    output_format: Optional[Literal["json", "html", "pdf"]] = Field("json", description="Output format")


class BulkReportResponse(BaseModel):
    """Response for bulk report generation"""
    
    job_id: str = Field(..., description="Bulk job ID")
    status: Literal["success", "processing", "failed"] = Field(..., description="Overall status")
    reports: Dict[str, ReportGenerationResponse] = Field(
        default_factory=dict,
        description="Individual report results"
    )
    total_generation_time_ms: Optional[float] = Field(None, description="Total generation time")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Helper Functions
# ============================================================================

def create_appraisal_context(data: Dict[str, Any]) -> AppraisalContextLock:
    """
    Create AppraisalContextLock from request data
    
    Args:
        data: Appraisal context data dictionary
        
    Returns:
        AppraisalContextLock instance (locked and immutable)
    """
    ctx = AppraisalContextLock()
    
    # Lock context with provided data (becomes immutable)
    ctx.lock(data)
    
    return ctx


def generate_report_id(report_type: str) -> str:
    """Generate unique report ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"{report_type}_{timestamp}_{short_uuid}"


def save_report_to_storage(report_id: str, report_data: Dict[str, Any], metadata: Dict[str, Any]):
    """Save report to in-memory storage (replace with DB in production)"""
    report_storage[report_id] = {
        "data": report_data,
        "metadata": metadata,
        "created_at": datetime.now().isoformat()
    }


# ============================================================================
# Report Generation Endpoints
# ============================================================================

@router.post("/pre-report", response_model=ReportGenerationResponse)
async def generate_pre_report(request: ReportGenerationRequest):
    """
    Generate Pre-Report (2-page Executive Summary)
    
    Quick screening report for initial land evaluation.
    Includes: LH Possibility Gauge, Key Metrics, Supply Type Recommendation
    """
    try:
        start_time = datetime.now()
        
        # Create AppraisalContext
        ctx = create_appraisal_context(request.appraisal_context)
        
        # Extract Composer data using adapter
        composer_data = ComposerDataAdapter.for_pre_report(ctx)
        
        # Generate report using Composer
        composer = PreReportComposer(**composer_data)
        report_data = composer.generate()  # PreReportComposer uses generate()
        
        # Generate report ID
        report_id = generate_report_id("pre_report")
        
        # Add metadata
        metadata = {
            "report_id": report_id,
            "version": "v3.3",
            "created_at": datetime.now().isoformat(),
            **request.metadata
        }
        
        # Save to storage
        save_report_to_storage(report_id, report_data, metadata)
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Build response based on output format
        response = ReportGenerationResponse(
            report_id=report_id,
            report_type="pre_report",
            version="v3.3",
            status="success",
            generation_time_ms=generation_time
        )
        
        if request.output_format == "json":
            response.data = report_data
        elif request.output_format == "html":
            response.html_url = f"/api/v3/reports/{report_id}/html"
        elif request.output_format == "pdf":
            response.pdf_url = f"/api/v3/reports/{report_id}/pdf"
        
        logger.info(f"✅ Pre-Report generated: {report_id} ({generation_time:.2f}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Pre-Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/comprehensive", response_model=ReportGenerationResponse)
async def generate_comprehensive_report(request: ReportGenerationRequest):
    """
    Generate Comprehensive Report (15-20 pages)
    
    Detailed analysis report for serious buyers.
    Includes: Executive Summary, Land Analysis, LH Compatibility, Financial Analysis, Risk Assessment
    """
    try:
        start_time = datetime.now()
        
        ctx = create_appraisal_context(request.appraisal_context)
        composer_data = ComposerDataAdapter.for_comprehensive(ctx)
        composer = ComprehensiveReportComposer(**composer_data)
        report_data = composer.compose(target_audience=request.target_audience)
        
        report_id = generate_report_id("comprehensive")
        metadata = {
            "report_id": report_id,
            "version": "v3.3",
            "created_at": datetime.now().isoformat(),
            **request.metadata
        }
        
        save_report_to_storage(report_id, report_data, metadata)
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = ReportGenerationResponse(
            report_id=report_id,
            report_type="comprehensive",
            version="v3.3",
            status="success",
            generation_time_ms=generation_time
        )
        
        if request.output_format == "json":
            response.data = report_data
        elif request.output_format == "html":
            response.html_url = f"/api/v3/reports/{report_id}/html"
        elif request.output_format == "pdf":
            response.pdf_url = f"/api/v3/reports/{report_id}/pdf"
        
        logger.info(f"✅ Comprehensive Report generated: {report_id} ({generation_time:.2f}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Comprehensive Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/lh-decision", response_model=ReportGenerationResponse)
async def generate_lh_decision_report(request: ReportGenerationRequest):
    """
    Generate LH Decision Report
    
    Professional report for LH evaluation process.
    Includes: LH Compatibility Analysis, Development Plan, Compliance Check
    """
    try:
        start_time = datetime.now()
        
        ctx = create_appraisal_context(request.appraisal_context)
        composer_data = ComposerDataAdapter.for_lh_decision(ctx)
        composer = LHDecisionReportComposer(**composer_data)
        report_data = composer.generate()  # LHDecisionReportComposer uses generate()
        
        report_id = generate_report_id("lh_decision")
        metadata = {
            "report_id": report_id,
            "version": "v3.3",
            "created_at": datetime.now().isoformat(),
            **request.metadata
        }
        
        save_report_to_storage(report_id, report_data, metadata)
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = ReportGenerationResponse(
            report_id=report_id,
            report_type="lh_decision",
            version="v3.3",
            status="success",
            generation_time_ms=generation_time
        )
        
        if request.output_format == "json":
            response.data = report_data
        elif request.output_format == "html":
            response.html_url = f"/api/v3/reports/{report_id}/html"
        elif request.output_format == "pdf":
            response.pdf_url = f"/api/v3/reports/{report_id}/pdf"
        
        logger.info(f"✅ LH Decision Report generated: {report_id} ({generation_time:.2f}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ LH Decision Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/investor", response_model=ReportGenerationResponse)
async def generate_investor_report(request: ReportGenerationRequest):
    """
    Generate Investor Report (10-12 pages)
    
    Investment-focused report for potential investors.
    Includes: Investment Grade, Financial Metrics (IRR/ROI/NPV), Scenario Analysis, Risk-Return Analysis
    """
    try:
        start_time = datetime.now()
        
        ctx = create_appraisal_context(request.appraisal_context)
        composer_data = ComposerDataAdapter.for_investor(ctx)
        composer = InvestorReportComposer(**composer_data)
        report_data = composer.compose()
        
        report_id = generate_report_id("investor")
        metadata = {
            "report_id": report_id,
            "version": "v1.0",
            "created_at": datetime.now().isoformat(),
            **request.metadata
        }
        
        save_report_to_storage(report_id, report_data, metadata)
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = ReportGenerationResponse(
            report_id=report_id,
            report_type="investor",
            version="v1.0",
            status="success",
            generation_time_ms=generation_time
        )
        
        if request.output_format == "json":
            response.data = report_data
        elif request.output_format == "html":
            response.html_url = f"/api/v3/reports/{report_id}/html"
        elif request.output_format == "pdf":
            response.pdf_url = f"/api/v3/reports/{report_id}/pdf"
        
        logger.info(f"✅ Investor Report generated: {report_id} ({generation_time:.2f}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Investor Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/land-price", response_model=ReportGenerationResponse)
async def generate_land_price_report(request: ReportGenerationRequest):
    """
    Generate Land Price Report (5-8 pages)
    
    Comprehensive land price analysis report.
    Includes: 4-Way Price Comparison, Public Price Trends, Appraisal Analysis, Fair Price Range
    """
    try:
        start_time = datetime.now()
        
        ctx = create_appraisal_context(request.appraisal_context)
        composer_data = ComposerDataAdapter.for_land_price(ctx)
        composer = LandPriceReportComposer(**composer_data)
        report_data = composer.compose()
        
        report_id = generate_report_id("land_price")
        metadata = {
            "report_id": report_id,
            "version": "v1.0",
            "created_at": datetime.now().isoformat(),
            **request.metadata
        }
        
        save_report_to_storage(report_id, report_data, metadata)
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = ReportGenerationResponse(
            report_id=report_id,
            report_type="land_price",
            version="v1.0",
            status="success",
            generation_time_ms=generation_time
        )
        
        if request.output_format == "json":
            response.data = report_data
        elif request.output_format == "html":
            response.html_url = f"/api/v3/reports/{report_id}/html"
        elif request.output_format == "pdf":
            response.pdf_url = f"/api/v3/reports/{report_id}/pdf"
        
        logger.info(f"✅ Land Price Report generated: {report_id} ({generation_time:.2f}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Land Price Report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/internal", response_model=ReportGenerationResponse)
async def generate_internal_assessment(request: ReportGenerationRequest):
    """
    Generate Internal Assessment Report (5 pages)
    
    Internal decision-making evaluation report.
    Includes: GO/CONDITIONAL/NO-GO Decision, Quantitative Metrics, Risk Flags, Actionable Next Steps
    """
    try:
        start_time = datetime.now()
        
        ctx = create_appraisal_context(request.appraisal_context)
        composer_data = ComposerDataAdapter.for_internal(ctx)
        composer = InternalAssessmentComposer(**composer_data)
        report_data = composer.compose()
        
        report_id = generate_report_id("internal")
        metadata = {
            "report_id": report_id,
            "version": "v1.0",
            "created_at": datetime.now().isoformat(),
            **request.metadata
        }
        
        save_report_to_storage(report_id, report_data, metadata)
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = ReportGenerationResponse(
            report_id=report_id,
            report_type="internal",
            version="v1.0",
            status="success",
            generation_time_ms=generation_time
        )
        
        if request.output_format == "json":
            response.data = report_data
        elif request.output_format == "html":
            response.html_url = f"/api/v3/reports/{report_id}/html"
        elif request.output_format == "pdf":
            response.pdf_url = f"/api/v3/reports/{report_id}/pdf"
        
        logger.info(f"✅ Internal Assessment generated: {report_id} ({generation_time:.2f}ms)")
        return response
        
    except Exception as e:
        logger.error(f"❌ Internal Assessment generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.post("/bulk", response_model=BulkReportResponse)
async def generate_bulk_reports(request: BulkReportRequest):
    """
    Generate multiple reports at once
    
    Useful for generating a full report package (e.g., Pre-Report + Comprehensive + Investor)
    """
    try:
        start_time = datetime.now()
        job_id = str(uuid.uuid4())
        
        ctx = create_appraisal_context(request.appraisal_context)
        results = {}
        
        # Generate each requested report
        for report_type in request.report_types:
            try:
                composer_map = {
                    "pre_report": PreReportComposer,
                    "comprehensive": ComprehensiveReportComposer,
                    "lh_decision": LHDecisionReportComposer,
                    "investor": InvestorReportComposer,
                    "land_price": LandPriceReportComposer,
                    "internal": InternalAssessmentComposer
                }
                
                if report_type not in composer_map:
                    logger.warning(f"Unknown report type: {report_type}")
                    continue
                
                # Get appropriate adapter method for this report type
                adapter_map = {
                    "pre_report": ComposerDataAdapter.for_pre_report,
                    "comprehensive": ComposerDataAdapter.for_comprehensive,
                    "lh_decision": ComposerDataAdapter.for_lh_decision,
                    "investor": ComposerDataAdapter.for_investor,
                    "land_price": ComposerDataAdapter.for_land_price,
                    "internal": ComposerDataAdapter.for_internal
                }
                
                composer_data = adapter_map[report_type](ctx)
                composer = composer_map[report_type](**composer_data)
                
                # Call appropriate method (some use generate(), some use compose())
                if report_type == "pre_report":
                    report_data = composer.generate()  # PreReportComposer uses generate()
                elif report_type == "lh_decision":
                    report_data = composer.generate()  # LHDecisionReportComposer uses generate()
                elif report_type == "comprehensive":
                    report_data = composer.compose(target_audience=request.target_audience)  # ComprehensiveReportComposer uses compose()
                else:
                    # investor, land_price, internal use compose()
                    report_data = composer.compose()
                
                report_id = generate_report_id(report_type)
                metadata = {"report_id": report_id, "created_at": datetime.now().isoformat()}
                save_report_to_storage(report_id, report_data, metadata)
                
                results[report_type] = ReportGenerationResponse(
                    report_id=report_id,
                    report_type=report_type,
                    version="v3.3",
                    status="success",
                    data=report_data if request.output_format == "json" else None,
                    pdf_url=f"/api/v3/reports/{report_id}/pdf" if request.output_format == "pdf" else None
                )
                
            except Exception as e:
                logger.error(f"Failed to generate {report_type}: {e}")
                results[report_type] = ReportGenerationResponse(
                    report_id=f"{report_type}_failed",
                    report_type=report_type,
                    version="v3.3",
                    status="failed",
                    error=str(e)
                )
        
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return BulkReportResponse(
            job_id=job_id,
            status="success",
            reports=results,
            total_generation_time_ms=total_time
        )
        
    except Exception as e:
        logger.error(f"❌ Bulk report generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Bulk generation failed: {str(e)}")


# ============================================================================
# Report Download Endpoints
# ============================================================================

@router.get("/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """
    Download report as PDF
    
    Note: PDF generation requires WeasyPrint fix (known issue with v60+)
    Currently returns JSON with fallback message
    """
    try:
        if report_id not in report_storage:
            raise HTTPException(status_code=404, detail="Report not found")
        
        stored_report = report_storage[report_id]
        report_data = stored_report["data"]
        metadata = stored_report["metadata"]
        
        # Determine report type from ID
        report_type = report_id.split("_")[0]
        
        # Generate PDF (will fail with current WeasyPrint v60+ - needs fix)
        try:
            pdf_bytes = pdf_generator.generate(report_type, report_data, metadata)
            
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename={report_id}.pdf"
                }
            )
        except Exception as pdf_error:
            # Fallback: Return JSON with error message
            logger.warning(f"PDF generation failed (known WeasyPrint issue): {pdf_error}")
            return JSONResponse(
                status_code=501,
                content={
                    "error": "PDF generation currently unavailable",
                    "reason": "WeasyPrint v60+ compatibility issue - downgrade to v59 required",
                    "fallback": "Use /html or /json endpoints instead",
                    "report_id": report_id,
                    "data": report_data
                }
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")


@router.get("/{report_id}/html")
async def download_report_html(report_id: str):
    """
    Download report as HTML
    
    Returns rendered HTML version of the report
    """
    try:
        if report_id not in report_storage:
            raise HTTPException(status_code=404, detail="Report not found")
        
        stored_report = report_storage[report_id]
        report_data = stored_report["data"]
        metadata = stored_report["metadata"]
        
        # Determine report type from ID
        report_type = report_id.split("_")[0]
        
        # Generate HTML using PDFGenerator's template engine
        html_content = pdf_generator.generate_html(report_type, report_data, metadata)
        
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Disposition": f"inline; filename={report_id}.html"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ HTML download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"HTML download failed: {str(e)}")


@router.get("/{report_id}/json")
async def download_report_json(report_id: str):
    """
    Download report as JSON
    
    Returns structured JSON data of the report
    """
    try:
        if report_id not in report_storage:
            raise HTTPException(status_code=404, detail="Report not found")
        
        stored_report = report_storage[report_id]
        
        return JSONResponse(content={
            "report_id": report_id,
            "data": stored_report["data"],
            "metadata": stored_report["metadata"]
        })
        
    except Exception as e:
        logger.error(f"❌ JSON download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"JSON download failed: {str(e)}")


@router.get("/{report_id}/status")
async def get_report_status(report_id: str):
    """
    Get report generation status
    
    Useful for async report generation tracking
    """
    try:
        if report_id not in report_storage:
            return JSONResponse(
                status_code=404,
                content={
                    "report_id": report_id,
                    "status": "not_found",
                    "message": "Report not found or not yet generated"
                }
            )
        
        stored_report = report_storage[report_id]
        
        return JSONResponse(content={
            "report_id": report_id,
            "status": "completed",
            "created_at": stored_report["created_at"],
            "report_type": report_id.split("_")[0],
            "available_formats": ["json", "html", "pdf"]
        })
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


# ============================================================================
# Land Appraisal Lookup API (v3.4)
# ============================================================================

class AppraisalLookupResponse(BaseModel):
    """Response for appraisal lookup"""
    
    success: bool = Field(..., description="Lookup success status")
    address: str = Field(..., description="Resolved address")
    parcel_id: Optional[str] = Field(None, description="Parcel ID (지번)")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    
    # Land basic info
    land_area_sqm: Optional[float] = Field(None, description="Land area in sqm")
    land_area_pyeong: Optional[float] = Field(None, description="Land area in pyeong")
    
    # Public price
    public_price_per_sqm: Optional[float] = Field(None, description="공시지가 (per sqm)")
    public_price_total: Optional[float] = Field(None, description="공시지가 (total)")
    public_price_year: Optional[int] = Field(None, description="공시지가 기준년도")
    
    # Zoning
    zoning_type: Optional[str] = Field(None, description="용도지역")
    far: Optional[float] = Field(None, description="용적률 (%)")
    bcr: Optional[float] = Field(None, description="건폐율 (%)")
    max_floors: Optional[int] = Field(None, description="최대 층수")
    
    # Comparable samples
    samples: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="거리사례")
    
    # Premium scores
    premium: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Premium 분석")
    
    # Error info
    error: Optional[str] = Field(None, description="Error message if failed")
    
    # Metadata
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


@router.get("/lookup")
async def lookup_appraisal(
    address: str = Query(..., description="토지 주소 (예: 서울특별시 강남구 테헤란로 123)")
):
    """
    토지 주소 기반 자동 감정평가 조회
    
    ZeroSite v3.4 핵심 기능:
    - 주소 입력 시 자동으로 공시지가, 용도지역, 거리사례 조회
    - Premium 점수 자동 계산
    - 사용자가 manual override 가능하도록 기본 데이터 제공
    
    Args:
        address: 토지 주소
    
    Returns:
        AppraisalLookupResponse: 조회된 감정평가 데이터
    """
    try:
        logger.info(f"🔍 Appraisal lookup requested for address: {address}")
        
        # Mock data for demonstration
        # TODO: Replace with real API calls to government databases
        # - 공시지가: 국토교통부 공시가격알리미 API
        # - 용도지역: 국토정보플랫폼 API
        # - 거리사례: 부동산거래관리시스템 API
        
        mock_response = AppraisalLookupResponse(
            success=True,
            address=address,
            parcel_id="서울 강남구 테헤란로 123",
            latitude=37.5048,
            longitude=127.0491,
            land_area_sqm=660.0,
            land_area_pyeong=199.6,
            public_price_per_sqm=4850000,
            public_price_total=3201000000,
            public_price_year=2024,
            zoning_type="제2종일반주거지역",
            far=250.0,
            bcr=50.0,
            max_floors=5,
            samples=[
                {
                    "id": "sample_1",
                    "price_per_sqm": 6800000,
                    "total_price": 4488000000,
                    "area_sqm": 660,
                    "distance_m": 150,
                    "transaction_date": "2024-11-15",
                    "zoning": "제2종일반주거지역"
                },
                {
                    "id": "sample_2",
                    "price_per_sqm": 6500000,
                    "total_price": 4290000000,
                    "area_sqm": 660,
                    "distance_m": 280,
                    "transaction_date": "2024-10-20",
                    "zoning": "제2종일반주거지역"
                },
                {
                    "id": "sample_3",
                    "price_per_sqm": 6200000,
                    "total_price": 4092000000,
                    "area_sqm": 660,
                    "distance_m": 420,
                    "transaction_date": "2024-09-05",
                    "zoning": "제2종일반주거지역"
                }
            ],
            premium={
                "road_score": 8.5,
                "road_description": "간선도로 접면, 교통 편리",
                "topography_score": 7.0,
                "topography_description": "평탄지, 개발 용이",
                "local_difficulty": "LOW",
                "local_description": "LH 승인 용이지역",
                "overall_premium": 30.0,
                "premium_description": "평균 대비 30% 할증 적용"
            }
        )
        
        logger.info(f"✅ Lookup successful for: {address}")
        return mock_response
        
    except Exception as e:
        logger.error(f"❌ Lookup failed: {e}", exc_info=True)
        return AppraisalLookupResponse(
            success=False,
            address=address,
            error=f"Lookup failed: {str(e)}"
        )


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def health_check():
    """
    API health check endpoint
    
    Returns status of all report composers
    """
    return {
        "status": "healthy",
        "version": "v3.4",  # Updated to v3.4
        "composers": {
            "pre_report": "operational",
            "comprehensive": "operational",
            "lh_decision": "operational",
            "investor": "operational",
            "land_price": "operational",
            "internal": "operational"
        },
        "pdf_generation": "degraded (WeasyPrint v60+ issue)",
        "lookup_api": "operational",  # New feature
        "total_reports_generated": len(report_storage),
        "timestamp": datetime.now().isoformat()
    }
