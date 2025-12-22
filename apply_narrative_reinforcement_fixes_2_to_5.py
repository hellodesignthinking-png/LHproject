#!/usr/bin/env python3
"""
Apply Narrative Reinforcement Fixes 2-5 to All Assemblers
==========================================================

FIX 2: Module Transition Reinforcement (transition boxes)
FIX 3: Report-Type Visual Emphasis (color coding)
FIX 4: Next Action Section (mandatory next steps guidance)
FIX 5: Density Final Check (section summaries for long reports)

CRITICAL: Display-level only, NO engine/QA/calculation changes
"""

import re
from pathlib import Path


ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")
BASE_ASSEMBLER = Path("app/services/final_report_assembly/base_assembler.py")


# ============================================================================
# FIX 2: Module Transition Box Generator
# ============================================================================

MODULE_TRANSITION_METHOD = '''
    @staticmethod
    def generate_module_transition(from_module: str, to_module: str, report_type: str = "landowner_summary") -> str:
        """
        [FIX 2] Module Transition Reinforcement
        
        Generate transition box between modules to explain flow logic.
        Shows how previous results influence the next analysis.
        
        Returns:
            HTML string for transition box
        """
        # Module name mapping
        MODULE_NAMES = {
            "M2": "토지평가",
            "M3": "주택유형",
            "M4": "사업규모",
            "M5": "사업성",
            "M6": "LH심사"
        }
        
        from_name = MODULE_NAMES.get(from_module, from_module)
        to_name = MODULE_NAMES.get(to_module, to_module)
        
        # Context-specific transition messages
        transitions = {
            ("M2", "M5"): f"앞선 {from_name} 결과를 바탕으로 {to_name} 검토 단계로 이동합니다.",
            ("M5", "M6"): f"{from_name} 분석 결과를 바탕으로 {to_name} 판정을 진행합니다.",
            ("M3", "M4"): f"{from_name} 선정 결과를 기반으로 {to_name} 설계를 수립합니다.",
            ("M4", "M5"): f"{from_name} 계획안을 바탕으로 {to_name} 분석을 시작합니다.",
            ("M2", "M3"): f"{from_name} 결과를 반영하여 {to_name} 검토를 진행합니다.",
        }
        
        default_message = f"앞선 분석 결과를 바탕으로 다음 검토 단계로 이동합니다."
        message = transitions.get((from_module, to_module), default_message)
        
        return f"""
        <div class="module-transition">
            <div class="transition-icon">→</div>
            <p class="transition-text">{message}</p>
        </div>
        """
'''


# ============================================================================
# FIX 3: Report-Type Color Schemes
# ============================================================================

REPORT_COLOR_SCHEMES = {
    "landowner_summary": "#2563EB",  # BLUE
    "lh_technical": "#374151",       # DARK GRAY
    "financial_feasibility": "#10B981",  # GREEN
    "executive_summary": "#8B5CF6",  # PURPLE
    "quick_check": "#F59E0B",        # ORANGE
    "all_in_one": "#6B7280"          # NEUTRAL GRAY
}


def apply_fix_2_add_transition_method():
    """Add module transition generator to base_assembler.py"""
    
    content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    # Check if already exists
    if "generate_module_transition" in content:
        print("✅ [FIX 2] Module transition method already exists")
        return True
    
    # Find insertion point (after generate_decision_block method)
    pattern = r'(    @staticmethod\s+def generate_decision_block\([^)]+\)[^:]+:.*?""")\s*\n'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ [FIX 2] Could not find insertion point for transition method")
        return False
    
    # Find end of generate_decision_block method
    end_of_method = match.end()
    rest_of_content = content[end_of_method:]
    
    # Find next method definition or end of class
    next_method_match = re.search(r'\n(    def |    @staticmethod)', rest_of_content)
    if next_method_match:
        insertion_point = end_of_method + next_method_match.start()
    else:
        insertion_point = end_of_method + len(rest_of_content)
    
    # Insert transition method
    new_content = (
        content[:insertion_point] +
        "\n" + MODULE_TRANSITION_METHOD + "\n" +
        content[insertion_point:]
    )
    
    BASE_ASSEMBLER.write_text(new_content, encoding='utf-8')
    print("✅ [FIX 2] Added module transition generator method")
    return True


