# 🏗️ 토지 및 건축 규모 검토 부분 수정 가이드

## 📋 현재 구조 분석

### 1️⃣ 토지 분석 엔진 위치

**주요 파일:**
- `app/api/endpoints/analysis_v9_1_REAL.py` - 메인 분석 API 엔드포인트
- `app/services/analysis_engine.py` - 기본 분석 엔진
- `app/services_v9/normalization_layer_v9_0.py` - v9.0 정규화 레이어

**분석 흐름:**
```
1. API Request → analysis_v9_1_REAL.py::analyze_land_real()
2. 좌표 변환 → 카카오 API로 주소 → 좌표
3. 용도지역 조회 → 국토부 API
4. 건축기준 매핑 → ZONE_TYPE_INFO
5. 세대수 추정 → estimate_units()
6. 결과 반환
```

---

## 🔍 핵심 검토 로직

### A. 토지 기본 정보 수집 (Step 1-2)

**파일:** `app/api/endpoints/analysis_v9_1_REAL.py`
**함수:** `analyze_land_real()` (라인 70-170)

```python
# Step 1: 주소 → 좌표 변환
coord = await kakao_service.address_to_coordinates(request.address)
latitude = coord['latitude']
longitude = coord['longitude']

# Step 2: 용도지역 조회
zone_info = await land_regulation_service.get_land_use_zone(
    latitude=latitude,
    longitude=longitude
)
```

**수정 포인트:**
- 좌표 정확도 검증
- 용도지역 매핑 규칙
- 예외 처리 로직

---

### B. 건축 규모 검토 (Step 3)

**파일:** `app/api/endpoints/analysis_v9_1_REAL.py`
**함수:** `estimate_units()` (라인 230-280)

```python
def estimate_units(land_area: float, bcr: float, far: float, zone_type: str):
    """
    세대수 및 건축 규모 추정
    
    계산 로직:
    1. 건축면적 = 대지면적 × 건폐율
    2. 연면적 = 대지면적 × 용적률
    3. 층수 = 용적률 / 건폐율
    4. 세대당 전용면적 가정 (60㎡)
    5. 세대수 = 연면적 / (전용면적 × 1.3)
    """
    building_area = land_area * (bcr / 100)
    total_floor_area = land_area * (far / 100)
    floors = max(1, int(far / bcr))
    
    avg_unit_area = 60  # ㎡
    efficiency = 0.77   # 전용률 77%
    unit_count = int(total_floor_area * efficiency / avg_unit_area)
    
    return {
        'unit_count': unit_count,
        'floors': floors,
        'building_area': building_area,
        'total_floor_area': total_floor_area
    }
```

**주요 가정:**
- 세대당 전용면적: 60㎡
- 전용률: 77%
- 공용면적 계수: 1.3

---

### C. 용도지역별 건축기준

**파일:** `app/api/endpoints/analysis_v9_1_REAL.py`
**변수:** `ZONE_TYPE_INFO` (라인 40-65)

```python
ZONE_TYPE_INFO = {
    "제1종일반주거지역": {
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 150.0,
        "max_floors": 4,
        "max_height": 15.0
    },
    "제2종일반주거지역": {
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 200.0,
        "max_floors": 7,
        "max_height": 21.0
    },
    "제3종일반주거지역": {
        "building_coverage_ratio": 50.0,
        "floor_area_ratio": 250.0,
        "max_floors": 15,
        "max_height": 45.0
    },
    # ... 기타 용도지역
}
```

---

## 🛠️ 빠른 수정 방법

### 1. 세대수 계산 로직 수정

**목표:** 더 정확한 세대수 추정

```python
# 파일: app/api/endpoints/analysis_v9_1_REAL.py
# 함수: estimate_units()

# 수정 전
avg_unit_area = 60  # 고정값

# 수정 후 (용도지역별 차등 적용)
UNIT_AREA_BY_ZONE = {
    "제1종일반주거지역": 45,  # 소형 위주
    "제2종일반주거지역": 60,  # 중형
    "제3종일반주거지역": 70,  # 대형
}
avg_unit_area = UNIT_AREA_BY_ZONE.get(zone_type, 60)
```

