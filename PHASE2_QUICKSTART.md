# ⚡ Phase 2 빠른 시작 가이드

## 🎯 새창에서 바로 시작하기

### 📍 현재 위치 확인
```bash
cd /home/user/webapp
git branch
# 출력: * phase2/business-simulation
```

---

## 🚀 1분 안에 시작하기

### Step 1: 환경 확인
```bash
cd /home/user/webapp && pwd
# /home/user/webapp

git log --oneline -1
# 36760ff fix: 보고서 생성기에서 dict 접근 방식으로 변경

git branch
# * phase2/business-simulation
```

### Step 2: 서버 상태 확인
```bash
ps aux | grep uvicorn | grep -v grep
# user  2083  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**서버 URL**: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai

---

## 📦 바로 개발 시작

### Option A: 백엔드부터 시작

```bash
# 1. 비즈니스 시뮬레이션 모듈 생성
cd /home/user/webapp
mkdir -p app/modules/business_simulation

# 2. 기본 파일 생성
cd app/modules/business_simulation
touch __init__.py models.py construction_cost.py purchase_price.py roi_calculator.py service.py

# 3. 에디터로 열어서 개발 시작!
```

**개발 순서:**
1. `models.py` - 데이터 모델 (Pydantic)
2. `construction_cost.py` - 건축비 계산
3. `purchase_price.py` - LH 매입가
4. `roi_calculator.py` - ROI/IRR
5. `service.py` - 비즈니스 로직 통합

### Option B: 프론트엔드부터 시작

```bash
# 1. React 프로젝트 초기화
cd /home/user/webapp
npm create vite@latest frontend -- --template react

# 2. 의존성 설치
cd frontend
npm install react-bootstrap bootstrap chart.js react-chartjs-2

# 3. 개발 서버 실행
npm run dev
```

---

## 🎨 첫 번째 기능: 건축비 계산기

### 1. 데이터 모델 작성

**파일**: `app/modules/business_simulation/models.py`

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class UnitType(str, Enum):
    YOUTH = "YOUTH"
    NEWLYWED = "NEWLYWED"
    PUBLIC_RENTAL = "PUBLIC_RENTAL"

class CostCalculationRequest(BaseModel):
    """건축비 계산 요청"""
    unit_type: UnitType
    gross_area: float = Field(gt=0, description="연면적 (㎡)")
    region: str = Field(description="지역명")
    num_units: int = Field(gt=0, description="총 세대수")

class CostBreakdown(BaseModel):
    """공사 항목별 비용"""
    civil: float = Field(description="토목공사비")
    architecture: float = Field(description="건축공사비")
    mechanical: float = Field(description="기계설비비")
    electrical: float = Field(description="전기공사비")
    landscaping: float = Field(description="조경공사비")
    others: float = Field(description="기타 비용")

class CostCalculationResponse(BaseModel):
    """건축비 계산 결과"""
    total_cost: float = Field(description="총 건축비")
    cost_per_pyeong: float = Field(description="평당 건축비")
    cost_breakdown: CostBreakdown
    additional_costs: float = Field(description="부대비용 (설계/감리 등)")
    grand_total: float = Field(description="총 사업비")
```

### 2. 건축비 계산 로직

**파일**: `app/modules/business_simulation/construction_cost.py`

```python
from .models import *

class ConstructionCostCalculator:
    """건축비 자동 산정"""
    
    # 2025년 기준 표준 건축비 (평당, 원)
    BASE_COSTS = {
        UnitType.YOUTH: 1_200_000,
        UnitType.NEWLYWED: 1_300_000,
        UnitType.PUBLIC_RENTAL: 1_100_000,
    }
    
    # 지역별 할증률
    REGIONAL_MULTIPLIERS = {
        "서울": 1.20,
        "경기": 1.10,
        "인천": 1.05,
        "세종": 1.08,
        "대전": 1.03,
        "대구": 1.03,
        "부산": 1.05,
        "광주": 1.02,
        "울산": 1.03,
    }
    
    # 공사 항목별 배분율
    COST_RATIOS = {
        "civil": 0.15,
        "architecture": 0.50,
        "mechanical": 0.15,
        "electrical": 0.10,
        "landscaping": 0.05,
        "others": 0.05,
    }
    
    def calculate(self, request: CostCalculationRequest) -> CostCalculationResponse:
        """건축비 계산"""
        
        # 1. 기본 평당 단가
        base_cost = self.BASE_COSTS[request.unit_type]
        
        # 2. 지역 할증률
        regional_multiplier = self.REGIONAL_MULTIPLIERS.get(
            request.region.split()[0],  # "서울특별시" -> "서울"
            1.0  # 기본값
        )
        
        # 3. 연면적을 평으로 변환 (1평 = 3.3㎡)
        total_pyeong = request.gross_area / 3.3
        
        # 4. 총 건축비 계산
        total_cost = base_cost * total_pyeong * regional_multiplier
        
        # 5. 공사 항목별 비용 산출
        breakdown = CostBreakdown(
            civil=total_cost * self.COST_RATIOS["civil"],
            architecture=total_cost * self.COST_RATIOS["architecture"],
            mechanical=total_cost * self.COST_RATIOS["mechanical"],
            electrical=total_cost * self.COST_RATIOS["electrical"],
            landscaping=total_cost * self.COST_RATIOS["landscaping"],
            others=total_cost * self.COST_RATIOS["others"],
        )
        
        # 6. 부대비용 (총 건축비의 10%)
        additional_costs = total_cost * 0.10
        
        # 7. 총 사업비
        grand_total = total_cost + additional_costs
        
        return CostCalculationResponse(
            total_cost=round(total_cost),
            cost_per_pyeong=round(base_cost * regional_multiplier),
            cost_breakdown=breakdown,
            additional_costs=round(additional_costs),
            grand_total=round(grand_total),
        )
```

