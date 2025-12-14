# 🔧 ZeroSite v40.2 Server Refactoring Plan

**Backend Refactor Plan for Appraisal-First Architecture**

**Date**: 2025-12-14  
**Duration**: 3-4시간 (집중 작업 시)  
**Status**: 🔴 CRITICAL - START IMMEDIATELY

---

## 🎯 목적 (Purpose)

서버 구조를 **"계산은 한 번, 조회는 여러 번"** 구조로 통합  
→ API 안정성 + 속도 + 확장성 3요소 강화

---

## 📅 Phase-by-Phase Implementation Plan

### 🟥 **Phase 1: 엔진 구조 개선** (1시간)

#### **목표**
- appraisal_engine_v39를 Core Engine으로 승격
- Zoning/FAR의 이중 계산 제거
- 모든 엔진이 context 기반으로 동작하도록 재작성

#### **변경 파일**
- `app/api/v40/router.py` (주요 수정)
- `app/engines/v30/appraisal_engine.py` (검증 추가)

#### **작업 내용**

##### **1.1) router.py 프로세스 순서 변경**

**Before** (잘못됨):
```python
# STEP 1: Zoning
zone_result = zoning_engine.get_zone_type()

# STEP 2: Land Price  
price_result = landprice_engine.get_land_price()

# STEP 3: Capacity
far = get_far_by_zone(zone_type)  # ❌ 감정평가 무시

# STEP 4: Appraisal (마지막)
appraisal_result = appraisal_engine.run_appraisal()
```

**After** (올바름):
```python
# STEP 1: Appraisal FIRST (모든 데이터 생성)
appraisal_result = appraisal_engine_v39.run_complete_appraisal(
    address=request.address,
    land_area=request.land_area_sqm,
    physical_characteristics={
        "land_shape": request.land_shape,
        "slope": request.slope,
        "road_access": request.road_access,
        "orientation": request.orientation
    }
)

# STEP 2: Extract views from appraisal result
diagnosis = extract_diagnosis_view(appraisal_result)
capacity = extract_capacity_view(appraisal_result)
scenario = calculate_scenario_view(appraisal_result)

# STEP 3: Store context
context_id = store_context({
    "appraisal": appraisal_result,
    "diagnosis": diagnosis,
    "capacity": capacity,
    "scenario": scenario
})

# STEP 4: Return summary
return {
    "context_id": context_id,
    "summary": create_summary(appraisal_result)
}
```

##### **1.2) 새로운 Helper Functions 작성**

```python
def extract_diagnosis_view(appraisal_result: Dict) -> Dict:
    """감정평가 결과에서 토지진단 뷰 추출"""
    return {
        "suitability": determine_suitability(appraisal_result["zoning"]),
        "zoning": appraisal_result["zoning"],  # 동일한 데이터
        "official_price": appraisal_result["official_price"],  # 동일
        "transactions": appraisal_result["transactions"],  # 동일
        "restrictions": appraisal_result.get("restrictions", []),
        "coordinates": appraisal_result["coordinates"]
    }

def extract_capacity_view(appraisal_result: Dict) -> Dict:
    """감정평가 결과에서 규모검토 뷰 추출"""
    zoning = appraisal_result["zoning"]
    land_area = appraisal_result["land_info"]["land_area"]
    
    # 감정평가의 FAR/BCR 강제 사용
    far = zoning["final_far"]
    bcr = zoning["bcr"]
    
    max_floor_area = land_area * (far / 100)
    max_units = estimate_units(max_floor_area)
    
    return {
        "zoning": zoning,  # 동일한 zoning
        "far": far,
        "bcr": bcr,
        "max_floor_area": max_floor_area,
        "max_units": max_units,
        "land_area": land_area
    }

def calculate_scenario_view(appraisal_result: Dict) -> Dict:
    """감정평가 결과 기반 시나리오 계산"""
    base_value = appraisal_result["final_value"]
    land_area = appraisal_result["land_info"]["land_area"]
    max_floor_area = appraisal_result["land_info"]["land_area"] * \
                     (appraisal_result["zoning"]["final_far"] / 100)
    
    scenarios = []
    for scenario_type in ["A안: 청년형", "B안: 신혼형", "C안: 고령자형"]:
        scenario_data = calculate_single_scenario(
            scenario_type=scenario_type,
            base_value=base_value,
            land_area=land_area,
            max_floor_area=max_floor_area
        )
        scenarios.append(scenario_data)
    
    # 최적 시나리오 자동 선택
    recommended = select_best_scenario(scenarios)
    
    return {
        "scenarios": scenarios,
        "recommended": recommended,
        "base_value": base_value  # 감정평가 기준 가격
    }
```

