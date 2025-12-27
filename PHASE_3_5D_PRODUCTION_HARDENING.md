# Phase 3.5D — 실전 완결 점검 (Production Hardening)

**Date**: 2025-12-27  
**Status**: 🔄 IN PROGRESS  
**Goal**: "엔지니어 기준 100%" → "외부 실무 기준 100%"

---

## 🎯 Phase 3.5D 목표

### 현재 상태
- ✅ 구조적 완성도: 100%
- ⚠️ 실무 가용성: 85% (데이터는 있으나 완전 통합 필요)
- ⚠️ 외부 오해 리스크: 중간

### 목표 상태
- ✅ 구조적 완성도: 100%
- ✅ 실무 가용성: 100%
- ✅ 외부 오해 리스크: 0

---

## 🔍 발견된 실전 리스크 (4가지)

### 1️⃣ PDF ↔ HTML 데이터 구조 불일치

**문제**:
```python
# HTML Renderer (✅ 올바름)
html_data = {
    'm6_result': {...},
    'modules': {
        'M2': {summary, details, raw_data},
        'M3': {summary, details, raw_data},
        ...
    }
}

# PDF Generator (❌ 문제)
pdf_data = request.data  # 단독 모듈 데이터만!
# M6 result가 없음!
```

**위험**:
- HTML은 M6 판단 표시 O
- PDF는 M6 판단 표시 X
- → **"PDF만 보면 이게 최종인가?" 오해 발생**

**영향**:
- 모듈별 PDF (M2~M5) 단독 배포 시 혼란
- LH/지자체 제출 시 리스크

---

### 2️⃣ 모듈별 PDF에 M6 판단 요약 블록 없음

**현재 구조**:
```
M2 PDF:
┌─────────────────────────────┐
│ M2: 토지가치 분석 보고서    │
├─────────────────────────────┤
│ 1. 토지가치 분석 요약       │
│ 2. 거래사례 분석            │
│ 3. 가격 범위 산정           │
└─────────────────────────────┘
```

**문제**: M6 최종 판단이 어디에도 없음!

**이상적 구조**:
```
M2 PDF:
┌─────────────────────────────┐
│ M2: 토지가치 분석 보고서    │
├─────────────────────────────┤
│ ⚠️ 본 보고서는 ZeroSite 4.0│
│    분석의 일부입니다        │
│                             │
│ 최종 판단: [M6 결론]        │
│ LH 점수: XX/100             │
│ 판정: GO/CONDITIONAL/NOGO   │
├─────────────────────────────┤
│ 1. M2 토지가치 분석 (근거)  │
│ 2. 거래사례 분석 (근거)     │
│ 3. 가격 범위 산정 (근거)    │
└─────────────────────────────┘
```

---

### 3️⃣ 최종보고서 6종 정보 밀도 차이

**현재**:
| 보고서 | M2 토지가치 | M3 유형 | M4 세대수 | M5 NPV | M6 판단 |
|--------|------------|---------|----------|--------|---------|
| AllInOne | ✅ 상세 | ✅ 상세 | ✅ 상세 | ✅ 상세 | ✅ 상세 |
| LandownerSummary | ❌ 없음 | ❌ 없음 | ❌ 없음 | ❌ 없음 | ✅ 있음 |
| QuickCheck | ❌ 없음 | ❌ 없음 | ❌ 없음 | ❌ 없음 | ✅ 있음 |

**위험**:
- "Landowner Summary에 M2 데이터가 없네? 이거 믿을 수 있나?"
- "Quick Check는 점수만 있고 근거가 없네?"

**해결**:
| 보고서 | M2 토지가치 | M3 유형 | M4 세대수 | M5 NPV | M6 판단 |
|--------|------------|---------|----------|--------|---------|
| AllInOne | ✅ 상세 표 | ✅ 상세 표 | ✅ 상세 표 | ✅ 상세 표 | ✅ 상세 |
| LandownerSummary | ✅ 1줄 요약 | ✅ 1줄 요약 | ✅ 1줄 요약 | ✅ 1줄 요약 | ✅ 상세 |
| QuickCheck | ✅ 수치만 | ✅ 수치만 | ✅ 수치만 | ✅ 수치만 | ✅ 상세 |

