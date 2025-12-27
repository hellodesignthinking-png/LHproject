# 🏢 ZeroSite 4.0 외부 제출용 버전 규칙

**Version**: 1.0  
**Date**: 2025-12-27  
**Target**: LH/지자체/토지주

---

## 🎯 외부 제출 시 핵심 원칙

### 1️⃣ 절대 불변 원칙

**❌ 외부 제출 버전에서 절대 금지:**
- M6 판단 로직 노출
- 점수 계산 알고리즘 공개
- 내부 가중치/임계값 공개
- 소스 코드 제공
- 데이터베이스 스키마 노출

**✅ 외부 제출 버전에 포함 가능:**
- 최종 보고서 (6종 중 선택)
- M6 판단 결과 (점수, 등급, 판정)
- 개선 포인트 목록
- 근거 데이터 (M1~M5 요약)

---

## 📊 2️⃣ 대상별 제출 규칙

### 🏛️ LH 공사 제출용

**제출 대상 보고서:**
- ✅ LH 기술검토 보고서 (`LHTechnicalReport`)
- ✅ 사업타당성 보고서 (`FinancialFeasibilityReport`)

**포함 내용:**
```python
{
    "report_type": "lh_technical",
    "m6_scorecard": {
        "total_score": 75.0,  # ✅ 포함
        "grade": "B",         # ✅ 포함
        "judgement": "CONDITIONAL",  # ✅ 포함
        "section_breakdown": {  # ✅ 포함
            "policy": 15,
            "location": 18,
            "construction": 12,
            "price": 10,
            "business": 10
        }
    },
    "deduction_reasons": [  # ✅ 포함
        "주차 효율 부족 -4점",
        "인근 공급 과잉 -3점"
    ],
    "improvement_points": [  # ✅ 포함
        "+6점: 주차 확보",
        "+4점: 차별화 전략"
    ],
    "technical_recommendation": "본 사업지는 ZeroSite v4.0 M6 기준에 따라 보완 조건 충족 시 LH 매입이 가능한 사업지로 판단된다."
}
```

**❌ 제외 내용:**
- 점수 계산 로직 (score_calculator.py)
- 가중치 테이블
- M6 판단 알고리즘
- 내부 데이터 검증 로직

**제출 포맷:**
- PDF (공식 제출용)
- Excel (데이터 제공용)

---

### 🏙️ 지자체 제출용

**제출 대상 보고서:**
- ✅ 종합 보고서 (`AllInOneReport`)
- ✅ LH 기술검토 보고서 (`LHTechnicalReport`)

**포함 내용:**
- M6 판단 결과 (점수, 등급, 판정)
- 입지 분석 (M1 요약)
- 주택 유형 분석 (M3 요약)
- 개선 포인트
- 정책 적합성 (M6 Section A)

**❌ 제외 내용:**
- 토지 평가액 (M2 상세)
- 재무 수익성 (M5 상세)
- 내부 알고리즘
- 협상 전략

**제출 포맷:**
- PDF (공식 제출용)
- PPT (프레젠테이션용)

---

### 🏡 토지주 제출용

**제출 대상 보고서:**
- ✅ 토지주 요약 보고서 (`LandownerSummaryReport`)
- ✅ 간편 체크 보고서 (`QuickCheckReport`)

**포함 내용:**
```python
{
    "report_type": "landowner_summary",
    "judgement": "CONDITIONAL",  # ✅ 포함 (한글 표현)
    "simple_message": "본 사업지는 ZeroSite v4.0 M6 기준에 따라 보완 조건 충족 시 LH 매입이 가능한 사업지로 판단된다.",
    "key_points": {
        "현재 점수": "75점/100점",
        "등급": "B",
        "개선 가능 항목": 2
    },
    "what_to_do_next": [  # Top 3만
        "+6점: 주차 확보",
        "+4점: 차별화 전략"
    ],
    "final_conclusion": "본 사업지는 ZeroSite v4.0 M6 기준에 따라 보완 조건 충족 시 LH 매입이 가능한 사업지로 판단된다."
}
```

**❌ 제외 내용:**
- 상세 점수 계산
- 내부 알고리즘
- 다른 사업지 비교
- LH 내부 기준

**제출 포맷:**
- PDF (1-2페이지 요약)
- 모바일 친화적 HTML

---

## 🔒 3️⃣ 데이터 보호 규칙

### 개인정보 보호

**제거 필수:**
- 토지주 개인 정보
- 연락처
- 주민등록번호
- 계좌 정보

**익명화 처리:**
- 주소: "서울특별시 강남구 테헤란로 123" → "서울특별시 강남구 ○○동 ○○번지"
- 면적만 표시, 지번 제거
- 평가액: 구간으로 표시 (예: "50~70억원")

---

### 영업 기밀 보호

