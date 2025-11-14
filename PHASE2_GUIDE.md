# 🚀 Phase 2 개발 가이드

## 📍 시작 포인트

### 현재 상태
- **브랜치**: `phase2/business-simulation`
- **기반 커밋**: `36760ff` (v2.0-stable 태그)
- **서버 상태**: 실행 중 (PID: 2083, Port: 8000)
- **URL**: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai

### 완료된 Phase 1 기능
- ✅ 토지진단 자동화 시스템
- ✅ LH 공식 보고서 생성
- ✅ 정책 모니터링 시스템 (LH/국토부 크롤러)
- ✅ 프로젝트 관리 시스템 (CRUD, Milestone, Risk)
- ✅ 회사 브랜딩 ((주)안테나)

---

## 🎯 Phase 2 개발 목표

### Module C: 사업성 시뮬레이션 도구

```
app/modules/business_simulation/
├── __init__.py
├── models.py              # 데이터 모델
├── construction_cost.py   # 건축비 산정
├── purchase_price.py      # 매입가 시뮬레이션
├── roi_calculator.py      # 수익률 계산
├── sensitivity.py         # 민감도 분석
└── service.py             # 비즈니스 로직
```

---

## 📐 1단계: 건축비 자동 산정

### 건축비 산정 로직

```python
# construction_cost.py

class ConstructionCostCalculator:
    """건축비 자동 산정"""
    
    # 2025년 기준 표준 건축비 (평당)
    BASE_COSTS = {
        "YOUTH": 1_200_000,      # 청년주택: 평당 120만원
        "NEWLYWED": 1_300_000,   # 신혼희망: 평당 130만원
        "PUBLIC_RENTAL": 1_100_000  # 공공임대: 평당 110만원
    }
    
    # 지역별 할증률
    REGIONAL_MULTIPLIER = {
        "서울": 1.2,
        "경기": 1.1,
        "인천": 1.05,
        "기타": 1.0
    }
    
    # 공사 종류별 비용
    COST_BREAKDOWN = {
        "토목공사": 0.15,      # 15%
        "건축공사": 0.50,      # 50%
        "기계설비": 0.15,      # 15%
        "전기공사": 0.10,      # 10%
        "조경공사": 0.05,      # 5%
        "기타": 0.05           # 5%
    }
```

### 핵심 계산식

```
총 건축비 = (연면적 × 평당 단가 × 지역 할증률) + 부대비용

부대비용 = 총 건축비 × 0.1 (설계비, 감리비, 인허가 등)
```

---

## 💰 2단계: LH 매입가 시뮬레이션

### LH 매입 방식 (2025년 기준)

```python
# purchase_price.py

class LHPurchaseCalculator:
    """LH 매입가 산정"""
    
    def calculate_purchase_price(self, project_data):
        """
        LH 매입가 = 토지비 + 건축비 + 적정이윤
        
        적정이윤 = (토지비 + 건축비) × 이윤율
        이윤율 = 7~10% (지역 및 사업 유형에 따라)
        """
        
        # 1. 토지 감정평가액
        land_value = self.get_land_appraisal_value()
        
        # 2. 건축비
        construction_cost = self.calculate_construction_cost()
        
        # 3. 적정이윤 (사업 유형별 차등)
        profit_rate = self.get_profit_rate(project_type)
        profit = (land_value + construction_cost) * profit_rate
        
        # 4. 총 매입가
        total_purchase = land_value + construction_cost + profit
        
        return {
            "land_value": land_value,
            "construction_cost": construction_cost,
            "profit": profit,
            "total_purchase": total_purchase,
            "unit_price_per_pyeong": total_purchase / total_pyeong
        }
```

### LH 매입 조건

```python
# LH 매입 기준 (2025)
PURCHASE_CRITERIA = {
    "YOUTH": {
        "max_area_per_unit": 60,      # 전용 60㎡ 이하
        "profit_rate": 0.08,            # 8% 적정이윤
        "min_units": 10,                # 최소 10세대
        "location": ["서울", "경기", "인천"]
    },
    "NEWLYWED": {
        "max_area_per_unit": 85,      # 전용 85㎡ 이하
        "profit_rate": 0.09,            # 9% 적정이윤
        "min_units": 20,                # 최소 20세대
        "location": ["전국"]
    }
}
```

---

## 📊 3단계: ROI/IRR 계산

### ROI (Return on Investment)

```python
# roi_calculator.py

def calculate_roi(investment, return_amount):
    """
    ROI = (수익 - 투자액) / 투자액 × 100
    
    투자액 = 토지비 + 건축비 + 부대비용
    수익 = LH 매입가
    """
    profit = return_amount - investment
    roi = (profit / investment) * 100
    return roi

# Example:
# 투자액: 50억
# LH 매입가: 55억
# ROI = (55억 - 50억) / 50억 × 100 = 10%
```

### IRR (Internal Rate of Return)

