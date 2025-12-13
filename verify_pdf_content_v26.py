#!/usr/bin/env python3
"""
Verify PDF v26.0 Content in Detail
PDF 내용 상세 검증
"""

from pypdf import PdfReader

pdf_path = '/home/user/uploaded_files/test_pdf_v26_20251213_084105.pdf'

print("=" * 80)
print("📄 Detailed PDF Content Verification v26.0")
print("=" * 80)

reader = PdfReader(pdf_path)
num_pages = len(reader.pages)

print(f"\n📊 Total Pages: {num_pages}\n")

for i, page in enumerate(reader.pages, 1):
    text = page.extract_text()
    print(f"\n{'=' * 80}")
    print(f"📄 Page {i} ({len(text)} characters)")
    print('=' * 80)
    print(text)
    print('\n')

# 핵심 검증 항목
print("\n" + "=" * 80)
print("🔍 Key Verification Checks")
print("=" * 80)

all_text = ""
for page in reader.pages:
    all_text += page.extract_text()

checks = {
    "표지": "상세 감정평가 보고서" in all_text,
    "주소": "역삼동" in all_text,
    "용도지역": "제3종" in all_text,
    "3-법 요약표": "3대 평가 방식" in all_text,
    "원가법": "원가법" in all_text or "Cost Approach" in all_text,
    "거래사례비교법": "거래사례비교법" in all_text or "Sales Comparison" in all_text,
    "수익환원법": "수익환원법" in all_text or "Income" in all_text,
    "가중 평균": "가중" in all_text,
    "거래사례 비교표": "거래사례" in all_text and "거래일" in all_text,
    "프리미엄 분석": "프리미엄" in all_text,
    "프리미엄 점수": "72.5" in all_text,
    "프리미엄 텍스트 설명": "물리적 특성" in all_text or "입지적 특성" in all_text,
    "재개발": "재개발" in all_text,
    "지하철": "지하철" in all_text,
    "8학군": "8학군" in all_text,
    "최종 평가액": "90.90" in all_text,
}

passed = 0
failed = 0

for name, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {name}: {result}")
    if result:
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 80)
print(f"📊 Test Results: {passed}/{len(checks)} passed")
if failed == 0:
    print("🎉 All verification checks PASSED! v26.0 is production-ready!")
else:
    print(f"⚠️ {failed} checks failed. Review needed.")
print("=" * 80)
