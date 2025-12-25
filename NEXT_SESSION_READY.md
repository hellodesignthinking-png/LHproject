# 🎉 **최종 준비 완료 - 다음 세션 실행 가이드**

**날짜:** 2025-12-25  
**상태:** ✅ **READY FOR NEXT SESSION**  
**목적:** 6종 보고서 최종 QA 및 LH 제출 품질 달성

---

## 📋 **준비 완료 현황**

### ✅ **작성된 문서 (4개)**

| 문서 | 크기 | 용도 |
|------|------|------|
| **FINAL_EXECUTION_PROMPT.md** | 4.7KB | 🔥 **메인 실행 프롬프트** |
| **FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md** | 9.8KB | 상세 가이드 (3가지 옵션) |
| **REPORT_FIX_PREPARATION_COMPLETE.md** | 5.8KB | 준비 완료 요약 |
| **NEXT_SESSION_READY.md** | (이 문서) | 실행 방법 안내 |

### ✅ **Git 커밋 완료**
- **Commit 1:** `3c8207c` - 실행 가이드 (3가지 옵션)
- **Commit 2:** `b37cd0a` - 준비 완료 요약
- **Commit 3:** `2033d07` - 최종 실행 프롬프트 ⭐
- **Branch:** `feature/expert-report-generator`
- **Status:** All pushed ✅

---

## 🎯 **다음 세션에서 할 일 (단 1가지)**

### **Option 1: 최종 통합 실행 (권장) 🔥**

```bash
# 1. 문서 읽기
Read: /home/user/webapp/FINAL_EXECUTION_PROMPT.md

# 2. 프롬프트 전체 복사

# 3. 다음 세션 첫 메시지로 붙여넣기

# 4. 자동 실행 대기
→ 디자인 통합
→ 데이터 바인딩 수정
→ 검증
→ 결과 출력

# 5. 커밋
git commit & push
```

**예상 소요 시간:** 30-45분  
**예상 결과:** LH 제출 품질 달성

---

### **Option 2: 단계별 실행 (보수적)**

```bash
# 1. 상세 가이드 읽기
Read: /home/user/webapp/FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md

# 2. 3가지 중 선택
[통합] - 디자인+데이터 한 번에
[①디자인만] - 레이아웃 먼저
[②데이터만] - 값 연동 먼저

# 3. 선택한 프롬프트 복사-붙여넣기

# 4. 실행 및 검증
```

**예상 소요 시간:** 20-30분 (각 단계)  
**예상 결과:** 단계별 품질 개선

---

## 📊 **실행 프롬프트 구조**

### **FINAL_EXECUTION_PROMPT.md** (메인) 🔥

```
구조:
├── 역할 정의 (QA 책임자)
├── 절대 금지 사항 (로직/내용 변경 ❌)
├── 최종 목표 (디자인+데이터+품질)
├── 1️⃣ 디자인 검증 & 수정
│   ├── 단일 CSS 강제
│   ├── 폰트 규격 (H1:22px~Body:14px)
│   └── inline style 제거
├── 2️⃣ 데이터 연동 검증
│   ├── 금지 패턴 (dict 직접 접근)
│   ├── 필수 패턴 (resolve_scalar + present)
│   └── 필수 값 목록 (토지감정가~LH판단)
├── 3️⃣ 6종 보고서 개별 체크
│   ├── 공통 체크 ({}, None, 내부키 ❌)
│   └── 보고서별 핵심 확인
├── 4️⃣ 최종 합격 기준
│   └── LH 기준 (결재선, 웹페이지, 이해성, 톤)
├── 5️⃣ 실행 단계
│   ├── Step 1: 현재 상태 파악
│   ├── Step 2: 디자인 통합
│   ├── Step 3: 데이터 바인딩
│   ├── Step 4: 검증
│   └── Step 5: 커밋
├── 출력 규칙 (성공/실패 메시지)
├── 육안 체크 10초 리스트
├── 수정 대상 파일 목록
└── 검증 명령어 (grep 커맨드)
```

---

## 🎯 **검증 기준 요약**

### **디자인 통일**
```
✅ 단일 CSS: unified_report_theme.css
✅ 폰트 규격: H1(22) → H2(18) → H3(15) → Body(14) → Table(13)
✅ line-height: 1.6
✅ inline style: 0건
✅ <style> 태그: 0건
```

### **데이터 연동**
```
✅ resolve_scalar 사용: 6개 이상
✅ present 함수 사용: 12개 이상
✅ "산출 중" 출현: 0건
✅ dict 직접 접근: 0건
✅ 필수 값 표시: 토지감정가, 세대수, NPV, IRR, LH판단
```

### **일관성**
```
✅ Data Signature = 본문 KPI = 카드 KPI
✅ 보고서 간 동일 수치 일치
✅ 6개 PDF 육안 구분 불가
```

---

## 🔍 **자동 검증 명령어**

### **디자인 검증**
```bash
# inline style 검색 (0이어야 함)
grep -r "style=" backend/reports/*.py | wc -l

# <style> 태그 검색 (0이어야 함)
grep -r "<style>" backend/reports/*.py | wc -l
```

### **데이터 검증**
```bash
# "산출 중" 검색 (0이어야 함)
grep -r "산출 중" backend/reports/*.py | wc -l

# dict 직접 접근 검색 (0이어야 함)
grep -r "\[\"" backend/reports/*.py | grep -v "canonical_summary" | wc -l
```

### **패턴 검증**
```bash
# resolve_scalar 사용 확인 (6개 이상)
grep -r "resolve_scalar" backend/reports/*.py | wc -l

# present 함수 사용 확인 (12개 이상)
grep -r "present_" backend/reports/*.py | wc -l
```

---

## 📁 **수정 대상 파일**

