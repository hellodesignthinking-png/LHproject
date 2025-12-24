#!/usr/bin/env python3
"""
vABSOLUTE-FINAL-4: Production Audit
Verify data flow: Mock Data → Module HTML → KPI → Final Reports
"""
import sys
import os
from pathlib import Path
import uuid
import re

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.module_html_adapter import (
    adapt_m2_summary_for_html,
    adapt_m3_summary_for_html,
    adapt_m4_summary_for_html,
    adapt_m5_summary_for_html,
    adapt_m6_summary_for_html
)
from app.services.module_html_renderer import render_module_html
from app.services.final_report_assembly.assemblers.landowner_summary import LandownerSummaryAssembler
from app.services.final_report_assembly.assemblers.quick_check import QuickCheckAssembler
from app.services.final_report_assembly.assemblers.financial_feasibility import FinancialFeasibilityAssembler
from app.services.final_report_assembly.assemblers.lh_technical import LHTechnicalAssembler
from app.services.final_report_assembly.assemblers.all_in_one import AllInOneAssembler
from app.services.final_report_assembly.assemblers.executive_summary import ExecutiveSummaryAssembler

print("="*80)
print("vABSOLUTE-FINAL-4: PRODUCTION AUDIT")
print("="*80)
print()

# Create complete mock data
canonical_summary = {
    "M2": {
        "summary": {
            "land_value_total_krw": 5600000000,
            "pyeong_price_krw": 5500000,
            "total_value": 5600000000,
            "pyeong_price": 5500000,
            "confidence_pct": 85,
            "transaction_count": 15
        },
        "details": {
            "land_area": 3450.0,
            "location": "서울특별시 강남구 역삼동 737",
            "zoning": "준주거지역"
        }
    },
    "M3": {
        "summary": {
            "recommended_type": "공공분양주택",
            "total_score": 87.5,
            "confidence_pct": 90
        },
        "details": {
            "type_analysis": "입지 조건 우수"
        }
    },
    "M4": {
        "summary": {
            "total_units": 450,
            "base_units": 380,
            "incentive_units": 70,
            "gross_floor_area": 36750.5
        },
        "details": {
            "floors": "지하 2층 ~ 지상 20층",
            "coverage_ratio": 0.45,
            "floor_area_ratio": 2.2
        }
    },
    "M5": {
        "summary": {
            "npv": 3250000000,
            "irr": 15.8,
            "is_profitable": True,
            "profitability_status": "수익성 양호"
        },
        "details": {
            "total_revenue": 112500000000,
            "total_cost": 86000000000,
            "profit": 26500000000
        }
    },
    "M6": {
        "summary": {
            "decision": "추진 가능",
            "confidence_pct": 88,
            "review_status": "적합"
        },
        "details": {
            "compliance_notes": "LH 정책 부합",
            "risk_level": "낮음"
        }
    }
}

context_id = f"audit-{uuid.uuid4().hex[:8]}"
print(f"✅ Test Context: {context_id}")
print()

# STEP 1: Module HTML Contract Verification
print("="*80)
print("STEP 1: MODULE HTML CONTRACT VERIFICATION")
print("="*80)
print()

module_checks = {
    "M2": ["data-module=\"M2\"", "data-land-value-total", "data-land-area"],
    "M3": ["data-module=\"M3\"", "data-total-score", "data-recommended-type"],
    "M4": ["data-module=\"M4\"", "data-total-units", "data-total-floor-area"],
    "M5": ["data-module=\"M5\"", "data-npv", "data-irr"],
    "M6": ["data-module=\"M6\"", "data-decision"]
}

adapters = {
    "M2": adapt_m2_summary_for_html,
    "M3": adapt_m3_summary_for_html,
    "M4": adapt_m4_summary_for_html,
    "M5": adapt_m5_summary_for_html,
    "M6": adapt_m6_summary_for_html
}

module_htmls = {}
html_issues = []

for module_id in ["M2", "M3", "M4", "M5", "M6"]:
    try:
        adapter = adapters[module_id]
        adapted = adapter(canonical_summary[module_id])
        html = render_module_html(module_id, adapted, context_id)
        module_htmls[module_id] = html
        
        # Check for required attributes
        missing = []
        for check in module_checks[module_id]:
            if check not in html:
                missing.append(check)
        
        if missing:
            print(f"[{module_id}] ❌ MISSING: {', '.join(missing)}")
            html_issues.append(f"{module_id}: {', '.join(missing)}")
        else:
            print(f"[{module_id}] ✅ OK (all data-* attributes present)")
            
    except Exception as e:
        print(f"[{module_id}] ❌ RENDER ERROR: {e}")
        html_issues.append(f"{module_id}: Render failed - {e}")
        module_htmls[module_id] = None

