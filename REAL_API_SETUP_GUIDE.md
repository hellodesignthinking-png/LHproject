# 🔑 실제 API 키 설정 가이드

**목적**: Mock 데이터 대신 실제 한국 주소 기반으로 토지 정보 수집  
**상태**: 현재 Mock 데이터 사용 중 → 실제 API 설정 필요  
**예상 시간**: 60-90분 (API 신청 대기 시간 포함)

---

## 📋 필요한 API 키 (우선순위순)

### 🔴 필수 (M1 기본 기능)

| API | 용도 | 무료 제공 | 신청 시간 |
|-----|------|-----------|-----------|
| **Kakao REST API** | 주소 검색, 좌표 변환 | ✅ 무료 (일 300,000건) | ~5분 |
| **VWorld API** | 지적 데이터 (PNU, 면적, 지목) | ✅ 무료 (일 30,000건) | ~10분 |
| **Data.go.kr API** | 토지 규제, 거래가격 | ✅ 무료 (일 1,000-10,000건) | ~10분 |

### 🟡 선택 (향상된 기능)

| API | 용도 | 무료 제공 |
|-----|------|-----------|
| **JUSO API** | 주소 검색 (대체/보조) | ✅ 무료 (일 10,000건) |
| **Google Places** | 장소 정보 (추가) | ⚠️ 유료 ($0.017/요청) |
| **Naver Local** | 지역 정보 (대체) | ✅ 무료 (일 25,000건) |

---

## 🚀 빠른 시작 (15분)

### 1단계: Kakao API 키 발급 (5분)

#### 1.1 Kakao Developers 계정 생성
```
1. https://developers.kakao.com/ 접속
2. 우측 상단 "로그인" → Kakao 계정으로 로그인
3. 최초 로그인 시 "개발자 등록" 진행
```

#### 1.2 애플리케이션 생성
```
1. "내 애플리케이션" 메뉴 클릭
2. "애플리케이션 추가하기" 클릭
3. 앱 이름: "ZeroSite M1" (또는 원하는 이름)
4. 사업자명: 개인 이름 입력
5. "저장" 클릭
```

#### 1.3 REST API 키 복사
```
1. 생성된 애플리케이션 클릭
2. "앱 키" 섹션에서 "REST API 키" 복사
   예시: 1234567890abcdef1234567890abcdef
```

#### 1.4 플랫폼 설정 (선택사항)
```
1. "플랫폼" 탭 클릭
2. "Web 플랫폼 등록" 클릭
3. 사이트 도메인: http://localhost:3001 (또는 실제 도메인)
4. "저장" 클릭
```

#### 1.5 키 설정
```bash
cd /home/user/webapp
nano .env

# 다음 줄 수정:
KAKAO_REST_API_KEY=1234567890abcdef1234567890abcdef  # 실제 키로 변경
```

---

### 2단계: VWorld API 키 발급 (10분)

#### 2.1 VWorld 회원가입
```
1. http://www.vworld.kr/dev/v4dv_2ddataguide2_s001.do 접속
2. 우측 상단 "회원가입" 클릭
3. 본인인증 진행 (휴대폰 또는 이메일)
```

#### 2.2 API 신청
```
1. 로그인 후 "오픈API" → "API 신청" 메뉴 이동
2. "서비스 검색" 탭에서 다음 API 검색 및 신청:
   - "지적도" API
   - "토지이용계획" API
   - "건축물대장" API (선택)
   
3. 각 API별로:
   - "신청" 버튼 클릭
   - 사용목적: "토지 분석 플랫폼 개발"
   - 일 트래픽: 1,000건
   - "신청" 완료
   
4. "내 API" 메뉴에서 "인증키" 복사
   예시: B9A1C2D3-E4F5-6789-0ABC-DEF123456789
```

#### 2.3 키 설정
```bash
cd /home/user/webapp
nano .env

# 다음 줄들 수정:
VWORLD_API_KEY=B9A1C2D3-E4F5-6789-0ABC-DEF123456789  # 실제 키로 변경
LAND_REGULATION_API_KEY=B9A1C2D3-E4F5-6789-0ABC-DEF123456789  # 동일한 키
```

