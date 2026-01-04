# 🔒 ZeroSite v6.5 - STATE MANAGEMENT & DATA FLOW LOCK

## FINAL LOCK: 주소 변경 시 전 모듈 데이터 100% 갱신 보장

**Version**: REAL APPRAISAL STANDARD v6.5 FINAL - STATE LOCK  
**Date**: 2025-12-29  
**Status**: 🔴 **CRITICAL - MUST APPLY BEFORE PUBLIC RELEASE**

---

## ⚠️ 현재 상태 진단

### ✅ 완벽한 부분
- M2~M6 보고서 품질: A++
- 모듈 간 논리 연결: 완전
- 파이프라인 구조: 완벽

### 🔴 위험한 부분
- **주소 변경 시 컨텍스트 초기화**: 명시되지 않음
- **모듈별 데이터 생성 시점**: 불분명
- **Single Execution Rule**: 부재

### 🚨 위험 시나리오
```
사용자가 주소 A 입력 → M2~M6 생성 (context_id: A123)
사용자가 주소 B 입력 → M2는 B 기준 (context_id: B456)
                    → M4·M5는 A 캐시 재사용 가능성 ⚠️
```

**결과**: 주소 B 입력했는데 일부 보고서는 주소 A 데이터 포함 가능

---

## 🔒 FINAL STATE MANAGEMENT LOCK PROMPT

### RULE 1: 주소 입력 시 컨텍스트 강제 초기화

```
[랜딩페이지] 주소 입력
     ↓
[MANDATORY] 기존 context_id 무효화
     ↓
[MANDATORY] 새로운 context_id 생성
     ↓
[MANDATORY] 이전 분석 결과 연결 차단
```

**적용 위치**: 
- `app.py` 또는 `main_api.py`의 주소 입력 핸들러
- 주소 변경 감지 시 무조건 새 context_id 생성

**코드 예시**:
```python
@app.route('/api/analyze', methods=['POST'])
def analyze_address():
    address = request.json.get('address')
    
    # 🔒 RULE 1: 항상 새 context_id 생성
    context_id = f"CTX_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    # 🔒 이전 context 무효화
    clear_previous_context()
    
    # M1~M6 실행
    ...
```

---

### RULE 2: Single Source of Truth 선언

```
M1에서 생성된 context_id는
M2, M3, M4, M5, M6 전 모듈의
유일한 데이터 기준(Source of Truth)이다.
```

**금지 사항**:
- ❌ 모듈별 독립 실행
- ❌ 이전 context 재참조
- ❌ 부분 재계산
- ❌ 캐시 재사용

**적용 위치**:
- 모든 generator 파일 (`generate_m2_classic.py`, `generate_m3_supply_type.py`, ...)
- context_id를 **필수 파라미터**로 받도록 수정

**코드 예시**:
```python
def generate_report(context_id, address, ...):
    # 🔒 RULE 2: context_id 필수
    if not context_id:
        raise ValueError("context_id is required - no default context allowed")
    
    # 🔒 이전 context 데이터 사용 금지
    assert not is_cached_context(context_id), "Fresh context required"
    
    ...
```

---

### RULE 3: Full Pipeline Rebuild 규칙

**주소 1회 입력 = M2~M6 전체 재계산 1회**

```
1. M1: 주소 → 기본 컨텍스트 생성 (NEW context_id)
2. M2: 토지 시가 감정 (NEW - context_id 기반)
3. M3: 공급 유형 판단 (NEW - context_id 기반)
4. M4: 건축 규모 판단 (NEW - context_id 기반)
5. M5: 사업성 분석 (NEW - context_id 기반)
6. M6: LH 종합 판단 (NEW - context_id 기반)
```

**보장 사항**:
- ✅ 모든 모듈이 동일한 context_id 사용
- ✅ 모든 결과가 이번 주소 입력에만 유효
- ✅ 생성 시각(timestamp)이 동일한 분석 세션

**적용 위치**:
- `app.py`의 메인 파이프라인 실행 로직
- 순차 실행 보장 + context_id 전달 체인

**코드 예시**:
```python
def run_full_pipeline(address):
    # 🔒 RULE 3: 새 context_id로 전체 재계산
    context_id = generate_new_context_id()
    timestamp = datetime.now()
    
    # 순차 실행 - 모두 동일 context_id + timestamp
    m2_result = generate_m2(context_id, address, timestamp)
    m3_result = generate_m3(context_id, address, timestamp, m2_result)
    m4_result = generate_m4(context_id, address, timestamp, m3_result)
    m5_result = generate_m5(context_id, address, timestamp, m4_result)
    m6_result = generate_m6(context_id, address, timestamp, m5_result)
    
    return {
        'context_id': context_id,
        'timestamp': timestamp,
        'results': [m2, m3, m4, m5, m6]
    }
```

---

### RULE 4: 캐시 및 재사용 금지 규칙

**절대 허용하지 않는 항목**:
- ❌ 이전 주소의 분석 결과 재사용
- ❌ 모듈 단위 캐싱
- ❌ 점수, 판단 결과의 재참조
- ❌ static HTML의 context 혼용

**적용 위치**:
- 모든 generator 파일
- 데이터 로딩 로직

**검증 코드**:
```python
def validate_no_cache_reuse(context_id, module_name):
    """캐시 재사용 검증"""
    
    # 🔒 RULE 4: 이전 context 데이터 확인
    previous_contexts = get_all_context_ids()
    
    # context_id가 기존에 없어야 함
    assert context_id not in previous_contexts, \
        f"{module_name}: context_id {context_id} already exists - cache reuse detected!"
    
    # 생성 시각이 현재 세션이어야 함
    context_timestamp = parse_context_timestamp(context_id)
    current_session = get_current_session_start()
    
    assert context_timestamp >= current_session, \
        f"{module_name}: context from previous session detected!"
```