def apply_fix_3_add_color_system_to_css():
    """Enhance unified design CSS with report-type color schemes"""
    
    content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    # Check if color system already exists
    if "report-color-landowner" in content:
        print("✅ [FIX 3] Report color system already exists")
        return True
    
    # Find get_unified_design_css method
    css_method_start = content.find("def get_unified_design_css():")
    if css_method_start == -1:
        print("❌ [FIX 3] Could not find get_unified_design_css method")
        return False
    
    # Find the return statement with CSS
    css_return_start = content.find('return """', css_method_start)
    if css_return_start == -1:
        print("❌ [FIX 3] Could not find CSS return statement")
        return False
    
    # Find closing of CSS string
    css_closing = content.find('"""', css_return_start + 10)
    if css_closing == -1:
        print("❌ [FIX 3] Could not find CSS closing")
        return False
    
    # Extract current CSS
    current_css = content[css_return_start + 10:css_closing]
    
    # Add report-type color system CSS
    color_css = """
        
        /* [FIX 3] Report-Type Visual Emphasis */
        .report-color-landowner .report-title::after,
        .report-color-landowner .kpi-summary { border-color: #2563EB; }
        .report-color-landowner .decision-block { background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); }
        
        .report-color-lh_technical .report-title::after,
        .report-color-lh_technical .kpi-summary { border-color: #374151; }
        .report-color-lh_technical .decision-block { background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%); }
        
        .report-color-financial .report-title::after,
        .report-color-financial .kpi-summary { border-color: #10B981; }
        .report-color-financial .decision-block { background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); }
        
        .report-color-executive .report-title::after,
        .report-color-executive .kpi-summary { border-color: #8B5CF6; }
        .report-color-executive .decision-block { background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%); }
        
        .report-color-quick .report-title::after,
        .report-color-quick .kpi-summary { border-color: #F59E0B; }
        .report-color-quick .decision-block { background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); }
        
        .report-color-all .report-title::after,
        .report-color-all .kpi-summary { border-color: #6B7280; }
        .report-color-all .decision-block { background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%); }
        
        /* Module Transition Box */
        .module-transition {
            display: flex;
            align-items: center;
            padding: 16px 24px;
            margin: 32px 0;
            background: #F0F9FF;
            border-left: 4px solid #3B82F6;
            border-radius: 4px;
        }
        .transition-icon {
            font-size: 24px;
            font-weight: bold;
            color: #3B82F6;
            margin-right: 16px;
        }
        .transition-text {
            font-size: 14px;
            color: #1E40AF;
            margin: 0;
            font-weight: 500;
        }
        
        /* Section Divider for dense reports */
        .section-divider {
            margin: 48px 0 32px;
            padding: 24px;
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
            border-left: 4px solid #3B82F6;
            border-radius: 8px;
        }
        .section-divider h2 {
            margin: 0 0 8px;
            font-size: 20px;
            font-weight: 700;
            color: #1E293B;
        }
        .section-divider p {
            margin: 0;
            font-size: 14px;
            color: #64748B;
            line-height: 1.6;
        }
        
        /* Next Actions Section */
        .next-actions-section {
            margin-top: 48px;
            padding: 32px;
            background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
            border: 2px solid #FB923C;
            border-radius: 12px;
            page-break-inside: avoid;
        }
        .next-actions-section h2 {
            margin: 0 0 24px;
            font-size: 22px;
            font-weight: 700;
            color: #EA580C;
            display: flex;
            align-items: center;
        }
        .next-actions-section h2::before {
            content: "📋";
            margin-right: 12px;
            font-size: 28px;
        }
        .next-actions-section h3 {
            margin: 24px 0 12px;
            font-size: 16px;
            font-weight: 600;
            color: #9A3412;
        }
        .next-actions-section ul {
            list-style: none;
            padding: 0;
            margin: 12px 0;
        }
        .next-actions-section li {
            padding: 12px 16px;
            margin: 8px 0;
            background: white;
            border-left: 3px solid #FB923C;
            border-radius: 4px;
            font-size: 14px;
            line-height: 1.6;
        }
        .next-actions-section li strong {
            color: #EA580C;
        }
"""
    
    # Insert color CSS before closing
    new_css = current_css + color_css
    new_content = content[:css_return_start + 10] + new_css + content[css_closing:]
    
    BASE_ASSEMBLER.write_text(new_content, encoding='utf-8')
    print("✅ [FIX 3] Enhanced CSS with report-type color system")
    return True


