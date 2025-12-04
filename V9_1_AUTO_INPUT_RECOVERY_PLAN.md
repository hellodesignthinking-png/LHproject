# 🚀 ZeroSite v9.1 - 자동화 입력 시스템 복구 계획

**Date**: 2025-12-04  
**Priority**: CRITICAL  
**Target**: v7.5 핵심 자동화 기능 복구 + 고도화

---

## 🔴 문제 현황 - v9.0의 3대 자동화 기능 미구현

### Issue #1: 지번 → 좌표 자동 변환 기능 없음
```
v7.5: 지번 입력 → 도로명주소 변환 → 좌표 획득 → POI 분석
v9.0: 위도/경도를 사용자가 직접 입력해야 함 ❌
```

**현재 상태 (확인 완료)**:
```python
# app/services_v9/normalization_layer_v9_0.py (Line 66-67)
latitude=raw_input.get("latitude"),      # 사용자 입력 필수
longitude=raw_input.get("longitude"),    # 사용자 입력 필수
```

**문제점**:
- 일반 사용자는 위도/경도를 모름
- v7.5에서는 자동으로 Kakao API 호출하여 좌표 획득했음
- 현재는 이 기능이 완전히 제거됨

---

### Issue #2: 세대수 자동 계산 기능 없음
```
v7.5: 용적률 × 대지면적 → 자동 세대수 산정
v9.0: 세대수를 사용자가 직접 입력해야 함 ❌
```

**필요한 자동 계산**:
```python
# 연면적 계산
total_gfa = land_area * (floor_area_ratio / 100)

# 주거 전용 면적 (상업/부대시설 제외)
residential_gfa = total_gfa * 0.85

# 세대수 계산 (세대당 평균 면적 60㎡ 가정)
estimated_units = residential_gfa / 60.0
```

**현재 상태**: 완전히 미구현

---

### Issue #3: 용도지역별 용적률/건폐율 자동 입력 없음
```
v7.5: 제3종일반주거지역 선택 → 50% / 300% 자동 입력
v9.0: 사용자가 직접 입력해야 함 ❌
```

**법정 기준표 (국토부)**:
| 용도지역 | 건폐율 | 용적률 |
|---------|--------|--------|
| 제1종전용주거지역 | 50% | 100% |
| 제2종전용주거지역 | 50% | 150% |
| 제1종일반주거지역 | 60% | 200% |
| 제2종일반주거지역 | 60% | 250% |
| 제3종일반주거지역 | 50% | 300% |
| 준주거지역 | 70% | 500% |
| 중심상업지역 | 90% | 1,500% |
| 일반상업지역 | 80% | 1,300% |
| 근린상업지역 | 70% | 900% |
| 유통상업지역 | 80% | 1,100% |
| 준공업지역 | 70% | 400% |

**현재 상태**: 기본값(50%, 200%) 사용, 자동 매핑 없음

---

## ✅ v9.1 복구 계획 - 3단계 자동화 시스템

### 🎯 목표: 사용자 입력 4개만으로 전체 분석 가능

**필수 입력 (4개)**:
1. 지번 주소 (예: "서울 마포구 성산동 123-45")
2. 대지 면적 (예: 660㎡)
3. 토지 가격 (예: 5,000,000,000원)
4. 용도 지역 (예: "제3종일반주거지역")

**자동 처리 (ZeroSite)**:
- 도로명 주소 변환
- 위도/경도 좌표 획득
- 용적률/건폐율 자동 설정
- 예상 세대수 자동 계산
- POI 분석 자동 실행
- 재무 분석 자동 실행

---

## 📐 v9.1 아키텍처 설계

### 1. 새로운 서비스: AddressResolverV9

**파일**: `app/services_v9/address_resolver_v9_0.py`

**기능**:
```python
class AddressResolverV9:
    """
    주소 정규화 및 좌표 획득 서비스
    
    Features:
    - 지번 → 도로명 주소 변환
    - 주소 → 위도/경도 좌표 획득
    - Kakao Local API 연동
    - Redis 캐싱 (24시간)
    """
    
    async def resolve_address(
        self, 
        address: str
    ) -> AddressInfo:
        """
        주소 정규화 및 좌표 획득
        
        Args:
            address: 지번 또는 도로명 주소
            
        Returns:
            AddressInfo:
                - road_address: 도로명 주소
                - parcel_address: 지번 주소
                - latitude: 위도
                - longitude: 경도
                - legal_code: 법정동 코드
        """
```

