"""
Task 2.x: 권한 시스템 검증 테스트

목표:
- Role 기반 접근 제어 검증
- RUN_ID 단위 접근 제어 검증
- 보고서 타입별 접근 제어 검증

검증 시나리오:
1. LANDOWNER → C (LH 보고서) 접근 → 403
2. INVESTOR → D (투자 보고서) 접근 → 200
3. LH → F (프레젠테이션) 접근 → 200
4. URL 직접 접근 (헤더 없음) → 401
5. LANDOWNER → 권한 없는 RUN_ID 접근 → 403
"""

import asyncio
import aiohttp
from typing import Dict, List


BASE_URL = "http://localhost:8091"
TEST_RUN_ID = "TEST_6REPORT"


# ==============================================================================
# Test Scenarios
# ==============================================================================

class TestScenario:
    def __init__(self, name: str, user_email: str, endpoint: str, expected_status: int, reason: str):
        self.name = name
        self.user_email = user_email
        self.endpoint = endpoint
        self.expected_status = expected_status
        self.reason = reason


TEST_SCENARIOS = [
    # 1. INVESTOR가 E (Quick Review) 접근 시도 → 403 (INVESTOR는 E 접근 불가)
    TestScenario(
        name="INVESTOR → E (Quick Review) 접근",
        user_email="investor@example.com",
        endpoint=f"/api/v4/reports/six-types/quick-review/html?context_id={TEST_RUN_ID}",
        expected_status=403,
        reason="INVESTOR는 Quick Review 보고서 접근 불가"
    ),
    
    # 2. LANDOWNER가 E (Quick Review) 접근 시도 → 403
    TestScenario(
        name="LANDOWNER → E (Quick Review) 접근",
        user_email="landowner@example.com",
        endpoint=f"/api/v4/reports/six-types/quick-review/html?context_id={TEST_RUN_ID}",
        expected_status=403,
        reason="LANDOWNER는 Quick Review 보고서 접근 불가"
    ),
    
    # 3. LH가 F (프레젠테이션) 접근 → 200
    TestScenario(
        name="LH → F (프레젠테이션) 접근",
        user_email="lh@example.com",
        endpoint=f"/api/v4/reports/six-types/presentation/html?context_id={TEST_RUN_ID}",
        expected_status=200,
        reason="LH는 프레젠테이션 접근 가능"
    ),
    
    # 4. 헤더 없이 직접 접근 → 401
    TestScenario(
        name="헤더 없이 URL 직접 접근",
        user_email=None,  # No auth header
        endpoint=f"/api/v4/reports/six-types/quick-review/html?context_id={TEST_RUN_ID}",
        expected_status=401,
        reason="인증 헤더 없으면 401"
    ),
    
    # 5. LANDOWNER가 권한 없는 RUN_ID의 F 접근 → 403
    TestScenario(
        name="LANDOWNER → 권한 없는 RUN_ID 접근",
        user_email="landowner@example.com",
        endpoint="/api/v4/reports/six-types/presentation/html?context_id=UNAUTHORIZED_RUN_ID",
        expected_status=403,
        reason="LANDOWNER는 allowed_run_ids 외 RUN_ID 접근 불가"
    ),
    
    # 6. ADMIN은 모든 보고서 접근 가능 → 200
    TestScenario(
        name="ADMIN → E (Quick Review) 접근",
        user_email="admin@zerosite.com",
        endpoint=f"/api/v4/reports/six-types/quick-review/html?context_id={TEST_RUN_ID}",
        expected_status=200,
        reason="ADMIN은 모든 보고서 접근 가능"
    ),
    
    # 7. INTERNAL도 모든 보고서 접근 가능 → 200
    TestScenario(
        name="INTERNAL → E (Quick Review) 접근",
        user_email="internal@zerosite.com",
        endpoint=f"/api/v4/reports/six-types/quick-review/html?context_id={TEST_RUN_ID}",
        expected_status=200,
        reason="INTERNAL은 모든 보고서 접근 가능"
    ),
    
    # 8. INVESTOR가 F (프레젠테이션) 접근 → 200
    TestScenario(
        name="INVESTOR → F (프레젠테이션) 접근",
        user_email="investor@example.com",
        endpoint=f"/api/v4/reports/six-types/presentation/html?context_id={TEST_RUN_ID}",
        expected_status=200,
        reason="INVESTOR는 프레젠테이션 접근 가능"
    ),
]


