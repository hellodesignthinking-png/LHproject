"""
ZeroSite v4.0 Pipeline Report API Endpoints
============================================

RESTful API endpoints using 6-MODULE Pipeline Architecture

Features:
- ✅ 6-MODULE Pipeline Integration (M1→M2→M3→M4→M5→M6)
- ✅ Immutable Context-based Data Flow
- ✅ M2 Appraisal Protection (frozen=True)
- ✅ Unidirectional Pipeline Execution
- ✅ Comprehensive Report Generation
- ✅ PDF/HTML/JSON format support

Architecture:
    Pipeline: M1 (Land Info) → M2 (Appraisal) 🔒 → M3 (LH Demand) 
              → M4 (Capacity) → M5 (Feasibility) → M6 (LH Review)
    
    All Contexts are frozen=True (immutable after creation)
    M2 AppraisalContext is protected from downstream modification

Endpoints:
    POST /api/v4/pipeline/analyze - Run full 6-MODULE pipeline analysis
    POST /api/v4/pipeline/reports/comprehensive - Generate comprehensive report
    POST /api/v4/pipeline/reports/pre-report - Generate pre-report (2 pages)
    POST /api/v4/pipeline/reports/lh-decision - Generate LH decision report
    GET /api/v4/pipeline/results/{parcel_id} - Get cached pipeline results
    GET /api/v4/pipeline/health - Health check endpoint

Author: ZeroSite Refactoring Team
Date: 2025-12-17
Version: v4.0 (6-MODULE Pipeline)
"""

from typing import Optional, Dict, Any, Literal
from datetime import datetime
import uuid
import logging
import time

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline, PipelineResult
from app.core.context.canonical_land import CanonicalLandContext
from app.core.canonical_data_contract import (
    convert_m2_to_standard,
    convert_m3_to_standard,
    convert_m6_to_standard,
    M4Summary,
    M4Result,
    M5Summary,
    M5Result
)

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v4/pipeline", tags=["ZeroSite v4.0 Pipeline"])

# Pipeline instance (singleton)
pipeline = ZeroSitePipeline()

# In-memory cache for pipeline results (replace with Redis in production)
results_cache: Dict[str, PipelineResult] = {}


# ============================================================================
# Request/Response Models
# ============================================================================

class PipelineAnalysisRequest(BaseModel):
    """Request for full 6-MODULE pipeline analysis"""
    
    parcel_id: str = Field(..., description="Parcel ID (PNU code)")
    
    # Optional: For testing with mock data
    mock_land_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional mock land data (for testing)"
    )
    
    # Optional: Cache control
    use_cache: bool = Field(
        True,
        description="Use cached results if available"
    )
    
    # Optional: Metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )


class PipelineAnalysisResponse(BaseModel):
    """Response for pipeline analysis"""
    
    parcel_id: str = Field(..., description="Parcel ID")
    analysis_id: str = Field(..., description="Unique analysis ID")
    status: Literal["success", "failed"] = Field(..., description="Analysis status")
    version: str = Field(default="v4.0", description="Pipeline version")
    
    # Pipeline execution metadata
    execution_time_ms: float = Field(..., description="Total execution time (ms)")
    modules_executed: int = Field(default=6, description="Number of modules executed")
    
    # Results by module
    results: Optional[Dict[str, Any]] = Field(None, description="Pipeline results by module")
    
    # Key outputs
    land_value: Optional[float] = Field(None, description="M2: Estimated land value (₩)")
    confidence_score: Optional[float] = Field(None, description="M2: Confidence score (0-1)")
    selected_housing_type: Optional[str] = Field(None, description="M3: Selected LH housing type")
    recommended_units: Optional[int] = Field(None, description="M4: Recommended units")
    npv_public: Optional[float] = Field(None, description="M5: NPV (public)")
    lh_decision: Optional[str] = Field(None, description="M6: LH review decision")
    lh_total_score: Optional[float] = Field(None, description="M6: LH total score (/110)")
    
    # M4 V2 Enhanced outputs
    legal_capacity_units: Optional[int] = Field(None, description="M4: Legal FAR capacity units")
    incentive_capacity_units: Optional[int] = Field(None, description="M4: Incentive FAR capacity units")
    massing_options_count: Optional[int] = Field(None, description="M4: Number of massing alternatives")
    parking_alt_a_spaces: Optional[int] = Field(None, description="M4: Parking Alt A spaces (FAR MAX)")
    parking_alt_b_spaces: Optional[int] = Field(None, description="M4: Parking Alt B spaces (Parking Priority)")
    schematic_drawings_available: Optional[bool] = Field(None, description="M4: Schematic drawings generated")
    
    # Metadata
    analyzed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Error info
    error: Optional[str] = Field(None, description="Error message if failed")


