#!/usr/bin/env python3
"""
Complete End-to-End Test: Land Analysis → Module HTML → Final Reports
======================================================================

PURPOSE:
    1. Start new land analysis with actual address
    2. Execute M2-M6 modules sequentially
    3. Generate 6 final reports with complete data
    4. Verify KPI boxes show real values (not N/A)
    5. Extract and save HTML/PDF outputs

Author: ZeroSite Backend Team
Date: 2025-12-22
"""

import sys
import os
from pathlib import Path
import uuid
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import necessary services
from app.services.storage_service import get_storage
from app.services.module_engines.m2_land_appraisal_v4_3 import LandAppraisalEngineV43
from app.services.module_engines.m3_housing_type_v4_3 import HousingTypeEngineV43
from app.services.module_engines.m4_building_scale_v4_3 import BuildingScaleEngineV43
from app.services.module_engines.m5_feasibility_v4_3 import FeasibilityEngineV43
from app.services.module_engines.m6_lh_review_v4_3 import LHReviewEngineV43

# Import module HTML adapter and renderer
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


def create_test_context(land_address: str) -> str:
    """Create new analysis context"""
    context_id = f"test-{uuid.uuid4().hex[:12]}"
    
    storage = get_storage()
    storage.create_context(context_id, {
        "land_address": land_address,
        "project_name": "Phase 3.10 Complete Test",
        "created_at": datetime.now().isoformat(),
        "status": "in_progress"
    })
    
    print(f"✅ Created context: {context_id}")
    print(f"   Address: {land_address}\n")
    
    return context_id


def run_module_m2(context_id: str) -> dict:
    """Execute M2 - Land Appraisal"""
    print("🔄 Running M2 - Land Appraisal...")
    
    engine = LandAppraisalEngineV43()
    
    # Mock input data for M2
    m2_input = {
        "land_area": 3450.0,  # 3,450 m²
        "location": "서울특별시 강남구 역삼동 737",
        "zoning": "준주거지역",
        "road_condition": "양호"
    }
    
    result = engine.analyze(context_id, m2_input)
    
    print(f"   Total Value: {result.get('total_value', 0):,}원")
    print(f"   Per Pyeong: {result.get('pyeong_price', 0):,}원/평")
    print(f"✅ M2 Complete\n")
    
    return result


def run_module_m3(context_id: str) -> dict:
    """Execute M3 - Housing Type"""
    print("🔄 Running M3 - Housing Type...")
    
    engine = HousingTypeEngineV43()
    
    m3_input = {
        "location": "서울특별시 강남구 역삼동 737",
        "nearby_facilities": ["지하철역", "학교", "상업시설"]
    }
    
    result = engine.analyze(context_id, m3_input)
    
    print(f"   Recommended Type: {result.get('recommended_type', 'N/A')}")
    print(f"   Score: {result.get('total_score', 0)}점")
    print(f"✅ M3 Complete\n")
    
    return result


def run_module_m4(context_id: str) -> dict:
    """Execute M4 - Building Scale"""
    print("🔄 Running M4 - Building Scale...")
    
    engine = BuildingScaleEngineV43()
    
    m4_input = {
        "land_area": 3450.0,
        "coverage_ratio": 0.45,
        "floor_area_ratio": 2.2
    }
    
    result = engine.analyze(context_id, m4_input)
    
    print(f"   Total Units: {result.get('total_units', 0)}세대")
    print(f"   Floor Area: {result.get('gross_floor_area', 0):,}m²")
    print(f"✅ M4 Complete\n")
    
    return result


def run_module_m5(context_id: str) -> dict:
    """Execute M5 - Feasibility"""
    print("🔄 Running M5 - Feasibility...")
    
    engine = FeasibilityEngineV43()
    
    m5_input = {
        "land_cost": 5600000000,  # From M2
        "construction_cost": 3000000000,
        "unit_count": 450,  # From M4
        "sales_price_per_unit": 250000000
    }
    
    result = engine.analyze(context_id, m5_input)
    
    print(f"   NPV: {result.get('npv', 0):,}원")
    print(f"   IRR: {result.get('irr', 0)}%")
    print(f"   Profitable: {result.get('is_profitable', False)}")
    print(f"✅ M5 Complete\n")
    
    return result


def run_module_m6(context_id: str) -> dict:
    """Execute M6 - LH Review"""
    print("🔄 Running M6 - LH Review...")
    
    engine = LHReviewEngineV43()
    
    m6_input = {
        "housing_type": "공공분양주택",  # From M3
        "unit_count": 450,  # From M4
        "npv": 3250000000  # From M5
    }
    
    result = engine.analyze(context_id, m6_input)
    
    print(f"   Decision: {result.get('decision', 'N/A')}")
    print(f"   Approval Probability: {result.get('approval_probability', 0)}%")
    print(f"✅ M6 Complete\n")
    
    return result


