#!/usr/bin/env python3
"""
ZeroSite v4.0 - Production Test with Real Context ID

Purpose: Test final reports with actual production Context IDs
Author: ZeroSite Backend Team
Date: 2025-12-25
"""

import sys
from typing import Dict, Any, Optional
from app.services.context_storage import get_frozen_context
from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html


def test_with_real_context(context_id: str) -> Dict[str, Any]:
    """
    실제 Context ID로 6종 보고서 생성 테스트
    
    Args:
        context_id: 실제 프로덕션 Context ID
    
    Returns:
        테스트 결과 딕셔너리
    """
    print(f"\n{'='*80}")
    print(f"🧪 PRODUCTION TEST: Context ID = {context_id}")
    print(f"{'='*80}\n")
    
    results = {
        "context_id": context_id,
        "frozen_context_loaded": False,
        "reports": {}
    }
    
    # Step 1: Load frozen context
    print("📦 Step 1: Loading frozen context...")
    try:
        frozen_context = get_frozen_context(context_id)
        if frozen_context is None:
            print(f"❌ Failed: Context ID '{context_id}' not found in storage")
            return results
        
        results["frozen_context_loaded"] = True
        print(f"✅ Success: Frozen context loaded")
        print(f"   Keys: {list(frozen_context.keys())}")
        
        # Check M2-M6 presence
        m2_present = "m2_result" in frozen_context
        m3_present = "m3_result" in frozen_context
        m4_present = "m4_result" in frozen_context
        m5_present = "m5_result" in frozen_context
        m6_present = "m6_result" in frozen_context
        
        print(f"\n   Module Presence:")
        print(f"   - M2 (토지감정): {'✓' if m2_present else '✗'}")
        print(f"   - M3 (주택유형): {'✓' if m3_present else '✗'}")
        print(f"   - M4 (용적률/세대수): {'✓' if m4_present else '✗'}")
        print(f"   - M5 (사업성): {'✓' if m5_present else '✗'}")
        print(f"   - M6 (LH 검토): {'✓' if m6_present else '✗'}")
        
    except Exception as e:
        print(f"❌ Error loading context: {e}")
        import traceback
        traceback.print_exc()
        return results
    
    # Step 2: Test 6 report types
    report_types = [
        ("quick_check", "Quick Check Report"),
        ("financial_feasibility", "Financial Feasibility Report"),
        ("lh_technical", "LH Technical Report"),
        ("executive_summary", "Executive Summary"),
        ("landowner_summary", "Landowner Summary"),
        ("all_in_one", "All-in-One Report (Primary)")
    ]
    
    print(f"\n{'='*80}")
    print("📊 Step 2: Generating 6 report types...")
    print(f"{'='*80}\n")
    
    for report_type, report_name in report_types:
        print(f"\n🔄 Generating {report_name}...")
        
        try:
            # Assemble report data
            assembled = assemble_final_report(
                report_type=report_type,
                canonical_data=frozen_context,
                context_id=context_id
            )
            
            if assembled is None:
                print(f"❌ Failed: Assembly returned None")
                results["reports"][report_type] = {
                    "status": "failed",
                    "error": "Assembly returned None"
                }
                continue
            
            # Render HTML
            html = render_final_report_html(report_type, assembled)
            
            if html is None:
                print(f"❌ Failed: Rendering returned None")
                results["reports"][report_type] = {
                    "status": "failed",
                    "error": "Rendering returned None"
                }
                continue
            
            # Success
            html_size = len(html)
            na_count = html.count('N/A')
            na_verification_count = html.count('N/A (검증 필요)')
            
            print(f"✅ Success: {report_name}")
            print(f"   HTML size: {html_size:,} characters")
            print(f"   N/A occurrences: {na_count}")
            print(f"   N/A (검증 필요): {na_verification_count}")
            
            # Check KPIs in HTML
            kpi_checks = {
                "토지감정가": any(x in html for x in ["토지감정가", "감정평가액", "land_value"]),
                "NPV": "NPV" in html or "순현재가치" in html,
                "IRR": "IRR" in html or "내부수익률" in html,
                "세대수": any(x in html for x in ["세대", "units"]),
                "주택유형": any(x in html for x in ["청년형", "신혼부부형", "고령자형", "housing_type"]),
                "LH 판단": any(x in html for x in ["추진 권장", "조건부", "보류", "GO", "CONDITIONAL", "NO-GO"])
            }
            
            kpi_present = sum(kpi_checks.values())
            print(f"   KPI presence: {kpi_present}/6")
            for kpi, present in kpi_checks.items():
                print(f"      - {kpi}: {'✓' if present else '✗'}")
            
            results["reports"][report_type] = {
                "status": "success",
                "html_size": html_size,
                "na_count": na_count,
                "na_verification_count": na_verification_count,
                "kpi_checks": kpi_checks,
                "kpi_present": kpi_present
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            results["reports"][report_type] = {
                "status": "error",
                "error": str(e)
            }
    
    # Step 3: Summary
    print(f"\n{'='*80}")
    print("📋 PRODUCTION TEST SUMMARY")
    print(f"{'='*80}\n")
    
    successful_reports = [k for k, v in results["reports"].items() if v.get("status") == "success"]
    failed_reports = [k for k, v in results["reports"].items() if v.get("status") != "success"]
    
    print(f"Context ID: {context_id}")
    print(f"Frozen Context: {'✓ Loaded' if results['frozen_context_loaded'] else '✗ Failed'}")
    print(f"\nReport Generation:")
    print(f"  ✅ Successful: {len(successful_reports)}/6")
    print(f"  ❌ Failed: {len(failed_reports)}/6")
    
    if successful_reports:
        print(f"\n✅ Successful Reports:")
        for rt in successful_reports:
            info = results["reports"][rt]
            print(f"   - {rt}: {info['html_size']:,} chars, KPI: {info['kpi_present']}/6")
    
    if failed_reports:
        print(f"\n❌ Failed Reports:")
        for rt in failed_reports:
            info = results["reports"][rt]
            print(f"   - {rt}: {info.get('error', 'Unknown error')}")
    
    # Final verdict
    print(f"\n{'='*80}")
    if len(successful_reports) == 6:
        print("✅ PRODUCTION TEST PASSED: All 6 reports generated successfully")
    elif len(successful_reports) >= 4:
        print("⚠️  PRODUCTION TEST PARTIAL: Most reports generated successfully")
    else:
        print("❌ PRODUCTION TEST FAILED: Multiple reports failed to generate")
    print(f"{'='*80}\n")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python production_test_with_real_context.py <context_id>")
        print("\nExample:")
        print("  python production_test_with_real_context.py 01234567-89ab-cdef-0123-456789abcdef")
        print("\nNote: Redis must be running and context must exist in storage")
        sys.exit(1)
    
    context_id = sys.argv[1]
    results = test_with_real_context(context_id)
    
    # Exit code based on results
    successful = sum(1 for v in results["reports"].values() if v.get("status") == "success")
    if successful == 6:
        sys.exit(0)  # All passed
    elif successful >= 4:
        sys.exit(1)  # Partial success
    else:
        sys.exit(2)  # Failed
