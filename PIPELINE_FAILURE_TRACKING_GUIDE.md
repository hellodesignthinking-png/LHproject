# 파이프라인 실패 추적 시스템 구현 가이드

**날짜**: 2025-12-27  
**목표**: "Pipeline execution failed" → 정확한 실패 단계 + 원인 + 해결방법

---

## ✅ 완료된 작업

### 1. PipelineTracer 클래스 생성
**파일**: `app/services/pipeline_tracer.py`

- ✅ trace_id 자동 생성 (`pl_YYYYMMDD_xxxxxxxx`)
- ✅ 단계별 추적 (PipelineStage enum)
- ✅ 원인 코드 (ReasonCode enum)
- ✅ PipelineExecutionError 표준화
- ✅ 한국어 사용자 메시지 자동 생성
- ✅ 로그에 debug_id 기록

### 2. DataBindingError 개선
**파일**: `app/services/data_contract.py`

- ✅ missing_paths 필드 추가
- ✅ to_dict() 메서드로 API 응답 표준화
- ✅ validate_assembled_data()에 missing_paths 추적

---

## 📋 적용 가이드

### Step 1: 파이프라인 엔드포인트 수정

**파일**: `app/api/endpoints/pipeline_reports_v4.py`

```python
from app.services.pipeline_tracer import (
    PipelineTracer, 
    PipelineStage,
    ReasonCode,
    PipelineExecutionError
)

@router.post("/analyze")
async def run_pipeline_analysis(request: PipelineAnalysisRequest):
    """파이프라인 실행 (단계별 추적)"""
    
    # 🔥 NEW: Tracer 초기화
    tracer = PipelineTracer(parcel_id=request.parcel_id)
    
    try:
        # M1 단계
        tracer.set_stage(PipelineStage.M1_INPUT)
        # ... M1 로직 ...
        
        # M2 단계
        tracer.set_stage(PipelineStage.M2)
        try:
            result = pipeline.run(parcel_id=request.parcel_id)
        except TimeoutError as e:
            raise tracer.wrap(
                e,
                ReasonCode.EXTERNAL_API_TIMEOUT,
                details={"module": "M2", "api": "data.go.kr"}
            )
        
        # M3 단계
        tracer.set_stage(PipelineStage.M3)
        # ... M3 로직 ...
        
        # 데이터 조립
        tracer.set_stage(PipelineStage.ASSEMBLE)
        assembled_data = build_assembled_data(...)
        
        # 검증
        tracer.set_stage(PipelineStage.VALIDATE)
        validate_assembled_data(assembled_data, strict=True)
        
        # 완료
        tracer.complete()
        return {"ok": True, ...}
        
    except DataValidationError as e:
        raise tracer.wrap(e, ReasonCode.DATA_BINDING_MISSING)
        
    except PipelineExecutionError:
        # Already wrapped, re-raise
        raise
        
    except Exception as e:
        raise tracer.wrap(e, ReasonCode.UNKNOWN)
```

### Step 2: 에러 핸들러 추가

**파일**: `app/api/endpoints/pipeline_reports_v4.py`

엔드포인트 상단에 추가:

```python
@router.exception_handler(PipelineExecutionError)
async def pipeline_error_handler(request, exc: PipelineExecutionError):
    """파이프라인 에러 표준 응답"""
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )
```

### Step 3: 외부 API 호출에 timeout + retry 추가

**예시**: M2 토지 감정평가 API

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(2), wait=wait_fixed(1))
async def call_appraisal_api(address: str, timeout: int = 10):
    """
    토지감정평가 API 호출 (retry 2회)
    
    Raises:
        TimeoutError: 타임아웃 시
        APIKeyError: API 키 오류 시
    """
    async with asyncio.timeout(timeout):
        response = await external_api.call(address)
        
        if "SERVICE_KEY_IS_NOT_REGISTERED" in response.text:
            raise APIKeyError("Invalid API key")
        
        return response.json()
```

### Step 4: 주소 정규화 강화

**파일**: `app/services/address_normalizer.py` (신규 또는 기존 파일)

```python
def normalize_address(address: str) -> str:
    """
    주소 정규화
    
    - 괄호/호수/빌딩명 제거
    - 공백/특수문자 정리
    - 지번/도로명 구분
    """
    # 괄호 제거
    address = re.sub(r'\([^)]*\)', '', address)
    
    # 빌딩명 제거 (동, 아파트, 빌딩 등)
    address = re.sub(r'[\d]+동', '', address)
    address = re.sub(r'(아파트|빌딩|오피스텔)', '', address)
    
    # 공백 정리
    address = re.sub(r'\s+', ' ', address).strip()
    
    return address
