# 🔧 ZeroSite 데이터 로딩·보강·분석 통합 개선 계획

## 📋 현재 상태 분석

### ✅ 완료된 항목
1. **Pydantic 검증 오류 수정**: `status="success (cached)"` → `status="success"` 수정 완료
2. **M4 DATA INSUFFICIENT Protection**: 100% 구현 완료
3. **M5 DATA NOT LOADED Protection**: 100% 구현 완료

### ❌ 개선 필요 항목
1. **데이터 재로딩 로직**: Context 기반 자동 로딩 미구현
2. **시스템 기본값 세트**: 정책 허용 범위 내 기본값 미적용
3. **상세 출력 규칙**: 서술형 + 수치 출력 부분적 구현
4. **메타 선언**: 데이터 보강 로직 선언 미추가

---

## 🎯 구현 우선순위

### 1️⃣ 즉시 구현 (Critical)

#### A. Pydantic 검증 오류 수정 ✅
**파일**: `app/api/endpoints/pipeline_reports_v4.py`  
**라인**: 469  
**변경**:
```python
# Before
status="success (cached)",

# After
status="success",  # Fixed: Pydantic validation
```
**상태**: ✅ 완료

---

### 2️⃣ 우선 구현 (High Priority)

#### B. Context 기반 데이터 재로딩 로직

**목표**: M4/M5 분석 시 필수 데이터 누락 시 Context에서 자동 재조회

**구현 위치**:
- `app/utils/m4_enhanced_logic.py`
- `app/utils/m5_enhanced_logic.py`

**구현 내용**:
```python
def reload_data_from_context(self, context_id: str) -> Dict[str, Any]:
    """
    Context 기반 데이터 재로딩 (1순위)
    
    Returns:
        Dict with reloaded M1/M2/M3 data
    """
    from app.api.endpoints.m1_context_freeze_v2 import frozen_contexts_v2
    
    # Try to load from frozen context
    if context_id in frozen_contexts_v2:
        context = frozen_contexts_v2[context_id]
        
        return {
            "address": context.land_info.address.jibun_address,
            "land_area": context.land_info.land.area_sqm,
            "zoning": context.land_info.zoning.type,
            "bcr": context.land_info.zoning.bcr,
            "far": context.land_info.zoning.far
        }
    
    # Fallback to system defaults if context not found
    return self.apply_system_defaults()
```

---

#### C. 시스템 기본값 세트 적용 (2순위)

**목표**: Context 로딩 실패 시 정책 허용 범위 내 기본값 사용

**구현 내용**:
```python
def apply_system_defaults(self) -> Dict[str, Any]:
    """
    시스템 기본값 세트 (2순위)
    
    ZeroSite 기본 가정값:
    - 용도지역: 제2종일반주거지역 (가장 보수적)
    - 건폐율: 60% (법정 기준)
    - 용적률: 200% (법정 기준)
    - 전용면적: 청년형 26~36㎡
    - 공용면적률: 20~25%
    
    Returns:
        Dict with default values
    """
    logger.warning("🔄 시스템 기본값 적용 (Context 로딩 실패)")
    
    return {
        "address": "시스템 기본 설정 (주소 미확인)",
        "land_area": self.m1_data.get("land_area", 500.0),  # 기존 값 유지 또는 500㎡ 기본값
        "zoning": "제2종일반주거지역",
        "bcr": 60.0,
        "far": 200.0,
        "supply_type": "청년형",
        "exclusive_area": 30.0,
        "common_area_ratio": 0.25,
        "_is_default": True,  # 기본값 플래그
        "_default_reason": "Context 데이터 로딩 실패로 인한 정책 허용 범위 내 기본값 적용"
    }
```

---

### 3️⃣ 점진적 개선 (Medium Priority)

#### D. 상세 출력 규칙 강화

