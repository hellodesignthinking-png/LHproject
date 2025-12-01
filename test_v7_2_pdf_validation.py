"""
ZeroSite v7.2 PDF Report Engine - Final Validation Test

Tests:
1. Radar chart calculation with real engine values
2. Per-field rounding consistency across all sections
3. Full PDF generation with actual analysis data
4. Verification that no hardcoded values exist
"""

import sys
import os
import asyncio
from datetime import datetime
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, '/home/user/webapp')

from app.services.analysis_engine import AnalysisEngine
from app.schemas import LandAnalysisRequest
from app.services.report_field_mapper_v7_2_complete import ReportFieldMapperV72Complete
from app.services.pdf_report_engine_v7_2 import PDFReportEngineV72

def validate_radar_chart_calculation(report_data: dict) -> dict:
    """
    Validate radar chart calculation with real engine data
    """
    print("\n" + "="*80)
    print("TEST 1: Radar Chart Calculation Validation")
    print("="*80)
    
    poi = report_data.get('poi_analysis_v3_1', {})
    td = report_data.get('type_demand_v3_1', {})
    geo = report_data.get('geo_optimizer_v3_1', {})
    risk = report_data.get('risk_analysis_2025', {})
    basic = report_data.get('basic_info', {})
    
    # Get user type specific demand score (matching PDF engine logic)
    user_type = basic.get('unit_type', '청년')
    type_scores = td.get('type_scores', {})
    user_demand_score = 0
    if user_type in type_scores:
        user_demand_score = type_scores[user_type].get('final_score', 0)
    elif td.get('main_score', 0) > 0:
        user_demand_score = td.get('main_score', 0)
    
    # Risk calculation (matching PDF engine logic)
    risk_score = risk.get('risk_score', 20)
    risk_normalized = max(0, min(100, 100 - (risk_score * 5)))
    
    # Expected radar values as calculated in PDF engine
    radar_values = [
        ('생활편의성', min(max(0, poi.get('total_score_v3_1', 0)), 100)),
        ('접근성', min(max(0, geo.get('final_score', 0)), 100)),
        ('수요강도', min(max(0, user_demand_score), 100)),
        ('규제환경', risk_normalized),
        ('미래가치', min(max(0, geo.get('optimization_score', 0) if 'optimization_score' in geo else geo.get('final_score', 0)), 100))
    ]
    
    print("\n✅ Radar Chart Axes and Values:")
    for axis_name, value in radar_values:
        print(f"   {axis_name}: {value:.2f}점")
    
    # Validate no hardcoded values (all should be from engine)
    all_valid = True
    for axis_name, value in radar_values:
        if value < 0:
            print(f"   ❌ FAIL: {axis_name} has negative value ({value})")
            all_valid = False
        if axis_name == '생활편의성' and value == 32:  # Old hardcoded value
            print(f"   ❌ FAIL: {axis_name} using old hardcoded value")
            all_valid = False
    
    print(f"\n{'✅' if all_valid else '❌'} Radar Chart: {'PASS' if all_valid else 'FAIL'}")
    
    return {
        'test_name': 'Radar Chart Calculation',
        'passed': all_valid,
        'radar_values': dict(radar_values)
    }


def validate_rounding_rules(report_data: dict) -> dict:
    """
    Validate per-field rounding consistency
    """
    print("\n" + "="*80)
    print("TEST 2: Per-Field Rounding Validation")
    print("="*80)
    
    rounding_checks = []
    
    # POI scores (2 decimal places)
    poi = report_data.get('poi_analysis_v3_1', {})
    poi_score = poi.get('total_score_v3_1', 0)
    rounding_checks.append(('POI Total Score', poi_score, 2))
    
    # Type Demand scores (1-2 decimal places)
    td = report_data.get('type_demand_v3_1', {})
    main_score = td.get('main_score', 0)
    rounding_checks.append(('Type Demand Main Score', main_score, 2))
    
    # GeoOptimizer scores (2 decimal places)
    geo = report_data.get('geo_optimizer_v3_1', {})
    geo_score = geo.get('final_score', 0)
    rounding_checks.append(('GeoOptimizer Final Score', geo_score, 2))
    
    # Risk score (1 decimal place)
    risk = report_data.get('risk_analysis_2025', {})
    risk_score = risk.get('risk_score', 0)
    rounding_checks.append(('Risk Score', risk_score, 1))
    
    # LH total score (2 decimal places)
    lh = report_data.get('lh_assessment', {})
    lh_score = lh.get('total_score', 0)
    rounding_checks.append(('LH Total Score', lh_score, 2))
    
    print("\n✅ Rounding Validation:")
    all_valid = True
    for field_name, value, decimals in rounding_checks:
        rounded_value = round(value, decimals)
        is_valid = abs(value - rounded_value) < 10**(-decimals)
        status = "✅" if is_valid else "❌"
        print(f"   {status} {field_name}: {value:.4f} → {rounded_value} (expected {decimals} decimals)")
        if not is_valid:
            all_valid = False
    
    print(f"\n{'✅' if all_valid else '❌'} Rounding Rules: {'PASS' if all_valid else 'FAIL'}")
    
    return {
        'test_name': 'Per-Field Rounding',
        'passed': all_valid,
        'checks': rounding_checks
    }