```

---

## 🧪 테스트 시나리오

### 파일: `tests/test_pipeline_failure_tracking.py`

```python
def test_address_not_found_error():
    """주소 미검색 시 정확한 에러 반환"""
    response = client.post("/api/v4/pipeline/analyze", json={
        "parcel_id": "test-001",
        "address": "존재하지않는주소123"
    })
    
    assert response.status_code == 400
    data = response.json()
    assert data["reason_code"] == "ADDRESS_NOT_FOUND"
    assert data["stage"] == "M1_INPUT"
    assert "debug_id" in data


def test_external_api_timeout():
    """외부 API 타임아웃 에러"""
    # Mock timeout
    with mock.patch("external_api.call", side_effect=TimeoutError):
        response = client.post("/api/v4/pipeline/analyze", json={
            "parcel_id": "test-002"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["reason_code"] == "EXTERNAL_API_TIMEOUT"
        assert data["stage"] in ["M2", "M3"]


def test_missing_module_data():
    """모듈 데이터 누락 에러"""
    # Mock empty M3
    with mock.patch("pipeline.run") as mock_run:
        mock_run.return_value.housing_type = None
        
        response = client.post("/api/v4/pipeline/analyze", json={
            "parcel_id": "test-003"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert data["reason_code"] == "DATA_BINDING_MISSING"
        assert "missing_paths" in data["details"]
```

---

## 📊 예상 API 응답

### ✅ 성공 시

```json
{
  "ok": true,
  "parcel_id": "test-001",
  "context_id": "test-001",
  "execution_time_ms": 2341,
  "results": {...}
}
```

### ❌ 실패 시 (주소 미검색)

```json
{
  "ok": false,
  "stage": "M1_INPUT",
  "reason_code": "ADDRESS_NOT_FOUND",
  "message_ko": "M1 입력 단계에서 입력하신 주소를 찾을 수 없습니다. 지번 또는 도로명 주소를 다시 확인해 주세요.",
  "debug_id": "pl_20251227_a1b2c3d4",
  "details": {
    "original_error": "Search returned 0 results",
    "input_address": "존재하지않는주소123"
  }
}
```

### ❌ 실패 시 (API 타임아웃)

```json
{
  "ok": false,
  "stage": "M2",
  "reason_code": "EXTERNAL_API_TIMEOUT",
  "message_ko": "M2 토지감정평가 단계에서 외부 API 응답이 지연되어 분석이 중단되었습니다. 잠시 후 다시 시도해 주세요.",
  "debug_id": "pl_20251227_e5f6g7h8",
  "details": {
    "provider": "data.go.kr",
    "endpoint": "https://api.data.go.kr/...",
    "timeout_sec": 10
  }
}
```

### ❌ 실패 시 (데이터 누락)

```json
{
  "ok": false,
  "stage": "VALIDATE",
  "reason_code": "DATA_BINDING_MISSING",
  "message_ko": "데이터 검증 단계에서 필수 데이터가 누락되었습니다. 이전 단계의 데이터를 확인해 주세요.",
  "debug_id": "pl_20251227_i9j0k1l2",
  "details": {
    "missing_paths": [
      "modules.M3.summary.preferred_type",
      "modules.M3.summary.score"
    ]
  }
}
```

---

## 🎯 완료 기준

### 필수 (MUST)
- [ ] PipelineTracer 적용 ✅ (완료)
- [ ] DataBindingError에 missing_paths ✅ (완료)
- [ ] 파이프라인 엔드포인트에 단계별 try/except (진행 중)
- [ ] "Pipeline execution failed" 문자열 제거
- [ ] 모든 실패 응답에 debug_id 포함

### 권장 (SHOULD)
- [ ] 외부 API timeout + retry 추가
- [ ] 주소 정규화 강화
- [ ] API 키 검증 추가

### 선택 (COULD)
- [ ] 테스트 케이스 추가
- [ ] 로그 대시보드 연동
- [ ] 슬랙/이메일 알림

---

## 📚 참고 파일

- `app/services/pipeline_tracer.py` - 추적 시스템
- `app/services/data_contract.py` - 데이터 검증
- `app/api/endpoints/pipeline_reports_v4.py` - 파이프라인 엔드포인트
- `tests/test_pipeline_failure_tracking.py` - 테스트

---

**Status**: 기반 클래스 완료, 엔드포인트 적용 필요  
**Next**: pipeline_reports_v4.py에 Tracer 적용
