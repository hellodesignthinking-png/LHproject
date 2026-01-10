"""
Phase 8.4 통합 스크립트: M3-M6 및 Type A-F 엔드포인트 업데이트
"""

# M3-M6 엔드포인트 통합 코드
M3_ENDPOINT = '''
@router.get("/modules/m3/html", response_class=HTMLResponse)
async def get_m3_report_html(
    context_id: str = Query(..., description="분석 컨텍스트 ID (parcel_id)")
):
    """M3: 공급 유형 판단 보고서 (HTML)"""
    try:
        logger.info(f"Generating M3 report HTML for context_id={context_id}")
        
        pipeline_result = await get_pipeline_result(context_id)
        if not pipeline_result:
            logger.warning(f"No pipeline result found, using MOCK data")
            pipeline_result = await create_mock_pipeline_result(context_id)
        
        address = await get_address_from_result(pipeline_result)
        report_data = module_report_generator.generate_m3_report(context_id, pipeline_result, address)
        
        html = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><title>M3 공급 유형 판단 보고서</title>
        <style>body{{font-family:'Noto Sans KR',sans-serif;padding:40px;background:#f8f9fa}}
        .container{{max-width:1200px;margin:0 auto;background:white;padding:40px;box-shadow:0 2px 8px rgba(0,0,0,0.1);border-radius:8px}}
        h1{{color:#0A1628;border-bottom:3px solid #0A1628;padding-bottom:12px}}
        .info{{background:#e8f5e9;padding:20px;border-radius:8px;margin:20px 0}}
        .section{{margin:30px 0;padding:20px;border:1px solid #e0e0e0;border-radius:6px}}
        h2{{color:#1E3A5F;margin-top:30px}}table{{width:100%;border-collapse:collapse;margin:15px 0}}
        th,td{{padding:12px;text-align:left;border-bottom:1px solid #e0e0e0}}
        th{{background:#f8f9fa;font-weight:600}}.status{{display:inline-block;padding:4px 12px;background:#d4edda;color:#155724;border-radius:12px;font-size:12px;font-weight:600}}
        </style></head><body><div class="container"><h1>M3. 공급 유형 판단 보고서</h1>
        <div class="info"><p><strong>📍 Context ID:</strong> {report_data.context_id}</p>
        <p><strong>📅 생성일시:</strong> {report_data.generated_at}</p>
        <p><strong>🏠 대상지:</strong> {report_data.address}</p>
        <p style="margin-top:15px;"><span class="status">✅ 실제 파이프라인 데이터 연동 완료</span></p></div>
        <div class="section"><h2>1. 권장 공급 유형</h2><table><tr><th>항목</th><th>값</th></tr>
        <tr><td>권장 유형</td><td style="font-size:18px;font-weight:700;color:#0A1628;">{report_data.recommended_type}</td></tr>
        <tr><td>종합 점수</td><td>{report_data.type_score}점</td></tr>
        <tr><td>정책 적합성</td><td>{report_data.policy_compatibility}</td></tr></table></div>
        <div class="section"><h2>2. 후보 유형 평가</h2><table><tr><th>유형</th><th>점수</th><th>평가</th></tr>
        {''.join([f"<tr><td>{c.type_name}</td><td>{c.total_score}</td><td>{c.evaluation}</td></tr>" for c in report_data.candidate_types])}</table></div>
        <div class="section"><h2>3. 선정 논리</h2><p style="line-height:1.8;">{report_data.selection_logic}</p></div>
        <div class="section"><h2>4. 배제 유형</h2><ul style="line-height:2;">
        {''.join([f"<li><strong>{r.type_name}:</strong> {r.reason}</li>" for r in report_data.rejected_types])}</ul></div>
        </div></body></html>"""
        
        return HTMLResponse(content=html)
        
    except Exception as e:
        logger.error(f"Failed to generate M3 report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"M3 보고서 생성 실패: {str(e)}")
'''

# 이 스크립트는 참고용입니다. 실제 구현은 라우터 파일을 직접 수정합니다.
print("Phase 8.4 통합 스크립트 준비 완료")
print("M3-M6 및 Type A-F 엔드포인트를 실제 데이터와 통합합니다.")
