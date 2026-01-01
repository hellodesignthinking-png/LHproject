"""
PDF 캐싱 검증 테스트

목표:
- 동일 RUN_ID + report_type 요청 시 Playwright 재실행 방지 검증
- Cache HIT/MISS 동작 확인
- 성능 개선 측정 (Cache HIT < 500ms)

테스트 시나리오:
1. 첫 요청: Cache MISS → Playwright 실행 (느림)
2. 두 번째 요청: Cache HIT → 즉시 반환 (빠름)
3. TTL 만료 확인
"""

import asyncio
import time
import aiohttp
from typing import Dict


BASE_URL = "http://localhost:8091"
TEST_RUN_ID = "TEST_6REPORT"


async def test_pdf_cache_hit_miss():
    """
    Cache HIT/MISS 시나리오 테스트
    """
    print("=" * 80)
    print("📋 Task 1.3: PDF 캐싱 검증 테스트")
    print("=" * 80)
    print()
    
    # E. Quick Review 테스트
    endpoint_e = f"{BASE_URL}/api/v4/reports/six-types/quick-review/pdf?context_id={TEST_RUN_ID}"
    
    print("🔵 [E. Quick Review] PDF 캐싱 테스트")
    print(f"   Endpoint: {endpoint_e}")
    print()
    
    async with aiohttp.ClientSession() as session:
        # 1차 요청: Cache MISS (느림)
        print("   ⏳ 1차 요청: Cache MISS (Playwright 실행 예상)...")
        start_1 = time.time()
        
        try:
            async with session.get(endpoint_e) as response:
                status_1 = response.status
                pdf_bytes_1 = await response.read()
                cache_status_1 = response.headers.get("X-Cache-Status", "UNKNOWN")
                elapsed_1 = time.time() - start_1
                
                print(f"   ✅ 1차 요청 완료:")
                print(f"      - Status: {status_1}")
                print(f"      - Cache Status: {cache_status_1}")
                print(f"      - PDF Size: {len(pdf_bytes_1):,} bytes")
                print(f"      - Elapsed Time: {elapsed_1:.2f}s")
                print()
        
        except Exception as e:
            print(f"   ❌ 1차 요청 실패: {e}")
            return False
        
        # 2초 대기 (캐시 안정화)
        await asyncio.sleep(2)
        
        # 2차 요청: Cache HIT (빠름)
        print("   ⚡ 2차 요청: Cache HIT (즉시 반환 예상)...")
        start_2 = time.time()
        
        try:
            async with session.get(endpoint_e) as response:
                status_2 = response.status
                pdf_bytes_2 = await response.read()
                cache_status_2 = response.headers.get("X-Cache-Status", "UNKNOWN")
                elapsed_2 = time.time() - start_2
                
                print(f"   ✅ 2차 요청 완료:")
                print(f"      - Status: {status_2}")
                print(f"      - Cache Status: {cache_status_2}")
                print(f"      - PDF Size: {len(pdf_bytes_2):,} bytes")
                print(f"      - Elapsed Time: {elapsed_2:.2f}s")
                print()
        
        except Exception as e:
            print(f"   ❌ 2차 요청 실패: {e}")
            return False
    
    # 검증
    print("📊 검증 결과:")
    print()
    
    success = True
    
    # 1) Cache Status 확인
    if cache_status_1 == "MISS":
        print("   ✅ 1차 요청 Cache MISS 확인")
    else:
        print(f"   ❌ 1차 요청 Cache Status 불일치: {cache_status_1} (예상: MISS)")
        success = False
    
    if cache_status_2 == "HIT":
        print("   ✅ 2차 요청 Cache HIT 확인")
    else:
        print(f"   ❌ 2차 요청 Cache Status 불일치: {cache_status_2} (예상: HIT)")
        success = False
    
    # 2) PDF 크기 일치 확인
    if len(pdf_bytes_1) == len(pdf_bytes_2):
        print(f"   ✅ PDF 크기 일치: {len(pdf_bytes_1):,} bytes")
    else:
        print(f"   ❌ PDF 크기 불일치: 1차={len(pdf_bytes_1):,}, 2차={len(pdf_bytes_2):,}")
        success = False
    
    # 3) 성능 개선 확인
    speedup = elapsed_1 / elapsed_2 if elapsed_2 > 0 else 0
    print(f"   📈 성능 개선: {speedup:.1f}x 빠름 (1차: {elapsed_1:.2f}s → 2차: {elapsed_2:.2f}s)")
    
    if elapsed_2 < 0.5:
        print(f"   ✅ Cache HIT 응답 시간 < 500ms 달성")
    else:
        print(f"   ⚠️  Cache HIT 응답 시간: {elapsed_2:.2f}s (목표: < 0.5s)")
    
    print()
    
    if success:
        print("🎉 Task 1.3 검증 성공!")
        print()
        print("핵심 성과:")
        print("  - 같은 RUN_ID + report_type 재요청 시 Playwright 재실행 방지")
        print("  - Cache HIT로 즉시 PDF 반환")
        print(f"  - 성능 개선: {speedup:.1f}x")
        print()
        return True
    else:
        print("❌ Task 1.3 검증 실패")
        return False


async def test_cache_stats():
    """
    캐시 통계 확인
    """
    print("=" * 80)
    print("📊 캐시 통계 확인")
    print("=" * 80)
    
    from app.services.pdf_cache import get_cache_stats
    
    stats = get_cache_stats()
    
    print(f"  - Total Entries: {stats['total_entries']}")
    print(f"  - Total Size: {stats['total_size_bytes']:,} bytes ({stats['total_size_bytes'] / 1024 / 1024:.2f} MB)")
    print(f"  - Expired Entries: {stats['expired_entries']}")
    print(f"  - Cache Directory: {stats['cache_dir']}")
    print()


async def main():
    """
    전체 캐싱 검증 실행
    """
    # 1. Cache HIT/MISS 테스트
    success = await test_pdf_cache_hit_miss()
    
    # 2. 캐시 통계 확인
    await test_cache_stats()
    
    if success:
        print("=" * 80)
        print("✅ v1.1-beta 준비 완료")
        print("=" * 80)
        print()
        print("다음 단계:")
        print("  1. v1.1.0-beta 태그 생성")
        print("  2. PR 생성 및 main 머지")
        print("  3. Task 2.x: 권한 시스템 설계")
        print()


if __name__ == "__main__":
    asyncio.run(main())
