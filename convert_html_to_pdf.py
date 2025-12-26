#!/usr/bin/env python3
"""
HTML에서 PDF로 변환 - LH 제출용
레이아웃, 폰트, 컬러, 모든 데이터 완벽 유지
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("❌ WeasyPrint not installed")
    print("   Run: pip install weasyprint")
    sys.exit(1)

def convert_html_to_pdf(html_path, pdf_path, verbose=True):
    """HTML을 PDF로 변환 (레이아웃/폰트/칼라 유지)"""
    try:
        if verbose:
            print(f"📄 변환 중: {Path(html_path).name}")
            print(f"   → {Path(pdf_path).name}")
        
        # Font configuration for better rendering
        font_config = FontConfiguration()
        
        # Custom CSS for PDF optimization
        pdf_css = CSS(string='''
            @page {
                size: A4;
                margin: 15mm 10mm;
            }
            
            body {
                font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
                line-height: 1.6;
            }
            
            /* Ensure colors are preserved */
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
            }
            
            /* Prevent page breaks inside important elements */
            .kpi-summary-card,
            .decision-card,
            .info-grid,
            .data-table {
                page-break-inside: avoid;
            }
            
            /* Ensure gradients are rendered */
            .kpi-summary-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            }
            
            h1, h2, h3 {
                page-break-after: avoid;
            }
            
            /* Table optimization */
            table {
                page-break-inside: auto;
            }
            
            tr {
                page-break-inside: avoid;
                page-break-after: auto;
            }
        ''', font_config=font_config)
        
        # Convert HTML to PDF
        html = HTML(filename=html_path)
        html.write_pdf(
            pdf_path,
            stylesheets=[pdf_css],
            font_config=font_config,
            presentational_hints=True,  # Keep inline styles
        )
        
        # Check file size
        size = os.path.getsize(pdf_path)
        size_mb = size / (1024 * 1024)
        
        if verbose:
            print(f"   ✅ 성공! 크기: {size_mb:.2f} MB")
        
        return True, size
        
    except Exception as e:
        if verbose:
            print(f"   ❌ 실패: {str(e)}")
        return False, 0

def main():
    """메인 실행 함수"""
    print("=" * 70)
    print("  📄 → 📕 HTML to PDF Converter")
    print("  LH 제출용 최종 보고서 생성")
    print("=" * 70)
    print()
    
    # 입출력 디렉토리
    input_dir = Path("final_reports_phase25")
    output_dir = Path("final_reports_pdf")
    output_dir.mkdir(exist_ok=True)
    
    # 6종 보고서 목록
    reports = {
        "quick_check_phase25_real_data.html": "1_빠른검토용.pdf",
        "financial_feasibility_phase25_real_data.html": "2_사업성중심보고서.pdf",
        "lh_technical_phase25_real_data.html": "3_LH기술검토용.pdf",
        "executive_summary_phase25_real_data.html": "4_경영진용요약본.pdf",
        "landowner_summary_phase25_real_data.html": "5_토지주용요약본.pdf",
        "all_in_one_phase25_real_data.html": "6_전체통합보고서.pdf",
    }
    
    # 변환 실행
    success_count = 0
    total_size = 0
    results = []
    
    print(f"입력: {input_dir}/")
    print(f"출력: {output_dir}/")
    print()
    print("-" * 70)
    print()
    
    for html_file, pdf_file in reports.items():
        html_path = input_dir / html_file
        pdf_path = output_dir / pdf_file
        
        if not html_path.exists():
            print(f"⚠️  HTML 파일 없음: {html_file}")
            results.append((pdf_file, False, 0))
            continue
        
        success, size = convert_html_to_pdf(str(html_path), str(pdf_path))
        
        if success:
            success_count += 1
            total_size += size
            results.append((pdf_file, True, size))
        else:
            results.append((pdf_file, False, 0))
        
        print()
    
    # 결과 요약
    print("=" * 70)
    print("  📊 변환 결과")
    print("=" * 70)
    print()
    
    for pdf_file, success, size in results:
        if success:
            size_mb = size / (1024 * 1024)
            print(f"✅ {pdf_file:<35} {size_mb:>6.2f} MB")
        else:
            print(f"❌ {pdf_file:<35} {'실패':>10}")
    
    print()
    print("-" * 70)
    total_mb = total_size / (1024 * 1024)
    print(f"총 {success_count}/6 성공   총 크기: {total_mb:.2f} MB")
    print()
    
    if success_count == 6:
        print("🎉 모든 PDF 변환 완료!")
        print(f"📁 저장 위치: {output_dir}/")
        print()
        print("✅ LH 제출 준비 완료")
        return 0
    else:
        print(f"⚠️  {6 - success_count}개 보고서 변환 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())
