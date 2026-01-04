# 🚨 주소 검색 오류 해결 가이드

## 문제 증상
- 주소 검색 시 "Mock 데이터" 경고 메시지 표시
- 실제 주소가 검색되지 않음
- 샘플 서울 주소만 표시됨

## 원인
**API 키가 설정되지 않았습니다!**

ZeroSite는 Kakao Maps API를 사용하여 주소를 검색합니다. 12월 31일 이후 `.env` 파일이 삭제되거나 SessionStorage가 만료되어 API 키가 없어진 상태입니다.

---

## ✅ 해결 방법

### 방법 1: 브라우저 콘솔에서 직접 설정 (즉시 해결)

1. **프론트엔드 접속**
   ```
   https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai
   ```

2. **F12 키를 눌러 개발자 도구 열기**

3. **Console 탭에서 아래 명령어 실행**
   ```javascript
   // Kakao API 키 설정
   sessionStorage.setItem('m1_api_keys', JSON.stringify({
       kakao: 'YOUR_KAKAO_API_KEY_HERE',
       vworld: '',
       dataGoKr: ''
   }));
   
   // 설정 확인
   console.log('API Keys set:', JSON.parse(sessionStorage.getItem('m1_api_keys')));
   
   // 페이지 새로고침
   location.reload();
   ```

4. **YOUR_KAKAO_API_KEY_HERE를 실제 Kakao REST API 키로 교체**

5. **Enter 키를 눌러 실행**

6. **페이지가 자동 새로고침되면 주소 검색 다시 시도**

---

### 방법 2: 백엔드 .env 파일 설정 (영구 해결)

1. **서버에 .env 파일 생성 완료** ✅
   ```bash
   /home/user/webapp/.env
   ```

2. **Kakao API 키 입력**
   
   `.env` 파일을 편집하여 아래 라인을 수정:
   ```bash
   KAKAO_REST_API_KEY=YOUR_KAKAO_API_KEY_HERE
   ```

3. **백엔드 재시작**
   ```bash
   # 프로세스 확인
   ps aux | grep uvicorn
   
   # 백엔드 재시작 (root 권한 필요)
   # 또는 서버 관리자에게 재시작 요청
   ```

---

## 📋 Kakao API 키 발급 방법

1. **Kakao Developers 접속**
   ```
   https://developers.kakao.com/
   ```

2. **로그인 후 "내 애플리케이션" 클릭**

3. **"애플리케이션 추가하기" 클릭**
   - 앱 이름: ZeroSite (또는 원하는 이름)
   - 회사명: 선택사항

4. **생성된 앱 클릭 → "앱 키" 메뉴**

5. **"REST API 키" 복사**
   - 예: `1234567890abcdef1234567890abcdef`

6. **위의 해결 방법 1 또는 2에 붙여넣기**

---

## 🔍 현재 상태 확인

### 브라우저 콘솔에서 확인
```javascript
// API 키 설정 여부 확인
const keys = sessionStorage.getItem('m1_api_keys');
console.log('Current API Keys:', keys ? JSON.parse(keys) : 'Not set');
```

### 주소 검색 테스트
1. 주소 입력: `서울시 강남구`
2. 검색 버튼 클릭
3. 콘솔에서 로그 확인:
   - ✅ 성공: `📝 검색 결과: { success: true, ... }`
   - ❌ 실패: `⚠️ MOCK DATA: API key not provided`

---

## 🎯 빠른 테스트용 공개 키 (제한적)

**주의**: 아래 키는 테스트용이며 실제 프로덕션에서는 사용하지 마세요!

```javascript
sessionStorage.setItem('m1_api_keys', JSON.stringify({
    kakao: '1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p',  // 예시 - 실제로는 작동 안함
    vworld: '',
    dataGoKr: ''
}));
```

실제 키는 위의 "Kakao API 키 발급 방법"을 따라 발급받으세요.

---

## 💡 추가 팁

### API 키 없이도 사용 가능 (제한적)
현재 시스템은 API 키가 없어도 **Mock 데이터**로 작동합니다:
- 서울 지역 샘플 주소 제공
- 개발/테스트 목적으로는 충분
- 실제 주소는 검색 불가

### 실제 프로덕션 사용 시
- 반드시 유효한 Kakao API 키 설정 필요
- VWorld API 키 (지적도 조회용)
- Data.go.kr API 키 (실거래가 조회용)

---

## 🔧 문제 해결이 안 될 경우

### 1. 캐시 삭제
```javascript
// 모든 캐시 삭제
sessionStorage.clear();
localStorage.clear();
location.reload();
```

### 2. 백엔드 로그 확인
```bash
cd /home/user/webapp
tail -100 backend.log | grep -i "kakao\|address"
```

### 3. 네트워크 확인
- F12 → Network 탭
- 주소 검색 시도
- `/api/m1/address/search` 요청 확인
- Response에 `using_mock_data: true` 있는지 확인

### 4. 백엔드 API 직접 테스트
```bash
curl -X POST http://localhost:49999/api/m1/address/search \
  -H "Content-Type: application/json" \
  -H "X-Kakao-API-Key: YOUR_KEY_HERE" \
  -d '{"query": "서울시 강남구"}'
```

---

## 📞 지원

문제가 계속되면 아래 정보와 함께 문의:
1. 브라우저 콘솔 로그 (F12 → Console)
2. 네트워크 요청/응답 (F12 → Network)
3. 사용 중인 API 키 (일부만 `****`)

---

**문서 생성일**: 2025-01-04  
**작성자**: ZeroSite Support Team  
**버전**: 1.0  
**상태**: ✅ Active Solution
