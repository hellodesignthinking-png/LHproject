#!/usr/bin/env python3
"""
Apply Narrative Reinforcement Methods to All 6 Assemblers
=========================================================

This script updates each assembler to:
1. Use generate_module_transition() between modules
2. Apply report-type color classes to HTML body
3. Add generate_next_actions_section() at end of report
4. Use generate_section_divider() for long reports

CRITICAL: Display-level only, NO engine/QA/calculation changes
"""

import re
from pathlib import Path


ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")

# Report type to color class mapping
REPORT_COLOR_CLASSES = {
    "landowner_summary": "report-color-landowner",
    "lh_technical": "report-color-lh_technical",
    "quick_check": "report-color-quick",
    "financial_feasibility": "report-color-financial",
    "all_in_one": "report-color-all",
    "executive_summary": "report-color-executive"
}


def update_landowner_summary():
    """Update landowner_summary.py with narrative methods"""
    
    file_path = ASSEMBLER_DIR / "landowner_summary.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already updated
    if "generate_module_transition" in content:
        print("✅ landowner_summary.py already has narrative methods")
        return True
    
    # Add module transitions in assemble() method
    # Find: transition_m2_m5 = self.narrative.transitions("M2", "M5")
    old_transition_m2_m5 = 'transition_m2_m5 = self.narrative.transitions("M2", "M5")'
    new_transition_m2_m5 = '''transition_m2_m5 = self.generate_module_transition("M2", "M5", self.report_type)'''
    
    old_transition_m5_m6 = 'transition_m5_m6 = self.narrative.transitions("M5", "M6")'
    new_transition_m5_m6 = '''transition_m5_m6 = self.generate_module_transition("M5", "M6", self.report_type)'''
    
    if old_transition_m2_m5 in content:
        content = content.replace(old_transition_m2_m5, new_transition_m2_m5)
        content = content.replace(old_transition_m5_m6, new_transition_m5_m6)
    
    # Add next actions section before decision_block in sections list
    # Find sections list and add next_actions
    pattern = r'(decision_block = self\.generate_decision_block\([^)]+\))'
    replacement = r'\1\n        \n        # [FIX 4] Generate Next Actions Section\n        next_actions = self.generate_next_actions_section(modules_data, self.report_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add next_actions to sections list (before decision_block)
    content = re.sub(
        r'(sections = \[.*?)(decision_block,)',
        r'\1next_actions,\n            \2',
        content,
        flags=re.DOTALL
    )
    
    # Add color class to HTML body wrapper (if it exists)
    pattern = r'<body class="final-report">'
    replacement = f'<body class="final-report {REPORT_COLOR_CLASSES["landowner_summary"]}">'
    content = content.replace(pattern, replacement)
    
    file_path.write_text(content, encoding='utf-8')
    print("✅ Updated landowner_summary.py with narrative methods")
    return True


def update_lh_technical():
    """Update lh_technical.py with narrative methods"""
    
    file_path = ASSEMBLER_DIR / "lh_technical.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already updated
    if "generate_module_transition" in content:
        print("✅ lh_technical.py already has narrative methods")
        return True
    
    # Find where transitions are used and replace
    # LH Technical uses M3, M4, M6
    patterns_to_replace = [
        (r'transition_m3_m4 = self\.narrative\.transitions\("M3", "M4"\)',
         'transition_m3_m4 = self.generate_module_transition("M3", "M4", self.report_type)'),
        (r'transition_m4_m6 = self\.narrative\.transitions\("M4", "M6"\)',
         'transition_m4_m6 = self.generate_module_transition("M4", "M6", self.report_type)'),
    ]
    
    for old, new in patterns_to_replace:
        content = re.sub(old, new, content)
    
    # Add next actions section
    pattern = r'(decision_block = self\.generate_decision_block\([^)]+\))'
    replacement = r'\1\n        \n        # [FIX 4] Generate Next Actions Section\n        next_actions = self.generate_next_actions_section(modules_data, self.report_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add to sections list
    content = re.sub(
        r'(sections = \[.*?)(decision_block,)',
        r'\1next_actions,\n            \2',
        content,
        flags=re.DOTALL
    )
    
    # Add color class
    pattern = r'<body class="final-report">'
    replacement = f'<body class="final-report {REPORT_COLOR_CLASSES["lh_technical"]}">'
    content = content.replace(pattern, replacement)
    
    file_path.write_text(content, encoding='utf-8')
    print("✅ Updated lh_technical.py with narrative methods")
    return True