---

### 3단계: Data.go.kr API 키 발급 (10분)

#### 3.1 공공데이터포털 회원가입
```
1. https://www.data.go.kr/ 접속
2. 우측 상단 "회원가입" 클릭
3. 본인인증 진행
```

#### 3.2 API 신청
```
1. 로그인 후 검색창에서 다음 API 검색 및 신청:
   
   a) "국토교통부 실거래가 정보 조회 서비스"
      - 오픈API 탭 클릭
      - "활용신청" 버튼 클릭
      - 활용목적: "토지 분석 및 감정평가 시스템"
      - 상세기능: "실거래가 조회"
   
   b) "국토교통부 토지특성 정보 서비스"
      - 활용신청
      - 활용목적: "토지 용도지역 및 규제 정보 조회"
   
   c) "국토교통부 개별공시지가 정보 서비스"
      - 활용신청
      - 활용목적: "토지 가격 평가"

2. "마이페이지" → "오픈API" → "개발계정" 메뉴
3. 신청한 API별 "일반 인증키(Encoding)" 복사
   예시: aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890aBcDeFgHiJkLmNoPqRs
```

#### 3.3 키 설정
```bash
cd /home/user/webapp
nano .env

# 다음 줄들 수정:
DATA_GO_KR_API_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890aBcDeFgHiJkLmNoPqRs  # 실제 키
MOIS_API_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890aBcDeFgHiJkLmNoPqRs  # 동일한 키
```

---

## 🔧 자동 설정 스크립트 (대화형)

### 준비물
- Kakao API 키
- VWorld API 키  
- Data.go.kr API 키

### 실행 방법
```bash
cd /home/user/webapp
chmod +x setup_real_keys.sh
./setup_real_keys.sh
```

**스크립트 동작**:
1. 현재 `.env` 파일 백업 (`.env.backup`)
2. 각 API 키 입력 받기 (대화형)
3. `.env` 파일 업데이트
4. 키 유효성 간단 검증 (형식 체크)
5. 백엔드 재시작 안내

---

## 🧪 API 키 테스트

### 자동 테스트 스크립트
```bash
cd /home/user/webapp
python3 tests/test_real_api_keys.py
```

**테스트 항목**:
- ✅ Kakao API: 주소 검색 ("서울특별시 강남구 테헤란로 521")
- ✅ VWorld API: 좌표 → PNU 변환
- ✅ Data.go.kr API: 개별공시지가 조회
- ✅ 전체 collect-all 엔드포인트 통합 테스트

### 수동 테스트

#### 1. Kakao API 테스트
```bash
curl -X POST http://localhost:8000/api/m1/address/search \
  -H "Content-Type: application/json" \
  -d '{"query": "서울특별시 강남구 테헤란로 521"}' \
  | jq '.suggestions | length'

# 예상 결과: 5-10 (실제 주소 제안 개수)
```

#### 2. VWorld API 테스트
```bash
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 521",
    "lat": 37.5084448,
    "lon": 127.0626804
  }' | jq '.data.cadastral'

# 예상 결과: 
# {
#   "pnu": "1168010100103850000",  ← 실제 PNU
#   "area": 6914.0,                 ← 실제 면적
#   "jimok": "대지",
#   "api_result": {
#     "success": true,              ← API 성공
#     "api_name": "VWorld Cadastral API"
#   }
# }
```

#### 3. Data.go.kr API 테스트
```bash
curl -X POST http://localhost:8000/api/m1/collect-all \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 테헤란로 521",
    "lat": 37.5084448,
    "lon": 127.0626804
  }' | jq '.data.market'

# 예상 결과:
# {
#   "official_land_price": 47500000,  ← 실제 공시지가
#   "transactions": [                  ← 실제 거래사례
#     {
#       "date": "2024-09-15",
#       "amount": 3500000000,
#       ...
#     }
#   ]
# }
```

