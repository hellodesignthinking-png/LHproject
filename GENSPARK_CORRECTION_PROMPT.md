# 🎯 Genspark AI 최종 수정 프롬프트

## ⚠️ 현재 상황

- **문제**: 최종 6종 PDF 내용이 코드 수정 후에도 전혀 바뀌지 않음
- **사용자 검증**: 업로드된 PDF를 바이너리 검색했을 때 `BUILD_SIGNATURE`, `DATA_SIGNATURE` 문자열이 **0건**
- **근본 원인**: (A) PDF가 캐시되거나 (B) 시그니처가 텍스트가 아닌 graphics/vector로만 렌더링되거나 (C) 구버전 경로를 타고 있음

---

## 🎯 목표

**최종 6종 PDF(QuickCheck/Financial/LH Technical/Executive/Landowner/All-in-one)가 코드 수정 후 반드시 바뀌도록 하며, 사용자가 바이너리 검색으로 100% 검증 가능하게 만들기**

---

## 📋 필수 수정 사항

### 1) PDF 다운로드 엔드포인트 - 캐시 완전 차단

#### 현황 파악
- `GET /api/v4/final-report/{report_type}/pdf?context_id=...` 엔드포인트 확인
- 파일 시스템/DB/S3에 저장된 기존 PDF를 재사용하는지 확인

#### 조치 사항

**A. 캐시 재사용 금지 조건**
```python
# 다음 조건 중 하나라도 변경되면 PDF 재생성 필수
cache_key = {
    "report_type": report_type,
    "context_id": context_id,
    "build_hash": current_build_hash,  # 코드 버전 해시
    "data_signature": data_signature_8  # 데이터 해시
}

# build_hash나 data_signature가 다르면 캐시 무효화
if cached_pdf["build_hash"] != current_build_hash:
    regenerate_pdf()
```

**B. HTTP 캐시 방지 헤더 (필수)**
```python
headers = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
    "X-Build-Hash": build_hash,
    "X-Build-Signature": "vABSOLUTE-FINAL-12",
    "X-Searchable-Signature": "true"
}
```

**C. 파일명에 build_hash 포함 (캐시 회피)**
```python
filename = f"{report_type}_{context_id}_{build_hash}_{data_signature}.pdf"
# 예: quick_check_abc123_9f8e7d6c_a1b2c3d4.pdf
```

---

### 2) BUILD/DATA SIGNATURE를 SEARCHABLE TEXT로 삽입 (최우선)

#### 문제
현재 시그니처가 visual watermark(graphics)로만 존재하여 텍스트 추출 불가능

#### 해결책
**모든 6개 보고서 HTML에 아래 블록을 본문 텍스트로 삽입** (footer 또는 body)

```html
<div style="font-size:10px; color:#b00000; border:1px solid #b00000; padding:6px; margin:12px 0; background:#fff8f8;">
  <div style="font-weight:bold; margin-bottom:4px;">
    📊 Report Verification Signature (보고서 검증 시그니처)
  </div>
  <div>
    BUILD_SIGNATURE: vABSOLUTE-FINAL-12<br/>
    BUILD_TS: {{iso_timestamp}}<br/>
    REPORT: {{report_type}}<br/>
    CONTEXT: {{context_id}}<br/>
    DATA_SIGNATURE: {{data_signature_8}}
  </div>
  <div style="font-size:8px; color:#666; margin-top:4px;">
    ※ This signature is embedded as searchable text for verification.
  </div>
</div>
```

**중요**: 이것은 **plain HTML text**여야 하며, WeasyPrint가 PDF로 변환할 때 **searchable text**로 남아야 함

#### 적용 대상
- `QuickCheckAssembler`
- `LandownerSummaryAssembler`
- `FinancialFeasibilityAssembler`
- `LHTechnicalAssembler`
- `AllInOneAssembler`
- `ExecutiveSummaryAssembler`

---

### 3) Narrative Generator - "N/A" 템플릿 완전 제거

#### 검색 대상
repo 전체에서 다음 문자열을 검색:
```python
grep -r "N/A" app/services/final_report_assembly/
grep -r "검증 필요" app/services/final_report_assembly/
grep -r "N/A (검증 필요)" app/services/final_report_assembly/
```

#### 조치 사항

**A. 고정 템플릿 금지**
```python
# ❌ 금지 (고정 템플릿)
def executive_summary(self, modules_data: Dict) -> str:
    return """
    <p>예상 순이익은 N/A (검증 필요)입니다.</p>
    """

# ✅ 필수 (실제 데이터 사용)
def executive_summary(self, modules_data: Dict) -> str:
    npv = modules_data.get("M5", {}).get("npv", 0)
    npv_str = f"{int(npv):,}원" if npv else "데이터 미확정 (모듈 M5 결과 누락)"
    
    return f"""
    <p>본 사업의 순현재가치(NPV)는 <strong>{npv_str}</strong>입니다.</p>
    """
```

