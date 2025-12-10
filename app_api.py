"""
ZeroSite v3 Report Generation API

FastAPI-based REST API for generating Expert Edition v3 reports.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 3.0.0 - PRODUCTION
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime
from pathlib import Path

from generate_v3_full_report import V3FullReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zerosite_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ZeroSite Report Generation API",
    description="Generate Expert Edition v3 reports with interactive charts",
    version="3.0.0",
    docs_url="/api/v3/docs",
    redoc_url="/api/v3/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize report generator
generator = V3FullReportGenerator()

# Request/Response Models
class LandParams(BaseModel):
    bcr: float = Field(..., description="건폐율 (%)", example=60.0)
    far: float = Field(..., description="용적률 (%)", example=200.0)
    max_floors: int = Field(..., description="최대 층수", example=8)
    zone_type: str = Field(..., description="용도지역", example="제2종일반주거지역")


class ReportRequest(BaseModel):
    address: str = Field(..., description="프로젝트 주소", example="서울특별시 강남구 테헤란로 123")
    land_area: float = Field(..., description="토지 면적 (㎡)", example=1000.0)
    land_params: LandParams
    unit_type: str = Field(default="청년", description="공급 유형", example="청년")
    land_price_per_sqm: float = Field(default=5_000_000, description="토지 단가 (원/㎡)", example=5000000)
    
    class Config:
        schema_extra = {
            "example": {
                "address": "서울특별시 강남구 테헤란로 123",
                "land_area": 1000.0,
                "land_params": {
                    "bcr": 60.0,
                    "far": 200.0,
                    "max_floors": 8,
                    "zone_type": "제2종일반주거지역"
                },
                "unit_type": "청년",
                "land_price_per_sqm": 5000000
            }
        }


class ReportResponse(BaseModel):
    status: str = Field(..., description="Status of request", example="success")
    message: str = Field(..., description="Response message", example="Report generated successfully")
    report_id: Optional[str] = Field(None, description="Report ID for retrieval")
    file_path: Optional[str] = Field(None, description="Path to generated file")
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")


class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    version: str = Field(..., example="3.0.0")
    timestamp: str = Field(..., example="2025-12-10T13:54:19")
    reports_generated: int = Field(..., example=42)


# Global statistics
stats = {
    "reports_generated": 0,
    "total_generation_time": 0.0,
    "errors": 0
}


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """API root endpoint with welcome message"""
    return """
    <html>
        <head><title>ZeroSite API v3</title></head>
        <body style="font-family: sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🎯 ZeroSite Report Generation API v3</h1>
            <p><strong>Status:</strong> <span style="color: green;">✅ PRODUCTION READY</span></p>
            <p><strong>Version:</strong> 3.0.0</p>
            
            <h2>📚 Documentation</h2>
            <ul>
                <li><a href="/api/v3/docs">Swagger UI (Interactive API Docs)</a></li>
                <li><a href="/api/v3/redoc">ReDoc (Alternative Docs)</a></li>
                <li><a href="/api/v3/health">Health Check</a></li>
            </ul>
            
            <h2>🚀 Quick Start</h2>
            <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px;">
# Generate HTML Report
curl -X POST "http://localhost:8000/api/v3/report/generate" \\
  -H "Content-Type: application/json" \\
  -d '{ "address": "서울특별시 강남구 테헤란로 123", "land_area": 1000, ... }'

# Generate PDF Report
curl -X POST "http://localhost:8000/api/v3/report/generate-pdf" \\
  -H "Content-Type: application/json" \\
  -d '{ ... }' > report.pdf
            </pre>
            
            <h2>📊 Features</h2>
            <ul>
                <li>✅ Phase 11-14 Integration (LH Policy, Narrative, Timeline)</li>
                <li>✅ 5 Interactive Plotly Charts</li>
                <li>✅ McKinsey 2x2 Risk Matrix</li>
                <li>✅ Tornado Chart (Sensitivity Analysis)</li>
                <li>✅ HTML + PDF Output</li>
                <li>✅ < 2s Generation Time</li>
            </ul>
        </body>
    </html>
    """


@app.get("/api/v3/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthResponse: API health status
    """
    return HealthResponse(
        status="healthy",
        version="3.0.0",
        timestamp=datetime.now().isoformat(),
        reports_generated=stats["reports_generated"]
    )


