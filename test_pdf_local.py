"""
ZeroSite v1.1 - PDF 생성 로컬 테스트

목표: E. 사전 검토 보고서를 PDF로 변환하여 실제 생성 확인
"""

import asyncio
import sys
import os

# app 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.pdf_generator_playwright import generate_pdf_from_url


async def test_quick_review_pdf():
    """
    E. 사전 검토 보고서 PDF 생성 테스트
    """
    print("\n" + "="*80)
    print("🚀 ZeroSite v1.1 - PDF Generation Test")
    print("="*80 + "\n")
    
    # 테스트 설정
    base_url = "http://localhost:8091"
    run_id = "TEST_6REPORT"
    report_type = "E"
    html_endpoint = f"{base_url}/api/v4/reports/six-types/quick-review/html?context_id={run_id}"
    output_filename = f"test_{report_type}_quick_review.pdf"
    
    print(f"📋 Test Configuration:")
    print(f"   - RUN_ID: {run_id}")
    print(f"   - Report Type: {report_type} (Quick Review)")
    print(f"   - HTML Endpoint: {html_endpoint}")
    print(f"   - Output File: {output_filename}")
    print()
    
    try:
        print("⏳ Starting PDF generation...")
        pdf_bytes = await generate_pdf_from_url(
            url=html_endpoint,
            run_id=run_id,
            report_type=report_type
        )
        
        # PDF 파일로 저장
        with open(output_filename, "wb") as f:
            f.write(pdf_bytes)
        
        print(f"✅ PDF generation successful!")
        print(f"   - File size: {len(pdf_bytes):,} bytes")
        print(f"   - File saved: {output_filename}")
        print()
        print("🎉 Task 1.1 완료: PDF 엔진 구축 성공!")
        print()
        print("📝 다음 단계:")
        print("   1. PDF 파일 열어서 육안 확인")
        print("   2. 한글 깨짐 없는지 확인")
        print("   3. 레이아웃 정상인지 확인")
        print("   4. 헤더/푸터 정상 출력 확인")
        print()
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def test_all_reports():
    """
    6종 보고서 모두 PDF 생성 테스트 (선택적)
    """
    base_url = "http://localhost:8091"
    run_id = "TEST_6REPORT"
    
    reports = [
        ("A", "master", "종합 최종"),
        ("B", "landowner", "토지주 제출용"),
        ("C", "lh/technical", "LH 기술검증"),
        ("D", "investment", "사업성·투자"),
        ("E", "quick-review", "사전 검토"),
        ("F", "presentation", "설명용 프레젠테이션"),
    ]
    
    print("\n" + "="*80)
    print("🚀 ZeroSite v1.1 - 6종 보고서 PDF 생성 테스트")
    print("="*80 + "\n")
    
    results = []
    
    for report_type, endpoint, name in reports:
        print(f"📄 Testing {report_type}. {name}...")
        html_url = f"{base_url}/api/v4/reports/six-types/{endpoint}/html?context_id={run_id}"
        output_file = f"test_{report_type}_{endpoint.replace('/', '_')}.pdf"
        
        try:
            pdf_bytes = await generate_pdf_from_url(
                url=html_url,
                run_id=run_id,
                report_type=report_type
            )
            
            with open(output_file, "wb") as f:
                f.write(pdf_bytes)
            
            print(f"   ✅ Success: {len(pdf_bytes):,} bytes → {output_file}")
            results.append((report_type, True, len(pdf_bytes)))
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results.append((report_type, False, 0))
        
        print()
    
    # 결과 요약
    print("="*80)
    print("📊 Test Results Summary")
    print("="*80)
    success_count = sum(1 for _, success, _ in results if success)
    print(f"✅ Success: {success_count} / {len(reports)}")
    print(f"❌ Failed: {len(reports) - success_count} / {len(reports)}")
    print()
    
    for report_type, success, size in results:
        status = "✅" if success else "❌"
        size_str = f"{size:,} bytes" if success else "N/A"
        print(f"   {status} {report_type}: {size_str}")
    
    print("="*80)


async def main():
    """
    메인 실행 함수
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="ZeroSite PDF Generation Test")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Test all 6 reports (default: only E report)"
    )
    
    args = parser.parse_args()
    
    if args.all:
        await test_all_reports()
    else:
        success = await test_quick_review_pdf()
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
