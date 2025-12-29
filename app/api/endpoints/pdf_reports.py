"""
PDF 보고서 생성 API
==================

모듈별 PDF 보고서 생성 엔드포인트

Author: ZeroSite Team
Date: 2025-12-18
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Any
import logging
from urllib.parse import quote

from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["PDF Reports"])

# PDF generator will be initialized per request to ensure latest code
# pdf_generator = ModulePDFGenerator()


class PDFGenerationRequest(BaseModel):
    """PDF 생성 요청"""
    module_id: str  # M2, M3, M4, M5, M6
    data: Dict[str, Any]


@router.post("/generate/{module_id}")
async def generate_module_pdf(module_id: str, request: PDFGenerationRequest):
    """
    모듈별 PDF 보고서 생성
    
    ⚠️ DEPRECATED: This endpoint now redirects to HTML generator.
    Use /api/v4/reports/module/{module_id}/html instead.
    
    Args:
        module_id: M2, M3, M4, M5, M6
        request: 모듈 데이터
    
    Returns:
        HTML report (use browser Ctrl+P to save as PDF)
    """
    try:
        logger.warning(f"⚠️ [DEPRECATED] PDF endpoint called for {module_id}, redirecting to HTML generator")
        
        # 🔥 NEW: Redirect to HTML generator (REAL APPRAISAL STANDARD format)
        # Users can use Ctrl+P in browser to save as PDF
        
        raise HTTPException(
            status_code=410,  # Gone
            detail={
                "message": "PDF generation is deprecated. Use HTML reports with browser print function.",
                "html_endpoint": f"/api/v4/reports/module/{module_id}/html?context_id={{context_id}}",
                "instruction": "Open HTML report and press Ctrl+P to save as PDF",
                "format": "REAL APPRAISAL STANDARD v6.5"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF generation failed for {module_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )
