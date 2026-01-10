"""
M7 커뮤니티 계획 전용 라우터
================================

M7 독립 보고서 HTML/PDF 엔드포인트

Version: 1.0
Date: 2026-01-10
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from typing import Optional
import logging

from app.services.final_report_assembler import FinalReportData, assemble_all_in_one_report
from app.services.template_renderer import render_m7_community_plan_report
from app.services.context_storage import context_storage

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v4/reports/m7",
    tags=["M7 Community Plan Reports"]
)


@router.get("/community-plan/html", response_class=HTMLResponse)
async def get_m7_community_plan_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M7 커뮤니티 계획 독립 보고서 (HTML)
    
    **기능**:
    - M7 커뮤니티 계획만 포함하는 독립 보고서
    - M2-M6 내용 제외, M7 전용 포맷
    
    **사용 예시**:
    ```
    GET /api/v4/reports/m7/community-plan/html?context_id=test_001
    ```
    
    **응답**: M7 커뮤니티 계획 HTML 보고서
    """
    try:
        # 1. Context 데이터 로드
        canonical_data = context_storage.get_frozen_context(context_id)
        if not canonical_data:
            raise HTTPException(
                status_code=404,
                detail=f"❌ 분석 데이터를 찾을 수 없습니다. Context ID: {context_id}"
            )
        
        # 2. FinalReportData 생성 및 M7 파싱
        data = FinalReportData(canonical_data, context_id)
        
        if not data.m7:
            raise HTTPException(
                status_code=404,
                detail="❌ M7 커뮤니티 계획 데이터가 없습니다. M3/M4 분석을 먼저 완료해주세요."
            )
        
        # 3. 전체 보고서 조립 (community_plan 추출용)
        full_report = assemble_all_in_one_report(data)
        
        if 'community_plan' not in full_report or not full_report['community_plan']:
            raise HTTPException(
                status_code=500,
                detail="❌ M7 커뮤니티 계획 섹션 조립 실패"
            )
        
        # 4. M7 독립 보고서 데이터 구성
        m7_report_data = {
            'context_id': context_id,
            'generated_at': full_report.get('generated_at'),
            'address': canonical_data.get('address', '주소 정보 없음'),
            'community_plan': full_report['community_plan']
        }
        
        # 5. M7 HTML 렌더링
        html = render_m7_community_plan_report(m7_report_data)
        
        logger.info(f"✅ M7 독립 보고서 HTML 생성 완료: context_id={context_id}")
        return HTMLResponse(content=html, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M7 독립 보고서 생성 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"M7 보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/community-plan/pdf")
async def get_m7_community_plan_pdf(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M7 커뮤니티 계획 독립 보고서 (PDF)
    
    **기능**:
    - M7 HTML을 PDF로 변환하여 다운로드
    - 파일명: m7_community_plan_{context_id}.pdf
    
    **사용 예시**:
    ```
    GET /api/v4/reports/m7/community-plan/pdf?context_id=test_001
    ```
    
    **응답**: PDF 파일 다운로드
    """
    try:
        # 1. HTML 생성
        html_response = await get_m7_community_plan_html(context_id)
        
        # 2. PDF 안내 메시지
        # WeasyPrint/pydyf 버전 호환성 문제로 인해 브라우저 프린트 권장
        logger.warning("⚠️ PDF direct generation disabled due to library compatibility")
        raise HTTPException(
            status_code=501,
            detail={
                "message": "PDF 직접 생성 기능은 현재 준비 중입니다",
                "workaround": "HTML 버전을 브라우저에서 열고 Ctrl+P → 'PDF로 저장' → '배경 그래픽 켜기'를 선택하세요",
                "html_endpoint": f"/api/v4/reports/m7/community-plan/html?context_id={context_id}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M7 PDF 생성 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"M7 PDF 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/status")
async def get_m7_status(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M7 커뮤니티 계획 생성 가능 여부 확인
    
    **기능**:
    - M7 데이터 존재 여부 확인
    - 생성 가능 여부 반환
    
    **사용 예시**:
    ```
    GET /api/v4/reports/m7/status?context_id=test_001
    ```
    """
    try:
        canonical_data = context_storage.get_frozen_context(context_id)
        if not canonical_data:
            return {
                "available": False,
                "reason": "분석 데이터를 찾을 수 없습니다",
                "context_id": context_id
            }
        
        data = FinalReportData(canonical_data, context_id)
        
        if not data.m7:
            return {
                "available": False,
                "reason": "M7 커뮤니티 계획 데이터가 없습니다. M3/M4 분석을 먼저 완료해주세요.",
                "context_id": context_id,
                "m3_available": data.m3 is not None,
                "m4_available": data.m4 is not None
            }
        
        # M7 데이터 요약
        return {
            "available": True,
            "context_id": context_id,
            "m7_summary": {
                "primary_resident_type": data.m7.primary_resident_type,
                "key_programs_count": data.m7.key_programs_count,
                "operation_model": data.m7.operation_model,
                "monthly_program_frequency": data.m7.monthly_program_frequency
            },
            "endpoints": {
                "html": f"/api/v4/reports/m7/community-plan/html?context_id={context_id}",
                "pdf": f"/api/v4/reports/m7/community-plan/pdf?context_id={context_id}"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ M7 상태 확인 실패: {e}")
        return {
            "available": False,
            "reason": f"오류 발생: {str(e)}",
            "context_id": context_id
        }
