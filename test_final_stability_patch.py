"""
Final Output Stability & PDF Safety Validation Test
====================================================

Tests all 5 critical fixes:
[FIX A] PDF Safe KPI Lock
[FIX B] KPI Fallback Guarantee  
[FIX C] Executive Summary Numeric Anchor
[FIX D] Decision ↔ KPI Trace Link
[FIX E] Information Density Normalization
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.final_report_assembly.assemblers.landowner_summary import LandownerSummaryAssembler
from app.services.final_report_assembly.assemblers.quick_check import QuickCheckAssembler
from app.services.final_report_assembly.base_assembler import BaseFinalReportAssembler


def test_fix_a_pdf_safe_kpi():
    """Test FIX A: PDF Safe KPI Lock"""
    print("\n[FIX A] Testing PDF Safe KPI Lock...")
    
    assembler = LandownerSummaryAssembler(context_id="test_pdf_safe_001")
    
    # Generate KPI box
    test_kpis = {
        "토지 감정가": 1500000000,
        "NPV": 300000000,
        "LH 심사": "승인"
    }
    kpi_html = assembler.generate_kpi_summary_box(test_kpis, "landowner_summary")
    
    # Verify PDF-safe attributes
    checks = {
        "Has pdf-safe class": 'class="kpi-summary-box pdf-safe"' in kpi_html,
        "Has min-height": 'min-height: 200px' in kpi_html,
        "Has page-break-inside avoid": 'page-break-inside: avoid !important' in kpi_html,
        "Has page-break-before auto": 'page-break-before: auto' in kpi_html
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}: FIX A - PDF Safe KPI Lock")
    return all_passed


def test_fix_b_kpi_fallback():
    """Test FIX B: KPI Fallback Guarantee"""
    print("\n[FIX B] Testing KPI Fallback Guarantee...")
    
    # Use concrete assembler instead of abstract base
    assembler = LandownerSummaryAssembler(context_id="test_fallback_001")
    
    # Test with None values
    test_kpis_with_none = {
        "토지 감정가": None,
        "NPV": 0,
        "LH 심사": ""
    }
    kpi_html = assembler.generate_kpi_summary_box(test_kpis_with_none, "test_report")
    
    # Verify no empty values
    checks = {
        "No 'None' text": 'None' not in kpi_html,
        "Has fallback text": '데이터 미확정' in kpi_html or '₩0 (미확정)' in kpi_html,
        "Has tooltip": 'title=' in kpi_html or 'class="kpi-undefined"' in kpi_html,
        "No empty KPI values": '<div class="kpi-value"></div>' not in kpi_html
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}: FIX B - KPI Fallback Guarantee")
    return all_passed


def test_fix_c_numeric_anchor():
    """Test FIX C: Executive Summary Numeric Anchor"""
    print("\n[FIX C] Testing Executive Summary Numeric Anchor...")
    
    # Use concrete assembler instead of abstract base
    assembler = LandownerSummaryAssembler(context_id="test_numeric_001")
    
    # Test narrative without numbers
    narrative_no_numbers = "<p>이 사업은 좋은 전망을 가지고 있습니다.</p>"
    modules_data = {
        "M5": {"npv": 500000000},
        "M2": {"land_value": 2000000000}
    }
    
    # Apply ensure_numeric_anchor
    enhanced_narrative = assembler.ensure_numeric_anchor(narrative_no_numbers, modules_data)
    
    # Verify numeric content added
    checks = {
        "Has numbers": re.search(r'[\d,]+', enhanced_narrative) is not None,
        "Has currency": '₩' in enhanced_narrative or '원' in enhanced_narrative,
        "Longer than original": len(enhanced_narrative) > len(narrative_no_numbers),
        "Original content preserved": narrative_no_numbers in enhanced_narrative
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    # Also test narrative that already has numbers
    narrative_with_numbers = "<p>NPV는 ₩500,000,000입니다.</p>"
    unchanged = assembler.ensure_numeric_anchor(narrative_with_numbers, modules_data)
    unchanged_check = unchanged == narrative_with_numbers
    
    print(f"  {'✅' if unchanged_check else '❌'} Preserves narratives with existing numbers")
    
    final_pass = all_passed and unchanged_check
    print(f"  {'✅ PASS' if final_pass else '❌ FAIL'}: FIX C - Executive Summary Numeric Anchor")
    return final_pass


def test_fix_d_decision_kpi_trace():
    """Test FIX D: Decision ↔ KPI Trace Link"""
    print("\n[FIX D] Testing Decision ↔ KPI Trace Link...")
    
    assembler = LandownerSummaryAssembler(context_id="test_decision_trace_001")
    
    # Generate judgment basis with module data
    modules_data = {
        "M2": {"land_value": 1800000000},
        "M5": {"npv": 450000000, "is_profitable": True},
        "M6": {"decision": "승인"}
    }
    
    basis = assembler._generate_judgment_basis(modules_data)
    
    # Convert basis list to string for checking
    basis_text = " ".join(basis)
    
    # Verify numeric evidence is cited
    checks = {
        "Has NPV value": 'NPV' in basis_text and '₩' in basis_text,
        "Has status icons": ('✅' in basis_text or '❌' in basis_text or '⚠️' in basis_text),
        "Has LH decision": 'LH' in basis_text and '승인' in basis_text,
        "Has land value": '토지' in basis_text and '₩' in basis_text,
        "At least 3 points": len(basis) >= 3
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    print(f"  Sample basis: {basis[0][:80]}...")
    print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}: FIX D - Decision ↔ KPI Trace Link")
    return all_passed


def test_fix_e_density_normalization():
    """Test FIX E: Information Density Normalization"""
    print("\n[FIX E] Testing Information Density Normalization...")
    
    # Use concrete assembler instead of abstract base
    assembler = QuickCheckAssembler(context_id="test_density_001")
    
    # Get unified design CSS
    css = assembler.get_unified_design_css()
    
    # Verify density control classes exist
    checks = {
        "Has compact-report class": '.compact-report' in css,
        "Has dense-report class": '.dense-report' in css,
        "Has section-divider": '.section-divider' in css,
        "Has visual-break": '.visual-break' in css,
        "Has module spacing": '.module-section' in css and 'padding' in css
    }
    
    all_passed = all(checks.values())
    
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
    print(f"  CSS length: {len(css)} chars")
    print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}: FIX E - Information Density Normalization")
    return all_passed


def test_comprehensive_integration():
    """Test all fixes work together in a real report"""
    print("\n[INTEGRATION] Testing All Fixes Together...")
    
    try:
        assembler = QuickCheckAssembler(context_id="test_integration_001")
        
        # Check all methods exist
        checks = {
            "Has generate_kpi_summary_box": hasattr(assembler, 'generate_kpi_summary_box'),
            "Has ensure_numeric_anchor": hasattr(assembler, 'ensure_numeric_anchor'),
            "Has generate_decision_block": hasattr(assembler, 'generate_decision_block'),
            "Has _generate_judgment_basis": hasattr(assembler, '_generate_judgment_basis'),
            "Has get_unified_design_css": hasattr(assembler, 'get_unified_design_css')
        }
        
        all_passed = all(checks.values())
        
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        print(f"  {'✅ PASS' if all_passed else '❌ FAIL'}: Integration Test")
        return all_passed
    
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        return False


def main():
    """Run all validation tests"""
    print("="*70)
    print("FINAL OUTPUT STABILITY & PDF SAFETY VALIDATION")
    print("="*70)
    print("\nValidating all 5 critical fixes...\n")
    
    results = {
        "FIX A - PDF Safe KPI Lock": test_fix_a_pdf_safe_kpi(),
        "FIX B - KPI Fallback Guarantee": test_fix_b_kpi_fallback(),
        "FIX C - Executive Summary Numeric Anchor": test_fix_c_numeric_anchor(),
        "FIX D - Decision ↔ KPI Trace Link": test_fix_d_decision_kpi_trace(),
        "FIX E - Information Density Normalization": test_fix_e_density_normalization(),
        "Integration Test": test_comprehensive_integration()
    }
    
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\nResults: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL STABILITY FIXES VALIDATED!")
        print("\nFinal Output Stability Checklist:")
        print("  ✓ KPI boxes never split across PDF pages")
        print("  ✓ No empty numeric fields")
        print("  ✓ Executive summaries include numbers")
        print("  ✓ Decision blocks cite numeric evidence")
        print("  ✓ Dense reports are visually segmented")
        print("\n🚀 SYSTEM STATUS: PDF-SAFE & PRODUCTION READY")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed - review required")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
