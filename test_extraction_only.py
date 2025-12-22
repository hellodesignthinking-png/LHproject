#!/usr/bin/env python3
"""Test Phase 3.9 KPI Extraction Only"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bs4 import BeautifulSoup

# Sample M2 HTML
m2_html = """
<div class="module-m2" data-module="M2">
    <h2>M2 - 토지 감정 평가</h2>
    <div class="kpi-summary">
        <div class="kpi-item" data-land-value="5600000000" data-land-value-total="5600000000" data-land-value-per-pyeong="5500000">
            <span class="label">총 토지 감정가</span>
            <span class="value">5,600,000,000원</span>
        </div>
    </div>
</div>
"""

print("\n" + "="*80)
print("🧪 TEST: Phase 3.9 KPI Extraction from HTML")
print("="*80 + "\n")

# Parse HTML
soup = BeautifulSoup(m2_html, 'html.parser')

# Method 1: data-* attributes
print("Method 1: data-* attributes")
kpi_items = soup.find_all(attrs=lambda attrs: attrs and any(k.startswith('data-') for k in attrs))
for item in kpi_items:
    print(f"  Found element: {item.name}")
    for attr in item.attrs:
        if attr.startswith('data-'):
            print(f"    {attr}: {item[attr]}")

# Try to extract land_value_per_pyeong specifically
print("\nTrying to extract land_value_per_pyeong:")
for tag in soup.find_all(True):  # All tags
    if tag.has_attr('data-land-value-per-pyeong'):
        print(f"  ✅ Found in <{tag.name}>: {tag['data-land-value-per-pyeong']}")

print("\n" + "="*80 + "\n")