```python
import numpy as np
from scipy.optimize import newton

def calculate_irr(cash_flows):
    """
    IRR = NPV가 0이 되는 할인율
    
    cash_flows = [
        -토지비 (0년차),
        -건축비 (1년차),
        +LH 매입가 (2년차)
    ]
    """
    def npv(rate):
        return sum(cf / (1 + rate) ** t for t, cf in enumerate(cash_flows))
    
    irr = newton(npv, 0.1)  # 초기값 10%
    return irr * 100

# Example:
# Year 0: -30억 (토지 매입)
# Year 1: -20억 (건축비)
# Year 2: +55억 (LH 매입)
# IRR ≈ 15.2%
```

---

## 🎨 4단계: 민감도 분석

### 주요 변수 시뮬레이션

```python
# sensitivity.py

class SensitivityAnalyzer:
    """민감도 분석"""
    
    VARIABLES = {
        "land_price": [-10, -5, 0, 5, 10],      # 토지가 변동 (%)
        "construction_cost": [-10, -5, 0, 5, 10],  # 건축비 변동 (%)
        "profit_rate": [7, 8, 9, 10]              # 이윤율 변동 (%)
    }
    
    def run_simulation(self, base_scenario):
        """
        각 변수를 변화시키면서 ROI/IRR 변화 분석
        """
        results = []
        
        for var_name, variations in self.VARIABLES.items():
            for variation in variations:
                scenario = self.adjust_scenario(base_scenario, var_name, variation)
                roi = calculate_roi(scenario)
                irr = calculate_irr(scenario)
                
                results.append({
                    "variable": var_name,
                    "change": f"{variation:+.0f}%",
                    "roi": roi,
                    "irr": irr
                })
        
        return results
```

---

## 🔌 5단계: API 엔드포인트

### 새로운 API 추가

```python
# app/api/endpoints/business.py

from fastapi import APIRouter, HTTPException
from app.modules.business_simulation.service import BusinessSimulationService

router = APIRouter(prefix="/api/business", tags=["business"])

@router.post("/calculate-cost")
async def calculate_construction_cost(request: CostCalculationRequest):
    """건축비 자동 산정"""
    service = BusinessSimulationService()
    result = service.calculate_cost(request)
    return result

@router.post("/simulate-purchase")
async def simulate_lh_purchase(request: PurchaseSimulationRequest):
    """LH 매입가 시뮬레이션"""
    service = BusinessSimulationService()
    result = service.simulate_purchase(request)
    return result

@router.post("/analyze-roi")
async def analyze_roi(request: ROIAnalysisRequest):
    """수익률 분석 (ROI/IRR)"""
    service = BusinessSimulationService()
    result = service.analyze_roi(request)
    return result

@router.post("/sensitivity-analysis")
async def run_sensitivity_analysis(request: SensitivityRequest):
    """민감도 분석"""
    service = BusinessSimulationService()
    result = service.run_sensitivity(request)
    return result
```

---

## 📱 6단계: Frontend 통합

### React 대시보드 초기 구조

```bash
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx           # 메인 대시보드
│   │   ├── BusinessSimulator.jsx   # 사업성 시뮬레이터
│   │   ├── ROIChart.jsx            # ROI 차트
│   │   └── SensitivityTable.jsx    # 민감도 분석 표
│   ├── services/
│   │   └── api.js                  # API 호출
│   ├── App.jsx
│   └── index.js
├── package.json
└── vite.config.js
```

### 시각화 컴포넌트

```javascript
// BusinessSimulator.jsx

import React, { useState } from 'react';
import { Card, Form, Button, Table } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';

function BusinessSimulator() {
  const [inputs, setInputs] = useState({
    landArea: 500,
    unitType: 'YOUTH',
    region: '서울'
  });
  
  const [result, setResult] = useState(null);
  
  const handleSimulate = async () => {
    const response = await fetch('/api/business/analyze-roi', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(inputs)
    });
    const data = await response.json();
    setResult(data);
  };
  
  return (
    <Card>
      <Card.Header>사업성 시뮬레이션</Card.Header>
      <Card.Body>
        {/* 입력 폼 */}
        <Form>
          <Form.Group>
            <Form.Label>토지 면적 (㎡)</Form.Label>
            <Form.Control
              type="number"
              value={inputs.landArea}
              onChange={e => setInputs({...inputs, landArea: e.target.value})}
            />
          </Form.Group>
          {/* ... 기타 입력 필드 ... */}
          
          <Button onClick={handleSimulate}>시뮬레이션 실행</Button>
        </Form>
        
        {/* 결과 표시 */}
        {result && (
          <div className="mt-4">
            <h5>분석 결과</h5>
            <Table>
              <tbody>
                <tr>
                  <td>건축비</td>
                  <td>{result.construction_cost.toLocaleString()}원</td>
                </tr>
                <tr>
                  <td>LH 매입가</td>
                  <td>{result.purchase_price.toLocaleString()}원</td>
                </tr>
                <tr>
                  <td>ROI</td>
                  <td>{result.roi}%</td>
                </tr>
                <tr>
                  <td>IRR</td>
                  <td>{result.irr}%</td>
                </tr>
              </tbody>
            </Table>
          </div>
        )}
      </Card.Body>
    </Card>
  );
}

export default BusinessSimulator;
```

