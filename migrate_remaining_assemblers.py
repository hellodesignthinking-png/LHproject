"""
Phase 3.10 Final Lock: Migrate Remaining 4 Assemblers
Applies Landowner Summary pattern to all remaining assemblers
"""

import re
from pathlib import Path

def migrate_assembler(filepath: Path, module_list: list) -> bool:
    """
    Migrate assembler to new KPI pipeline
    
    Args:
        filepath: Path to assembler file
        module_list: List of module IDs (e.g., ["M2", "M5", "M6"])
    """
    print(f"\n📄 Migrating {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Step 1: Remove old extraction methods
    print("  🗑️  Removing old extraction methods...")
    
    # Remove _extract_kpi_from_module_html
    pattern1 = r'    def _extract_kpi_from_module_html\(.*?\n(?:.*?\n)*?        return kpis\n'
    content = re.sub(pattern1, '', content, flags=re.DOTALL)
    
    # Remove _extract_module_data
    pattern2 = r'    def _extract_module_data\(.*?\n(?:.*?\n)*?        return modules_data\n'
    content = re.sub(pattern2, '', content, flags=re.DOTALL)
    
    # Step 2: Replace KPI extraction block
    print("  🔄 Replacing KPI extraction block...")
    
    # Build module dict string
    module_dict_str = ', '.join([f'"{m}": {m.lower()}_html' for m in module_list])
    module_list_str = ', '.join([f'"{m}"' for m in module_list])
    
    # Old pattern (flexible to match variations)
    old_patterns = [
        r'        modules_data = self\._extract_module_data\(\{.*?\}\)\s*\n\s*# \[Phase 3\.10\].*?(?=\n        # Generate|exec_summary|# \[FIX)',
    ]
    
    # New block (Landowner Summary pattern)
    new_block = f'''        # [Phase 3.10 Final Lock] Extract KPI using new pipeline
        required_map = MANDATORY_KPI[self.report_type]
        modules_data = {{}}
        
        for module_id in [{module_list_str}]:
            html = self.load_module_html(module_id)
            required_keys = required_map.get(module_id, [])
            modules_data[module_id] = KPIExtractor.extract_module_kpi(
                html=html,
                module_id=module_id,
                required_keys=required_keys
            )
        
        # [Phase 3.10 Final Lock] Hard-Fail validation
        missing = []
        for module_id, keys in required_map.items():
            for k in keys:
                if modules_data.get(module_id, {{}}).get(k) is None:
                    missing.append(f"{{module_id}}.{{k}}")
        
        if missing:
            error_msg = f"[BLOCKED] Missing required KPI: {{', '.join(missing)}}"
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
            }}
        
        # Generate KPI summary from modules_data
        kpi_summary = self.generate_kpi_summary_box(modules_data, self.report_type)
'''
    
    for pattern in old_patterns:
        if re.search(pattern, content, flags=re.DOTALL):
            content = re.sub(pattern, new_block, content, flags=re.DOTALL)
            break
    
    # Step 3: Clean up old imports
    print("  🧹 Cleaning up old imports...")
    content = re.sub(r'from \.\.kpi_hard_fail_enforcement import.*?\n', '', content)
    content = re.sub(r'from app\.services\.final_report_assembly\.kpi_extraction_vlast import.*?\n', '', content)
    
    # Check if anything changed
    if content == original:
        print("  ⚠️  No changes made (pattern may need adjustment)")
        return False
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("  ✅ Migration complete")
    return True

def main():
    assemblers_dir = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")
    
    # Define assemblers and their modules
    assemblers = {
        "financial_feasibility.py": ["M2", "M5"],
        "lh_technical.py": ["M3", "M4", "M6"],
        "all_in_one.py": ["M2", "M3", "M4", "M5", "M6"],
        "executive_summary.py": ["M2", "M5", "M6"],
    }
    
    print("=" * 80)
    print("Phase 3.10 Final Lock: Migrating Remaining 4 Assemblers")
    print("=" * 80)
    
    success_count = 0
    
    for filename, modules in assemblers.items():
        filepath = assemblers_dir / filename
        if not filepath.exists():
            print(f"\n❌ {filename}: Not found")
            continue
        
        if migrate_assembler(filepath, modules):
            success_count += 1
    
    print("\n" + "=" * 80)
    print(f"✅ Migration Complete: {success_count}/{len(assemblers)} assemblers")
    print("=" * 80)

if __name__ == "__main__":
    main()
