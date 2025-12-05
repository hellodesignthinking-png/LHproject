# Google Sheets 연동 설정 가이드

## 개요
LH 토지진단 시스템은 모든 분석 결과를 Google Sheets에 자동으로 저장하여 이력 관리 및 중복 검토 기능을 제공합니다.

## 주요 기능

### 1. 자동 저장
- 모든 토지 분석 결과가 자동으로 Google Sheets에 기록됩니다
- 분석일시, 주소, 면적, 추천유형, 수요점수, 담당자 정보 등이 저장됩니다

### 2. 중복 검토
- 같은 토지가 이전에 분석되었는지 자동으로 확인합니다
- 주소와 면적을 기준으로 유사도를 판단합니다
- 중복 발견 시 해당 행을 노란색으로 표시합니다

### 3. 이력 관리
- 모든 분석 이력을 시간순으로 확인할 수 있습니다
- 담당자별 필터링이 가능합니다
- 엑셀 다운로드 등 Google Sheets의 모든 기능을 활용할 수 있습니다

---

## 설정 방법

### 1단계: Google Cloud 프로젝트 생성

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속합니다
2. 새 프로젝트를 생성합니다 (예: "LH-토지진단-시스템")
3. 프로젝트를 선택합니다

### 2단계: Google Sheets API 활성화

1. 좌측 메뉴에서 **"API 및 서비스"** → **"라이브러리"** 선택
2. "Google Sheets API" 검색 후 선택
3. **"사용 설정"** 버튼 클릭
4. "Google Drive API"도 동일하게 활성화

### 3단계: 서비스 계정 생성

1. **"API 및 서비스"** → **"사용자 인증 정보"** 선택
2. **"사용자 인증 정보 만들기"** → **"서비스 계정"** 선택
3. 서비스 계정 세부정보 입력:
   - 이름: `lh-land-analysis-bot`
   - 설명: `LH 토지진단 시스템 자동 저장용`
4. **"만들기 및 계속하기"** 클릭
5. 역할 선택: **"편집자"** 또는 **"뷰어"** (권장: 편집자)
6. **"완료"** 클릭

### 4단계: JSON 키 파일 다운로드

1. 생성된 서비스 계정 클릭
2. **"키"** 탭 선택
3. **"키 추가"** → **"새 키 만들기"**
4. 키 유형: **JSON** 선택
5. **"만들기"** 클릭
6. JSON 파일이 자동으로 다운로드됩니다

### 5단계: JSON 파일 설정

1. 다운로드한 JSON 파일의 이름을 `google_credentials.json`으로 변경
2. 프로젝트 루트 디렉토리(`/home/user/webapp/`)에 복사
3. 파일 권한 설정 (보안):
   ```bash
   chmod 600 /home/user/webapp/google_credentials.json
   ```

### 6단계: Google Sheets 생성 및 공유

