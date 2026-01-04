# 🔑 카카오 API 키 설정 가이드

## 📋 개요

ZeroSite에서 실제 주소 검색을 사용하려면 카카오 REST API 키가 필요합니다.
현재는 Mock 데이터를 사용하고 있지만, 실제 API 키를 설정하면 정확한 주소 검색이 가능합니다.

---

## 🎯 카카오 API 키 발급 받기

### 1단계: 카카오 개발자 사이트 접속
```
https://developers.kakao.com/
```

### 2단계: 로그인
- 카카오 계정으로 로그인
- 개발자 등록 (처음이라면)

### 3단계: 애플리케이션 추가
1. "내 애플리케이션" 메뉴 클릭
2. "애플리케이션 추가하기" 클릭
3. 앱 이름 입력 (예: "ZeroSite")
4. 사업자명 입력 (개인 또는 회사명)

### 4단계: REST API 키 복사
1. 생성된 앱 클릭
2. "앱 키" 섹션에서 "REST API 키" 복사
3. 예시: `1234567890abcdef1234567890abcdef`

### 5단계: 플랫폼 설정 (선택사항)
1. "플랫폼" 메뉴 클릭
2. "Web 플랫폼 등록"
3. 사이트 도메인 등록:
   ```
   https://5173-ivaebkgzir7elqapbc68q-8f57ffe2.sandbox.novita.ai
   http://localhost:5173
   ```

---

## 🔧 ZeroSite에 API 키 설정하기

### 방법 1: 환경변수 설정 (백엔드 서버 전체)

**파일:** `/home/user/webapp/.env`

```bash
# 기존 Mock 키 대신 실제 키로 교체
KAKAO_REST_API_KEY=your_actual_kakao_rest_api_key_here
```

**서버 재시작:**
```bash
cd /home/user/webapp
pkill -f app_production.py
python3 app_production.py > /tmp/backend.log 2>&1 &
```

**장점:**
- ✅ 모든 사용자에게 적용
- ✅ 서버 시작 시 자동 로드
- ✅ 별도 설정 불필요

**단점:**
- ❌ 서버 재시작 필요
- ❌ 키가 서버에 저장됨

---

### 방법 2: 프론트엔드 UI에서 설정 (권장)

**현재 상태:** API 키 설정 화면이 skip되어 있음

**활성화 방법:**

1. **M1LandingPage.tsx 수정**
```typescript
// 현재 (skip됨)
currentStep: 0

// 변경 (API 키 설정 화면 활성화)
currentStep: -1
```

2. **프론트엔드에서 사용**
- Step -1: API 키 입력 화면
- 카카오 REST API 키 입력
- SessionStorage에 저장
- 모든 API 요청 시 자동 포함

**장점:**
- ✅ 서버 재시작 불필요
- ✅ 사용자별 개별 설정 가능
- ✅ 브라우저 세션 종료 시 자동 삭제 (보안)

**단점:**
- ❌ 브라우저마다 설정 필요
- ❌ 세션 종료 시 재입력 필요

---

### 방법 3: API 요청 헤더로 전달 (고급 사용자)

**Postman/cURL 사용 시:**

```bash
curl -X POST "http://localhost:8091/api/m1/address/search" \
  -H "Content-Type: application/json" \
  -H "X-Kakao-API-Key: your_actual_kakao_rest_api_key" \
  -d '{"query": "서울 강남구 테헤란로 521"}'
```

**프론트엔드 fetch 사용 시:**
```typescript
fetch('/api/m1/address/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Kakao-API-Key': 'your_actual_kakao_rest_api_key'
  },
  body: JSON.stringify({ query: '서울 강남구' })
});
```

---

## 🚀 빠른 설정 (권장)

### 백엔드 환경변수 방식

```bash
# 1. .env 파일 편집
cd /home/user/webapp
nano .env

# 2. 다음 줄 찾기
KAKAO_REST_API_KEY=mock_kakao_api_key_for_development

# 3. 실제 키로 교체
KAKAO_REST_API_KEY=1234567890abcdef1234567890abcdef

# 4. 저장 (Ctrl+O, Enter, Ctrl+X)

# 5. 백엔드 재시작
pkill -f app_production.py
python3 app_production.py > /tmp/backend.log 2>&1 &

# 6. 확인
sleep 3
curl -X POST "http://localhost:8091/api/m1/address/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "서울 강남구 테헤란로"}'
```

