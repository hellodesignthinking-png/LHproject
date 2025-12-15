"""
Test Regional Appraisal Rate Database
======================================
Verify the appraisal rate database functionality
"""

from app.data.regional_appraisal_rates import (
    get_appraisal_db,
    Region,
    HousingType,
    ProjectScale
)

def main():
    print("\n" + "=" * 80)
    print("Regional Appraisal Rate Database Test")
    print("=" * 80)
    
    db = get_appraisal_db()
    
    # Test 1: Database statistics
    print("\n📊 DATABASE STATISTICS")
    print("-" * 80)
    stats = db.get_statistics()
    print(f"Total Entries: {stats['total_entries']}")
    print(f"Regions Covered: {stats['regions']}")
    print(f"Housing Types: {stats['housing_types']}")
    print(f"Average Land Appraisal Rate: {stats['avg_land_rate']:.1%}")
    print(f"Average Building Acknowledgment Rate: {stats['avg_building_rate']:.1%}")
    print(f"Average Safety Factor: {stats['avg_safety_factor']:.1%}")
    
    # Test 2: Query by region
    print("\n📍 TEST QUERIES BY REGION")
    print("-" * 80)
    
    test_regions = [
        (Region.SEOUL, HousingType.YOUTH, "서울 청년주택"),
        (Region.GYEONGGI, HousingType.GENERAL, "경기 일반주택"),
        (Region.BUSAN, HousingType.YOUTH, "부산 청년주택"),
        (Region.INCHEON, HousingType.GENERAL, "인천 일반주택"),
    ]
    
    for region, housing_type, desc in test_regions:
        rate = db.get_rate(region, housing_type)
        print(f"\n{desc}:")
        print(f"  Land Rate: {rate.land_appraisal_rate:.1%}")
        print(f"  Building Rate: {rate.building_ack_rate:.1%}")
        print(f"  Safety Factor: {rate.safety_factor:.1%}")
        print(f"  Notes: {rate.notes}")
    
    # Test 3: Query by address
    print("\n🏠 TEST QUERIES BY ADDRESS")
    print("-" * 80)
    
    test_addresses = [
        "서울특별시 마포구 월드컵북로 120",
        "경기도 성남시 분당구 정자동 178-1",
        "인천광역시 남동구 구월동 1408",
        "부산광역시 해운대구 센텀2로 25",
        "대전광역시 유성구 대학로 291",
    ]
    
    print(f"\n{'Address':<45} {'Land':<8} {'Building':<10} {'Safety':<8}")
    print("-" * 80)
    
    for address in test_addresses:
        rate = db.get_rate_by_address(address)
        region_name = address.split()[0]
        print(f"{region_name:<45} {rate.land_appraisal_rate:.1%}    {rate.building_ack_rate:.1%}      {rate.safety_factor:.1%}")
    
    # Test 4: Compare regions
    print("\n📈 REGIONAL COMPARISON (General Housing)")
    print("-" * 80)
    
    regions_to_compare = [
        Region.SEOUL,
        Region.GYEONGGI,
        Region.INCHEON,
        Region.BUSAN,
        Region.DAEGU,
        Region.SEJONG,
    ]
    
    print(f"\n{'Region':<20} {'Land Rate':<12} {'Building Rate':<15} {'Combined*':<12}")
    print("-" * 80)
    
    for region in regions_to_compare:
        rate = db.get_rate(region, HousingType.GENERAL)
        combined = rate.land_appraisal_rate * 0.3 + rate.building_ack_rate * 0.7  # Weighted average
        print(f"{region.value:<20} {rate.land_appraisal_rate:.1%}        {rate.building_ack_rate:.1%}           {combined:.1%}")
    
    print("\n*Combined = Land(30%) + Building(70%) weighted average")
    
    # Test 5: Housing type comparison (Seoul)
    print("\n🏘️  HOUSING TYPE COMPARISON (Seoul)")
    print("-" * 80)
    
    housing_types = [HousingType.YOUTH, HousingType.NEWLYWED, HousingType.GENERAL]
    
    print(f"\n{'Housing Type':<20} {'Land Rate':<12} {'Building Rate':<15} {'Notes':<30}")
    print("-" * 80)
    
    for htype in housing_types:
        rate = db.get_rate(Region.SEOUL, htype)
        print(f"{htype.value:<20} {rate.land_appraisal_rate:.1%}        {rate.building_ack_rate:.1%}           {rate.notes[:27]}...")
    
    # Test 6: Sensitivity analysis
    print("\n💡 SENSITIVITY ANALYSIS")
    print("-" * 80)
    
    base_capex = 15_000_000_000  # 150억원
    
    print(f"\nBase CAPEX: {base_capex/1e8:.1f}억원")
    print(f"\n{'Region':<20} {'Land (30%)':<12} {'Building (70%)':<15} {'Final LH Price':<15}")
    print("-" * 80)
    
    for region in [Region.SEOUL, Region.GYEONGGI, Region.BUSAN, Region.DAEGU]:
        rate = db.get_rate(region, HousingType.GENERAL)
        
        land_portion = base_capex * 0.3
        building_portion = base_capex * 0.7
        
        land_appraised = land_portion * rate.land_appraisal_rate
        building_appraised = building_portion * rate.building_ack_rate
        
        subtotal = land_appraised + building_appraised
        final_price = subtotal * rate.safety_factor
        
        print(f"{region.value:<20} {land_appraised/1e8:.1f}억       {building_appraised/1e8:.1f}억          {final_price/1e8:.1f}억")
    
    print("\n" + "=" * 80)
    print("✅ Database Test Complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
