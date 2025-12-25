"""
Fix syntax errors from format_currency/format_units replacement
"""
import os
import re

ASSEMBLERS = [
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/landowner_summary.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/quick_check.py"
]

def fix_syntax(file_path: str):
    """Fix broken syntax from regex replacement"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # Fix pattern: format_currency(value)) and value > 0 else "")
    # Should be: format_currency(value) if isinstance(value, (int, float)) and value > 0 else "산출 진행 중"
    
    # Pattern 1: land_area_str
    content = re.sub(
        r'land_area_str = format_currency\(land_area\)\) and land_area > 0 else ""\)',
        'land_area_str = format_currency(land_area) if isinstance(land_area, (int, float)) and land_area > 0 else "산출 진행 중"',
        content
    )
    
    # Pattern 2: total_units_str  
    content = re.sub(
        r'total_units_str = format_units\(total_units\)\) and total_units > 0 else ""\)',
        'total_units_str = format_units(total_units) if isinstance(total_units, (int, float)) and total_units > 0 else "산출 진행 중"',
        content
    )
    
    # Pattern 3: npv_str
    content = re.sub(
        r'npv_str = format_currency\(npv\)\) and npv != 0 else ""\)',
        'npv_str = format_currency(npv) if isinstance(npv, (int, float)) else "산출 진행 중"',
        content
    )
    
    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Fixed: {file_path}")
        return True
    else:
        print(f"⚠️ No changes: {file_path}")
        return False

print("Fixing syntax errors...\n")
fixed_count = 0

for assembler in ASSEMBLERS:
    if os.path.exists(assembler):
        if fix_syntax(assembler):
            fixed_count += 1
    else:
        print(f"❌ Not found: {assembler}")

print(f"\n✅ Fixed {fixed_count}/{len(ASSEMBLERS)} assemblers")
