# 토지/건축규모 검토 핵심 코드 Quick Reference

## 📁 파일 위치
- **메인 API 엔드포인트**: `/home/user/webapp/app/api/endpoints/analysis_v9_1_REAL.py`
- **용도지역 매핑**: `/home/user/webapp/app/services_v9/zoning_auto_mapper_v9_0.py`
- **세대수 추정기**: `/home/user/webapp/app/services_v9/unit_estimator_v9_0.py`

---

## 🎯 핵심 수정 포인트

### 1️⃣ 세대수/연면적 계산 로직 (`analysis_v9_1_REAL.py` 라인 286-319)

```python
# STEP 3: Unit Estimation (세대수/층수/주차)
unit_estimator = get_unit_estimator()
estimation = unit_estimator.estimate_units(
    land_area=request.land_area,
    floor_area_ratio=raw_input['floor_area_ratio'],
    building_coverage_ratio=raw_input['building_coverage_ratio'],
    zone_type=request.zone_type
)

# 자동 계산 필드 저장
auto_calculated.unit_count = estimation.total_units
auto_calculated.floors = estimation.floors
auto_calculated.parking_spaces = estimation.parking_spaces
auto_calculated.total_gfa = round(estimation.total_gfa, 2)
auto_calculated.residential_gfa = round(estimation.residential_gfa, 2)
```

**수정 가능 파라미터:**
- `unit_estimator.estimate_units()` 내부의 평당 세대수 계산식
- 주차대수 계산 공식 (`parking_spaces`)
- 층수 계산 로직 (`floors`)

---

### 2️⃣ 용도지역별 건축기준 (`zoning_auto_mapper_v9_0.py`)

다음 파일을 확인해서 수정 필요:

```bash
# 파일 위치 확인
cat /home/user/webapp/app/services_v9/zoning_auto_mapper_v9_0.py | head -100
```

**주요 수정 사항:**
- 용도지역별 건폐율/용적률 기본값
- 최대 층수/높이제한 규칙
- 특정 지역 예외 처리

---

### 3️⃣ 세대수 추정 상세 로직 (`unit_estimator_v9_0.py`)

```bash
# 파일 내용 확인
cat /home/user/webapp/app/services_v9/unit_estimator_v9_0.py
```

**핵심 수정 포인트:**
- **평균 세대 면적** (`avg_unit_area`): 기본값 60㎡ → 변경 가능
- **효율** (`efficiency`): 기본값 77% → 변경 가능
- **주차대수 계산**: 세대당 주차대수 비율
- **층수 계산**: 용적률 → 층수 변환 로직

---

## 🔧 빠른 수정 예시

### 예시 1: 평균 세대 면적을 50㎡로 변경

```python
# unit_estimator_v9_0.py 내부
def estimate_units(self, land_area, floor_area_ratio, building_coverage_ratio, zone_type):
    avg_unit_area = 50  # 기존 60 → 50으로 변경
    efficiency = 0.77
    
    # 총 연면적
    total_gfa = land_area * (floor_area_ratio / 100)
    
    # 주거 연면적 (효율 적용)
    residential_gfa = total_gfa * efficiency
    
    # 세대수 = 주거 연면적 / 평균 세대 면적
    total_units = int(residential_gfa / avg_unit_area)
    
    # ...
```

### 예시 2: 특정 용도지역의 용적률 변경

```python
# zoning_auto_mapper_v9_0.py 내부
ZONE_STANDARDS = {
    "제2종일반주거지역": {
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 250.0,  # 기존 200% → 250%로 변경
        "max_floors": 7,
        "max_height": None
    },
    # ...
}
```

### 예시 3: 주차대수 계산 비율 변경

```python
# unit_estimator_v9_0.py 내부
def calculate_parking(self, unit_count, zone_type):
    # 세대당 주차대수 비율
    if "제1종" in zone_type:
        parking_ratio = 0.8  # 기존 0.7 → 0.8로 변경
    elif "제2종" in zone_type:
        parking_ratio = 1.0
    elif "제3종" in zone_type:
        parking_ratio = 1.2  # 기존 1.0 → 1.2로 변경
    else:
        parking_ratio = 1.0
    
    return int(unit_count * parking_ratio)
```

