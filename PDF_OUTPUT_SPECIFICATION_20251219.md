# ZeroSite M2-M6 PDF 출력 규격서 (Output Specification)

**Document Type**: PDF/HTML Output Quality Standard  
**Product**: ZeroSite M2-M6 Report Generation System  
**Version**: v4.0 Final Specification  
**Date**: 2025-12-19  
**Purpose**: 모든 PDF/HTML 출력물의 품질 기준 및 검증 절차 정의

---

## 📋 Executive Summary

### 목적

본 문서는 ZeroSite M2~M6 각 모듈의 **PDF 및 HTML 출력물이 충족해야 할 최종 품질 기준**을 정의합니다. 이 규격은:
- 개발자가 PDF 생성 로직을 수정할 때 준수해야 할 **강제 규칙**
- QA 팀이 결과물을 검증할 때 사용하는 **체크리스트**
- AI 코드 생성 시 참조하는 **프롬프트 템플릿**

으로 활용됩니다.

### 적용 범위

- **M2**: 토지 감정평가 보고서
- **M3**: LH 선호유형 분석 보고서
- **M4**: 건축규모 결정 보고서
- **M5**: 사업성 분석 보고서
- **M6**: LH 심사예측 종합 판단 보고서

---

## 1. 공통 출력 규칙 (All Modules)

### 1.1 데이터 소스 원칙

**CRITICAL RULE**: 모든 PDF 및 HTML 출력은 **`summary` 필드만 사용**

```python
# ✅ CORRECT
score = data['summary']['total_score']

# ❌ WRONG
score = data['details']['scores']['total']  # details는 PDF 본문 상세용
score = data['total_score']  # root level은 deprecated
```

**예외**: PDF 본문의 상세 설명 섹션에서만 `details` 사용 허용

---

### 1.2 Zero Value 처리 원칙

**금지**: `0%`, `₩0`, `0점`, `0세대` 표시

**규칙**:
| 상황 | 표시 방법 | 예시 |
|------|----------|------|
| 값이 None | `N/A (검증 필요)` | 신뢰도: N/A (검증 필요) |
| 값이 실제 0 | `0` (숫자만) | 하자보수비: ₩0 (계약 조건) |
| 계산 불가 | `N/A + 사유 문장` | FAR: N/A (대지면적 미확정) |

---

### 1.3 디자인 시스템 (ZeroSite Theme)

#### **컬러 팔레트** (강제 적용)
```
Primary:   #1E3A8A (Deep Blue)
Accent:    #06B6D4 (Cyan)
Warning:   #F59E0B (Amber) - M4 제약 조건, M6 조건부 판정
Error:     #DC2626 (Red) - M6 Hard Fail만
Gray Text: #64748B (Medium Gray)
Border:    #E2E8F0 (Light Gray)
```

#### **폰트 시스템** (강제 적용)
```
Font Family: NanumBarunGothic (모든 모듈 통일)
H1 (Main Title): 22pt Bold
H2 (Section): 16pt Bold
Body: 10.5pt Regular
Caption (Footer): 9pt Regular
```

#### **페이지 레이아웃** (강제 적용)
```
Margins:
  Top: 25mm
  Bottom: 25mm
  Left: 22mm
  Right: 22mm

Header (모든 페이지):
  - 모듈명 (예: M4: 건축규모 결정 분석)
  - 분석 대상 주소 또는 Parcel ID

Footer (모든 페이지):
  - Page Number (중앙)
  - Copyright: "ⓒ ZEROSITE by Antenna Holdings | nataiheum" (하단 중앙)
```

---

### 1.4 표(Table) 스타일 (강제 적용)

**모든 표는 동일한 스타일 사용**:
```
Header Row:
  - Background: Primary Color (#1E3A8A)
  - Text: White, Bold, 11pt
  - Padding: 10pt

Body Rows:
  - Alternating: White / #F8FAFC (Very Light Gray)
  - Text: Body Font, 10.5pt
  - Padding: 6pt vertical
  - Border: 0.5pt, Border Color (#E2E8F0)
```