---

### 🟧 **Phase 2: API Gateway 개선** (30분)

#### **목표**
- run_analysis 단일 API로 모든 계산 수행
- context 저장 후 UI는 읽기 전용 endpoint만 사용

#### **작업 내용**

##### **2.1) 기존 endpoint 수정**

```python
@router_v40.post("/run-analysis")
async def run_full_land_analysis(request: FullLandAnalysisRequest):
    """
    🚀 v40.2 UNIFIED ANALYSIS - Appraisal-First Architecture
    
    실행 순서:
    1. Appraisal Engine v39 실행 (모든 데이터 생성)
    2. 파생 뷰 추출 (진단, 규모, 시나리오)
    3. Context 저장
    4. Summary 반환
    """
    try:
        context_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # =======================================
        # STEP 1: APPRAISAL FIRST
        # =======================================
        appraisal_result = await run_complete_appraisal(
            address=request.address,
            land_area_sqm=request.land_area_sqm,
            physical_characteristics={
                "land_shape": request.land_shape,
                "slope": request.slope,
                "road_access": request.road_access,
                "orientation": request.orientation
            }
        )
        
        # 검증: 필수 필드 확인
        validate_appraisal_result(appraisal_result)
        
        # =======================================
        # STEP 2: EXTRACT VIEWS
        # =======================================
        diagnosis = extract_diagnosis_view(appraisal_result)
        capacity = extract_capacity_view(appraisal_result)
        scenario = calculate_scenario_view(appraisal_result)
        
        # =======================================
        # STEP 3: STORE CONTEXT
        # =======================================
        complete_context = {
            "context_id": context_id,
            "timestamp": timestamp,
            "input": {
                "address": request.address,
                "land_area_sqm": request.land_area_sqm,
                "physical_characteristics": {
                    "land_shape": request.land_shape,
                    "slope": request.slope,
                    "road_access": request.road_access,
                    "orientation": request.orientation
                }
            },
            "appraisal": appraisal_result,  # ← Single Source of Truth
            "diagnosis": diagnosis,
            "capacity": capacity,
            "scenario": scenario
        }
        
        CONTEXT_STORAGE[context_id] = complete_context
        
        # =======================================
        # STEP 4: RETURN SUMMARY
        # =======================================
        return {
            "status": "success",
            "context_id": context_id,
            "timestamp": timestamp,
            "summary": {
                "appraisal_value": appraisal_result["final_value"],
                "value_per_sqm": appraisal_result["value_per_sqm"],
                "suitability": diagnosis["suitability"],
                "max_units": capacity["max_units"],
                "recommended_scenario": scenario["recommended"]
            },
            "message": "종합 토지분석 완료. Context ID로 상세 결과를 조회하세요."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류: {str(e)}")
```

##### **2.2) 조회 전용 endpoints**

```python
@router_v40.get("/context/{context_id}/{tab}")
async def get_context_tab(context_id: str, tab: str):
    """
    특정 탭 데이터 조회 (READ-ONLY)
    
    Valid tabs:
    - diagnosis: 토지진단
    - capacity: 규모검토
    - appraisal: 감정평가
    - scenario: 시나리오
    """
    if context_id not in CONTEXT_STORAGE:
        raise HTTPException(status_code=404, detail="Context를 찾을 수 없습니다.")
    
    context = CONTEXT_STORAGE[context_id]
    
    # 탭 검증
    valid_tabs = ['diagnosis', 'capacity', 'appraisal', 'scenario']
    if tab not in valid_tabs:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 탭입니다. 사용 가능: {', '.join(valid_tabs)}"
        )
    
    # 단순 조회만 (재계산 없음)
    return {
        "tab": tab,
        "context_id": context_id,
        "data": context[tab]
    }
```

---

### 🟨 **Phase 3: 보고서 엔진 통합** (1시간)

#### **목표**
- 보고서 엔진에서 v39 결과를 100% 사용하도록 코드 개편
- 보고서 내 fallback 값 사용 불가하도록 차단 로직 삽입

#### **작업 내용**

##### **3.1) 보고서 생성 검증**

