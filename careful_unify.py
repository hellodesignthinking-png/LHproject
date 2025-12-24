#!/usr/bin/env python3
"""
Carefully apply vPOST-FINAL pattern preserving class structure
"""

# Only fix all_in_one.py imports for now
filepath = "app/services/final_report_assembly/assemblers/all_in_one.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix imports
if "get_critical_kpi" not in content:
    content = content.replace(
        "from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi",
        "from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi, get_critical_kpi"
    )

if "validate_kpi_with_safe_gate" not in content:
    content = content.replace(
        "from ..kpi_extractor import (\n    KPIExtractor,",
        "from ..kpi_extractor import (\n    KPIExtractor, \n    validate_kpi_with_safe_gate,"
    )

# Find the specific validation block inside assemble() method
old_validation_pattern = r'(def assemble\(self\).*?# \[Phase 3\.10 Final Lock\] Extract KPI using new extractor\s+mandatory_kpi = get_mandatory_kpi\(self\.report_type\)\s+modules_data = self\._extract_module_data\(\s+\{[^}]+\},\s+mandatory_kpi\s+\)\s+# \[Phase 3\.10 Final Lock\] HARD-FAIL: Validate mandatory KPI\s+missing_kpi = validate_mandatory_kpi.*?return \{[^}]+\}[^}]+\}\s+\})'

# Replace with SAFE-GATE
new_validation = '''def assemble(self) -> Dict[str, str]:
        """Assemble All-In-One comprehensive report"""
        m2_html_raw = self.load_module_html("M2")
        m3_html_raw = self.load_module_html("M3")
        m4_html_raw = self.load_module_html("M4")
        m5_html_raw = self.load_module_html("M5")
        m6_html_raw = self.load_module_html("M6")
        
        m2_html = self.sanitize_module_html(m2_html_raw, "M2")
        m3_html = self.sanitize_module_html(m3_html_raw, "M3")
        m4_html = self.sanitize_module_html(m4_html_raw, "M4")
        m5_html = self.sanitize_module_html(m5_html_raw, "M5")
        m6_html = self.sanitize_module_html(m6_html_raw, "M6")
        
        # [Phase 3.10 Final Lock + vPOST-FINAL] Extract KPI using SAFE-GATE
        mandatory_kpi = get_mandatory_kpi(self.report_type)
        critical_kpi = get_critical_kpi(self.report_type)
        modules_data = self._extract_module_data(
            {"M2": m2_html, "M3": m3_html, "M4": m4_html, "M5": m5_html, "M6": m6_html},
            mandatory_kpi
        )
        
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

import re

# More specific: find just the validation block, not the entire method
validation_block_pattern = r'        # \[Phase 3\.10 Final Lock\] Extract KPI using new extractor.*?            \}\n        \}'

if re.search(validation_block_pattern, content, re.DOTALL):
    replacement = '''        # [Phase 3.10 Final Lock + vPOST-FINAL] Extract KPI using SAFE-GATE
        mandatory_kpi = get_mandatory_kpi(self.report_type)
        critical_kpi = get_critical_kpi(self.report_type)
        modules_data = self._extract_module_data(
            {"M2": m2_html, "M3": m3_html, "M4": m4_html, "M5": m5_html, "M6": m6_html},
            mandatory_kpi
        )
        
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
    
    content = re.sub(validation_block_pattern, replacement, content, flags=re.DOTALL)
    print("✅ Validation block replaced")
else:
    print("⚠️  Pattern not found")

# Add panel to sections
if "data_completeness_panel," not in content:
    content = content.replace(
        "sections = [\n            self._generate_cover_page(),",
        "sections = [\n            self._generate_cover_page(),\n            data_completeness_panel,"
    )
    print("✅ Panel inserted")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ all_in_one.py updated")