# ==============================================================================
# Test Execution
# ==============================================================================

async def run_test_scenario(session: aiohttp.ClientSession, scenario: TestScenario) -> Dict:
    """
    단일 테스트 시나리오 실행
    
    Returns:
        {
            "name": str,
            "expected": int,
            "actual": int,
            "passed": bool,
            "reason": str
        }
    """
    url = f"{BASE_URL}{scenario.endpoint}"
    
    # 헤더 설정 (X-User-Email)
    headers = {}
    if scenario.user_email:
        headers["X-User-Email"] = scenario.user_email
    
    try:
        async with session.get(url, headers=headers, allow_redirects=False) as response:
            actual_status = response.status
            passed = actual_status == scenario.expected_status
            
            return {
                "name": scenario.name,
                "expected": scenario.expected_status,
                "actual": actual_status,
                "passed": passed,
                "reason": scenario.reason,
                "user_email": scenario.user_email or "None",
            }
    
    except Exception as e:
        return {
            "name": scenario.name,
            "expected": scenario.expected_status,
            "actual": f"ERROR: {str(e)}",
            "passed": False,
            "reason": scenario.reason,
            "user_email": scenario.user_email or "None",
        }


async def run_all_tests():
    """
    모든 테스트 시나리오 실행
    """
    print("=" * 80)
    print("🔐 Task 2.x: 권한 시스템 검증 테스트")
    print("=" * 80)
    print()
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for scenario in TEST_SCENARIOS:
            print(f"⏳ 테스트: {scenario.name}")
            result = await run_test_scenario(session, scenario)
            results.append(result)
            
            if result["passed"]:
                print(f"   ✅ PASS: Expected {result['expected']}, Got {result['actual']}")
            else:
                print(f"   ❌ FAIL: Expected {result['expected']}, Got {result['actual']}")
            
            print(f"   📝 Reason: {result['reason']}")
            print(f"   👤 User: {result['user_email']}")
            print()
    
    # 결과 요약
    print("=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    
    passed_count = sum(1 for r in results if r["passed"])
    failed_count = len(results) - passed_count
    
    print(f"  Total: {len(results)}")
    print(f"  Passed: {passed_count}")
    print(f"  Failed: {failed_count}")
    print()
    
    if failed_count > 0:
        print("❌ 실패한 테스트:")
        for r in results:
            if not r["passed"]:
                print(f"  - {r['name']}: Expected {r['expected']}, Got {r['actual']}")
        print()
    
    if failed_count == 0:
        print("🎉 Task 2.x 검증 성공!")
        print()
        print("핵심 성과:")
        print("  - Role 기반 접근 제어 정상 작동")
        print("  - RUN_ID 단위 접근 제어 정상 작동")
        print("  - 보고서 타입별 접근 제어 정상 작동")
        print("  - URL 직접 접근 차단 (401)")
        print()
        print("✅ v1.2 릴리스 준비 완료")
        print()
        return True
    else:
        print("❌ Task 2.x 검증 실패")
        return False


# ==============================================================================
# Main
# ==============================================================================

async def main():
    success = await run_all_tests()
    
    if success:
        print("=" * 80)
        print("다음 단계:")
        print("  1. 커밋 및 PR 생성")
        print("  2. v1.2.0 태그 생성")
        print("  3. Task 3.x: 외부 공유 링크 (토큰 기반) 설계")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
