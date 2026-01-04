"""
CanonicalAppraisalResult 구조로 M2 파싱 테스트
"""
import sys
sys.path.insert(0, "/home/user/webapp")

from app.services.final_report_assembler import FinalReportData, assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html

# CanonicalAppraisalResult.to_context_dict() 실제 구조
test_canonical = {
    "m2_result": {
        "version": "v8.7",
        "locked": True,
        "calculation": {
            "base_price_per_sqm": 12000000,
            "premium_adjusted_per_sqm": 15000000,
            "land_area_sqm": 500.0,
            "final_appraised_total": 7500000000  # 75억
        },
        "confidence": {
            "overall_score": 0.82,  # 82%
            "factors": {
                "data_completeness": 0.85,
                "case_similarity": 0.80,
                "time_relevance": 0.81
            }
        },
        "transaction_cases": [
            {"address": "역삼동 123-40", "price": 14500000},
            {"address": "역삼동 123-50", "price": 15500000},
            {"address": "역삼동 123-60", "price": 15000000}
        ]
    },
    "m3_result": {
        "selected": {"type": "youth", "name": "청년형", "confidence": 0.85},
        "scores": {"youth": {"total": 82.5}}
    },
    "m4_result": {
        "legal_capacity": {"total_units": 150},
        "incentive_capacity": {"total_units": 180},
        "parking_solutions": {
            "alternative_A": {"total_parking": 180},
            "alternative_B": {"total_parking": 150}
        }
    },
    "m5_result": {
        "financials": {"npv_public": 1850000000, "irr_public": 18.5, "roi": 26.3},
        "profitability": {"grade": "B"}
    },
    "m6_result": {
        "decision": {"type": "CONDITIONAL"},
        "approval": {"probability": 0.72},
        "scores": {"total": 78.5},
        "grade": "B"
    }
}

print("=" * 80)
print("CanonicalAppraisalResult 구조 테스트")
print("=" * 80)

# M2 파싱 테스트
print("\n[Step 1] M2 파싱...")
data = FinalReportData(canonical_data=test_canonical, context_id="canonical-test")

if data.m2:
    print(f"✅ M2 파싱 성공:")
    print(f"   - 토지감정가: {data.m2.land_value_total_krw:,}원")
    print(f"   - 평당가격: {data.m2.pyeong_price_krw:,}원")
    print(f"   - 신뢰도: {data.m2.confidence_pct}%")
    print(f"   - 거래사례: {data.m2.transaction_count}건")
else:
    print("❌ M2 파싱 실패!")
    sys.exit(1)

# 전체 통합 테스트
print("\n[Step 2] Assembler → Renderer...")
assembled = assemble_final_report("all_in_one", test_canonical, "canonical-test")
html = render_final_report_html("all_in_one", assembled)

# N/A 검증
na_count = html.count("N/A (검증 필요)")
print(f"\n[Step 3] N/A 검증...")
print(f"   - 'N/A (검증 필요)' 발생 횟수: {na_count}")

# 실제 값 확인
print(f"\n[Step 4] 실제 값 출력 확인...")
checks = {
    "토지가치": "7,500,000,000",
    "평당가격": "49,587,000",  # 15,000,000 * 3.3058
    "신뢰도": "82",
    "거래사례": "3"
}

verified = 0
for name, expected in checks.items():
    if expected in html:
        print(f"   ✅ {name}: {expected}")
        verified += 1
    else:
        print(f"   ❌ {name}: {expected} 미발견")

print("\n" + "=" * 80)
if na_count == 0 and verified == len(checks):
    print("🎉 CANONICAL STRUCTURE PARSING VERIFIED")
    print("✅ Production-ready M2 parsing")
else:
    print(f"⚠️  N/A: {na_count}, Verified: {verified}/{len(checks)}")
print("=" * 80)
