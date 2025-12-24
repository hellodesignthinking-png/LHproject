import re
from pathlib import Path

assemblers_dir = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")
assembler_files = [f for f in assemblers_dir.glob("*.py") if f.name not in ["__init__.py"]]

for file_path in assembler_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix: Remove extra closing parenthesis
    original = content
    content = re.sub(
        r'from \.\.base_assembler import ([^)]+), get_report_brand_class\)',
        r'from ..base_assembler import \1, get_report_brand_class',
        content
    )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed: {file_path.name}")
    else:
        print(f"ℹ️  OK: {file_path.name}")
