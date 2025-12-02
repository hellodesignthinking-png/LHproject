#!/usr/bin/env python3
"""
ZeroSite v8.1 - POI Integration Test
====================================

Tests comprehensive POI integration in v7.5 FINAL report generation.
"""

import asyncio
import sys
from app.services.poi_integration_v8_1 import POIIntegrationV81
from app.schemas import Coordinates


async def test_poi_integration():
    """Test POI Integration v8.1"""
    
    print("="*80)
    print("🧪 ZeroSite v8.1 - POI Integration Test")
    print("="*80)
    
    # Test coordinates (Seoul Gangnam-gu Yeoksam-dong)
    test_coords = Coordinates(latitude=37.5006, longitude=127.0366)
    test_address = "서울특별시 강남구 역삼동 123-45"
    
    print(f"\n📍 Test Location:")
    print(f"   Address: {test_address}")
    print(f"   Coordinates: ({test_coords.latitude:.6f}, {test_coords.longitude:.6f})")
    
    # Initialize POI Integration Service
    print("\n🔧 Initializing POI Integration Service...")
    poi_service = POIIntegrationV81()
    
    # Run comprehensive POI analysis
    print("\n🚀 Running Comprehensive POI Analysis...")
    try:
        result = await poi_service.analyze_comprehensive_poi(test_coords, test_address)
        
        print("\n" + "="*80)
        print("📊 POI Analysis Results")
        print("="*80)
        
        # Category scores
        print(f"\n🎓 Education Infrastructure: {result.education_score:.1f}/100")
        print(f"   - Elementary Schools: {result.elementary_schools.count} facilities")
        print(f"     Nearest: {result.elementary_schools.nearest_distance:.0f}m")
        print(f"   - Middle Schools: {result.middle_schools.count} facilities")
        print(f"     Nearest: {result.middle_schools.nearest_distance:.0f}m")
        print(f"   - High Schools: {result.high_schools.count} facilities")
        print(f"     Nearest: {result.high_schools.nearest_distance:.0f}m")
        
        print(f"\n🚇 Transportation Infrastructure: {result.transportation_score:.1f}/100")
        print(f"   - Subway Stations: {result.subway_stations.count} facilities")
        print(f"     Nearest: {result.subway_stations.nearest_distance:.0f}m")
        print(f"   - Bus Stops: {result.bus_stops.count} facilities")
        print(f"     Nearest: {result.bus_stops.nearest_distance:.0f}m")
        
        print(f"\n🏥 Healthcare Infrastructure: {result.healthcare_score:.1f}/100")
        print(f"   - Hospitals: {result.hospitals.count} facilities")
        print(f"     Nearest: {result.hospitals.nearest_distance:.0f}m")
        print(f"   - Clinics: {result.clinics.count} facilities")
        print(f"     Nearest: {result.clinics.nearest_distance:.0f}m")
        
        print(f"\n🛒 Commercial Infrastructure: {result.commercial_score:.1f}/100")
        print(f"   - Supermarkets: {result.supermarkets.count} facilities")
        print(f"     Nearest: {result.supermarkets.nearest_distance:.0f}m")
        print(f"   - Convenience Stores: {result.convenience_stores.count} facilities")
        print(f"     Nearest: {result.convenience_stores.nearest_distance:.0f}m")
        
        print(f"\n🎭 Cultural Infrastructure: {result.cultural_score:.1f}/100")
        print(f"   - Parks: {result.parks.count} facilities")
        print(f"     Nearest: {result.parks.nearest_distance:.0f}m")
        print(f"   - Libraries: {result.libraries.count} facilities")
        print(f"     Nearest: {result.libraries.nearest_distance:.0f}m")
        
        # Overall assessment
        print(f"\n" + "="*80)
        print(f"🎯 Overall Infrastructure Score: {result.overall_infrastructure_score:.1f}/100")
        print(f"📊 Livability Grade: {result.livability_grade}")
        print("="*80)
        
        # Strengths
        print(f"\n✅ Strengths ({len(result.strengths)}):")
        for i, strength in enumerate(result.strengths, 1):
            print(f"   {i}. {strength}")
        
        # Weaknesses
        print(f"\n⚠️  Weaknesses ({len(result.weaknesses)}):")
        for i, weakness in enumerate(result.weaknesses, 1):
            print(f"   {i}. {weakness}")
        
        # Recommendations
        print(f"\n💡 Recommendations ({len(result.recommendations)}):")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Test success criteria
        print("\n" + "="*80)
        print("✅ Test Success Criteria:")
        print("="*80)
        
        tests_passed = []
        tests_failed = []
        
        # Test 1: Overall score should be calculated
        if 0 <= result.overall_infrastructure_score <= 100:
            tests_passed.append("✓ Overall infrastructure score is valid (0-100)")
        else:
            tests_failed.append("✗ Overall infrastructure score is invalid")
        
        # Test 2: Grade should be assigned
        if result.livability_grade in ['A+', 'A', 'B+', 'B', 'C', 'D', 'F']:
            tests_passed.append("✓ Livability grade is valid")
        else:
            tests_failed.append("✗ Livability grade is invalid")
        
        # Test 3: All category scores should be valid
        category_scores = [
            result.education_score,
            result.transportation_score,
            result.healthcare_score,
            result.commercial_score,
            result.cultural_score
        ]
        if all(0 <= score <= 100 for score in category_scores):
            tests_passed.append("✓ All category scores are valid (0-100)")
        else:
            tests_failed.append("✗ Some category scores are invalid")
        
        # Test 4: At least some facilities should be found
        total_facilities = sum([
            result.elementary_schools.count,
            result.subway_stations.count,
            result.hospitals.count,
            result.supermarkets.count,
            result.parks.count
        ])
        if total_facilities > 0:
            tests_passed.append(f"✓ Facilities found: {total_facilities} total")
        else:
            tests_failed.append("✗ No facilities found")
        
        # Test 5: Analysis should provide insights
        if result.strengths or result.weaknesses or result.recommendations:
            tests_passed.append("✓ SWOT analysis generated")
        else:
            tests_failed.append("✗ No SWOT analysis")
        
        # Print results
        for test in tests_passed:
            print(f"   {test}")
        for test in tests_failed:
            print(f"   {test}")
        
        print("\n" + "="*80)
        if not tests_failed:
            print("🎉 ALL TESTS PASSED!")
            print("="*80)
            return 0
        else:
            print(f"❌ {len(tests_failed)} TEST(S) FAILED")
            print("="*80)
            return 1
    
    except Exception as e:
        print(f"\n❌ Test failed with error:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main test runner"""
    result = asyncio.run(test_poi_integration())
    sys.exit(result)


if __name__ == "__main__":
    main()
