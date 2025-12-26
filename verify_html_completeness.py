#!/usr/bin/env python3
"""HTML 보고서 완전성 검증 - 모든 모듈 데이터 포함 확인"""

import os
import re
from pathlib import Path

def verify_html_report(filepath):
    """HTML 보고서 검증"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    filename = Path(filepath).name
    report_name = filename.replace('_phase25_real_data.html', '')
    
    checks = {
        'file_size': len(content),
        'has_title': bool(re.search(r'<title>.+</title>', content)),
        'has_style': bool(re.search(r'<style>', content)),
        'has_kpi_card': bool(re.search(r'kpi-summary-card', content)),
        'has_data_values': bool(re.search(r'1,621,848,717|793,000,000|7\.9억', content)),
        'has_units': bool(re.search(r'26세대|26\s*세대', content)),
        'has_approval': bool(re.search(r'75\.0%|75%', content)),
        'has_grade': bool(re.search(r'B등급', content)),
        'has_address': bool(re.search(r'서울|강남|테헤란', content)),
        'has_zoning': bool(re.search(r'제2종일반주거', content)),
        'has_strong_tags': len(re.findall(r'<strong>', content)),
        'has_headers': len(re.findall(r'<h[123]>', content)),
    }
    
    return report_name, checks

# 검증 실행
reports_dir = 'final_reports_phase25'
html_files = [
    'all_in_one_phase25_real_data.html',
    'financial_feasibility_phase25_real_data.html',
    'lh_technical_phase25_real_data.html',
    'executive_summary_phase25_real_data.html',
    'landowner_summary_phase25_real_data.html',
    'quick_check_phase25_real_data.html',
]

print("=" * 70)
print("  📊 HTML 보고서 완전성 검증")
print("=" * 70)
print()

total_checks = 0
passed_checks = 0

for html_file in html_files:
    filepath = os.path.join(reports_dir, html_file)
    if not os.path.exists(filepath):
        print(f"❌ {html_file}: 파일 없음")
        continue
    
    report_name, checks = verify_html_report(filepath)
    
    print(f"📄 {report_name}")
    print(f"   파일명: {html_file}")
    print(f"   크기: {checks['file_size']:,} bytes")
    print()
    
    # 핵심 검증 항목
    critical = [
        ('제목', checks['has_title']),
        ('스타일', checks['has_style']),
        ('KPI 카드', checks['has_kpi_card']),
        ('데이터 값', checks['has_data_values']),
        ('세대수', checks['has_units']),
        ('승인율', checks['has_approval']),
    ]
    
    for name, result in critical:
        symbol = "✅" if result else "❌"
        print(f"   {symbol} {name}: {result}")
        total_checks += 1
        if result:
            passed_checks += 1
    
    # 추가 정보
    print(f"   📌 <strong> 태그: {checks['has_strong_tags']}개")
    print(f"   📌 헤더 태그: {checks['has_headers']}개")
    print()
    print("-" * 70)
    print()

print("=" * 70)
print(f"  최종 결과: {passed_checks}/{total_checks} 검증 통과")
print("=" * 70)

if passed_checks == total_checks:
    print("✅ 모든 HTML 보고서가 완전한 데이터를 포함하고 있습니다.")
    print("✅ PDF 변환 준비 완료")
else:
    print(f"⚠️  {total_checks - passed_checks}개 항목 미달")
    print("⚠️  일부 데이터 누락 가능성")
