"""
Simple Premium PDF Test (No API calls)
"""

from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
from datetime import datetime

def test_premium_pdf_simple():
    """Simple test with mock data"""
    
    print("=" * 80)
    print("🧪 Simple Premium PDF Test")
    print("=" * 80)
    
    # Mock appraisal data with premium info
    appraisal_data = {
        'address': '서울시 강남구 역삼동 123',
        'land_area_sqm': 660,
        'zone_type': '제3종일반주거지역',
        'individual_land_price_per_sqm': 7000000,
        'final_appraisal_value': 100.7,  # 억원
        'final_value_per_sqm': 15257575,
        'cost_approach': 46.2,
        'sales_comparison': 120.5,
        'income_approach': 135.4,
        'weights': {
            'cost': 0.4,
            'sales': 0.4,
            'income': 0.2
        },
        'premium_info': {
            'has_premium': True,
            'base_value': 53.0,
            'premium_percentage': 90.0,
            'adjusted_value': 100.7,
            'top_5_factors': [
                {'name': '재개발 상황', 'value': 60.0, 'category': 'development'},
                {'name': 'GTX역 거리', 'value': 50.0, 'category': 'development'},
                {'name': '지하철역 거리', 'value': 30.0, 'category': 'location'},
                {'name': '8학군', 'value': 25.0, 'category': 'location'},
                {'name': '토지형상', 'value': 15.0, 'category': 'physical'},
            ]
        },
        'metadata': {
            'appraisal_date': datetime.now().strftime('%Y-%m-%d')
        }
    }
    
    print("\n📝 Mock Data:")
    print(f"  주소: {appraisal_data['address']}")
    print(f"  최종 평가액: {appraisal_data['final_appraisal_value']:.2f} 억원")
    print(f"  프리미엄: {appraisal_data['premium_info']['premium_percentage']:+.1f}%")
    
    try:
        # Generate PDF
        pdf_generator = UltimateAppraisalPDFGenerator()
        
        print("\n🔄 Generating PDF HTML...")
        html_content = pdf_generator.generate_pdf_html(appraisal_data)
        
        print(f"✅ HTML generated: {len(html_content):,} characters")
        
        # Check premium section
        checks = {
            '프리미엄 요인 분석': '프리미엄 요인 분석' in html_content,
            '상위 5개 프리미엄 요인': '상위 5개' in html_content,
            '기본 평가액': '기본 평가액' in html_content,
            '프리미엄 조정': ('프리미엄 조정' in html_content or 'Premium' in html_content),
            '최종 평가액': '최종 평가액' in html_content,
        }
        
        print("\n📊 Content Checks:")
        for label, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {label}: {'FOUND' if result else 'NOT FOUND'}")
        
        # Save HTML
        html_filename = f"test_premium_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n📄 HTML saved to: {html_filename}")
        
        # Generate PDF
        print("\n🔄 Generating PDF bytes...")
        pdf_bytes = pdf_generator.generate_pdf_bytes(html_content)
        
        pdf_filename = f"test_premium_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_bytes)
        
        pdf_size_kb = len(pdf_bytes) / 1024
        print(f"✅ PDF generated: {pdf_size_kb:.1f} KB")
        print(f"📄 PDF saved to: {pdf_filename}")
        
        # Summary
        all_passed = all(checks.values())
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ TEST PASSED - Premium sections present in PDF")
        else:
            print("⚠️ TEST PARTIAL - Some premium sections missing")
        print("=" * 80)
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_premium_pdf_simple()
    exit(0 if success else 1)
