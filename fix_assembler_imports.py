"""Fix imports in all assemblers"""
import re
from pathlib import Path

assemblers_dir = Path("/home/user/webapp/app/services/final_report_assembly/assemblers")

for file in ["quick_check.py", "financial_feasibility.py", "lh_technical.py", "all_in_one.py", "executive_summary.py"]:
    filepath = assemblers_dir / file
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure MANDATORY_KPI and KPIExtractor are imported
    if 'from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi' not in content:
        content = re.sub(
            r'from \.\.report_type_configs import REPORT_TYPE_CONFIGS',
            'from ..report_type_configs import REPORT_TYPE_CONFIGS, MANDATORY_KPI',
            content
        )
    
    if 'from ..kpi_extractor import KPIExtractor' not in content:
        # Add after report_type_configs import
        content = re.sub(
            r'(from \.\.report_type_configs import.*?\n)',
            r'\1from ..kpi_extractor import KPIExtractor\n',
            content
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {file}")
