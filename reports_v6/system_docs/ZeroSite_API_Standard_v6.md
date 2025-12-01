# ZeroSite v6.0 API 통합 표준 문서
## API Integration Standard Document

**버전:** v6.0  
**작성일:** 2025-12-01  
**작성자:** ZeroSite System Architecture Team  
**분류:** 사내 기술문서 (Confidential)

---

## 📋 문서 개요

본 문서는 ZeroSite Land Engine v6.0이 연동하는 모든 외부 API의 표준, 인증 방식, 데이터 포맷, 에러 처리 방법을 정의합니다.

---

## 🗺️ 1. Kakao Map API

### 용도
- 주소 → 좌표 변환 (Geocoding)
- 좌표 → 주소 변환 (Reverse Geocoding)
- 장소 검색 (교통, 편의시설)

### 인증
```python
headers = {
    "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
}
```

### Endpoints

#### 1.1 주소 검색 (Address Search)
```
GET https://dapi.kakao.com/v2/local/search/address.json
```

**Parameters:**
- `query`: 주소 문자열 (예: "서울특별시 중구 세종대로 110")
- `analyze_type`: `similar` | `exact`

**Response:**
```json
{
  "documents": [{
    "address_name": "서울 중구 세종대로 110",
    "x": "126.978013429741",
    "y": "37.566535177648",
    "address": {
      "region_1depth_name": "서울",
      "region_2depth_name": "중구",
      "region_3depth_name": "세종로"
    }
  }]
}
```

#### 1.2 카테고리 검색 (Category Search)
```
GET https://dapi.kakao.com/v2/local/search/category.json
```

**Parameters:**
- `category_group_code`: `MT1` (대형마트), `HP8` (병원), `PK6` (주차장)
- `x`, `y`: 중심 좌표
- `radius`: 검색 반경 (meter)

**ZeroSite 활용 예시:**
```python
# 지하철역 검색
response = requests.get(
    "https://dapi.kakao.com/v2/local/search/keyword.json",
    headers={"Authorization": f"KakaoAK {API_KEY}"},
    params={
        "query": "지하철역",
        "x": 126.9780,
        "y": 37.5665,
        "radius": 1000
    }
)
```

### Rate Limit
- 무료: 300 req/day
- 유료: 10,000 req/day

---

## 🏢 2. 건축물대장 API (국토교통부)

### 용도
- 건축물 기본 정보 조회
- 용도지역, 건폐율, 용적률

### 인증
```
Service Key (URL 인코딩 필요)
```

### Endpoints

#### 2.1 건축물대장 기본정보 조회
```
GET http://apis.data.go.kr/1613000/BldRgstService_v2/getBrTitleInfo
```

**Parameters:**
- `sigunguCd`: 시군구코드 (5자리)
- `bjdongCd`: 법정동코드 (5자리)
- `bun`: 번
- `ji`: 지
- `ServiceKey`: 인증키

**Response:**
```xml
<response>
  <body>
    <items>
      <item>
        <archArea>987.65</archArea> <!-- 건축면적 -->
        <bcRat>60.0</bcRat> <!-- 건폐율 -->
        <vlRat>200.0</vlRat> <!-- 용적률 -->
        <mainPurpsCdNm>공동주택</mainPurpsCdNm>
      </item>
    </items>
  </body>
</response>
```

### Rate Limit
- 1,000 req/day (일반)
- 10,000 req/day (활용신청 후)

---

## 🌍 3. VWorld API (국토지리정보원)

### 용도
- 지적도 조회
- 토지 용도지역 확인
- 3D 건물 데이터

### 인증
```
API Key (URL Parameter)
```

### Endpoints

#### 3.1 지적도 WMS 서비스
```
GET http://api.vworld.kr/req/wms
```

**Parameters:**
- `SERVICE`: WMS
- `REQUEST`: GetMap
- `LAYERS`: `lp_pa_cbnd_bubun` (지적도)
- `CRS`: EPSG:4326
- `BBOX`: `{minx},{miny},{maxx},{maxy}`
- `key`: API Key

#### 3.2 토지이용계획 확인
```
GET http://api.vworld.kr/req/data
```

**Parameters:**
- `service`: data
- `request`: GetFeature
- `data`: LP_PA_CBND_BUBUN
- `geomFilter`: POINT(126.978 37.566)
- `key`: API Key

**Response:**
```json
{
  "response": {
    "result": {
      "featureCollection": {
        "features": [{
          "properties": {
            "pnu": "1114010100100010000",
            "jibun": "110",
            "jimok_nm": "대",
            "area": 850.5
          }
        }]
      }
    }
  }
}
```

---

## 📐 4. 토지이용규제 정보서비스 (국토교통부)

### 용도
- 용도지역지구 조회
- 개발행위허가 제한 확인

### Endpoints

#### 4.1 토지이용계획확인서 정보
```
GET http://apis.data.go.kr/1611000/nsdi/LandUseService/attr/getLandUseAttr
```

**Parameters:**
- `pnu`: 필지 고유번호 (19자리)
- `ServiceKey`: 인증키

**Response:**
```xml
<response>
  <body>
    <items>
      <item>
        <useAreaNm>제2종일반주거지역</useAreaNm>
        <prposAreaNm>-</prposAreaNm>
      </item>
    </items>
  </body>
</response>
```

---

## 🏛️ 5. 행정구역 API (행정안전부)

### 용도
- 법정동/행정동 코드 변환
- 시군구 코드 조회

### Endpoints

#### 5.1 법정동코드 조회
```
GET http://apis.data.go.kr/1741000/StanReginCd/getStanReginCdList
```

**Parameters:**
- `locatadd_nm`: 지역명 (예: "서울특별시 중구")
- `ServiceKey`: 인증키

---

