#!/usr/bin/env python3
"""
ZeroSite v4.0 - Final Verification Script
==========================================
최종 검증: 6종 보고서 HTML 생성 및 KPI 일치 확인
"""

import sys
from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html

# 테스트 데이터 (CanonicalAppraisalResult 구조)
test_canonical = {
    "m2_result": {
        "version": "v8.7",
        "locked": True,
        "timestamp": "2025-12-25T12:00:00",
        "zoning": {
            "zone_type": "제2종일반주거지역",
            "land_use": "공동주택용지"
        },
        "official_land_price": {
            "price_per_sqm": 12000000,
            "reference_date": "2025-01-01"
        },
        "transaction_cases": [
            {"price": 7200000000, "date": "2024-11-15"},
            {"price": 7800000000, "date": "2024-10-20"},
            {"price": 7500000000, "date": "2024-09-10"}
        ],
        "premium": {
            "rate": 0.25,
            "factors": ["location", "development"]
        },
        "calculation": {
            "base_price_per_sqm": 39669000,
            "premium_adjusted_per_sqm": 49587000,
            "land_area_sqm": 151.29,
            "final_appraised_total": 7500000000
        },
        "confidence": {
            "overall_score": 0.82,
            "data_completeness": 0.85,
            "case_similarity": 0.80,
            "time_relevance": 0.81
        },
        "metadata": {
            "appraiser": "ZeroSite AI",
            "calculation_date": "2025-12-25"
        }
    },
    "m3_result": {
        "selected": {
            "name": "청년형",
            "code": "YOUTH"
        },
        "scores": {
            "청년형": {"total": 82.5, "location": 28, "scale": 18, "feasibility": 25, "compliance": 11.5},
            "신혼부부형": {"total": 78.0, "location": 26, "scale": 17, "feasibility": 24, "compliance": 11.0}
        },
        "confidence": 85,
        "recommendations": ["청년형 추천", "신혼부부형 차선책"]
    },
    "m4_result": {
        "legal_capacity": {
            "total_units": 150,
            "floors": 15,
            "bcr": 0.6,
            "far": 2.5
        },
        "incentive_capacity": {
            "total_units": 180,
            "floors": 18,
            "bcr": 0.65,
            "far": 3.0
        },
        "parking_solutions": {
            "alternative_A": {
                "total_spaces": 180,
                "type": "지하 2층"
            },
            "alternative_B": {
                "total_spaces": 150,
                "type": "지하 1층 + 지상"
            }
        }
    },
    "m5_result": {
        "financials": {
            "npv_public": 1850000000,
            "npv_market": 2100000000,
            "irr_public": 0.185,
            "irr_market": 0.21,
            "roi": 0.263
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
    "m6_result": {
        "decision": {
            "type": "CONDITIONAL",
            "rationale": "조건부 추진 권장"
        },
        "approval": {
            "probability": 0.72,  # 0-1 범위
            "key_factors": ["위치", "규모"]
        },
        "scores": {
            "total": 78.5,
            "location": 28,
            "scale": 16,
            "feasibility": 25,
            "compliance": 9.5
        },
        "grade": "B"
    }
}

# 6종 보고서 타입
REPORT_TYPES = [
    "quick_check",
    "financial_feasibility",
    "lh_technical",
    "executive_summary",
    "landowner_summary",
    "all_in_one"
]

def verify_kpi_values(html: str, report_type: str) -> dict:
    """KPI 값 검증"""
    checks = {
        "land_value_found": "7,500,000,000" in html or "75억" in html,
        "npv_found": "1,850,000,000" in html or "18.5억" in html,
        "irr_found": "18.5" in html,
        "units_found": "180" in html,
        "housing_type_found": "청년형" in html,
        "decision_found": "CONDITIONAL" in html or "조건부" in html,
        "na_count": html.count("N/A") + html.count("검증 필요") + html.count(">None<")
    }
    return checks

def main():
    print("=" * 80)
    print("ZeroSite v4.0 - FINAL VERIFICATION")
    print("=" * 80)
    print()
    
    context_id = "test-final-verification"
    all_passed = True
    
    for report_type in REPORT_TYPES:
        print(f"[{report_type}] 생성 중...")
        try:
            # 1. Assemble
            assembled = assemble_final_report(report_type, test_canonical, context_id)
            
            # 2. Render HTML
            html = render_final_report_html(report_type, assembled)
            
            # 3. Verify
            checks = verify_kpi_values(html, report_type)
            
            print(f"  ✓ HTML 생성 완료 (길이: {len(html):,} chars)")
            print(f"  - 토지감정가: {'✓' if checks['land_value_found'] else '✗'}")
            print(f"  - NPV: {'✓' if checks['npv_found'] else '✗'}")
            print(f"  - IRR: {'✓' if checks['irr_found'] else '✗'}")
            print(f"  - 세대수: {'✓' if checks['units_found'] else '✗'}")
            print(f"  - 주택유형: {'✓' if checks['housing_type_found'] else '✗'}")
            print(f"  - LH 판단: {'✓' if checks['decision_found'] else '✗'}")
            print(f"  - N/A 잔존: {checks['na_count']}건")
            
            if checks['na_count'] > 0:
                all_passed = False
                print(f"  ❌ N/A 잔존 발견!")
            
            if not all(v for k, v in checks.items() if k != 'na_count'):
                all_passed = False
                print(f"  ⚠️  일부 KPI 값 누락")
            
            print()
            
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            all_passed = False
            print()
    
    print("=" * 80)
    if all_passed:
        print("FINAL 6 REPORTS VERIFIED")
        print("Production data structure supported")
        print("Ready for LH submission")
        return 0
    else:
        print("FAILED")
        print("Reason: KPI mismatch or N/A remaining")
        return 1

if __name__ == "__main__":
    sys.exit(main())
