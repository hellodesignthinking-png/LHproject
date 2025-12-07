"""
Test LH Approval Probability Model
===================================
Verify the approval probability prediction functionality
"""

from app.services.lh_approval_model import (
    get_approval_model,
    ApprovalFactors,
    ApprovalProbability
)

def print_result(title: str, result):
    """Print approval result in formatted way"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")
    
    prob_map = {
        "very_high": "⭐⭐⭐⭐⭐ VERY HIGH (90%+)",
        "high": "⭐⭐⭐⭐ HIGH (70-90%)",
        "medium": "⭐⭐⭐ MEDIUM (50-70%)",
        "low": "⭐⭐ LOW (30-50%)",
        "very_low": "⭐ VERY LOW (<30%)"
    }
    
    print(f"\n🎯 승인 확률: {prob_map[result.probability.value]}")
    print(f"📊 종합 점수: {result.score:.1f}/100")
    print(f"🎲 신뢰도: {result.confidence:.1%}")
    
    print(f"\n세부 점수:")
    print(f"  재무 점수: {result.financial_score:.1f}/100 (가중치 40%)")
    print(f"  지역 점수: {result.regional_score:.1f}/100 (가중치 25%)")
    print(f"  사업 점수: {result.project_score:.1f}/100 (가중치 20%)")
    print(f"  정책 점수: {result.policy_score:.1f}/100 (가중치 15%)")
    
    if result.strengths:
        print(f"\n✅ 강점:")
        for s in result.strengths:
            print(f"  - {s}")
    
    if result.weaknesses:
        print(f"\n⚠️  약점:")
        for w in result.weaknesses:
            print(f"  - {w}")
    
    if result.recommendations:
        print(f"\n💡 개선 권장사항:")
        for r in result.recommendations:
            print(f"  - {r}")

def main():
    print("\n" + "=" * 80)
    print("LH Approval Probability Model Test")
    print("=" * 80)
    
    model = get_approval_model()
    
    # Test Case 1: Excellent Project (Very High Approval)
    factors_excellent = ApprovalFactors(
        roi_pct=-3.0,
        irr_pct=-1.5,
        payback_years=4.0,
        region_score=90,
        market_demand=85,
        project_scale=80,
        housing_type_score=90,
        policy_alignment=95,
        priority_area=True
    )
    
    result1 = model.predict_approval_probability(factors_excellent)
    print_result("TEST CASE 1: 우수 프로젝트 (서울 청년주택, 최적 입지)", result1)
    
    # Test Case 2: Good Project (High Approval)
    factors_good = ApprovalFactors(
        roi_pct=-8.0,
        irr_pct=-4.5,
        payback_years=7.0,
        region_score=75,
        market_demand=70,
        project_scale=100,
        housing_type_score=80,
        policy_alignment=75,
        priority_area=True
    )
    
    result2 = model.predict_approval_probability(factors_good)
    print_result("TEST CASE 2: 양호 프로젝트 (경기 신혼부부, 양호한 입지)", result2)
    
    # Test Case 3: Average Project (Medium Approval)
    factors_average = ApprovalFactors(
        roi_pct=-12.0,
        irr_pct=-6.5,
        payback_years=12.0,
        region_score=60,
        market_demand=55,
        project_scale=60,
        housing_type_score=65,
        policy_alignment=60,
        priority_area=False
    )
    
    result3 = model.predict_approval_probability(factors_average)
    print_result("TEST CASE 3: 보통 프로젝트 (인천 일반주택, 보통 입지)", result3)
    
    # Test Case 4: Poor Project (Low Approval)
    factors_poor = ApprovalFactors(
        roi_pct=-18.0,
        irr_pct=-9.0,
        payback_years=20.0,
        region_score=45,
        market_demand=40,
        project_scale=25,
        housing_type_score=50,
        policy_alignment=45,
        priority_area=False
    )
    
    result4 = model.predict_approval_probability(factors_poor)
    print_result("TEST CASE 4: 미흡 프로젝트 (지방 소규모, 낮은 수익성)", result4)
    
    # Test Case 5: Very Poor Project (Very Low Approval)
    factors_very_poor = ApprovalFactors(
        roi_pct=-25.0,
        irr_pct=-12.0,
        payback_years=999.0,
        region_score=30,
        market_demand=25,
        project_scale=15,
        housing_type_score=35,
        policy_alignment=30,
        priority_area=False
    )
    
    result5 = model.predict_approval_probability(factors_very_poor)
    print_result("TEST CASE 5: 불량 프로젝트 (구조적 문제)", result5)
    
    # Summary Statistics
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    test_results = [
        ("우수", result1),
        ("양호", result2),
        ("보통", result3),
        ("미흡", result4),
        ("불량", result5)
    ]
    
    print(f"\n{'등급':<10} {'종합점수':<12} {'승인확률':<20} {'재무':<8} {'지역':<8} {'사업':<8} {'정책':<8}")
    print("-" * 80)
    
    for grade, result in test_results:
        prob_text = {
            "very_high": "VERY HIGH",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW",
            "very_low": "VERY LOW"
        }[result.probability.value]
        
        print(f"{grade:<10} {result.score:>10.1f} {prob_text:<20} "
              f"{result.financial_score:>6.1f} {result.regional_score:>6.1f} "
              f"{result.project_score:>6.1f} {result.policy_score:>6.1f}")
    
    # Factor Sensitivity Analysis
    print("\n" + "=" * 80)
    print("🔬 SENSITIVITY ANALYSIS - ROI Impact")
    print("=" * 80)
    
    print(f"\n{'ROI (%)':<10} {'종합점수':<12} {'승인확률':<20}")
    print("-" * 80)
    
    base_factors = ApprovalFactors(
        roi_pct=0,  # Will vary
        irr_pct=-5.0,
        payback_years=7.0,
        region_score=70,
        market_demand=70,
        project_scale=80,
        housing_type_score=75,
        policy_alignment=70,
        priority_area=True
    )
    
    for roi in [-2, -5, -10, -15, -20, -25]:
        base_factors.roi_pct = roi
        result = model.predict_approval_probability(base_factors)
        prob_text = {
            "very_high": "VERY HIGH",
            "high": "HIGH",
            "medium": "MEDIUM",
            "low": "LOW",
            "very_low": "VERY LOW"
        }[result.probability.value]
        
        print(f"{roi:>8.0f}% {result.score:>10.1f} {prob_text:<20}")
    
    print("\n" + "=" * 80)
    print("✅ Approval Model Test Complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
