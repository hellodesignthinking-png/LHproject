# ZeroSite v8.5 구현 가이드

## 📌 현재 상태

### ✅ 완료된 작업 (Phase 1)
1. **visualization_engine_v85.py** ✅
   - 6가지 시각화 데이터 생성 함수 구현
   - JSON 포맷으로 프론트엔드 렌더링 가능
   
2. **lh_criteria_checker_v85.py** ✅
   - LH LINKED 모델 사업성 평가 로직
   - ROI 기반 평가 (v7.5의 세대당 상한 제거)

### ⏳ 남은 작업 (Phase 2 - 필수)

#### 1. main.py 수정
**파일**: `app/main.py`
**수정 위치**: `/api/analyze-land` 또는 `/api/generate-report` 엔드포인트

**현재 코드**:
```python
return JSONResponse({
    "success": True,
    "analysis_id": analysis_id,
    "html": response['html'],
    "metadata": {...}
})
```

**수정 후 코드**:
```python
from app.services.visualization_engine_v85 import VisualizationEngineV85
from app.services.lh_criteria_checker_v85 import LHCriteriaCheckerV85

# 시각화 생성
viz_engine = VisualizationEngineV85()
visualizations = viz_engine.generate_all_visualizations(
    analysis_data=result,
    financial_result=financial_analysis
)

# LH 점수 계산 (v8.5)
lh_checker = LHCriteriaCheckerV85()
financial_score_breakdown = lh_checker.get_financial_score_breakdown({
    "roi": financial_analysis['returns']['cap_rate_percent'],
    "lh_purchase_price": lh_price_sim.get('lh_purchase_price', 0),
    "total_cost": financial_analysis['capex']['total_capex'],
    "verified_cost": financial_analysis['capex'].get('construction_hard_costs', {}).get('subtotal', 0),
    "land_appraisal": request.land_appraisal_price,
    "expected_units": financial_analysis['capex']['unit_count']
})

return JSONResponse({
    "success": True,
    "analysis_id": analysis_id,
    "html": response['html'],
    "financial_result": {
        "land_appraisal": request.land_appraisal_price,
        "verified_cost": financial_analysis['capex'].get('construction_hard_costs', {}).get('subtotal', 0),
        "lh_purchase_price": lh_price_sim.get('lh_purchase_price', 0),
        "total_cost": financial_analysis['capex']['total_capex'],
        "roi": financial_analysis['returns']['cap_rate_percent'],
        "expected_units": financial_analysis['capex']['unit_count'],
        "decision": lh_price_sim.get('recommendation', 'N/A'),
        "cost_breakdown": financial_analysis['capex'].get('breakdown', {}),
        "sensitivity": financial_analysis.get('sensitivity', {})
    },
    "visualization": visualizations,
    "lh_scores": {
        "location": result.get("grade_info", {}).get("total_score", 0) * 0.35,  # 임시
        "scale": 65,  # 임시
        "financial": financial_score_breakdown["total_financial_score"],  # ✅ v8.5 로직
        "regulation": 91  # 임시
    },
    "metadata": {
        ...response['metadata'],
        "version": "v8.5",
        "model_type": "LH_LINKED"
    }
})
```

#### 2. UltraReportGeneratorV8_5 생성 (선택 사항)
**파일**: `app/services/ultra_report_generator_v8_5.py`

v7.5 FINAL 코드를 복사하여:
- `__init__`에서 `financial_result` 파라미터 추가
- Chapter 6 "재무 사업성 분석"에서 `self.financial_result` 값 사용
- Chapter 9 "최종 의사결정"에서 `self.financial_result["decision"]` 사용

**예시**:
```python
def _generate_financial_chapter(self):
    financial = self.financial_result
    
    html = f"""
    <h1>재무 사업성 분석</h1>
    <table>
        <tr>
            <td>토지 감정가</td>
            <td>{self._format_krw(financial.get('land_appraisal', 0))}</td>
        </tr>
        <tr>
            <td>Verified Cost</td>
            <td>{self._format_krw(financial.get('verified_cost', 0))}</td>
        </tr>
        <tr>
            <td>LH 매입가</td>
            <td>{self._format_krw(financial.get('lh_purchase_price', 0))}</td>
        </tr>
        <tr>
            <td>ROI</td>
            <td>{financial.get('roi', 0):.2f}%</td>
        </tr>
    </table>
    """
    return html
```

---

## 🧪 테스트 방법

### 1. 시각화 엔진 테스트
```bash
cd /home/user/webapp
python app/services/visualization_engine_v85.py
```

