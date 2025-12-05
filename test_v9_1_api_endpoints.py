"""
ZeroSite v9.1 API Endpoints Test Suite
========================================

Tests for Phase 3: API Integration - New v9.1 Endpoints

Test Coverage:
1. POST /api/v9/resolve-address - Address resolution
2. POST /api/v9/estimate-units - Unit count estimation
3. GET /api/v9/zoning-standards/{zone_type} - Zoning standards lookup
4. POST /api/v9/analyze-land - Enhanced minimal input analysis
5. GET /api/v9/health - Health check

Author: ZeroSite Development Team
Date: 2025-12-04
Version: 9.1.0
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime

# Import v9.1 API functions
import sys
sys.path.insert(0, '/home/user/webapp')

from app.api.endpoints.analysis_v9_1 import (
    resolve_address,
    estimate_units,
    get_zoning_standards,
    analyze_land_v91,
    health_check,
    ResolveAddressRequest,
    EstimateUnitsRequest,
    AnalyzeLandRequestV91
)

# Test configuration
PRINT_DETAIL = True
SAVE_RESULTS = True


class TestResult:
    """Test result container"""
    def __init__(self, test_name: str, endpoint: str):
        self.test_name = test_name
        self.endpoint = endpoint
        self.success = False
        self.message = ""
        self.duration_ms = 0
        self.response_data = None
        self.error = None


class V91APIEndpointTester:
    """v9.1 API Endpoints Test Runner"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.total_tests = 0
        self.passed_tests = 0
    
    async def run_all_tests(self):
        """Run all test suites"""
        print("=" * 80)
        print("ZeroSite v9.1 API Endpoints - Integration Test Suite")
        print("=" * 80)
        print(f"Test Start Time: {datetime.now().isoformat()}")
        print("")
        
        # Test Suite 1: Address Resolution API
        print("\n" + "=" * 80)
        print("Test Suite 1: POST /api/v9/resolve-address")
        print("=" * 80)
        await self.test_resolve_address()
        
        # Test Suite 2: Unit Estimation API
        print("\n" + "=" * 80)
        print("Test Suite 2: POST /api/v9/estimate-units")
        print("=" * 80)
        await self.test_estimate_units()
        
        # Test Suite 3: Zoning Standards API
        print("\n" + "=" * 80)
        print("Test Suite 3: GET /api/v9/zoning-standards/{zone_type}")
        print("=" * 80)
        await self.test_zoning_standards()
        
        # Test Suite 4: Enhanced Land Analysis API
        print("\n" + "=" * 80)
        print("Test Suite 4: POST /api/v9/analyze-land (v9.1 Minimal Input)")
        print("=" * 80)
        await self.test_analyze_land_v91()
        
        # Test Suite 5: Health Check API
        print("\n" + "=" * 80)
        print("Test Suite 5: GET /api/v9/health")
        print("=" * 80)
        await self.test_health_check()
        
        # Print summary
        self.print_summary()
        
        # Save results
        if SAVE_RESULTS:
            self.save_results()
    
    async def test_resolve_address(self):
        """Test address resolution endpoint"""
        test_cases = [
            {
                "name": "서울 마포구 주소 해석",
                "request": ResolveAddressRequest(
                    address="서울특별시 마포구 월드컵북로 120"
                ),
                "expected_contains": ["latitude", "longitude", "road_address"]
            },
            {
                "name": "강남구 역삼동 지번 주소",
                "request": ResolveAddressRequest(
                    address="서울특별시 강남구 역삼동 123-45"
                ),
                "expected_contains": ["latitude", "longitude"]
            },
            {
                "name": "경기도 성남시 주소",
                "request": ResolveAddressRequest(
                    address="경기도 성남시 분당구 판교역로 166"
                ),
                "expected_contains": ["latitude", "longitude", "legal_code"]
            }
        ]
        
        for tc in test_cases:
            result = TestResult(tc["name"], "POST /api/v9/resolve-address")
            self.total_tests += 1
            
            try:
                start_time = datetime.now()
                response = await resolve_address(tc["request"])
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                result.duration_ms = round(duration, 2)
                
                if response.success and response.data:
                    # Check expected fields
                    has_all_fields = all(
                        field in response.data 
                        for field in tc["expected_contains"]
                    )
                    
                    if has_all_fields:
                        result.success = True
                        result.message = f"✓ 주소 해석 성공: {response.data.get('road_address', 'N/A')}"
                        result.response_data = response.data
                        self.passed_tests += 1
                    else:
                        result.message = f"✗ 필수 필드 누락: {tc['expected_contains']}"
                else:
                    result.message = f"✗ API 응답 실패: {response.message}"
                
            except Exception as e:
                result.message = f"✗ 예외 발생: {str(e)}"
                result.error = str(e)
            
            self.results.append(result)
            self.print_test_result(result)
    
    async def test_estimate_units(self):
        """Test unit estimation endpoint"""
        test_cases = [
            {
                "name": "소규모 주거지역 (500㎡)",
                "request": EstimateUnitsRequest(
                    land_area=500.0,
                    zone_type="제2종일반주거지역",
                    building_coverage_ratio=60.0,
                    floor_area_ratio=200.0
                ),
                "expected_range": {"units": (10, 25)}
            },
            {
                "name": "중규모 주거지역 (1000㎡)",
                "request": EstimateUnitsRequest(
                    land_area=1000.0,
                    zone_type="제3종일반주거지역"
                ),
                "expected_range": {"units": (35, 50)}
            },
            {
                "name": "대규모 준주거지역 (2000㎡)",
                "request": EstimateUnitsRequest(
                    land_area=2000.0,
                    zone_type="준주거지역"
                ),
                "expected_range": {"units": (80, 120)}
            }
        ]
        
        for tc in test_cases:
            result = TestResult(tc["name"], "POST /api/v9/estimate-units")
            self.total_tests += 1
            
            try:
                start_time = datetime.now()
                response = await estimate_units(tc["request"])
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                result.duration_ms = round(duration, 2)
                
                if response.success and response.data:
                    units = response.data.get("estimated_units", 0)
                    expected_min, expected_max = tc["expected_range"]["units"]
                    
                    if expected_min <= units <= expected_max:
                        result.success = True
                        result.message = (
                            f"✓ 세대수 추정 성공: {units}세대 "
                            f"(층수: {response.data.get('estimated_floors')}층, "
                            f"주차: {response.data.get('parking_spaces')}면)"
                        )
                        result.response_data = response.data
                        self.passed_tests += 1
                    else:
                        result.message = (
                            f"✗ 세대수 범위 초과: {units}세대 "
                            f"(예상: {expected_min}-{expected_max})"
                        )
                else:
                    result.message = f"✗ API 응답 실패: {response.message}"
                
            except Exception as e:
                result.message = f"✗ 예외 발생: {str(e)}"
                result.error = str(e)
            
            self.results.append(result)
            self.print_test_result(result)
    
    async def test_zoning_standards(self):
        """Test zoning standards lookup endpoint"""
        test_cases = [
            {
                "name": "제3종일반주거지역",
                "zone_type": "제3종일반주거지역",
                "expected": {
                    "building_coverage_ratio": 50.0,
                    "floor_area_ratio": 300.0
                }
            },
            {
                "name": "준주거지역",
                "zone_type": "준주거지역",
                "expected": {
                    "building_coverage_ratio": 70.0,
                    "floor_area_ratio": 500.0
                }
            },
            {
                "name": "중심상업지역",
                "zone_type": "중심상업지역",
                "expected": {
                    "building_coverage_ratio": 90.0,
                    "floor_area_ratio": 1500.0
                }
            }
        ]
        
        for tc in test_cases:
            result = TestResult(tc["name"], "GET /api/v9/zoning-standards/{zone_type}")
            self.total_tests += 1
            
            try:
                start_time = datetime.now()
                response = await get_zoning_standards(tc["zone_type"])
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                result.duration_ms = round(duration, 2)
                
                if response.success and response.data:
                    bcr = response.data.get("building_coverage_ratio")
                    far = response.data.get("floor_area_ratio")
                    
                    if (bcr == tc["expected"]["building_coverage_ratio"] and
                        far == tc["expected"]["floor_area_ratio"]):
                        result.success = True
                        result.message = (
                            f"✓ 용도지역 기준 조회 성공: "
                            f"건폐율 {bcr}%, 용적률 {far}%"
                        )
                        result.response_data = response.data
                        self.passed_tests += 1
                    else:
                        result.message = (
                            f"✗ 기준 불일치: BCR {bcr}% (예상: {tc['expected']['building_coverage_ratio']}%), "
                            f"FAR {far}% (예상: {tc['expected']['floor_area_ratio']}%)"
                        )
                else:
                    result.message = f"✗ API 응답 실패: {response.message}"
                
            except Exception as e:
                result.message = f"✗ 예외 발생: {str(e)}"
                result.error = str(e)
            
            self.results.append(result)
            self.print_test_result(result)
    
    async def test_analyze_land_v91(self):
        """Test v9.1 enhanced land analysis endpoint (minimal input)"""
        test_cases = [
            {
                "name": "v9.1 최소 입력 (4개 필드)",
                "request": AnalyzeLandRequestV91(
                    address="서울특별시 마포구 월드컵북로 120",
                    land_area=1000.0,
                    land_appraisal_price=9000000,
                    zone_type="제3종일반주거지역"
                ),
                "expected_auto_calc": ["latitude", "longitude", "building_coverage_ratio", "floor_area_ratio", "unit_count"]
            },
            {
                "name": "v9.1 준주거지역 분석",
                "request": AnalyzeLandRequestV91(
                    address="서울특별시 강남구 역삼동 123-45",
                    land_area=1500.0,
                    land_appraisal_price=12000000,
                    zone_type="준주거지역"
                ),
                "expected_auto_calc": ["latitude", "longitude", "unit_count"]
            }
        ]
        
        for tc in test_cases:
            result = TestResult(tc["name"], "POST /api/v9/analyze-land")
            self.total_tests += 1
            
            try:
                start_time = datetime.now()
                response = await analyze_land_v91(tc["request"])
                duration = (datetime.now() - start_time).total_seconds() * 1000
                
                result.duration_ms = round(duration, 2)
                
                if response.success:
                    auto_calc = response.auto_calculated_fields or {}
                    
                    # Check if expected fields were auto-calculated
                    has_auto_calc = all(
                        field in auto_calc 
                        for field in tc["expected_auto_calc"]
                    )
                    
                    if has_auto_calc:
                        result.success = True
                        result.message = (
                            f"✓ v9.1 토지 분석 성공: "
                            f"{len(auto_calc)}개 필드 자동 계산 "
                            f"(세대수: {auto_calc.get('unit_count', 'N/A')})"
                        )
                        result.response_data = {
                            "auto_calculated_count": len(auto_calc),
                            "auto_calculated_fields": auto_calc
                        }
                        self.passed_tests += 1
                    else:
                        result.message = f"✗ 자동 계산 필드 부족: {tc['expected_auto_calc']}"
                else:
                    result.message = f"✗ API 응답 실패: {response.message}"
                
            except Exception as e:
                result.message = f"✗ 예외 발생: {str(e)}"
                result.error = str(e)
            
            self.results.append(result)
            self.print_test_result(result)
    
    async def test_health_check(self):
        """Test health check endpoint"""
        result = TestResult("API 상태 확인", "GET /api/v9/health")
        self.total_tests += 1
        
        try:
            start_time = datetime.now()
            response = await health_check()
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            result.duration_ms = round(duration, 2)
            
            if response.get("status") == "healthy":
                result.success = True
                result.message = f"✓ API 정상 작동: v{response.get('version', 'N/A')}"
                result.response_data = response
                self.passed_tests += 1
            else:
                result.message = f"✗ API 상태 이상: {response}"
            
        except Exception as e:
            result.message = f"✗ 예외 발생: {str(e)}"
            result.error = str(e)
        
        self.results.append(result)
        self.print_test_result(result)
    
    def print_test_result(self, result: TestResult):
        """Print individual test result"""
        status_icon = "✓" if result.success else "✗"
        status_text = "PASS" if result.success else "FAIL"
        
        print(f"\n[{status_icon}] {result.test_name}")
        print(f"    Endpoint: {result.endpoint}")
        print(f"    Status: {status_text}")
        print(f"    Duration: {result.duration_ms}ms")
        print(f"    {result.message}")
        
        if PRINT_DETAIL and result.response_data:
            print(f"    Response Data:")
            for key, value in result.response_data.items():
                print(f"      - {key}: {value}")
    
    def print_summary(self):
        """Print test summary"""
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("")
        
        # Group by endpoint
        endpoint_stats = {}
        for result in self.results:
            if result.endpoint not in endpoint_stats:
                endpoint_stats[result.endpoint] = {"total": 0, "passed": 0}
            endpoint_stats[result.endpoint]["total"] += 1
            if result.success:
                endpoint_stats[result.endpoint]["passed"] += 1
        
        print("Endpoint-wise Results:")
        print("-" * 80)
        for endpoint, stats in endpoint_stats.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"{endpoint}")
            print(f"  {stats['passed']}/{stats['total']} tests passed ({rate:.1f}%)")
        
        print("=" * 80)
        
        # Overall status
        if success_rate >= 90:
            print("✓ v9.1 API Integration Test: EXCELLENT")
        elif success_rate >= 70:
            print("⚠ v9.1 API Integration Test: GOOD (Some issues)")
        else:
            print("✗ v9.1 API Integration Test: NEEDS ATTENTION")
    
    def save_results(self):
        """Save test results to JSON file"""
        output_file = "test_v9_1_api_results.json"
        
        results_data = {
            "test_suite": "ZeroSite v9.1 API Endpoints",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.total_tests - self.passed_tests,
                "success_rate": round((self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0, 2)
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "endpoint": r.endpoint,
                    "success": r.success,
                    "message": r.message,
                    "duration_ms": r.duration_ms,
                    "response_data": r.response_data,
                    "error": r.error
                }
                for r in self.results
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Test results saved to: {output_file}")


async def main():
    """Main test runner"""
    tester = V91APIEndpointTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
