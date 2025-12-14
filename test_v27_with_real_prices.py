#!/usr/bin/env python3
"""
Test v27.0 PDF Generator with Real Market Prices
실제 구별 시세가 반영된 PDF 생성 테스트
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.complete_appraisal_pdf_generator import CompleteAppraisalPDFGenerator
from weasyprint import HTML
from datetime import datetime
from pypdf import PdfReader

print("=" * 100)
print("🧪 v27.0 PDF Generator - Real Market Prices Test")
print("=" * 100)

# 테스트 케이스: 강남구 vs 마포구
test_cases = [
    {
        'name': '강남구 (18M/㎡ 기준)',
        'data': {
            'address': '서울 강남구 역삼동 123-4',
            'land_area_sqm': 660,
            'zone_type': '제3종일반주거지역',
            'individual_land_price': 18000000,
            'final_appraisal_value': 130.0,
            'cost_approach_value': 120.0,
            'sales_comparison_value': 135.0,
            'income_approach_value': 125.0,
            'cost_weight': 0.2,
            'sales_weight': 0.5,
            'income_weight': 0.3,
            'premium_info': {
                'premium_percentage': 45.0,
                'base_value': 90.0,
                'adjusted_value': 130.0,
                'top_5_factors': [
                    {'name': '재개발 상황', 'category': '개발', 'value': 30.0},
                    {'name': '지하철역 거리', 'category': '입지', 'value': 25.0},
                    {'name': '8학군 여부', 'category': '입지', 'value': 20.0},
                    {'name': '정방형 필지', 'category': '물리적', 'value': 15.0},
                    {'name': '대로변 위치', 'category': '입지', 'value': 10.0}
                ]
            }
        }
    },
    {
        'name': '마포구 (12M/㎡ 기준)',
        'data': {
            'address': '서울 마포구 공덕동 100',
            'land_area_sqm': 500,
            'zone_type': '일반상업지역',
            'individual_land_price': 12000000,
            'final_appraisal_value': 70.0,
            'cost_approach_value': 65.0,
            'sales_comparison_value': 72.0,
            'income_approach_value': 68.0,
            'cost_weight': 0.2,
            'sales_weight': 0.5,
            'income_weight': 0.3,
            'premium_info': {
                'premium_percentage': 25.0,
                'base_value': 56.0,
                'adjusted_value': 70.0,
                'top_5_factors': [
                    {'name': '지하철역 거리', 'category': '입지', 'value': 20.0},
                    {'name': '상권 발달', 'category': '입지', 'value': 15.0},
                    {'name': '정방형 필지', 'category': '물리적', 'value': 10.0},
                    {'name': '도로 접면', 'category': '물리적', 'value': 5.0}
                ]
            }
        }
    }
]

for test_case in test_cases:
    print(f"\n{'=' * 100}")
    print(f"TEST: {test_case['name']}")
    print('=' * 100)
    
    data = test_case['data']
    
    try:
        # PDF 생성
        print("\n1️⃣ Generating HTML...")
        generator = CompleteAppraisalPDFGenerator()
        html = generator.generate_pdf_html(data)
        print(f"   ✅ HTML: {len(html)} characters")
        
        # WeasyPrint로 PDF 변환
        print("\n2️⃣ Converting to PDF...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 파일명에 구 이름 포함
        gu_name = 'gangnam' if '강남구' in data['address'] else 'mapo'
        output_file = f'/home/user/uploaded_files/test_v27_{gu_name}_{timestamp}.pdf'
        
        HTML(string=html).write_pdf(output_file)
        
        import os
        file_size = os.path.getsize(output_file)
        print(f"   ✅ PDF Created: {output_file}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # PDF 검증
        print("\n3️⃣ Validating PDF...")
        reader = PdfReader(output_file)
        num_pages = len(reader.pages)
        print(f"   ✅ Total Pages: {num_pages}")
        
        # 페이지 4 (거래사례) 텍스트 추출
        page_4 = reader.pages[3]  # 0-indexed
        page_4_text = page_4.extract_text()
        
        # 단가 추출 (예: 18,000,000원/㎡ 또는 12,000,000원/㎡)
        import re
        price_pattern = r'(\d{1,2},\d{3},\d{3})원/㎡'
        prices = re.findall(price_pattern, page_4_text)
        
        if prices:
            print(f"\n   📊 거래사례 단가 (샘플):")
            unique_prices = list(set(prices))[:5]
            for price in unique_prices:
                price_int = int(price.replace(',', ''))
                print(f"      - {price}원/㎡ ({price_int/10000:.0f}만원)")
            
            # 평균 단가 계산
            price_ints = [int(p.replace(',', '')) for p in prices]
            avg_price = sum(price_ints) / len(price_ints)
            print(f"\n   💰 평균 단가: {avg_price:,.0f}원/㎡")
            
            # 구별 기준 단가와 비교
            expected_ranges = {
                '강남구': (14000000, 22000000),  # ±20%
                '마포구': (9600000, 14400000)    # ±20%
            }
            
            gu = '강남구' if '강남구' in data['address'] else '마포구'
            min_price, max_price = expected_ranges[gu]
            
            if min_price <= avg_price <= max_price:
                print(f"   ✅ {gu} 시세 범위 내 ({min_price/10000:.0f}~{max_price/10000:.0f}만원)")
            else:
                print(f"   ⚠️ {gu} 시세 범위 벗어남")
        
        # 데이터 출처 확인
        if '국토교통부' in page_4_text or 'MOLIT' in page_4_text:
            print("\n   🟢 데이터 출처: MOLIT API")
        elif '지능형' in page_4_text or '시세 데이터' in page_4_text:
            print("\n   🔵 데이터 출처: 지능형 Fallback (구별 시세 반영)")
        
        print(f"\n   ✅ {test_case['name']} PDF 생성 완료!")
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 100)
print("🎉 All Tests Completed!")
print("=" * 100)
print("\n📁 생성된 PDF 파일:")
print("   - /home/user/uploaded_files/test_v27_gangnam_*.pdf (강남구 18M 기준)")
print("   - /home/user/uploaded_files/test_v27_mapo_*.pdf (마포구 12M 기준)")
print("\n👉 두 PDF를 비교하여 구별 시세가 정확히 반영되었는지 확인하세요!")
