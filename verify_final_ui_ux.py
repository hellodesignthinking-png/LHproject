"""
Final UI/UX Verification Test
Checks all 6 reports for:
1. Layout & Font Standard
2. No internal data structure exposure
3. KPI display correctness
4. Data Signature display
"""
import requests
import re

CONTEXT_ID = "116801010001230045"
BASE_URL = "http://localhost:8005/api/v4/final-report"

REPORT_TYPES = [
    "quick_check",
    "financial_feasibility", 
    "lh_technical",
    "executive_summary",
    "landowner_summary",
    "all_in_one"
]

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
    
    # 1. Check for dict/JSON exposure
    if re.search(r'\{["\']?\w+["\']?:\s*["\']?\w+', html):
        # Exclude legitimate CSS and script blocks
        if not re.search(r'<style.*?\{', html, re.DOTALL):
            results["issues"].append("❌ Dict/JSON structure exposed")
    
    # 2. Check Data Signature format
    data_sig_match = re.search(r'데이터 시그니처.*?([0-9a-f]{12})', html, re.DOTALL)
    if data_sig_match:
        # Check for key data points
        sig_section = html[data_sig_match.start():data_sig_match.end()+500]
        
        # Check if numbers are formatted correctly
        if '산출 진행 중' in sig_section and '토지감정가' in sig_section:
            results["issues"].append("⚠️ 토지감정가: 산출 진행 중 (should have value)")
        
        # Check for dict exposure in signature
        if '{' in sig_section and 'style' not in sig_section:
            results["issues"].append("❌ Data Signature contains dict")
    
    # 3. Check for None string
    if '"None"' in html or '>None<' in html:
        results["issues"].append("❌ 'None' string exposed")
    
    # 4. Check font standard
    if 'font-family: "Noto Sans KR"' not in html:
        results["issues"].append("⚠️ Font standard not applied")
    
    # 5. Extract key metrics
    land_value = re.search(r'토지감정가[:\s]*([0-9,]+)원', html)
    total_units = re.search(r'총세대수[:\s]*(\d+)세대', html)
    npv = re.search(r'NPV[:\s]*([0-9,]+)원', html)
    decision = re.search(r'LH 판단[:\s]*(적합|조건부 적합|부적합)', html)
    
    results["metrics"] = {
        "land_value": land_value.group(1) if land_value else "NOT FOUND",
        "total_units": total_units.group(1) if total_units else "NOT FOUND",
        "npv": npv.group(1) if npv else "NOT FOUND",
        "decision": decision.group(1) if decision else "NOT FOUND"
    }
    
    return results

def main():
    print("="*80)
    print("FINAL UI/UX VERIFICATION TEST")
    print("="*80)
    print()
    
    all_results = []
    total_issues = 0
    
    for report_type in REPORT_TYPES:
        print(f"📄 Testing {report_type}...")
        result = check_report(report_type)
        all_results.append(result)
        
        if result["generated"]:
            print(f"  ✅ Generated ({result['size']:,} bytes)")
            
            # Display metrics
            print(f"     토지감정가: {result['metrics']['land_value']}")
            print(f"     총세대수: {result['metrics']['total_units']}")
            print(f"     NPV: {result['metrics']['npv']}")
            print(f"     LH판단: {result['metrics']['decision']}")
            
            # Display issues
            if result["issues"]:
                for issue in result["issues"]:
                    print(f"     {issue}")
                total_issues += len(result["issues"])
            else:
                print(f"     ✅ No issues")
        else:
            print(f"  ❌ Failed to generate")
            total_issues += 1
        
        print()
    
    print("="*80)
    print("FINAL RESULTS")
    print("="*80)
    print()
    
    generated_count = sum(1 for r in all_results if r["generated"])
    print(f"✅ {generated_count}/6 reports generated")
    print(f"{'✅' if total_issues == 0 else '⚠️'} {total_issues} total issues found")
    print()
    
    if generated_count == 6 and total_issues == 0:
        print("🎉 FINAL REPORT UI/UX LOCK COMPLETE")
        print("   Layout, font, and data rendering unified")
        print("   6 final reports production-ready")
    else:
        print("⚠️ VERIFICATION INCOMPLETE")
        print(f"   Issues remaining: {total_issues}")

if __name__ == "__main__":
    main()
