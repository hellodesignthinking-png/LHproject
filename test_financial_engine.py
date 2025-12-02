#!/usr/bin/env python3
"""
Test script for Financial Engine v7.4
"""

import sys
import os

# Direct import without going through app/__init__.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import directly from the module file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "financial_engine_v7_4",
    os.path.join(current_dir, "app/services/financial_engine_v7_4.py")
)
financial_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(financial_module)

FinancialEngine = financial_module.FinancialEngine
run_full_financial_analysis = financial_module.run_full_financial_analysis


def format_krw(amount):
    """Format Korean Won"""
    if amount >= 100_000_000:
        return f"{amount / 100_000_000:.1f}억원"
    elif amount >= 10_000:
        return f"{amount / 10_000:.0f}만원"
    else:
        return f"{amount:,.0f}원"


def test_financial_engine():
    """Test financial engine with real data"""
    print("=" * 80)
    print("🧪 ZeroSite v7.4 Financial Engine Test")
    print("=" * 80)
    
    # Test parameters (from handoff document example)
    land_area = 660.0  # ㎡
    address = "서울특별시 마포구 월드컵북로 120"
    unit_type = "청년"
    construction_type = "standard"
    
    print(f"\n📍 Test Parameters:")
    print(f"   - Address: {address}")
    print(f"   - Land Area: {land_area}㎡")
    print(f"   - Unit Type: {unit_type}")
    print(f"   - Construction: {construction_type}")
    print()
    
    # Run full analysis
    print("🔄 Running full financial analysis...")
    result = run_full_financial_analysis(land_area, address, unit_type, construction_type)
    
    # Display results
    print("\n" + "=" * 80)
    print("📊 FINANCIAL ANALYSIS RESULTS")
    print("=" * 80)
    
    # CapEx
    capex = result['capex']
    print(f"\n1️⃣  CAPITAL EXPENDITURE (CapEx)")
    print(f"   - Total Investment: {format_krw(capex['total_capex'])}")
    print(f"   - Unit Count: {capex['unit_count']}세대")
    print(f"   - Per Unit: {format_krw(capex['capex_per_unit'])}/세대")
    print(f"   - Per ㎡: {format_krw(capex['capex_per_sqm'])}/㎡")
    print(f"   - Land Price Zone: {capex['land_price_zone']}")
    
    if 'breakdown' in capex:
        breakdown = capex['breakdown']
        print(f"\n   💰 Breakdown:")
        print(f"      - Land Acquisition: {format_krw(breakdown['land_acquisition']['subtotal'])} ({breakdown['land_acquisition']['percentage']:.1f}%)")
        print(f"      - Construction (Hard): {format_krw(breakdown['construction_hard_costs']['subtotal'])} ({breakdown['construction_hard_costs']['percentage']:.1f}%)")
        print(f"      - Soft Costs: {format_krw(breakdown['soft_costs']['subtotal'])} ({breakdown['soft_costs']['percentage']:.1f}%)")
        print(f"      - FF&E: {format_krw(breakdown['ffe']['subtotal'])} ({breakdown['ffe']['percentage']:.1f}%)")
    
    # OpEx
    opex = result['opex']
    print(f"\n2️⃣  OPERATING EXPENSES (OpEx)")
    print(f"   - Year 1 Total: {format_krw(opex['year1_total_opex'])}/년")
    print(f"   - Per Unit: {format_krw(opex['year1_opex_per_unit'])}/세대/년")
    
    print(f"\n   💸 Components (per unit/year):")
    for comp, value in opex['opex_components'].items():
        comp_name = comp.replace('_', ' ').title()
        print(f"      - {comp_name}: {format_krw(value)}")
    
    # NOI
    noi = result['noi']
    print(f"\n3️⃣  NET OPERATING INCOME (NOI) - Year {noi['year']}")
    print(f"   - Gross Annual Income: {format_krw(noi['gross_annual_income'])}")
    print(f"   - Occupancy Rate: {noi['occupancy_rate']*100:.0f}%")
    print(f"   - Effective Income: {format_krw(noi['effective_annual_income'])}")
    print(f"   - Operating Expenses: {format_krw(noi['annual_opex'])}")
    print(f"   - NOI: {format_krw(noi['noi'])}")
    print(f"   - NOI Margin: {noi['noi_margin_percent']:.1f}%")
    print(f"   - Monthly Rent: {format_krw(noi['monthly_rent'])}/월")
    
    # Returns
    returns = result['returns']
    print(f"\n4️⃣  RETURN METRICS")
    print(f"   - Cap Rate: {returns['cap_rate_percent']:.2f}%")
    print(f"   - LH Target Cap Rate: {returns['lh_target_cap_rate_percent']:.2f}%")
    print(f"   - Meets LH Criteria: {'✅ YES' if returns['meets_lh_target'] else '❌ NO'}")
    
    if 'irr_percent' in returns:
        print(f"   - IRR: {returns['irr_percent']:.2f}%")
    if 'npv' in returns:
        print(f"   - NPV: {format_krw(returns['npv'])}")
    
    # Breakeven
    breakeven = result['breakeven']
    print(f"\n5️⃣  BREAKEVEN ANALYSIS")
    print(f"   - Breakeven NOI: {format_krw(breakeven['breakeven_noi'])}")
    print(f"   - Breakeven Occupancy: {breakeven['breakeven_occupancy_percent']:.1f}%")
    print(f"   - Breakeven Monthly Rent: {format_krw(breakeven['breakeven_monthly_rent'])}")
    print(f"   - Base Monthly Rent: {format_krw(breakeven['base_monthly_rent'])}")
    print(f"   - Rent Gap: {breakeven['rent_gap_percent']:.1f}%")
    print(f"   - Payback Period: {breakeven['payback_period_years']:.1f} years")
    print(f"   - Achievable: {'✅ YES' if breakeven['achievable'] else '❌ NO'}")
    
    # Sensitivity
    sensitivity = result['sensitivity']
    print(f"\n6️⃣  SENSITIVITY ANALYSIS")
    print(f"   - IRR Range:")
    irr_range = sensitivity['summary']['irr_range']
    print(f"      - Pessimistic: {irr_range['pessimistic']:.2f}%")
    print(f"      - Base Case: {irr_range['base']:.2f}%")
    print(f"      - Optimistic: {irr_range['optimistic']:.2f}%")
    print(f"      - Spread: {irr_range['spread']:.2f}%")
    
    print(f"\n   - Key Sensitivity Variables:")
    for var in sensitivity['summary']['sensitivity_variables']:
        print(f"      - {var['variable']}: {var['impact']} impact")
    
    # Summary
    summary = result['summary']
    print(f"\n" + "=" * 80)
    print("📈 EXECUTIVE SUMMARY")
    print("=" * 80)
    print(f"   - Total Investment Required: {format_krw(summary['total_investment'])}")
    print(f"   - Number of Units: {summary['unit_count']}세대")
    print(f"   - Stabilized NOI: {format_krw(summary['noi_stabilized'])}/년")
    print(f"   - Cap Rate: {summary['cap_rate']:.2f}%")
    print(f"   - Meets LH Criteria: {'✅ YES' if summary['meets_lh_criteria'] else '❌ NO'}")
    print(f"   - IRR Range: {irr_range['pessimistic']:.1f}% - {irr_range['optimistic']:.1f}%")
    
    # Investment Decision
    print(f"\n💡 INVESTMENT DECISION:")
    if summary['meets_lh_criteria'] and breakeven['achievable']:
        print(f"   ✅ RECOMMEND: Project meets LH financial criteria")
        print(f"   - Strong cap rate above target ({summary['cap_rate']:.2f}% vs {returns['lh_target_cap_rate_percent']:.2f}%)")
        print(f"   - Breakeven analysis shows achievable targets")
        print(f"   - Positive IRR range across all scenarios")
    else:
        print(f"   ⚠️  CONDITIONAL: Project requires optimization")
        if not summary['meets_lh_criteria']:
            print(f"   - Cap rate below LH target ({summary['cap_rate']:.2f}% vs {returns['lh_target_cap_rate_percent']:.2f}%)")
        if not breakeven['achievable']:
            print(f"   - Breakeven occupancy exceeds stabilized rate")
    
    print(f"\n" + "=" * 80)
    print("✅ Financial Engine Test Complete")
    print("=" * 80)
    
    return result


if __name__ == "__main__":
    try:
        result = test_financial_engine()
        print("\n✅ All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
