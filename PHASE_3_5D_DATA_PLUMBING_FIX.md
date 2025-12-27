# Phase 3.5D — 데이터 배관 완전 봉인 (실전 완결)

**Date**: 2025-12-27  
**Status**: 🔄 진행중  
**Critical**: 데이터 계약 불일치로 인한 조용한 실패(Silent Failure)

---

## 🚨 핵심 진단

### 문제의 본질
**"데이터는 있지만, 서로 못 알아봄"**

```
Assembler → m1_m5_evidence = {"m2": {...}, "m3": {...}}  (소문자)
                    ↓
Report Generator → data.get("M2")  (대문자) → None!
                    ↓
HTML Renderer → modules["M2"]["summary"]  (대문자) → None!
                    ↓
Result: "N/A" everywhere
```

---

## 🔍 발견된 4가지 불일치

### 1️⃣ 키 이름 불일치 (가장 치명적)
```python
# Assembler (현재)
m1_m5_evidence = {
    'm1': ...,  # ❌ 소문자
    'm2': ...,  # ❌ 소문자
    'm3': ...,  # ❌ 소문자
}

# Data Contract (표준)
assembled_data = {
    "modules": {
        "M2": ...,  # ✅ 대문자
        "M3": ...,  # ✅ 대문자
    }
}
```

### 2️⃣ 구조 깊이 불일치
```python
# 현재: flat 구조
data["m2"]["land_value"]

# 표준: nested 구조
data["modules"]["M2"]["summary"]["land_value"]
```

### 3️⃣ PDF API가 단독 데이터만 받음
```python
# 현재
PDFGenerationRequest:
    data: Dict[str, Any]  # M2 단독 데이터

# 필요
PDFGenerationRequest:
    assembled_data: Dict[str, Any]  # 전체 구조
```

### 4️⃣ Generator 인터페이스 불일치
```python
# 현재
def generate(self, m1_m5_data: Dict[str, Any])

# 표준
def generate(self, assembled_data: Dict[str, Any])
```

---

## ✅ 해결 방안 (우선순위순)

### 프롬프트① Assembler 수정 (최우선, 70% 해결)

**파일**: `app/services/final_report_assembler.py`

**현재**:
```python
m1_m5_evidence = {
    'm1': canonical_data.get('m1', {}),
    'm2': canonical_data.get('m2_result', {}),
    'm3': canonical_data.get('m3_result', {}),
    'm4': canonical_data.get('m4_result', {}),
    'm5': canonical_data.get('m5_result', {}),
}

report_data = create_m6_centered_report(
    report_type=report_type,
    m6_result=m6_result,
    m1_m5_data=m1_m5_evidence  # ❌ 소문자 키
)
```

**수정**:
```python
# ✅ 표준 스키마로 assembled_data 생성
assembled_data = {
    "m6_result": m6_result,
    "modules": {
        "M1": {
            "summary": canonical_data.get('m1', {}),
            "details": {},
            "raw_data": {}
        },
        "M2": {
            "summary": canonical_data.get('m2_result', {}),
            "details": {},
            "raw_data": {}
        },
        "M3": {
            "summary": canonical_data.get('m3_result', {}),
            "details": {},
            "raw_data": {}
        },
        "M4": {
            "summary": canonical_data.get('m4_result', {}),
            "details": {},
            "raw_data": {}
        },
        "M5": {
            "summary": canonical_data.get('m5_result', {}),
            "details": {},
            "raw_data": {}
        }
    }
}

report_data = create_m6_centered_report(
    report_type=report_type,
    assembled_data=assembled_data  # ✅ 표준 스키마
)
```

---

### 프롬프트② Report Generator 인터페이스 통일

**파일**: `app/services/m6_centered_report_base.py`

**현재**:
```python
class AllInOneReport(M6CenteredReportBase):
    def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
        m2 = m1_m5_data.get('m2', {})  # ❌ 소문자, flat
        ...
```

**수정**:
```python
class AllInOneReport(M6CenteredReportBase):
    def generate(self, assembled_data: Dict[str, Any]) -> Dict[str, Any]:
        # ✅ 표준 스키마 사용
        m2_summary = assembled_data["modules"]["M2"]["summary"]
        m3_summary = assembled_data["modules"]["M3"]["summary"]
        m4_summary = assembled_data["modules"]["M4"]["summary"]
        m5_summary = assembled_data["modules"]["M5"]["summary"]
        
        # ✅ 헬퍼 함수 사용
        from app.services.data_contract import get_module_summary
        m2_summary = get_module_summary(assembled_data, "M2")
        ...
```

**적용 대상** (6개 클래스):
1. AllInOneReport
2. LandownerSummaryReport
3. LHTechnicalReport
4. FinancialFeasibilityReport
5. QuickCheckReport
6. PresentationReport

---

### 프롬프트③ Simple HTML Renderer 수정

**파일**: `app/services/simple_html_renderer.py`

**현재**:
```python
def render_simple_html(report_data: Dict[str, Any]) -> str:
    evidence = report_data.get('evidence_data', {})
    m2 = evidence.get('m2_appraisal', {})  # ❌ 커스텀 키
    ...
```

**수정**:
```python
def render_simple_html(assembled_data: Dict[str, Any]) -> str:
    # ✅ 표준 스키마 직접 참조
    from app.services.data_contract import get_module_summary
    
    m2_summary = get_module_summary(assembled_data, "M2")
    m3_summary = get_module_summary(assembled_data, "M3")
    m4_summary = get_module_summary(assembled_data, "M4")
    m5_summary = get_module_summary(assembled_data, "M5")
    
    # M6 판단
    m6_result = assembled_data["m6_result"]
    ...
```

---

### 프롬프트④ PDF API 엔드포인트 수정

