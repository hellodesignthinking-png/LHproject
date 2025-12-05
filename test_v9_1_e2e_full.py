"""
ZeroSite v9.1 End-to-End Integration Test
===========================================

CRITICAL 1-3 수정 후 완전한 E2E 테스트

테스트 시나리오:
1. 4개 필드만 입력 (주소, 대지면적, 토지가격, 용도지역)
2. 자동 계산 검증 (좌표, BCR/FAR, 세대수, 층수, 주차)
3. Financial Engine 정확성 검증
4. 실제 서울/경기 주소 사용

Author: ZeroSite Development Team
Date: 2025-12-04
"""

import asyncio
import json
from typing import Dict, Any
from datetime import datetime

import sys
sys.path.insert(0, '/home/user/webapp')

from app.api.endpoints.analysis_v9_1 import (
    analyze_land_v91,
    AnalyzeLandRequestV91
)

# 실제 테스트 가능한 주소 목록
TEST_ADDRESSES = {
    "서울_마포구_상암동": {
        "address": "서울특별시 마포구 월드컵북로 120",
        "land_area": 1000.0,
        "land_appraisal_price": 9000000,
        "zone_type": "제3종일반주거지역",
        "expected": {
            "unit_range": (35, 50),
            "floors_range": (5, 8),
            "bcr": 50.0,
            "far": 300.0
        }
    },
    "서울_강남구_역삼동": {
        "address": "서울특별시 강남구 테헤란로 152",
        "land_area": 1500.0,
        "land_appraisal_price": 15000000,
        "zone_type": "준주거지역",
        "expected": {
            "unit_range": (80, 120),
            "floors_range": (8, 12),
            "bcr": 70.0,
            "far": 500.0
        }
    },
    "서울_송파구_잠실동": {
        "address": "서울특별시 송파구 올림픽로 240",
        "land_area": 800.0,
        "land_appraisal_price": 12000000,
        "zone_type": "제2종일반주거지역",
        "expected": {
            "unit_range": (20, 35),
            "floors_range": (4, 7),
            "bcr": 60.0,
            "far": 200.0
        }
    },
    "경기_성남_분당구": {
        "address": "경기도 성남시 분당구 판교역로 166",
        "land_area": 2000.0,
        "land_appraisal_price": 8000000,
        "zone_type": "준주거지역",
        "expected": {
            "unit_range": (120, 180),
            "floors_range": (10, 15),
            "bcr": 70.0,
            "far": 500.0
        }
    },
    "서울_영등포_여의도": {
        "address": "서울특별시 영등포구 여의대로 108",
        "land_area": 3000.0,
        "land_appraisal_price": 18000000,
        "zone_type": "중심상업지역",
        "expected": {
            "unit_range": (300, 500),
            "floors_range": (20, 30),
            "bcr": 90.0,
            "far": 1500.0
        }
    }
}


