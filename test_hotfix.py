#!/usr/bin/env python3
"""
HOTFIX Verification Test Script
Tests for Bug 1 (transport_score.py) and Bug 2 (demand_prediction.py)
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.transport_score import get_transport_score
from app.services.demand_prediction import MunicipalDemandPredictor


def test_transport_score():
    """Bug 1 - 버스 점수 미반영 문제 테스트"""
    print("=" * 60)
    print("🔧 BUG 1 FIX TEST: Transport Score (Bus Not Reflecting)")
    print("=" * 60)
    
    test_cases = [
        # (subway_distance, bus_distance, expected_score, description)
        (None, 10, 3.5, "지하철 없음, 버스 10m → 3.5점"),
        (0, 10, 3.5, "지하철 0m, 버스 10m → 3.5점"),
        ("0", 10, 3.5, "지하철 '0' (문자열), 버스 10m → 3.5점"),
        ("", 20, 3.5, "지하철 '' (빈문자열), 버스 20m → 3.5점"),
        (0.0, 30, 3.5, "지하철 0.0, 버스 30m → 3.5점"),
        (450, 20, 5.0, "지하철 450m, 버스 20m → 5.0점 (지하철 우선)"),
        (1200, 20, 3.5, "지하철 1200m, 버스 20m → 3.5점 (버스 fallback)"),
        (1500, 80, 2.0, "지하철 1500m, 버스 80m → 2.0점 (버스 근접)"),
        (2000, 150, 0.0, "지하철 2000m, 버스 150m → 0.0점 (접근 불량)"),
    ]
    
    print("\n📋 테스트 케이스 실행:")
    print("-" * 60)
    
    all_passed = True
    for subway_dist, bus_dist, expected_score, description in test_cases:
        score, grade, details = get_transport_score(subway_dist, bus_dist)
        passed = abs(score - expected_score) < 0.01
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {description}")
        print(f"   입력: subway={subway_dist}, bus={bus_dist}")
        print(f"   결과: score={score:.1f}, grade={grade}, mode={details['mode']}")
        print(f"   기대: {expected_score:.1f}")
        
        if not passed:
            all_passed = False
            print(f"   ❌ ERROR: Expected {expected_score}, got {score}")
        
        print()
    
    print("-" * 60)
    if all_passed:
        print("✅ BUG 1 FIX: ALL TESTS PASSED!")
    else:
        print("❌ BUG 1 FIX: SOME TESTS FAILED!")
    print()
    
    return all_passed


def test_household_type_weighting():
    """Bug 2 - 세대유형 가중치 미적용 문제 테스트"""
    print("=" * 60)
    print("🔧 BUG 2 FIX TEST: Household Type Weighting")
    print("=" * 60)
    
    predictor = MunicipalDemandPredictor()
    
    # 테스트 케이스 1: 대학 800m 근처 → 청년형 가중치 +20%
    print("\n📋 테스트 케이스 1: 대학 800m 근처")
    print("-" * 60)
    
    result1 = predictor.predict(
        subway_distance=600,
        university_distance=1500,
        youth_ratio=28,
        avg_rent_price=45,
        existing_rental_units=50,
        target_units=50,
        unit_type="청년",
        nearby_facilities={
            "university": 800,  # 대학 800m → 청년형 +20%
            "elementary_school": 1200,
            "middle_school": 1500,
            "hospital": 2000,
            "senior_welfare": 3000
        }
    )
    
    print(f"기본 demand_score: {result1.demand_score}")
    print(f"세대유형별 점수:")
    for household_type, score in result1.household_type_scores.items():
        print(f"  - {household_type}: {score}")
    
    # 청년형 점수가 다른 유형보다 높아야 함 (대학 800m 때문에)
    청년_score = result1.household_type_scores["청년"]
    신혼_score = result1.household_type_scores["신혼"]
    고령자_score = result1.household_type_scores["고령자"]
    
    test1_passed = 청년_score > 신혼_score and 청년_score > 고령자_score
    status1 = "✅ PASS" if test1_passed else "❌ FAIL"
    print(f"\n{status1} | 청년 점수({청년_score}) > 신혼({신혼_score}), 고령자({고령자_score})")
    
    # 가중치 비율 확인 (1.20배 적용 여부)
    expected_ratio = 1.20
    actual_ratio = 청년_score / 신혼_score if 신혼_score > 0 else 0
    ratio_check = abs(actual_ratio - expected_ratio) < 0.05
    print(f"청년/신혼 비율: {actual_ratio:.3f} (기대: {expected_ratio:.2f}) {'✅' if ratio_check else '❌'}")
    
    # 테스트 케이스 2: 초등학교 600m 근처 → 신혼형 가중치 +15%
    print("\n📋 테스트 케이스 2: 초등학교 600m 근처")
    print("-" * 60)
    
    result2 = predictor.predict(
        subway_distance=700,
        university_distance=2000,
        youth_ratio=25,
        avg_rent_price=42,
        existing_rental_units=60,
        target_units=50,
        unit_type="신혼·신생아 I",
        nearby_facilities={
            "university": 2500,
            "elementary_school": 600,  # 초등학교 600m → 신혼형 +15%
            "middle_school": 700,
            "hospital": 1800,
            "senior_welfare": 2500
        }
    )
    
    print(f"기본 demand_score: {result2.demand_score}")
    print(f"세대유형별 점수:")
    for household_type, score in result2.household_type_scores.items():
        print(f"  - {household_type}: {score}")
    
    청년_score2 = result2.household_type_scores["청년"]
    신혼_score2 = result2.household_type_scores["신혼"]
    고령자_score2 = result2.household_type_scores["고령자"]
    
    test2_passed = 신혼_score2 > 청년_score2 and 신혼_score2 > 고령자_score2
    status2 = "✅ PASS" if test2_passed else "❌ FAIL"
    print(f"\n{status2} | 신혼 점수({신혼_score2}) > 청년({청년_score2}), 고령자({고령자_score2})")
    
    # 가중치 비율 확인 (1.15배 적용 여부)
    expected_ratio2 = 1.15
    actual_ratio2 = 신혼_score2 / 청년_score2 if 청년_score2 > 0 else 0
    ratio_check2 = abs(actual_ratio2 - expected_ratio2) < 0.05
    print(f"신혼/청년 비율: {actual_ratio2:.3f} (기대: {expected_ratio2:.2f}) {'✅' if ratio_check2 else '❌'}")
    
    # 테스트 케이스 3: 대형병원 1000m 근처 → 고령자형 가중치 +25%
    print("\n📋 테스트 케이스 3: 대형병원 1000m 근처")
    print("-" * 60)
    
    result3 = predictor.predict(
        subway_distance=650,
        university_distance=2500,
        youth_ratio=22,
        avg_rent_price=40,
        existing_rental_units=70,
        target_units=50,
        unit_type="고령자",
        nearby_facilities={
            "university": 3000,
            "elementary_school": 1500,
            "middle_school": 1600,
            "hospital": 1000,  # 대형병원 1000m → 고령자형 +25%
            "senior_welfare": 800
        }
    )
    
    print(f"기본 demand_score: {result3.demand_score}")
    print(f"세대유형별 점수:")
    for household_type, score in result3.household_type_scores.items():
        print(f"  - {household_type}: {score}")
    
    청년_score3 = result3.household_type_scores["청년"]
    신혼_score3 = result3.household_type_scores["신혼"]
    고령자_score3 = result3.household_type_scores["고령자"]
    
    test3_passed = 고령자_score3 > 청년_score3 and 고령자_score3 > 신혼_score3
    status3 = "✅ PASS" if test3_passed else "❌ FAIL"
    print(f"\n{status3} | 고령자 점수({고령자_score3}) > 청년({청년_score3}), 신혼({신혼_score3})")
    
    # 가중치 비율 확인 (1.25배 적용 여부)
    expected_ratio3 = 1.25
    actual_ratio3 = 고령자_score3 / 청년_score3 if 청년_score3 > 0 else 0
    ratio_check3 = abs(actual_ratio3 - expected_ratio3) < 0.05
    print(f"고령자/청년 비율: {actual_ratio3:.3f} (기대: {expected_ratio3:.2f}) {'✅' if ratio_check3 else '❌'}")
    
    print("\n" + "-" * 60)
    all_passed = test1_passed and test2_passed and test3_passed
    if all_passed:
        print("✅ BUG 2 FIX: ALL TESTS PASSED!")
    else:
        print("❌ BUG 2 FIX: SOME TESTS FAILED!")
    print()
    
    return all_passed


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 60)
    print("🚨 LH Land Diagnosis System V2.0 - HOTFIX VERIFICATION")
    print("=" * 60)
    print()
    
    # Bug 1 테스트
    bug1_passed = test_transport_score()
    
    # Bug 2 테스트
    bug2_passed = test_household_type_weighting()
    
    # 종합 결과
    print("=" * 60)
    print("📊 HOTFIX VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Bug 1 (Transport Score): {'✅ FIXED' if bug1_passed else '❌ FAILED'}")
    print(f"Bug 2 (Household Weighting): {'✅ FIXED' if bug2_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if bug1_passed and bug2_passed:
        print("\n🎉 ALL HOTFIXES VERIFIED SUCCESSFULLY!")
        return 0
    else:
        print("\n❌ SOME HOTFIXES FAILED - REVIEW REQUIRED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
