"""
Test Land Diagnosis Fallback Engine
"""
import sys
sys.path.insert(0, '/home/user/webapp')

from app.services.land_diagnosis_fallback_engine import get_fallback_engine
import logging

logging.basicConfig(level=logging.INFO)

print("="*80)
print("🧪 Land Diagnosis Fallback Engine 테스트")
print("="*80)

# Test cases with missing/invalid data
test_cases = [
    {
        "name": "완전히 비어있는 입력",
        "input": {}
    },
    {
        "name": "주소만 있는 경우",
        "input": {
            "address": "서울시 강남구 역삼동"
        }
    },
    {
        "name": "음수/0 값들",
        "input": {
            "address": "서울 마포구",
            "land_area_sqm": 0,
            "bcr": -10,
            "far": 0,
            "individual_land_price_per_sqm": -1000
        }
    },
    {
        "name": "정상 입력 (Fallback 불필요)",
        "input": {
            "address": "서울시 송파구 잠실동 123",
            "land_area_sqm": 660,
            "zone_type": "제2종일반주거지역",
            "bcr": 60,
            "far": 200,
            "individual_land_price_per_sqm": 12000000
        }
    }
]

engine = get_fallback_engine()

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"테스트 {i}: {test_case['name']}")
    print(f"{'='*80}")
    
    print(f"\n📥 입력 데이터:")
    for key, value in test_case['input'].items():
        print(f"   {key}: {value}")
    
    # Apply fallback
    fixed = engine.validate_and_fix_input(test_case['input'])
    
    print(f"\n✅ 복구된 데이터:")
    for key, value in fixed.items():
        print(f"   {key}: {value}")
    
    # Show fallback log
    summary = engine.generate_fallback_summary()
    
    if summary['fallback_used']:
        print(f"\n🔄 Fallback 적용 내역 ({summary['fallback_count']}건):")
        for detail in summary['fallback_details']:
            print(f"   - {detail['field']}: {detail['original']} → {detail['fallback']}")
    else:
        print(f"\n✅ Fallback 불필요 (모든 데이터 정상)")

print(f"\n{'='*80}")
print("🧪 Zero Division 보호 테스트")
print(f"{'='*80}")

# Test safe_divide
test_divisions = [
    (100, 0, "100 / 0"),
    (50, 2, "50 / 2"),
    (0, 0, "0 / 0"),
    (None, 10, "None / 10"),
    (100, None, "100 / None")
]

for num, denom, description in test_divisions:
    result = engine.safe_divide(num or 0, denom or 0, default=-1)
    print(f"   {description} = {result}")

print(f"\n{'='*80}")
print("🧪 Fallback 거래사례 생성 테스트")
print(f"{'='*80}")

sales = engine.generate_fallback_comparable_sales(
    address="서울시 강남구 역삼동",
    land_area_sqm=660,
    zone_type="제2종일반주거지역",
    count=5
)

print(f"\n생성된 거래사례: {len(sales)}건")
for i, sale in enumerate(sales, 1):
    print(f"\n{i}. {sale['location']}")
    print(f"   면적: {sale['land_area_sqm']:,}㎡")
    print(f"   단가: {sale['price_per_sqm']:,}원/㎡")
    print(f"   총액: {sale['total_price']/100000000:.2f}억원")
    print(f"   거리: {sale['distance_km']}km")

print(f"\n{'='*80}")
print("✅ 모든 테스트 완료")
print(f"{'='*80}")
