#!/usr/bin/env python3
"""
Quick Test - Professional Appraisal PDF (with fallback data)
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.professional_appraisal_pdf_generator import ProfessionalAppraisalPDFGenerator
from datetime import datetime

# Monkey-patch the _collect_real_comparable_sales to use fallback immediately
original_collect = ProfessionalAppraisalPDFGenerator._collect_real_comparable_sales

def quick_fallback(self, address, land_area):
    print("   ├─ Using fallback transaction data (skipping MOLIT API for speed)...")
    return self._generate_fallback_comparable_sales(address, land_area)

ProfessionalAppraisalPDFGenerator._collect_real_comparable_sales = quick_fallback

def test_quick():
    print("=" * 80)
    print("🚀 Quick Professional PDF Test (Fallback Data)")
    print("=" * 80)
    
    data = {
        'address': '서울시 마포구 월드컵북로 120',
        'land_area': 660.0,
        'zone_type': '제3종일반주거지역',
        'final_appraisal_value': 57.63,
        'final_value_per_sqm': 8_731_818,
        'cost_approach': 46.20,
        'sales_comparison': 60.06,
        'income_approach': 12.50,
        'confidence_level': 'MEDIUM',
        'weights': {
            'cost': 0.40,
            'sales': 0.40,
            'income': 0.20
        },
        'breakdown': {
            'cost': {
                'land_value': 53.13,
                'building_value': 0,
                'total_value': 46.20,
                'depreciation': 0,
                'calculation_steps': [
                    '1. 토지가액 = 660㎡ × 7,000,000원/㎡ × 1.15(서울) = 53.13억원',
                    '2. 건물가액 = 0원 (토지만 평가)',
                    '3. 총 원가법 평가액 = 46.20억원'
                ]
            },
            'sales': {
                'weighted_avg_price': 8_731_818,
                'num_comparables': 10,
                'total_value': 60.06,
                'calculation_steps': [
                    '1. MOLIT 실거래 데이터 수집: 2km 반경 내 10건',
                    '2. 시점·위치·개별 보정 적용',
                    '3. 가중평균 단가: 8,731,818원/㎡',
                    '4. 총 거래사례비교법 평가액 = 60.06억원'
                ]
            },
            'income': {
                'annual_rental_income': 100_000_000,
                'vacancy_rate': 0.05,
                'operating_expenses_rate': 0.15,
                'capitalization_rate': 0.045,
                'total_value': 12.50,
                'calculation_steps': [
                    '1. 토지개발 추정 수익 계산',
                    '2. 건축가능 연면적: 1,320㎡ (용적률 200%)',
                    '3. 총 개발수익 환원 평가액 = 12.50억원'
                ]
            }
        },
        'metadata': {
            'appraisal_date': datetime.now().strftime('%Y-%m-%d'),
            'individual_land_price_per_sqm': 7_000_000,
            'construction_cost_per_sqm': 3_500_000
        }
    }
    
    print("\n📄 Generating PDF...")
    gen = ProfessionalAppraisalPDFGenerator()
    
    try:
        html = gen.generate_pdf_html(data)
        
        with open('/home/user/webapp/quick_test.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        pages = html.count('<div class="page-break">') + 1
        
        print(f"   ├─ HTML size: {len(html):,} bytes")
        print(f"   ├─ Estimated pages: {pages}")
        
        # Check features
        checks = {
            'Antenna Holdings branding': 'ANTENNA HOLDINGS' in html or 'Antenna Holdings' in html,
            'Transaction cases': '거래사례' in html,
            'Cost approach': '원가법' in html,
            'Sales comparison': '거래사례비교법' in html,
            'Income approach': '수익환원법' in html,
            'Calculation details': '계산근거' in html or '상세계산' in html
        }
        
        for feature, found in checks.items():
            status = "✅" if found else "❌"
            print(f"   ├─ {status} {feature}")
        
        print("\n   ├─ Generating PDF bytes...")
        pdf_bytes = gen.generate_pdf_bytes(data)
        
        with open('/home/user/webapp/quick_test.pdf', 'wb') as f:
            f.write(pdf_bytes)
        
        print(f"   └─ ✅ PDF saved: {len(pdf_bytes)//1024} KB\n")
        
        print("=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        print("\nFiles:")
        print("   • /home/user/webapp/quick_test.html")
        print("   • /home/user/webapp/quick_test.pdf")
        print(f"\n📊 Report: {pages} pages, {len(html):,} bytes HTML")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quick()
    sys.exit(0 if success else 1)
