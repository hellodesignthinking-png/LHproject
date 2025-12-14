"""
Test Script for PDF Export v7.4

Tests converting HTML reports to professional PDF documents.
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, '/home/user/webapp')

from app.services.pdf_export_v7_4 import convert_html_file_to_pdf

def main():
    """Test PDF export"""
    
    print("=" * 80)
    print("📄 ZeroSite v7.4 PDF Export Test")
    print("=" * 80)
    print()
    
    # Find the most recent sample HTML report
    webapp_dir = Path('/home/user/webapp')
    html_files = list(webapp_dir.glob('v7_4_sample_report_*.html'))
    
    if not html_files:
        print("❌ No sample HTML reports found!")
        print("   Please run test_v7_4_sample_report.py first to generate a report.")
        return False
    
    # Get most recent file
    html_file = max(html_files, key=lambda p: p.stat().st_mtime)
    pdf_file = html_file.with_suffix('.pdf')
    
    print(f"📊 Input HTML: {html_file.name}")
    print(f"📄 Output PDF: {pdf_file.name}")
    print()
    
    print("🔄 Converting HTML to PDF...")
    print("   This may take 10-20 seconds...")
    print()
    
    success = convert_html_file_to_pdf(
        html_file_path=str(html_file),
        output_pdf_path=str(pdf_file)
    )
    
    if success:
        # Check PDF file
        pdf_size = pdf_file.stat().st_size
        pdf_size_mb = pdf_size / (1024 * 1024)
        
        print("=" * 80)
        print("✅ PDF EXPORT COMPLETE!")
        print("=" * 80)
        print()
        print("📊 Results:")
        print(f"   • Input: {html_file.name}")
        print(f"   • Output: {pdf_file.name}")
        print(f"   • PDF Size: {pdf_size_mb:.2f} MB")
        print(f"   • Full Path: {pdf_file}")
        print()
        print("🎯 Next Steps:")
        print("   1. Open the PDF file to view the report")
        print("   2. Verify page layout and formatting")
        print("   3. Check page numbers and headers/footers")
        print("   4. Validate print quality")
        print()
        return True
    else:
        print("❌ PDF conversion failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
