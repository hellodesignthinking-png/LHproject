"""
Test script for ReportContextBuilder

Tests the comprehensive REPORT_CONTEXT structure with real data.
"""

import json
from app.services_v13.report_full.report_context_builder import ReportContextBuilder

def test_context_builder():
    """Test ReportContextBuilder with Gangnam test address"""
    
    print("🧪 Testing ReportContextBuilder...")
    print("=" * 80)
    
    # Test address
    address = "서울시 강남구 역삼동 123"
    land_area_sqm = 500.0
    coordinates = (37.5013, 127.0374)  # Gangnam coordinates
    
    # Build context
    builder = ReportContextBuilder()
    context = builder.build_context(
        address=address,
        land_area_sqm=land_area_sqm,
        coordinates=coordinates,
        multi_parcel=False,
        parcels=None,
        additional_params=None
    )
    
    print(f"\n✅ REPORT_CONTEXT generated successfully!")
    print(f"\n📊 Context Structure:")
    print(f"  - Metadata: {len(context['metadata'])} fields")
    print(f"  - Site: {len(context['site'])} fields")
    print(f"  - Zoning: {len(context['zoning'])} fields")
    print(f"  - Demand: {len(context['demand'])} fields")
    print(f"  - Market: {len(context['market'])} fields")
    print(f"  - Cost: {len(context['cost'])} fields")
    print(f"  - Finance: {len(context['finance'])} fields")
    print(f"  - Scenario Comparison: {len(context['scenario_comparison'])} scenarios")
    print(f"  - Risk Analysis: {len(context['risk_analysis'])} risk types")
    print(f"  - Decision: {context['decision']['recommendation']}")
    
    print(f"\n📋 Key Results:")
    print(f"  - Recommended Housing Type: {context['demand']['recommended_type_kr']} ({context['demand']['recommended_type']})")
    print(f"  - Demand Score: {context['demand']['overall_score']:.1f}")
    print(f"  - Market Signal: {context['market']['signal']} ({context['market']['delta_pct']:+.1f}%)")
    print(f"  - Construction Cost: {context['cost']['construction']['total'] / 1e8:.1f}억원")
    print(f"  - CAPEX Total: {context['finance']['capex']['total'] / 1e8:.1f}억원")
    print(f"  - NPV (Public): {context['finance']['npv']['public'] / 1e8:.1f}억원")
    print(f"  - IRR (Public): {context['finance']['irr']['public']:.2f}%")
    print(f"  - Payback Period: {context['finance']['payback']['years']:.1f} years")
    print(f"  - Overall Risk: {context['risk_analysis']['overall_level']}")
    print(f"  - Final Decision: {context['decision']['recommendation']} (confidence: {context['decision']['confidence']})")
    
    print(f"\n💡 Decision Reasoning:")
    for i, reason in enumerate(context['decision']['reasoning'], 1):
        print(f"  {i}. {reason}")
    
    print(f"\n🎯 Demand Reasoning:")
    for key, reason in context['demand']['reasoning'].items():
        print(f"  - {reason}")
    
    print(f"\n📈 Market Reasoning:")
    for key, reason in context['market']['reasoning'].items():
        print(f"  - {reason}")
    
    print(f"\n⚠️ Risk Analysis:")
    for risk_type in ['legal', 'market', 'construction', 'financial']:
        risk = context['risk_analysis'][risk_type]
        print(f"  - {risk_type.title()}: {risk['level']} - {risk['description']}")
    
    print(f"\n💰 Scenario Comparison:")
    for scenario_name in ['base', 'optimistic', 'pessimistic']:
        scenario = context['scenario_comparison'][scenario_name]
        print(f"  - {scenario_name.title()}:")
        print(f"      CAPEX: {scenario['capex'] / 1e8:.1f}억원")
        print(f"      NPV: {scenario['npv_public'] / 1e8:.1f}억원")
        print(f"      IRR: {scenario['irr']:.2f}%")
        if scenario_name != 'base':
            print(f"      Cost Change: {scenario['cost_change_pct']:+.1f}%")
    
    print(f"\n💵 Cash Flow (10-year):")
    for year_data in context['finance']['cashflow'][:5]:  # Show first 5 years
        print(f"  Year {year_data['year']}: CF = {year_data['cf'] / 1e8:.2f}억원, Cumulative = {year_data['cumulative'] / 1e8:.2f}억원")
    print(f"  ...")
    
    # Save to JSON for inspection
    output_path = "/tmp/report_context_test.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(context, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Full context saved to: {output_path}")
    print(f"\n✅ ReportContextBuilder test complete!")
    print("=" * 80)
    
    return context


if __name__ == "__main__":
    context = test_context_builder()
