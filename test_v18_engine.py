"""
ZeroSite v18 Engine Test Script
================================
PolicyTransactionFinancialEngineV18 단독 테스트
"""

from app.services.policy_transaction_financial_engine_v18 import (
    PolicyTransactionFinancialEngineV18,
    TransactionInputs
)

# ==========================================
# 테스트 케이스: 월드컵북로 120
# ==========================================

print("=" * 80)
print("🚀 ZeroSite v18 - Policy Transaction Financial Engine Test")
print("=" * 80)
print()

# 입력 데이터
inputs = TransactionInputs(
    # 기본 정보
    land_area_m2=660.0,                       # 대지면적 660㎡
    building_area_m2=1650.0,                  # 연면적 1650㎡ (용적률 250%)
    
    # 가격 정보 (거래사례 기반)
    land_price_per_m2=10_000_000,             # 토지 1천만원/㎡ (서울 평균)
    construction_cost_per_m2=3_500_000,       # 건설비 350만원/㎡
    
    # LH 감정평가 파라미터
    land_appraisal_rate=0.95,                 # 토지 95% 인정
    building_ack_rate=0.90,                   # 건물 90% 인정
    appraisal_safety_factor=0.98,             # 안전계수 98%
    
    # 공사비 연동제
    construction_index_rate=1.05,             # 105% (5% 상승)
)

print("📋 입력 데이터:")
print(f"   대지면적: {inputs.land_area_m2:.1f}㎡")
print(f"   연면적: {inputs.building_area_m2:.1f}㎡")
print(f"   토지단가: {inputs.land_price_per_m2/1e4:.0f}만원/㎡")
print(f"   건설단가: {inputs.construction_cost_per_m2/1e4:.0f}만원/㎡")
print()

# 엔진 생성 및 실행
engine = PolicyTransactionFinancialEngineV18(inputs)
result = engine.evaluate()

# 결과 출력
print()
print("=" * 80)
print("📊 ZeroSite v18 분석 결과")
print("=" * 80)
print()

print("■ 총사업비 (CAPEX)")
print(f"   토지비: {result.capex.land_cost/1e8:.2f}억원")
print(f"   취득세: {result.capex.land_acquisition_tax/1e8:.2f}억원")
print(f"   건설비(연동제): {result.capex.indexed_construction_cost/1e8:.2f}억원")
print(f"   설계비: {result.capex.design_cost/1e8:.2f}억원")
print(f"   감리비: {result.capex.supervision_cost/1e8:.2f}억원")
print(f"   인허가비: {result.capex.permit_cost/1e8:.2f}억원")
print(f"   예비비: {result.capex.contingency_cost/1e8:.2f}억원")
print(f"   금융비용: {result.capex.financing_cost/1e8:.2f}억원")
print(f"   기타비용: {result.capex.misc_cost/1e8:.2f}억원")
print(f"   ─────────────────────")
print(f"   총사업비: {result.capex.total_capex/1e8:.2f}억원")
print()

print("■ LH 감정평가")
print(f"   토지 감정가액: {result.appraisal.land_appraised_value/1e8:.2f}억원")
print(f"   건물 감정가액: {result.appraisal.building_appraised_value/1e8:.2f}억원")
print(f"   연동제 조정: {result.appraisal.indexing_adjustment/1e8:.2f}억원")
print(f"   안전계수 조정: {result.appraisal.safety_factor_adjustment/1e8:.2f}억원")
print(f"   ─────────────────────")
print(f"   최종 매입가: {result.appraisal.final_appraisal_value/1e8:.2f}억원")
print()

print("■ 사업 수익성")
print(f"   LH 매입가: {result.revenue/1e8:.2f}억원")
print(f"   총사업비: {result.cost/1e8:.2f}억원")
print(f"   {'━' * 30}")
print(f"   {'📗' if result.profit >= 0 else '📕'} 사업이익: {result.profit/1e8:+.2f}억원")
print(f"   {'✅' if result.roi_pct >= 0 else '❌'} ROI: {result.roi_pct:+.2f}%")
print(f"   📊 IRR (2.5년): {result.irr_pct:+.2f}%")
print(f"   ⏱️  회수기간: {result.payback_years:.1f}년")
print()

print("■ 의사결정")
print(f"   🎯 판단: {result.decision}")
print(f"   📝 근거: {result.decision_reason}")
if result.conditional_requirements:
    print(f"   📌 조건:")
    for req in result.conditional_requirements:
        print(f"      - {req}")
print()

# 민감도 분석
print("=" * 80)
print("📊 민감도 분석")
print("=" * 80)
print()

sensitivity = engine.sensitivity_analysis()

print("■ 토지비 민감도")
for key in ['land_-10%', 'land_+0%', 'land_+10%']:
    if key in sensitivity['scenarios']:
        s = sensitivity['scenarios'][key]
        print(f"   {s['label']}: 이익 {s['profit']:+.2f}억, ROI {s['roi']:+.2f}%, {s['decision']}")
print()

print("■ 공사비 민감도")
for key in ['construction_-15%', 'construction_+0%', 'construction_+15%']:
    if key in sensitivity['scenarios']:
        s = sensitivity['scenarios'][key]
        print(f"   {s['label']}: 이익 {s['profit']:+.2f}억, ROI {s['roi']:+.2f}%, {s['decision']}")
print()

print("■ 감정평가율 민감도")
for key in ['appraisal_85%', 'appraisal_90%', 'appraisal_95%']:
    if key in sensitivity['scenarios']:
        s = sensitivity['scenarios'][key]
        print(f"   {s['label']}: 이익 {s['profit']:+.2f}억, ROI {s['roi']:+.2f}%, {s['decision']}")
print()

print("=" * 80)
print("✅ ZeroSite v18 Engine Test 완료")
print("=" * 80)
