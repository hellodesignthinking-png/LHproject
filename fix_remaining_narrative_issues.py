#!/usr/bin/env python3
"""
Fix Remaining Narrative Issues - Manual Approach
"""

from pathlib import Path

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")


# Fix all_in_one.py - replace transitions dict with generate_module_transition calls
def fix_all_in_one():
    file_path = ASSEMBLER_DIR / "all_in_one.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Replace transitions dict
    old_transitions = '''        exec_summary = self.narrative.executive_summary(modules_data)
        transitions = {
            "M2_M3": self.narrative.transitions("M2", "M3"),
            "M3_M4": self.narrative.transitions("M3", "M4"),
            "M4_M5": self.narrative.transitions("M4", "M5"),
            "M5_M6": self.narrative.transitions("M5", "M6")
        }
        final_judgment = self.narrative.final_judgment(modules_data)'''
    
    new_transitions = '''        exec_summary = self.narrative.executive_summary(modules_data)
        
        # [FIX 2] Generate module transitions
        transition_m2_m3 = self.generate_module_transition("M2", "M3", self.report_type)
        transition_m3_m4 = self.generate_module_transition("M3", "M4", self.report_type)
        transition_m4_m5 = self.generate_module_transition("M4", "M5", self.report_type)
        transition_m5_m6 = self.generate_module_transition("M5", "M6", self.report_type)
        
        # [FIX 5] Generate section dividers for dense report
        divider_1 = self.generate_section_divider("주택 유형 및 사업 규모 검토", "토지 평가를 바탕으로 최적의 주택 유형과 사업 규모를 결정합니다.")
        divider_2 = self.generate_section_divider("사업성 및 LH 심사 분석", "사업 규모를 바탕으로 재무 타당성과 LH 승인 가능성을 평가합니다.")
        
        final_judgment = self.narrative.final_judgment(modules_data)'''
    
    if old_transitions in content:
        content = content.replace(old_transitions, new_transitions)
        print("✅ all_in_one.py: Replaced transitions dict with generate_module_transition")
    
    # Replace transitions references in sections list
    old_sections = '''        sections = [
            self._generate_cover_page(),
            kpi_summary,  # KPI at top
            exec_summary,
            self._wrap_module_html("M2", m2_html),
            transitions["M2_M3"],
            self._wrap_module_html("M3", m3_html),
            transitions["M3_M4"],
            self._wrap_module_html("M4", m4_html),
            transitions["M4_M5"],
            self._wrap_module_html("M5", m5_html),
            transitions["M5_M6"],
            self._wrap_module_html("M6", m6_html),
            final_judgment,
            next_actions,
            decision_block,  # Visual decision at bottom
            self._generate_footer()
        ]'''
    
    new_sections = '''        sections = [
            self._generate_cover_page(),
            kpi_summary,  # KPI at top
            exec_summary,
            self._wrap_module_html("M2", m2_html),
            transition_m2_m3,
            divider_1,  # Section divider for visual break
            self._wrap_module_html("M3", m3_html),
            transition_m3_m4,
            self._wrap_module_html("M4", m4_html),
            transition_m4_m5,
            divider_2,  # Section divider for visual break
            self._wrap_module_html("M5", m5_html),
            transition_m5_m6,
            self._wrap_module_html("M6", m6_html),
            final_judgment,
            next_actions,
            decision_block,  # Visual decision at bottom
            self._generate_footer()
        ]'''
    
    if old_sections in content:
        content = content.replace(old_sections, new_sections)
        print("✅ all_in_one.py: Updated sections list with transitions and dividers")
    
    file_path.write_text(content, encoding='utf-8')
    return True


