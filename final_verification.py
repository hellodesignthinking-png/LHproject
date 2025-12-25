"""
최종 검증: 6종 보고서 재생성 + KPI 검증
목적: 출고 가능 여부 확정
"""
import sys
sys.path.insert(0, "/home/user/webapp")

from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html

# 실제 프로덕션 구조 (CanonicalAppraisalResult)
canonical_data = {
    "m2_result": {
        "version": "v8.7",
        "locked": True,
        "calculation": {
            "base_price_per_sqm": 12000000,
            "premium_adjusted_per_sqm": 15000000,
            "land_area_sqm": 500.0,
            "final_appraised_total": 7500000000
        },
        "confidence": {
            "overall_score": 0.82
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

context_id = "final-verification-001"

print("=" * 80)
print("🎯 FINAL VERIFICATION - 6 REPORTS")
print("=" * 80)

# 6종 보고서 목록
report_types = [
    "quick_check",
    "financial_feasibility", 
    "lh_technical",
    "executive_summary",
    "landowner_summary",
    "all_in_one"
]

# KPI 기대값
expected_kpis = {
    "토지감정가": "7,500,000,000",
    "평당가격": "49,587,000",
    "신뢰도": "82",
    "거래사례": "3",
    "총세대수": "180",
    "NPV": "1,850,000,000",
    "IRR": "18.5",
    "주택유형": "청년형",
    "LH판단": "CONDITIONAL"
}

print("\n[Step 1] 6종 보고서 생성...")
reports = {}
failed = []

for report_type in report_types:
    try:
        print(f"\n   {report_type}...")
        assembled = assemble_final_report(report_type, canonical_data, context_id)
        html = render_final_report_html(report_type, assembled)
        reports[report_type] = html
        print(f"      ✅ 생성 성공 ({len(html):,} chars)")
    except Exception as e:
        print(f"      ❌ 생성 실패: {e}")
        failed.append(report_type)

if failed:
    print(f"\n❌ 보고서 생성 실패: {failed}")
    print("\nFAILED")
    print("Reason: PDF not regenerated")
    sys.exit(1)

print(f"\n✅ 6종 보고서 생성 완료 (총 {len(reports)}개)")

# 1-2. KPI 핵심 값 육안 검증
print("\n" + "=" * 80)
print("[Step 2] KPI 핵심 값 검증...")
print("=" * 80)

kpi_results = {}
for report_type, html in reports.items():
    kpi_results[report_type] = {}
    for kpi_name, expected in expected_kpis.items():
        found = expected in html
        kpi_results[report_type][kpi_name] = found

# 결과 출력
all_pass = True
for kpi_name in expected_kpis:
    results = [kpi_results[rt][kpi_name] for rt in report_types]
    status = "✅" if all(results) else "❌"
    consistency = "✅" if len(set(results)) == 1 else "❌ 불일치"
    print(f"\n{status} {kpi_name}: {expected_kpis[kpi_name]}")
    
    if not all(results):
        all_pass = False
        missing = [rt for rt in report_types if not kpi_results[rt][kpi_name]]
        print(f"      ❌ 누락: {missing}")
    elif len(set(results)) > 1:
        all_pass = False
        print(f"      {consistency}")

if not all_pass:
    print("\n❌ KPI 검증 실패")
    print("\nFAILED")
    print("Reason: KPI inconsistency")
    sys.exit(1)

# 1-3. N/A 잔존 여부 확인
print("\n" + "=" * 80)
print("[Step 3] N/A 잔존 여부 확인...")
print("=" * 80)

forbidden_strings = ["N/A (검증 필요)", "검증 필요", "None"]
na_found = {}

for report_type, html in reports.items():
    na_count = 0
    for forbidden in forbidden_strings:
        na_count += html.count(forbidden)
    na_found[report_type] = na_count
    
    status = "✅" if na_count == 0 else "❌"
    print(f"\n{status} {report_type}: {na_count}개")

total_na = sum(na_found.values())
if total_na > 0:
    print(f"\n❌ N/A 잔존: 총 {total_na}개")
    print("\nFAILED")
    print("Reason: N/A still present")
    sys.exit(1)

print(f"\n✅ N/A 검증 통과 (총 0개)")

# 최종 판정
print("\n" + "=" * 80)
print("📊 최종 검증 결과")
print("=" * 80)
print(f"\n✅ 6종 보고서 생성: 성공")
print(f"✅ KPI 일치성: 통과 (9개 항목)")
print(f"✅ N/A 제거: 통과 (0개)")
print(f"✅ 데이터 구조: CanonicalAppraisalResult 지원")

print("\n" + "=" * 80)
print("🎉 FINAL 6 REPORTS VERIFIED")
print("Production data structure supported")
print("Ready for LH submission")
print("=" * 80)

# HTML 파일 저장 (선택적)
print("\n💾 HTML 파일 저장...")
for report_type, html in reports.items():
    filename = f"/home/user/webapp/final_output_{report_type}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"   ✅ {filename}")

print("\n✅ 최종 검증 완료")
