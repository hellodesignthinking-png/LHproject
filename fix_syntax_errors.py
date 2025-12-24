#!/usr/bin/env python3
"""
Fix syntax errors in assemblers (missing closing braces)
"""

files = [
    "app/services/final_report_assembly/assemblers/quick_check.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py",
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find line with return { ... } missing closing brace before _extract_module_data
    for i in range(len(lines)):
        if "def _extract_module_data" in lines[i]:
            # Check the previous lines for the return statement
            for j in range(i-1, max(0, i-20), -1):
                if '"reason": "Hard-Fail: Required KPI missing"' in lines[j]:
                    # Check if next line has closing braces
                    if j+1 < len(lines) and "}" not in lines[j+1]:
                        # Add closing braces
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        lines[j+1] = " " * (indent-4) + "}\n" + lines[j+1]
                        print(f"✅ Fixed {filepath.split('/')[-1]} at line {j+1}")
                        break
            break
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

print("\n✅ Syntax errors fixed")
