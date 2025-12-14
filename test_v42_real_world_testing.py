#!/usr/bin/env python3
"""
ZeroSite v41: Real-World Testing Suite
======================================

목적: 실제 주소로 10+ 테스트 실행 및 LH 실제 결정과 비교

테스트 계획:
1. 10개 실제 주소 (서울/경기 다양한 지역)
2. 각 주소에 대해 ZeroSite 분석 실행
3. LH AI Judge 예측 점수 기록
4. (추후) 실제 LH 결정과 비교
5. Accuracy Report 생성

Date: 2025-12-14
Version: v41.0
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import sys

# Server Configuration
BASE_URL = "http://localhost:8001"
API_V40_2 = f"{BASE_URL}/api/v40.2"
API_LH_REVIEW = f"{BASE_URL}/api/v40/lh-review"

# Test Cases: 10+ Real Addresses
REAL_WORLD_TEST_CASES = [
    {
        "id": "TC001",
        "name": "서울 강남구 역삼동 (상업·업무 밀집지)",
        "address": "서울특별시 강남구 역삼동 123-45",
        "land_area_pyeong": 300,
        "land_area_sqm": 991.74,
        "zoning": "제3종일반주거지역",
        "official_land_price_per_sqm": 5000000,
        "expected_lh_score_range": (80, 90),  # 예상 점수 범위
        "expected_risk": "LOW",
        "notes": "역세권, 업무지구 중심, 높은 지가"
    },
    {
        "id": "TC002",
        "name": "서울 관악구 봉천동 (주거지역)",
        "address": "서울특별시 관악구 봉천동 234-56",
        "land_area_pyeong": 250,
        "land_area_sqm": 826.45,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 3200000,
        "expected_lh_score_range": (70, 80),
        "expected_risk": "MEDIUM",
        "notes": "대학가 인접, 중간 지가"
    },
    {
        "id": "TC003",
        "name": "서울 송파구 잠실동 (대규모 주거단지)",
        "address": "서울특별시 송파구 잠실동 345-67",
        "land_area_pyeong": 400,
        "land_area_sqm": 1322.32,
        "zoning": "제3종일반주거지역",
        "official_land_price_per_sqm": 4500000,
        "expected_lh_score_range": (75, 85),
        "expected_risk": "LOW",
        "notes": "잠실 올림픽파크 인근, 교통 좋음"
    },
    {
        "id": "TC004",
        "name": "경기 성남시 분당구 정자동 (신도시)",
        "address": "경기도 성남시 분당구 정자동 456-78",
        "land_area_pyeong": 350,
        "land_area_sqm": 1157.03,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 3800000,
        "expected_lh_score_range": (75, 85),
        "expected_risk": "LOW",
        "notes": "분당 신도시, 계획도시, 교통·교육 우수"
    },
    {
        "id": "TC005",
        "name": "경기 수원시 장안구 조원동 (일반 주거)",
        "address": "경기도 수원시 장안구 조원동 567-89",
        "land_area_pyeong": 280,
        "land_area_sqm": 925.62,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 2800000,
        "expected_lh_score_range": (65, 75),
        "expected_risk": "MEDIUM",
        "notes": "경기 지역, 중간 지가"
    },
    {
        "id": "TC006",
        "name": "서울 마포구 상암동 (DMC 단지)",
        "address": "서울특별시 마포구 상암동 678-90",
        "land_area_pyeong": 320,
        "land_area_sqm": 1057.9,
        "zoning": "준주거지역",
        "official_land_price_per_sqm": 4200000,
        "expected_lh_score_range": (75, 85),
        "expected_risk": "LOW",
        "notes": "DMC 디지털미디어시티, 준주거지역"
    },
    {
        "id": "TC007",
        "name": "서울 영등포구 당산동 (주상복합 가능)",
        "address": "서울특별시 영등포구 당산동 789-01",
        "land_area_pyeong": 380,
        "land_area_sqm": 1256.2,
        "zoning": "준주거지역",
        "official_land_price_per_sqm": 3900000,
        "expected_lh_score_range": (70, 80),
        "expected_risk": "MEDIUM",
        "notes": "영등포 중심, 지하철 2·9호선"
    },
    {
        "id": "TC008",
        "name": "경기 고양시 일산동구 백석동 (신도시)",
        "address": "경기도 고양시 일산동구 백석동 890-12",
        "land_area_pyeong": 300,
        "land_area_sqm": 991.74,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 3200000,
        "expected_lh_score_range": (70, 80),
        "expected_risk": "MEDIUM",
        "notes": "일산 신도시, 교육·교통 양호"
    },
    {
        "id": "TC009",
        "name": "서울 노원구 상계동 (대단지 주거)",
        "address": "서울특별시 노원구 상계동 901-23",
        "land_area_pyeong": 260,
        "land_area_sqm": 859.5,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 2900000,
        "expected_lh_score_range": (65, 75),
        "expected_risk": "MEDIUM",
        "notes": "노원구, 지하철 4·7호선"
    },
    {
        "id": "TC010",
        "name": "경기 화성시 동탄동 (신도시)",
        "address": "경기도 화성시 동탄2동 012-34",
        "land_area_pyeong": 350,
        "land_area_sqm": 1157.03,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 2600000,
        "expected_lh_score_range": (60, 75),
        "expected_risk": "MEDIUM",
        "notes": "동탄2 신도시, 개발 중"
    },
    {
        "id": "TC011",
        "name": "서울 강서구 화곡동 (서울 서부)",
        "address": "서울특별시 강서구 화곡동 123-45",
        "land_area_pyeong": 280,
        "land_area_sqm": 925.62,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 3100000,
        "expected_lh_score_range": (65, 75),
        "expected_risk": "MEDIUM",
        "notes": "강서구, 공항철도 인근"
    },
    {
        "id": "TC012",
        "name": "경기 용인시 수지구 동천동 (신도시)",
        "address": "경기도 용인시 수지구 동천동 234-56",
        "land_area_pyeong": 320,
        "land_area_sqm": 1057.9,
        "zoning": "제2종일반주거지역",
        "official_land_price_per_sqm": 3400000,
        "expected_lh_score_range": (70, 80),
        "expected_risk": "MEDIUM",
        "notes": "수지구, 교육 우수, 분당 인접"
    }
]


class RealWorldTestRunner:
    """Real-World Test Runner for ZeroSite v41"""
    
    def __init__(self):
        self.results = []
        self.start_time = datetime.now()
        
    def check_server_health(self) -> bool:
        """서버 헬스체크"""
        try:
            response = requests.get(f"{API_V40_2}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ Server Healthy: {health.get('name', 'ZeroSite')} v{health.get('version', 'unknown')}")
                return True
            else:
                print(f"❌ Server Health Check Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Server Connection Failed: {e}")
            return False
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """단일 테스트 실행"""
        print(f"\n{'='*60}")
        print(f"Test Case: {test_case['id']} - {test_case['name']}")
        print(f"{'='*60}")
        
        result = {
            "test_case_id": test_case["id"],
            "name": test_case["name"],
            "address": test_case["address"],
            "land_area_sqm": test_case["land_area_sqm"],
            "zoning": test_case["zoning"],
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING",
            "error": None
        }
        
        try:
            # Step 1: Create Analysis Context
            print(f"\n[Step 1] Creating analysis context...")
            analysis_payload = {
                "address": test_case["address"],
                "land_area_pyeong": test_case["land_area_pyeong"],
                "land_area_sqm": test_case["land_area_sqm"],
                "zoning": test_case["zoning"],
                "official_land_price_per_sqm": test_case["official_land_price_per_sqm"]
            }
            
            response = requests.post(
                f"{API_V40_2}/run-analysis",
                json=analysis_payload,
                timeout=30
            )
            
            if response.status_code != 200:
                result["status"] = "FAILED"
                result["error"] = f"Analysis failed: {response.status_code}"
                print(f"❌ Analysis Failed: {response.status_code}")
                return result
            
            analysis_data = response.json()
            context_id = analysis_data.get("context_id")
            result["context_id"] = context_id
            
            print(f"✅ Context Created: {context_id}")
            
            # Step 2: Get Appraisal Data
            print(f"\n[Step 2] Retrieving appraisal data...")
            appraisal_response = requests.get(
                f"{API_V40_2}/context/{context_id}/appraisal",
                timeout=10
            )
            
            if appraisal_response.status_code == 200:
                appraisal_data = appraisal_response.json()
                result["appraisal"] = {
                    "final_value": appraisal_data.get("final_value", 0),
                    "value_per_sqm": appraisal_data.get("value_per_sqm", 0),
                    "confidence_level": appraisal_data.get("confidence_level", "unknown")
                }
                print(f"✅ Appraisal: {result['appraisal']['final_value']:,.0f}원 (㎡당 {result['appraisal']['value_per_sqm']:,.0f}원)")
            
            # Step 3: Run LH Review (AI Judge)
            print(f"\n[Step 3] Running LH AI Judge prediction...")
            lh_review_payload = {
                "context_id": context_id,
                "housing_type": "청년",
                "target_units": 50
            }
            
            lh_review_response = requests.post(
                f"{API_LH_REVIEW}/predict",
                json=lh_review_payload,
                timeout=15
            )
            
            if lh_review_response.status_code != 200:
                result["status"] = "FAILED"
                result["error"] = f"LH Review failed: {lh_review_response.status_code}"
                print(f"❌ LH Review Failed: {lh_review_response.status_code}")
                return result
            
            lh_review_data = lh_review_response.json()
            result["lh_review"] = {
                "predicted_score": lh_review_data.get("predicted_score", 0),
                "pass_probability": lh_review_data.get("pass_probability", 0),
                "risk_level": lh_review_data.get("risk_level", "UNKNOWN"),
                "factors": lh_review_data.get("factors", [])
            }
            
            print(f"✅ LH Score: {result['lh_review']['predicted_score']:.1f}/100")
            print(f"   Pass Probability: {result['lh_review']['pass_probability']:.1f}%")
            print(f"   Risk Level: {result['lh_review']['risk_level']}")
            
            # Step 4: Compare with Expected Range
            expected_range = test_case["expected_lh_score_range"]
            actual_score = result["lh_review"]["predicted_score"]
            
            if expected_range[0] <= actual_score <= expected_range[1]:
                result["prediction_accuracy"] = "WITHIN_RANGE"
                print(f"✅ Score within expected range: {expected_range}")
            else:
                result["prediction_accuracy"] = "OUT_OF_RANGE"
                print(f"⚠️ Score outside expected range: {expected_range} (actual: {actual_score:.1f})")
            
            result["status"] = "SUCCESS"
            
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            print(f"❌ Error: {e}")
        
        return result
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """모든 테스트 실행"""
        print("\n" + "="*60)
        print("ZeroSite v41: Real-World Testing Suite")
        print("="*60)
        print(f"Total Test Cases: {len(REAL_WORLD_TEST_CASES)}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check server health first
        if not self.check_server_health():
            print("\n❌ Server is not healthy. Aborting tests.")
            return []
        
        # Run each test
        for i, test_case in enumerate(REAL_WORLD_TEST_CASES, 1):
            print(f"\n\n{'#'*60}")
            print(f"Test {i}/{len(REAL_WORLD_TEST_CASES)}")
            print(f"{'#'*60}")
            
            result = self.run_single_test(test_case)
            self.results.append(result)
            
            # Sleep between tests to avoid overwhelming server
            if i < len(REAL_WORLD_TEST_CASES):
                time.sleep(2)
        
        return self.results
    
    def generate_summary_report(self) -> str:
        """테스트 결과 요약 리포트 생성"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # Count results
        total = len(self.results)
        success = sum(1 for r in self.results if r["status"] == "SUCCESS")
        failed = sum(1 for r in self.results if r["status"] == "FAILED")
        error = sum(1 for r in self.results if r["status"] == "ERROR")
        
        within_range = sum(1 for r in self.results if r.get("prediction_accuracy") == "WITHIN_RANGE")
        out_of_range = sum(1 for r in self.results if r.get("prediction_accuracy") == "OUT_OF_RANGE")
        
        # Calculate statistics
        lh_scores = [r["lh_review"]["predicted_score"] for r in self.results if r.get("lh_review")]
        avg_score = sum(lh_scores) / len(lh_scores) if lh_scores else 0
        min_score = min(lh_scores) if lh_scores else 0
        max_score = max(lh_scores) if lh_scores else 0
        
        report = f"""
{'='*80}
ZeroSite v41: Real-World Testing - Summary Report
{'='*80}

📅 Test Period:
   Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
   End:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}
   Duration: {duration:.1f} seconds

📊 Test Results:
   Total Test Cases: {total}
   ✅ Success: {success}
   ❌ Failed: {failed}
   ⚠️ Error: {error}
   Success Rate: {(success/total*100) if total > 0 else 0:.1f}%

🎯 Prediction Accuracy:
   Within Expected Range: {within_range}/{success} ({(within_range/success*100) if success > 0 else 0:.1f}%)
   Out of Range: {out_of_range}/{success}

📈 LH Score Statistics:
   Average Score: {avg_score:.1f}/100
   Min Score: {min_score:.1f}/100
   Max Score: {max_score:.1f}/100

{'='*80}

📋 Detailed Results:
"""
        
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            accuracy_icon = "🎯" if result.get("prediction_accuracy") == "WITHIN_RANGE" else "⚠️"
            
            report += f"\n{i}. {status_icon} {result['name']}\n"
            report += f"   ID: {result['test_case_id']}\n"
            report += f"   Address: {result['address']}\n"
            
            if result.get("lh_review"):
                lh = result["lh_review"]
                report += f"   {accuracy_icon} LH Score: {lh['predicted_score']:.1f}/100\n"
                report += f"   Pass Probability: {lh['pass_probability']:.1f}%\n"
                report += f"   Risk Level: {lh['risk_level']}\n"
            
            if result.get("error"):
                report += f"   ⚠️ Error: {result['error']}\n"
            
            report += "\n"
        
        report += f"{'='*80}\n"
        
        return report
    
    def save_results(self, filename: str = "v41_real_world_test_results.json"):
        """결과를 JSON 파일로 저장"""
        output = {
            "test_suite": "ZeroSite v41 Real-World Testing",
            "version": "v41.0",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "success": sum(1 for r in self.results if r["status"] == "SUCCESS"),
                "failed": sum(1 for r in self.results if r["status"] == "FAILED"),
                "error": sum(1 for r in self.results if r["status"] == "ERROR")
            },
            "results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to: {filename}")


def main():
    """Main entry point"""
    runner = RealWorldTestRunner()
    
    try:
        # Run all tests
        results = runner.run_all_tests()
        
        if not results:
            print("\n❌ No tests were executed. Exiting.")
            sys.exit(1)
        
        # Generate and print summary report
        summary = runner.generate_summary_report()
        print(summary)
        
        # Save results to JSON
        runner.save_results()
        
        # Determine exit code
        success_count = sum(1 for r in results if r["status"] == "SUCCESS")
        total_count = len(results)
        
        if success_count == total_count:
            print(f"\n✅ All tests passed! ({success_count}/{total_count})")
            sys.exit(0)
        elif success_count > 0:
            print(f"\n⚠️ Some tests failed. ({success_count}/{total_count} passed)")
            sys.exit(1)
        else:
            print(f"\n❌ All tests failed. ({success_count}/{total_count})")
            sys.exit(2)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
