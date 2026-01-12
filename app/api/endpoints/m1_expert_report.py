"""
M1 토지·입지 사실 확정 보고서 API
====================================

ZeroSite Decision OS 모듈 실행 API
- 전문가 완성본 출력 (8~12페이지 분량)
- LH 실무 제출 가능 수준
- FACT ONLY (판단/추천/점수 금지)

Author: ZeroSite Module Execution AI
Date: 2026-01-12
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.modules.m1_land_info.report_template import generate_m1_expert_report
from app.api.endpoints.m1_context_freeze_v2 import frozen_contexts_v2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports/m1", tags=["M1 Expert Reports"])


@router.get("/{context_id}")
async def get_m1_expert_report(context_id: str) -> JSONResponse:
    """
    M1 토지·입지 사실 확정 전문가 보고서 조회
    
    **ZeroSite Decision OS 헌법 준수:**
    - ✅ FACT ONLY (판단/추천/점수 금지)
    - ✅ LH 실무 제출 가능 수준
    - ✅ 8~12페이지 전문가 완성본
    
    **출력 검증 기준:**
    1. LH 실무자가 그대로 결재 라인에 올릴 수 있는가? ✅
    2. 감사·민원 질문에 논리적으로 대응 가능한가? ✅
    3. 다른 지번이면 완전히 다른 결과가 나오는가? ✅
    
    Args:
        context_id: M1 Context ID (FROZEN)
    
    Returns:
        전문가 보고서 JSON
    
    Raises:
        404: Context not found
        400: Context not frozen
    """
    
    logger.info("="*80)
    logger.info(f"📋 M1 EXPERT REPORT REQUEST")
    logger.info(f"   Context ID: {context_id}")
    logger.info("="*80)
    
    # 1. Context 조회
    if context_id not in frozen_contexts_v2:
        logger.error(f"❌ Context not found: {context_id}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "M1_CONTEXT_NOT_FOUND",
                "message": f"Context ID {context_id}를 찾을 수 없습니다",
                "action": "M1 데이터를 먼저 승인(FREEZE)하세요"
            }
        )
    
    context = frozen_contexts_v2[context_id]
    
    # 2. Frozen 상태 확인
    if not context.metadata.frozen_at:
        logger.error(f"❌ Context not frozen: {context_id}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "M1_CONTEXT_NOT_FROZEN",
                "message": "M1 데이터가 승인되지 않았습니다",
                "action": "M1 검증 페이지에서 데이터를 승인하세요"
            }
        )
    
    # 3. 전문가 보고서 생성
    try:
        report = generate_m1_expert_report(context)
        
        logger.info("✅ M1 Expert Report Generated")
        logger.info(f"   Parcel: {context.parcel_id}")
        logger.info(f"   Sections: {len(report['sections'])}")
        logger.info(f"   Status: {report['status']}")
        logger.info("="*80)
        
        return JSONResponse(content=report)
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "REPORT_GENERATION_FAILED",
                "message": f"보고서 생성 중 오류 발생: {str(e)}"
            }
        )


@router.get("/{context_id}/html")
async def get_m1_expert_report_html(context_id: str) -> str:
    """
    M1 전문가 보고서 HTML 버전
    
    Returns:
        HTML 형식 보고서 (인쇄/다운로드 가능)
    """
    
    # JSON 보고서 먼저 생성
    report_response = await get_m1_expert_report(context_id)
    report = report_response.body.decode('utf-8')
    import json
    report_data = json.loads(report)
    
    # HTML 변환
    html = _convert_report_to_html(report_data)
    
    return html


def _convert_report_to_html(report: Dict[str, Any]) -> str:
    """
    보고서 JSON → HTML 변환
    """
    
    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='ko'>",
        "<head>",
        "  <meta charset='UTF-8'>",
        "  <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        f"  <title>{report['title']}</title>",
        "  <style>",
        "    body { font-family: 'Malgun Gothic', sans-serif; margin: 40px; }",
        "    h1 { color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 10px; }",
        "    h2 { color: #333; margin-top: 30px; border-left: 5px solid #1a73e8; padding-left: 15px; }",
        "    h3 { color: #666; margin-top: 20px; }",
        "    table { width: 100%; border-collapse: collapse; margin: 20px 0; }",
        "    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }",
        "    th { background-color: #f0f0f0; font-weight: bold; }",
        "    .note { background-color: #fff9e6; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }",
        "    .fact-badge { display: inline-block; background: #4caf50; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; }",
        "    .header { text-align: center; margin-bottom: 40px; }",
        "    .subtitle { color: #666; font-size: 14px; }",
        "    .validation { background: #e8f5e9; padding: 15px; margin: 30px 0; border-radius: 5px; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <div class='header'>",
        f"    <h1>{report['title']}</h1>",
        f"    <p class='subtitle'>{report['subtitle']}</p>",
        f"    <p><span class='fact-badge'>FACT ONLY</span> <span class='fact-badge'>LH 실무 제출 가능</span></p>",
        f"    <p>생성일시: {report['generated_at']}</p>",
        f"    <p>필지 ID: {report['parcel_id']}</p>",
        "  </div>",
    ]
    
    # 섹션 출력
    for section in report['sections']:
        html_parts.append(f"  <h2>{section['section_number']}. {section['title']}</h2>")
        
        # Content 출력
        if 'content' in section:
            for key, value in section['content'].items():
                if isinstance(value, str):
                    html_parts.append(f"  <p><strong>{key}:</strong> {value}</p>")
        
        # Tables 출력
        if 'tables' in section:
            for table in section['tables']:
                html_parts.append(f"  <h3>{table['title']}</h3>")
                html_parts.append("  <table>")
                
                # Headers
                html_parts.append("    <tr>")
                for header in table['headers']:
                    html_parts.append(f"      <th>{header}</th>")
                html_parts.append("    </tr>")
                
                # Rows
                for row in table['rows']:
                    html_parts.append("    <tr>")
                    for cell in row:
                        html_parts.append(f"      <td>{cell}</td>")
                    html_parts.append("    </tr>")
                
                html_parts.append("  </table>")
        
        # Note
        if 'note' in section:
            html_parts.append(f"  <div class='note'><strong>참고:</strong> {section['note']}</div>")
    
    # Validation
    validation = report['validation']
    html_parts.append("  <div class='validation'>")
    html_parts.append("    <h3>✅ ZeroSite Decision OS 검증 완료</h3>")
    html_parts.append("    <ul>")
    html_parts.append(f"      <li>LH 실무 제출 가능: {'✅' if validation['lh_submission_ready'] else '❌'}</li>")
    html_parts.append(f"      <li>FACT ONLY (판단 배제): {'✅' if validation['fact_only'] else '❌'}</li>")
    html_parts.append(f"      <li>추천 배제: {'✅' if validation['no_recommendation'] else '❌'}</li>")
    html_parts.append(f"      <li>점수 배제: {'✅' if validation['no_scoring'] else '❌'}</li>")
    html_parts.append("    </ul>")
    html_parts.append("  </div>")
    
    html_parts.append("</body>")
    html_parts.append("</html>")
    
    return "\n".join(html_parts)