**예상 출력**:
```
Visualization Engine v8.5 Test Results
================================================================================

financial_bar_chart:
  Type: bar
  Title: 재무 구조 비교

infra_radar_chart:
  Type: radar
  Title: 인프라 종합 평가
  
...
```

### 2. LH Criteria Checker 테스트
```bash
cd /home/user/webapp
python app/services/lh_criteria_checker_v85.py
```

**예상 출력**:
```
LH Criteria Checker v8.5 Test Results
================================================================================

1. ROI Score: 0/20 (ROI: -4.49%)
2. LH Ratio Score: 10/10 (Ratio: 95.5%)
3. Verified Cost Score: 10/10 (Per Unit: 1.32억원)

📊 Total Financial Score: 20/40 (50.0%)
```

### 3. API 통합 테스트
```bash
curl -X POST "URL/api/analyze-land" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울시 강남구",
    "land_area": 1500,
    "unit_type": "청년",
    "land_appraisal_price": 5500000,
    "report_mode": "v7.5_final"
  }'
```

**검증 포인트**:
- `financial_result.roi` != 0
- `financial_result.lh_purchase_price` > 0
- `visualization.financial_bar_chart` != null
- `lh_scores.financial` > 0 (v8.5 로직으로 계산됨)

---

## 📊 v7.5 vs v8.5 비교

| 항목 | v7.5 | v8.5 LH LINKED |
|------|------|----------------|
| **사업성 평가** | 세대당 1.5억원 기준 | ROI 기반 평가 |
| **토지비 비중** | 25~45% 기준 | 감정가 기준 (비중 제거) |
| **Gap 분석** | 토지/공사비 Gap | Gap 제거 |
| **LH 매입가** | 추정 | 감정가 + Verified Cost |
| **사업성 점수** | 0~40점 (v7.5 기준) | 0~40점 (v8.5 기준) |

### v8.5 사업성 점수 구성
1. **ROI**: 0~20점
   - ≥15%: 20점
   - 10~15%: 15점
   - 5~10%: 10점
   - 0~5%: 5점
   - <0%: 0점

2. **LH 매입가 비율**: 0~10점
   - ≤100%: 10점
   - 100~105%: 5점
   - >105%: 0점

3. **Verified Cost**: 0~10점
   - 1.2~1.5억/세대: 10점
   - 1.0~1.2억 또는 1.5~1.8억: 7점
   - 기타: 3점

---

## 🚀 배포 체크리스트

### Phase 1 (완료)
- [x] visualization_engine_v85.py 생성
- [x] lh_criteria_checker_v85.py 생성
- [x] 테스트 코드 작성

### Phase 2 (진행 필요)
- [ ] main.py 수정 (financial_result 연결)
- [ ] LH 점수 계산 v8.5로 업그레이드
- [ ] API 응답 구조 수정
- [ ] UltraReportGeneratorV8_5 생성 (선택)

### Phase 3 (테스트)
- [ ] 단위 테스트 (visualization, lh_checker)
- [ ] 통합 테스트 (API 엔드포인트)
- [ ] 재무 데이터 검증 (0이 아닌 값)
- [ ] 시각화 데이터 검증 (JSON 포맷)

---

## 💡 주요 개선 사항

### 1. 재무 데이터 0 문제 해결
**Before**:
```json
{
  "roi": 0,
  "lh_purchase_price": 0,
  "total_cost": 0
}
```

**After**:
```json
{
  "roi": -4.49,
  "lh_purchase_price": 22145790240,
  "total_cost": 23186642381,
  "land_appraisal": 8662500000,
  "verified_cost": 13483290240
}
```

### 2. 시각화 데이터 추가
**Before**: 시각화 없음

**After**: 6가지 시각화 JSON 데이터
- Financial Bar Chart
- Infrastructure Radar
- Grade Gauge
- LH Framework
- Cost Pie Chart
- ROI Trend Line

### 3. 사업성 점수 정확도 향상
**Before**: 항상 0점 (v7.5 기준 부적합)

**After**: ROI 기반 0~40점 (v8.5 LH LINKED 기준)

---

## 📞 지원

### 파일 위치
- **Visualization Engine**: `/home/user/webapp/app/services/visualization_engine_v85.py`
- **LH Criteria Checker**: `/home/user/webapp/app/services/lh_criteria_checker_v85.py`
- **Main API**: `/home/user/webapp/app/main.py`

### 커밋 정보
- 커밋 해시: (생성 후 업데이트 필요)
- 브랜치: `feature/expert-report-generator`
- PR: [PR #4](https://github.com/hellodesignthinking-png/LHproject/pull/4)

---

**작성일**: 2025-12-04  
**버전**: v8.5 Phase 1 완료  
**다음 단계**: main.py 수정 및 통합 테스트
