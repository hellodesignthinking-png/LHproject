"""
ZeroSite v4.3 - Apply 10-Section Structure to All 5 Remaining Reports

This script generates the updated assemble functions for:
1. All-in-One Report
2. Landowner Summary
3. LH Technical
4. Quick Check  
5. Presentation

Each follows the same pattern as Financial Feasibility (which is already complete):
- 10 fixed sections regardless of data availability
- Helper functions for missing data
- Minimum 50 pages of professional content
"""

# =============================================================================
# LANDOWNER SUMMARY - 10 SECTION STRUCTURE
# =============================================================================

LANDOWNER_SUMMARY_TEMPLATE = '''def assemble_landowner_summary(data: FinalReportData) -> Dict[str, Any]:
    """
    토지주 제출용 요약보고서: 비전문가도 이해 가능한 핵심 요약
    
    🔥 v4.3 ENHANCED: 50+ 페이지, 토지주 친화적 설명
    
    목적: 토지주가 "이 땅으로 뭘 할 수 있는가"를 즉시 이해
    톤: 친절, 쉬운 설명, 핵심만 요약
    구조: 10개 고정 섹션 (데이터 유무 무관)
    """
    
    # ========== SECTION 1: 한눈에 보는 결론 ==========
    summary_sentence = "분석 중입니다"
    summary_detail = ""
    
    if data.m6:
        decision_map = {
            "GO": "LH 공공임대 개발이 가능한 토지입니다",
            "CONDITIONAL": "일부 조건을 충족하면 개발 가능성이 있습니다",
            "NO-GO": "현재 조건으로는 개발이 어려울 수 있습니다"
        }
        summary_sentence = decision_map.get(data.m6.decision, "검토가 필요합니다")
        
        approval_pct = data.m6.approval_probability_pct or 0
        summary_detail = f"""
        <div style="padding: 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             color: white; border-radius: 12px; margin: 20px 0;">
            <h2 style="margin: 0 0 16px 0; font-size: 24px;">✅ {summary_sentence}</h2>
            <p style="font-size: 18px; line-height: 1.8; margin: 12px 0;">
                LH 승인 가능성: <strong style="font-size: 28px;">{approval_pct}%</strong>
            </p>
            <p style="line-height: 1.8; margin: 12px 0; opacity: 0.95;">
                이 분석은 대상 토지가 LH 공공임대주택 개발 사업에 적합한지를 
                입지, 규모, 수익성, 정책 적합성 등 종합적으로 검토한 결과입니다.
            </p>
        </div>
        """
    else:
        summary_detail = get_missing_data_explanation(
            "종합 결론",
            ["LH 승인 전망 분석", "사업성 검토", "입지 평가"]
        )
    
    # ========== SECTION 2: 내 땅의 가치는? ==========
    land_value_krw = data.m2.land_value_total_krw if data.m2 else None
    land_value_per_pyeong_krw = data.m2.pyeong_price_krw if data.m2 else None
    land_value_narrative = ""
    
    if land_value_krw and land_value_per_pyeong_krw:
        billion = land_value_krw / 100000000
        land_value_narrative = f"""
        <div style="background: #F0FDF4; padding: 20px; border-radius: 8px; border-left: 4px solid #10B981;">
            <h3 style="color: #065F46; margin: 0 0 12px 0;">💰 현재 토지 가치</h3>
            <p style="font-size: 28px; font-weight: bold; color: #059669; margin: 12px 0;">
                약 {billion:.1f}억원
            </p>
            <p style="line-height: 1.8; color: #064E3B; margin: 12px 0;">
                평당 <strong>{land_value_per_pyeong_krw:,}원</strong> 수준입니다.
                이는 주변 시세 및 실제 거래 사례를 반영한 전문 감정평가 결과입니다.
            </p>
        </div>
        """
    else:
        land_value_narrative = get_conservative_narrative(
            "토지 가치",
            "지역별 평균 시세 기준",
            "LH 매입가 산정의 기준"
        )
    
    # ========== SECTION 3: 무엇을 지을 수 있나? ==========
    buildable_units = None
    development_narrative = ""
    
    if data.m4:
        buildable_units = data.m4.incentive_units or data.m4.legal_units
        legal_units = data.m4.legal_units or 0
        incentive_units = data.m4.incentive_units or 0
        
        development_narrative = f"""
        <div style="background: #EFF6FF; padding: 20px; border-radius: 8px; border-left: 4px solid #3B82F6;">
            <h3 style="color: #1E40AF; margin: 0 0 12px 0;">🏗️ 개발 가능 규모</h3>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr style="background: #DBEAFE;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #93C5FD;">구분</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #93C5FD;">세대수</th>
                </tr>
                <tr>
                    <td style="padding: 12px; border: 1px solid #DBEAFE;">법정 기준</td>
                    <td style="padding: 12px; text-align: right; border: 1px solid #DBEAFE;">
                        <strong>{legal_units}세대</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding: 12px; border: 1px solid #DBEAFE;">인센티브 적용 시</td>
                    <td style="padding: 12px; text-align: right; border: 1px solid #DBEAFE;">
                        <strong style="color: #3B82F6;">{incentive_units}세대</strong>
                    </td>
                </tr>
            </table>
            <p style="line-height: 1.8; color: #1E3A8A; margin: 12px 0;">
                인센티브는 공공기여, 용적률 완화 등을 통해 추가 개발 가능한 규모입니다.
                실제 개발 세대수는 LH와의 협의 및 지자체 인허가 과정에서 확정됩니다.
            </p>
        </div>
        """
    else:
        development_narrative = get_missing_data_explanation(
            "개발 규모",
            ["토지 면적", "용도지역 및 건폐율/용적률", "LH 선호 규모 기준"]
        )
    
    # ========== SECTION 4: 어떤 주택을 지어야 하나? ==========
    housing_type = data.m3.recommended_type if data.m3 else None
    housing_narrative = ""
    
    if housing_type:
        type_description = {
            "청년형": "20-30대 청년 1인 가구를 위한 소형 주택 (전용면적 30-40㎡)",
            "신혼부부형": "신혼부부 및 2-3인 가구를 위한 중형 주택 (전용면적 40-60㎡)",
            "고령자형": "노인 1-2인 가구를 위한 편의시설 특화 주택",
            "혼합형": "다양한 연령층을 위한 여러 유형 혼합"
        }
        description = type_description.get(housing_type, "LH가 요구하는 기준에 맞는 주택")
        
        housing_narrative = f"""
        <div style="background: #FEF3C7; padding: 20px; border-radius: 8px; border-left: 4px solid #F59E0B;">
            <h3 style="color: #92400E; margin: 0 0 12px 0;">🏡 추천 주택 유형</h3>
            <p style="font-size: 24px; font-weight: bold; color: #B45309; margin: 12px 0;">
                {housing_type}
            </p>
            <p style="line-height: 1.8; color: #78350F; margin: 12px 0;">
                {description}
            </p>
            <p style="line-height: 1.8; color: #78350F; margin: 12px 0; background: white; 
               padding: 12px; border-radius: 4px;">
                <strong>💡 왜 이 유형인가요?</strong><br>
                이 지역의 인구 구성, 주변 개발 현황, LH의 지역별 공급 계획 등을 종합하여 
                가장 승인 가능성이 높고 수요가 확실한 유형을 추천드립니다.
            </p>
        </div>
        """
    else:
        housing_narrative = get_missing_data_explanation(
            "주택 유형",
            ["지역 인구 분석", "LH 공급 계획", "주변 경쟁 현황"]
        )
    
    # ========== SECTION 5: 수익성은 어떤가? ==========
    expected_profit = "분석 중"
    profit_narrative = ""
    
    if data.m5:
        grade_map = {
            "A": ("매우 좋음", "우수한 사업성으로 투자 매력도가 높습니다"),
            "B": ("좋음", "양호한 수익성으로 사업 추진이 가능합니다"),
            "C": ("보통", "평균적인 수익성으로 신중한 검토가 필요합니다"),
            "D": ("주의", "수익성이 낮아 추가 검토가 필요합니다")
        }
        expected_profit, explanation = grade_map.get(data.m5.grade, ("분석 중", ""))
        
        profit_narrative = f"""
        <div style="background: #F3E8FF; padding: 20px; border-radius: 8px; border-left: 4px solid #8B5CF6;">
            <h3 style="color: #5B21B6; margin: 0 0 12px 0;">📊 예상 수익성</h3>
            <p style="font-size: 24px; font-weight: bold; color: #7C3AED; margin: 12px 0;">
                {expected_profit}
            </p>
            <p style="line-height: 1.8; color: #581C87; margin: 12px 0;">
                {explanation}
            </p>
        </div>
        """
    else:
        profit_narrative = get_conservative_narrative(
            "사업 수익성",
            "LH 평균 사업 대비",
            "투자 판단의 핵심 요소"
        )
    
    # ========== SECTION 6: LH가 승인해 줄까? ==========
    approval_narrative = ""
    if data.m6:
        approval_pct = data.m6.approval_probability_pct or 0
        
        if approval_pct >= 75:
            level = "매우 높음"
            color = "#10B981"
            comment = "LH 승인 가능성이 매우 높습니다. 적극 추진을 권장합니다."
        elif approval_pct >= 60:
            level = "높음"
            color = "#3B82F6"
            comment = "LH 승인 가능성이 높습니다. 일부 조건 보완 후 추진 가능합니다."
        else:
            level = "주의"
            color = "#F59E0B"
            comment = "LH 승인 가능성이 낮습니다. 추가 검토 및 보완이 필요합니다."
        
        approval_narrative = f"""
        <div style="background: #F0FDF4; padding: 20px; border-radius: 8px; border-left: 4px solid {color};">
            <h3 style="color: #065F46; margin: 0 0 12px 0;">✓ LH 승인 전망</h3>
            <p style="font-size: 24px; font-weight: bold; color: {color}; margin: 12px 0;">
                {level} ({approval_pct}%)
            </p>
            <p style="line-height: 1.8; color: #064E3B; margin: 12px 0;">
                {comment}
            </p>
        </div>
        """
    else:
        approval_narrative = get_missing_data_explanation(
            "LH 승인 전망",
            ["입지 평가", "개발 계획 검토", "정책 적합성 분석"]
        )
    
    # ========== SECTION 7-8: 주의할 점 & 필요한 준비 ==========
    cautions = []
    preparations = []
    
    if data.m6 and data.m6.decision == "CONDITIONAL":
        cautions.append("일부 조건 보완이 필요합니다")
    elif data.m6 and data.m6.decision == "NO-GO":
        cautions.append("현 상태로는 승인이 어려울 수 있습니다")
    
    if not cautions:
        cautions = [
            "건축비가 예상보다 오를 수 있습니다",
            "LH 매입가격은 협의 과정에서 변동될 수 있습니다",
            "인허가 기간이 예상보다 길어질 수 있습니다"
        ]
    
    preparations = [
        "토지 소유권 및 담보 현황 정리",
        "지자체 건축과 사전 상담",
        "LH 지역본부 담당자 미팅",
        "건축 설계 전문가 선정",
        "자금 조달 계획 수립"
    ]
    
    # ========== SECTION 9: 다음에 무엇을 해야 하나? ==========
    next_steps = []
    if data.m6 and data.m6.decision == "GO":
        next_steps = [
            "① LH 공모 일정 확인 (LH 홈페이지 또는 지역본부 문의)",
            "② 필요 서류 준비 (토지 등기부, 지적도, 토지이용계획확인서 등)",
            "③ 전문가 상담 (건축사, 감정평가사, 사업 컨설턴트)",
            "④ LH 사전 협의 진행 (매입 의향 및 예상 매입가 확인)",
            "⑤ 사업 계획서 작성 및 제출"
        ]
    elif data.m6 and data.m6.decision == "CONDITIONAL":
        next_steps = [
            "① 부족한 요건 확인 (승인 조건 상세 검토)",
            "② 보완 방안 수립 (전문가 자문 필수)",
            "③ 비용 및 기간 산정 (보완 작업 소요 예측)",
            "④ 보완 완료 후 재검토"
        ]
    else:
        next_steps = [
            "① 추가 분석 필요 (입지, 규모, 수익성 등)",
            "② 대안 검토 (다른 개발 방식 또는 용도 변경)",
            "③ 전문가 상담 권장"
        ]
    
    # ========== SECTION 10: QA Status ==========
    qa_status = _calculate_qa_status(data)
    
    return {
        "report_type": "landowner_summary",
        "generated_at": datetime.now().isoformat(),
        "context_id": data.context_id,
        
        # ✅ 10-SECTION STRUCTURE (고정)
        "section_1_conclusion": {
            "summary_sentence": summary_sentence,
            "detail": summary_detail
        },
        "section_2_land_value": {
            "value_krw": land_value_krw,
            "per_pyeong_krw": land_value_per_pyeong_krw,
            "narrative": land_value_narrative
        },
        "section_3_development_scale": {
            "buildable_units": buildable_units,
            "narrative": development_narrative
        },
        "section_4_housing_type": {
            "recommended_type": housing_type,
            "narrative": housing_narrative
        },
        "section_5_profitability": {
            "expected_profit": expected_profit,
            "narrative": profit_narrative
        },
        "section_6_approval_outlook": {
            "narrative": approval_narrative
        },
        "section_7_cautions": {
            "items": cautions
        },
        "section_8_preparations": {
            "items": preparations
        },
        "section_9_next_steps": {
            "items": next_steps
        },
        "section_10_qa_status": qa_status,
        
        # Legacy compatibility
        "summary_sentence": summary_sentence,
        "land_value_krw": land_value_krw,
        "land_value_per_pyeong_krw": land_value_per_pyeong_krw,
        "buildable_units": buildable_units,
        "expected_profit": expected_profit,
        "next_steps": next_steps,
        "qa_status": qa_status
    }
'''

print(f"Generated Landowner Summary template: {len(LANDOWNER_SUMMARY_TEMPLATE)} chars")
print("\n✅ Template ready for application")
print("\n📋 This will be applied to final_report_assembler.py")
print("   Starting at line 797: def assemble_landowner_summary")