### 3. API 엔드포인트 추가

**파일**: `app/api/endpoints/business.py` (새로 생성)

```python
from fastapi import APIRouter, HTTPException
from app.modules.business_simulation.models import *
from app.modules.business_simulation.construction_cost import ConstructionCostCalculator

router = APIRouter(prefix="/api/business", tags=["business-simulation"])

@router.post("/calculate-cost", response_model=CostCalculationResponse)
async def calculate_construction_cost(request: CostCalculationRequest):
    """
    건축비 자동 산정
    
    - **unit_type**: 주택 유형 (YOUTH/NEWLYWED/PUBLIC_RENTAL)
    - **gross_area**: 연면적 (㎡)
    - **region**: 지역명 (예: 서울특별시, 경기도)
    - **num_units**: 총 세대수
    """
    try:
        calculator = ConstructionCostCalculator()
        result = calculator.calculate(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4. 메인 앱에 라우터 등록

**파일**: `app/main.py` (수정)

```python
# 기존 imports...
from app.api.endpoints import business  # 추가

# 기존 router includes...
app.include_router(business.router)  # 추가
```

### 5. 테스트

```bash
# 서버 재시작
cd /home/user/webapp
# Ctrl+C로 기존 서버 종료 후
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**curl 테스트:**
```bash
curl -X POST "http://localhost:8000/api/business/calculate-cost" \
  -H "Content-Type: application/json" \
  -d '{
    "unit_type": "YOUTH",
    "gross_area": 1000,
    "region": "서울특별시",
    "num_units": 20
  }'
```

**예상 결과:**
```json
{
  "total_cost": 436363636,
  "cost_per_pyeong": 1440000,
  "cost_breakdown": {
    "civil": 65454545,
    "architecture": 218181818,
    "mechanical": 65454545,
    "electrical": 43636363,
    "landscaping": 21818181,
    "others": 21818181
  },
  "additional_costs": 43636363,
  "grand_total": 480000000
}
```

---

## 🎯 다음 할 일

### 즉시 진행 가능한 작업

1. **건축비 계산기 완성** ✅ (위 코드 복사)
2. **LH 매입가 시뮬레이터** (다음 단계)
3. **ROI/IRR 계산기** (그 다음)

### 상세 가이드

전체 개발 계획은 `PHASE2_GUIDE.md` 참조

---

## 🐛 문제 해결

### 서버가 실행되지 않는 경우
```bash
# 프로세스 확인
ps aux | grep uvicorn

# 포트 사용 중인 경우
kill -9 <PID>

# 재시작
cd /home/user/webapp && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Import 오류
```bash
# 모듈 경로 확인
cd /home/user/webapp
find . -name "*.py" -path "*/business_simulation/*"

# __init__.py 확인
ls -la app/modules/business_simulation/__init__.py
```

---

## 📚 참고 문서

- **전체 가이드**: `PHASE2_GUIDE.md`
- **아키텍처**: `PLATFORM_ARCHITECTURE.md`
- **Phase 1 완료**: Tag `v2.0-stable`

---

## ✅ 현재 상태 스냅샷

```
Branch: phase2/business-simulation
Commit: 36760ff (v2.0-stable)
Server: Running (PID: 2083, Port: 8000)
Status: Ready for Phase 2 development

Phase 1 완료:
✅ 토지진단 시스템
✅ 정책 모니터링
✅ 프로젝트 관리
✅ 보고서 생성
✅ 회사 브랜딩

Phase 2 목표:
⏳ 건축비 계산
⏳ LH 매입가 시뮬레이션
⏳ ROI/IRR 분석
⏳ React 대시보드
```

---

**시작 준비 완료! 🚀**

새창을 열고 위의 코드를 복사하여 개발을 시작하세요!
