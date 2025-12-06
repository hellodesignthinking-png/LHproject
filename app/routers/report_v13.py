"""
Phase 11.2: Minimal UI - FastAPI Router
Simple 2-endpoint API for LH report generation

Endpoints:
- POST /api/v13/report - Generate report and return report_id
- GET /api/v13/report/{report_id} - Download PDF report
- GET /api/v13/report/{report_id}/summary - Get report summary
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from pathlib import Path
import logging
from datetime import datetime
import io

# Phase 10.5: Full Report Generator
from app.services_v13.report_full.report_full_generator import LHFullReportGenerator
from app.services_v13.report_full.pdf_exporter_full import PDFExporterFull
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v13", tags=["Phase 11.2 - Minimal UI"])

# In-memory storage for generated reports (for demo purposes)
# In production, use Redis or database
REPORTS_CACHE = {}


class ReportRequest(BaseModel):
    """Request model for report generation"""
    address: str = Field(..., description="대상지 주소", example="서울시 강남구 역삼동 123")
    land_area_sqm: float = Field(..., gt=0, description="대지면적 (㎡)", example=500.0)
    merge: bool = Field(default=False, description="다필지 합필 여부")
    appraisal_price: Optional[float] = Field(None, description="감정평가액 (원)")


class ReportResponse(BaseModel):
    """Response model for report generation"""
    report_id: str = Field(..., description="보고서 ID")
    status: str = Field(default="pending", description="생성 상태")
    message: str = Field(default="보고서 생성이 시작되었습니다")


class ReportSummary(BaseModel):
    """Report summary model"""
    report_id: str
    address: str
    housing_type: str
    npv_public: float
    irr: float
    payback_period: float
    market_signal: str
    generated_at: str


@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate LH Official Full Report
    
    이 엔드포인트는 주소와 대지면적을 받아서 30-50페이지 LH 공식 제출 보고서를 생성합니다.
    
    - **address**: 대상지 주소
    - **land_area_sqm**: 대지면적 (제곱미터)
    - **merge**: 다필지 합필 여부 (옵션)
    - **appraisal_price**: 감정평가액 (옵션)
    
    Returns report_id which can be used to download the PDF.
    """
    try:
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        logger.info(f"Generating report {report_id} for address: {request.address}")
        
        # Initialize report generator
        generator = LHFullReportGenerator()
        
        # Generate report data
        additional_params = {}
        if request.appraisal_price:
            additional_params['appraisal_price'] = request.appraisal_price
        
        report_data = generator.generate_full_report_data(
            address=request.address,
            land_area_sqm=request.land_area_sqm,
            additional_params=additional_params
        )
        
        # Render HTML template
        template_dir = Path(__file__).parent.parent / 'templates_v13'
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('lh_submission_full.html.jinja2')
        html_content = template.render(**report_data)
        
        # Store report data and HTML in cache
        REPORTS_CACHE[report_id] = {
            'report_data': report_data,
            'html_content': html_content,
            'request': request.dict(),
            'generated_at': datetime.now().isoformat(),
            'status': 'completed'
        }
        
        logger.info(f"Report {report_id} generated successfully")
        
        return ReportResponse(
            report_id=report_id,
            status="completed",
            message="보고서가 성공적으로 생성되었습니다"
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/report/{report_id}")
async def download_report(report_id: str):
    """
    Download report as PDF
    
    이 엔드포인트는 생성된 보고서를 PDF 파일로 다운로드합니다.
    
    - **report_id**: 보고서 생성 시 받은 ID
    
    Returns PDF file stream.
    """
    try:
        # Check if report exists in cache
        if report_id not in REPORTS_CACHE:
            raise HTTPException(
                status_code=404,
                detail="보고서를 찾을 수 없습니다. 다시 생성해주세요."
            )
        
        cached_report = REPORTS_CACHE[report_id]
        html_content = cached_report['html_content']
        
        logger.info(f"Generating PDF for report {report_id}")
        
        # Generate PDF
        pdf_exporter = PDFExporterFull()
        
        # Create temporary BytesIO for PDF
        pdf_buffer = io.BytesIO()
        
        # Export to BytesIO instead of file
        # Note: WeasyPrint's write_pdf can write to BytesIO
        from weasyprint import HTML as WeasyHTML, CSS
        
        weasy_html = WeasyHTML(string=html_content)
        weasy_html.write_pdf(
            pdf_buffer,
            stylesheets=[CSS(string=pdf_exporter._get_pdf_css())]
        )
        
        # Seek to beginning of buffer
        pdf_buffer.seek(0)
        
        logger.info(f"PDF generated successfully for report {report_id}")
        
        # Get address for filename (use simple ID to avoid encoding issues)
        filename = f"LH_Report_{report_id[:8]}.pdf"
        
        # Return PDF as streaming response
        # Use RFC 5987 encoding for non-ASCII characters
        from urllib.parse import quote
        encoded_filename = quote(filename)
        
        return StreamingResponse(
            io.BytesIO(pdf_buffer.read()),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PDF 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/report/{report_id}/summary", response_model=ReportSummary)
async def get_report_summary(report_id: str):
    """
    Get report summary
    
    이 엔드포인트는 생성된 보고서의 요약 정보를 반환합니다.
    
    - **report_id**: 보고서 생성 시 받은 ID
    
    Returns summary with key metrics.
    """
    try:
        # Check if report exists in cache
        if report_id not in REPORTS_CACHE:
            raise HTTPException(
                status_code=404,
                detail="보고서를 찾을 수 없습니다. 다시 생성해주세요."
            )
        
        cached_report = REPORTS_CACHE[report_id]
        report_data = cached_report['report_data']
        
        # Extract key metrics
        financial = report_data.get('financial_analysis', {})
        regional = report_data.get('regional_analysis', {})
        market = report_data.get('market_analysis', {})
        site = report_data.get('site_overview', {})
        
        summary = ReportSummary(
            report_id=report_id,
            address=site.get('address', 'N/A'),
            housing_type=regional.get('recommended_type', 'youth'),
            npv_public=financial.get('npv_public', 0),
            irr=financial.get('irr', 0),
            payback_period=financial.get('payback_period', 0),
            market_signal=market.get('signal', 'FAIR'),
            generated_at=cached_report['generated_at']
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"요약 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ZeroSite v13.0 - Phase 11.2",
        "reports_cached": len(REPORTS_CACHE)
    }
