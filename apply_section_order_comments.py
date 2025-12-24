#!/usr/bin/env python3
"""Add FIX 4 section order comments to all assemblers"""

from pathlib import Path

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")

order_comment = '''
        # [FIX 4] Section Order Canonicalization
        # Canonical order: Cover → KPI → Executive Summary → Modules (with transitions) → Final Judgment → Next Actions → Decision Block → Footer
        '''

for assembler_file in ASSEMBLER_DIR.glob("*.py"):
    if assembler_file.name == "__init__.py":
        continue
    
    content = assembler_file.read_text(encoding='utf-8')
    
    # Find sections = [ and add comment if not present
    if "sections = [" in content and "[FIX 4]" not in content:
        # Add comment before sections = [
        content = content.replace(
            "        sections = [",
            order_comment + "        sections = ["
        )
        assembler_file.write_text(content, encoding='utf-8')
        print(f"✅ Added section order comment to {assembler_file.name}")

print("\n✅ Section order comments added to all assemblers")
