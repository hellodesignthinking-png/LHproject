# 다음 세션 실행 프롬프트

당신은 이제 **시스템을 고치는 개발자**가 아니다.
**LH·금융기관·토지주에게 실제로 제출되는 '50페이지 종합보고서(all_in_one)'를 구현하는 보고서 집필자 + 구현자**다.

⚠️ 절대 수정 금지 사항:
* 서버 / API / 계산 로직 / canonical_summary 구조
* resolve_scalar, unified CSS, present 함수
* QA / Runtime / Signature 로직

👉 **이번 세션의 작업 범위는 오직 `all_in_one.py`의 콘텐츠 구현이다.**

---

## 🎯 이번 세션의 단일 목표

> **전체 통합 보고서(all_in_one)를
> 실제 PDF 기준 50페이지로 완성한다.**

* 다른 5종 보고서 ❌ (절대 건드리지 말 것)
* 코드 안정화 ❌
* 기능 개선 ❌
* 콘텐츠 구현 ⭕️

---

## 0️⃣ 반드시 참고해야 할 파일 (세션 시작 시 먼저 읽기)

1. `CURRENT_STATUS_AND_NEXT_STEPS.md`
2. `canonical_summary_structure.txt`
3. `canonical_summary_raw.json`
4. 이전 대화에서 작성된 **④ M4 / ⑤ M6 / ⑥ LH 톤 문안**

❌ 구조를 추측해서 쓰지 말 것
❌ canonical_summary에 없는 데이터 서술 금지

---

## 1️⃣ 구현 방식 (절대 준수)

❌ 한 번에 50페이지 구현 금지
✅ **섹션 단위로 순차 구현 + 검증**

다음 순서로만 진행한다:

1. Executive Summary (3p)
2. M2 토지 가치 분석 (6p)
3. M4 건축·법정 검토 (6p)
4. M5 사업성 분석 (10p)
5. M6 LH 심사 판단 (6p)
6. 이해관계자 분석 (6p)
7. 리스크 종합 (5p)
8. 결론 & Next Steps (4p)

👉 **각 섹션 구현 후 PDF 미리보기로 페이지 수 확인**

---

## 2️⃣ 콘텐츠 구현 규칙 (가장 중요)

모든 숫자 KPI에는 반드시 아래 3가지를 포함한다:

1. **수치의 의미**
2. **LH 내부 기준에서의 해석**
3. **리스크 또는 보완 가능성**

❌ 표만 있고 문장 없는 페이지 금지
❌ bullet-only 페이지 금지
❌ "일반적으로 / 보통 / 통상" 같은 추상 표현 금지

---

## 3️⃣ 문체 규칙 (LH 톤 고정)

* 판단형 문장 사용
* 감정/마케팅 표현 금지
* 기준·조건·전제 명시

예시:

> ❌ "사업성이 좋다"
> ✅ "공공 기준 적용 시 재무적 결격 사유는 확인되지 않았다"

---

## 4️⃣ all_in_one.py 구현 원칙

* HTML 구조는 기존 패턴 유지
* `<h2>` = 페이지 시작
* `<h3>` = 소주제
* `<p class="analysis">` = 해석 문단

❌ inline style 금지
❌ CSS 수정 금지

---

## 5️⃣ 완료 판정 기준 (이 세션의 Definition of Done)

다음이 모두 충족되면 성공이다:

1. all_in_one 단독 PDF 50페이지 이상
2. 모든 핵심 KPI에 해석 문단 존재
3. LH 실무자가 질문 없이 이해 가능
4. "보고서 같다"는 외관·톤 확보
5. 다른 보고서와 무관하게 독립 완결

---

## 🔚 출력 규칙

이 세션이 끝나면 **정확히 이 문장만 출력한다**

```
ALL_IN_ONE REPORT COMPLETE
50-page external submission ready
Foundation successfully extended to full content
```

실패 시

```
FAILED
Reason: (section / page / missing interpretation)
```

---

## 📋 참고: 제공된 실제 문안 위치

이전 대화에서 다음 섹션의 실제 문안이 제공되었음:

1. **Executive Summary (3p)** - Page 1-3
2. **M2 토지 가치 분석 (6p)** - Page 4-9
3. **M5 사업성 분석 (10p)** - Page 10-18
4. **M4 건축·법정 검토 (6p)** - Page 19-24
5. **M6 LH 심사 관점 (6p)** - Page 25-30
6. **LH 톤 수정 원칙** - ⑥ 섹션

이 문안들을 `all_in_one.py`에 구현하되, canonical_summary의 실제 데이터와 연결하여 동적으로 생성되도록 코드로 작성할 것.

---

## ⚡ 빠른 시작 체크리스트

다음 세션 시작 시:

- [ ] `CURRENT_STATUS_AND_NEXT_STEPS.md` 읽기
- [ ] `canonical_summary_structure.txt` 확인
- [ ] 이전 대화의 실제 문안(④⑤⑥) 복사
- [ ] `all_in_one.py` 파일 열기
- [ ] Executive Summary부터 순차 구현 시작

**목표:** 50페이지 외부 제출 가능 보고서 완성
**방법:** 순차적 섹션 구현 + 검증
**금지:** 다른 파일 수정, 시스템 변경
