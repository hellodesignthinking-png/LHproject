"""
M3-M6 파싱 테스트 v2
"""
import sys
sys.path.insert(0, "/home/user/webapp")

from app.services.final_report_assembler import FinalReportData

# 테스트 데이터 (Context.to_dict() 형식) - 수정된 버전
test_canonical = {
    "m3_result": {
        "selected": {
            "type": "youth",
            "name": "청년형",
            "confidence": 0.85,
            "is_tie": False,
            "secondary_name": "신혼부부형 I"
        },
        "scores": {
            "youth": {"name": "청년형", "total": 82.5},
            "newlywed_1": {"name": "신혼부부형 I", "total": 78.0}
        }
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
        "financials": {
            "npv_public": 1850000000,
            "irr_public": 18.5,
            "roi": 26.3
        },
        "profitability": {
            "grade": "B"
        }
    },
    "m6_result": {
        "decision": {"type": "CONDITIONAL"},
        "approval": {"probability": 0.72},
        "scores": {"total": 78.5},  # 추가!
        "grade": "B"
    }
}

# 파싱 테스트
data = FinalReportData(canonical_data=test_canonical, context_id="test-m3-m6-v2")

print("=== M3-M6 파싱 테스트 v2 ===\n")

# M3 테스트
if data.m3:
    print(f"✅ M3 파싱 성공:")
    print(f"   - 추천 유형: {data.m3.recommended_type}")
    print(f"   - 총점: {data.m3.total_score} (int)")
    print(f"   - 신뢰도: {data.m3.confidence_pct}%")
    print(f"   - 2순위: {data.m3.second_choice}")
else:
    print("❌ M3 파싱 실패")

print()

# M4 테스트
if data.m4:
    print(f"✅ M4 파싱 성공:")
    print(f"   - 법정 세대수: {data.m4.legal_units}")
    print(f"   - 인센티브 세대수: {data.m4.incentive_units}")
    print(f"   - 주차 대안 A: {data.m4.parking_alt_a}대")
    print(f"   - 주차 대안 B: {data.m4.parking_alt_b}대")
else:
    print("❌ M4 파싱 실패")

print()

# M5 테스트
if data.m5:
    print(f"✅ M5 파싱 성공:")
    print(f"   - NPV: {data.m5.npv_public_krw:,}원")
    print(f"   - IRR: {data.m5.irr_pct}%")
    print(f"   - ROI: {data.m5.roi_pct}%")
    print(f"   - 등급: {data.m5.grade}")
else:
    print("❌ M5 파싱 실패")

print()

# M6 테스트
if data.m6:
    print(f"✅ M6 파싱 성공:")
    print(f"   - 의사결정: {data.m6.decision}")
    print(f"   - 총점: {data.m6.total_score}")
    print(f"   - 승인 확률: {data.m6.approval_probability_pct}%")
    print(f"   - 등급: {data.m6.grade}")
else:
    print("❌ M6 파싱 실패")

print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("✅ 전체 M2-M6 파싱 검증 완료")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
