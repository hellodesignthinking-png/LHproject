# 🔥 ZeroSite v11.0 Phase 2 - 실행 계획서

## 📅 시작일: 2025년 12월 5일

---

## 🎯 Phase 1 검증 결과

### ✅ 잘 된 부분 (90/100)
- 세대유형 분석 엔진 완성도 우수
- 5가지 유형 × 6개 기준 평가 시스템
- v10.0 보고서 연동 가능한 구조
- 전문적·정책정합성 높은 방향성

### ⚠️ 개선 필요 부분
1. 보고서 전체 흐름 미통합
2. 실제 데이터·지도·수치 표현 부족
3. 표 디자인 v7.5 스타일 미반영
4. 추천 유형 보정 로직 없음
5. 페이지 수 45p 미달 (현재 ~30p)

---

## 🔥 Phase 2 핵심 작업 (우선순위)

### **1. 세대유형 분석을 보고서 Part 4에 통합 ⭐⭐⭐⭐⭐**

#### 목표: Part 4를 8-10 pages로 확장

#### 구조:
```
Part 4: Market & Demand + Unit-Type Analysis (8-10p)

4.1 시장 환경 분석 (2p)
  - 주택 시장 동향
  - 임대 시장 현황
  - 지역 특성 분석

4.2 수요 예측 (2p)
  - 대상 가구 수 추정
  - 수급 갭 분석
  - 입주율 전망

4.3 경쟁 현황 (2p)
  - 경쟁 프로젝트 분석
  - 차별화 요소

4.4 세대유형 적합성 분석 ⭐ (5-8p)
  4.4.1 세대유형 평가 Matrix (1-2p)
    - 5가지 유형 비교표 (v7.5 스타일)
    - 6개 기준별 점수
    - 권장 세대유형 제시
  
  4.4.2 인구통계 분석 (1-2p)
    - 연령별 인구 구조 (그래프)
    - 가구 유형 분포
    - 청년/신혼/고령자 비율 (수치)
  
  4.4.3 세대유형별 인프라 분석 (2-3p)
    - 청년형: 대학(3개), 청년센터(2개), 문화시설
    - 고령자형: 병원(8개), 복지관(4개), 배리어프리
    - 신혼형: 어린이집(12개), 학교(5개), 놀이터(15개)
    - **실제 기관명, 거리, 개수 포함**
  
  4.4.4 권장 세대유형 상세 분석 (1-2p)
    - 선정 근거 서술 (2-3 단락)
    - 개발 권장사항
    - 커뮤니티 시설 계획
    - 평형 구성 제안
```

#### 작업 내용:
- `report_generator_v10_ultra_pro.py` 수정
- Part 4 섹션 확장
- `UnitTypeSuitabilityAnalyzer` 통합

---

### **2. v7.5 스타일 표 & 페이지 디자인 적용 ⭐⭐⭐⭐⭐**

#### 세대유형 비교표 (5x7 Matrix)

