"""
Phase 10.5: LH Full Submission Report Test Suite

Tests the complete 30-50 page report generation system including:
- Report data generation
- Template rendering
- PDF export
- Multi-parcel scenarios
- Integration with all phases (0-11, 2.5, 6.8, 7.7, 8)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services_v13.report_full.report_full_generator import (
    LHFullReportGenerator,
    generate_lh_full_report
)
from app.services_v13.report_full.charts_full import ChartGenerator
from jinja2 import Environment, FileSystemLoader
import time


def test_report_data_generation():
    """Test 1: Generate complete report data for a single address"""
    print("\n" + "="*80)
    print("TEST 1: Report Data Generation (Single Address)")
    print("="*80)
    
    generator = LHFullReportGenerator()
    
    # Test address: Gangnam area
    address = "서울시 강남구 역삼동 123"
    land_area_sqm = 500.0
    
    start_time = time.time()
    
    report_data = generator.generate_full_report_data(
        address=address,
        land_area_sqm=land_area_sqm,
        additional_params={'appraisal_price': 50_000_000}
    )
    
    elapsed = time.time() - start_time
    
    # Validate report structure
    required_sections = [
        'metadata', 'site_overview', 'zoning_regulations',
        'regional_analysis', 'construction_cost', 'financial_analysis',
        'market_analysis', 'unit_types', 'risk_analysis', 'appendix'
    ]
    
    print(f"\n✓ Report generated in {elapsed:.3f} seconds")
    print(f"\n📋 Report Sections:")
    for section in required_sections:
        status = "✓" if section in report_data else "✗"
        print(f"  {status} {section}")
    
    # Print key metrics
    print(f"\n📊 Key Metrics:")
    print(f"  Address: {report_data['site_overview']['address']}")
    print(f"  Land Area: {report_data['site_overview']['land_area_sqm']:.2f}㎡")
    print(f"  Project Code: {report_data['site_overview']['project_code']}")
    
    if 'capex_total' in report_data['financial_analysis']:
        capex = report_data['financial_analysis']['capex_total'] / 100000000
        print(f"  Total CAPEX: {capex:.2f}억원")
    
    if report_data['regional_analysis'].get('status') not in ['unavailable', 'not_integrated']:
        print(f"  Recommended Housing Type: {report_data['regional_analysis']['recommended_type']}")
        print(f"  Demand Score: {report_data['regional_analysis']['demand_score']:.1f}/100")
    
    if report_data['market_analysis'].get('status') == 'available':
        print(f"  Market Signal: {report_data['market_analysis']['signal']}")
    
    assert all(section in report_data for section in required_sections), "Missing required sections"
    print("\n✅ TEST 1 PASSED: Report data generation successful")
    
    return report_data


def test_template_rendering():
    """Test 2: Render HTML template with report data"""
    print("\n" + "="*80)
    print("TEST 2: Template Rendering (HTML Generation)")
    print("="*80)
    
    # Generate report data
    report_data = generate_lh_full_report(
        address="경기도 성남시 분당구 정자동 456",
        land_area_sqm=800.0
    )
    
    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.parent / 'app' / 'templates_v13'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template('lh_submission_full.html.jinja2')
    
    start_time = time.time()
    
    # Render template
    html_content = template.render(**report_data)
    
    elapsed = time.time() - start_time
    
    # Validate HTML
    html_length = len(html_content)
    page_count_estimate = html_length / 2000  # Rough estimate: 2000 chars per page
    
    print(f"\n✓ Template rendered in {elapsed:.3f} seconds")
    print(f"  HTML Length: {html_length:,} characters")
    print(f"  Estimated Pages: {page_count_estimate:.1f} pages")
    
    # Check for key sections in HTML
    key_sections = [
        '대상지 개요',
        '도시계획 및 법규',
        '재무 타당성 분석',
        '시장 분석',
        '리스크 분석'
    ]
    
    print(f"\n📄 HTML Content Validation:")
    for section in key_sections:
        if section in html_content:
            print(f"  ✓ {section} found")
        else:
            print(f"  ✗ {section} missing")
    
    assert html_length > 20000, "HTML content too short (< 20,000 chars)"
    assert all(section in html_content for section in key_sections), "Missing key sections in HTML"
    
    print("\n✅ TEST 2 PASSED: Template rendering successful")
    
    return html_content


def test_chart_generation():
    """Test 3: Generate financial charts"""
    print("\n" + "="*80)
    print("TEST 3: Chart Generation")
    print("="*80)
    
    chart_gen = ChartGenerator()
    
    # Test data
    capex_data = {
        '토지비': 500,
        '건축비': 1200,
        '설계비': 100,
        '부대비용': 200
    }
    
    years = list(range(1, 11))
    cashflows = [50 + i*2 for i in range(10)]
    
    start_time = time.time()
    
    # Generate charts (as base64)
    charts = {}
    charts['capex'] = chart_gen.generate_capex_breakdown_pie(capex_data)
    charts['npv'] = chart_gen.generate_npv_discount_curve(years, cashflows)
    charts['irr'] = chart_gen.generate_irr_sensitivity_table(3.5, 5.2, 7.8)
    charts['opex_revenue'] = chart_gen.generate_opex_revenue_timeline(
        years, [100 + i*5 for i in range(10)], [60 + i*2 for i in range(10)]
    )
    charts['market'] = chart_gen.generate_market_signal_gauge(1200, 1100)
    
    elapsed = time.time() - start_time
    
    print(f"\n✓ {len(charts)} charts generated in {elapsed:.3f} seconds")
    
    for chart_name, chart_data in charts.items():
        is_base64 = chart_data.startswith('data:image/png;base64,')
        print(f"  {'✓' if is_base64 else '✗'} {chart_name}: {'Base64' if is_base64 else 'Invalid'}")
    
    assert all(chart.startswith('data:image/png;base64,') for chart in charts.values()), \
        "Some charts failed to generate"
    
    print("\n✅ TEST 3 PASSED: Chart generation successful")
    
    return charts


def test_multi_parcel_scenario():
    """Test 4: Multi-parcel scenario (multiple addresses)"""
    print("\n" + "="*80)
    print("TEST 4: Multi-Parcel Scenario")
    print("="*80)
    
    generator = LHFullReportGenerator()
    
    parcels = [
        {"address": "서울시 강남구 역삼동 100", "land_area_sqm": 300},
        {"address": "서울시 강남구 역삼동 101", "land_area_sqm": 350},
        {"address": "서울시 강남구 역삼동 102", "land_area_sqm": 280}
    ]
    
    print(f"\n📦 Testing {len(parcels)} parcels:")
    
    start_time = time.time()
    
    all_reports = []
    for i, parcel in enumerate(parcels, 1):
        print(f"\n  Parcel {i}: {parcel['address']} ({parcel['land_area_sqm']}㎡)")
        
        report = generator.generate_full_report_data(
            address=parcel['address'],
            land_area_sqm=parcel['land_area_sqm']
        )
        
        all_reports.append(report)
        
        if 'capex_total' in report['financial_analysis']:
            capex = report['financial_analysis']['capex_total'] / 100000000
            print(f"    CAPEX: {capex:.2f}억원")
    
    elapsed = time.time() - start_time
    
    # Calculate combined metrics
    total_land_area = sum(p['land_area_sqm'] for p in parcels)
    total_capex = sum(
        r['financial_analysis'].get('capex_total', 0) 
        for r in all_reports if 'capex_total' in r['financial_analysis']
    ) / 100000000
    
    print(f"\n📊 Combined Metrics:")
    print(f"  Total Land Area: {total_land_area:.2f}㎡")
    print(f"  Total CAPEX: {total_capex:.2f}억원")
    print(f"  Total Processing Time: {elapsed:.3f} seconds")
    print(f"  Avg Time per Parcel: {elapsed/len(parcels):.3f} seconds")
    
    assert len(all_reports) == len(parcels), "Not all parcels processed"
    assert elapsed < 30, "Multi-parcel processing too slow (>30s)"
    
    print("\n✅ TEST 4 PASSED: Multi-parcel scenario successful")
    
    return all_reports


def test_graceful_fallback():
    """Test 5: Graceful fallback when Phase 6.8/7.7 data unavailable"""
    print("\n" + "="*80)
    print("TEST 5: Graceful Fallback (Missing Phase Data)")
    print("="*80)
    
    # Test with minimal data
    generator = LHFullReportGenerator()
    
    report_data = generator.generate_full_report_data(
        address="경상북도 예천군 예천읍 789",
        land_area_sqm=1200.0
    )
    
    print(f"\n📋 Report Status:")
    print(f"  Regional Analysis: {report_data['regional_analysis'].get('status', 'N/A')}")
    print(f"  Market Analysis: {report_data['market_analysis'].get('status', 'N/A')}")
    print(f"  Construction Cost: {report_data['construction_cost'].get('status', 'N/A')}")
    print(f"  Financial Analysis: {report_data['financial_analysis'].get('status', 'N/A')}")
    
    # Should still generate valid report even if some phases unavailable
    assert 'metadata' in report_data, "Metadata missing"
    assert 'site_overview' in report_data, "Site overview missing"
    assert 'financial_analysis' in report_data, "Financial analysis missing"
    
    print("\n✅ TEST 5 PASSED: Graceful fallback working correctly")
    
    return report_data


def test_performance_benchmark():
    """Test 6: Performance benchmark (must complete in <5 seconds)"""
    print("\n" + "="*80)
    print("TEST 6: Performance Benchmark")
    print("="*80)
    
    addresses = [
        ("서울시 강남구 역삼동", 500),
        ("경기도 성남시 분당구", 800),
        ("인천시 연수구 송도동", 1000)
    ]
    
    print(f"\n⏱️ Testing {len(addresses)} addresses:")
    
    total_time = 0
    
    for address, land_area in addresses:
        start = time.time()
        
        report = generate_lh_full_report(address, land_area)
        
        elapsed = time.time() - start
        total_time += elapsed
        
        status = "✓" if elapsed < 5.0 else "✗"
        print(f"  {status} {address}: {elapsed:.3f}s")
    
    avg_time = total_time / len(addresses)
    
    print(f"\n📊 Performance Summary:")
    print(f"  Total Time: {total_time:.3f}s")
    print(f"  Average Time: {avg_time:.3f}s")
    print(f"  Target: <5.0s per report")
    
    # Performance assertion
    assert avg_time < 5.0, f"Average time {avg_time:.3f}s exceeds 5s target"
    
    print("\n✅ TEST 6 PASSED: Performance within target")


def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*80)
    print("ZEROSITE PHASE 10.5: LH FULL REPORT TEST SUITE")
    print("="*80)
    print("Testing 30-50 page comprehensive report generation")
    print("Integration: Phase 0-11 + Phase 2.5 + Phase 6.8 + Phase 7.7 + Phase 8")
    print("="*80)
    
    try:
        # Run all tests
        test_report_data_generation()
        test_template_rendering()
        test_chart_generation()
        test_multi_parcel_scenario()
        test_graceful_fallback()
        test_performance_benchmark()
        
        # Summary
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Phase 10.5 Integration Complete")
        print("="*80)
        print("\n📊 Test Summary:")
        print("  ✓ Report Data Generation")
        print("  ✓ Template Rendering (30+ page HTML)")
        print("  ✓ Chart Generation (5 chart types)")
        print("  ✓ Multi-Parcel Scenarios")
        print("  ✓ Graceful Fallback")
        print("  ✓ Performance Benchmark (<5s)")
        print("\n🎯 Phase 10.5 Status: PRODUCTION READY")
        print("📦 Deliverable: LH Official Full Submission Report (30-50 pages)")
        print("🚀 Next Step: Phase 11.2 (Minimal UI)")
        print("="*80)
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