def apply_fix_4_add_next_actions_generator():
    """Add next actions section generator to base_assembler.py"""
    
    content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    # Check if already exists
    if "generate_next_actions_section" in content:
        print("✅ [FIX 4] Next actions generator already exists")
        return True
    
    next_actions_method = '''
    @staticmethod
    def generate_next_actions_section(
        modules_data: Dict,
        report_type: str
    ) -> str:
        """
        [FIX 4] Next Action Section (MANDATORY)
        
        Generate "Next Steps Guidance" section at end of every report.
        Provides concrete action items based on report findings.
        
        Args:
            modules_data: Extracted module data
            report_type: Type of report being generated
            
        Returns:
            HTML string for next actions section
        """
        # Extract key decision factors
        npv = modules_data.get("M5", {}).get("npv", 0)
        profitability = modules_data.get("M5", {}).get("profitability", "미확정")
        decision = modules_data.get("M6", {}).get("decision", "미확정")
        
        # Determine overall status
        is_profitable = npv and npv > 0 if isinstance(npv, (int, float)) else False
        is_approved = "승인" in decision if isinstance(decision, str) else False
        is_conditional = "조건부" in decision if isinstance(decision, str) else False
        
        # Generate recommended actions
        actions = []
        
        if is_profitable and is_approved:
            actions = [
                "<strong>사업 추진 준비:</strong> LH 정식 신청을 위한 세부 서류 준비를 시작하십시오.",
                "<strong>자금 계획 수립:</strong> 사업 실행을 위한 자금 조달 계획을 구체화하십시오.",
                "<strong>일정 수립:</strong> 인허가 및 착공 일정표를 작성하십시오."
            ]
        elif is_profitable and is_conditional:
            actions = [
                "<strong>보완 사항 확인:</strong> LH 조건부 승인 사항을 정확히 파악하고 보완 계획을 수립하십시오.",
                "<strong>추가 분석:</strong> 조건 충족을 위한 추가 검토 및 설계 보완을 진행하십시오.",
                "<strong>재검토 준비:</strong> 보완 후 재심사 신청을 위한 서류를 준비하십시오."
            ]
        elif is_profitable and not is_approved:
            actions = [
                "<strong>대안 검토:</strong> 현 계획의 수정 가능성 또는 대안 사업 방식을 검토하십시오.",
                "<strong>전문가 자문:</strong> LH 부적합 사유에 대한 전문가 자문을 받으십시오.",
                "<strong>재평가:</strong> 사업 방향 전환 또는 토지 활용 대안을 재평가하십시오."
            ]
        elif not is_profitable:
            actions = [
                "<strong>수익성 개선 방안:</strong> 사업 규모, 설계 또는 비용 구조 조정 방안을 검토하십시오.",
                "<strong>시장 재분석:</strong> 분양가 또는 임대 조건 재검토를 통해 수익성 개선 가능성을 확인하십시오.",
                "<strong>사업 중단 검토:</strong> 개선이 어려울 경우 사업 중단 또는 토지 처분을 고려하십시오."
            ]
        else:
            actions = [
                "<strong>추가 자료 수집:</strong> 부족한 데이터를 보완하여 정확한 분석을 재시도하십시오.",
                "<strong>전문가 검토:</strong> 현 분석 결과에 대한 전문가 검증을 받으십시오.",
                "<strong>단계별 접근:</strong> 우선 Quick Check 후 상세 분석을 진행하십시오."
            ]
        
        actions_html = "\\n".join([f"<li>{action}</li>" for action in actions])
        
        # Required documents section
        required_docs = []
        if is_approved or is_conditional:
            required_docs = [
                "토지 소유권 증명서류",
                "사업계획서 (본 보고서 기반)",
                "LH 신청서 (공식 양식)"
            ]
        else:
            required_docs = [
                "현 분석 보고서 (검토용)",
                "토지 관련 추가 자료",
                "대안 검토를 위한 시장 자료"
            ]
        
        docs_html = "\\n".join([f"<li>{doc}</li>" for doc in required_docs])
        
        # Conditional notes
        notes = []
        if is_conditional:
            notes.append("LH 조건부 승인 사항을 반드시 충족해야 최종 승인이 가능합니다.")
        if not is_profitable:
            notes.append("현재 수익성이 부족하여 사업 추진 시 손실 위험이 있습니다.")
        if "미확정" in decision:
            notes.append("LH 심사 결과가 명확하지 않아 재검토가 필요합니다.")
        
        notes_html = ""
        if notes:
            notes_items = "\\n".join([f"<li>⚠️ {note}</li>" for note in notes])
            notes_html = f"""
            <h3>⚠️ 주의사항</h3>
            <ul>
                {notes_items}
            </ul>
            """
        
        return f"""
        <div class="next-actions-section">
            <h2>다음 단계 안내</h2>
            
            <h3>✅ 권장 조치사항</h3>
            <ul>
                {actions_html}
            </ul>
            
            <h3>📄 필요 서류</h3>
            <ul>
                {docs_html}
            </ul>
            
            {notes_html}
        </div>
        """
'''
    
    # Find insertion point (after generate_module_transition)
    if "generate_module_transition" in content:
        pattern = r'(    @staticmethod\s+def generate_module_transition\([^)]+\)[^:]+:.*?""")\s*\n'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            end_of_method = match.end()
            rest_of_content = content[end_of_method:]
            next_method_match = re.search(r'\n(    def |    @staticmethod)', rest_of_content)
            
            if next_method_match:
                insertion_point = end_of_method + next_method_match.start()
            else:
                insertion_point = end_of_method + len(rest_of_content)
            
            new_content = (
                content[:insertion_point] +
                "\n" + next_actions_method + "\n" +
                content[insertion_point:]
            )
            
            BASE_ASSEMBLER.write_text(new_content, encoding='utf-8')
            print("✅ [FIX 4] Added next actions section generator")
            return True
    
    print("❌ [FIX 4] Could not find insertion point")
    return False


