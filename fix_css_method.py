"""
Fix _get_report_css() method in all assemblers
"""
import os

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

NEW_METHOD = f'''    def _get_report_css(self) -> str:
        """[UNIFIED] Report CSS - DO NOT MODIFY"""
        base_css = """{UNIFIED_CSS}"""
        
        # Add watermark and copyright CSS
        return base_css + self.get_unified_design_css() + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()
'''

def fix_method(file_path: str):
    """Replace entire _get_report_css method"""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find method start and end
    method_start = -1
    method_end = -1
    indent_level = 0
    
    for i, line in enumerate(lines):
        if "def _get_report_css(self)" in line:
            method_start = i
            indent_level = len(line) - len(line.lstrip())
        elif method_start >= 0 and method_end < 0:
            # Check if next method starts (same or less indentation)
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('"""'):
                current_indent = len(line) - len(line.lstrip())
                if current_indent <= indent_level and "def " in line:
                    method_end = i
                    break
    
    if method_start >= 0:
        if method_end < 0:
            method_end = len(lines)
        
        # Replace method
        new_lines = lines[:method_start] + [NEW_METHOD + "\n"] + lines[method_end:]
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        
        print(f"✅ Fixed: {file_path}")
        return True
    else:
        print(f"⚠️ Method not found: {file_path}")
        return False

print("Fixing _get_report_css() in all assemblers...\n")
fixed_count = 0

for assembler in ASSEMBLERS:
    if os.path.exists(assembler):
        if fix_method(assembler):
            fixed_count += 1
    else:
        print(f"❌ Not found: {assembler}")

print(f"\n✅ Fixed {fixed_count}/{len(ASSEMBLERS)} assemblers")
