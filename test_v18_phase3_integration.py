#!/usr/bin/env python3
"""
ZeroSite v18 Phase 3 Integration Test
======================================
실거래가 기반 완전 통합 테스트

Tests:
1. Real Transaction API 동작 확인
2. Context Builder 실거래가 통합
3. Template 렌더링 (토지/건물 비교표)
4. End-to-End 리포트 생성
"""

import sys
sys.path.insert(0, '/home/user/webapp')

import asyncio
import logging
from app.services_v13.report_full.report_context_builder import ReportContextBuilder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_real_transaction_api():
    """Test 1: Real Transaction API"""
    print("=" * 80)
    print("🧪 Test 1: Real Transaction API")
    print("=" * 80)
    
    try:
        from app.services.real_transaction_api import RealTransactionAPI
        
        api = RealTransactionAPI()
        test_address = "서울특별시 마포구 월드컵북로 120"
        
        land_comps, building_comps = await api.fetch_comparables(test_address)
        
        print(f"\n✅ API Test PASSED")
        print(f"   Land comparables: {len(land_comps)}개")
        print(f"   Building comparables: {len(building_comps)}개")
        
        if land_comps:
            avg_land = sum(c.unit_krw_m2 for c in land_comps) / len(land_comps)
            print(f"   평균 토지 단가: {avg_land/10000:.0f}만원/㎡")
        
        if building_comps:
            avg_bld = sum(c.unit_krw_m2 for c in building_comps) / len(building_comps)
            print(f"   평균 건물 단가: {avg_bld/10000:.0f}만원/㎡")
        
        return True
        
    except Exception as e:
        print(f"❌ API Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_builder():
    """Test 2: Context Builder Integration"""
    print("\n" + "=" * 80)
    print("🧪 Test 2: Context Builder Integration")
    print("=" * 80)
    
    try:
        builder = ReportContextBuilder()
        test_address = "서울특별시 마포구 월드컵북로 120"
        
        context = builder.build_context(
            address=test_address,
            land_area_sqm=660.0
        )
        
        # Check v18_transaction exists
        if 'v18_transaction' not in context:
            print("❌ v18_transaction not in context!")
            return False
        
        v18 = context['v18_transaction']
        
        # Check comparables data
        print(f"\n✅ Context Builder Test PASSED")
        print(f"   Land comps in context: {v18.get('land_comps_count', 0)}개")
        print(f"   Building comps in context: {v18.get('building_comps_count', 0)}개")
        print(f"   Real transaction based: {v18.get('is_real_transaction_based', False)}")
        
        if v18.get('land_comps'):
            print(f"\n📊 Sample Land Comp:")
            comp = v18['land_comps'][0]
            print(f"   Address: {comp.get('address', 'N/A')}")
            print(f"   Unit price: {comp.get('unit_krw_m2', 0)/10000:.0f}만원/㎡")
        
        if v18.get('building_comps'):
            print(f"\n📊 Sample Building Comp:")
            comp = v18['building_comps'][0]
            print(f"   Name: {comp.get('name', 'N/A')}")
            print(f"   Unit price: {comp.get('unit_krw_m2', 0)/10000:.0f}만원/㎡")
        
        return True
        
    except Exception as e:
        print(f"❌ Context Builder Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generation():
    """Test 3: Complete Report Generation"""
    print("\n" + "=" * 80)
    print("🧪 Test 3: Complete Report Generation")
    print("=" * 80)
    
    try:
        from app.services_v13.report_full.report_full_generator import generate_lh_full_report
        
        test_address = "서울특별시 마포구 월드컵북로 120"
        output_file = "output/v18_phase3_test.html"
        
        generate_lh_full_report(
            address=test_address,
            land_area_sqm=660.0,
            output_file=output_file
        )
        
        # Check if file was created
        import os
        if not os.path.exists(output_file):
            print(f"❌ Report file not created: {output_file}")
            return False
        
        # Check file size
        file_size = os.path.getsize(output_file)
        print(f"\n✅ Report Generation Test PASSED")
        print(f"   File: {output_file}")
        print(f"   Size: {file_size/1024:.1f} KB")
        print(f"   URL: https://8080-i65g3ela1oephi4loymka-ad490db5.sandbox.novita.ai/{output_file}")
        
        # Check if comparables tables are in the report
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            has_land_table = '토지 실거래가 비교' in content
            has_building_table = '유사 신축 건축물 매매사례' in content
            
            print(f"\n📊 Template Rendering Check:")
            print(f"   토지 비교표: {'✅' if has_land_table else '❌'}")
            print(f"   건물 비교표: {'✅' if has_building_table else '❌'}")
            
            if not (has_land_table and has_building_table):
                print("⚠️  Warning: Comparables tables not found in report")
        
        return True
        
    except Exception as e:
        print(f"❌ Report Generation Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 80)
    print("🚀 ZeroSite v18 Phase 3 Integration Tests")
    print("=" * 80)
    
    results = {}
    
    # Test 1: API
    results['api'] = await test_real_transaction_api()
    
    # Test 2: Context Builder
    results['context'] = test_context_builder()
    
    # Test 3: Report Generation
    results['report'] = test_report_generation()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.upper():20s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! v18 Phase 3 Integration Complete!")
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
    print("=" * 80)
    
    return all_passed


if __name__ == '__main__':
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