1. [Google Sheets](https://sheets.google.com/)에서 새 스프레드시트 생성
2. 이름 설정: `LH 토지분석 기록`
3. 스프레드시트 URL에서 ID 복사:
   ```
   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
   ```
   예: `1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0`

4. **중요**: 스프레드시트를 서비스 계정과 공유:
   - 우측 상단 **"공유"** 버튼 클릭
   - JSON 파일의 `client_email` 값 복사 (예: `lh-land-analysis-bot@project-id.iam.gserviceaccount.com`)
   - 이메일 주소 입력란에 붙여넣기
   - 권한: **"편집자"** 선택
   - **"전송"** 클릭

### 7단계: 환경 변수 설정

`.env` 파일을 열고 다음 값을 설정합니다:

```env
# Google Sheets Integration
GOOGLE_SHEETS_CREDENTIALS_PATH=./google_credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0
GOOGLE_SHEETS_WORKSHEET_NAME=토지분석기록
```

---

## 검증

### 1. 서버 재시작
```bash
cd /home/user/webapp && python -m uvicorn app.main:app --host 0.0.0.0 --port 8018 --reload
```

### 2. 로그 확인
서버 시작 시 다음 메시지가 표시되어야 합니다:
```
✅ Google Sheets 연동 활성화
```

오류 메시지가 표시되는 경우:
```
⚠️ Google Sheets 연동 미설정 (credentials 또는 spreadsheet_id 없음)
⚠️ Google Sheets 초기화 실패: {오류내용}
```

### 3. 분석 테스트
1. 토지 분석을 실행합니다
2. 분석 완료 후 다음 메시지 확인:
   ```
   📊 Google Sheets에 분석 결과 저장 중...
   ✅ Google Sheets 저장 완료 (행 2)
   ```
3. Google Sheets를 열어 데이터가 저장되었는지 확인합니다

---

## 저장되는 데이터 항목

| 컬럼명 | 설명 | 예시 |
|--------|------|------|
| 분석일시 | 분석이 실행된 날짜와 시간 | 2024-01-15 14:30:25 |
| 주소 | 토지의 도로명 주소 | 서울특별시 강남구 역삼동 679 |
| 지번주소 | 토지의 지번 주소 | 서울특별시 강남구 역삼동 679번지 |
| 토지면적(㎡) | 토지 면적 | 500 |
| 용도지역 | 용도지역 분류 | 제2종일반주거지역 |
| 추천유형 | 시스템이 추천한 세대 유형 | 신혼·신생아 I |
| 수요점수 | 수요 분석 점수 (0-100) | 67.5 |
| 예상세대수 | 건축 가능한 세대 수 | 12 |
| 예상층수 | 건축 가능한 층수 | 5 |
| 건폐율(%) | 건폐율 | 60 |
| 용적률(%) | 용적률 | 200 |
| 담당자_이름 | 컨설팅 담당자 이름 | 홍길동 |
| 담당자_연락처 | 담당자 전화번호 | 010-1234-5678 |
| 담당자_부서 | 담당자 소속 부서 | 토지개발팀 |
| 담당자_이메일 | 담당자 이메일 | hong@example.com |
| 리스크개수 | 발견된 리스크 총 개수 | 3 |
| 치명적리스크 | 치명적 리스크 목록 | 고압선 인접, 주유소 25m |
| LH매입제외여부 | LH 매입 제외 대상 여부 | 아니오 |
| 보고서경로 | 생성된 보고서 경로 | /api/reports/abc123.pdf |
| 분석ID | 고유 분석 식별자 | 20240115_143025_1234 |

---

## 중복 검사 로직

### 검사 기준
1. **주소 유사도**: 입력 주소와 기존 주소가 서로 포함 관계에 있는지 확인
2. **면적 유사도**: 면적 차이가 허용 오차(±10㎡) 이내인지 확인

### 결과 표시
- 중복 발견 시 해당 행의 배경색을 **노란색**으로 표시
- 로그에 중복 경고 메시지 출력:
  ```
  ⚠️ 중복 경고: 이 토지는 이전에 2회 분석되었습니다
     분석 날짜: 2024-01-10 10:20:30, 2024-01-12 15:45:12
  ```

---

## 문제 해결

### 연동이 안 될 때

**증상 1**: `⚠️ Google Sheets 연동 미설정`
- **원인**: JSON 파일이 없거나 `.env`에 설정이 누락됨
- **해결**: `google_credentials.json` 파일과 `.env` 설정 확인

**증상 2**: `⚠️ Google Sheets 초기화 실패: [Errno 2] No such file or directory`
- **원인**: JSON 파일 경로가 잘못됨
- **해결**: 파일이 `/home/user/webapp/google_credentials.json`에 있는지 확인

**증상 3**: `gspread.exceptions.APIError: {'code': 403, 'message': 'Forbidden'}`
- **원인**: 스프레드시트를 서비스 계정과 공유하지 않음
- **해결**: Google Sheets에서 서비스 계정 이메일(`client_email`)로 공유

**증상 4**: `ValueError: Spreadsheet not found`
- **원인**: Spreadsheet ID가 잘못됨
- **해결**: Google Sheets URL에서 올바른 ID를 복사하여 `.env`에 설정

**증상 5**: `gspread.exceptions.WorksheetNotFound`
- **원인**: 워크시트 이름이 일치하지 않음
- **해결**: `.env`의 `GOOGLE_SHEETS_WORKSHEET_NAME`과 실제 시트 이름 확인

### 권한 오류

JSON 파일 권한이 너무 개방적일 경우:
```bash
chmod 600 /home/user/webapp/google_credentials.json
chown $USER:$USER /home/user/webapp/google_credentials.json
```

---

## 선택사항 (비활성화)

Google Sheets 연동을 사용하지 않으려면:

1. `.env` 파일에서 다음 줄 제거 또는 주석 처리:
   ```env
   # GOOGLE_SHEETS_CREDENTIALS_PATH=./google_credentials.json
   # GOOGLE_SHEETS_SPREADSHEET_ID=
   ```

2. 시스템은 정상적으로 작동하지만 Google Sheets 저장은 건너뜁니다:
   ```
   ⚠️ Google Sheets 연동 미설정 (credentials 또는 spreadsheet_id 없음)
   ```

---

## 추가 기능 (향후 개발 가능)

- [ ] 대시보드: 분석 통계 및 트렌드 시각화
- [ ] 알림: 중복 토지 발견 시 이메일/슬랙 알림
- [ ] 필터링: 담당자별, 지역별, 날짜별 분석 이력 조회 API
- [ ] 자동 보고서: 주간/월간 분석 요약 보고서 생성
- [ ] 데이터 분석: 가장 많이 분석된 지역, 평균 수요 점수 등

---

## 보안 주의사항

1. **JSON 파일 보호**: `google_credentials.json` 파일은 절대 Git에 커밋하지 마세요
   - `.gitignore`에 추가: `google_credentials.json`

2. **권한 최소화**: 서비스 계정에 필요한 최소 권한만 부여하세요

3. **공유 제한**: Google Sheets는 서비스 계정과만 공유하고, 불필요한 사용자는 제거하세요

4. **정기 감사**: 주기적으로 서비스 계정 키를 재생성하고 업데이트하세요

---

## 참고 자료

- [Google Sheets API 문서](https://developers.google.com/sheets/api)
- [gspread 라이브러리 문서](https://docs.gspread.org/)
- [Google Cloud 서비스 계정 가이드](https://cloud.google.com/iam/docs/service-accounts)
