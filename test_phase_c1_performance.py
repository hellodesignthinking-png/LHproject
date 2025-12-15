"""
Phase C.1: Performance Optimization & Measurement
Measures current performance and tests optimizations
Target: 5-7 seconds total generation time
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
sys.path.insert(0, str(Path(__file__).parent))

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from app.services_v13.report_full.charts_full import ChartGenerator
from app.services_v13.report_full.narrative_interpreter import NarrativeInterpreter
from app.routers.report_v13 import _flatten_context_for_template
from jinja2 import Environment, FileSystemLoader

class PerformanceMeasurement:
    """Performance measurement and tracking"""
    
    def __init__(self):
        self.timings = {}
        self.start_times = {}
    
    def start(self, task_name: str):
        """Start timing a task"""
        self.start_times[task_name] = time.time()
    
    def end(self, task_name: str) -> float:
        """End timing a task and return duration"""
        if task_name not in self.start_times:
            return 0.0
        duration = time.time() - self.start_times[task_name]
        self.timings[task_name] = duration
        return duration
    
    def report(self) -> str:
        """Generate performance report"""
        total = sum(self.timings.values())
        
        report = "\n" + "="*80 + "\n"
        report += "PERFORMANCE REPORT\n"
        report += "="*80 + "\n\n"
        
        # Sort by duration (longest first)
        sorted_timings = sorted(self.timings.items(), key=lambda x: x[1], reverse=True)
        
        for task, duration in sorted_timings:
            percentage = (duration / total * 100) if total > 0 else 0
            report += f"  {task:.<50} {duration:>6.2f}s ({percentage:>5.1f}%)\n"
        
        report += "\n" + "-"*80 + "\n"
        report += f"  {'TOTAL':.<50} {total:>6.2f}s (100.0%)\n"
        report += "="*80 + "\n"
        
        # Performance assessment
        if total <= 7.0:
            status = "✅ EXCELLENT"
            color = "green"
        elif total <= 10.0:
            status = "✅ GOOD"
            color = "yellow"
        elif total <= 15.0:
            status = "⚠️  ACCEPTABLE"
            color = "orange"
        else:
            status = "❌ NEEDS OPTIMIZATION"
            color = "red"
        
        report += f"\n{status}: Total time {total:.2f}s (Target: 5-7s)\n"
        
        return report


def prepare_minimal_chart_data(context: dict) -> dict:
    """Prepare chart data efficiently"""
    chart_data = {}
    
    # Extract core data
    finance = context.get('finance', {})
    capex_krw = finance.get('capex', {}).get('total_krw', 1250.0)
    npv_krw = finance.get('npv_public_krw', 250.0)
    irr_pct = finance.get('irr_public_pct', 5.8)
    payback = finance.get('payback_period_years', 12.5)
    
    site = context.get('site', {})
    address = site.get('address', '역삼동 737번지')
    land_area = site.get('land_area_sqm', 800)
    
    # 1. Gantt Chart milestones
    chart_data['milestones'] = [
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
    
    # 2. NPV Tornado Chart
    chart_data['base_npv'] = npv_krw
    chart_data['sensitivity_data'] = {
        '분양가/임대료': {'low': npv_krw - 70, 'high': npv_krw + 70},
        '건축비': {'low': npv_krw + 60, 'high': npv_krw - 60},
        '토지비': {'low': npv_krw + 40, 'high': npv_krw - 40},
        '할인율': {'low': npv_krw + 30, 'high': npv_krw - 30},
        '공실률': {'low': npv_krw + 20, 'high': npv_krw - 20},
        '관리비': {'low': npv_krw + 10, 'high': npv_krw - 10},
    }
    
    # 3. Financial Scorecard
    roi = (npv_krw / capex_krw) * 100 if capex_krw > 0 else 0
    grade = 'A-' if npv_krw > 200 and irr_pct > 5 else 'B+' if npv_krw > 100 else 'B'
    
    chart_data['kpis'] = {
        'capex': capex_krw,
        'npv': npv_krw,
        'irr': irr_pct,
        'payback': payback,
        'roi': roi,
        'grade': grade
    }
    
    # 4. Competitive Analysis
    total_units = int(land_area / 40)
    chart_data['current_project'] = {
        'name': f'{address} (당사 사업지)',
        'price': 2800,
        'distance': 0.0,
        'units': total_units,
        'completion': '2028'
    }
    chart_data['competitors'] = [
        {'name': '강남구 A 프로젝트', 'price': 3200, 'distance': 1.2, 'units': 150, 'completion': '2027'},
        {'name': '서초구 B 프로젝트', 'price': 2900, 'distance': 2.5, 'units': 180, 'completion': '2027'},
        {'name': '강남구 C 프로젝트', 'price': 3500, 'distance': 0.8, 'units': 200, 'completion': '2026'},
        {'name': '송파구 D 프로젝트', 'price': 2600, 'distance': 3.0, 'units': 100, 'completion': '2028'},
    ]
    
    # 5. 30-Year Cashflow
    years_30 = list(range(30))
    revenues_30, expenses_30 = [], []
    for year in years_30:
        if year < 3:
            revenues_30.append(0)
            expenses_30.append(400)
        else:
            revenues_30.append(80 + (year - 3) * 2)
            expenses_30.append(30 + (year - 3) * 0.5)
    
    chart_data['years_30'] = years_30
    chart_data['revenues_30'] = revenues_30
    chart_data['expenses_30'] = expenses_30
    chart_data['net_cashflows_30'] = [r - e for r, e in zip(revenues_30, expenses_30)]
    
    # 6-11. Legacy charts
    chart_data['capex_breakdown'] = {
        '토지비': capex_krw * 0.4,
        '건축비': capex_krw * 0.35,
        '설계비': capex_krw * 0.1,
        '금융비용': capex_krw * 0.1,
        '기타': capex_krw * 0.05
    }
    chart_data['years'] = list(range(1, 11))
    chart_data['cashflows'] = [cf * 100 for cf in [-400, -300, -200, 50, 80, 90, 95, 100, 105, 110]]
    chart_data['base_irr'] = irr_pct
    chart_data['optimistic_irr'] = irr_pct + 0.5
    chart_data['pessimistic_irr'] = irr_pct - 0.5
    chart_data['revenues'] = [80, 85, 88, 90, 92, 94, 96, 98, 100, 102]
    chart_data['opex'] = [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
    chart_data['zerosite_value'] = capex_krw * 0.9
    chart_data['market_avg'] = capex_krw * 1.1
    chart_data['demand_scores'] = {
        '청년': 65.0,
        '신혼부부': 72.0,
        '고령자': 58.0,
        '일반': 60.0
    }
    
    return chart_data


def generate_charts_sequential(chart_data: dict, output_dir: Path, perf: PerformanceMeasurement) -> dict:
    """Generate all 11 charts sequentially (current method)"""
    charts = {}
    generator = ChartGenerator()
    
    # Phase B charts
    perf.start("chart_gantt")
    charts['gantt_chart'] = generator.generate_gantt_chart(
        chart_data['milestones'], output_dir / 'gantt_chart.png'
    )
    perf.end("chart_gantt")
    
    perf.start("chart_tornado")
    charts['npv_tornado'] = generator.generate_npv_tornado_chart(
        chart_data['sensitivity_data'],
        chart_data['base_npv'],
        output_dir / 'npv_tornado.png'
    )
    perf.end("chart_tornado")
    
    perf.start("chart_scorecard")
    charts['financial_scorecard'] = generator.generate_financial_scorecard(
        chart_data['kpis'], output_dir / 'financial_scorecard.png'
    )
    perf.end("chart_scorecard")
    
    perf.start("chart_competitive")
    charts['competitive_analysis'] = generator.generate_competitive_analysis_table(
        chart_data['competitors'],  # List that includes current project
        chart_data['current_project'],
        output_dir / 'competitive_analysis.png'
    )
    perf.end("chart_competitive")
    
    perf.start("chart_cashflow_30y")
    charts['30year_cashflow'] = generator.generate_30year_cashflow_chart(
        chart_data['years_30'],
        chart_data['revenues_30'],
        chart_data['expenses_30'],
        chart_data['net_cashflows_30'],
        output_dir / '30year_cashflow.png'
    )
    perf.end("chart_cashflow_30y")
    
    # Phase A legacy charts
    perf.start("chart_capex_breakdown")
    charts['capex_breakdown'] = generator.generate_capex_breakdown_pie(
        chart_data['capex_breakdown'], output_dir / 'capex_breakdown.png'
    )
    perf.end("chart_capex_breakdown")
    
    perf.start("chart_npv_curve")
    charts['npv_curve'] = generator.generate_npv_discount_curve(
        chart_data['years'], chart_data['cashflows'], 0.02, output_dir / 'npv_curve.png'
    )
    perf.end("chart_npv_curve")
    
    perf.start("chart_irr_sensitivity")
    charts['irr_sensitivity'] = generator.generate_irr_sensitivity_table(
        chart_data['base_irr'],
        chart_data['optimistic_irr'],
        chart_data['pessimistic_irr'],
        output_dir / 'irr_sensitivity.png'
    )
    perf.end("chart_irr_sensitivity")
    
    perf.start("chart_opex_revenue")
    charts['opex_revenue'] = generator.generate_opex_revenue_timeline(
        chart_data['years'], chart_data['revenues'], chart_data['opex'],
        output_dir / 'opex_revenue.png'
    )
    perf.end("chart_opex_revenue")
    
    perf.start("chart_market_signal")
    charts['market_signal'] = generator.generate_market_signal_gauge(
        chart_data['zerosite_value'],
        chart_data['market_avg'],
        output_dir / 'market_signal.png'
    )
    perf.end("chart_market_signal")
    
    perf.start("chart_demand_score")
    charts['demand_score'] = generator.generate_demand_score_bar(
        chart_data['demand_scores'], output_dir / 'demand_score.png'
    )
    perf.end("chart_demand_score")
    
    return charts


def test_current_performance():
    """Measure current performance (baseline)"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "Phase C.1: Performance Optimization Test" + " "*22 + "║")
    print("║" + " "*20 + "Current Performance Measurement" + " "*26 + "║")
    print("╚" + "="*78 + "╝")
    
    perf = PerformanceMeasurement()
    
    # Test parameters
    test_address = "서울특별시 강남구 역삼동 737"
    test_land_area = 800.0
    test_coords = (37.5, 127.0)
    
    print(f"\n📍 Test Project: {test_address} ({test_land_area}㎡)")
    
    try:
        # TOTAL TIMER START
        perf.start("TOTAL")
        
        # Step 1: Context Building
        perf.start("1. Context Building")
        builder = ReportContextBuilder()
        context = builder.build_expert_context(
            address=test_address,
            land_area_sqm=test_land_area,
            coordinates=test_coords
        )
        duration_context = perf.end("1. Context Building")
        print(f"✅ Context built in {duration_context:.2f}s ({len(context)} sections)")
        
        # Step 2: Narrative Generation
        perf.start("2. Narrative Generation")
        interpreter = NarrativeInterpreter()
        narratives = interpreter.generate_all_narratives(context)
        duration_narrative = perf.end("2. Narrative Generation")
        total_chars = sum(len(str(v)) for v in narratives.values())
        print(f"✅ Narratives generated in {duration_narrative:.2f}s ({total_chars} chars)")
        
        context['narratives'] = narratives
        
        # Step 3: Chart Data Preparation
        perf.start("3. Chart Data Prep")
        chart_data = prepare_minimal_chart_data(context)
        duration_prep = perf.end("3. Chart Data Prep")
        print(f"✅ Chart data prepared in {duration_prep:.2f}s")
        
        # Step 4: Chart Generation (Sequential - Current Method)
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        perf.start("4. Chart Generation (Sequential)")
        charts = generate_charts_sequential(chart_data, output_dir, perf)
        duration_charts = perf.end("4. Chart Generation (Sequential)")
        print(f"✅ All 11 charts generated in {duration_charts:.2f}s")
        
        context['charts'] = charts
        
        # Step 5: Template Rendering
        perf.start("5. Template Rendering")
        env = Environment(loader=FileSystemLoader('app/services_v13/report_full'))
        template = env.get_template('lh_expert_edition_v3.html.jinja2')
        flat_context = _flatten_context_for_template(context, test_land_area)
        html_output = template.render(**flat_context)
        duration_render = perf.end("5. Template Rendering")
        print(f"✅ Template rendered in {duration_render:.2f}s")
        
        # Step 6: File Writing
        perf.start("6. File Writing")
        output_path = Path('output/phase_c1_performance_test.html')
        output_path.write_text(html_output, encoding='utf-8')
        duration_write = perf.end("6. File Writing")
        print(f"✅ HTML saved in {duration_write:.2f}s ({len(html_output)/1024:.1f}KB)")
        
        # TOTAL TIMER END
        total_time = perf.end("TOTAL")
        
        # Performance Report
        print(perf.report())
        
        # Optimization Recommendations
        print("\n" + "="*80)
        print("OPTIMIZATION RECOMMENDATIONS")
        print("="*80)
        
        chart_time = duration_charts
        if chart_time > 2.0:
            print(f"🔧 Chart generation: {chart_time:.2f}s → Target: <1.5s")
            print(f"   → Implement parallel generation (ThreadPoolExecutor)")
            print(f"   → Expected speedup: {chart_time/1.5:.1f}x faster")
        
        if duration_context > 3.0:
            print(f"🔧 Context building: {duration_context:.2f}s → Target: <2.5s")
            print(f"   → Cache API responses")
            print(f"   → Optimize data processing")
        
        if duration_render > 1.0:
            print(f"🔧 Template rendering: {duration_render:.2f}s → Target: <0.8s")
            print(f"   → Pre-compile template")
            print(f"   → Optimize Jinja2 filters")
        
        print("\n" + "="*80)
        print(f"🎯 NEXT STEP: Implement parallel chart generation")
        print(f"   Current: {chart_time:.2f}s (sequential)")
        print(f"   Target: <1.5s (parallel with ThreadPoolExecutor)")
        print("="*80)
        
        return True, total_time, perf.timings
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0, {}


