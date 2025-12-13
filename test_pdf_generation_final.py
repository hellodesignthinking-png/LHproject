#!/usr/bin/env python3
"""Final PDF Generation & A4 Layout Test"""
import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
from app.services.premium_calculator import PremiumCalculator
from dataclasses import asdict

# Test data
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
    'breakdown': {
        'cost': {'total_value': 85.0},
        'sales': {'total_value': 110.0},
        'income': {'total_value': 95.0}
    }
}

print("=" * 80)
print("🔍 PDF Generation & A4 Layout Verification Test")
print("=" * 80)

# Calculate premium
calculator = PremiumCalculator()
premium_factors = {
    'redevelopment_status': 60,
    'gtx_station': 50,
    'subway_distance': 30,
    'school_district_8': 25,
    'large_park': 20
}

print(f"\n📊 Input Data:")
print(f"   Address: {test_data['address']}")
print(f"   Land Area: {test_data['land_area_sqm']} ㎡ ({test_data['land_area_sqm']/3.3:.0f} 평)")
print(f"   Zone: {test_data['zone_type']}")
print(f"   Base Value: {test_data['final_appraisal_value']:.2f} 억원")

total_premium, top_5, details = calculator.calculate_premium(premium_factors)
base_value = test_data['final_appraisal_value']
adjusted_value = calculator.apply_premium_to_value(base_value * 100_000_000, total_premium) / 100_000_000

print(f"\n🌟 Premium Calculation:")
print(f"   Total Premium: {total_premium:+.1f}%")
print(f"   Adjusted Value: {adjusted_value:.2f} 억원")
print(f"   Increase: {adjusted_value - base_value:.2f} 억원 ({(adjusted_value/base_value - 1)*100:.1f}%)")

print(f"\n🏆 Top 5 Premium Factors:")
for i, factor in enumerate(top_5, 1):
    # Convert PremiumFactor to dict if needed
    if hasattr(factor, '__dict__'):
        f_dict = asdict(factor) if hasattr(factor, '__dataclass_fields__') else factor.__dict__
    else:
        f_dict = factor
    print(f"   {i}. {f_dict['name']}: {f_dict['value']:+.1f}%")

# Add premium info to test data
test_data['premium_info'] = {
    'has_premium': True,
    'base_value': base_value,
    'premium_percentage': total_premium,
    'adjusted_value': adjusted_value,
    'premium_details': details,
    'top_5_factors': [
        {
            'name': f['name'] if isinstance(f, dict) else (asdict(f)['name'] if hasattr(f, '__dataclass_fields__') else f.name),
            'value': f['value'] if isinstance(f, dict) else (asdict(f)['value'] if hasattr(f, '__dataclass_fields__') else f.value),
            'category': f['category'] if isinstance(f, dict) else (asdict(f)['category'] if hasattr(f, '__dataclass_fields__') else f.category)
        }
        for f in top_5
    ]
}

print("\n" + "=" * 80)
print("📄 Generating PDF...")
print("=" * 80)

try:
    generator = UltimateAppraisalPDFGenerator()
    html = generator.generate_pdf_html(test_data)
    
    print(f"\n✅ HTML Generated: {len(html):,} characters")
    
    # Verify premium section
    if '프리미엄 요인 분석' in html:
        print("✅ Premium section present in HTML")
    else:
        print("❌ Premium section MISSING in HTML")
        print("⚠️  Checking premium_info...")
        print(f"   has_premium: {test_data['premium_info']['has_premium']}")
    
    # Verify A4 layout
    checks = {
        '@page': '@page directive' in html,
        '210mm': '210mm width' in html,
        '297mm': '297mm height' in html,
        'size: A4': 'size: A4' in html or 'size:A4' in html,
    }
    
    print(f"\n📐 A4 Layout Verification:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}: {result}")
    
    # Check for key sections
    sections = [
        ('평가 개요', 'Executive Summary'),
        ('프리미엄 요인 분석', 'Premium Factors'),
        ('원가법', 'Cost Approach'),
        ('거래사례비교법', 'Sales Comparison'),
        ('수익환원법', 'Income Approach'),
    ]
    
    print(f"\n📋 Content Verification:")
    for korean, english in sections:
        present = korean in html
        status = "✅" if present else "❌"
        print(f"   {status} {english} ({korean})")
    
    # Generate PDF bytes
    print(f"\n🔄 Converting HTML to PDF...")
    pdf_bytes = generator.generate_pdf_bytes(html)
    
    # Save to file
    output_path = '/home/user/webapp/test_final_output.pdf'
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"\n✅ PDF Generated Successfully!")
    print(f"   Size: {len(pdf_bytes):,} bytes ({len(pdf_bytes)/1024:.1f} KB)")
    print(f"   Path: {output_path}")
    
    # Estimate page count (rough)
    estimated_pages = len(html) // 3000  # Rough estimate
    print(f"   Estimated Pages: ~{estimated_pages}")
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE - PDF READY FOR REVIEW")
    print("=" * 80)
    print(f"\n📥 Download the PDF to verify:")
    print(f"   File: {output_path}")
    print(f"\n🔍 What to check:")
    print(f"   1. A4 layout (210mm × 297mm)")
    print(f"   2. Premium section (Pages 4-5)")
    print(f"   3. All 5 premium factors listed")
    print(f"   4. Calculation formula displayed")
    print(f"   5. Professional formatting")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