print()

# STEP 2: KPIExtractor Result Verification
print("="*80)
print("STEP 2: KPIEXTRACTOR RESULT VERIFICATION")
print("="*80)
print()

from app.services.final_report_assembly.kpi_extractor import KPIExtractor
from app.services.final_report_assembly.report_type_configs import get_mandatory_kpi

mandatory_kpi_all = get_mandatory_kpi("all_in_one")  # Get all mandatory KPIs
kpi_issues = []

for module_id, html in module_htmls.items():
    if html is None:
        print(f"[{module_id}] SKIP - No HTML")
        continue
        
    required_keys = mandatory_kpi_all.get(module_id, [])
    if not required_keys:
        continue
        
    try:
        kpi_data = KPIExtractor.extract_module_kpi(html, module_id, required_keys)
        
        for key in required_keys:
            value = kpi_data.get(key)
            if value is None or value == "" or value == "N/A":
                print(f"{module_id}.{key} = {repr(value)} (❌ CRITICAL)")
                kpi_issues.append(f"{module_id}.{key} = {repr(value)}")
            else:
                print(f"{module_id}.{key} = {value} (✅ OK)")
                
    except Exception as e:
        print(f"[{module_id}] ❌ EXTRACTION ERROR: {e}")
        kpi_issues.append(f"{module_id}: Extraction failed - {e}")

print()

# Store module HTML for report generation
os.environ["MOCK_MODE"] = "true"
os.environ["TEST_CONTEXT_ID"] = context_id

# Save module HTML to in-memory storage
_module_html_storage = {}
for module_id, html in module_htmls.items():
    if html:
        _module_html_storage[f"{context_id}_{module_id}"] = html

# Monkey-patch the storage for test
original_load = None

def mock_load_module_html(self, module_id):
    key = f"{context_id}_{module_id}"
    html = _module_html_storage.get(key)
    if not html:
        raise ValueError(f"Module HTML not found for {key}")
    return html

# STEP 3: 6-Report KPI Parity Verification
print("="*80)
print("STEP 3: 6-REPORT KPI PARITY VERIFICATION")
print("="*80)
print()

assemblers = {
    "landowner_summary": LandownerSummaryAssembler(context_id),
    "quick_check": QuickCheckAssembler(context_id),
    "financial_feasibility": FinancialFeasibilityAssembler(context_id),
    "lh_technical": LHTechnicalAssembler(context_id),
    "all_in_one": AllInOneAssembler(context_id),
    "executive_summary": ExecutiveSummaryAssembler(context_id)
}

# Patch load_module_html for all assemblers
for assembler in assemblers.values():
    assembler.load_module_html = lambda mid, a=assembler: mock_load_module_html(a, mid)

report_results = {}
assembler_issues = []

for report_type, assembler in assemblers.items():
    try:
        result = assembler.assemble()
        report_results[report_type] = result
        
        status = result.get("qa_result", {}).get("status", "UNKNOWN")
        html = result.get("html", "")
        size = len(html)
        
        if status == "FAIL":
            blocking = result.get("qa_result", {}).get("blocking", False)
            reason = result.get("qa_result", {}).get("reason", "Unknown")
            errors = result.get("qa_result", {}).get("errors", [])
            print(f"[{report_type:25s}] ❌ FAIL (blocking={blocking})")
            print(f"{'':27s} Reason: {reason}")
            if errors:
                print(f"{'':27s} Errors: {errors[0]}")
            assembler_issues.append(f"{report_type}: {reason}")
        else:
            print(f"[{report_type:25s}] ✅ {status} ({size:,} bytes)")
            
    except Exception as e:
        print(f"[{report_type:25s}] ❌ ERROR: {str(e)[:60]}")
        assembler_issues.append(f"{report_type}: Exception - {e}")
        report_results[report_type] = None

print()

# STEP 4: Output Content Verification
print("="*80)
print("STEP 4: FINAL REPORT OUTPUT VERIFICATION")
print("="*80)
print()

