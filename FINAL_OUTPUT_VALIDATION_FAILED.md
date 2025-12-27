# 🚨 ZeroSite 4.0 최종 출력물 검증 결과 - FAILED

**검증 일시**: 2025-12-27  
**검증 대상**: HTML Renderer, PDF Generator, 6종 최종 보고서  
**검증 기준**: Phase 2/3+ M6 Single Source of Truth 원칙

---

## ❌ **검증 결과: FAILED**

### 종합 판정

| 항목 | 상태 | 위반 건수 |
|------|------|----------|
| **HTML ↔ PDF 정합성** | ⏳ 검증 중 | N/A |
| **6종 보고서 판단 일관성** | ⏳ 검증 중 | N/A |
| **M6 중심성** | ❌ **FAILED** | 다수 |
| **조건 로직 금지** | ❌ **FAILED** | **11+건** |
| **표현 리스크** | 🔴 **HIGH** | 다수 |

---

## 🔴 발견된 심각한 위반 사항

### 1. HTML Renderer에서 독립 판단 로직 발견

#### 위반 1-1: 문자열 패턴 매칭으로 판단 추론

**파일**: `app/services/final_report_html_renderer.py`  
**라인**: 596-607

```python
if "추진 권장" in data.get("final_decision", ""):
    decision_class = ""
elif "조건부" in data.get("final_decision", ""):
    decision_class = "conditional"
else:
    decision_class = "negative"
```

**문제**:
- M6 `judgement` 값(`GO`/`CONDITIONAL`/`NOGO`)이 아닌 **한국어 문자열**을 파싱
- 문자열 변경 시 로직이 깨질 수 있음
- Phase 2 원칙 위반: Renderer는 View-only여야 함

**영향도**: 🔴 **CRITICAL**

---

#### 위반 1-2: ROI 기반 판단 문장 생성 (다수)

**파일**: `app/services/final_report_html_renderer.py`

| 라인 | 코드 | 문제 |
|------|------|------|
| 1572 | `'우수한' if roi_pct >= 15 else '적정한'` | ROI 기반 주관 판단 |
| 1626 | `'경쟁력 있는' if roi_pct >= 12 else '검토가 필요한'` | ROI 기반 주관 판단 |
| 2130-2131 | `'업계 평균 이상' if roi_pct >= 15 else '평균 수준'` | ROI 기반 비교 판단 |
| 2132 | `100000000 * roi_pct / 100 if roi_pct else None` | ROI 기반 계산 표시 |
| 2761 | `'#10B981' if roi_pct >= 15 else '#F59E0B'` | ROI 기반 색상 결정 |
| 2765 | `'✅ 업계 평균 이상' if roi_pct >= 15` | ROI 기반 평가 |

**문제**:
- **Kill-Switch를 통과했지만 실제로는 위반**
- ROI 값에 따라 "우수한", "경쟁력 있는" 등 **판단 표현 생성**
- M6 판단과 무관하게 **독립적인 품질 평가** 수행
- 사용자가 "ROI 15% 넘으면 우수하구나"라고 **오해 가능**

**영향도**: 🔴 **CRITICAL**

---

#### 위반 1-3: NPV 기반 판단 문장

**파일**: `app/services/final_report_html_renderer.py`  
**라인**: 3265

```python
'충분히' if npv_krw and npv_krw >= 500000000 else ''
```

**문제**:
- NPV 5억 이상이면 "충분히 있다고 판단"
- NPV 5억 미만이면 그냥 "있다고 판단"
- **M6 판단과 무관한 재무 판단**

**영향도**: 🔴 **CRITICAL**

---

### 2. Kill-Switch 탐지 누락 원인 분석

#### 왜 이 패턴들이 탐지되지 않았는가?

**Kill-Switch 패턴**:
```python
pattern=r"if\s+roi\s*[><=!]+\s*\d+"
```

**실제 코드**:
```python
'우수한' if roi_pct >= 15 else '적정한'
```

**문제**:
- Kill-Switch는 `if roi >= 10` 형태만 탐지
- **삼항 연산자** `value if condition else other` 형태는 미탐지
- **변수명 차이** (`roi` vs `roi_pct`)도 누락 원인

**해결책**: Kill-Switch 패턴 강화 필요

---

## 🔴 체크 결과 상세

### ✅ 체크 1: M6 중심성

**결과**: ❌ **FAILED**

