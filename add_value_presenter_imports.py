"""
Add value_presenter imports to all assemblers
"""
import os

ASSEMBLERS = [
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/landowner_summary.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/quick_check.py"
]

IMPORT_LINE = "from ..value_presenter import present, present_soft_kpi, format_currency, format_units, format_percentage\n"

def add_import(file_path: str):
    """Add value_presenter import if not exists"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if already imported
    if "from ..value_presenter import" in content:
        print(f"⚠️ Already imported: {file_path}")
        return False
    
    # Find the last import line
    lines = content.split("\n")
    last_import_idx = -1
    
    for i, line in enumerate(lines):
        if line.startswith("from") or line.startswith("import"):
            last_import_idx = i
    
    if last_import_idx >= 0:
        # Insert after last import
        lines.insert(last_import_idx + 1, IMPORT_LINE.strip())
        updated = "\n".join(lines)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)
        
        print(f"✅ Added import: {file_path}")
        return True
    else:
        print(f"❌ Could not find import section: {file_path}")
        return False

print("Adding value_presenter imports...\n")
updated_count = 0

for assembler in ASSEMBLERS:
    if os.path.exists(assembler):
        if add_import(assembler):
            updated_count += 1
    else:
        print(f"❌ Not found: {assembler}")

print(f"\n✅ Added imports to {updated_count}/{len(ASSEMBLERS)} assemblers")
