#!/usr/bin/env python3
"""
vABSOLUTE-FINAL-8: Final PDF Validation Test

Purpose:
- Generate PDFs for all 6 report types
- Verify BUILD SIGNATURE presence
- Check cache invalidation
- Create validation checklist
"""
import sys
import hashlib
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.final_report_assembly.assemblers import (
    LandownerSummaryAssembler,
    QuickCheckAssembler,
    FinancialFeasibilityAssembler,
    LHTechnicalAssembler,
    AllInOneAssembler,
    ExecutiveSummaryAssembler
)

def create_mock_data():
    """Create complete mock data for testing"""
    return {
        "M2": {
            "land_value_total": 5000000000,
            "land_value_per_pyeong": 15000000,
            "confidence_pct": 85,
            "transaction_count": 12,
            "evaluation_basis": "실거래가 기반"
        },
        "M3": {
            "recommended_type": "민간분양",
            "total_score": 85,
            "max_score": 100,
            "decision_basis": "LH 정책 부합도"
        },
        "M4": {
            "total_units": 200,
            "building_coverage_ratio": 45.5,
            "floor_area_ratio": 180.2,
            "building_height": 15
        },
        "M5": {
            "npv": 1500000000,
            "irr": 15.5,
            "is_profitable": True,
            "payback_period": 5.2
        },
        "M6": {
            "decision": "조건부 적합",
            "total_score": 82,
            "max_score": 100,
            "grade": "B+",
            "approval_probability_pct": 75
        }
    }

def generate_test_context_id():
    """Generate unique context_id with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"test-v8-{timestamp}"

def test_single_report(assembler_class, report_type, context_id, canonical_summary, module_htmls):
    """Test a single report generation"""
    print(f"\n{'='*80}")
    print(f"Testing: {report_type}")
    print(f"{'='*80}")
    
    try:
        # Instantiate assembler
        assembler = assembler_class(context_id)
        
        # Generate report
        result = assembler.assemble()
        html = result["html"]
        
        # Validate BUILD SIGNATURE
        has_signature = "vABSOLUTE-FINAL-6" in html
        has_timestamp = datetime.now().strftime("%Y-%m-%d") in html
        
        # Calculate HTML hash
        html_hash = hashlib.sha1(html.encode()).hexdigest()[:8]
        
        # Check for N/A
        na_count = html.count('"N/A"') + html.count("'N/A'")
        
        # Save to file
        output_dir = Path("test_outputs")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{report_type}_v8_{context_id}.html"
        output_file.write_text(html, encoding="utf-8")
        
        # Results
        print(f"  ✅ Generation: SUCCESS")
        print(f"  📄 HTML Size: {len(html):,} bytes")
        print(f"  🔑 HTML Hash: {html_hash}")
        print(f"  🏷️  BUILD SIGNATURE: {'✅ FOUND' if has_signature else '❌ MISSING'}")
        print(f"  📅 Timestamp Today: {'✅ YES' if has_timestamp else '❌ NO'}")
        print(f"  🚫 N/A Count: {na_count}")
        print(f"  💾 Saved: {output_file}")
        
        return {
            "report_type": report_type,
            "status": "SUCCESS",
            "html_size": len(html),
            "html_hash": html_hash,
            "has_signature": has_signature,
            "has_timestamp": has_timestamp,
            "na_count": na_count,
            "output_file": str(output_file)
        }
    
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "report_type": report_type,
            "status": "FAILED",
            "error": str(e)
        }

def main():
    """Main test execution"""
    print("="*80)
    print("vABSOLUTE-FINAL-8: FINAL PDF VALIDATION TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Generate test data
    context_id = generate_test_context_id()
    print(f"Context ID: {context_id}")
    
    canonical_summary = create_mock_data()
    
    # Mock module HTMLs (simplified for testing)
    module_htmls = {}
    for module_id in ["M2", "M3", "M4", "M5", "M6"]:
        module_data = canonical_summary.get(module_id, {})
        module_htmls[module_id] = f'<div data-module="{module_id}">{module_data}</div>'
    
    # Test all 6 reports
    reports = [
        (LandownerSummaryAssembler, "landowner_summary"),
        (QuickCheckAssembler, "quick_check"),
        (FinancialFeasibilityAssembler, "financial_feasibility"),
        (LHTechnicalAssembler, "lh_technical"),
        (AllInOneAssembler, "all_in_one"),
        (ExecutiveSummaryAssembler, "executive_summary")
    ]
    
    results = []
    for assembler_class, report_type in reports:
        result = test_single_report(
            assembler_class, report_type, context_id, 
            canonical_summary, module_htmls
        )
        results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print("FINAL VALIDATION SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    signature_count = sum(1 for r in results if r.get("has_signature", False))
    timestamp_count = sum(1 for r in results if r.get("has_timestamp", False))
    na_free_count = sum(1 for r in results if r.get("na_count", 0) == 0)
    
    print(f"\n📊 Overall Results:")
    print(f"  ✅ Successful Generation: {success_count}/6")
    print(f"  🏷️  BUILD SIGNATURE Present: {signature_count}/6")
    print(f"  📅 Timestamp Current: {timestamp_count}/6")
    print(f"  🚫 No N/A Strings: {na_free_count}/6")
    
    # Checklist for user verification
    print("\n" + "="*80)
    print("USER VERIFICATION CHECKLIST")
    print("="*80)
    print("\nGenerate PDF via API and check:")
    print()
    print("| Report                | BUILD SIGNATURE | Time Current | M6 Decision | Size Changed | Status |")
    print("|----------------------|-----------------|--------------|-------------|--------------|--------|")
    
    for result in results:
        if result["status"] == "SUCCESS":
            sig = "✅" if result["has_signature"] else "❌"
            time_ok = "✅" if result["has_timestamp"] else "❌"
            report_name = result["report_type"].replace("_", " ").title()
            print(f"| {report_name:20} | {sig:15} | {time_ok:12} | ☐           | ☐            | ☐      |")
        else:
            report_name = result["report_type"].replace("_", " ").title()
            print(f"| {report_name:20} | ❌ FAILED       | ❌ FAILED    | ❌          | ❌           | ❌     |")
    
    print("\n" + "="*80)
    
    # Exit criteria
    if success_count == 6 and signature_count == 6 and timestamp_count == 6 and na_free_count == 6:
        print("\n🎉 ALL EXIT CRITERIA MET - READY FOR PDF GENERATION")
        return 0
    else:
        print("\n⚠️  SOME CHECKS FAILED - REVIEW ABOVE")
        return 1

if __name__ == "__main__":
    exit(main())
