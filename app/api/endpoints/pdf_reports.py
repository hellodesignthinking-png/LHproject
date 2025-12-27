"""
PDF 보고서 생성 API
==================

모듈별 PDF 보고서 생성 엔드포인트

Phase 3.5D: assembled_data 표준 스키마 사용

Author: ZeroSite Team
Date: 2025-12-27
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from urllib.parse import quote

from app.services.pdf_generators.module_pdf_generator import ModulePDFGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/pdf", tags=["PDF Reports"])


class PDFGenerationRequest(BaseModel):
    """
    PDF 생성 요청 (Phase 3.5D 표준)
    
    ✅ assembled_data: 표준 Data Contract
        {
            "m6_result": {...},
            "modules": {
                "M2": {"summary": {...}, "details": {}, "raw_data": {}},
                "M3": {...},
                "M4": {...},
                "M5": {...}
            }
        }
    
    ❌ 금지: request.data (모듈 단독 데이터)
    """
    assembled_data: Dict[str, Any]
    module_id: Optional[str] = None  # 호환성 유지


@router.post("/generate/{module_id}")
async def generate_module_pdf(module_id: str, request: PDFGenerationRequest):
    """
    모듈별 PDF 보고서 생성 (Phase 3.5D)
    
    Args:
        module_id: M2, M3, M4, M5, M6
        request: assembled_data (표준 스키마)
    
    Returns:
        PDF 파일
    """
    try:
        logger.info(f"📄 Generating PDF for {module_id}")
        
        # ✅ assembled_data 검증
        from app.services.data_contract import validate_assembled_data
        
        if not validate_assembled_data(request.assembled_data):
            logger.error(f"❌ Invalid assembled_data for {module_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid assembled_data: missing m6_result or modules"
            )
        
        # Initialize PDF generator per request to ensure latest code
        pdf_generator = ModulePDFGenerator()
        logger.info(f"✅ PDF Generator initialized (Korean font: {pdf_generator.korean_font_available})")
        
        # ✅ assembled_data 전체 전달 (HTML과 동일한 데이터)
        if module_id == "M2":
            pdf_bytes = pdf_generator.generate_m2_appraisal_pdf(
                request.assembled_data  # ✅ 표준 스키마
            )
            filename = "M2_토지감정평가_보고서.pdf"
        elif module_id == "M3":
            pdf_bytes = pdf_generator.generate_m3_housing_type_pdf(
                request.assembled_data  # ✅ 표준 스키마
            )
            filename = "M3_LH선호유형_보고서.pdf"
        elif module_id == "M4":
            pdf_bytes = pdf_generator.generate_m4_capacity_pdf(
                request.assembled_data  # ✅ 표준 스키마
            )
            filename = "M4_건축규모분석_보고서.pdf"
        elif module_id == "M5":
            pdf_bytes = pdf_generator.generate_m5_feasibility_pdf(
                request.assembled_data  # ✅ 표준 스키마
            )
            filename = "M5_사업성분석_보고서.pdf"
        elif module_id == "M6":
            pdf_bytes = pdf_generator.generate_m6_lh_review_pdf(
                request.assembled_data  # ✅ 표준 스키마
            )
            filename = "M6_LH심사예측_보고서.pdf"
        else:
            raise HTTPException(status_code=400, detail=f"Invalid module_id: {module_id}")
        
        logger.info(f"✅ PDF generated for {module_id}: {len(pdf_bytes)} bytes")
        
        # URL-encode filename for proper Korean character support
        encoded_filename = quote(filename.encode('utf-8'))
        
        # PDF 응답 반환
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ PDF generation failed for {module_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )
