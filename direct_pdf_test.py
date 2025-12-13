"""
수정된 코드를 직접 테스트
"""
import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
import logging

logging.basicConfig(level=logging.INFO)

# Test data
appraisal_data = {
    'address': '서울시 강남구 역삼동 123',
    'land_area_sqm': 660.0,
    'zone_type': '제2종일반주거지역',
    'individual_land_price_per_sqm': 12000000
}

final_result = {
    'final_value': 6487600000,  # 64.88억원
    'cost_value': 4620000000,
    'sales_value': 5266600000,
    'income_value': 6750000000,
    'weights': {'cost': 0.4, 'sales': 0.4, 'income': 0.2},
    'zone_premium': 1.0,
    'market_reflection_rate': 0.84
}

print("="*80)
print("🧪 수정된 코드 직접 테스트")
print("="*80)

try:
    generator = UltimateAppraisalPDFGenerator()
    print(f"\n✅ Generator 초기화 완료")
    
    # Test _extract_gu_name
    print(f"\n📍 구 이름 추출 테스트:")
    test_addresses = [
        "서울시 강남구 역삼동 123",
        "월드컵북로 120",
        "테스트 주소"
    ]
    
    for addr in test_addresses:
        gu_name = generator._extract_gu_name(addr)
        print(f"   '{addr}' → '{gu_name}'")
        
        if gu_name == 'default':
            print(f"      ❌ 여전히 'default' 반환!")
        elif gu_name in ['강남구', '서초구', '마포구']:
            print(f"      ✅ 정상 구 이름")
    
    # Test fallback sales generation
    print(f"\n📊 Fallback 거래사례 생성 테스트:")
    fallback_sales = generator._generate_enhanced_fallback_sales(
        address=appraisal_data['address'],
        land_area_sqm=appraisal_data['land_area_sqm'],
        zone_type=appraisal_data['zone_type']
    )
    
    print(f"   생성된 거래사례 수: {len(fallback_sales)}")
    
    # Check first 3 sales
    for i, sale in enumerate(fallback_sales[:3], 1):
        location = sale.get('location', 'N/A')
        print(f"   {i}. {location}")
        
        if 'default' in location.lower():
            print(f"      ❌ 'default' 발견!")
        else:
            print(f"      ✅ 정상 주소")
    
    # Test executive summary with price_per_pyeong
    print(f"\n💰 Executive Summary 생성 테스트:")
    summary_html = generator._generate_executive_summary_v2(
        appraisal_data=appraisal_data,
        final_result=final_result,
        comparable_sales=fallback_sales
    )
    
    # Check for key elements
    if '평당' in summary_html:
        print(f"   ✅ '평당' 텍스트 발견")
    else:
        print(f"   ❌ '평당' 텍스트 미발견")
    
    # Calculate expected price per pyeong
    land_area_pyeong = appraisal_data['land_area_sqm'] / 3.3058
    expected_price_per_pyeong = final_result['final_value'] / land_area_pyeong
    
    print(f"   예상 평당 가격: {expected_price_per_pyeong:,.0f}원")
    
    price_str = f"{expected_price_per_pyeong:,.0f}"
    if price_str in summary_html:
        print(f"   ✅ 평당 가격 숫자 발견: {price_str}원")
    else:
        print(f"   ⚠️ 평당 가격 숫자 미발견")
    
    print(f"\n✅ 모든 테스트 완료")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