→ **분량은 다르지만 핵심 수치는 모두 존재**

---

### 4️⃣ 단위 포맷 통일 필요

**현재**:
```python
# HTML Renderer
format_currency(6081933538) → "60.82억원"

# PDF Generator
f"{value:,.0f}원" → "6,081,933,538원"

# Excel Export (있다면)
f"{value/100000000:.2f}" → "60.82"
```

**위험**:
- 같은 숫자가 다르게 표시
- "HTML: 60.82억원, PDF: 6,081,933,538원 → 다른 값인가?"

---

## ✅ 해결 방안

### 프롬프트① PDF ↔ HTML 데이터 구조 통일

**현재 문제**:
```python
# app/api/endpoints/pdf_reports.py
@router.post("/generate/{module_id}")
async def generate_module_pdf(module_id: str, request: PDFGenerationRequest):
    pdf_bytes = pdf_generator.generate_m2_appraisal_pdf(request.data)
    # request.data = M2 데이터만! M6 없음!
```

**수정안**:
```python
# 1. PDFGenerationRequest 수정
class PDFGenerationRequest(BaseModel):
    module_id: str
    data: Dict[str, Any]
    m6_result: Dict[str, Any]  # ✅ 추가!

# 2. PDF Generator 수정
class ModulePDFGenerator:
    def generate_m2_appraisal_pdf(
        self, 
        data: Dict[str, Any],
        m6_result: Dict[str, Any] = None  # ✅ 추가!
    ) -> bytes:
        # ✅ M6 결과 header 추가
        if m6_result:
            self._add_m6_header(story, m6_result)
        
        # 기존 M2 내용
        ...
```

**검증 코드**:
```python
def test_pdf_html_data_consistency():
    """PDF와 HTML이 동일한 데이터 구조 사용 확인"""
    assembled_data = assemble_final_report('all_in_one', canonical_data, ctx)
    
    # HTML 생성
    html = render_simple_html(assembled_data)
    
    # PDF 생성 (동일한 assembled_data 사용)
    pdf = generate_pdf(assembled_data)
    
    # 데이터 추출
    html_m2_value = extract_value(html, 'M2 토지가치')
    pdf_m2_value = extract_value(pdf, 'M2 토지가치')
    
    assert html_m2_value == pdf_m2_value
```

---

### 프롬프트② 모듈별 PDF에 M6 판단 헤더 추가

**파일**: `app/services/pdf_generators/module_pdf_generator.py`

**추가 메서드**:
```python
def _add_m6_disclaimer_header(self, story, m6_result: Dict[str, Any]):
    """
    M6 판단 요약 헤더 추가 (모든 모듈 PDF에 공통)
    
    Args:
        story: ReportLab story
        m6_result: M6 판단 결과
    """
    styles = self._get_styles()
    
    # Disclaimer box
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName=self.font_name,
        fontSize=10,
        textColor=colors.HexColor('#DC2626'),  # Red
        backColor=colors.HexColor('#FEF2F2'),  # Light red
        borderPadding=10,
        borderWidth=1,
        borderColor=colors.HexColor('#DC2626')
    )
    
    judgement = m6_result.get('judgement', 'N/A')
    score = m6_result.get('lh_score_total', 0)
    conclusion = m6_result.get('conclusion', '판단 없음')
    
    disclaimer_text = f"""
<b>⚠️ 본 보고서는 ZeroSite 4.0 종합 분석의 일부입니다</b><br/>
<br/>
본 보고서의 데이터는 최종 판단을 위한 <b>근거 자료</b>이며,
단독으로 사업 가부를 결정할 수 없습니다.<br/>
<br/>
<b>최종 판단 (M6):</b> {conclusion}<br/>
<b>LH 심사 점수:</b> {score:.1f}/100<br/>
<b>판정:</b> {judgement}<br/>
<br/>
<i>※ 전체 분석 결과는 ZeroSite 4.0 종합 보고서를 참조하십시오.</i>
"""
    
    story.append(Paragraph(disclaimer_text, disclaimer_style))
    story.append(Spacer(1, 0.3*inch))
```

