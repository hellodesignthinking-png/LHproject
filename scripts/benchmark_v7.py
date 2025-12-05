#!/usr/bin/env python3
"""
ZeroSite v7.1 Performance Benchmark

Tests system performance under various loads
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json


BASE_URL = "http://localhost:8000"

TEST_ADDRESS = {
    "address": "서울특별시 강남구 테헤란로 152",
    "land_area": 500.0,
    "unit_type": "청년"
}


async def single_request(session: aiohttp.ClientSession) -> Dict:
    """Execute single API request"""
    start = time.time()
    
    try:
        async with session.post(
            f"{BASE_URL}/api/analyze-land",
            json=TEST_ADDRESS,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            duration = time.time() - start
            
            return {
                "success": response.status == 200,
                "status_code": response.status,
                "duration_ms": duration * 1000
            }
    except Exception as e:
        duration = time.time() - start
        return {
            "success": False,
            "error": str(e),
            "duration_ms": duration * 1000
        }


async def run_concurrent_test(num_concurrent: int, num_requests: int) -> List[Dict]:
    """Run concurrent load test"""
    print(f"\n🔄 Running {num_requests} requests with {num_concurrent} concurrency...")
    
    async with aiohttp.ClientSession() as session:
        results = []
        
        for batch_start in range(0, num_requests, num_concurrent):
            batch_size = min(num_concurrent, num_requests - batch_start)
            
            tasks = [single_request(session) for _ in range(batch_size)]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            results.extend([r for r in batch_results if isinstance(r, dict)])
            
            # Show progress
            print(f"  Progress: {len(results)}/{num_requests}", end="\r")
    
    print()  # New line
    return results


def analyze_results(results: List[Dict]):
    """Analyze benchmark results"""
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    durations = [r["duration_ms"] for r in successful]
    
    print(f"\n" + "="*60)
    print(f"📊 BENCHMARK RESULTS")
    print(f"="*60)
    
    print(f"\n✅ Success Rate: {len(successful)}/{len(results)} ({len(successful)/len(results)*100:.1f}%)")
    
    if durations:
        print(f"\n⏱️  Response Times:")
        print(f"   Average: {statistics.mean(durations):.1f}ms")
        print(f"   Median: {statistics.median(durations):.1f}ms")
        print(f"   Min: {min(durations):.1f}ms")
        print(f"   Max: {max(durations):.1f}ms")
        print(f"   P95: {sorted(durations)[int(len(durations)*0.95)]:.1f}ms")
        print(f"   P99: {sorted(durations)[int(len(durations)*0.99)]:.1f}ms")
    
    if failed:
        print(f"\n❌ Failed Requests: {len(failed)}")
    
    # Performance rating
    if durations:
        avg_ms = statistics.mean(durations)
        if avg_ms < 700:
            print(f"\n🏆 EXCELLENT: <700ms average (Target met!)")
        elif avg_ms < 1000:
            print(f"\n✅ GOOD: <1000ms average")
        elif avg_ms < 2000:
            print(f"\n⚠️  ACCEPTABLE: <2000ms average")
        else:
            print(f"\n❌ SLOW: >{avg_ms:.0f}ms average (needs optimization)")


async def main():
    """Main benchmark execution"""
    print("="*60)
    print("🚀 ZeroSite v7.1 Performance Benchmark")
    print("="*60)
    
    # Test 1: Single request baseline
    print(f"\n📍 Test 1: Baseline (single request)")
    results_1 = await run_concurrent_test(num_concurrent=1, num_requests=3)
    analyze_results(results_1)
    
    # Test 2: Moderate load
    print(f"\n📍 Test 2: Moderate Load (5 concurrent, 20 total)")
    results_2 = await run_concurrent_test(num_concurrent=5, num_requests=20)
    analyze_results(results_2)
    
    # Test 3: High load
    print(f"\n📍 Test 3: High Load (10 concurrent, 30 total)")
    results_3 = await run_concurrent_test(num_concurrent=10, num_requests=30)
    analyze_results(results_3)
    
    print(f"\n" + "="*60)
    print(f"✅ Benchmark Complete")
    print(f"="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Benchmark failed: {e}")