**M4 출력 개선**:
```python
def generate_detailed_analysis_text(self) -> str:
    """
    M4 상세 분석 텍스트 생성
    
    Returns:
        Detailed analysis text for LH reviewers
    """
    land_area = self.m1_data.get("land_area", 0)
    zoning = self.m1_data.get("zoning", "")
    bcr = self.zoning_limits.get("coverage", 60)
    far = self.zoning_limits.get("far", 200)
    
    # 법적 조건 설명
    legal_explanation = f"""
## 법적 건축 조건

본 대상지는 {zoning}로 지정되어 있으며, 이는 다음과 같은 건축 한계를 의미합니다:

1. **건폐율 {bcr}% 적용**
   - 토지면적 {land_area:,.0f}㎡ × {bcr}% = 최대 건축면적 {land_area * bcr / 100:,.0f}㎡
   - 이는 건물이 차지할 수 있는 땅의 최대 면적입니다.

2. **용적률 {far}% 적용**
   - 토지면적 {land_area:,.0f}㎡ × {far}% = 최대 연면적 {land_area * far / 100:,.0f}㎡
   - 이는 전체 층을 합한 최대 바닥면적입니다.

3. **세대수에 미치는 영향**
   - 연면적 ÷ 세대당 면적 = 총 세대수
   - 청년형 기준: 세대당 약 {self.UNIT_AREA_BY_TYPE['청년형']['standard']:.0f}㎡ (전용) + 공용면적
   - 최종 산정 가능 세대수: 약 {int(land_area * far / 100 / (self.UNIT_AREA_BY_TYPE['청년형']['standard'] / (1 - self.COMMON_AREA_RATIO)))}세대
"""
    
    # 규모 산정 과정
    calculation_process = """
## 규모 산정 과정

### 단계 1: 건축면적 산정
- 토지면적 × 건폐율 = {land_area:,.0f}㎡ × {bcr}% = {land_area * bcr / 100:,.0f}㎡

### 단계 2: 연면적 산정
- 토지면적 × 용적률 = {land_area:,.0f}㎡ × {far}% = {land_area * far / 100:,.0f}㎡

### 단계 3: 세대수 산정
- 연면적 ÷ 세대당 연면적 = {land_area * far / 100:,.0f}㎡ ÷ {self.UNIT_AREA_BY_TYPE['청년형']['standard'] / (1 - self.COMMON_AREA_RATIO):.0f}㎡/세대
- **권장 규모**: {int(land_area * far / 100 / (self.UNIT_AREA_BY_TYPE['청년형']['standard'] / (1 - self.COMMON_AREA_RATIO)) * 0.9)}세대
  (최대 가능 대비 90% 적용 - 안정적 사업 추진)

### 🔴 '권장 규모'와 '최대 가능' 구분
- **최대 가능**: 법적으로 허용되는 한계 (리스크 높음)
- **권장 규모**: LH 심사 통과 가능성을 고려한 적정 규모
- 본 분석에서는 **권장 규모 기준**으로 산정
"""
    
    # 합리성 설명
    rationale = """
## 이 규모가 합리적인 이유

### LH 심사 관점
1. **과밀 리스크 회피**: 최대 가능 규모 대비 10% 감축으로 안정성 확보
2. **주차 계획 실현 가능성**: 주차 공간 확보 여유 확보
3. **단지 관리 효율성**: 적정 세대수로 관리비 부담 최소화

### 과밀/과소 리스크
- **과밀 시**: 주차 부족, 관리비 증가, LH 심사 탈락 가능성
- **과소 시**: 사업성 저하, 토지 활용도 하락

### 주차·관리 부담
- 법정 주차 대수: {int(land_area * far / 100 / (self.UNIT_AREA_BY_TYPE['청년형']['standard'] / (1 - self.COMMON_AREA_RATIO)) * 0.5)}대 (청년형 완화 기준 0.5대/세대)
- 지하 주차장 확보 방안: 기계식 또는 2개 층 계획
"""
    
    return legal_explanation + calculation_process + rationale
```

---

