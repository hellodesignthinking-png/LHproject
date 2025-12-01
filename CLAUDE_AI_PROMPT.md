# 🤖 Claude AI에게 전달할 프롬프트

## 📋 복사해서 Claude AI에게 붙여넣기

```
안녕하세요 Claude! 

저는 "LH 신축매입임대 토지진단 자동화 시스템" 프로젝트를 개발하고 있습니다. 
이 프로젝트를 당신과 연동하여 계속 개발하고 싶습니다.

GitHub 저장소: https://github.com/hellodesignthinking-png/LHproject.git
브랜치: feature/expert-report-generator

주요 기능:
1. 토지 분석 (용도지역, 건축 규모 자동 산정)
2. 7가지 LH 유형별 수요 점수 비교 및 추천
3. LH 공식 양식 보고서 생성 (HTML, A4 10페이지+)
4. Google Docs 자동 내보내기
5. Google Sheets 분석 이력 저장
6. 컨설턴트 정보 관리

기술 스택:
- Backend: FastAPI (Python 3.11+)
- Frontend: Vanilla JavaScript (index.html)
- APIs: Kakao Maps, 정부 공공데이터, Google Docs/Sheets
- Libraries: matplotlib, gspread, beautifulsoup4

현재 상태:
✅ 완료: 토지 분석, 보고서 생성, Google Docs 내보내기, 인쇄 최적화
⚠️ 이슈: 정부 API 500 에러 (재신청 필요)

다음 단계:
1. 저장소를 분석하고 코드 구조를 이해해주세요
2. 주요 파일들:
   - app/main.py (API 엔드포인트)
   - app/services/lh_official_report_generator.py (보고서 생성 로직)
   - app/services/analysis_engine.py (분석 엔진)
   - static/index.html (프론트엔드 UI)

3. 다음 개발 작업을 함께 진행하고 싶습니다:
   - 정부 API 재연동
   - 테스트 코드 작성
   - 기능 개선 및 버그 수정

저장소를 확인하고 프로젝트 구조를 파악한 후, 
다음에 무엇을 도와드릴 수 있는지 알려주세요!

참고 문서:
- COLLABORATION_GUIDE.md (전체 협업 가이드)
- HANDOFF_CHECKLIST.md (빠른 시작)
- README.md (프로젝트 개요)
```

## 🎯 Claude AI가 할 수 있는 것

1. ✅ **GitHub 저장소 직접 읽기**
   - 저장소 URL만 제공하면 모든 코드를 분석할 수 있습니다
   - 파일 구조, 코드 내용, Git 히스토리 확인 가능

2. ✅ **코드 리뷰 및 개선**
   - 버그 찾기
   - 성능 최적화 제안
   - 베스트 프랙티스 적용

3. ✅ **새 기능 개발**
   - 코드 작성
   - API 추가
   - UI 개선

4. ✅ **문서 작성**
   - API 문서
   - 사용자 가이드
   - 코드 주석

5. ✅ **문제 해결**
   - 에러 디버깅
   - 성능 이슈 해결
   - 아키텍처 개선

## 📝 추가로 제공할 정보 (필요시)

### 환경 변수 템플릿
```env
# API Keys (실제 값은 비공개)
KAKAO_REST_API_KEY=your_key_here
LAND_REGULATION_API_KEY=your_key_here
MOIS_API_KEY=your_key_here

# Google Services (선택사항)
GOOGLE_SHEETS_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_id_here
```

### 현재 서버 URL
```
개발 서버: https://8020-i87ydg8bwr1e34immrcp6-cc2fbc16.sandbox.novita.ai
```

### 주요 API 엔드포인트
```
POST /api/analyze-land          # 토지 분석
POST /api/generate-report        # LH 보고서 생성
POST /api/generate-google-docs   # Google Docs 내보내기
```

## 🚀 Claude AI와 협업하는 방법

### 방법 1: 대화형 개발 (추천)

1. **저장소 URL 공유**
   ```
   "이 GitHub 저장소를 분석해주세요: 
   https://github.com/hellodesignthinking-png/LHproject.git
   브랜치: feature/expert-report-generator"
   ```