**B. 모든 6개 Narrative Generator 수정**
- `LandownerNarrativeGenerator.executive_summary()`
- `QuickCheckNarrativeGenerator.executive_summary()`
- `FinancialFeasibilityNarrativeGenerator.executive_summary()`
- `LHTechnicalNarrativeGenerator.executive_summary()`
- `AllInOneNarrativeGenerator.executive_summary()`
- `ExecutiveSummaryNarrativeGenerator.executive_summary()`

**C. 데이터 추출 규칙**
```python
# modules_data에서 실제 값 추출 (여러 key 시도)
m5_data = modules_data.get("M5", {})
npv = m5_data.get("npv", m5_data.get("NPV", 0))
irr = m5_data.get("irr", m5_data.get("IRR", 0))
roi = m5_data.get("roi", m5_data.get("ROI", 0))

m2_data = modules_data.get("M2", {})
land_value = m2_data.get("land_value_total", m2_data.get("total_land_value", 0))

m4_data = modules_data.get("M4", {})
total_units = m4_data.get("total_units", m4_data.get("household_count", 0))

# 안전한 포매팅
npv_str = f"{int(npv):,}원" if npv and npv != 0 else "산출 불가"
```

---

### 4) 레거시 경로 완전 차단

#### 조사 대상
```python
# PDF 엔드포인트가 호출하는 함수 체인 추적
GET /api/v4/final-report/{type}/pdf
  → final_report_api.py
  → Assembler.assemble()
  → NarrativeGenerator.executive_summary()
  → HTML → PDF
```

#### 차단 대상
- `v4.1` 템플릿 경로
- 구버전 renderer
- 레거시 `lh_report_generator_v7_5_final.py` (최종 보고서에 사용 안 됨)

#### 차단 방법
```python
# 레거시 경로가 있으면 즉시 에러 발생
if "v4.1" in template_path or "v7_5_final" in generator_name:
    raise RuntimeError(
        "BLOCKED: Legacy template path detected. "
        "Use Phase 3 FinalReportAssembly only."
    )
```

---

### 5) 자동 검증 테스트 추가 (CI/CD에서 막기)

#### 테스트 1: PDF 바이너리 시그니처 검색
```python
def test_pdf_has_searchable_signature():
    """PDF must contain searchable text signatures"""
    context_id = create_test_context()
    pdf_bytes = generate_pdf("quick_check", context_id)
    
    # Binary search
    assert b'BUILD_SIGNATURE:' in pdf_bytes, "BUILD_SIGNATURE missing!"
    assert b'DATA_SIGNATURE:' in pdf_bytes, "DATA_SIGNATURE missing!"
    assert b'vABSOLUTE-FINAL-12' in pdf_bytes, "Version signature missing!"
    assert b'REPORT:' in pdf_bytes, "REPORT field missing!"
```

#### 테스트 2: "N/A" 제거 확인
```python
def test_pdf_has_no_na_strings():
    """PDF must not contain 'N/A (검증 필요)' templates"""
    context_id = create_test_context_with_data()  # 데이터 있는 context
    pdf_bytes = generate_pdf("quick_check", context_id)
    
    text = extract_text_from_pdf(pdf_bytes)
    
    # ❌ 금지된 문구들
    forbidden = ["N/A (검증 필요)", "분석 중입니다", "검토 중입니다"]
    for phrase in forbidden:
        assert phrase not in text, f"Template phrase found: {phrase}"
```

#### 테스트 3: build_hash 변경 시 내용 변경 검증
```python
def test_pdf_changes_when_build_hash_changes():
    """PDF content must change when build_hash changes"""
    context_id = create_test_context()
    
    pdf1 = generate_pdf("quick_check", context_id, build_hash="aaa111")
    pdf2 = generate_pdf("quick_check", context_id, build_hash="bbb222")
    
    # 파일 내용이 달라야 함
    assert pdf1 != pdf2, "PDF did not change despite build_hash change!"
```

---

### 6) 완료 기준 (이 기준 충족 전까지 '완료' 금지)

✅ **1. Searchable Signature 존재**
```bash
strings report.pdf | grep 'BUILD_SIGNATURE:'
# 출력: BUILD_SIGNATURE: vABSOLUTE-FINAL-12
```

✅ **2. Data Signature 존재**
```bash
strings report.pdf | grep 'DATA_SIGNATURE:'
# 출력: DATA_SIGNATURE: abc12345
```

✅ **3. "N/A" 문자열 0개**
```bash
strings report.pdf | grep -c "N/A (검증 필요)"
# 출력: 0
```

✅ **4. 실제 숫자 최소 1개 이상**
```bash
strings report.pdf | grep -E "[0-9]{1,3}(,[0-9]{3})+(원|%)"
# 출력: 420,000,000원, 13.20%, etc.
```

✅ **5. 6개 보고서 모두 동일 기준 적용**
- QuickCheck, Financial, LH Technical, Executive, Landowner, All-in-One

✅ **6. Python 바이너리 검증 통과**
```python
with open('report.pdf', 'rb') as f:
    content = f.read()
    assert b'BUILD_SIGNATURE:' in content
    assert b'DATA_SIGNATURE:' in content
```

---

## 📦 제출물

