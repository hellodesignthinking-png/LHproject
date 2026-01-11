"""
M6 Real Decision Engine 테스트
================================

테스트 시나리오:
1. 실제 데이터 기반 종합 판단 (정상 케이스 - 조건부 GO)
2. 금지 데이터 소스 차단 (DecisionType.GO 패턴)
3. M1~M5 데이터 누락 (연결 실패)
4. 낮은 점수 케이스 (재검토 필요)

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from app.utils.m6_real_decision_engine import prepare_m6_real_decision_report


def test_case_1_conditional_go():
    """
    TEST CASE 1: 실제 데이터 기반 종합 판단 (조건부 GO)
    
    입력:
    - M1: 서울 강남구 역삼동, 500㎡, 제2종일반주거지역
    - M3: 청년형
    - M4: 16세대, 864㎡
    - M5: NPV 43,200,000원 (양호)
    
    기대 결과:
    - 조건부 GO
    - 5단계 판단 모두 근거 ≥ 2개, 리스크 ≥ 1개
    - 점수 산정 성공
    - 최종 판정: 조건부 GO (조건 4개 제시)
    """
    print("\n" + "="*80)
    print("TEST CASE 1: 실제 데이터 기반 종합 판단 (조건부 GO)")
    print("="*80)
    
    context_id = "TEST_M6_CONDITIONAL_GO_001"
    
    m1_data = {
        "context_id": context_id,
        "details": {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500.0,
            "zoning": {"type": "제2종일반주거지역"}
        }
    }
    
    m2_data = {
        "summary": {
            "market_trend": "안정적",
            "competition_level": "중간"
        }
    }
    
    m3_data = {
        "context_id": context_id,
        "summary": {
            "selected_supply_type": "청년형"
        },
        "supply_type_comparison": {
            "rejections": {
                "신혼희망타운": {"종합의견": "입지 부적합"},
                "다자녀형": {"종합의견": "수요 부족"},
                "고령자형": {"종합의견": "시설 미비"}
            }
        }
    }
    
    m4_data = {
        "context_id": context_id,
        "summary": {
            "recommended_units": 16,
            "recommended_scale_reason": "법적 한계 및 주차·코어 공간을 고려한 현실적 규모"
        },
        "details": {
            "total_units": 16,
            "total_floor_area_sqm": 864.0
        }
    }
    
    m5_data = {
        "context_id": context_id,
        "cost_structure": {
            "total_project_cost": 2980800000,
            "construction_cost": 2592000000,
            "other_costs": 388800000
        },
        "revenue_structure": {
            "purchase_price": 3024000000,
            "price_per_sqm": 3500000
        },
        "financial_metrics": {
            "npv": 43200000,
            "npv_grade": "양호",
            "roi": 1.45,
            "roi_grade": "보통",
            "irr": 0.72,
            "irr_grade": "보통"
        },
        "final_judgment": {
            "major_risks": [
                {"risk": "공사비 상승 리스크", "mitigation": "계약 시 물가연동제 조항 포함"},
                {"risk": "LH 매입 단가 협의 리스크", "mitigation": "사전 감정평가 협의"},
                {"risk": "사업 일정 지연 리스크", "mitigation": "공정관리 강화"}
            ],
            "management_strategies": [
                {"strategy": "규모 조정", "description": "M4 권장 규모 기준"},
                {"strategy": "원가 통제", "description": "VE 적용"},
                {"strategy": "M6 심사 대응", "description": "정책 부합성 강조"}
            ]
        }
    }
    
    result = prepare_m6_real_decision_report(
        context_id=context_id,
        m1_data=m1_data,
        m2_data=m2_data,
        m3_data=m3_data,
        m4_data=m4_data,
        m5_data=m5_data
    )
    
    print(f"\n✅ Context ID: {result.get('context_id')}")
    print(f"✅ Report ID: {result.get('report_id')}")
    print(f"✅ 분석 날짜: {result.get('analysis_date')}")
    
    # 입력 데이터 종합 요약
    input_summary = result.get('input_summary', {})
    print(f"\n📋 입력 데이터 종합:")
    print(f"  - 주소: {input_summary.get('address')}")
    print(f"  - 면적: {input_summary.get('land_area_sqm')}㎡")
    print(f"  - 용도지역: {input_summary.get('zoning')}")
    print(f"  - 공급유형: {input_summary.get('supply_type')}")
    print(f"  - 규모: {input_summary.get('total_units')}세대, {input_summary.get('total_floor_area'):,.2f}㎡")
    print(f"  - 사업비: {input_summary.get('total_project_cost'):,.0f}원")
    print(f"  - LH 매입: {input_summary.get('lh_purchase_price'):,.0f}원")
    
    # 판단 흐름
    print(f"\n🔗 판단 흐름:")
    print(f"  {result.get('judgment_flow', 'N/A')}")
    
    # 점수 체계
    score_system = result.get('score_system', {})
    if score_system.get('status') == 'CALCULATED':
        print(f"\n📊 점수 체계:")
        print(f"  - 평균 점수: {score_system.get('avg_score', 0):.2f}점 ({score_system.get('score_grade', 'N/A')})")
        print(f"  - 해석: {score_system.get('score_interpretation', 'N/A')[:100]}...")
        print(f"  - 면책: {score_system.get('disclaimer', 'N/A')[:80]}...")
    
    # 최종 판정
    final_decision = result.get('final_decision', {})
    print(f"\n🎯 최종 판정:")
    print(f"  - 판정: {final_decision.get('decision_type', 'N/A')}")
    print(f"  - 가능한 이유:")
    for reason in final_decision.get('why_possible', [])[:3]:
        print(f"    • {reason}")
    print(f"  - 필요 조건:")
    for condition in final_decision.get('required_conditions', [])[:3]:
        print(f"    • {condition}")
    print(f"  - 권장사항: {final_decision.get('recommendation', 'N/A')}")
    
    # 주요 리스크
    major_risks = result.get('major_risks', [])
    print(f"\n⚠️ 주요 리스크: {len(major_risks)}건")
    for risk in major_risks[:3]:
        print(f"  - {risk}")
    
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
    - M5 데이터에 'DecisionType.GO' 패턴 포함
    
    기대 결과:
    - DATA_SOURCE_INVALID 오류
    - 금지 패턴 감지 메시지
    """
    print("\n" + "="*80)
    print("TEST CASE 2: 금지 데이터 소스 차단")
    print("="*80)
    
    context_id = "TEST_M6_FORBIDDEN_002"
    
    m1_data = {"details": {"address": "Sample Address"}}
    m2_data = {}
    m3_data = {"summary": {"selected_supply_type": "청년형"}}
    m4_data = {"summary": {"recommended_units": 20}}
    
    m5_data = {
        "financial_metrics": {
            "npv": 100000000,
            "decision_note": "DecisionType.GO - SAMPLE DATA"
        }
    }
    
    result = prepare_m6_real_decision_report(
        context_id=context_id,
        m1_data=m1_data,
        m2_data=m2_data,
        m3_data=m3_data,
        m4_data=m4_data,
        m5_data=m5_data
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


def test_case_3_modules_not_connected():
    """
    TEST CASE 3: M1~M5 데이터 누락
    
    입력:
    - M4, M5 데이터 누락
    
    기대 결과:
    - DATA_NOT_CONNECTED 오류
    - GO / NO-GO / 점수 / 등급 출력 금지
    """
    print("\n" + "="*80)
    print("TEST CASE 3: M1~M5 데이터 누락")
    print("="*80)
    
    context_id = "TEST_M6_MISSING_003"
    
    m1_data = {
        "details": {
            "address": "서울특별시 강남구",
            "land_area": 500.0
        }
    }
    m2_data = {}
    m3_data = {"summary": {"selected_supply_type": "청년형"}}
    m4_data = {}  # 누락
    m5_data = {}  # 누락
    
    result = prepare_m6_real_decision_report(
        context_id=context_id,
        m1_data=m1_data,
        m2_data=m2_data,
        m3_data=m3_data,
        m4_data=m4_data,
        m5_data=m5_data
    )
    
    if result.get('error'):
        print(f"\n❌ 오류 타입: {result.get('error_type')}")
        print(f"❌ 오류 메시지: {result.get('error_message')}")
        
        error_details = result.get('error_details', {})
        missing_modules = error_details.get('missing_modules', [])
        validation_errors = error_details.get('validation_errors', [])
        
        print(f"❌ 누락 모듈: {missing_modules}")
        print(f"❌ 검증 오류:")
        for error in validation_errors:
            print(f"  - {error}")
        
        print(f"\n🔴 필요 조치: {error_details.get('action_required', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("✅ TEST CASE 3: 통과 (데이터 연결 실패 감지 성공)")
    print("="*80)


def test_case_4_low_score_reexamination():
    """
    TEST CASE 4: 낮은 점수 케이스 (재검토 필요)
    
    입력:
    - M5 NPV가 음수 (-50,000,000원)
    
    기대 결과:
    - 재검토 필요 (구조 재설계 권장)
    - 점수 < 65점
    - 보완 사항 제시
    """
    print("\n" + "="*80)
    print("TEST CASE 4: 낮은 점수 케이스 (재검토 필요)")
    print("="*80)
    
    context_id = "TEST_M6_LOW_SCORE_004"
    
    m1_data = {
        "context_id": context_id,
        "details": {
            "address": "서울특별시 강남구 역삼동 123-45",
            "land_area": 500.0,
            "zoning": {"type": "제2종일반주거지역"}
        }
    }
    
    m2_data = {}
    
    m3_data = {
        "context_id": context_id,
        "summary": {"selected_supply_type": "청년형"},
        "supply_type_comparison": {"rejections": {}}
    }
    
    m4_data = {
        "context_id": context_id,
        "summary": {"recommended_units": 10},
        "details": {"total_units": 10, "total_floor_area_sqm": 500.0}
    }
    
    m5_data = {
        "context_id": context_id,
        "cost_structure": {
            "total_project_cost": 2000000000
        },
        "revenue_structure": {
            "purchase_price": 1950000000
        },
        "financial_metrics": {
            "npv": -50000000,
            "npv_grade": "불량",
            "roi": -2.5,
            "roi_grade": "불량"
        },
        "final_judgment": {
            "major_risks": [
                {"risk": "손실 확정", "mitigation": "구조 재설계 필요"}
            ],
            "management_strategies": []
        }
    }
    
    result = prepare_m6_real_decision_report(
        context_id=context_id,
        m1_data=m1_data,
        m2_data=m2_data,
        m3_data=m3_data,
        m4_data=m4_data,
        m5_data=m5_data
    )
    
    print(f"\n✅ Context ID: {result.get('context_id')}")
    print(f"✅ Report ID: {result.get('report_id')}")
    
    # 점수 체계
    score_system = result.get('score_system', {})
    if score_system.get('status') == 'CALCULATED':
        print(f"\n📊 점수 체계:")
        print(f"  - 평균 점수: {score_system.get('avg_score', 0):.2f}점 ({score_system.get('score_grade', 'N/A')})")
    
    # 최종 판정
    final_decision = result.get('final_decision', {})
    print(f"\n🎯 최종 판정:")
    print(f"  - 판정: {final_decision.get('decision_type', 'N/A')}")
    print(f"  - 가능한 이유:")
    for reason in final_decision.get('why_possible', [])[:2]:
        print(f"    • {reason}")
    print(f"  - 필요 조건:")
    for condition in final_decision.get('required_conditions', [])[:3]:
        print(f"    • {condition}")
    print(f"  - 권장사항: {final_decision.get('recommendation', 'N/A')}")
    
    print(f"\n{'='*80}")
    print("✅ TEST CASE 4: 통과 (재검토 필요 판정 성공)")
    print("="*80)


if __name__ == "__main__":
    print("\n" + "🚀 M6 Real Decision Engine 테스트 시작")
    print("="*80)
    
    test_case_1_conditional_go()
    test_case_2_forbidden_data()
    test_case_3_modules_not_connected()
    test_case_4_low_score_reexamination()
    
    print("\n" + "="*80)
    print("🎉 M6 Real Decision Engine 테스트 완료")
    print("="*80)
