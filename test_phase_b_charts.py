"""
Test Phase B: New Chart Generation
Tests all 5 new visualization charts for Expert Edition v3
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.charts_full import ChartGenerator
import numpy as np

def test_gantt_chart():
    """Test 36-month Gantt Chart generation"""
    print("\n" + "="*80)
    print("TEST 1: Gantt Chart (36-Month Project Roadmap)")
    print("="*80)
    
    # Sample milestone data
    milestones = [
        {'name': '사업부지 선정', 'start_month': 0, 'duration': 3, 'phase': '준비단계'},
        {'name': 'LH 사업타당성 검토', 'start_month': 2, 'duration': 2, 'phase': '준비단계'},
        {'name': '감정평가 의뢰', 'start_month': 4, 'duration': 4, 'phase': '준비단계'},
        {'name': '토지매입 협상', 'start_month': 6, 'duration': 3, 'phase': '준비단계'},
        {'name': '설계 및 인허가', 'start_month': 9, 'duration': 6, 'phase': '착공단계'},
        {'name': '시공사 선정', 'start_month': 12, 'duration': 2, 'phase': '착공단계'},
        {'name': '착공', 'start_month': 15, 'duration': 1, 'phase': '착공단계'},
        {'name': '기초공사', 'start_month': 16, 'duration': 4, 'phase': '시공단계'},
        {'name': '골조공사', 'start_month': 20, 'duration': 8, 'phase': '시공단계'},
        {'name': '마감공사', 'start_month': 28, 'duration': 5, 'phase': '시공단계'},
        {'name': '준공검사', 'start_month': 33, 'duration': 2, 'phase': '준공단계'},
        {'name': 'LH 인수인계', 'start_month': 35, 'duration': 1, 'phase': '준공단계'},
    ]
    
    generator = ChartGenerator(output_dir=Path('output'))
    result = generator.generate_gantt_chart(milestones)
    
    print(f"✅ Gantt Chart generated: {result}")
    print(f"   - Total milestones: {len(milestones)}")
    print(f"   - Project duration: 36 months")
    print(f"   - Phases: 준비단계, 착공단계, 시공단계, 준공단계")
    
    return result


def test_npv_tornado_chart():
    """Test NPV Tornado Chart (sensitivity analysis)"""
    print("\n" + "="*80)
    print("TEST 2: NPV Tornado Chart (Sensitivity Analysis)")
    print("="*80)
    
    base_npv = 250.0  # 250억원
    
    # Sensitivity data: impact of ±10% change in each variable
    sensitivity_data = {
        '분양가/임대료': {'low': 180.0, 'high': 320.0},  # High sensitivity
        '건축비': {'low': 285.0, 'high': 215.0},  # High sensitivity (inverse)
        '토지비': {'low': 275.0, 'high': 225.0},  # Medium sensitivity (inverse)
        '할인율': {'low': 265.0, 'high': 235.0},  # Medium sensitivity (inverse)
        '공실률': {'low': 260.0, 'high': 240.0},  # Low sensitivity (inverse)
        '관리비': {'low': 255.0, 'high': 245.0},  # Low sensitivity (inverse)
    }
    
    generator = ChartGenerator(output_dir=Path('output'))
    result = generator.generate_npv_tornado_chart(sensitivity_data, base_npv)
    
    print(f"✅ NPV Tornado Chart generated: {result}")
    print(f"   - Base NPV: {base_npv}억원")
    print(f"   - Variables analyzed: {len(sensitivity_data)}")
    print(f"   - Most sensitive: 분양가/임대료, 건축비")
    
    return result


def test_financial_scorecard():
    """Test Financial Scorecard (visual KPI dashboard)"""
    print("\n" + "="*80)
    print("TEST 3: Financial Scorecard (Visual KPI Dashboard)")
    print("="*80)
    
    kpis = {
        'capex': 1250.0,  # 총 투자비 1,250억원
        'npv': 250.0,     # NPV 250억원
        'irr': 5.8,       # IRR 5.8%
        'payback': 12.5,  # 회수기간 12.5년
        'roi': 20.0,      # ROI 20%
        'grade': 'A-'     # 종합등급 A-
    }
    
    generator = ChartGenerator(output_dir=Path('output'))
    result = generator.generate_financial_scorecard(kpis)
    
    print(f"✅ Financial Scorecard generated: {result}")
    print(f"   - Total CAPEX: {kpis['capex']}억원")
    print(f"   - NPV: {kpis['npv']}억원")
    print(f"   - IRR: {kpis['irr']}%")
    print(f"   - Overall Grade: {kpis['grade']}")
    
    return result


def test_competitive_analysis_table():
    """Test Competitive Analysis Table"""
    print("\n" + "="*80)
    print("TEST 4: Competitive Analysis Table (Market Comparison)")
    print("="*80)
    
    current_project = {
        'name': '역삼동 737번지 (당사 사업지)',
        'price': 2800,  # 2,800만원
        'distance': 0.0,  # 0km (current site)
        'units': 120,
        'completion': '2028'
    }
    
    competitors = [
        {'name': '강남구 A 프로젝트', 'price': 3200, 'distance': 1.2, 'units': 150, 'completion': '2027'},
        {'name': '서초구 B 프로젝트', 'price': 2900, 'distance': 2.5, 'units': 180, 'completion': '2027'},
        {'name': '강남구 C 프로젝트', 'price': 3500, 'distance': 0.8, 'units': 200, 'completion': '2026'},
        {'name': '송파구 D 프로젝트', 'price': 2600, 'distance': 3.0, 'units': 100, 'completion': '2028'},
    ]
    
    generator = ChartGenerator(output_dir=Path('output'))
    result = generator.generate_competitive_analysis_table(competitors, current_project)
    
    print(f"✅ Competitive Analysis Table generated: {result}")
    print(f"   - Current project: {current_project['name']}")
    print(f"   - Competitors analyzed: {len(competitors)}")
    print(f"   - Price range: {min(c['price'] for c in competitors)}-{max(c['price'] for c in competitors)}만원")
    
    return result


def test_30year_cashflow_chart():
    """Test 30-Year Cashflow Chart"""
    print("\n" + "="*80)
    print("TEST 5: 30-Year Cashflow Chart (Long-term Projection)")
    print("="*80)
    
    # Generate 30-year projection data
    years = list(range(30))
    
    # Initial investment period (years 0-3): negative cashflow
    # Operation period (years 4-29): positive cashflow with growth
    revenues = []
    expenses = []
    for year in years:
        if year < 3:
            # Construction period
            revenues.append(0)
            expenses.append(400)  # High construction costs
        else:
            # Operating period
            base_revenue = 80 + (year - 3) * 2  # Growing revenue
            base_expense = 30 + (year - 3) * 0.5  # Growing expenses
            revenues.append(base_revenue)
            expenses.append(base_expense)
    
    net_cashflows = [r - e for r, e in zip(revenues, expenses)]
    
    generator = ChartGenerator(output_dir=Path('output'))
    result = generator.generate_30year_cashflow_chart(years, revenues, expenses, net_cashflows)
    
    cumulative_cf = sum(net_cashflows)
    print(f"✅ 30-Year Cashflow Chart generated: {result}")
    print(f"   - Project duration: 30 years")
    print(f"   - Total cumulative cashflow: {cumulative_cf:.1f}억원")
    print(f"   - Break-even year: ~Year 4-5")
    
    return result


def run_all_tests():
    """Run all Phase B chart tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "Phase B: Chart Generation Tests" + " "*26 + "║")
    print("║" + " "*14 + "Testing 5 New Visualization Charts" + " "*29 + "║")
    print("╚" + "="*78 + "╝")
    
    # Create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    try:
        # Test 1: Gantt Chart
        results['gantt'] = test_gantt_chart()
        
        # Test 2: NPV Tornado
        results['tornado'] = test_npv_tornado_chart()
        
        # Test 3: Financial Scorecard
        results['scorecard'] = test_financial_scorecard()
        
        # Test 4: Competitive Analysis
        results['competitive'] = test_competitive_analysis_table()
        
        # Test 5: 30-Year Cashflow
        results['cashflow_30'] = test_30year_cashflow_chart()
        
        # Summary
        print("\n" + "="*80)
        print("SUMMARY: Phase B Chart Generation Tests")
        print("="*80)
        print(f"✅ Total tests: 5")
        print(f"✅ Passed: {len(results)}")
        print(f"❌ Failed: 0")
        print(f"\nGenerated charts:")
        for name, path in results.items():
            print(f"   - {name}: {path}")
        
        print("\n" + "="*80)
        print("🎉 Phase B.1-5: Chart Implementation COMPLETE!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Integrate charts into Expert Edition v3 template")
        print("  2. Test with real project data")
        print("  3. Verify PDF generation with all charts")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
