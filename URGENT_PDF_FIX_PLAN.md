# 🚨 ZeroSite v7.2 PDF Report - 긴급 수정 계획

## 현황 분석

**문제의 파일**: `app/services/lh_official_report_generator.py` (3,395 lines)
- 이 파일이 실제 PDF/HTML 보고서 생성
- 5.0 만점 시스템 사용 (v7.2 점수 체계와 다름)
- 하드코딩된 더미 값 다수 존재

---

## 12가지 문제 및 수정 방법

### ❗ FIX 1: POI 데이터 (편의시설/버스/지하철/학교/병원) 실제 엔진 값으로 교체

**문제**:
- PDF p.3, p.5: "생활편의시설: 3개 확인"
- PDF p.8: "지하철 3개소, 버스정류장 0개소 확인"
- PDF p.9: "편의점, 음식점 등 0개소 이상 분포"

**실제 엔진 값**:
- 편의시설 245개, 버스 107개, 지하철 3개, 학교 42개, 병원 19개

**수정 위치**:
- Line 1834: `생활편의시설 {facilities_count}개 확인`
- Line 1895: `• 생활편의시설: {facilities_count}개 확인`
- Line 866: `총 {len(facilities)}개의 주요 생활편의시설`

**수정 방법**:
```python
# 현재:
facilities = data.get('facilities', [])  # 하드코딩된 빈 리스트
facilities_count = len(facilities)

# 수정:
poi_data = data.get('poi_analysis_v3_1', {})
pois = poi_data.get('pois', {})
convenience_count = len([p for k, p in pois.items() if 'convenience' in k.lower() or 'restaurant' in k.lower()])
bus_count = sum([p.get('count', 0) for k, p in pois.items() if 'bus' in k.lower()])
subway_count = sum([p.get('count', 0) for k, p in pois.items() if 'subway' in k.lower()])
school_count = sum([p.get('count', 0) for k, p in pois.items() if 'school' in k.lower()])
hospital_count = sum([p.get('count', 0) for k, p in pois.items() if 'hospital' in k.lower()])
```

---

### ❗ FIX 2: 레이더 차트 더미 값(32/12/24/18/16) 완전 제거

**문제**:
- PDF p.6 레이더차트: 인구통계 32.0, 접근성 12.0, 시장규모 24.0, 규제환경 18.0, 주변환경 16.0
- 이것은 개발 초기 더미 값

**수정 위치**:
- `chart_service.py` 또는 레이더 차트 생성 부분

**수정 방법**:
```python
# 현재: 하드코딩된 값
radar_data = [32.0, 12.0, 24.0, 18.0, 16.0]

# 수정: v7.2 엔진 값 사용
poi = data.get('poi_analysis_v3_1', {})
td = data.get('type_demand_v3_1', {})
geo = data.get('geo_optimizer_v3_1', {})
risk = data.get('risk_analysis_2025', {})

radar_data = [
    min(max(0, poi.get('total_score_v3_1', 0)), 100),  # 생활편의성
    min(max(0, geo.get('final_score', 0)), 100),        # 접근성
    min(max(0, user_demand_score), 100),                # 수요강도
    max(0, min(100, 100 - (risk.get('risk_score', 20) * 5))),  # 규제환경
    min(max(0, geo.get('optimization_score', 0)), 100)  # 미래가치
]
```

---

### ❗ FIX 3: 인구 데이터 더미 값 제거

**문제**:
- PDF p.5, p.8, p.20, p.21: 총 인구 500,000명, 청년 150,000명 → 전국 평균 추정치 (가짜)

**수정 방법**:
```python
# 현재:
total_population = 500000
youth_population = 150000

# 수정:
demographic = data.get('demographic_info', {})
total_population = demographic.get('total_population', None)
youth_population = demographic.get('youth_population', None)

# PDF 표시:
if total_population is None:
    population_text = "인구 데이터: API 미연결 (행정안전부 API 연동 대기 중)"
else:
    population_text = f"총 인구: {total_population:,}명"
```

---

### ❗ FIX 4: 교통 점수 2.0/5.0 제거, GeoOptimizer 점수로 교체

**문제**:
- PDF p.3: 교통편의성 2.0/5.0

**수정 위치**:
- Line 306-309: `_score_transit()` 메서드