---

### 1.5 워터마크 및 브랜딩

**모든 PDF 페이지에 적용**:
- **Watermark**: "ZEROSITE" (중앙, 45도 회전, 6% 투명도)
- **Copyright**: 하단 중앙 "ⓒ ZEROSITE by Antenna Holdings | nataiheum"
- **생성일시**: 첫 페이지에만 표시 (YYYY년 MM월 DD일 HH:MM:SS)

---

## 2. 모듈별 PDF 출력 규격

### 2.1 M2: 토지 감정평가 보고서

#### **문서 톤 & 목적**
- **감정평가 전문 보고서**
- 숫자보다 **해석 문장 우선**
- 가격은 **범위 + 신뢰 구간** 표시

#### **필수 출력 항목**
1. **표지 요약**:
   - 총 토지가치 (₩, summary.land_value_total_krw)
   - 평당 가격 (₩, summary.pyeong_price_krw)
   - 신뢰도 (%, summary.confidence_pct)
   - 거래사례 건수 (summary.transaction_count)

2. **본문 구조**:
   - Executive Summary (신뢰도 해석 포함)
   - 감정평가 방법론 설명
   - 거래사례 비교 (details 사용)
   - 가격 산출 근거
   - 신뢰 구간 및 제약 조건

#### **디자인 규칙**
- **컬러**: Primary (Deep Blue) + Gray만 사용
- **강조**: 없음 (중립성 유지)
- **표**: 거래사례 비교표 1개
- **그래프**: 선택 사항 (가격 추이)

#### **금지 사항**
- ❌ `₩0` 표시
- ❌ Raw 거래가 나열 (해석 없이)
- ❌ 표만 있고 해석 없음
- ❌ "확정 가격"이라는 표현

---

### 2.2 M3: LH 선호유형 분석 보고서

#### **문서 톤 & 목적**
- **선호도 분석 리포트**
- 점수는 **보조 수단**
- 유형 추천은 **서술형 결론**

#### **필수 출력 항목**
1. **표지 요약**:
   - 추천 유형 (summary.recommended_type)
   - 종합 점수 (summary.total_score / 100)
   - 신뢰도 (summary.confidence_pct)
   - 차선책 유형 (summary.second_choice, Optional)

2. **본문 구조**:
   - Executive Summary (추천 근거 1문단)
   - 입지 분석 (대중교통, 학교, 상권)
   - LH 7대 유형 점수 비교
   - 최종 추천 근거 (2-3 문단)

#### **디자인 규칙**
- **컬러**: Primary + Accent (Cyan) 사용 가능
- **아이콘**: 유형별 아이콘 사용 가능
- **표**: 유형 비교표 1개
- **그래프**: 레이더 차트 (7개 유형 점수)

#### **금지 사항**
- ❌ `0점` 표시
- ❌ 점수만 나열 (해석 없이)
- ❌ "최적 유형"이라는 단정적 표현 (→ "추천 유형" 사용)

---

### 2.3 M4: 건축규모 결정 보고서 (⚠️ CRITICAL)

#### **문서 톤 & 목적**
- **엔지니어 보고서 + 행정 문서 중간 톤**
- 계산 과정 ❌ / 결과 요약 ✅
- M5 사업성 분석의 **입력 시나리오** 제공

#### **필수 출력 항목**
1. **표지 요약**:
   - 법정 세대수 (summary.legal_units)
   - 인센티브 세대수 (summary.incentive_units)
   - Alt A 주차대수 (summary.parking_alt_a)
   - Alt B 주차대수 (summary.parking_alt_b)

2. **본문 구조**:
   - Executive Summary (M4의 역할 설명)
   - 법정 FAR/BCR 기준
   - 인센티브 용적률 분석
   - 주차 제약 조건 (핵심!)
   - Alternative 비교 (Alt A vs Alt B)
   - M5 연계 시나리오 요약

