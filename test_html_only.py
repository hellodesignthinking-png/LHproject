#!/usr/bin/env python3
"""Test HTML generation only (no PDF conversion)"""
import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator

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
    },
    'breakdown': {
        'cost': {'total_value': 85.0},
        'sales': {'total_value': 110.0},
        'income': {'total_value': 95.0}
    },
    'premium_info': {
        'has_premium': True,
        'base_value': 100.5,
        'premium_percentage': 92.5,
        'adjusted_value': 193.46,
        'top_5_factors': [
            {'name': '재개발 상황', 'value': 60, 'category': 'development'},
            {'name': 'GTX역 거리', 'value': 50, 'category': 'location'},
            {'name': '지하철역 거리', 'value': 30, 'category': 'location'},
            {'name': '8학군', 'value': 25, 'category': 'location'},
            {'name': '대형공원', 'value': 20, 'category': 'location'},
        ],
        'premium_details': {}
    }
}

print("HTML Generation Test")
print("=" * 70)

try:
    generator = UltimateAppraisalPDFGenerator()
    html = generator.generate_pdf_html(test_data)
    
    print(f"✅ HTML Generated: {len(html):,} chars")
    
    # Check for key elements
    checks = {
        '프리미엄 요인 분석': 'Premium section',
        '@page': 'Page directive',
        '210mm': 'A4 width',
        '297mm': 'A4 height',
        '재개발 상황': 'Redevelopment factor',
        'GTX역 거리': 'GTX factor',
        '+92.5%': 'Premium percentage',
    }
    
    print("\nContent Checks:")
    for text, desc in checks.items():
        found = text in html
        status = "✅" if found else "❌"
        print(f"  {status} {desc}: {found}")
    
    # Save HTML for inspection
    with open('/home/user/webapp/test_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n✅ HTML saved to: /home/user/webapp/test_output.html")
    
    # Show snippet of premium section
    if '프리미엄 요인 분석' in html:
        idx = html.find('프리미엄 요인 분석')
        snippet = html[idx:idx+500]
        print(f"\n📄 Premium Section Snippet:")
        print(snippet[:200] + "...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
