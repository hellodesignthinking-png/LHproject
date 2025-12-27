# 🎯 ZeroSite 4.0 보고서 시스템 전환 가이드

## 📋 현재 상태

### ✅ 완료된 작업 (Phase 1)

1. **M6 Single Source of Truth 시스템 구축**
   - 파일: `app/services/m6_centered_report_base.py`
   - 클래스: `M6SingleSourceOfTruth`
   - 기능: 모든 보고서의 유일한 판단 근거

2. **6종 보고서 베이스 클래스 생성**
   - `AllInOneReport` - 종합 보고서
   - `LandownerSummaryReport` - 토지주 요약
   - `LHTechnicalReport` - LH 기술검토
   - `FinancialFeasibilityReport` - 사업타당성
   - `QuickCheckReport` - 간편 체크
   - `PresentationReport` - 프레젠테이션

3. **일관성 검증 시스템**
   - `validate_consistency()` - 자동 검증
   - 점수/판단/등급 일치 확인

4. **결론 문장 통일**
   - GO/CONDITIONAL/NOGO 강제 템플릿
   - 모든 보고서 동일 문장 사용

---

## 🔄 다음 단계 (Phase 2): 기존 시스템 통합

### 작업 목록

#### 1. `pdf_download_standardized.py` 수정

**현재 문제:**
```python
# 기존: 각 보고서가 독립적으로 생성
assembled_data = assemble_final_report(...)
html = render_final_report_html(...)
```

**수정 방향:**
```python
from app.services.m6_centered_report_base import create_m6_centered_report

# M6 결과 가져오기
m6_result = get_m6_result_from_context(context_id)

# M6 중심 보고서 생성
report_data = create_m6_centered_report(
    report_type=report_type,
    m6_result=m6_result,
    m1_m5_data=m1_m5_data
)

# HTML 렌더링 (M6 중심)
html = render_m6_centered_html(report_data)
```

#### 2. `report_generator_v4.py` 수정

**현재 문제:**
- M7이 독립적으로 보고서 생성
- M6 결과를 단순 참조만 함

**수정 방향:**
```python
from app.services.m6_centered_report_base import M6SingleSourceOfTruth

class ReportGeneratorV4:
    def generate(self, ..., m6_result):
        # M6를 Single Source of Truth로 변환
        m6_truth = M6SingleSourceOfTruth(
            lh_total_score=m6_result.lh_score_total,
            judgement=m6_result.judgement,
            ...
        )
        
        # M6 진실을 기반으로 보고서 생성
        report = self._build_from_m6_truth(m6_truth)
        return report
```

#### 3. `final_report_assembler.py` 수정

**현재 문제:**
- 각 모듈 데이터를 독립적으로 조립
- M6 우선순위 명확하지 않음

**수정 방향:**
```python
def assemble_final_report(report_type, canonical_data, context_id):
    # Step 1: M6 결과 추출 (최우선)
    m6_result = extract_m6_from_canonical(canonical_data)
    
    # Step 2: M6를 Single Source of Truth로 변환
    m6_truth = convert_to_m6_truth(m6_result)
    
    # Step 3: M1~M5는 근거로만 사용
    m1_m5_evidence = extract_m1_m5_as_evidence(canonical_data)
    
    # Step 4: M6 중심 보고서 생성
    report = create_m6_centered_report(
        report_type=report_type,
        m6_result=m6_truth,
        m1_m5_data=m1_m5_evidence
    )
    
    return report
```

#### 4. `final_report_html_renderer.py` 수정

**현재 문제:**
- HTML 템플릿이 각 모듈 데이터를 독립적으로 표시
- M6 결론이 맨 마지막에만 나타남

**수정 방향:**
```html
<!-- Step 1: M6 결론 먼저 (Executive Summary) -->
<div class="m6-conclusion-first">
  <h2>M6 최종 판단</h2>
  <p>{{ m6_truth.judgement }}</p>
  <p>{{ m6_truth.final_conclusion }}</p>
</div>

<!-- Step 2: 감점 요인 (Why this judgement?) -->
<div class="m6-deductions">
  <h3>감점 요인</h3>
  <ul>
    {% for deduction in m6_truth.key_deductions %}
    <li>{{ deduction }}</li>
    {% endfor %}
  </ul>
</div>

<!-- Step 3: 개선 포인트 (How to improve?) -->
<div class="m6-improvements">
  <h3>개선 방안</h3>
  <ul>
    {% for improvement in m6_truth.improvement_points %}
    <li>{{ improvement }}</li>
    {% endfor %}
  </ul>
</div>

<!-- Step 4: M1~M5 근거 데이터 -->
<div class="evidence-data">
  <h3>근거 데이터 (M1~M5)</h3>
  <p style="color: #6B7280;">
    아래 데이터는 M6 판단의 근거로 사용되었습니다.
  </p>
  <!-- M1~M5 데이터 표시 -->
</div>

<!-- Step 5: M6 결론 재확인 (Final Conclusion) -->
<div class="m6-conclusion-final">
  <h2>최종 결론</h2>
  <p>{{ m6_truth.final_conclusion }}</p>
</div>
```

