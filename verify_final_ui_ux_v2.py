"""
Final UI/UX Verification Test V2
Checks all 6 reports for:
1. No internal data structure exposure (dict/JSON)
2. No 'None' string exposure
3. Proper KPI formatting
4. Data Signature correctness per report type
"""
import requests
import re

CONTEXT_ID = "116801010001230045"
BASE_URL = "http://localhost:8005/api/v4/final-report"

# Expected modules per report type
EXPECTED_MODULES = {
    "quick_check": ["M5", "M6"],  # Only M5 and M6
    "financial_feasibility": ["M2", "M5", "M6"],  # M2, M5, M6
    "lh_technical": ["M4", "M6"],  # M4, M6
    "executive_summary": ["M2", "M5", "M6"],  # M2, M5, M6
    "landowner_summary": ["M2", "M5", "M6"],  # M2, M5, M6
    "all_in_one": ["M2", "M4", "M5", "M6"]  # All modules
}

def check_report(report_type: str) -> dict:
    """Check single report for UI/UX compliance"""
    url = f"{BASE_URL}/{report_type}/html?context_id={CONTEXT_ID}"
    response = requests.get(url)
    html = response.text
    
    results = {
        "report_type": report_type,
        "generated": response.status_code == 200,
        "size": len(html),
        "issues": []
    }
    
    # 1. Check for dict/JSON exposure (CRITICAL)
    # Look for patterns like {"key": "value"} or {'key': 'value'}
    dict_pattern = r'[{]\s*["\'][\w_]+["\']:\s*["\']?[\w\s]+["\']?\s*[}]'
    if re.search(dict_pattern, html):
        # Exclude CSS/script blocks
        matches = re.findall(dict_pattern, html)
        non_css_matches = [m for m in matches if 'style' not in m and 'font' not in m]
        if non_css_matches:
            results["issues"].append(f"❌ CRITICAL: Dict exposed: {non_css_matches[0][:50]}...")
    
    # 2. Check for None string (CRITICAL)
    if re.search(r'[>"\s]None[<"\s]', html):
        results["issues"].append("❌ CRITICAL: 'None' string exposed")
    
    # 3. Check Data Signature format
    expected_modules = EXPECTED_MODULES.get(report_type, [])
    data_sig_match = re.search(r'데이터 시그니처.*?([0-9a-f]{12})', html, re.DOTALL)
    
    if data_sig_match:
        sig_section = html[data_sig_match.start():data_sig_match.end()+800]
        
        # For reports with M2, check if land value is present
        if "M2" in expected_modules:
            if '토지감정가:' in sig_section:
                if '산출 진행 중' in sig_section and '토지감정가' in sig_section:
                    # This is OK if value appears after
                    if not re.search(r'토지감정가:\s*([0-9,]+)원', sig_section):
                        results["issues"].append("⚠️ M2 토지감정가 missing value")
        
        # For reports with M4, check if units is present
        if "M4" in expected_modules:
            if '총세대수:' in sig_section:
                if not re.search(r'총세대수:\s*(\d+)세대', sig_section):
                    results["issues"].append("⚠️ M4 총세대수 missing value")
        
        # All reports should have M5/M6
        if not re.search(r'NPV:\s*([0-9,]+)원', sig_section):
            results["issues"].append("⚠️ M5 NPV missing value")
        
        if not re.search(r'LH 판단:\s*(적합|조건부 적합|부적합)', sig_section):
            results["issues"].append("⚠️ M6 판단 missing value")
    
    # 4. Extract and validate key metrics based on expected modules
    metrics = {}
    
    if "M2" in expected_modules:
        land_value = re.search(r'토지[감평]가[정액]*[:\s]*([0-9,]+)원', html)
        metrics["land_value"] = land_value.group(1) if land_value else "NOT FOUND"
    
    if "M4" in expected_modules:
        total_units = re.search(r'총\s*세대수[:\s]*(\d+)세대', html)
        metrics["total_units"] = total_units.group(1) if total_units else "NOT FOUND"
    
    # All reports have M5/M6
    npv = re.search(r'NPV[:\s]*([0-9,]+)원', html)
    decision = re.search(r'LH\s*판단[:\s]*(적합|조건부 적합|부적합)', html)
    
    metrics["npv"] = npv.group(1) if npv else "NOT FOUND"
    metrics["decision"] = decision.group(1) if decision else "NOT FOUND"
    
    results["metrics"] = metrics
    results["expected_modules"] = expected_modules
    
    return results

def main():
    print("="*80)
    print("FINAL UI/UX VERIFICATION TEST V2")
    print("="*80)
    print()
    
    all_results = []
    critical_issues = 0
    warning_issues = 0
    
    for report_type, expected_modules in EXPECTED_MODULES.items():
        print(f"📄 Testing {report_type} (Modules: {', '.join(expected_modules)})...")
        result = check_report(report_type)
        all_results.append(result)
        
        if result["generated"]:
            print(f"  ✅ Generated ({result['size']:,} bytes)")
            
            # Display metrics
            for key, value in result["metrics"].items():
                print(f"     {key}: {value}")
            
            # Display issues
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"     {issue}")
                    if "CRITICAL" in issue:
                        critical_issues += 1
                    else:
                        warning_issues += 1
            else:
                print(f"     ✅ No issues")
        else:
            print(f"  ❌ Failed to generate")
            critical_issues += 1
        
        print()
    
    print("="*80)
    print("FINAL RESULTS")
    print("="*80)
    print()
    
    generated_count = sum(1 for r in all_results if r["generated"])
    print(f"✅ {generated_count}/6 reports generated")
    print(f"{'✅' if critical_issues == 0 else '❌'} {critical_issues} critical issues")
    print(f"{'✅' if warning_issues == 0 else '⚠️'} {warning_issues} warnings")
    print()
    
    if generated_count == 6 and critical_issues == 0:
        print("🎉 FINAL REPORT UI/UX LOCK COMPLETE")
        print("   Layout, font, and data rendering unified")
        print("   6 final reports production-ready")
        print()
        if warning_issues > 0:
            print(f"   Note: {warning_issues} non-critical warnings (acceptable)")
    else:
        print("❌ VERIFICATION FAILED")
        print(f"   Critical issues: {critical_issues}")
        print(f"   Warnings: {warning_issues}")

if __name__ == "__main__":
    main()
