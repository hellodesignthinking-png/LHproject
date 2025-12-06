"""
Financial Engine Test
=====================

독립 테스트 - Phase 1 결과 없이도 동작 가능

Usage:
    python test_financial_engine.py
"""

import json
from app.services_v9.financial_engine import (
    FinancialEngine,
    FinancialInput,
    CalculationMode
)


def test_financial_engine():
    """Test financial engine with sample data"""
    
    print("="*80)
    print("🧪 Financial Engine Test")
    print("="*80)
    
    # Test data (from Phase 1 MVP result)
    input_data = FinancialInput(
        land_area=850.0,
        gross_floor_area=2125.0,
        residential_gfa=1806.25,
        unit_count=30,
        parking_count=30,
        zone_type="제2종일반주거지역",
        land_appraisal_price=4500000000,  # 45억
        construction_period=24,
        calculation_mode=CalculationMode.COST_INDEX,
        region="서울"
    )
    
    print("\n📥 Input Data:")
    print(f"   Land: {input_data.land_area}m²")
    print(f"   GFA: {input_data.gross_floor_area}m²")
    print(f"   Units: {input_data.unit_count}")
    print(f"   Zone: {input_data.zone_type}")
    print(f"   Region: {input_data.region}")
    
    # Run analysis
    print("\n🚀 Running Financial Analysis...")
    engine = FinancialEngine()
    result = engine.analyze(input_data)
    
    # Display results
    print("\n" + "="*80)
    print("📊 FINANCIAL ANALYSIS RESULTS")
    print("="*80)
    
    print("\n💰 CAPEX (Total Investment):")
    print(f"   Direct Construction: ₩{result.capex.direct_construction:,.0f}")
    print(f"   Indirect Cost: ₩{result.capex.indirect_cost:,.0f}")
    print(f"   Finance Cost: ₩{result.capex.finance_cost:,.0f}")
    print(f"   Land Cost: ₩{result.capex.land_cost:,.0f}")
    print(f"   ─────────────────────────────")
    print(f"   TOTAL CAPEX: ₩{result.capex.total_capex:,.0f}")
    
    print("\n🏠 Operating Expenses (Annual):")
    print(f"   Maintenance: ₩{result.opex.maintenance:,.0f}")
    print(f"   Management: ₩{result.opex.management:,.0f}")
    print(f"   Utilities: ₩{result.opex.utilities:,.0f}")
    print(f"   Insurance: ₩{result.opex.insurance:,.0f}")
    print(f"   Other: ₩{result.opex.other:,.0f}")
    print(f"   ─────────────────────────────")
    print(f"   TOTAL OPEX: ₩{result.opex.total_opex:,.0f}")
    
    print("\n💵 Revenue Structure (Annual):")
    print(f"   Rent/Unit: ₩{result.revenue.rent_per_unit:,.0f}/month")
    print(f"   Total Units: {result.revenue.total_units}")
    print(f"   Occupancy: {result.revenue.occupancy_rate:.0%}")
    print(f"   Gross Income: ₩{result.revenue.gross_income:,.0f}")
    print(f"   ─────────────────────────────")
    print(f"   NOI: ₩{result.revenue.net_operating_income:,.0f}")
    
    print("\n📈 Financial Metrics:")
    print(f"   ROI: {result.metrics.roi:.2%}")
    print(f"   IRR (10yr): {result.metrics.irr_10yr:.2%}")
    print(f"   Cap Rate: {result.metrics.cap_rate:.2%}")
    print(f"   Payback Period: {result.metrics.payback_period:.1f} years")
    
    print("\n🎯 LH Gap Analysis:")
    print(f"   Estimated LH Price: ₩{result.lh_gap.estimated_lh_price:,.0f}")
    print(f"   Total Project Cost: ₩{result.lh_gap.total_project_cost:,.0f}")
    print(f"   ─────────────────────────────")
    print(f"   Gap Amount: ₩{result.lh_gap.gap_amount:,.0f}")
    print(f"   Gap Ratio: {result.lh_gap.gap_ratio:.1f}%")
    print(f"   Profitable: {'✅ YES' if result.lh_gap.is_profitable else '❌ NO'}")
    
    print("\n🔍 Feasibility Assessment:")
    print(f"   Is Feasible: {'✅ YES' if result.is_feasible else '❌ NO'}")
    print(f"   Risk Level: {result.risk_level}")
    print(f"   Recommendation: {result.recommendation}")
    
    print("\n" + "="*80)
    print("✅ Test Complete!")
    print("="*80)
    
    # Export JSON
    print("\n📄 Exporting JSON...")
    json_output = result.model_dump_json(indent=2)
    with open('/tmp/financial_result.json', 'w', encoding='utf-8') as f:
        f.write(json_output)
    print("   ✅ Saved to: /tmp/financial_result.json")
    
    # Validation
    print("\n✔️ Validation:")
    assert result.capex.total_capex > 0, "CAPEX should be positive"
    assert result.revenue.net_operating_income != 0, "NOI should not be zero"
    assert result.metrics.roi is not None, "ROI should be calculated"
    assert result.lh_gap.gap_amount is not None, "LH Gap should be calculated"
    print("   ✅ All assertions passed")
    
    return result


if __name__ == "__main__":
    try:
        result = test_financial_engine()
        print("\n🎉 SUCCESS! Financial Engine is working correctly.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
