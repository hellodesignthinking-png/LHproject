# ZeroSite v7.2 Engine Output Field Mapping

**Generated:** 2025-12-01
**Purpose:** Complete field mapping for Report Engine v7.2 upgrade

---

## CORE ANALYSIS

| Field Name | Type & Description |
|------------|--------------------|
| `analysis_id` | str - 분석 ID |
| `timestamp` | str (ISO timestamp) - 분석 시간 |
| `address` | str - 분석 주소 |
| `coordinates` | Dict (lat, lng) - 좌표 |
| `area` | float (sqm) - 면적 |
| `zoning_type` | str - 용도지역 |
| `unit_type` | str - 주거 유형 |
| `lh_score` | float (0-100) - LH 점수 |
| `lh_grade` | str (A/B/C) - LH 등급 |
| `lh_version` | str (2024/2025) - LH 기준 버전 |
| `overall_suitability` | str (적합/검토필요/부적합) - 종합 적합성 |
| `recommendation` | str - 추천 사항 |
| `risk_factors` | List[Dict] - 리스크 요인 |
| `risk_count` | int - 리스크 개수 |
| `estimated_units` | int - 예상 세대수 |
| `estimated_floors` | int - 예상 층수 |
| `building_coverage_ratio` | float (%) - 건폐율 |
| `floor_area_ratio` | float (%) - 용적률 |
| `negotiation_strategies` | List[str] - 협상 전략 (8개) |
| `final_score_after_strategy` | float - 전략 반영 후 최종 점수 |

## TYPE DEMAND V3 1

| Field Name | Type & Description |
|------------|--------------------|
| `type_demand_score` | float (0-100) - 유형별 수요 점수 |
| `type_demand_grade` | str (높음/보통/낮음) - 수요 등급 |
| `청년_score` | float - 청년주택 수요 점수 |
| `신혼신생아I_score` | float - 신혼·신생아 I 점수 |
| `신혼신생아II_score` | float - 신혼·신생아 II 점수 |
| `다자녀_score` | float - 다자녀 점수 |
| `고령자_score` | float - 고령자 점수 |
| `일반_score` | float - 일반 점수 (if applicable) |
| `든든전세_score` | float - 든든전세 점수 (if applicable) |
| `lh_2025_weights_applied` | bool - LH 2025 가중치 적용 여부 |
| `poi_distance_weight` | float - POI 거리 가중치 |
| `school_distance` | float (meters) - 학교까지 거리 |
| `hospital_distance` | float (meters) - 병원까지 거리 |
| `station_distance` | float (meters) - 역까지 거리 |
| `market_distance` | float (meters) - 시장까지 거리 |
| `youth_population_ratio` | float (0-100%) - 청년인구 비율 |
| `household_growth_rate` | float (%) - 가구증가율 |
| `accessibility_score` | float (0-100) - 접근성 점수 |
| `drainage_optimization_score` | float - 배수시설 최적화 점수 |
| `drainage_quality` | str (good/fair/poor) - 배수시설 품질 |

## GEO OPTIMIZER V3 1

| Field Name | Type & Description |
|------------|--------------------|
| `geo_optimizer_score` | float (0-100) - 지리적 최적화 점수 |
| `optimization_grade` | str (excellent/good/fair/poor) - 최적화 등급 |
| `alternative_locations` | List[Dict] - 3개 대안 입지 |
| `alt_1_lat` | float - 대안1 위도 |
| `alt_1_lng` | float - 대안1 경도 |
| `alt_1_score` | float - 대안1 점수 |
| `alt_1_distance` | float (meters) - 대안1 거리 |
| `alt_2_lat` | float - 대안2 위도 |
| `alt_2_lng` | float - 대안2 경도 |
| `alt_2_score` | float - 대안2 점수 |
| `alt_2_distance` | float (meters) - 대안2 거리 |
| `alt_3_lat` | float - 대안3 위도 |
| `alt_3_lng` | float - 대안3 경도 |
| `alt_3_score` | float - 대안3 점수 |
| `alt_3_distance` | float (meters) - 대안3 거리 |
| `poi_density_score` | float - POI 밀도 점수 |
| `total_pois_nearby` | int - 주변 POI 개수 |
| `poi_diversity_index` | float - POI 다양성 지수 |
| `distance_penalty_factor` | float (0-1) - 거리 페널티 계수 |
| `accessibility_bonus` | float - 접근성 보너스 |

## MULTI PARCEL V3 0

| Field Name | Type & Description |
|------------|--------------------|
| `parcel_count` | int (2-10) - 분석 필지 개수 |
| `total_area` | float (sqm) - 총 면적 |
| `center_point_lat` | float - 중심점 위도 (면적 가중평균) |
| `center_point_lng` | float - 중심점 경도 (면적 가중평균) |
| `center_point_method` | str (geometric_centroid) - 중심점 계산 방법 |
| `shape_compactness_ratio` | float (0-1) - 형태 밀집도 비율 |
| `shape_quality` | str (excellent/good/fair/poor) - 형태 품질 |
| `shape_penalty_factor` | float (0.8-1.0) - 형태 페널티 계수 |
| `boundary_irregularity` | float (0-1) - 경계 불규칙성 |
| `dominant_zoning_type` | str - 주 용도지역 |
| `zoning_consistency` | str (uniform/mixed) - 용도지역 일관성 |
| `mixed_zones` | bool - 혼합 용도지역 여부 |
| `dominant_zoning_ratio` | float (0-1) - 주 용도지역 비율 |
| `combined_lh_score` | float (0-100) - 결합 LH 점수 |
| `combined_lh_grade` | str (A/B/C) - 결합 LH 등급 |
| `weighted_base_score` | float - 가중 기본 점수 |
| `shape_penalty_applied` | float - 적용된 형태 페널티 |
| `individual_parcels` | List[Dict] - 개별 필지 정보 |
| `parcel_contribution_ratios` | List[float] - 필지별 기여도 |

