"""
Test Phase 1 Implementation
===========================
Verify all 5 tasks are working:
1. Executive Summary Scorecard
2. 5-Scenario Sensitivity Analysis
3. NPV Tornado Diagram
4. 30-Year Cash Flow Statement
5. Financial Ratios (DSCR, LTV, ROI, ROE)
"""

from app.services_v13.report_full.report_context_builder import ReportContextBuilder

# Initialize builder
builder = ReportContextBuilder()

# Test case
address = '서울시 강남구 역삼동 123'
land_area_sqm = 500.0

# Generate Expert Context (with Phase 1 additions)
print("=" * 80)
print("🚀 Testing Phase 1 Implementation (Tasks 1.1-1.5)")
print("=" * 80)
print(f"📍 Test Address: {address}")
print(f"📐 Land Area: {land_area_sqm}㎡")
print()

context = builder.build_expert_context(
    address=address,
    land_area_sqm=land_area_sqm
)

print("✅ Context Built Successfully!")
print(f"   Total Sections: {len(context)}")
print()

# Test 1.1: Executive Summary Scorecard
if 'executive_summary' in context:
    exec_summary = context['executive_summary']
    scorecard = exec_summary['scorecard']
    print('✅ TASK 1.1: Executive Summary Scorecard')
    print(f'   Overall Score: {scorecard["overall"]["score"]:.1f} ({scorecard["overall"]["grade"]})')
    print(f'   Recommendation: {scorecard["overall"]["recommendation"]}')
    print(f'   Confidence: {scorecard["overall"]["confidence"]}')
    print(f'   ')
    print(f'   Category Scores:')
    print(f'     Location: {scorecard["location"]["score"]:.1f} ({scorecard["location"]["grade"]})')
    print(f'     Finance:  {scorecard["finance"]["score"]:.1f} ({scorecard["finance"]["grade"]})')
    print(f'     Market:   {scorecard["market"]["score"]:.1f} ({scorecard["market"]["grade"]})')
    print(f'     Risk:     {scorecard["risk"]["score"]:.1f} ({scorecard["risk"]["grade"]})')
    print(f'     Policy:   {scorecard["policy"]["score"]:.1f} ({scorecard["policy"]["grade"]})')
    print()
else:
    print('❌ TASK 1.1: Executive Summary MISSING')
    print()

# Test 1.2: 5-Scenario Sensitivity Analysis
if 'scenario_comparison' in context:
    scenarios = context['scenario_comparison']
    print('✅ TASK 1.2: 5-Scenario Sensitivity Analysis')
    print(f'   Best Case NPV:    {scenarios["best_case"]["npv_public"]/1e8:8.1f}억원 ({scenarios["best_case"]["scenario_name"]})')
    print(f'   Optimistic NPV:   {scenarios["optimistic"]["npv_public"]/1e8:8.1f}억원 ({scenarios["optimistic"]["scenario_name"]})')
    print(f'   Base NPV:         {scenarios["base"]["npv_public"]/1e8:8.1f}억원 ({scenarios["base"]["scenario_name"]})')
    print(f'   Pessimistic NPV:  {scenarios["pessimistic"]["npv_public"]/1e8:8.1f}억원 ({scenarios["pessimistic"]["scenario_name"]})')
    print(f'   Worst Case NPV:   {scenarios["worst_case"]["npv_public"]/1e8:8.1f}억원 ({scenarios["worst_case"]["scenario_name"]})')
    print(f'   ')
    print(f'   NPV Range: {scenarios["comparison_table"]["npv_range"]["span_kr"]}')
    print(f'   Recommendation: {scenarios["comparison_table"]["recommendation"]}')
    print()
else:
    print('❌ TASK 1.2: Scenario Comparison MISSING')
    print()

# Test 1.3: NPV Tornado Diagram
if 'scenario_comparison' in context and 'tornado_diagram' in context['scenario_comparison']:
    tornado = context['scenario_comparison']['tornado_diagram']
    print('✅ TASK 1.3: NPV Tornado Diagram')
    print(f'   Top 3 Variables: {", ".join(tornado["summary"]["top_impact_variables"])}')
    print(f'   Total Potential Swing: {tornado["summary"]["total_potential_swing_kr"]}')
    print(f'   ')
    print(f'   Variable Impact Rankings:')
    for i, var in enumerate(tornado['variables'][:3], 1):
        print(f'     {i}. {var["name_kr"]}: {var["npv_swing_kr"]} ({var["impact_pct"]:.1f}% impact)')
    print(f'   ')
    print(f'   Recommendation: {tornado["summary"]["recommendation"]}')
    print()
