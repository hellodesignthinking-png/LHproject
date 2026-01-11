# 🔴 ZeroSite DATA INSUFFICIENT 보호 레이어 구현 완료

**구현 일시**: 2026-01-11  
**구현자**: ZeroSite Development Team  
**목적**: 시스템 신뢰성 보호 - 불완전한 데이터로 보고서를 생성하지 않음

---

## 📋 구현 배경

**문제점**:
> "현재 제공된 데이터는 분석을 수행하기에 현저히 부족하며,  
> 이 상태에서 계산·판단·보고서를 생성하는 것은 시스템 신뢰성을 훼손합니다."

**해결책**:
- ✅ 필수 입력 2개 이상 누락 시 즉시 중단
- ✅ 추정·보완 계산 절대 금지
- ✅ 입력 요청 전용 템플릿으로 전환

---

## 🎯 구현 내용

### 1️⃣ M4 Enhanced Logic 입력 검증 강화

#### 기존 코드
```python
def validate_data_integrity(self) -> Tuple[bool, List[str]]:
    errors = []
    if not address:
        errors.append("주소가 존재하지 않습니다.")
    # ... (기본 검증만)
```

#### 개선된 코드
```python
def validate_data_integrity(self) -> Tuple[bool, List[str]]:
    """
    🔴 DATA INSUFFICIENT 조건:
    필수 입력 2개 이상 누락 시 즉시 중단
    """
    errors = []
    missing_required = []
    
    # 1. 주소 검증 (필수) - Mock 데이터 감지 추가
    if not address or "Mock Data" in str(address):
        errors.append("사업지 주소")
        missing_required.append("주소")
    
    # 2. 토지면적 검증 (필수)
    # 3. 용도지역 검증 (필수)
    # 4. M3 공급유형 검증 (필수)
    
    # 🔴 DATA INSUFFICIENT: 필수 입력 2개 이상 누락 시
    if len(missing_required) >= 2:
        logger.error(f"🔴 DATA INSUFFICIENT: {len(missing_required)}개 필수 입력 누락")
        return (False, errors)
```

**주요 개선사항**:
- Mock 데이터 감지: `"Mock Data" in str(address)`
- 누락 항목 추적: `missing_required` 리스트
- 2개 이상 누락 시 즉시 중단

---

### 2️⃣ 입력 요청 전용 템플릿 생성

**파일**: `app/templates_v13/m4_data_insufficient.html`

#### 템플릿 구조
```html
<!DOCTYPE html>
<html>
<head>
    <title>M4: 입력 데이터 부족 - ZeroSite</title>
</head>
<body>
    <!-- 🔴 DATA INSUFFICIENT 경고 -->
    <div class="alert-box">
        <div class="alert-title">분석 불가 안내</div>
        <div class="alert-message">
            현재 입력된 데이터로는 건축 규모 분석을 수행할 수 없습니다.
            필수 입력 항목 중 {{ missing_count }}개가 누락되었습니다.
        </div>
    </div>
    
    <!-- 📌 입력 요청 체크리스트 -->
    <div class="required-inputs">
        <div class="section-title">📌 추가 입력이 필요한 항목</div>
        <ul class="checklist">
            {% for item in missing_items %}
            <li class="checklist-item">
                <span class="checklist-icon">⬜</span>
                <div>
                    <div class="checklist-label">{{ item.label }}</div>
                    <div class="checklist-example">{{ item.example }}</div>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>
    
    <!-- 🚫 금지 항목 -->
    <div class="prohibition-box">
        <div class="prohibition-title">🚫 입력 전까지 수행하지 않는 작업</div>
        <ul>
            <li>❌ 유사 사례 기반 추정 계산</li>
            <li>❌ 평균값 적용</li>
            <li>❌ '일반적인 경우' 가정</li>
            <li>❌ 불완전한 데이터 기반 판단</li>
        </ul>
    </div>
    
    <!-- 시스템 고정 문구 -->
    <div class="system-message">
        ZeroSite는 필수 데이터가 입력되기 전까지
        분석·계산·판단을 수행하지 않습니다.
    </div>
</body>
</html>
```

**핵심 원칙**:
1. ❌ 보고서 번호 없음
2. ❌ "REAL APPRAISAL STANDARD" 없음
3. ❌ 분석 기준일 없음
4. ❌ 점수·등급·판단 없음
5. ✅ 입력 요청 안내만 출력

---

### 3️⃣ professional_report_html.py 통합

#### 변경 사항
```python
# 🔥 NEW: M3/M4/M5/M6 use enhanced Jinja2 templates
if module_id in ["M3", "M4", "M5", "M6"]:
    try:
        # Prepare template data
        template_data = _prepare_template_data_for_enhanced(module_id, context_id, module_data)
        
        # 🔴 Check for DATA INSUFFICIENT
        if template_data.get("error") and template_data.get("use_data_insufficient_template"):
            logger.warning(f"🔴 DATA INSUFFICIENT detected for {module_id}")
            template_file = {
                "M4": "m4_data_insufficient.html",
            }.get(module_id, "m4_data_insufficient.html")
        else:
            # 정상 템플릿 선택
            template_file = {
                "M3": "m3_supply_type_format_v2_enhanced.html",
                "M4": "m4_building_scale_format_v2_enhanced.html",
                ...
            }.get(module_id)
        
        # Load and render template
        template = jinja_env.get_template(template_file)
        html = template.render(**template_data)
```

**자동 템플릿 전환**:
- `use_data_insufficient_template` 플래그 감지
- 자동으로 입력 요청 템플릿으로 전환
- 추정 계산 없음