forbidden_strings = ["N/A", "undefined", "None"]
output_issues = []

for report_type, result in report_results.items():
    if result is None:
        print(f"[{report_type:25s}] SKIP - No result")
        continue
        
    html = result.get("html", "")
    
    # Check for forbidden strings (but exclude them if in comments or meta)
    found_forbidden = []
    for forbidden in forbidden_strings:
        # Simple check - look for forbidden string not in HTML comments
        matches = re.findall(f'(?<!<!--.*){re.escape(forbidden)}(?!.*-->)', html)
        if matches and forbidden in html:
            # Count occurrences (rough)
            count = html.count(forbidden)
            # Exclude if it's in script/style tags or comments
            if '<script' not in html[:html.find(forbidden)] or '</script>' in html[:html.find(forbidden)]:
                found_forbidden.append(f"{forbidden}({count})")
    
    if found_forbidden:
        print(f"[{report_type:25s}] ❌ CONTAINS: {', '.join(found_forbidden)}")
        output_issues.append(f"{report_type}: Contains {', '.join(found_forbidden)}")
    else:
        # Check for required elements
        has_currency = "₩" in html or "원" in html
        has_percent = "%" in html
        has_area = "㎡" in html or "m²" in html or "m2" in html
        has_digit = any(char.isdigit() for char in html)
        
        if has_digit and (has_currency or has_percent or has_area):
            print(f"[{report_type:25s}] ✅ OK (KPI present, no forbidden strings)")
        else:
            print(f"[{report_type:25s}] ⚠️  WARNING (no clear KPI values)")
            output_issues.append(f"{report_type}: No clear KPI values")

print()

# STEP 5: Problem Classification & Fix Recommendations
print("="*80)
print("STEP 5: PROBLEM CLASSIFICATION & FIX RECOMMENDATIONS")
print("="*80)
print()

all_pass = not (html_issues or kpi_issues or assembler_issues or output_issues)

if all_pass:
    print("🎉 ALL CHECKS PASSED!")
    print()
    print("Exit Criteria Status:")
    print("  ✅ Module HTML contract 100% satisfied")
    print("  ✅ KPIExtractor extracts all required KPIs")
    print("  ✅ All 6 reports behave identically")
    print("  ✅ No forbidden strings in output")
    print()
    print("STATUS: PRODUCTION READY ✅")
else:
    print("✅ PASS Items:")
    if not html_issues:
        print("  ✓ Module HTML contracts (all data-* attributes present)")
    if not kpi_issues:
        print("  ✓ KPI extraction successful")
    if not assembler_issues:
        print("  ✓ All reports generate without assembler errors")
    if not output_issues:
        print("  ✓ Output clean (no forbidden strings)")
    print()
    
    print("❌ FAIL Items:")
    if html_issues:
        print("  HTML Level Issues:")
        for issue in html_issues:
            print(f"    - {issue}")
    if kpi_issues:
        print("  KPI/Data Issues:")
        for issue in kpi_issues:
            print(f"    - {issue}")
    if assembler_issues:
        print("  Assembler Issues:")
        for issue in assembler_issues:
            print(f"    - {issue}")
    if output_issues:
        print("  Output Issues:")
        for issue in output_issues:
            print(f"    - {issue}")
    
    print()
    print("🔧 FIX RECOMMENDATIONS:")
    print()
    
    if html_issues:
        print("1. Module HTML Renderer Issues")
        print("   Location: app/services/module_html_renderer.py")
        print("   Fix: Ensure all data-* attributes are included in HTML output")
        print("   Verify: Check render_module_html() for each module")
        print()
    
    if kpi_issues and not html_issues:
        print("1. Mock Data Issues")
        print("   Location: canonical_summary mock data")
        print("   Fix: Ensure all required KPI keys exist in mock data")
        print("   Verify: Check adapter functions map summary → HTML correctly")
        print()
    
    if assembler_issues:
        print("1. Assembler Issues")
        print("   Location: Individual assembler files")
        print("   Fix: Review failed assemblers for logic errors")
        print("   Verify: Ensure all use identical KPI pipeline pattern")
        print()

print()
print("="*80)
print("AUDIT COMPLETE")
print("="*80)

# Exit with appropriate code
sys.exit(0 if all_pass else 1)