else:
    print('❌ TASK 1.3: Tornado Diagram MISSING')
    print()

# Test 1.4: 30-Year Cash Flow Statement
if 'finance' in context and 'cashflow' in context['finance']:
    cashflow = context['finance']['cashflow']
    print('✅ TASK 1.4: 30-Year Cash Flow Statement')
    print(f'   Cash Flow Periods: {len(cashflow)} years')
    print(f'   ')
    print(f'   Sample Cash Flows:')
    print(f'     Year  1: {cashflow[0]["cf"]/1e8:6.2f}억원 (Cumulative: {cashflow[0]["cumulative"]/1e8:7.1f}억원)')
    print(f'     Year 10: {cashflow[9]["cf"]/1e8:6.2f}억원 (Cumulative: {cashflow[9]["cumulative"]/1e8:7.1f}억원)')
    print(f'     Year 20: {cashflow[19]["cf"]/1e8:6.2f}억원 (Cumulative: {cashflow[19]["cumulative"]/1e8:7.1f}억원)')
    print(f'     Year 30: {cashflow[29]["cf"]/1e8:6.2f}억원 (Cumulative: {cashflow[29]["cumulative"]/1e8:7.1f}억원)')
    print()
else:
    print('❌ TASK 1.4: 30-Year Cash Flow MISSING')
    print()

# Test 1.5: Financial Ratios
if 'finance' in context and 'ratios' in context['finance']:
    ratios = context['finance']['ratios']
    print('✅ TASK 1.5: Key Financial Ratios')
    print(f'   ')
    print(f'   DSCR (부채상환비율):')
    print(f'     Value: {ratios["dscr"]["value"]} ({ratios["dscr"]["grade"]} 등급)')
    print(f'     {ratios["dscr"]["interpretation"]}')
    print(f'     Benchmark: {ratios["dscr"]["benchmark"]}')
    print(f'   ')
    print(f'   LTV (담보인정비율):')
    print(f'     Value: {ratios["ltv"]["value"]}% ({ratios["ltv"]["grade"]} 등급)')
    print(f'     Loan: {ratios["ltv"]["loan_amount_kr"]}, Equity: {ratios["ltv"]["equity_kr"]}')
    print(f'     {ratios["ltv"]["interpretation"]}')
    print(f'   ')
    print(f'   ROI (투자수익률):')
    print(f'     Annual: {ratios["roi"]["annual"]}% ({ratios["roi"]["grade"]} 등급)')
    print(f'     30-Year Cumulative: {ratios["roi"]["cumulative_30yr"]}%')
    print(f'     {ratios["roi"]["interpretation"]}')
    print(f'   ')
    print(f'   ROE (자기자본이익률):')
    print(f'     Annual: {ratios["roe"]["annual"]}% ({ratios["roe"]["grade"]} 등급)')
    print(f'     {ratios["roe"]["interpretation"]}')
    print(f'   ')
    print(f'   Additional Ratios:')
    print(f'     Cap Rate: {ratios["cap_rate"]["value"]}%')
    print(f'     OER: {ratios["oer"]["value"]}%')
    print(f'     Annual Debt Service: {ratios["debt_service"]["annual_kr"]}')
    print()
else:
    print('❌ TASK 1.5: Financial Ratios MISSING')
    print()

print("=" * 80)
print("🎉 Phase 1 Testing Complete!")
print("=" * 80)
print()
print("Summary:")
print("  1.1 Executive Summary Scorecard:   " + ("✅" if 'executive_summary' in context else "❌"))
print("  1.2 5-Scenario Analysis:          " + ("✅" if 'scenario_comparison' in context and 'best_case' in context['scenario_comparison'] else "❌"))
print("  1.3 NPV Tornado Diagram:          " + ("✅" if 'scenario_comparison' in context and 'tornado_diagram' in context['scenario_comparison'] else "❌"))
print("  1.4 30-Year Cash Flow:            " + ("✅" if 'finance' in context and len(context['finance'].get('cashflow', [])) == 30 else "❌"))
print("  1.5 Financial Ratios:             " + ("✅" if 'finance' in context and 'ratios' in context['finance'] else "❌"))
print()