---

## 🔥 핵심 수정 원칙

### 1. M6 우선 표시
- 모든 보고서의 첫 번째 섹션 = M6 결론
- Executive Summary는 M6 점수/판단/등급

### 2. M1~M5는 근거만
- "M1~M5 근거 데이터" 섹션 명시
- "아래 데이터는 M6 판단의 근거로 사용되었습니다" 문구 추가

### 3. 결론 재확인
- 모든 보고서 마지막 = M6 결론 문장 재표시
- 색상 코드로 강조 (GO=Green, CONDITIONAL=Amber, NOGO=Red)

### 4. 일관성 검증
- 보고서 생성 직후 `validate_consistency()` 호출
- 검증 실패 시 에러 로그 + 재생성

---

## 📊 수정 우선순위

### High Priority (즉시)
1. `pdf_download_standardized.py` - 보고서 API 엔드포인트
2. `final_report_assembler.py` - 보고서 데이터 조립
3. `final_report_html_renderer.py` - HTML 템플릿

### Medium Priority (다음)
4. `report_generator_v4.py` - M7 보고서 생성기
5. 프론트엔드 연동 테스트

### Low Priority (추후)
6. PDF 템플릿 수정
7. 다국어 지원 (영문 보고서)

---

## 🧪 테스트 시나리오

### 시나리오 1: 기본 플로우
```python
# 1. M1 Context Freeze
context_id = freeze_m1_context(address, area, coordinates)

# 2. M2~M6 파이프라인 실행
pipeline_result = run_pipeline(context_id)

# 3. 6종 보고서 생성
for report_type in ["all_in_one", "landowner_summary", ...]:
    report_html = get_final_report_html(report_type, context_id)
    
    # 검증: 모든 보고서가 동일한 M6 결론 사용
    assert "CONDITIONAL" in report_html  # 예시
    assert "75.0/100" in report_html
```

### 시나리오 2: 일관성 검증
```python
# 6종 보고서 생성
reports = []
for report_type in REPORT_TYPES:
    report = create_m6_centered_report(report_type, m6_result, m1_m5_data)
    reports.append(report)

# 검증: 모든 보고서가 동일한 점수/판단/등급
scores = [r["total_score"] for r in reports]
assert len(set(scores)) == 1  # 모든 점수가 동일

judgements = [r["judgement"] for r in reports]
assert len(set(judgements)) == 1  # 모든 판단이 동일
```

### 시나리오 3: 결론 문장 통일
```python
# 모든 보고서의 결론 문장 추출
conclusions = []
for report_type in REPORT_TYPES:
    report_html = get_final_report_html(report_type, context_id)
    conclusion = extract_conclusion_sentence(report_html)
    conclusions.append(conclusion)

# 검증: 모든 결론 문장이 동일
assert len(set(conclusions)) == 1
```

---

## 📝 체크리스트

### Phase 1: 기반 시스템 (✅ 완료)
- [x] M6SingleSourceOfTruth 클래스 생성
- [x] M6CenteredReportBase 클래스 생성
- [x] 6종 보고서 클래스 생성
- [x] 일관성 검증 로직
- [x] 결론 문장 템플릿
- [x] 문서화
- [x] 커밋 & 푸시

### Phase 2: 통합 작업 (🔄 진행 중)
- [ ] `pdf_download_standardized.py` 수정
- [ ] `final_report_assembler.py` 수정
- [ ] `final_report_html_renderer.py` 수정
- [ ] `report_generator_v4.py` 수정
- [ ] HTML 템플릿 수정

### Phase 3: 검증 & 배포 (⏳ 대기)
- [ ] E2E 테스트 작성
- [ ] 6종 보고서 논리 검증
- [ ] 프론트엔드 연동 테스트
- [ ] 스테이징 배포
- [ ] 프로덕션 배포

---

## 🎓 핵심 메시지

> **"하나의 판단을 6가지 언어로 설명"**

- M6가 유일한 진실
- M1~M5는 M6의 근거
- 모든 보고서는 M6를 다른 방식으로 설명할 뿐
- 점수/판단/등급은 절대 불일치 금지

---

## 📞 문의 & 지원

- **작성자**: ZeroSite 4.0 Team
- **날짜**: 2025-12-27
- **버전**: Phase 1 완료
- **다음 업데이트**: Phase 2 통합 작업 완료 시

---

**✅ ZeroSite 4.0 보고서 시스템 전환 - Phase 1 완료**
