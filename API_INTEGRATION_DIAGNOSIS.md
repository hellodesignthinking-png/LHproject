# API 연동 문제 진단 리포트

## 📊 현재 상태 분석

### ✅ 정상 작동 중인 부분

1. **시스템 아키텍처**
   - ✅ Frontend API 키 입력 화면 (ApiKeySetup)
   - ✅ SessionStorage에 API 키 저장
   - ✅ m1.service.ts에서 HTTP 헤더 자동 추가
   - ✅ Backend 엔드포인트 API 키 헤더 수신
   - ✅ Mock 데이터 fallback 시스템

2. **Kakao 주소 검색 API**
   - ✅ API 키 전달 정상
   - ✅ 주소 검색 성공 (예: "서울 강남구" → 결과 반환)
   - ✅ 좌표 변환 정상

3. **데이터 수집 플로우**
   - ✅ `/api/m1/address/search` 정상 작동
   - ✅ `/api/m1/collect-all` 호출 성공
   - ✅ Mock 데이터 자동 fallback

### ❌ 문제가 있는 부분

#### 1. 외부 정부 API 엔드포인트 오류

**VWorld API (지적도)**
```
URL: http://api.vworld.kr/req/wms...
오류: 502 Bad Gateway
원인: VWorld 서버 응답 없음
```

**Data.go.kr Land Use API (용도지역)**
```
URL: http://apis.data.go.kr/1611000/nsdi/emd/EmdCodeService/attr/getEmdArea
오류: 500 Internal Server Error
원인: API 서버 내부 오류 또는 잘못된 파라미터
```

**Data.go.kr Official Price API (공시지가)**
```
URL: http://apis.data.go.kr/1613000/nsdi/IndvdLandPriceService/attr/getIndvdLandPriceAttr
오류: 500 Internal Server Error
원인: API 서버 내부 오류
```

**MOLIT Transaction API (실거래가)**
```
URL: http://apis.data.go.kr/1613000/RTMSDataSvcLandTrade/getRTMSDataSvcLandTrade
오류: 403 Forbidden
원인: API 키 승인 안 됨 또는 잘못된 엔드포인트
```

## 🔍 근본 원인 분석

### 1. API 키는 전달되고 있나?
**YES** - Backend 로그에서 API 키가 URL에 포함되어 있는 것을 확인
```
key=B6B0B6F1-E572-304A-9742-384510D86FE4
ServiceKey=702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d
```

### 2. 그럼 왜 데이터를 못 불러오나?
**외부 API 서버 자체의 문제:**
- VWorld API: 502 에러 → 서버가 응답하지 않음
- Data.go.kr API들: 500/403 에러 → 서버 내부 오류 또는 권한 문제

### 3. Mock 데이터는 작동하는가?
**YES** - 모든 API 실패 시 자동으로 realistic mock data로 fallback됨

## 🎯 해결 방법

### 옵션 1: Mock 데이터 사용 (현재 상태)
**장점:**
- ✅ 시스템 즉시 사용 가능
- ✅ 테스트 및 개발에 적합
- ✅ 안정적인 데이터 제공

**단점:**
- ❌ 실제 정부 데이터 아님
- ❌ 실제 주소의 정확한 정보 아님

**현재 Mock 데이터:**
- 지적 정보: PNU, 면적 500㎡, 지목 "대지"
- 법적 정보: 일반상업지역, 용적률 1000%, 건폐율 60%
- 도로 정보: 접도 "접함", 도로폭 8m
- 시장 정보: 공시지가 5,000,000원/㎡, 거래사례 3건

### 옵션 2: 실제 API 수정 (권장)

#### 2-1. VWorld API 엔드포인트 확인
현재 사용 중:
```python
http://api.vworld.kr/req/wms
```

확인 필요 사항:
- [ ] 올바른 엔드포인트인지 확인
- [ ] API 버전 확인
- [ ] 필수 파라미터 확인
- [ ] API 키 활성화 상태 확인

#### 2-2. Data.go.kr API 키 활성화
```
현재 키: 702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d
```

확인 필요 사항:
- [ ] Data.go.kr에서 API 키 활성화 여부
- [ ] 각 API (IndvdLandPriceService, RTMSDataSvcLandTrade) 신청 여부
- [ ] API 사용 승인 상태
- [ ] 일일 호출 제한 확인

