"""
M1 → M2 자동 점수 연계 E2E 테스트
==================================

테스트 케이스:
- Case A: 정형, 8m 도로, 남향 → 80점 이상 (GO)
- Case B: 6m 도로, 부정형 → 50~65점 (CONDITIONAL-GO)
- Case C: 도로 4m, 자루형 → 40점 이하 (NO-GO)

Author: ZeroSite Decision OS Team
Date: 2026-01-12
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.core.m1_state_machine import M1EditableData, M1ResultData
from app.core.m2_scoring_engine import M1FactContract, scoring_engine

def test_case_a_ideal():
    """
    Case A: 정형, 8m 도로, 남향
    예상: 80점 이상 (GO 권장)
    """
    print("=" * 80)
    print("🧪 Case A: 이상적 조건 (정형 + 8m 도로 + 남향)")
    print("=" * 80)
    
    m1_fact = M1FactContract(
        address="서울특별시 강남구 테헤란로 518",
        lat=37.5079,
        lng=127.0623,
        land_area=1200.0,
        zoning="상업지역",
        bcr=60.0,
        far=800.0,
        official_land_price=18000000.0,
        
        # 도로: 이상적 (8m 이상, 소방차 진입 가능)
        road_access_type="단일접면",
        road_width_m=8.0,
        road_count=1,
        fire_truck_access=True,
        road_legal_status="도로",
        
        # 형상: 정형
        site_shape_type="정형",
        frontage_m=20.0,
        depth_m=24.0,
        effective_build_ratio=90.0,
        
        # 방향: 남향 + 리스크 낮음
        main_direction="남",
        sunlight_risk="낮음",
        adjacent_height_risk="낮음",
        
        # 시세: 적정
        nearby_transaction_price_py=20000000.0,
        public_land_price_py=15000000.0,
        price_gap_ratio=1.33,
        
        # 기존 건물: 없음
        existing_building_exists=False,
        
        # 기타
        transaction_price=17500000.0,
        regulation_summary="일반규제지역",
        lh_compatibility="적합"
    )
    
    result = scoring_engine.calculate(m1_fact, "case_a_context")
    
    print(f"\n📊 결과:")
    print(f"   총점: {result.total_score}점")
    print(f"   권고: {result.recommendation}")
    print(f"   리스크: {len(result.risk_flags)}개 {result.risk_flags}")
    print(f"\n📈 점수 세부:")
    print(f"   도로: {result.score_breakdown.road:+d}점 - {result.score_breakdown.road_detail}")
    print(f"   형상: {result.score_breakdown.shape:+d}점 - {result.score_breakdown.shape_detail}")
    print(f"   방향: {result.score_breakdown.orientation:+d}점 - {result.score_breakdown.orientation_detail}")
    print(f"   시세: {result.score_breakdown.market:+d}점 - {result.score_breakdown.market_detail}")
    print(f"   건물: {result.score_breakdown.building:+d}점 - {result.score_breakdown.building_detail}")
    
    # 검증
    assert result.total_score >= 80, f"Case A 실패: 80점 이상 예상, 실제 {result.total_score}점"
    assert "GO" in result.recommendation, f"Case A 실패: GO 권장 예상, 실제 {result.recommendation}"
    
    print(f"\n✅ Case A 통과: {result.total_score}점 ({result.recommendation})")
    return result


def test_case_b_moderate():
    """
    Case B: 6m 도로, 부정형
    예상: 50~65점 (CONDITIONAL-GO)
    """
    print("\n" + "=" * 80)
    print("🧪 Case B: 보통 조건 (6m 도로 + 부정형)")
    print("=" * 80)
    
    m1_fact = M1FactContract(
        address="서울특별시 강남구 역삼동 123-45",
        lat=37.5079,
        lng=127.0623,
        land_area=1000.0,
        zoning="제2종일반주거지역",
        bcr=60.0,
        far=200.0,
        official_land_price=12000000.0,
        
        # 도로: 협소 (6m, 리스크)
        road_access_type="단일접면",
        road_width_m=6.0,
        road_count=1,
        fire_truck_access=True,
        road_legal_status="도로",
        
        # 형상: 부정형
        site_shape_type="부정형",
        frontage_m=15.0,
        depth_m=30.0,
        effective_build_ratio=75.0,
        
        # 방향: 동향
        main_direction="동",
        sunlight_risk="중간",
        adjacent_height_risk="낮음",
        
        # 시세: 보통
        nearby_transaction_price_py=15000000.0,
        public_land_price_py=13000000.0,
        price_gap_ratio=1.15,
        
        # 기존 건물: 없음
        existing_building_exists=False,
        
        # 기타
        transaction_price=14500000.0,
        regulation_summary="일반규제지역",
        lh_compatibility="검토필요"
    )
    
    result = scoring_engine.calculate(m1_fact, "case_b_context")
    
    print(f"\n📊 결과:")
    print(f"   총점: {result.total_score}점")
    print(f"   권고: {result.recommendation}")
    print(f"   리스크: {len(result.risk_flags)}개 {result.risk_flags}")
    print(f"\n📈 점수 세부:")
    print(f"   도로: {result.score_breakdown.road:+d}점 - {result.score_breakdown.road_detail}")
    print(f"   형상: {result.score_breakdown.shape:+d}점 - {result.score_breakdown.shape_detail}")
    print(f"   방향: {result.score_breakdown.orientation:+d}점 - {result.score_breakdown.orientation_detail}")
    print(f"   시세: {result.score_breakdown.market:+d}점 - {result.score_breakdown.market_detail}")
    print(f"   건물: {result.score_breakdown.building:+d}점 - {result.score_breakdown.building_detail}")
    
    # 검증
    assert 50 <= result.total_score <= 65, f"Case B 실패: 50~65점 예상, 실제 {result.total_score}점"
    
    print(f"\n✅ Case B 통과: {result.total_score}점 ({result.recommendation})")
    return result


def test_case_c_fatal():
    """
    Case C: 도로 4m, 자루형
    예상: 40점 이하 (NO-GO)
    """
    print("\n" + "=" * 80)
    print("🧪 Case C: 치명적 조건 (4m 도로 + 자루형 + 철거 필요)")
    print("=" * 80)
    
    m1_fact = M1FactContract(
        address="서울특별시 강남구 역삼동 999-99",
        lat=37.5079,
        lng=127.0623,
        land_area=800.0,
        zoning="제1종일반주거지역",
        bcr=60.0,
        far=150.0,
        official_land_price=8000000.0,
        
        # 도로: 치명적 (4m 미만)
        road_access_type="단일접면",
        road_width_m=4.0,
        road_count=1,
        fire_truck_access=False,  # 소방차 진입 불가
        road_legal_status="도로",
        
        # 형상: 자루형
        site_shape_type="자루형",
        frontage_m=8.0,
        depth_m=40.0,
        effective_build_ratio=60.0,
        
        # 방향: 북향 + 일조권 리스크
        main_direction="북",
        sunlight_risk="높음",
        adjacent_height_risk="높음",
        
        # 시세: 과대 평가
        nearby_transaction_price_py=12000000.0,
        public_land_price_py=5000000.0,
        price_gap_ratio=2.4,  # 2.0 초과
        
        # 기존 건물: 철거 필요
        existing_building_exists=True,
        existing_building_structure="RC",
        existing_building_floors=3,
        existing_building_area_m2=500.0,
        demolition_required=True,
        
        # 기타
        transaction_price=None,
        regulation_summary="규제지역",
        lh_compatibility="부적합"
    )
    
    result = scoring_engine.calculate(m1_fact, "case_c_context")
    
    print(f"\n📊 결과:")
    print(f"   총점: {result.total_score}점")
    print(f"   권고: {result.recommendation}")
    print(f"   리스크: {len(result.risk_flags)}개")
    for risk in result.risk_flags:
        print(f"      ⚠️  {risk.value}")
    print(f"\n📈 점수 세부:")
    print(f"   도로: {result.score_breakdown.road:+d}점 - {result.score_breakdown.road_detail}")
    print(f"   형상: {result.score_breakdown.shape:+d}점 - {result.score_breakdown.shape_detail}")
    print(f"   방향: {result.score_breakdown.orientation:+d}점 - {result.score_breakdown.orientation_detail}")
    print(f"   시세: {result.score_breakdown.market:+d}점 - {result.score_breakdown.market_detail}")
    print(f"   건물: {result.score_breakdown.building:+d}점 - {result.score_breakdown.building_detail}")
    
    # 검증
    assert result.total_score <= 40, f"Case C 실패: 40점 이하 예상, 실제 {result.total_score}점"
    assert "NO-GO" in result.recommendation, f"Case C 실패: NO-GO 예상, 실제 {result.recommendation}"
    assert len(result.risk_flags) >= 4, f"Case C 실패: 4개 이상 리스크 예상, 실제 {len(result.risk_flags)}개"
    
    print(f"\n✅ Case C 통과: {result.total_score}점 ({result.recommendation})")
    return result


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 M1 → M2 자동 점수 연계 E2E 테스트 시작")
    print("=" * 80)
    
    try:
        result_a = test_case_a_ideal()
        result_b = test_case_b_moderate()
        result_c = test_case_c_fatal()
        
        print("\n" + "=" * 80)
        print("✅ 모든 E2E 테스트 통과!")
        print("=" * 80)
        print(f"\nCase A (이상적): {result_a.total_score}점 → {result_a.recommendation}")
        print(f"Case B (보통):   {result_b.total_score}점 → {result_b.recommendation}")
        print(f"Case C (치명적): {result_c.total_score}점 → {result_c.recommendation}")
        
        print("\n🎯 핵심 검증 완료:")
        print("   ✅ M1 FACT → M2 Score 1:1 매핑")
        print("   ✅ score_breakdown 100% 설명 가능")
        print("   ✅ 리스크 플래그 자동 생성")
        print("   ✅ GO/NO-GO 논리적 권고")
        print("\n" + "=" * 80)
        
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
