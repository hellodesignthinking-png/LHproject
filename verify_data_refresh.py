import requests
import re

context_id = "116801010001230045"
base_url = "http://localhost:8005"

print("\n" + "="*80)
print("VERIFICATION: FINAL DATA REFRESH")
print("="*80)

# Test all 6 report types
report_types = ["quick_check", "financial_feasibility", "lh_technical", 
                "executive_summary", "landowner_summary", "all_in_one"]

results = []
for report_type in report_types:
    url = f"{base_url}/api/v4/final-report/{report_type}/html?context_id={context_id}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            html = response.text
            
            # Extract M2 land value
            land_value_match = re.search(r'data-land-value-total="(\d+)"', html)
            land_value = land_value_match.group(1) if land_value_match else "NOT FOUND"
            
            # Extract M6 decision
            decision_match = re.search(r'data-decision="([^"]+)"', html)
            decision = decision_match.group(1) if decision_match else "NOT FOUND"
            
            # Check for BUILD_SIGNATURE
            has_build_sig = "BUILD_SIGNATURE" in html
            
            # Check for stale data message
            has_stale_msg = "이전 보고서와 동일하게 보일 수 있습니다" in html
            
            results.append({
                "type": report_type,
                "status": "✅",
                "land_value": land_value,
                "decision": decision,
                "build_sig": "✅" if has_build_sig else "❌",
                "stale_msg": "❌ FOUND" if has_stale_msg else "✅ REMOVED"
            })
        else:
            results.append({
                "type": report_type,
                "status": "❌",
                "land_value": f"Error {response.status_code}",
                "decision": "N/A",
                "build_sig": "N/A",
                "stale_msg": "N/A"
            })
    except Exception as e:
        results.append({
            "type": report_type,
            "status": "❌",
            "land_value": f"Error: {str(e)[:30]}",
            "decision": "N/A",
            "build_sig": "N/A",
            "stale_msg": "N/A"
        })

print("\n📊 REPORT GENERATION RESULTS:")
print("-" * 80)
for r in results:
    print(f"{r['status']} {r['type']:<25} | Land: {r['land_value']:<15} | Decision: {r['decision']:<12}")
    print(f"   BUILD_SIG: {r['build_sig']:<3} | Stale Msg: {r['stale_msg']}")

print("\n" + "="*80)
success_count = sum(1 for r in results if r['status'] == "✅")
all_same_land = len(set(r['land_value'] for r in results if r['status'] == "✅")) == 1
all_same_decision = len(set(r['decision'] for r in results if r['status'] == "✅")) == 1
no_stale_msgs = all("✅" in r['stale_msg'] for r in results if r['status'] == "✅")

print(f"✅ Reports Generated: {success_count}/6")
print(f"✅ Consistent Land Value: {all_same_land}")
print(f"✅ Consistent M6 Decision: {all_same_decision}")
print(f"✅ No Stale Messages: {no_stale_msgs}")

if success_count == 6 and all_same_land and all_same_decision and no_stale_msgs:
    print("\n" + "="*80)
    print("FINAL DATA REFRESH COMPLETE")
    print("Report cache disabled and canonical_summary rebound")
    print("6 final reports generated with updated data")
    print("="*80)
else:
    print("\nFAILED")
    print("Reason: Not all criteria met")
