#!/usr/bin/env python3
"""Direct PDF generation test"""
import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
from app.services.premium_calculator import PremiumCalculator

# Minimal test data
test_data = {
    'address': '서울시 강남구 역삼동 123',
    'land_area_sqm': 660,
    'zone_type': '제2종일반주거지역',
    'individual_land_price_per_sqm': 12000000,
    'final_appraisal_value': 100.5,
    'final_value_per_sqm': 15227272,
    'cost_approach': 85.0,
    'sales_comparison': 110.0,
    'income_approach': 95.0,
    'confidence_level': 'MEDIUM',
    'location_factor': 1.2,
    'weights': {'cost': 0.3, 'sales': 0.5, 'income': 0.2},
    'metadata': {
        'appraisal_date': '2025-12-13',
        'individual_land_price_per_sqm': 12000000,
        'construction_cost_per_sqm': 2000000,
        'market_conditions': '정상'
    },
    'notes': '테스트 감정평가',
}

# Add premium info
calculator = PremiumCalculator()
premium_factors = {
    'redevelopment_status': 60,
    'gtx_station': 50,
    'subway_distance': 30,
    'school_district_8': 25,
    'large_park': 20
}

total_premium, top_5, details = calculator.calculate_premium(premium_factors)
base_value = 100.5
adjusted_value = calculator.apply_premium_to_value(base_value * 100_000_000, total_premium) / 100_000_000

test_data['premium_info'] = {
    'has_premium': True,
    'base_value': base_value,
    'premium_percentage': total_premium,
    'adjusted_value': adjusted_value,
    'premium_details': details,
    'top_5_factors': top_5
}

print("=" * 70)
print("PDF Generation Test")
print("=" * 70)
print(f"Base Value: {base_value:.2f}억원")
print(f"Premium: {total_premium:+.1f}%")
print(f"Final Value: {adjusted_value:.2f}억원")
print(f"\nTop 5 Premium Factors:")
for i, f in enumerate(top_5, 1):
    print(f"  {i}. {f['name']}: {f['value']:+.1f}%")

try:
    generator = UltimateAppraisalPDFGenerator()
    html = generator.generate_pdf_html(test_data)
    
    # Check for premium section
    if '프리미엄 요인 분석' in html:
        print("\n✅ Premium section found in HTML")
    else:
        print("\n❌ Premium section NOT found in HTML")
    
    # Generate PDF
    pdf_bytes = generator.generate_pdf_bytes(html)
    
    # Save to file
    output_path = '/home/user/webapp/test_output.pdf'
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"\n✅ PDF generated: {len(pdf_bytes):,} bytes")
    print(f"✅ Saved to: {output_path}")
    
    # Check A4 layout in HTML
    if '@page' in html and '210mm' in html and '297mm' in html:
        print("✅ A4 layout (210mm × 297mm) detected")
    else:
        print("⚠️ A4 layout might not be properly set")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
