"""
Integrated Report Generation API
=================================

ZeroSite Decision OS - M1~M7 통합 보고서 자동 생성
목적: 전체 모듈 결과를 단일 PDF/HTML 보고서로 결합

Author: ZeroSite Decision OS
Date: 2026-01-12
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, Any
import json
import logging
from app.services.pdf_generator import get_pdf_generator

logger = logging.getLogger(__name__)

# ========================================
# Router 초기화
# ========================================
router = APIRouter(
    prefix="/api/reports/integrated",
    tags=["Integrated Reports"]
)

# ========================================
# API Endpoints
# ========================================

@router.get(
    "/{context_id}",
    summary="통합 보고서 조회 (JSON)",
    description="M1~M7 전체 모듈 결과를 결합한 통합 보고서를 JSON 형식으로 조회합니다."
)
async def get_integrated_report_json(
    context_id: str = Path(..., description="M1 Context ID")
):
    """통합 보고서 조회 (JSON)"""
    
    try:
        # M1~M7 데이터 수집 (Mock)
        integrated_data = {
            "report_type": "INTEGRATED_FULL",
            "context_id": context_id,
            "generated_at": "2026-01-12T10:00:00Z",
            "modules": {
                "M1": {"status": "FROZEN", "title": "토지·입지 FACT"},
                "M2": {"status": "COMPLETED", "title": "토지 매입 적정성"},
                "M3": {"status": "COMPLETED", "title": "공급유형 적합성"},
                "M4": {"status": "COMPLETED", "title": "건축 규모 검토"},
                "M5": {"status": "COMPLETED", "title": "사업성·리스크"},
                "M6": {"status": "COMPLETED", "title": "LH 종합 판단"},
                "M7": {"status": "COMPLETED", "title": "커뮤니티 계획"}
            },
            "executive_summary": {
                "final_decision": "GO (조건부)",
                "lh_pass_probability": "높음",
                "key_findings": [
                    "보수적 설계 적용으로 LH 심사 통과 가능성 높음",
                    "안전 마진 12.76%로 리스크 관리 가능",
                    "민원 방어 전략 수립 완료"
                ]
            },
            "report_url": f"/api/reports/integrated/{context_id}/pdf",
            "html_url": f"/api/reports/integrated/{context_id}/html"
        }
        
        return integrated_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통합 보고서 생성 실패: {str(e)}"
        )

@router.get(
    "/{context_id}/html",
    response_class=HTMLResponse,
    summary="통합 보고서 조회 (HTML)",
    description="M1~M7 전체 모듈 결과를 결합한 통합 보고서를 HTML 형식으로 조회합니다."
)
async def get_integrated_report_html(
    context_id: str = Path(..., description="M1 Context ID")
):
    """통합 보고서 조회 (HTML)"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ZeroSite 통합 보고서</title>
        <style>
            body {{
                font-family: 'Malgun Gothic', sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .cover {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 60px;
                text-align: center;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .cover h1 {{
                font-size: 36px;
                margin: 0 0 20px 0;
            }}
            .section {{
                background: white;
                padding: 30px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }}
            .module-status {{
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                margin: 5px;
            }}
            .status-completed {{
                background: #28a745;
                color: white;
            }}
            .status-frozen {{
                background: #17a2b8;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="cover">
            <h1>🏢 ZeroSite Decision OS</h1>
            <h2>LH 신축매입임대 종합 보고서</h2>
            <p>Context ID: {context_id}</p>
            <p>생성일시: 2026-01-12</p>
        </div>
        
        <div class="section">
            <h2>📋 Executive Summary</h2>
            <p><strong>최종 판단:</strong> GO (조건부)</p>
            <p><strong>LH 매입 가능성:</strong> 높음</p>
            <h3>핵심 발견사항</h3>
            <ul>
                <li>보수적 설계 적용으로 LH 심사 통과 가능성 높음</li>
                <li>안전 마진 12.76%로 리스크 관리 가능</li>
                <li>민원 방어 전략 수립 완료</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>📊 모듈별 상태</h2>
            <p>
                <span class="module-status status-frozen">M1: FROZEN</span>
                <span class="module-status status-completed">M2: COMPLETED</span>
                <span class="module-status status-completed">M3: COMPLETED</span>
                <span class="module-status status-completed">M4: COMPLETED</span>
                <span class="module-status status-completed">M5: COMPLETED</span>
                <span class="module-status status-completed">M6: COMPLETED</span>
                <span class="module-status status-completed">M7: COMPLETED</span>
            </p>
        </div>
        
        <div class="section">
            <h2>📄 상세 보고서</h2>
            <p><strong>M1: 토지·입지 FACT</strong> - <a href="/api/reports/m1/{context_id}">상세 보기</a></p>
            <p><strong>M2: 토지 매입 적정성</strong> - <a href="/api/reports/m2/{context_id}">상세 보기</a></p>
            <p><strong>M3: 공급유형 적합성</strong> - <a href="/api/reports/m3/{context_id}">상세 보기</a></p>
            <p><strong>M4: 건축 규모 검토</strong> - 상세 보기 (준비 중)</p>
            <p><strong>M5: 사업성·리스크</strong> - <a href="/api/reports/m5/{context_id}">상세 보기</a></p>
            <p><strong>M6: LH 종합 판단</strong> - 상세 보기 (준비 중)</p>
            <p><strong>M7: 커뮤니티 계획</strong> - 상세 보기 (준비 중)</p>
        </div>
        
        <footer style="text-align: center; padding: 20px; color: #666;">
            <p>ⓒ ZeroSite Decision OS by AntennaHoldings</p>
            <p>System Mode: LH-READY | Version: 1.0</p>
        </footer>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get(
    "/{context_id}/pdf",
    response_class=FileResponse,
    summary="통합 보고서 다운로드 (PDF)",
    description="M1~M7 전체 모듈 결과를 결합한 통합 보고서를 PDF로 다운로드합니다."
)
async def get_integrated_report_pdf(
    context_id: str = Path(..., description="M1 Context ID")
):
    """통합 보고서 다운로드 (PDF)"""
    
    try:
        # 1. HTML 보고서 생성
        html_content = await _generate_html_report(context_id)
        
        # 2. 메타데이터 준비
        metadata = {
            "project_name": f"프로젝트 {context_id[:8]}",
            "land_address": "N/A",  # M1 데이터에서 가져올 예정
            "generated_at": "2026-01-12"
        }
        
        # 3. PDF 생성
        pdf_generator = get_pdf_generator()
        output_filename = f"zerosite_report_{context_id}.pdf"
        
        pdf_path = pdf_generator.generate_pdf_from_html(
            html_content,
            output_filename,
            add_cover=True,
            add_toc=True,
            add_watermark=True,
            metadata=metadata
        )
        
        logger.info(f"✅ PDF generated: {pdf_path}")
        
        # 4. PDF 파일 반환
        return FileResponse(
            path=pdf_path,
            media_type='application/pdf',
            filename=output_filename
        )
        
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF 생성 실패: {str(e)}"
        )


async def _generate_html_report(context_id: str) -> str:
    """HTML 보고서 생성 (내부 함수)"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>ZeroSite 통합 보고서</title>
    </head>
    <body>
        <div id="executive-summary" class="module-section">
            <h1>Executive Summary (M6)</h1>
            <p><strong>최종 판단:</strong> GO (조건부)</p>
            <p><strong>LH 매입 가능성:</strong> 높음</p>
            <h3>핵심 발견사항</h3>
            <ul>
                <li>보수적 설계 적용으로 LH 심사 통과 가능성 높음</li>
                <li>안전 마진 12.76%로 리스크 관리 가능</li>
                <li>민원 방어 전략 수립 완료</li>
            </ul>
        </div>
        
        <div id="m1" class="module-section">
            <h1>M1. 토지·입지 사실 확정</h1>
            <p>상태: FROZEN</p>
            <h2>1.1 토지 개요</h2>
            <table>
                <tr><th>항목</th><th>내용</th></tr>
                <tr><td>지번</td><td>서울특별시 강남구 역삼동 XXX-X</td></tr>
                <tr><td>대지면적</td><td>1,500㎡</td></tr>
                <tr><td>용도지역</td><td>제2종일반주거지역</td></tr>
            </table>
        </div>
        
        <div id="m2" class="module-section">
            <h1>M2. 토지 매입 적정성</h1>
            <p>LH 매입 관점의 적정가 범위 산정</p>
            <h2>2.1 적정 매입가</h2>
            <table>
                <tr><th>항목</th><th>금액</th></tr>
                <tr><td>적정 매입가</td><td>420억원</td></tr>
                <tr><td>신뢰도</td><td>82%</td></tr>
            </table>
        </div>
        
        <div id="m3" class="module-section">
            <h1>M3. 공급유형 적합성</h1>
            <p>추천 유형: 청년 매입임대</p>
            <p>LH 통과 점수: 85점</p>
        </div>
        
        <div id="m4" class="module-section">
            <h1>M4. 건축 규모 검토</h1>
            <p>세대수: 240세대</p>
            <p>보수적 설계 적용</p>
        </div>
        
        <div id="m5" class="module-section">
            <h1>M5. 사업성·리스크 검증</h1>
            <p>안전 마진: 12.76%</p>
            <p>리스크 관리 가능</p>
        </div>
        
        <div id="m7" class="module-section">
            <h1>M7. 커뮤니티 계획</h1>
            <p>콘셉트: 청년 생활안정형</p>
            <p>민원 방어 전략 수립 완료</p>
        </div>
        
        <div id="appendix" class="module-section">
            <h1>부록</h1>
            <h2>출처</h2>
            <ul>
                <li>국토교통부 공시지가</li>
                <li>LH 공공주택 업무처리지침</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html_content