```python
@router_v40.get("/reports/{context_id}/{report_type}")
async def generate_report(context_id: str, report_type: str):
    """
    보고서 생성 (감정평가 필수)
    
    Report Types:
    - appraisal_v39: 23페이지 전문 감정평가서
    - lh_submission: LH 제출용 보고서
    - professional: 전문가용 보고서
    - brief: 토지주 간략 보고서
    """
    # Context 조회
    if context_id not in CONTEXT_STORAGE:
        raise HTTPException(status_code=404, detail="Context를 찾을 수 없습니다.")
    
    context = CONTEXT_STORAGE[context_id]
    
    # ===================================
    # 검증: 감정평가 결과 필수
    # ===================================
    if "appraisal" not in context or not context["appraisal"]:
        raise HTTPException(
            status_code=400,
            detail="감정평가 결과가 없습니다. 먼저 토지분석을 실행하세요."
        )
    
    # 검증: 필수 필드 확인
    validate_appraisal_for_report(context["appraisal"])
    
    # ===================================
    # 보고서 생성 (100% 감정평가 데이터 사용)
    # ===================================
    if report_type == "appraisal_v39":
        from app.services.v30.pdf_generator_v39 import PDFGeneratorV39
        pdf_gen = PDFGeneratorV39()
        pdf_bytes = pdf_gen.generate(context["appraisal"])
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Appraisal_Report_v39.pdf"
            }
        )
    
    # 다른 보고서 타입 처리...
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 보고서 타입입니다.")


def validate_appraisal_for_report(appraisal: Dict):
    """보고서 생성을 위한 감정평가 데이터 검증"""
    required_fields = [
        "final_value",
        "value_per_sqm",
        "zoning.final_zone",
        "official_price",
        "transactions",  # minimum 10건
        "premium_summary"
    ]
    
    for field in required_fields:
        if not get_nested_value(appraisal, field):
            raise ValidationError(f"필수 필드 누락: {field}")
    
    # 거래사례 개수 확인
    if len(appraisal.get("transactions", [])) < 10:
        raise ValidationError("거래사례가 부족합니다 (최소 10건 필요)")
```

---

### 🟩 **Phase 4: UI 데이터 바인딩 맞춤화** (1시간)

#### **목표**
- index_v40.html → run_analysis 결과만 사용
- 각 탭은 `/context/{uuid}` API만 호출
- 중복 계산 제거

#### **변경 파일**
- `public/index_v40_FINAL.html`
- `public/js/app_v40.js`

#### **작업 내용**

##### **4.1) app_v40.js 수정**

```javascript
// =======================================
// v40.2: Appraisal-First Architecture
// =======================================

let globalContextId = null;  // 전역 Context ID 저장

// 분석 실행 (1회만)
async function runAnalysis() {
    const address = document.getElementById('address').value;
    const landArea = parseFloat(document.getElementById('land_area').value);
    
    // 입력 검증
    if (!address || !landArea) {
        alert('주소와 면적을 입력하세요');
        return;
    }
    
    // 진행 상황 표시
    showProgressIndicator();
    
    try {
        // API 호출 (1회 실행)
        const response = await fetch('/api/v40/run-analysis', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                address: address,
                land_area_sqm: landArea,
                land_shape: document.getElementById('land_shape')?.value || '정방형',
                slope: document.getElementById('slope')?.value || '평지',
                road_access: document.getElementById('road_access')?.value || '중로',
                orientation: document.getElementById('orientation')?.value || '남향'
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Context ID 저장
            globalContextId = result.context_id;
            
            // 대시보드 표시
            showDashboard(result.summary);
            
            // 모든 탭 데이터 로드 (조회만)
            loadAllTabs(globalContextId);
        }
        
    } catch (error) {
        alert('분석 중 오류가 발생했습니다: ' + error.message);
    } finally {
        hideProgressIndicator();
    }
}

// 모든 탭 데이터 로드 (READ-ONLY)
async function loadAllTabs(contextId) {
    const tabs = ['diagnosis', 'capacity', 'appraisal', 'scenario'];
    
    for (const tab of tabs) {
        await loadTabData(contextId, tab);
    }
}

// 특정 탭 데이터 로드
async function loadTabData(contextId, tab) {
    try {
        const response = await fetch(`/api/v40/context/${contextId}/${tab}`);
        const result = await response.json();
        
        // 탭에 데이터 표시
        renderTabData(tab, result.data);
        
    } catch (error) {
        console.error(`${tab} 탭 로드 실패:`, error);
    }
}

// 탭 클릭 이벤트 (재계산 없음, 이미 로드된 데이터 표시만)
function onTabClick(tabName) {
    // 단순히 표시/숨김만 토글
    hideAllTabs();
    showTab(tabName);
}

// 보고서 다운로드
async function downloadReport(reportType) {
    if (!globalContextId) {
        alert('먼저 토지분석을 실행하세요');
        return;
    }
    
    const url = `/api/v40/reports/${globalContextId}/${reportType}`;
    window.open(url, '_blank');
}
```

---

### 🟦 **Phase 5: 최종 QA 및 회귀테스트** (1시간)

