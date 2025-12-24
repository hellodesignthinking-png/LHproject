#!/usr/bin/env python3
"""
FIX: Add data-* attributes to Module HTML Renderer
=====================================================

PROBLEM:
    Phase 3.9/3.10 extraction logic relies on data-* attributes,
    but module_html_renderer.py doesn't include them.
    
    Result: Final Reports can't extract KPIs from module HTML.

SOLUTION:
    Patch all M2-M6 render functions to include:
    - data-module="M2" (module identifier)
    - data-{field-name}="{value}" for all KPI fields
    
Author: ZeroSite Backend Team
Date: 2025-12-22
"""

import re
from pathlib import Path

def add_data_attributes_to_m2(content: str) -> str:
    """Add data-* attributes to M2 renderer"""
    
    # Find M2 render function
    pattern = r'(def _render_m2_html\(data: Dict\[str, Any\]\) -> str:.*?"""Render M2.*?""")'
    
    # Add after the function starts, insert data attribute generation
    replacement = r'''\1
    
    # Extract KPI values for data-* attributes
    land_value_total = data.get("land_value_total", 0)
    land_value_per_pyeong = data.get("land_value_per_pyeong", 0)
    land_area = data.get("land_area", 0)
    '''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Find the main container div and add data attributes
    # Pattern: <div class="container">
    container_pattern = r'(<div class="container">)'
    container_replacement = r'<div class="container" data-module="M2" data-land-value-total="{land_value_total}" data-land-value-per-pyeong="{land_value_per_pyeong}" data-land-area="{land_area}">'
    
    content = content.replace(
        '<div class="container">',
        '<div class="container" data-module="M2" data-land-value-total="{land_value_total}" data-land-value-per-pyeong="{land_value_per_pyeong}" data-land-area="{land_area}">'
    )
    
    return content


def add_data_attributes_to_m3(content: str) -> str:
    """Add data-* attributes to M3 renderer"""
    
    # Find the key-result-card div
    pattern = r'(<div class="key-result-card">)'
    replacement = r'<div class="key-result-card" data-module="M3" data-recommended-type="{rec_type[\'name\']}" data-total-score="{rec_type[\'score\']}" data-grade="{rec_type[\'grade\']}">'
    
    content = content.replace(
        '<div class="key-result-card">',
        replacement
    )
    
    return content


def add_data_attributes_to_m4(content: str) -> str:
    """Add data-* attributes to M4 renderer"""
    
    # Find the container or key section
    pattern = r'(<div class="container">)'
    replacement = r'<div class="container" data-module="M4" data-total-units="{total_units}" data-floor-area="{total_floor_area}">'
    
    content = content.replace(
        '<div class="container">',
        replacement
    )
    
    return content


def add_data_attributes_to_m5(content: str) -> str:
    """Add data-* attributes to M5 renderer"""
    
    pattern = r'(<div class="container">)'
    replacement = r'<div class="container" data-module="M5" data-npv="{npv_value}" data-irr="{irr_value}" data-is-profitable="{is_profitable}">'
    
    content = content.replace(
        '<div class="container">',
        replacement
    )
    
    return content


def add_data_attributes_to_m6(content: str) -> str:
    """Add data-* attributes to M6 renderer"""
    
    pattern = r'(<div class="container">)'
    replacement = r'<div class="container" data-module="M6" data-decision="{lh_decision}" data-risk-summary="{risk_summary}">'
    
    content = content.replace(
        '<div class="container">',
        replacement
    )
    
    return content


def main():
    renderer_path = Path("/home/user/webapp/app/services/module_html_renderer.py")
    
    print("\n" + "="*80)
    print("🔧 FIX: Adding data-* attributes to Module HTML Renderer")
    print("="*80 + "\n")
    
    # Read current content
    content = renderer_path.read_text()
    print(f"📄 Read {len(content):,} bytes from module_html_renderer.py")
    
    # Check if already patched
    if 'data-module="M2"' in content:
        print("✅ Already patched! data-* attributes found.")
        return
    
    print("\n🔄 Applying patches...\n")
    
    # Apply all patches
    original_len = len(content)
    
    # Note: Due to the complexity of the HTML structure,
    # we'll need to manually inspect and patch each function.
    # For now, let's create a detailed instruction.
    
    print("⚠️  Manual patching required!")
    print("\nInstructions:")
    print("1. For each _render_m*_html() function:")
    print("   - Add data-* attributes to the main container or key-result-card")
    print("   - Include all KPI fields from KPI_CANONICAL_SCHEMA")
    print("\n2. KPI fields to include:")
    print("   M2: data-land-value-total, data-land-value-per-pyeong")
    print("   M3: data-recommended-type, data-total-score, data-grade")
    print("   M4: data-total-units, data-floor-area")
    print("   M5: data-npv, data-irr, data-is-profitable")
    print("   M6: data-decision, data-risk-summary")
    print("\n" + "="*80 + "\n")
    
    # Since automatic patching is complex, let's create a NEW version
    print("📝 Creating detailed patch plan...\n")
    
    # Detect function boundaries
    functions = re.findall(r'def (_render_m\d_html)\(.*?\):', content)
    print(f"Found {len(functions)} module render functions: {functions}")
    
    return functions


if __name__ == "__main__":
    main()
