#!/bin/bash
# Generate Sample v3.2 Report Script

echo "📄 Generating Sample v3.2 Report"
echo "======================================"

cd /home/user/webapp

# Try direct Python generation (server may not be running)
echo "⚙️  Generating report via Python..."

python3 << 'PYTHON_SCRIPT'
import sys
sys.path.append('/home/user/webapp')

try:
    from backend.services_v9.expert_v3_generator import ExpertV3ReportGenerator
    
    print("✅ Importing ExpertV3ReportGenerator...")
    generator = ExpertV3ReportGenerator()
    
    print("⚙️  Generating complete report...")
    result = generator.generate_complete_report(
        address="서울특별시 마포구 월드컵북로 120",
        land_area_sqm=660.0,
        bcr_legal=50.0,
        far_legal=300.0
    )
    
    html = result['html']
    metadata = result['metadata']
    
    print(f"✅ Report generated: {len(html)} bytes")
    
    # Save to file
    with open('sample_report_verification.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Saved to: sample_report_verification.html")
    print(f"📊 Metadata:")
    print(f"   - Address: {metadata['address']}")
    print(f"   - Land Area: {metadata['land_area_sqm']}㎡")
    print(f"   - Recommended: {metadata['recommended_scenario']}")
    print(f"   - Version: {metadata['version']}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
PYTHON_SCRIPT

echo ""
echo "======================================"
echo "📊 Sample Report Status"
echo "======================================"

ls -lh sample_report*.html test_expert_v3_2_output.html 2>/dev/null || echo "⚠️  No sample reports found"

echo ""
echo "✅ Sample report generation complete"
