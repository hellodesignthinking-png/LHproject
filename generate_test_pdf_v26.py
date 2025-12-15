#!/usr/bin/env python3
"""
Generate Complete Test PDF v26.0
완전한 PDF 파일 생성 (WeasyPrint)
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.complete_appraisal_pdf_generator import CompleteAppraisalPDFGenerator
from weasyprint import HTML
from datetime import datetime

# 테스트 데이터
test_data = {
    'address': '서울시 강남구 역삼동 123-4',
    'land_area_sqm': 660,
    'zone_type': '제3종일반주거지역',
    'individual_land_price': 8500000,
    'final_appraisal_value': 90.90,
    'client_name': '테스트 의뢰인',
    
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
print("📄 Generating Complete Test PDF v26.0")
print("=" * 80)

try:
    # 1. HTML 생성
    print("\n1️⃣ Generating HTML...")
    generator = CompleteAppraisalPDFGenerator()
    html = generator.generate_pdf_html(test_data)
    print(f"   ✅ HTML: {len(html)} characters")
    
    # 2. PDF 생성
    print("\n2️⃣ Converting to PDF...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'/home/user/uploaded_files/test_pdf_v26_{timestamp}.pdf'
    
    HTML(string=html).write_pdf(output_file)
    
    import os
    file_size = os.path.getsize(output_file)
    print(f"   ✅ PDF Created: {output_file}")
    print(f"   📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    # 3. PDF 검증
    print("\n3️⃣ Validating PDF...")
    from pypdf import PdfReader
    
    reader = PdfReader(output_file)
    num_pages = len(reader.pages)
    print(f"   ✅ Total Pages: {num_pages}")
    
    # 페이지별 텍스트 검증
    for i, page in enumerate(reader.pages[:5], 1):
        text = page.extract_text()
        print(f"   📄 Page {i}: {len(text)} characters")
        
        # 핵심 키워드 확인
        if i == 1:
            if '상세 감정평가 보고서' in text:
                print(f"      ✅ Cover page detected")
        elif i == 2:
            if '평가 개요' in text and '제3종' in text:
                print(f"      ✅ Executive Summary with zone type")
        elif i == 3:
            if '3대 평가 방식' in text:
                print(f"      ✅ 3-Method Summary Table")
        elif i == 4:
            if '거래사례' in text or '거래일' in text:
                print(f"      ✅ Transaction Comparison Table")
        elif i == 5:
            if '프리미엄' in text and '72.5' in text:
                print(f"      ✅ Premium Analysis with explanation")
    
    print("\n" + "=" * 80)
    print(f"🎉 PDF Generation Complete!")
    print(f"📁 Location: {output_file}")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
