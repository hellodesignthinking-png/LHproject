"""Quick v15 Phase 2 Test"""
import sys
sys.path.insert(0, '/home/user/webapp')

from app.services_v13.report_full.report_context_builder import ReportContextBuilder

print("="*80)
print("🚀 ZeroSite v15 Phase 2 - S-Grade (100%) Test")
print("="*80)

builder = ReportContextBuilder()
context = builder.build_expert_context('서울특별시 강남구 역삼동 737', 800.0)

print("\n✅ v15 Phase 2 Components Check:")
checks = {
    'v15_simulation': context.get('v15_simulation'),
    'v15_sensitivity': context.get('v15_sensitivity'),
    'v15_approval': context.get('v15_approval'),
    'v15_government_page': context.get('v15_government_page')
}

for comp, val in checks.items():
    status = "✅ PRESENT" if val else "❌ MISSING"
    print(f"  {comp}: {status}")
    if val and isinstance(val, dict):
        print(f"    Keys: {list(val.keys())[:5]}")

if all(checks.values()):
    print("\n🎉 v15 Phase 2 (S-Grade) - ALL COMPONENTS PRESENT!")
    print("📊 Approval Probability:", context['v15_approval'].get('probability_pct', 'N/A'))
    print("🎲 Expected NPV:", f"{context['v15_simulation'].get('expected_values', {}).get('npv_krw', 0):.1f}억원")
else:
    print("\n⚠️ Some components missing")

print("\n" + "="*80)
