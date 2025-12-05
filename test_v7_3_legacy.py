#!/usr/bin/env python3
"""
Test v7.3 Legacy Report Generator
"""
import requests
import json

API_BASE = "http://0.0.0.0:8000"

payload = {
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area": 660.0,
    "unit_type": "청년",
    "report_mode": "legacy"  # v7.3 Legacy mode
}

print("=" * 80)
print("🧪 Testing v7.3 Legacy Report Generation")
print("=" * 80)
print(f"\n📤 Request:")
print(f"   POST {API_BASE}/api/generate-report")
print(f"   Body: {json.dumps(payload, ensure_ascii=False, indent=2)}")

try:
    response = requests.post(
        f"{API_BASE}/api/generate-report",
        json=payload,
        timeout=60
    )
    
    print(f"\n📥 Response:")
    print(f"   Status: {response.status_code}")
    print(f"   Size: {len(response.content):,} bytes")
    
    if response.status_code == 200:
        # Save report
        report_path = "/tmp/v7_3_legacy_report.html"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"\n✅ SUCCESS - v7.3 Legacy Report Generated")
        print(f"   Report saved: {report_path}")
        
        # Check key sections
        html = response.text
        sections = [
            "사업 대상지 기본 개요",
            "입지 종합 분석",
            "교통 접근성 해설",
            "생활 편의시설 해석",
            "인구·수요 분석",
            "법적·규제 환경 분석",
            "GeoOptimizer 대안지 비교",
            "Risk 요인 상세 해설",
            "사업성 분석",
            "종합 평가",
            "결론 및 권고사항",
            "Appendix"
        ]
        
        print(f"\n📋 Section Validation:")
        found_sections = 0
        for section in sections:
            if section in html:
                print(f"   ✓ {section}")
                found_sections += 1
            else:
                print(f"   ✗ {section} missing")
        
        print(f"\n📊 Section Detection Rate: {found_sections}/{len(sections)} ({found_sections/len(sections)*100:.0f}%)")
        
        # Count paragraphs
        paragraph_count = html.count('<p class="paragraph">')
        print(f"\n📝 Content Statistics:")
        print(f"   Paragraphs: {paragraph_count}")
        print(f"   Total Size: {len(html):,} bytes")
        
    else:
        print(f"\n❌ FAILED - Status {response.status_code}")
        print(f"   Error: {response.text[:500]}")

except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

print("\n" + "=" * 80)
