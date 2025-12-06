#!/usr/bin/env python3
"""
Test Expert Edition v3 Context Generation
==========================================

Quick test to verify all Expert Edition modules are working
"""

import sys
sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_context_builder import ReportContextBuilder

def test_expert_edition():
    """Test Expert Edition context generation"""
    
    print("=" * 80)
    print("🎓 Testing ZeroSite Expert Edition v3")
    print("=" * 80)
    
    # Initialize builder
    builder = ReportContextBuilder()
    
    # Test Expert Edition context
    address = "서울시 강남구 역삼동 123"
    land_area = 500.0
    
    print(f"\n📊 Generating Expert Edition context for:")
    print(f"   Address: {address}")
    print(f"   Area: {land_area}㎡")
    
    try:
        context = builder.build_expert_context(
            address=address,
            land_area_sqm=land_area
        )
        
        print("\n✅ Expert Edition Context Generated Successfully!")
        print(f"\n📌 Context Sections:")
        for key in context.keys():
            print(f"   - {key}")
        
        # Check Expert Edition specific sections
        if 'policy_framework' in context:
            print("\n✅ Policy Framework: PRESENT")
            print(f"   - National Context: {len(context['policy_framework']['national_context']['narrative'])} chars")
        
        if 'implementation_roadmap' in context:
            print("\n✅ Implementation Roadmap: PRESENT")
            print(f"   - Phases: {len(context['implementation_roadmap']['phases'])}")
            print(f"   - Milestones: {len(context['implementation_roadmap']['milestones'])}")
        
        if 'academic_conclusion' in context:
            print("\n✅ Academic Conclusion: PRESENT")
            print(f"   - Abstract: {len(context['academic_conclusion']['abstract'])} chars")
        
        # Financial summary
        print(f"\n📈 Financial Summary:")
        print(f"   - CAPEX: {context['finance']['capex']['total']/1e8:.2f}억원")
        print(f"   - NPV: {context['finance']['npv']['public']/1e8:+.2f}억원")
        print(f"   - IRR: {context['finance']['irr']['public']:.2f}%")
        print(f"   - Decision: {context['decision']['recommendation']}")
        
        print("\n" + "=" * 80)
        print("✅ TEST PASSED - Expert Edition v3 is ready!")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_expert_edition()
    sys.exit(0 if success else 1)
