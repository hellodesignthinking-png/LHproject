"""
Phase 4.0: Apply New Design System to All Assemblers
Updates _wrap_in_document to use get_report_brand_class()
"""

import re
from pathlib import Path

def update_assembler_body_class(file_path: Path) -> bool:
    """Update body class to use proper brand class"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern 1: Fixed class like "report-color-landowner"
    content = re.sub(
        r'<body class="final-report report-color-(\w+)',
        r'<body class="final-report {get_report_brand_class(self.report_type)}',
        content
    )
    
    # Pattern 2: With {self.report_type} at end
    content = re.sub(
        r'<body class="final-report report-color-(\w+) \{self\.report_type\}">',
        r'<body class="final-report {get_report_brand_class(self.report_type)} {self.report_type}">',
        content
    )
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def add_import_if_missing(file_path: Path) -> bool:
    """Add get_report_brand_class import if missing"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "get_report_brand_class" in content:
        return False  # Already imported
    
    # Find the base_assembler import line
    import_pattern = r'(from \.\.base_assembler import [^\n]+)'
    match = re.search(import_pattern, content)
    
    if match:
        old_import = match.group(1)
        # Add get_report_brand_class to imports
        new_import = old_import.rstrip(')') + ', get_report_brand_class)'
        content = content.replace(old_import, new_import)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    assemblers_dir = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")
    assembler_files = [f for f in assemblers_dir.glob("*.py") if f.name not in ["__init__.py", "__pycache__"]]
    
    print("=" * 80)
    print("Phase 4.0: Applying New Design System to Assemblers")
    print("=" * 80)
    
    for file_path in sorted(assembler_files):
        print(f"\n📄 {file_path.name}")
        
        # Step 1: Add import
        import_added = add_import_if_missing(file_path)
        if import_added:
            print("  ✅ Added get_report_brand_class import")
        else:
            print("  ℹ️  Import already exists or not needed")
        
        # Step 2: Update body class
        updated = update_assembler_body_class(file_path)
        if updated:
            print("  ✅ Updated body class to use get_report_brand_class()")
        else:
            print("  ℹ️  Body class already correct")
    
    print("\n" + "=" * 80)
    print("✅ Phase 4.0 Design System Applied to All Assemblers")
    print("=" * 80)

if __name__ == "__main__":
    main()
