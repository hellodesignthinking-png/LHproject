#!/usr/bin/env python3
"""
vABSOLUTE-FINAL-15: M6 HTML Pipeline Connection
================================================

Problem: M6 HTML adapter exists but not called before report generation
Solution: Inject HTML generation step into assembler pipeline

This fixes the final missing link:
  canonical_summary["M6"] exists ✅
  adapt_m6_summary_for_html() exists ✅
  module_htmls["M6"] generation ❌ <- FIX THIS
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.module_html_adapter import (
    adapt_m6_summary_for_html,
    adapt_m5_summary_for_html,
    adapt_m4_summary_for_html,
    adapt_m3_summary_for_html,
    adapt_m2_summary_for_html
)

def generate_module_htmls_from_canonical(canonical_summary: dict) -> dict:
    """
    Generate module HTMLs from canonical_summary
    
    This is the missing pipeline step that needs to run
    BEFORE assembler.assemble()
    
    Args:
        canonical_summary: Complete M2-M6 data
    
    Returns:
        module_htmls: Dict with HTML for each module
    """
    module_htmls = {}
    
    # Generate M2 HTML
    if "M2" in canonical_summary:
        m2_adapted = adapt_m2_summary_for_html(canonical_summary)
        module_htmls["M2"] = _render_module_html("M2", m2_adapted)
    
    # Generate M3 HTML
    if "M3" in canonical_summary:
        m3_adapted = adapt_m3_summary_for_html(canonical_summary)
        module_htmls["M3"] = _render_module_html("M3", m3_adapted)
    
    # Generate M4 HTML
    if "M4" in canonical_summary:
        m4_adapted = adapt_m4_summary_for_html(canonical_summary)
        module_htmls["M4"] = _render_module_html("M4", m4_adapted)
    
    # Generate M5 HTML
    if "M5" in canonical_summary:
        m5_adapted = adapt_m5_summary_for_html(canonical_summary)
        module_htmls["M5"] = _render_module_html("M5", m5_adapted)
    
    # Generate M6 HTML (CRITICAL)
    if "M6" in canonical_summary:
        m6_adapted = adapt_m6_summary_for_html(canonical_summary)
        module_htmls["M6"] = _render_module_html("M6", m6_adapted)
    
    return module_htmls


def _render_module_html(module_id: str, adapted_data: dict) -> str:
    """
    Render adapted data as HTML with data-module attribute
    
    This ensures KPIExtractor can find module root via:
    section[data-module='M6'] or div[data-module='M6']
    """
    import json
    
    # Build HTML with proper structure for KPI extraction
    html_parts = [
        f'<section data-module="{module_id}" class="module-section">',
        f'<h2>{adapted_data.get("title", module_id)}</h2>',
        '<div class="module-content">',
    ]
    
    # Embed data as data-* attributes for KPI extraction
    if module_id == "M2" and "land_value_total" in adapted_data:
        html_parts.append(f'<div data-land-value-total="{adapted_data["land_value_total"]}"></div>')
    
    if module_id == "M3" and "recommended_type" in adapted_data:
        rec_type = adapted_data["recommended_type"]
        if isinstance(rec_type, dict):
            html_parts.append(f'<div data-recommended-type="{rec_type.get("name", "")}"></div>')
    
    if module_id == "M4" and "total_units" in adapted_data:
        html_parts.append(f'<div data-total-units="{adapted_data["total_units"]}"></div>')
    
    if module_id == "M5":
        if "npv" in adapted_data:
            html_parts.append(f'<div data-npv="{adapted_data["npv"]}"></div>')
        if "irr" in adapted_data:
            html_parts.append(f'<div data-irr="{adapted_data["irr"]}"></div>')
        if "roi" in adapted_data:
            html_parts.append(f'<div data-roi="{adapted_data["roi"]}"></div>')
    
    if module_id == "M6" and "review_result" in adapted_data:
        result = adapted_data["review_result"]
        html_parts.append(f'<div data-decision="{result.get("decision", "")}"></div>')
        html_parts.append(f'<div data-total-score="{result.get("total_score", 0)}"></div>')
        html_parts.append(f'<div data-grade="{result.get("grade", "")}"></div>')
    
    # Close tags
    html_parts.extend([
        '</div>',  # module-content
        '</section>'  # module-section
    ])
    
    return '\n'.join(html_parts)


# Test
if __name__ == "__main__":
    from app.services.context_storage import context_storage
    
    context_id = "test-vabs14-20251224-032117"
    frozen_context = context_storage.get_frozen_context(context_id)
    
    if not frozen_context:
        print("❌ Context not found")
        sys.exit(1)
    
    canonical_summary = frozen_context.get("canonical_summary", {})
    
    if not canonical_summary:
        print("❌ canonical_summary not found")
        sys.exit(1)
    
    print("=== GENERATING MODULE HTMLs ===")
    module_htmls = generate_module_htmls_from_canonical(canonical_summary)
    
    for module_id, html in module_htmls.items():
        has_data_module = f'data-module="{module_id}"' in html
        print(f"{'✅' if has_data_module else '❌'} {module_id}: {len(html)} chars, data-module={has_data_module}")
        
        if module_id == "M6":
            has_decision = 'data-decision' in html
            print(f"   {'✅' if has_decision else '❌'} M6 has data-decision attribute")
            if has_decision:
                import re
                match = re.search(r'data-decision="([^"]+)"', html)
                if match:
                    print(f"   Decision value: {match.group(1)}")
    
    print(f"\n✅ MODULE_HTMLS READY: {list(module_htmls.keys())}")