**문제점**:
1. HTML Renderer가 `final_decision` 문자열을 파싱하여 스타일 결정
2. M6 `judgement` Enum(`GO`/`CONDITIONAL`/`NOGO`)을 직접 참조하지 않음
3. 보고서 첫 섹션에 M6 판단이 명시되지만, **중간에 M5 데이터가 판단처럼 보임**

**예시**:
```html
ROI 15%는 '업계 평균 이상'으로 '우수한' 수익성을 보입니다.
```
→ 사용자 오해: "ROI 15%면 우수한 거구나"

---

### ⏳ 체크 2: HTML ↔ PDF 정합성

**결과**: ⏳ **검증 필요**

**이유**: PDF Generator 코드 미확인

**다음 단계**: `pdf_download_standardized.py` 검증 필요

---

### ❌ 체크 3: 시각 요소의 판단 오염

**결과**: ❌ **FAILED**

**문제**:
- Line 2761: ROI 15% 이상이면 녹색, 미만이면 주황색
- **M6 판단과 무관하게 색상 결정**
- 사용자가 "녹색 = 좋음"으로 오해

---

### ⏳ 체크 4: 6종 보고서 독립 읽기 테스트

**결과**: ⏳ **검증 필요**

**다음 단계**: 각 보고서 타입별 출력 샘플 생성 및 교차 검증 필요

---

### ❌ 체크 5: 보완 포인트 표현 일관성

**결과**: ❌ **FAILED** (추정)

**문제 예상**:
- "향후 조정하면 가능할 수 있음" 같은 희망 표현
- "전략", "제안", "권장" 등 혼재

**검증 필요**: `final_report_assembler.py`의 improvement_points 생성 로직

---

### ❌ 체크 6: 사람 기준 리스크 문구

**결과**: ❌ **FAILED**

**발견된 금지 문구**:
- Line 1572: "우수한" (주관적 평가)
- Line 1626: "경쟁력 있는" (주관적 평가)
- Line 3265: "충분히" (강조 표현)

---

## 📋 수정 필요 프롬프트

### 🔴 우선순위 1: HTML Renderer 조건 로직 제거

#### 수정 1-1: decision_class 로직 교체

**파일**: `app/services/final_report_html_renderer.py`  
**라인**: 596-607

**문제**:
```python
if "추진 권장" in data.get("final_decision", ""):
    decision_class = ""
elif "조건부" in data.get("final_decision", ""):
    decision_class = "conditional"
else:
    decision_class = "negative"
```

**수정 지시**:
```python
# Phase 3+: M6 judgement Enum 직접 참조로 교체
judgement = data.get("judgement", "NOGO")  # M6 표준 필드
decision_class_map = {
    "GO": "positive",
    "CONDITIONAL": "conditional",
    "NOGO": "negative"
}
decision_class = decision_class_map.get(judgement, "negative")
```

**검증 방법**:
- `data`에 `judgement` 필드가 M6에서 올바르게 전달되는지 확인
- 없으면 `final_report_assembler.py`에서 추가

---

#### 수정 1-2: ROI 기반 판단 문장 제거 (6건)

**파일**: `app/services/final_report_html_renderer.py`  
**라인**: 1572, 1626, 2130-2131, 2132, 2761, 2765

**수정 지시 (통일)**:
```
모든 ROI 기반 조건문 삭제:
- '우수한' if roi_pct >= 15 → '양호'로 고정
- '경쟁력 있는' if roi_pct >= 12 → '업계 평균 수준'으로 고정
- 색상 조건 'if roi_pct >= 15' → judgement 기반으로 교체:
  * judgement == 'GO' → 녹색
  * judgement == 'CONDITIONAL' → 주황색
  * judgement == 'NOGO' → 빨간색
```

**Before**:
```python
{'우수한' if roi_pct >= 15 else '적정한'}
```

**After**:
```python
양호  # 고정값, M5 데이터는 숫자만 표시
```

**Before**:
```python
color: {'#10B981' if roi_pct >= 15 else '#F59E0B'}
```

**After**:
```python
color: {get_judgement_color(data.get('judgement', 'NOGO'))}

# 헬퍼 함수 추가:
def get_judgement_color(judgement):
    return {
        'GO': '#10B981',      # Green
        'CONDITIONAL': '#F59E0B',  # Amber
        'NOGO': '#DC2626'     # Red
    }.get(judgement, '#6B7280')  # Gray fallback
```