def update_quick_check():
    """Update quick_check.py with narrative methods"""
    
    file_path = ASSEMBLER_DIR / "quick_check.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already updated
    if "generate_next_actions_section" in content:
        print("✅ quick_check.py already has narrative methods")
        return True
    
    # Quick check uses M5, M6 - add transition
    pattern = r'(m6_html = self\.sanitize_module_html\(m6_html_raw, "M6"\))'
    replacement = r'\1\n        \n        # [FIX 2] Generate module transition\n        transition_m5_m6 = self.generate_module_transition("M5", "M6", self.report_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add next actions section
    pattern = r'(decision_block = self\.generate_decision_block\([^)]+\))'
    replacement = r'\1\n        \n        # [FIX 4] Generate Next Actions Section\n        next_actions = self.generate_next_actions_section(modules_data, self.report_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add to sections list (insert transition_m5_m6 and next_actions)
    # First add transition after m5_html
    content = re.sub(
        r'(sections = \[.*?m5_html,)',
        r'\1\n            transition_m5_m6,',
        content,
        flags=re.DOTALL
    )
    
    # Then add next_actions before decision_block
    content = re.sub(
        r'(sections = \[.*?)(decision_block,)',
        r'\1next_actions,\n            \2',
        content,
        flags=re.DOTALL
    )
    
    # Add color class
    pattern = r'<body class="final-report">'
    replacement = f'<body class="final-report {REPORT_COLOR_CLASSES["quick_check"]}">'
    content = content.replace(pattern, replacement)
    
    file_path.write_text(content, encoding='utf-8')
    print("✅ Updated quick_check.py with narrative methods")
    return True


def update_financial_feasibility():
    """Update financial_feasibility.py with narrative methods"""
    
    file_path = ASSEMBLER_DIR / "financial_feasibility.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already updated
    if "generate_module_transition" in content:
        print("✅ financial_feasibility.py already has narrative methods")
        return True
    
    # Financial feasibility uses M2, M4, M5
    patterns_to_replace = [
        (r'transition_m2_m4 = self\.narrative\.transitions\("M2", "M4"\)',
         'transition_m2_m4 = self.generate_module_transition("M2", "M4", self.report_type)'),
        (r'transition_m4_m5 = self\.narrative\.transitions\("M4", "M5"\)',
         'transition_m4_m5 = self.generate_module_transition("M4", "M5", self.report_type)'),
    ]
    
    for old, new in patterns_to_replace:
        content = re.sub(old, new, content)
    
    # Add next actions section
    pattern = r'(decision_block = self\.generate_decision_block\([^)]+\))'
    replacement = r'\1\n        \n        # [FIX 4] Generate Next Actions Section\n        next_actions = self.generate_next_actions_section(modules_data, self.report_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add to sections list
    content = re.sub(
        r'(sections = \[.*?)(decision_block,)',
        r'\1next_actions,\n            \2',
        content,
        flags=re.DOTALL
    )
    
    # Add color class
    pattern = r'<body class="final-report">'
    replacement = f'<body class="final-report {REPORT_COLOR_CLASSES["financial_feasibility"]}">'
    content = content.replace(pattern, replacement)
    
    file_path.write_text(content, encoding='utf-8')
    print("✅ Updated financial_feasibility.py with narrative methods")
    return True


def update_all_in_one():
    """Update all_in_one.py with narrative methods"""
    
    file_path = ASSEMBLER_DIR / "all_in_one.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already updated
    if "generate_module_transition" in content:
        print("✅ all_in_one.py already has narrative methods")
        return True
    
    # All-in-one uses M2, M3, M4, M5, M6 - lots of transitions
    patterns_to_replace = [
        (r'transition_m2_m3 = self\.narrative\.transitions\("M2", "M3"\)',
         'transition_m2_m3 = self.generate_module_transition("M2", "M3", self.report_type)'),
        (r'transition_m3_m4 = self\.narrative\.transitions\("M3", "M4"\)',
         'transition_m3_m4 = self.generate_module_transition("M3", "M4", self.report_type)'),
        (r'transition_m4_m5 = self\.narrative\.transitions\("M4", "M5"\)',
         'transition_m4_m5 = self.generate_module_transition("M4", "M5", self.report_type)'),
        (r'transition_m5_m6 = self\.narrative\.transitions\("M5", "M6"\)',
         'transition_m5_m6 = self.generate_module_transition("M5", "M6", self.report_type)'),
    ]
    
    for old, new in patterns_to_replace:
        content = re.sub(old, new, content)
    
    # [FIX 5] Add section dividers for this dense report
    # After M2, M4 modules
    pattern = r'(m2_html,\n\s+transition_m2_m3,)'
    replacement = r'\1\n            self.generate_section_divider("주택 유형 및 사업 규모 검토", "토지 평가를 바탕으로 최적의 주택 유형과 사업 규모를 결정합니다."),'
    content = re.sub(pattern, replacement, content)
    
    pattern = r'(m4_html,\n\s+transition_m4_m5,)'
    replacement = r'\1\n            self.generate_section_divider("사업성 및 LH 심사 분석", "사업 규모를 바탕으로 재무 타당성과 LH 승인 가능성을 평가합니다."),'
    content = re.sub(pattern, replacement, content)
    
    # Add next actions section
    pattern = r'(decision_block = self\.generate_decision_block\([^)]+\))'
    replacement = r'\1\n        \n        # [FIX 4] Generate Next Actions Section\n        next_actions = self.generate_next_actions_section(modules_data, self.report_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add to sections list
    content = re.sub(
        r'(sections = \[.*?)(decision_block,)',
        r'\1next_actions,\n            \2',
        content,
        flags=re.DOTALL
    )
    
    # Add color class + dense-report class
    pattern = r'<body class="final-report">'
    replacement = f'<body class="final-report dense-report {REPORT_COLOR_CLASSES["all_in_one"]}">'
    content = content.replace(pattern, replacement)
    
    file_path.write_text(content, encoding='utf-8')
    print("✅ Updated all_in_one.py with narrative methods (includes section dividers)")
    return True


