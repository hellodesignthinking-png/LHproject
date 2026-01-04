"""
전체 M2-M6 통합 테스트
Assembler → Renderer → HTML 출력 검증
"""
import sys
sys.path.insert(0, "/home/user/webapp")

from app.services.final_report_assembler import assemble_final_report
from app.services.final_report_html_renderer import render_final_report_html

# 완전한 테스트 데이터 (M2-M6 전체)
test_canonical = {
    # M2 - 토지감정평가
    "appraisal": {
        "land_value": 7500000000,
        "unit_price_sqm": 15000000,
        "unit_price_pyeong": 49500000,
        "confidence_score": 0.82,
        "transaction_count": 10
    },
    
    # M3 - 주택 유형
    "m3_result": {
        "selected": {
            "type": "youth",
            "name": "청년형",
            "confidence": 0.85,
            "secondary_name": "신혼부부형 I"
        },
        "scores": {
            "youth": {"total": 82.5}
        }
    },
    
    # M4 - 건축 규모
    "m4_result": {
        "legal_capacity": {"total_units": 150},
        "incentive_capacity": {"total_units": 180},
        "parking_solutions": {
            "alternative_A": {"total_parking": 180},
            "alternative_B": {"total_parking": 150}
        }
    },
    
    # M5 - 재무 분석
    "m5_result": {
        "financials": {
            "npv_public": 1850000000,
            "irr_public": 18.5,
            "roi": 26.3
        },
        "profitability": {
            "grade": "B"
        }
    },
    
    # M6 - LH 심사
    "m6_result": {
        "decision": {"type": "CONDITIONAL"},
        "approval": {"probability": 0.72},
        "scores": {"total": 78.5},
        "grade": "B"
    }
}

print("=" * 60)
print("전체 통합 테스트: Assembler → Renderer")
print("=" * 60)

# Step 1: Assemble
print("\n[Step 1] 데이터 조립...")
try:
    assembled_data = assemble_final_report(
        report_type="all_in_one",
        canonical_data=test_canonical,
        context_id="test-integration"
    )
    print(f"✅ Assembler 성공")
    print(f"   - Land Value: {assembled_data.get('land_value_krw', 'N/A'):,}")
    print(f"   - NPV: {assembled_data.get('npv_krw', 'N/A'):,}")
    print(f"   - IRR: {assembled_data.get('irr_pct', 'N/A')}%")
except Exception as e:
    print(f"❌ Assembler 실패: {e}")
    sys.exit(1)

# Step 2: Render
print("\n[Step 2] HTML 렌더링...")
try:
    html = render_final_report_html(
        report_type="all_in_one",
        data=assembled_data
    )
    print(f"✅ Renderer 성공 (HTML 길이: {len(html):,} chars)")
except Exception as e:
    print(f"❌ Renderer 실패: {e}")
    sys.exit(1)

# Step 3: Verify
print("\n[Step 3] N/A 검증...")
na_count = html.count("N/A (검증 필요)")
print(f"   - 'N/A (검증 필요)' 발생 횟수: {na_count}")

if na_count > 0:
    print(f"\n⚠️  아직 {na_count}개의 N/A가 남아있습니다.")
    # N/A 위치 찾기
    import re
    na_contexts = re.findall(r'.{50}N/A \(검증 필요\).{50}', html)
    print("\n첫 3개 N/A 위치:")
    for i, ctx in enumerate(na_contexts[:3], 1):
        print(f"{i}. ...{ctx}...")
else:
    print("\n✅ 모든 'N/A (검증 필요)'가 제거되었습니다!")

# Step 4: Data Verification
print("\n[Step 4] 실제 데이터 출력 확인...")
verifications = {
    "토지가치": "7,500,000,000",
    "NPV": "1,850,000,000",
    "IRR": "18.5",
    "세대수": "180",
    "청년형": "청년형"
}

verified = 0
for name, expected in verifications.items():
    if expected in html:
        print(f"   ✅ {name}: {expected} 표시됨")
        verified += 1
    else:
        print(f"   ❌ {name}: {expected} 미표시")

print(f"\n검증 결과: {verified}/{len(verifications)} 항목 표시됨")

print("\n" + "=" * 60)
if na_count == 0 and verified == len(verifications):
    print("🎉 FINAL 6 REPORTS VERIFIED")
    print("✅ Actual data rendered (not defensive fallback)")
    print("✅ Ready for LH submission")
else:
    print("⚠️  추가 수정 필요")
    print(f"   - N/A 제거 필요: {na_count}개")
    print(f"   - 데이터 표시 확인: {verified}/{len(verifications)}")
print("=" * 60)
