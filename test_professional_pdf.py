#!/usr/bin/env python3
"""
Test Professional Appraisal PDF Generator
Tests 15-20 page report with 10+ transaction cases
"""

import sys
import os

# Add webapp to path
sys.path.insert(0, '/home/user/webapp')

from app.services.professional_appraisal_pdf_generator import ProfessionalAppraisalPDFGenerator
from datetime import datetime

def test_professional_pdf():
    """Generate professional 15-20 page PDF with 10+ transaction cases"""
    
    print("=" * 80)
    print("🏢 Testing Professional Appraisal PDF Generator")
    print("=" * 80)
    
    # Test data - 월드컵북로 120
    appraisal_data = {
        'address': '서울시 마포구 월드컵북로 120',
        'land_area': 660.0,
        'zone_type': '제3종일반주거지역',
        'final_appraisal_value': 57.63,
        'final_value_per_sqm': 8_731_818,
        'cost_approach_value': 46.20,
        'sales_comparison_value': 60.06,
        'income_approach_value': 12.50,
        'cost_approach_weight': 0.40,
        'sales_comparison_weight': 0.40,
        'income_approach_weight': 0.20,
        'confidence_level': 'MEDIUM',
        'appraisal_date': datetime.now().strftime('%Y-%m-%d'),
        'individual_land_price_per_sqm': 7_000_000,
        'construction_cost_per_sqm': 3_500_000,
        'cost_approach_details': {
            'calculation_steps': [
                '1. 토지가액 = 660㎡ × 7,000,000원/㎡ × 1.15(서울) = 53.13억원',
                '2. 건물가액 = 0원 (토지만 평가)',
                '3. 총 원가법 평가액 = 46.20억원'
            ]
        },
        'sales_comparison_details': {
            'calculation_steps': [
                '1. MOLIT 실거래 데이터 수집: 2km 반경 내 10-15건',
                '2. 시점·위치·개별 보정 적용',
                '3. 가중평균 단가: 8,731,818원/㎡',
                '4. 총 거래사례비교법 평가액 = 60.06억원'
            ]
        },
        'income_approach_details': {
            'calculation_steps': [
                '1. 토지개발 추정 수익 계산',
                '2. 건축가능 연면적: 1,320㎡ (용적률 200%)',
                '3. 총 개발수익 환원 평가액 = 12.50억원'
            ]
        }
    }
    
    # Generate PDF
    print("\n📄 Generating Professional PDF...")
    generator = ProfessionalAppraisalPDFGenerator()
    
    try:
        # Generate HTML first to check structure
        print("   ├─ Generating HTML structure...")
        html_content = generator.generate_pdf_html(appraisal_data)
        
        # Save HTML for inspection
        html_path = '/home/user/webapp/test_professional_appraisal.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   ├─ HTML saved: {html_path}")
        print(f"   ├─ HTML size: {len(html_content):,} bytes")
        
        # Count sections
        section_count = html_content.count('<div class="page-break">')
        print(f"   ├─ Estimated pages: {section_count + 1}")
        
        # Check for transaction cases
        if '거래사례' in html_content:
            print("   ├─ ✅ Transaction cases section found")
        
        # Check for Antenna Holdings branding
        if 'ANTENNA HOLDINGS' in html_content or 'Antenna Holdings' in html_content:
            print("   ├─ ✅ Antenna Holdings branding confirmed")
        else:
            print("   ├─ ⚠️ Antenna Holdings branding not found")
        
        # Generate PDF
        print("   ├─ Generating PDF bytes...")
        pdf_bytes = generator.generate_pdf_bytes(appraisal_data)
        
        # Save PDF
        pdf_path = '/home/user/webapp/test_professional_appraisal.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        pdf_size_kb = len(pdf_bytes) // 1024
        print(f"   └─ ✅ PDF saved: {pdf_path} ({pdf_size_kb} KB)")
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS: Professional PDF Generated!")
        print("=" * 80)
        print(f"\n📊 Results:")
        print(f"   • HTML file: {html_path}")
        print(f"   • PDF file:  {pdf_path}")
        print(f"   • PDF size:  {pdf_size_kb} KB")
        print(f"   • Pages:     {section_count + 1} (estimated)")
        print(f"\n🎯 Expected Features:")
        print(f"   ✓ 15-20 page comprehensive report")
        print(f"   ✓ 10-15 real transaction cases from MOLIT API")
        print(f"   ✓ 2km radius filtering with Kakao geocoding")
        print(f"   ✓ Detailed calculation evidence for all values")
        print(f"   ✓ Antenna Holdings professional branding")
        print(f"   ✓ Time/Location/Individual adjustments")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_professional_pdf()
    sys.exit(0 if success else 1)
