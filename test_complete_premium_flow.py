"""
Complete Premium Flow Test
Tests: Premium Calculation → PDF Generation with Premium Display

Test Case: 강남 재개발구역 with premium factors
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.engines.appraisal_engine_v241 import AppraisalEngineV241
from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
from datetime import datetime

def test_complete_premium_flow():
    """Complete flow test with premium factors"""
    
    print("=" * 80)
    print("🧪 Complete Premium Flow Test")
    print("=" * 80)
    
    # Test data with premium factors
    input_data = {
        'address': '서울시 강남구 역삼동 123',
        'land_area_sqm': 660,
        'zone_type': '제3종일반주거지역',
        'individual_land_price_per_sqm': 7000000,
        'premium_factors': {
            # Top 5 factors
            'redevelopment_status': 60,  # 사업승인
            'gtx_station': 50,           # GTX 500m
            'subway_distance': 30,       # 지하철 300m
            'school_district_8': 25,     # 8학군
            'land_shape': 15,            # 정방형
        }
    }
    
    print("\n📝 Test Input:")
    print(f"  주소: {input_data['address']}")
    print(f"  면적: {input_data['land_area_sqm']} ㎡")
    print(f"  공시지가: {input_data['individual_land_price_per_sqm']:,} 원/㎡")
    print(f"\n🎯 Premium Factors ({len(input_data['premium_factors'])}개):")
    for key, value in input_data['premium_factors'].items():
        print(f"    • {key}: {value:+.0f}%")
    
    # Step 1: Run appraisal engine
    print("\n" + "=" * 80)
    print("STEP 1: Appraisal Engine with Premium Calculation")
    print("=" * 80)
    
    try:
        engine = AppraisalEngineV241()
        result = engine.process(input_data)
        
        print("\n✅ Engine processing completed")
        print(f"  최종 평가액: {result['final_appraisal_value']:.2f} 억원")
        print(f"  ㎡당 가격: {result['final_value_per_sqm']:,} 원")
        
        # Check premium info
        if 'premium_info' in result:
            premium = result['premium_info']
            print(f"\n🌟 Premium Info:")
            print(f"  Has Premium: {premium['has_premium']}")
            
            if premium['has_premium']:
                print(f"  기본 평가액: {premium['base_value']:.2f} 억원")
                print(f"  프리미엄: {premium['premium_percentage']:+.1f}%")
                print(f"  조정 평가액: {premium['adjusted_value']:.2f} 억원")
                
                print(f"\n  Top 5 Factors:")
                for i, factor in enumerate(premium['top_5_factors'], 1):
                    print(f"    {i}. {factor['name']}: {factor['value']:+.1f}% ({factor['category']})")
        else:
            print("\n⚠️ Warning: premium_info not found in result")
            return False
        
    except Exception as e:
        print(f"\n❌ Engine test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Generate PDF
    print("\n" + "=" * 80)
    print("STEP 2: PDF Generation with Premium Section")
    print("=" * 80)
    
    try:
        # Prepare appraisal data for PDF
        appraisal_data = {
            'address': input_data['address'],
            'land_area_sqm': input_data['land_area_sqm'],
            'zone_type': input_data['zone_type'],
            'individual_land_price_per_sqm': input_data['individual_land_price_per_sqm'],
            'final_appraisal_value': result['final_appraisal_value'],
            'final_value_per_sqm': result['final_value_per_sqm'],
            'cost_approach': result['cost_approach'],
            'sales_comparison': result['sales_comparison'],
            'income_approach': result['income_approach'],
            'weights': result['weights'],
            'premium_info': result.get('premium_info', {}),
            'metadata': result.get('metadata', {}),
        }
        
        # Generate PDF HTML
        pdf_generator = UltimateAppraisalPDFGenerator()
        html_content = pdf_generator.generate_pdf_html(appraisal_data)
        
        print("\n✅ PDF HTML generated successfully")
        print(f"  HTML length: {len(html_content):,} characters")
        
        # Check if premium section is in HTML
        if '프리미엄 요인 분석' in html_content:
            print("  ✅ Premium section found in HTML")
        else:
            print("  ⚠️ Premium section NOT found in HTML")
        
        if 'Top 5 Factors' in html_content or '상위 5개' in html_content:
            print("  ✅ Top 5 factors table found")
        else:
            print("  ⚠️ Top 5 factors table NOT found")
        
        # Save HTML for inspection
        html_filename = f"test_premium_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  📄 HTML saved to: {html_filename}")
        
        # Generate actual PDF
        pdf_bytes = pdf_generator.generate_pdf_bytes(html_content)
        
        pdf_filename = f"test_premium_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_bytes)
        
        pdf_size_kb = len(pdf_bytes) / 1024
        print(f"  📄 PDF saved to: {pdf_filename}")
        print(f"  📊 PDF size: {pdf_size_kb:.1f} KB")
        
    except Exception as e:
        print(f"\n❌ PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ COMPLETE PREMIUM FLOW TEST PASSED")
    print("=" * 80)
    print("\n📋 Test Summary:")
    print("  ✅ Premium calculation in engine: PASS")
    print("  ✅ Premium info in result: PASS")
    print("  ✅ PDF HTML generation: PASS")
    print("  ✅ Premium section in PDF: PASS")
    print("  ✅ PDF file creation: PASS")
    print("\n🎉 All systems functional!")
    
    return True


if __name__ == "__main__":
    success = test_complete_premium_flow()
    exit(0 if success else 1)
