"""
M3 – HOUSING TYPE SUITABILITY (LH-GRADE)
공급유형 적합성 전문가 보고서 API

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
    prefix="/api/reports/m3",
    tags=["M3 - Expert Report"]
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
                detail="M2 result not found"
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

def get_m3_result(context_id: str) -> Dict[str, Any]:
    """M3 분석 결과 조회"""
    try:
        from app.api.endpoints.m3_housing_type_api import m3_results
        
        if context_id not in m3_results:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "M3_RESULT_NOT_FOUND",
                    "message": "M3 analysis not yet performed",
                    "action": "Please analyze M3 first: POST /api/projects/{project_id}/modules/M3/analyze"
                }
            )
        
        result = m3_results[context_id]
        
        if hasattr(result, 'model_dump'):
            return result.model_dump()
        elif hasattr(result, 'dict'):
            return result.dict()
        else:
            return dict(result)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load M3 result: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load M3 result: {str(e)}"
        )

# ============================================================
# API Endpoints
# ============================================================

@router.get("/{context_id}")
async def get_m3_expert_report_json(context_id: str):
    """
    M3 전문가 보고서 조회 (JSON)
    
    Args:
        context_id: M1 Context ID (FROZEN 상태)
    
    Returns:
        M3 전문가 보고서 (JSON 포맷)
    """
    logger.info(f"📊 M3 Expert Report Request - Context: {context_id}")
    
    try:
        # M1 데이터 로드
        m1_data = get_m1_frozen_data(context_id)
        logger.info(f"✅ M1 데이터 로드 완료")
        
        # M2 결과 로드
        m2_data = get_m2_result(context_id)
        logger.info(f"✅ M2 결과 로드 완료")
        
        # M3 결과 로드
        m3_result = get_m3_result(context_id)
        logger.info(f"✅ M3 결과 로드 완료")
        
        # 전문가 보고서 생성
        from app.modules.m3_lh_demand.report_template import generate_m3_expert_report
        
        report = generate_m3_expert_report(m1_data, m2_data, m3_result)
        
        logger.info(f"✅ M3 Expert Report 생성 완료")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M3 Report 생성 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate M3 report: {str(e)}"
        )

@router.get("/{context_id}/html", response_class=HTMLResponse)
async def get_m3_expert_report_html(context_id: str):
    """
    M3 전문가 보고서 조회 (HTML)
    
    Args:
        context_id: M1 Context ID (FROZEN 상태)
    
    Returns:
        M3 전문가 보고서 (HTML 포맷)
    """
    logger.info(f"📄 M3 Expert Report HTML Request - Context: {context_id}")
    
    try:
        # JSON 보고서 조회
        report = await get_m3_expert_report_json(context_id)
        
        # HTML 변환
        html_content = convert_m3_report_to_html(report)
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ M3 HTML 생성 실패: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate M3 HTML: {str(e)}"
        )

# ============================================================
# HTML Conversion
# ============================================================

def convert_m3_report_to_html(report: Dict[str, Any]) -> str:
    """M3 보고서를 HTML로 변환"""
    
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
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 30px;
            }}
            .header h1 {{
                font-size: 32px;
                color: #4CAF50;
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
                background-color: #e8f5e9;
                color: #4CAF50;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
            }}
            .section {{
                margin-bottom: 50px;
            }}
            .section-header {{
                background-color: #4CAF50;
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
            .success {{
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 15px 0;
            }}
            .recommendation-box {{
                background-color: #e8f5e9;
                border: 2px solid #4CAF50;
                padding: 20px;
                margin: 20px 0;
                border-radius: 10px;
            }}
            .recommendation-box h3 {{
                color: #4CAF50;
                margin-top: 0;
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
                color: #4CAF50;
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
    if validation.get('lh_pass_probability'):
        html += '<span class="badge">✅ LH 통과 확률 기반</span>'
    if validation.get('policy_based'):
        html += '<span class="badge">✅ 정책 근거 명확</span>'
    if validation.get('rejection_logic'):
        html += '<span class="badge">✅ 탈락 논리 제시</span>'
    if validation.get('single_recommendation'):
        html += '<span class="badge">✅ 단일 추천</span>'
    
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
        
        # Tables
        for key, value in content.items():
            if isinstance(value, dict) and 'columns' in value and 'rows' in value:
                html += "<table>"
                html += "<tr>" + "".join([f"<th>{col}</th>" for col in value['columns']]) + "</tr>"
                for row in value['rows']:
                    html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
                html += "</table>"
        
        # Recommendation Box
        if 'recommendation_box' in content:
            box = content['recommendation_box']
            html += f"""
            <div class="recommendation-box">
                <h3>{box.get('title')}</h3>
                <p><strong>LH 통과 점수:</strong> {box.get('score')}점</p>
                <p><strong>선정 논리:</strong> {box.get('rationale')}</p>
            </div>
            """
        
        # LH Persuasion Text
        if 'lh_persuasion_text' in content:
            html += f"""
            <div class="success">
                <strong>LH 설득 논리:</strong><br>
                {content['lh_persuasion_text']}
            </div>
            """
        
        # Lists
        for list_key in ['evaluation_criteria', 'key_policies', 'key_differentiators', 
                          'rejection_logic', 'lh_internal_review', 'next_steps']:
            if list_key in content:
                html += f"<p><strong>{list_key.replace('_', ' ').title()}:</strong></p><ul>"
                for item in content[list_key]:
                    html += f"<li>{item}</li>"
                html += "</ul>"
        
        # Persuasion Points
        if 'persuasion_points' in content:
            html += "<h4>주요 설득 포인트:</h4>"
            for point in content['persuasion_points']:
                html += f"""
                <div class="highlight">
                    <strong>{point.get('point')}:</strong> {point.get('logic')}<br>
                    <em>근거: {point.get('evidence')}</em>
                </div>
                """
        
        # Final Statement
        if 'final_statement' in content:
            html += f"<div class='highlight'><strong>최종 의견:</strong> {content['final_statement']}</div>"
        
        # Note
        if 'note' in content:
            html += f"<p><em>{content['note']}</em></p>"
        
        html += """
                </div>
            </div>
        """
    
    # Footer
    html += f"""
            <div class="footer">
                <p>© ZeroSite by AntennaHoldings | Natai Heum</p>
                <p>Module: M3 – HOUSING TYPE SUITABILITY (LH-GRADE)</p>
                <p>Generated: {report['generated_at']}</p>
                <p>Context ID: {report['context_id']}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html
