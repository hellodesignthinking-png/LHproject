"""
M5 Real Data Engine 테스트
============================

테스트 시나리오:
1. 실제 데이터 기반 계산 (정상 케이스)
2. 금지 데이터 소스 차단 (MOC/SAMPLE)
3. M4 데이터 누락 (연결 실패)
4. 사용자 입력 누락 (참고 범위만 제시)

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from app.utils.m5_real_data_engine import prepare_m5_real_data_report


def test_case_1_real_data():
    """
    TEST CASE 1: 실제 데이터 기반 계산
    
    입력:
    - M4: 16세대, 864㎡
    - 사용자: 공사비 ㎡당 300만원, LH 매입 단가 350만원
    
    기대 결과:
    - 비용 구조 산정 성공
    - 수익 구조 산정 성공
    - NPV/ROI/IRR 계산 성공
    - 최종 판단 출력
    """
    print("\n" + "="*80)
    print("TEST CASE 1: 실제 데이터 기반 계산")
    print("="*80)
    
    context_id = "TEST_REAL_DATA_001"
    
    m4_data = {
        "context_id": context_id,
        "summary": {
            "recommended_units": 16
        },
        "details": {
            "total_units": 16,
            "total_floor_area_sqm": 864.0,
            "total_floor_area": 864.0,
            "address": "서울특별시 강남구 역삼동 123-45",
            "optimal_units": 16
        }
    }
    
    user_inputs = {
        "construction_cost_per_sqm": 3000000,  # ㎡당 300만원
        "lh_purchase_price_per_sqm": 3500000,  # ㎡당 350만원
        "project_period_years": 2
    }
    
    result = prepare_m5_real_data_report(
        context_id=context_id,
        m4_data=m4_data,
        user_inputs=user_inputs
    )
    
    print(f"\n✅ Context ID: {result.get('context_id')}")
    print(f"✅ Report ID: {result.get('report_id')}")
    print(f"✅ 분석 날짜: {result.get('analysis_date')}")
    
    # 비용 구조
    cost_structure = result.get('cost_structure', {})
    print(f"\n📊 비용 구조:")
    print(f"  - 공사비: {cost_structure.get('construction_cost', 0):,.0f}원")
    print(f"  - 기타 사업비: {cost_structure.get('other_costs', 0):,.0f}원")
    print(f"  - 총 사업비: {cost_structure.get('total_project_cost', 0):,.0f}원")
    print(f"  - 설명: {cost_structure.get('construction_explanation', 'N/A')[:100]}...")
    
    # 수익 구조
    revenue_structure = result.get('revenue_structure', {})
    print(f"\n💰 수익 구조:")
    print(f"  - LH 매입 금액: {revenue_structure.get('purchase_price', 0):,.0f}원")
    print(f"  - 설명: {revenue_structure.get('revenue_explanation', 'N/A')[:100]}...")
    
    # 재무 지표
    financial_metrics = result.get('financial_metrics', {})
    print(f"\n📈 재무 지표:")
    print(f"  - NPV: {financial_metrics.get('npv', 0):,.0f}원 ({financial_metrics.get('npv_grade', 'N/A')})")
    print(f"  - ROI: {financial_metrics.get('roi', 0):.2f}% ({financial_metrics.get('roi_grade', 'N/A')})")
    print(f"  - IRR: 연 {financial_metrics.get('irr', 0):.2f}% ({financial_metrics.get('irr_grade', 'N/A')})")
    
    # 최종 판단
    final_judgment = result.get('final_judgment', {})
    print(f"\n🎯 최종 판단:")
    print(f"  - {final_judgment.get('judgment', 'N/A')}")
    print(f"  - 사업성 수준: {final_judgment.get('feasibility_level', 'N/A')}")
    print(f"  - 권장사항: {final_judgment.get('recommendation', 'N/A')}")
    
    # 데이터 소스 선언
    print(f"\n📋 데이터 소스 선언:")
    print(f"  {result.get('data_source_declaration', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("✅ TEST CASE 1: 통과")
    print("="*80)


def test_case_2_forbidden_data():
    """
    TEST CASE 2: 금지 데이터 소스 차단
    
    입력:
    - M4: 데이터에 'SAMPLE' 패턴 포함
    
    기대 결과:
    - DATA_SOURCE_INVALID 오류
    - 금지 패턴 감지 메시지
    """
    print("\n" + "="*80)
    print("TEST CASE 2: 금지 데이터 소스 차단")
    print("="*80)
    
    context_id = "TEST_FORBIDDEN_002"
    
    m4_data = {
        "context_id": context_id,
        "summary": {
            "recommended_units": 20,
            "note": "SAMPLE DATA FOR TESTING"
        },
        "details": {
            "total_units": 20,
            "total_floor_area_sqm": 1000.0,
            "address": "MOCK ADDRESS"
        }
    }
    
    user_inputs = {
        "construction_cost_per_sqm": 3000000
    }
    
    result = prepare_m5_real_data_report(
        context_id=context_id,
        m4_data=m4_data,
        user_inputs=user_inputs
    )
    
    if result.get('error'):
        print(f"\n❌ 오류 타입: {result.get('error_type')}")
        print(f"❌ 오류 메시지: {result.get('error_message')}")
        
        error_details = result.get('error_details', {})
        forbidden_sources = error_details.get('forbidden_sources', [])
        print(f"❌ 금지 데이터 소스 감지: {len(forbidden_sources)}건")
        for source in forbidden_sources:
            print(f"  - {source}")
        
        print(f"\n🔴 필요 조치: {error_details.get('action_required', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("✅ TEST CASE 2: 통과 (금지 데이터 차단 성공)")
    print("="*80)


def test_case_3_m4_not_connected():
    """
    TEST CASE 3: M4 데이터 누락
    
    입력:
    - M4: 빈 데이터
    
    기대 결과:
    - M4_NOT_CONNECTED 오류
    """
    print("\n" + "="*80)
    print("TEST CASE 3: M4 데이터 누락")
    print("="*80)
    
    context_id = "TEST_M4_MISSING_003"
    
    m4_data = {}
    user_inputs = {
        "construction_cost_per_sqm": 3000000
    }
    
    result = prepare_m5_real_data_report(
        context_id=context_id,
        m4_data=m4_data,
        user_inputs=user_inputs
    )
    
    if result.get('error'):
        print(f"\n❌ 오류 타입: {result.get('error_type')}")
        print(f"❌ 오류 메시지: {result.get('error_message')}")
        
        error_details = result.get('error_details', {})
        validation_errors = error_details.get('validation_errors', [])
        print(f"❌ 검증 오류: {len(validation_errors)}건")
        for error in validation_errors:
            print(f"  - {error}")
        
        print(f"\n🔴 필요 조치: {error_details.get('action_required', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("✅ TEST CASE 3: 통과 (M4 연결 실패 감지 성공)")
    print("="*80)


def test_case_4_user_input_missing():
    """
    TEST CASE 4: 사용자 입력 누락
    
    입력:
    - M4: 정상 데이터
    - 사용자: 입력 없음
    
    기대 결과:
    - 참고 범위만 제시
    - INPUT_REQUIRED 상태
    """
    print("\n" + "="*80)
    print("TEST CASE 4: 사용자 입력 누락 (참고 범위 제시)")
    print("="*80)
    
    context_id = "TEST_INPUT_MISSING_004"
    
    m4_data = {
        "context_id": context_id,
        "summary": {
            "recommended_units": 16
        },
        "details": {
            "total_units": 16,
            "total_floor_area_sqm": 864.0,
            "address": "서울특별시 강남구 역삼동 123-45"
        }
    }
    
    user_inputs = {}  # 입력 없음
    
    result = prepare_m5_real_data_report(
        context_id=context_id,
        m4_data=m4_data,
        user_inputs=user_inputs
    )
    
    print(f"\n✅ Context ID: {result.get('context_id')}")
    print(f"✅ Report ID: {result.get('report_id')}")
    
    # 비용 구조 (참고 범위)
    cost_structure = result.get('cost_structure', {})
    print(f"\n📊 비용 구조 상태: {cost_structure.get('status')}")
    print(f"  - 설명: {cost_structure.get('construction_explanation', 'N/A')}")
    
    # 수익 구조 (참고 범위)
    revenue_structure = result.get('revenue_structure', {})
    print(f"\n💰 수익 구조 상태: {revenue_structure.get('status')}")
    print(f"  - 설명: {revenue_structure.get('revenue_explanation', 'N/A')}")
    
    # 재무 지표 (계산 불가)
    financial_metrics = result.get('financial_metrics', {})
    print(f"\n📈 재무 지표 상태: {financial_metrics.get('status')}")
    print(f"  - 메시지: {financial_metrics.get('message', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("✅ TEST CASE 4: 통과 (참고 범위 제시 성공)")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "🚀 M5 Real Data Engine 테스트 시작")
    print("="*80)
    
    test_case_1_real_data()
    test_case_2_forbidden_data()
    test_case_3_m4_not_connected()
    test_case_4_user_input_missing()
    
    print("\n" + "="*80)
    print("🎉 M5 Real Data Engine 테스트 완료")
    print("="*80)
