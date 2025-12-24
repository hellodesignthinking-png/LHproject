#!/usr/bin/env python3
"""Fix BUILD SIGNATURE definition in assemblers"""
from pathlib import Path

CORRECT_METHOD = '''    def _wrap_in_document(self, sections: List[str]) -> str:
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
            <style>
            {self._get_report_css()}
            </style>
        </head>
        <body class="final-report {get_report_brand_class(self.report_type)} {self.report_type}">
            {build_signature}
            {"".join(sections)}
        </body>
        </html>
        """'''

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")
FILES = ["lh_technical.py", "all_in_one.py", "executive_summary.py"]

for filename in FILES:
    filepath = ASSEMBLER_DIR / filename
    content = filepath.read_text()
    
    # Find and replace _wrap_in_document method
    method_start = '    def _wrap_in_document(self, sections: List[str]) -> str:'
    if method_start in content:
        # Find method end (next def or end of file)
        start_idx = content.find(method_start)
        # Find next method definition
        next_def = content.find('\n    def ', start_idx + 1)
        if next_def == -1:
            next_def = len(content)
        
        # Replace method
        old_method = content[start_idx:next_def]
        content = content[:start_idx] + CORRECT_METHOD + content[next_def:]
        
        filepath.write_text(content)
        print(f"✅ {filename}: BUILD SIGNATURE fixed")
    else:
        print(f"❌ {filename}: Method not found")

print("\n🎉 Complete!")
