"""
ZeroSite MVP Analysis API
=========================

Single endpoint for complete MVP flow:
Land Input → Building Scale → Unit Analysis → LH Evaluation → PDF Report

Author: ZeroSite Development Team
Date: 2025-12-06
Version: MVP 1.0
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import logging
import traceback

from app.services.mvp_orchestrator import get_orchestrator, MVPAnalysisResult
from app.report_generator_v11_complete import run_v11_engines
from app.adapters.v11_to_v75_adapter import convert_v11_analysis_to_v75_format
from app.services.lh_report_generator_v7_5_final import LHReportGeneratorV75Final

logger = logging.getLogger(__name__)

# Initialize Router
router = APIRouter(prefix="/api/mvp", tags=["ZeroSite MVP"])


# ============================================================================
# Request/Response Models
# ============================================================================

class MVPAnalyzeRequest(BaseModel):
    """MVP Analysis Request"""
    
    address: str = Field(
        ...,
        description="Property address",
        example="서울특별시 강남구 테헤란로 123"
    )
    land_area: float = Field(
        ...,
        gt=0,
        description="Land area in m²",
        example=850.0
    )
    land_appraisal_price: Optional[float] = Field(
        None,
        gt=0,
        description="Land appraisal price (optional)",
        example=4500000.0
    )
    zone_type: Optional[str] = Field(
        None,
        description="Zone type (auto-detected if not provided)",
        example="제2종일반주거지역"
    )
    output_format: Literal["json", "pdf"] = Field(
        default="json",
        description="Output format: 'json' for analysis only, 'pdf' for full report"
    )
    
    @validator('land_area')
    def validate_land_area(cls, v):
        if v < 100:
            raise ValueError("Land area must be at least 100 m²")
        if v > 100000:
            raise ValueError("Land area must be less than 100,000 m²")
        return v


class MVPAnalyzeResponse(BaseModel):
    """MVP Analysis Response"""
    
    ok: bool = Field(
        default=True,
        description="Success flag"
    )
    data: Dict[str, Any] = Field(
        ...,
        description="Analysis result data"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Response timestamp"
    )
    execution_time_ms: int = Field(
        ...,
        description="Total execution time in milliseconds"
    )


# ============================================================================
# Helper Functions
# ============================================================================

def create_error_response(
    code: str,
    message: str,
    status_code: int = 500,
    details: Any = None
):
    """Create standardized error response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error": {
                "code": code,
                "message": message,
                "details": details
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


# ============================================================================
# API Endpoints
# ============================================================================

