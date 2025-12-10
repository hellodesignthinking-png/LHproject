"""
Test Construction Cost Index Service
=====================================
Verify the construction cost index functionality
"""

from app.services.construction_cost_index import (
    get_cost_index_service,
    ConstructionType
)

def main():
    print("\n" + "=" * 80)
    print("Construction Cost Index Service Test")
    print("=" * 80)
    
    service = get_cost_index_service()
    
    # Test 1: Service statistics
    print("\n📊 SERVICE STATISTICS")
    print("-" * 80)
    stats = service.get_statistics()
    print(f"Data Points: {stats['total_data_points']}")
    print(f"Date Range: {stats['date_range']}")
    print(f"Latest Date: {stats['latest_date']}")
    print(f"Latest Residential Index: {stats['latest_residential_index']:.1f}")
    print(f"Month-over-Month Change: {stats['latest_mom_change']:.1f}%")
    print(f"Year-over-Year Change: {stats['latest_yoy_change']:.1f}%")
    
    # Test 2: Latest index
    print("\n📈 LATEST INDEX (December 2024)")
    print("-" * 80)
    latest = service.get_latest_index()
    print(f"Base Index: {latest.base_index:.1f}")
    print(f"Residential Index: {latest.residential_index:.1f}")
    print(f"Commercial Index: {latest.commercial_index:.1f}")
    print(f"Steel Index: {latest.steel_index:.1f}")
    print(f"Concrete Index: {latest.concrete_index:.1f}")
    print(f"Labor Index: {latest.labor_index:.1f}")
    
    # Test 3: Cost adjustment calculation
    print("\n💰 COST ADJUSTMENT EXAMPLES")
    print("-" * 80)
    
    base_cost = 3_500_000  # 350만원/㎡
    
    test_cases = [
        ("2024-01", "2024-12", "1년간 변동"),
        ("2024-06", "2024-12", "6개월간 변동"),
        ("2024-10", "2024-12", "2개월간 변동"),
    ]
    
    print(f"\n기준 건축비: {base_cost/10000:.0f}만원/㎡")
    print(f"\n{'기간':<20} {'조정 전':<15} {'조정 후':<15} {'조정률':<10}")
    print("-" * 80)
    
    for start_date, end_date, desc in test_cases:
        adjusted_cost, rate = service.calculate_cost_adjustment(
            base_cost, start_date, end_date, ConstructionType.RESIDENTIAL
        )
        print(f"{desc:<20} {base_cost/10000:.1f}만원/㎡      {adjusted_cost/10000:.1f}만원/㎡      {(rate-1)*100:+.2f}%")
    
    # Test 4: Trend analysis
    print("\n📊 TREND ANALYSIS")
    print("-" * 80)
    
    for months in [3, 6, 12]:
        trend = service.get_trend_analysis(months)
        print(f"\n최근 {months}개월 ({trend['first_date']} ~ {trend['last_date']}):")
        print(f"  평균 월간 변동률: {trend['avg_mom_change']:.2f}%")
        print(f"  평균 연간 변동률: {trend['avg_yoy_change']:.2f}%")
        print(f"  총 변동률: {trend['total_change_pct']:+.2f}%")
        print(f"  추세: {trend['trend']}")
    
    # Test 5: Future cost prediction
    print("\n🔮 FUTURE COST PREDICTION")
    print("-" * 80)
    
    current_cost = 3_500_000  # 350만원/㎡
    
    print(f"\n현재 건축비: {current_cost/10000:.0f}만원/㎡")
    print(f"월평균 성장률: 0.5%")
    print(f"\n{'기간':<15} {'예측 건축비':<20} {'증가율':<15}")
    print("-" * 80)
    
    for months in [6, 12, 24, 36]:
        predicted = service.predict_future_cost(current_cost, months, 0.5)
        increase = ((predicted - current_cost) / current_cost) * 100
        print(f"{months}개월 후     {predicted/10000:.1f}만원/㎡         {increase:+.1f}%")
    
    # Test 6: Project cost calculation example
    print("\n🏗️  PROJECT COST CALCULATION EXAMPLE")
    print("-" * 80)
    
    building_area = 1_320  # 660㎡ × 200%
    base_unit_cost = 3_500_000
    
    print(f"\n프로젝트 사양:")
    print(f"  연면적: {building_area:,}㎡")
    print(f"  기준 단가 (2024-01): {base_unit_cost/10000:.0f}만원/㎡")
    
    adjusted_cost, rate = service.calculate_cost_adjustment(
        base_unit_cost, "2024-01", "2024-12", ConstructionType.RESIDENTIAL
    )
    
    base_total = building_area * base_unit_cost
    adjusted_total = building_area * adjusted_cost
    
    print(f"\n건축비 계산:")
    print(f"  2024-01 기준: {base_total/1e8:.2f}억원")
    print(f"  2024-12 조정: {adjusted_total/1e8:.2f}억원")
    print(f"  차액: {(adjusted_total - base_total)/1e8:+.2f}억원 ({(rate-1)*100:+.2f}%)")
    
    print(f"\n💡 공사비 연동제 적용 시:")
    print(f"  조정률: {rate:.4f} (×{rate:.2f})")
    print(f"  LH 감정평가 반영: 건축비 상승분 자동 인정")
    
    # Test 7: Material-specific indices
    print("\n🔧 MATERIAL-SPECIFIC INDICES")
    print("-" * 80)
    
    print(f"\n{'자재':<15} {'지수':<10} {'전년 대비':<15}")
    print("-" * 80)
    
    materials = [
        ("철강재", latest.steel_index),
        ("콘크리트", latest.concrete_index),
        ("인건비", latest.labor_index),
    ]
    
    for material, index in materials:
        print(f"{material:<15} {index:<10.1f} {latest.yoy_change:>13.1f}%")
    
    print("\n" + "=" * 80)
    print("✅ Construction Cost Index Test Complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