**예상 결과 (실제 API 사용):**
```json
{
  "suggestions": [
    {
      "road_address": "서울특별시 강남구 테헤란로 521",
      "jibun_address": "서울특별시 강남구 삼성동 143-20",
      "coordinates": {"lat": 37.5084448, "lon": 127.0626804},
      "building_name": "삼성동 파르나스타워"
    }
  ],
  "success": true,
  "using_mock_data": false
}
```

**주목:** `"using_mock_data": false` → 실제 API 사용 중!

---

## 🔍 설정 확인 방법

### 1. 백엔드 로그 확인
```bash
tail -f /home/user/webapp/logs/zerosite.log | grep -i kakao
```

**정상 동작 시:**
```
✅ Kakao API Key provided: True
✅ Found 10 REAL address suggestions
```

**Mock 사용 시:**
```
⚠️ No Kakao API key provided - using mock data
⚠️ Using Mock data for development
```

### 2. API 응답 확인
```bash
curl -X POST "http://localhost:8091/api/m1/address/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "서울 강남구"}' | jq '.using_mock_data'
```

**결과:**
- `false` → 실제 카카오 API 사용 ✅
- `true` → Mock 데이터 사용 ❌

---

## ⚠️ 주의사항

### API 키 보안
1. **절대 공개 저장소에 커밋하지 마세요**
   ```bash
   # .gitignore에 추가
   .env
   .env.local
   .env.production
   ```

2. **환경변수로 관리**
   - Development: `.env.local`
   - Production: 서버 환경변수

3. **키 노출 시 재발급**
   - 카카오 개발자 콘솔에서 즉시 재발급
   - 기존 키 삭제

### API 할당량
- **무료 플랜:** 하루 300,000건
- **초과 시:** 요금 발생 또는 제한
- **모니터링:** 카카오 개발자 콘솔에서 확인

### 도메인 설정
- **localhost:** 개발 시 자동 허용
- **프로덕션:** 도메인 등록 필수
- **Sandbox URL:** 플랫폼에 등록 권장

---

## 🧪 테스트 시나리오

### 실제 API 키 설정 후 테스트

**1. 일반 주소 검색**
```
입력: 서울 강남구 테헤란로 521
결과: 삼성동 파르나스타워 (실제 건물)
```

**2. 상세 주소 검색**
```
입력: 서울특별시 마포구 월드컵북로 396
결과: 누리꿈스퀘어 (정확한 좌표)
```

**3. 지번 주소 검색**
```
입력: 서울 종로구 세종로 1
결과: 광화문 일대 (실제 행정구역)
```

**4. Mock과 비교**
- Mock: 미리 정의된 3-5개 주소
- 실제: 검색어에 따라 다양한 결과

---

## 📊 Before / After 비교

| 항목 | Mock 데이터 | 실제 카카오 API |
|------|-------------|----------------|
| 검색 결과 수 | 3-5개 고정 | 최대 10개 동적 |
| 정확도 | 샘플 데이터 | 실제 주소 DB |
| 건물명 | 제한적 | 상세 정보 |
| 좌표 | 대략적 | 정확한 GPS |
| 업데이트 | 수동 | 실시간 |
| 비용 | 무료 | 무료 (할당량 내) |

---

## 🔗 관련 링크

- **카카오 개발자:** https://developers.kakao.com/
- **Local API 문서:** https://developers.kakao.com/docs/latest/ko/local/dev-guide
- **REST API 키 발급:** https://developers.kakao.com/console/app
- **API 가이드:** https://developers.kakao.com/docs/latest/ko/local/common

---

## 💡 추천 설정

### 개발 환경 (현재)
```bash
# .env
KAKAO_REST_API_KEY=your_development_key
```
- 테스트용 키 사용
- 로컬에서만 작동
- 무료 할당량 내 사용

### 프로덕션 환경 (배포 시)
```bash
# 서버 환경변수
export KAKAO_REST_API_KEY=your_production_key
```
- 프로덕션 전용 키
- 도메인 등록 필수
- 모니터링 설정

---

## ✅ 설정 완료 체크리스트

- [ ] 카카오 개발자 사이트 가입
- [ ] 애플리케이션 생성
- [ ] REST API 키 발급
- [ ] 플랫폼 도메인 등록
- [ ] .env 파일에 키 설정
- [ ] 백엔드 재시작
- [ ] API 테스트 (using_mock_data: false 확인)
- [ ] 프론트엔드 주소 검색 테스트
- [ ] 실제 주소 데이터 확인

---

**지금 바로 카카오 API 키를 발급받아 설정하시면, 정확한 실제 주소 검색을 사용하실 수 있습니다!** 🎉

---

**© 2025 ZeroSite v6.5 | Antenna Holdings Co., Ltd.**
