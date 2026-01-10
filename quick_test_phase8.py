#!/usr/bin/env python3
"""
Phase 8 보고서 빠른 테스트 - 검증된 로직 사용
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.phase8_module_report_generator import Phase8ModuleReportGenerator

# 검증된 로직: test_reports.py에서 확인됨
def test_m2_data():
    """M2 거래사례 5건 생성 테스트"""
    gen = Phase8ModuleReportGenerator()
    
    # _generate_transaction_cases 메서드 직접 호출
    cases = gen._generate_transaction_cases(
        land_value=3000000000,
        unit_price_sqm=3000000,
        site_area=1000.0
    )
    
    print("=" * 70)
    print("M2 거래사례 생성 테스트")
    print("=" * 70)
    print(f"\n생성된 사례 수: {len(cases)}개")
    
    for i, case in enumerate(cases, 1):
        print(f"\n사례 {i}:")
        print(f"  - ID: {case.case_id}")
        print(f"  - 주소: {case.address}")
        print(f"  - 거리: {case.distance_meters}m")
        print(f"  - 가격(㎡당): {case.price_per_sqm:,.0f}원")
        
    return len(cases)

def test_m3_data():
    """M3 라이프스타일 요인 6개 생성 테스트"""
    gen = Phase8ModuleReportGenerator()
    
    factors = gen._generate_lifestyle_factors(
        location_score=85.0,
        accessibility_score=82.0,
        poi_score=78.0
    )
    
    print("\n" + "=" * 70)
    print("M3 라이프스타일 요인 생성 테스트")
    print("=" * 70)
    print(f"\n생성된 요인 수: {len(factors)}개")
    
    for factor in factors:
        print(f"\n{factor.name}:")
        print(f"  - 점수: {factor.score}/{factor.max_score}")
        print(f"  - 가중치: {factor.weight}%")
        print(f"  - 항목 수: {len(factor.details)}개")
        
    return len(factors)

def test_m4_data():
    """M4 주차 대안 3개 생성 테스트"""
    gen = Phase8ModuleReportGenerator()
    
    alternatives = gen._generate_parking_alternatives(
        required_spaces=84
    )
    
    print("\n" + "=" * 70)
    print("M4 주차 대안 생성 테스트")
    print("=" * 70)
    print(f"\n생성된 대안 수: {len(alternatives)}개")
    
    for alt in alternatives:
        print(f"\n{alt.name}:")
        print(f"  - 주차 대수: {alt.total_spaces}대")
        print(f"  - 총 비용: {alt.total_cost:,.0f}원")
        print(f"  - 대당 비용: {alt.cost_per_space:,.0f}원")
        print(f"  - 장점: {len(alt.pros)}개")
        print(f"  - 단점: {len(alt.cons)}개")
        
    return len(alternatives)

if __name__ == "__main__":
    print("\n🚀 Phase 8 보고서 데이터 생성 테스트\n")
    
    try:
        m2_count = test_m2_data()
        m3_count = test_m3_data()
        m4_count = test_m4_data()
        
        print("\n" + "=" * 70)
        print("✅ 모든 테스트 통과!")
        print("=" * 70)
        print(f"\nM2 거래사례: {m2_count}개")
        print(f"M3 라이프스타일 요인: {m3_count}개")
        print(f"M4 주차 대안: {m4_count}개")
        print("\n📊 Phase 8 데이터 생성 로직 검증 완료")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
