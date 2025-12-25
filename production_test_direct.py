#!/usr/bin/env python3
"""
Production Test - Direct Mode (without Redis)
Tests report generation with mock production data
"""

import sys
import time
from typing import Dict, Any

sys.path.insert(0, '.')

from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html


# Mock production-quality data
MOCK_PRODUCTION_CONTEXT = {
    "context_id": "prod-test-001",
    "created_at": "2025-12-25T15:00:00",
    
    # M2: Land Appraisal (CanonicalAppraisalResult structure)
    "m2_result": {
        "calculation": {
            "final_appraised_total": 7500000000,  # 75억원
            "premium_adjusted_per_sqm": 49587000,  # 평당 약 1.64억원
            "base_price_per_sqm": 12000000,
        },
        "confidence": {
            "overall_score": 0.82,
        },
        "transaction_cases": [
            {"price": 5000000000, "date": "2024-06-15"},
            {"price": 6200000000, "date": "2024-08-20"},
            {"price": 7100000000, "date": "2024-10-10"},
            {"price": 7800000000, "date": "2024-11-25"},
            {"price": 8000000000, "date": "2024-12-05"},
        ]
    },
    
    # M3: Housing Type Selection
    "m3_result": {
        "selected": {
            "name": "청년형",
            "total_score": 85,
            "confidence": 0.82
        },
        "alternatives": [
            {"name": "신혼부부형", "score": 78},
            {"name": "고령자형", "score": 62}
        ],
        "scores": {
            "청년형": {"total": 85},
            "신혼부부형": {"total": 78},
            "고령자형": {"total": 62}
        }
    },
    
    # M4: Capacity Planning
    "m4_result": {
        "legal_capacity": {
            "total_units": 150,
            "parking_spaces": 180
        },
        "incentive_capacity": {
            "total_units": 180,
            "parking_spaces": 210
        },
        "recommended": {
            "scenario": "incentive",
            "total_units": 180
        }
    },
    
    # M5: Financial Feasibility
    "m5_result": {
        "financials": {
            "npv_public": 1850000000,  # 18.5억원
            "npv_market": 2100000000,
            "irr_public": 0.185,  # 18.5% (will be converted)
            "irr_market": 0.21,
            "roi": 0.263  # 26.3% (will be converted)
        },
        "profitability": {
            "grade": "B",
            "score": 78.5,
            "is_profitable": True
        },
        "costs": {
            "total_cost": 5200000000,
            "land_acquisition": 7500000000,
            "construction": 3800000000
        }
    },
    
    # M6: LH Review Prediction
    "m6_result": {
        "decision": {
            "type": "CONDITIONAL",
            "rationale": "조건부 추진 권장 - 위치 우수, 사업성 양호, 일부 보완 필요"
        },
        "approval": {
            "probability": 0.72
        },
        "scores": {
            "total": 78.5
        },
        "grade": "B",
        "max_score": 100,
        "key_factors": ["위치 우수", "수요 적합", "사업성 양호"],
        "risks": ["주차 여건 검토 필요", "인근 경쟁 프로젝트 모니터링"]
    }
}


