#!/usr/bin/env python3
"""
M7 커뮤니티 계획 통합 테스트
"""

from app.services.final_report_assembler import FinalReportData, assemble_all_in_one_report

# 테스트 데이터 (M7 포함)
test_context = {
    "address": "서울시 마포구 월드컵북로 120",
    
    # M2-M6 데이터
    "m2_result": {
        "summary": {
            "land_value_total_krw": 1621848717,
            "pyeong_price_krw": 10723014,
            "confidence_pct": 85,
            "transaction_count": 10
        }
    },
    "m3_result": {
        "selected": {
            "type": "YOUTH",
            "name": "청년형",
            "confidence": 0.85,
            "secondary_name": "신혼부부형"
        },
        "scores": {
            "YOUTH": {
                "total": 85
            }
        }
    },
    "m4_result": {
        "summary": {
            "legal_units": 20,
            "incentive_units": 26,
            "parking_alt_a": 18,
            "parking_alt_b": 20
        }
    },
    "m5_result": {
        "summary": {
            "npv_public_krw": 340000000,
            "irr_pct": 4.8,
            "roi_pct": 5.2,
            "grade": "B+"
        }
    },
    "m6_result": {
        "summary": {
            "decision": "CONDITIONAL",
            "total_score": 85,
            "approval_probability_pct": 77,
            "grade": "A"
        }
    },
    
    # ✅ M7 커뮤니티 계획 데이터 (NEW)
    "m7_result": {
        "summary": {
            "primary_resident_type": "청년형",
            "community_goal_summary": "입주자 간 고립 방지 및 안전망 구축",
            "key_programs_count": 4,
            "operation_model": "LH 직접 운영",
            "sustainability_score": 75.0,
            "space_count": 3,
            "monthly_program_frequency": 2,
            "participation_target_pct": 30.0
        }
    }
}

print("=" * 70)
print("M7 커뮤니티 계획 통합 테스트")
print("=" * 70)
print()

# FinalReportData 생성
data = FinalReportData(test_context, "m7_test_integration")

# M7 파싱 확인
print("✅ FinalReportData.m7:")
if data.m7:
    print(f"   - primary_resident_type: {data.m7.primary_resident_type}")
    print(f"   - community_goal_summary: {data.m7.community_goal_summary}")
    print(f"   - key_programs_count: {data.m7.key_programs_count}")
    print(f"   - operation_model: {data.m7.operation_model}")
    print(f"   - space_count: {data.m7.space_count}")
    print(f"   - monthly_program_frequency: {data.m7.monthly_program_frequency}")
    print(f"   - participation_target_pct: {data.m7.participation_target_pct}%")
    print(f"   - sustainability_score: {data.m7.sustainability_score}")
else:
    print("   ❌ M7 파싱 실패 또는 데이터 없음")

print()

# 최종 보고서 조립
print("🔄 assemble_all_in_one_report 호출 중...")
result = assemble_all_in_one_report(data)

# M7 커뮤니티 계획 섹션 확인
print()
if "community_plan" in result and result["community_plan"]:
    print("✅ M7 커뮤니티 계획 섹션이 포함되었습니다!")
    print()
    print("📋 M7 커뮤니티 계획 섹션 내용:")
    cp = result["community_plan"]
    print(f"   - primary_resident_type: {cp.get('primary_resident_type')}")
    print(f"   - community_goal: {cp.get('community_goal')}")
    print(f"   - operation_model: {cp.get('operation_model')}")
    print(f"   - key_programs_count: {cp.get('key_programs_count')}")
    print(f"   - monthly_program_frequency: {cp.get('monthly_program_frequency')}")
    print(f"   - participation_target_pct: {cp.get('participation_target_pct')}%")
    print(f"   - space_count: {cp.get('space_count')}")
    print(f"   - sustainability_score: {cp.get('sustainability_score')}")
    
    print()
    print("📝 커뮤니티 목표 해석:")
    print(cp.get('goal_interpretation', '없음')[:200] + "...")
    
    print()
    print("📝 프로그램 운영 계획:")
    print(cp.get('program_plan', '없음')[:200] + "...")
    
else:
    print("❌ M7 커뮤니티 계획 섹션이 최종 보고서에 포함되지 않았습니다.")
    print(f"   result keys: {list(result.keys())}")

print()
print("=" * 70)
print("테스트 완료")
print("=" * 70)
