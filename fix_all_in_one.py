#!/usr/bin/env python3
"""
Fix all_in_one.py: Complete KPI extraction migration
"""

import re

filepath = "app/services/final_report_assembly/assemblers/all_in_one.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: Find the extraction block after module sanitization
old_pattern = r'(\s+# Extract data from modules\s+modules_data = \{\s+["\']M2["\']: \{[^}]+\},\s+["\']M3["\']: \{[^}]+\},\s+["\']M4["\']: \{[^}]+\},\s+["\']M5["\']: \{[^}]+\},\s+["\']M6["\']: \{[^}]+\},?\s+\})'

new_block = '''
        # [Phase 3.10] Unified KPI Extraction with Hard-Fail Validation
        report_type = "all_in_one"
        required_map = MANDATORY_KPI.get(report_type, {})
        
        modules_data = {}
        for module_id in ["M2", "M3", "M4", "M5", "M6"]:
            html = module_htmls.get(module_id, "")
            required_keys = required_map.get(module_id, [])
            modules_data[module_id] = KPIExtractor.extract_module_kpi(html, module_id, required_keys)
        
        # Hard-Fail validation: Check mandatory KPIs
        missing = []
        for module_id, keys in required_map.items():
            for k in keys:
                if modules_data.get(module_id, {}).get(k) is None:
                    missing.append(f"{module_id}.{k}")
        
        if missing:
            raise FinalReportAssemblyError(
                f"[BLOCKED] All-In-One report generation failed: Missing required KPI: {missing}"
            )
        
        # Log extraction status
        logger.info(f"[Phase 3.10] All-In-One KPI extraction complete: {list(modules_data.keys())}")
'''

if re.search(old_pattern, content, re.DOTALL):
    content = re.sub(old_pattern, new_block, content, flags=re.DOTALL)
    print("✅ Found and replaced old extraction pattern")
else:
    # Fallback: Replace any remaining _extract_module_data call
    if "modules_data = self._extract_module_data({" in content:
        # Find the full call
        start = content.find("modules_data = self._extract_module_data({")
        if start != -1:
            # Find the closing }
            depth = 0
            i = start + len("modules_data = self._extract_module_data(")
            while i < len(content):
                if content[i] == '{':
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            
            old_call = content[start:i+2]  # Include closing )
            content = content.replace(old_call, new_block.strip())
            print("✅ Replaced _extract_module_data call")
    else:
        print("⚠️  No old pattern found - may already be migrated")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ All-In-One migration complete")