수정 완료 후 다음을 제출하세요:

### 1. 수정한 파일 목록
```
- app/routers/final_report_api.py (PDF 엔드포인트)
- app/services/final_report_assembly/assemblers/quick_check.py
- app/services/final_report_assembly/assemblers/landowner_summary.py
- app/services/final_report_assembly/assemblers/financial_feasibility.py
- app/services/final_report_assembly/assemblers/lh_technical.py
- app/services/final_report_assembly/assemblers/all_in_one.py
- app/services/final_report_assembly/assemblers/executive_summary.py
- app/services/final_report_assembly/narrative_generator.py
```

### 2. PDF 엔드포인트 호출 체인 증거
```
GET /api/v4/final-report/quick_check/pdf
  → final_report_api.py:get_final_report_pdf()
  → QuickCheckAssembler.assemble()
  → QuickCheckNarrativeGenerator.executive_summary()
  → _generate_footer() with searchable signature
  → HTML → WeasyPrint → PDF
  
✅ 레거시 경로 차단됨: v4.1 template path → RuntimeError
```

### 3. 테스트 실행 로그
```bash
pytest tests/test_pdf_signature.py -v

test_pdf_has_searchable_signature PASSED ✅
test_pdf_has_no_na_strings PASSED ✅
test_pdf_changes_when_build_hash_changes PASSED ✅
```

### 4. 새로 생성한 6종 PDF 샘플
- `QuickCheck_abc123_9f8e7d6c.pdf` (15MB)
- `Financial_abc123_9f8e7d6c.pdf` (18MB)
- `LHTechnical_abc123_9f8e7d6c.pdf` (16MB)
- `Executive_abc123_9f8e7d6c.pdf` (12MB)
- `Landowner_abc123_9f8e7d6c.pdf` (14MB)
- `AllInOne_abc123_9f8e7d6c.pdf` (22MB)

### 5. 바이너리 검증 결과
```bash
for pdf in *.pdf; do
  echo "=== $pdf ==="
  strings "$pdf" | grep 'BUILD_SIGNATURE:'
  strings "$pdf" | grep 'DATA_SIGNATURE:'
  echo ""
done

# 예상 출력:
=== QuickCheck_abc123.pdf ===
BUILD_SIGNATURE: vABSOLUTE-FINAL-12
DATA_SIGNATURE: abc12345

=== Financial_abc123.pdf ===
BUILD_SIGNATURE: vABSOLUTE-FINAL-12
DATA_SIGNATURE: abc12345

(... 6개 모두 동일)
```

---

## ⚠️ 중요 체크포인트

### 반드시 확인할 것

1. **시그니처가 텍스트인가?**
   - ✅ HTML에 plain text로 삽입됨
   - ✅ PDF에서 `strings` 명령으로 추출 가능
   - ❌ graphics/vector/image로 렌더링 안 됨

2. **캐시가 완전히 차단되었는가?**
   - ✅ HTTP 헤더: `Cache-Control: no-store`
   - ✅ 파일명에 build_hash 포함
   - ✅ build_hash 변경 시 강제 재생성

3. **Narrative가 실제 데이터를 사용하는가?**
   - ✅ `modules_data` 에서 값 추출
   - ✅ NPV, IRR, ROI 실제 숫자 표시
   - ❌ "N/A (검증 필요)" 템플릿 사용 안 함

4. **6개 보고서 모두 동일 기준 적용되었는가?**
   - ✅ QuickCheck, Financial, LH Technical
   - ✅ Executive, Landowner, All-in-One

---

## 🎯 사용자 검증 방법

사용자는 다음 명령으로 검증할 것입니다:

```bash
# 1. 바이너리 검색
strings report.pdf | grep 'BUILD_SIGNATURE'

# 2. Python 스크립트
python <<EOF
with open('report.pdf', 'rb') as f:
    content = f.read()
    print("BUILD_SIGNATURE:", b'BUILD_SIGNATURE:' in content)
    print("DATA_SIGNATURE:", b'DATA_SIGNATURE:' in content)
EOF

# 3. PyPDF2 텍스트 추출
python <<EOF
import PyPDF2
with open('report.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    text = ''.join(p.extract_text() for p in reader.pages)
    print("Signatures found:", "BUILD_SIGNATURE" in text)
EOF
```

**예상 결과**: 모두 `True` 또는 시그니처 문자열 출력

---

## 📌 핵심 요약

1. ✅ **Searchable Signature**: 모든 PDF에 텍스트로 삽입
2. ✅ **Cache Busting**: build_hash 기반 강제 재생성
3. ✅ **N/A 제거**: Narrative가 실제 데이터 사용
4. ✅ **Legacy 차단**: v4.1 경로 완전 제거
5. ✅ **Test Coverage**: 자동 검증 테스트 추가
6. ✅ **Binary Verifiable**: `strings` 명령으로 검증 가능

---

**이 프롬프트를 Genspark AI에 그대로 제출하세요.**

수정 완료 후 **실제 PDF 샘플 1세트**와 **바이너리 검증 결과**를 첨부해야 합니다.
