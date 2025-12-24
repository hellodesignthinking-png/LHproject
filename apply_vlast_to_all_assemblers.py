#!/usr/bin/env python3
"""
Apply vLAST Fix to All 6 Final Report Assemblers
================================================

This script replaces the old _extract_kpi_from_module_html() method
with the new unified extract_module_kpis() function in all assemblers.
"""

import os
from pathlib import Path

def apply_vlast_to_assembler(file_path: Path) -> bool:
    """Apply vLAST fix to a single assembler file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already uses new function
    if "from app.services.final_report_assembly.kpi_extraction_vlast import extract_module_kpis" in content:
        print(f"  ✅ {file_path.name}: Already patched")
        return False
    
    # Add import
    import_line = "from app.services.final_report_assembly.kpi_extraction_vlast import extract_module_kpis\n"
    
    # Find last import line
    lines = content.split('\n')
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            last_import_idx = i
    
    if last_import_idx != -1:
        lines.insert(last_import_idx + 1, import_line)
        content = '\n'.join(lines)
    
    # Replace method calls
    # Old: self._extract_kpi_from_module_html(module_id, html)
    # New: extract_module_kpis(html, module_id)  # Note: swapped parameter order!
    
    # Find and replace in _extract_module_data method
    content = content.replace(
        'self._extract_kpi_from_module_html(',
        'extract_module_kpis('
    )
    
    # Note: Parameter order is SWAPPED in new function
    # Old: _extract_kpi_from_module_html(module_id, html)
    # New: extract_module_kpis(html, module_id)
    # We need to swap parameters in calls
    
    import re
    content = re.sub(
        r'extract_module_kpis\((["\'][M][2-6]["\']),\s*([a-z_]+)\)',
        r'extract_module_kpis(\2, \1)',
        content
    )
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ {file_path.name}: vLAST fix applied")
    return True


def main():
    print("\n" + "="*80)
    print("🔥 Applying vLAST Fix to All Assemblers")
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
    
    patched_count = 0
    
    for assembler in assemblers:
        file_path = assembler_dir / assembler
        if file_path.exists():
            if apply_vlast_to_assembler(file_path):
                patched_count += 1
        else:
            print(f"  ❌ {assembler}: Not found")
    
    print(f"\n✅ Patched {patched_count}/{len(assemblers)} assemblers")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