---

#### 수정 1-3: NPV 기반 판단 제거

**파일**: `app/services/final_report_html_renderer.py`  
**라인**: 3265

**Before**:
```python
'충분히' if npv_krw >= 500000000 else ''
```

**After**:
```python
''  # 강조 표현 완전 제거
```

---

### 🔴 우선순위 2: Kill-Switch 패턴 강화

**파일**: `scripts/kill_switch_checker.py`

**추가 패턴**:
```python
# 기존 패턴 (단순 if문)
ForbiddenPattern(
    pattern=r"if\s+roi\s*[><=!]+\s*\d+",
    description="ROI-based judgement (if roi >= 10)",
    severity="CRITICAL"
),

# 신규 패턴 (삼항 연산자)
ForbiddenPattern(
    pattern=r"if\s+roi[_a-z]*\s*(?:and\s+)?[_a-z]*\s*[><=!]+\s*\d+",
    description="ROI-based judgement in ternary (value if roi_pct >= 15)",
    severity="CRITICAL"
),
ForbiddenPattern(
    pattern=r"['\"]우수한['\"].*if.*roi",
    description="Subjective phrase with ROI condition ('우수한' if roi)",
    severity="CRITICAL"
),
ForbiddenPattern(
    pattern=r"['\"]경쟁력\s*있는['\"].*if",
    description="Subjective phrase with condition ('경쟁력 있는' if)",
    severity="CRITICAL"
),
ForbiddenPattern(
    pattern=r"if\s+npv[_a-z]*\s*[><=!]+\s*\d+",
    description="NPV-based judgement (if npv >= 500000000)",
    severity="CRITICAL"
),
```

---

### 🔴 우선순위 3: final_report_assembler.py 검증

**다음 검증 필요**:
1. `judgement` 필드가 6종 보고서 모두에 포함되는가?
2. `improvement_points` 표현이 일관적인가?
3. M5 데이터를 판단처럼 서술하는 곳이 있는가?

**검증 명령**:
```bash
grep -n "judgement\|decision\|recommended" app/services/final_report_assembler.py
```

---

## 🎯 수정 완료 기준

### ✅ PASS 조건 (재확인)

1. **조건 로직 0건**
   - `if roi`, `if npv`, `if profit` 패턴 완전 제거
   - Kill-Switch 통과

2. **M6 judgement 직접 참조**
   - 모든 색상/아이콘/스타일이 `judgement` Enum 기반
   - 문자열 파싱 금지

3. **주관 표현 제거**
   - "우수한", "경쟁력 있는", "충분히" 등 제거
   - 객관적 표현으로 대체: "양호", "업계 평균 수준" 등

4. **사람 오해 테스트 통과**
   - "이 보고서는 좀 더 좋아 보이네?" → NO
   - "ROI 15%면 우수한 거구나?" → NO
   - "M6 판단만 보면 되겠네" → YES

---

## 🔥 긴급 조치 필요

### 즉시 수정해야 할 이유

1. **현재 상태**: HTML Renderer가 **독립적으로 판단**을 생성
2. **리스크**: 사용자가 M6 판단과 **다른 인상**을 받을 수 있음
3. **심각도**: 🔴 **CRITICAL** - 배포 즉시 차단 필요

### 수정 순서

1. ✅ Kill-Switch 강화 (삼항 연산자 패턴 추가)
2. ❌ HTML Renderer 조건 로직 제거 (우선순위 1)
3. ⏳ PDF Generator 검증
4. ⏳ 6종 보고서 교차 검증
5. ⏳ 사람 오해 테스트

---

## 📊 검증 진행률

| 단계 | 상태 | 진행률 |
|------|------|--------|
| **HTML Renderer 검증** | ❌ FAILED | 100% |
| **PDF Generator 검증** | ⏳ TODO | 0% |
| **6종 보고서 검증** | ⏳ TODO | 0% |
| **사람 오해 테스트** | ⏳ TODO | 0% |
| **수정 적용** | ⏳ TODO | 0% |
| **재검증** | ⏳ TODO | 0% |

---

**작성일**: 2025-12-27  
**검증자**: ZeroSite 4.0 최종 출력물 검증 엔진  
**상태**: 🔴 **FAILED - 즉시 수정 필요**  
**다음 단계**: 우선순위 1 수정 적용 → Kill-Switch 재실행 → 재검증