#### **FAR/BCR 표기 규칙** (CRITICAL)
```
IF far_max is None:
  → "N/A (대지면적 미확정)" + 사유 문장
ELIF far_max == 0:
  → "0% (용도지역 제한)" + 설명
ELSE:
  → "250%" (실제 값)
```

#### **디자인 규칙**
- **컬러**: Primary + Warning (Amber, 제약 조건)
- **표**: 2~3개 (법정/인센티브 비교, Alt A/B 비교)
- **강조**: Warning 컬러로 제약 조건 박스 강조

#### **금지 사항**
- ❌ `0%` 표시 (사유 없이)
- ❌ 계산 과정 상세 나열
- ❌ "최종 결정"이라는 표현 (→ M4는 시나리오 제공)

---

### 2.4 M5: 사업성 분석 보고서

#### **문서 톤 & 목적**
- **투자 검토 자료**
- ROI/IRR은 **Summary 값만 사용**
- 계산 근거는 서술형으로

#### **필수 출력 항목**
1. **표지 요약**:
   - NPV (Public) (summary.npv_public_krw)
   - IRR (summary.irr_pct)
   - ROI (summary.roi_pct)
   - 사업성 등급 (summary.grade)

2. **본문 구조**:
   - Executive Summary (사업성 종합 판단)
   - 비용 구조 (토지비, 건축비, 부대비)
   - 수익 구조 (LH 매입가, 임대수익)
   - 재무 지표 해석 (NPV/IRR/ROI)
   - M4 시나리오별 사업성 비교
   - M6 연계 (사업성 우수 → M6 판정 중요)

#### **디자인 규칙**
- **컬러**: Primary + 숫자 강조 (Accent, 1곳만)
- **표**: 2~3개 (비용/수익 구조, 시나리오 비교)
- **그래프**: 1~2개 (NPV 추이, IRR 민감도 선택)

#### **금지 사항**
- ❌ `₩0 NPV` 표시 (사유 없이)
- ❌ 과도한 금융 디테일 (DCF 단계별 계산 등)
- ❌ "투자 추천"이라는 단정적 표현 (→ "사업성 우수" 사용)

---

### 2.5 M6: LH 심사예측 종합 판단 보고서 (FINAL)

#### **문서 톤 & 목적**
- **판결문 / 투자 의견서**
- 점수는 참고, **문장형 결론 필수**
- GO / CONDITIONAL GO / NO-GO 명확히

#### **필수 출력 항목**
1. **표지 요약**:
   - 최종 결정 (summary.decision: GO/CONDITIONAL/NO-GO)
   - 종합 점수 (summary.total_score / 110)
   - 심사 등급 (summary.grade: A/B/C/D)
   - 예상 승인율 (summary.approval_probability_pct)

2. **본문 구조**:
   - Executive Summary (최종 판단 1문단)
   - Hard Fail 항목 체크 (5개 필수 기준)
   - 정량 점수 (110점 체계, 4개 카테고리)
   - M5 사업성 결합 분석
   - 조건부 시나리오 (CONDITIONAL 시)
   - **최종 판단 페이지** (마지막 페이지 고정)

#### **점수 표기 규칙** (CRITICAL - SSoT)
```python
# 모든 섹션에서 동일 변수 사용
m6_score = summary.get('total_score')  # 단일 소스

# 표지 요약
f"{m6_score:.1f}/110점"

# 본문 판정
f"종합 점수 {m6_score}점으로..."

# 레이더 차트
radar_chart_data['total'] = m6_score
```

#### **디자인 규칙**
- **컬러**: Primary + Error (Red, Hard Fail만)
- **최소주의**: 가장 심플한 디자인
- **강조**: 최종 판단 문장만 Bold + 박스
- **표**: 2개 (Hard Fail 체크, 점수 분석)

#### **최종 판단 문장 템플릿**
```
IF decision == "GO":
  "본 사업은 LH 승인 가능성이 높으며, 즉시 추진을 권장합니다."

ELIF decision == "CONDITIONAL":
  "본 사업은 조건부 승인 가능 단계입니다. [조건 명시] 개선 후 추진하십시오."

ELIF decision == "NO-GO":
  "본 사업은 현 상태에서 LH 승인이 어렵습니다. 재설계를 권장합니다."
```

