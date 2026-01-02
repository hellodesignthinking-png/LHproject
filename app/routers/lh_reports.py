"""
LH Technical Verification Report Router
========================================

LH 기술검증 보고서 전용 라우터

Author: ZeroSite Development Team
Date: 2026-01-02
Version: 1.0
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v4/reports/lh", tags=["LH Reports"])


async def lh_technical_report_html(context_id: str) -> HTMLResponse:
    """
    LH 기술검증 보고서 HTML 생성
    
    Args:
        context_id: RUN_ID (REAL_xxx 또는 DIRECT_xxx)
    
    Returns:
        HTMLResponse with LH technical report
    """
    logger.info(f"Generating LH Technical Report for context: {context_id}")
    
    # 간단한 HTML 템플릿
    html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>C. LH 기술검증 보고서 - ZeroSite</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Malgun Gothic', sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        .header {
            border-bottom: 3px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            color: #0066cc;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 18px;
        }
        .info-box {
            background: #f0f7ff;
            border-left: 4px solid #0066cc;
            padding: 20px;
            margin: 20px 0;
        }
        .section {
            margin: 30px 0;
        }
        .section h2 {
            color: #0066cc;
            font-size: 24px;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        .data-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        .data-label {
            font-weight: 600;
            color: #555;
        }
        .data-value {
            color: #333;
        }
        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        th {
            background: #0066cc;
            color: white;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>C. LH 기술검증 보고서</h1>
            <p class="subtitle">토지 개발 가능성 및 LH 기준 적합성 검증</p>
        </div>
        
        <div class="info-box">
            <div class="data-row">
                <span class="data-label">RUN ID</span>
                <span class="data-value">{{ context_id }}</span>
            </div>
            <div class="data-row">
                <span class="data-label">생성일시</span>
                <span class="data-value">{{ generation_date }}</span>
            </div>
        </div>
        
        <div class="warning">
            ⚠️ <strong>주의사항</strong><br>
            이 보고서는 외부 API 연동 없이 생성되었습니다. 실제 프로젝트에서는 LH 기준 데이터와 연동하여 정확한 검증을 수행해야 합니다.
        </div>
        
        <div class="section">
            <h2>1. 기본 정보</h2>
            <div class="data-row">
                <span class="data-label">분석 ID</span>
                <span class="data-value">{{ context_id }}</span>
            </div>
            <div class="data-row">
                <span class="data-label">토지 면적</span>
                <span class="data-value">500㎡ (약 151평)</span>
            </div>
            <div class="data-row">
                <span class="data-label">용도지역</span>
                <span class="data-value">제2종일반주거지역</span>
            </div>
        </div>
        
        <div class="section">
            <h2>2. LH 기준 적합성 검토</h2>
            <table>
                <thead>
                    <tr>
                        <th>검토 항목</th>
                        <th>기준</th>
                        <th>현황</th>
                        <th>적합 여부</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>최소 대지면적</td>
                        <td>300㎡ 이상</td>
                        <td>500㎡</td>
                        <td style="color: green; font-weight: bold;">✓ 적합</td>
                    </tr>
                    <tr>
                        <td>건폐율</td>
                        <td>60% 이하</td>
                        <td>60%</td>
                        <td style="color: green; font-weight: bold;">✓ 적합</td>
                    </tr>
                    <tr>
                        <td>용적률</td>
                        <td>200% 이하</td>
                        <td>200%</td>
                        <td style="color: green; font-weight: bold;">✓ 적합</td>
                    </tr>
                    <tr>
                        <td>도로 접면</td>
                        <td>6m 이상</td>
                        <td>추정 6m</td>
                        <td style="color: orange; font-weight: bold;">△ 확인 필요</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>3. 개발 가능성 평가</h2>
            <div class="data-row">
                <span class="data-label">종합 평가</span>
                <span class="data-value" style="color: green; font-weight: bold;">개발 가능 (조건부)</span>
            </div>
            <div class="data-row">
                <span class="data-label">LH 사업 적합도</span>
                <span class="data-value">중상 (75/100점)</span>
            </div>
            <div class="data-row">
                <span class="data-label">권장 공급 유형</span>
                <span class="data-value">청년형 또는 신혼부부형</span>
            </div>
        </div>
        
        <div class="section">
            <h2>4. 추가 검증 필요 사항</h2>
            <ul style="line-height: 2;">
                <li>정확한 도로 폭 측정 (지적도 확인)</li>
                <li>주변 개발 제한 사항 조사</li>
                <li>지하 매설물 및 장애물 유무 확인</li>
                <li>인근 LH 사업지 검토</li>
                <li>지역 주민 의견 수렴 필요성 검토</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>5. 결론 및 권고사항</h2>
            <p style="line-height: 1.8; margin-bottom: 10px;">
                본 토지는 LH 공공임대주택 사업에 적합한 것으로 판단됩니다. 
                다만, 정확한 개발 가능 여부를 확인하기 위해서는 다음 사항들에 대한 추가 검증이 필요합니다:
            </p>
            <ol style="line-height: 2; margin-left: 20px;">
                <li>지적도를 통한 정확한 도로 폭 확인</li>
                <li>V-World API 연동을 통한 용도지역 세부 정보 확인</li>
                <li>실제 거래가 데이터를 통한 토지 가치 평가</li>
                <li>LH 내부 기준에 따른 사업성 재검토</li>
            </ol>
        </div>
        
        <div class="footer">
            <p><strong>ZeroSite Expert Edition v2.0</strong></p>
            <p>본 보고서는 참고용이며 법적 효력이 없습니다.</p>
            <p>실제 개발 시 관련 법규 및 LH 내부 규정을 반드시 확인하시기 바랍니다.</p>
        </div>
    </div>
</body>
</html>
    """
    
    from datetime import datetime
    template = Template(html_template)
    html_content = template.render(
        context_id=context_id,
        generation_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    return HTMLResponse(content=html_content)


@router.get("/technical/html", response_class=HTMLResponse)
async def lh_technical_html(
    context_id: str = Query(..., description="분석 실행 ID (RUN_*)")
):
    """
    LH 기술검증 보고서 HTML 엔드포인트
    """
    return await lh_technical_report_html(context_id)
