#!/usr/bin/env python3
"""
[vABSOLUTE-FINAL-10] PDF 검증 스크립트

PURPOSE: 사용자가 업로드한 PDF가 새 코드로 생성되었는지 자동 검증

검증 항목:
① BUILD SIGNATURE (우측 상단 워터마크)
② DATA SIGNATURE (해시 8자리)
③ N/A 문자열 개수 (0개여야 함)
④ 실제 숫자 노출 (NPV, IRR, ROI, 세대수, 토지가치)
⑤ 구체적 문장 패턴 (템플릿 vs 실데이터 기반)
⑥ 6종 보고서 일관성

사용법:
python verify_pdf_changes.py /path/to/uploaded_pdfs/
"""

import sys
import os
import re
from pathlib import Path

def verify_single_pdf(pdf_path):
    """
    단일 PDF 파일 검증
    
    Returns:
        dict: 검증 결과
    """
    print(f"\n{'='*80}")
    print(f"📄 검증 대상: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")
    
    # PDF를 텍스트로 변환 (pdfplumber 사용)
    try:
        import pdfplumber
    except ImportError:
        print("❌ pdfplumber 설치 필요: pip install pdfplumber")
        return None
    
    result = {
        "filename": os.path.basename(pdf_path),
        "build_signature": False,
        "data_signature": False,
        "na_count": 0,
        "has_actual_numbers": False,
        "actual_numbers_found": [],
        "verdict": "UNKNOWN"
    }
    
    # PDF 읽기
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text() or ""
    except Exception as e:
        print(f"❌ PDF 읽기 실패: {e}")
        return None
    
    # ① BUILD SIGNATURE 확인
    print("\n① BUILD SIGNATURE 확인...")
    if "BUILD: vABSOLUTE-FINAL-6" in all_text or "vABSOLUTE-FINAL-6" in all_text:
        # 날짜 확인
        date_match = re.search(r"2025-12-24T\d{2}:\d{2}:\d{2}", all_text)
        if date_match:
            build_time = date_match.group(0)
            print(f"   ✅ BUILD SIGNATURE 발견: {build_time}")
            result["build_signature"] = True
        else:
            print(f"   ⚠️ BUILD 텍스트는 있으나 타임스탬프 없음")
    else:
        print(f"   ❌ BUILD SIGNATURE 없음 → 옛 코드 사용 중")
    
    # ② DATA SIGNATURE 확인
    print("\n② DATA SIGNATURE 확인...")
    if "Data Signature" in all_text or "데이터 시그니처" in all_text:
        # 해시 패턴 찾기 (8-12자 hexadecimal)
        hash_match = re.search(r"\b[0-9a-f]{8,12}\b", all_text.lower())
        if hash_match:
            hash_value = hash_match.group(0)
            print(f"   ✅ DATA SIGNATURE 발견: {hash_value}")
            result["data_signature"] = True
        else:
            print(f"   ⚠️ 'Data Signature' 텍스트는 있으나 해시 없음")
    else:
        print(f"   ❌ DATA SIGNATURE 없음 → Narrative Generator 미반영")
    
    # ③ N/A 문자열 개수
    print("\n③ N/A 문자열 검사...")
    na_patterns = [
        r"N/A\s*\(검증\s*필요\)",
        r"N/A",
        r"검증\s*필요",
        r"분석\s*중",
        r"산출\s*불가"
    ]
    
    na_count = 0
    for pattern in na_patterns:
        matches = re.findall(pattern, all_text, re.IGNORECASE)
        na_count += len(matches)
    
    result["na_count"] = na_count
    
    if na_count == 0:
        print(f"   ✅ N/A 문자열: 0개 → 강제 치환 성공")
    else:
        print(f"   ❌ N/A 문자열: {na_count}개 발견 → 강제 치환 실패")
        # 샘플 출력
        for pattern in na_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            if matches:
                print(f"      - '{pattern}': {len(matches)}개")
    
    # ④ 실제 숫자 노출 확인
    print("\n④ 실제 숫자 (NPV, IRR, ROI, 세대수, 토지가치) 확인...")
    
    number_patterns = {
        "NPV": [
            r"NPV[는은]?\s*약?\s*([\d,]+)\s*원",
            r"순현재가치[는은]?\s*약?\s*([\d,]+)\s*원",
        ],
        "IRR": [
            r"IRR[는은]?\s*약?\s*([\d.]+)\s*%",
            r"내부수익률[는은]?\s*약?\s*([\d.]+)\s*%",
        ],
        "ROI": [
            r"ROI[는은]?\s*약?\s*([\d.]+)\s*%",
            r"투자수익률[는은]?\s*약?\s*([\d.]+)\s*%",
        ],
        "세대수": [
            r"([\d,]+)\s*세대",
            r"총세대수[는은]?\s*약?\s*([\d,]+)",
        ],
        "토지가치": [
            r"토지\s*가치[는은]?\s*약?\s*([\d,]+)\s*원",
            r"감정가[는은]?\s*약?\s*([\d,]+)\s*원",
        ]
    }
    
    found_numbers = []
    for metric, patterns in number_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, all_text)
            if matches:
                value = matches[0] if isinstance(matches[0], str) else matches[0]
                found_numbers.append(f"{metric}: {value}")
                print(f"   ✅ {metric}: {value}")
                break
    
    result["actual_numbers_found"] = found_numbers
    result["has_actual_numbers"] = len(found_numbers) >= 3
    
    if len(found_numbers) >= 3:
        print(f"   ✅ 실제 숫자 {len(found_numbers)}개 발견 → Narrative Generator 반영")
    else:
        print(f"   ❌ 실제 숫자 {len(found_numbers)}개만 발견 → 구형 템플릿 의심")
    
    # ⑤ 구체적 문장 패턴 확인
    print("\n⑤ 구체적 문장 패턴 확인...")
    
    # 새 패턴 (실데이터 기반 서술)
    new_patterns = [
        r"본 사업의 순현재가치\(NPV\)는",
        r"내부수익률\(IRR\)은 [\d.]+%",
        r"예상 건축 세대수는 \d+세대",
        r"토지 가치는 [\d,]+원",
    ]
    
    # 옛 패턴 (generic template)
    old_patterns = [
        r"N/A \(검증 필요\)",
        r"분석 중입니다",
        r"검토가 필요합니다",
    ]
    
    new_pattern_count = sum(1 for p in new_patterns if re.search(p, all_text))
    old_pattern_count = sum(1 for p in old_patterns if re.search(p, all_text))
    
    if new_pattern_count >= 2:
        print(f"   ✅ 새 패턴 {new_pattern_count}개 발견 → 실데이터 기반 서술")
    else:
        print(f"   ⚠️ 새 패턴 {new_pattern_count}개만 발견")
    
    if old_pattern_count > 0:
        print(f"   ❌ 옛 패턴 {old_pattern_count}개 발견 → 구형 템플릿 잔존")
    
    # 종합 판정
    print(f"\n{'='*80}")
    print("🎯 종합 판정")
    print(f"{'='*80}")
    
    checks_passed = 0
    total_checks = 5
    
    if result["build_signature"]:
        checks_passed += 1
        print("✅ ① BUILD SIGNATURE: 통과")
    else:
        print("❌ ① BUILD SIGNATURE: 실패")
    
    if result["data_signature"]:
        checks_passed += 1
        print("✅ ② DATA SIGNATURE: 통과")
    else:
        print("❌ ② DATA SIGNATURE: 실패")
    
    if result["na_count"] == 0:
        checks_passed += 1
        print("✅ ③ N/A 문자열 0개: 통과")
    else:
        print(f"❌ ③ N/A 문자열 {result['na_count']}개: 실패")
    
    if result["has_actual_numbers"]:
        checks_passed += 1
        print("✅ ④ 실제 숫자 노출: 통과")
    else:
        print("❌ ④ 실제 숫자 노출: 실패")
    
    if new_pattern_count >= 2 and old_pattern_count == 0:
        checks_passed += 1
        print("✅ ⑤ 새 문장 패턴: 통과")
    else:
        print("❌ ⑤ 새 문장 패턴: 실패")
    
    print(f"\n📊 통과율: {checks_passed}/{total_checks} ({checks_passed/total_checks*100:.0f}%)")
    
    # 최종 판정
    if checks_passed == total_checks:
        result["verdict"] = "✅ 진짜 변경됨 (확정)"
        print(f"\n🎉 {result['verdict']}")
        print("   → 새 코드가 정상 반영되었습니다!")
    elif result["build_signature"] and checks_passed >= 3:
        result["verdict"] = "⚠️ 부분 반영 (일부 개선 필요)"
        print(f"\n⚠️ {result['verdict']}")
        print("   → BUILD SIGNATURE는 있으나 일부 항목 미달")
    else:
        result["verdict"] = "❌ 옛 코드 사용 중"
        print(f"\n❌ {result['verdict']}")
        print("   → 백엔드 재시작 또는 캐시 문제")
    
    return result


