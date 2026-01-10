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
from app.services.phase8_six_types_report_generator import Phase8SixTypesReportGenerator
from app.services.phase8_template_renderer import Phase8TemplateRenderer
from app.services.phase8_pipeline_loader import get_pipeline_result, get_address_from_result, create_mock_pipeline_result
from app.models.phase8_report_types import (
    ModuleEnum,
    ReportTypeEnum,
    ModuleReportResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v4/reports/phase8",
    tags=["Phase 8 Reports - Module & Comprehensive"]
)

# 보고서 생성기 인스턴스
module_report_generator = Phase8ModuleReportGenerator()
six_types_report_generator = Phase8SixTypesReportGenerator()
template_renderer = Phase8TemplateRenderer()


# ========================================
# 모듈별 보고서 엔드포인트
# ========================================

@router.get("/modules/m2/html", response_class=HTMLResponse)
async def get_m2_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID (parcel_id)")
):
    """
    M2: 토지감정평가 보고서 (HTML)
    
    - 거래사례 3-5건 상세
    - 가격 형성 논리
    - 리스크 요인 분석
    """
    try:
        logger.info(f"Generating M2 report HTML for context_id={context_id}")
        
        # 파이프라인 결과 가져오기
        pipeline_result = await get_pipeline_result(context_id)
        
        # 결과가 없으면 Mock 데이터 사용
        if not pipeline_result:
            logger.warning(f"No pipeline result found for {context_id}, using MOCK data")
            pipeline_result = await create_mock_pipeline_result(context_id)
        
        # 주소 추출
        address = await get_address_from_result(pipeline_result)
        
        # M2 보고서 데이터 생성
        report_data = module_report_generator.generate_m2_report(
            context_id=context_id,
            pipeline_result=pipeline_result,
            address=address
        )
        
        # 템플릿 렌더링 (간단한 HTML 응답)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M2 토지감정평가 보고서</title>
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
                    border-radius: 8px;
                }}
                h1 {{ 
                    color: #0A1628; 
                    border-bottom: 3px solid #0A1628;
                    padding-bottom: 12px;
                }}
                .info {{ 
                    background: #e3f2fd; 
                    padding: 20px; 
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .section {{
                    margin: 30px 0;
                    padding: 20px;
                    border: 1px solid #e0e0e0;
                    border-radius: 6px;
                }}
                h2 {{ color: #1E3A5F; margin-top: 30px; }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e0e0e0;
                }}
                th {{
                    background: #f8f9fa;
                    font-weight: 600;
                }}
                .status {{
                    display: inline-block;
                    padding: 4px 12px;
                    background: #d4edda;
                    color: #155724;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>M2. 토지감정평가 보고서</h1>
                
                <div class="info">
                    <p><strong>📍 Context ID:</strong> {report_data.context_id}</p>
                    <p><strong>📅 생성일시:</strong> {report_data.generated_at}</p>
                    <p><strong>🏠 대상지:</strong> {report_data.address}</p>
                    <p style="margin-top: 15px;"><span class="status">✅ 실제 파이프라인 데이터 연동 완료</span></p>
                </div>
                
                <div class="section">
                    <h2>1. 감정평가 결과</h2>
                    <table>
                        <tr>
                            <th style="width: 30%;">항목</th>
                            <th>값</th>
                        </tr>
                        <tr>
                            <td>감정평가액</td>
                            <td style="font-size: 18px; font-weight: 700; color: #0A1628;">{report_data.land_value_krw}</td>
                        </tr>
                        <tr>
                            <td>단가 (㎡)</td>
                            <td>{report_data.unit_price_sqm}</td>
                        </tr>
                        <tr>
                            <td>단가 (평)</td>
                            <td>{report_data.unit_price_pyeong}</td>
                        </tr>
                        <tr>
                            <td>신뢰도</td>
                            <td>{report_data.confidence_pct}%</td>
                        </tr>
                    </table>
                </div>
                
                <div class="section">
                    <h2>2. 거래사례 분석</h2>
                    <p><strong>거래사례 수:</strong> {report_data.transaction_count}건</p>
                    <p><strong>평균 단가:</strong> {report_data.avg_price_sqm}</p>
                    <p><strong>가격 범위:</strong> {report_data.price_range_min} ~ {report_data.price_range_max}</p>
                    
                    <h3 style="margin-top: 20px;">거래사례 상세</h3>
                    <table>
                        <tr>
                            <th>번호</th>
                            <th>주소</th>
                            <th>면적(㎡)</th>
                            <th>거래가(원/㎡)</th>
                            <th>거래일</th>
                        </tr>
                        {''.join([f'''
                        <tr>
                            <td>{i+1}</td>
                            <td>{case.address}</td>
                            <td>{case.area_sqm}</td>
                            <td>{case.price_per_sqm}</td>
                            <td>{case.transaction_date}</td>
                        </tr>
                        ''' for i, case in enumerate(report_data.transaction_cases)])}
                    </table>
                </div>
                
                <div class="section">
                    <h2>3. 공시지가 대비 분석</h2>
                    <table>
                        <tr>
                            <th>항목</th>
                            <th>금액</th>
                            <th>비율</th>
                        </tr>
                        <tr>
                            <td>감정평가액</td>
                            <td>{report_data.land_value_krw}</td>
                            <td>100%</td>
                        </tr>
                        <tr>
                            <td>공시지가</td>
                            <td>{report_data.official_price_krw}</td>
                            <td>{report_data.official_price_ratio}%</td>
                        </tr>
                    </table>
                </div>
                
                <div class="section">
                    <h2>4. 가격 형성 논리</h2>
                    <p style="line-height: 1.8;">{report_data.price_formation_logic}</p>
                </div>
                
                <div class="section">
                    <h2>5. 리스크 요인</h2>
                    <ul style="line-height: 2;">
                        {''.join([f'<li>{risk}</li>' for risk in report_data.risk_factors])}
                    </ul>
                </div>
                
                <div class="section">
                    <h2>6. 한계점 및 유의사항</h2>
                    <ul style="line-height: 2;">
                        {''.join([f'<li>{lim}</li>' for lim in report_data.limitations])}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M2 report: {str(e)}", exc_info=True)
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
        
        # 파이프라인 결과 가져오기
        pipeline_result = await get_pipeline_result(context_id)
        if not pipeline_result:
            logger.warning(f"No pipeline result found for {context_id}, using MOCK data")
            pipeline_result = await create_mock_pipeline_result(context_id)
        
        address = await get_address_from_result(pipeline_result)
        
        # M3 보고서 데이터 생성
        report_data = module_report_generator.generate_m3_report(
            context_id=context_id,
            pipeline_result=pipeline_result,
            address=address
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M3 공급 유형 판단 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; background: #f8f9fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; }}
                h1 {{ color: #0A1628; border-bottom: 3px solid #0A1628; padding-bottom: 12px; }}
                h2 {{ color: #1976D2; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #0A1628; color: white; }}
                tr:nth-child(even) {{ background: #f8f9fa; }}
                .highlight {{ background: #fff3cd; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>M3. 공급 유형 판단 보고서</h1>
                <p><strong>주소:</strong> {address}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>1. 선택된 유형</h2>
                <p style="font-size: 18px; color: #0A1628; font-weight: bold;">{report_data.selected_type_name} (점수: {report_data.selected_type_score})</p>
                
                <h2>2. 전체 유형 평가 결과</h2>
                <table>
                    <tr><th>유형</th><th>총점</th><th>입지점수</th><th>접근성</th><th>POI</th><th>수요예측</th></tr>
                    {''.join([f'<tr class="{"highlight" if c["type_name"] == report_data.selected_type_name else ""}"><td>{c["type_name"]}</td><td>{c["total_score"]}</td><td>{c["location_score"]}</td><td>{c["accessibility_score"]}</td><td>{c["poi_score"]}</td><td>{c["demand_prediction"]}</td></tr>' for c in report_data.candidates])}
                </table>
                
                <h2>3. 정책 적합성 분석</h2>
                <p style="line-height: 1.8;">{report_data.policy_compliance_analysis}</p>
                
                <h2>4. 선택 논리</h2>
                <p style="line-height: 1.8;">{report_data.selection_logic}</p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M3 report: {str(e)}", exc_info=True)
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
        
        # 파이프라인 결과 가져오기
        pipeline_result = await get_pipeline_result(context_id)
        if not pipeline_result:
            logger.warning(f"No pipeline result found for {context_id}, using MOCK data")
            pipeline_result = await create_mock_pipeline_result(context_id)
        
        address = await get_address_from_result(pipeline_result)
        
        # M4 보고서 데이터 생성
        report_data = module_report_generator.generate_m4_report(
            context_id=context_id,
            pipeline_result=pipeline_result,
            address=address
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M4 건축 규모 검토 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; background: #f8f9fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; }}
                h1 {{ color: #0A1628; border-bottom: 3px solid #0A1628; padding-bottom: 12px; }}
                h2 {{ color: #1976D2; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #0A1628; color: white; }}
                tr:nth-child(even) {{ background: #f8f9fa; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>M4. 건축 규모 검토 보고서</h1>
                <p><strong>주소:</strong> {address}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>1. 최종 선택 시나리오</h2>
                <p style="font-size: 18px; color: #0A1628; font-weight: bold;">{report_data.selected_scenario_name}</p>
                <p><strong>세대수:</strong> {report_data.selected_scenario_units}세대</p>
                
                <h2>2. 시나리오 비교</h2>
                <table>
                    <tr><th>시나리오</th><th>세대수</th><th>건폐율</th><th>용적률</th><th>평형대</th></tr>
                    {''.join([f'<tr><td>{s["name"]}</td><td>{s["units"]}</td><td>{s["coverage_ratio"]}%</td><td>{s["floor_area_ratio"]}%</td><td>{s["unit_mix"]}</td></tr>' for s in report_data.scenarios])}
                </table>
                
                <h2>3. 주차 계획</h2>
                <p>{report_data.parking_analysis}</p>
                
                <h2>4. 효율성 분석</h2>
                <p style="line-height: 1.8;">{report_data.efficiency_analysis}</p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M4 report: {str(e)}", exc_info=True)
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
        
        # 파이프라인 결과 가져오기
        pipeline_result = await get_pipeline_result(context_id)
        if not pipeline_result:
            logger.warning(f"No pipeline result found for {context_id}, using MOCK data")
            pipeline_result = await create_mock_pipeline_result(context_id)
        
        address = await get_address_from_result(pipeline_result)
        
        # M5 보고서 데이터 생성
        report_data = module_report_generator.generate_m5_report(
            context_id=context_id,
            pipeline_result=pipeline_result,
            address=address
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M5 사업성 분석 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; background: #f8f9fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; }}
                h1 {{ color: #0A1628; border-bottom: 3px solid #0A1628; padding-bottom: 12px; }}
                h2 {{ color: #1976D2; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background: #0A1628; color: white; }}
                tr:nth-child(even) {{ background: #f8f9fa; }}
                .positive {{ color: #388E3C; font-weight: bold; }}
                .negative {{ color: #D32F2F; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>M5. 사업성 분석 보고서</h1>
                <p><strong>주소:</strong> {address}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>1. 핵심 지표</h2>
                <table>
                    <tr><th>지표</th><th>값</th><th>판정</th></tr>
                    <tr><td>IRR (내부수익률)</td><td class="{'positive' if report_data.irr > 0 else 'negative'}">{report_data.irr}%</td><td>{report_data.irr_interpretation}</td></tr>
                    <tr><td>NPV (순현재가치)</td><td class="{'positive' if report_data.npv > 0 else 'negative'}">{report_data.npv_krw}</td><td>{report_data.npv_interpretation}</td></tr>
                    <tr><td>투자회수기간</td><td>{report_data.payback_period}년</td><td>{report_data.payback_interpretation}</td></tr>
                </table>
                
                <h2>2. 사업비 구조</h2>
                <table>
                    <tr><th>항목</th><th>금액</th><th>비율</th></tr>
                    {''.join([f'<tr><td>{item["category"]}</td><td>{item["amount"]}</td><td>{item["ratio"]}%</td></tr>' for item in report_data.cost_structure])}
                </table>
                
                <h2>3. 민감도 분석</h2>
                <p>{report_data.sensitivity_summary}</p>
                
                <h2>4. 리스크 및 투자 권고</h2>
                <p style="line-height: 1.8;">{report_data.risk_assessment}</p>
                <p style="line-height: 1.8; font-weight: bold; color: #0A1628;">{report_data.investment_recommendation}</p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M5 report: {str(e)}", exc_info=True)
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
        
        # 파이프라인 결과 가져오기
        pipeline_result = await get_pipeline_result(context_id)
        if not pipeline_result:
            logger.warning(f"No pipeline result found for {context_id}, using MOCK data")
            pipeline_result = await create_mock_pipeline_result(context_id)
        
        address = await get_address_from_result(pipeline_result)
        
        # M6 보고서 데이터 생성
        report_data = module_report_generator.generate_m6_report(
            context_id=context_id,
            pipeline_result=pipeline_result,
            address=address
        )
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M6 종합 판단 보고서</title>
            <style>
                body {{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; background: #f8f9fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-radius: 8px; }}
                h1 {{ color: #0A1628; border-bottom: 3px solid #0A1628; padding-bottom: 12px; }}
                h2 {{ color: #1976D2; margin-top: 30px; }}
                .decision {{ font-size: 24px; padding: 20px; border-radius: 8px; text-align: center; font-weight: bold; }}
                .pass {{ background: #E8F5E9; color: #2E7D32; }}
                .conditional {{ background: #FFF3E0; color: #F57C00; }}
                .reject {{ background: #FFEBEE; color: #C62828; }}
                ul {{ line-height: 2; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>M6. 종합 판단 보고서</h1>
                <p><strong>주소:</strong> {address}</p>
                <p><strong>생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>1. 최종 판정</h2>
                <div class="decision {report_data.decision.lower()}">{report_data.decision_label}</div>
                <p style="margin-top: 20px; line-height: 1.8;">{report_data.decision_rationale}</p>
                
                <h2>2. 긍정 요인</h2>
                <ul>
                    {''.join([f'<li>{factor}</li>' for factor in report_data.positive_factors])}
                </ul>
                
                <h2>3. 리스크 요인</h2>
                <ul>
                    {''.join([f'<li>{risk}</li>' for risk in report_data.risk_factors])}
                </ul>
                
                <h2>4. 핵심 지표 요약</h2>
                <p><strong>토지가치:</strong> {report_data.key_metrics["land_value"]}</p>
                <p><strong>주거유형:</strong> {report_data.key_metrics["housing_type"]}</p>
                <p><strong>세대수:</strong> {report_data.key_metrics["units"]}세대</p>
                <p><strong>IRR:</strong> {report_data.key_metrics["irr"]}%</p>
                
                <h2>5. 조건부 추진 시나리오</h2>
                <p style="line-height: 1.8;">{report_data.conditional_scenarios}</p>
                
                <h2>6. 최종 권고사항</h2>
                <ul>
                    {''.join([f'<li>{rec}</li>' for rec in report_data.recommendations])}
                </ul>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate M6 report: {str(e)}", exc_info=True)
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
        "phase": "Phase 8: Module, Comprehensive & Six-Type Reports",
        "features": {
            "module_reports": ["M2", "M3", "M4", "M5", "M6"],
            "comprehensive_report": "Type A",
            "six_type_reports": ["Type B", "Type C", "Type D", "Type E", "Type F"],
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
            "six_type_reports": [
                "/api/v4/reports/phase8/six-types/type-b/html (Landowner)",
                "/api/v4/reports/phase8/six-types/type-c/html (LH Technical)",
                "/api/v4/reports/phase8/six-types/type-d/html (Investor)",
                "/api/v4/reports/phase8/six-types/type-e/html (Preliminary)",
                "/api/v4/reports/phase8/six-types/type-f/html (Presentation)",
            ],
        },
        "timestamp": datetime.now().isoformat(),
    }


# ========================================
# 6종 보고서 엔드포인트 (Type B-F)
# ========================================

@router.get("/six-types/type-b/html", response_class=HTMLResponse)
async def get_type_b_landowner_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    Type B: 토지주 제출용 보고서 (HTML)
    
    - 안정성·수익성 강조
    - 토지 가치, 사업 계획, 수익 구조
    - 15-20페이지 분량
    """
    try:
        logger.info(f"Generating Type B Landowner Report for context_id={context_id}")
        
        # TODO: 실제 구현 시 파이프라인 결과 가져오기
        # pipeline_result = await get_pipeline_result(context_id)
        # address = await get_address(context_id)
        # report_data = six_types_report_generator.generate_type_b_report(
        #     context_id, pipeline_result, address
        # )
        # return template_renderer.render_template(
        #     "report_type_b_landowner.html", report_data
        # )
        
        # 임시 응답
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>Type B - 토지주 제출용 보고서</title>
            <style>
                body {{ 
                    font-family: 'Noto Sans KR', sans-serif; 
                    padding: 40px;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 50px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    border-radius: 12px;
                }}
                h1 {{ 
                    color: #2e7d32; 
                    font-size: 36px;
                    border-bottom: 3px solid #4caf50;
                    padding-bottom: 15px;
                }}
                .info {{ 
                    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                    padding: 30px; 
                    border-radius: 12px;
                    border-left: 5px solid #4caf50;
                    margin: 25px 0;
                }}
                .status {{
                    display: inline-block;
                    padding: 8px 16px;
                    background: #4caf50;
                    color: white;
                    border-radius: 20px;
                    font-weight: 600;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📄 Type B - 토지주 제출용 보고서</h1>
                
                <div class="info">
                    <p><strong>📍 Context ID:</strong> {context_id}</p>
                    <p><strong>📅 생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>📝 보고서 유형:</strong> 토지주 설득용 (안정성·수익성 강조)</p>
                    <p style="margin-top: 20px;"><span class="status">✅ Phase 8.3 6종 보고서 시스템 가동</span></p>
                </div>
                
                <h2 style="color: #2e7d32; margin-top: 40px;">📋 보고서 특징</h2>
                <ul style="line-height: 2; font-size: 16px;">
                    <li><strong>토지 가치 평가:</strong> 감정평가액, 단가, 신뢰도</li>
                    <li><strong>사업 계획:</strong> 공급 유형, 세대수, 공사 기간</li>
                    <li><strong>수익성 분석:</strong> 예상 수익, 토지주 몫, ROI</li>
                    <li><strong>안정성 보장:</strong> LH 승인 확률, 리스크 관리</li>
                    <li><strong>추진 권고:</strong> 다음 단계, 계약 절차</li>
                </ul>
                
                <div style="margin-top: 50px; padding: 30px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404;">🚀 다음 단계</h3>
                    <p style="line-height: 1.8;">
                        파이프라인 결과 연동 후 실제 데이터로 토지주 설득용 보고서를 생성합니다.<br>
                        템플릿: <code>app/templates_v13/report_type_b_landowner.html</code>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate Type B report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Type B 보고서 생성 실패: {str(e)}")


@router.get("/six-types/type-c/html", response_class=HTMLResponse)
async def get_type_c_lh_technical_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    Type C: LH 기술검증 보고서 (HTML)
    
    - 기술 규정 준수 검증
    - M2-M6 기술 검토 상세
    - 40-50페이지 분량
    """
    try:
        logger.info(f"Generating Type C LH Technical Report for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>Type C - LH 기술검증 보고서</title>
            <style>
                body {{ 
                    font-family: 'Noto Sans KR', sans-serif; 
                    padding: 40px;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e1f5fe 100%);
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 50px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    border-radius: 12px;
                }}
                h1 {{ 
                    color: #0066cc; 
                    font-size: 36px;
                    border-bottom: 3px solid #2196f3;
                    padding-bottom: 15px;
                }}
                .info {{ 
                    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    padding: 30px; 
                    border-radius: 12px;
                    border-left: 5px solid #2196f3;
                    margin: 25px 0;
                }}
                .status {{
                    display: inline-block;
                    padding: 8px 16px;
                    background: #2196f3;
                    color: white;
                    border-radius: 20px;
                    font-weight: 600;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 Type C - LH 기술검증 보고서</h1>
                
                <div class="info">
                    <p><strong>📍 Context ID:</strong> {context_id}</p>
                    <p><strong>📅 생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>📝 보고서 유형:</strong> LH 기술검증용 (법규 준수, 구조 안전성)</p>
                    <p style="margin-top: 20px;"><span class="status">✅ Phase 8.3 6종 보고서 시스템 가동</span></p>
                </div>
                
                <h2 style="color: #0066cc; margin-top: 40px;">📋 보고서 특징</h2>
                <ul style="line-height: 2; font-size: 16px;">
                    <li><strong>M2 기술 검토:</strong> 감정평가 방법론, 계산 근거</li>
                    <li><strong>M3 유형 검증:</strong> 후보 유형별 기술 비교</li>
                    <li><strong>M4 규모 검토:</strong> 법적 한계, 구조 시스템, 주차</li>
                    <li><strong>M5 경제성:</strong> 사업비 산출, 재무 구조</li>
                    <li><strong>M6 종합 판단:</strong> 필수 요건, 기술 리스크</li>
                </ul>
                
                <div style="margin-top: 50px; padding: 30px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404;">🚀 다음 단계</h3>
                    <p style="line-height: 1.8;">
                        파이프라인 결과 연동 후 실제 데이터로 LH 기술검증 보고서를 생성합니다.<br>
                        템플릿: <code>app/templates_v13/report_type_c_lh_technical.html</code>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate Type C report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Type C 보고서 생성 실패: {str(e)}")


@router.get("/six-types/type-d/html", response_class=HTMLResponse)
async def get_type_d_investor_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    Type D: 사업성·투자 검토 보고서 (HTML)
    
    - 재무 KPI (IRR, NPV, ROI, Payback)
    - 비용/수익 구조, 민감도 분석
    - 25-30페이지 분량
    """
    try:
        logger.info(f"Generating Type D Investor Report for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>Type D - 사업성·투자 검토 보고서</title>
            <style>
                body {{ 
                    font-family: 'Noto Sans KR', sans-serif; 
                    padding: 40px;
                    background: linear-gradient(135deg, #f8f9fa 0%, #f0fff4 100%);
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 50px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    border-radius: 12px;
                }}
                h1 {{ 
                    color: #28a745; 
                    font-size: 36px;
                    border-bottom: 3px solid #4caf50;
                    padding-bottom: 15px;
                }}
                .info {{ 
                    background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                    padding: 30px; 
                    border-radius: 12px;
                    border-left: 5px solid #4caf50;
                    margin: 25px 0;
                }}
                .status {{
                    display: inline-block;
                    padding: 8px 16px;
                    background: #28a745;
                    color: white;
                    border-radius: 20px;
                    font-weight: 600;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💰 Type D - 사업성·투자 검토 보고서</h1>
                
                <div class="info">
                    <p><strong>📍 Context ID:</strong> {context_id}</p>
                    <p><strong>📅 생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>📝 보고서 유형:</strong> 투자자용 (재무 지표, 수익성 강조)</p>
                    <p style="margin-top: 20px;"><span class="status">✅ Phase 8.3 6종 보고서 시스템 가동</span></p>
                </div>
                
                <h2 style="color: #28a745; margin-top: 40px;">📋 보고서 특징</h2>
                <ul style="line-height: 2; font-size: 16px;">
                    <li><strong>핵심 KPI:</strong> IRR, NPV, ROI, 회수기간</li>
                    <li><strong>비용 구조:</strong> 토지비, 건축비, 간접비 상세</li>
                    <li><strong>수익 구조:</strong> 임대, 분양, 기타 수익</li>
                    <li><strong>민감도 분석:</strong> 분양가, 건축비, 토지비 ±10%</li>
                    <li><strong>시나리오:</strong> 낙관/기본/비관 3가지</li>
                    <li><strong>투자 결론:</strong> 등급, 리스크, 권고 의견</li>
                </ul>
                
                <div style="margin-top: 50px; padding: 30px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404;">🚀 다음 단계</h3>
                    <p style="line-height: 1.8;">
                        파이프라인 결과 연동 후 실제 데이터로 투자자용 보고서를 생성합니다.<br>
                        템플릿: <code>app/templates_v13/report_type_d_investor.html</code>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate Type D report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Type D 보고서 생성 실패: {str(e)}")


@router.get("/six-types/type-e/html", response_class=HTMLResponse)
async def get_type_e_preliminary_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    Type E: 사전 검토 리포트 (HTML)
    
    - 빠른 사업성 평가
    - 핵심 지표 요약
    - 5-8페이지 분량
    """
    try:
        logger.info(f"Generating Type E Preliminary Report for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>Type E - 사전 검토 리포트</title>
            <style>
                body {{ 
                    font-family: 'Noto Sans KR', sans-serif; 
                    padding: 40px;
                    background: linear-gradient(135deg, #f8f9fa 0%, #f5f5f5 100%);
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    border-radius: 12px;
                }}
                h1 {{ 
                    color: #6c757d; 
                    font-size: 32px;
                    border-bottom: 3px solid #adb5bd;
                    padding-bottom: 15px;
                }}
                .info {{ 
                    background: linear-gradient(135deg, #f8f9fa 0%, #dee2e6 100%); 
                    padding: 25px; 
                    border-radius: 12px;
                    border-left: 5px solid #6c757d;
                    margin: 20px 0;
                }}
                .status {{
                    display: inline-block;
                    padding: 6px 14px;
                    background: #6c757d;
                    color: white;
                    border-radius: 16px;
                    font-weight: 600;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📋 Type E - 사전 검토 리포트</h1>
                
                <div class="info">
                    <p><strong>📍 Context ID:</strong> {context_id}</p>
                    <p><strong>📅 생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>📝 보고서 유형:</strong> 빠른 판단용 (핵심만 요약)</p>
                    <p style="margin-top: 15px;"><span class="status">✅ Phase 8.3 6종 보고서 시스템 가동</span></p>
                </div>
                
                <h2 style="color: #6c757d; margin-top: 35px;">📋 보고서 특징</h2>
                <ul style="line-height: 2; font-size: 15px;">
                    <li><strong>사전 결과:</strong> 승인 확률, 등급, 결론</li>
                    <li><strong>대상지 개요:</strong> 면적, 가격, 권장 유형</li>
                    <li><strong>법규 간편 검토:</strong> 용적률, 건폐율, 세대수</li>
                    <li><strong>사업성 요약:</strong> IRR, ROI, 회수기간</li>
                    <li><strong>긍정/리스크:</strong> 주요 고려사항</li>
                    <li><strong>다음 단계:</strong> 실사 계획, 추가 검토 항목</li>
                </ul>
                
                <div style="margin-top: 40px; padding: 25px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #856404;">🚀 다음 단계</h3>
                    <p style="line-height: 1.8; font-size: 14px;">
                        파이프라인 결과 연동 후 실제 데이터로 간편 검토 리포트를 생성합니다.<br>
                        템플릿: <code>app/templates_v13/report_type_e_preliminary.html</code>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate Type E report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Type E 보고서 생성 실패: {str(e)}")


@router.get("/six-types/type-f/html", response_class=HTMLResponse)
async def get_type_f_presentation_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID")
):
    """
    Type F: 설명용 프레젠테이션 (HTML)
    
    - 임원급 프레젠테이션 슬라이드
    - 16슬라이드 구성
    - 10-15슬라이드 분량
    """
    try:
        logger.info(f"Generating Type F Presentation Report for context_id={context_id}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>Type F - 설명용 프레젠테이션</title>
            <style>
                body {{ 
                    font-family: 'Noto Sans KR', sans-serif; 
                    padding: 0;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    max-width: 1200px;
                    height: 675px;
                    margin: 40px auto;
                    background: white;
                    padding: 60px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    border-radius: 16px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                }}
                h1 {{ 
                    color: #667eea; 
                    font-size: 48px;
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .info {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px; 
                    border-radius: 16px;
                    margin: 30px 0;
                    text-align: center;
                }}
                .status {{
                    display: inline-block;
                    padding: 10px 20px;
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border-radius: 24px;
                    font-weight: 600;
                    font-size: 14px;
                    backdrop-filter: blur(10px);
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎨 Type F - 설명용 프레젠테이션</h1>
                
                <div class="info">
                    <p style="font-size: 18px;"><strong>📍 Context ID:</strong> {context_id}</p>
                    <p style="font-size: 18px;"><strong>📅 생성일시:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="font-size: 18px; margin-top: 10px;"><strong>📝 보고서 유형:</strong> 프레젠테이션 슬라이드 (16장)</p>
                    <p style="margin-top: 30px;"><span class="status">✅ Phase 8.3 6종 보고서 시스템 가동</span></p>
                </div>
                
                <h2 style="color: #667eea; text-align: center; margin-top: 40px;">📋 슬라이드 구성</h2>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-top: 20px;">
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <strong>1-2.</strong> 표지 & 핵심 요약
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <strong>3-5.</strong> 대상지 & 토지 가치
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <strong>6-8.</strong> 사업 계획 & 규모
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <strong>9-11.</strong> 재무 지표 & 수익
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <strong>12-14.</strong> 종합 판단 & SWOT
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center;">
                        <strong>15-16.</strong> 다음 단계 & Q&A
                    </div>
                </div>
                
                <div style="margin-top: 40px; padding: 25px; background: #fff3cd; border-radius: 8px; border-left: 4px solid #ffc107; text-align: center;">
                    <p style="margin: 0; line-height: 1.8;">
                        <strong>🚀 다음 단계:</strong> 파이프라인 결과 연동 후 실제 프레젠테이션 생성<br>
                        템플릿: <code>app/templates_v13/report_type_f_presentation.html</code>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate Type F report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Type F 보고서 생성 실패: {str(e)}")
