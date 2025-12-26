#!/usr/bin/env python3
"""빠른 PDF 변환"""

from weasyprint import HTML
import os

html_dir = '/home/user/webapp/final_reports_phase25'
pdf_dir = '/home/user/webapp/final_reports_pdf'
os.makedirs(pdf_dir, exist_ok=True)

reports = [
    ('quick_check_phase25_real_data.html', '1_빠른검토용.pdf'),
    ('financial_feasibility_phase25_real_data.html', '2_사업성중심보고서.pdf'),
    ('lh_technical_phase25_real_data.html', '3_LH기술검토용.pdf'),
    ('executive_summary_phase25_real_data.html', '4_경영진용요약본.pdf'),
    ('landowner_summary_phase25_real_data.html', '5_토지주용요약본.pdf'),
    ('all_in_one_phase25_real_data.html', '6_전체통합보고서.pdf')
]

for html_file, pdf_file in reports:
    print(f"📄 {pdf_file} 변환 중...")
    try:
        html_path = f'{html_dir}/{html_file}'
        pdf_path = f'{pdf_dir}/{pdf_file}'
        HTML(filename=html_path).write_pdf(pdf_path)
        size = os.path.getsize(pdf_path) / 1024
        print(f"   ✅ 완료: {size:.1f} KB\n")
    except Exception as e:
        print(f"   ❌ 실패: {e}\n")
