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

# Phase 10.5: Expert Edition v3 - Context Builder
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.services_v13.report_full.pdf_exporter_full import PDFExporterFull
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v13", tags=["Phase 11.2 - Minimal UI"])

# In-memory storage for generated reports (for demo purposes)
# In production, use Redis or database
REPORTS_CACHE = {}


def _flatten_context_for_template(context: dict, land_area_sqm: float) -> dict:
    """
    Flatten context dictionary for Expert Edition v3 template compatibility.
    
    This fixes the \"0억원\" bug by correctly mapping context keys.
    The issue was that template was reading wrong keys (e.g., site['floor_area_ratio'])
    when the actual data was in different locations (e.g., zoning['far']).
    
    Args:
        context: Raw context from build_expert_context()
        land_area_sqm: Land area for calculations
        
    Returns:
        Flattened context ready for template rendering
    """
    # Extract nested data
    site = context.get('site', {})
    zoning = context.get('zoning', {})
    demand = context.get('demand', {})
    market = context.get('market', {})
    finance = context.get('finance', {})
    cost = context.get('cost', {})
    
    # Add basic site info
    context['land_area_sqm'] = land_area_sqm
    context['land_area_pyeong'] = land_area_sqm / 3.3058
    context['address'] = context.get('site', {}).get('address', '')
    
    # FIX: Map zoning keys correctly (bcr/far instead of building_coverage/floor_area_ratio)
    context['floor_area_ratio'] = zoning.get('far', 200.0)
    context['building_coverage'] = zoning.get('bcr', 60.0)
    context['building_area_sqm'] = zoning.get('building_area', land_area_sqm * 0.6)
    context['total_floor_area_sqm'] = zoning.get('gross_floor_area', land_area_sqm * 2.0)
    context['building_height_m'] = zoning.get('max_height', 35.0)
    context['max_building_coverage'] = 60.0
    context['max_floor_area_ratio'] = 250.0
    context['max_height_m'] = 35.0
    context['zone_type'] = zoning.get('zone_type', '제2종일반주거지역')
    context['land_category'] = '대'
    
    # Demand metrics (Phase 6.8)
    context['demand_score'] = demand.get('overall_score', 60.0)
    context['recommended_housing_type'] = demand.get('recommended_type_kr', demand.get('recommended_type', '청년형'))
    context['demand_confidence'] = 85.0 if demand.get('confidence_level') == 'high' else 70.0
    context['recommended_units'] = demand.get('recommended_units', int(land_area_sqm / 20))
    
    # Fix housing_types structure
    housing_types_raw = demand.get('all_scores', {})
    if isinstance(housing_types_raw, dict):
        context['housing_types'] = [
            {'name': k, 'score': v, 'suitability': v, 'recommended_units': int(v * 2)}
            for k, v in housing_types_raw.items()
        ]
    else:
        context['housing_types'] = []
    
    # Market metrics (Phase 7.7)
    context['market_signal'] = market.get('signal', 'FAIR')
    context['market_temperature'] = market.get('temperature', 'STABLE')
    context['market_delta_pct'] = market.get('delta_pct', 0.0)
    zerosite_val = market.get('zerosite_value_per_sqm', 0.0)
    market_val = market.get('market_avg_price_per_sqm', 0.0)
    context['zerosite_value_per_sqm'] = zerosite_val / 10000 if zerosite_val > 0 else 0
    context['market_avg_price_per_sqm'] = market_val / 10000 if market_val > 0 else 0
    
    # FIX: Financial metrics - ALWAYS convert KRW → 억원
    capex_raw = finance.get('capex', {}).get('total', 0.0)
    npv_raw = finance.get('npv', {}).get('public', 0.0)
    irr_raw = finance.get('irr', {}).get('public', 0.0)
    payback_raw = finance.get('payback', {}).get('years', 0.0)
    
    context['capex_krw'] = capex_raw / 100000000  # Always convert
    context['npv_public_krw'] = npv_raw / 100000000
    context['irr_public_pct'] = irr_raw
    context['payback_period_years'] = payback_raw if payback_raw != float('inf') else 999
    
    # Fix cashflow structure
    cashflow_raw = finance.get('cashflow', [])
    context['cash_flow_table'] = [
        {
            'year': cf.get('year', i+1),
            'revenue': cf.get('revenue', 0.0),
            'expense': cf.get('expense', 0.0),
            'net_cf': cf.get('cf', 0.0),
            'cumulative_cf': cf.get('cumulative', 0.0)
        }
        for i, cf in enumerate(cashflow_raw)
    ]
    
    # Cost metrics (Phase 8) - ALL in KRW, convert to 억원
    total_const_cost = cost.get('construction', {}).get('total', 0.0)
    per_sqm_cost = cost.get('construction', {}).get('per_sqm', 0.0)
    context['total_construction_cost_krw'] = total_const_cost / 100000000
    context['cost_per_sqm_krw'] = per_sqm_cost / 10000
    context['cost_confidence'] = cost.get('verification', {}).get('confidence', 85.0)
    
    breakdown = cost.get('construction', {}).get('breakdown', {})
    context['direct_cost_krw'] = breakdown.get('direct', 0.0) / 100000000
    context['indirect_cost_krw'] = breakdown.get('indirect', 0.0) / 100000000
    context['design_cost_krw'] = breakdown.get('design', 0.0) / 100000000
    context['other_cost_krw'] = breakdown.get('contingency', 0.0) / 100000000
    
    # Decision
    decision_data = context.get('decision', {})
    context['decision'] = decision_data.get('result', 'NO-GO')
    
    # Risk matrix (generate sample if not present)
    if 'risk_matrix' not in context:
        context['risk_matrix'] = [
            {'category': f'Risk-{i+1}', 'level': 'low' if i%3==0 else ('medium' if i%3==1 else 'high'),
             'impact': 3.5, 'mitigation': f'Mitigation strategy {i+1}'}
            for i in range(25)
        ]
    
    # Analysis parameters
    context['discount_rate'] = 4.5
    context['analysis_period'] = 30
    context['rent_escalation'] = 2.0
    context['vacancy_rate'] = 5.0
    
    # Report metadata
    context['report_date'] = datetime.now().strftime('%Y년 %m월 %d일')
    context['report_id'] = f"EXP-V3-{datetime.now().strftime('%Y%m%d')}"
    
    # v14.5: Date variables for bibliography section
    context['current_year'] = datetime.now().year
    context['current_month'] = datetime.now().month
    
    return context


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
        
        # Initialize Expert Edition v3 Context Builder
        builder = ReportContextBuilder()
        
        # Prepare additional parameters
        additional_params = {}
        if request.appraisal_price:
            additional_params['appraisal_price'] = request.appraisal_price
        
        # Build Expert Edition v3 context
        logger.info("Building Expert Edition v3 context...")
        context = builder.build_expert_context(
            address=request.address,
            land_area_sqm=request.land_area_sqm,
            additional_params=additional_params
        )
        
        # FIX: Apply context flattening for template compatibility
        # This fixes the "0값" bug by mapping context keys correctly
        context = _flatten_context_for_template(context, request.land_area_sqm)
        
        logger.info(f"Context built with {len(context.keys())} sections")
        
        # Render Expert Edition v3 HTML template
        template_dir = Path(__file__).parent.parent / 'services_v13' / 'report_full'
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template('lh_expert_edition_v3.html.jinja2')
        html_content = template.render(**context)
        
        # Use context as report_data for backward compatibility
        report_data = context
        
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
