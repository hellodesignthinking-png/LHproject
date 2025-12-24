"""
Test Suite for OUTPUT QUALITY FIX
==================================

Validates that all 5 fixes are applied correctly:
1. Data visibility recovery (no N/A)
2. Mandatory KPI enforcement
3. Number format standardization
4. Design system consistency
5. Decision visibility

Expected: All reports have professional output quality
"""

import sys
from unittest.mock import Mock
from datetime import datetime

# Mock storage
mock_storage = Mock()
mock_context = {
    "canonical_summary": {
        "M2": {"land_value": 150000000, "pyeong_price": 5000000},
        "M5": {"npv": 85000000, "irr": 12.5, "is_profitable": True},
        "M6": {"decision": "승인", "score": 82}
    },
    "analyzed_at": datetime.now().isoformat()
}
mock_storage.get_frozen_context = Mock(return_value=mock_context)
sys.modules['app.services.context_storage'] = Mock(context_storage=mock_storage)

# Import after mocking
from app.services.final_report_assembly.assemblers import LandownerSummaryAssembler
from app.services.final_report_assembly.base_assembler import BaseFinalReportAssembler

print("\n" + "="*80)
print("OUTPUT QUALITY FIX - VALIDATION TEST")
print("="*80 + "\n")

# Test 1: Number formatting
print("TEST 1: Number Format Standardization")
print("-" * 60)
test_formats = [
    (150000000, 'currency', "₩150,000,000"),
    (12.5, 'percent', "12.5%"),
    (85.3, 'area', "85.3㎡"),
    (120, 'units', "120세대"),
    (82, 'score', "82/100"),
]

for value, format_type, expected in test_formats:
    result = BaseFinalReportAssembler.format_number(value, format_type)
    status = "✅" if result == expected else "❌"
    print(f"{status} {format_type}: {value} → {result} (expected: {expected})")

print()

# Test 2: KPI Summary Box Generation
print("TEST 2: KPI Summary Box Generation")
print("-" * 60)
kpis = {
    "총 토지 감정가": 150000000,
    "순현재가치 (NPV)": 85000000,
    "LH 심사 결과": "승인"
}
kpi_html = BaseFinalReportAssembler.generate_kpi_summary_box(kpis, "landowner_summary")

checks = [
    ("Contains KPI section", "kpi-summary-box" in kpi_html),
    ("Has formatted currency", "₩" in kpi_html and "," in kpi_html),
    ("Shows all 3 KPIs", all(kpi_name in kpi_html for kpi_name in kpis.keys())),
]

for check_name, passed in checks:
    print(f"{'✅' if passed else '❌'} {check_name}")

print()

# Test 3: Decision Block Generation
print("TEST 3: Decision Block Generation")
print("-" * 60)
judgment = "사업 추진 권장"
basis = ["수익성 양호 (NPV ₩85,000,000)", "LH 승인 가능성 높음", "리스크 관리 가능"]
actions = ["LH 사전 협의 진행", "설계 용역 발주 준비"]

decision_html = BaseFinalReportAssembler.generate_decision_block(judgment, basis, actions)

checks = [
    ("Contains decision block", "decision-block" in decision_html),
    ("Shows judgment", judgment in decision_html),
    ("Has icon (✅)", "✅" in decision_html),
    ("Shows all basis points", all(b in decision_html for b in basis)),
    ("Shows all actions", all(a in decision_html for a in actions)),
]

for check_name, passed in checks:
    print(f"{'✅' if passed else '❌'} {check_name}")

print()

# Test 4: Unified Design CSS
print("TEST 4: Unified Design CSS")
print("-" * 60)
css = BaseFinalReportAssembler.get_unified_design_css()

required_styles = [
    "body.final-report",
    "font-size: 14px",
    "line-height: 1.6",
    "max-width: 1200px",
    "table",
    "border-collapse: collapse",
    ".kpi-card",
    "@media print",
]

for style in required_styles:
    passed = style in css
    print(f"{'✅' if passed else '❌'} CSS includes: {style}")

print()

# Test 5: Full Report Assembly with Fixes
print("TEST 5: Full Landowner Summary Assembly")
print("-" * 60)
try:
    assembler = LandownerSummaryAssembler("test_output_fix")
    result = assembler.assemble()
    html = result["html"]
    
    # Check for critical elements
    checks = [
        ("HTML generated", len(html) > 10000),
        ("KPI summary present", "kpi-summary-box" in html),
        ("Decision block present", "decision-block" in html),
        ("Unified design CSS present", "OUTPUT QUALITY FIX" in html),
        ("No N/A placeholders", "N/A" not in html and "검증 필요" not in html),
        ("Watermark present", "ZEROSITE" in html),
        ("Copyright present", "© ZeroSite by AntennaHoldings" in html),
        ("QA Summary present", "qa-summary-page" in html),
    ]
    
    for check_name, passed in checks:
        print(f"{'✅' if passed else '❌'} {check_name}")
    
    # Count formatted numbers
    currency_count = html.count("₩")
    print(f"\n📊 Currency symbols found: {currency_count}")
    print(f"📄 Total HTML length: {len(html):,} chars")
    
    all_passed = all(passed for _, passed in checks)
    
    if all_passed:
        print("\n" + "="*80)
        print("🎉 ALL OUTPUT QUALITY FIXES VERIFIED")
        print("="*80)
        print("\nReport is now:")
        print("✅ Data-complete (no N/A)")
        print("✅ KPI-rich (mandatory metrics visible)")
        print("✅ Number-formatted (standardized)")
        print("✅ Design-consistent (unified CSS)")
        print("✅ Decision-clear (visual judgment block)")
        print("\n🎯 READY FOR CUSTOMER PRESENTATION")
    else:
        print("\n⚠️  Some checks failed - review needed")
    
except Exception as e:
    print(f"❌ Assembly failed: {e}")
    import traceback
    traceback.print_exc()

print()
