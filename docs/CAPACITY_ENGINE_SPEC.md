# Capacity Engine Specification (규모검토 엔진 사양서)

**Version**: 24.0.0  
**Priority**: 🔴 CRITICAL  
**Date**: 2025-12-12  
**Status**: Design Phase

---

## Executive Summary

Capacity Engine은 ZeroSite v24의 핵심 기능으로, 토지의 건축 가능 규모를 자동으로 계산합니다.

### Core Functions
1. **층수 계산** (Floor Calculation)
2. **세대수 계산** (Unit Count Calculation)
3. **주차대수 계산** (Parking Space Calculation)
4. **일조권 체크** (Daylight Regulation Check)

---

## 1. 층수 계산 (Floor Calculation)

### 1.1 기본 원리
```
최대 층수 = min(
    높이 제한 / 층고,
    용적률 제한 층수,
    일조권 제한 층수
)
```

### 1.2 입력 데이터
- `land_area_sqm`: 대지면적 (㎡)
- `zoning_type`: 용도지역 (제1종일반주거, 제2종일반주거, 제3종일반주거, 준주거)
- `far_limit`: 용적률 한계 (%)
- `bcr_limit`: 건폐율 한계 (%)
- `height_limit`: 높이 제한 (m)
- `floor_height`: 층고 (m, default: 3.0m)

### 1.3 계산 로직

#### A. 높이 제한에 의한 층수
```python
max_floors_by_height = floor(height_limit / floor_height)
```

#### B. 용적률 제한에 의한 층수
```python
# 건축면적 = 대지면적 × 건폐율
building_footprint = land_area_sqm * (bcr_limit / 100)

# 총 연면적 = 대지면적 × 용적률
total_floor_area = land_area_sqm * (far_limit / 100)

# 최대 층수 = 총 연면적 / 건축면적
max_floors_by_far = floor(total_floor_area / building_footprint)
```

#### C. 일조권 제한 (Daylight Regulation)
- **제1종일반주거**: 9m 높이까지는 정북방향 인접 대지경계선으로부터 1.5m, 9m를 초과하는 부분은 높이의 1/2 이상 거리 확보
- **제2종일반주거**: 9m 높이까지는 정북방향 인접 대지경계선으로부터 1.0m, 9m를 초과하는 부분은 높이의 1/2 이상 거리 확보
- **제3종일반주거/준주거**: 9m를 초과하는 부분은 높이의 1/2 이상 거리 확보

```python
def calculate_daylight_limit(zoning_type: str, land_depth_m: float, floor_height: float) -> int:
    """
    일조권 제한에 의한 최대 층수 계산
    
    Args:
        zoning_type: 용도지역 ('제1종일반주거', '제2종일반주거', '제3종일반주거', '준주거')
        land_depth_m: 토지 깊이 (정북방향 길이, m)
        floor_height: 층고 (m)
    
    Returns:
        최대 층수
    """
    
    if zoning_type == '제1종일반주거':
        setback_base = 1.5  # 9m까지는 1.5m 이격
        setback_ratio = 0.5  # 9m 초과 부분은 높이의 1/2
    elif zoning_type == '제2종일반주거':
        setback_base = 1.0  # 9m까지는 1.0m 이격
        setback_ratio = 0.5  # 9m 초과 부분은 높이의 1/2
    else:  # 제3종일반주거, 준주거
        setback_base = 0  # 9m까지는 이격 없음
        setback_ratio = 0.5  # 9m 초과 부분은 높이의 1/2
    
    # 9m (약 3층)까지의 이격
    usable_depth_9m = land_depth_m - setback_base
    
    # 9m 초과 부분의 이격 (높이의 1/2)
    # H = 9 + (land_depth - setback_base - 9) / 0.5
    # where H <= land_depth - setback_base + 9
    
    if usable_depth_9m <= 0:
        return 0
    
    # 9m까지는 3층으로 계산
    max_height_9m = 9.0
    floors_9m = int(max_height_9m / floor_height)
    
    # 9m 초과 부분 계산
    if usable_depth_9m > max_height_9m:
        # 추가 가능한 높이 = (사용 가능 깊이 - 9m) / (1 + setback_ratio)
        additional_height = (usable_depth_9m - max_height_9m) / (1 + setback_ratio)
        additional_floors = int(additional_height / floor_height)
        
        return floors_9m + additional_floors
    else:
        return floors_9m
```

#### D. 최종 층수 결정
```python
max_floors = min(
    max_floors_by_height,
    max_floors_by_far,
    max_floors_by_daylight
)
```

---

## 2. 세대수 계산 (Unit Count Calculation)

### 2.1 기본 원리
```
총 세대수 = (총 연면적 - 공용면적) / 평균 전용면적
```