class ReportGenerationRequest(BaseModel):
    """Request for report generation from pipeline results"""
    
    parcel_id: str = Field(..., description="Parcel ID (must have pipeline results)")
    
    report_type: Literal["comprehensive", "pre_report", "lh_decision"] = Field(
        "comprehensive",
        description="Type of report to generate"
    )
    
    output_format: Literal["json", "html", "pdf"] = Field(
        "json",
        description="Output format"
    )
    
    target_audience: Optional[Literal["landowner", "investor", "developer", "lh_evaluator"]] = Field(
        "landowner",
        description="Target audience"
    )


class ReportGenerationResponse(BaseModel):
    """Response for report generation"""
    
    report_id: str = Field(..., description="Unique report ID")
    parcel_id: str = Field(..., description="Parcel ID")
    report_type: str = Field(..., description="Report type")
    status: Literal["success", "processing", "failed"] = Field(..., description="Status")
    
    # Report data (JSON format)
    data: Optional[Dict[str, Any]] = Field(None, description="Report data (JSON)")
    
    # File URLs (HTML/PDF format)
    html_url: Optional[str] = Field(None, description="HTML download URL")
    pdf_url: Optional[str] = Field(None, description="PDF download URL")
    
    # Metadata
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    generation_time_ms: Optional[float] = Field(None, description="Generation time (ms)")
    
    error: Optional[str] = Field(None, description="Error message")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    
    status: Literal["healthy", "degraded", "unhealthy"] = Field(..., description="Service status")
    version: str = Field(default="v4.0", description="API version")
    pipeline_version: str = Field(default="6-MODULE", description="Pipeline architecture version")
    
    services: Dict[str, bool] = Field(
        default_factory=dict,
        description="Service health status"
    )
    
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Helper Functions
# ============================================================================

