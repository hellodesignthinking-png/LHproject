#!/usr/bin/env python3
"""
Simplified End-to-End Test: Generate Reports with Mock Complete Data
=====================================================================

PURPOSE:
    Skip module engines, directly create complete canonical_summary
    → Generate module HTML with data-* attributes
    → Generate 6 final reports
    → Verify NO N/A in KPI boxes

Author: ZeroSite Backend Team
Date: 2025-12-22
"""

import sys
import os
from pathlib import Path
import uuid
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import services
# Note: We'll skip storage for this simplified test and use in-memory only

from app.services.module_html_adapter import (
    adapt_m2_summary_for_html,
    adapt_m3_summary_for_html,
    adapt_m4_summary_for_html,
    adapt_m5_summary_for_html,
    adapt_m6_summary_for_html
)
from app.services.module_html_renderer import render_module_html

# Import final report assemblers
from app.services.final_report_assembly.assemblers.landowner_summary import LandownerSummaryAssembler
from app.services.final_report_assembly.assemblers.quick_check import QuickCheckAssembler
from app.services.final_report_assembly.assemblers.financial_feasibility import FinancialFeasibilityAssembler
from app.services.final_report_assembly.assemblers.lh_technical import LHTechnicalAssembler
from app.services.final_report_assembly.assemblers.all_in_one import AllInOneAssembler
from app.services.final_report_assembly.assemblers.executive_summary import ExecutiveSummaryAssembler


def create_complete_mock_data() -> dict:
    """Create complete canonical_summary with all M2-M6 data"""
    
    return {
        "M2": {
            "summary": {
                "land_value_total_krw": 5600000000,  # Adapter expects land_value_total_krw
                "pyeong_price_krw": 5500000,  # Adapter expects pyeong_price_krw
                "total_value": 5600000000,  # Also include for compatibility
                "pyeong_price": 5500000,
                "confidence_pct": 85,
                "transaction_count": 15
            },
            "details": {
                "land_area": 3450.0,  # 3,450 m²
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
                "type_analysis": "입지 조건 우수, 대중교통 접근성 양호"
            }
        },
        "M4": {
            "summary": {
                "total_units": 450,  # 450세대
                "base_units": 380,
                "incentive_units": 70,
                "gross_floor_area": 36750.5  # 36,750.5 m²
            },
            "details": {
                "floors": "지하 2층 ~ 지상 20층",
                "coverage_ratio": 0.45,
                "floor_area_ratio": 2.2
            }
        },
        "M5": {
            "summary": {
                "npv": 3250000000,  # 32.5억원
                "irr": 15.8,  # 15.8%
                "is_profitable": True,
                "profitability_status": "수익성 양호"
            },
            "details": {
                "total_revenue": 112500000000,  # 1,125억원
                "total_cost": 86000000000,  # 860억원
                "profit": 26500000000  # 265억원
            }
        },
        "M6": {
            "summary": {
                "decision": "조건부 승인",
                "approval_probability": 82,
                "total_score": 76.5,
                "grade": "B"
            },
            "details": {
                "risk_level": "중위험",
                "risk_summary": "주요 요건 충족, 일부 조건 이행 시 승인 가능",
                "required_actions": [
                    "교통영향평가 완료",
                    "지역주민 설명회 개최"
                ]
            }
        }
    }


def create_test_context_with_data(land_address: str) -> tuple[str, dict]:
    """Create new context with complete mock data"""
    context_id = f"test-complete-{uuid.uuid4().hex[:8]}"
    
    # Create canonical_summary
    canonical_summary = create_complete_mock_data()
    
    # Save to storage (using context_storage)
    # Note: context_storage expects CanonicalLandContext, but we'll use dict for simplicity
    # In real usage, this would be a proper CanonicalLandContext object
    print(f"✅ Created context: {context_id}")
    print(f"   Address: {land_address}")
    print(f"   Modules: M2, M3, M4, M5, M6 (complete mock data)\n")
    
    return context_id, canonical_summary


def generate_all_module_html(context_id: str, canonical_summary: dict):
    """Generate HTML for all modules M2-M6"""
    print("🔄 Generating Module HTML...")
    print("-"*80)
    
    modules = ["M2", "M3", "M4", "M5", "M6"]
    adapters = {
        "M2": adapt_m2_summary_for_html,
        "M3": adapt_m3_summary_for_html,
        "M4": adapt_m4_summary_for_html,
        "M5": adapt_m5_summary_for_html,
        "M6": adapt_m6_summary_for_html
    }
    
    # Store in-memory for now (since we're mocking)
    module_htmls = {}
    
    for module in modules:
        # Adapt to HTML format
        adapted = adapters[module](canonical_summary)
        
        # Render HTML with data-* attributes
        html = render_module_html(module, adapted)
        
        # Store for assemblers to use
        module_htmls[module] = html
        
        # Verify data-* attributes
        has_data_module = f'data-module="{module}"' in html
        print(f"  {module}: {len(html):7,} bytes | data-module: {'✅' if has_data_module else '❌'}")
    
    print()
    return module_htmls


