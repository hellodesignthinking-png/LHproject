import os
import re

# Fix pattern in all assemblers
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
    
    # Fix: modules_data.get("M2") or {}.get("key") -> (modules_data.get("M2") or {}).get("key")
    # This pattern is WRONG and returns the entire dict
    patterns_to_fix = [
        (r'modules_data\.get\("M2"\) or \{\}\.get\("land_value_total"', 
         r'(modules_data.get("M2") or {}).get("land_value_total"'),
        (r'modules_data\.get\("M4"\) or \{\}\.get\("total_units"',
         r'(modules_data.get("M4") or {}).get("total_units"'),
        (r'modules_data\.get\("M5"\) or \{\}\.get\("total_units"',
         r'(modules_data.get("M5") or {}).get("total_units"'),
        (r'modules_data\.get\("M5"\) or \{\}\.get\("npv"',
         r'(modules_data.get("M5") or {}).get("npv"'),
        (r'modules_data\.get\("M6"\) or \{\}\.get\("decision"',
         r'(modules_data.get("M6") or {}).get("decision"'),
    ]
    
    for pattern, replacement in patterns_to_fix:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {filepath}")

print("\n✅ All data signature extractions fixed!")
