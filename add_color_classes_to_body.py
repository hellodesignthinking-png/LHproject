#!/usr/bin/env python3
"""Add report-type color classes to body tags in all assemblers"""

from pathlib import Path

ASSEMBLER_DIR = Path("app/services/final_report_assembly/assemblers")

color_mappings = {
    "landowner_summary": "report-color-landowner",
    "lh_technical": "report-color-lh_technical",
    "quick_check": "report-color-quick",
    "financial_feasibility": "report-color-financial",
    "all_in_one": "report-color-all",
    "executive_summary": "report-color-executive"
}

assemblers = [
    "landowner_summary.py",
    "lh_technical.py",
    "quick_check.py",
    "financial_feasibility.py",
    "all_in_one.py",
    "executive_summary.py"
]

for assembler in assemblers:
    file_path = ASSEMBLER_DIR / assembler
    content = file_path.read_text(encoding='utf-8')
    
    # Get report type (remove .py extension)
    report_type = assembler.replace(".py", "")
    color_class = color_mappings[report_type]
    
    # Replace body tag pattern
    old_pattern = f'<body class="final-report {report_type}">'
    
    # Add density class for specific reports
    if report_type == "all_in_one":
        new_pattern = f'<body class="final-report dense-report {color_class} {report_type}">'
    elif report_type == "executive_summary":
        new_pattern = f'<body class="final-report compact-report {color_class} {report_type}">'
    else:
        new_pattern = f'<body class="final-report {color_class} {report_type}">'
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ {assembler}: Added '{color_class}'")
    else:
        print(f"⚠️  {assembler}: Pattern not found: {old_pattern[:60]}...")

print("\n✅ All color classes added!")
