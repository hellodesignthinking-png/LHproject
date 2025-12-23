#!/usr/bin/env python3
"""vABSOLUTE-FINAL-7: Apply BUILD SIGNATURE to remaining assemblers"""
from pathlib import Path

SIGNATURE_INJECTION = '''        #[vABSOLUTE-FINAL-7] BUILD SIGNATURE for visual verification
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
        """'''

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")
FILES = ["financial_feasibility.py", "lh_technical.py", "all_in_one.py", "executive_summary.py"]

for filename in FILES:
    filepath = ASSEMBLER_DIR / filename
    content = filepath.read_text()
    
    # Find <body> tag and inject signature
    body_pattern = '<body class="final-report'
    if body_pattern in content:
        # Split at body tag
        parts = content.split(body_pattern, 1)
        if len(parts) == 2:
            # Find end of body tag (>)
            body_tag_end = parts[1].find('>')
            if body_tag_end > 0:
                # Inject after body tag
                before = parts[0] + body_pattern + parts[1][:body_tag_end + 1]
                after = parts[1][body_tag_end + 1:]
                
                # Check if signature already exists
                if "vABSOLUTE-FINAL-6" not in content:
                    new_content = before + "\n            {build_signature}" + after
                    filepath.write_text(new_content)
                    print(f"✅ {filename}: BUILD SIGNATURE injected")
                else:
                    print(f"⏭️ {filename}: BUILD SIGNATURE already exists")
    else:
        print(f"❌ {filename}: Could not find body tag")

print("\n🎉 Complete!")
