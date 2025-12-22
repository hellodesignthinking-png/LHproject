"""
FINAL REPORT NARRATIVE & VISUAL REINFORCEMENT PATCH
====================================================

Enhances report completeness, interpretability, and delivery quality.

[FIX 1] Interpretation Paragraph Enforcement - explain what numbers mean
[FIX 2] Module Transition Reinforcement - connect analysis flow
[FIX 3] Report-Type Visual Emphasis - differentiate by color
[FIX 4] "Next Action" Section - clear next steps
[FIX 5] Density Final Check - section summaries for long reports

⚠️ NARRATIVE & VISUAL POLISH ONLY - No engine/calculation changes
"""

import re
import os


# Report type color schemes
REPORT_COLORS = {
    "landowner_summary": {
        "primary": "#007bff",  # BLUE
        "secondary": "#e3f2fd",
        "name": "토지주용"
    },
    "lh_technical": {
        "primary": "#495057",  # DARK GRAY
        "secondary": "#f8f9fa",
        "name": "LH 기술검토용"
    },
    "financial_feasibility": {
        "primary": "#28a745",  # GREEN
        "secondary": "#d4edda",
        "name": "재무타당성용"
    },
    "executive_summary": {
        "primary": "#6f42c1",  # PURPLE
        "secondary": "#e2d9f3",
        "name": "경영진용"
    },
    "quick_check": {
        "primary": "#fd7e14",  # ORANGE
        "secondary": "#ffe5d0",
        "name": "빠른의사결정용"
    },
    "all_in_one": {
        "primary": "#6c757d",  # NEUTRAL
        "secondary": "#f8f9fa",
        "name": "종합보고서"
    }
}


def apply_fix_1_interpretation_paragraphs():
    """
    [FIX 1] Add interpretation paragraphs after KPI boxes
    
    Explains what the data means and why it matters for this report type
    """
    print("\n[FIX 1] Applying Interpretation Paragraph Enforcement...")
    
    filepath = "app/services/final_report_assembly/base_assembler.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add helper method to generate interpretation paragraphs
    helper_method = '''
    @staticmethod
    def generate_interpretation_paragraph(module_id: str, report_type: str, module_data: dict) -> str:
        """
        [FIX 1] Generate interpretation paragraph explaining what the data means
        
        Args:
            module_id: M2, M3, M4, M5, or M6
            report_type: landowner_summary, lh_technical, etc.
            module_data: Extracted data from the module
        
        Returns:
            HTML paragraph explaining the significance
        """
        interpretations = {
            "M2": {
                "landowner_summary": "이 감정가는 귀하의 토지 자산 가치를 나타내며, LH 매입 협상 시 기준가로 활용됩니다.",
                "lh_technical": "토지 감정가는 LH 매입 가능성 판단의 기준값으로, 이후 사업성 분석의 출발점이 됩니다.",
                "financial_feasibility": "토지 감정가는 초기 투자비용의 핵심 항목이며, ROI 산출의 기초 데이터입니다.",
                "executive_summary": "토지 감정가는 사업 타당성 검토의 첫 번째 관문으로, 전체 사업비 규모를 결정합니다.",
                "all_in_one": "토지 감정가는 사업의 출발점이자 LH 협의의 기준이 되는 핵심 지표입니다."
            },
            "M3": {
                "lh_technical": "선호 유형 분석 결과는 LH 정책 부합성을 직접적으로 나타내며, 사업 승인 가능성의 첫 번째 관문입니다.",
                "all_in_one": "LH 선호 유형 매칭 결과는 정책적 실현 가능성을 보여주는 핵심 지표입니다."
            },
            "M4": {
                "lh_technical": "계획 세대수는 LH 공급 목표와의 정합성을 판단하는 기준이며, 건축 규모의 적정성을 나타냅니다.",
                "financial_feasibility": "계획 세대수는 매출 규모를 결정하는 핵심 변수로, 사업성 산출의 기초가 됩니다.",
                "all_in_one": "계획 세대수는 사업 규모와 수익성을 동시에 결정하는 핵심 설계 요소입니다."
            },
            "M5": {
                "landowner_summary": "NPV와 수익성 분석 결과는 사업 추진 여부를 판단하는 가장 중요한 재무적 근거입니다.",
                "financial_feasibility": "재무 분석 결과는 투자 의사결정의 핵심으로, NPV/IRR이 모두 양호해야 추진 가능합니다.",
                "quick_check": "수익성 분석은 GO/NO-GO 결정의 가장 중요한 기준입니다. NPV가 양수일 때만 추진을 권장합니다.",
                "executive_summary": "재무 타당성은 사업 추진의 필수 조건이며, 이사회 승인의 핵심 근거가 됩니다.",
                "all_in_one": "재무 분석 결과는 토지주, 투자자, LH 모두에게 가장 중요한 판단 기준입니다."
            },
            "M6": {
                "landowner_summary": "LH 심사 결과는 사업 실현 가능성을 최종적으로 결정하는 가장 중요한 단계입니다.",
                "lh_technical": "LH 심사 결과는 정책 부합성과 기술적 타당성을 종합한 최종 평가로, 사업 승인의 직접적 근거입니다.",
                "quick_check": "LH 심사 결과가 '승인'이어야 실제 사업 추진이 가능합니다.",
                "executive_summary": "LH 최종 심사는 사업 추진의 결정적 관문으로, 승인 없이는 진행이 불가능합니다.",
                "all_in_one": "LH 심사는 모든 분석의 종합 평가이자, 실제 사업 추진 여부를 결정하는 최종 단계입니다."
            }
        }
        
        # Get interpretation text
        interpretation_text = interpretations.get(module_id, {}).get(
            report_type, 
            f"{module_id} 분석 결과는 이후 단계의 중요한 기초 자료로 활용됩니다."
        )
        
        # Add specific data if available
        data_insight = ""
        if module_id == "M2" and "land_value" in module_data:
            land_value = module_data["land_value"]
            if land_value > 0:
                formatted_value = BaseFinalReportAssembler.format_number(land_value, 'currency')
                data_insight = f" 현재 감정가 {formatted_value}는 "
                if land_value > 1000000000:
                    data_insight += "대규모 사업에 적합한 수준입니다."
                else:
                    data_insight += "중소규모 사업에 적합한 수준입니다."
        
        elif module_id == "M5" and "npv" in module_data:
            npv = module_data["npv"]
            if npv is not None:
                formatted_npv = BaseFinalReportAssembler.format_number(npv, 'currency')
                data_insight = f" 산출된 NPV {formatted_npv}는 "
                if npv > 0:
                    data_insight += "재무적으로 타당한 사업임을 나타냅니다."
                else:
                    data_insight += "재무 구조 개선이 필요함을 시사합니다."
        
        elif module_id == "M6" and "decision" in module_data:
            decision = module_data["decision"]
            if "승인" in decision:
                data_insight = " 승인 결과는 사업 추진이 가능함을 의미합니다."
            elif "조건부" in decision:
                data_insight = " 조건부 판정은 보완 후 재심사가 필요함을 의미합니다."
        
        return f'''
        <div class="interpretation-box" style="
            background: #fffbea;
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
        ">
            <p style="margin: 0; font-size: 14px; line-height: 1.6; color: #856404;">
                <strong>💡 해석:</strong> {interpretation_text}{data_insight}
            </p>
        </div>
        '''
'''
    
    # Find insertion point
    insert_marker = '\n    @staticmethod\n    def get_unified_design_css() -> str:'
    
    if insert_marker in content:
        content = content.replace(insert_marker, helper_method + insert_marker)
        print("  ✅ Added generate_interpretation_paragraph helper method")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ [FIX 1] Complete: Interpretation Paragraph helper added")


