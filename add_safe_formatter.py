import os

# Add safe_format_value function to each assembler
safe_formatter = '''
    def safe_format_value(self, val, default="산출 진행 중"):
        """Safely format a value, preventing dict/list exposure"""
        if val is None:
            return default
        if isinstance(val, dict):
            return default
        if isinstance(val, list):
            return default
        if isinstance(val, str) and (val.upper() == "N/A" or not val.strip()):
            return default
        if isinstance(val, (int, float)):
            if val == 0:
                return default
            return f"{val:,.0f}"
        return str(val)
'''

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
    
    # Check if safe_format_value already exists
    if 'def safe_format_value' in content:
        print(f"⏭️  Skipped (already exists): {filepath}")
        continue
    
    # Find the class definition and add the method after __init__
    import re
    # Find the first method after __init__
    pattern = r'(def __init__\(self.*?\n(?:.*?\n)*?    def )'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Insert before the next method
        insert_pos = match.end() - 8  # Before "    def "
        content = content[:insert_pos] + '\n' + safe_formatter + '\n    def ' + content[insert_pos+8:]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Added safe_format_value to: {filepath}")
    else:
        print(f"⚠️  Could not find insertion point: {filepath}")

print("\n✅ Safe formatter added to all assemblers!")
