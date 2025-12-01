# Google Docs 내보내기 기능 설정 가이드

## 📋 개요

LH 토지진단 보고서를 Google Docs로 자동 변환하여 내보낼 수 있습니다.

## 🔧 설정 방법

### 1. Google Cloud Console 설정

1. **Google Cloud Console 접속**
   - URL: https://console.cloud.google.com/

2. **새 프로젝트 생성** (또는 기존 프로젝트 선택)
   - 프로젝트 이름: `lh-land-analysis` (원하는 이름)

3. **API 활성화**
   - 좌측 메뉴 → "API 및 서비스" → "라이브러리"
   - 검색 및 활성화:
     - ✅ **Google Docs API**
     - ✅ **Google Drive API**

4. **서비스 계정 생성**
   - 좌측 메뉴 → "IAM 및 관리자" → "서비스 계정"
   - "서비스 계정 만들기" 클릭
   - 서비스 계정 이름: `lh-report-generator`
   - 역할: "편집자" 또는 "소유자"
   - "완료" 클릭

5. **서비스 계정 키 생성**
   - 생성한 서비스 계정 클릭
   - "키" 탭으로 이동
   - "키 추가" → "새 키 만들기"
   - 키 유형: **JSON** 선택
   - "만들기" 클릭 → JSON 파일 자동 다운로드

### 2. Credentials 파일 배치

다운로드한 JSON 파일을 프로젝트 루트에 배치:

```bash
# 파일 이름을 변경하여 저장
mv ~/Downloads/your-project-xxxxx.json /home/user/webapp/google_credentials.json
```

### 3. 환경 변수 설정 (선택사항)

`.env` 파일에 추가:

```bash
# Google Credentials 경로
GOOGLE_SHEETS_CREDENTIALS_PATH=./google_credentials.json

# Google Drive 폴더 ID (선택사항)
# 특정 폴더에 문서를 저장하려면 설정
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
```

**Google Drive 폴더 ID 찾기**:
- Google Drive에서 폴더 열기
- URL에서 폴더 ID 복사
- 예: `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j`
- 폴더 ID: `1a2b3c4d5e6f7g8h9i0j`

### 4. 서버 재시작

```bash
# 서버 재시작 (credentials 자동 감지)
# 서비스가 자동으로 활성화됩니다
```

## 🎯 사용 방법

1. **토지 분석 실행**
   - 주소, 면적 등 정보 입력
   - "토지 분석하기" 클릭

2. **Google Docs로 내보내기**
   - "📝 Google Docs로 내보내기" 버튼 클릭
   - 문서 생성 대기 (약 10-30초)

3. **생성된 문서 열기**
   - 링크가 자동으로 표시됨
   - "🔗 Google Docs에서 열기" 클릭

## ✅ 확인 방법

서버 시작 시 로그 확인:

```bash
✅ Google Docs 연동 활성화  # 성공
⚠️ Google Docs 연동 미설정 (credentials 없음)  # 실패
```

## 🔐 보안 주의사항

1. **Credentials 파일 보안**
   - `.gitignore`에 `google_credentials.json` 추가됨
   - 절대 Git에 커밋하지 마세요
   - 프로덕션 환경에서는 환경 변수 사용 권장

2. **서비스 계정 권한**
   - 필요한 최소 권한만 부여
   - 정기적으로 키 로테이션

3. **문서 공유 설정**
   - 생성된 문서는 자동으로 "링크를 통해 볼 수 있음" 권한 설정
   - 민감한 정보 주의

## 🆘 문제 해결

### 오류: "Google Docs 서비스가 활성화되지 않았습니다"

**원인**: credentials 파일이 없거나 잘못된 위치

**해결**:
1. `google_credentials.json` 파일 확인
2. 파일 위치: `/home/user/webapp/google_credentials.json`
3. JSON 형식 유효성 확인
4. 서버 재시작

### 오류: "403 Forbidden" 또는 "API not enabled"

**원인**: Google Cloud Console에서 API 미활성화

**해결**:
1. Google Cloud Console 접속
2. "API 및 서비스" → "라이브러리"
3. Google Docs API 및 Google Drive API 활성화

### 오류: "Invalid credentials"

**원인**: 서비스 계정 키가 만료되었거나 삭제됨

**해결**:
1. Google Cloud Console에서 새 키 생성
2. 새 JSON 파일로 교체
3. 서버 재시작

## 📚 추가 자료

- [Google Docs API 문서](https://developers.google.com/docs/api)
- [Google Drive API 문서](https://developers.google.com/drive/api)
- [서비스 계정 가이드](https://cloud.google.com/iam/docs/service-accounts)

## 💡 팁

1. **테스트 프로젝트 사용**
   - 개발 환경에서는 별도의 테스트 프로젝트 사용 권장

2. **폴더 정리**
   - `GOOGLE_DRIVE_FOLDER_ID` 설정으로 문서 자동 정리

3. **배치 크기 제한**
   - 한 번에 너무 많은 문서 생성 시 API 할당량 주의

4. **문서 템플릿**
   - 향후 업데이트에서 템플릿 기능 추가 예정