---

## 🧪 테스트 방법

### 1. 서버 재시작

```bash
cd /home/user/webapp
pkill -9 -f "uvicorn.*8003"
sleep 3
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 &
sleep 5
```

### 2. API 테스트

```bash
curl -X POST "http://localhost:8003/api/v9/real/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area": 1200,
    "land_appraisal_price": 10800000000,
    "zone_type": "제2종일반주거지역"
  }' | jq '.auto_calculated'
```

### 3. 결과 확인 항목

```json
{
  "unit_count": 45,           // ← 세대수
  "floors": 7,                // ← 층수
  "parking_spaces": 45,       // ← 주차대수
  "total_gfa": 2400.0,        // ← 총 연면적
  "residential_gfa": 1848.0,  // ← 주거 연면적
  "building_coverage_ratio": 60.0,
  "floor_area_ratio": 200.0
}
```

---

## 📊 현재 기본값 요약

| 항목 | 기본값 | 위치 | 수정 난이도 |
|------|--------|------|------------|
| 평균 세대 면적 | 60㎡ | `unit_estimator_v9_0.py` | ⭐ 쉬움 |
| 효율 (전용률) | 77% | `unit_estimator_v9_0.py` | ⭐ 쉬움 |
| 주차대수 비율 | 세대당 0.7~1.2대 | `unit_estimator_v9_0.py` | ⭐⭐ 보통 |
| 용도지역별 기준 | 각 지역별 다름 | `zoning_auto_mapper_v9_0.py` | ⭐⭐ 보통 |
| 층수 계산 로직 | 용적률 기반 자동 | `unit_estimator_v9_0.py` | ⭐⭐⭐ 어려움 |

---

## 🚨 주의사항

1. **파일 수정 후 반드시 서버 재시작 필요**
   - Python은 모듈 캐싱 때문에 재시작 필수

2. **자동 계산 필드는 `analysis_v9_1_REAL.py` STEP 3에서 호출**
   - `unit_estimator_v9_0.py`만 수정하면 됨 (API 엔드포인트 수정 불필요)

3. **용도지역 기준 수정 시 `zoning_auto_mapper_v9_0.py` 확인**
   - ZONE_STANDARDS 딕셔너리 수정

4. **Git 커밋 필수**
   ```bash
   cd /home/user/webapp
   git add -A
   git commit -m "fix: 토지/건축규모 계산 로직 수정"
   git push origin main
   ```

---

## 🎯 다음 단계

현재 상태에서 수정하고 싶은 부분을 알려주시면:

1. **해당 파일을 열어서** → 현재 코드 확인
2. **수정 사항 적용** → 코드 변경
3. **서버 재시작** → 테스트
4. **결과 검증** → API 호출 테스트

위 순서로 진행하겠습니다.

---

## 📞 빠른 명령어 모음

```bash
# 1. 세대수 추정기 코드 확인
cat /home/user/webapp/app/services_v9/unit_estimator_v9_0.py

# 2. 용도지역 매퍼 코드 확인
cat /home/user/webapp/app/services_v9/zoning_auto_mapper_v9_0.py

# 3. 메인 API 엔드포인트 확인 (STEP 3 부분)
sed -n '286,319p' /home/user/webapp/app/api/endpoints/analysis_v9_1_REAL.py

# 4. 서버 재시작
pkill -9 -f "uvicorn.*8003"; sleep 3; cd /home/user/webapp && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 &

# 5. API 테스트
curl -X POST "http://localhost:8003/api/v9/real/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{"address":"서울특별시 마포구 월드컵북로 120","land_area":1200,"land_appraisal_price":10800000000,"zone_type":"제2종일반주거지역"}' \
  | jq '.auto_calculated'
```

---

**저장 완료: `/home/user/webapp/LAND_BUILD_QUICK_REF.md`**
