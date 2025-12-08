"""
ZeroSite v18 Phase 4 - Multi-Region Batch Test
===============================================
다중 주소 배치 테스트 (5+ 지역)

Test Regions:
1. 서울 마포구 (Urban Core)
2. 경기 성남시 분당구 (Suburban Premium)
3. 경기 고양시 일산동구 (Suburban Standard)
4. 인천 남동구 (Port City)
5. 경기 화성시 동탄 (New Town)
6. 경기 수원시 영통구 (University District)
"""

import asyncio
import time
from datetime import datetime
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.services_v13.report_full.report_full_generator import generate_lh_full_report

# Test addresses (diverse regions)
TEST_ADDRESSES = [
    {
        "address": "서울특별시 마포구 월드컵북로 120",
        "region": "Seoul Mapo-gu",
        "type": "Urban Core",
        "land_area_m2": 660.0,
        "zoning": "제3종일반주거지역"
    },
    {
        "address": "경기도 성남시 분당구 정자동 178-1",
        "region": "Gyeonggi Seongnam Bundang",
        "type": "Suburban Premium",
        "land_area_m2": 800.0,
        "zoning": "제2종일반주거지역"
    },
    {
        "address": "경기도 고양시 일산동구 장항동 906",
        "region": "Gyeonggi Goyang Ilsan",
        "type": "Suburban Standard",
        "land_area_m2": 1000.0,
        "zoning": "제2종일반주거지역"
    },
    {
        "address": "인천광역시 남동구 구월동 1408",
        "region": "Incheon Namdong-gu",
        "type": "Port City",
        "land_area_m2": 750.0,
        "zoning": "일반상업지역"
    },
    {
        "address": "경기도 화성시 동탄순환대로 21길 87",
        "region": "Gyeonggi Hwaseong Dongtan",
        "type": "New Town",
        "land_area_m2": 900.0,
        "zoning": "제3종일반주거지역"
    },
    {
        "address": "경기도 수원시 영통구 광교로 145",
        "region": "Gyeonggi Suwon Yeongtong",
        "type": "University District",
        "land_area_m2": 700.0,
        "zoning": "준주거지역"
    }
]


async def test_single_address(test_case: dict, test_num: int) -> dict:
    """단일 주소 테스트"""
    print("\n" + "=" * 80)
    print(f"TEST {test_num}: {test_case['region']} ({test_case['type']})")
    print("=" * 80)
    print(f"📍 Address: {test_case['address']}")
    print(f"📐 Land Area: {test_case['land_area_m2']}㎡")
    print(f"🏗️  Zoning: {test_case['zoning']}")
    
    start_time = time.time()
    
    try:
        # Build context directly (synchronous)
        builder = ReportContextBuilder()
        context = builder.build_context(
            address=test_case['address'],
            land_area_sqm=test_case['land_area_m2'],
            coordinates=None,
            multi_parcel=False,
            parcels=None,
            additional_params=None
        )
        
        duration = time.time() - start_time
        
        # Extract key results from context
        v18 = context.get('v18_transaction', {})
        summary = v18.get('summary', {})
        
        result = {
            "status": "✅ SUCCESS",
            "duration": duration,
            "total_capex": summary.get('total_capex_krw', 0),
            "lh_purchase": summary.get('lh_purchase_price_krw', 0),
            "profit": summary.get('profit_krw', 0),
            "roi_pct": summary.get('roi_pct', 0),
            "irr_pct": summary.get('irr_pct', 0),
            "decision": summary.get('decision', 'N/A'),
            "land_comps": len(v18.get('land_comps', [])),
            "building_comps": len(v18.get('building_comps', []))
        }
        
        print(f"\n⏱️  Generation Time: {duration:.2f}s")
        print(f"💰 Total CAPEX: {result['total_capex']/1e8:.1f}억원")
        print(f"🏛️  LH Purchase: {result['lh_purchase']/1e8:.1f}억원")
        print(f"📊 Profit: {result['profit']/1e8:.1f}억원")
        print(f"📈 ROI: {result['roi_pct']:.2f}%")
        print(f"📉 IRR: {result['irr_pct']:.2f}%")
        print(f"✅ Decision: {result['decision']}")
        print(f"🏞️  Land Comparables: {result['land_comps']}")
        print(f"🏢 Building Comparables: {result['building_comps']}")
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ ERROR: {str(e)}")
        print(f"⏱️  Duration: {duration:.2f}s")
        
        return {
            "status": "❌ FAILED",
            "duration": duration,
            "error": str(e)
        }


