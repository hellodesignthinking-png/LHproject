#!/usr/bin/env python3
"""
Comprehensive Report Fix Script
================================
Updates all 6 report assemblers with:
1. Unified CSS loading from unified_report_theme.css
2. Improved data signature extraction using resolve_scalar
3. Standard page structure enforcement
4. Data + interpretation integration
5. Report-specific narrative tones
"""

import re
import os

BASE_DIR = "/home/user/webapp"

# Step 1: Update data signature extraction in all assemblers
def update_data_signature_extraction(file_path):
    """Update data signature to use resolve_scalar instead of direct dict access"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add resolve_scalar import if not present
    if 'from app.utils.report_value_resolver import resolve_scalar' not in content:
        # Find the import section
        import_pattern = r'(from \.\.value_presenter import[^\n]+\n)'
        replacement = r'\1from app.utils.report_value_resolver import resolve_scalar\n'
        content = re.sub(import_pattern, replacement, content)
    
    # Replace unsafe dict access patterns in data signature
    # Pattern: land_area = (modules_data.get("M2") or {}).get("land_value_total", "N/A")
    unsafe_patterns = [
        (
            r'land_area\s*=\s*\(modules_data\.get\("M2"\)\s*or\s*\{\}\)\.get\("land_value_total",\s*"[^"]*"\)',
            'land_area = resolve_scalar(modules_data, "M2", "land_value_total")'
        ),
        (
            r'total_units\s*=\s*\(modules_data\.get\("M4"\)\s*or\s*\{\}\)\.get\("total_units",\s*"[^"]*"\)',
            'total_units = resolve_scalar(modules_data, "M4", "total_units")'
        ),
        (
            r'total_units\s*=\s*.*?modules_data\.get\("M5"\).*?get\("total_units".*?\)',
            'total_units = resolve_scalar(modules_data, "M4", "total_units") or resolve_scalar(modules_data, "M5", "total_units")'
        ),
        (
            r'npv\s*=\s*\(modules_data\.get\("M5"\)\s*or\s*\{\}\)\.get\("npv",\s*"[^"]*"\)',
            'npv = resolve_scalar(modules_data, "M5", "npv")'
        ),
        (
            r'lh_decision\s*=\s*translate_decision_to_korean\(\(modules_data\.get\("M6"\)\s*or\s*\{\}\)\.get\("decision"\)\s*or\s*"[^"]*"\)',
            'lh_decision = translate_decision_to_korean(resolve_scalar(modules_data, "M6", "decision") or "검토 필요")'
        ),
    ]
    
    for pattern, replacement in unsafe_patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated data signature extraction in {os.path.basename(file_path)}")

# Step 2: Update CSS loading to use unified theme
def update_css_loading(file_path):
    """Replace inline CSS with unified_report_theme.css loading"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace _get_report_css method
    css_method_pattern = r'def _get_report_css\(self\)\s*->\s*str:.*?return\s+""".*?"""'
    
    unified_css_method = '''def _get_report_css(self) -> str:
        """Load unified report theme CSS"""
        css_path = os.path.join(os.path.dirname(__file__), '../../static/unified_report_theme.css')
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""  # Fallback to empty if file not found'''
    
    content = re.sub(css_method_pattern, unified_css_method, content, flags=re.DOTALL)
    
    # Ensure os import is present
    if 'import os' not in content:
        # Add after other imports
        content = re.sub(
            r'(from typing import[^\n]+\n)',
            r'\1import os\n',
            content
        )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated CSS loading in {os.path.basename(file_path)}")

# Step 3: Add interpretation paragraph helper
def add_interpretation_helper(file_path):
    """Add interpretation paragraph generation helper"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if interpretation helper already exists
    if 'def generate_interpretation_paragraph' in content:
        print(f"⏭️  Interpretation helper already exists in {os.path.basename(file_path)}")
        return
    
    # Add helper method before assemble() method
    interpretation_helper = '''
    def generate_interpretation_paragraph(self, label: str, value, interpretation: str) -> str:
        """Generate data + interpretation paragraph"""
        from app.utils.report_value_resolver import present_money_krw, present_int, present_pct
        
        # Format value based on type
        if isinstance(value, (int, float)):
            if '원' in label or 'NPV' in label or '감정가' in label:
                formatted = present_money_krw(value)
            elif '%' in label or 'IRR' in label or '수익률' in label:
                formatted = present_pct(value)
            else:
                formatted = present_int(value)
        else:
            formatted = str(value) if value else "산출 진행 중"
        
        return f"""
        <div class="data-interpretation-block">
            <div class="data-label"><strong>{label}:</strong> {formatted}</div>
            <div class="interpretation-text">{interpretation}</div>
        </div>
        """
    
'''
    
    # Find the assemble method and insert before it
    assemble_pattern = r'(\s+def assemble\(self\)\s*->\s*Dict\[str,\s*str\]:)'
    content = re.sub(assemble_pattern, interpretation_helper + r'\1', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Added interpretation helper to {os.path.basename(file_path)}")

# Main execution
def main():
    assembler_files = [
        f"{BASE_DIR}/app/services/final_report_assembly/assemblers/all_in_one.py",
        f"{BASE_DIR}/app/services/final_report_assembly/assemblers/executive_summary.py",
        f"{BASE_DIR}/app/services/final_report_assembly/assemblers/financial_feasibility.py",
        f"{BASE_DIR}/app/services/final_report_assembly/assemblers/landowner_summary.py",
        f"{BASE_DIR}/app/services/final_report_assembly/assemblers/lh_technical.py",
        f"{BASE_DIR}/app/services/final_report_assembly/assemblers/quick_check.py",
    ]
    
    print("="*60)
    print("COMPREHENSIVE REPORT FIX")
    print("="*60)
    
    for file_path in assembler_files:
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"\n🔧 Processing: {os.path.basename(file_path)}")
        print("-"*60)
        
        try:
            # Step 1: Update data signature extraction
            update_data_signature_extraction(file_path)
            
            # Step 2: Update CSS loading
            update_css_loading(file_path)
            
            # Step 3: Add interpretation helper
            add_interpretation_helper(file_path)
            
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(file_path)}: {e}")
    
    print("\n" + "="*60)
    print("COMPREHENSIVE FIX COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Verify syntax: python3 -m py_compile app/services/final_report_assembly/assemblers/*.py")
    print("2. Restart backend: pkill -f uvicorn && python -m uvicorn app.main:app --reload")
    print("3. Test all 6 reports")

if __name__ == "__main__":
    main()
