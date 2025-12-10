"""
ZeroSite v18 Phase 4 - Simplified Multi-Region Batch Test
===========================================================
Based on working test_v18_integration.py
"""

import asyncio
from app.services.policy_transaction_financial_engine_v18 import PolicyTransactionFinancialEngineV18

# Test addresses (diverse regions)
TEST_ADDRESSES = [
    {
        "name": "Seoul Mapo-gu",
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area_m2": 660.0,
        "land_price": 10000000,  # 1000만원/㎡
        "construction_cost": 3500000  # 350만원/㎡
    },
    {
        "name": "Gyeonggi Seongnam Bundang",
        "address": "경기도 성남시 분당구 정자동 178-1",
        "land_area_m2": 800.0,
        "land_price": 9000000,  # 900만원/㎡
        "construction_cost": 3200000  # 320만원/㎡
    },
    {
        "name": "Gyeonggi Goyang Ilsan",
        "address": "경기도 고양시 일산동구 장항동 906",
        "land_area_m2": 1000.0,
        "land_price": 7000000,  # 700만원/㎡
        "construction_cost": 3000000  # 300만원/㎡
    },
    {
        "name": "Incheon Namdong-gu",
        "address": "인천광역시 남동구 구월동 1408",
        "land_area_m2": 750.0,
        "land_price": 6000000,  # 600만원/㎡
        "construction_cost": 2800000  # 280만원/㎡
    },
    {
        "name": "Gyeonggi Hwaseong Dongtan",
        "address": "경기도 화성시 동탄순환대로 21길 87",
        "land_area_m2": 900.0,
        "land_price": 8000000,  # 800만원/㎡
        "construction_cost": 3300000  # 330만원/㎡
    },
    {
        "name": "Gyeonggi Suwon Yeongtong",
        "address": "경기도 수원시 영통구 광교로 145",
        "land_area_m2": 700.0,
        "land_price": 8500000,  # 850만원/㎡
        "construction_cost": 3400000  # 340만원/㎡
    }
]


def test_region(test_case: dict, test_num: int):
    """Test single region with v18 engine"""
    print("\n" + "=" * 80)
    print(f"TEST {test_num}: {test_case['name']}")
    print("=" * 80)
    print(f"📍 Address: {test_case['address']}")
    print(f"📐 Land Area: {test_case['land_area_m2']}㎡")
    print(f"💰 Land Price: {test_case['land_price']/10000:.0f}만원/㎡")
    print(f"🏗️  Construction Cost: {test_case['construction_cost']/10000:.0f}만원/㎡")
    
    # Calculate building area (assume 200% floor area ratio)
    building_area_m2 = test_case['land_area_m2'] * 2.0
    
    # Create inputs
    from app.services.policy_transaction_financial_engine_v18 import TransactionInputs
    
    inputs = TransactionInputs(
        land_area_m2=test_case['land_area_m2'],
        building_area_m2=building_area_m2,
        land_price_per_m2=test_case['land_price'],
        construction_cost_per_m2=test_case['construction_cost']
    )
    
    # Initialize v18 engine
    engine = PolicyTransactionFinancialEngineV18(inputs)
    
    # Evaluate
    result = engine.evaluate()
    
    print(f"\n💰 Financial Results:")
    print(f"   Total CAPEX: {result.cost/1e8:.2f}억원")
    print(f"   LH Purchase: {result.revenue/1e8:.2f}억원")
    print(f"   Profit: {result.profit/1e8:.2f}억원")
    print(f"   ROI: {result.roi_pct:.2f}%")
    print(f"   IRR: {result.irr_pct:.2f}%")
    print(f"   Payback: {result.payback_years:.1f} years")
    print(f"   ✅ Decision: {result.decision}")
    print(f"   📝 Reason: {result.decision_reason}")
    
    return {
        "name": test_case['name'],
        "capex": result.cost,
        "lh_purchase": result.revenue,
        "profit": result.profit,
        "roi": result.roi_pct,
        "irr": result.irr_pct,
        "decision": result.decision
    }


def main():
    print("\n" + "=" * 80)
    print("ZeroSite v18 Phase 4 - Multi-Region Batch Test (Simplified)")
    print("=" * 80)
    print(f"\n📋 Testing {len(TEST_ADDRESSES)} regions across Korea\n")
    
    results = []
    
    for idx, test_case in enumerate(TEST_ADDRESSES, 1):
        try:
            result = test_region(test_case, idx)
            results.append(result)
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            results.append({
                "name": test_case['name'],
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 BATCH TEST SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Region':<35} {'CAPEX':<12} {'Profit':<12} {'ROI':<10} {'Decision':<15}")
    print("-" * 80)
    
    for r in results:
        if 'error' not in r:
            print(f"{r['name']:<35} "
                  f"{r['capex']/1e8:>10.1f}억 "
                  f"{r['profit']/1e8:>10.1f}억 "
                  f"{r['roi']:>8.1f}% "
                  f"{r['decision']:<15}")
        else:
            print(f"{r['name']:<35} ERROR: {r['error']}")
    
    print("-" * 80)
    
    # Financial Statistics
    valid_results = [r for r in results if 'error' not in r]
    
    if valid_results:
        avg_capex = sum(r['capex'] for r in valid_results) / len(valid_results)
        avg_profit = sum(r['profit'] for r in valid_results) / len(valid_results)
        avg_roi = sum(r['roi'] for r in valid_results) / len(valid_results)
        avg_irr = sum(r['irr'] for r in valid_results) / len(valid_results)
        
        print(f"\n💰 Average Metrics:")
        print(f"   CAPEX: {avg_capex/1e8:.1f}억원")
        print(f"   Profit: {avg_profit/1e8:.1f}억원")
        print(f"   ROI: {avg_roi:.2f}%")
        print(f"   IRR: {avg_irr:.2f}%")
        
        # Decision distribution
        decisions = {}
        for r in valid_results:
            d = r['decision']
            decisions[d] = decisions.get(d, 0) + 1
        
        print(f"\n✅ Decision Distribution:")
        for dec, count in decisions.items():
            print(f"   {dec}: {count} ({count/len(valid_results)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("✅ BATCH TEST COMPLETE!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