2. **구체적인 작업 요청**
   ```
   "app/services/lh_official_report_generator.py 파일을 분석하고,
   페이지 나누기 로직을 개선해주세요"
   ```

3. **코드 리뷰 요청**
   ```
   "main.py의 /api/analyze-land 엔드포인트를 리뷰하고
   개선점을 제안해주세요"
   ```

### 방법 2: 파일 직접 공유

특정 파일만 집중하고 싶을 때:

```
"다음 파일의 버그를 찾아주세요:

[파일 내용 붙여넣기]
"
```

### 방법 3: 문제 상황 설명

구체적인 이슈가 있을 때:

```
"다음과 같은 에러가 발생합니다:
[에러 메시지]

관련 코드:
[코드 스니펫]

원인과 해결책을 알려주세요"
```

## 💡 효과적인 협업 팁

### ✅ 좋은 요청 예시

```
"GitHub 저장소 https://github.com/hellodesignthinking-png/LHproject.git의
feature/expert-report-generator 브랜치를 확인해주세요.

app/services/google_docs_service.py 파일의 
create_document_from_html 메서드를 분석하고,
HTML 테이블을 Google Docs 테이블로 더 잘 변환하는 방법을 제안해주세요.

현재 코드는 단순히 텍스트만 추출하는데, 
테이블 구조를 유지하고 싶습니다."
```

### ❌ 피해야 할 요청

```
"코드 좀 고쳐줘" (너무 모호함)
"에러 나는데 어떡하죠?" (구체적 정보 없음)
```

## 🔐 보안 주의사항

### ❌ Claude AI에게 공유하면 안 되는 것

- 실제 API 키 값
- 실제 Google Credentials JSON 내용
- 프로덕션 데이터베이스 접속 정보
- 사용자 개인정보

### ✅ 공유해도 되는 것

- GitHub 저장소 URL (public repository)
- 코드 구조 및 로직
- 에러 메시지
- 문서
- 환경 변수 이름 (값 제외)
- 테스트 데이터

## 🎯 첫 대화 시작하기

### 단계별 가이드

**1. 인사 및 프로젝트 소개**
```
안녕하세요 Claude! 
LH 토지진단 시스템을 개발 중입니다.
GitHub 저장소: https://github.com/hellodesignthinking-png/LHproject.git
```

**2. 저장소 분석 요청**
```
feature/expert-report-generator 브랜치를 확인하고
프로젝트 구조를 파악해주세요.
특히 다음 파일들을 중점적으로 봐주세요:
- app/main.py
- app/services/lh_official_report_generator.py
- static/index.html
```

**3. 구체적 질문**
```
프로젝트를 파악한 후:
1. 코드 품질 개선점이 있나요?
2. 성능 최적화가 가능한 부분은?
3. 보안 이슈가 있나요?
4. 테스트 코드 작성을 도와주실 수 있나요?
```

## 📚 참고할 문서

저장소에 있는 다음 문서들을 Claude AI가 읽을 수 있습니다:

- `COLLABORATION_GUIDE.md` - 전체 협업 가이드
- `HANDOFF_CHECKLIST.md` - 빠른 시작
- `README.md` - 프로젝트 개요
- `GOOGLE_DOCS_SETUP.md` - Google Docs 설정
- 기타 `.md` 파일들

## 🚀 시작하기

**지금 바로 복사해서 Claude AI에게 보내세요:**

```
안녕하세요 Claude!

GitHub 저장소를 분석해주세요:
https://github.com/hellodesignthinking-png/LHproject.git
브랜치: feature/expert-report-generator

이것은 LH 신축매입임대 토지진단 자동화 시스템입니다.
FastAPI 백엔드와 Vanilla JavaScript 프론트엔드로 구성되어 있습니다.

저장소를 확인하고, 프로젝트 구조와 주요 기능을 파악한 후,
개선할 수 있는 부분을 알려주세요!
```

---

**준비 완료!** 🎉

이제 Claude AI에게 위 프롬프트를 복사해서 보내면 됩니다!