### 2.2 입력 데이터
- `total_floor_area`: 총 연면적 (㎡)
- `unit_types`: 평형 분포 (e.g., {"59": 0.6, "84": 0.4})
- `efficiency_ratio`: 주거전용률 (default: 0.75 = 75%)
- `common_area_ratio`: 공용면적 비율 (default: 0.25 = 25%)

### 2.3 계산 로직

```python
def calculate_unit_count(
    total_floor_area: float,
    unit_types: Dict[str, float],  # {"59": 0.6, "84": 0.4}
    efficiency_ratio: float = 0.75,
    common_area_ratio: float = 0.25
) -> Dict[str, int]:
    """
    세대수 계산
    
    Returns:
        {
            "total_units": int,
            "units_by_type": {"59": 36, "84": 24},
            "residential_area": float,
            "common_area": float
        }
    """
    
    # 1. 주거 전용면적 계산
    residential_area = total_floor_area * efficiency_ratio
    common_area = total_floor_area * common_area_ratio
    
    # 2. 평균 전용면적 계산
    avg_unit_area = sum(
        float(unit_type) * ratio 
        for unit_type, ratio in unit_types.items()
    )
    
    # 3. 총 세대수
    total_units = int(residential_area / avg_unit_area)
    
    # 4. 평형별 세대수
    units_by_type = {}
    for unit_type, ratio in unit_types.items():
        units_by_type[unit_type] = round(total_units * ratio)
    
    # 5. 반올림 오차 보정
    actual_total = sum(units_by_type.values())
    if actual_total != total_units:
        # 가장 많은 비율의 평형에서 조정
        max_type = max(unit_types, key=unit_types.get)
        units_by_type[max_type] += (total_units - actual_total)
    
    return {
        "total_units": total_units,
        "units_by_type": units_by_type,
        "residential_area": round(residential_area, 2),
        "common_area": round(common_area, 2),
        "avg_unit_area": round(avg_unit_area, 2)
    }
```

---

## 3. 주차대수 계산 (Parking Space Calculation)

### 3.1 기본 원리
주차대수는 세대수와 용도지역에 따라 결정됩니다.

### 3.2 주차대수 기준 (서울시 기준)

| 용도지역 | 세대당 주차대수 |
|----------|----------------|
| 제1종일반주거 | 0.7대/세대 |
| 제2종일반주거 | 0.8대/세대 |
| 제3종일반주거 | 1.0대/세대 |
| 준주거지역 | 1.0대/세대 |

### 3.3 계산 로직

```python
PARKING_RATIOS = {
    '제1종일반주거': 0.7,
    '제2종일반주거': 0.8,
    '제3종일반주거': 1.0,
    '준주거': 1.0,
}

def calculate_parking_spaces(
    total_units: int,
    zoning_type: str
) -> Dict[str, Any]:
    """
    주차대수 계산
    
    Returns:
        {
            "required_spaces": int,
            "parking_ratio": float,
            "zoning_type": str
        }
    """
    
    parking_ratio = PARKING_RATIOS.get(zoning_type, 1.0)
    required_spaces = ceil(total_units * parking_ratio)
    
    return {
        "required_spaces": required_spaces,
        "parking_ratio": parking_ratio,
        "zoning_type": zoning_type,
        "calculation": f"{total_units}세대 × {parking_ratio} = {required_spaces}대"
    }
```

---

## 4. 일조권 검증 (Daylight Regulation Check)

### 4.1 검증 항목
1. 정북방향 이격거리 확인
2. 층수별 이격거리 계산
3. 법규 준수 여부 판정

### 4.2 검증 로직

```python
def validate_daylight_compliance(
    zoning_type: str,
    building_height: float,
    setback_distance: float
) -> Dict[str, Any]:
    """
    일조권 법규 준수 검증
    
    Returns:
        {
            "compliant": bool,
            "required_setback": float,
            "actual_setback": float,
            "shortfall": float,
            "regulation": str
        }
    """
    
    if zoning_type == '제1종일반주거':
        if building_height <= 9.0:
            required_setback = 1.5
            regulation = "9m 이하: 1.5m 이격"
        else:
            required_setback = 1.5 + (building_height - 9.0) * 0.5
            regulation = "9m 초과: 1.5m + (H-9m)×0.5"
    
    elif zoning_type == '제2종일반주거':
        if building_height <= 9.0:
            required_setback = 1.0
            regulation = "9m 이하: 1.0m 이격"
        else:
            required_setback = 1.0 + (building_height - 9.0) * 0.5
            regulation = "9m 초과: 1.0m + (H-9m)×0.5"
    
    else:  # 제3종일반주거, 준주거
        if building_height <= 9.0:
            required_setback = 0
            regulation = "9m 이하: 이격거리 없음"
        else:
            required_setback = (building_height - 9.0) * 0.5
            regulation = "9m 초과: (H-9m)×0.5"
    
    compliant = setback_distance >= required_setback
    shortfall = max(0, required_setback - setback_distance)
    
    return {
        "compliant": compliant,
        "required_setback": round(required_setback, 2),
        "actual_setback": round(setback_distance, 2),
        "shortfall": round(shortfall, 2),
        "regulation": regulation,
        "status": "✅ 준수" if compliant else "❌ 미준수"
    }
```