---

## 🧪 7단계: 테스트

### 단위 테스트

```python
# tests/test_business_simulation.py

import pytest
from app.modules.business_simulation.construction_cost import ConstructionCostCalculator
from app.modules.business_simulation.purchase_price import LHPurchaseCalculator

def test_construction_cost_calculation():
    """건축비 계산 테스트"""
    calculator = ConstructionCostCalculator()
    
    result = calculator.calculate({
        "unit_type": "YOUTH",
        "gross_area": 1000,  # 1000㎡
        "region": "서울"
    })
    
    # 예상: 1000㎡ × 3.3 × 120만 × 1.2 = 약 47.5억
    assert result["total_cost"] > 4_500_000_000
    assert result["total_cost"] < 5_000_000_000

def test_lh_purchase_simulation():
    """LH 매입가 시뮬레이션 테스트"""
    calculator = LHPurchaseCalculator()
    
    result = calculator.calculate({
        "land_value": 3_000_000_000,      # 토지 30억
        "construction_cost": 2_000_000_000,  # 건축 20억
        "unit_type": "YOUTH"
    })
    
    # 예상: (30억 + 20억) × 1.08 = 54억
    assert result["total_purchase"] == pytest.approx(5_400_000_000, rel=0.01)
```

---

## 📊 개발 우선순위

### Week 1-2: 백엔드 개발
1. ✅ Phase 2 브랜치 생성
2. ⏳ `models.py` - 데이터 모델 정의
3. ⏳ `construction_cost.py` - 건축비 계산 로직
4. ⏳ `purchase_price.py` - LH 매입가 시뮬레이션
5. ⏳ `roi_calculator.py` - ROI/IRR 계산
6. ⏳ `service.py` - 비즈니스 로직 통합
7. ⏳ API 엔드포인트 추가

### Week 3: 프론트엔드 개발
8. ⏳ React 프로젝트 초기화
9. ⏳ 사업성 시뮬레이터 컴포넌트
10. ⏳ 차트 및 시각화
11. ⏳ 기존 시스템과 통합

### Week 4: 테스트 및 배포
12. ⏳ 단위 테스트 작성
13. ⏳ 통합 테스트
14. ⏳ 문서화
15. ⏳ 배포 및 운영

---

## 🚀 시작 명령어

### 1. 현재 브랜치 확인
```bash
cd /home/user/webapp
git branch
# * phase2/business-simulation
```

### 2. 서버 실행 (이미 실행 중)
```bash
# 서버가 이미 실행 중입니다
# PID: 2083
# Port: 8000
# URL: https://8000-iadrkxedqg14xkst1ju95-b9b802c4.sandbox.novita.ai
```

### 3. 개발 시작
```bash
# 새 모듈 생성
mkdir -p app/modules/business_simulation
cd app/modules/business_simulation

# 파일 생성
touch __init__.py models.py construction_cost.py purchase_price.py roi_calculator.py service.py
```

---

## 📝 중요 참고사항

### 실제 데이터 기준 (2025년)
- **청년주택 평당 건축비**: 120만원 (서울 기준 1.2배 = 144만원)
- **LH 적정이윤**: 7-10%
- **평균 사업 기간**: 2-3년
- **최소 사업 규모**: 10세대 이상

### LH 사업 방식
1. **토지임대부 분양주택**: LH가 토지 소유, 건물만 분양
2. **매입약정형**: 완공 후 LH가 전체 매입
3. **수익공유형**: 분양 후 수익 일부 환원

---

## 🎯 Phase 2 완료 체크리스트

- [ ] 건축비 자동 산정 기능
- [ ] LH 매입가 시뮬레이션
- [ ] ROI/IRR 계산기
- [ ] 민감도 분석
- [ ] API 엔드포인트 4개 추가
- [ ] React 대시보드 초기 버전
- [ ] 시각화 컴포넌트 3개
- [ ] 단위 테스트 10개 이상
- [ ] 통합 테스트
- [ ] 문서화 완료
- [ ] Git 커밋 및 PR

---

## 🔗 관련 문서

- `PLATFORM_ARCHITECTURE.md` - 전체 시스템 아키텍처
- `README.md` - 프로젝트 개요
- Phase 1 완료 상태: Tag `v2.0-stable`

---

## 💡 다음 단계

Phase 2를 새창에서 시작하려면:

1. **이 문서를 참조**하여 개발 진행
2. **models.py부터 시작** (데이터 구조 정의)
3. **각 모듈을 순차적으로 개발**
4. **API 테스트 후 프론트엔드 연결**

질문이나 도움이 필요하면 언제든지 요청하세요! 🚀

---

**Generated**: 2025-11-12  
**Branch**: phase2/business-simulation  
**Based on**: v2.0-stable (commit 36760ff)
