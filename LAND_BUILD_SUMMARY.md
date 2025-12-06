# 🎯 토지/건축규모 검토 핵심 요약

## 현재 시스템 구조

```
입력 (4개)
   ↓
주소 → 좌표 변환 (Kakao API)
   ↓
용도지역 → 건폐율/용적률 (ZoningMapper)
   ↓
대지면적 + 용적률 → 세대수/층수 (UnitEstimator)
   ↓
결과 반환
```

---

## 📊 현재 기본값

| 항목 | 현재값 | 파일 위치 |
|------|--------|-----------|
| **평균 세대 면적** | 60㎡ | `unit_estimator_v9_0.py` 라인 86 |
| **주거/상업 비율** | 85% / 15% | `unit_estimator_v9_0.py` 라인 91-92 |
| **세대 유형** | 59㎡(60%) + 74㎡(30%) + 84㎡(10%) | `unit_estimator_v9_0.py` 라인 102-106 |

### 용도지역별 건축 기준

| 용도지역 | 건폐율 | 용적률 | 최대층수 | 주차비율 |
|----------|--------|--------|----------|----------|
| 제1종일반주거지역 | 60% | 200% | 4층 | 0.8대/세대 |
| 제2종일반주거지역 | 60% | 250% | 7층 | 1.0대/세대 |
| 제3종일반주거지역 | 50% | 300% | 15층 | 1.0대/세대 |
| 준주거지역 | 70% | 500% | 20층 | 1.2대/세대 |

---

## 🔧 빠른 수정 가이드

### 1️⃣ 평균 세대 면적 변경 (예: 60㎡ → 50㎡)

**파일**: `/home/user/webapp/app/services_v9/unit_estimator_v9_0.py`  
**라인**: 86

```python
# 현재
DEFAULT_UNIT_AREA = 60.0  # m² (약 18평)

# 변경
DEFAULT_UNIT_AREA = 50.0  # m² (약 15평)
```

**영향**: 세대수 증가 (같은 연면적에서 더 많은 세대 수용)

---

### 2️⃣ 용도지역별 용적률 변경 (예: 제2종일반 200% → 250%)

**파일**: `/home/user/webapp/app/services_v9/zoning_auto_mapper_v9_0.py`  
**라인**: 92-98

```python
# 현재
"제2종일반주거지역": {
    "building_coverage_ratio": 60.0,
    "floor_area_ratio": 250.0,  # ← 여기 수정
    "max_height": None,
    "parking_ratio": 1.0,
    "description": "중층 주택 위주 지역"
},
```

**영향**: 총 연면적 증가 → 세대수 증가

---

### 3️⃣ 주차대수 비율 변경 (예: 제2종일반 1.0 → 1.2대/세대)

**파일**: `/home/user/webapp/app/services_v9/unit_estimator_v9_0.py`  
**라인**: 120-130

```python
# 현재
ZONE_PARKING_RATIOS = {
    "제1종일반주거지역": 0.8,
    "제2종일반주거지역": 1.0,  # ← 여기 수정 (예: 1.0 → 1.2)
    "제3종일반주거지역": 1.0,
    ...
}
```

**영향**: 세대당 주차대수 증가

---

### 4️⃣ 최대 층수 제한 변경 (예: 제2종일반 7층 → 10층)

**파일**: `/home/user/webapp/app/services_v9/unit_estimator_v9_0.py`  
**라인**: 109-118

```python
# 현재
ZONE_MAX_FLOORS = {
    "제1종일반주거지역": 4,
    "제2종일반주거지역": 7,  # ← 여기 수정 (예: 7 → 10)
    "제3종일반주거지역": 15,
    ...
}
```

**영향**: 층수 증가 가능 (하지만 용적률 제약은 여전히 적용됨)

---

### 5️⃣ 주거/상업 비율 변경 (예: 85/15 → 80/20)

**파일**: `/home/user/webapp/app/services_v9/unit_estimator_v9_0.py`  
**라인**: 90-92

