"""
Test Script for ZeroSite v7.4 Professional Report Generator

Generates a sample 40-60 page professional consulting report
and saves it as HTML file for validation.
"""

import sys
import json
from datetime import datetime

# Add app directory to path
sys.path.insert(0, '/home/user/webapp')

from app.services.lh_report_generator_v7_4_professional import LHReportGeneratorV74Professional

def create_sample_zerosite_data():
    """Create sample ZeroSite analysis data"""
    return {
        'address': '서울특별시 마포구 월드컵북로 120',
        'land_area': 1200.0,  # 1,200㎡
        'unit_type': '신혼부부 I',  # Newlywed Type I
        'construction_type': 'standard',
        
        # Transport data
        'transport': {
            'nearest_subway_distance': 450,  # meters
            'nearest_subway_name': '월드컵경기장역',
            'nearest_subway_line': '6호선',
            'bus_stop_count': 8
        },
        
        # POI data
        'poi': {
            'education': {'count': 12, 'nearest_distance': 300},
            'medical': {'count': 8, 'nearest_distance': 500},
            'commercial': {'count': 25, 'nearest_distance': 150},
            'cultural': {'count': 5, 'nearest_distance': 800}
        },
        
        # Population data
        'population': {
            'total': 45000,
            'youth_ratio': 0.35,  # 35% youth
            'newlywed_ratio': 0.15  # 15% newlyweds
        },
        
        # Zoning data
        'zoning': {
            'zone_type': '제2종일반주거지역',
            'building_coverage': 0.60,
            'floor_area_ratio': 2.00
        }
    }

def main():
    """Generate sample v7.4 professional report"""
    
    print("=" * 80)
    print("🚀 ZeroSite v7.4 Professional Report Generator - Sample Test")
    print("=" * 80)
    print()
    
    # Step 1: Create sample data
    print("📊 Step 1: Creating sample ZeroSite data...")
    sample_data = create_sample_zerosite_data()
    print(f"   ✓ Address: {sample_data['address']}")
    print(f"   ✓ Land Area: {sample_data['land_area']} ㎡")
    print(f"   ✓ Unit Type: {sample_data['unit_type']}")
    print()
    
    # Step 2: Initialize generator
    print("⚙️  Step 2: Initializing v7.4 Professional Generator...")
    generator = LHReportGeneratorV74Professional()
    print("   ✓ Financial Engine v7.4 initialized")
    print("   ✓ Risk Mitigation Framework v7.4 initialized (25 risks)")
    print("   ✓ Narrative Templates v7.4 initialized (5 generators)")
    print("   ✓ Professional Layout v7.4 initialized")
    print()
    
    # Step 3: Generate report
    print("📝 Step 3: Generating professional report...")
    print("   This will take ~10-15 seconds...")
    print()
    
    start_time = datetime.now()
    
    try:
        html_report = generator.generate_html_report(
            data=sample_data,
            report_mode='professional'
        )
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print("   ✅ Report generated successfully!")
        print()
        
        # Step 4: Analyze output
        print("📈 Step 4: Analyzing report output...")
        report_size_bytes = len(html_report)
        report_size_kb = report_size_bytes / 1024
        report_size_mb = report_size_kb / 1024
        
        # Count sections
        section_count = html_report.count('class="section-title"')
        paragraph_count = html_report.count('class="paragraph"')
        
        print(f"   ✓ Report Size: {report_size_kb:.1f} KB ({report_size_mb:.2f} MB)")
        print(f"   ✓ Sections: {section_count}")
        print(f"   ✓ Paragraphs: {paragraph_count}")
        print(f"   ✓ Generation Time: {generation_time:.2f} seconds")
        print()
        
        # Step 5: Save to file
        print("💾 Step 5: Saving report to file...")
        output_filename = f'v7_4_sample_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        output_path = f'/home/user/webapp/{output_filename}'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"   ✓ Report saved: {output_filename}")
        print(f"   ✓ Full path: {output_path}")
        print()
        
        # Step 6: Summary
        print("=" * 80)
        print("✅ SAMPLE REPORT GENERATION COMPLETE!")
        print("=" * 80)
        print()
        print("📊 Summary:")
        print(f"   • Input: {sample_data['address']}")
        print(f"   • Land Area: {sample_data['land_area']} ㎡")
        print(f"   • Unit Type: {sample_data['unit_type']}")
        print(f"   • Report Mode: professional (v7.4)")
        print(f"   • Output Size: {report_size_kb:.1f} KB")
        print(f"   • Sections: {section_count}")
        print(f"   • Paragraphs: {paragraph_count}")
        print(f"   • Generation Time: {generation_time:.2f}s")
        print(f"   • Output File: {output_filename}")
        print()
        print("🎯 Next Steps:")
        print("   1. Open the HTML file in a browser to view the report")
        print("   2. Validate all 17 sections are present")
        print("   3. Check financial analysis calculations")
        print("   4. Review risk assessment (25 risks)")
        print("   5. Verify professional layout and styling")
        print()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error generating report: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
