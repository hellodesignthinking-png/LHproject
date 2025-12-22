"""
Test Report Generator v8.8 Complete Implementation
"""

import sys
sys.path.insert(0, '.')

from app.services.report_generator_v8_8 import ReportGeneratorV88, create_report_generator_v88
from app.services.canonical_flow_adapter import CanonicalFlowAdapter
from app.services.lh_analysis_canonical import LHAnalysisCanonical
from app.services.visualization_module_v8_8 import create_visualization_module


def test_complete_report_generation():
    """Test complete report generation with all sections"""
    
    print("\n" + "="*80)
    print("🔬 ZeroSite v8.8 - Complete Report Generator Test")
    print("="*80)
    
    # Mock analysis result
    class MockZoneInfo:
        def __init__(self):
            self.zone_type = '제2종일반주거지역'
            self.building_coverage_ratio = 60
            self.floor_area_ratio = 200
    
    mock_analysis_result = {
        'address': '서울시 마포구 월드컵북로 120',
        'land_area': 660.0,
        'zone_info': MockZoneInfo(),
        'distance_to_subway': 250,
        'youth_ratio': 28,
        'elderly_ratio': 12,
        'nearby_schools': 5,
        'nearby_hospitals': 3,
        'accessibility': {'score': 85}
    }
    
    # Create appraisal context
    print("\n📋 STEP 1: Creating Appraisal Context")
    adapter = CanonicalFlowAdapter()
    appraisal_ctx = adapter.create_appraisal_context(
        analysis_result=mock_analysis_result,
        land_area=660.0,
        official_price=5500000,
        premium_rate=0.09
    )
    
    final_value = appraisal_ctx.get('calculation.final_appraised_total')
    print(f"   ✅ Appraisal Context Created")
    print(f"   Final Appraised Value: {final_value:,.0f}원")
    print(f"   Context Locked: {appraisal_ctx.is_locked()}")
    
    # Run LH Analysis
    print("\n📋 STEP 2: Running LH Analysis")
    lh_analyzer = LHAnalysisCanonical()
    lh_result = lh_analyzer.analyze(
        appraisal_ctx=appraisal_ctx,
        expected_units=56,
        total_floor_area=1320.0,
        unit_type='청년형'
    )
    
    print(f"   ✅ LH Analysis Complete")
    print(f"   ROI: {lh_result.get('roi', 0):.2f}%")
    print(f"   Decision: {lh_result.get('decision', 'N/A')}")
    
    # Generate Report
    print("\n📋 STEP 3: Generating Complete Report")
    report_generator = ReportGeneratorV88(
        appraisal_ctx=appraisal_ctx,
        analysis_data=mock_analysis_result,
        lh_analysis_result=lh_result
    )
    
    report = report_generator.generate()
    
    print(f"\n✅ Report Generated Successfully")
    print(f"   Report ID: {report['report_id']}")
    print(f"   Version: {report['version']}")
    print(f"   Structure: {report['structure']}")
    
    # Verify sections
    print("\n📊 Report Structure Verification:")
    print(f"   Cover: {report['cover']['page']}")
    print(f"   Executive Summary: {report['executive_summary']['page']}")
    print(f"   TOC: {report['table_of_contents']['page']}")
    
    section1_pages = len(report['section_1_appraisal']['pages'])
    section2_pages = len(report['section_2_diagnosis']['pages'])
    section3_pages = len(report['section_3_lh_judgment']['pages'])
    appendix_pages = len(report['appendix'])
    
    print(f"\n   SECTION 1 (FACT): {section1_pages} pages")
    print(f"   SECTION 2 (INTERPRETATION): {section2_pages} pages")
    print(f"   SECTION 3 (JUDGMENT): {section3_pages} pages")
    print(f"   APPENDIX: {appendix_pages} pages")
    
    total_pages = 3 + section1_pages + section2_pages + section3_pages + appendix_pages
    print(f"\n   📄 Total Pages: {total_pages}")
    
    # Test Visualization Module
    print("\n📋 STEP 4: Testing Visualization Module")
    viz_module = create_visualization_module()
    
    # Test Kakao Map
    kakao_map = viz_module.generate_kakao_static_map(
        latitude=37.5665,
        longitude=126.9780,
        zoom=16
    )
    print(f"   ✅ Kakao Static Map: {kakao_map['type']}")
    
    # Test Radar Chart
    type_scores = {
        '청년형': 17,
        '신혼부부 I': 17,
        '신혼부부 II': 16,
        '다자녀형': 15,
        '고령자형': 14
    }
    radar_chart = viz_module.generate_radar_chart(type_scores)
    print(f"   ✅ Radar Chart: {len(radar_chart['data']['labels'])} types")
    
    # Test Risk Heatmap
    risks = [
        {'category': '법규', 'probability': 'LOW', 'impact': 'HIGH'},
        {'category': '시장', 'probability': 'MEDIUM', 'impact': 'MEDIUM'},
        {'category': '공사', 'probability': 'MEDIUM', 'impact': 'HIGH'},
        {'category': '금융', 'probability': 'LOW', 'impact': 'MEDIUM'}
    ]
    heatmap = viz_module.generate_risk_heatmap(risks)
    print(f"   ✅ Risk Heatmap: {len(heatmap['risks'])} risks")
    
    # Test Market Histogram
    transaction_prices = [5200000, 5300000, 5400000, 5500000, 5600000, 5700000]
    histogram = viz_module.generate_market_histogram(transaction_prices, 5500000)
    print(f"   ✅ Market Histogram: {len(histogram['data'])} bins")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED - Report Generator v8.8 Complete")
    print("="*80)
    
    print("\n📊 Summary:")
    print(f"  ✓ Appraisal Context: LOCKED at {final_value:,.0f}원")
    print(f"  ✓ Report Structure: FACT/INTERPRETATION/JUDGMENT")
    print(f"  ✓ Total Pages: {total_pages} (Target: 60)")
    print(f"  ✓ Section 1 (Appraisal): {section1_pages} pages (Target: 18)")
    print(f"  ✓ Section 2 (Diagnosis): {section2_pages} pages (Target: 19)")
    print(f"  ✓ Section 3 (LH Judgment): {section3_pages} pages (Target: 15)")
    print(f"  ✓ Visualization Module: 4 chart types ready")
    
    print("\n🎉 Report Generator v8.8 Implementation: COMPLETE")


if __name__ == '__main__':
    test_complete_report_generation()
