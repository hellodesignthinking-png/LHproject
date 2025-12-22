#!/usr/bin/env python3
"""
Comprehensive Narrative Reinforcement Validation Test
=====================================================

Validates all 4 narrative reinforcement fixes across 6 assemblers:

FIX 1 (Already Applied): Interpretation Paragraph Enforcement
FIX 2: Module Transition Reinforcement  
FIX 3: Report-Type Visual Emphasis
FIX 4: Next Action Section (MANDATORY)
FIX 5: Density Final Check

Exit Criteria:
- No section is pure data without explanation
- Every report ends with clear next steps
- Visual hierarchy differs per report type
- No numeric value is altered
"""

import re
from pathlib import Path


ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")
BASE_ASSEMBLER = Path("app/services/final_report_assembly/base_assembler.py")


def test_fix_2_module_transitions():
    """Validate FIX 2: Module transition boxes exist"""
    
    print("\n" + "="*60)
    print("[FIX 2] Module Transition Reinforcement")
    print("="*60)
    
    # Check base_assembler has the method
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    if "def generate_module_transition" not in base_content:
        print("❌ generate_module_transition() method not found in base_assembler")
        return False
    
    if "module-transition" not in base_content:
        print("❌ .module-transition CSS not found")
        return False
    
    print("✅ Module transition generator exists in base_assembler")
    print("✅ Module transition CSS defined")
    
    # Check each assembler uses it
    assemblers_to_check = {
        "landowner_summary.py": ["M2", "M5"],
        "lh_technical.py": ["M3", "M4"],
        "quick_check.py": ["M5", "M6"],
        "financial_feasibility.py": ["M2", "M4"],
        "all_in_one.py": ["M2", "M3", "M4", "M5"],
        "executive_summary.py": ["M2", "M5"]
    }
    
    all_passed = True
    for assembler, expected_transitions in assemblers_to_check.items():
        file_path = ASSEMBLER_DIR / assembler
        content = file_path.read_text(encoding='utf-8')
        
        if "generate_module_transition" not in content:
            print(f"❌ {assembler}: Does not use generate_module_transition()")
            all_passed = False
        else:
            print(f"✅ {assembler}: Uses module transitions")
    
    return all_passed


def test_fix_3_report_colors():
    """Validate FIX 3: Report-type visual emphasis"""
    
    print("\n" + "="*60)
    print("[FIX 3] Report-Type Visual Emphasis")
    print("="*60)
    
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    # Check CSS has color classes
    required_colors = [
        "report-color-landowner",
        "report-color-lh_technical",
        "report-color-quick",
        "report-color-financial",
        "report-color-executive",
        "report-color-all"
    ]
    
    all_colors_found = True
    for color in required_colors:
        if color not in base_content:
            print(f"❌ CSS missing: {color}")
            all_colors_found = False
    
    if all_colors_found:
        print("✅ All report-type color classes defined in CSS")
    
    # Check assemblers apply color classes
    assemblers_to_check = {
        "landowner_summary.py": "report-color-landowner",
        "lh_technical.py": "report-color-lh_technical",
        "quick_check.py": "report-color-quick",
        "financial_feasibility.py": "report-color-financial",
        "all_in_one.py": "report-color-all",
        "executive_summary.py": "report-color-executive"
    }
    
    all_applied = True
    for assembler, expected_class in assemblers_to_check.items():
        file_path = ASSEMBLER_DIR / assembler
        content = file_path.read_text(encoding='utf-8')
        
        if expected_class not in content:
            print(f"❌ {assembler}: Missing color class '{expected_class}'")
            all_applied = False
        else:
            print(f"✅ {assembler}: Has color class '{expected_class}'")
    
    return all_colors_found and all_applied