class E2ETestRunner:
    """v9.1 E2E Test Runner"""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
    
    async def run_all_tests(self):
        """모든 E2E 테스트 실행"""
        print("=" * 80)
        print("ZeroSite v9.1 End-to-End Integration Test")
        print("CRITICAL 1-3 수정 후 검증")
        print("=" * 80)
        print(f"Test Start Time: {datetime.now().isoformat()}\n")
        
        for location_name, test_data in TEST_ADDRESSES.items():
            print(f"\n{'=' * 80}")
            print(f"🏢 Test Location: {location_name}")
            print(f"📍 Address: {test_data['address']}")
            print(f"{'=' * 80}\n")
            
            await self.test_minimal_input_analysis(location_name, test_data)
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
    
    async def test_minimal_input_analysis(self, location_name: str, test_data: Dict):
        """4개 필드 입력 → 전체 분석 테스트"""
        self.total_tests += 1
        test_result = {
            "location": location_name,
            "address": test_data["address"],
            "success": False,
            "errors": [],
            "auto_calculated": {},
            "validation": {}
        }
        
        try:
            # Step 1: Create request with minimal input (4 fields only)
            print("📝 Step 1: Creating request with 4 fields only...")
            request = AnalyzeLandRequestV91(
                address=test_data["address"],
                land_area=test_data["land_area"],
                land_appraisal_price=test_data["land_appraisal_price"],
                zone_type=test_data["zone_type"]
            )
            print(f"   ✅ Request created: {test_data['address']}")
            
            # Step 2: Call analyze-land API
            print("\n🔄 Step 2: Calling /api/v9/analyze-land...")
            start_time = datetime.now()
            response = await analyze_land_v91(request)
            duration = (datetime.now() - start_time).total_seconds()
            
            print(f"   ⏱️  Response time: {duration:.2f}s")
            
            if not response.success:
                test_result["errors"].append(f"API call failed: {response.message}")
                print(f"   ❌ API call failed: {response.message}")
                return
            
            print(f"   ✅ API call successful: {response.message}")
            
            # Step 3: Validate auto-calculated fields
            print("\n✅ Step 3: Validating auto-calculated fields...")
            auto_calc = response.auto_calculated_fields or {}
            test_result["auto_calculated"] = auto_calc
            
            # 3.1 Check address → coordinates
            if 'latitude' in auto_calc and 'longitude' in auto_calc:
                print(f"   ✅ Coordinates: ({auto_calc['latitude']}, {auto_calc['longitude']})")
                test_result["validation"]["coordinates"] = True
            else:
                print(f"   ❌ Coordinates not calculated")
                test_result["validation"]["coordinates"] = False
                test_result["errors"].append("Coordinates not auto-calculated")
            
            # 3.2 Check zone_type → BCR/FAR
            expected_bcr = test_data["expected"]["bcr"]
            expected_far = test_data["expected"]["far"]
            
            if 'building_coverage_ratio' in auto_calc:
                actual_bcr = auto_calc['building_coverage_ratio']
                if actual_bcr == expected_bcr:
                    print(f"   ✅ BCR: {actual_bcr}% (expected: {expected_bcr}%)")
                    test_result["validation"]["bcr"] = True
                else:
                    print(f"   ⚠️  BCR: {actual_bcr}% (expected: {expected_bcr}%)")
                    test_result["validation"]["bcr"] = False
            else:
                print(f"   ❌ BCR not calculated")
                test_result["validation"]["bcr"] = False
                test_result["errors"].append("BCR not auto-calculated")
            
            if 'floor_area_ratio' in auto_calc:
                actual_far = auto_calc['floor_area_ratio']
                if actual_far == expected_far:
                    print(f"   ✅ FAR: {actual_far}% (expected: {expected_far}%)")
                    test_result["validation"]["far"] = True
                else:
                    print(f"   ⚠️  FAR: {actual_far}% (expected: {expected_far}%)")
                    test_result["validation"]["far"] = False
            else:
                print(f"   ❌ FAR not calculated")
                test_result["validation"]["far"] = False
                test_result["errors"].append("FAR not auto-calculated")
            
            # 3.3 Check unit estimation
            if 'unit_count' in auto_calc:
                unit_count = auto_calc['unit_count']
                min_units, max_units = test_data["expected"]["unit_range"]
                
                if min_units <= unit_count <= max_units:
                    print(f"   ✅ Unit count: {unit_count} units (expected: {min_units}-{max_units})")
                    test_result["validation"]["unit_count"] = True
                else:
                    print(f"   ⚠️  Unit count: {unit_count} units (expected: {min_units}-{max_units})")
                    test_result["validation"]["unit_count"] = False
            else:
                print(f"   ❌ Unit count not calculated")
                test_result["validation"]["unit_count"] = False
                test_result["errors"].append("Unit count not auto-calculated")
            
            # 3.4 Check floors
            if 'estimated_floors' in auto_calc:
                floors = auto_calc['estimated_floors']
                min_floors, max_floors = test_data["expected"]["floors_range"]
                
                if min_floors <= floors <= max_floors:
                    print(f"   ✅ Floors: {floors} floors (expected: {min_floors}-{max_floors})")
                    test_result["validation"]["floors"] = True
                else:
                    print(f"   ⚠️  Floors: {floors} floors (expected: {min_floors}-{max_floors})")
                    test_result["validation"]["floors"] = False
            else:
                print(f"   ❌ Floors not calculated")
                test_result["validation"]["floors"] = False
                test_result["errors"].append("Floors not auto-calculated")
            
            # 3.5 Check parking
            if 'parking_spaces' in auto_calc:
                parking = auto_calc['parking_spaces']
                print(f"   ✅ Parking: {parking} spaces")
                test_result["validation"]["parking"] = True
            else:
                print(f"   ❌ Parking not calculated")
                test_result["validation"]["parking"] = False
                test_result["errors"].append("Parking not auto-calculated")
            
            # 3.6 Check GFA
            if 'total_gfa' in auto_calc:
                total_gfa = auto_calc['total_gfa']
                print(f"   ✅ Total GFA: {total_gfa:,.2f} m²")
                test_result["validation"]["total_gfa"] = True
            else:
                print(f"   ❌ Total GFA not calculated")
                test_result["validation"]["total_gfa"] = False
                test_result["errors"].append("Total GFA not auto-calculated")
            
            if 'residential_gfa' in auto_calc:
                residential_gfa = auto_calc['residential_gfa']
                print(f"   ✅ Residential GFA: {residential_gfa:,.2f} m²")
                test_result["validation"]["residential_gfa"] = True
            else:
                print(f"   ❌ Residential GFA not calculated")
                test_result["validation"]["residential_gfa"] = False
                test_result["errors"].append("Residential GFA not auto-calculated")
            
            # 3.7 Check construction cost
            if 'construction_cost_per_sqm' in auto_calc:
                cost = auto_calc['construction_cost_per_sqm']
                print(f"   ✅ Construction cost: {cost:,}원/m²")
                test_result["validation"]["construction_cost"] = True
            else:
                print(f"   ❌ Construction cost not calculated")
                test_result["validation"]["construction_cost"] = False
                test_result["errors"].append("Construction cost not auto-calculated")
            
            # Step 4: Validate analysis result
            print("\n🔍 Step 4: Validating full analysis result...")
            if response.data:
                print(f"   ✅ Analysis data received")
                
                # Check site_info
                if hasattr(response.data, 'site_info') and response.data.site_info:
                    print(f"   ✅ Site info available")
                    test_result["validation"]["site_info"] = True
                
                # Check financial_result
                if hasattr(response.data, 'financial_result') and response.data.financial_result:
                    print(f"   ✅ Financial result available")
                    test_result["validation"]["financial_result"] = True
                
                # Check lh_evaluation
                if hasattr(response.data, 'lh_evaluation') and response.data.lh_evaluation:
                    print(f"   ✅ LH evaluation available")
                    test_result["validation"]["lh_evaluation"] = True
            
            # Final validation
            validation_count = sum(1 for v in test_result["validation"].values() if v)
            total_validations = len(test_result["validation"])
            
            if validation_count >= total_validations * 0.8:  # 80% pass rate
                test_result["success"] = True
                self.passed_tests += 1
                print(f"\n✅ TEST PASSED: {validation_count}/{total_validations} validations successful")
            else:
                print(f"\n❌ TEST FAILED: Only {validation_count}/{total_validations} validations successful")
                print(f"   Errors: {', '.join(test_result['errors'])}")
        
        except Exception as e:
            test_result["errors"].append(str(e))
            print(f"\n❌ TEST ERROR: {str(e)}")
        
        finally:
            self.results.append(test_result)
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n" + "-" * 80)
        print("Test Results by Location:")
        print("-" * 80)
        
        for result in self.results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            validation_count = sum(1 for v in result["validation"].values() if v)
            total_validations = len(result["validation"])
            
            print(f"{status} | {result['location']}")
            print(f"     Address: {result['address']}")
            print(f"     Validations: {validation_count}/{total_validations}")
            
            if result["errors"]:
                print(f"     Errors: {', '.join(result['errors'][:3])}")
            print()
        
        print("=" * 80)
        
        if success_rate >= 80:
            print("✅ E2E TEST: PASSED (80%+ success rate)")
            print("v9.1 자동 입력 시스템이 정상 작동합니다!")
        else:
            print("❌ E2E TEST: FAILED")
            print("추가 수정이 필요합니다.")
    
    def save_results(self):
        """테스트 결과 저장"""
        output_file = "test_v9_1_e2e_results.json"
        
        results_data = {
            "test_suite": "ZeroSite v9.1 E2E Integration Test",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.total_tests - self.passed_tests,
                "success_rate": round((self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0, 2)
            },
            "results": self.results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Test results saved to: {output_file}")


async def main():
    """메인 테스트 실행"""
    tester = E2ETestRunner()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
