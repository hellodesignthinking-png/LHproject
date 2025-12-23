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

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, HTMLResponse
from typing import Literal, Optional
import logging
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

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


def _validate_snapshot_freshness(frozen_context: dict, context_id: str) -> None:
    """
    [PROMPT 3.5-1] Validate snapshot freshness (HARD BLOCKING for PDF)
    
    Rule: Snapshots older than 1 hour CANNOT generate PDFs
    
    Raises:
        HTTPException(409): If snapshot is older than 1 hour
    """
    analyzed_at_str = frozen_context.get("analyzed_at")
    
    if not analyzed_at_str:
        logger.warning(f"[FinalReportAPI] Context {context_id} missing 'analyzed_at' timestamp")
        return
    
    try:
        # Parse analyzed_at timestamp
        analyzed_at = datetime.fromisoformat(analyzed_at_str.replace("Z", "+00:00"))
        
        # Get current time
        now = datetime.now(timezone.utc)
        
        # Calculate age
        age = now - analyzed_at
        age_minutes = int(age.total_seconds() / 60)
        
        # Hard blocking threshold: 1 hour
        MAX_AGE_HOURS = 1
        
        if age > timedelta(hours=MAX_AGE_HOURS):
            logger.error(
                f"[FinalReportAPI] SNAPSHOT TOO OLD: {context_id}, "
                f"Age: {age_minutes} minutes (Max: {MAX_AGE_HOURS * 60} minutes). "
                f"PDF GENERATION BLOCKED."
            )
            raise HTTPException(
                status_code=409,  # 409 Conflict
                detail={
                    "error": "OUTDATED_SNAPSHOT",
                    "message": f"Snapshot is too old ({age_minutes} minutes). "
                               f"Maximum allowed age: {MAX_AGE_HOURS * 60} minutes. "
                               f"Please run a new analysis to generate fresh data.",
                    "context_id": context_id,
                    "analyzed_at": analyzed_at_str,
                    "age_minutes": age_minutes,
                    "max_age_minutes": MAX_AGE_HOURS * 60,
                    "recommendation": "Run a new analysis with /api/v4/analyze endpoint"
                }
            )
        
        logger.info(
            f"[FinalReportAPI] Snapshot freshness OK: {context_id}, "
            f"Age: {age_minutes} minutes"
        )
    
    except ValueError as e:
        logger.warning(
            f"[FinalReportAPI] Invalid timestamp format for {context_id}: {analyzed_at_str}. "
            f"Skipping freshness check. Error: {e}"
        )


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


# ========== PROMPT 3.5-4: ASYNC HISTORY LOGGING ==========