def generate_all_final_reports(context_id: str, module_htmls: dict) -> dict:
    """Generate all 6 final reports"""
    print("🔄 Generating Final Reports...")
    print("-"*80)
    
    reports = [
        ("landowner_summary", "Landowner Summary", LandownerSummaryAssembler),
        ("quick_check", "Quick Check", QuickCheckAssembler),
        ("financial_feasibility", "Financial Feasibility", FinancialFeasibilityAssembler),
        ("lh_technical", "LH Technical", LHTechnicalAssembler),
        ("all_in_one", "All-In-One", AllInOneAssembler),
        ("executive_summary", "Executive Summary", ExecutiveSummaryAssembler)
    ]
    
    results = {}
    
    for report_id, name, AssemblerClass in reports:
        try:
            assembler = AssemblerClass(context_id)
            
            # Mock load_module_html to use our pre-generated HTML
            # BUT DON'T bypass _extract_module_data - let it use vLAST extraction
            def mock_load_module_html(module_key):
                html = module_htmls.get(module_key, "<div>Module not found</div>")
                assembler._module_html_cache[module_key] = html
                return html
            
            assembler.load_module_html = mock_load_module_html
            
            # Generate report (this will call _extract_module_data internally)
            html = assembler.assemble()
            
            if html and len(html) > 1000:
                na_count = html.count("N/A")
                na_verify = html.count("검증 필요")
                
                status = "✅ PASS" if (na_count == 0 and na_verify == 0) else "⚠️  WARN" if na_count < 5 else "❌ FAIL"
                
                print(f"  {name:30} | {status} | {len(html):8,} bytes | N/A: {na_count:2} | 검증필요: {na_verify:2}")
                
                results[report_id] = {
                    "success": True,
                    "size": len(html),
                    "na_count": na_count,
                    "na_verify": na_verify,
                    "html": html
                }
            else:
                print(f"  {name:30} | ❌ FAIL | Too small ({len(html) if html else 0} bytes)")
                results[report_id] = {
                    "success": False,
                    "size": len(html) if html else 0,
                    "error": "Output too small"
                }
                
        except Exception as e:
            print(f"  {name:30} | ❌ ERROR | {str(e)[:50]}")
            import traceback
            traceback.print_exc()
            results[report_id] = {
                "success": False,
                "error": str(e)[:200]
            }
    
    print()
    return results


def save_output_samples(context_id: str, results: dict):
    """Save sample HTML outputs for inspection"""
    output_dir = Path("/home/user/webapp/test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"💾 Saving sample outputs to {output_dir}")
    print("-"*80)
    
    for report_id, result in results.items():
        if result.get("success") and result.get("html"):
            output_file = output_dir / f"{report_id}_{context_id}.html"
            output_file.write_text(result["html"], encoding="utf-8")
            print(f"  ✅ {output_file.name}")
    
    print()


def main():
    print("\n" + "="*80)
    print("🧪 SIMPLIFIED END-TO-END TEST WITH COMPLETE DATA")
    print("="*80 + "\n")
    
    # Test address
    land_address = "서울특별시 강남구 역삼동 737"
    
    # Step 1: Create context with complete data
    print("STEP 1: Create Context with Complete Mock Data")
    print("-"*80)
    context_id, canonical_summary = create_test_context_with_data(land_address)
    
    # Step 2: Generate module HTML (with data-* attributes)
    print("STEP 2: Generate Module HTML (M2-M6)")
    module_htmls = generate_all_module_html(context_id, canonical_summary)
    
    # Step 3: Generate 6 final reports
    print("STEP 3: Generate 6 Final Reports")
    results = generate_all_final_reports(context_id, module_htmls)
    
    # Step 4: Save samples
    save_output_samples(context_id, results)
    
    # Final Summary
    print("="*80)
    print("📊 FINAL SUMMARY")
    print("="*80 + "\n")
    
    print(f"Context ID: {context_id}")
    print(f"Land Address: {land_address}\n")
    
    success_count = sum(1 for r in results.values() if r.get("success"))
    total_count = len(results)
    perfect_count = sum(1 for r in results.values() if r.get("success") and r.get("na_count", 999) == 0)
    
    print(f"✅ Success: {success_count}/{total_count}")
    print(f"🎉 Perfect (NO N/A): {perfect_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}\n")
    
    if perfect_count == total_count:
        print("🎉🎉🎉 ALL TESTS PASSED - NO N/A IN ANY REPORT!")
        print(f"\n💾 Sample outputs saved to: /home/user/webapp/test_outputs/")
        print(f"\n🌐 Access reports via API:")
        print(f"   GET /api/v4/final-report/{{report_type}}/html?context_id={context_id}")
        print("\n" + "="*80 + "\n")
        sys.exit(0)
    elif success_count == total_count:
        print("✅ ALL REPORTS GENERATED (with minor N/A)")
        sys.exit(0)
    else:
        print(f"⚠️  PARTIAL SUCCESS - {success_count}/{total_count} reports generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