```python
# 현재
COMMERCIAL_RATIO = 0.15   # 15%
RESIDENTIAL_RATIO = 0.85  # 85%

# 변경
COMMERCIAL_RATIO = 0.20   # 20%
RESIDENTIAL_RATIO = 0.80  # 80%
```

**영향**: 주거 연면적 감소 → 세대수 감소

---

## 🧪 테스트 절차

### 1단계: 코드 수정

```bash
# 예: 평균 세대 면적을 50㎡로 변경
nano /home/user/webapp/app/services_v9/unit_estimator_v9_0.py
# 라인 86: DEFAULT_UNIT_AREA = 50.0
```

### 2단계: 서버 재시작

```bash
cd /home/user/webapp
pkill -9 -f "uvicorn.*8003"
sleep 3
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8003 &
sleep 5
curl -s http://localhost:8003/health | jq
```

### 3단계: API 테스트

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

### 4단계: 결과 확인

```json
{
  "unit_count": 45,           // ← 세대수
  "floors": 7,                // ← 층수
  "parking_spaces": 45,       // ← 주차대수
  "total_gfa": 3000.0,        // ← 총 연면적
  "residential_gfa": 2550.0,  // ← 주거 연면적
  "building_coverage_ratio": 60.0,
  "floor_area_ratio": 250.0
}
```

---

## 📁 파일 위치 총정리

```
/home/user/webapp/
├── app/
│   ├── api/endpoints/
│   │   └── analysis_v9_1_REAL.py         # 메인 API (STEP 1~3)
│   └── services_v9/
│       ├── unit_estimator_v9_0.py        # 세대수/층수/주차 계산
│       └── zoning_auto_mapper_v9_0.py    # 용도지역 → 건폐율/용적률
├── LAND_BUILD_QUICK_REF.md               # 상세 가이드
└── LAND_BUILD_SUMMARY.md                 # 이 파일 (요약)
```

---

## 🚨 주의사항

1. **파일 수정 후 반드시 서버 재시작** (Python 모듈 캐싱)
2. **Git 커밋 필수**
   ```bash
   cd /home/user/webapp
   git add -A
   git commit -m "fix: 토지/건축규모 계산 로직 수정"
   git push origin main
   ```
3. **수정 전 백업 권장**
   ```bash
   cp app/services_v9/unit_estimator_v9_0.py app/services_v9/unit_estimator_v9_0.py.backup
   ```

---

## 💡 실전 예시

### 예시 1: 소형 세대 중심으로 변경 (60㎡ → 45㎡)

```python
# unit_estimator_v9_0.py 라인 86
DEFAULT_UNIT_AREA = 45.0  # 기존 60 → 45

# 예상 효과:
# - 같은 연면적에서 세대수 약 33% 증가
# - 1200㎡ 대지, 용적률 250% 기준
#   기존: 약 42세대 → 변경 후: 약 56세대
```

### 예시 2: 제2종일반주거지역 용적률 상향 (250% → 300%)

```python
# zoning_auto_mapper_v9_0.py 라인 94
"floor_area_ratio": 300.0,  # 기존 250 → 300

# 예상 효과:
# - 총 연면적 20% 증가
# - 1200㎡ 대지 기준
#   기존: 3000㎡ → 변경 후: 3600㎡
# - 세대수 약 20% 증가
#   기존: 42세대 → 변경 후: 약 51세대
```

### 예시 3: 주차대수 증가 (1.0 → 1.5대/세대)

```python
# unit_estimator_v9_0.py 라인 123
"제2종일반주거지역": 1.5,  # 기존 1.0 → 1.5

# 예상 효과:
# - 주차대수 50% 증가
# - 42세대 기준
#   기존: 42대 → 변경 후: 63대
```

---

## 🎯 다음 단계

수정하고 싶은 내용을 알려주시면:
1. 해당 파일 열기
2. 정확한 라인 확인
3. 코드 수정 적용
4. 서버 재시작
5. 결과 검증

바로 진행하겠습니다!

---

**저장 완료: 2025-12-06**
**서버 URL**: https://8003-ismcj42l609zyihh62150-ad490db5.sandbox.novita.ai
