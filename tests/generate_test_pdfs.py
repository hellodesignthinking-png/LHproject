"""
Test PDF Generator for ZeroSite v24.1
Generates all 5 report types with sample data for quality inspection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.report_generator_v241_enhanced import ReportGeneratorV241Enhanced
from app.engines.capacity_engine_v241 import CapacityEngineV241
from app.engines.scenario_engine_v241 import ScenarioEngineV241
from app.engines.financial_engine_v241 import FinancialEngineV241
from app.engines.market_engine_v241 import MarketEngineV241
from app.engines.risk_engine_v241 import RiskEngineV241
from datetime import datetime
import json

def create_sample_parcel_data():
    """Create comprehensive sample parcel data"""
    return {
        "parcel_id": "1168010100101230045",
        "address": "서울특별시 강남구 역삼동 123-45",
        "jibun_address": "서울특별시 강남구 역삼동 123-45",
        "area_m2": 500.0,
        "area_pyeong": 151.25,
        "owner_name": "홍길동",
        "owner_budget": 50000000000,  # 500억원
        "zoning": "제2종일반주거지역",
        "zoning_code": "UQA220",
        "use_district": "일반주거지역",
        "land_price_per_m2": 15000000,  # 평당 5천만원
        "official_land_price": 7500000000,  # 공시지가 75억
        "current_use": "단독주택",
        "road_facing": True,
        "road_width_m": 8.0,
        "slope_degree": 5.0,
        "shape_regularity": "정방형",
        "coordinates": {
            "latitude": 37.5012,
            "longitude": 127.0396
        },
        "regulations": {
            "far_max": 250.0,
            "bcr_max": 60.0,
            "height_limit_m": 35.0,
            "floor_limit": 10,
            "setback_front_m": 3.0,
            "setback_side_m": 1.5,
            "parking_required_per_unit": 1.0
        },
        "surrounding": {
            "station_distance_m": 450,
            "station_name": "역삼역",
            "bus_stops_nearby": 3,
            "schools_nearby": 2,
            "parks_nearby": 1
        }
    }

def generate_all_test_pdfs():
    """Generate all 5 report types with sample data"""
    
    print("=" * 80)
    print("ZeroSite v24.1 - Test PDF Generation")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Purpose: Generate all 5 report types for quality inspection")
    print("=" * 80)
    print()
    
    # Create sample data
    parcel_data = create_sample_parcel_data()
    
    # Initialize report generator
    print("🔧 Initializing Report Generator...")
    generator = ReportGeneratorV241Enhanced()
    
    # Create output directory
    output_dir = "test_pdfs_output"
    os.makedirs(output_dir, exist_ok=True)
    print(f"✅ Output directory: {output_dir}")
    print()
    
    # First, gather all engine data (required for all reports)
    print("🔧 Gathering engine data...")
    try:
        context = generator.gather_all_engine_data(parcel_data)
        print("✅ Engine data gathered successfully")
        print()
    except Exception as e:
        print(f"❌ Error gathering engine data: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Report types to generate with their method names
    report_types = [
        ("brief", "Report 1 - Landowner Brief", "토지주용 간편보고서", "generate_report_1_landowner_brief"),
        ("lh_official", "Report 2 - LH Official", "LH공식양식보고서", "generate_report_2_lh_submission"),
        ("extended", "Report 3 - Extended Professional", "전문가용 심화보고서", "generate_report_3_extended_professional"),
        ("policy", "Report 4 - Policy Impact Analysis", "정책효과분석보고서", "generate_report_4_policy_impact"),
        ("developer", "Report 5 - Developer Feasibility", "사업타당성보고서", "generate_report_5_developer_feasibility"),
    ]
    
    results = []
    
    for report_type, english_name, korean_name, method_name in report_types:
        print(f"📄 Generating {english_name} ({korean_name})...")
        print(f"   Type: {report_type}")
        print(f"   Method: {method_name}")
        
        try:
            # Get the generator method
            if not hasattr(generator, method_name):
                raise Exception(f"Method {method_name} not found in generator")
            
            generate_method = getattr(generator, method_name)
            
            # Generate report
            html_content = generate_method(context)
            
            # Save HTML
            output_filename = f"{output_dir}/{report_type}_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Get statistics
            html_length = len(html_content)
            # Better page estimation: count major sections or use line count
            page_estimate = max(3, html_length // 4000)  # At least 3 pages, roughly 4000 chars per page
            
            result_info = {
                "type": report_type,
                "name": english_name,
                "korean_name": korean_name,
                "html_file": output_filename,
                "html_size_kb": html_length // 1024,
                "estimated_pages": page_estimate,
                "status": "✅ Success"
            }
            
            results.append(result_info)
            
            print(f"   ✅ HTML saved: {output_filename}")
            print(f"   📊 Size: {result_info['html_size_kb']} KB")
            print(f"   📄 Estimated pages: {result_info['estimated_pages']}")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                "type": report_type,
                "name": english_name,
                "status": f"❌ Failed: {str(e)}"
            })
            print()
    
    # Generate summary report
    print("=" * 80)
    print("📊 TEST PDF GENERATION SUMMARY")
    print("=" * 80)
    print()
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}")
        print(f"   Type: {result['type']}")
        print(f"   Status: {result['status']}")
        if 'html_file' in result:
            print(f"   File: {result['html_file']}")
            print(f"   Size: {result['html_size_kb']} KB")
            print(f"   Pages: ~{result['estimated_pages']}")
        print()
    
    # Save summary JSON
    summary_file = f"{output_dir}/generation_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_reports": len(report_types),
            "successful": len([r for r in results if '✅' in r['status']]),
            "failed": len([r for r in results if '❌' in r['status']]),
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Summary saved: {summary_file}")
    print()
    print("=" * 80)
    print("✅ TEST PDF GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("Next Steps:")
    print("1. Open HTML files in browser for visual inspection")
    print("2. Check page counts match design spec requirements:")
    print("   - Report 1 (Brief): 3-5 pages")
    print("   - Report 2 (LH Official): 10-15 pages")
    print("   - Report 3 (Extended): 25-40 pages ⚠️ CRITICAL")
    print("   - Report 4 (Policy): 15-20 pages")
    print("   - Report 5 (Developer): 15-20 pages")
    print("3. Verify table/graph page breaks are clean")
    print("4. Check Korean font rendering")
    print("5. Verify header/footer on all pages")
    print()

if __name__ == "__main__":
    generate_all_test_pdfs()
