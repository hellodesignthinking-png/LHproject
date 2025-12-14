#!/usr/bin/env python3
"""
Financial Engine Debug Test
"""
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.services.financial_engine_v7_4 import FinancialEngine

def test_financial_engine():
    """Test financial engine with Mapo address"""
    
    engine = FinancialEngine()
    
    # Test parameters
    land_area = 660.0  # sqm
    address = "서울특별시 마포구 월드컵북로 120"
    unit_type = "youth"
    housing_type = "youth"
    
    print("=" * 80)
    print(f"🧪 Testing Financial Engine")
    print("=" * 80)
    print(f"📍 Address: {address}")
    print(f"📏 Land Area: {land_area} sqm")
    print(f"🏠 Unit Type: {unit_type}")
    print()
    
    # Run sensitivity analysis
    result = engine.run_sensitivity_analysis(
        land_area=land_area,
        address=address,
        unit_type=unit_type,
        construction_type='standard',
        housing_type=housing_type
    )
    
    # Extract base scenario
    base = result.get('base', {})
    
    print("📊 Base Scenario Results:")
    print("-" * 80)
    
    # CAPEX
    capex_data = base.get('capex', {})
    print(f"\n💰 CAPEX:")
    print(f"  - Total CAPEX: {capex_data.get('total_capex', 0):,.0f} 원 ({capex_data.get('total_capex', 0)/1e8:.1f}억)")
    print(f"  - Land Cost: {capex_data.get('land_cost', 0):,.0f} 원")
    print(f"  - Construction: {capex_data.get('construction_cost', 0):,.0f} 원")
    print(f"  - Unit Count: {capex_data.get('unit_count', 0)}")
    
    # OpEx
    opex_data = base.get('opex', {})
    print(f"\n💸 OpEx:")
    print(f"  - Year 1 Total OpEx: {opex_data.get('year1_total_opex', 0):,.0f} 원 ({opex_data.get('year1_total_opex', 0)/1e8:.2f}억)")
    
    # NOI
    noi_data = base.get('noi', {})
    print(f"\n📈 NOI:")
    print(f"  - NOI: {noi_data.get('noi', 0):,.0f} 원 ({noi_data.get('noi', 0)/1e8:.1f}억)")
    print(f"  - Gross Annual Income: {noi_data.get('gross_annual_income', 0):,.0f} 원")
    print(f"  - Effective Annual Income: {noi_data.get('effective_annual_income', 0):,.0f} 원")
    print(f"  - Occupancy Rate: {noi_data.get('occupancy_rate', 0)*100:.1f}%")
    print(f"  - Monthly Rent: {noi_data.get('monthly_rent', 0):,.0f} 원")
    
    # Return Metrics
    return_metrics = base.get('return_metrics', {})
    print(f"\n📊 Return Metrics:")
    print(f"  - IRR: {return_metrics.get('irr_percent', 0):.2f}%")
    print(f"  - NPV: {return_metrics.get('npv', 0):,.0f} 원")
    print(f"  - Cap Rate: {return_metrics.get('cap_rate_percent', 0):.2f}%")
    
    # Enhanced Metrics (if available)
    if 'npv_public' in return_metrics:
        print(f"\n💡 Enhanced Metrics:")
        print(f"  - NPV (Public): {return_metrics.get('npv_public', 0):,.0f} 원 ({return_metrics.get('npv_public', 0)/1e8:.1f}억)")
        print(f"  - NPV (Private): {return_metrics.get('npv_private', 0):,.0f} 원 ({return_metrics.get('npv_private', 0)/1e8:.1f}억)")
        print(f"  - Payback Period: {return_metrics.get('payback_period_years', 0):.1f} years")
        print(f"  - IRR (Public): {return_metrics.get('irr_public_percent', 0):.2f}%")
        print(f"  - IRR (Private): {return_metrics.get('irr_private_percent', 0):.2f}%")
    
    print("\n" + "=" * 80)
    print("✅ Test Complete")
    print("=" * 80)

if __name__ == "__main__":
    test_financial_engine()