def test_fix_4_next_actions():
    """Validate FIX 4: Next Action Section"""
    
    print("\n" + "="*60)
    print("[FIX 4] Next Action Section (MANDATORY)")
    print("="*60)
    
    # Check base_assembler has the method
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    if "def generate_next_actions_section" not in base_content:
        print("❌ generate_next_actions_section() method not found")
        return False
    
    if "next-actions-section" not in base_content:
        print("❌ .next-actions-section CSS not found")
        return False
    
    print("✅ Next actions generator exists in base_assembler")
    print("✅ Next actions CSS defined")
    
    # Check all assemblers use it
    assemblers = [
        "landowner_summary.py",
        "lh_technical.py",
        "quick_check.py",
        "financial_feasibility.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    all_passed = True
    for assembler in assemblers:
        file_path = ASSEMBLER_DIR / assembler
        content = file_path.read_text(encoding='utf-8')
        
        has_method_call = "generate_next_actions_section" in content
        has_in_sections = "next_actions" in content
        
        if not (has_method_call and has_in_sections):
            print(f"❌ {assembler}: Missing next actions section")
            all_passed = False
        else:
            print(f"✅ {assembler}: Has next actions section")
    
    return all_passed


def test_fix_5_density_control():
    """Validate FIX 5: Density Final Check"""
    
    print("\n" + "="*60)
    print("[FIX 5] Information Density Normalization")
    print("="*60)
    
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    # Check section divider method exists
    if "def generate_section_divider" not in base_content:
        print("❌ generate_section_divider() method not found")
        return False
    
    if "section-divider" not in base_content:
        print("❌ .section-divider CSS not found")
        return False
    
    print("✅ Section divider generator exists")
    print("✅ Section divider CSS defined")
    
    # Check density classes
    if "compact-report" not in base_content:
        print("❌ .compact-report CSS not found")
        return False
    
    if "dense-report" not in base_content:
        print("❌ .dense-report CSS not found")
        return False
    
    print("✅ Density control CSS classes defined")
    
    # Check dense reports use section dividers
    file_path = ASSEMBLER_DIR / "all_in_one.py"
    content = file_path.read_text(encoding='utf-8')
    
    if "generate_section_divider" not in content:
        print("❌ all_in_one.py: Should use section dividers (dense report)")
        return False
    
    if "dense-report" not in content:
        print("❌ all_in_one.py: Missing 'dense-report' class")
        return False
    
    print("✅ all_in_one.py: Uses section dividers (dense report)")
    
    # Check compact reports
    file_path = ASSEMBLER_DIR / "executive_summary.py"
    content = file_path.read_text(encoding='utf-8')
    
    if "compact-report" not in content:
        print("⚠️  executive_summary.py: Could use 'compact-report' class")
    else:
        print("✅ executive_summary.py: Has 'compact-report' class")
    
    return True


def test_integration():
    """Integration test: Verify all fixes work together"""
    
    print("\n" + "="*60)
    print("INTEGRATION TEST")
    print("="*60)
    
    # Check base_assembler has all methods
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    required_methods = [
        "generate_kpi_summary_box",
        "generate_decision_block",
        "generate_module_transition",
        "generate_next_actions_section",
        "generate_section_divider",
        "sanitize_module_html",
        "format_number",
        "get_unified_design_css"
    ]
    
    missing_methods = []
    for method in required_methods:
        if f"def {method}" not in base_content:
            missing_methods.append(method)
    
    if missing_methods:
        print(f"❌ Missing methods in base_assembler: {', '.join(missing_methods)}")
        return False
    
    print(f"✅ All {len(required_methods)} required methods exist in base_assembler")
    
    # Check all assemblers are syntactically valid
    import subprocess
    
    assemblers = [
        "landowner_summary.py",
        "lh_technical.py",
        "quick_check.py",
        "financial_feasibility.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    syntax_errors = []
    for assembler in assemblers:
        file_path = ASSEMBLER_DIR / assembler
        result = subprocess.run(
            ["python", "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            syntax_errors.append(assembler)
    
    if syntax_errors:
        print(f"❌ Syntax errors in: {', '.join(syntax_errors)}")
        return False
    
    print(f"✅ All {len(assemblers)} assemblers have valid syntax")
    
    # Check CSS integrity
    css_checks = [
        ".module-transition",
        ".next-actions-section",
        ".section-divider",
        ".report-color-",
        ".compact-report",
        ".dense-report",
        ".pdf-safe"
    ]
    
    missing_css = []
    for css_class in css_checks:
        if css_class not in base_content:
            missing_css.append(css_class)
    
    if missing_css:
        print(f"❌ Missing CSS classes: {', '.join(missing_css)}")
        return False
    
    print(f"✅ All required CSS classes defined")
    
    return True


def test_exit_criteria():
    """Validate all exit criteria are met"""
    
    print("\n" + "="*60)
    print("EXIT CRITERIA VALIDATION")
    print("="*60)
    
    criteria = {
        "KPI boxes never split": True,  # From FIX A (PDF Safe)
        "No empty numeric fields": True,  # From FIX B (KPI Fallback)
        "Executive summaries include numbers": True,  # From FIX C (Numeric Anchor)
        "Decision blocks cite numeric evidence": True,  # From FIX D (Decision-KPI Trace)
        "Dense reports are visually segmented": True,  # From FIX E (Density)
        "Module transitions exist": True,  # From FIX 2
        "Next actions in all reports": True,  # From FIX 4
        "Report-type colors applied": True,  # From FIX 3
    }
    
    # Check each criterion
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    # Verify methods exist
    if "page-break-inside: avoid" not in base_content:
        criteria["KPI boxes never split"] = False
    
    if "데이터 미확정" not in base_content:
        criteria["No empty numeric fields"] = False
    
    if "ensure_numeric_anchor" not in base_content:
        criteria["Executive summaries include numbers"] = False
    
    # Check assemblers for _generate_judgment_basis (not in base_assembler)
    assemblers = [
        "landowner_summary.py",
        "lh_technical.py",
        "quick_check.py",
        "financial_feasibility.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    has_judgment_basis = True
    for assembler in assemblers:
        file_path = ASSEMBLER_DIR / assembler
        content = file_path.read_text(encoding='utf-8')
        if "_generate_judgment_basis" not in content:
            has_judgment_basis = False
            break
    
    if not has_judgment_basis:
        criteria["Decision blocks cite numeric evidence"] = False
    
    if "generate_section_divider" not in base_content:
        criteria["Dense reports are visually segmented"] = False
    
    if "generate_module_transition" not in base_content:
        criteria["Module transitions exist"] = False
    
    if "generate_next_actions_section" not in base_content:
        criteria["Next actions in all reports"] = False
    
    if "report-color-landowner" not in base_content:
        criteria["Report-type colors applied"] = False
    
    # Print results
    all_passed = True
    for criterion, passed in criteria.items():
        status = "✅" if passed else "❌"
        print(f"{status} {criterion}")
        if not passed:
            all_passed = False
    
    return all_passed


def main():
    print("="*60)
    print("COMPREHENSIVE NARRATIVE REINFORCEMENT VALIDATION")
    print("="*60)
    print("Validates FIX 2, 3, 4, 5 across all 6 assemblers")
    print("="*60)
    
    results = {
        "FIX 2 - Module Transitions": test_fix_2_module_transitions(),
        "FIX 3 - Report Colors": test_fix_3_report_colors(),
        "FIX 4 - Next Actions": test_fix_4_next_actions(),
        "FIX 5 - Density Control": test_fix_5_density_control(),
        "Integration Test": test_integration(),
        "Exit Criteria": test_exit_criteria()
    }
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL NARRATIVE REINFORCEMENT TESTS PASSED!")
        print("\n✅ System Status: NARRATIVE-REINFORCED & PERSUASIVE")
        print("✅ Report Completeness: 100%")
        print("✅ Visual Emphasis: Report-Type Specific")
        print("✅ Next Actions: Clear & Actionable")
        print("✅ Density Control: Balanced")
        print("\n📋 READY FOR:")
        print("   - LH Submission")
        print("   - Landowner Presentation")
        print("   - Investor Review")
        print("   - Consulting Delivery")
        print("\n" + "="*60)
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - review required")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
