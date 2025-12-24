#!/usr/bin/env python3
"""
Remove OLD QA Validator from All Assemblers
============================================

OLD validator checks HTML for N/A and sets FAIL status,
but still returns the HTML (doesn't block generation).

Phase 3.10 Hard-Fail already blocks generation at the
extraction/binding stage, so OLD validator is redundant.

This script removes OLD validator calls from all assemblers.
"""

import re
from pathlib import Path

def remove_old_validator(file_path: Path) -> bool:
    """Remove OLD QA validator from assembler"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if OLD validator is used
    if "FinalReportQAValidator.validate_kpi_completeness" not in content:
        print(f"  ✅ {file_path.name}: No OLD validator found")
        return False
    
    original_content = content
    
    # Remove import
    content = re.sub(
        r'from app\.services\.final_report_assembly\.qa_validator import FinalReportQAValidator\s*\n',
        '',
        content
    )
    
    # Remove validation call and error handling
    # Pattern: kpi_valid, na_kpis = FinalReportQAValidator.validate_kpi_completeness(...)
    #          if not kpi_valid: ...
    
    # Find and remove the validation block
    pattern = r'''
        \s*#\s*\[P0 FIX\].*KPI completeness.*\n
        \s*from\s+app\.services\.final_report_assembly\.qa_validator\s+import\s+FinalReportQAValidator\s*\n
        \s*\n
        \s*kpi_valid,\s*na_kpis\s*=\s*FinalReportQAValidator\.validate_kpi_completeness\([^)]+\)\s*\n
        \s*\n
        \s*if\s+not\s+kpi_valid:\s*\n
        \s*logger\.error\([^)]+\)\s*\n
        \s*qa_result\["status"\]\s*=\s*"FAIL"\s*\n
        \s*qa_result\["errors"\]\.append\([^)]+\)\s*\n
    '''
    
    content = re.sub(pattern, '\n        # [vLAST] OLD validator removed - Phase 3.10 Hard-Fail handles validation\n', content, flags=re.VERBOSE)
    
    # If regex didn't work, try simpler approach
    if "FinalReportQAValidator.validate_kpi_completeness" in content:
        # Find the block manually
        lines = content.split('\n')
        new_lines = []
        skip_until_blank = False
        
        for i, line in enumerate(lines):
            if "FinalReportQAValidator.validate_kpi_completeness" in line:
                skip_until_blank = True
                new_lines.append('        # [vLAST] OLD validator removed - Phase 3.10 Hard-Fail handles validation')
                continue
            
            if skip_until_blank:
                if 'if not kpi_valid:' in line:
                    continue
                if 'KPI validation FAILED' in line:
                    continue
                if 'qa_result["status"] = "FAIL"' in line:
                    continue
                if 'qa_result["errors"].append' in line and 'Core KPIs contain N/A' in line:
                    skip_until_blank = False
                    continue
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Remove OLD validator import if still present
    content = re.sub(
        r'from app\.services\.final_report_assembly\.qa_validator import FinalReportQAValidator\s*',
        '',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {file_path.name}: OLD validator removed")
        return True
    else:
        print(f"  ⚠️  {file_path.name}: No changes made")
        return False


def main():
    print("\n" + "="*80)
    print("🔥 Removing OLD QA Validator from All Assemblers")
    print("="*80 + "\n")
    
    assembler_dir = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")
    
    assemblers = [
        "landowner_summary.py",
        "quick_check.py",
        "financial_feasibility.py",
        "lh_technical.py",
        "all_in_one.py",
        "executive_summary.py"
    ]
    
    removed_count = 0
    
    for assembler in assemblers:
        file_path = assembler_dir / assembler
        if file_path.exists():
            if remove_old_validator(file_path):
                removed_count += 1
        else:
            print(f"  ❌ {assembler}: Not found")
    
    print(f"\n✅ Removed OLD validator from {removed_count}/{len(assemblers)} assemblers")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
