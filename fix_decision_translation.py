import os
import re

# Add translator import to all assembler files
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
    
    # Add import if not present
    if 'translate_decision_to_korean' not in content:
        # Find the base_assembler import line
        import_pattern = r'(from \.\.base_assembler import [^\n]+)'
        
        def add_translator(match):
            imports = match.group(1)
            if 'translate_decision_to_korean' not in imports:
                # Check if imports end with parenthesis
                if imports.strip().endswith(')'):
                    # Multi-line import
                    imports = imports.rstrip()[:-1] + ', translate_decision_to_korean)'
                else:
                    # Single line import
                    imports = imports + ', translate_decision_to_korean'
            return imports
        
        content = re.sub(import_pattern, add_translator, content)
    
    # Wrap all decision extractions with translator
    # Pattern: lh_decision = xxx.get("decision") or "..."
    patterns = [
        (r'lh_decision\s*=\s*([^\n]+\.get\("decision"\)[^\n]*)', 
         r'lh_decision = translate_decision_to_korean(\1)'),
        (r'decision\s*=\s*(m6_data\.get\("decision"\)[^\n]*)',
         r'decision = translate_decision_to_korean(\1)'),
    ]
    
    for pattern, replacement in patterns:
        # Check if already wrapped
        if 'translate_decision_to_korean' not in content or content.count('translate_decision_to_korean(') < 5:
            content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed: {filepath}")

print("\n✅ All assemblers fixed!")
