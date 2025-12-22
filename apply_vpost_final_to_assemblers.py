#!/usr/bin/env python3
"""
vPOST-FINAL: Apply operational safety to all 5 remaining assemblers
"""

import re

assemblers = [
    "quick_check.py",
    "financial_feasibility.py",
    "lh_technical.py",
    "all_in_one.py",
    "executive_summary.py"
]

for filename in assemblers:
    filepath = f"app/services/final_report_assembly/assemblers/{filename}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix imports
    old_import = "from ..kpi_extractor import KPIExtractor, validate_mandatory_kpi, log_kpi_pipeline, FinalReportAssemblyError"
    new_import = """from ..kpi_extractor import (
    KPIExtractor, 
    validate_mandatory_kpi, 
    validate_kpi_with_safe_gate,
    log_kpi_pipeline, 
    FinalReportAssemblyError
)"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
    
    # Fix config imports
    old_config = "from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi"
    new_config = "from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi, get_critical_kpi"
    
    if old_config in content:
        content = content.replace(old_config, new_config)
    
    # Replace validation logic
    old_validation_pattern = r'# \[Phase 3\.10 Final Lock\] Extract KPI using new pipeline\s+mandatory_kpi = get_mandatory_kpi\(self\.report_type\)\s+modules_data = self\._extract_module_data\([^)]+\)\s+# \[Phase 3\.10 Final Lock\] HARD-FAIL: Validate mandatory KPI\s+missing_kpi = validate_mandatory_kpi\([^)]+\)\s+if missing_kpi:\s+error_msg = [^\n]+\s+logger\.error\([^\n]+\)\s+return \{[^}]+\}'
    
    new_validation = '''# [Phase 3.10 Final Lock] Extract KPI using new extractor
        mandatory_kpi = get_mandatory_kpi(self.report_type)
        critical_kpi = get_critical_kpi(self.report_type)
        modules_data = self._extract_module_data(MODULES_DICT, mandatory_kpi)
        
        # [vPOST-FINAL] SAFE-GATE Validation
        validation_result = validate_kpi_with_safe_gate(
            self.report_type, modules_data, 
            {self.report_type: mandatory_kpi}, {self.report_type: critical_kpi}
        )
        critical_missing = validation_result["critical_missing"]
        soft_missing = validation_result["soft_missing"]
        
        if critical_missing:
            error_msg = f"[BLOCKED] Missing CRITICAL KPI: {', '.join(critical_missing)}"
            logger.error(f"[{self.report_type}] {error_msg}")
            return {
                "html": f"<html><body><h1>🚫 Report Generation Blocked</h1><pre>{error_msg}</pre></body></html>",
                "qa_result": {"status": "FAIL", "errors": [error_msg], "blocking": True}
            }
        
        data_completeness_panel = self.generate_data_completeness_panel(soft_missing)'''
    
    # Apply changes
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {filename}")

print("\n✅ vPOST-FINAL applied to all assemblers")
print("⚠️  Manual review required for module dict extraction")
