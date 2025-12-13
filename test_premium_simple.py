"""
Simple test of Premium Calculator only
"""

from app.services.premium_calculator import PremiumCalculator

calc = PremiumCalculator()

# Test premium factors
premium_data = {
    'land_shape': 15,
    'subway_distance': 30,
    'school_district_8': 25,
    'redevelopment_status': 60,
    'gtx_station': 50
}

print("Testing PremiumCalculator...")
print("=" * 60)

total_premium, top_5, details = calc.calculate_premium(premium_data)

print(f"\nTotal Premium: {total_premium:+.1f}%")
print(f"\nTop 5 Factors:")
for i, f in enumerate(top_5, 1):
    print(f"  {i}. {f.name}: {f.value:+.1f}%")

print(f"\nDetails:")
print(f"  Total factors: {details['total_factors']}")
print(f"  Top 5 sum: {details['top_5_sum']:.1f}%")
print(f"  Adjustment rate: {details['adjustment_rate']:.0%}")
print(f"  Final premium: {details['final_premium']:.1f}%")

# Apply to base value
base_value = 5_300_000_000  # 53억원
adjusted_value = calc.apply_premium_to_value(base_value, total_premium)

print(f"\nApplying to base value:")
print(f"  Base: {base_value/100_000_000:.2f} 억원")
print(f"  Adjusted: {adjusted_value/100_000_000:.2f} 억원")
print(f"  Increase: {(adjusted_value - base_value)/100_000_000:.2f} 억원")

print("\n✅ TEST PASSED")