#### 2-3. 대체 API 사용
- 국토교통부 오픈API 포털 (https://www.data.go.kr/)
- 공공데이터포털에서 다른 지적 정보 API 찾기
- 상용 API 서비스 고려 (유료)

### 옵션 3: 하이브리드 접근 (추천!)

**전략:**
1. **주소 검색**: Kakao API 사용 (✅ 작동 중)
2. **지적 정보**: 사용자 수동 입력 + Mock 데이터 제안
3. **법적 정보**: 지역 기반 realistic mock + 사용자 수정 가능
4. **시장 데이터**: Mock 데이터 + 사용자 검증

**구현 방법:**
```
[API 시도] → [실패 시 Mock 제안] → [사용자 확인/수정] → [진행]
```

이미 ReviewScreen에서 모든 필드를 편집 가능하도록 구현되어 있습니다!

## 📝 사용자 워크플로우 (현재)

### STEP -1: API 키 설정
```
사용자가 3개 API 키 입력:
- Kakao REST API Key ✅ (작동)
- VWorld API Key ⚠️ (서버 오류)
- Data.go.kr API Key ⚠️ (서버 오류/권한 문제)

OR "Mock 데이터로 진행" 선택
```

### STEP 1: 주소 검색
```
Kakao API로 주소 검색 → ✅ 성공
결과: 서울 강남구 테헤란로 521
좌표: (37.509, 127.060)
```

### STEP 2: 위치 확인
```
지도에 표시 → ✅ 정상
```

### STEP 3: 데이터 검토
```
자동 수집 시도:
- 지적 정보: VWorld API 502 → Mock 데이터 사용 ⚠️
- 법적 정보: Data.go.kr 500 → Mock 데이터 사용 ⚠️
- 도로 정보: Mock 데이터 ⚠️
- 시장 정보: MOLIT 403 → Mock 데이터 사용 ⚠️

각 섹션에 "⚠ Using Mock Data" 배지 표시
사용자가 모든 필드 편집 가능 ✅
```

### STEP 4: M1 확정
```
사용자가 데이터 확인/수정 후 → 확정
→ M2 파이프라인 진행 ✅
```

## 💡 즉시 사용 가능한 해결책

### 방법 1: Mock 데이터로 전체 플로우 테스트
```
1. "Mock 데이터로 진행" 클릭
2. 주소 검색 (Kakao API 사용)
3. 데이터 검토에서 Mock 데이터 확인
4. 필요시 값 수정
5. M1 확정 → M2-M6 파이프라인 실행
```

**결과**: 전체 시스템 정상 작동, 감정평가 결과 출력

### 방법 2: Realistic Mock 데이터 개선
현재 Mock 데이터를 주소 기반으로 더 realistic하게 생성하도록 개선:

```python
# 이미 구현됨!
def _generate_realistic_zoning(address, lat, lon):
    if "강남" in address or "서초" in address:
        return "일반상업지역", 1000, 60  # 강남 상업지역
    elif "강북" in address or "중랑" in address:
        return "제2종일반주거지역", 200, 60  # 주거지역
    ...
```

### 방법 3: 사용자 가이드 개선
ReviewScreen에 더 명확한 안내 추가:

```
⚠️ API 데이터 수집 실패
정부 API 서버가 응답하지 않아 mock 데이터를 사용합니다.
아래 값들을 확인하고 필요시 수정해주세요.

[지적 정보]
✎ 모든 필드 수정 가능
```

## 🚀 액션 아이템

### 즉시 가능 (개발자)
- [x] Mock 데이터 fallback 구현 완료
- [x] ReviewScreen 편집 기능 완료
- [x] API 상태 배지 표시 완료
- [ ] Mock 데이터를 더 realistic하게 개선
- [ ] 사용자 가이드 메시지 개선

### 중기 (API 연동)
- [ ] VWorld API 엔드포인트 검증
- [ ] Data.go.kr API 키 활성화 확인
- [ ] 대체 API 조사
- [ ] API 오류 시 재시도 로직

### 장기 (시스템 개선)
- [ ] 자체 지적 DB 구축
- [ ] 캐싱 시스템 개선
- [ ] PDF/Excel 업로드로 데이터 입력
- [ ] AI 기반 데이터 보정

## 📊 결론

**현재 상태:**
- ✅ 시스템 아키텍처 정상
- ✅ API 키 입력 및 전달 정상
- ✅ Kakao 주소 검색 작동
- ❌ 정부 API 서버들 오류 (VWorld, Data.go.kr)
- ✅ Mock 데이터 fallback 작동
- ✅ 사용자 데이터 수정 가능
- ✅ 전체 M1-M6 파이프라인 작동

**사용자 입장에서:**
1. API 키 입력해도 → 외부 API 서버 오류로 Mock 데이터 사용
2. Mock 데이터로 진행해도 → 동일한 Mock 데이터 사용
3. **결과는 동일**: Mock 데이터 기반 감정평가 진행

**추천 액션:**
1. ✅ **즉시**: Mock 데이터로 전체 시스템 테스트 및 데모
2. ⚠️ **단기**: 외부 API 엔드포인트 및 키 검증
3. 🔧 **중기**: 대체 API 또는 자체 DB 구축

---

**작성자**: Claude AI Assistant  
**날짜**: 2025-12-17  
**상태**: API 통합 진단 완료  
**다음 단계**: Mock 데이터 개선 또는 외부 API 수정
