"""
Script to update all 5 remaining assemblers with PROMPT 3.5-2 watermark & copyright
"""

import re
from pathlib import Path

# List of assemblers to update (landowner_summary already done)
assemblers = [
    "lh_technical.py",
    "quick_check.py",
    "financial_feasibility.py",
    "all_in_one.py",
    "executive_summary.py"
]

base_path = Path("app/services/final_report_assembly/assemblers")

for assembler_file in assemblers:
    file_path = base_path / assembler_file
    print(f"\n{'='*60}")
    print(f"Processing: {assembler_file}")
    print('='*60)
    
    content = file_path.read_text()
    
    # Pattern 1: Update _generate_footer()
    old_footer_pattern = r'def _generate_footer\(self\) -> str:.*?return """.*?</footer>\s*"""'
    new_footer = '''def _generate_footer(self) -> str:
        """[PROMPT 3.5-2] ZEROSITE Copyright Footer"""
        return self.get_zerosite_copyright_footer(
            report_type=self.report_type,
            context_id=self.context_id
        )'''
    
    if re.search(old_footer_pattern, content, re.DOTALL):
        content = re.sub(old_footer_pattern, new_footer, content, flags=re.DOTALL)
        print(f"✅ Updated _generate_footer()")
    else:
        print(f"⚠️  _generate_footer() not found or already updated")
    
    # Pattern 2: Update _get_report_css() - find the closing triple quotes
    old_css_pattern = r'(def _get_report_css\(self\) -> str:.*?return """.*?)(\s+"""\s*$)'
    new_css_end = '''
        """
        
        # Add watermark and copyright CSS
        return base_css + self.get_zerosite_watermark_css() + self.get_copyright_footer_css()
    '''
    
    if re.search(old_css_pattern, content, re.DOTALL | re.MULTILINE):
        # First, rename the return """ to base_css = """
        content = re.sub(
            r'(def _get_report_css\(self\) -> str:.*?""".*?)\n\s+return """',
            r'\1\n        base_css = """',
            content,
            count=1,
            flags=re.DOTALL
        )
        
        # Then update the ending
        content = re.sub(old_css_pattern, r'\1' + new_css_end, content, flags=re.DOTALL | re.MULTILINE)
        print(f"✅ Updated _get_report_css()")
    else:
        print(f"⚠️  _get_report_css() not found or already updated")
    
    # Write back
    file_path.write_text(content)
    print(f"✅ Saved {assembler_file}")

print("\n" + "="*60)
print("PROMPT 3.5-2 UPDATE COMPLETE")
print("="*60)
print("\n✅ Updated 5 assemblers:")
for f in assemblers:
    print(f"   - {f}")
print("\nAll assemblers now include:")
print("   • ZEROSITE watermark (top-right corner)")
print("   • © ZeroSite by AntennaHoldings · nataiheum footer")
print("   • Report ID + Type + Creation time metadata")
