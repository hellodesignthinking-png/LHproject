"""
Update all 6 assemblers to use unified CSS
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

# Read unified CSS
with open("app/services/final_report_assembly/base_report_style.css", "r") as f:
    UNIFIED_CSS = f.read()

def update_css_method(file_path: str):
    """Update _get_report_css() to return unified CSS"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Pattern to find _get_report_css method
    pattern = r'(def _get_report_css\(self\) -> str:.*?""")(.*?)(return .*?\n)'
    
    def replacement(match):
        method_def = match.group(1)
        # Replace with unified CSS
        new_body = f'''
        # UNIFIED CSS - DO NOT MODIFY
        base_css = """{UNIFIED_CSS}"""
        
        # Add watermark and copyright CSS
        '''
        return method_def + new_body + match.group(3)
    
    # Apply replacement
    updated = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)
        print(f"✅ Updated: {file_path}")
        return True
    else:
        print(f"⚠️ No changes: {file_path}")
        return False

print("Updating CSS in all assemblers...\n")
updated_count = 0

for assembler in ASSEMBLERS:
    if os.path.exists(assembler):
        if update_css_method(assembler):
            updated_count += 1
    else:
        print(f"❌ Not found: {assembler}")

print(f"\n✅ Updated {updated_count}/{len(ASSEMBLERS)} assemblers")