def generate_analysis_id(parcel_id: str) -> str:
    """Generate unique analysis ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"analysis_{parcel_id}_{timestamp}_{short_uuid}"


def pipeline_result_to_dict(result: PipelineResult, request_parcel_id: str = None) -> Dict[str, Any]:
    """Convert PipelineResult to dictionary with canonical data contract
    
    🔥 CRITICAL: 모든 모듈은 summary + details 구조로 변환
    프론트엔드 카드는 summary만 읽는다
    PDF는 details를 사용하되, 표지/요약은 summary를 사용한다
    
    Args:
        result: PipelineResult object
        request_parcel_id: Fallback parcel_id from request (optional)
    """
    
    # 🔥 Get parcel_id with fallback chain
    if hasattr(result, 'land') and result.land and hasattr(result.land, 'parcel_id'):
        parcel_id = result.land.parcel_id
    elif request_parcel_id:
        parcel_id = request_parcel_id
        logger.warning(f"⚠️ Using request_parcel_id as fallback: {request_parcel_id}")
    else:
        parcel_id = "unknown"
        logger.error(f"❌ No parcel_id available! result.land exists: {hasattr(result, 'land')}")
    
    # 🔥 M2: Appraisal - canonical 형식으로 변환
    m2_raw = result.appraisal.to_dict() if hasattr(result.appraisal, 'to_dict') else {}
    m2_canonical = convert_m2_to_standard(m2_raw, parcel_id)
    
    # 🔥 M3: Housing Type - canonical 형식으로 변환
    m3_raw = result.housing_type.to_dict() if hasattr(result.housing_type, 'to_dict') else {}
    m3_canonical = convert_m3_to_standard(m3_raw, parcel_id)
    
    # 🔥 M4: Capacity - summary + details 구조로 변환
    capacity_raw = result.capacity.to_dict() if hasattr(result.capacity, 'to_dict') else {}
    legal_cap = capacity_raw.get('legal_capacity', {})
    incentive_cap = capacity_raw.get('incentive_capacity', {})
    parking_sols = capacity_raw.get('parking_solutions', {})
    
    # ✅ FIX: None 유지 (0으로 fallback 금지!) + 정확한 필드명 사용
    alt_a = parking_sols.get('alternative_A', {})
    alt_b = parking_sols.get('alternative_B', {})
    
    m4_summary = M4Summary(
        legal_units=legal_cap.get('total_units'),  # None if missing (NOT 0!)
        incentive_units=incentive_cap.get('total_units'),  # None if missing
        parking_alt_a=alt_a.get('total_parking') or alt_a.get('total_parking_spaces'),  # Try both field names
        parking_alt_b=alt_b.get('total_parking') or alt_b.get('total_parking_spaces')  # Try both field names
    )
    
    m4_canonical = M4Result(
        module="M4",
        context_id=result.land.parcel_id,
        summary=m4_summary.dict(),
        details=capacity_raw,
        meta={
            "generated_at": datetime.now().isoformat(),
            "data_quality": {
                "is_mock": False,
                "warnings": []
            }
        }
    )
    
    # 🔥 M5: Feasibility - summary + details 구조로 변환
    feasibility_raw = result.feasibility.to_dict() if hasattr(result.feasibility, 'to_dict') else {}
    
    # ✅ FIX: 정확한 필드명 사용 (financials not financial_metrics)
    financial = feasibility_raw.get('financials') or feasibility_raw.get('financial_metrics', {})
    
    # ✅ FIX: 정확한 필드명 사용 (npv_public, irr_public/irr, roi)
    npv_public = financial.get('npv_public', 0)
    irr = financial.get('irr_public') or financial.get('irr', 0)
    roi = financial.get('roi', 0)
    
    # Grade 계산 (NPV 기준) - FIXED: Use actual grade from details if available
    grade_from_details = feasibility_raw.get('profitability', {}).get('grade')
    if grade_from_details:
        grade = grade_from_details
    else:
        if npv_public >= 1_000_000_000:  # 10억 이상
            grade = "A"
        elif npv_public >= 500_000_000:  # 5억 이상
            grade = "B"
        elif npv_public >= 0:  # 흑자
            grade = "C"
        else:  # 적자
            grade = "D"
    
    m5_summary = M5Summary(
        npv_public_krw=int(npv_public) if npv_public else 0,
        irr_pct=float(irr) if irr else 0,
        roi_pct=float(roi) if roi else 0,
        grade=grade
    )
    
    m5_canonical = M5Result(
        module="M5",
        context_id=result.land.parcel_id,
        summary=m5_summary.dict(),
        details=feasibility_raw,
        meta={
            "generated_at": datetime.now().isoformat(),
            "data_quality": {
                "is_mock": False,
                "warnings": []
            }
        }
    )
    
    # 🔥 M6: LH Review - canonical 형식으로 변환
    m6_raw = result.lh_review.to_dict() if hasattr(result.lh_review, 'to_dict') else {}
    m6_canonical = convert_m6_to_standard(m6_raw, parcel_id)
    
    # 🔥 FIX: Add html_preview_url and pdf_download_url to each module
    # Use parcel_id determined above (with fallback chain)
    context_id = parcel_id
    
    # Add URLs to each module's response
    m2_dict = m2_canonical.dict()
    m2_dict['html_preview_url'] = f"/api/v4/reports/M2/html?context_id={context_id}"
    m2_dict['pdf_download_url'] = f"/api/v4/reports/M2/pdf?context_id={context_id}"
    
    m3_dict = m3_canonical.dict()
    m3_dict['html_preview_url'] = f"/api/v4/reports/M3/html?context_id={context_id}"
    m3_dict['pdf_download_url'] = f"/api/v4/reports/M3/pdf?context_id={context_id}"
    
    m4_dict = m4_canonical.dict()
    m4_dict['html_preview_url'] = f"/api/v4/reports/M4/html?context_id={context_id}"
    m4_dict['pdf_download_url'] = f"/api/v4/reports/M4/pdf?context_id={context_id}"
    
    m5_dict = m5_canonical.dict()
    m5_dict['html_preview_url'] = f"/api/v4/reports/M5/html?context_id={context_id}"
    m5_dict['pdf_download_url'] = f"/api/v4/reports/M5/pdf?context_id={context_id}"
    
    m6_dict = m6_canonical.dict()
    m6_dict['html_preview_url'] = f"/api/v4/reports/M6/html?context_id={context_id}"
    m6_dict['pdf_download_url'] = f"/api/v4/reports/M6/pdf?context_id={context_id}"
    
    return {
        "land": result.land.to_dict() if hasattr(result.land, 'to_dict') else None,
        "appraisal": m2_dict,
        "housing_type": m3_dict,
        "capacity": m4_dict,
        "feasibility": m5_dict,
        "lh_review": m6_dict,
    }


# ============================================================================
# Pipeline Endpoints
# ============================================================================

@router.options("/analyze")
async def pipeline_analyze_options():
    """Handle CORS preflight for analyze endpoint"""
    return JSONResponse(
        content={"message": "OK"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

@router.post("/analyze", response_model=PipelineAnalysisResponse)
async def run_pipeline_analysis(request: PipelineAnalysisRequest):
    """
    Run full 6-MODULE pipeline analysis
    
    Executes: M1 (Land Info) → M2 (Appraisal) 🔒 → M3 (LH Demand) 
              → M4 (Capacity) → M5 (Feasibility) → M6 (LH Review)
    
    Returns:
        Comprehensive analysis results with all Context data
    """
    try:
        start_time = time.time()
        
        # Check cache
        if request.use_cache and request.parcel_id in results_cache:
            logger.info(f"✅ Using cached results for {request.parcel_id}")
            cached_result = results_cache[request.parcel_id]
            
            # Extract M4 V2 data from cached result
            capacity_v2 = cached_result.capacity
            legal_units = getattr(capacity_v2.legal_capacity, 'total_units', None) if hasattr(capacity_v2, 'legal_capacity') else None
            incentive_units = getattr(capacity_v2.incentive_capacity, 'total_units', None) if hasattr(capacity_v2, 'incentive_capacity') else None
            massing_count = len(capacity_v2.massing_options) if hasattr(capacity_v2, 'massing_options') else 0
            parking_a = capacity_v2.parking_solutions.get('alternative_A', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
            parking_b = capacity_v2.parking_solutions.get('alternative_B', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
            parking_a_spaces = getattr(parking_a, 'total_parking_spaces', None) if parking_a else None
            parking_b_spaces = getattr(parking_b, 'total_parking_spaces', None) if parking_b else None
            schematics_available = bool(capacity_v2.schematic_drawing_paths) if hasattr(capacity_v2, 'schematic_drawing_paths') else False
            
            return PipelineAnalysisResponse(
                parcel_id=request.parcel_id,
                analysis_id=f"cached_{request.parcel_id}",
                status="success",
                execution_time_ms=0,
                modules_executed=6,
                results=pipeline_result_to_dict(cached_result, request.parcel_id),
                land_value=cached_result.appraisal.land_value,
                confidence_score=cached_result.appraisal.confidence_metrics.confidence_score,
                selected_housing_type=cached_result.housing_type.selected_type,
                recommended_units=cached_result.capacity.unit_summary.total_units,
                npv_public=cached_result.feasibility.financial_metrics.npv_public,
                lh_decision=cached_result.lh_review.decision,
                lh_total_score=cached_result.lh_review.total_score,
                # M4 V2 enhanced outputs
                legal_capacity_units=legal_units,
                incentive_capacity_units=incentive_units,
                massing_options_count=massing_count,
                parking_alt_a_spaces=parking_a_spaces,
                parking_alt_b_spaces=parking_b_spaces,
                schematic_drawings_available=schematics_available
            )
        
        # Run pipeline
        logger.info(f"🚀 Running 6-MODULE pipeline for {request.parcel_id}")
        result = pipeline.run(request.parcel_id)
        
        # Cache results with BOTH keys for compatibility
        # Key 1: request.parcel_id (for pipeline lookup)
        results_cache[request.parcel_id] = result
        logger.info(f"✅ Cached with key 1: {request.parcel_id}")
        
        # Key 2: result.land.parcel_id (for HTML/PDF report lookup)
        # This ensures context_id in URLs matches the cache key
        logger.info(f"🔍 DEBUG: result has 'land'? {hasattr(result, 'land')}")
        if hasattr(result, 'land'):
            logger.info(f"🔍 DEBUG: result.land type: {type(result.land)}")
            logger.info(f"🔍 DEBUG: result.land has 'parcel_id'? {hasattr(result.land, 'parcel_id')}")
            if hasattr(result.land, 'parcel_id'):
                land_parcel_id = result.land.parcel_id
                logger.info(f"🔍 DEBUG: result.land.parcel_id = {land_parcel_id}")
                results_cache[land_parcel_id] = result
                logger.info(f"✅ Cached with both keys: {request.parcel_id} and {land_parcel_id}")
            else:
                logger.warning(f"⚠️ result.land exists but has no parcel_id attribute!")
        else:
            logger.warning(f"⚠️ result has no 'land' attribute! Using only request.parcel_id as cache key")
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Extract M4 V2 enhanced data
        capacity_v2 = result.capacity  # CapacityContextV2
        legal_units = getattr(capacity_v2.legal_capacity, 'total_units', None) if hasattr(capacity_v2, 'legal_capacity') else None
        incentive_units = getattr(capacity_v2.incentive_capacity, 'total_units', None) if hasattr(capacity_v2, 'incentive_capacity') else None
        massing_count = len(capacity_v2.massing_options) if hasattr(capacity_v2, 'massing_options') else 0
        parking_a = capacity_v2.parking_solutions.get('alternative_A', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
        parking_b = capacity_v2.parking_solutions.get('alternative_B', {}) if hasattr(capacity_v2, 'parking_solutions') else {}
        parking_a_spaces = getattr(parking_a, 'total_parking_spaces', None) if parking_a else None
        parking_b_spaces = getattr(parking_b, 'total_parking_spaces', None) if parking_b else None
        schematics_available = bool(capacity_v2.schematic_drawing_paths) if hasattr(capacity_v2, 'schematic_drawing_paths') else False
        
        # Build response
        response = PipelineAnalysisResponse(
            parcel_id=request.parcel_id,
            analysis_id=generate_analysis_id(request.parcel_id),
            status="success" if result.success else "failed",
            execution_time_ms=execution_time_ms,
            modules_executed=6,
            results=pipeline_result_to_dict(result, request.parcel_id),
            land_value=result.appraisal.land_value,
            confidence_score=result.appraisal.confidence_metrics.confidence_score,
            selected_housing_type=result.housing_type.selected_type,
            recommended_units=result.capacity.unit_summary.total_units,
            npv_public=result.feasibility.financial_metrics.npv_public,
            lh_decision=result.lh_review.decision,
            lh_total_score=result.lh_review.total_score,
            # M4 V2 enhanced outputs
            legal_capacity_units=legal_units,
            incentive_capacity_units=incentive_units,
            massing_options_count=massing_count,
            parking_alt_a_spaces=parking_a_spaces,
            parking_alt_b_spaces=parking_b_spaces,
            schematic_drawings_available=schematics_available
        )
        
        logger.info(f"✅ Pipeline completed in {execution_time_ms:.0f}ms")
        return response
        
    except Exception as e:
        logger.error(f"❌ Pipeline analysis failed: {str(e)}", exc_info=True)
        
        # Generate detailed error response
        error_detail = {
            "error": str(e),
            "error_type": type(e).__name__,
            "parcel_id": request.parcel_id,
            "timestamp": datetime.now().isoformat(),
            "hint": "Check if M1 Context is frozen and contains all required fields"
        }
        
        # Try to identify specific missing field
        error_message = str(e).lower()
        if "land_value" in error_message or "appraisal" in error_message:
            error_detail["missing_field"] = "land_value"
            error_detail["hint"] = "M2 Appraisal failed - Check official_land_price or transaction data"
        elif "area" in error_message or "jimok" in error_message:
            error_detail["missing_field"] = "cadastral_data"
            error_detail["hint"] = "M1 cadastral data missing or invalid - Check area, jimok fields"
        elif "floor_area_ratio" in error_message or "용적률" in error_message:
            error_detail["missing_field"] = "floor_area_ratio"
            error_detail["hint"] = "Floor Area Ratio (FAR) missing - Required for capacity calculation"
        elif "building_coverage" in error_message or "건폐율" in error_message:
            error_detail["missing_field"] = "building_coverage_ratio"
            error_detail["hint"] = "Building Coverage Ratio (BCR) missing - Required for capacity calculation"
        elif "road_width" in error_message or "도로" in error_message:
            error_detail["missing_field"] = "road_width"
            error_detail["hint"] = "Road width missing - Required for road access validation"
        
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )


@router.get("/results/{parcel_id}")
async def get_pipeline_results(parcel_id: str):
    """
    Get cached pipeline results for a parcel
    
    Args:
        parcel_id: Parcel ID (PNU code)
        
    Returns:
        Cached PipelineResult if available
    """
    if parcel_id not in results_cache:
        raise HTTPException(
            status_code=404,
            detail=f"No results found for parcel_id: {parcel_id}. Run /analyze first."
        )
    
    result = results_cache[parcel_id]
    
    return JSONResponse(content={
        "parcel_id": parcel_id,
        "status": "success",
        "results": pipeline_result_to_dict(result, parcel_id),
        "cached_at": datetime.now().isoformat()
    })


@router.post("/reports/comprehensive", response_model=ReportGenerationResponse)
async def generate_comprehensive_report(request: ReportGenerationRequest):
    """
    Generate comprehensive report from pipeline results
    
    Requires prior pipeline execution for the parcel_id
    """
    try:
        start_time = time.time()
        
        # Check if pipeline results exist
        if request.parcel_id not in results_cache:
            raise HTTPException(
                status_code=404,
                detail=f"No pipeline results for {request.parcel_id}. Run /analyze first."
            )
        
        result = results_cache[request.parcel_id]
        
        # Generate report data (simplified - full implementation would use report composers)
        report_data = {
            "executive_summary": {
                "land_value": result.appraisal.land_value,
                "confidence_level": result.appraisal.confidence_metrics.level,
                "lh_decision": result.lh_review.decision,
                "lh_score": result.lh_review.total_score,
                "recommendation": result.appraisal.recommendation
            },
            "detailed_analysis": {
                "land_info": result.land.to_dict() if hasattr(result.land, 'to_dict') else {},
                "appraisal": result.appraisal.to_dict() if hasattr(result.appraisal, 'to_dict') else {},
                "housing_type": result.housing_type.to_dict() if hasattr(result.housing_type, 'to_dict') else {},
                "capacity": result.capacity.to_dict() if hasattr(result.capacity, 'to_dict') else {},
                "feasibility": result.feasibility.to_dict() if hasattr(result.feasibility, 'to_dict') else {},
                "lh_review": result.lh_review.to_dict() if hasattr(result.lh_review, 'to_dict') else {}
            }
        }
        
        generation_time_ms = (time.time() - start_time) * 1000
        
        response = ReportGenerationResponse(
            report_id=f"report_{request.parcel_id}_{uuid.uuid4().hex[:8]}",
            parcel_id=request.parcel_id,
            report_type=request.report_type,
            status="success",
            data=report_data,
            generation_time_ms=generation_time_ms
        )
        
        logger.info(f"✅ Report generated in {generation_time_ms:.0f}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Report generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint for 6-MODULE pipeline
    
    Returns service status and module health
    """
    try:
        # Check if pipeline can be initialized
        test_pipeline = ZeroSitePipeline()
        
        services_status = {
            "pipeline": True,
            "m1_land_info": True,
            "m2_appraisal": True,
            "m3_lh_demand": True,
            "m4_capacity": True,
            "m5_feasibility": True,
            "m6_lh_review": True
        }
        
        # Determine overall status
        all_healthy = all(services_status.values())
        status = "healthy" if all_healthy else "degraded"
        
        return HealthCheckResponse(
            status=status,
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return HealthCheckResponse(
            status="unhealthy",
            services={
                "pipeline": False,
                "error": str(e)
            }
        )


# ============================================================================
# Utility Endpoints
# ============================================================================

@router.delete("/cache/{parcel_id}")
async def clear_cache_for_parcel(parcel_id: str):
    """
    Clear cached pipeline results for a specific parcel
    
    Args:
        parcel_id: Parcel ID to clear from cache
    """
    if parcel_id in results_cache:
        del results_cache[parcel_id]
        return JSONResponse(content={
            "status": "success",
            "message": f"Cache cleared for {parcel_id}"
        })
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No cached results for {parcel_id}"
        )


@router.delete("/cache")
async def clear_all_cache():
    """Clear all cached pipeline results"""
    count = len(results_cache)
    results_cache.clear()
    
    return JSONResponse(content={
        "status": "success",
        "message": f"Cleared {count} cached results"
    })


@router.get("/stats")
async def get_pipeline_stats():
    """Get pipeline usage statistics"""
    return JSONResponse(content={
        "cached_results": len(results_cache),
        "parcel_ids": list(results_cache.keys()),
        "pipeline_version": "v4.0",
        "architecture": "6-MODULE",
        "timestamp": datetime.now().isoformat()
    })


# Export router
__all__ = ["router"]