@app.post("/api/v3/report/generate", response_class=HTMLResponse)
async def generate_report(request: ReportRequest):
    """
    Generate v3 Full Complete Report (HTML)
    
    Args:
        request: ReportRequest with project details
        
    Returns:
        HTMLResponse: Generated report as HTML
        
    Raises:
        HTTPException: If report generation fails
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Generating report for: {request.address}")
        
        # Generate report
        html_content = generator.generate_report(
            address=request.address,
            land_area=request.land_area,
            land_params=request.land_params.dict(),
            unit_type=request.unit_type,
            land_price_per_sqm=request.land_price_per_sqm
        )
        
        # Update statistics
        generation_time = (datetime.now() - start_time).total_seconds()
        stats["reports_generated"] += 1
        stats["total_generation_time"] += generation_time
        
        logger.info(f"Report generated in {generation_time:.2f}s")
        
        return HTMLResponse(
            content=html_content,
            headers={
                "X-Generation-Time": str(generation_time),
                "X-Report-Version": "3.0.0"
            }
        )
        
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"Report generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.post("/api/v3/report/generate-pdf", response_class=FileResponse)
async def generate_pdf_report(request: ReportRequest):
    """
    Generate v3 Full Complete Report (PDF)
    
    Args:
        request: ReportRequest with project details
        
    Returns:
        FileResponse: Generated report as PDF
        
    Raises:
        HTTPException: If report generation fails
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Generating PDF report for: {request.address}")
        
        # Generate HTML
        html_content = generator.generate_report(
            address=request.address,
            land_area=request.land_area,
            land_params=request.land_params.dict(),
            unit_type=request.unit_type,
            land_price_per_sqm=request.land_price_per_sqm
        )
        
        # Save HTML
        output_path = generator.save_report(html_content)
        
        # Convert to PDF
        try:
            from weasyprint import HTML
            pdf_path = output_path.replace(".html", ".pdf")
            HTML(output_path).write_pdf(pdf_path)
            
            generation_time = (datetime.now() - start_time).total_seconds()
            stats["reports_generated"] += 1
            stats["total_generation_time"] += generation_time
            
            logger.info(f"PDF report generated in {generation_time:.2f}s")
            
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename=f"zerosite_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                headers={
                    "X-Generation-Time": str(generation_time),
                    "X-Report-Version": "3.0.0"
                }
            )
            
        except ImportError:
            raise HTTPException(
                status_code=501,
                detail="PDF generation not available. Install weasyprint: pip install weasyprint"
            )
            
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"PDF report generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@app.post("/api/v3/report/generate-async", response_model=ReportResponse)
async def generate_report_async(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    Generate report asynchronously (for large reports)
    
    Args:
        request: ReportRequest with project details
        background_tasks: FastAPI background tasks
        
    Returns:
        ReportResponse: Job status and report ID
    """
    report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def generate_in_background(report_id: str, request: ReportRequest):
        try:
            html_content = generator.generate_report(
                address=request.address,
                land_area=request.land_area,
                land_params=request.land_params.dict(),
                unit_type=request.unit_type,
                land_price_per_sqm=request.land_price_per_sqm
            )
            output_path = generator.save_report(html_content, f"generated_reports/{report_id}.html")
            logger.info(f"Background report generated: {report_id}")
        except Exception as e:
            logger.error(f"Background generation failed: {str(e)}")
    
    background_tasks.add_task(generate_in_background, report_id, request)
    
    return ReportResponse(
        status="processing",
        message="Report generation started in background",
        report_id=report_id
    )


@app.get("/api/v3/stats", response_class=JSONResponse)
async def get_statistics():
    """
    Get API usage statistics
    
    Returns:
        JSONResponse: API statistics
    """
    avg_time = (stats["total_generation_time"] / stats["reports_generated"] 
                if stats["reports_generated"] > 0 else 0)
    
    return JSONResponse({
        "reports_generated": stats["reports_generated"],
        "total_generation_time": round(stats["total_generation_time"], 2),
        "average_generation_time": round(avg_time, 2),
        "errors": stats["errors"],
        "success_rate": round(
            (stats["reports_generated"] / (stats["reports_generated"] + stats["errors"]) * 100)
            if (stats["reports_generated"] + stats["errors"]) > 0 else 100,
            2
        )
    })


# Run with: uvicorn app_api:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("🚀 Starting ZeroSite Report API v3")
    print("="*80)
    print("\n📚 API Documentation:")
    print("   - Swagger UI: http://localhost:8000/api/v3/docs")
    print("   - ReDoc: http://localhost:8000/api/v3/redoc")
    print("   - Health Check: http://localhost:8000/api/v3/health")
    print("\n" + "="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