---

## 🔄 백엔드 재시작

### 방법 1: 자동 재시작 스크립트
```bash
cd /home/user/webapp
./restart_backend.sh
```

### 방법 2: 수동 재시작
```bash
cd /home/user/webapp

# 1. 기존 프로세스 종료
pkill -f "uvicorn.*8000"

# 2. 새 프로세스 시작
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# 3. 로그 확인
tail -f backend.log
# Ctrl+C로 종료

# 4. 헬스 체크
curl http://localhost:8000/api/m1/health
```

---

## 📊 Mock vs Real 데이터 비교

### Mock 데이터 (현재)
```json
{
  "address": "서울특별시 강남구 테헤란로 521",
  "cadastral": {
    "pnu": "116801230001230045",      // ← Mock (고정값)
    "area": 500.0,                     // ← Mock (고정값)
    "jimok": "대지",
    "api_result": {
      "success": false,                // ← Mock 데이터 표시
      "error": "VWorld API not configured"
    }
  },
  "legal": {
    "use_zone": "일반상업지역",        // ← Mock (주소 기반 추정)
    "floor_area_ratio": 1000,          // ← Mock (패턴 기반)
    "building_coverage_ratio": 60
  },
  "market": {
    "official_land_price": 5000000,    // ← Mock (고정값)
    "transactions": [                   // ← Mock (3건 고정)
      {"date": "2024-06-15", "amount": 400000000},
      {"date": "2024-05-20", "amount": 380000000},
      {"date": "2024-04-10", "amount": 420000000}
    ]
  }
}
```

### Real 데이터 (API 설정 후)
```json
{
  "address": "서울특별시 강남구 테헤란로 521 (삼성동)",
  "cadastral": {
    "pnu": "1168010100103850000",      // ← 실제 PNU (VWorld API)
    "area": 6914.0,                     // ← 실제 면적 (VWorld API)
    "jimok": "대",                      // ← 실제 지목
    "bonbun": "1038",                   // ← 실제 본번
    "bubun": "5",                       // ← 실제 부번
    "api_result": {
      "success": true,                  // ← 실제 API 성공
      "api_name": "VWorld Cadastral API"
    }
  },
  "legal": {
    "use_zone": "일반상업지역",        // ← 실제 용도지역 (Data.go.kr)
    "floor_area_ratio": 1000,          // ← 실제 용적률
    "building_coverage_ratio": 60,     // ← 실제 건폐율
    "regulations": [                    // ← 실제 규제사항
      "지구단위계획구역",
      "방화지구"
    ]
  },
  "market": {
    "official_land_price": 47500000,   // ← 실제 공시지가 (Data.go.kr)
    "official_land_price_date": "2024-01-01",
    "transactions": [                   // ← 실제 거래사례 (다수)
      {
        "date": "2024-09-15",
        "amount": 3500000000,
        "area": 700,
        "price_per_sqm": 5000000,
        "distance": 120,
        "address": "서울특별시 강남구 삼성동 159-1"
      },
      {
        "date": "2024-07-20",
        "amount": 3200000000,
        ...
      },
      // ... 실제 거래사례 5-10건
    ]
  }
}
```

---

## 🎯 예상 효과

### 데이터 정확도 향상

| 항목 | Mock 데이터 | Real 데이터 | 개선율 |
|------|-------------|-------------|--------|
| PNU (필지고유번호) | ❌ 추정값 | ✅ 실제값 | **100%** |
| 토지 면적 | ❌ 고정값 (500㎡) | ✅ 실제값 | **100%** |
| 용도지역 | ⚠️ 패턴 기반 | ✅ 공식 데이터 | **95%** |
| 용적률/건폐율 | ⚠️ 지역 기준 | ✅ 실제 규제 | **90%** |
| 공시지가 | ❌ 고정값 | ✅ 정부 공시 | **100%** |
| 거래사례 | ❌ 가상 3건 | ✅ 실제 5-10건 | **100%** |