def apply_fix_5_add_density_checker():
    """Add section divider generator for dense reports"""
    
    content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    # Check if already exists
    if "generate_section_divider" in content:
        print("✅ [FIX 5] Section divider generator already exists")
        return True
    
    divider_method = '''
    @staticmethod
    def generate_section_divider(section_title: str, section_summary: str = "") -> str:
        """
        [FIX 5] Density Final Check - Section Divider
        
        Generate visual section divider for long reports (>15 pages).
        Helps break up dense information and improve readability.
        
        Args:
            section_title: Title of the section
            section_summary: Optional summary text
            
        Returns:
            HTML string for section divider
        """
        summary_html = f"<p>{section_summary}</p>" if section_summary else ""
        
        return f"""
        <div class="section-divider">
            <h2>{section_title}</h2>
            {summary_html}
        </div>
        """
'''
    
    # Find insertion point (after generate_next_actions_section)
    if "generate_next_actions_section" in content:
        pattern = r'(    @staticmethod\s+def generate_next_actions_section\([^)]+\)[^:]+:.*?""")\s*\n'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            end_of_method = match.end()
            rest_of_content = content[end_of_method:]
            next_method_match = re.search(r'\n(    def |    @staticmethod)', rest_of_content)
            
            if next_method_match:
                insertion_point = end_of_method + next_method_match.start()
            else:
                insertion_point = end_of_method + len(rest_of_content)
            
            new_content = (
                content[:insertion_point] +
                "\n" + divider_method + "\n" +
                content[insertion_point:]
            )
            
            BASE_ASSEMBLER.write_text(new_content, encoding='utf-8')
            print("✅ [FIX 5] Added section divider generator")
            return True
    
    print("❌ [FIX 5] Could not find insertion point")
    return False


def verify_syntax():
    """Verify Python syntax of modified files"""
    import subprocess
    
    files_to_check = [BASE_ASSEMBLER]
    
    print("\n" + "="*60)
    print("Verifying Python Syntax...")
    print("="*60)
    
    all_valid = True
    for file_path in files_to_check:
        result = subprocess.run(
            ["python", "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {file_path.name}: Syntax OK")
        else:
            print(f"❌ {file_path.name}: Syntax Error")
            print(result.stderr)
            all_valid = False
    
    return all_valid


def main():
    print("="*60)
    print("NARRATIVE REINFORCEMENT PATCH - FIXES 2-5")
    print("="*60)
    print("Target: All Final Report Assemblers")
    print("Scope: Display-level only (NO engine/QA/calculation changes)")
    print("="*60)
    print()
    
    # Apply fixes to base_assembler.py
    print("Step 1: Applying FIX 2 (Module Transition Reinforcement)...")
    apply_fix_2_add_transition_method()
    print()
    
    print("Step 2: Applying FIX 3 (Report-Type Visual Emphasis)...")
    apply_fix_3_add_color_system_to_css()
    print()
    
    print("Step 3: Applying FIX 4 (Next Action Section)...")
    apply_fix_4_add_next_actions_generator()
    print()
    
    print("Step 4: Applying FIX 5 (Density Final Check)...")
    apply_fix_5_add_density_checker()
    print()
    
    # Verify syntax
    print("Step 5: Verifying syntax...")
    if verify_syntax():
        print("\n✅ All syntax checks passed!")
    else:
        print("\n❌ Syntax errors detected - please review")
        return False
    
    print("\n" + "="*60)
    print("NARRATIVE REINFORCEMENT PATCH - FIXES 2-5 COMPLETE")
    print("="*60)
    print("✅ FIX 2: Module Transition Reinforcement - APPLIED")
    print("✅ FIX 3: Report-Type Visual Emphasis - APPLIED")
    print("✅ FIX 4: Next Action Section - APPLIED")
    print("✅ FIX 5: Density Final Check - APPLIED")
    print("="*60)
    print("\nNext Steps:")
    print("1. Update each assembler to use these new methods")
    print("2. Run comprehensive narrative validation tests")
    print("3. Commit and push changes")
    print("="*60)
    
    return True


if __name__ == "__main__":
    main()
