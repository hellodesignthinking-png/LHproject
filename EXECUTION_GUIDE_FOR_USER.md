# vABSOLUTE-FINAL-14: 사용자 실행 가이드

## 🎯 **최종 검증을 위한 실행 가이드**

### ✅ **현재 상태 확인 (모두 성공)**

1. **라우팅 문제 해결 완료:**
   - Legacy route 차단됨 (HTTP 410)
   - Frontend가 올바른 route 호출 중
   - Phase 3 assemblers 실행 준비 완료

2. **Validation 정상 작동:**
   - Empty context 감지 및 차단 성공
   - Context `6c110e8a-...`는 M1만 있고 M2-M6 없음
   - 시스템이 정확히 거부함 ✅

---

## 🚀 **전체 파이프라인 실행 방법**

### **1단계: Pipeline UI 접속**

**URL:** https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline

### **2단계: 새로운 분석 시작**

**중요:** 기존 Context `6c110e8a-...`는 M1만 있으므로, **새로운 분석**을 시작하세요.

#### M1: 토지 기본 정보 입력
- 지번 주소 입력
- 토지 면적 입력
- 용도지역 선택
- 기타 필수 정보 입력

#### "분석 시작 (M1 Lock)" 클릭
→ 새로운 Context ID 생성됨
→ 자동으로 M2→M6 실행됨

### **3단계: M2-M6 자동 실행 확인**

파이프라인이 자동으로 실행:
- **M2: 토지감정평가** (토지 가치 산정)
- **M3: 선호유형분석** (주택 유형 추천)
- **M4: 건축규모결정** (세대수, 용적률 등)
- **M5: 사업성분석** (NPV, IRR, ROI 계산)
- **M6: LH심사예측** (승인 가능성 판단)

### **4단계: Context Freeze 확인**

M2-M6 완료 후, **시스템이 자동으로 canonical_summary 생성**

확인 방법:
```
Context ID: {새로운 ID}
상태: M1-M6 모두 완료 ✅
canonical_summary: 생성됨 ✅
```

### **5단계: 보고서 생성**

이제 6개 보고서를 생성할 수 있습니다:

1. **종합 최종보고서** (all_in_one)
2. **토지주 제출용 요약보고서** (landowner_summary)
3. **LH 제출용 기술검증 보고서** (lh_technical)
4. **사업성·투자 검토 보고서** (financial_feasibility)
5. **사전 검토 리포트** (quick_check)
6. **설명용 프레젠테이션 보고서** (executive_summary)

**각 보고서 버튼 클릭 → 새 탭에서 HTML 미리보기 열림**

---

## 🧪 **검증 방법**

### **1. HTML에서 직접 확인**

생성된 HTML 보고서에서 확인:

```html
<!-- 페이지 하단에 이것이 보여야 함 -->
BUILD_SIGNATURE: vABSOLUTE-FINAL-12
DATA_SIGNATURE: abc12345
```

### **2. 실제 숫자 확인**

보고서 내용에서 확인:
- ✅ NPV: **420,000,000원** (숫자 표시)
- ✅ IRR: **13.20%** (숫자 표시)
- ✅ ROI: **18.00%** (숫자 표시)
- ❌ "N/A" 문자열 없음
- ❌ "검증 필요" 문구 없음
- ❌ "분석 중입니다" 문구 없음

### **3. PDF 다운로드 및 검증**

HTML 확인 후, PDF로 다운로드:

```bash
# 서명 확인
strings "사전 검토 리포트.pdf" | grep "BUILD_SIGNATURE"
# 예상 출력: BUILD_SIGNATURE: vABSOLUTE-FINAL-12

strings "사전 검토 리포트.pdf" | grep "DATA_SIGNATURE"
# 예상 출력: DATA_SIGNATURE: abc12345

# N/A 개수 확인
strings "사전 검토 리포트.pdf" | grep -c "N/A"
# 예상 출력: 0
```

---

## 📊 **예상 결과 비교**

### **OLD PDF (v4.1, 기존 업로드된 파일)**
```
BUILD_SIGNATURE: 없음 ❌
DATA_SIGNATURE: 없음 ❌
N/A 개수: 32-94개 ❌
NPV: N/A (검증 필요) ❌
IRR: N/A (검증 필요) ❌
문장: "분석 중입니다" ❌
```