#### **테스트 요소**

##### **5.1) 데이터 일관성 테스트**

```python
def test_data_consistency():
    """모든 탭에서 동일한 데이터 표시 확인"""
    test_addresses = [
        "서울특별시 관악구 신림동 1524-8",
        "서울특별시 강남구 역삼동 123-45",
        "부산광역시 해운대구 우동 456-78"
    ]
    
    for address in test_addresses:
        context_id = run_analysis(address, 450)
        context = get_context(context_id)
        
        # 용도지역 일치 확인
        appraisal_zone = context["appraisal"]["zoning"]["final_zone"]
        diagnosis_zone = context["diagnosis"]["zoning"]["final_zone"]
        capacity_zone = context["capacity"]["zoning"]["final_zone"]
        
        assert appraisal_zone == diagnosis_zone == capacity_zone, \
            f"용도지역 불일치: {address}"
        
        # 공시지가 일치 확인
        appraisal_price = context["appraisal"]["official_price"]
        diagnosis_price = context["diagnosis"]["official_price"]
        
        assert appraisal_price == diagnosis_price, \
            f"공시지가 불일치: {address}"
        
        print(f"✅ {address}: 데이터 일관성 검증 통과")
```

##### **5.2) 보고서 정합성 테스트**

```python
def test_report_consistency():
    """보고서와 감정평가 탭 데이터 일치 확인"""
    context_id = run_analysis("서울특별시 관악구 신림동 1524-8", 450)
    context = get_context(context_id)
    
    # PDF 생성
    pdf_bytes = generate_report(context_id, "appraisal_v39")
    
    # PDF 내용 추출 (텍스트 파싱)
    pdf_content = extract_pdf_content(pdf_bytes)
    
    # 감정평가 탭 데이터와 비교
    appraisal_value = context["appraisal"]["final_value"]
    
    # PDF에 동일한 값이 포함되어 있는지 확인
    assert str(appraisal_value) in pdf_content, \
        "보고서와 감정평가 데이터 불일치"
    
    print("✅ 보고서 정합성 검증 통과")
```

---

## 📊 작업 타임라인 (Timeline)

```
Hour 1:  Phase 1 - 엔진 구조 개선
         ├─ router.py 리팩토링 (40min)
         └─ Helper functions 작성 (20min)

Hour 2:  Phase 2 - API Gateway 개선 (30min)
         Phase 3 - 보고서 엔진 통합 시작 (30min)

Hour 3:  Phase 3 - 보고서 엔진 통합 완료 (30min)
         Phase 4 - UI 데이터 바인딩 시작 (30min)

Hour 4:  Phase 4 - UI 완료 (30min)
         Phase 5 - QA 및 테스트 (30min)

Total: 4시간
```

---

## ✅ 완료 체크리스트

### **Phase 1 완료 확인**
- [ ] router.py에서 appraisal_engine이 첫 번째로 실행됨
- [ ] extract_diagnosis_view() 함수 작동 확인
- [ ] extract_capacity_view() 함수 작동 확인
- [ ] calculate_scenario_view() 함수 작동 확인

### **Phase 2 완료 확인**
- [ ] /run-analysis API가 context_id 반환
- [ ] /context/{id}/{tab} API가 조회만 수행 (재계산 없음)
- [ ] Context 저장 구조가 올바름

### **Phase 3 완료 확인**
- [ ] 보고서 생성 전 감정평가 검증 로직 작동
- [ ] 감정평가 없으면 에러 발생 확인
- [ ] PDF에 표시된 데이터가 appraisal_result와 100% 일치

### **Phase 4 완료 확인**
- [ ] Frontend에서 1회 실행 + N회 조회 구조 작동
- [ ] 탭 클릭 시 재계산 일어나지 않음
- [ ] globalContextId가 올바르게 저장/사용됨

### **Phase 5 완료 확인**
- [ ] 10개 주소로 데이터 일관성 테스트 통과
- [ ] 보고서 정합성 테스트 통과
- [ ] 회귀 테스트 스위트 실행 성공

---

## 🚀 배포 준비 (Deployment Ready)

### **Before Deployment**
1. 모든 Phase 완료 확인
2. 전체 테스트 스위트 통과
3. 문서 업데이트 완료
4. Git commit 및 PR 생성

### **After Deployment**
1. 운영 모니터링 24시간
2. 사용자 피드백 수집
3. 버그 리포트 빠른 대응

---

**문서 작성**: GenSpark AI Developer  
**상태**: 🟢 READY TO START  
**Target Completion**: 2025-12-14 (오늘)  
**Effort**: 4시간 (집중 작업)
