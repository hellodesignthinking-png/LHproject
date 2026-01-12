"""
M5 Expert Report API
===================

ZeroSite Decision OS - M5 전문가 보고서 API
목적: M5 사업성·리스크 검증 보고서 생성 및 조회

Author: ZeroSite Decision OS
Date: 2026-01-12
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import json

from app.modules.m5_feasibility.report_template import generate_m5_expert_report

# ========================================
# Router 초기화
# ========================================
router = APIRouter(
    prefix="/api/reports/m5",
    tags=["M5 Expert Report"]
)

# ========================================
# Mock Data Helpers (실제 구현 시 DB 연동)
# ========================================

def get_m1_data(context_id: str) -> Dict[str, Any]:
    """M1 데이터 조회"""
    return {
        "area_sqm": 1500,
        "zone_type": "준주거지역",
        "bcr": 60,
        "far": 300,
        "official_land_price": 25000000,
        "address": "서울시 마포구 성산동 123-4",
        "frozen_at": "2026-01-12T10:00:00Z"
    }

def get_m2_data(context_id: str) -> Dict[str, Any]:
    """M2 데이터 조회"""
    return {
        "adjusted_land_value": 42000000000,
        "value_range": {"lower": 38000000000, "upper": 46000000000},
        "unit_price_sqm": 28000000,
        "confidence_score": 0.82
    }

def get_m3_data(context_id: str) -> Dict[str, Any]:
    """M3 데이터 조회"""
    return {
        "recommended_type": "청년 매입임대",
        "lh_pass_score": 85,
        "policy_alignment": "청년 주거 안정 정책과 부합"
    }

def get_m4_data(context_id: str) -> Dict[str, Any]:
    """M4 데이터 조회"""
    return {
        "lh_recommended": {
            "total_floor_area": 10200,
            "units": 240,
            "floors_estimated": 12
        },
        "parking_plan": {"applied": 90}
    }

def get_m5_result(context_id: str) -> Dict[str, Any]:
    """M5 결과 조회"""
    return {
        "cost_breakdown": {
            "land_cost": 38000000000,
            "construction_cost": 28560000000,
            "design_supervision": 2570400000,
            "contingency": 3456520000,
            "total_cost": 72586920000
        },
        "lh_purchase": {
            "base_price": 81840000000,
            "community_bonus": 0,
            "total_purchase_price": 81840000000,
            "buffer_ratio": 12.76
        },
        "risk_summary": [
            {
                "risk": "공사비 상승",
                "level": "MEDIUM",
                "probability": "중간",
                "impact": "총사업비 5~10% 증가 가능",
                "mitigation": "표준형 설계 적용 및 예비비 5% 확보"
            }
        ],
        "stability_assessment": "✅ 안정적: LH 매입 기준에서 적정 범위. 사업 추진 가능.",
        "feasibility_conclusion": "LH 매입 구조 기준으로 사업성 확보. 안전 마진 12.8%로 리스크 흡수 가능.",
        "calculated_at": "2026-01-12T10:30:00Z"
    }

# ========================================
# API Endpoints
# ========================================

@router.get(
    "/{context_id}",
    summary="M5 Expert Report 조회 (JSON)",
    description="M5 사업성·리스크 검증 전문가 보고서를 JSON 형식으로 조회합니다."
)
async def get_m5_report_json(
    context_id: str = Path(..., description="M1 Context ID")
):
    """M5 Expert Report 조회 (JSON)"""
    
    try:
        # 데이터 수집
        m1_data = get_m1_data(context_id)
        m2_data = get_m2_data(context_id)
        m3_data = get_m3_data(context_id)
        m4_data = get_m4_data(context_id)
        m5_result = get_m5_result(context_id)
        
        # 보고서 생성
        report = generate_m5_expert_report(
            project_id="sample-project",
            context_id=context_id,
            m5_result=m5_result,
            m1_data=m1_data,
            m2_data=m2_data,
            m3_data=m3_data,
            m4_data=m4_data
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"M5 보고서 생성 실패: {str(e)}"
        )

@router.get(
    "/{context_id}/html",
    response_class=HTMLResponse,
    summary="M5 Expert Report 조회 (HTML)",
    description="M5 사업성·리스크 검증 전문가 보고서를 HTML 형식으로 조회합니다."
)
async def get_m5_report_html(
    context_id: str = Path(..., description="M1 Context ID")
):
    """M5 Expert Report 조회 (HTML)"""
    
    try:
        # JSON 보고서 생성
        report = await get_m5_report_json(context_id)
        
        # HTML 변환
        html_content = generate_html_report(report)
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"M5 HTML 보고서 생성 실패: {str(e)}"
        )

# ========================================
# HTML 생성 함수
# ========================================

def generate_html_report(report: Dict[str, Any]) -> str:
    """M5 보고서를 HTML로 변환"""
    
    sections_html = ""
    
    for section in report.get("sections", []):
        sections_html += f"""
        <section class="report-section">
            <h2>{section['title']}</h2>
            <div class="section-content">
                {format_content_to_html(section['content'])}
            </div>
        </section>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>M5 사업성·리스크 검증 보고서</title>
        <style>
            body {{
                font-family: 'Malgun Gothic', sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .report-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .report-header h1 {{
                margin: 0 0 10px 0;
                font-size: 28px;
            }}
            .report-section {{
                background: white;
                padding: 25px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .report-section h2 {{
                color: #667eea;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
            }}
            .highlight {{
                background-color: #fff3cd;
                padding: 15px;
                border-left: 4px solid #ffc107;
                margin: 15px 0;
            }}
            .risk-high {{
                color: #dc3545;
                font-weight: bold;
            }}
            .risk-medium {{
                color: #ffc107;
                font-weight: bold;
            }}
            .risk-low {{
                color: #28a745;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="report-header">
            <h1>🏢 M5 사업성·리스크 검증 보고서</h1>
            <p>ZeroSite Decision OS - Module M5 (LH-SAFE)</p>
            <p>Context ID: {report.get('context_id', 'N/A')}</p>
            <p>생성일시: {report.get('generated_at', 'N/A')}</p>
        </div>
        
        {sections_html}
        
        <footer style="text-align: center; padding: 20px; color: #666;">
            <p>ⓒ ZeroSite Decision OS | Module: M5 – FEASIBILITY & RISK (LH-SAFE)</p>
        </footer>
    </body>
    </html>
    """
    
    return html

def format_content_to_html(content: Any) -> str:
    """콘텐츠를 HTML로 포맷팅"""
    
    if isinstance(content, dict):
        html = "<table>"
        for key, value in content.items():
            html += f"<tr><th>{key}</th><td>{format_content_to_html(value)}</td></tr>"
        html += "</table>"
        return html
    elif isinstance(content, list):
        html = "<ul>"
        for item in content:
            html += f"<li>{format_content_to_html(item)}</li>"
        html += "</ul>"
        return html
    else:
        return str(content)
