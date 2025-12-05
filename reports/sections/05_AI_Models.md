# 5. AI 모델 및 알고리즘

## 5.1 Type-specific Demand Scoring Model

### 알고리즘 개요
각 주거 유형(청년, 신혼I/II, 다자녀, 고령자 등)에 대해 독립적으로 수요 점수를 산정하는 모델입니다.

### 청년형 점수 산정식
```python
def calculate_youth_score(data):
    score = 0
    
    # 지하철 접근성 (최대 25점)
    if subway_distance <= 500:
        score += 25
    elif subway_distance <= 1000:
        score += 15
    
    # 대학 근접도 (최대 15점)
    if university_distance <= 2000:
        score += 15
    
    # 청년 인구 비율 (최대 20점)
    score += min(youth_ratio * 0.8, 20)
    
    # 상업시설 접근성 (최대 15점)
    commercial_score = evaluate_commercial_access()
    score += commercial_score
    
    return min(score, 100)
```

### 신혼·신생아형 점수 산정식
```python
def calculate_newlywed_score(data):
    score = 0
    
    # 초등학교 접근성 (최대 25점)
    if school_distance <= 400:
        score += 25
    elif school_distance <= 800:
        score += 15
    
    # 어린이집 접근성 (최대 20점)
    if daycare_distance <= 500:
        score += 20
    
    # 공원 접근성 (최대 20점)
    if park_distance <= 500:
        score += 20
    
    return min(score, 100)
```

## 5.2 Geo Optimization Algorithm

### 4방향 탐색 알고리즘
```python
def find_alternative_sites(lat, lng, radius_km=3):
    candidates = []
    directions = ['NORTH', 'EAST', 'SOUTH', 'WEST']
    
    for direction in directions:
        # 각 방향으로 후보지 탐색
        sites = search_direction(lat, lng, direction, radius_km)
        candidates.extend(sites[:2])  # 방향당 최대 2개
    
    # 점수 계산
    for site in candidates:
        site.score = calculate_optimization_score(site)
    
    # 상위 3~5개 반환
    return sorted(candidates, key=lambda x: x.score, reverse=True)[:5]
```

**Watermark**: ZeroSite | ZeroSite Land Report v5.0 | AI Models | Page 6