**M5 출력 개선**:
```python
def generate_detailed_feasibility_text(self) -> str:
    """
    M5 상세 사업성 분석 텍스트 생성
    
    Returns:
        Detailed feasibility text for LH reviewers
    """
    # 사업 구조 설명
    structure_explanation = """
## 사업 구조 설명

본 사업은 **LH 일괄 매입형 신축임대 사업**으로, 다음과 같은 특징이 있습니다:

1. **분양 리스크 없음**
   - 준공 즉시 LH가 전량 매입
   - 시장 변동에 따른 분양 불확실성 제로

2. **수익 구조: 매입 대금 단일**
   - 매출 = LH 매입 대금 (감정평가액 기준)
   - 임대료 수익 없음 (LH 운영)
   - 수익 구조 명확, 예측 가능

3. **사업 안정성 높음**
   - 정부 기관 계약 (신용 리스크 제로)
   - 장기 임대 운영 리스크 없음
"""
    
    # 비용 구조 상세
    cost_breakdown = """
## 비용 구조 상세

### 1. 토지비
- 감정평가액: {land_value:,.0f}원
- 취득세 등: {land_value * 0.04:,.0f}원 (4% 가정)
- **토지비 합계**: {land_value * 1.04:,.0f}원

### 2. 공사비
- 연면적: {total_gfa:,.0f}㎡
- 단위 공사비: 3,000,000원/㎡ (2026년 기준)
- **공사비 합계**: {total_gfa * 3000000:,.0f}원

### 3. 간접비
- 설계비: {total_gfa * 3000000 * 0.05:,.0f}원 (5%)
- 인허가비: {total_gfa * 3000000 * 0.02:,.0f}원 (2%)
- 금융비용: {(land_value * 1.04 + total_gfa * 3000000) * 0.03:,.0f}원 (3%)
- **간접비 합계**: {total_gfa * 3000000 * 0.07 + (land_value * 1.04 + total_gfa * 3000000) * 0.03:,.0f}원

### 총 사업비
**{land_value * 1.04 + total_gfa * 3000000 * 1.07 + (land_value * 1.04 + total_gfa * 3000000) * 0.03:,.0f}원**
"""
    
    # 수익 구조 상세
    revenue_breakdown = """
## 수익 구조 상세

### LH 매입 단가 산정 논리
1. **기준**: 감정평가액 + 프리미엄
2. **프리미엄 근거**: 신축, 입지, LH 정책 우선순위
3. **산정 공식**: 감정평가액 × (1 + 프리미엄율 10%)

### 총 매입 금액 계산
- 세대당 감정평가액: {appraisal_per_unit:,.0f}원
- 세대당 매입 단가: {appraisal_per_unit * 1.1:,.0f}원 (10% 프리미엄)
- 총 세대수: {unit_count:,.0f}세대
- **총 매입 금액**: {appraisal_per_unit * 1.1 * unit_count:,.0f}원
"""
    
    # 지표 해석
    metric_interpretation = """
## 재무 지표 해석

### NPV (순현재가치)
- **의미**: 사업비 대비 수익의 현재가치 환산 후 차액
- **본 사업 NPV**: {npv:,.0f}원
- **해석**: NPV > 0이므로 사업비 대비 수익 초과 (수익성 양호)

### IRR (내부수익률)
- **의미**: 사업의 연평균 수익률
- **본 사업 IRR 제한 이유**: LH 매입형은 단일 시점 수익으로 IRR 산정에 제약
- **대안 지표**: ROI (투자 대비 수익률) 활용

### 손실 가능성 평가
- **리스크 요인**: 
  1. LH 매입가 변동 (감정평가 결과에 따름)
  2. 공사비 상승 (인플레이션)
  3. 인허가 지연 (금융비용 증가)
  
- **손실 방지 대책**:
  1. LH 사전 협의로 매입가 범위 확정
  2. 공사비 연동제 적용
  3. 단계별 예비비 확보 (5%)

- **종합 평가**: 손실 가능성 낮음 (정부 기관 계약, 수익 구조 명확)
"""
    
    return structure_explanation + cost_breakdown + revenue_breakdown + metric_interpretation
```

---

### 4️⃣ 최종 개선 (Low Priority)

#### E. 메타 선언 추가

**모든 보고서 하단에 추가**:
```
본 분석은 ZeroSite 데이터 재로딩 및 보강 로직을 통해 생성되었으며,
일부 수치는 정책 허용 범위 내 합리적 가정을 포함합니다.

⚠️ 데이터 출처:
- M1 토지정보: {data_source} {if is_default: "(시스템 기본값 적용)"}
- M3 공급유형: {data_source}
- 건축 규모: 법정 기준 + LH 정책 고려

ⓒ ZeroSite by AntennaHoldings | Natai Heum
Watermark: ZEROSITE
Tone: 공공주택 실무 검토용 상세 분석 보고서
```

---

## 📝 구현 타임라인

### Phase 1: 긴급 수정 (완료)
- ✅ Pydantic 검증 오류 수정

### Phase 2: 데이터 재로딩 (다음 단계)
- ⏳ Context 기반 자동 로딩 구현
- ⏳ 시스템 기본값 세트 구현

### Phase 3: 출력 개선 (후속 작업)
- ⏳ M4 상세 출력 규칙 적용
- ⏳ M5 상세 출력 규칙 적용
- ⏳ 메타 선언 추가

---

## 🎯 핵심 원칙

1. **데이터가 없으면 바로 "분석 불가"로 종료 ❌**
   → Context 재로딩 → 시스템 기본값 → 사용자 입력 요청 순서로 시도

2. **근거 없는 점수/등급 출력 ❌**
   → 모든 수치에 계산 과정 및 근거 명시

3. **IRR·ROI만 던지고 설명 없는 출력 ❌**
   → 지표의 의미, 제한 사유, 해석 방법 모두 서술

4. **built-in / object / None / N/A 노출 ❌**
   → 모든 출력 값 검증 및 sanitization

5. **M4 → M5 → M6 자연스러운 연결**
   → 각 모듈의 출력이 다음 모듈의 입력으로 명확히 연계

---

**ⓒ ZeroSite by AntennaHoldings | Natai Heum**