## LH NOTICE LOADER V2 1

| Field Name | Type & Description |
|------------|--------------------|
| `notice_id` | str - 공고 ID |
| `notice_title` | str - 공고 제목 |
| `published_date` | str (ISO date) - 발행일 |
| `category` | str - 카테고리 |
| `region` | str - 지역 |
| `parsed_content` | Dict - 파싱된 내용 |
| `extraction_method` | str (pdfplumber) - 추출 방법 |
| `extraction_confidence` | float (0-100%) - 추출 신뢰도 |
| `lh_eligibility_requirements` | List[str] - LH 적격 요건 |
| `lh_location_requirements` | Dict - 입지 요건 |
| `lh_price_limits` | Dict - 가격 제한 |
| `lh_notice_summary` | str - 공고 요약 |
| `lh_risk_flags` | List[str] - LH 리스크 플래그 |
| `lh_compatibility_score` | float (0-100) - LH 호환성 점수 |

## RATE LIMIT CACHE STATS

| Field Name | Type & Description |
|------------|--------------------|
| `api_retry_count` | int - API 재시도 횟수 |
| `circuit_breaker_state` | str (CLOSED/OPEN/HALF_OPEN) - 회로차단기 상태 |
| `provider_used` | str (kakao/naver/google) - 사용된 제공자 |
| `failover_occurred` | bool - 장애조치 발생 여부 |
| `total_api_calls` | int - 총 API 호출 횟수 |
| `failed_api_calls` | int - 실패한 API 호출 횟수 |
| `cache_hit_rate` | float (0-100%) - 캐시 적중률 |
| `cache_hits` | int - 캐시 히트 수 |
| `cache_misses` | int - 캐시 미스 수 |
| `cache_backend` | str (redis/memory) - 캐시 백엔드 |
| `cache_ttl_used` | Dict[str, int] - 서비스별 TTL |
| `analysis_start_time` | str (ISO timestamp) - 분석 시작 시간 |
| `analysis_end_time` | str (ISO timestamp) - 분석 종료 시간 |
| `total_analysis_duration` | float (seconds) - 총 분석 시간 |
| `avg_api_response_time` | float (ms) - 평균 API 응답시간 |

---

## Example v7.2 Engine Output

```json
{
  "analysis_id": "zerosite_20241201_abc123",
  "timestamp": "2025-12-01T12:00:00Z",
  "address": "서울특별시 강남구 역삼동 123-45",
  "coordinates": {
    "lat": 37.4979,
    "lng": 127.0276
  },
  "area": 660.0,
  "zoning_type": "제3종일반주거지역",
  "unit_type": "청년",
  "lh_score": 92.0,
  "lh_grade": "A",
  "lh_version": "2025",
  "type_demand_score": 88.2,
  "type_demand_grade": "높음",
  "lh_2025_weights_applied": true,
  "청년_score": 88.2,
  "신혼신생아I_score": 78.8,
  "고령자_score": 68.0,
  "poi_distance_weight": 0.35,
  "school_distance": 288.0,
  "hospital_distance": 179.0,
  "youth_population_ratio": 30.0,
  "accessibility_score": 65.0,
  "drainage_optimization_score": 85.0,
  "geo_optimizer_score": 82.0,
  "optimization_grade": "good",
  "alternative_locations": [
    {
      "lat": 37.498,
      "lng": 127.028,
      "score": 85.0,
      "distance": 120
    },
    {
      "lat": 37.4975,
      "lng": 127.027,
      "score": 83.0,
      "distance": 150
    },
    {
      "lat": 37.4985,
      "lng": 127.0285,
      "score": 81.0,
      "distance": 180
    }
  ],
  "poi_density_score": 78.0,
  "total_pois_nearby": 71,
  "distance_penalty_factor": 0.92,
  "api_retry_count": 2,
  "circuit_breaker_state": "CLOSED",
  "provider_used": "kakao",
  "failover_occurred": false,
  "cache_hit_rate": 65.0,
  "cache_backend": "redis",
  "total_analysis_duration": 1.2,
  "avg_api_response_time": 320.5,
  "overall_suitability": "검토 필요 - 조건부 적합",
  "estimated_units": 56,
  "estimated_floors": 6,
  "risk_factors": [],
  "negotiation_strategies": [
    "전략1",
    "전략2",
    "전략3",
    "전략4",
    "전략5",
    "전략6",
    "전략7",
    "전략8"
  ],
  "final_score_after_strategy": 91.6
}
```

---

## Field Mapping Notes

### 1. Obsolete v6.x Fields (DO NOT USE)
- `old_type_score` → use `type_demand_score`
- `simple_geo_score` → use `geo_optimizer_score`
- `basic_lh_score` → use `lh_score` + `lh_version`
- `mock_data_flag` → REMOVED (all real data)

### 2. New Required Fields (v7.2)
- `lh_2025_weights_applied` - MUST be True
- `cache_hit_rate` - Performance tracking
- `circuit_breaker_state` - Reliability indicator
- `shape_compactness_ratio` - Multi-parcel only

### 3. Conditional Fields
- Multi-Parcel fields: Only when `parcel_count` >= 2
- LH Notice fields: Only when LH notice analysis requested
- Alternative locations: Always 3 alternatives

---

*ZeroSite v7.2 Field Mapping - Complete*
