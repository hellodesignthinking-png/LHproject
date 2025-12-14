"""
Test Production API v13 with Expert Edition v3 Upgrade
Verifies that real financial values are generated
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.routers.report_v13 import router, _flatten_context_for_template
from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def test_production_context_generation():
    """Test that production API generates real values"""
    
    print("="*80)
    print("🧪 Testing Production API v13 Context Generation")
    print("="*80)
    print()
    
    # Test parameters (same as uploaded PDF)
    address = "월드컵북로 120"
    land_area_sqm = 660.0
    
    print(f"📍 Test Address: {address}")
    print(f"📐 Land Area: {land_area_sqm}㎡")
    print()
    
    # Step 1: Build context using Expert Edition v3
    print("⏳ Step 1/3: Building Expert Edition v3 Context...")
    builder = ReportContextBuilder()
    
    try:
        context = builder.build_expert_context(
            address=address,
            land_area_sqm=land_area_sqm
        )
        print(f"✅ Context built with {len(context.keys())} sections")
    except Exception as e:
        print(f"❌ Context build failed: {e}")
        return False
    
    # Step 2: Flatten context
    print()
    print("⏳ Step 2/3: Flattening context for template...")
    try:
        context = _flatten_context_for_template(context, land_area_sqm)
        print(f"✅ Context flattened")
    except Exception as e:
        print(f"❌ Context flattening failed: {e}")
        return False
    
    # Step 3: Verify values
    print()
    print("⏳ Step 3/3: Verifying financial values...")
    print()
    
    capex = context.get('capex_krw', 0)
    npv = context.get('npv_public_krw', 0)
    irr = context.get('irr_public_pct', 0)
    demand_score = context.get('demand_score', 0)
    market_signal = context.get('market_signal', 'N/A')
    
    print("="*80)
    print("📊 Generated Values:")
    print("="*80)
    print(f"💰 CAPEX (총 사업비): {capex:.2f}억원")
    print(f"📈 NPV (순현재가치): {npv:.2f}억원")
    print(f"📊 IRR (내부수익률): {irr:.2f}%")
    print(f"🏠 Demand Score: {demand_score:.1f}")
    print(f"📊 Market Signal: {market_signal}")
    print()
    
    # Validation
    print("="*80)
    print("✅ Validation:")
    print("="*80)
    
    success = True
    
    if capex == 0:
        print("❌ CAPEX = 0억원 (FAILED - should be > 0)")
        success = False
    else:
        print(f"✅ CAPEX = {capex:.2f}억원 (PASS)")
    
    if npv == 0:
        print("❌ NPV = 0억원 (FAILED - should be ≠ 0)")
        success = False
    else:
        print(f"✅ NPV = {npv:.2f}억원 (PASS)")
    
    if irr == 0:
        print("❌ IRR = 0% (FAILED - should be ≠ 0)")
        success = False
    else:
        print(f"✅ IRR = {irr:.2f}% (PASS)")
    
    if demand_score == 0:
        print("⚠️  Demand Score = 0 (WARNING - using default)")
    else:
        print(f"✅ Demand Score = {demand_score:.1f} (PASS)")
    
    print()
    print("="*80)
    if success:
        print("✅ ALL TESTS PASSED - Production API is FIXED!")
        print("="*80)
        print()
        print("🎯 Next Steps:")
        print("1. Commit changes to report_v13.py")
        print("2. Restart FastAPI server")
        print("3. Generate new PDF using POST /api/v13/report")
        print("4. Verify PDF shows real values (not 0억원)")
    else:
        print("❌ TESTS FAILED - Values are still 0")
        print("="*80)
    
    return success


if __name__ == "__main__":
    success = test_production_context_generation()
    sys.exit(0 if success else 1)