def test_report_generation(context_id: str = "prod-test-001") -> Dict[str, Any]:
    """보고서 생성 테스트"""
    
    print(f"\n{'='*80}")
    print(f"🧪 PRODUCTION TEST (DIRECT MODE)")
    print(f"{'='*80}\n")
    print(f"Context ID: {context_id}")
    print(f"Mode: Direct assembly (no Redis)")
    print(f"\n{'='*80}\n")
    
    results = {
        "context_id": context_id,
        "reports": {},
        "summary": {
            "total": 0,
            "successful": 0,
            "failed": 0
        }
    }
    
    report_types = [
        ("quick_check", "Quick Check Report"),
        ("financial_feasibility", "Financial Feasibility Report"),
        ("lh_technical", "LH Technical Report"),
        ("executive_summary", "Executive Summary"),
        ("landowner_summary", "Landowner Summary"),
        ("all_in_one", "All-in-One Report (Primary)")
    ]
    
    for report_type, report_name in report_types:
        results["summary"]["total"] += 1
        print(f"🔄 Generating: {report_name}...")
        
        start_time = time.time()
        
        try:
            # Assemble report data
            assembled = assemble_final_report(
                report_type=report_type,
                canonical_data=MOCK_PRODUCTION_CONTEXT,
                context_id=context_id
            )
            
            if assembled is None:
                raise ValueError("Assembly returned None")
            
            # Render HTML
            html = render_final_report_html(report_type, assembled)
            
            if html is None:
                raise ValueError("Rendering returned None")
            
            # Calculate metrics
            duration_ms = (time.time() - start_time) * 1000
            html_size = len(html)
            na_count = html.count('N/A')
            na_verification = html.count('N/A (검증 필요)')
            
            # Check KPIs
            kpi_checks = {
                "토지감정가": any(x in html for x in ["7,500,000,000", "75억", "7.5B"]),
                "NPV": any(x in html for x in ["1,850,000,000", "18.5억", "1.85B", "NPV"]),
                "IRR": any(x in html for x in ["18.5%", "18.5", "IRR"]),
                "세대수": any(x in html for x in ["180세대", "180", "units"]),
                "주택유형": "청년형" in html,
                "LH판단": any(x in html for x in ["조건부", "CONDITIONAL", "추진 권장"])
            }
            
            kpi_present = sum(kpi_checks.values())
            
            print(f"✅ Success: {report_name}")
            print(f"   Duration: {duration_ms:.1f} ms")
            print(f"   HTML size: {html_size:,} characters")
            print(f"   N/A count: {na_count}")
            print(f"   N/A (검증 필요): {na_verification}")
            print(f"   KPI present: {kpi_present}/6")
            
            for kpi, present in kpi_checks.items():
                status = "✓" if present else "✗"
                print(f"      {status} {kpi}")
            
            results["summary"]["successful"] += 1
            results["reports"][report_type] = {
                "status": "success",
                "duration_ms": duration_ms,
                "html_size": html_size,
                "na_count": na_count,
                "na_verification": na_verification,
                "kpi_present": kpi_present,
                "kpi_checks": kpi_checks
            }
            
            print()
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            print(f"❌ Failed: {report_name}")
            print(f"   Error: {str(e)}")
            print(f"   Duration: {duration_ms:.1f} ms\n")
            
            results["summary"]["failed"] += 1
            results["reports"][report_type] = {
                "status": "failed",
                "error": str(e),
                "duration_ms": duration_ms
            }
            
            # Print traceback for debugging
            import traceback
            traceback.print_exc()
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"📋 TEST SUMMARY")
    print(f"{'='*80}\n")
    
    total = results["summary"]["total"]
    successful = results["summary"]["successful"]
    failed = results["summary"]["failed"]
    success_rate = (successful / total * 100) if total > 0 else 0
    
    print(f"Total Reports: {total}")
    print(f"✅ Successful: {successful}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{total} ({100-success_rate:.1f}%)")
    
    if successful > 0:
        print(f"\n✅ Successful Reports:")
        for rt, info in results["reports"].items():
            if info["status"] == "success":
                print(f"   - {rt:25} {info['html_size']:8,} chars  |  KPI: {info['kpi_present']}/6  |  {info['duration_ms']:.0f}ms")
    
    if failed > 0:
        print(f"\n❌ Failed Reports:")
        for rt, info in results["reports"].items():
            if info["status"] == "failed":
                print(f"   - {rt:25} {info['error']}")
    
    # Calculate aggregate metrics
    if successful > 0:
        successful_reports = [r for r in results["reports"].values() if r["status"] == "success"]
        avg_duration = sum(r["duration_ms"] for r in successful_reports) / len(successful_reports)
        avg_size = sum(r["html_size"] for r in successful_reports) / len(successful_reports)
        avg_kpi = sum(r["kpi_present"] for r in successful_reports) / len(successful_reports)
        avg_na = sum(r["na_count"] for r in successful_reports) / len(successful_reports)
        
        print(f"\n📊 Performance Metrics:")
        print(f"   Average Duration:  {avg_duration:.1f} ms")
        print(f"   Average HTML Size: {avg_size:,.0f} characters")
        print(f"   Average KPI:       {avg_kpi:.1f}/6")
        print(f"   Average N/A:       {avg_na:.1f}")
    
    # Final verdict
    print(f"\n{'='*80}")
    if successful == total:
        print(f"✅ PRODUCTION TEST PASSED: All {total} reports generated successfully")
        verdict = "PASSED"
    elif successful >= total * 0.8:
        print(f"⚠️  PRODUCTION TEST PARTIAL: {successful}/{total} reports successful")
        verdict = "PARTIAL"
    else:
        print(f"❌ PRODUCTION TEST FAILED: Only {successful}/{total} reports successful")
        verdict = "FAILED"
    print(f"{'='*80}\n")
    
    results["verdict"] = verdict
    
    return results


if __name__ == "__main__":
    results = test_report_generation()
    
    # Exit code
    if results["verdict"] == "PASSED":
        sys.exit(0)
    elif results["verdict"] == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)
