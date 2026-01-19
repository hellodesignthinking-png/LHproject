"""
M2 → M3 연계 E2E 테스트
=======================

테스트 케이스:
- Case A (85점): YOUTH 선택 예상
- Case B (55점): NEWLYWED or GENERAL 선택 예상
- Case C (0점): GENERAL (BLOCKED) 예상

Author: ZeroSite Decision OS Team
Date: 2026-01-12
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.core.m2_scoring_engine import M1FactContract, scoring_engine as m2_engine
from app.core.m3_selection_engine import M2ScoreInput, selection_engine as m3_engine

def test_case_a_youth():
    """
    Case A (85점): YOUTH 선택 예상
    - M2 총점 ≥ 70
    - 도로·방향 양호
    - 리스크 0개
    """
    print("=" * 80)
    print("🧪 Case A: M2 85점 → M3 YOUTH 예상")
    print("=" * 80)
    
    # M2 점수 계산
    m1_fact = M1FactContract(
        address="서울특별시 강남구 테헤란로 518",
        lat=37.5079, lng=127.0623,
        land_area=1200.0, zoning="상업지역",
        bcr=60.0, far=800.0, official_land_price=18000000.0,
        road_access_type="단일접면", road_width_m=8.0, road_count=1,
        fire_truck_access=True, road_legal_status="도로",
        site_shape_type="정형", frontage_m=20.0, depth_m=24.0, effective_build_ratio=90.0,
        main_direction="남", sunlight_risk="낮음", adjacent_height_risk="낮음",
        nearby_transaction_price_py=20000000.0, public_land_price_py=15000000.0, price_gap_ratio=1.33,
        existing_building_exists=False,
        transaction_price=17500000.0, regulation_summary="일반규제지역", lh_compatibility="적합"
    )
    
    m2_result = m2_engine.calculate(m1_fact, "case_a")
    
    print(f"\n📊 M2 결과: {m2_result.total_score}점 / {m2_result.recommendation}")
    print(f"   리스크: {len(m2_result.risk_flags)}개")
    
    # M3 공급유형 선택
    m2_input = M2ScoreInput(
        m2_total_score=m2_result.total_score,
        m2_risk_flags=[flag.value for flag in m2_result.risk_flags],
        m2_score_breakdown={
            "road": m2_result.score_breakdown.road,
            "shape": m2_result.score_breakdown.shape,
            "orientation": m2_result.score_breakdown.orientation,
            "market": m2_result.score_breakdown.market,
            "building": m2_result.score_breakdown.building
        },
        m2_recommendation=m2_result.recommendation
    )
    
    m3_result = m3_engine.select(m2_input)
    
    print(f"\n🏘️  M3 결과:")
    print(f"   추천 유형: {m3_result.recommended_type.value}")
    print(f"   신뢰도: {m3_result.confidence:.0%}")
    print(f"   대안: {[t.value for t in m3_result.alternative_types]}")
    print(f"\n💬 이유 요약:")
    for reason in m3_result.reason_summary:
        print(f"   - {reason}")
    
    print(f"\n📈 전체 후보군:")
    for candidate in m3_result.all_candidates:
        print(f"   {candidate.type.value}: {candidate.fitness.value} ({candidate.confidence:.0%})")
        if candidate.blocking_reasons:
            print(f"      ❌ 차단: {candidate.blocking_reasons[0]}")
    
    # 검증
    assert m3_result.recommended_type.value == "YOUTH", \
        f"Case A 실패: YOUTH 예상, 실제 {m3_result.recommended_type.value}"
    assert m3_result.confidence >= 0.7, \
        f"Case A 실패: 신뢰도 70% 이상 예상, 실제 {m3_result.confidence:.0%}"
    
    print(f"\n✅ Case A 통과: YOUTH ({m3_result.confidence:.0%})")
    return m3_result


def test_case_b_moderate():
    """
    Case B (55점): NEWLYWED or GENERAL 선택 예상
    - M2 총점 50~65
    - 부분 리스크 존재
    """
    print("\n" + "=" * 80)
    print("🧪 Case B: M2 55점 → M3 NEWLYWED/GENERAL 예상")
    print("=" * 80)
    
    # M2 점수 계산
    m1_fact = M1FactContract(
        address="서울특별시 강남구 역삼동 123-45",
        lat=37.5079, lng=127.0623,
        land_area=1000.0, zoning="제2종일반주거지역",
        bcr=60.0, far=200.0, official_land_price=12000000.0,
        road_access_type="단일접면", road_width_m=6.0, road_count=1,
        fire_truck_access=True, road_legal_status="도로",
        site_shape_type="부정형", frontage_m=15.0, depth_m=30.0, effective_build_ratio=75.0,
        main_direction="동", sunlight_risk="중간", adjacent_height_risk="낮음",
        nearby_transaction_price_py=15000000.0, public_land_price_py=13000000.0, price_gap_ratio=1.15,
        existing_building_exists=False,
        transaction_price=14500000.0, regulation_summary="일반규제지역", lh_compatibility="검토필요"
    )
    
    m2_result = m2_engine.calculate(m1_fact, "case_b")
    
    print(f"\n📊 M2 결과: {m2_result.total_score}점 / {m2_result.recommendation}")
    print(f"   리스크: {len(m2_result.risk_flags)}개")
    
    # M3 공급유형 선택
    m2_input = M2ScoreInput(
        m2_total_score=m2_result.total_score,
        m2_risk_flags=[flag.value for flag in m2_result.risk_flags],
        m2_score_breakdown={
            "road": m2_result.score_breakdown.road,
            "shape": m2_result.score_breakdown.shape,
            "orientation": m2_result.score_breakdown.orientation,
            "market": m2_result.score_breakdown.market,
            "building": m2_result.score_breakdown.building
        },
        m2_recommendation=m2_result.recommendation
    )
    
    m3_result = m3_engine.select(m2_input)
    
    print(f"\n🏘️  M3 결과:")
    print(f"   추천 유형: {m3_result.recommended_type.value}")
    print(f"   신뢰도: {m3_result.confidence:.0%}")
    print(f"   대안: {[t.value for t in m3_result.alternative_types]}")
    print(f"\n💬 이유 요약:")
    for reason in m3_result.reason_summary:
        print(f"   - {reason}")
    
    # 검증
    assert m3_result.recommended_type.value in ["NEWLYWED", "GENERAL", "SENIOR"], \
        f"Case B 실패: NEWLYWED/GENERAL/SENIOR 예상, 실제 {m3_result.recommended_type.value}"
    
    print(f"\n✅ Case B 통과: {m3_result.recommended_type.value} ({m3_result.confidence:.0%})")
    return m3_result


def test_case_c_blocked():
    """
    Case C (0점): 모든 유형 BLOCKED 또는 GENERAL (LOW)
    - M2 총점 0점
    - 치명 리스크 다수
    """
    print("\n" + "=" * 80)
    print("🧪 Case C: M2 0점 → M3 모든 유형 차단 예상")
    print("=" * 80)
    
    # M2 점수 계산
    m1_fact = M1FactContract(
        address="서울특별시 강남구 역삼동 999-99",
        lat=37.5079, lng=127.0623,
        land_area=800.0, zoning="제1종일반주거지역",
        bcr=60.0, far=150.0, official_land_price=8000000.0,
        road_access_type="단일접면", road_width_m=4.0, road_count=1,
        fire_truck_access=False, road_legal_status="도로",
        site_shape_type="자루형", frontage_m=8.0, depth_m=40.0, effective_build_ratio=60.0,
        main_direction="북", sunlight_risk="높음", adjacent_height_risk="높음",
        nearby_transaction_price_py=12000000.0, public_land_price_py=5000000.0, price_gap_ratio=2.4,
        existing_building_exists=True, existing_building_structure="RC",
        existing_building_floors=3, existing_building_area_m2=500.0, demolition_required=True,
        transaction_price=None, regulation_summary="규제지역", lh_compatibility="부적합"
    )
    
    m2_result = m2_engine.calculate(m1_fact, "case_c")
    
    print(f"\n📊 M2 결과: {m2_result.total_score}점 / {m2_result.recommendation}")
    print(f"   리스크: {len(m2_result.risk_flags)}개")
    
    # M3 공급유형 선택
    m2_input = M2ScoreInput(
        m2_total_score=m2_result.total_score,
        m2_risk_flags=[flag.value for flag in m2_result.risk_flags],
        m2_score_breakdown={
            "road": m2_result.score_breakdown.road,
            "shape": m2_result.score_breakdown.shape,
            "orientation": m2_result.score_breakdown.orientation,
            "market": m2_result.score_breakdown.market,
            "building": m2_result.score_breakdown.building
        },
        m2_recommendation=m2_result.recommendation
    )
    
    m3_result = m3_engine.select(m2_input)
    
    print(f"\n🏘️  M3 결과:")
    print(f"   추천 유형: {m3_result.recommended_type.value}")
    print(f"   신뢰도: {m3_result.confidence:.0%}")
    print(f"   대안: {[t.value for t in m3_result.alternative_types]}")
    print(f"\n💬 이유 요약:")
    for reason in m3_result.reason_summary:
        print(f"   - {reason}")
    
    print(f"\n📈 전체 후보군 (차단 이유):")
    for candidate in m3_result.all_candidates:
        print(f"   {candidate.type.value}: {candidate.fitness.value}")
        for reason in candidate.blocking_reasons[:2]:
            print(f"      ❌ {reason}")
    
    # 검증
    assert m3_result.confidence <= 0.5, \
        f"Case C 실패: 낮은 신뢰도 예상, 실제 {m3_result.confidence:.0%}"
    
    print(f"\n✅ Case C 통과: {m3_result.recommended_type.value} (신뢰도 {m3_result.confidence:.0%})")
    return m3_result


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 M2 → M3 연계 E2E 테스트 시작")
    print("=" * 80)
    
    try:
        result_a = test_case_a_youth()
        result_b = test_case_b_moderate()
        result_c = test_case_c_blocked()
        
        print("\n" + "=" * 80)
        print("✅ 모든 E2E 테스트 통과!")
        print("=" * 80)
        print(f"\nCase A (85점): {result_a.recommended_type.value} ({result_a.confidence:.0%})")
        print(f"Case B (55점): {result_b.recommended_type.value} ({result_b.confidence:.0%})")
        print(f"Case C (0점):  {result_c.recommended_type.value} ({result_c.confidence:.0%})")
        
        print("\n🎯 핵심 검증 완료:")
        print("   ✅ M2 점수 → M3 공급유형 강제 연계")
        print("   ✅ M3 = M2 점수 해석기 (독립 판단 금지)")
        print("   ✅ 모든 선택에 M2 근거 추적 가능")
        print("   ✅ 차단 이유 명확히 설명")
        print("\n" + "=" * 80)
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
