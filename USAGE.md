# LH 토지진단 시스템 사용 가이드

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 설정

`.env` 파일이 이미 생성되어 있으며, API 키가 설정되어 있습니다.

```env
KAKAO_REST_API_KEY=1b172a21a17b8b51dd47884b45228483
LAND_REGULATION_API_KEY=702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d
MOIS_API_KEY=702ee131547fa817de152355d87249805da836374a7ffefee1c511897353807d
```

### 3. 서버 실행

```bash
# 개발 서버 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 다음 URL에서 접근 가능합니다:
- API 문서: http://localhost:8000/docs
- 대체 문서: http://localhost:8000/redoc

---

## 📖 사용 방법

### 방법 1: API 직접 호출

#### cURL 사용

```bash
curl -X POST "http://localhost:8000/api/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 679",
    "land_area": 500,
    "unit_type": "청년형"
  }'
```

#### Python requests 사용

```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze-land",
    json={
        "address": "서울특별시 강남구 역삼동 679",
        "land_area": 500,
        "unit_type": "청년형"
    }
)

result = response.json()
print(result)
```

### 방법 2: 예제 스크립트 실행

#### 간단한 API 테스트

```bash
python test_api_simple.py
```

이 스크립트는 다음을 테스트합니다:
- ✅ 카카오맵 API (주소→좌표, 주변시설)
- ✅ 토지규제 API (용도지역, 개발제한)
- ✅ 행정안전부 API (인구통계)

#### 전체 분석 예제

```bash
python example_usage.py
```

실제 토지를 분석하여 다음을 출력합니다:
- 📍 좌표 및 용도지역 정보
- 🏗️ 건축 규모 산정 (세대수, 층수, 주차대수)
- ⚠️ 리스크 요인 분석
- 👥 인구통계 분석
- 📈 수요 점수 및 적합성 판단

---

## 🔍 API 엔드포인트

### 1. 토지 분석 API

**POST** `/api/analyze-land`

**요청 본문:**

```json
{
  "address": "서울특별시 강남구 역삼동 679",
  "land_area": 500.0,
  "unit_type": "청년형"
}
```

**세대 유형 옵션:**
- `청년형` - 청년 1인 가구용 (30㎡)
- `신혼부부형` - 신혼부부 2-3인 (50㎡)
- `고령자형` - 고령자 1-2인 (40㎡)

**응답 예시:**

```json
{
  "status": "success",
  "analysis_id": "abc12345",
  "address": "서울특별시 강남구 역삼동 679",
  "land_area": 500.0,
  "unit_type": "청년형",
  "coordinates": {
    "latitude": 37.5012,
    "longitude": 127.0396
  },
  "zone_info": {
    "zone_type": "제2종일반주거지역",
    "building_coverage_ratio": 60.0,
    "floor_area_ratio": 200.0
  },
  "building_capacity": {
    "building_area": 300.0,
    "total_floor_area": 1000.0,
    "floors": 7,
    "units": 28,
    "parking_spaces": 14
  },
  "risk_factors": [],
  "demographic_info": {
    "total_population": 500000,
    "youth_population": 150000,
    "youth_ratio": 30.0,
    "single_households": 155000,
    "single_household_ratio": 31.0
  },
  "demand_analysis": {
    "demand_score": 85.0,
    "key_factors": [
      "청년 인구 비중 30% (높음)",
      "지하철역 450m (도보 10분 이내)"
    ],
    "recommendation": "적합"
  },
  "summary": {
    "is_eligible": true,
    "estimated_units": 28,
    "demand_score": 85.0,
    "recommendation": "적합 - LH 매입 가능성 높음",
    "risk_count": 0
  }
}
```

### 2. 헬스 체크

**GET** `/health`

시스템 상태 및 API 설정 확인

### 3. API 테스트 엔드포인트

개별 API 서비스를 테스트할 수 있는 엔드포인트:

- **POST** `/api/test-kakao?address=서울특별시 강남구 역삼동`
- **POST** `/api/test-land-regulation?lat=37.5&lon=127.0`
- **POST** `/api/test-mois?address=서울특별시 강남구`

---

## 📊 분석 프로세스

시스템은 다음 6단계로 토지를 분석합니다:

### 1단계: 주소 → 좌표 변환
- 카카오맵 API를 사용하여 주소를 위경도 좌표로 변환

### 2단계: 외부 API 데이터 수집 (병렬)
- 용도지역 정보 (토지규제 API)
- 개발 제한사항 (토지규제 API)
- 유해시설 검색 (카카오 API)
- 접근성 분석 (카카오 API)
- 인구통계 (행정안전부 API)

### 3단계: 리스크 요인 분석
- 법적제한 (개발제한구역, 군사시설 등)
- 유해시설 (주유소, 공장 등 500m 이내)
- 접근성 (지하철역 거리, 대중교통)

### 4단계: 건축 규모 산정
- 건폐율/용적률 기반 건축면적 계산
- 층수 및 연면적 산정
- 세대수 계산 (세대 유형별 면적 기준)
- 주차대수 산정 (세대 유형별 기준)

### 5단계: 입지 및 수요 분석
- 인구통계 점수 (청년인구 비중, 1인가구)
- 접근성 점수 (대중교통, 편의시설)
- 시장 규모 점수 (타겟 인구)
- 종합 수요 점수 계산 (100점 만점)

### 6단계: 종합 적합성 판단
- LH 매입 적격 여부
- 예상 세대수
- 수요 점수
- 최종 추천 (적합/검토필요/부적합)

---

## 🛠️ 개발자 가이드

### 프로젝트 구조

```
webapp/
├── app/
│   ├── main.py                 # FastAPI 메인 앱
│   ├── config.py              # 설정 관리
│   ├── schemas.py             # 데이터 모델
│   ├── services/              # 외부 API 서비스
│   │   ├── kakao_service.py
│   │   ├── land_regulation_service.py
│   │   ├── mois_service.py
│   │   └── analysis_engine.py # 통합 분석 엔진
│   └── utils/
│       └── calculations.py    # 계산 유틸리티
├── tests/                     # 테스트 코드
├── output/                    # 생성된 보고서
├── .env                       # 환경 변수 (API 키)
├── requirements.txt           # Python 의존성
└── README.md                  # 프로젝트 설명
```

### 새로운 API 추가하기

1. `app/services/` 에 새로운 서비스 파일 생성
2. 비동기 메서드로 API 호출 구현
3. `analysis_engine.py`에서 새 서비스 통합
4. `schemas.py`에 응답 모델 추가

### 계산 로직 수정하기

`app/utils/calculations.py`의 `BuildingCalculator` 클래스를 수정하여:
- 세대 면적 기준 변경
- 주차대수 산정 기준 조정
- 층수 제한 규칙 업데이트

---

## 🐳 Docker 실행 (선택사항)

### Docker Compose로 전체 스택 실행

```bash
# 컨테이너 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f api