**파일**: `app/api/endpoints/pdf_reports.py`

**현재**:
```python
class PDFGenerationRequest(BaseModel):
    module_id: str
    data: Dict[str, Any]  # ❌ 단독 모듈 데이터

@router.post("/generate/{module_id}")
async def generate_module_pdf(module_id: str, request: PDFGenerationRequest):
    pdf_bytes = pdf_generator.generate_m2_appraisal_pdf(request.data)
    # ❌ M6 없음!
```

**수정**:
```python
class PDFGenerationRequest(BaseModel):
    assembled_data: Dict[str, Any]  # ✅ 전체 구조

@router.post("/generate/{module_id}")
async def generate_module_pdf(module_id: str, request: PDFGenerationRequest):
    # ✅ assembled_data 전체 전달
    pdf_bytes = pdf_generator.generate_module_pdf(
        module_id=module_id,
        assembled_data=request.assembled_data
    )
```

---

### 프롬프트⑤ PDF Generator 수정

**파일**: `app/services/pdf_generators/module_pdf_generator.py`

**현재**:
```python
def generate_m2_appraisal_pdf(self, data: Dict[str, Any]) -> bytes:
    land_value = data.get('land_value', 0)  # ❌ flat 구조
    ...
```

**수정**:
```python
def generate_module_pdf(
    self,
    module_id: str,
    assembled_data: Dict[str, Any]
) -> bytes:
    """
    모듈 PDF 생성 (표준 스키마 사용)
    
    Args:
        module_id: M2, M3, M4, M5
        assembled_data: 표준 스키마
    """
    # ✅ M6 헤더 추가
    m6_result = assembled_data["m6_result"]
    self._add_m6_disclaimer_header(story, m6_result)
    
    # ✅ 표준 스키마 사용
    from app.services.data_contract import get_module_summary
    module_summary = get_module_summary(assembled_data, module_id)
    
    # 모듈별 분기
    if module_id == "M2":
        return self._generate_m2_content(story, module_summary, m6_result)
    elif module_id == "M3":
        return self._generate_m3_content(story, module_summary, m6_result)
    ...
```

---

## 🧪 검증 테스트

### test_data_contract_consistency.py (신규)

```python
def test_assembler_produces_standard_schema():
    """Assembler가 표준 스키마 생성하는지 확인"""
    assembled = assemble_final_report('all_in_one', canonical_data, ctx)
    
    # 표준 스키마 검증
    assert "m6_result" in assembled
    assert "modules" in assembled
    assert "M2" in assembled["modules"]
    assert "summary" in assembled["modules"]["M2"]
    
    # 금지 패턴 확인
    assert "m2" not in assembled  # 소문자 금지
    assert "land_value" not in assembled  # flat 구조 금지


def test_all_components_use_same_keys():
    """모든 컴포넌트가 동일한 키 사용하는지 확인"""
    assembled = assemble_final_report('all_in_one', canonical_data, ctx)
    
    # HTML Renderer
    html = render_simple_html(assembled)
    assert "60.82억원" in html  # M2 data
    
    # Report Generator
    report = create_m6_centered_report('all_in_one', assembled)
    assert report['evidence_data']['m2_appraisal']['land_value'] > 0
    
    # PDF (미래 구현)
    # pdf = generate_module_pdf("M2", assembled)
    # assert "60.82억원" in extract_text(pdf)
```

---

## 📝 작업 순서 (Critical Path)

### Step 1: Data Contract 생성 ✅
- [x] app/services/data_contract.py 작성
- [x] 표준 스키마 정의
- [x] 헬퍼 함수 구현

### Step 2: Assembler 수정 (최우선!)
- [ ] m1_m5_evidence → assembled_data["modules"] 변경
- [ ] 대문자 키 사용 (M2, M3, M4, M5)
- [ ] summary/details/raw_data 구조 생성

### Step 3: Report Generator 수정
- [ ] 6개 클래스의 generate() 시그니처 변경
- [ ] m1_m5_data → assembled_data 변경
- [ ] get_module_summary() 헬퍼 사용

### Step 4: HTML Renderer 수정
- [ ] evidence_data 대신 assembled_data 직접 참조
- [ ] 표준 스키마 키 사용

### Step 5: 검증 테스트
- [ ] test_data_contract_consistency.py 작성
- [ ] Phase 3.5C 테스트 재실행
- [ ] 실제 데이터 표시 확인

---

## 🎯 Phase 3.5D 완료 기준

| 기준 | 현재 | 목표 |
|------|------|------|
| 키 이름 일관성 | ❌ m2 vs M2 | ✅ 전부 M2 |
| 구조 깊이 일관성 | ❌ flat vs nested | ✅ 전부 nested |
| Assembler 표준 준수 | ❌ 커스텀 | ✅ 표준 |
| Generator 표준 준수 | ❌ m1_m5_data | ✅ assembled_data |
| Renderer 표준 준수 | ❌ evidence_data | ✅ assembled_data |
| HTML 데이터 표시 | ⚠️ 일부 | ✅ 전체 |
| PDF 데이터 표시 | ❌ N/A | ✅ 전체 |

---

## 💡 왜 이게 70% 해결인가?

**Data Contract 통일 = 모든 컴포넌트가 같은 언어로 말함**

Before:
```
Assembler: "m2 데이터 줄게"
Generator: "M2 데이터 어디 있어?"
Renderer: "modules.M2.summary 어디 있어?"
→ 서로 못 알아봄 → N/A
```

After:
```
Assembler: "modules.M2.summary 줄게"
Generator: "modules.M2.summary 받았어"
Renderer: "modules.M2.summary 표시할게"
→ 완벽하게 통신 → 60.82억원
```

---

**Generated**: 2025-12-27  
**Priority**: CRITICAL  
**Next**: Assembler 수정 착수
