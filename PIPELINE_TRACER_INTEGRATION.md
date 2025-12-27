# Pipeline Tracer Integration - Critical Changes

이 파일은 `app/api/endpoints/pipeline_reports_v4.py`에 적용할 변경사항입니다.

## 변경 1: Import 추가 (파일 상단)

```python
# 기존 import 유지하고 아래 추가
from app.services.pipeline_tracer import (
    PipelineTracer,
    PipelineStage,
    ReasonCode,
    PipelineExecutionError
)
from app.services.data_contract import DataValidationError, DataBindingError
```

## 변경 2: analyze 엔드포인트 수정

### Step 1: Tracer 초기화 (358행 근처)
```python
async def run_pipeline_analysis(request: PipelineAnalysisRequest):
    # 🔥 NEW: Initialize Pipeline Tracer
    tracer = PipelineTracer(parcel_id=request.parcel_id)
    
    try:
        tracer.set_stage(PipelineStage.INIT)
        start_time = time.time()
        # ... 기존 코드 계속
```

### Step 2: 캐시된 결과 반환 전 (398행 근처)
```python
            # 캐시 응답 반환 전에 추가
            tracer.complete()
            
            return PipelineAnalysisResponse(...)
```

### Step 3: Pipeline 실행 부분 (401-402행)
```python
        # 🔥 Run pipeline with stage tracking
        logger.info(f"🚀 Running 6-MODULE pipeline for {request.parcel_id}")
        
        # Stage: M1-M6 Pipeline Execution
        tracer.set_stage(PipelineStage.M2)
        
        try:
            result = pipeline.run(request.parcel_id)
        except TimeoutError as e:
            raise tracer.wrap(
                e,
                ReasonCode.EXTERNAL_API_TIMEOUT,
                details={"module": "Pipeline", "timeout_sec": 60}
            )
        except AttributeError as e:
            # Common error: missing M1 data
            if "land" in str(e).lower() or "context" in str(e).lower():
                raise tracer.wrap(
                    e,
                    ReasonCode.MODULE_DATA_MISSING,
                    message_ko="M1 입력 데이터가 누락되었습니다. M1 확정을 먼저 완료해 주세요.",
                    details={"missing_context": "M1", "error": str(e)}
                )
            raise
```

### Step 4: 데이터 조립 단계 (411행 근처)
```python
        # Cache results
        results_cache[request.parcel_id] = result
        
        # 🔥 Stage: Data Assembly
        tracer.set_stage(PipelineStage.ASSEMBLE)
        
        context_id = request.parcel_id
        # ... 기존 assembled_data 생성 코드 ...
```

### Step 5: 데이터 검증 단계 (저장 전, 458행 근처)
```python
        # Store in context_storage
        tracer.set_stage(PipelineStage.SAVE)
        
        try:
            context_storage.store_frozen_context(
                context_id=context_id,
                land_context=assembled_data,
                ttl_hours=24,
                parcel_id=request.parcel_id
            )
            logger.info(f"✅ Pipeline results saved to context_storage: {context_id}")
        except Exception as storage_err:
            # Storage error shouldn't fail the pipeline
            logger.error(f"⚠️ Failed to save to context_storage: {storage_err}")
            raise tracer.wrap(
                storage_err,
                ReasonCode.STORAGE_ERROR,
                details={"context_id": context_id}
            )
```

### Step 6: 완료 및 응답 (538-539행)
```python
        logger.info(f"✅ Pipeline completed in {execution_time_ms:.0f}ms")
        tracer.complete()
        return response
```

### Step 7: 예외 처리 전면 교체 (541-574행 전체)
```python
    except DataValidationError as e:
        # Data validation failed
        raise tracer.wrap(
            e,
            ReasonCode.DATA_BINDING_MISSING,
            details={"validation_errors": getattr(e, 'technical_message', str(e))}
        )
    
    except DataBindingError as e:
        # Data binding failed
        raise tracer.wrap(
            e,
            ReasonCode.DATA_BINDING_MISSING,
            details={
                "missing_paths": getattr(e, 'missing_paths', []),
                "error": str(e)
            }
        )
    
    except PipelineExecutionError:
        # Already wrapped by tracer, just re-raise
        raise
    
    except Exception as e:
        # Unknown error - wrap it
        logger.error(f"❌ Pipeline analysis failed: {str(e)}", exc_info=True)
        raise tracer.wrap(
            e,
            ReasonCode.UNKNOWN,
            details={
                "error_type": type(e).__name__,
                "parcel_id": request.parcel_id
            }
        )
```

## 변경 3: 에러 핸들러 추가 (라우터 상단, 100행 근처)

```python
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse  # 추가

# ... 기존 import ...

router = APIRouter()

# 🔥 NEW: PipelineExecutionError Handler
@app.exception_handler(PipelineExecutionError)
async def pipeline_execution_error_handler(request, exc: PipelineExecutionError):
    """
    파이프라인 실행 에러 표준 응답
    
    Returns:
        JSONResponse with stage, reason_code, debug_id, message_ko
    """
    return JSONResponse(
        status_code=400,
        content=exc.to_dict()
    )

# ... 기존 라우터 정의 ...
```

---

## 테스트 방법

### 1. 정상 실행
```bash
curl -X POST http://localhost:8001/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d '{"parcel_id": "test-001"}'
```

### 2. M1 미확정 에러
```bash
curl -X POST http://localhost:8001/api/v4/pipeline/analyze \
  -H "Content-Type: application/json" \
  -d '{"parcel_id": "nonexistent-001"}'

# 예상 응답:
# {
#   "ok": false,
#   "stage": "M2",
#   "reason_code": "MODULE_DATA_MISSING",
#   "message_ko": "M1 입력 데이터가 누락되었습니다...",
#   "debug_id": "pl_20251227_xxxxxxxx"
# }
```

### 3. 로그 확인
```bash
# debug_id로 전체 스택트레이스 검색
grep "pl_20251227_xxxxxxxx" server.log
```

---

## 완료 체크리스트

- [ ] Import 추가
- [ ] Tracer 초기화
- [ ] 단계별 set_stage 호출
- [ ] Pipeline 실행에 try/except 추가
- [ ] 데이터 조립/검증 단계 표시
- [ ] 예외 처리 전면 교체
- [ ] 에러 핸들러 추가
- [ ] 테스트 실행

---

**중요**: 이 변경은 backward compatible합니다. 기존 API 응답은 유지되고, 
에러 발생 시에만 새로운 표준화된 응답이 반환됩니다.
