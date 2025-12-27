"""
Pipeline Failure Tracking Tests
================================

파이프라인 실패 추적 시스템 테스트

Author: ZeroSite Backend Team
Date: 2025-12-27
"""

import pytest
from app.services.pipeline_tracer import (
    PipelineTracer,
    PipelineStage,
    ReasonCode,
    PipelineExecutionError
)


def test_tracer_initialization():
    """Tracer 초기화 테스트"""
    tracer = PipelineTracer(parcel_id="test-001")
    
    assert tracer.parcel_id == "test-001"
    assert tracer.trace_id.startswith("pl_")
    assert tracer.current_stage == PipelineStage.INIT
    assert len(tracer.stage_history) == 0


def test_tracer_set_stage():
    """단계 설정 테스트"""
    tracer = PipelineTracer(parcel_id="test-002")
    
    tracer.set_stage(PipelineStage.M1_INPUT)
    assert tracer.current_stage == PipelineStage.M1_INPUT
    assert len(tracer.stage_history) == 1
    
    tracer.set_stage(PipelineStage.M2)
    assert tracer.current_stage == PipelineStage.M2
    assert len(tracer.stage_history) == 2


def test_tracer_wrap_exception():
    """예외 래핑 테스트"""
    tracer = PipelineTracer(parcel_id="test-003")
    tracer.set_stage(PipelineStage.M2)
    
    original_error = TimeoutError("Connection timeout")
    
    wrapped = tracer.wrap(
        original_error,
        ReasonCode.EXTERNAL_API_TIMEOUT,
        details={"endpoint": "https://api.example.com"}
    )
    
    assert isinstance(wrapped, PipelineExecutionError)
    assert wrapped.stage == PipelineStage.M2
    assert wrapped.reason_code == ReasonCode.EXTERNAL_API_TIMEOUT
    assert wrapped.debug_id == tracer.trace_id
    assert "M2 토지감정평가" in wrapped.message_ko
    assert "외부 API 응답이 지연" in wrapped.message_ko
    assert wrapped.details["endpoint"] == "https://api.example.com"


def test_tracer_wrap_with_custom_message():
    """커스텀 메시지로 예외 래핑 테스트"""
    tracer = PipelineTracer(parcel_id="test-004")
    tracer.set_stage(PipelineStage.M3)
    
    original_error = ValueError("Invalid housing type")
    custom_message = "M3 선호유형 분석 중 유형 데이터가 유효하지 않습니다."
    
    wrapped = tracer.wrap(
        original_error,
        ReasonCode.MODULE_DATA_MISSING,
        message_ko=custom_message
    )
    
    assert wrapped.message_ko == custom_message
    assert wrapped.stage == PipelineStage.M3


def test_pipeline_execution_error_to_dict():
    """PipelineExecutionError.to_dict() 테스트"""
    tracer = PipelineTracer(parcel_id="test-005")
    tracer.set_stage(PipelineStage.M4)
    
    error = tracer.wrap(
        Exception("Test error"),
        ReasonCode.VALIDATION_FAILED,
        details={"test_key": "test_value"}
    )
    
    error_dict = error.to_dict()
    
    assert error_dict["ok"] is False
    assert error_dict["stage"] == PipelineStage.M4
    assert error_dict["reason_code"] == ReasonCode.VALIDATION_FAILED
    assert error_dict["debug_id"] == tracer.trace_id
    assert "message_ko" in error_dict
    assert error_dict["details"]["test_key"] == "test_value"


def test_reason_code_messages():
    """각 ReasonCode에 대한 한국어 메시지 테스트"""
    tracer = PipelineTracer(parcel_id="test-006")
    
    # ADDRESS_NOT_FOUND
    tracer.set_stage(PipelineStage.M1_INPUT)
    error = tracer.wrap(Exception(), ReasonCode.ADDRESS_NOT_FOUND)
    assert "주소를 찾을 수 없습니다" in error.message_ko
    
    # API_KEY_MISSING
    tracer.set_stage(PipelineStage.M2)
    error = tracer.wrap(Exception(), ReasonCode.API_KEY_MISSING)
    assert "API 키가 설정되지 않았습니다" in error.message_ko
    
    # EXTERNAL_API_TIMEOUT
    tracer.set_stage(PipelineStage.M3)
    error = tracer.wrap(Exception(), ReasonCode.EXTERNAL_API_TIMEOUT)
    assert "외부 API 응답이 지연" in error.message_ko
    
    # DATA_BINDING_MISSING
    tracer.set_stage(PipelineStage.VALIDATE)
    error = tracer.wrap(Exception(), ReasonCode.DATA_BINDING_MISSING)
    assert "필수 데이터가 누락" in error.message_ko


def test_tracer_complete():
    """파이프라인 완료 테스트"""
    tracer = PipelineTracer(parcel_id="test-007")
    
    tracer.set_stage(PipelineStage.M1_INPUT)
    tracer.set_stage(PipelineStage.M2)
    tracer.set_stage(PipelineStage.M3)
    tracer.complete()
    
    assert tracer.current_stage == PipelineStage.COMPLETE
    assert len(tracer.stage_history) == 4  # M1, M2, M3, COMPLETE


def test_stage_history_tracking():
    """단계 이력 추적 테스트"""
    tracer = PipelineTracer(parcel_id="test-008")
    
    stages = [
        PipelineStage.M1_INPUT,
        PipelineStage.M1_FREEZE,
        PipelineStage.M2,
        PipelineStage.M3,
        PipelineStage.M4
    ]
    
    for stage in stages:
        tracer.set_stage(stage)
    
    assert len(tracer.stage_history) == len(stages)
    
    # 각 이력 항목에 stage와 timestamp가 있는지 확인
    for history_item in tracer.stage_history:
        assert "stage" in history_item
        assert "timestamp" in history_item


def test_integration_with_pipeline():
    """파이프라인 통합 테스트 (모의)"""
    tracer = PipelineTracer(parcel_id="integration-test")
    
    try:
        # Stage 1: Init
        tracer.set_stage(PipelineStage.INIT)
        
        # Stage 2: M1 Input
        tracer.set_stage(PipelineStage.M1_INPUT)
        # ... M1 로직 ...
        
        # Stage 3: M2
        tracer.set_stage(PipelineStage.M2)
        # Simulate error
        raise TimeoutError("API timeout")
        
    except TimeoutError as e:
        error = tracer.wrap(e, ReasonCode.EXTERNAL_API_TIMEOUT)
        
        # 에러가 올바르게 래핑되었는지 확인
        assert error.stage == PipelineStage.M2
        assert error.reason_code == ReasonCode.EXTERNAL_API_TIMEOUT
        assert error.debug_id.startswith("pl_")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
