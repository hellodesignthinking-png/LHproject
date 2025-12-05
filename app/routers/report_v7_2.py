"""
ZeroSite Report API v7.2
New endpoints for v7.2 Report Engine integration
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from app.services.report_engine_v7_2 import ReportEngineV72, generate_v72_report
from app.services.analysis_engine import AnalysisEngine
from app.schemas import LandAnalysisRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v7.2", tags=["Reports v7.2"])


class ReportV72Request(BaseModel):
    """v7.2 Report generation request"""
    analysis_id: Optional[str] = None
    address: str
    land_area: float
    unit_type: Optional[str] = None
    report_type: str = "comprehensive"  # comprehensive, executive, technical
    format: str = "markdown"  # markdown, html, json


class ReportV72Response(BaseModel):
    """v7.2 Report generation response"""
    success: bool
    version: str
    report_type: str
    format: str
    content: str
    metadata: Dict[str, Any]
    statistics: Dict[str, Any]
    generated_at: str


@router.post("/generate-report", response_model=ReportV72Response)
async def generate_report_v72(request: ReportV72Request):
    """
    Generate ZeroSite v7.2 report with real engine integration
    
    Features:
    - Real engine output (no mock data)
    - 120+ v7.2 field mapping
    - Type Demand v3.1, GeoOptimizer v3.1, Multi-Parcel v3.0
    - API fallback: API → cache → failover → safe mock
    - 3 report types: comprehensive, executive, technical
    - 3 formats: markdown, html, json
    
    Args:
        request: Report generation request
    
    Returns:
        Complete report with metadata and statistics
    """
    try:
        logger.info(f"🔄 v7.2 Report generation request: {request.address}")
        
        # Step 1: Run land analysis using v7.2 engine
        logger.info("🔄 Step 1: Running land analysis...")
        engine = AnalysisEngine()
        
        # Create analysis request
        analysis_request = LandAnalysisRequest(
            address=request.address,
            land_area=request.land_area,
            unit_type=request.unit_type
        )
        
        # Get analysis result
        engine_output = await engine.analyze_land(analysis_request)
        
        # Step 2: Generate v7.2 report
        logger.info(f"🔄 Step 2: Generating {request.report_type} report in {request.format} format...")
        
        report_engine = ReportEngineV72()
        report_result = report_engine.generate_report(
            engine_output=engine_output,
            report_type=request.report_type,
            format=request.format
        )
        
        if not report_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {report_result.get('error', 'Unknown error')}"
            )
        
        # Step 3: Return response
        logger.info(f"✅ v7.2 Report generated successfully: {report_result['statistics']['total_characters']} chars")
        
        return ReportV72Response(
            success=report_result['success'],
            version=report_result['version'],
            report_type=report_result['report_type'],
            format=report_result['format'],
            content=report_result['content'],
            metadata=report_result['metadata'],
            statistics=report_result['statistics'],
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ v7.2 Report generation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Report generation failed",
                "message": str(e),
                "version": "7.2"
            }
        )


@router.post("/analyze-and-report")
async def analyze_and_report_v72(request: ReportV72Request):
    """
    Complete workflow: Analyze land + Generate v7.2 report in one call
    
    This endpoint combines land analysis and report generation for convenience.
    
    Returns:
        Both analysis result and generated report
    """
    try:
        logger.info(f"🔄 v7.2 Analyze & Report: {request.address}")
        
        # Step 1: Analysis
        engine = AnalysisEngine()
        analysis_request = LandAnalysisRequest(
            address=request.address,
            land_area=request.land_area,
            unit_type=request.unit_type
        )
        engine_output = await engine.analyze_land(analysis_request)
        
        # Step 2: Report
        report_result = generate_v72_report(
            engine_output=engine_output,
            report_type=request.report_type,
            format=request.format
        )
        
        return {
            "success": True,
            "version": "7.2",
            "analysis": engine_output,
            "report": report_result,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Analyze & Report error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Analysis and report generation failed",
                "message": str(e)
            }
        )


@router.get("/report-types")
async def get_report_types():
    """
    Get available report types and formats for v7.2
    """
    return {
        "version": "7.2",
        "report_types": [
            {
                "type": "comprehensive",
                "description": "Full 10+ section analysis (500+ lines)",
                "sections": [
                    "Executive Summary",
                    "Basic Info",
                    "LH Assessment",
                    "Type Demand v3.1",
                    "GeoOptimizer v3.1",
                    "Multi-Parcel v3.0 (if applicable)",
                    "Risk Analysis",
                    "Development Plan",
                    "Performance Stats",
                    "Conclusion"
                ]
            },
            {
                "type": "executive",
                "description": "2-3 page executive summary",
                "sections": ["Key Judgment", "Main Indicators"]
            },
            {
                "type": "technical",
                "description": "Technical specs and raw data",
                "sections": ["Engine Config", "Raw Data JSON"]
            }
        ],
        "formats": ["markdown", "html", "json"],
        "engines": {
            "type_demand": "v3.1",
            "geo_optimizer": "v3.1",
            "multi_parcel": "v3.0"
        }
    }


@router.get("/health")
async def health_check_v72():
    """
    v7.2 Report Engine health check
    """
    try:
        # Test field mapper
        from app.services.report_field_mapper_v7_2 import ReportFieldMapperV72
        mapper = ReportFieldMapperV72()
        
        # Test report engine
        engine = ReportEngineV72()
        
        return {
            "status": "healthy",
            "version": "7.2",
            "components": {
                "field_mapper": "ok",
                "report_engine": "ok"
            },
            "features": {
                "real_engine_output": True,
                "mock_data_removed": True,
                "field_mapping_count": "120+",
                "api_fallback": True,
                "cache_integration": True
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
