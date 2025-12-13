#!/usr/bin/env python3
"""
Test v26.0 PDF Generator
테스트: 3-법 요약표 + 프리미엄 텍스트 설명
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.complete_appraisal_pdf_generator import CompleteAppraisalPDFGenerator
from datetime import datetime

# 테스트 데이터
test_data = {
    'address': '서울시 강남구 역삼동 123-4',
    'land_area_sqm': 660,
    'zone_type': '제3종일반주거지역',
    'individual_land_price': 8500000,
    'final_appraisal_value': 90.90,
    
    # 3-법 데이터
    'cost_approach_value': 85.5,
    'sales_comparison_value': 92.3,
    'income_approach_value': 88.7,
    'cost_weight': 0.2,
    'sales_weight': 0.5,
    'income_weight': 0.3,
    
    # 프리미엄 정보
    'premium_info': {
        'premium_percentage': 72.5,
        'base_value': 52.5,
        'adjusted_value': 90.90,
        'top_5_factors': [
            {'name': '재개발 상황', 'category': '개발', 'value': 60.0},
            {'name': '지하철역 거리', 'category': '입지', 'value': 30.0},
            {'name': '8학군 여부', 'category': '입지', 'value': 25.0},
            {'name': '정방형 필지', 'category': '물리적', 'value': 20.0},
            {'name': 'GTX 노선', 'category': '개발', 'value': 10.0}
        ]
    }
}

print("=" * 80)
print("🧪 Testing v26.0 PDF Generator")
print("=" * 80)

try:
    generator = CompleteAppraisalPDFGenerator()
    html = generator.generate_pdf_html(test_data)
    
    print(f"\n✅ HTML Generated: {len(html)} characters")
    
    # 핵심 검증
    checks = {
        '3-법 요약표': '3대 평가 방식 요약' in html,
        '원가법': '원가법' in html or 'Cost Approach' in html,
        '거래사례비교법': '거래사례비교법' in html,
        '수익환원법': '수익환원법' in html,
        '프리미엄 텍스트 설명': '프리미엄 72.5% 산정 근거' in html,
        '물리적 특성': '물리적 특성' in html,
        '입지적 특성': '입지적 특성' in html,
        '개발 가능성': '개발 가능성' in html,
        '역삼동': '역삼동' in html,
        '재개발': '재개발' in html,
        '72.5%': '72.5%' in html
    }
    
    print("\n📋 Content Verification:")
    for name, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}: {result}")
    
    # PDF 저장 (테스트용)
    output_file = f'/home/user/uploaded_files/test_v26_pdf_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n💾 HTML saved to: {output_file}")
    
    # 통과 여부
    all_passed = all(checks.values())
    if all_passed:
        print("\n🎉 All tests PASSED! v26.0 is ready!")
    else:
        print("\n⚠️ Some tests FAILED. Please check the implementation.")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