def update_executive_summary():
    """Update executive_summary.py with narrative methods"""
    
    file_path = ASSEMBLER_DIR / "executive_summary.py"
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already updated
    if "generate_module_transition" in content:
        print("✅ executive_summary.py already has narrative methods")
        return True
    
    # Executive summary uses M2, M5, M6
    patterns_to_replace = [
        (r'transition_m2_m5 = self\.narrative\.transitions\("M2", "M5"\)',
         'transition_m2_m5 = self.generate_module_transition("M2", "M5", self.report_type)'),
        (r'transition_m5_m6 = self\.narrative\.transitions\("M5", "M6"\)',
         'transition_m5_m6 = self.generate_module_transition("M5", "M6", self.report_type)'),
    ]
    
    for old, new in patterns_to_replace:
        content = re.sub(old, new, content)
    
    # Add next actions section
    pattern = r'(decision_block = self\.generate_decision_block\([^)]+\))'
    replacement = r'\1\n        \n        # [FIX 4] Generate Next Actions Section\n        next_actions = self.generate_next_actions_section(modules_data, self.report_type)'
    content = re.sub(pattern, replacement, content)
    
    # Add to sections list
    content = re.sub(
        r'(sections = \[.*?)(decision_block,)',
        r'\1next_actions,\n            \2',
        content,
        flags=re.DOTALL
    )
    
    # Add color class + compact-report class
    pattern = r'<body class="final-report">'
    replacement = f'<body class="final-report compact-report {REPORT_COLOR_CLASSES["executive_summary"]}">'
    content = content.replace(pattern, replacement)
    
    file_path.write_text(content, encoding='utf-8')
    print("✅ Updated executive_summary.py with narrative methods")
    return True


def verify_syntax():
    """Verify Python syntax of all assemblers"""
    import subprocess
    
    assemblers = [
        "landowner_summary.py",
        "lh_technical.py",
        "quick_check.py",
        "financial_feasibility.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    print("\n" + "="*60)
    print("Verifying Python Syntax...")
    print("="*60)
    
    all_valid = True
    for assembler in assemblers:
        file_path = ASSEMBLER_DIR / assembler
        result = subprocess.run(
            ["python", "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {assembler}: Syntax OK")
        else:
            print(f"❌ {assembler}: Syntax Error")
            print(result.stderr)
            all_valid = False
    
    return all_valid


def main():
    print("="*60)
    print("APPLY NARRATIVE METHODS TO ALL 6 ASSEMBLERS")
    print("="*60)
    print("Updates:")
    print("- FIX 2: Module transitions")
    print("- FIX 3: Report-type color classes")
    print("- FIX 4: Next actions section")
    print("- FIX 5: Section dividers (for dense reports)")
    print("="*60)
    print()
    
    # Update all assemblers
    update_landowner_summary()
    update_lh_technical()
    update_quick_check()
    update_financial_feasibility()
    update_all_in_one()
    update_executive_summary()
    
    print()
    
    # Verify syntax
    if verify_syntax():
        print("\n✅ All assemblers updated and syntax verified!")
        print("\nNext step: Create and run comprehensive narrative validation test")
        return True
    else:
        print("\n❌ Syntax errors detected - please review")
        return False


if __name__ == "__main__":
    main()
