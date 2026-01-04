# 🚨 주소 검색 실패 - 즉시 해결 방법

## ✅ 해결 방법 (3분 안에!)

### 🎯 **API 키 자동 설정 페이지 사용 (가장 쉬움!)**

#### 1단계: API 키 설정 페이지 접속
```
https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/setup-api-keys.html
```
**👆 이 링크를 클릭하세요!**

#### 2단계: "API Keys 설정하기" 버튼 클릭
- 자동으로 3개 API 키 모두 설정됩니다
- ✅ Kakao API
- ✅ VWorld API  
- ✅ Data.go.kr API

#### 3단계: "주소 검색 테스트" 버튼 클릭 (선택)
- 주소 검색이 정상 작동하는지 확인

#### 4단계: "메인 페이지로 이동" 버튼 클릭
- 메인 서비스로 자동 이동
- 주소 검색 시작!

---

## 🔧 대체 방법 (수동 설정)

### 브라우저 콘솔에서 직접 설정

1. **메인 페이지 접속**
   ```
   https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai
   ```

2. **F12 키 누르기** (개발자 도구 열기)

3. **Console 탭 선택**

4. **아래 코드 복사 붙여넣기 후 Enter**
   ```javascript
   sessionStorage.setItem('m1_api_keys', JSON.stringify({
       kakao: '1b172a21a17b8b51dd47884b45228483',
       vworld: '781864DB-126D-3B14-A0EE-1FD1B1000534',
       dataGoKr: '702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d'
   }));
   alert('✅ API Keys 설정 완료!');
   location.reload();
   ```

5. **페이지 자동 새로고침 → 주소 검색 시도**

---

## 📱 화면별 가이드

### API 키 설정 페이지 화면
```
┌─────────────────────────────────────┐
│        🔑                           │
│   API Keys 자동 설정                │
│                                     │
│   현재 상태:                        │
│   Kakao API:      ✗ 미설정         │
│   VWorld API:     ✗ 미설정         │
│   Data.go.kr API: ✗ 미설정         │
│                                     │
│   [API Keys 설정하기]               │
└─────────────────────────────────────┘
```

### 설정 완료 후
```
┌─────────────────────────────────────┐
│        🔑                           │
│   API Keys 자동 설정                │
│                                     │
│   현재 상태:                        │
│   Kakao API:      ✓ 설정됨         │
│   VWorld API:     ✓ 설정됨         │
│   Data.go.kr API: ✓ 설정됨         │
│                                     │
│   ✅ API Keys가 성공적으로          │
│      설정되었습니다!                │
│                                     │
│   [주소 검색 테스트]                │
│   [메인 페이지로 이동]              │
└─────────────────────────────────────┘
```

---

## 🎯 핵심 URL 모음

| 이름 | URL | 용도 |
|------|-----|------|
| **API 키 설정** | https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/setup-api-keys.html | ⭐ **여기서 시작!** |
| 메인 서비스 | https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai | 주소 검색 & 분석 |
| PDF 다운로드 | https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/reports/ | 보고서 다운로드 |

---

## ❓ 왜 자꾸 실패하나요?

### 문제의 원인
1. **백엔드가 root 권한으로 실행 중**
   - 일반 사용자가 생성한 `.env` 파일을 읽지 못함
   - 환경 변수가 로드되지 않음

2. **SessionStorage는 브라우저마다 독립적**
   - 새 브라우저/시크릿 모드 = 새 SessionStorage
   - API 키가 다시 설정되어야 함

3. **세션 만료**
   - 브라우저를 닫으면 SessionStorage 삭제
   - 다음 방문 시 다시 설정 필요

### 영구 해결책 (백엔드 재시작 필요)
```bash
# 관리자 권한으로 백엔드 재시작
sudo systemctl restart zerosite-backend
# 또는
sudo kill <PID> && sudo uvicorn app.main:app --host 0.0.0.0 --port 49999
```

---

## 🔍 설정 확인 방법

### 브라우저 콘솔에서 확인
```javascript
// API 키 설정 여부 확인
const keys = sessionStorage.getItem('m1_api_keys');
console.log(keys ? JSON.parse(keys) : '미설정');

// 예상 결과:
// {
//   kakao: "1b172a21a17b8b51dd47884b45228483",
//   vworld: "781864DB-126D-3B14-A0EE-1FD1B1000534",
//   dataGoKr: "702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d"
// }
```

### 주소 검색 테스트
1. 주소 입력: `서울시 강남구`
2. 검색 버튼 클릭
3. **성공**: 실제 주소 10+ 개 표시
4. **실패**: "⚠️ MOCK DATA" 경고 표시

---

## 📞 추가 지원

### 여전히 안 될 때
1. **캐시 삭제**
   ```javascript
   sessionStorage.clear();
   localStorage.clear();
   location.reload();
   ```

2. **다른 브라우저 시도**
   - Chrome, Firefox, Edge 중 하나

3. **시크릿/프라이빗 모드**
   - Ctrl+Shift+N (Chrome)
   - Ctrl+Shift+P (Firefox)

4. **API 키 재설정**
   - 설정 페이지 다시 방문
   - "API Keys 설정하기" 다시 클릭

---

## ✅ 요약

### 가장 쉬운 방법
1. **이 페이지로 이동**: https://5173-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/setup-api-keys.html
2. **버튼 클릭**: "API Keys 설정하기"
3. **완료**: "메인 페이지로 이동"

**3분이면 끝!** 🚀

---

**작성**: 2025-01-04  
**상태**: ✅ **즉시 사용 가능**  
**커밋**: a0d4907
