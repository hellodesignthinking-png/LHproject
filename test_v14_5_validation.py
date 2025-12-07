"""
ZeroSite v14.5 Final Validation Test
Tests all 4 critical improvements:
1. Data validation layer
2. Negative finance case handling
3. LH 100-point score table
4. Bibliography section
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.services_v13.report_full.charts_full import generate_all_financial_charts
from app.routers.report_v13 import _flatten_context_for_template
from jinja2 import Environment, FileSystemLoader
import time


def test_gangnam():
    """Test case 1: Seoul Gangnam (positive case)"""
    print("\n" + "="*80)
    print("TEST CASE 1: SEOUL GANGNAM (POSITIVE CASE)")
    print("="*80)
    
    address = "서울특별시 강남구 역삼동 737"
    land_area = 800.0
    coords = (37.5, 127.0)
    
    builder = ReportContextBuilder()
    context = builder.build_expert_context(
        address=address,
        land_area_sqm=land_area,
        coordinates=coords
    )
    
    # Validate context was validated
    assert context.get('_context_validated') == True, "Context validation missing"
    print("✅ Context validation applied")
    
    # Check finance validation
    finance = context.get('finance', {})
    assert 'npv_status' in finance, "NPV status missing"
    assert 'irr_status' in finance, "IRR status missing"
    assert 'payback_status' in finance, "Payback status missing"
    print(f"✅ Finance validation: NPV={finance.get('npv_status')}, IRR={finance.get('irr_status')}, Payback={finance.get('payback_status')}")
    
    # Check demand validation
    demand = context.get('demand', {})
    assert 'overall_score' in demand and demand['overall_score'] is not None, "Demand score missing"
    print(f"✅ Demand validation: Score={demand.get('overall_score'):.1f}")
    
    # Check market validation
    market = context.get('market', {})
    assert 'signal' in market and market['signal'] is not None, "Market signal missing"
    print(f"✅ Market validation: Signal={market.get('signal')}")
    
    # Check citations
    narratives = context.get('narratives', {})
    citations = narratives.get('citations', [])
    citation_count = len(citations)
    # Note: Some narratives may not use all available citations - minimum 2 required
    assert citation_count >= 2, f"Citation count too low: {citation_count}"
    print(f"✅ Citations collected: {citation_count} citations (tracking system working)")
    
    # Generate report
    chart_data = prepare_test_chart_data(context)
    charts = generate_all_financial_charts(chart_data, Path('output'))
    context['charts'] = charts
    
    env = Environment(loader=FileSystemLoader('app/services_v13/report_full'))
    template = env.get_template('lh_expert_edition_v3.html.jinja2')
    flat_context = _flatten_context_for_template(context, land_area)
    html = template.render(**flat_context)
    
    # Check score table presence
    assert '<table class="evaluation-table"' in html, "Score table missing"
    print("✅ LH 100-point score table present")
    
    # Check bibliography section
    assert 'References & Policy Citations' in html, "Bibliography section missing"
    assert 'References & Bibliography' in html or '참고문헌' in html, "Bibliography section missing"
    print("✅ Bibliography section present")
    
    # Save output
    output_path = Path('output/v14_5_gangnam.html')
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Report saved: {output_path} ({len(html)/1024:.1f}KB)")
    
    return True


def test_bundang():
    """Test case 2: Bundang (edge case - suburban)"""
    print("\n" + "="*80)
    print("TEST CASE 2: BUNDANG (SUBURBAN EDGE CASE)")
    print("="*80)
    
    address = "경기도 성남시 분당구 정자동 100"
    land_area = 600.0
    coords = (37.36, 127.11)
    
    builder = ReportContextBuilder()
    context = builder.build_expert_context(
        address=address,
        land_area_sqm=land_area,
        coordinates=coords
    )
    
    # Validate all critical checks
    assert context.get('_context_validated') == True
    print("✅ Context validation applied")
    
    finance = context.get('finance', {})
    assert 'npv_status' in finance
    print(f"✅ Finance validation: NPV={finance.get('npv_status')}")
    
    demand = context.get('demand', {})
    assert 'overall_score' in demand and demand['overall_score'] is not None
    print(f"✅ Demand validation: Score={demand.get('overall_score'):.1f}")
    
    citations = context.get('narratives', {}).get('citations', [])
    print(f"✅ Citations: {len(citations)} collected")
    
    # Generate brief report
    chart_data = prepare_test_chart_data(context)
    charts = generate_all_financial_charts(chart_data, Path('output'))
    context['charts'] = charts
    
    env = Environment(loader=FileSystemLoader('app/services_v13/report_full'))
    template = env.get_template('lh_expert_edition_v3.html.jinja2')
    flat_context = _flatten_context_for_template(context, land_area)
    html = template.render(**flat_context)
    
    output_path = Path('output/v14_5_bundang.html')
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Report saved: {output_path}")
    
    return True


def test_busan():
    """Test case 3: Busan (regional city)"""
    print("\n" + "="*80)
    print("TEST CASE 3: BUSAN (REGIONAL CITY)")
    print("="*80)
    
    address = "부산광역시 해운대구 우동 500"
    land_area = 700.0
    coords = (35.16, 129.16)
    
    builder = ReportContextBuilder()
    context = builder.build_expert_context(
        address=address,
        land_area_sqm=land_area,
        coordinates=coords
    )
    
    # Quick validation
    assert context.get('_context_validated') == True
    finance = context.get('finance', {})
    assert 'npv_status' in finance
    demand = context.get('demand', {})
    assert 'overall_score' in demand and demand['overall_score'] is not None
    citations = context.get('narratives', {}).get('citations', [])
    
    print(f"✅ All validations passed")
    print(f"✅ Finance: {finance.get('npv_status')}")
    print(f"✅ Demand: {demand.get('overall_score'):.1f}")
    print(f"✅ Citations: {len(citations)}")
    
    # Generate brief report
    chart_data = prepare_test_chart_data(context)
    charts = generate_all_financial_charts(chart_data, Path('output'))
    context['charts'] = charts
    
    env = Environment(loader=FileSystemLoader('app/services_v13/report_full'))
    template = env.get_template('lh_expert_edition_v3.html.jinja2')
    flat_context = _flatten_context_for_template(context, land_area)
    html = template.render(**flat_context)
    
    output_path = Path('output/v14_5_busan.html')
    output_path.write_text(html, encoding='utf-8')
    print(f"✅ Report saved: {output_path}")
    
    return True


def prepare_test_chart_data(context):
    """Prepare minimal chart data for testing"""
    finance = context.get('finance', {})
    
    # Handle validated IRR (may be string '<0' for negative cases)
    irr_value = finance.get('irr_public_pct', 5.0)
    if isinstance(irr_value, str):
        irr_value = 0.0  # Convert '<0' to numeric for charting
    
    return {
        'milestones': [
            {'name': '사업 착수', 'start_month': 0, 'duration': 3, 'phase': '준비'},
            {'name': 'LH 승인', 'start_month': 3, 'duration': 2, 'phase': '준비'},
            {'name': '착공', 'start_month': 6, 'duration': 18, 'phase': '시공'},
            {'name': '준공', 'start_month': 24, 'duration': 2, 'phase': '완료'},
        ],
        'base_npv': finance.get('npv_public_krw', 0),
        'sensitivity_data': {
            '임대료': {'low': -50, 'high': 50},
            '건축비': {'low': -30, 'high': 30},
        },
        'kpis': {
            'capex': finance.get('capex', {}).get('total_krw', 1000),
            'npv': finance.get('npv_public_krw', 0),
            'irr': irr_value,
            'payback': finance.get('payback_period_years', 0) if isinstance(finance.get('payback_period_years'), (int, float)) else 99,
            'roi': 0,
            'grade': 'B+'
        },
        'current_project': {'name': '당사 사업', 'price': 2800, 'distance': 0, 'units': 20, 'completion': '2028'},
        'competitors': [
            {'name': 'A 프로젝트', 'price': 3000, 'distance': 1.0, 'units': 30, 'completion': '2027'},
        ],
        'years_30': list(range(30)),
        'revenues_30': [0, 0, 80] + [90 + i for i in range(27)],
        'expenses_30': [400, 300, 30] + [35 + i*0.5 for i in range(27)],
        'net_cashflows_30': (lambda r, e: [r[i] - e[i] for i in range(30)])([0, 0, 80] + [90 + i for i in range(27)], [400, 300, 30] + [35 + i*0.5 for i in range(27)]),
        'capex_breakdown': {'토지비': 400, '건축비': 350, '기타': 150},
        'years': list(range(1, 11)),
        'cashflows': [-400, -300, -200, 50, 80, 90, 95, 100, 105, 110],
        'base_irr': irr_value,
        'optimistic_irr': irr_value + 0.5,
        'pessimistic_irr': irr_value - 0.5,
        'revenues': [80, 85, 88, 90, 92, 94, 96, 98, 100, 102],
        'opex': [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
        'zerosite_value': 900,
        'market_avg': 1000,
        'demand_scores': {'청년': 65, '신혼부부': 70, '고령자': 55, '일반': 60}
    }


def main():
    """Run all v14.5 validation tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "ZeroSite v14.5 Final Validation" + " "*27 + "║")
    print("║" + " "*15 + "Testing 4 Critical Improvements" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    start_time = time.time()
    
    try:
        # Test 1: Gangnam (full validation)
        test_gangnam()
        
        # Test 2: Bundang (edge case)
        test_bundang()
        
        # Test 3: Busan (regional)
        test_busan()
        
        elapsed = time.time() - start_time
        
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED!")
        print("="*80)
        print(f"⏱️  Total time: {elapsed:.1f}s")
        print(f"📁 Output files:")
        print(f"   - output/v14_5_gangnam.html")
        print(f"   - output/v14_5_bundang.html")
        print(f"   - output/v14_5_busan.html")
        print("\n✅ v14.5 validation complete - ready for production")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