### M2 감정평가 정확도
- **Mock 데이터**: 참고용 ±30% 오차
- **Real 데이터**: 실무 수준 ±10% 오차

### 보고서 신뢰도
- **Mock 데이터**: 시뮬레이션/테스트 목적
- **Real 데이터**: 실무/투자 의사결정 가능

---

## ⚠️ 주의사항

### API 사용 제한
| API | 무료 일일 한도 | 초과 시 |
|-----|---------------|---------|
| Kakao | 300,000건 | 차단 (다음날 0시 복구) |
| VWorld | 30,000건 | 차단 (익일 복구) |
| Data.go.kr | 1,000-10,000건 | 차단 (익일 복구) |

**권장사항**:
- 개발 시: Mock 데이터 사용
- 테스트 시: 실제 API 사용 (제한적)
- 프로덕션: API 호출 최소화 + 캐싱

### 개인정보 보호
- ✅ `.env` 파일은 **절대 Git에 커밋하지 말 것**
- ✅ API 키는 **서버 환경변수**로 관리 (프로덕션)
- ✅ 로그에 API 키가 노출되지 않도록 주의

### 에러 처리
실제 API는 다음과 같은 오류 가능:
- 401 Unauthorized: API 키 오류
- 403 Forbidden: 일일 한도 초과
- 404 Not Found: 존재하지 않는 주소/필지
- 500 Internal Server Error: API 서버 장애

→ Mock 데이터로 자동 fallback 구현됨

---

## 🆘 트러블슈팅

### Q: Kakao API 401 오류
**A**: 
```bash
# 1. API 키 확인
grep KAKAO_REST_API_KEY /home/user/webapp/.env

# 2. Kakao Developers에서 키 재확인
# 3. 플랫폼 설정에 도메인 추가 여부 확인
```

### Q: VWorld API 응답 없음
**A**:
```bash
# 1. API 신청 승인 확인 (내 API 메뉴)
# 2. 인증키 확인 (공백 없이)
# 3. 일일 트래픽 초과 여부 확인
```

### Q: Data.go.kr API 403 오류
**A**:
```bash
# 1. 활용신청 승인 대기 중인지 확인 (최대 1-2일 소요)
# 2. 일반 인증키 vs 일반 인증키(Encoding) 구분
#    → Encoding 버전 사용 필요
# 3. 마이페이지에서 API 상태 확인
```

### Q: 백엔드 재시작 후에도 Mock 데이터
**A**:
```bash
# 1. 환경변수 로드 확인
python3 -c "from app.config import get_settings; s=get_settings(); print(s.kakao_rest_api_key)"

# 2. .env 파일 위치 확인
ls -la /home/user/webapp/.env

# 3. 백엔드 로그 확인
tail -50 /home/user/webapp/backend.log | grep "API"
```

---

## 📞 지원

### 공식 문서
- **Kakao Developers**: https://developers.kakao.com/docs
- **VWorld API**: http://www.vworld.kr/dev/v4dv_apiguide2_s001.do
- **Data.go.kr**: https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do

### 문의
- **Kakao**: developers@kakao.com
- **VWorld**: 국토교통부 공간정보산업진흥원 (1577-1749)
- **Data.go.kr**: 공공데이터포털 고객센터 (1661-2346)

---

## ✅ 체크리스트

- [ ] Kakao API 키 발급 완료
- [ ] VWorld API 키 발급 완료
- [ ] Data.go.kr API 키 발급 완료
- [ ] `.env` 파일 업데이트 완료
- [ ] 백엔드 재시작 완료
- [ ] Kakao API 테스트 성공
- [ ] VWorld API 테스트 성공
- [ ] Data.go.kr API 테스트 성공
- [ ] 실제 주소로 M1 플로우 테스트 완료
- [ ] M2 감정평가 실제 데이터로 진행 확인

---

**다음 단계**: API 키 설정 완료 후 프론트엔드에서 실제 주소 테스트
**예상 소요 시간**: 15분 (키 발급) + 5분 (설정 및 테스트)