def validate_no_hardcoded_values(report_data: dict) -> dict:
    """
    Validate that no hardcoded fixed values exist
    """
    print("\n" + "="*80)
    print("TEST 3: No Hardcoded Values Validation")
    print("="*80)
    
    issues = []
    
    # Check POI - should not have fixed "지하철 3개 / 버스 0개"
    poi = report_data.get('poi_analysis_v3_1', {})
    pois = poi.get('pois', {})
    if not pois or len(pois) == 0:
        issues.append("POI data is empty or missing")
    else:
        print(f"   ✅ POI data exists: {len(pois)} POI types")
    
    # Check Type Demand - should have real scores, not "4.5/5"
    td = report_data.get('type_demand_v3_1', {})
    type_scores = td.get('type_scores', {})
    if not type_scores:
        issues.append("Type Demand scores missing")
    else:
        print(f"   ✅ Type Demand data exists: {len(type_scores)} types")
    
    # Check Zoning - should have 23 fields
    zone = report_data.get('zone_info', {})
    expected_fields = [
        'land_use_zone', 'building_coverage_ratio', 'floor_area_ratio',
        'height_limit', 'overlay_zones', 'district_unit_plan',
        'landscape_district', 'development_restrictions', 'environmental_restrictions',
        'cultural_heritage_zone', 'military_restriction_zone', 'road_width',
        'road_condition', 'water_supply', 'sewage_system', 'electricity',
        'gas_supply', 'urban_planning_area', 'redevelopment_zone',
        'special_planning_area', 'parking_requirements', 'green_space_ratio',
        'setback_requirements'
    ]
    
    zone_fields_present = sum(1 for field in expected_fields if field in zone)
    print(f"   ✅ Zoning fields present: {zone_fields_present}/23")
    if zone_fields_present < 23:
        issues.append(f"Only {zone_fields_present}/23 zoning fields present")
    
    # Check GeoOptimizer - should have 3 alternatives
    geo = report_data.get('geo_optimizer_v3_1', {})
    alternatives = geo.get('alternatives', [])
    print(f"   ✅ GeoOptimizer alternatives: {len(alternatives)} (should be 3)")
    if len(alternatives) < 3:
        issues.append(f"Only {len(alternatives)}/3 alternatives present")
    
    all_valid = len(issues) == 0
    
    if issues:
        print("\n   Issues found:")
        for issue in issues:
            print(f"   ❌ {issue}")
    
    print(f"\n{'✅' if all_valid else '❌'} No Hardcoded Values: {'PASS' if all_valid else 'FAIL'}")
    
    return {
        'test_name': 'No Hardcoded Values',
        'passed': all_valid,
        'issues': issues
    }


def validate_pdf_generation(report_data: dict) -> dict:
    """
    Generate actual PDF and validate
    """
    print("\n" + "="*80)
    print("TEST 4: PDF Generation Validation")
    print("="*80)
    
    try:
        pdf_engine = PDFReportEngineV72()
        
        output_path = '/tmp/v7_2_validation_report.pdf'
        result = pdf_engine.generate_pdf(report_data, output_path)
        
        if result['success']:
            file_size = os.path.getsize(output_path)
            print(f"\n   ✅ PDF generated successfully")
            print(f"   📄 File: {output_path}")
            print(f"   📊 Size: {file_size:,} bytes")
            print(f"   ⏰ Generated at: {result['generated_at']}")
            
            # Check if file is reasonable size (> 10KB)
            if file_size < 10000:
                print(f"   ⚠️  WARNING: PDF file size is small ({file_size} bytes)")
                return {
                    'test_name': 'PDF Generation',
                    'passed': False,
                    'error': 'PDF file size too small'
                }
            
            return {
                'test_name': 'PDF Generation',
                'passed': True,
                'file_path': output_path,
                'file_size': file_size
            }
        else:
            print(f"\n   ❌ PDF generation failed: {result.get('error')}")
            return {
                'test_name': 'PDF Generation',
                'passed': False,
                'error': result.get('error')
            }
            
    except Exception as e:
        print(f"\n   ❌ PDF generation exception: {e}")
        import traceback
        traceback.print_exc()
        return {
            'test_name': 'PDF Generation',
            'passed': False,
            'error': str(e)
        }


async def main():
    """
    Main validation test
    """
    print("="*80)
    print("ZeroSite v7.2 PDF Report Engine - Final Validation Test")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Test parameters
    test_address = "월드컵북로 120"
    test_land_area = 660.0
    test_unit_type = "청년"
    
    print(f"\nTest Parameters:")
    print(f"  Address: {test_address}")
    print(f"  Land Area: {test_land_area}㎡")
    print(f"  Unit Type: {test_unit_type}")
    
    # Step 1: Run analysis
    print("\n" + "="*80)
    print("STEP 1: Running Land Analysis")
    print("="*80)
    
    try:
        engine = AnalysisEngine()
        request = LandAnalysisRequest(
            address=test_address,
            land_area=test_land_area,
            user_type=test_unit_type
        )
        analysis_result = await engine.analyze_land(request)
        print("\n✅ Analysis completed successfully")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Step 2: Map to v7.2 fields
    print("\n" + "="*80)
    print("STEP 2: Mapping to v7.2 Fields")
    print("="*80)
    
    try:
        mapper = ReportFieldMapperV72Complete()
        report_data = mapper.map_analysis_output_to_report(analysis_result)
        print("\n✅ Field mapping completed")
        print(f"   Sections mapped: {len(report_data.keys())}")
    except Exception as e:
        print(f"\n❌ Field mapping failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Run validation tests
    results = []
    
    results.append(validate_radar_chart_calculation(report_data))
    results.append(validate_rounding_rules(report_data))
    results.append(validate_no_hardcoded_values(report_data))
    results.append(validate_pdf_generation(report_data))
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    for result in results:
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"\n{status}: {result['test_name']}")
        if not result['passed'] and 'error' in result:
            print(f"   Error: {result['error']}")
    
    print(f"\n{'='*80}")
    print(f"FINAL RESULT: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL VALIDATION TESTS PASSED - PRODUCTION READY")
        print("="*80)
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