**API 엔드포인트**:
```
POST /api/v9/resolve-address
```

**Request**:
```json
{
  "address": "서울 마포구 성산동 123-45"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "road_address": "서울특별시 마포구 월드컵북로 120",
    "parcel_address": "서울특별시 마포구 성산동 123-45",
    "latitude": 37.564123,
    "longitude": 126.912345,
    "legal_code": "1144010100",
    "administrative_district": "마포구"
  }
}
```

---

### 2. 새로운 서비스: ZoningAutoMapperV9

**파일**: `app/services_v9/zoning_auto_mapper_v9_0.py`

**기능**:
```python
class ZoningAutoMapperV9:
    """
    용도지역별 법정 기준 자동 매핑
    
    Features:
    - 용도지역 → 용적률/건폐율 자동 설정
    - 법정 주차 대수 계산
    - 층수 제한 자동 설정
    - 지역별 규제 사항 조회
    """
    
    def get_zoning_standards(
        self,
        zone_type: str
    ) -> ZoningStandards:
        """
        용도지역 법정 기준 조회
        
        Args:
            zone_type: 용도지역 (예: "제3종일반주거지역")
            
        Returns:
            ZoningStandards:
                - building_coverage_ratio: 건폐율 (%)
                - floor_area_ratio: 용적률 (%)
                - max_height: 최대 높이 (m)
                - parking_ratio: 주차 대수 비율
        """
```

**내장 데이터**:
```python
ZONING_STANDARDS = {
    "제1종전용주거지역": {
        "building_coverage_ratio": 50.0,
        "floor_area_ratio": 100.0,
        "max_height": None,
        "parking_ratio": 1.0
    },
    "제2종전용주거지역": {
        "building_coverage_ratio": 50.0,
        "floor_area_ratio": 150.0,
        "max_height": None,
        "parking_ratio": 1.0
    },
    "제1종일반주거지역": {
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 200.0,
        "max_height": None,
        "parking_ratio": 1.0
    },
    "제2종일반주거지역": {
        "building_coverage_ratio": 60.0,
        "floor_area_ratio": 250.0,
        "max_height": None,
        "parking_ratio": 1.0
    },
    "제3종일반주거지역": {
        "building_coverage_ratio": 50.0,
        "floor_area_ratio": 300.0,
        "max_height": None,
        "parking_ratio": 1.0
    },
    "준주거지역": {
        "building_coverage_ratio": 70.0,
        "floor_area_ratio": 500.0,
        "max_height": None,
        "parking_ratio": 1.0
    },
    # ... 전체 용도지역 표
}
```

---

### 3. 새로운 서비스: UnitEstimatorV9

**파일**: `app/services_v9/unit_estimator_v9_0.py`

**기능**:
```python
class UnitEstimatorV9:
    """
    자동 세대수 산정 엔진
    
    Features:
    - 용적률 기반 연면적 계산
    - 세대 유형별 면적 배분
    - 층수 및 층별 세대수 계산
    - 주차 대수 자동 계산
    - 건축 가능성 검증
    """
    
    def estimate_units(
        self,
        land_area: float,
        floor_area_ratio: float,
        building_coverage_ratio: float,
        unit_type_mix: Dict[str, float] = None
    ) -> UnitEstimate:
        """
        자동 세대수 산정
        
        Args:
            land_area: 대지 면적 (m²)
            floor_area_ratio: 용적률 (%)
            building_coverage_ratio: 건폐율 (%)
            unit_type_mix: 세대 유형 비율
                {
                    "59㎡": 0.3,  # 30%
                    "74㎡": 0.5,  # 50%
                    "84㎡": 0.2   # 20%
                }
                
        Returns:
            UnitEstimate:
                - total_units: 총 세대수
                - total_gfa: 연면적
                - residential_gfa: 주거 전용 면적
                - commercial_gfa: 부대시설 면적
                - floors: 층수
                - units_per_floor: 층별 세대수
                - parking_spaces: 주차 대수
                - unit_type_distribution: 세대 유형별 배분
        """
```

