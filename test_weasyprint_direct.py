"""
Direct WeasyPrint Test
Test WeasyPrint directly without wrapper
"""

from pathlib import Path
import time

# Try importing
try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    print("✅ WeasyPrint imported successfully")
except ImportError as e:
    print(f"❌ Failed to import WeasyPrint: {e}")
    exit(1)

# Test HTML
TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: "Noto Sans KR", "Malgun Gothic", sans-serif;
            margin: 40px;
        }
        h1 { color: #2c3e50; }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        table th, table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        table th {
            background-color: #3498db;
            color: white;
        }
    </style>
</head>
<body>
    <h1>ZeroSite v18 - PDF Generation Test</h1>
    <p>한국어 테스트: 서울특별시 마포구 월드컵북로 120</p>
    
    <h2>재무 분석 (Financial Analysis)</h2>
    <table>
        <thead>
            <tr>
                <th>항목</th>
                <th>금액 (억원)</th>
                <th>비율 (%)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>총사업비 (Total CAPEX)</td>
                <td>137.6</td>
                <td>100.0</td>
            </tr>
            <tr>
                <td>LH 매입가 (LH Purchase)</td>
                <td>106.1</td>
                <td>77.1</td>
            </tr>
            <tr>
                <td>사업수익 (Profit)</td>
                <td>-31.5</td>
                <td>-22.9</td>
            </tr>
        </tbody>
    </table>
    
    <h2>결론 (Conclusion)</h2>
    <p>본 프로젝트는 구조적 수익성이 미흡하여 <strong>NO-GO</strong> 판정입니다.</p>
</body>
</html>
"""

def test_direct_conversion():
    print("\n" + "=" * 80)
    print("🧪 Direct WeasyPrint Test")
    print("=" * 80 + "\n")
    
    output_dir = Path("output/pdf_test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = output_dir / "test_direct.pdf"
    
    print(f"📄 Generating PDF: {pdf_path.name}")
    
    try:
        # Initialize font configuration
        font_config = FontConfiguration()
        
        # Create HTML object
        start_time = time.time()
        html = HTML(string=TEST_HTML)
        
        # Generate PDF
        html.write_pdf(str(pdf_path), font_config=font_config)
        
        duration = time.time() - start_time
        
        if pdf_path.exists():
            file_size_kb = pdf_path.stat().st_size / 1024
            file_size_mb = file_size_kb / 1024
            
            print(f"✅ PDF created successfully!")
            print(f"   📊 Size: {file_size_kb:.1f} KB ({file_size_mb:.3f} MB)")
            print(f"   ⏱️  Duration: {duration:.2f}s")
            print(f"   📁 Path: {pdf_path.absolute()}")
            
            return True
        else:
            print(f"❌ PDF file not created")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_conversion()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 Direct WeasyPrint Test PASSED! ✅")
    else:
        print("❌ Direct WeasyPrint Test FAILED")
    print("=" * 80 + "\n")
    
    exit(0 if success else 1)
