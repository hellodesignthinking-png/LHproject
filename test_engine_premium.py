"""
Direct test of AppraisalEngine with Premium Factors
"""

from app.engines.appraisal_engine_v241 import AppraisalEngineV241
import json

# Create engine
engine = AppraisalEngineV241()

# Test data
input_data = {
    'address': '서울시 마포구 월드컵북로 120',
    'land_area_sqm': 660,
    'zone_type': '제3종일반주거지역',
    'individual_land_price_per_sqm': 7000000,
    'premium_factors': {
        'land_shape': 15,
        'subway_distance': 30,
        'school_district_8': 25,
        'redevelopment_status': 60,
        'gtx_station': 50
    }
}

print("Testing AppraisalEngine with Premium Factors...")
print("=" * 60)

try:
    result = engine.process(input_data)
    
    print("✅ Engine processing successful!")
    print(f"\n최종 평가액: {result['final_appraisal_value']:.2f} 억원")
    print(f"㎡당 가격: {result['final_value_per_sqm']:,} 원")
    
    if 'premium_info' in result:
        premium = result['premium_info']
        print(f"\nPremium Info Found: {premium['has_premium']}")
        
        if premium['has_premium']:
            print(f"  기본 평가액: {premium['base_value']:.2f} 억원")
            print(f"  프리미엄: {premium['premium_percentage']:+.1f}%")
            print(f"  조정 평가액: {premium['adjusted_value']:.2f} 억원")
            
            print(f"\n  상위 5개 요인:")
            for i, factor in enumerate(premium['top_5_factors'], 1):
                print(f"    {i}. {factor['name']}: {factor['value']:+.1f}%")
    else:
        print("\n⚠️ premium_info not found in result")
        
    print("\n✅ TEST PASSED")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
