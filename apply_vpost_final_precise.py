#!/usr/bin/env python3
"""
Apply vPOST-FINAL pattern to quick_check and lh_technical assemblers
Surgical precision editing
"""
import re

def apply_vpost_final(file_path: str, modules: list[str]):
    """Apply vPOST-FINAL pattern to an assembler"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix imports
    old_import = r'from \.\.report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi\n\n# \[Phase 3\.10 Final Lock\] KPI Extractor\nfrom \.\.kpi_extractor import KPIExtractor.*'
    new_import = '''from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi, get_critical_kpi

# [Phase 3.10 Final Lock + vPOST-FINAL] KPI Extractor with operational safety
from ..kpi_extractor import (
    KPIExtractor, 
    validate_mandatory_kpi, 
    validate_kpi_with_safe_gate,
    log_kpi_pipeline, 
    FinalReportAssemblyError
)'''
    
    content = re.sub(old_import, new_import, content, flags=re.DOTALL)
    
    # 2. Replace Hard-Fail validation block
    # Build module dict pattern
    module_dict = ", ".join([f'"{m}": {m}_html' for m in modules])
    
    old_validation = rf'''        # \[Phase 3\.10 Final Lock\] Extract KPI using new pipeline
        mandatory_kpi = get_mandatory_kpi\(self\.report_type\)
        modules_data = self\._extract_module_data\(
            \{{{module_dict}\}},
            mandatory_kpi
        \)
        
        # \[Phase 3\.10 Final Lock\] HARD-FAIL: Validate mandatory KPI
        missing_kpi = validate_mandatory_kpi\(self\.report_type, modules_data, \{{self\.report_type: mandatory_kpi\}}\)
        if missing_kpi:
            error_msg = f"\[BLOCKED\] Missing required KPI: \{{', '\.join\(missing_kpi\)\}}"
            logger\.error\(f"\[{{self\.report_type\}}\] \{{error_msg\}}"\)
            return \{{
                "html": f"<html><body><h1>❌ Report Generation Blocked</h1><pre>\{{error_msg\}}</pre></body></html>",
                "qa_result": \{{
                    "status": "FAIL",
                    "errors": \[error_msg\],
                    "warnings": \[\],
                    "blocking": True,
                    "reason": "Hard-Fail: Required KPI missing"
                \}}
            \}}'''
    
    new_validation = f'''        # [Phase 3.10 Final Lock + vPOST-FINAL] Extract KPI using SAFE-GATE
        mandatory_kpi = get_mandatory_kpi(self.report_type)
        critical_kpi = get_critical_kpi(self.report_type)
        modules_data = self._extract_module_data(
            {{{module_dict}}},
            mandatory_kpi
        )
        
        # [vPOST-FINAL] SAFE-GATE Validation: Critical vs Soft failures
        validation_result = validate_kpi_with_safe_gate(
            self.report_type, 
            modules_data, 
            {{self.report_type: mandatory_kpi}},
            {{self.report_type: critical_kpi}}
        )
        
        critical_missing = validation_result["critical_missing"]
        soft_missing = validation_result["soft_missing"]
        
        # Hard-Fail ONLY if CRITICAL KPI is missing
        if critical_missing:
            error_msg = f"[BLOCKED] Missing CRITICAL KPI: {{', '.join(critical_missing)}}"
            logger.error(f"[{{self.report_type}}] {{error_msg}}")
            return {{
                "html": f"<html><body><h1>🚫 Report Generation Blocked</h1><pre>{{error_msg}}</pre><p>These KPIs are critical for decision-making and must be present.</p></body></html>",
                "qa_result": {{
                    "status": "FAIL",
                    "errors": [error_msg],
                    "warnings": [f"Soft KPI missing: {{', '.join(soft_missing)}}"] if soft_missing else [],
                    "blocking": True,
                    "reason": "Hard-Fail: Critical KPI missing"
                }}
            }}
        
        # Generate data completeness panel if soft KPIs are missing
        data_completeness_panel = self.generate_data_completeness_panel(soft_missing)'''
    
    content = re.sub(old_validation, new_validation, content, flags=re.DOTALL)
    
    # 3. Insert data_completeness_panel into sections array
    # Find first occurrence of "sections = [" and insert after cover page
    sections_pattern = r'(sections = \[\s+self\._generate_cover_page\(\),)'
    sections_replacement = r'\1\n            data_completeness_panel,'
    
    content = re.sub(sections_pattern, sections_replacement, content)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Applied vPOST-FINAL to {file_path}")

# Apply to quick_check (M5, M6)
apply_vpost_final('app/services/final_report_assembly/assemblers/quick_check.py', ['M5', 'M6'])

# Apply to lh_technical (M3, M4, M6)
apply_vpost_final('app/services/final_report_assembly/assemblers/lh_technical.py', ['M3', 'M4', 'M6'])

print("\n✅ vPOST-FINAL applied to all remaining assemblers")
