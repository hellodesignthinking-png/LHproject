#!/usr/bin/env python3
"""
Phase 8.4.2: M3-M6 엔드포인트에 파이프라인 결과 통합
M2 패턴을 M3, M4, M5, M6에 적용
"""

import re

# Read the current router file
with open("app/routers/phase8_reports_router.py", "r", encoding="utf-8") as f:
    content = f.read()

# M3 endpoint replacement
m3_old = r'''@router\.get\("/modules/m3/html", response_class=HTMLResponse\)
async def get_m3_report_html\(
    context_id: str = Query\(\.\.\., description="분석 컨텍스트 ID"\)
\):
    """
    M3: 공급 유형 판단 보고서 \(HTML\)
    
    - 5개 후보 유형 전체 평가
    - 정책 적합성 매트릭스
    - 최종 선택 논리
    """
    try:
        logger\.info\(f"Generating M3 report HTML for context_id=\{context_id\}"\)
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>M3 공급 유형 판단 보고서</title>
            <style>
                body \{\{ font-family: 'Noto Sans KR', sans-serif; padding: 40px; \}\}
                h1 \{\{ color: #0A1628; \}\}
                \.info \{\{ background: #e8f5e9; padding: 20px; border-radius: 8px; \}\}
            </style>
        </head>
        <body>
            <h1>M3\. 공급 유형 판단 보고서</h1>
            <div class="info">
                <p><strong>Context ID:</strong> \{context_id\}</p>
                <p><strong>생성일시:</strong> \{datetime\.now\(\)\.strftime\('%Y-%m-%d %H:%M:%S'\)\}</p>
                <p><em>Phase 8 모듈별 보고서 시스템이 정상 작동 중입니다\.</em></p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse\(content=html_content\)
        
    except Exception as e:
        logger\.error\(f"Failed to generate M3 report: \{str\(e\)\}"\)
        raise HTTPException\(status_code=500, detail=f"M3 보고서 생성 실패: \{str\(e\)\}"\)'''

m3_new = '''@router.get("/modules/m3/html", response_class=HTMLResponse)
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
        raise HTTPException(status_code=500, detail=f"M3 보고서 생성 실패: {str(e)}")'''

print("Updating M3 endpoint...")
content = re.sub(m3_old, m3_new, content, flags=re.MULTILINE | re.DOTALL)

# M4 endpoint - simpler replacement using line markers
m4_start = content.find('@router.get("/modules/m4/html"')
m4_end = content.find('\n\n@router.get("/modules/m5/html"', m4_start)

m4_new_func = '''@router.get("/modules/m4/html", response_class=HTMLResponse)
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
        raise HTTPException(status_code=500, detail=f"M4 보고서 생성 실패: {str(e)}")'''

print("Updating M4 endpoint...")
content = content[:m4_start] + m4_new_func + content[m4_end:]

# M5 endpoint
m5_start = content.find('@router.get("/modules/m5/html"')
m5_end = content.find('\n\n@router.get("/modules/m6/html"', m5_start)

m5_new_func = '''@router.get("/modules/m5/html", response_class=HTMLResponse)
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
        raise HTTPException(status_code=500, detail=f"M5 보고서 생성 실패: {str(e)}")'''

print("Updating M5 endpoint...")
content = content[:m5_start] + m5_new_func + content[m5_end:]

# M6 endpoint
m6_start = content.find('@router.get("/modules/m6/html"')
# Find the next router endpoint after M6
m6_end = content.find('\n\n# ========================================\n# 종합 최종보고서', m6_start)

m6_new_func = '''@router.get("/modules/m6/html", response_class=HTMLResponse)
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
        raise HTTPException(status_code=500, detail=f"M6 보고서 생성 실패: {str(e)}")'''

print("Updating M6 endpoint...")
content = content[:m6_start] + m6_new_func + content[m6_end:]

# Write back the updated content
with open("app/routers/phase8_reports_router.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ M3-M6 endpoints updated successfully!")
print("   - M3: Housing Type Selection Report")
print("   - M4: Capacity Review Report")
print("   - M5: Feasibility Analysis Report")
print("   - M6: Comprehensive Decision Report")
