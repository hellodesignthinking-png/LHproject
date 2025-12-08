#!/usr/bin/env python3
"""
ZeroSite v18 Integration Test
==============================
Test complete v18 integration with ReportContextBuilder and template
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_context_builder import ReportContextBuilder
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_v18_integration():
    """Test v18 transaction finance integration"""
    
    print("=" * 80)
    print("🧪 ZeroSite v18 Integration Test")
    print("=" * 80)
    
    # Test address
    test_address = '서울특별시 마포구 월드컵북로 120'
    
    try:
        # Initialize context builder
        logger.info("Initializing ReportContextBuilder...")
        builder = ReportContextBuilder()
        
        # Build context with v18 integration
        logger.info(f"Building context for: {test_address}")
        context = builder.build_context(
            address=test_address,
            land_area_sqm=660.0,
            additional_params={
                'appraisal_price': 10_000_000  # 1000만원/㎡
            }
        )
        
        # Check v18_transaction exists
        logger.info("Checking v18_transaction in context...")
        if 'v18_transaction' in context:
            v18 = context['v18_transaction']
            logger.info("✅ v18_transaction found!")
            
            # Print summary
            print("\n" + "=" * 80)
            print("📊 v18 Transaction Finance Results")
            print("=" * 80)
            
            if 'summary' in v18:
                summary = v18['summary']
                print(f"\n💰 Financial Summary:")
                print(f"   Total CAPEX: {summary.get('total_capex_krw', 'N/A')}")
                print(f"   LH Purchase Price: {summary.get('lh_purchase_price_krw', 'N/A')}")
                print(f"   Profit: {summary.get('profit_krw', 'N/A')}")
                print(f"   ROI: {summary.get('roi_display', 'N/A')}")
                print(f"   IRR: {summary.get('irr_display', 'N/A')}")
                print(f"   Payback: {summary.get('payback_display', 'N/A')}")
                print(f"   Decision: {summary.get('decision', 'N/A')}")
                print(f"   Reason: {summary.get('decision_reason', 'N/A')}")
            
            if 'capex_detail' in v18:
                print(f"\n🏗️  CAPEX Breakdown:")
                capex = v18['capex_detail']
                print(f"   Land Cost: {capex.get('land_cost_krw', 'N/A')}")
                print(f"   Construction Cost (indexed): {capex.get('indexed_construction_cost_krw', 'N/A')}")
                print(f"   Design Fee: {capex.get('design_cost_krw', 'N/A')}")
                print(f"   Total: {capex.get('total_capex_krw', 'N/A')}")
            
            if 'appraisal' in v18:
                print(f"\n🏛️  LH Appraisal:")
                appraisal = v18['appraisal']
                print(f"   Land Appraised: {appraisal.get('land_appraised_value_krw', 'N/A')}")
                print(f"   Building Appraised: {appraisal.get('building_appraised_value_krw', 'N/A')}")
                print(f"   Final Appraisal: {appraisal.get('final_appraisal_value_krw', 'N/A')}")
            
            if 'sensitivity' in v18 and 'results' in v18['sensitivity']:
                print(f"\n📈 Sensitivity Analysis:")
                for result in v18['sensitivity']['results'][:3]:  # Show first 3
                    print(f"   {result.get('variable', 'N/A')} {result.get('variation', 'N/A')}: "
                          f"ROI={result.get('roi_pct', 0):.2f}%, "
                          f"IRR={result.get('irr_pct', 0):.2f}%")
            
            print("\n✅ v18 Integration Test PASSED")
            print("=" * 80)
            return True
            
        else:
            logger.error("❌ v18_transaction NOT found in context!")
            logger.info(f"Available keys: {list(context.keys())}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_v18_integration()
    sys.exit(0 if success else 1)
