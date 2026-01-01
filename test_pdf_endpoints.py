"""
ZeroSite v1.1 Task 1.2 - PDF Endpoint Test

목표: E, F 보고서 PDF 다운로드 엔드포인트 테스트
"""

import asyncio
import sys
import aiohttp
from pathlib import Path


async def test_pdf_endpoint(session, report_type: str, endpoint: str, context_id: str):
    """
    PDF 엔드포인트 테스트
    """
    base_url = "http://localhost:8091"
    pdf_url = f"{base_url}{endpoint}?context_id={context_id}"
    output_file = Path(f"test_{report_type}_{context_id}.pdf")
    
    print(f"\n{'='*80}")
    print(f"📄 Testing {report_type} PDF Endpoint")
    print(f"{'='*80}")
    print(f"URL: {pdf_url}")
    print(f"Output: {output_file}")
    print()
    
    try:
        print("⏳ Requesting PDF...")
        async with session.get(pdf_url, timeout=aiohttp.ClientTimeout(total=90)) as response:
            if response.status == 200:
                pdf_bytes = await response.read()
                
                # PDF 파일로 저장
                with open(output_file, "wb") as f:
                    f.write(pdf_bytes)
                
                print(f"✅ PDF Downloaded Successfully!")
                print(f"   - Status: {response.status}")
                print(f"   - Size: {len(pdf_bytes):,} bytes ({len(pdf_bytes) / 1024:.1f} KB)")
                print(f"   - File: {output_file}")
                
                # Content-Type 확인
                content_type = response.headers.get('Content-Type', 'N/A')
                print(f"   - Content-Type: {content_type}")
                
                # Content-Disposition 확인
                content_disp = response.headers.get('Content-Disposition', 'N/A')
                print(f"   - Content-Disposition: {content_disp}")
                
                return True
            else:
                error_text = await response.text()
                print(f"❌ HTTP {response.status}")
                print(f"   Error: {error_text[:500]}")
                return False
                
    except asyncio.TimeoutError:
        print(f"❌ Timeout (90 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """
    Task 1.2 테스트 실행
    """
    print("\n" + "="*80)
    print("🚀 ZeroSite v1.1 Task 1.2 - PDF Endpoint Test")
    print("="*80)
    print()
    
    context_id = "TEST_6REPORT"
    
    tests = [
        ("E. Quick Review", "/api/v4/reports/six-types/quick-review/pdf"),
        ("F. Presentation", "/api/v4/reports/six-types/presentation/pdf"),
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for report_name, endpoint in tests:
            success = await test_pdf_endpoint(session, report_name.split(".")[0].strip(), endpoint, context_id)
            results.append((report_name, success))
            print()
    
    # 결과 요약
    print("="*80)
    print("📊 Test Results Summary")
    print("="*80)
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for report_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {report_name}")
    
    print()
    print(f"Total: {success_count}/{total_count} passed")
    print("="*80)
    
    if success_count == total_count:
        print()
        print("🎉 Task 1.2 완료: E, F 보고서 PDF 엔드포인트 성공!")
        print()
        print("📝 다음 단계:")
        print("   1. 생성된 PDF 파일 육안 확인")
        print("   2. 한글 깨짐 없는지 확인")
        print("   3. 레이아웃 정상인지 확인")
        print("   4. 헤더/푸터 정상 출력 확인")
        print("   5. Git 커밋 후 Task 1.3으로 진행")
        print()
        return True
    else:
        print()
        print("❌ 일부 테스트 실패. 로그를 확인하세요.")
        print()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