# 종료
docker-compose down
```

포함된 서비스:
- FastAPI 앱 (포트 8000)
- PostgreSQL + PostGIS (포트 5432)
- Redis (포트 6379)
- Celery Worker

---

## 🧪 테스트

### 단위 테스트 실행

```bash
pytest tests/
```

### 커버리지 측정

```bash
pytest --cov=app tests/
```

---

## 📝 다음 단계

현재 구현된 기능:
- ✅ 3개 외부 API 통합 (카카오, 토지규제, 행정안전부)
- ✅ 건축 규모 자동 계산
- ✅ 리스크 요인 분석
- ✅ 수요 분석 및 적합성 판단
- ✅ FastAPI 서버 및 API 엔드포인트

추가 개발 예정:
- [ ] OpenAI/Claude API 연동 (AI 보고서 생성)
- [ ] PDF 보고서 자동 생성
- [ ] 데이터베이스 연동 (분석 이력 저장)
- [ ] 프론트엔드 대시보드
- [ ] 배치 분석 기능

---

## 🔧 문제 해결

### API 키 오류

```
❌ 주소 변환 실패: Unauthorized
```

→ `.env` 파일의 API 키를 확인하세요.

### 의존성 설치 실패

```bash
# 시스템 라이브러리가 필요한 경우 (Ubuntu/Debian)
sudo apt-get install libgeos-dev libproj-dev gdal-bin

# macOS
brew install geos proj gdal
```

### 포트 충돌

```
ERROR: Address already in use
```

→ 다른 포트로 실행: `uvicorn app.main:app --port 8001`

---

## 📞 지원

문제가 발생하면:
1. 로그 확인: 서버 터미널 출력
2. API 문서 확인: http://localhost:8000/docs
3. 예제 스크립트 실행: `python test_api_simple.py`

---

**버전:** 1.0.0  
**최종 업데이트:** 2024-11-09