@router.post(
    "/analyze",
    response_model=MVPAnalyzeResponse,
    summary="MVP Single-Parcel Analysis",
    description="""
    Complete MVP analysis flow:
    
    1. **Land Input**: Address → Coordinates → Zoning Rules
    2. **Building Scale**: Flexity-style calculation (BCR/FAR → GFA → Units)
    3. **Unit Analysis**: v11.0 AI engine (unit type recommendation)
    4. **LH Evaluation**: v11.0 LH Score + Decision
    5. **Report**: v7.5 design + v11.0 data (optional PDF)
    
    **Input** (4 fields):
    - address (required)
    - land_area (required, m²)
    - land_appraisal_price (optional)
    - zone_type (optional, auto-detected)
    
    **Output** (JSON):
    - land_input
    - coordinates
    - zoning_info
    - building_scale (GFA, units, floors, parking)
    - unit_analysis (v11.0)
    - lh_evaluation (v11.0, score/grade/decision)
    
    **Test Case**:
    ```json
    {
      "address": "서울특별시 강남구 테헤란로 123",
      "land_area": 850,
      "land_appraisal_price": 4500000,
      "zone_type": "제2종일반주거지역"
    }
    ```
    
    **Expected**:
    - BCR: 60%
    - FAR: 250%
    - Units: ~28
    - Floors: 4-7
    - LH Score: 60-80 (Grade C-B)
    """,
    status_code=status.HTTP_200_OK
)
async def mvp_analyze(request: MVPAnalyzeRequest):
    """
    MVP Complete Analysis
    
    Single endpoint that orchestrates:
    1. Land input validation
    2. Building scale calculation
    3. v11.0 AI analysis
    4. Optional PDF generation
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info("="*80)
        logger.info(f"🚀 MVP Analysis Request: {request.address}")
        logger.info("="*80)
        
        # ================================================================
        # STEP 1-3: MVP Orchestrator (Land + Building Scale)
        # ================================================================
        logger.info("\n📊 Running MVP Orchestrator...")
        orchestrator = get_orchestrator()
        
        mvp_result = await orchestrator.analyze(
            address=request.address,
            land_area=request.land_area,
            land_appraisal_price=request.land_appraisal_price,
            zone_type=request.zone_type
        )
        
        logger.info("✅ MVP Orchestrator Complete")
        
        # ================================================================
        # STEP 4-5: v11.0 AI Engines (Unit Analysis + LH Evaluation)
        # ================================================================
        logger.info("\n🤖 Running v11.0 AI Engines...")
        
        # Prepare analysis_result for v11 engines
        analysis_result = {
            "land_area": request.land_area,
            "zone_type": mvp_result.building_scale.zone_type,
            "building_coverage_ratio": mvp_result.building_scale.building_coverage_ratio,
            "floor_area_ratio": mvp_result.building_scale.floor_area_ratio,
            "unit_count": mvp_result.building_scale.max_units,
            "floors": mvp_result.building_scale.floor_count,
            "parking_spaces": mvp_result.building_scale.parking_required,
            "total_gfa": mvp_result.building_scale.total_gross_area,
            "residential_gfa": mvp_result.building_scale.residential_gfa,
            "latitude": mvp_result.coordinates["latitude"],
            "longitude": mvp_result.coordinates["longitude"]
        }
        
        # Run v11.0 engines
        v11_result = run_v11_engines(
            address=request.address,
            land_area=request.land_area,
            land_appraisal_price=request.land_appraisal_price or 0,
            zone_type=mvp_result.building_scale.zone_type,
            analysis_result=analysis_result
        )
        
        # Extract unit analysis and LH evaluation
        mvp_result.unit_analysis = {
            "recommended_type": v11_result.get("unit_analysis", {}).get("recommended_type"),
            "score_matrix": v11_result.get("unit_analysis", {}).get("score_matrix"),
            "reasoning": v11_result.get("unit_analysis", {}).get("reasoning")
        }
        
        mvp_result.lh_evaluation = {
            "total_score": v11_result.get("lh_score", {}).get("total_score"),
            "grade": v11_result.get("lh_score", {}).get("grade"),
            "breakdown": v11_result.get("lh_score", {}).get("breakdown"),
            "decision": v11_result.get("decision", {}).get("decision"),
            "confidence": v11_result.get("decision", {}).get("confidence"),
            "key_reasons": v11_result.get("decision", {}).get("primary_reason")
        }
        
        logger.info("✅ v11.0 AI Engines Complete")
        logger.info(f"   LH Score: {mvp_result.lh_evaluation['total_score']}/100")
        logger.info(f"   Grade: {mvp_result.lh_evaluation['grade']}")
        logger.info(f"   Decision: {mvp_result.lh_evaluation['decision']}")
        
        # ================================================================
        # RESPONSE: JSON or PDF
        # ================================================================
        
        end_time = datetime.utcnow()
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        if request.output_format == "pdf":
            logger.info("\n📄 Generating PDF Report...")
            
            # Convert to v7.5 format
            v75_data = convert_v11_analysis_to_v75_format(
                address=request.address,
                land_area=request.land_area,
                land_appraisal_price=request.land_appraisal_price or 0,
                zone_type=mvp_result.building_scale.zone_type,
                v11_analysis_result=v11_result
            )
            
            # Generate v7.5 report
            v75_generator = LHReportGeneratorV75Final()
            report_result = v75_generator.run(
                option=4,  # Ultra-Professional
                tone="administrative",
                cover="black-minimal",
                pages=50,
                address=request.address,
                land_area=request.land_area,
                land_appraisal_price=request.land_appraisal_price or 0,
                data=v75_data
            )
            
            if report_result.get("success"):
                html_content = report_result["html"]
                logger.info(f"✅ PDF Report Generated ({len(html_content):,} chars)")
                
                # Return HTML (PDF conversion can be done client-side or with additional endpoint)
                return Response(
                    content=html_content,
                    media_type="text/html",
                    headers={
                        "Content-Disposition": f"inline; filename=zerosite_mvp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    }
                )
            else:
                logger.error("❌ PDF generation failed")
                raise HTTPException(
                    status_code=500,
                    detail="PDF generation failed"
                )
        
        # JSON response
        response_data = orchestrator.to_dict(mvp_result)
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ MVP Analysis Complete ({execution_time_ms}ms)")
        logger.info("="*80)
        
        return MVPAnalyzeResponse(
            ok=True,
            data=response_data,
            execution_time_ms=execution_time_ms
        )
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        return create_error_response(
            code="VALIDATION_ERROR",
            message=str(e),
            status_code=400
        )
    
    except Exception as e:
        logger.error(f"❌ Analysis error: {str(e)}")
        logger.error(traceback.format_exc())
        return create_error_response(
            code="ANALYSIS_ERROR",
            message="Analysis failed",
            status_code=500,
            details=str(e)
        )


@router.get(
    "/config",
    summary="Get MVP Configuration",
    description="Get current MVP configuration (unit area, parking ratios, etc.)"
)
async def get_mvp_config():
    """Get current MVP configuration"""
    from app.config.mvp_config import get_mvp_config
    
    config = get_mvp_config()
    
    return {
        "ok": True,
        "config": {
            "building": {
                "default_unit_area": config.building.default_unit_area,
                "residential_ratio": config.building.residential_ratio,
                "commercial_ratio": config.building.commercial_ratio,
                "parking_ratios": config.building.parking_ratios,
                "max_floors_by_zone": config.building.max_floors_by_zone,
                "min_units": config.building.min_units
            },
            "report": {
                "default_pages": config.default_report_pages,
                "timeout": config.report_generation_timeout
            }
        }
    }


@router.post(
    "/config/update",
    summary="Update MVP Configuration",
    description="Update MVP configuration values (requires admin)"
)
async def update_mvp_config(updates: Dict[str, Any]):
    """Update MVP configuration"""
    from app.config.mvp_config import update_mvp_config
    
    try:
        updated_config = update_mvp_config(**updates)
        
        return {
            "ok": True,
            "message": "Configuration updated successfully",
            "updated_fields": list(updates.keys())
        }
    except Exception as e:
        logger.error(f"❌ Config update error: {str(e)}")
        return create_error_response(
            code="CONFIG_UPDATE_ERROR",
            message="Failed to update configuration",
            status_code=500,
            details=str(e)
        )
