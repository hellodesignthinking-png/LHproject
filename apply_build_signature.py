#!/usr/bin/env python3
"""
vABSOLUTE-FINAL-7: Apply BUILD SIGNATURE to all 6 assemblers
"""
import re
from pathlib import Path

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")

BUILD_SIGNATURE_CODE = '''    def _wrap_in_document(self, sections: list) -> str:
        """Wrap all sections in HTML document"""
        # [vABSOLUTE-FINAL-7] BUILD SIGNATURE for visual verification
        from datetime import datetime
        build_signature = f"""
        <div style="
            position: fixed;
            top: 10px;
            right: 10px;
            font-size: 11px;
            color: red;
            background: rgba(255,255,255,0.9);
            padding: 8px;
            border: 2px solid red;
            z-index: 9999;
            font-family: monospace;
        ">
            ✅ BUILD: vABSOLUTE-FINAL-6<br/>
            📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC<br/>
            🔧 REPORT: {self.report_type}
        </div>
        """
        
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>{self.config.name_kr}</title>
            <style>{self._get_report_css()}</style>
        </head>
        <body class="final-report {get_report_brand_class(self.report_type)}-check {self.report_type}">
            {build_signature}
            {"".join(sections)}
        </body>
        </html>
        """'''

OLD_PATTERN = r'''    def _wrap_in_document\(self, sections: list\) -> str:
        """Wrap all sections in HTML document"""
        return f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <title>\{self\.config\.name_kr\}</title>
            <style>\{self\._get_report_css\(\)\}</style>
        </head>
        <body class="final-report \{get_report_brand_class\(self\.report_type\)\}.*?\{self\.report_type\}">
            \{""\.\join\(sections\)\}
        </body>
        </html>
        """'''

FILES = [
    "landowner_summary.py",
    "financial_feasibility.py",
    "lh_technical.py",
    "all_in_one.py",
    "executive_summary.py"
]

for filename in FILES:
    filepath = ASSEMBLER_DIR / filename
    
    if not filepath.exists():
        print(f"❌ {filename}: NOT FOUND")
        continue
    
    content = filepath.read_text()
    
    # Find and replace _wrap_in_document method
    if "def _wrap_in_document(self, sections: list)" in content:
        # Use simple string replacement for safety
        old_method_start = '    def _wrap_in_document(self, sections: list) -> str:\n        """Wrap all sections in HTML document"""\n        return f"""'
        
        if old_method_start in content:
            # Find the end of the method (next line with triple quotes)
            method_start_idx = content.find(old_method_start)
            method_body_start = method_start_idx + len(old_method_start)
            
            # Find closing triple quotes
            closing_quotes_idx = content.find('"""', method_body_start)
            
            if closing_quotes_idx > 0:
                # Replace entire method
                old_method = content[method_start_idx:closing_quotes_idx + 3]
                content = content.replace(old_method, BUILD_SIGNATURE_CODE)
                
                filepath.write_text(content)
                print(f"✅ {filename}: BUILD SIGNATURE applied")
            else:
                print(f"⚠️ {filename}: Could not find method end")
        else:
            print(f"⚠️ {filename}: Method format different, needs manual fix")
    else:
        print(f"❌ {filename}: _wrap_in_document not found")

print("\n🎉 BUILD SIGNATURE application complete!")