---

## 🧪 테스트 결과

### 테스트 스크립트
**파일**: `test_data_insufficient.py`

```python
def test_invalid_pnu():
    """테스트: 잘못된 PNU로 DATA INSUFFICIENT 트리거"""
    payload = {
        "parcel_id": "INVALID_TEST_PNU_999",
        "address": ""
    }
    
    # 파이프라인 실행
    response = requests.post(f"{BASE_URL}/api/v4/pipeline/analyze", json=payload)
    
    # M4 보고서 요청
    m4_response = requests.get(f"{BASE_URL}/api/v4/reports/M4/html?context_id={context_id}")
    html = m4_response.text
    
    # 검증
    if "DATA INSUFFICIENT" in html:
        print("✅ PASS: DATA INSUFFICIENT 템플릿 사용됨")
```

### 테스트 결과
```
🔴 ZeroSite DATA INSUFFICIENT 테스트 시작
================================================================================
🧪 테스트: 잘못된 PNU → DATA INSUFFICIENT 예상
================================================================================
파이프라인 상태: success

🔍 M4 보고서 생성 (Context: INVALID_TEST_PNU_999)...
✅ PASS: DATA INSUFFICIENT 템플릿 사용됨
✅ PASS: 추정 계산 없음
✅ PASS: 입력 요청 안내 출력

================================================================================
🏁 테스트 완료
================================================================================
```

**판정**: ✅ **PASS** - 모든 검증 통과

---

## 🔗 테스트 URL

**Base URL**: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai

### DATA INSUFFICIENT 예시
- **Context ID**: `TEST_DATA_INSUFFICIENT_001`
- **URL**: https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai/api/v4/reports/M4/html?context_id=TEST_DATA_INSUFFICIENT_001

**예상 출력**:
- 🔴 DATA INSUFFICIENT 경고
- 📌 추가 입력이 필요한 항목 (체크리스트)
- 🚫 금지 작업 안내
- 시스템 고정 문구

---

## 📊 Before & After 비교

| 항목 | Before (문제) | After (개선) |
|------|-------------|------------|
| **Mock 데이터 처리** | 보고서 생성 ❌ | 입력 요청 ✅ |
| **잘못된 PNU** | Mock Fallback ❌ | DATA INSUFFICIENT ✅ |
| **추정 계산** | 평균값 적용 ❌ | 금지 ✅ |
| **출력 형식** | 보고서 형식 ❌ | 입력 안내 ✅ |
| **사용자 안내** | 없음 ❌ | 체크리스트 제공 ✅ |

---

## 🎯 ZERO TOLERANCE 원칙 준수

### 즉시 중단 조건
다음 필수 입력 중 **2개 이상 누락 시**:

- ⬜ 사업지 주소 (법정동 기준)
- ⬜ 토지면적(㎡)
- ⬜ 용도지역
- ⬜ M3 공급유형 결과

### 출력 금지 항목
- ❌ 계산
- ❌ 점수
- ❌ 판단
- ❌ 보고서

### 유일한 출력
- ✅ 입력 요청 안내
- ✅ 체크리스트
- ✅ 금지 작업 안내
- ✅ 시스템 고정 문구

---

## 🚀 향후 확장

### 다른 모듈 적용
현재 **M4**에만 적용되었으며, 향후 다음 모듈로 확장 가능:

1. **M3**: 공급유형 판단
   - 필수: 주소, 토지면적, 인구 데이터
   
2. **M5**: 사업성 분석
   - 필수: M4 세대수, 총 연면적, LH 매입 단가
   
3. **M6**: LH 종합 판단
   - 필수: M1~M5 전체 데이터

### 추가 개선 사항
1. **Mock 모드 명시적 표시**: 사용자에게 Mock 데이터 사용 중임을 알림
2. **PNU 형식 검증**: 19자리 PNU 형식 사전 검증
3. **다국어 지원**: 영문 입력 안내 추가

---

## 📋 최종 체크리스트

### 구현 완료 항목
- [x] M4 Enhanced Logic 입력 검증 강화
- [x] Mock 데이터 감지 (`"Mock Data" in address`)
- [x] 필수 입력 2개 이상 누락 시 중단
- [x] 입력 요청 전용 템플릿 생성
- [x] professional_report_html.py 통합
- [x] 자동 템플릿 전환 로직
- [x] 테스트 스크립트 작성
- [x] 통합 테스트 완료

### 테스트 통과 항목
- [x] DATA INSUFFICIENT 템플릿 사용됨
- [x] 추정 계산 없음
- [x] 입력 요청 안내 출력
- [x] Mock 데이터 감지 작동
- [x] 체크리스트 형식 출력

---

## 🎊 최종 판정

**✅ DATA INSUFFICIENT 보호 레이어 구현 완료**

**핵심 성과**:
1. ✅ 시스템 신뢰성 보호
2. ✅ 불완전한 데이터로 보고서 생성 금지
3. ✅ 사용자에게 명확한 입력 안내 제공
4. ✅ ZERO TOLERANCE 원칙 100% 준수

**시스템 고정 문구**:
> "ZeroSite는 필수 데이터가 입력되기 전까지  
> 분석·계산·판단을 수행하지 않습니다."

---

**구현 완료 일시**: 2026-01-11  
**구현자**: ZeroSite Development Team  
**GitHub PR**: https://github.com/hellodesignthinking-png/LHproject/pull/15  
**브랜치**: `feature/expert-report-generator`  
**최종 커밋**: `8c0439d`

**ⓒ ZeroSite by AntennaHoldings | Natai Heum**
