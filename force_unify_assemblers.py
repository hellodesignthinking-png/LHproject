#!/usr/bin/env python3
"""
vABSOLUTE-FINAL: Force unify all 5 remaining assemblers
Copy landowner_summary pattern EXACTLY
"""

import re

# Read reference implementation
with open("app/services/final_report_assembly/assemblers/landowner_summary.py", 'r', encoding='utf-8') as f:
    reference = f.read()

# Extract the validation block from landowner_summary
validation_block_match = re.search(
    r'# \[Phase 3\.10 Final Lock\] Extract KPI using new extractor.*?# Generate KPI summary box from modules_data',
    reference,
    re.DOTALL
)

if not validation_block_match:
    print("❌ Could not find reference validation block")
    exit(1)

reference_validation = validation_block_match.group(0)

print("✅ Reference validation block extracted from landowner_summary.py")
print(f"   Length: {len(reference_validation)} characters")

# Target assemblers
assemblers = {
    "quick_check.py": ["M5", "M6"],
    "financial_feasibility.py": ["M2", "M4", "M5"],
    "lh_technical.py": ["M3", "M4", "M6"],
    "all_in_one.py": ["M2", "M3", "M4", "M5", "M6"],
    "executive_summary.py": ["M2", "M5", "M6"]
}

for filename, modules in assemblers.items():
    filepath = f"app/services/final_report_assembly/assemblers/{filename}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix imports (add missing ones)
    if "get_critical_kpi" not in content:
        content = content.replace(
            "from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi",
            "from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi, get_critical_kpi"
        )
    
    if "validate_kpi_with_safe_gate" not in content:
        old_import = "from ..kpi_extractor import ("
        if old_import in content:
            content = content.replace(
                old_import + "\n    KPIExtractor,",
                old_import + "\n    KPIExtractor, \n    validate_kpi_with_safe_gate,"
            )
    
    # 2. Build module dict string for this assembler
    module_dict_str = "{" + ", ".join([f'"{m}": {m.lower()}_html' for m in modules]) + "}"
    
    # 3. Create validation block for this assembler
    validation_for_this = reference_validation.replace(
        '{"M2": m2_html, "M5": m5_html, "M6": m6_html}',
        module_dict_str
    )
    
    # 4. Find and replace old validation block
    old_pattern = r'# \[Phase 3\.10 Final Lock\].*?(?=\n\n\s+# Generate|# \[FIX 2\]|kpi_summary = self\.generate_kpi_summary_box)'
    
    if re.search(old_pattern, content, re.DOTALL):
        content = re.sub(old_pattern, validation_for_this.rstrip(), content, flags=re.DOTALL)
        print(f"✅ {filename}: Validation block replaced")
    else:
        print(f"⚠️  {filename}: Pattern not found, may need manual review")
    
    # 5. Ensure data_completeness_panel is in sections
    if "data_completeness_panel" not in content:
        # Find sections list
        sections_match = re.search(r'sections = \[\s+self\._generate_cover_page\(\),', content)
        if sections_match:
            content = content.replace(
                'sections = [\n            self._generate_cover_page(),',
                'sections = [\n            self._generate_cover_page(),\n            data_completeness_panel,'
            )
            print(f"   + data_completeness_panel inserted")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filename} unified")

print("\n" + "="*60)
print("✅ All 5 assemblers forced to landowner_summary pattern")
print("="*60)