**수정 방법**:
```python
# 현재:
def _score_transit(self, data: Dict[str, Any]) -> float:
    return 2.0  # 하드코딩

# 수정:
def _score_transit(self, data: Dict[str, Any]) -> float:
    geo = data.get('geo_optimizer_v3_1', {})
    geo_score = geo.get('final_score', 0)
    # 0-100 scale을 0-5 scale로 변환
    return min(5.0, geo_score / 20.0)
```

---

### ❗ FIX 5: LH 5점 만점 평가표 제거, v7.2 점수 체계로 교체

**문제**:
- 전체 보고서가 5.0 만점 시스템 사용
- v7.2는 0-100 점수 + S/A/B/C/D 등급 시스템

**수정 방법**:
1. `_calculate_5point_scores()` 메서드를 `_calculate_v7_2_scores()`로 변경
2. 모든 5.0 만점 텍스트를 v7.2 점수로 변경

```python
def _calculate_v7_2_scores(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """v7.2 점수 체계 계산 (0-100 + 등급)"""
    poi = analysis_data.get('poi_analysis_v3_1', {})
    td = analysis_data.get('type_demand_v3_1', {})
    geo = analysis_data.get('geo_optimizer_v3_1', {})
    risk = analysis_data.get('risk_analysis_2025', {})
    lh = analysis_data.get('lh_assessment', {})
    
    return {
        'poi': {
            'score': poi.get('total_score_v3_1', 0),
            'grade': poi.get('lh_grade', 'N/A'),
            'max': 100
        },
        'type_demand': {
            'score': td.get('main_score', 0),
            'grade': td.get('demand_level', 'N/A'),
            'max': 100
        },
        'geo_optimizer': {
            'score': geo.get('final_score', 0),
            'grade': self._get_score_grade(geo.get('final_score', 0)),
            'max': 100
        },
        'risk': {
            'score': risk.get('risk_score', 20),
            'grade': risk.get('risk_level', 'N/A'),
            'max': 20
        },
        'lh_final': {
            'score': lh.get('total_score', 0),
            'grade': lh.get('grade', 'N/A'),
            'max': 100
        }
    }
```

---

### ❗ FIX 6-11: 기타 수정 사항

**FIX 6**: 사업 일정/LH 절차 - 데이터 기반으로 변경 (중요도: Medium)
**FIX 7**: 학교/병원 접근성 - POI 데이터에서 가져오기
**FIX 8**: 레이더 차트 축 단위 - LH 기준에 맞게 수정
**FIX 9**: '사회적기업(주)안테나' → 'ZeroSite'로 전역 치환
**FIX 10**: LH 체크리스트 - risk_table_v2025 데이터 매핑
**FIX 11**: 리스크 점수 - PDF에 명시적으로 표시

---

## 실행 계획

### Phase 1: 긴급 수정 (High Priority)
1. ✅ '안테나' → 'ZeroSite' 전역 치환
2. ✅ 레이더 차트 더미 값 제거
3. ✅ POI 데이터 실제 값으로 교체
4. ✅ 5.0 만점 → v7.2 점수 체계로 전환

### Phase 2: 데이터 매핑 완성
5. ✅ 인구 데이터 API 미연결 표시
6. ✅ 교통 점수 GeoOptimizer 연동
7. ✅ LH 체크리스트 데이터 매핑
8. ✅ 리스크 점수 표시

### Phase 3: 최종 검증
9. ✅ 전체 PDF 생성 테스트
10. ✅ v7.2 엔진 데이터 일치율 검증 (목표: 95%+)

---

## 예상 소요 시간

- Phase 1: 30-45분 (긴급 수정)
- Phase 2: 45-60분 (데이터 매핑)
- Phase 3: 15-30분 (검증)
- **총 예상 시간**: 1.5-2.5시간

---

## 우선순위 정리

**즉시 수정 필요 (Critical)**:
1. 레이더 차트 더미 값
2. POI 데이터 오류
3. '안테나' → 'ZeroSite'
4. 5.0 만점 → v7.2 점수

**중요 (High)**:
5. 교통 점수 연동
6. 인구 데이터 처리
7. 리스크 점수 표시
8. LH 체크리스트

**개선 사항 (Medium)**:
9. 사업 일정 자동화
10. 학교/병원 접근성
11. 레이더 축 단위
12. 전체 구조 최적화

---

**작성자**: AI Assistant
**작성일**: 2025-12-01
**목표**: v7.2 엔진 데이터 일치율 70% → 95%+