#### **금지 사항**
- ❌ 점수 불일치 (0.0 / 110 vs 85.0 / 110)
- ❌ "승인 확정"이라는 표현 (→ "승인 가능성 높음" 사용)
- ❌ 최종 판단 없이 점수만 나열

---

## 3. HTML 미리보기 기능 규격

### 3.1 목적

**PDF 다운로드 전** 사용자가 결과물을 확인할 수 있도록 **HTML 렌더링** 제공:
- 데이터 불일치 사전 차단
- QA Phase 3 (육안 검증) 대응
- 디자이너/기획자/고객 검증 가능

### 3.2 구현 요구사항

#### **버튼 배치**
각 모듈 카드(M2~M6)에 다음 버튼 추가:
```
📄 PDF 다운로드
📋 HTML 미리보기
```

#### **HTML 렌더링 규칙**
- PDF와 **동일한 `summary` 데이터** 사용
- PDF 레이아웃을 HTML/CSS로 **1:1 재현**
- 폰트/컬러/표 스타일 동일
- 페이지 구분은 `<div class="page">` 사용

#### **HTML 템플릿 구조**
```html
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>M4 건축규모 결정 보고서 - HTML Preview</title>
  <style>
    /* ZeroSite Theme CSS */
    body { font-family: 'Nanum Barun Gothic', sans-serif; }
    .page { width: 210mm; min-height: 297mm; padding: 25mm 22mm; }
    h1 { font-size: 22pt; color: #1E3A8A; }
    /* ... */
  </style>
</head>
<body>
  <div class="page">
    <h1>M4: 건축규모 결정 분석 보고서</h1>
    <table>
      <tr><td>법정 세대수</td><td>{{ summary.legal_units }}세대</td></tr>
      <!-- ... -->
    </table>
  </div>
  <footer>ⓒ ZEROSITE by Antenna Holdings | nataiheum</footer>
</body>
</html>
```

---

## 4. 최종 품질 검증 체크리스트

### 4.1 모든 PDF에 공통 적용

**자동 검증 항목**:
- [ ] `summary` 필드 사용 (details 직접 참조 없음)
- [ ] 0%, ₩0, 0점 표시 없음 (N/A로 대체)
- [ ] Footer에 Copyright 표기
- [ ] Watermark "ZEROSITE" 존재
- [ ] 폰트 일관성 (NanumBarunGothic)
- [ ] 컬러 팔레트 준수

**수동 검증 항목** (QA Phase 3):
- [ ] 문서 톤이 모듈 목적과 일치
- [ ] 표/그래프가 가독성 있음
- [ ] 해석 문장이 충분함 (숫자만 나열 X)

---

### 4.2 모듈별 핵심 체크

#### **M2 감정평가**
- [ ] 가격이 범위로 표시 (확정값 표현 X)
- [ ] 신뢰도 해석 포함

#### **M3 선호유형**
- [ ] 추천 근거 서술 (점수만 나열 X)
- [ ] 7개 유형 비교표 존재

#### **M4 건축규모** (CRITICAL)
- [ ] FAR/BCR이 N/A 또는 실제 값
- [ ] Alt A/B 비교 명확
- [ ] "M5 연계" 문구 포함

#### **M5 사업성**
- [ ] NPV/IRR/ROI가 summary 출처
- [ ] 시나리오별 비교 존재
- [ ] 재무 지표 해석 포함

#### **M6 종합 판단** (CRITICAL)
- [ ] 점수 불일치 없음 (SSoT 적용)
- [ ] GO/CONDITIONAL/NO-GO 명확
- [ ] 최종 판단 페이지 존재

---

### 4.3 HTML 미리보기 검증

- [ ] PDF와 데이터 100% 일치
- [ ] PDF와 레이아웃 거의 일치 (폰트/컬러)
- [ ] 버튼 클릭 시 즉시 표시 (로딩 3초 이내)

---

## 5. 출력 규격 준수 강제 방법

