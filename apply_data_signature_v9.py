#!/usr/bin/env python3
"""
vABSOLUTE-FINAL-9: Apply DATA SIGNATURE to all 6 assemblers
"""
from pathlib import Path

DATA_SIGNATURE_CODE = '''        # [vABSOLUTE-FINAL-9] Generate DATA SIGNATURE for content verification
        import hashlib
        import json
        
        # Create deterministic data signature from modules_data
        data_for_signature = {
            module_id: {
                k: str(v) for k, v in data.items() 
                if not k.startswith('_')  # Exclude metadata
            }
            for module_id, data in modules_data.items()
        }
        data_signature = hashlib.sha1(
            json.dumps(data_for_signature, sort_keys=True).encode()
        ).hexdigest()[:12]
        
        # Extract key input values for display
        land_area = modules_data.get("M2", {}).get("land_value_total", "N/A")
        total_units = modules_data.get("M4", {}).get("total_units", "N/A") if "M4" in modules_data else modules_data.get("M5", {}).get("total_units", "N/A")
        lh_decision = modules_data.get("M6", {}).get("decision", "N/A")
        npv = modules_data.get("M5", {}).get("npv", "N/A")
        
        # Generate DATA SIGNATURE panel
        data_signature_panel = f"""
        <div style="
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 12px;
            margin: 20px 0;
            font-size: 11px;
            color: #495057;
        ">
            <div style="font-weight: bold; margin-bottom: 8px; color: #212529;">
                📊 Data Signature (데이터 시그니처)
            </div>
            <div style="font-family: monospace; color: #6c757d; margin-bottom: 8px;">
                {data_signature}
            </div>
            <div style="font-size: 10px; color: #6c757d; line-height: 1.6;">
                • 토지감정가: {land_area if isinstance(land_area, str) else f"{land_area:,.0f}원"}<br/>
                • 총세대수: {total_units if isinstance(total_units, str) else f"{total_units:,.0f}세대"}<br/>
                • NPV: {npv if isinstance(npv, str) else f"{npv:,.0f}원"}<br/>
                • LH 판단: {lh_decision}
            </div>
            <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #dee2e6; font-size: 9px; color: #adb5bd;">
                ※ 이 보고서는 입력 데이터가 동일할 경우 이전 보고서와 동일하게 보일 수 있습니다. 이는 정상 동작입니다.<br/>
                ※ 데이터 시그니처가 다르면 입력값이 변경되었음을 의미합니다.
            </div>
        </div>
        """
        
        logger.info(f"[{self.report_type}] DATA SIGNATURE: {data_signature}")
        
'''

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")
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
    
    # Find insertion point: right before "# Generate KPI summary"
    marker = "# Generate KPI summary from modules_data"
    
    if marker in content:
        # Insert DATA SIGNATURE code before KPI summary
        content = content.replace(marker, DATA_SIGNATURE_CODE + marker)
        
        # Also need to insert data_signature_panel into sections list
        # Find "sections = ["
        sections_marker = "sections = ["
        if sections_marker in content:
            # Add data_signature_panel as first element
            content = content.replace(
                sections_marker,
                sections_marker + "\n            data_signature_panel,  # [vABSOLUTE-FINAL-9] Data signature first"
            )
        
        filepath.write_text(content)
        print(f"✅ {filename}: DATA SIGNATURE applied")
    else:
        print(f"⚠️ {filename}: Marker not found")

print("\n🎉 DATA SIGNATURE application complete!")
