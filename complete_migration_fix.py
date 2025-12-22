"""Complete migration fix for all remaining old code"""
import re
from pathlib import Path

def fix_assembler(filepath: Path, report_name: str, modules: list) -> None:
    """Fix a single assembler"""
    print(f"\n🔧 Fixing {filepath.name}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the old _extract_module_data call
    module_dict = "{" + ", ".join([f'"{m}": {m.lower()}_html' for m in modules]) + "}"
    old_call_pattern = rf'modules_data = self\._extract_module_data\({re.escape(module_dict)}\)'
    
    # Check if old call exists
    if re.search(old_call_pattern, content):
        print(f"  ❌ Found old _extract_module_data call - replacing...")
        
        # Build new code block
        module_list_str = ', '.join([f'"{m}"' for m in modules])
        new_code = f'''# [Phase 3.10 Final Lock] Extract KPI using new pipeline
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
            }}'''
        
        content = re.sub(old_call_pattern, new_code, content)
        
        # Also remove any subsequent try/except blocks for old binding
        try_except_pattern = r'\n\s+# \[Phase 3\.10\] HARD-FAIL:.*?\n\s+try:.*?^\s+\}$'
        content = re.sub(try_except_pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # Remove old kpi_summary generation if it's using old pattern
        old_kpi_gen = r'kpi_summary = self\.generate_kpi_summary_box\(bound_kpis, self\.report_type\)'
        if re.search(old_kpi_gen, content):
            content = re.sub(old_kpi_gen, '', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Fixed")
    else:
        print(f"  ℹ️  Already migrated or no old call found")

def main():
    assemblers_dir = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")
    
    # Define assemblers and their modules
    assemblers = {
        "financial_feasibility.py": ["M2", "M4", "M5"],
        "lh_technical.py": ["M3", "M4", "M6"],
        "all_in_one.py": ["M2", "M3", "M4", "M5", "M6"],
        "executive_summary.py": ["M2", "M5", "M6"],
    }
    
    print("=" * 80)
    print("Complete Migration Fix")
    print("=" * 80)
    
    for filename, modules in assemblers.items():
        filepath = assemblers_dir / filename
        if filepath.exists():
            fix_assembler(filepath, filename.replace('.py', ''), modules)

if __name__ == "__main__":
    main()