## 🌤️ 6. Open-METEO Weather API

### 용도
- 기상 데이터 (일조, 바람)
- Geo Optimizer v2.0 환경 분석

### Endpoints

#### 6.1 Historical Weather Data
```
GET https://archive-api.open-meteo.com/v1/archive
```

**Parameters:**
- `latitude`: 37.5665
- `longitude`: 126.9780
- `start_date`: 2024-01-01
- `end_date`: 2024-12-31
- `daily`: sunshine_duration, windspeed_10m_max, wind_direction_10m_dominant

**Response:**
```json
{
  "latitude": 37.5,
  "longitude": 127.0,
  "daily": {
    "time": ["2024-01-01", "2024-01-02"],
    "sunshine_duration": [5.2, 6.1],
    "windspeed_10m_max": [12.5, 8.3],
    "wind_direction_10m_dominant": [225, 180]
  }
}
```

**ZeroSite 활용:**
- 동지 일조시간 계산
- 주풍향 분석 (여름/겨울)

---

## 📊 7. KOSIS (통계청 국가통계포털)

### 용도
- 인구 통계 (청년/신혼/고령자)
- 가구 특성 (1인 가구, 소득)

### Endpoints

#### 7.1 인구총조사 API
```
GET https://kosis.kr/openapi/Param/statisticsParameterData.do
```

**Parameters:**
- `method`: getList
- `apiKey`: 인증키
- `itmId`: 항목ID
- `objL1`: 시도
- `objL2`: 시군구

**ZeroSite 활용 예시:**
```python
# 청년 인구 비율 조회
params = {
    "method": "getList",
    "apiKey": KOSIS_API_KEY,
    "itmId": "T1",  # 인구수
    "objL1": "11000",  # 서울
    "objL2": "11140",  # 중구
    "format": "json",
    "jsonVD": "Y"
}
```

---

## 🏪 8. 소상공인시장진흥공단 상권정보 API

### 용도
- 상권 분석 데이터
- 유동인구, 매출 정보

### Endpoints

#### 8.1 상권정보 조회
```
GET http://apis.data.go.kr/B553077/api/open/sdsc2/storeZoneOne
```

**Parameters:**
- `key`: 인증키
- `ServiceKey`: 서비스키
- `pageNo`: 페이지 번호
- `numOfRows`: 10

---

## 🏦 9. KB국민은행 부동산 시세 API

### 용도
- 실거래가 정보
- 토지 시세 추정

### Endpoints

#### 9.1 아파트 실거래가 조회
```
GET https://api.kbland.kr/land-price/price/real-transaction
```

**Parameters:**
- `lawdCd`: 법정동코드
- `dealYmd`: 거래연월 (YYYYMM)

---

## 🔄 API 호출 표준 프로세스

### 1. Retry 로직
```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_api(url, headers, params):
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    return response.json()
```

### 2. Circuit Breaker
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
def call_external_api(endpoint):
    return requests.get(endpoint)
```

### 3. 캐싱 전략
```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## ⚠️ 에러 처리 표준

### HTTP Status Code 매핑

| Status | 의미 | ZeroSite 대응 |
|--------|------|---------------|
| 200 | 성공 | 정상 처리 |
| 400 | Bad Request | 파라미터 검증 실패 → 로그 기록 |
| 401 | Unauthorized | API Key 갱신 필요 → 알림 |
| 429 | Too Many Requests | Rate Limit 초과 → 대기 후 재시도 |
| 500 | Internal Server Error | 외부 API 장애 → Fallback 데이터 사용 |

### Fallback 전략
```python
def get_traffic_score_with_fallback(lat, lng):
    try:
        # Primary: Kakao API
        return call_kakao_api(lat, lng)
    except Exception as e:
        log.warning(f"Kakao API failed: {e}")
        try:
            # Fallback 1: VWorld API
            return call_vworld_api(lat, lng)
        except Exception as e2:
            log.error(f"VWorld API also failed: {e2}")
            # Fallback 2: 캐시 데이터
            return get_cached_score(lat, lng)
```

---

## 📊 API 모니터링 지표

### 수집 항목
1. **응답 시간** (Response Time): p50, p95, p99
2. **성공률** (Success Rate): 200 OK / Total Requests
3. **에러율** (Error Rate): 4xx, 5xx / Total Requests
4. **Rate Limit 사용률**: Current / Max

### Grafana Dashboard 예시
```
Panel 1: API Response Time (Line Chart)
- Kakao Map: 평균 250ms
- VWorld: 평균 800ms
- KOSIS: 평균 1200ms

Panel 2: API Success Rate (Gauge)
- Kakao: 99.5%
- 건축물대장: 97.2%
- 토지이용규제: 95.8%
```

---

## 🔐 보안 지침

### 1. API Key 관리
```python
# ❌ 잘못된 예시
api_key = "1234567890abcdef"

# ✅ 올바른 예시
import os
api_key = os.environ.get("KAKAO_API_KEY")
```

### 2. Secret 암호화
- AWS Secrets Manager
- HashiCorp Vault
- GitHub Secrets

---

## 📚 참고 자료

| API | 공식 문서 URL |
|-----|---------------|
| Kakao Map | https://developers.kakao.com/docs/latest/ko/local/dev-guide |
| VWorld | https://www.vworld.kr/dev/v4dv_2ddataguide2_s001.do |
| 건축물대장 | https://www.data.go.kr/data/15044713/openapi.do |
| Open-METEO | https://open-meteo.com/en/docs |
| KOSIS | https://kosis.kr/openapi/index/index.jsp |

---

**문서 버전:** 1.0  
**최종 업데이트:** 2025-12-01  
**다음 리뷰:** 2025-03-01

**© 2025 ZeroSite. All Rights Reserved.**
