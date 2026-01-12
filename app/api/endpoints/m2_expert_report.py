"""
M2 – LAND VALUATION (LH-GRADE)
토지감정평가 전문가 보고서 API

역할:
- M2 계산 결과를 LH 제출 가능한 전문가 보고서로 변환
- 8개 필수 섹션 (8~12페이지 분량)
- JSON 및 HTML 포맷 지원

Author: ZeroSite Decision OS Team
Date: 2026-01-12
Version: 2.0
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/reports/m2",
    tags=["M2 - Expert Report"]
)

# ============================================================
# Helper Functions
# ============================================================

def get_m1_frozen_data(context_id: str) -> Dict[str, Any]:
    """M1 FROZEN 데이터 조회"""
    try:
        from app.api.endpoints.m1_context_freeze_v2 import frozen_contexts_v2
        
        if context_id not in frozen_contexts_v2:
            raise HTTPException(
                status_code=404,
                detail=f"M1 Context not found: {context_id}"
            )
        
        frozen_ctx = frozen_contexts_v2[context_id]
        
        if hasattr(frozen_ctx, 'model_dump'):
            return frozen_ctx.model_dump()
        elif hasattr(frozen_ctx, 'dict'):
            return frozen_ctx.dict()
        else:
            return dict(frozen_ctx)
            
    except Exception as e:
        logger.error(f"Failed to load M1 data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load M1 data: {str(e)}"
        )

def get_m2_result(context_id: str) -> Dict[str, Any]:
    """M2 계산 결과 조회"""
    try:
        from app.api.endpoints.m2_valuation_api import m2_results
        
        if context_id not in m2_results:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "M2_RESULT_NOT_FOUND",
                    "message": "M2 calculation not yet performed",
                    "action": "Please calculate M2 first: POST /api/projects/{project_id}/modules/M2/calculate"
                }
            )
        
        result = m2_results[context_id]
        
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        else:
            return dict(result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load M2 result: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load M2 result: {str(e)}"
        )

# ============================================================
# API Endpoints
# ============================================================

@router.get("/{context_id}")
async def get_m2_expert_report_json(context_id: str):
    """
    M2 전문가 보고서 조회 (JSON)
    
    Args:
        context_id: M1 Context ID (FROZEN 상태)
    
    Returns:
        M2 전문가 보고서 (JSON 포맷)
    """
    logger.info(f"📊 M2 Expert Report Request - Context: {context_id}")
    
    try:
        # M1 데이터 로드
        m1_data = get_m1_frozen_data(context_id)
        logger.info(f"✅ M1 데이터 로드 완료")
        
        # M2 결과 로드
        m2_result = get_m2_result(context_id)
        logger.info(f"✅ M2 결과 로드 완료")
        
        # 전문가 보고서 생성
        from app.modules.m2_appraisal.report_template import generate_m2_expert_report
        
        report = generate_m2_expert_report(m1_data, m2_result)
        
        logger.info(f"✅ M2 Expert Report 생성 완료")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M2 Report 생성 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate M2 report: {str(e)}"
        )

@router.get("/{context_id}/html", response_class=HTMLResponse)
async def get_m2_expert_report_html(context_id: str):
    """
    M2 전문가 보고서 조회 (HTML)
    
    Args:
        context_id: M1 Context ID (FROZEN 상태)
    
    Returns:
        M2 전문가 보고서 (HTML 포맷)
    """
    logger.info(f"📄 M2 Expert Report HTML Request - Context: {context_id}")
    
    try:
        # JSON 보고서 조회
        report = await get_m2_expert_report_json(context_id)
        
        # HTML 변환
        html_content = convert_m2_report_to_html(report)
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M2 HTML 생성 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate M2 HTML: {str(e)}"
        )

# ============================================================
# HTML Conversion
# ============================================================

def convert_m2_report_to_html(report: Dict[str, Any]) -> str:
    """M2 보고서를 HTML로 변환"""
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report['title']}</title>
        <style>
            body {{
                font-family: 'Noto Sans KR', sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px;
                line-height: 1.6;
                background-color: #f5f5f5;
            }}
            .report-container {{
                background-color: white;
                padding: 60px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                margin-bottom: 60px;
                border-bottom: 3px solid #0066cc;
                padding-bottom: 30px;
            }}
            .header h1 {{
                font-size: 32px;
                color: #0066cc;
                margin-bottom: 10px;
            }}
            .header .subtitle {{
                font-size: 16px;
                color: #666;
            }}
            .validation-badges {{
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 20px 0;
            }}
            .badge {{
                background-color: #e8f4f8;
                color: #0066cc;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            .section {{
                margin-bottom: 50px;
            }}
            .section-header {{
                background-color: #0066cc;
                color: white;
                padding: 15px 20px;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .section-content {{
                padding: 0 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #f0f0f0;
                font-weight: bold;
            }}
            .highlight {{
                background-color: #fff9e6;
                padding: 15px;
                border-left: 4px solid #ffc107;
                margin: 15px 0;
            }}
            .warning {{
                background-color: #fff3cd;
                border-left: 4px solid #ff9800;
                padding: 15px;
                margin: 15px 0;
            }}
            .success {{
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 15px 0;
            }}
            ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            ul li {{
                padding: 8px 0;
                padding-left: 25px;
                position: relative;
            }}
            ul li:before {{
                content: "▸";
                position: absolute;
                left: 0;
                color: #0066cc;
            }}
            .footer {{
                margin-top: 60px;
                text-align: center;
                font-size: 12px;
                color: #999;
                border-top: 1px solid #ddd;
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="report-container">
            <div class="header">
                <h1>{report['title']}</h1>
                <div class="subtitle">{report['subtitle']}</div>
                <div class="validation-badges">
    """
    
    # 검증 배지
    validation = report.get('validation', {})
    if validation.get('lh_submission_ready'):
        html += '<span class="badge">✅ LH 제출 가능</span>'
    if validation.get('auditable'):
        html += '<span class="badge">✅ 감사 대응 가능</span>'
    if validation.get('explainable'):
        html += '<span class="badge">✅ 논리 설명 가능</span>'
    if validation.get('range_based'):
        html += '<span class="badge">✅ 범위 기반 평가</span>'
    if validation.get('risk_disclosed'):
        html += '<span class="badge">✅ 리스크 공개</span>'
    
    html += """
                </div>
            </div>
    """
    
    # 섹션 렌더링
    for section in report.get('sections', []):
        html += f"""
            <div class="section">
                <div class="section-header">
                    {section['section_number']}. {section['section_title']}
                </div>
                <div class="section-content">
        """
        
        content = section.get('content', {})
        
        # Description
        if 'description' in content:
            html += f"<p>{content['description']}</p>"
        
        # Purpose, Scope, Methodology
        if 'purpose' in content:
            html += f"<div class='highlight'><strong>목적:</strong> {content['purpose']}</div>"
        if 'scope' in content:
            html += f"<p><strong>범위:</strong> {content['scope']}</p>"
        if 'methodology' in content:
            html += f"<p><strong>방법론:</strong> {content['methodology']}</p>"
        
        # Tables
        for key, value in content.items():
            if isinstance(value, dict) and 'columns' in value and 'rows' in value:
                html += "<table>"
                html += "<tr>" + "".join([f"<th>{col}</th>" for col in value['columns']]) + "</tr>"
                for row in value['rows']:
                    html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
                html += "</table>"
        
        # Lists
        if 'key_findings' in content:
            html += "<div class='success'><strong>주요 발견사항:</strong><ul>"
            for item in content['key_findings']:
                html += f"<li>{item}</li>"
            html += "</ul></div>"
        
        if 'correction_factors' in content:
            html += "<p><strong>보정 요인:</strong></p><ul>"
            for item in content['correction_factors']:
                html += f"<li>{item}</li>"
            html += "</ul>"
        
        if 'disclaimer' in content:
            html += "<div class='warning'><strong>⚠️ 주의사항:</strong><ul>"
            for item in content['disclaimer']:
                html += f"<li>{item}</li>"
            html += "</ul></div>"
        
        if 'lh_review_notes' in content:
            html += "<div class='highlight'><strong>LH 검토 의견:</strong><ul>"
            for note in content['lh_review_notes']:
                if isinstance(note, dict):
                    priority = note.get('priority', 'MEDIUM')
                    priority_emoji = "🔴" if priority == "HIGH" else "🟡"
                    html += f"<li>{priority_emoji} {note.get('note', '')}</li>"
                else:
                    html += f"<li>{note}</li>"
            html += "</ul></div>"
        
        if 'next_steps' in content:
            html += "<p><strong>다음 단계:</strong></p><ul>"
            for step in content['next_steps']:
                html += f"<li>{step}</li>"
            html += "</ul>"
        
        if 'final_statement' in content:
            html += f"<div class='highlight'><strong>최종 의견:</strong> {content['final_statement']}</div>"
        
        html += """
                </div>
            </div>
        """
    
    # Footer
    html += f"""
            <div class="footer">
                <p>© ZeroSite by AntennaHoldings | Natai Heum</p>
                <p>Module: M2 – LAND VALUATION (LH-GRADE)</p>
                <p>Generated: {report['generated_at']}</p>
                <p>Context ID: {report['context_id']}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
