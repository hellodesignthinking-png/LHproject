"""
ZeroSite Export API
===================

API endpoints for exporting analysis reports in multiple formats.

Author: ZeroSite Phase 3 Team
Date: 2026-01-11
Version: 1.0
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import json
import io
from datetime import datetime

from app.services.report_generator import report_generator
from app.core.analysis_status import analysis_status_storage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/export", tags=["Export & Reporting"])


# ============================================================================
# Response Models
# ============================================================================

class ReportResponse(BaseModel):
    """Final report response"""
    success: bool
    report: Dict[str, Any]
    generated_at: str


class ExportResponse(BaseModel):
    """Export file response metadata"""
    success: bool
    filename: str
    size_bytes: int
    format: str
    download_url: str


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/projects/{project_id}/report")
async def get_final_report(project_id: str) -> ReportResponse:
    """
    Get comprehensive final report (JSON)
    
    Aggregates all M1-M6 data into a structured report.
    """
    
    try:
        # Get project status
        status = analysis_status_storage.get_status(project_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
        
        # Check if all modules are completed
        required_modules = ["M1", "M2", "M3", "M4", "M5", "M6"]
        for module in required_modules:
            module_info = status.get_module_status(module)
            if module_info.status.value not in ["COMPLETED", "VERIFIED"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"{module} is not completed. Cannot generate report."
                )
        
        # Get module results
        m1_info = status.get_module_status("M1")
        m2_info = status.get_module_status("M2")
        m3_info = status.get_module_status("M3")
        m4_info = status.get_module_status("M4")
        m5_info = status.get_module_status("M5")
        m6_info = status.get_module_status("M6")
        
        # Generate report
        report = report_generator.generate_final_report(
            project_id=project_id,
            project_name=status.project_name,
            address=status.address,
            m1_data=m1_info.result_summary or {},
            m2_data=m2_info.result_summary or {},
            m3_data=m3_info.result_summary or {},
            m4_data=m4_info.result_summary or {},
            m5_data=m5_info.result_summary or {},
            m6_data=m6_info.result_summary or {},
            context_id=status.current_context_id,
            verification_log=[]  # TODO: Implement verification log
        )
        
        logger.info(f"✅ Final report generated for project {project_id}")
        
        return ReportResponse(
            success=True,
            report=report,
            generated_at=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/export/pdf")
async def export_pdf(project_id: str):
    """
    Export report as PDF
    
    Returns a government-compliant PDF document.
    """
    
    try:
        # Get report data
        report_response = await get_final_report(project_id)
        report = report_response.report
        
        # Generate filename
        project_name = report['report_metadata']['project_name']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ZeroSite_{project_name}_{timestamp}.pdf"
        
        # TODO: Implement actual PDF generation
        # For now, return JSON as placeholder
        
        pdf_content = json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"❌ PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/export/excel")
async def export_excel(project_id: str):
    """
    Export report as Excel
    
    Returns an Excel workbook with multiple worksheets.
    """
    
    try:
        # Get report data
        report_response = await get_final_report(project_id)
        report = report_response.report
        
        # Generate filename
        project_name = report['report_metadata']['project_name']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ZeroSite_{project_name}_{timestamp}.xlsx"
        
        # TODO: Implement actual Excel generation
        # For now, return JSON as placeholder
        
        excel_content = json.dumps(report, ensure_ascii=False, indent=2).encode('utf-8')
        
        return StreamingResponse(
            io.BytesIO(excel_content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Excel export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/export/package")
async def export_submission_package(
    project_id: str,
    template: str = "lh"  # lh, local_gov, financial
):
    """
    Export complete submission package
    
    Returns a ZIP file containing:
    - PDF report
    - Excel data
    - Verification log
    - README
    """
    
    try:
        # Get report data
        report_response = await get_final_report(project_id)
        report = report_response.report
        
        # Generate filename
        project_name = report['report_metadata']['project_name']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ZeroSite_Submission_{project_name}_{timestamp}.zip"
        
        # TODO: Implement actual ZIP package generation
        # Should include: PDF, Excel, verification_log.txt, README.txt
        
        package_content = json.dumps({
            "package_info": {
                "template": template,
                "generated_at": datetime.now().isoformat(),
                "contents": ["report.pdf", "data.xlsx", "verification_log.txt", "README.txt"]
            },
            "report": report
        }, ensure_ascii=False, indent=2).encode('utf-8')
        
        return StreamingResponse(
            io.BytesIO(package_content),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Package export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/verification-log")
async def get_verification_log(project_id: str):
    """
    Get complete verification history
    
    Returns chronological log of all verifications and changes.
    """
    
    try:
        # Get project status
        status = analysis_status_storage.get_status(project_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
        
        # Collect verification events
        verification_log = []
        
        for module_name in ["M1", "M2", "M3", "M4", "M5", "M6"]:
            module_info = status.get_module_status(module_name)
            
            if module_info.verified_at:
                verification_log.append({
                    "timestamp": module_info.verified_at,
                    "module": module_name,
                    "action": "VERIFIED",
                    "status": module_info.verification_status.value if module_info.verification_status else None,
                    "verified_by": module_info.verified_by
                })
            
            if module_info.executed_at:
                verification_log.append({
                    "timestamp": module_info.executed_at,
                    "module": module_name,
                    "action": "EXECUTED",
                    "status": module_info.status.value
                })
        
        # Sort by timestamp
        verification_log.sort(key=lambda x: x['timestamp'])
        
        return {
            "success": True,
            "project_id": project_id,
            "context_id": status.current_context_id,
            "log_entries": verification_log,
            "total_events": len(verification_log)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get verification log: {e}")
        raise HTTPException(status_code=500, detail=str(e))