**제거 필수:**
- ZeroSite 내부 알고리즘
- 점수 계산 가중치
- M6 판단 로직
- 데이터베이스 구조
- API 엔드포인트

**워터마크 추가:**
```
본 보고서는 ZeroSite v4.0 시스템에서 생성되었으며,
M6 Single Source of Truth 원칙에 따라 작성되었습니다.

보고서 ID: [UUID]
생성 일시: [Timestamp]
유효 기간: 생성일로부터 3개월

본 보고서의 무단 복제 및 배포를 금지합니다.
```

---

## 📤 4️⃣ 제출 절차

### Step 1: 보고서 생성

```python
from app.services.m6_centered_report_base import create_m6_centered_report
from app.services.external_report_generator import ExternalReportGenerator

# 내부용 보고서 생성
internal_report = create_m6_centered_report('all_in_one', m6_result, m1_m5_data)

# 외부용 보고서 생성 (민감 정보 제거)
external_report = ExternalReportGenerator.sanitize_for_external(
    internal_report,
    target='LH',  # 'LH' / 'GOVT' / 'LANDOWNER'
    include_detailed_scores=False,  # 상세 점수 제외
    anonymize_address=True  # 주소 익명화
)
```

---

### Step 2: 검증

```python
# 외부 제출용 보고서 검증
validator = ExternalReportValidator()

# 민감 정보 누락 검증
assert validator.no_internal_logic(external_report)
assert validator.no_personal_info(external_report)
assert validator.no_trade_secrets(external_report)

# M6 일관성 검증
assert validator.m6_consistency(external_report)
```

---

### Step 3: 포맷 변환

```python
# PDF 생성
from app.services.pdf_export_external import ExternalPDFExporter

pdf_path = ExternalPDFExporter.generate(
    report=external_report,
    template='lh_official',  # 'lh_official' / 'govt_standard' / 'landowner_simple'
    watermark=True,
    confidential_level='PUBLIC'  # 'PUBLIC' / 'INTERNAL' / 'CONFIDENTIAL'
)
```

---

### Step 4: 제출

```bash
# 1. 보고서 검증
python scripts/validate_external_report.py --report-id [UUID]

# 2. PDF 생성
python scripts/generate_external_pdf.py --report-id [UUID] --target LH

# 3. 제출 패키지 생성
python scripts/create_submission_package.py --report-id [UUID]

# 출력: submission_package_[UUID].zip
# 포함: 
#   - report.pdf (공식 보고서)
#   - summary.xlsx (데이터 요약)
#   - metadata.json (메타데이터)
#   - README.txt (사용 안내)
```

---

## 🚨 5️⃣ 긴급 대응 절차

### 민감 정보 유출 시

**즉시 조치:**
1. 제출된 보고서 회수 요청
2. 해당 보고서 ID 블랙리스트 등록
3. 유출 경로 파악
4. 시스템 로그 분석
5. 보안 패치 적용

```python
# 긴급 회수 스크립트
python scripts/emergency_recall.py --report-id [UUID] --reason "sensitive_data_leak"
```

---

### 판단 오류 발견 시

**조치 절차:**
1. M6 판단 재검증
2. Kill-Switch 실행
3. E2E 테스트 재실행
4. 영향받은 보고서 목록 확인
5. 정정 보고서 발행

```python
# 판단 재검증
python scripts/revalidate_judgement.py --report-id [UUID]

# 정정 보고서 발행
python scripts/issue_correction.py --original-id [UUID] --reason "m6_revalidation"
```

---

## 📋 6️⃣ 외부 제출 체크리스트

### 제출 전 필수 확인

- [ ] **민감 정보 제거**
  - [ ] 내부 알고리즘 미포함
  - [ ] 개인 정보 익명화
  - [ ] 영업 기밀 미포함

- [ ] **M6 일관성 검증**
  - [ ] Kill-Switch PASSED
  - [ ] E2E Tests PASSED
  - [ ] 6종 보고서 일관성 확인

- [ ] **포맷 검증**
  - [ ] PDF 생성 정상
  - [ ] 워터마크 포함
  - [ ] 메타데이터 정확

- [ ] **대상별 커스터마이징**
  - [ ] LH: LHTechnicalReport 포함
  - [ ] 지자체: AllInOneReport 포함
  - [ ] 토지주: LandownerSummaryReport 포함

---

## 🎯 Phase 3.5B 완료 기준

### 외부 제출 준비 완료

- [x] 외부 제출 규칙 문서화: ✅
- [ ] ExternalReportGenerator 구현: ⏳ TODO
- [ ] ExternalReportValidator 구현: ⏳ TODO
- [ ] ExternalPDFExporter 구현: ⏳ TODO
- [ ] 제출 패키지 생성 스크립트: ⏳ TODO

---

**외부 제출 규칙 버전**: 1.0  
**최종 업데이트**: 2025-12-27  
**승인**: ZeroSite 4.0 Team