**계산 로직**:
```python
# 1. 연면적 계산
total_gfa = land_area * (floor_area_ratio / 100)

# 2. 건축 면적 계산
building_footprint = land_area * (building_coverage_ratio / 100)

# 3. 주거 전용 면적 (부대시설 15% 제외)
residential_gfa = total_gfa * 0.85

# 4. 세대당 평균 면적 (전용면적 + 공용면적)
avg_unit_area = 60.0  # m² (약 18평)

# 5. 추정 세대수
estimated_units = int(residential_gfa / avg_unit_area)

# 6. 층수 계산
floors = int(total_gfa / building_footprint)

# 7. 층별 세대수
units_per_floor = int(estimated_units / floors)

# 8. 주차 대수 (세대당 1대)
parking_spaces = estimated_units
```

---

## 🔧 v9.1 구현 계획

### Phase 1: 주소 자동 변환 (1-2일)
1. **AddressResolverV9 구현**
   - Kakao Local API 연동
   - 주소 정규화
   - 좌표 획득
   - Redis 캐싱

2. **API 엔드포인트 추가**
   ```
   POST /api/v9/resolve-address
   ```

3. **Normalization Layer 수정**
   - 좌표 미입력 시 자동 resolve
   - 기본 동작 변경

---

### Phase 2: 용적률/건폐율 자동 설정 (1일)
1. **ZoningAutoMapperV9 구현**
   - 용도지역 표 내장
   - 자동 매핑 로직

2. **Normalization Layer 통합**
   - 용도지역 입력 시 자동 설정
   - 사용자 입력 우선순위 유지

---

### Phase 3: 세대수 자동 계산 (2-3일)
1. **UnitEstimatorV9 구현**
   - 연면적 계산
   - 세대수 산정
   - 층수 계산
   - 주차 대수 계산

2. **FinancialEngineV9 연동**
   - 자동 산정된 세대수 사용
   - 사용자 입력 세대수 우선

3. **LHEngineV9 연동**
   - 규모 점수 자동 계산

---

### Phase 4: Frontend 입력 UI 간소화 (1-2일)
1. **필수 입력 4개만 표시**
   ```
   [ ] 지번 주소
   [ ] 대지 면적 (m²)
   [ ] 토지 가격 (원)
   [ ] 용도 지역 (선택)
   ```

2. **고급 옵션 (접기/펼치기)**
   ```
   [▼] 고급 옵션 (자동 계산 무시)
       [ ] 위도
       [ ] 경도
       [ ] 건폐율 (%)
       [ ] 용적률 (%)
       [ ] 세대수
   ```

3. **자동 계산 결과 표시**
   ```
   📍 주소 정보
   - 도로명: 서울특별시 마포구 월드컵북로 120
   - 좌표: 37.564, 126.912
   
   📐 건축 기준
   - 건폐율: 50% (법정 기준)
   - 용적률: 300% (법정 기준)
   
   🏢 예상 규모
   - 연면적: 1,980 m²
   - 세대수: 28세대 (자동 산정)
   - 층수: 6층
   ```

---

## 📊 v9.1 API 플로우

### Before (v9.0 - 현재)
```
사용자 입력 (10개 필드)
  ├─ 주소
  ├─ 위도 ❌ (사용자가 모름)
  ├─ 경도 ❌ (사용자가 모름)
  ├─ 대지면적
  ├─ 토지가격
  ├─ 용도지역
  ├─ 건폐율 ❌ (모름)
  ├─ 용적률 ❌ (모름)
  ├─ 세대수 ❌ (모름)
  └─ 높이제한

↓

Normalization Layer
  └─ 그대로 사용 (자동화 없음)

↓

분석 엔진
```

### After (v9.1 - 목표)
```
사용자 입력 (4개 필드만)
  ├─ 주소
  ├─ 대지면적
  ├─ 토지가격
  └─ 용도지역

↓

Auto Input System (NEW!)
  ├─ AddressResolver
  │   └─ 주소 → 위도/경도 자동 변환
  │
  ├─ ZoningAutoMapper
  │   └─ 용도지역 → 건폐율/용적률 자동 설정
  │
  └─ UnitEstimator
      └─ 용적률 → 세대수 자동 계산

↓

Normalization Layer (Enhanced)
  └─ 모든 필드 자동 완성

↓

분석 엔진
```

---

## 🎯 v9.1 완료 기준

