# 🔑 API 설정 가이드

ZeroSite v3.4 랜딩페이지에서 **실제 토지 데이터**를 조회하려면 API 키 설정이 필요합니다.

## ⚠️ 현재 상태 확인

주소 조회 시 아래와 같은 경고가 표시된다면 API 키가 설정되지 않은 상태입니다:

```
⚠️ 카카오 API 연결 실패: API 키를 확인해주세요.
현재 테스트용 Mock 데이터를 표시중입니다.
```

## 🚀 빠른 설정 (3분 완성)

### 1️⃣ .env 파일 생성

프로젝트 루트 디렉토리에서 `.env.example` 파일을 복사하여 `.env` 파일을 만듭니다:

```bash
cp .env.example .env
```

### 2️⃣ 필수 API 키 발급 및 설정

아래 3개의 API 키를 발급받아 `.env` 파일에 입력합니다:

#### 📍 Kakao REST API (주소 → 좌표 변환)

**발급 방법:**
1. https://developers.kakao.com/ 접속
2. 로그인 후 `내 애플리케이션` → `애플리케이션 추가하기`
3. 앱 이름 입력 (예: "ZeroSite Land Analysis")
4. 생성된 앱 선택 → `앱 키` 탭 → **REST API 키** 복사

`.env` 파일 수정:
```env
KAKAO_REST_API_KEY=당신의_카카오_REST_API_키
```

#### 🌍 VWorld API (토지이용규제 정보)

**발급 방법:**
1. https://www.vworld.kr/ 접속
2. 회원가입 후 로그인
3. `오픈API` → `인증키 발급` → `신규발급`
4. 서비스명 입력 (예: "ZeroSite") → **API 키** 복사

`.env` 파일 수정:
```env
VWORLD_API_KEY=당신의_VWorld_API_키
# or
LAND_REGULATION_API_KEY=당신의_VWorld_API_키
```

#### 📊 공공데이터포털 API (토지특성, 공시지가, 실거래가)

**발급 방법:**
1. https://www.data.go.kr/ 접속
2. 회원가입 후 로그인
3. 검색창에 "토지특성정보" 검색 → 활용신청
4. `마이페이지` → `오픈API` → **인증키(일반 인증키)** 복사

`.env` 파일 수정:
```env
DATA_GO_KR_API_KEY=당신의_공공데이터포털_API_키
# or
MOIS_API_KEY=당신의_공공데이터포털_API_키
```

### 3️⃣ 서버 재시작

API 키를 설정한 후 서버를 재시작합니다:

```bash
# 개발 서버
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 Docker 사용 시
docker-compose restart
```

## ✅ 설정 확인

### 방법 1: 웹 브라우저에서 확인

브라우저에서 아래 URL에 접속:

```
http://localhost:8000/api/v3/land/health
```

**정상 응답 예시:**
```json
{
  "service": "Land Data API v3.4",
  "status": "ready",
  "api_keys": {
    "kakao_rest_api": "✅ 설정됨",
    "data_go_kr_api": "✅ 설정됨",
    "vworld_api": "✅ 설정됨"
  },
  "message": "✅ 모든 API 키가 올바르게 설정되었습니다."
}
```

### 방법 2: 랜딩페이지에서 확인

1. 브라우저에서 `http://localhost:8000` 접속
2. 주소 입력 (예: "서울특별시 강남구 역삼동 858")
3. `자동조회 실행` 버튼 클릭

**성공:**
- 데이터 출처 표시가 **녹색**으로 "데이터 출처: 정부 공공데이터 API (실제 데이터)" 표시

**실패 (Mock 데이터):**
- 데이터 출처 표시가 **주황색**으로 경고 메시지 표시
- 확인 창에서 API 키 상태 확인 가능

## 🧪 테스트 주소

설정이 완료되면 아래 주소로 테스트해보세요:

```
서울특별시 강남구 역삼동 858
경기도 성남시 분당구 정자동 178-1
서울특별시 서초구 서초동 1234
```

## 🔧 트러블슈팅

### Q1: API 키를 설정했는데도 Mock 데이터가 나옵니다

**해결 방법:**
1. `.env` 파일이 프로젝트 루트 디렉토리에 있는지 확인
2. API 키에 `your_` 또는 `example` 같은 플레이스홀더가 남아있는지 확인
3. 서버를 재시작했는지 확인
4. API 키 앞뒤로 따옴표("")가 없는지 확인

### Q2: "카카오 API 연결 실패" 에러가 계속 발생합니다

**해결 방법:**
1. Kakao Developers에서 **REST API 키**를 복사했는지 확인 (JavaScript 키 아님!)
2. API 키가 활성화 상태인지 확인
3. 네트워크 방화벽이 `dapi.kakao.com` 접근을 차단하는지 확인

### Q3: 공공데이터 API가 작동하지 않습니다

**해결 방법:**
1. 공공데이터포털에서 **일반 인증키(Encoding)**를 복사했는지 확인
2. API 활용신청 후 승인까지 **최대 2시간** 소요될 수 있습니다
3. 서비스 상태가 "정상운영"인지 확인

### Q4: Docker 환경에서 설정하려면?

`docker-compose.yml` 파일에 환경변수를 추가하거나, `.env` 파일을 Docker 컨테이너에 마운트합니다:

```yaml
services:
  app:
    environment:
      - KAKAO_REST_API_KEY=${KAKAO_REST_API_KEY}
      - VWORLD_API_KEY=${VWORLD_API_KEY}
      - DATA_GO_KR_API_KEY=${DATA_GO_KR_API_KEY}
```

## 📚 추가 리소스

- [Kakao Developers 가이드](https://developers.kakao.com/docs/latest/ko/local/dev-guide)
- [VWorld API 문서](https://www.vworld.kr/dev/v4dv_2ddataguide2_s002.do)
- [공공데이터포털 가이드](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15001169)

## 💡 참고사항

- **무료 플랜**: 모든 API는 무료 플랜으로 시작할 수 있습니다
- **할당량**: 일일 API 호출 제한이 있으니 각 플랫폼의 정책을 확인하세요
- **보안**: `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다

---

**문제가 계속되면?**
- GitHub Issues: https://github.com/hellodesignthinking-png/LHproject/issues
- 이메일: [your-email@example.com]
