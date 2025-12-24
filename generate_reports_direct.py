#!/usr/bin/env python3
"""
Generate Complete Reports - Direct Method
==========================================

Directly creates complete test data and generates reports
"""

import sys
import uuid
sys.path.insert(0, '/home/user/webapp')

from app.services.storage_service import StorageService
from app.services.final_report_assembly.assemblers.landowner_summary import LandownerSummaryAssembler
from app.services.final_report_assembly.assemblers.quick_check import QuickCheckAssembler
from app.services.final_report_assembly.assemblers.financial_feasibility import FinancialFeasibilityAssembler
from app.services.final_report_assembly.assemblers.lh_technical import LHTechnicalAssembler
from app.services.final_report_assembly.assemblers.executive_summary import ExecutiveSummaryAssembler
from app.services.final_report_assembly.assemblers.all_in_one import AllInOneAssembler

print("=" * 80)
print("🚀 GENERATING COMPLETE REPORTS WITH TEST DATA")
print("=" * 80)
print()

# Create new context
context_id = str(uuid.uuid4())
print(f"Context ID: {context_id}")
print()

# Store complete test data
storage = StorageService()

test_data = {
    "M2": {
        "land_value_total": 5000000000,
        "land_value_per_pyeong": 15000000,
        "land_area_m2": 1000.0,
        "land_area_pyeong": 302.5,
        "status": "complete"
    },
    "M3": {
        "preferred_type": "공공지원민간임대",
        "type_score": 85.5,
        "grade": "A",
        "status": "complete"
    },
    "M4": {
        "unit_count": 250,
        "total_floor_area": 18500.0,
        "status": "complete"
    },
    "M5": {
        "npv": 1200000000,
        "irr": 8.5,
        "profitability_text": "수익성 양호",
        "is_profitable": True,
        "status": "complete"
    },
    "M6": {
        "decision": "추진 가능",
        "risk_summary": "일부 보완 필요하나 승인 가능성 높음",
        "status": "complete"
    }
}

print("Storing test data...")
for module_id, data in test_data.items():
    storage.store_canonical_summary(context_id, module_id, data)
    print(f"  ✅ {module_id}: {data.get('status')}")

print()

# Generate reports
assemblers = {
    "landowner_summary": LandownerSummaryAssembler,
    "quick_check": QuickCheckAssembler,
    "financial_feasibility": FinancialFeasibilityAssembler,
    "lh_technical": LHTechnicalAssembler,
    "executive_summary": ExecutiveSummaryAssembler,
    "all_in_one": AllInOneAssembler
}

print("Generating reports...")
print()

results = {}

for report_type, AssemblerClass in assemblers.items():
    print(f"  {report_type}...")
    
    try:
        assembler = AssemblerClass(context_id)
        result = assembler.assemble()
        
        qa_status = result['qa_result']['status']
        html = result['html']
        
        # Check for issues
        na_count = html.count("N/A") + html.count("데이터 미확정") + html.count("검증 필요")
        has_blocked = "Report Generation Blocked" in html
        
        if qa_status == "FAIL":
            print(f"    ❌ FAILED: {result['qa_result'].get('errors', [])}")
            results[report_type] = "FAIL"
        elif has_blocked:
            print(f"    ⚠️  BLOCKED")
            results[report_type] = "BLOCKED"
        elif na_count > 10:  # Allow some N/A in labels
            print(f"    ⚠️  Has {na_count} N/A occurrences")
            results[report_type] = f"N/A:{na_count}"
        else:
            print(f"    ✅ SUCCESS ({len(html):,} bytes, {na_count} N/A)")
            results[report_type] = "SUCCESS"
            
            # Save HTML
            output_file = f"/tmp/report_{report_type}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"       → {output_file}")
            
    except Exception as e:
        print(f"    ❌ Exception: {e}")
        results[report_type] = f"ERROR"
        import traceback
        traceback.print_exc()
    
    print()

# Summary
print("=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print()

for report_type, status in results.items():
    icon = "✅" if status == "SUCCESS" else "❌"
    print(f"{icon} {report_type:30s} → {status}")

success_count = sum(1 for s in results.values() if s == "SUCCESS")
print()
print(f"Success Rate: {success_count}/{len(assemblers)}")
print(f"Context ID: {context_id}")
print(f"Reports saved to: /tmp/report_*.html")
print()
print("=" * 80)
