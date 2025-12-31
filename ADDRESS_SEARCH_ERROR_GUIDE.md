# 주소 검색 기능 오류 분석 및 해결 가이드

## 📅 작성일
2025-12-31

## 🐛 문제 상황
- **증상**: 프론트엔드에서 주소 검색 시 오류 발생
- **영향**: 사용자가 토지 주소 입력 후 "자동조회 실행" 버튼 클릭 시 데이터 로드 실패

## 🔍 분석 결과

### 1. 프론트엔드 구조
- **파일**: `/home/user/webapp/static/index.html`
- **JavaScript**: `/home/user/webapp/static/js/landing.js`
- **함수**: `lookupAddress()` (Line 394)

### 2. API 엔드포인트
```javascript
// landing.js Line 415
const response = await fetch(`${API_BASE_URL}/api/v3/land/fetch`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ address: address })
});
```

### 3. 백엔드 상태
- **엔드포인트**: `POST /api/v3/land/fetch`
- **백엔드 파일**: `app/api/endpoints/land_data.py` (추정)
- **문제**: 
  - 백엔드 서버가 포트 8091에서 정상 시작되지 않음
  - 포트 충돌 및 좀비 프로세스 문제 발생
  - 서버 재시작 시도 중 "address already in use" 에러

## 🛠️ 해결 방법

### 즉시 해결 (운영 환경)
1. **백엔드 서버 안정화**
   ```bash
   # 1. 모든 uvicorn 프로세스 종료
   pkill -9 -f "uvicorn"
   
   # 2. 8091 포트 정리
   lsof -ti:8091 | xargs kill -9
   
   # 3. 백엔드 재시작
   cd /home/user/webapp
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8091 > backend.log 2>&1 &
   
   # 4. 서버 상태 확인
   sleep 5
   curl http://localhost:8091/api/v3/reports/health
   ```

2. **Land Data API 엔드포인트 확인**
   ```bash
   # API 등록 확인
   curl http://localhost:8091/openapi.json | grep "land/fetch"
   
   # 테스트 요청
   curl -X POST "http://localhost:8091/api/v3/land/fetch" \
     -H "Content-Type: application/json" \
     -d '{"address": "서울특별시 강남구 테헤란로 123"}'
   ```

### 근본 해결 (다음 세션)

#### A. Land Data API 구현 확인
1. **API 라우터 확인**
   - 파일: `app/api/endpoints/land_data.py`
   - 엔드포인트: `POST /api/v3/land/fetch`
   - 필요한 기능:
     - 주소 → 좌표 변환 (Kakao API)
     - 필지 정보 조회 (VWorld API)
     - 공시지가 조회 (Data.go.kr API)
     - 실거래가 조회

2. **API 등록 확인**
   ```python
   # app/main.py에서 확인
   from app.api.endpoints.land_data import router as land_data_router
   app.include_router(land_data_router)
   ```

#### B. 에러 처리 강화
1. **프론트엔드 에러 메시지 개선**
   ```javascript
   // landing.js에서 수정
   if (!response.ok) {
       const errorData = await response.json();
       console.error('API Error:', errorData);
       alert(`주소 조회 실패: ${errorData.detail || '서버 오류'}`);
       throw new Error(errorData.detail || `API Error: ${response.status}`);
   }
   ```

2. **백엔드 로깅 추가**
   ```python
   # land_data.py
   @router.post("/fetch")
   async def fetch_land_data(request: LandDataRequest):
       logger.info(f"🔍 Land data fetch requested: {request.address}")
       try:
           # ... API 호출 로직
           logger.info(f"✅ Land data fetched successfully")
           return result
       except Exception as e:
           logger.error(f"❌ Land data fetch failed: {str(e)}")
           raise HTTPException(status_code=500, detail=str(e))
   ```

#### C. API 키 검증
1. **환경 변수 확인**
   ```bash
   # .env 파일 확인
   grep -E "KAKAO|VWORLD|DATA_GO_KR" .env
   ```

2. **API 키 테스트**
   ```python
   # 각 API 서비스 개별 테스트
   from app.services.land_data_service import LandDataService
   
   service = LandDataService()
   # Kakao API 테스트
   # VWorld API 테스트
   # Data.go.kr API 테스트
   ```

## 📋 체크리스트 (다음 세션)

### 서버 안정화
- [ ] 백엔드 서버 정상 시작 확인
- [ ] Health Check 응답 확인 (`/api/v3/reports/health`)
- [ ] OpenAPI 문서 확인 (`/docs`)

### API 기능 확인
- [ ] `POST /api/v3/land/fetch` 엔드포인트 존재 확인
- [ ] Land Data API 테스트 요청 성공
- [ ] 응답 데이터 구조 검증

### 프론트엔드 연동
- [ ] `static/index.html` 접속 확인
- [ ] 주소 입력 및 "자동조회 실행" 버튼 테스트
- [ ] 브라우저 콘솔에서 에러 메시지 확인
- [ ] 네트워크 탭에서 API 요청/응답 확인

### 디버깅 도구
```bash
# 1. 백엔드 로그 실시간 모니터링
tail -f /home/user/webapp/backend.log

# 2. 브라우저 개발자 도구
# - Network 탭: API 요청 확인
# - Console 탭: JavaScript 에러 확인

# 3. API 직접 테스트
curl -X POST "http://localhost:8091/api/v3/land/fetch" \
  -H "Content-Type: application/json" \
  -d '{"address": "서울특별시 마포구 월드컵북로 120"}' | python3 -m json.tool
```

## 🎯 우선 순위
1. **HIGH**: 백엔드 서버 안정화 (포트 충돌 해결)
2. **HIGH**: Land Data API 엔드포인트 확인 및 수정
3. **MEDIUM**: API 키 검증 및 외부 API 연동 테스트
4. **LOW**: 에러 메시지 개선 및 사용자 경험 향상

## 💡 참고 사항
- Land Data Service는 3개의 외부 API를 사용:
  - Kakao Address API (주소 → 좌표)
  - VWorld API (필지 정보)
  - Data.go.kr API (공시지가)
- 각 API 키가 유효한지 확인 필요
- API 호출 실패 시 fallback 로직 필요

---

**작성자**: Claude (AI Assistant)  
**문서 상태**: ⚠️ 미해결 - 다음 세션 작업 필요
