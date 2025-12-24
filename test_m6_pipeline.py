#!/usr/bin/env python3
"""
vABSOLUTE-FINAL-5: Complete End-to-End Verification
Tests: M6 Decision Contract → Module HTML → KPI → Final 6 Reports
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.module_html_adapter import adapt_m6_summary_for_html
from app.services.module_html_renderer import render_module_html
from app.services.final_report_assembly.kpi_extractor import KPIExtractor
import re

print("="*80)
print("vABSOLUTE-FINAL-5: END-TO-END VERIFICATION")
print("="*80)
print()

# Test canonical_summary with M6 decision
test_cases = [
    ("적합", "적합"),
    ("조건부 적합", "조건부 적합"),
    ("부적합", "부적합"),
    ("추진 가능", "적합"),  # Legacy value → normalized
    ("조건부 승인", "조건부 적합"),  # Legacy value → normalized
]

print("STEP 1: M6 Decision Data Contract Verification")
print("-" * 80)

for input_value, expected_output in test_cases:
    try:
        canonical = {
            "M6": {
                "summary": {
                    "decision": input_value,
                    "total_score": 85,
                    "max_score": 110,
                    "grade": "B",
                    "approval_probability_pct": 88
                }
            }
        }
        
        # STEP 1: Adapter Test
        adapted = adapt_m6_summary_for_html(canonical)
        actual_decision = adapted["review_result"]["decision"]
        
        if actual_decision == expected_output:
            print(f"✅ Input: {input_value:15s} → Output: {actual_decision}")
        else:
            print(f"❌ Input: {input_value:15s} → Expected: {expected_output}, Got: {actual_decision}")
            
    except Exception as e:
        print(f"❌ Input: {input_value:15s} → ERROR: {e}")

print()

# Test invalid value (should raise ValueError)
print("Testing Invalid Decision Value (should FAIL):")
print("-" * 80)
try:
    invalid_canonical = {
        "M6": {
            "summary": {
                "decision": "INVALID_VALUE_123",
                "total_score": 85
            }
        }
    }
    adapted = adapt_m6_summary_for_html(invalid_canonical)
    print("❌ ERROR: Invalid value was accepted (should have raised ValueError)")
except ValueError as e:
    print(f"✅ Correctly rejected invalid value: {str(e)[:80]}...")
except Exception as e:
    print(f"⚠️  Unexpected error: {e}")

print()
print("="*80)
print("STEP 2: Module HTML Generation Test")
print("="*80)
print()

# Test with official contract value
canonical_official = {
    "M6": {
        "summary": {
            "decision": "조건부 적합",
            "total_score": 92,
            "max_score": 110,
            "grade": "A",
            "approval_probability_pct": 88
        },
        "details": {
            "compliance_notes": "LH 정책 부합",
            "risk_level": "낮음"
        }
    }
}

adapted = adapt_m6_summary_for_html(canonical_official)
html = render_module_html("M6", adapted)

# Check for data-decision attribute
match = re.search(r'data-decision="([^"]+)"', html)
if match:
    found_value = match.group(1)
    print(f"✅ data-decision attribute found: \"{found_value}\"")
    
    if found_value == "조건부 적합":
        print("✅ Value matches expected: 조건부 적합")
    else:
        print(f"❌ Value mismatch: expected '조건부 적합', got '{found_value}'")
else:
    print("❌ data-decision attribute NOT FOUND in HTML")

# Check for data-module
if 'data-module="M6"' in html:
    print("✅ data-module=\"M6\" present")
else:
    print("❌ data-module=\"M6\" missing")

print()
print("="*80)
print("STEP 3: KPIExtractor Verification")
print("="*80)
print()

# Extract KPI using KPIExtractor
try:
    kpi_data = KPIExtractor.extract_module_kpi(html, "M6", ["decision"])
    
    extracted_decision = kpi_data.get("decision")
    print(f"Extracted KPI: decision = {repr(extracted_decision)}")
    
    if extracted_decision == "조건부 적합":
        print("✅ KPIExtractor correctly extracted decision")
    elif extracted_decision is None or extracted_decision == "":
        print("❌ FAIL: KPIExtractor returned None/empty")
    else:
        print(f"⚠️  WARNING: Unexpected value: {repr(extracted_decision)}")
        
except Exception as e:
    print(f"❌ KPIExtractor ERROR: {e}")

print()
print("="*80)
print("STEP 4: Full Pipeline Test Summary")
print("="*80)
print()

# Check all components
checks = {
    "M6 Decision Contract": actual_decision == expected_output,
    "Module HTML Generation": match is not None,
    "data-decision Attribute": found_value == "조건부 적합",
    "KPI Extraction": extracted_decision == "조건부 적합",
}

all_pass = all(checks.values())

for check_name, result in checks.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status:10s} {check_name}")

print()
if all_pass:
    print("🎉 ALL CHECKS PASSED - M6 Pipeline Complete!")
    sys.exit(0)
else:
    print("❌ SOME CHECKS FAILED - Review above")
    sys.exit(1)
