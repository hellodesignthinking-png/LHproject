import os
import re

assembler_files = [
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/landowner_summary.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/quick_check.py",
]

for filepath in assembler_files:
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace land_area_str = format_value(land_area...) with self.safe_format_value
    patterns = [
        (r'land_area_str = format_value\(land_area[^)]*\)',
         'land_area_str = self.safe_format_value(land_area, default="산출 진행 중") + ("원" if isinstance(land_area, (int, float)) and land_area > 0 else "")'),
        (r'total_units_str = format_value\(total_units[^)]*\)',
         'total_units_str = self.safe_format_value(total_units, default="산출 진행 중") + ("세대" if isinstance(total_units, (int, float)) and total_units > 0 else "")'),
        (r'npv_str = format_value\(npv[^)]*\)',
         'npv_str = self.safe_format_value(npv, default="산출 진행 중") + ("원" if isinstance(npv, (int, float)) and npv != 0 else "")'),
        (r'lh_decision_str = str\(lh_decision\)[^"]*"N/A"',
         'lh_decision_str = self.safe_format_value(lh_decision, default="심사 진행 중")'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {filepath}")

print("\n✅ All data signature displays updated!")