async def main():
    print("\n" + "=" * 80)
    print("ZeroSite v18 Phase 4 - Multi-Region Batch Test")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"\n📋 Testing {len(TEST_ADDRESSES)} regions across Korea")
    print("   - Urban Core: Seoul")
    print("   - Suburban Areas: Bundang, Ilsan, Dongtan, Yeongtong")
    print("   - Port City: Incheon")
    print()
    
    overall_start = time.time()
    results = []
    
    # Test each address
    for idx, test_case in enumerate(TEST_ADDRESSES, 1):
        result = await test_single_address(test_case, idx)
        results.append({
            "test_case": test_case,
            "result": result
        })
        
        # Brief pause between tests
        if idx < len(TEST_ADDRESSES):
            await asyncio.sleep(1)
    
    overall_duration = time.time() - overall_start
    
    # Summary Report
    print("\n" + "=" * 80)
    print("📊 BATCH TEST SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in results if r['result']['status'] == "✅ SUCCESS")
    failed = len(results) - successful
    
    print(f"\nTotal Tests: {len(results)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Time: {overall_duration:.2f}s")
    print(f"⏱️  Average Time per Test: {overall_duration/len(results):.2f}s")
    
    # Detailed results table
    print("\n" + "-" * 80)
    print(f"{'Region':<30} {'Status':<12} {'CAPEX':<10} {'Profit':<10} {'Decision':<15}")
    print("-" * 80)
    
    for item in results:
        tc = item['test_case']
        res = item['result']
        
        if res['status'] == "✅ SUCCESS":
            capex_str = f"{res['total_capex']/1e8:.1f}억"
            profit_str = f"{res['profit']/1e8:.1f}억"
            decision = res['decision']
        else:
            capex_str = "N/A"
            profit_str = "N/A"
            decision = "ERROR"
        
        print(f"{tc['region']:<30} {res['status']:<12} {capex_str:<10} {profit_str:<10} {decision:<15}")
    
    print("-" * 80)
    
    # Financial Summary (for successful tests only)
    successful_results = [r['result'] for r in results if r['result']['status'] == "✅ SUCCESS"]
    
    if successful_results:
        print("\n" + "=" * 80)
        print("💰 FINANCIAL SUMMARY (Successful Tests)")
        print("=" * 80)
        
        avg_capex = sum(r['total_capex'] for r in successful_results) / len(successful_results)
        avg_lh = sum(r['lh_purchase'] for r in successful_results) / len(successful_results)
        avg_profit = sum(r['profit'] for r in successful_results) / len(successful_results)
        avg_roi = sum(r['roi_pct'] for r in successful_results) / len(successful_results)
        avg_irr = sum(r['irr_pct'] for r in successful_results) / len(successful_results)
        
        print(f"Average CAPEX: {avg_capex/1e8:.1f}억원")
        print(f"Average LH Purchase: {avg_lh/1e8:.1f}억원")
        print(f"Average Profit: {avg_profit/1e8:.1f}억원")
        print(f"Average ROI: {avg_roi:.2f}%")
        print(f"Average IRR: {avg_irr:.2f}%")
        
        # Decision distribution
        decisions = {}
        for r in successful_results:
            dec = r['decision']
            decisions[dec] = decisions.get(dec, 0) + 1
        
        print("\nDecision Distribution:")
        for dec, count in decisions.items():
            print(f"  {dec}: {count} ({count/len(successful_results)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ BATCH TEST COMPLETE!")
    print("=" * 80)
    print(f"\nResults Summary:")
    print(f"  - Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"  - Total Duration: {overall_duration:.2f}s")
    print(f"  - Average per Region: {overall_duration/len(results):.2f}s")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
