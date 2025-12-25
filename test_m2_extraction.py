import sys
sys.path.append('/home/user/webapp')

from app.services.context_storage import context_storage
from app.services.module_html_adapter import adapt_m2_summary_for_html
from app.services.module_html_renderer import render_module_html
from app.services.final_report_assembly.kpi_extractor import KPIExtractor

context_id = "116801010001230045"
frozen_context = context_storage.get_frozen_context(context_id)

if frozen_context:
    canonical_summary = frozen_context.get("canonical_summary", {})
    
    # Adapt M2
    m2_adapted = adapt_m2_summary_for_html(canonical_summary)
    print("\nM2 Adapted Data:")
    print(f"  total_value: {m2_adapted.get('appraisal_result', {}).get('total_value')}")
    print(f"  fallback: {m2_adapted.get('fallback')}")
    
    # Render M2 HTML
    m2_html = render_module_html("M2", m2_adapted)
    
    # Extract from HTML
    root = KPIExtractor.get_module_root(m2_html, "M2")
    raw_kpi = KPIExtractor.extract_raw_kpi_from_root(root)
    
    print("\nM2 Extracted KPI:")
    for key, val in raw_kpi.items():
        print(f"  {key}: {val}")
else:
    print("Context not found")
