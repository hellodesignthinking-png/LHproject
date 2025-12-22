"""
ZeroSite Final Report API Router (PROMPT 7)
============================================

Complete API for 6 Final Report types.

Endpoints:
- GET /api/v4/final-report/{report_type}/html
- GET /api/v4/final-report/{report_type}/pdf

Features:
1. context_id validation
2. Report type validation
3. Assembler instantiation
4. QA validation (BLOCKING mode)
5. HTML/PDF generation

VERSION: 1.0 (PROMPT 7 Implementation)
DATE: 2025-12-22
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from typing import Literal
import logging
import io
from datetime import datetime

# Phase 3 imports
from app.services.final_report_assembly.assemblers import (
    LandownerSummaryAssembler,
    LHTechnicalAssembler,
    QuickCheckAssembler,
    FinancialFeasibilityAssembler,
    AllInOneAssembler,
    ExecutiveSummaryAssembler
)
from app.services.final_report_assembly.qa_validator import (
    FinalReportQAValidator,
    should_block_pdf_generation,
    log_qa_result
)
from app.services.context_storage import context_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v4/final-report", tags=["Final Reports (Phase 3)"])


# ========== ASSEMBLER REGISTRY ==========

ASSEMBLER_MAP = {
    "landowner_summary": LandownerSummaryAssembler,
    "lh_technical": LHTechnicalAssembler,
    "quick_check": QuickCheckAssembler,
    "financial_feasibility": FinancialFeasibilityAssembler,
    "all_in_one": AllInOneAssembler,
    "executive_summary": ExecutiveSummaryAssembler,
}

VALID_REPORT_TYPES = list(ASSEMBLER_MAP.keys())


# ========== HELPER FUNCTIONS ==========

def _validate_report_type(report_type: str):
    """Validate report type"""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type: {report_type}. "
                   f"Valid types: {', '.join(VALID_REPORT_TYPES)}"
        )


def _validate_context_exists(context_id: str):
    """Validate context_id exists"""
    frozen_context = context_storage.get_frozen_context(context_id)
    if not frozen_context:
        raise HTTPException(
            status_code=404,
            detail=f"Context not found: {context_id}. "
                   f"Please run analysis first."
        )
    
    # Check canonical_summary exists
    canonical_summary = frozen_context.get("canonical_summary")
    if not canonical_summary:
        raise HTTPException(
            status_code=400,
            detail=f"Context {context_id} has no canonical_summary. "
                   f"Cannot generate final report."
        )
    
    return frozen_context


def _extract_modules_data_for_qa(html_content: str) -> dict:
    """
    Extract minimal module data from HTML for QA validation
    
    This is NOT calculation - just reading displayed values for QA checks
    """
    import re
    
    modules_data = {}
    
    # Extract M5 NPV (for decision-readiness check)
    npv_match = re.search(r'NPV[:\s]*([+-]?\d{1,3}(?:,\d{3})*)', html_content, re.IGNORECASE)
    if npv_match:
        npv_str = npv_match.group(1).replace(",", "")
        modules_data["M5"] = {
            "npv": int(npv_str),
            "is_profitable": int(npv_str) > 0
        }
    
    # Extract M6 decision
    decision_keywords = ["승인", "조건부 승인", "부적합", "탈락"]
    for keyword in decision_keywords:
        if keyword in html_content:
            modules_data["M6"] = {"decision": keyword}
            break
    
    return modules_data


# ========== API ENDPOINTS ==========

@router.get("/{report_type}/html")
async def get_final_report_html(
    report_type: str,
    context_id: str = Query(..., description="Frozen context ID (required)")
):
    """
    Generate Final Report HTML
    
    Args:
        report_type: One of: landowner_summary, lh_technical, quick_check,
                     financial_feasibility, all_in_one, executive_summary
        context_id: Frozen context ID from analysis
    
    Returns:
        HTMLResponse with assembled final report
    
    Example:
        GET /api/v4/final-report/landowner_summary/html?context_id=abc123
    """
    logger.info(f"[FinalReportAPI] HTML request: {report_type}, context={context_id}")
    
    # Step 1: Validate inputs
    _validate_report_type(report_type)
    frozen_context = _validate_context_exists(context_id)
    
    try:
        # Step 2: Instantiate assembler
        assembler_class = ASSEMBLER_MAP[report_type]
        assembler = assembler_class(context_id)
        
        logger.info(f"[FinalReportAPI] Assembler: {assembler_class.__name__}")
        
        # Step 3: Assemble report
        result = assembler.assemble()
        html_content = result["html"]
        
        logger.info(f"[FinalReportAPI] Assembly complete ({len(html_content):,} chars)")
        
        # Step 4: QA validation
        modules_data = _extract_modules_data_for_qa(html_content)
        qa_result = FinalReportQAValidator.validate(
            report_type=report_type,
            html_content=html_content,
            modules_data=modules_data
        )
        
        log_qa_result(qa_result)
        
        # Step 5: Check QA blocking
        if qa_result["status"] == "FAIL" and qa_result["blocking_issues"]:
            logger.error(
                f"[FinalReportAPI] QA FAILED with blocking issues: {qa_result['blocking_issues']}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"QA FAILED - Report does not meet quality standards. "
                       f"Issues: {', '.join(qa_result['blocking_issues'])}"
            )
        
        # Step 6: Log warnings
        if qa_result["warnings"]:
            for warning in qa_result["warnings"]:
                logger.warning(f"[FinalReportAPI] QA Warning: {warning}")
        
        # Step 7: Return HTML
        logger.info(f"[FinalReportAPI] HTML generation SUCCESS")
        return HTMLResponse(content=html_content)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FinalReportAPI] Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during final report generation: {str(e)}"
        )


@router.get("/{report_type}/pdf")
async def get_final_report_pdf(
    report_type: str,
    context_id: str = Query(..., description="Frozen context ID (required)")
):
    """
    Generate Final Report PDF
    
    Workflow:
    1. Generate HTML (same as /html endpoint)
    2. Run QA validation (BLOCKING mode)
    3. Convert HTML → PDF
    4. Return PDF with proper headers
    
    Args:
        report_type: One of the 6 final report types
        context_id: Frozen context ID from analysis
    
    Returns:
        StreamingResponse with PDF file
    
    Example:
        GET /api/v4/final-report/landowner_summary/pdf?context_id=abc123
    """
    logger.info(f"[FinalReportAPI] PDF request: {report_type}, context={context_id}")
    
    # Step 1: Validate inputs
    _validate_report_type(report_type)
    frozen_context = _validate_context_exists(context_id)
    
    try:
        # Step 2: Generate HTML (reuse HTML generation logic)
        assembler_class = ASSEMBLER_MAP[report_type]
        assembler = assembler_class(context_id)
        
        result = assembler.assemble()
        html_content = result["html"]
        
        logger.info(f"[FinalReportAPI] HTML generated for PDF conversion")
        
        # Step 3: QA validation (CRITICAL for PDF)
        modules_data = _extract_modules_data_for_qa(html_content)
        qa_result = FinalReportQAValidator.validate(
            report_type=report_type,
            html_content=html_content,
            modules_data=modules_data
        )
        
        log_qa_result(qa_result)
        
        # Step 4: BLOCKING check
        if should_block_pdf_generation(qa_result):
            logger.error(
                f"[FinalReportAPI] PDF BLOCKED due to QA failure. "
                f"Status: {qa_result['status']}, "
                f"Blocking issues: {qa_result.get('blocking_issues', [])}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"PDF generation blocked - Quality standards not met. "
                       f"Status: {qa_result['status']}. "
                       f"Please check HTML version for details."
            )
        
        # Step 5: Convert HTML to PDF
        # For now, we'll return HTML as PDF placeholder
        # TODO: Integrate actual HTML→PDF conversion library
        from weasyprint import HTML
        
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        logger.info(f"[FinalReportAPI] PDF generated ({len(pdf_bytes):,} bytes)")
        
        # Step 6: Generate filename
        timestamp = frozen_context.get("analyzed_at", datetime.now().isoformat())[:19].replace(":", "-")
        filename = f"FinalReport_{report_type}_{context_id}_{timestamp}.pdf"
        
        # Step 7: Return PDF
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    
    except HTTPException:
        raise
    except ImportError as e:
        logger.error(f"[FinalReportAPI] WeasyPrint not available: {e}")
        raise HTTPException(
            status_code=501,
            detail="PDF generation not available - WeasyPrint library required"
        )
    except Exception as e:
        logger.error(f"[FinalReportAPI] PDF generation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during PDF generation: {str(e)}"
        )


@router.get("/types")
async def list_report_types():
    """
    List available final report types
    
    Returns:
        Dict with available report types and their descriptions
    """
    from app.services.final_report_assembly.report_type_configs import REPORT_TYPE_CONFIGS
    
    return {
        "report_types": [
            {
                "id": report_type,
                "title": REPORT_TYPE_CONFIGS[report_type]["title"],
                "description": REPORT_TYPE_CONFIGS[report_type]["description"],
                "target_audience": REPORT_TYPE_CONFIGS[report_type]["target_audience"],
                "modules": REPORT_TYPE_CONFIGS[report_type]["modules"]
            }
            for report_type in VALID_REPORT_TYPES
        ]
    }