def apply_fix_2_module_transitions():
    """
    [FIX 2] Add module transition boxes between sections
    """
    print("\n[FIX 2] Applying Module Transition Reinforcement...")
    
    filepath = "app/services/final_report_assembly/base_assembler.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add helper method for transitions
    helper_method = '''
    @staticmethod
    def generate_module_transition(from_module: str, to_module: str) -> str:
        """
        [FIX 2] Generate transition box between modules
        
        Args:
            from_module: Source module (M2, M3, etc.)
            to_module: Destination module
        
        Returns:
            HTML transition box
        """
        transitions = {
            ("M2", "M5"): "토지 평가 결과를 바탕으로 사업성 분석을 진행합니다.",
            ("M2", "M3"): "토지 가치 평가 후 최적 공급 유형을 분석합니다.",
            ("M3", "M4"): "선호 유형 분석 결과에 따라 건축 규모를 산정합니다.",
            ("M4", "M5"): "건축 규모 산정 결과를 기반으로 재무 타당성을 검토합니다.",
            ("M5", "M6"): "재무 분석 결과를 종합하여 LH 정책 부합성을 최종 검토합니다.",
        }
        
        transition_text = transitions.get(
            (from_module, to_module),
            f"{from_module} 분석 결과를 바탕으로 {to_module} 검토로 이동합니다."
        )
        
        return f'''
        <div class="module-transition" style="
            text-align: center;
            padding: 20px;
            margin: 30px 0;
            background: linear-gradient(90deg, transparent 0%, #e9ecef 50%, transparent 100%);
        ">
            <p style="
                display: inline-block;
                background: white;
                padding: 10px 30px;
                border-radius: 20px;
                border: 2px solid #007bff;
                margin: 0;
                font-weight: 600;
                color: #007bff;
            ">
                ➡️ {transition_text}
            </p>
        </div>
        '''
'''
    
    # Find insertion point (after generate_interpretation_paragraph)
    insert_marker = '\n    @staticmethod\n    def get_unified_design_css() -> str:'
    
    if insert_marker in content:
        content = content.replace(insert_marker, helper_method + insert_marker)
        print("  ✅ Added generate_module_transition helper method")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ [FIX 2] Complete: Module Transition helper added")


def apply_fix_3_report_type_colors():
    """
    [FIX 3] Add report-type specific color schemes
    """
    print("\n[FIX 3] Applying Report-Type Visual Emphasis...")
    
    filepath = "app/services/final_report_assembly/base_assembler.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add color scheme data and helper method
    color_data = f"""
    # [FIX 3] Report-Type Color Schemes
    REPORT_TYPE_COLORS = {repr(REPORT_COLORS)}
"""
    
    helper_method = '''
    @staticmethod
    def get_report_type_color(report_type: str, shade: str = "primary") -> str:
        """
        [FIX 3] Get color for specific report type
        
        Args:
            report_type: landowner_summary, lh_technical, etc.
            shade: 'primary' or 'secondary'
        
        Returns:
            Hex color code
        """
        from app.services.final_report_assembly.base_assembler import BaseFinalReportAssembler
        colors = BaseFinalReportAssembler.REPORT_TYPE_COLORS.get(
            report_type,
            {"primary": "#007bff", "secondary": "#e3f2fd"}
        )
        return colors.get(shade, colors["primary"])
'''
    
    # Find class definition to add color data
    class_marker = 'class BaseFinalReportAssembler:'
    if class_marker in content:
        # Add after class docstring
        docstring_end = content.find('"""', content.find(class_marker) + 100)
        if docstring_end > -1:
            insert_pos = content.find('\n', docstring_end + 3)
            content = content[:insert_pos] + color_data + content[insert_pos:]
            print("  ✅ Added REPORT_TYPE_COLORS data")
    
    # Add helper method
    insert_marker = '\n    @staticmethod\n    def get_unified_design_css() -> str:'
    if insert_marker in content:
        content = content.replace(insert_marker, helper_method + insert_marker)
        print("  ✅ Added get_report_type_color helper method")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ [FIX 3] Complete: Report-Type Color system added")


def apply_fix_4_next_action_section():
    """
    [FIX 4] Add mandatory "Next Action" section template
    """
    print("\n[FIX 4] Applying Next Action Section...")
    
    filepath = "app/services/final_report_assembly/base_assembler.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add helper method for next actions
    helper_method = '''
    @staticmethod
    def generate_next_action_section(report_type: str, modules_data: dict, judgment: str) -> str:
        """
        [FIX 4] Generate "Next Action" section with clear next steps
        
        Args:
            report_type: Type of report
            modules_data: Module analysis data
            judgment: Final judgment text
        
        Returns:
            HTML for next action section
        """
        # Determine actions based on judgment
        if "권장" in judgment or "추진 가능" in judgment:
            status_icon = "✅"
            status_color = "#28a745"
            recommended_actions = [
                "LH 사전 협의 및 매입 의향 확인",
                "설계 용역 발주 준비",
                "인허가 사전 검토 착수"
            ]
            required_docs = [
                "토지 등기부등본",
                "지적도 및 토지이용계획확인서",
                "사업계획서 초안"
            ]
        elif "조건부" in judgment:
            status_icon = "⚠️"
            status_color = "#ffc107"
            recommended_actions = [
                "LH 지적 사항 상세 검토 및 보완",
                "재무 구조 개선 방안 수립",
                "보완 후 재분석 및 재제출"
            ]
            required_docs = [
                "LH 심사 의견서",
                "보완 계획서",
                "수정 사업계획서"
            ]
        else:
            status_icon = "❌"
            status_color = "#dc3545"
            recommended_actions = [
                "사업 계획 전면 재검토",
                "대안 부지 탐색",
                "사업 구조 재설계"
            ]
            required_docs = [
                "현 분석 결과 리포트",
                "대안 검토 자료",
                "리스크 분석 보고서"
            ]
        
        # Add report-type specific recommendations
        if report_type == "landowner_summary":
            recommended_actions.append("전문 컨설팅 업체와 추가 상담 권장")
        elif report_type == "financial_feasibility":
            recommended_actions.append("투자자 IR 자료 준비")
        elif report_type == "lh_technical":
            recommended_actions.append("LH 담당 부서와 기술 협의")
        
        actions_html = "\\n".join([f"<li>{action}</li>" for action in recommended_actions])
        docs_html = "\\n".join([f"<li>{doc}</li>" for doc in required_docs])
        
        return f"""
        <section class="next-action-section" style="
            background: linear-gradient(135deg, {status_color}15 0%, {status_color}05 100%);
            border: 2px solid {status_color};
            border-radius: 12px;
            padding: 30px;
            margin: 40px 0;
            page-break-inside: avoid;
        ">
            <h2 style="
                color: {status_color};
                font-size: 22px;
                margin: 0 0 20px 0;
                display: flex;
                align-items: center;
                gap: 10px;
            ">
                {status_icon} 다음 단계 안내
            </h2>
            
            <div style="margin: 20px 0;">
                <h3 style="font-size: 16px; color: #333; margin: 15px 0 10px 0;">
                    📋 권장 조치사항
                </h3>
                <ol style="margin: 0; padding-left: 25px; line-height: 1.8;">
                    {actions_html}
                </ol>
            </div>
            
            <div style="margin: 20px 0;">
                <h3 style="font-size: 16px; color: #333; margin: 15px 0 10px 0;">
                    📄 준비 필요 서류
                </h3>
                <ul style="margin: 0; padding-left: 25px; line-height: 1.8;">
                    {docs_html}
                </ul>
            </div>
            
            <div style="
                margin-top: 25px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                border-left: 4px solid {status_color};
            ">
                <p style="margin: 0; font-size: 13px; color: #666; line-height: 1.6;">
                    <strong>💡 참고:</strong> 본 분석 결과는 현재 시점 기준이며, 
                    실제 추진 시 최신 정책 및 시장 상황을 재확인하시기 바랍니다.
                    추가 문의사항은 담당 컨설턴트에게 연락 주시기 바랍니다.
                </p>
            </div>
        </section>
        """
'''
    
    # Add helper method
    insert_marker = '\n    @staticmethod\n    def get_unified_design_css() -> str:'
    if insert_marker in content:
        content = content.replace(insert_marker, helper_method + insert_marker)
        print("  ✅ Added generate_next_action_section helper method")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ [FIX 4] Complete: Next Action Section helper added")


def apply_fix_5_density_check():
    """
    [FIX 5] Add section summary for long reports
    """
    print("\n[FIX 5] Applying Density Final Check...")
    
    filepath = "app/services/final_report_assembly/base_assembler.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add helper method for section summaries
    helper_method = '''
    @staticmethod
    def generate_section_summary(modules_covered: list, key_findings: dict) -> str:
        """
        [FIX 5] Generate section summary for dense reports
        
        Args:
            modules_covered: List of modules in this section (e.g., ['M2', 'M3'])
            key_findings: Dict of key findings {module_id: finding_text}
        
        Returns:
            HTML section summary
        """
        findings_html = ""
        for module_id in modules_covered:
            finding = key_findings.get(module_id, f"{module_id} 분석 완료")
            findings_html += f"<li><strong>{module_id}:</strong> {finding}</li>\\n"
        
        return f"""
        <div class="section-summary" style="
            background: #f8f9fa;
            border: 2px dashed #6c757d;
            border-radius: 8px;
            padding: 20px;
            margin: 40px 0;
        ">
            <h3 style="
                color: #495057;
                font-size: 16px;
                margin: 0 0 15px 0;
            ">
                📊 구간 요약 (Modules: {', '.join(modules_covered)})
            </h3>
            <ul style="
                margin: 0;
                padding-left: 25px;
                line-height: 1.8;
                color: #495057;
            ">
                {findings_html}
            </ul>
        </div>
        """
'''
    
    # Add helper method
    insert_marker = '\n    @staticmethod\n    def get_unified_design_css() -> str:'
    if insert_marker in content:
        content = content.replace(insert_marker, helper_method + insert_marker)
        print("  ✅ Added generate_section_summary helper method")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ [FIX 5] Complete: Section Summary helper added")


def apply_all_fixes():
    """Execute all 5 narrative/visual fixes"""
    print("="*70)
    print("FINAL REPORT NARRATIVE & VISUAL REINFORCEMENT PATCH")
    print("="*70)
    print("\nEnhancing report completeness and delivery quality...")
    print("\n⚠️  NARRATIVE & VISUAL POLISH ONLY - No engine/calculation changes\n")
    
    try:
        apply_fix_1_interpretation_paragraphs()
        apply_fix_2_module_transitions()
        apply_fix_3_report_type_colors()
        apply_fix_4_next_action_section()
        apply_fix_5_density_check()
        
        print("\n" + "="*70)
        print("✅ ALL 5 NARRATIVE/VISUAL FIXES APPLIED")
        print("="*70)
        print("\nFinal Report Reinforcement Complete!")
        print("\nNext Steps:")
        print("  1. Apply helpers to individual assemblers")
        print("  2. Run narrative validation tests")
        print("  3. Generate sample reports for review")
        print("  4. Commit changes")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error during patch application: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = apply_all_fixes()
    exit(0 if success else 1)
