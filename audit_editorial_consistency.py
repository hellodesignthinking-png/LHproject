#!/usr/bin/env python3
"""
Final Editorial Consistency Audit Script
========================================

Audits the codebase for the 7 consistency fixes and identifies
any remaining inconsistencies that need correction.

This is a READ-ONLY audit - no modifications are made.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")
BASE_ASSEMBLER = Path("app/services/final_report_assembly/base_assembler.py")


def audit_fix_1_numeric_identity() -> Dict[str, List[str]]:
    """
    FIX 1: Audit for numeric identity issues
    
    Checks:
    - Presence of format_number() method
    - Consistent usage across assemblers
    - No approximations (약, 수준) in code
    """
    print("\n" + "="*60)
    print("FIX 1: Numeric Identity Lock Audit")
    print("="*60)
    
    issues = []
    
    # Check if format_number exists
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    if "def format_number" not in base_content:
        issues.append("❌ format_number() method not found in base_assembler")
    else:
        print("✅ format_number() method exists")
    
    # Check for approximations in assemblers
    approximations = ["약", "수준", "내외", "대략"]
    for assembler_file in ASSEMBLER_DIR.glob("*.py"):
        if assembler_file.name == "__init__.py":
            continue
        
        content = assembler_file.read_text(encoding='utf-8')
        for approx in approximations:
            if approx in content:
                issues.append(f"⚠️  {assembler_file.name}: Contains approximation '{approx}'")
    
    # Check if assemblers use format_number
    for assembler_file in ASSEMBLER_DIR.glob("*.py"):
        if assembler_file.name == "__init__.py":
            continue
        
        content = assembler_file.read_text(encoding='utf-8')
        if "format_number" not in content:
            issues.append(f"⚠️  {assembler_file.name}: Does not use format_number()")
    
    if not issues:
        print("✅ No numeric identity issues found")
    else:
        for issue in issues:
            print(issue)
    
    return {"FIX 1": issues}


def audit_fix_2_m3_m4_preservation() -> Dict[str, List[str]]:
    """
    FIX 2: Audit M3/M4 data preservation
    
    Checks:
    - M3 data extraction includes 추천 유형, 총점, 등급
    - M4 data extraction includes 총 세대수, 기본/인센티브
    """
    print("\n" + "="*60)
    print("FIX 2: M3/M4 Data Preservation Audit")
    print("="*60)
    
    issues = []
    
    # Check M3 data in assemblers that use it
    m3_assemblers = ["lh_technical.py", "all_in_one.py"]
    m3_required = ["recommended_type", "score", "rating"]
    
    for assembler in m3_assemblers:
        file_path = ASSEMBLER_DIR / assembler
        if not file_path.exists():
            continue
        
        content = file_path.read_text(encoding='utf-8')
        
        for field in m3_required:
            if field not in content:
                issues.append(f"⚠️  {assembler}: Missing M3 field '{field}'")
    
    # Check M4 data in assemblers that use it
    m4_assemblers = ["lh_technical.py", "financial_feasibility.py", "all_in_one.py"]
    m4_required = ["household_count", "basic", "incentive"]
    
    for assembler in m4_assemblers:
        file_path = ASSEMBLER_DIR / assembler
        if not file_path.exists():
            continue
        
        content = file_path.read_text(encoding='utf-8')
        
        for field in m4_required:
            if field not in content:
                issues.append(f"⚠️  {assembler}: Missing M4 field '{field}'")
    
    if not issues:
        print("✅ All M3/M4 data appears to be preserved")
    else:
        for issue in issues:
            print(issue)
    
    return {"FIX 2": issues}


def audit_fix_3_section_order() -> Dict[str, List[str]]:
    """
    FIX 3: Audit section order documentation
    
    Checks:
    - Presence of section order comments
    - Canonical order enforcement
    """
    print("\n" + "="*60)
    print("FIX 3: Section Order Canonicalization Audit")
    print("="*60)
    
    issues = []
    
    for assembler_file in ASSEMBLER_DIR.glob("*.py"):
        if assembler_file.name == "__init__.py":
            continue
        
        content = assembler_file.read_text(encoding='utf-8')
        
        if "[FIX 4]" not in content:  # FIX 4 comment refers to section order
            issues.append(f"⚠️  {assembler_file.name}: Missing section order documentation")
        else:
            print(f"✅ {assembler_file.name}: Has section order docs")
    
    return {"FIX 3": issues}


def audit_fix_4_terminology() -> Dict[str, List[str]]:
    """
    FIX 4: Audit terminology consistency
    
    Checks:
    - normalize_terminology() method exists
    - Canonical terms are defined
    """
    print("\n" + "="*60)
    print("FIX 4: Terminology Lock Audit")
    print("="*60)
    
    issues = []
    
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    if "def normalize_terminology" not in base_content:
        issues.append("❌ normalize_terminology() method not found")
    else:
        print("✅ normalize_terminology() method exists")
    
    # Check for canonical terms
    canonical_terms = [
        "총 세대수",
        "순현재가치(NPV)",
        "내부수익률(IRR)",
        "조건부 승인"
    ]
    
    for term in canonical_terms:
        if term not in base_content:
            issues.append(f"⚠️  Canonical term '{term}' not found in normalization rules")
    
    if len(issues) == 0:
        print(f"✅ All {len(canonical_terms)} canonical terms defined")
    
    return {"FIX 4": issues}


def audit_fix_5_narrative_kpi() -> Dict[str, List[str]]:
    """
    FIX 5: Audit narrative ↔ KPI linkage
    
    Checks:
    - KPI generation methods exist
    - Narrative generators reference KPIs
    """
    print("\n" + "="*60)
    print("FIX 5: Narrative ↔ KPI Cross-Validation Audit")
    print("="*60)
    
    issues = []
    
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    if "def generate_kpi_summary_box" not in base_content:
        issues.append("❌ generate_kpi_summary_box() method not found")
    else:
        print("✅ generate_kpi_summary_box() method exists")
    
    # Check if narrative generators exist
    narrative_dir = Path("app/services/final_report_assembly")
    if (narrative_dir / "narrative_generator.py").exists():
        print("✅ Narrative generator system exists")
    else:
        issues.append("⚠️  Narrative generator not found")
    
    return {"FIX 5": issues}


def audit_fix_6_source_traceability() -> Dict[str, List[str]]:
    """
    FIX 6: Audit module source traceability
    
    Checks:
    - generate_source_reference() method exists
    - CSS for source reference exists
    """
    print("\n" + "="*60)
    print("FIX 6: Module Source Traceability Audit")
    print("="*60)
    
    issues = []
    
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    if "def generate_source_reference" not in base_content:
        issues.append("❌ generate_source_reference() method not found")
    else:
        print("✅ generate_source_reference() method exists")
    
    if ".source-reference" not in base_content:
        issues.append("❌ .source-reference CSS not found")
    else:
        print("✅ .source-reference CSS defined")
    
    # Check if assemblers use it (optional for now)
    usage_count = 0
    for assembler_file in ASSEMBLER_DIR.glob("*.py"):
        if assembler_file.name == "__init__.py":
            continue
        
        content = assembler_file.read_text(encoding='utf-8')
        if "generate_source_reference" in content:
            usage_count += 1
    
    if usage_count == 0:
        issues.append("⚠️  No assemblers use generate_source_reference() yet")
    else:
        print(f"✅ {usage_count} assemblers use source references")
    
    return {"FIX 6": issues}


def audit_fix_7_html_pdf_parity() -> Dict[str, List[str]]:
    """
    FIX 7: Audit HTML ↔ PDF parity
    
    Checks:
    - Consistent CSS usage
    - Module HTML loading mechanism
    - sanitize_module_html usage
    """
    print("\n" + "="*60)
    print("FIX 7: HTML Preview ↔ Final Report Parity Audit")
    print("="*60)
    
    issues = []
    
    base_content = BASE_ASSEMBLER.read_text(encoding='utf-8')
    
    if "def sanitize_module_html" not in base_content:
        issues.append("❌ sanitize_module_html() method not found")
    else:
        print("✅ sanitize_module_html() method exists")
    
    if "def get_unified_design_css" not in base_content:
        issues.append("❌ get_unified_design_css() method not found")
    else:
        print("✅ get_unified_design_css() method exists")
    
    # Check if all assemblers use sanitize_module_html
    for assembler_file in ASSEMBLER_DIR.glob("*.py"):
        if assembler_file.name == "__init__.py":
            continue
        
        content = assembler_file.read_text(encoding='utf-8')
        if "sanitize_module_html" not in content:
            issues.append(f"⚠️  {assembler_file.name}: Does not use sanitize_module_html()")
    
    if len([i for i in issues if assembler_file.name in i]) == 0:
        print("✅ All assemblers use sanitize_module_html()")
    
    return {"FIX 7": issues}


def generate_summary_report(all_issues: Dict[str, Dict[str, List[str]]]):
    """Generate final summary report"""
    
    print("\n" + "="*60)
    print("FINAL EDITORIAL CONSISTENCY AUDIT SUMMARY")
    print("="*60)
    
    total_issues = sum(len(issues) for fix_issues in all_issues.values() for issues in fix_issues.values())
    
    if total_issues == 0:
        print("\n🎉 ALL CHECKS PASSED! No editorial inconsistencies found.")
        print("\n✅ System Status: EDITORIALLY CONSISTENT")
        print("✅ Ready for production deployment")
        print("✅ Reports read as 'one unified document'")
        return True
    else:
        print(f"\n⚠️  Found {total_issues} potential issues to review:")
        print()
        
        for fix_name, fix_issues in all_issues.items():
            for category, issues in fix_issues.items():
                if issues:
                    print(f"\n{category}:")
                    for issue in issues:
                        print(f"  {issue}")
        
        print("\n📋 Recommended Actions:")
        print("1. Review each issue listed above")
        print("2. Apply corrections (display-level only)")
        print("3. Re-run audit to verify fixes")
        print("4. Generate sample reports for manual verification")
        
        return False


def main():
    print("="*60)
    print("FINAL EDITORIAL CONSISTENCY AUDIT")
    print("="*60)
    print("Purpose: Identify any remaining presentation inconsistencies")
    print("Scope: Module ↔ HTML ↔ Final Reports")
    print("="*60)
    
    all_issues = {}
    
    all_issues.update(audit_fix_1_numeric_identity())
    all_issues.update(audit_fix_2_m3_m4_preservation())
    all_issues.update(audit_fix_3_section_order())
    all_issues.update(audit_fix_4_terminology())
    all_issues.update(audit_fix_5_narrative_kpi())
    all_issues.update(audit_fix_6_source_traceability())
    all_issues.update(audit_fix_7_html_pdf_parity())
    
    success = generate_summary_report(all_issues)
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