**적용**:
```python
def generate_m2_appraisal_pdf(self, data: Dict[str, Any], m6_result: Dict[str, Any] = None):
    story = []
    
    # ✅ M6 헤더 추가
    if m6_result:
        self._add_m6_disclaimer_header(story, m6_result)
    
    # 기존 M2 내용
    story.append(Paragraph("M2: 토지가치 분석 보고서", title_style))
    ...
```

---

### 프롬프트③ 최종보고서 6종 정보 밀도 보정

**파일**: `app/services/m6_centered_report_base.py`

**수정 포인트**:

#### LandownerSummaryReport
```python
def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
    # ✅ 핵심 수치 1줄 요약 추가
    m2 = m1_m5_data.get('m2', {})
    m3 = m1_m5_data.get('m3', {})
    m4 = m1_m5_data.get('m4', {})
    m5 = m1_m5_data.get('m5', {})
    
    return {
        'report_type': 'landowner_summary',
        'report_name': '토지주 요약 보고서',
        
        # ✅ 추가: 핵심 수치 요약
        'key_numbers': {
            'm2_land_value': m2.get('land_value', 0),
            'm3_recommended_type': m3.get('recommended_type', 'N/A'),
            'm4_units': m4.get('total_units', 0),
            'm5_npv': m5.get('npv_public_krw', 0),
            'm5_irr': m5.get('irr_pct', 0)
        },
        
        # 기존 필드들...
        'final_conclusion': self.get_conclusion_sentence(),
        ...
    }
```

#### QuickCheckReport
```python
def generate(self, m1_m5_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'report_type': 'quick_check',
        'report_name': '간편 체크 보고서 - 1분 요약',
        
        # ✅ 추가: 핵심 수치 카드
        'quick_metrics': [
            {'label': '토지가치', 'value': format_currency(m2.get('land_value', 0))},
            {'label': '추천유형', 'value': m3.get('recommended_type', 'N/A')},
            {'label': '세대수', 'value': f"{m4.get('total_units', 0)}세대"},
            {'label': 'NPV', 'value': format_currency(m5.get('npv_public_krw', 0))},
            {'label': 'IRR', 'value': f"{m5.get('irr_pct', 0):.1f}%"}
        ],
        
        # 기존 필드들...
    }
```

---

### 프롬프트④ 단위 포맷 공통 유틸 통일

**파일**: `app/services/format_utils.py` (신규)

```python
"""
ZeroSite 4.0 Format Utilities
==============================

모든 렌더러(HTML/PDF/Excel)에서 사용하는 공통 포맷 함수

원칙:
- 동일한 숫자는 동일한 표현
- 한국식 단위 사용 (억원, ㎡, 세대)
"""

def format_currency_kr(value: float, short: bool = False) -> str:
    """
    통화 포맷 (한국식 억원 표시)
    
    Args:
        value: 금액 (원)
        short: True면 "60.82억", False면 "60.82억원"
    
    Returns:
        포맷된 문자열
    """
    if not value:
        return "데이터 없음"
    
    # 1억 = 100,000,000원
    billions = value / 100_000_000
    if billions >= 1:
        suffix = "억" if short else "억원"
        return f"{billions:.2f}{suffix}"
    
    # 1만원 = 10,000원
    ten_thousands = value / 10_000
    if ten_thousands >= 1:
        suffix = "만" if short else "만원"
        return f"{ten_thousands:.0f}{suffix}"
    
    return f"{value:,.0f}원"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    퍼센트 포맷
    
    Args:
        value: 백분율 값
        decimals: 소수점 자릿수
    
    Returns:
        포맷된 문자열
    """
    if value is None:
        return "데이터 없음"
    return f"{value:.{decimals}f}%"


def format_area_sqm(value: float) -> str:
    """
    면적 포맷 (㎡)
    
    Args:
        value: 면적 (제곱미터)
    
    Returns:
        포맷된 문자열
    """
    if not value:
        return "데이터 없음"
    return f"{value:,.0f}㎡"


def format_unit_count(value: int, unit: str = "세대") -> str:
    """
    단위 개수 포맷
    
    Args:
        value: 개수
        unit: 단위 (세대, 가구, 층 등)
    
    Returns:
        포맷된 문자열
    """
    if not value:
        return "데이터 없음"
    return f"{value:,}{unit}"


# ✅ 모든 렌더러에서 import
# from app.services.format_utils import (
#     format_currency_kr,
#     format_percentage,
#     format_area_sqm,
#     format_unit_count
# )
```