---

## 5. Capacity Engine API Interface

### 5.1 Input Schema

```python
{
    "land_area_sqm": 660.0,
    "zoning_type": "제2종일반주거",
    "far_limit": 200.0,
    "bcr_limit": 60.0,
    "height_limit": 35.0,
    "land_depth_m": 25.0,  # 정북방향 토지 깊이
    "unit_types": {
        "59": 0.6,
        "84": 0.4
    },
    "floor_height": 3.0,
    "efficiency_ratio": 0.75,
    "common_area_ratio": 0.25
}
```

### 5.2 Output Schema

```python
{
    "success": true,
    "engine": "CapacityEngine",
    "version": "24.0.0",
    "timestamp": "2025-12-12T10:00:00",
    "data": {
        "floors": {
            "max_floors": 8,
            "max_floors_by_height": 11,
            "max_floors_by_far": 10,
            "max_floors_by_daylight": 8,
            "limiting_factor": "daylight",
            "building_height": 24.0
        },
        "units": {
            "total_units": 60,
            "units_by_type": {
                "59": 36,
                "84": 24
            },
            "residential_area": 4500.0,
            "common_area": 1500.0,
            "avg_unit_area": 75.0
        },
        "parking": {
            "required_spaces": 48,
            "parking_ratio": 0.8,
            "zoning_type": "제2종일반주거"
        },
        "daylight": {
            "compliant": true,
            "required_setback": 8.5,
            "actual_setback": 10.0,
            "shortfall": 0,
            "status": "✅ 준수"
        },
        "summary": {
            "land_area": 660.0,
            "building_footprint": 396.0,
            "total_floor_area": 1320.0,
            "far_actual": 200.0,
            "bcr_actual": 60.0
        }
    }
}
```

---

## 6. Test Cases

### Test Case 1: 제2종일반주거 (마포구 월드컵북로 120)
```python
input_data = {
    "land_area_sqm": 660.0,
    "zoning_type": "제2종일반주거",
    "far_limit": 200.0,
    "bcr_limit": 60.0,
    "height_limit": 35.0,
    "land_depth_m": 25.0,
    "unit_types": {"59": 0.6, "84": 0.4}
}

expected_output = {
    "max_floors": 8,  # 일조권 제한
    "total_units": 60,  # 1320㎡ × 0.75 / 16.5㎡
    "parking_spaces": 48  # 60세대 × 0.8
}
```

### Test Case 2: 제1종일반주거 (작은 필지)
```python
input_data = {
    "land_area_sqm": 300.0,
    "zoning_type": "제1종일반주거",
    "far_limit": 150.0,
    "bcr_limit": 50.0,
    "height_limit": 20.0,
    "land_depth_m": 15.0,
    "unit_types": {"59": 1.0}
}

expected_output = {
    "max_floors": 4,  # 일조권 제한 (15m 깊이)
    "total_units": 17,  # 450㎡ × 0.75 / 59㎡
    "parking_spaces": 12  # 17세대 × 0.7
}
```

### Test Case 3: 준주거지역 (고밀도)
```python
input_data = {
    "land_area_sqm": 1650.0,
    "zoning_type": "준주거",
    "far_limit": 500.0,
    "bcr_limit": 60.0,
    "height_limit": 50.0,
    "land_depth_m": 40.0,
    "unit_types": {"84": 0.5, "114": 0.5}
}

expected_output = {
    "max_floors": 15,  # 높이 제한 (50m / 3.3m)
    "total_units": 83,  # 8250㎡ × 0.75 / 99㎡
    "parking_spaces": 83  # 83세대 × 1.0
}
```

---

## 7. Implementation Priority

### Phase 2.1: Design ✅ (This Document)
- [x] Algorithm definition
- [x] Test case specification
- [x] API interface design

### Phase 2.2: Implementation (Next)
- [ ] Create `capacity_engine.py`
- [ ] Implement floor calculation
- [ ] Implement unit count calculation
- [ ] Implement parking calculation
- [ ] Implement daylight validation
- [ ] Integration tests

### Phase 2.3: Testing & Validation
- [ ] Unit tests (3 test cases)
- [ ] Integration with other engines
- [ ] Performance testing
- [ ] Documentation

---

## 8. Success Criteria

✅ **Accuracy**: Unit count within ±1 of manual calculation  
✅ **FAR Accuracy**: 100% accuracy vs. regulatory standards  
✅ **Daylight Compliance**: Correct identification of violations  
✅ **Performance**: < 0.5 seconds processing time  
✅ **Test Coverage**: 95%+ code coverage

---

**Document Status**: Design Complete ✅  
**Next Step**: Phase 2.2 Implementation  
**Owner**: ZeroSite Development Team
