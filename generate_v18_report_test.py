#!/usr/bin/env python3
"""
Generate v18 Report Test
========================
Generate complete HTML report with v18 integration
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_full_generator import generate_lh_full_report
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Generating v18 Test Report")
    print("=" * 80)
    
    test_address = '서울특별시 마포구 월드컵북로 120'
    output_file = 'output/v18_integration_test.html'
    
    try:
        generate_lh_full_report(
            address=test_address,
            land_area_sqm=660.0,
            output_file=output_file,
            additional_params={
                'appraisal_price': 10_000_000  # 1000만원/㎡
            }
        )
        
        print(f"\n✅ Report generated: {output_file}")
        print(f"📊 View at: https://8080-i65g3ela1oephi4loymka-ad490db5.sandbox.novita.ai/{output_file}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