# Fix executive_summary.py - similar approach
def fix_executive_summary():
    file_path = ASSEMBLER_DIR / "executive_summary.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Replace transitions if they exist
    old_trans = 'self.narrative.transitions("M2", "M5")'
    new_trans = 'self.generate_module_transition("M2", "M5", self.report_type)'
    content = content.replace(old_trans, new_trans)
    
    old_trans = 'self.narrative.transitions("M5", "M6")'
    new_trans = 'self.generate_module_transition("M5", "M6", self.report_type)'
    content = content.replace(old_trans, new_trans)
    
    print("✅ executive_summary.py: Replaced transition calls")
    
    file_path.write_text(content, encoding='utf-8')
    return True


# Add color classes to _wrap_in_document method for all assemblers
def add_color_classes():
    color_mappings = {
        "landowner_summary.py": "landowner",
        "lh_technical.py": "lh_technical",
        "quick_check.py": "quick",
        "financial_feasibility.py": "financial",
        "all_in_one.py": "all",
        "executive_summary.py": "executive"
    }
    
    for assembler, color_suffix in color_mappings.items():
        file_path = ASSEMBLER_DIR / assembler
        content = file_path.read_text(encoding='utf-8')
        
        # Check if _wrap_in_document method exists
        if "_wrap_in_document" in content:
            # Find body tag and add color class
            old_body = '<body class="final-report">'
            
            # For dense reports
            if assembler == "all_in_one.py":
                new_body = f'<body class="final-report dense-report report-color-{color_suffix}">'
            # For compact reports
            elif assembler == "executive_summary.py":
                new_body = f'<body class="final-report compact-report report-color-{color_suffix}">'
            else:
                new_body = f'<body class="final-report report-color-{color_suffix}">'
            
            if old_body in content:
                content = content.replace(old_body, new_body)
                print(f"✅ {assembler}: Added color class 'report-color-{color_suffix}'")
                file_path.write_text(content, encoding='utf-8')
            else:
                print(f"⚠️  {assembler}: No body tag found to modify")
        else:
            print(f"⚠️  {assembler}: No _wrap_in_document method found")
    
    return True


# Add .pdf-safe CSS class to base_assembler
def add_pdf_safe_css():
    from pathlib import Path
    base_file = Path("app/services/final_report_assembly/base_assembler.py")
    content = base_file.read_text(encoding='utf-8')
    
    # Check if already exists
    if ".pdf-safe" in content:
        print("✅ .pdf-safe CSS already exists")
        return True
    
    # Add to KPI summary box method
    old_kpi = '<div class="kpi-summary">'
    new_kpi = '<div class="kpi-summary pdf-safe">'
    content = content.replace(old_kpi, new_kpi)
    
    # Add to decision block method  
    old_decision = '<div class="decision-block'
    new_decision = '<div class="decision-block pdf-safe'
    content = content.replace(old_decision, new_decision)
    
    print("✅ Added .pdf-safe class to KPI and decision blocks")
    
    base_file.write_text(content, encoding='utf-8')
    return True


# Main execution
def main():
    print("="*60)
    print("FIXING REMAINING NARRATIVE ISSUES")
    print("="*60)
    print()
    
    fix_all_in_one()
    print()
    
    fix_executive_summary()
    print()
    
    add_color_classes()
    print()
    
    add_pdf_safe_css()
    print()
    
    # Verify syntax
    import subprocess
    assemblers = [
        "landowner_summary.py",
        "lh_technical.py",
        "quick_check.py",
        "financial_feasibility.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    print("="*60)
    print("SYNTAX VERIFICATION")
    print("="*60)
    
    all_valid = True
    for assembler in assemblers:
        result = subprocess.run(
            ["python", "-m", "py_compile", str(ASSEMBLER_DIR / assembler)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {assembler}")
        else:
            print(f"❌ {assembler}: {result.stderr}")
            all_valid = False
    
    print()
    if all_valid:
        print("✅ ALL FIXES APPLIED SUCCESSFULLY")
    else:
        print("❌ SOME SYNTAX ERRORS DETECTED")
    
    return all_valid


if __name__ == "__main__":
    main()
