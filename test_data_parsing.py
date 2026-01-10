#!/usr/bin/env python3
"""
데이터 파싱 디버깅 스크립트
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.final_report_assembler import FinalReportData, assemble_all_in_one_report
import json

# 테스트 컨텍스트 데이터
test_context = {
    "address": "서울시 마포구 월드컵북로 120",
    "parcel_id": "116801010001230045",
    "generated_at": "2026-01-10 10:13:37",
    
    # M2 데이터 (v4.0 표준 구조)
    "m2_result": {
        "summary": {
            "land_value_total_krw": 1621848717,
            "pyeong_price_krw": 10723014,
            "confidence_pct": 85,
            "transaction_count": 10
        }
    },
    
    # M3 데이터 (v4.0 표준 구조)
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
    
    # M4 데이터 (v4.0 표준 구조)
    "m4_result": {
        "summary": {
            "legal_units": 20,
            "incentive_units": 26,
            "parking_alt_a": 18,
            "parking_alt_b": 20
        }
    },
    
    # M5 데이터 (v4.0 표준 구조)
    "m5_result": {
        "summary": {
            "npv_public_krw": 340000000,
            "irr_pct": 4.8,
            "roi_pct": 5.2,
            "grade": "B+"
        }
    },
    
    # M6 데이터 (v4.0 표준 구조)
    "m6_result": {
        "summary": {
            "decision": "CONDITIONAL",
            "total_score": 85,
            "grade": "A",
            "approval_probability_pct": 77
        }
    },
}

print("=" * 60)
print("데이터 파싱 테스트")
print("=" * 60)

# FinalReportData 인스턴스 생성
data = FinalReportData(test_context, "test_demo_debug")

print(f"\n✅ FinalReportData 생성됨")
print(f"   - M2: {data.m2}")
print(f"   - M3: {data.m3}")
print(f"   - M4: {data.m4}")
print(f"   - M5: {data.m5}")
print(f"   - M6: {data.m6}")

# assemble_all_in_one_report 호출
print(f"\n🔄 assemble_all_in_one_report 호출 중...")
assembled = assemble_all_in_one_report(data)

print(f"\n✅ 조립 완료!")
print(f"\n주요 데이터:")
print(f"   - land_value_krw: {assembled.get('land_value_krw')}")
print(f"   - recommended_housing_type: {assembled.get('recommended_housing_type')}")
print(f"   - legal_units: {assembled.get('legal_units')}")
print(f"   - npv_krw: {assembled.get('npv_krw')}")
print(f"   - final_decision: {assembled.get('final_decision')}")
print(f"   - approval_probability_pct: {assembled.get('approval_probability_pct')}")

print(f"\n📄 전체 조립 데이터:")
print(json.dumps(assembled, indent=2, ensure_ascii=False))
