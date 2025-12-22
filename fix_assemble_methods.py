#!/usr/bin/env python3
"""
Fix assemble() methods in 4 assemblers to use _extract_module_data() pattern
"""

import re

fixes = {
    "quick_check.py": {
        "modules": ["M5", "M6"],
        "start_marker": "# [Phase 3.10 Final Lock] Extract KPI using new pipeline",
        "end_marker": "            }",
    },
    "financial_feasibility.py": {
        "modules": ["M2", "M4", "M5"],
        "start_marker": "# [Phase 3.10 Final Lock] Extract KPI using new pipeline",
        "end_marker": "            }",
    },
    "all_in_one.py": {
        "modules": ["M2", "M3", "M4", "M5", "M6"],
        "start_marker": "# [Phase 3.10 Final Lock] Extract KPI using new pipeline",
        "end_marker": "            }",
    },
    "executive_summary.py": {
        "modules": ["M2", "M5", "M6"],
        "start_marker": "# [Phase 3.10 Final Lock] Extract KPI using new pipeline",
        "end_marker": "            }",
    },
}

for filename, config in fixes.items():
    filepath = f"app/services/final_report_assembly/assemblers/{filename}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the section to replace
    # Look for the old inline extraction pattern
    old_pattern = r'# \[Phase 3\.10 Final Lock\] Extract KPI using new pipeline\s+mandatory_kpi = get_mandatory_kpi\(self\.report_type\)\s+modules_data = \{\}.*?# \[Phase 3\.10 Final Lock\] Hard-Fail validation.*?            \}'
    
    modules_str = ', '.join([f'"{m}"' for m in config["modules"]])
    modules_dict = '{' + ', '.join([f'"{m}": {m.lower()}_html' for m in config["modules"]]) + '}'
    
    new_block = f'''# [Phase 3.10 Final Lock] Extract KPI using new pipeline
        mandatory_kpi = get_mandatory_kpi(self.report_type)
        modules_data = self._extract_module_data(
            {modules_dict},
            mandatory_kpi
        )
        
        # [Phase 3.10 Final Lock] HARD-FAIL: Validate mandatory KPI
        missing_kpi = validate_mandatory_kpi(self.report_type, modules_data, {{self.report_type: mandatory_kpi}})
        if missing_kpi:
            error_msg = f"[BLOCKED] Missing required KPI: {{', '.join(missing_kpi)}}"
            logger.error(f"[{{self.report_type}}] {{error_msg}}")
            return {{
                "html": f"<html><body><h1>❌ Report Generation Blocked</h1><pre>{{error_msg}}</pre></body></html>",
                "qa_result": {{
                    "status": "FAIL",
                    "errors": [error_msg],
                    "warnings": [],
                    "blocking": True,
                    "reason": "Hard-Fail: Required KPI missing"
                }}
            }}'''
    
    if re.search(old_pattern, content, re.DOTALL):
        content = re.sub(old_pattern, new_block, content, flags=re.DOTALL)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename}")
    else:
        print(f"⚠️  {filename} - pattern not found")

print("\n✅ Assemble methods fixed")
