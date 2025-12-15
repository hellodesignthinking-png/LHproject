"""
ZeroSite v9.1 REAL Version Test
================================

실제로 작동하는 v9.1 REAL 버전 테스트

Author: ZeroSite Development Team  
Date: 2025-12-05
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_real_version():
    """v9.1 REAL 버전 테스트"""
    print("="*80)
    print("🧪 ZeroSite v9.1 REAL Version Test")
    print("="*80)
    
    # Import after path setup
    from app.api.endpoints.analysis_v9_1_REAL import analyze_land_real, AnalyzeLandRequestReal
    
    # Test data
    test_request = AnalyzeLandRequestReal(
        address="서울특별시 마포구 월드컵북로 120",
        land_area=1000.0,
        land_appraisal_price=9000000,
        zone_type="제3종일반주거지역"
    )
    
    print("\n📥 Test Input (4 fields):")
    print(f"   - Address: {test_request.address}")
    print(f"   - Land Area: {test_request.land_area} m²")
    print(f"   - Appraisal Price: {test_request.land_appraisal_price:,} KRW/m²")
    print(f"   - Zone Type: {test_request.zone_type}")
    
    print("\n🚀 Starting analysis...")
    
    try:
        # Run analysis
        response = await analyze_land_real(test_request)
        
        # Check if response is dict or Pydantic model
        if hasattr(response, 'dict'):
            response_dict = response.dict()
        else:
            response_dict = response
        
        print("\n✅ Analysis Complete!")
        print(f"\n📊 Auto-Calculated Fields ({len([k for k, v in response_dict.get('auto_calculated', {}).items() if v is not None])} fields):")
        
        auto_calc = response_dict.get('auto_calculated', {})
        
        # Group by source
        print("\n   📍 Address Resolution:")
        print(f"      - Latitude: {auto_calc.get('latitude')}")
        print(f"      - Longitude: {auto_calc.get('longitude')}")
        print(f"      - Legal Code: {auto_calc.get('legal_code')}")
        
        print("\n   🏗️ Building Standards:")
        print(f"      - Building Coverage Ratio: {auto_calc.get('building_coverage_ratio')}%")
        print(f"      - Floor Area Ratio: {auto_calc.get('floor_area_ratio')}%")
        print(f"      - Max Height: {auto_calc.get('max_height') if auto_calc.get('max_height') else 'No limit'}")
        
        print("\n   🏘️ Unit Estimation:")
        print(f"      - Unit Count: {auto_calc.get('unit_count')} units")
        print(f"      - Floors: {auto_calc.get('floors')} floors")
        print(f"      - Parking Spaces: {auto_calc.get('parking_spaces')} spaces")
        print(f"      - Total GFA: {auto_calc.get('total_gfa'):,.0f} m²")
        print(f"      - Residential GFA: {auto_calc.get('residential_gfa'):,.0f} m²")
        
        print("\n   💰 Cost Estimation:")
        print(f"      - Construction Cost/m²: {auto_calc.get('construction_cost_per_sqm'):,} KRW")
        print(f"      - Total Land Cost: {auto_calc.get('total_land_cost'):,.0f} KRW")
        print(f"      - Total Construction Cost: {auto_calc.get('total_construction_cost'):,.0f} KRW")
        
        # Analysis result
        analysis = response_dict.get('analysis_result', {})
        if analysis:
            lh_scores = analysis.get('lh_scores', {})
            print("\n   🎯 Analysis Results:")
            print(f"      - LH Score: {lh_scores.get('total_score', 'N/A')}")
            
            # Handle grade (could be enum or dict)
            grade = lh_scores.get('grade', 'N/A')
            if hasattr(grade, 'value'):
                grade_str = grade.value
            elif isinstance(grade, dict):
                grade_str = grade.get('value', str(grade))
            else:
                grade_str = str(grade)
            print(f"      - LH Grade: {grade_str}")
            
            risk = analysis.get('risk_assessment', {})
            print(f"      - Risk Level: {risk.get('overall_risk_level', 'N/A')}")
            
            recommendation = analysis.get('final_recommendation', {})
            decision = recommendation.get('decision', 'N/A')
            if hasattr(decision, 'value'):
                decision_str = decision.value
            elif isinstance(decision, dict):
                decision_str = decision.get('value', str(decision))
            else:
                decision_str = str(decision)
            print(f"      - Decision: {decision_str}")
            print(f"      - Confidence: {recommendation.get('confidence_level', 'N/A')}%")
        
        print("\n" + "="*80)
        print("✅ TEST PASSED - v9.1 REAL is working!")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_real_version())
    sys.exit(0 if success else 1)
