"""
Phase 8: 모듈별 보고서 및 종합 최종보고서 API 라우터
========================================================

M2-M6 모듈별 보고서와 종합 최종보고서(Type A)를 생성하는 API 엔드포인트

작성일: 2026-01-10
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from typing import Optional
import logging
from datetime import datetime

from app.services.phase8_module_report_generator import Phase8ModuleReportGenerator
from app.models.phase8_report_types import (
    ModuleEnum,
    ModuleReportResponse,
)

# 기존 파이프라인 및 컨텍스트 임포트 (실제 구현에 맞게 조정 필요)
# from app.core.pipeline.zer0site_pipeline import ZeroSitePipeline
# from app.services.context_manager import ContextManager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v4/reports/phase8",
    tags=["Phase 8 Reports - Module & Comprehensive"]
)

# 보고서 생성기 인스턴스
report_generator = Phase8ModuleReportGenerator()


# ========================================
# 모듈별 보고서 엔드포인트
# ========================================

@router.get("/modules/m2/html", response_class=HTMLResponse)
async def get_m2_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M2: 토지감정평가 보고서 (HTML)
    
    - 거래사례 3-5건 상세
    - 가격 형성 논리
    - 리스크 요인 분석
    """
    try:
        logger.info(f"Generating M2 report HTML for context_id={context_id}")
        
        # TODO: 실제 구현 시 파이프라인 결과를 가져와야 함
        # pipeline_result = await get_pipeline_result(context_id)
        # address = await get_address(context_id)
        
        # 임시 응답 (실제 구현 필요)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M2 토지감정평가 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; }}
                h1 {{ color: #0A1628; }}
                .info {{ background: #e3f2fd; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>M2. 토지감정평가 보고서</h1>
            <div class="info">
                <p><strong>Context ID:</strong> {context_id}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><em>Phase 8 모듈별 보고서 시스템이 정상 작동 중입니다.</em></p>
                <p><strong>다음 단계:</strong> 파이프라인 결과 연동 후 실제 보고서 생성</p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M2 report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"M2 보고서 생성 실패: {str(e)}")


@router.get("/modules/m3/html", response_class=HTMLResponse)
async def get_m3_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M3: 공급 유형 판단 보고서 (HTML)
    
    - 5개 후보 유형 전체 평가
    - 정책 적합성 매트릭스
    - 최종 선택 논리
    """
    try:
        logger.info(f"Generating M3 report HTML for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M3 공급 유형 판단 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; }}
                h1 {{ color: #0A1628; }}
                .info {{ background: #e8f5e9; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>M3. 공급 유형 판단 보고서</h1>
            <div class="info">
                <p><strong>Context ID:</strong> {context_id}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><em>Phase 8 모듈별 보고서 시스템이 정상 작동 중입니다.</em></p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M3 report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"M3 보고서 생성 실패: {str(e)}")


@router.get("/modules/m4/html", response_class=HTMLResponse)
async def get_m4_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M4: 건축 규모 검토 보고서 (HTML)
    
    - 3개 시나리오 비교
    - 주차 계획 대안
    - 최적 규모 선택 논리
    """
    try:
        logger.info(f"Generating M4 report HTML for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M4 건축 규모 검토 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; }}
                h1 {{ color: #0A1628; }}
                .info {{ background: #fff3e0; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>M4. 건축 규모 검토 보고서</h1>
            <div class="info">
                <p><strong>Context ID:</strong> {context_id}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><em>Phase 8 모듈별 보고서 시스템이 정상 작동 중입니다.</em></p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M4 report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"M4 보고서 생성 실패: {str(e)}")


@router.get("/modules/m5/html", response_class=HTMLResponse)
async def get_m5_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M5: 사업성 분석 보고서 (HTML)
    
    - 사업비 구조 상세
    - IRR/NPV 해석
    - Sensitivity 분석
    """
    try:
        logger.info(f"Generating M5 report HTML for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M5 사업성 분석 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; }}
                h1 {{ color: #0A1628; }}
                .info {{ background: #f3e5f5; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>M5. 사업성 분석 보고서</h1>
            <div class="info">
                <p><strong>Context ID:</strong> {context_id}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><em>Phase 8 모듈별 보고서 시스템이 정상 작동 중입니다.</em></p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M5 report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"M5 보고서 생성 실패: {str(e)}")


@router.get("/modules/m6/html", response_class=HTMLResponse)
async def get_m6_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    M6: 종합 판단 보고서 (HTML)
    
    - M2-M5 결과 통합
    - 긍정 요인 vs 리스크 요인
    - 최종 권고사항
    """
    try:
        logger.info(f"Generating M6 report HTML for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M6 종합 판단 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; }}
                h1 {{ color: #0A1628; }}
                .info {{ background: #e0f2f1; padding: 20px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <h1>M6. 종합 판단 보고서</h1>
            <div class="info">
                <p><strong>Context ID:</strong> {context_id}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><em>Phase 8 모듈별 보고서 시스템이 정상 작동 중입니다.</em></p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M6 report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"M6 보고서 생성 실패: {str(e)}")


# ========================================
# 종합 최종보고서(Type A) 엔드포인트
# ========================================

@router.get("/comprehensive/type-a/html", response_class=HTMLResponse)
async def get_type_a_comprehensive_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID"),
    include_m7: bool = Query(True, description="M7 커뮤니티 계획 포함 여부"),
    expand_appendix: bool = Query(True, description="부록 확장 여부")
):
    """
    Type A: 종합 최종보고서 (Master Comprehensive Report)
    
    - M2-M6 전체 모듈 상세 분석
    - M7 커뮤니티 계획 (선택)
    - 부록/Appendix (선택)
    - 60-70페이지 분량
    """
    try:
        logger.info(f"Generating Type A Comprehensive Report for context_id={context_id}")
        logger.info(f"Options: include_m7={include_m7}, expand_appendix={expand_appendix}")
        
        # TODO: 실제 구현 시 파이프라인 결과를 가져와서 템플릿에 전달
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>종합 최종보고서 (Type A) - ZeroSite</title>
            <style>
                body {{ 
                    font-family: 'Noto Sans KR', sans-serif; 
                    padding: 40px;
                    background: #f8f9fa;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                h1 {{ 
                    color: #0A1628; 
                    font-size: 32px;
                    border-bottom: 3px solid #0A1628;
                    padding-bottom: 12px;
                }}
                .info {{ 
                    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    padding: 24px; 
                    border-radius: 8px;
                    border-left: 4px solid #2196f3;
                    margin: 20px 0;
                }}
                .module-section {{
                    margin: 40px 0;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }}
                .module-title {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #1E3A5F;
                    margin-bottom: 20px;
                }}
                ul {{
                    line-height: 1.8;
                }}
                .status {{
                    display: inline-block;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 14px;
                }}
                .status.success {{
                    background: #e8f5e9;
                    color: #2e7d32;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 종합 최종보고서 (Type A)</h1>
                
                <div class="info">
                    <p><strong>📍 Context ID:</strong> {context_id}</p>
                    <p><strong>📅 생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>🔧 M7 포함:</strong> {'예' if include_m7 else '아니오'}</p>
                    <p><strong>📚 부록 확장:</strong> {'예' if expand_appendix else '아니오'}</p>
                    <p><span class="status success">✅ Phase 8 시스템 정상 작동</span></p>
                </div>
                
                <h2 style="color: #1E3A5F; margin-top: 40px;">📋 보고서 구성</h2>
                
                <div class="module-section">
                    <div class="module-title">M2. 토지감정평가</div>
                    <ul>
                        <li>거래사례 3-5건 상세 분석</li>
                        <li>가격 형성 논리 설명</li>
                        <li>리스크 요인 및 한계점</li>
                    </ul>
                </div>
                
                <div class="module-section">
                    <div class="module-title">M3. 공급 유형 판단</div>
                    <ul>
                        <li>5개 후보 유형 전체 평가</li>
                        <li>정책 적합성 매트릭스</li>
                        <li>최종 선택 논리 및 배제 근거</li>
                    </ul>
                </div>
                
                <div class="module-section">
                    <div class="module-title">M4. 건축 규모 검토</div>
                    <ul>
                        <li>3개 시나리오 비교 (법적 최대, 인센티브, 보수적)</li>
                        <li>주차 계획 대안 3가지</li>
                        <li>동선/구조 효율 분석</li>
                    </ul>
                </div>
                
                <div class="module-section">
                    <div class="module-title">M5. 사업성 분석</div>
                    <ul>
                        <li>사업비 구조 상세 설명</li>
                        <li>IRR/NPV 해석 논리</li>
                        <li>Sensitivity 분석 (비용/수익 ±10%)</li>
                        <li>리스크 해석 및 투자 권고</li>
                    </ul>
                </div>
                
                <div class="module-section">
                    <div class="module-title">M6. 종합 판단</div>
                    <ul>
                        <li>M2-M5 모듈별 결과 통합</li>
                        <li>긍정 요인 vs 리스크 요인</li>
                        <li>조건부 추진 시나리오</li>
                        <li>다음 단계 실사 계획</li>
                        <li>최종 권고사항</li>
                    </ul>
                </div>
                
                {f'''
                <div class="module-section" style="background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);">
                    <div class="module-title">M7. 커뮤니티 운영 계획</div>
                    <ul>
                        <li>커뮤니티 기획 목표 및 방향</li>
                        <li>프로그램 운영 계획</li>
                        <li>운영 주체 및 역할 분담</li>
                        <li>지속 가능성 확보 방안</li>
                    </ul>
                </div>
                ''' if include_m7 else ''}
                
                {f'''
                <div class="module-section">
                    <div class="module-title">부록 (Appendix)</div>
                    <ul>
                        <li>A. 거래사례 원문 및 상세 데이터</li>
                        <li>B. 관련 법규 및 규정 요약</li>
                        <li>C. 시나리오별 계산 근거</li>
                    </ul>
                </div>
                ''' if expand_appendix else ''}
                
                <div style="margin-top: 60px; padding: 30px; background: #f8f9fa; border-radius: 8px;">
                    <h3 style="color: #0A1628;">🚀 다음 단계</h3>
                    <ol style="line-height: 2;">
                        <li><strong>파이프라인 결과 연동:</strong> 실제 M2-M6 분석 데이터 가져오기</li>
                        <li><strong>템플릿 렌더링:</strong> Phase8ModuleReportGenerator와 템플릿 통합</li>
                        <li><strong>PDF 생성:</strong> Playwright PDF Generator 연동</li>
                        <li><strong>통합 테스트:</strong> 전체 보고서 생성 검증</li>
                    </ol>
                </div>
                
                <div style="margin-top: 40px; padding: 20px; background: #e8f5e9; border-radius: 8px; border-left: 4px solid #4caf50;">
                    <p style="margin: 0;"><strong>✅ Phase 8.1 Step 2 진행 중</strong></p>
                    <p style="margin: 8px 0 0 0; font-size: 14px; color: #666;">
                        API 라우터 구현 완료, 템플릿 통합 준비 중
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate Type A report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"종합 최종보고서 생성 실패: {str(e)}")


# ========================================
# Health Check
# ========================================

@router.get("/health")
async def health_check():
    """Phase 8 시스템 상태 확인"""
    return {
        "status": "healthy",
        "phase": "Phase 8: Module & Comprehensive Reports",
        "features": {
            "module_reports": ["M2", "M3", "M4", "M5", "M6"],
            "comprehensive_report": "Type A",
            "pdf_generation": "pending",
        },
        "endpoints": {
            "module_reports": [
                "/api/v4/reports/phase8/modules/m2/html",
                "/api/v4/reports/phase8/modules/m3/html",
                "/api/v4/reports/phase8/modules/m4/html",
                "/api/v4/reports/phase8/modules/m5/html",
                "/api/v4/reports/phase8/modules/m6/html",
            ],
            "comprehensive_report": "/api/v4/reports/phase8/comprehensive/type-a/html",
        },
        "timestamp": datetime.now().isoformat(),
    }