---

### RULE 5: 사용자 체감 규칙 (UI 기준)

**랜딩페이지 보장 사항**:
```
주소 입력 → "새 분석을 시작합니다"
         → M2~M6 진행 상태 표시
         → 모든 보고서 동일 시각(timestamp) 생성
```

**UI 표시 예시**:
```
[분석 중] 새로운 분석 세션을 시작합니다
         Context ID: CTX_20251229152400123
         
         ✅ M2 토지감정평가 완료
         ✅ M3 공급유형 판단 완료
         ✅ M4 건축규모 판단 완료
         ✅ M5 사업성분석 완료
         ✅ M6 종합판단 완료
         
         생성 시각: 2025-12-29 15:24:00
```

---

### RULE 6: 최종 검증 질문 (LOCK CONDITION)

**다음 4문항에 항상 YES여야 실행 허용**:

#### Q1: 주소를 바꾸면 모든 숫자가 달라질 수 있는가?
- ✅ YES: 새 context_id로 전체 재계산
- ❌ NO: 캐시 재사용 위험

#### Q2: 이전 주소의 결과가 섞일 가능성은 0%인가?
- ✅ YES: context_id 강제 초기화
- ❌ NO: 이전 context 재사용 위험

#### Q3: M2~M6 모든 보고서의 context_id는 동일한가?
- ✅ YES: Single Source of Truth
- ❌ NO: 모듈별 독립 실행 위험

#### Q4: 모든 보고서 생성 시각이 동일한 분석 세션인가?
- ✅ YES: Full Pipeline Rebuild
- ❌ NO: 부분 재계산 위험

**검증 스크립트**:
```python
def verify_state_management(results):
    """STATE MANAGEMENT LOCK 검증"""
    
    # Q1: 새 주소 = 새 숫자
    assert all_values_are_new(results), "Q1 FAIL: 캐시 재사용 감지"
    
    # Q2: 이전 context 혼입 없음
    assert no_previous_context_mixed(results), "Q2 FAIL: 이전 결과 섞임"
    
    # Q3: 동일 context_id
    context_ids = [r['context_id'] for r in results]
    assert len(set(context_ids)) == 1, "Q3 FAIL: context_id 불일치"
    
    # Q4: 동일 timestamp
    timestamps = [r['timestamp'] for r in results]
    time_diff = max(timestamps) - min(timestamps)
    assert time_diff < timedelta(seconds=60), "Q4 FAIL: 생성 시각 불일치"
    
    return True
```

---

## 📊 적용 전후 비교

| 항목 | 적용 전 | 적용 후 |
|------|---------|---------|
| **주소 변경 안정성** | ⚠️ 불확실 | ✅ 100% 보장 |
| **캐시 재사용 위험** | ⚠️ 존재 | ✅ 완전 차단 |
| **Context 혼입** | ⚠️ 가능 | ✅ 불가능 |
| **외부 공개 안전성** | ⚠️ 위험 | ✅ 안전 |
| **PUBLIC RELEASE** | ❌ NOT READY | ✅ **READY** |

---

## 🔧 구현 체크리스트

### Phase 1: 코드 수정
- [ ] `app.py`: 주소 입력 핸들러에 context_id 강제 초기화 추가
- [ ] 모든 generator: context_id 필수 파라미터로 수정
- [ ] 파이프라인 실행: 순차 실행 + context_id 전달 체인
- [ ] 캐시 금지: 모든 재사용 로직 제거

### Phase 2: 검증 스크립트
- [ ] `verify_state_management.py` 작성
- [ ] 4문항 자동 검증 로직 구현
- [ ] 테스트 시나리오 작성 (주소 A → B → C)

### Phase 3: 문서화
- [ ] STATE MANAGEMENT LOCK 적용 가이드
- [ ] 개발자 가이드 업데이트
- [ ] API 문서 업데이트

### Phase 4: 최종 검증
- [ ] 주소 변경 시나리오 테스트 (10회)
- [ ] context_id 일관성 확인
- [ ] timestamp 일관성 확인
- [ ] PUBLIC RELEASE 최종 승인

---

## 🎯 최종 선언

```
ZeroSite는 주소 단위로 판단한다.
모든 판단은 주소마다 새롭게 생성된다.
이전 주소의 결과는 절대 재사용하지 않는다.

이 규칙이 지켜지지 않으면,
ZeroSite는 실행을 중단하고 재시작한다.
```

---

## 📋 적용 우선순위

### 🔴 CRITICAL (즉시 적용 필수)
- **RULE 1**: 주소 입력 시 컨텍스트 강제 초기화
- **RULE 2**: Single Source of Truth
- **RULE 6**: 최종 검증 4문항

### 🟡 HIGH (빠른 시일 내 적용)
- **RULE 3**: Full Pipeline Rebuild
- **RULE 4**: 캐시 및 재사용 금지

### 🟢 MEDIUM (안정화 단계에서 적용)
- **RULE 5**: 사용자 체감 규칙 (UI)

---

## 🚨 경고

**이 문서의 규칙이 100% 적용되기 전까지는:**

❌ **PUBLIC RELEASE 금지**  
❌ **외부 공개 금지**  
❌ **실무 제출 금지**

**적용 후에만:**

✅ **PUBLIC RELEASE READY**  
✅ **외부 공개 안전**  
✅ **실무 제출 가능**

---

**Version**: REAL APPRAISAL STANDARD v6.5 FINAL - STATE LOCK  
**Date**: 2025-12-29  
**Company**: Antenna Holdings · Nataiheum  
**Engine**: ZeroSite Analysis Engine  

**🔒 STATE MANAGEMENT LOCK - MUST APPLY BEFORE PUBLIC RELEASE**