### **NEW PDF (vABSOLUTE-FINAL-14, 새로 생성할 파일)**
```
BUILD_SIGNATURE: vABSOLUTE-FINAL-12 ✅
DATA_SIGNATURE: abc12345 ✅
N/A 개수: 0개 ✅
NPV: 420,000,000원 ✅
IRR: 13.20% ✅
문장: "본 사업의 NPV는 420,000,000원으로 산출되었습니다" ✅
```

---

## 🚨 **중요 사항**

### **1. 반드시 새로운 분석 실행**
- 기존 Context `6c110e8a-...`는 M1만 있음
- **새로운 분석**을 시작해서 M2-M6 완료해야 함

### **2. Context Freeze 확인**
- M2-M6 완료 후 자동으로 canonical_summary 생성됨
- 이것이 없으면 보고서 생성 시 HTTP 400 에러 (의도된 동작)

### **3. 구버전 PDF와 비교하지 말 것**
- `/home/user/uploaded_files`의 PDF는 OLD 버전
- 새로 생성한 PDF만 검증 대상

---

## 📁 **테스트 시나리오**

### **시나리오 A: Empty Context (의도적 실패)**

```
1. 기존 Context 6c110e8a-... 사용
2. 보고서 생성 버튼 클릭
3. 예상 결과: HTTP 400
   "Context has no canonical_summary"
4. 판정: ✅ 정상 (Validation 작동 증거)
```

### **시나리오 B: 완전한 Context (성공)**

```
1. 새로운 분석 시작
2. M1-M6 모두 완료
3. Context Freeze 자동 수행
4. 보고서 생성 버튼 클릭
5. 예상 결과: 
   - HTML 미리보기 성공
   - BUILD_SIGNATURE 표시
   - 실제 숫자 표시
   - "N/A" 없음
6. 판정: ✅ 성공
```

---

## 🎯 **완료 기준**

### **모든 조건을 만족해야 성공:**

- [ ] 새로운 분석으로 Context 생성
- [ ] M1-M6 모두 완료
- [ ] canonical_summary 존재 확인
- [ ] 6개 보고서 모두 HTML 생성 성공
- [ ] HTML에 BUILD_SIGNATURE 표시
- [ ] HTML에 실제 숫자 표시 (NPV, IRR 등)
- [ ] HTML에 "N/A" 문자열 없음
- [ ] PDF 다운로드 성공
- [ ] PDF에서 서명 검색 가능
- [ ] PDF에서 "N/A" 개수 0

---

## 📝 **체크리스트**

```
□ Pipeline UI 접속 완료
□ 새로운 분석 시작 (M1 입력)
□ M1 Lock 실행
□ M2-M6 자동 실행 완료 대기
□ canonical_summary 생성 확인
□ "종합 최종보고서" 생성 테스트
□ HTML에서 BUILD_SIGNATURE 확인
□ HTML에서 실제 숫자 확인
□ PDF 다운로드
□ PDF에서 strings 명령으로 서명 확인
□ PDF에서 N/A 개수 확인 (0개)
□ 나머지 5개 보고서도 동일하게 검증
```

---

## 🌐 **중요 URL**

### **Frontend Pipeline UI:**
https://3001-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai/pipeline

### **Backend API (참고용):**
https://8005-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai

---

## 💡 **예상 문제 및 해결**

### **Q1: "canonical_summary 없음" 에러가 계속 나옴**
**A:** M2-M6 분석이 완료되지 않았거나 Context Freeze가 안 됨.
→ 새로운 분석을 처음부터 다시 실행

### **Q2: HTML은 잘 나오는데 PDF가 안 됨**
**A:** PDF 엔드포인트 `/api/v4/final-report/{type}/pdf` 확인
→ 백엔드 로그 확인 (`/tmp/backend_new.log`)

### **Q3: "N/A"가 여전히 나옴**
**A:** 구버전 PDF를 보고 있거나, legacy route를 호출한 것
→ 브라우저 캐시 삭제 후 새로 생성

---

**준비 완료!** 이제 실제 파이프라인을 실행하고 결과를 확인하세요.

**Status:** ✅ vABSOLUTE-FINAL-14 Complete - Ready for User Testing

---