### 5.1 코드 레벨 강제

**PDF 생성 함수 템플릿**:
```python
def generate_m4_capacity_pdf(self, data: Dict[str, Any]) -> bytes:
    """M4 건축규모 PDF 생성
    
    ✅ MUST FOLLOW: PDF_OUTPUT_SPECIFICATION_20251219.md
    """
    # Step 1: Extract summary (SSoT)
    summary = data.get('summary', {})
    
    # Step 2: Validate required fields
    if summary.get('legal_units') is None:
        logger.warning("legal_units is None → will display N/A")
    
    # Step 3: Generate PDF with theme
    doc = self._create_document(buffer)  # Uses ZeroSiteTheme
    
    # Step 4: Add content (summary only for cover)
    legal_units = summary.get('legal_units')
    units_display = f"{legal_units}세대" if legal_units else "N/A (검증 필요)"
    
    # Step 5: Add footer and watermark
    doc.build(story, onFirstPage=self._add_watermark_and_footer, ...)
```

---

### 5.2 AI 프롬프트 레벨 강제

**모든 PDF 생성 수정 시 다음 프롬프트 참조 필수**:
```
당신은 ZeroSite M{N} PDF 생성 함수를 수정하고 있습니다.

반드시 다음 문서를 준수하십시오:
- PDF_OUTPUT_SPECIFICATION_20251219.md (출력 규격)
- FINAL_QA_VERIFICATION_REPORT_20251219.md (검증 기준)

특히 다음 규칙은 절대 위반 금지:
1. summary 필드만 사용 (details 직접 참조 X)
2. 0%, ₩0, 0점 표시 금지 (N/A로 대체)
3. ZeroSiteTheme 컬러/폰트 준수
4. Footer Copyright 필수
```

---

### 5.3 QA 자동화

**CI/CD Pipeline에 추가**:
```bash
# PDF 생성 테스트
pytest tests/test_pdf_output_spec.py

# 체크 항목:
# - summary 필드 사용 확인
# - "0%" 문자열 존재 여부
# - Footer "ⓒ ZEROSITE" 존재 확인
# - Watermark 존재 확인
```

---

## 6. 버전 관리 및 업데이트 정책

### 6.1 규격 변경 절차

본 문서(PDF_OUTPUT_SPECIFICATION)를 수정할 때:
1. 버전 번호 업데이트 (v4.0 → v4.1)
2. 변경 이유 및 영향 범위 명시
3. 모든 모듈 PDF 재생성 및 검증 필요

### 6.2 하위 호환성

- **v4.0**: 현재 규격 (2025-12-19)
- **이전 버전**: Deprecated (summary 필드 없음)

---

## 7. 참고 자료

**관련 문서**:
- `FINAL_QA_VERIFICATION_REPORT_20251219.md` - 품질 검증 보고서
- `app/services/pdf_generators/report_theme.py` - ZeroSite Theme 구현
- `app/core/canonical_data_contract.py` - Summary/Details 데이터 계약

**Git Repository**:
- https://github.com/hellodesignthinking-png/LHproject
- Pull Request #11

---

## 8. 결론

본 규격서는 ZeroSite M2-M6 PDF 출력물의 **품질 기준선**입니다.

**준수 의무**:
- ✅ 모든 PDF 생성 코드는 본 규격 참조 필수
- ✅ AI 코드 생성 시 프롬프트에 본 문서 포함 필수
- ✅ QA 검증 시 4.1~4.3 체크리스트 사용 필수

**비준수 시 결과**:
- 데이터 불일치 재발
- 사용자 신뢰도 저하
- LH 제출 문서 반려 가능성

본 규격서를 **변경 불가능한 기준**으로 삼아, ZeroSite 출력물의 일관성과 신뢰성을 보장합니다.

---

**Document Status**: 🟢 **APPROVED & ENFORCED**  
**Last Updated**: 2025-12-19  
**Next Review**: 실사용 환경 배포 후 1개월

ⓒ **ZEROSITE by Antenna Holdings | nataiheum**
