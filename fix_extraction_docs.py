#!/usr/bin/env python3
"""Fix _extract_module_data documentation"""

from pathlib import Path

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")

new_docstring = '''        """
        [FIX 1, 2, 3] Extract data from module HTML with strict consistency rules:
        
        1. NEVER recalculate - extract EXACT displayed values
        2. Preserve ALL core M3/M4 data (even in summary reports)
        3. Apply terminology normalization for consistency
        4. Match units and rounding from source module
        
        NOTE: This is NOT calculation - just extracting displayed values
        """'''

for assembler_file in ASSEMBLER_DIR.glob("*.py"):
    if assembler_file.name == "__init__.py":
        continue
    
    content = assembler_file.read_text(encoding='utf-8')
    
    if "_extract_module_data" in content and "[FIX 1, 2, 3]" not in content:
        # Find and replace the docstring
        import re
        
        # Pattern to match the method definition and its docstring
        pattern = r'(    def _extract_module_data\([^)]+\)[^:]*:)\s*"""\s*[^"]*\s*"""'
        
        if re.search(pattern, content):
            content = re.sub(pattern, r'\1' + new_docstring, content)
            assembler_file.write_text(content, encoding='utf-8')
            print(f"✅ Updated: {assembler_file.name}")
        else:
            print(f"⚠️  Pattern not found in {assembler_file.name}")

print("\n✅ Extraction documentation updated")