---

### 2. 건폐율/용적률 검증 강화

**목표:** 실제 건축 가능 여부 확인

```python
# 추가 검증 로직
def validate_building_standards(land_area, bcr, far, zone_type):
    # 최소 대지면적 체크
    MIN_LAND_AREA = 200  # ㎡
    if land_area < MIN_LAND_AREA:
        return False, "대지면적 부족 (최소 200㎡ 필요)"
    
    # 건폐율/용적률 범위 체크
    if bcr > 70 or far > 300:
        return False, "건폐율/용적률 기준 초과"
    
    # 층수 계산 검증
    floors = far / bcr
    max_floors = ZONE_TYPE_INFO[zone_type]['max_floors']
    if floors > max_floors:
        return False, f"층수 제한 초과 ({floors:.1f} > {max_floors})"
    
    return True, "적합"
```

---

### 3. 주차 대수 계산 추가

**목표:** 주차장 법규 준수 확인

```python
def calculate_parking_requirement(unit_count, zone_type):
    """
    주차대수 계산
    
    기준:
    - 주거지역: 세대당 1대
    - 상업지역: 세대당 0.7대
    """
    if "주거" in zone_type:
        ratio = 1.0
    elif "상업" in zone_type:
        ratio = 0.7
    else:
        ratio = 0.8
    
    required_parking = int(unit_count * ratio)
    
    return {
        'required': required_parking,
        'ratio': ratio,
        'standard': f"세대당 {ratio}대"
    }
```

---

## 📂 수정 대상 파일 요약

| 파일 | 라인 | 내용 | 우선순위 |
|------|------|------|----------|
| `analysis_v9_1_REAL.py` | 230-280 | `estimate_units()` 함수 | ⭐⭐⭐ 최우선 |
| `analysis_v9_1_REAL.py` | 40-65 | `ZONE_TYPE_INFO` 상수 | ⭐⭐⭐ 최우선 |
| `analysis_v9_1_REAL.py` | 70-170 | `analyze_land_real()` 함수 | ⭐⭐ 중요 |
| `analysis_engine.py` | 전체 | 기본 분석 로직 | ⭐ 참고 |

---

## 🎯 수정 시작 방법

### 1단계: 현재 로직 확인
```bash
# estimate_units 함수 읽기
cd /home/user/webapp
grep -A 50 "def estimate_units" app/api/endpoints/analysis_v9_1_REAL.py
```

### 2단계: 백업 생성
```bash
cp app/api/endpoints/analysis_v9_1_REAL.py app/api/endpoints/analysis_v9_1_REAL.py.backup
```

### 3단계: 수정 작업
- 파일 읽기: Read tool 사용
- 수정: Edit tool 사용
- 테스트: API 호출하여 검증

### 4단계: 테스트
```python
# 테스트 코드
import requests

response = requests.post(
    "http://localhost:8003/api/v9/real/analyze-land",
    json={
        "address": "서울특별시 강남구 테헤란로 123",
        "land_area": 1000,
        "land_appraisal_price": 5000000000,
        "zone_type": "제2종일반주거지역"
    }
)

print(response.json())
```

---

## 🚨 주의사항

1. **기존 로직 보존**: 큰 변경 전 반드시 백업
2. **점진적 수정**: 한 번에 하나씩 수정하고 테스트
3. **하위 호환성**: 기존 API 응답 구조 유지
4. **문서화**: 수정 내용 주석으로 기록

---

## 📞 다음 단계

수정하고 싶은 구체적인 내용을 알려주시면:
1. 해당 코드 섹션을 정확히 찾아드립니다
2. 수정 전/후 코드를 보여드립니다
3. 즉시 적용하여 테스트합니다

**예시 요청:**
- "세대수 계산을 더 보수적으로 변경"
- "용적률 200% 이하일 때만 진행"
- "주차대수 계산 추가"
- "최소 대지면적 500㎡로 변경"

어떤 부분을 수정하시겠습니까?
