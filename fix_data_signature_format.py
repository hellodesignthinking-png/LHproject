#!/usr/bin/env python3
"""Fix DATA SIGNATURE formatting to handle None values"""
from pathlib import Path

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")
FILES = [
    "landowner_summary.py",
    "financial_feasibility.py",
    "lh_technical.py",
    "all_in_one.py",
    "executive_summary.py"
]

OLD_EXTRACT = '''        # Extract key input values for display
        land_area = modules_data.get("M2", {}).get("land_value_total", "N/A")
        total_units = modules_data.get("M4", {}).get("total_units", "N/A") if "M4" in modules_data else modules_data.get("M5", {}).get("total_units", "N/A")
        lh_decision = modules_data.get("M6", {}).get("decision", "N/A")
        npv = modules_data.get("M5", {}).get("npv", "N/A")'''

NEW_EXTRACT = '''        # Extract key input values for display
        land_area = modules_data.get("M2", {}).get("land_value_total", "N/A")
        total_units = modules_data.get("M4", {}).get("total_units", "N/A") if "M4" in modules_data else modules_data.get("M5", {}).get("total_units", "N/A")
        lh_decision = modules_data.get("M6", {}).get("decision", "N/A")
        npv = modules_data.get("M5", {}).get("npv", "N/A")
        
        # Format values safely
        def format_value(val, fmt=",.0f", unit=""):
            if val is None or val == "N/A" or (isinstance(val, str) and val.upper() == "N/A"):
                return "N/A"
            try:
                if isinstance(val, (int, float)):
                    return f"{val:{fmt}}{unit}"
                return str(val)
            except:
                return str(val)
        
        land_area_str = format_value(land_area, unit="원")
        total_units_str = format_value(total_units, unit="세대")
        npv_str = format_value(npv, unit="원")
        lh_decision_str = str(lh_decision) if lh_decision else "N/A"'''

OLD_DISPLAY = '''                • 토지감정가: {land_area if isinstance(land_area, str) else f"{land_area:,.0f}원"}<br/>
                • 총세대수: {total_units if isinstance(total_units, str) else f"{total_units:,.0f}세대"}<br/>
                • NPV: {npv if isinstance(npv, str) else f"{npv:,.0f}원"}<br/>
                • LH 판단: {lh_decision}'''

NEW_DISPLAY = '''                • 토지감정가: {land_area_str}<br/>
                • 총세대수: {total_units_str}<br/>
                • NPV: {npv_str}<br/>
                • LH 판단: {lh_decision_str}'''

for filename in FILES:
    filepath = ASSEMBLER_DIR / filename
    content = filepath.read_text()
    
    if OLD_EXTRACT in content:
        content = content.replace(OLD_EXTRACT, NEW_EXTRACT)
        print(f"✅ {filename}: Extract fixed")
    
    if OLD_DISPLAY in content:
        content = content.replace(OLD_DISPLAY, NEW_DISPLAY)
        print(f"✅ {filename}: Display fixed")
    
    filepath.write_text(content)

print("\n🎉 Format fix complete!")
