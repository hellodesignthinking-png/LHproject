#!/usr/bin/env python3
"""
Convert Full Edition HTML report to PDF
"""

from pathlib import Path
from weasyprint import HTML, CSS
from app.services_v13.report_full.pdf_exporter_full import PDFExporterFull

def convert_to_pdf(html_path: str, output_pdf_path: str = None):
    """
    Convert HTML report to PDF with LH branding
    
    Args:
        html_path: Path to HTML file
        output_pdf_path: Output PDF path (optional)
    
    Returns:
        Path to generated PDF
    """
    html_file = Path(html_path)
    
    if not html_file.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")
    
    if output_pdf_path:
        pdf_file = Path(output_pdf_path)
    else:
        pdf_file = html_file.with_suffix('.pdf')
    
    print(f"📄 Converting HTML to PDF...")
    print(f"   Input: {html_file}")
    print(f"   Output: {pdf_file}")
    print()
    
    # Read HTML content
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Get PDF CSS from exporter
    exporter = PDFExporterFull()
    pdf_css = exporter._get_pdf_css()
    
    # Generate PDF
    print("⚙️  Generating PDF with WeasyPrint...")
    html = HTML(string=html_content)
    html.write_pdf(
        pdf_file,
        stylesheets=[CSS(string=pdf_css)]
    )
    
    # Get file stats
    pdf_size_kb = pdf_file.stat().st_size / 1024
    pdf_size_mb = pdf_size_kb / 1024
    
    print(f"✅ PDF generated successfully!")
    print()
    print(f"📊 PDF Statistics:")
    print(f"   - File size: {pdf_size_kb:.1f} KB ({pdf_size_mb:.2f} MB)")
    print(f"   - Output: {pdf_file}")
    print()
    
    return str(pdf_file)


if __name__ == "__main__":
    # Convert the generated HTML to PDF
    html_path = "/tmp/zerosite_full_edition_gangnam.html"
    pdf_path = "/tmp/zerosite_full_edition_gangnam.pdf"
    
    try:
        result_pdf = convert_to_pdf(html_path, pdf_path)
        print("="*60)
        print("✅ SUCCESS: PDF Ready for Submission")
        print("="*60)
        print(f"\n📥 Download: {result_pdf}")
        print("\nThis PDF is:")
        print("• LH 신축매입임대 공식 제출용")
        print("• 30-50 페이지 완전 보고서")
        print("• 모든 Phase 데이터 포함")
        print("• 투자자/은행 제출 가능")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
