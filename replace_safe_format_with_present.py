"""
Replace safe_format_value with unified present() function
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

def replace_in_file(file_path: str):
    """Replace safe_format_value with present()"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    original = content
    
    # Remove safe_format_value method definition
    content = re.sub(
        r'def safe_format_value\(self, val.*?\n(?=    def |\Z)',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Replace self.safe_format_value calls with present() or format_currency()
    # Pattern 1: self.safe_format_value(value, default="...") + "원"
    content = re.sub(
        r'self\.safe_format_value\(([^,]+),\s*default="[^"]+"\)\s*\+\s*\("원"[^)]*\)',
        r'format_currency(\1)',
        content
    )
    
    # Pattern 2: self.safe_format_value(value, default="...") + "세대"
    content = re.sub(
        r'self\.safe_format_value\(([^,]+),\s*default="[^"]+"\)\s*\+\s*\("세대"[^)]*\)',
        r'format_units(\1)',
        content
    )
    
    # Pattern 3: self.safe_format_value(value, default="...")
    content = re.sub(
        r'self\.safe_format_value\(([^,]+),\s*default="([^"]+)"\)',
        r'present(\1)',
        content
    )
    
    # Pattern 4: self.safe_format_value(value)
    content = re.sub(
        r'self\.safe_format_value\(([^)]+)\)',
        r'present(\1)',
        content
    )
    
    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Updated: {file_path}")
        return True
    else:
        print(f"⚠️ No changes: {file_path}")
        return False

print("Replacing safe_format_value with present()...\n")
updated_count = 0

for assembler in ASSEMBLERS:
    if os.path.exists(assembler):
        if replace_in_file(assembler):
            updated_count += 1
    else:
        print(f"❌ Not found: {assembler}")

print(f"\n✅ Updated {updated_count}/{len(ASSEMBLERS)} assemblers")
