#!/usr/bin/env python3
"""
Apply landowner_summary wrapper pattern to remaining 5 assemblers
"""

import re

files = [
    "app/services/final_report_assembly/assemblers/quick_check.py",
    "app/services/final_report_assembly/assemblers/financial_feasibility.py",
    "app/services/final_report_assembly/assemblers/lh_technical.py",
    "app/services/final_report_assembly/assemblers/all_in_one.py",
    "app/services/final_report_assembly/assemblers/executive_summary.py",
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix imports
    if "from ..report_type_configs import MANDATORY_KPI" in content:
        content = content.replace(
            "from ..report_type_configs import MANDATORY_KPI",
            "from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi"
        )
    
    if "from ..kpi_extractor import KPIExtractor" in content:
        content = content.replace(
            "from ..kpi_extractor import KPIExtractor",
            "from ..kpi_extractor import KPIExtractor, validate_mandatory_kpi, log_kpi_pipeline, FinalReportAssemblyError"
        )
    
    # Replace the extraction pattern
    # Pattern 1: required_map = MANDATORY_KPI[self.report_type]
    content = re.sub(
        r'required_map = MANDATORY_KPI\[self\.report_type\]',
        'mandatory_kpi = get_mandatory_kpi(self.report_type)',
        content
    )
    
    # Pattern 2: required_map = MANDATORY_KPI.get(report_type, {})
    content = re.sub(
        r'required_map = MANDATORY_KPI\.get\(report_type, \{\}\)',
        'mandatory_kpi = get_mandatory_kpi(report_type)',
        content
    )
    
    # Pattern 3: Replace the extraction loop
    old_loop = r'(\s+)modules_data = \{\}\s+for module_id in \[[^\]]+\]:\s+html = module_htmls\.get\(module_id, ""\)\s+required_keys = required_map\.get\(module_id, \[\]\)\s+modules_data\[module_id\] = KPIExtractor\.extract_module_kpi\(html, module_id, required_keys\)'
    
    new_loop = r'\1modules_data = self._extract_module_data(module_htmls, mandatory_kpi)'
    
    content = re.sub(old_loop, new_loop, content, flags=re.DOTALL)
    
    # Pattern 4: Replace hard-fail validation
    old_validation = r'(\s+)# Hard-Fail validation: Check mandatory KPIs\s+missing = \[\]\s+for module_id, keys in required_map\.items\(\):\s+for k in keys:\s+if modules_data\.get\(module_id, \{\}\)\.get\(k\) is None:\s+missing\.append\(f"\{module_id\}\.\{k\}"\)\s+if missing:\s+raise FinalReportAssemblyError\([^\)]+\)'
    
    new_validation = r'''\1# [Phase 3.10 Final Lock] HARD-FAIL: Validate mandatory KPI
\1missing_kpi = validate_mandatory_kpi(self.report_type, modules_data, {self.report_type: mandatory_kpi})
\1if missing_kpi:
\1    error_msg = f"[BLOCKED] Missing required KPI: {', '.join(missing_kpi)}"
\1    logger.error(f"[{self.report_type}] {error_msg}")
\1    return {
\1        "html": f"<html><body><h1>❌ Report Generation Blocked</h1><pre>{error_msg}</pre></body></html>",
\1        "qa_result": {
\1            "status": "FAIL",
\1            "errors": [error_msg],
\1            "warnings": [],
\1            "blocking": True,
\1            "reason": "Hard-Fail: Required KPI missing"
\1        }
\1    }'''
    
    content = re.sub(old_validation, new_validation, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filepath.split('/')[-1]}")

print("\n✅ All 5 assemblers updated with wrapper pattern")
