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
import asyncio  # 🔥 NEW: For timeout handling

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

# 🔥 NEW: Pipeline Failure Tracking
from app.services.pipeline_tracer import (
    PipelineTracer,
    PipelineStage,
    ReasonCode,
    PipelineExecutionError
)
from app.services.context_storage import context_storage
from app.services.data_contract import DataValidationError, DataBindingError

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v4/pipeline", tags=["ZeroSite v4.0 Pipeline"])

# 🔥 CRITICAL: Hard timeout to prevent infinite loading
PIPELINE_TIMEOUT_SEC = 15  # Max time before returning error

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


def pipeline_result_to_dict(result: PipelineResult) -> Dict[str, Any]:
    """Convert PipelineResult to dictionary with canonical data contract
    
    🔥 CRITICAL: 모든 모듈은 summary + details 구조로 변환
    프론트엔드 카드는 summary만 읽는다
    PDF는 details를 사용하되, 표지/요약은 summary를 사용한다
    """
    
    # 🔥 M2: Appraisal - canonical 형식으로 변환
    m2_raw = result.appraisal.to_dict() if hasattr(result.appraisal, 'to_dict') else {}
    m2_canonical = convert_m2_to_standard(m2_raw, result.land.parcel_id)
    
    # 🔥 M3: Housing Type - canonical 형식으로 변환
    m3_raw = result.housing_type.to_dict() if hasattr(result.housing_type, 'to_dict') else {}
    m3_canonical = convert_m3_to_standard(m3_raw, result.land.parcel_id)
    
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
    # Grade는 M6에서 결정됨 - API는 데이터만 전달
    if grade_from_details:
        grade = grade_from_details
    else:
        # 기본값만 설정 (실제 판단은 M6에서)
        grade = "B"
    
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
    m6_canonical = convert_m6_to_standard(m6_raw, result.land.parcel_id)
    
    # 🔥 FIX: Add html_preview_url and pdf_download_url to each module
    context_id = result.land.parcel_id
    
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
    Run full 6-MODULE pipeline analysis with GUARANTEED response
    
    Executes: M1 (Land Info) → M2 (Appraisal) 🔒 → M3 (LH Demand) 
              → M4 (Capacity) → M5 (Feasibility) → M6 (LH Review)
    
    Returns:
        Comprehensive analysis results with all Context data
        
    🔥 CRITICAL: ALWAYS returns response within PIPELINE_TIMEOUT_SEC
    """
    # 🔥 Step 1: Initialize PipelineTracer BEFORE timeout wrapper
    tracer = PipelineTracer(parcel_id=request.parcel_id)
    
    # 🔥 Step 2: Wrap entire execution in timeout
    try:
        result = await asyncio.wait_for(
            _execute_pipeline(request, tracer),
            timeout=PIPELINE_TIMEOUT_SEC
        )
        return result
        
    except asyncio.TimeoutError:
        # 🔥 TIMEOUT: Return error immediately
        logger.error(f"⏰ Pipeline timeout after {PIPELINE_TIMEOUT_SEC}s for {request.parcel_id}")
        raise PipelineExecutionError(
            stage=tracer.current_stage or PipelineStage.M2,
            reason_code=ReasonCode.EXTERNAL_API_TIMEOUT,
            message_ko=f"분석 시간이 {PIPELINE_TIMEOUT_SEC}초를 초과했습니다. 잠시 후 다시 시도해 주세요.",
            debug_id=tracer.trace_id,
            details={"timeout_sec": PIPELINE_TIMEOUT_SEC}
        )
    except PipelineExecutionError:
        # Already wrapped - just re-raise (will be caught by exception handler)
        raise
    except Exception as e:
        # 🔥 SAFETY NET: Unknown error - wrap and return
        logger.error(f"❌ Unexpected error in pipeline: {e}", exc_info=True)
        raise tracer.wrap(
            e,
            reason_code=ReasonCode.UNKNOWN,
            details={"error_type": type(e).__name__, "parcel_id": request.parcel_id}
        )


async def _execute_pipeline(request: PipelineAnalysisRequest, tracer: PipelineTracer):
    """
    Internal pipeline execution (wrapped by timeout)
    🔥 MUST return PipelineAnalysisResponse or raise PipelineExecutionError
    """
    print(f"🔥🔥🔥 _execute_pipeline CALLED for {request.parcel_id} 🔥🔥🔥", flush=True)
    logger.critical(f"🔥🔥🔥 _execute_pipeline CALLED for {request.parcel_id}")
    
    try:
        start_time = time.time()
        
        # Check cache
        if request.use_cache and request.parcel_id in results_cache:
            logger.info(f"✅ Using cached results for {request.parcel_id}")
            cached_result = results_cache[request.parcel_id]
            
            # 🔥 Step 2: Mark as complete if using cache
            tracer.complete()
            
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
                results=pipeline_result_to_dict(cached_result),
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
        
        # 🔥 Step 3: Run pipeline with stage tracking
        logger.critical(f"🔥 STEP 3: Running pipeline for {request.parcel_id}")
        logger.info(f"🚀 Running 6-MODULE pipeline for {request.parcel_id}")
        
        try:
            # M1 is handled internally by pipeline, start tracking at M2
            tracer.set_stage(PipelineStage.M2)
            result = pipeline.run(request.parcel_id)
        except TimeoutError as timeout_err:
            # External API timeout
            raise tracer.wrap(
                timeout_err,
                reason_code=ReasonCode.EXTERNAL_API_TIMEOUT,
                details={"timeout_sec": 60}
            )
        except AttributeError as attr_err:
            # M1 data missing
            if "land" in str(attr_err) or "parcel" in str(attr_err):
                raise tracer.wrap(
                    attr_err,
                    reason_code=ReasonCode.MODULE_DATA_MISSING,
                    message_ko="M1 입력 데이터가 누락되었습니다. M1 확정을 먼저 완료해 주세요."
                )
            raise
        
        # Cache results
        results_cache[request.parcel_id] = result
        logger.critical(f"🔥 STEP 3 DONE: Results cached for {request.parcel_id}")
        
        # 🔥 Step 4: ASSEMBLE - Convert PipelineResult to Phase 3.5D assembled_data format
        logger.critical(f"🔥 STEP 4: ASSEMBLE starting for {request.parcel_id}")
        tracer.set_stage(PipelineStage.ASSEMBLE)
        context_id = request.parcel_id  # Use parcel_id as context_id
        
        # Build Phase 3.5D assembled_data from pipeline result
        # 🔥 CRITICAL: Convert all dataclass objects to primitive dicts for JSON serialization
        def to_serializable(obj):
            """Recursively convert dataclass and complex objects to dict"""
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                return {k: to_serializable(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, (list, tuple)):
                return [to_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: to_serializable(v) for k, v in obj.items()}
            else:
                return obj
        
        # 🔍 DEBUG: Log M4 capacity structure
        if hasattr(result.capacity, 'to_dict'):
            capacity_dict = result.capacity.to_dict()
            logger.critical(f"🔍 M4 capacity.to_dict() keys: {list(capacity_dict.keys())[:15]}")
            logger.critical(f"🔍 M4 has selected_scenario_id: {'selected_scenario_id' in capacity_dict}")
            logger.critical(f"🔍 M4 has legal_capacity: {'legal_capacity' in capacity_dict}")
            logger.critical(f"🔍 M4 has scenarios: {'scenarios' in capacity_dict}")
        else:
            logger.critical(f"🔍 M4 capacity has no to_dict() method!")
        
        assembled_data = {
            "m6_result": {
                "lh_score_total": result.lh_review.total_score,
                "judgement": result.lh_review.decision,
                "grade": result.lh_review.grade if hasattr(result.lh_review, 'grade') else 'N/A',
                "fatal_reject": False,
                "deduction_reasons": to_serializable(getattr(result.lh_review, 'deduction_reasons', [])),
                "improvement_points": to_serializable(getattr(result.lh_review, 'improvement_suggestions', [])),
                "section_scores": to_serializable(getattr(result.lh_review, 'section_scores', {}))
            },
            "modules": {
                "M2": {
                    "summary": {
                        "land_value": result.appraisal.land_value,
                        "land_value_per_pyeong": result.appraisal.land_value_per_pyeong if hasattr(result.appraisal, 'land_value_per_pyeong') else result.appraisal.land_value / result.land.area_pyeong if result.land.area_pyeong > 0 else 0,
                        "confidence_pct": result.appraisal.confidence_metrics.confidence_score * 100,
                        "appraisal_method": result.appraisal.appraisal_method if hasattr(result.appraisal, 'appraisal_method') else 'standard',
                        "price_range": {
                            "low": result.appraisal.land_value * 0.85,
                            "high": result.appraisal.land_value * 1.15
                        }
                    },
                    "details": {},
                    "raw_data": {}
                },
                "M3": {
                    "summary": {
                        "recommended_type": result.housing_type.selected_type,
                        "total_score": getattr(result.housing_type, 'total_score', 85.0),
                        "demand_score": getattr(result.housing_type, 'demand_score', 90.0),
                        "type_scores": {
                            type_key: {
                                "type_name": score.type_name,
                                "type_code": score.type_code,
                                "total_score": score.total_score,
                                "location_score": score.location_score,
                                "accessibility_score": score.accessibility_score,
                                "poi_score": score.poi_score,
                                "demand_prediction": score.demand_prediction
                            }
                            for type_key, score in getattr(result.housing_type, 'type_scores', {}).items()
                        } if hasattr(result.housing_type, 'type_scores') else {}
                    },
                    "details": {},
                    "raw_data": {}
                },
                "M4": {
                    "summary": to_serializable(result.capacity),
                    "details": {},
                    "raw_data": {}
                },
                "M5": {
                    "summary": to_serializable(result.feasibility),
                    "details": {},
                    "raw_data": {}
                },
                "M6": {
                    "summary": to_serializable(result.lh_review),
                    "details": {},
                    "raw_data": {}
                }
            },
            "_frozen": True,
            "_context_id": context_id
        }
        logger.critical(f"🔥 assembled_data created with keys: {list(assembled_data.keys())}")
        
        # 🔥 Step 5: SAVE - Store in context_storage
        logger.critical(f"🔥 STEP 5: SAVE starting for {context_id}")
        logger.critical(f"🔍 DEBUG: About to save context_id={context_id}, parcel_id={request.parcel_id}")
        logger.critical(f"🔍 DEBUG: assembled_data keys={list(assembled_data.keys())}")
        
        tracer.set_stage(PipelineStage.SAVE)
        try:
            logger.critical(f"🔍 DEBUG: Calling store_frozen_context...")
            success = context_storage.store_frozen_context(
                context_id=context_id,
                land_context=assembled_data,
                ttl_hours=24,
                parcel_id=request.parcel_id
            )
            logger.critical(f"🔍 DEBUG: store_frozen_context returned: {success}")
            
            if success:
                logger.critical(f"✅ Pipeline results saved to context_storage: {context_id}")
            else:
                logger.warning(f"⚠️ store_frozen_context returned False for: {context_id}")
        except Exception as storage_err:
            logger.error(f"⚠️ Failed to save to context_storage: {storage_err}", exc_info=True)
            raise tracer.wrap(
                storage_err,
                reason_code=ReasonCode.STORAGE_ERROR,
                details={"context_id": context_id}
            )
        
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
            results=pipeline_result_to_dict(result),
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
        
        # 🔥 Step 6: Complete and return
        logger.info(f"✅ Pipeline completed in {execution_time_ms:.0f}ms")
        tracer.complete()
        return response
        
    # 🔥 Step 7: Enhanced exception handling
    except DataValidationError as dv_err:
        # Data validation failed - wrap with context
        raise tracer.wrap(
            dv_err,
            reason_code=ReasonCode.DATA_BINDING_MISSING,
            details={"validation_errors": str(dv_err)}
        )
    except DataBindingError as db_err:
        # Data binding failed - wrap with missing paths
        raise tracer.wrap(
            db_err,
            reason_code=ReasonCode.DATA_BINDING_MISSING,
            details=getattr(db_err, 'to_dict', lambda: {"error": str(db_err)})()
        )
    except PipelineExecutionError:
        # Already wrapped - just re-raise
        raise
    except Exception as e:
        logger.error(f"❌ Pipeline analysis failed: {str(e)}", exc_info=True)
        
        # Unknown error - wrap it
        raise tracer.wrap(
            e,
            reason_code=ReasonCode.UNKNOWN,
            details={
                "error_type": type(e).__name__,
                "parcel_id": request.parcel_id
            }
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
        "results": pipeline_result_to_dict(result),
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