def test_parallel_performance():
    """Test performance with parallel chart generation"""
    from app.services_v13.report_full.charts_full import generate_all_financial_charts_parallel
    
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*13 + "Phase C.1: Parallel Chart Generation Test" + " "*22 + "║")
    print("║" + " "*18 + "Testing ThreadPoolExecutor Optimization" + " "*19 + "║")
    print("╚" + "="*78 + "╝")
    
    perf = PerformanceMeasurement()
    
    # Test parameters
    test_address = "서울특별시 강남구 역삼동 737"
    test_land_area = 800.0
    test_coords = (37.5, 127.0)
    
    print(f"\n📍 Test Project: {test_address} ({test_land_area}㎡)")
    
    try:
        # TOTAL TIMER START
        perf.start("TOTAL_PARALLEL")
        
        # Step 1: Context Building
        perf.start("1. Context Building")
        builder = ReportContextBuilder()
        context = builder.build_expert_context(
            address=test_address,
            land_area_sqm=test_land_area,
            coordinates=test_coords
        )
        duration_context = perf.end("1. Context Building")
        print(f"✅ Context built in {duration_context:.2f}s ({len(context)} sections)")
        
        # Step 2: Narrative Generation
        perf.start("2. Narrative Generation")
        interpreter = NarrativeInterpreter()
        narratives = interpreter.generate_all_narratives(context)
        duration_narrative = perf.end("2. Narrative Generation")
        total_chars = sum(len(str(v)) for v in narratives.values())
        print(f"✅ Narratives generated in {duration_narrative:.2f}s ({total_chars} chars)")
        
        context['narratives'] = narratives
        
        # Step 3: Chart Data Preparation
        perf.start("3. Chart Data Prep")
        chart_data = prepare_minimal_chart_data(context)
        duration_prep = perf.end("3. Chart Data Prep")
        print(f"✅ Chart data prepared in {duration_prep:.2f}s")
        
        # Step 4: Chart Generation (PARALLEL - Optimized Method)
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
        perf.start("4. Chart Generation (Parallel)")
        charts = generate_all_financial_charts_parallel(
            chart_data, output_dir, max_workers=4
        )
        duration_charts = perf.end("4. Chart Generation (Parallel)")
        print(f"✅ All 11 charts generated in {duration_charts:.2f}s (PARALLEL)")
        
        context['charts'] = charts
        
        # Step 5: Template Rendering
        perf.start("5. Template Rendering")
        env = Environment(loader=FileSystemLoader('app/services_v13/report_full'))
        template = env.get_template('lh_expert_edition_v3.html.jinja2')
        flat_context = _flatten_context_for_template(context, test_land_area)
        html_output = template.render(**flat_context)
        duration_render = perf.end("5. Template Rendering")
        print(f"✅ Template rendered in {duration_render:.2f}s")
        
        # Step 6: File Writing
        perf.start("6. File Writing")
        output_path = Path('output/phase_c1_parallel_test.html')
        output_path.write_text(html_output, encoding='utf-8')
        duration_write = perf.end("6. File Writing")
        print(f"✅ HTML saved in {duration_write:.2f}s ({len(html_output)/1024:.1f}KB)")
        
        # TOTAL TIMER END
        total_time = perf.end("TOTAL_PARALLEL")
        
        # Performance Report
        print(perf.report())
        
        return True, total_time, duration_charts
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, 0, 0


