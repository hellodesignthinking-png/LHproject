# 🔑 Kakao API 키 설정 가이드

## 📋 개요

현재 Mock 데이터 대신 **실제 Kakao API**를 사용하여 전국 주소를 검색할 수 있습니다.

---

## 🚀 빠른 설정 (3가지 방법)

### 방법 1: 환경 변수 (권장)

```bash
# 1. .env 파일 생성
cd /home/user/webapp
cp .env.example .env

# 2. .env 파일 편집
nano .env

# 3. API 키 입력
KAKAO_REST_API_KEY=your_actual_api_key_here

# 4. 서버 재시작
pkill -f simple_report_server
python3 simple_report_server.py 8005 &
```

### 방법 2: 프론트엔드에서 입력 (SessionStorage)

1. Pipeline 접속
2. "Step 0: API 키 설정" 클릭
3. Kakao REST API 키 입력
4. 저장 (SessionStorage에 저장됨)
5. 주소 검색 시 자동으로 API 키 전송

### 방법 3: 임시 환경 변수

```bash
export KAKAO_REST_API_KEY="your_api_key"
python3 simple_report_server.py 8005 &
```

---

## 🔐 Kakao API 키 발급 방법

### Step 1: Kakao Developers 가입
1. https://developers.kakao.com/ 접속
2. 카카오 계정으로 로그인
3. 개발자 등록 (처음 1회)

### Step 2: 애플리케이션 생성
1. **"내 애플리케이션"** 클릭
2. **"애플리케이션 추가하기"** 클릭
3. 앱 이름 입력: `LH주택 분석 도구` (예시)
4. 회사명: (선택사항)
5. **"저장"** 클릭

### Step 3: REST API 키 확인
1. 생성한 앱 클릭
2. **"앱 설정" → "앱 키"** 메뉴
3. **"REST API 키"** 복사
   ```
   예: 1234567890abcdef1234567890abcdef
   ```

### Step 4: 플랫폼 등록
1. **"앱 설정" → "플랫폼"** 메뉴
2. **"Web 플랫폼 등록"** 클릭
3. 사이트 도메인 입력:
   ```
   http://localhost:3001
   https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai
   ```
4. **"저장"** 클릭

### Step 5: 활성화 설정
1. **"제품 설정" → "Kakao 로컬"** 메뉴
2. **"활성화"** 버튼 클릭
3. 주소 검색 API 사용 가능 확인

---

## 🧪 테스트

### 1. API 키 확인
```bash
curl -X GET "https://dapi.kakao.com/v2/local/search/address.json?query=서울" \
  -H "Authorization: KakaoAK YOUR_API_KEY"
```

**성공 응답**:
```json
{
  "meta": {
    "total_count": 10,
    "pageable_count": 10,
    "is_end": false
  },
  "documents": [...]
}
```

### 2. 서버 테스트
```bash
# 환경 변수 설정
export KAKAO_REST_API_KEY="your_api_key"

# 서버 재시작
cd /home/user/webapp
pkill -f simple_report_server
python3 simple_report_server.py 8005 &

# API 테스트
curl -X POST http://localhost:8005/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query":"서울특별시 강남구"}'
```