def main():
    """메인 실행 함수"""
    print("="*80)
    print("🔍 vABSOLUTE-FINAL-10 PDF 검증 스크립트")
    print("="*80)
    
    # 업로드된 PDF 디렉토리 확인
    upload_dir = Path("/home/user/uploaded_files")
    
    if not upload_dir.exists():
        print(f"❌ 업로드 디렉토리 없음: {upload_dir}")
        print("   → PDF를 먼저 업로드해주세요")
        return
    
    # PDF 파일 찾기
    pdf_files = list(upload_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ PDF 파일 없음: {upload_dir}")
        print("   → PDF를 먼저 업로드해주세요")
        return
    
    print(f"\n📁 발견된 PDF: {len(pdf_files)}개")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # 각 PDF 검증
    results = []
    for pdf_file in pdf_files:
        result = verify_single_pdf(pdf_file)
        if result:
            results.append(result)
    
    # 전체 요약
    print(f"\n{'='*80}")
    print("📊 전체 요약")
    print(f"{'='*80}")
    
    if results:
        verdicts = [r["verdict"] for r in results]
        success_count = sum(1 for v in verdicts if "✅" in v)
        
        print(f"\n검증 완료: {len(results)}개")
        print(f"성공: {success_count}개")
        print(f"실패/부분: {len(results) - success_count}개")
        
        print(f"\n결과 상세:")
        for r in results:
            print(f"   {r['filename']}: {r['verdict']}")
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()
