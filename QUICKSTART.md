# 🚀 빠른 시작 가이드

## 5분 만에 시작하기

### 1단계: 서버 실행 (30초)

```bash
# 방법 1: 스크립트 사용
./start_server.sh

# 방법 2: 직접 실행
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**서버 실행 확인:**
```
🚀 LH 토지진단 시스템 시작
📍 환경: 개발
🔑 API Keys 로드됨
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

### 2단계: API 테스트 (1분)

#### 웹 브라우저로 확인
1. http://localhost:8000/docs 접속
2. "POST /api/analyze-land" 클릭
3. "Try it out" 버튼 클릭
4. 다음 JSON 입력:

```json
{
  "address": "서울특별시 강남구 역삼동 679",
  "land_area": 500,
  "unit_type": "청년형"
}
```

5. "Execute" 클릭
6. 결과 확인!

#### 또는 cURL 사용

```bash
curl -X POST "http://localhost:8000/api/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 강남구 역삼동 679",
    "land_area": 500,
    "unit_type": "청년형"
  }'
```

---

### 3단계: Python으로 사용하기 (2분)

#### 간단한 API 테스트

```bash
python test_api_simple.py
```

**출력 예시:**
```
🗺️  카카오맵 API 테스트
✅ 좌표 변환 성공
   위도: 37.5020942117804
   경도: 127.036798241165
📊 접근성 점수: 80/100
🚇 인근 지하철역: 역삼역 2호선 (160m)
```

#### 전체 분석 예제

```bash
python example_usage.py
```

**출력 예시:**
```
🏢 LH 신축매입임대 토지진단 시스템
======================================

📊 분석 결과 요약
✅ 1. 기본 정보
   용도지역: 제2종일반주거지역
   건폐율: 60.0%
   용적률: 200.0%

🏗️  2. 건축 규모 산정
   세대수: 34세대
   층수: 4층
   주차대수: 17대

📈 5. 입지 및 수요 분석
   수요 점수: 78.0/100
   적합성 판단: 적합

🎯 종합 판단
💡 최종 추천: 부적합 - 매입 제외 대상
   (유해시설 리스크로 인해 부적격)
```

---

### 4단계: 다른 주소로 테스트하기

#### Python 코드 예제

```python
import requests

# API 엔드포인트
url = "http://localhost:8000/api/analyze-land"

# 분석할 토지 정보
data = {
    "address": "서울특별시 마포구 서교동 395-1",
    "land_area": 600,
    "unit_type": "신혼부부형"
}

# API 호출
response = requests.post(url, json=data)
result = response.json()

# 결과 출력
print(f"분석 ID: {result['analysis_id']}")
print(f"예상 세대수: {result['summary']['estimated_units']}세대")
print(f"수요 점수: {result['summary']['demand_score']}/100")
print(f"최종 판단: {result['summary']['recommendation']}")
```

---

## 📍 주요 엔드포인트

### 1. 헬스 체크
```bash
curl http://localhost:8000/health
```

### 2. 토지 분석
```bash
curl -X POST http://localhost:8000/api/analyze-land \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### 3. API 문서
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🎯 세대 유형 옵션

분석할 때 다음 3가지 유형 중 선택:

| 유형 | 설명 | 전용면적 | 주차비율 |
|------|------|----------|----------|
| `청년형` | 청년 1인 가구용 | 30㎡ | 0.5대/세대 |
| `신혼부부형` | 신혼부부 2-3인 | 50㎡ | 0.7대/세대 |
| `고령자형` | 고령자 1-2인 | 40㎡ | 0.3대/세대 |

---

## 🔍 응답 구조 이해하기

### 요청
```json
{
  "address": "서울특별시 강남구 역삼동 679",
  "land_area": 500,
  "unit_type": "청년형"
}
```

### 응답 (주요 필드)

```json
{
  "status": "success",
  "analysis_id": "abc12345",
  
  "coordinates": {
    "latitude": 37.502094,
    "longitude": 127.036798
  },
  
  "zone_info": {
    "zone_type": "제2종일반주거지역",
    "building_coverage_ratio": 60.0,
    "floor_area_ratio": 200.0
  },
  
  "building_capacity": {
    "units": 34,          // 예상 세대수
    "floors": 4,          // 층수
    "parking_spaces": 17  // 주차대수
  },
  
  "risk_factors": [       // 리스크 요인 배열
    {
      "category": "유해시설",
      "description": "주유소 73m 이내",
      "severity": "high"
    }
  ],
  
  "demand_analysis": {
    "demand_score": 78.0,          // 수요 점수 (0-100)
    "recommendation": "적합",       // 적합성 판단
    "key_factors": [...]           // 핵심 수요 요인
  },
  
  "summary": {
    "is_eligible": false,          // LH 매입 적격 여부
    "estimated_units": 34,         // 예상 세대수
    "demand_score": 78.0,          // 수요 점수
    "recommendation": "부적합",     // 최종 추천
    "risk_count": 3                // 리스크 개수
  }
}
```

---

## 💡 유용한 팁

### 1. 여러 토지 비교하기

```python
addresses = [
    "서울특별시 강남구 역삼동 679",
    "서울특별시 마포구 서교동 395-1",
    "서울특별시 성동구 성수동1가 656-37"
]

for address in addresses:
    response = requests.post(url, json={
        "address": address,
        "land_area": 500,
        "unit_type": "청년형"
    })
    result = response.json()
    print(f"{address}: {result['summary']['demand_score']}/100")
```

### 2. 리스크만 빠르게 확인

```python
result = response.json()
if result['risk_factors']:
    print("⚠️ 리스크 요인:")
    for risk in result['risk_factors']:
        print(f"  - [{risk['severity']}] {risk['description']}")
else:
    print("✅ 리스크 없음")
```

### 3. 에러 처리

```python
try:
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
    result = response.json()
    
    if result['status'] == 'success':
        print("✅ 분석 성공")
    else:
        print(f"❌ 분석 실패: {result.get('message')}")
        
except requests.exceptions.Timeout:
    print("⏱️ 요청 시간 초과 (30초)")
except requests.exceptions.RequestException as e:
    print(f"❌ 요청 실패: {e}")
```

---

## 🛠️ 문제 해결

### 서버가 시작되지 않아요
```bash
# 포트 충돌 확인
lsof -i :8000

# 다른 포트로 실행
python -m uvicorn app.main:app --port 8001
```

### API 키 오류
```bash
# .env 파일 확인
cat .env

# API 키가 올바르게 설정되었는지 확인
grep KAKAO_REST_API_KEY .env
```

### 모듈을 찾을 수 없어요
```bash
# 의존성 재설치
pip install -r requirements.txt
```

---

## 📚 더 알아보기

- **상세 가이드**: [USAGE.md](USAGE.md)
- **프로젝트 개요**: [README.md](README.md)
- **완료 현황**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **API 문서**: http://localhost:8000/docs

---

## 🎉 성공!

이제 LH 토지진단 시스템을 사용할 준비가 완료되었습니다!

**다음 단계:**
1. 실제 토지 주소로 테스트해보기
2. 여러 토지를 비교 분석하기
3. 결과를 바탕으로 투자 결정하기

**질문이나 문제가 있다면:**
- 로그 확인: 서버 터미널 출력
- 헬스체크: `curl http://localhost:8000/health`
- API 문서: http://localhost:8000/docs

---

**버전:** 1.0.0  
**최종 업데이트:** 2024-11-09