**실제 API 응답**:
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "road_address": "서울특별시 강남구 ...",
        "jibun_address": "서울특별시 강남구 ...",
        "zone_no": "06234",
        "display": "서울특별시 강남구 ..."
      }
    ],
    "using_mock_data": false,
    "message": "Real Kakao API results"
  }
}
```

---

## 📊 기능 비교

| 기능 | Mock 데이터 | Kakao API |
|------|-------------|-----------|
| **검색 범위** | 서울 강남구만 | 전국 |
| **결과 개수** | 3개 고정 | 최대 10개 |
| **도로명 주소** | ✅ | ✅ |
| **지번 주소** | ✅ | ✅ |
| **우편번호** | ✅ | ✅ |
| **실시간 검색** | ❌ | ✅ |
| **API 키 필요** | ❌ | ✅ |
| **비용** | 무료 | 무료 (한도 내) |

---

## 🎯 사용 방법

### 프론트엔드에서 API 키 입력

1. **Pipeline 접속**
   ```
   https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai/pipeline
   ```

2. **Step 0: API 키 설정**
   - "API 키 설정" 버튼 클릭
   - Kakao REST API 키 입력
   - "저장" 클릭

3. **주소 검색**
   - "M1 입력하기" 클릭
   - 원하는 주소 입력 (예: "서울특별시 송파구 잠실동")
   - 실제 Kakao API 결과 표시!

---

## 🔍 로그 확인

### 서버 로그
```bash
tail -f /home/user/webapp/report_server.log
```

**Mock 사용 시**:
```
[Address Search] Query: '서울 강남'
[Address Search] API Key present: False
[Address Search] Using Mock data (no API key or no results)
```

**Kakao API 사용 시**:
```
[Address Search] Query: '서울 송파'
[Address Search] API Key present: True
[Kakao API] Searching: '서울 송파'
[Kakao API] Found 10 results
[Address Search] Using Kakao API - 10 results
```

### 브라우저 콘솔 (F12)
```javascript
// Mock 데이터
{
  "using_mock_data": true,
  "message": "Mock data - Kakao API key not configured"
}

// 실제 API
{
  "using_mock_data": false,
  "message": "Real Kakao API results"
}
```

---

## ⚠️ 주의사항

### API 사용량 제한
- **무료**: 하루 100,000건
- **초과 시**: 익일 0시 재설정
- **모니터링**: Kakao Developers 콘솔

### API 키 보안
- ❌ Git에 커밋 금지
- ❌ 프론트엔드에 하드코딩 금지
- ✅ 환경 변수 사용
- ✅ SessionStorage (임시 저장)

### 플랫폼 등록
반드시 사용하는 도메인을 플랫폼에 등록해야 합니다:
```
http://localhost:3001
https://3001-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai
```

---

## 🐛 문제 해결

### API 키가 작동하지 않음
1. **API 키 확인**
   ```bash
   echo $KAKAO_REST_API_KEY
   ```

2. **플랫폼 등록 확인**
   - Kakao Developers → 앱 설정 → 플랫폼
   - 사용 중인 도메인이 등록되어 있는지 확인

3. **API 활성화 확인**
   - 제품 설정 → Kakao 로컬
   - "활성화" 상태 확인

### "검색 결과가 없습니다"
1. **주소 형식 확인**
   - ✅ "서울특별시 강남구"
   - ✅ "서울 강남구 테헤란로"
   - ❌ "강남" (너무 짧음)

2. **API 로그 확인**
   ```bash
   tail -f /home/user/webapp/report_server.log
   ```

3. **브라우저 콘솔 확인**
   - F12 → Console 탭
   - `using_mock_data` 값 확인

---

## 📝 예제

### 검색 가능한 주소 예시

**서울**:
- 서울특별시 강남구 테헤란로
- 서울 송파구 잠실동
- 서울 서초구 반포대로

**경기**:
- 경기도 성남시 분당구
- 경기 수원시 영통구
- 경기도 고양시 일산동구

**기타 지역**:
- 부산광역시 해운대구
- 대구광역시 수성구
- 인천광역시 연수구

---

## 🎉 완료!

이제 **전국 주소 검색**이 가능합니다!

✅ Kakao API 키 발급  
✅ 환경 변수 또는 프론트엔드에서 설정  
✅ 실제 주소 검색 사용  
✅ Mock 데이터 자동 fallback  

---

**작성일**: 2025-12-26  
**상태**: 사용 가능 ✅  
**관련 문서**: ADDRESS_SEARCH_EMPTY_RESULTS_FIXED.md, CORS_ISSUE_RESOLVED.md