### 필수 기능
- [x] AddressResolverV9 구현
- [x] ZoningAutoMapperV9 구현
- [x] UnitEstimatorV9 구현
- [x] API 엔드포인트 추가
- [x] Normalization Layer 통합
- [x] Frontend UI 간소화

### 테스트 케이스
```
Input:
  - 주소: "서울 마포구 성산동 123-45"
  - 대지면적: 660㎡
  - 토지가격: 5,000,000,000원
  - 용도지역: "제3종일반주거지역"

Expected Output:
  ✅ 위도: 37.564123 (자동)
  ✅ 경도: 126.912345 (자동)
  ✅ 건폐율: 50% (자동)
  ✅ 용적률: 300% (자동)
  ✅ 세대수: 28세대 (자동)
  ✅ 층수: 6층 (자동)
  ✅ 주차: 28대 (자동)
```

---

## 📋 v9.1 타임라인

### Week 1 (1-2일)
- Day 1: AddressResolverV9 구현
- Day 2: API 엔드포인트 + 테스트

### Week 2 (1일)
- Day 3: ZoningAutoMapperV9 구현

### Week 3 (2-3일)
- Day 4-5: UnitEstimatorV9 구현
- Day 6: 통합 테스트

### Week 4 (1-2일)
- Day 7-8: Frontend UI 간소화
- Day 9: 최종 통합 테스트

**Total**: **7-9일** (약 1.5-2주)

---

## 🚀 즉시 시작 가능

### 준비 사항
1. ✅ Kakao REST API Key (기존 사용 중)
2. ✅ Redis (캐싱용, 기존 사용 중)
3. ✅ 용도지역 표 (국토부 기준)

### 첫 번째 구현: AddressResolverV9

**Step 1**: 서비스 파일 생성
```bash
touch app/services_v9/address_resolver_v9_0.py
```

**Step 2**: 기본 구조 작성
```python
from typing import Optional
import httpx
from app.core.config import settings

class AddressResolverV9:
    """주소 정규화 및 좌표 획득"""
    
    def __init__(self):
        self.kakao_api_key = settings.KAKAO_REST_API_KEY
        self.base_url = "https://dapi.kakao.com/v2/local"
    
    async def resolve_address(self, address: str):
        """주소 → 좌표 변환"""
        # 구현
        pass
```

---

## ⚠️ Critical Issues 해결 우선순위

### 현재 v9.0 Critical Issues (from expert review)
1. 🔴 Financial Engine 비현실적 수치 (HIGH)
2. 🟠 Grade System 비표준 (MEDIUM)
3. 🔴 Frontend Integration 오류 (HIGH)

### v9.1 자동화 시스템 추가
4. 🔴 **주소 자동 변환 미구현 (HIGH)** ← NEW
5. 🔴 **세대수 자동 계산 미구현 (HIGH)** ← NEW
6. 🟠 **용적률/건폐율 자동 설정 미구현 (MEDIUM)** ← NEW

**권장 순서**:
1. ✅ v9.1 자동화 시스템 구현 (사용성 최우선)
2. ✅ Financial Engine 수정 (정확성)
3. ✅ Frontend Integration 수정 (안정성)
4. ✅ Grade System 표준화 (일관성)

---

## 📞 최종 권고

**ZeroSite v9.0의 가장 큰 문제는 "사용성 저하"**입니다.

v7.5에서 제공하던 **3대 자동화 기능**이 사라지면서:
- 일반 사용자 진입 장벽 ↑↑
- 필수 입력 항목 10개 → 사용 포기
- "간편 분석"이라는 브랜드 정체성 상실

**v9.1 자동화 시스템 복구는 필수**이며, **다른 모든 개선보다 우선**해야 합니다.

**즉시 시작 가능:**
1. AddressResolverV9 구현 (1-2일)
2. ZoningAutoMapperV9 구현 (1일)
3. UnitEstimatorV9 구현 (2-3일)
4. Frontend UI 간소화 (1-2일)

**Total**: 약 **1.5-2주면 v9.1 배포 가능**

---

**Date**: 2025-12-04  
**Status**: **PLANNING COMPLETE**  
**Priority**: **CRITICAL (Higher than v9.0 bugs)**  
**Target**: **v9.1 Release in 2 weeks**  
**Recommendation**: **START IMMEDIATELY** 🚀
