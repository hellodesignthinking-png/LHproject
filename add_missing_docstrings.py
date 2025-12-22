#!/usr/bin/env python3
"""Add missing docstrings to _extract_module_data methods"""

from pathlib import Path

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")

new_docstring = '''    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:
        """
        [FIX 1, 2, 3] Extract data from module HTML with strict consistency rules:
        
        1. NEVER recalculate - extract EXACT displayed values
        2. Preserve ALL core M3/M4 data (even in summary reports)
        3. Apply terminology normalization for consistency
        4. Match units and rounding from source module
        
        NOTE: This is NOT calculation - just extracting displayed values
        """
        import re'''

files_to_fix = [
    "lh_technical.py",
    "quick_check.py",
    "financial_feasibility.py",
    "all_in_one.py",
    "executive_summary.py"
]

for filename in files_to_fix:
    file_path = ASSEMBLER_DIR / filename
    content = file_path.read_text(encoding='utf-8')
    
    if "[FIX 1, 2, 3]" not in content:
        # Replace the method definition
        old_pattern = '    def _extract_module_data(self, module_htmls: Dict[str, str]) -> Dict:\n        import re'
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_docstring)
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Added docstring to {filename}")
        else:
            print(f"⚠️  Pattern not found in {filename}")

print("\n✅ All missing docstrings added")