**적용**:
```python
# HTML Renderer
from app.services.format_utils import format_currency_kr

value = format_currency_kr(6081933538)  # "60.82억원"

# PDF Generator
from app.services.format_utils import format_currency_kr

value = format_currency_kr(6081933538)  # "60.82억원"

# Excel Generator (if exists)
from app.services.format_utils import format_currency_kr

value = format_currency_kr(6081933538)  # "60.82억원"
```

---

## 🧪 최종 PASS 조건 (실무 기준)

| # | 질문 | 검증 방법 | PASS 기준 |
|---|------|----------|----------|
| 1 | M2~M5 PDF 단독으로 봐도 "최종 판단은 M6"가 명확한가 | PDF 상단에 M6 disclaimer 있는지 확인 | YES |
| 2 | HTML과 PDF의 숫자·표·섹션 순서가 동일한가 | 동일 데이터로 생성 후 수치 비교 | YES |
| 3 | 최종보고서 6종에서 핵심 수치가 빠진 게 없는가 | Landowner/Quick에도 M2~M5 수치 있는지 | YES |
| 4 | 보고서 종류 차이는 "분량"이지 "결론 인상"이 아닌가 | 결론 문장 동일 & 판단 없는지 | YES |
| 5 | 외부(LH/지자체/토지주)가 오해할 여지가 없는가 | 실제 사용자 시뮬레이션 | YES |

---

## 📝 작업 계획

### Step 1: 단위 포맷 유틸 생성 ✅
- [ ] `app/services/format_utils.py` 생성
- [ ] 공통 함수 4개 구현
- [ ] 테스트 작성

### Step 2: HTML Renderer에 적용
- [ ] `simple_html_renderer.py`에서 format_utils import
- [ ] 기존 format_currency → format_currency_kr 변경

### Step 3: PDF Generator 수정
- [ ] M6 result 파라미터 추가
- [ ] `_add_m6_disclaimer_header()` 메서드 추가
- [ ] 모든 generate 메서드에 적용
- [ ] format_utils 적용

### Step 4: 최종보고서 6종 보정
- [ ] LandownerSummaryReport에 key_numbers 추가
- [ ] QuickCheckReport에 quick_metrics 추가
- [ ] HTML renderer에서 표시

### Step 5: 검증 테스트
- [ ] test_pdf_html_consistency.py 작성
- [ ] test_module_pdf_has_m6_header.py 작성
- [ ] test_all_reports_have_key_numbers.py 작성
- [ ] test_format_consistency.py 작성

### Step 6: 최종 실전 점검
- [ ] 5개 PASS 조건 실제 검증
- [ ] 외부 제출 시뮬레이션

---

## 🎯 예상 결과

### Before (Phase 3.5C)
- 구조적 완성도: 100%
- 실무 가용성: 85%
- 외부 오해 리스크: 중간

### After (Phase 3.5D)
- 구조적 완성도: 100%
- 실무 가용성: 100%
- 외부 오해 리스크: 0

---

**Generated**: 2025-12-27  
**Status**: 🔄 IN PROGRESS  
**Priority**: HIGH