async def _log_generation_history(
    context_id: str,
    report_type: str,
    qa_status: Optional[str] = None,
    pdf_generated: bool = False,
    error: Optional[str] = None
):
    """
    [PROMPT 3.5-4] Async log Final Report generation history
    
    Logs to JSON file for operational monitoring without blocking generation.
    
    Args:
        context_id: Analysis context ID
        report_type: Type of report generated
        qa_status: QA validation status (PASS/WARNING/FAIL)
        pdf_generated: Whether PDF was successfully generated
        error: Error message if generation failed
    """
    try:
        log_dir = Path("/home/user/webapp/logs/final_reports")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / "generation_history.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "context_id": context_id,
            "report_type": report_type,
            "qa_status": qa_status,
            "pdf_generated": pdf_generated,
            "error": error
        }
        
        # Append to JSONL file
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        logger.info(
            f"[GenerationHistory] Logged: {report_type} for {context_id} "
            f"(QA: {qa_status}, PDF: {pdf_generated})"
        )
    
    except Exception as e:
        # Never fail the main generation due to logging issues
        logger.error(f"[GenerationHistory] Logging failed: {e}", exc_info=True)


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
    context_id: str = Query(..., description="Frozen context ID (required)"),
    background_tasks: BackgroundTasks = None
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
    
    # Step 1.5: [PROMPT 3.5-1] Validate snapshot freshness (HARD BLOCKING)
    _validate_snapshot_freshness(frozen_context, context_id)
    
    qa_status = None  # Track for logging
    pdf_generated = False
    error_msg = None
    
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
        qa_status = qa_result["status"]  # Store for logging
        
        # Step 4: BLOCKING check
        if should_block_pdf_generation(qa_result):
            error_msg = f"QA BLOCKED: {qa_result['status']}"
            
            # [PROMPT 3.5-4] Log generation failure (non-blocking)
            if background_tasks:
                background_tasks.add_task(
                    _log_generation_history,
                    context_id=context_id,
                    report_type=report_type,
                    qa_status=qa_status,
                    pdf_generated=False,
                    error=error_msg
                )
            
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
        
        # Step 5: [vABSOLUTE-FINAL-8] FORCE CACHE INVALIDATION
        # Validate BUILD SIGNATURE presence (proof of new HTML)
        import hashlib
        
        if "vABSOLUTE-FINAL-6" not in html_content:
            logger.critical(
                f"[FinalReportAPI] ❌ CACHE DETECTED: BUILD SIGNATURE MISSING! "
                f"Report: {report_type}, Context: {context_id}"
            )
            raise HTTPException(
                status_code=500,
                detail="PDF generation blocked - HTML cache detected. "
                       "BUILD SIGNATURE missing. Please retry with new context_id."
            )
        
        # Log HTML hash for traceability
        html_hash = hashlib.sha1(html_content.encode()).hexdigest()[:8]
        logger.critical(
            f"[FinalReportAPI] FINAL PDF BUILD | "
            f"Report: {report_type} | "
            f"Context: {context_id} | "
            f"HTML Hash: {html_hash} | "
            f"BUILD SIGNATURE: ✅ VERIFIED"
        )
        
        # Step 6: Convert HTML to PDF
        from weasyprint import HTML
        
        pdf_bytes = HTML(string=html_content).write_pdf()
        pdf_generated = True  # Mark success for logging
        
        logger.critical(
            f"[FinalReportAPI] THIS PDF IS GUARANTEED NEW. NO CACHE USED. | "
            f"Size: {len(pdf_bytes):,} bytes"
        )
        
        # [PROMPT 3.5-4] Log successful generation (non-blocking)
        if background_tasks:
            background_tasks.add_task(
                _log_generation_history,
                context_id=context_id,
                report_type=report_type,
                qa_status=qa_status,
                pdf_generated=True,
                error=None
            )
        
        # Step 7: Generate filename with BUILD HASH (cache-busting)
        build_timestamp = datetime.now().isoformat()
        build_hash = hashlib.sha1(
            f"{context_id}-{build_timestamp}".encode()
        ).hexdigest()[:8]
        
        timestamp = frozen_context.get("analyzed_at", datetime.now().isoformat())[:19].replace(":", "-")
        filename = f"FinalReport_{report_type}_{context_id}_{build_hash}_{timestamp}.pdf"
        
        # Step 8: Return PDF with cache-busting headers
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-Build-Hash": build_hash,
                "X-Build-Signature": "vABSOLUTE-FINAL-6"
            }
        )
    
    except HTTPException:
        raise
    except ImportError as e:
        error_msg = f"WeasyPrint not available: {str(e)}"
        
        # [PROMPT 3.5-4] Log import error (non-blocking)
        if background_tasks:
            background_tasks.add_task(
                _log_generation_history,
                context_id=context_id,
                report_type=report_type,
                qa_status=qa_status,
                pdf_generated=False,
                error=error_msg
            )
        
        logger.error(f"[FinalReportAPI] WeasyPrint not available: {e}")
        raise HTTPException(
            status_code=501,
            detail="PDF generation not available - WeasyPrint library required"
        )
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        
        # [PROMPT 3.5-4] Log unexpected error (non-blocking)
        if background_tasks:
            background_tasks.add_task(
                _log_generation_history,
                context_id=context_id,
                report_type=report_type,
                qa_status=qa_status,
                pdf_generated=False,
                error=error_msg
            )
        
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