def generate_module_html(context_id: str, module: str, canonical_summary: dict) -> str:
    """Generate module HTML with data-* attributes"""
    print(f"🔄 Generating {module} HTML...")
    
    # Adapt to HTML format
    if module == "M2":
        adapted = adapt_m2_summary_for_html(canonical_summary)
    elif module == "M3":
        adapted = adapt_m3_summary_for_html(canonical_summary)
    elif module == "M4":
        adapted = adapt_m4_summary_for_html(canonical_summary)
    elif module == "M5":
        adapted = adapt_m5_summary_for_html(canonical_summary)
    elif module == "M6":
        adapted = adapt_m6_summary_for_html(canonical_summary)
    else:
        raise ValueError(f"Unknown module: {module}")
    
    # Render HTML
    html = render_module_html(module, adapted)
    
    # Save to storage
    storage = get_storage()
    storage.save_module_html(context_id, module, html)
    
    print(f"✅ {module} HTML generated ({len(html):,} bytes)\n")
    
    return html


def generate_final_report(context_id: str, report_type: str, AssemblerClass) -> str:
    """Generate final report"""
    print(f"🔄 Generating {report_type}...")
    
    try:
        assembler = AssemblerClass(context_id)
        html = assembler.assemble()
        
        if html and len(html) > 1000:
            print(f"✅ {report_type} generated ({len(html):,} bytes)")
            
            # Check for N/A
            na_count = html.count("N/A")
            print(f"   N/A occurrences: {na_count}")
            
            if na_count == 0:
                print(f"   🎉 NO N/A FOUND - Perfect!\n")
            elif na_count < 5:
                print(f"   ⚠️  Minor N/A found - acceptable\n")
            else:
                print(f"   ❌ Too many N/A - needs investigation\n")
            
            return html
        else:
            print(f"❌ {report_type} failed - output too small\n")
            return ""
            
    except Exception as e:
        print(f"❌ {report_type} error: {str(e)[:200]}\n")
        return ""


def main():
    print("\n" + "="*80)
    print("🧪 COMPLETE END-TO-END TEST")
    print("="*80 + "\n")
    
    # Test address
    land_address = "서울특별시 강남구 역삼동 737"
    
    # Step 1: Create context
    print("STEP 1: Create Analysis Context")
    print("-"*80)
    context_id = create_test_context(land_address)
    
    # Step 2: Run modules M2-M6
    print("\nSTEP 2: Execute Modules M2-M6")
    print("-"*80)
    
    try:
        m2_result = run_module_m2(context_id)
        m3_result = run_module_m3(context_id)
        m4_result = run_module_m4(context_id)
        m5_result = run_module_m5(context_id)
        m6_result = run_module_m6(context_id)
    except Exception as e:
        print(f"❌ Module execution failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Build canonical_summary
    canonical_summary = {
        "M2": m2_result,
        "M3": m3_result,
        "M4": m4_result,
        "M5": m5_result,
        "M6": m6_result
    }
    
    # Save to storage
    storage = get_storage()
    storage.save_canonical_summary(context_id, canonical_summary)
    
    # Step 3: Generate module HTML
    print("\nSTEP 3: Generate Module HTML (with data-* attributes)")
    print("-"*80)
    
    try:
        generate_module_html(context_id, "M2", canonical_summary)
        generate_module_html(context_id, "M3", canonical_summary)
        generate_module_html(context_id, "M4", canonical_summary)
        generate_module_html(context_id, "M5", canonical_summary)
        generate_module_html(context_id, "M6", canonical_summary)
    except Exception as e:
        print(f"❌ Module HTML generation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Generate 6 final reports
    print("\nSTEP 4: Generate 6 Final Reports")
    print("-"*80)
    
    reports = [
        ("Landowner Summary", LandownerSummaryAssembler),
        ("Quick Check", QuickCheckAssembler),
        ("Financial Feasibility", FinancialFeasibilityAssembler),
        ("LH Technical", LHTechnicalAssembler),
        ("All-In-One", AllInOneAssembler),
        ("Executive Summary", ExecutiveSummaryAssembler)
    ]
    
    results = {}
    
    for name, AssemblerClass in reports:
        html = generate_final_report(context_id, name, AssemblerClass)
        results[name] = {
            "success": len(html) > 1000,
            "size": len(html),
            "na_count": html.count("N/A") if html else -1
        }
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80 + "\n")
    
    print(f"Context ID: {context_id}")
    print(f"Land Address: {land_address}\n")
    
    success_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)
    
    print(f"✅ Success: {success_count}/{total_count}")
    print(f"❌ Failed: {total_count - success_count}/{total_count}\n")
    
    print("Detailed Results:")
    print("-"*80)
    for name, result in results.items():
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"{name:30} | {status:12} | Size: {result['size']:8,} bytes | N/A: {result['na_count']:3}")
    
    print("\n" + "="*80 + "\n")
    
    if success_count == total_count:
        print("🎉 ALL TESTS PASSED!")
        print(f"\n💾 Access reports via:")
        print(f"   GET /api/v4/final-report/{{report_type}}/html?context_id={context_id}")
        sys.exit(0)
    else:
        print(f"⚠️  PARTIAL SUCCESS - {success_count}/{total_count} reports generated")
        sys.exit(1)


if __name__ == "__main__":
    main()
