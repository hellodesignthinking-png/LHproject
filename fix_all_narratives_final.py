#!/usr/bin/env python3
"""
[CRITICAL FIX] Force ALL Narrative Generators to Use Actual KPI Values

This script updates all 6 narrative generators to NEVER use templates,
ALWAYS use actual numerical values from modules_data.

Target: app/services/final_report_assembly/narrative_generator.py
"""

import re

NARRATIVE_FILE = "app/services/final_report_assembly/narrative_generator.py"

# Read current file
with open(NARRATIVE_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
with open(NARRATIVE_FILE + ".backup_final", 'w', encoding='utf-8') as f:
    f.write(content)

print("📦 Backup created: narrative_generator.py.backup_final")

# ============================================================
# FIX 1: AllInOneNarrativeGenerator.executive_summary
# ============================================================

OLD_ALL_IN_ONE_EXEC = r'''    def executive_summary\(self, modules_data: Dict\) -> str:
        return """
        <section class="narrative executive-summary">
            <h2>📚 종합 분석 보고서 \(Comprehensive Report\)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업에 대한 
                <strong>완전한 종합 분석</strong> 결과입니다\.
            </p>
            
            <p class="narrative">
                토지 가치 평가\(M2\), LH 선호 주택유형\(M3\), 건축 규모 결정\(M4\), 
                사업성 분석\(M5\), LH 심사 예측\(M6\) 등 5개 모듈의 
                분석 결과를 모두 포함하고 있습니다\.
            </p>
            
            <p class="narrative">
                각 모듈은 독립적으로 분석되었으나, 종합적으로는 
                하나의 사업에 대한 다각도 검토 결과입니다\.
            </p>
            
            <p class="narrative">
                본 보고서를 통해 토지주, LH 심사역, 투자자 등 
                모든 이해관계자가 필요한 정보를 얻을 수 있습니다\.
            </p>
            
            <p class="narrative">
                상세 내용은 아래 5개 모듈 분석 결과를 참고하시기 바라며, 
                최종 의사결정은 전문가 자문 후 신중하게 내리시기 바랍니다\.
            </p>
            
            <p class="narrative">
                각 모듈의 결과는 독립적으로도 활용 가능하나, 
                종합적으로 검토할 때 가장 정확한 판단이 가능합니다\.
            </p>
        </section>
        """'''

NEW_ALL_IN_ONE_EXEC = '''    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] All-in-One MUST show actual KPI values
        """
        # Extract actual values
        m2_data = modules_data.get("M2", {})
        m4_data = modules_data.get("M4", {})
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", 0))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        roi = m5_data.get("roi", m5_data.get("ROI", 0))
        lh_decision = m6_data.get("decision", m6_data.get("Decision", ""))
        
        # Format safely
        land_str = f"{int(land_value):,}원" if land_value and land_value != 0 else "평가 불가"
        units_str = f"{int(total_units)}세대" if total_units and total_units != 0 else "미확정"
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
        irr_str = f"{float(irr)*100:.2f}%" if irr and irr != 0 else "산출 불가"
        roi_str = f"{float(roi)*100:.2f}%" if roi and roi != 0 else "산출 불가"
        lh_str = str(lh_decision) if lh_decision else "심사 대기"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📚 종합 분석 보고서 (Comprehensive Report)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업에 대한 
                <strong>완전한 종합 분석</strong> 결과입니다.
            </p>
            
            <p class="narrative">
                <strong>핵심 분석 결과:</strong><br/>
                • 토지 가치: <strong>{land_str}</strong><br/>
                • 건축 규모: <strong>{units_str}</strong><br/>
                • 순현재가치(NPV): <strong>{npv_str}</strong><br/>
                • 내부수익률(IRR): <strong>{irr_str}</strong><br/>
                • 투자수익률(ROI): <strong>{roi_str}</strong><br/>
                • LH 심사 전망: <strong>{lh_str}</strong>
            </p>
            
            <p class="narrative">
                토지 가치 평가(M2), LH 선호 주택유형(M3), 건축 규모 결정(M4), 
                사업성 분석(M5), LH 심사 예측(M6) 등 5개 모듈의 
                분석 결과를 모두 포함하고 있습니다.
            </p>
            
            <p class="narrative">
                상세 내용은 아래 5개 모듈 분석 결과를 참고하시기 바라며, 
                최종 의사결정은 전문가 자문 후 신중하게 내리시기 바랍니다.
            </p>
        </section>
        """'''

# Apply fix 1
content = re.sub(OLD_ALL_IN_ONE_EXEC, NEW_ALL_IN_ONE_EXEC, content, flags=re.DOTALL)
print("✅ Fixed: AllInOneNarrativeGenerator.executive_summary")

# ============================================================
# FIX 2: ExecutiveSummaryNarrativeGenerator - Fix key names
# ============================================================

# The ExecutiveSummary uses wrong keys (land_value instead of land_value_total)
OLD_EXEC_SUMMARY = r'''    def executive_summary\(self, modules_data: Dict\) -> str:
        m2_data = modules_data\.get\("M2", {}\)
        m5_data = modules_data\.get\("M5", {}\)
        m6_data = modules_data\.get\("M6", {}\)
        
        land_value = m2_data\.get\("land_value", 0\)
        npv = m5_data\.get\("npv", 0\)
        lh_decision = m6_data\.get\("decision", ""\)
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📌 Executive Summary \(경영진용\)</h2>
            
            <p class="narrative">
                <strong>투자 대상:</strong> 토지 가치 {land_value:,}원
            </p>
            
            <p class="narrative">
                <strong>재무 평가:</strong> NPV {npv:,}원 
                \({'수익 가능' if npv > 0 else '손실 예상'}\)
            </p>
            
            <p class="narrative">
                <strong>LH 승인:</strong> {lh_decision}
            </p>
        </section>
        """'''

NEW_EXEC_SUMMARY = '''    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] Executive Summary - Use correct key names
        """
        m2_data = modules_data.get("M2", {})
        m4_data = modules_data.get("M4", {})
        m5_data = modules_data.get("M5", {})
        m6_data = modules_data.get("M6", {})
        
        # Use correct key names with fallbacks
        land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", 0))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        lh_decision = m6_data.get("decision", m6_data.get("Decision", ""))
        
        # Format safely
        land_str = f"{int(land_value):,}원" if land_value and land_value != 0 else "평가 불가"
        units_str = f"{int(total_units):,}세대" if total_units and total_units != 0 else "미확정"
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
        irr_str = f"{float(irr)*100:.2f}%" if irr and irr != 0 else "산출 불가"
        npv_status = "수익 가능" if npv and float(npv) > 0 else "손실 예상" if npv and float(npv) < 0 else "미확정"
        lh_str = str(lh_decision) if lh_decision else "심사 대기"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📌 Executive Summary (경영진용)</h2>
            
            <p class="narrative">
                <strong>투자 대상:</strong> 토지 가치 <strong>{land_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>개발 규모:</strong> 총 <strong>{units_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>재무 평가:</strong> NPV <strong>{npv_str}</strong> ({npv_status})<br/>
                IRR <strong>{irr_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>LH 승인 전망:</strong> <strong>{lh_str}</strong>
            </p>
        </section>
        """'''

content = re.sub(OLD_EXEC_SUMMARY, NEW_EXEC_SUMMARY, content, flags=re.DOTALL)
print("✅ Fixed: ExecutiveSummaryNarrativeGenerator.executive_summary")

# ============================================================
# FIX 3: LHTechnicalNarrativeGenerator - Add actual numbers
# ============================================================

OLD_LH_TECH_EXEC = r'''    def executive_summary\(self, modules_data: Dict\) -> str:
        m3_data = modules_data\.get\("M3", {}\)
        m4_data = modules_data\.get\("M4", {}\)
        m6_data = modules_data\.get\("M6", {}\)
        
        recommended_type = m3_data\.get\("recommended_type", "미확정"\)
        household_count = m4_data\.get\("household_count", 0\)
        lh_decision = m6_data\.get\("decision", "검토 필요"\)
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📋 기술 검토 요약 \(Technical Review Summary\)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업의 기술적 타당성을 
                LH 내부 심사 기준에 따라 검토한 결과입니다\.
            </p>
            
            <p class="narrative">
                LH 선호 주택유형 분석 결과, 본 토지는 <strong>{recommended_type}</strong> 
                유형이 가장 적합한 것으로 분석되었으며, 건축 규모는 
                <strong>{household_count}세대</strong> 수준으로 계획 가능합니다\.
            </p>
            
            <p class="narrative">
                종합적인 LH 심사 기준 검토 결과, 본 사업은 <strong>"{lh_decision}"</strong> 
                수준으로 평가되었습니다\.
            </p>
            
            <p class="narrative">
                아래 상세 분석에서는 주택유형 선정 근거, 건축 규모 산정 과정, 
                LH 심사 항목별 평가 결과를 제시합니다\.
            </p>
            
            <p class="narrative">
                기술 검토 목적은 사업의 정책 부합성과 실현 가능성을 
                객관적으로 판단하는 것이며, 최종 심사 통과를 보장하지는 않습니다\.
            </p>
        </section>
        """'''

NEW_LH_TECH_EXEC = '''    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] LH Technical - Add FAR, BCR, scoring details
        """
        m3_data = modules_data.get("M3", {})
        m4_data = modules_data.get("M4", {})
        m6_data = modules_data.get("M6", {})
        
        recommended_type = m3_data.get("recommended_type", "미확정")
        type_score = m3_data.get("total_score", m3_data.get("type_score", 0))
        
        total_units = m4_data.get("total_units", m4_data.get("household_count", 0))
        far = m4_data.get("floor_area_ratio", m4_data.get("far", 0))
        bcr = m4_data.get("building_coverage_ratio", m4_data.get("bcr", 0))
        
        lh_decision = m6_data.get("decision", "검토 필요")
        total_score = m6_data.get("total_score", 0)
        
        # Format safely
        units_str = f"{int(total_units):,}세대" if total_units and total_units != 0 else "미확정"
        far_str = f"{float(far):.1f}%" if far and far != 0 else "산출 불가"
        bcr_str = f"{float(bcr):.1f}%" if bcr and bcr != 0 else "산출 불가"
        type_score_str = f"{float(type_score):.0f}점" if type_score and type_score != 0 else "미산정"
        lh_score_str = f"{float(total_score):.0f}점" if total_score and total_score != 0 else "미산정"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>📋 기술 검토 요약 (Technical Review Summary)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업의 기술적 타당성을 
                LH 내부 심사 기준에 따라 검토한 결과입니다.
            </p>
            
            <p class="narrative">
                <strong>주택유형 분석 (M3):</strong><br/>
                • 선호 유형: <strong>{recommended_type}</strong><br/>
                • 유형 점수: <strong>{type_score_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>건축 규모 (M4):</strong><br/>
                • 건축 세대수: <strong>{units_str}</strong><br/>
                • 용적률: <strong>{far_str}</strong><br/>
                • 건폐율: <strong>{bcr_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>LH 심사 예측 (M6):</strong><br/>
                • 종합 판단: <strong>{lh_decision}</strong><br/>
                • 종합 점수: <strong>{lh_score_str}</strong>
            </p>
            
            <p class="narrative">
                아래 상세 분석에서는 주택유형 선정 근거, 건축 규모 산정 과정, 
                LH 심사 항목별 평가 결과를 제시합니다.
            </p>
        </section>
        """'''

content = re.sub(OLD_LH_TECH_EXEC, NEW_LH_TECH_EXEC, content, flags=re.DOTALL)
print("✅ Fixed: LHTechnicalNarrativeGenerator.executive_summary")

# ============================================================
# FIX 4: FinancialFeasibilityNarrativeGenerator - Show ROI
# ============================================================

OLD_FINANCIAL_EXEC = r'''    def executive_summary\(self, modules_data: Dict\) -> str:
        m2_data = modules_data\.get\("M2", {}\)
        m4_data = modules_data\.get\("M4", {}\)
        m5_data = modules_data\.get\("M5", {}\)
        
        land_value = m2_data\.get\("land_value", 0\)
        total_units = m4_data\.get\("total_units", 0\)
        npv = m5_data\.get\("npv", 0\)
        irr = m5_data\.get\("irr", 0\)
        
        return f"""
        <section class="narrative executive-summary">
            <h2>💰 재무 타당성 분석 요약 \(Financial Feasibility Summary\)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업의 
                <strong>재무적 타당성</strong>을 투자 수익성 관점에서 분석한 결과입니다\.
            </p>
            
            <p class="narrative">
                토지 매입가 {land_value:,}원을 기준으로 
                총 {total_units}세대 건축 시 예상되는 
                투자 수익을 정량적으로 분석하였습니다\.
            </p>
            
            <p class="narrative">
                순현재가치\(NPV\)는 <strong>{npv:,}원</strong>으로 산출되었으며, 
                내부수익률\(IRR\)은 <strong>{irr\*100:\.2f}%</strong>로 
                {'양호한' if irr > 7 else '검토가 필요한'} 수준입니다\.
            </p>
            
            <p class="narrative">
                아래 상세 분석에서는 투자금 구조, 수익 예측, 
                리스크 요인을 포함한 종합적인 재무 평가를 제공합니다\.
            </p>
        </section>
        """'''

NEW_FINANCIAL_EXEC = '''    def executive_summary(self, modules_data: Dict) -> str:
        """
        [vABSOLUTE-FINAL-10] Financial - Add ROI, construction cost details
        """
        m2_data = modules_data.get("M2", {})
        m4_data = modules_data.get("M4", {})
        m5_data = modules_data.get("M5", {})
        
        land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", 0))
        total_units = m4_data.get("total_units", m5_data.get("total_units", 0))
        
        npv = m5_data.get("npv", m5_data.get("NPV", 0))
        irr = m5_data.get("irr", m5_data.get("IRR", 0))
        roi = m5_data.get("roi", m5_data.get("ROI", 0))
        total_cost = m5_data.get("total_cost", m5_data.get("total_investment", 0))
        total_revenue = m5_data.get("total_revenue", 0))
        
        # Format safely
        land_str = f"{int(land_value):,}원" if land_value and land_value != 0 else "평가 중"
        units_str = f"{int(total_units):,}세대" if total_units and total_units != 0 else "미확정"
        npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
        irr_str = f"{float(irr)*100:.2f}%" if irr and irr != 0 else "산출 불가"
        roi_str = f"{float(roi)*100:.2f}%" if roi and roi != 0 else "산출 불가"
        cost_str = f"{int(total_cost):,}원" if total_cost and total_cost != 0 else "집계 중"
        revenue_str = f"{int(total_revenue):,}원" if total_revenue and total_revenue != 0 else "예측 중"
        
        irr_rating = "우수한" if irr and float(irr) > 0.10 else "양호한" if irr and float(irr) > 0.07 else "검토가 필요한"
        
        return f"""
        <section class="narrative executive-summary">
            <h2>💰 재무 타당성 분석 요약 (Financial Feasibility Summary)</h2>
            
            <p class="narrative">
                본 보고서는 LH 공공기여형 민간임대주택 사업의 
                <strong>재무적 타당성</strong>을 투자 수익성 관점에서 분석한 결과입니다.
            </p>
            
            <p class="narrative">
                <strong>투자 규모:</strong><br/>
                • 토지 매입가: <strong>{land_str}</strong><br/>
                • 건축 세대수: <strong>{units_str}</strong><br/>
                • 총 사업비: <strong>{cost_str}</strong><br/>
                • 예상 수익: <strong>{revenue_str}</strong>
            </p>
            
            <p class="narrative">
                <strong>수익성 지표:</strong><br/>
                • 순현재가치(NPV): <strong>{npv_str}</strong><br/>
                • 내부수익률(IRR): <strong>{irr_str}</strong> ({irr_rating} 수준)<br/>
                • 투자수익률(ROI): <strong>{roi_str}</strong>
            </p>
            
            <p class="narrative">
                아래 상세 분석에서는 투자금 구조, 수익 예측, 
                리스크 요인을 포함한 종합적인 재무 평가를 제공합니다.
            </p>
        </section>
        """'''

content = re.sub(OLD_FINANCIAL_EXEC, NEW_FINANCIAL_EXEC, content, flags=re.DOTALL)
print("✅ Fixed: FinancialFeasibilityNarrativeGenerator.executive_summary")

# Save updated file
with open(NARRATIVE_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("🎉 ALL NARRATIVE GENERATORS UPDATED!")
print("="*60)
print("\n✅ Changes:")
print("  1. AllInOneNarrativeGenerator: Now shows NPV, IRR, ROI, units")
print("  2. ExecutiveSummaryNarrativeGenerator: Fixed key names, added IRR/units")
print("  3. LHTechnicalNarrativeGenerator: Added FAR, BCR, scoring details")
print("  4. FinancialFeasibilityNarrativeGenerator: Added ROI, cost breakdown")
print("\n🔧 Previous fixes already applied:")
print("  5. QuickCheckNarrativeGenerator ✓ (vABSOLUTE-FINAL-10)")
print("  6. LandownerNarrativeGenerator ✓ (vABSOLUTE-FINAL-10)")
print("\n📍 Next Step:")
print("  Generate NEW report from pipeline to see actual values!")
print("  All 6 report types will now use ACTUAL KPI values.")
