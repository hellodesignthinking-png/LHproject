# 🔍 토지 및 건축 규모 검토 - 핵심 코드

## 📍 위치: app/api/endpoints/analysis_v9_1_REAL.py

---

## 1️⃣ 용도지역별 건축기준 (라인 40-65)

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
    "준주거지역": {
        "building_coverage_ratio": 70.0,
        "floor_area_ratio": 400.0,
        "max_floors": 20,
        "max_height": 60.0
    },
    "중심상업지역": {
        "building_coverage_ratio": 90.0,
        "floor_area_ratio": 1500.0,
        "max_floors": 50,
        "max_height": 150.0
    },
    "일반상업지역": {
        "building_coverage_ratio": 80.0,
        "floor_area_ratio": 800.0,
        "max_floors": 30,
        "max_height": 90.0
    },
    "근린상업지역": {
        "building_coverage_ratio": 70.0,
        "floor_area_ratio": 500.0,
        "max_floors": 15,
        "max_height": 45.0
    }
}
```

---

## 2️⃣ 세대수 추정 함수 (라인 230-280)

```python
def estimate_units(
    land_area: float,
    bcr: float,
    far: float,
    zone_type: str
) -> Dict[str, Any]:
    """
    세대수 및 건축 규모 추정
    
    Args:
        land_area: 대지면적 (㎡)
        bcr: 건폐율 (%)
        far: 용적률 (%)
        zone_type: 용도지역
        
    Returns:
        {
            'unit_count': 세대수,
            'floors': 층수,
            'building_area': 건축면적,
            'total_floor_area': 연면적
        }
    """
    # 건축면적 = 대지면적 × 건폐율
    building_area = land_area * (bcr / 100)
    
    # 연면적 = 대지면적 × 용적률
    total_floor_area = land_area * (far / 100)
    
    # 층수 계산
    if building_area > 0:
        floors = max(1, int(total_floor_area / building_area))
    else:
        floors = int(far / bcr) if bcr > 0 else 1
    
    # 세대당 전용면적 (기본값: 60㎡)
    avg_unit_area = 60
    
    # 전용률 (77%)
    efficiency = 0.77
    
    # 세대수 = 연면적 × 전용률 / 세대당 전용면적
    unit_count = int(total_floor_area * efficiency / avg_unit_area)
    
    # 최소 세대수 보정
    unit_count = max(1, unit_count)
    
    return {
        'unit_count': unit_count,
        'floors': floors,
        'building_area': round(building_area, 2),
        'total_floor_area': round(total_floor_area, 2),
        'avg_unit_area': avg_unit_area,
        'efficiency': efficiency
    }
```

---

## 3️⃣ 토지 분석 메인 함수 (라인 70-200)

```python
async def analyze_land_real(request: AnalyzeLandRequestReal):
    """
    토지 분석 실행
    
    프로세스:
    1. 주소 → 좌표 변환 (카카오 API)
    2. 용도지역 조회 (국토부 API)
    3. 건축기준 매핑
    4. 세대수 추정
    5. 결과 반환
    """
    
    # Step 1: 주소 → 좌표
    try:
        coord = await kakao_service.address_to_coordinates(request.address)
        latitude = coord['latitude']
        longitude = coord['longitude']
        legal_code = coord.get('legal_code')
    except:
        # 실패 시 기본값
        latitude = 37.5665
        longitude = 126.9780
        legal_code = None
    
    # Step 2: 용도지역 조회
    try:
        zone_info = await land_regulation_service.get_land_use_zone(
            latitude=latitude,
            longitude=longitude
        )
        api_zone_type = zone_info.get('landUseZone')
    except:
        api_zone_type = None
    
    # Step 3: 건축기준 매핑
    zone_type = request.zone_type  # 사용자 입력 우선
    if zone_type in ZONE_TYPE_INFO:
        standards = ZONE_TYPE_INFO[zone_type]
    else:
        # 기본값
        standards = {
            "building_coverage_ratio": 60.0,
            "floor_area_ratio": 200.0,
            "max_floors": 7,
            "max_height": 21.0
        }
    
    bcr = standards['building_coverage_ratio']
    far = standards['floor_area_ratio']
    
    # Step 4: 세대수 추정
    development = estimate_units(
        land_area=request.land_area,
        bcr=bcr,
        far=far,
        zone_type=zone_type
    )
    
    # Step 5: 결과 반환
    return {
        "address": request.address,
        "latitude": latitude,
        "longitude": longitude,
        "land_area": request.land_area,
        "zone_type": zone_type,
        "building_coverage_ratio": bcr,
        "floor_area_ratio": far,
        "unit_count": development['unit_count'],
        "floors": development['floors'],
        "building_area": development['building_area'],
        "total_floor_area": development['total_floor_area']
    }
```

---

## 🔧 수정 가능한 파라미터

### 세대수 계산 관련
- `avg_unit_area = 60` → 세대당 전용면적 (㎡)
- `efficiency = 0.77` → 전용률 (77%)

### 용도지역별 기준
- `building_coverage_ratio` → 건폐율 (%)
- `floor_area_ratio` → 용적률 (%)
- `max_floors` → 최대 층수
- `max_height` → 최대 높이 (m)

---

## 📝 수정 예시

### 예시 1: 세대당 면적을 용도지역별로 차등 적용

```python
# 수정 전
avg_unit_area = 60

# 수정 후
UNIT_AREA_BY_ZONE = {
    "제1종일반주거지역": 45,
    "제2종일반주거지역": 60,
    "제3종일반주거지역": 70,
    "준주거지역": 65,
}
avg_unit_area = UNIT_AREA_BY_ZONE.get(zone_type, 60)
```

### 예시 2: 전용률을 동적으로 조정

```python
# 수정 전
efficiency = 0.77

# 수정 후
if total_floor_area < 1000:
    efficiency = 0.75  # 소규모
elif total_floor_area < 3000:
    efficiency = 0.77  # 중규모
else:
    efficiency = 0.80  # 대규모
```

---

## 🎯 즉시 테스트 명령어

```bash
# 1. 현재 코드 확인
cd /home/user/webapp
grep -A 30 "def estimate_units" app/api/endpoints/analysis_v9_1_REAL.py

# 2. 테스트 실행
python3 << 'TEST'
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

result = response.json()
print(f"세대수: {result['unit_count']}")
print(f"층수: {result['floors']}")
print(f"건축면적: {result['building_area']}㎡")
print(f"연면적: {result['total_floor_area']}㎡")
TEST
```

---

## ✅ 체크리스트

- [ ] 세대당 전용면적 조정
- [ ] 전용률 조정
- [ ] 용도지역별 건축기준 수정
- [ ] 최소/최대 제한 추가
- [ ] 주차대수 계산 추가
- [ ] 검증 로직 강화

---

수정하실 내용을 알려주시면 즉시 적용해드리겠습니다!