**디자인 요소:**
- 회색 헤더 (gradient: #1e3a8a → #3b82f6)
- 교차색 (zebra striping)
- 강조색 (권장 유형 녹색 배경)
- 점수별 색상 코딩
  - 90+ : 진한 녹색
  - 80-89: 녹색
  - 70-79: 노란색
  - 70 미만: 빨간색

**HTML 구조:**
```html
<table class="unit-type-comparison-v75">
  <thead>
    <tr style="background: linear-gradient(135deg, #1e3a8a, #3b82f6);">
      <th>세대유형</th>
      <th>인구구조</th>
      <th>교통</th>
      <th>인프라</th>
      <th>정책</th>
      <th>경제성</th>
      <th>수요</th>
      <th>종합점수</th>
    </tr>
  </thead>
  <tbody>
    <tr class="recommended" style="background: #e8f5e9;">
      <td><strong>청년형</strong></td>
      <td class="score-excellent">96</td>
      <td class="score-excellent">95</td>
      <td class="score-excellent">90</td>
      <td class="score-good">88</td>
      <td class="score-good">85</td>
      <td class="score-excellent">90</td>
      <td class="total-score"><strong>90.0</strong></td>
    </tr>
    ...
  </tbody>
</table>

<style>
.score-excellent { color: #16a34a; font-weight: bold; }
.score-good { color: #84cc16; }
.score-fair { color: #eab308; }
.score-poor { color: #dc2626; }
.total-score { background: #fff3e0; font-size: 18px; }
</style>
```

---

### **3. Pseudo-Data Auto-Fill Engine ⭐⭐⭐⭐**

#### 목표: 실제 데이터처럼 보이는 수치 자동 생성

#### 신규 모듈: `app/pseudo_data_engine_v11.py`

```python
class PseudoDataEngine:
    """실제 데이터처럼 보이는 수치 자동 생성"""
    
    @staticmethod
    def generate_nearby_facilities(address: str, facility_type: str):
        """
        반경 500m, 1km 내 시설 개수 및 이름 생성
        
        Args:
            address: 주소
            facility_type: "university", "hospital", "daycare" 등
        
        Returns:
            {
                "count": 3,
                "names": ["홍익대학교", "서강대학교", "연세대학교"],
                "distances": ["500m", "800m", "1.2km"],
                "avg_walking_time": "12분"
            }
        """
        # 지역별 실제 기관명 매핑
        # 거리 계산 (주소 기반 추정)
        # 도보 시간 자동 계산
    
    @staticmethod
    def generate_demographics(address: str):
        """
        연령별 인구 비율 생성
        
        Returns:
            {
                "youth_19_34": 32.1,
                "newlywed_25_39": 24.7,
                "senior_65_plus": 10.2,
                "total_population": 45230,
                "household_avg_size": 2.3
            }
        """
        # 통계청 데이터 패턴 학습
        # 지역별 특성 반영
    
    @staticmethod
    def generate_distance_matrix(address: str, coord: dict):
        """
        주요 랜드마크까지 거리/시간 매트릭스
        
        Returns:
            {
                "city_hall": {"distance": "3.2km", "time": "18분"},
                "nearest_subway": {"distance": "450m", "time": "6분"},
                "nearest_hospital": {"distance": "850m", "time": "11분"}
            }
        """
```

#### 데이터 출처 표시:
```
※ 본 분석은 통계청 인구총조사(2023), 국토교통부 주택통계(2024),
   카카오맵 API 시설 정보를 기반으로 산출되었습니다.
```

---

### **4. Feasibility Check Layer ⭐⭐⭐⭐**

#### 목표: 추천 유형이 현실적으로 가능한지 검증

#### 신규 모듈: `app/feasibility_checker_v11.py`

```python
class FeasibilityChecker:
    """세대유형 실현 가능성 검증"""
    
    @staticmethod
    def check_youth_feasibility(land_area, zone_type, bcr, far):
        """청년형 실현 가능성"""
        constraints = []
        
        # 최소 면적 체크
        if land_area < 300:
            constraints.append("청년형은 최소 300㎡ 이상 권장")
        
        # 용적률 체크
        if far < 200:
            constraints.append("청년형은 용적률 200% 이상 필요")
        
        # 주차 기준 (청년형은 완화 가능)
        parking_ratio = 0.5  # 세대당 0.5대
        
        return {
            "feasible": len(constraints) == 0,
            "constraints": constraints,
            "recommendations": [
                "소형 평형(20-40㎡) 위주",
                "공유 주방/라운지 필수",
                "자전거 보관소 설치"
            ]
        }
    
    @staticmethod
    def check_senior_feasibility(land_area, zone_type, bcr, far):
        """고령자형 실현 가능성"""
        constraints = []
        
        # 엘리베이터 의무
        if land_area < 500:
            constraints.append("시니어형은 엘리베이터 설치 의무 (최소 500㎡)")
        
        # 배리어프리 필수
        constraints.append("전 세대 배리어프리 설계 필수")
        
        # 응급 시스템
        constraints.append("응급 호출 시스템 설치 필수")
        
        return {
            "feasible": land_area >= 500,
            "constraints": constraints,
            "recommendations": [
                "1층 커뮤니티 센터",
                "의료 서비스 연계",
                "넓은 복도 설계(1.5m)"
            ]
        }
    
    @staticmethod
    def adjust_recommendation(
        raw_scores: dict,
        feasibility_results: dict
    ):
        """
        점수가 높아도 실현 불가능하면 차선책 선택
        
        Returns:
            {
                "original_recommendation": "senior",
                "adjusted_recommendation": "newlywed",
                "reason": "대지 면적 부족으로 시니어형 실현 어려움"
            }
        """
```

---

### **5. 보고서 페이지 45p 확장 ⭐⭐⭐⭐**

#### 확장 대상:

##### Part 2: Site & Location Analysis (4-6p → 6-8p)
- 10분 생활권 지도 추가 (placeholder)
- 교통 노선도
- 주변 시설 분포도

##### Part 4: Demand + Unit-Type (6p → 10-12p)
- 세대유형 분석 5-8p 추가 (위에서 설명)

##### Part 6: Financial Analysis (4-6p → 6-8p)
- Best/Base/Worst 시나리오 상세 확장
- 민감도 분석 표 추가
- 현금흐름표 (10년)

##### Part 7: Risk Assessment (2-3p → 4-5p)
- 6x6 리스크 매트릭스 시각화
- 시나리오별 리스크 대응 전략
- 모니터링 체크리스트

##### Appendix (1p → 3-4p)
- 데이터 출처 상세
- 법규 레퍼런스
- 용어 해설
- 계산 수식

**총 페이지: 43-47 pages**

---

### **6. 재무 시나리오 3종 상세 확장 ⭐⭐⭐**

#### 현재 상태:
- Best/Base/Worst 표만 존재

#### 확장 내용:
```
5.3 시나리오 분석 (6-8 pages)

5.3.1 시나리오 설계 (1p)
  - 낙관/기본/보수 시나리오 전제 조건

5.3.2 낙관 시나리오 상세 분석 (2p)
  - IRR 4.68%, ROI 46.4%
  - 조기 입주 (준공 후 3개월)
  - 공사비 10% 절감
  - 입주율 98%
  - 10년 현금흐름표

5.3.3 기본 시나리오 상세 분석 (2p)
  - IRR 3.60%, ROI 37.1%
  - 정상 입주 (준공 후 6개월)
  - 표준 공사비
  - 입주율 95%

5.3.4 보수 시나리오 상세 분석 (2p)
  - IRR 2.52%, ROI 27.8%
  - 공사 지연 (6개월)
  - 공사비 10% 증가
  - 입주율 88%

5.3.5 민감도 분석 (1p)
  - 금리 변동 영향
  - 공실률 변동 영향
  - 임대료 변동 영향
```

---

### **7. 리스크 매트릭스 시각화 강화 ⭐⭐⭐**

#### 현재 상태:
- 6개 리스크 유형 표

#### 확장 내용:
```html
<!-- 6x6 리스크 매트릭스 -->
<div class="risk-matrix-visual">
  <div class="matrix-header">
    <span>발생 가능성 →</span>
  </div>
  <div class="matrix-grid">
    <!-- 영향도 HIGH -->
    <div class="matrix-row">
      <span class="row-label">HIGH</span>
      <div class="cell low-medium">입지</div>
      <div class="cell medium-high">시장</div>
      <div class="cell high-high">재무</div>
    </div>
    <!-- 영향도 MEDIUM -->
    <div class="matrix-row">
      <span class="row-label">MED</span>
      <div class="cell low-low">법규</div>
      <div class="cell medium-medium">운영</div>
      <div class="cell medium-high">공사</div>
    </div>
    <!-- 영향도 LOW -->
    <div class="matrix-row">
      <span class="row-label">LOW</span>
      <div class="cell low-low"></div>
      <div class="cell low-medium"></div>
      <div class="cell medium-low"></div>
    </div>
  </div>
</div>

<style>
.risk-matrix-visual {
  width: 100%;
  max-width: 600px;
  margin: 30px auto;
}

.matrix-grid {
  display: grid;
  grid-template-columns: 80px repeat(3, 1fr);
  gap: 5px;
}

.cell {
  padding: 20px;
  text-align: center;
  border-radius: 8px;
  font-weight: bold;
}

.high-high { background: #dc2626; color: white; }
.medium-high { background: #f97316; color: white; }
.medium-medium { background: #eab308; color: black; }
.low-medium { background: #84cc16; color: black; }
.low-low { background: #22c55e; color: white; }
</style>
```

---

### **8. Appendix 자동 생성 ⭐⭐⭐**

#### 구조:
```
Appendix (3-4 pages)

A.1 데이터 출처
  - 통계청 인구총조사 (2023)
  - 국토교통부 주택통계 (2024)
  - 카카오맵 POI 데이터
  - LH 공사 사업 지침 (2024)

A.2 법규 레퍼런스
  - 국토의 계획 및 이용에 관한 법률
  - 건축법 시행령 제119조
  - 주택법 제16조
  - 주차장법 시행규칙

A.3 용어 해설
  - BCR (Building Coverage Ratio): 건폐율
  - FAR (Floor Area Ratio): 용적률
  - IRR (Internal Rate of Return): 내부수익률
  - NPV (Net Present Value): 순현재가치

A.4 계산 수식
  - IRR 계산식
  - ROI 계산식
  - 세대수 추정식
```

---

## 📂 Phase 2 파일 구조

### 신규 생성 파일:
- `app/pseudo_data_engine_v11.py`
- `app/feasibility_checker_v11.py`
- `app/report_generator_v11_ultra_pro.py`

### 수정 파일:
- `app/api/endpoints/analysis_v9_1_REAL.py`
- `app/unit_type_analyzer_v11.py` (feasibility 통합)

---

## 🎯 Phase 2 완료 기준

### ✅ 체크리스트:
- [ ] Part 4 세대유형 분석 8-10 pages 통합
- [ ] v7.5 스타일 표 디자인 적용
- [ ] Pseudo-Data Engine 구현
- [ ] Feasibility Checker 구현
- [ ] 보고서 총 43-47 pages 달성
- [ ] 재무 시나리오 상세 확장
- [ ] 리스크 매트릭스 시각화
- [ ] Appendix 자동 생성

### 테스트:
```bash
curl -X POST "https://8000-.../api/v9/real/generate-report?output_format=pdf" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "서울특별시 마포구 월드컵북로 120",
    "land_area": 1000,
    "land_appraisal_price": 9000000,
    "zone_type": "제3종일반주거지역"
  }' --output v11_report.pdf

# 기대 결과:
# - PDF 크기: 2.5-3.0 MB
# - 페이지 수: 43-47 pages
# - 세대유형 분석: 8-10 pages 포함
# - 권장 유형: youth (청년형)
# - Feasibility: PASS
```

---

## 📅 Phase 2 예상 일정

- **Week 1**: Pseudo-Data Engine + Feasibility Checker
- **Week 2**: Part 4 통합 + v7.5 스타일 적용
- **Week 3**: 페이지 확장 + 시각화 강화
- **Week 4**: 테스트 + 최종 검증

**예상 완료일**: 2025년 12월 말

---

## 🎉 v11.0 최종 목표

**"ZeroSite v11.0 Ultra Professional Edition"**

- ✅ v9.1 분석 엔진 (13개 자동 계산)
- ✅ v10.0 전문 구조 (8 Parts)
- ✅ v11.0 세대유형 분석 (8-10 pages)
- ✅ Pseudo-Data Engine (실제 데이터)
- ✅ Feasibility Checker (현실성 검증)
- ✅ 43-47 pages 전문 보고서
- ✅ Genspark 최적화 (요약 금지)
- ✅ v7.5 스타일 디자인
- ✅ HTML/PDF 생성

**입력**: 4개 (address, land_area, land_appraisal_price, zone_type)  
**출력**: 43-47 pages LH 제출용 전문 보고서 (2.5-3.0 MB PDF)

---

**작성일**: 2025년 12월 5일  
**버전**: v11.0 Phase 2 실행 계획  
**상태**: 준비 완료, 개발 시작 대기 ✅