### **CSS (생성 또는 확인)**
```
/home/user/webapp/static/unified_report_theme.css
```

### **6종 보고서 (수정)**
```
1. backend/reports/quick_check.py
2. backend/reports/financial_feasibility.py
3. backend/reports/lh_technical.py
4. backend/reports/executive_summary.py
5. backend/reports/landowner_summary.py
6. backend/reports/all_in_one.py
```

### **유틸리티 (확인만)**
```
app/utils/report_value_resolver.py
app/utils/present.py
```

---

## 🎯 **예상 결과**

### **Before (현재 상태)**
```
❌ 6종 보고서 폰트/여백 제각각
❌ "산출 중" / None 노출
❌ Data Signature ≠ 본문 KPI
❌ dict 직접 접근
❌ 웹페이지처럼 보임
```

### **After (목표 상태)**
```
✅ 6개 PDF 완벽한 통일
✅ 모든 KPI 실제 값 표시
✅ Data Signature = 본문 = 카드
✅ resolve_scalar + present 패턴
✅ LH 제출 품질
```

---

## 🔚 **출력 메시지**

### **성공 시**
```
FINAL 6 REPORTS VERIFIED
Design unified, data bound correctly
Ready for LH submission
```

### **실패 시**
```
FAILED
Reason: (report_type / design_or_data_issue)
```

---

## 🚀 **실행 순서 (다음 세션)**

### **1단계: 준비**
```bash
# 작업 디렉토리 확인
cd /home/user/webapp
pwd

# 문서 읽기
cat FINAL_EXECUTION_PROMPT.md
```

### **2단계: 실행**
```
프롬프트 전체 복사
↓
다음 세션 첫 메시지로 붙여넣기
↓
시스템 자동 실행
```

### **3단계: 검증**
```bash
# 자동 검증 명령어 실행
grep -r "산출 중" backend/reports/*.py | wc -l
grep -r "resolve_scalar" backend/reports/*.py | wc -l
grep -r "present_" backend/reports/*.py | wc -l
```

### **4단계: 커밋**
```bash
git add .
git commit -m "fix: Unify 6 reports design and fix data binding"
git push origin feature/expert-report-generator
```

### **5단계: PR 업데이트**
```bash
gh pr edit 11 --body "Updated PR description with fix results"
```

---

## 📚 **참고 문서 위치**

### **실행 문서**
```
/home/user/webapp/FINAL_EXECUTION_PROMPT.md          (⭐ 메인)
/home/user/webapp/FIX_REPORTS_DESIGN_DATA_NEXT_SESSION.md
/home/user/webapp/REPORT_FIX_PREPARATION_COMPLETE.md
/home/user/webapp/NEXT_SESSION_READY.md              (이 문서)
```

### **기존 구현 문서**
```
/home/user/webapp/ALL_IN_ONE_IMPLEMENTATION_COMPLETE.md
/home/user/webapp/SESSION_COMPLETE_SUMMARY.md
/home/user/webapp/canonical_summary_structure.txt
/home/user/webapp/canonical_summary_raw.json
```

---

## 🔗 **Git 정보**

### **Branch & Commits**
```
Branch: feature/expert-report-generator
Latest: 2033d07 (Final execution prompt)
Previous: b37cd0a (Preparation complete)
Previous: 3c8207c (Fix guide with 3 options)
```

### **Pull Request**
```
PR #11: https://github.com/hellodesignthinking-png/LHproject/pull/11
Status: OPEN
Title: [PRODUCTION READY] ZeroSite v4.0 Expert Report System
```

---

## ✅ **준비 체크리스트**

### **문서 준비**
- [x] 최종 실행 프롬프트 작성
- [x] 상세 가이드 작성 (3가지 옵션)
- [x] 준비 완료 요약 작성
- [x] 실행 방법 안내 작성

### **코드 상태**
- [x] 6종 보고서 기본 구현 완료
- [x] all_in_one 50페이지 완성
- [x] canonical_summary 데이터 구조 정의
- [x] 유틸리티 함수 구현 (resolve_scalar, present)

### **Git 상태**
- [x] 모든 문서 커밋 완료
- [x] remote에 push 완료
- [x] PR 상태 확인 완료

### **다음 세션 준비**
- [x] 실행 프롬프트 준비 완료
- [x] 검증 명령어 준비 완료
- [x] 예상 결과 정의 완료
- [x] 성공/실패 기준 명확화 완료

---

## 🎉 **최종 상태**

### **✅ ALL READY FOR NEXT SESSION**

모든 준비가 완료되었습니다!

**다음 세션에서:**
1. `FINAL_EXECUTION_PROMPT.md` 읽기
2. 프롬프트 전체 복사
3. 첫 메시지로 붙여넣기
4. 자동 실행 대기
5. 결과 확인 및 커밋

**예상 소요 시간:** 30-45분  
**예상 결과:** 6종 보고서 LH 제출 품질 달성

---

## 🎯 **핵심 포인트**

### **1. 명확한 목표**
```
6종 보고서 → LH 제출 가능한 품질
```

### **2. 구체적 기준**
```
디자인: 단일 CSS, 폰트 규격
데이터: resolve_scalar + present
일관성: Signature = 본문 = 카드
```

### **3. 측정 가능**
```
grep 명령어로 자동 검증
0건 / N건 이상 등 정량 기준
```

### **4. 즉시 실행**
```
복사-붙여넣기만으로 시작
추가 설명 불필요
```

---

**작성일:** 2025-12-25  
**최종 업데이트:** 2025-12-25  
**Git Commit:** `2033d07`  
**상태:** ✅ **READY**

---

**🎊 다음 세션에서 바로 실행 가능합니다! 🎊**

---

**END OF NEXT SESSION READY GUIDE**