if __name__ == "__main__":
    # Test 1: Sequential (baseline)
    print("\n🔷 TEST 1: SEQUENTIAL CHART GENERATION (Baseline)")
    print("="*80)
    success_seq, total_seq, timings_seq = test_current_performance()
    
    if not success_seq:
        print("\n❌ Sequential test failed!")
        sys.exit(1)
    
    chart_time_seq = timings_seq.get("4. Chart Generation (Sequential)", 0)
    
    # Test 2: Parallel (optimized)
    print("\n\n🔷 TEST 2: PARALLEL CHART GENERATION (Optimized)")
    print("="*80)
    success_par, total_par, chart_time_par = test_parallel_performance()
    
    if not success_par:
        print("\n❌ Parallel test failed!")
        sys.exit(1)
    
    # Performance Comparison
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PERFORMANCE COMPARISON SUMMARY" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\n{'Metric':<30} {'Sequential':<15} {'Parallel':<15} {'Speedup':>10}")
    print("-" * 80)
    print(f"{'Total Time':<30} {total_seq:>6.2f}s{'':<8} {total_par:>6.2f}s{'':<8} {total_seq/total_par:>9.2f}x")
    print(f"{'Chart Generation':<30} {chart_time_seq:>6.2f}s{'':<8} {chart_time_par:>6.2f}s{'':<8} {chart_time_seq/chart_time_par:>9.2f}x")
    print("-" * 80)
    
    improvement = ((total_seq - total_par) / total_seq) * 100
    print(f"\n🚀 OPTIMIZATION RESULTS:")
    print(f"   - Total time improved by {improvement:.1f}%")
    print(f"   - Chart generation {chart_time_seq/chart_time_par:.1f}x faster")
    
    if total_par <= 5.0:
        status = "🎉 EXCELLENT"
    elif total_par <= 7.0:
        status = "✅ TARGET MET"
    else:
        status = "⚠️  ACCEPTABLE"
    
    print(f"\n{status}: Parallel version {total_par:.2f}s (Target: 5-7s)")
    
    if total_par <= 7.0:
        print("\n✅ Phase C.1: Performance Optimization COMPLETE!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Further optimization needed: {total_par:.2f}s > 7s")
        sys.exit(1)
