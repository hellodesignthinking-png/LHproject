"""
Pipeline Execution Tracer - 파이프라인 실행 추적 및 에러 컨텍스트
=====================================================

파이프라인 실행 중 각 단계를 추적하고, 
실패 시 정확한 단계와 원인을 기록하는 시스템

Author: ZeroSite Backend Team
Date: 2025-12-27
Version: 1.0
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """파이프라인 실행 단계"""
    INIT = "INIT"
    M1_INPUT = "M1_INPUT"
    M1_NORMALIZE = "M1_NORMALIZE"
    M1_FREEZE = "M1_FREEZE"
    M2 = "M2"
    M3 = "M3"
    M4 = "M4"
    M5 = "M5"
    M6 = "M6"
    ASSEMBLE = "ASSEMBLE"
    VALIDATE = "VALIDATE"
    SAVE = "SAVE"
    COMPLETE = "COMPLETE"


class ReasonCode(str, Enum):
    """실패 원인 코드"""
    # 주소 관련
    ADDRESS_NOT_FOUND = "ADDRESS_NOT_FOUND"
    ADDRESS_NORMALIZE_FAILED = "ADDRESS_NORMALIZE_FAILED"
    PNU_CONVERSION_FAILED = "PNU_CONVERSION_FAILED"
    
    # 외부 API
    API_KEY_MISSING = "API_KEY_MISSING"
    API_KEY_INVALID = "API_KEY_INVALID"
    EXTERNAL_API_TIMEOUT = "EXTERNAL_API_TIMEOUT"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    
    # 데이터 검증
    DATA_BINDING_MISSING = "DATA_BINDING_MISSING"
    MODULE_DATA_MISSING = "MODULE_DATA_MISSING"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    
    # 시스템
    STORAGE_ERROR = "STORAGE_ERROR"
    UNKNOWN = "UNKNOWN"


class PipelineExecutionError(Exception):
    """
    파이프라인 실행 에러 (표준화)
    
    항상 다음 정보를 포함:
    - stage: 실패한 단계
    - reason_code: 실패 원인 코드
    - debug_id: 디버깅용 추적 ID
    - message_ko: 한국어 사용자 메시지
    - details: 상세 정보 (dict)
    """
    
    def __init__(
        self,
        stage: PipelineStage,
        reason_code: ReasonCode,
        debug_id: str,
        message_ko: str,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        self.stage = stage
        self.reason_code = reason_code
        self.debug_id = debug_id
        self.message_ko = message_ko
        self.details = details or {}
        self.original_exception = original_exception
        
        # 로그 기록
        logger.error(
            f"[{debug_id}] Pipeline failed at {stage}: {reason_code} - {message_ko}",
            extra={
                "debug_id": debug_id,
                "stage": stage,
                "reason_code": reason_code,
                "details": details
            },
            exc_info=original_exception
        )
        
        super().__init__(message_ko)
    
    def to_dict(self) -> Dict[str, Any]:
        """API 응답용 딕셔너리"""
        return {
            "ok": False,
            "stage": self.stage,
            "reason_code": self.reason_code,
            "message_ko": self.message_ko,
            "debug_id": self.debug_id,
            "details": self.details
        }


class PipelineTracer:
    """
    파이프라인 실행 추적기
    
    Usage:
        tracer = PipelineTracer()
        
        try:
            tracer.set_stage(PipelineStage.M1_INPUT)
            # ... M1 로직
            
            tracer.set_stage(PipelineStage.M2)
            # ... M2 로직
            
        except Exception as e:
            raise tracer.wrap(e, ReasonCode.EXTERNAL_API_TIMEOUT)
    """
    
    def __init__(self, parcel_id: Optional[str] = None):
        """
        Args:
            parcel_id: 토지 ID (선택)
        """
        self.trace_id = self._generate_trace_id()
        self.parcel_id = parcel_id
        self.current_stage = PipelineStage.INIT
        self.start_time = datetime.now()
        self.stage_history: List[Dict[str, Any]] = []
        
        logger.info(
            f"[{self.trace_id}] Pipeline started",
            extra={"trace_id": self.trace_id, "parcel_id": parcel_id}
        )
    
    def _generate_trace_id(self) -> str:
        """trace_id 생성: pl_YYYYMMDD_xxxxxxxx"""
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = uuid.uuid4().hex[:8]
        return f"pl_{date_str}_{random_str}"
    
    def set_stage(self, stage: PipelineStage):
        """
        현재 실행 단계 설정
        
        Args:
            stage: 파이프라인 단계
        """
        self.current_stage = stage
        self.stage_history.append({
            "stage": stage,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(
            f"[{self.trace_id}] Stage: {stage}",
            extra={"trace_id": self.trace_id, "stage": stage}
        )
    
    def wrap(
        self,
        exception: Exception,
        reason_code: ReasonCode,
        message_ko: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> PipelineExecutionError:
        """
        예외를 PipelineExecutionError로 감싸기
        
        Args:
            exception: 원본 예외
            reason_code: 실패 원인 코드
            message_ko: 사용자 메시지 (없으면 자동 생성)
            details: 추가 상세 정보
        
        Returns:
            PipelineExecutionError
        """
        # 메시지 자동 생성
        if not message_ko:
            message_ko = self._generate_user_message(reason_code)
        
        # 상세 정보 보강
        if details is None:
            details = {}
        
        details["original_error"] = str(exception)
        details["stage_history"] = self.stage_history
        
        return PipelineExecutionError(
            stage=self.current_stage,
            reason_code=reason_code,
            debug_id=self.trace_id,
            message_ko=message_ko,
            details=details,
            original_exception=exception
        )
    
    def _generate_user_message(self, reason_code: ReasonCode) -> str:
        """
        reason_code에 따른 한국어 사용자 메시지 생성
        
        Args:
            reason_code: 실패 원인 코드
        
        Returns:
            한국어 메시지
        """
        stage_ko = self._get_stage_korean(self.current_stage)
        
        messages = {
            ReasonCode.ADDRESS_NOT_FOUND: f"{stage_ko} 단계에서 입력하신 주소를 찾을 수 없습니다. 지번 또는 도로명 주소를 다시 확인해 주세요.",
            ReasonCode.ADDRESS_NORMALIZE_FAILED: f"{stage_ko} 단계에서 주소 정규화에 실패했습니다. 주소 형식을 확인해 주세요.",
            ReasonCode.PNU_CONVERSION_FAILED: f"{stage_ko} 단계에서 주소를 PNU(필지번호)로 변환할 수 없습니다.",
            
            ReasonCode.API_KEY_MISSING: f"{stage_ko} 단계에서 필요한 API 키가 설정되지 않았습니다. 관리자에게 문의하세요.",
            ReasonCode.API_KEY_INVALID: f"{stage_ko} 단계에서 API 키가 유효하지 않습니다. 관리자에게 문의하세요.",
            ReasonCode.EXTERNAL_API_TIMEOUT: f"{stage_ko} 단계에서 외부 API 응답이 지연되어 분석이 중단되었습니다. 잠시 후 다시 시도해 주세요.",
            ReasonCode.EXTERNAL_API_ERROR: f"{stage_ko} 단계에서 외부 API 호출 중 오류가 발생했습니다.",
            
            ReasonCode.DATA_BINDING_MISSING: f"{stage_ko} 단계에서 필수 데이터가 누락되었습니다. 이전 단계의 데이터를 확인해 주세요.",
            ReasonCode.MODULE_DATA_MISSING: f"{stage_ko} 단계의 분석 결과 데이터가 생성되지 않았습니다.",
            ReasonCode.VALIDATION_FAILED: f"{stage_ko} 단계에서 데이터 검증에 실패했습니다.",
            
            ReasonCode.STORAGE_ERROR: f"{stage_ko} 단계에서 데이터 저장 중 오류가 발생했습니다.",
            ReasonCode.UNKNOWN: f"{stage_ko} 단계에서 알 수 없는 오류가 발생했습니다. 관리자에게 문의하세요."
        }
        
        return messages.get(reason_code, f"{stage_ko} 단계에서 오류가 발생했습니다.")
    
    def _get_stage_korean(self, stage: PipelineStage) -> str:
        """단계명 한국어 변환"""
        stage_names = {
            PipelineStage.INIT: "초기화",
            PipelineStage.M1_INPUT: "M1 입력",
            PipelineStage.M1_NORMALIZE: "M1 주소 정규화",
            PipelineStage.M1_FREEZE: "M1 확정",
            PipelineStage.M2: "M2 토지감정평가",
            PipelineStage.M3: "M3 LH 선호유형",
            PipelineStage.M4: "M4 건축규모",
            PipelineStage.M5: "M5 사업성 분석",
            PipelineStage.M6: "M6 LH 심사예측",
            PipelineStage.ASSEMBLE: "데이터 조립",
            PipelineStage.VALIDATE: "데이터 검증",
            PipelineStage.SAVE: "저장",
            PipelineStage.COMPLETE: "완료"
        }
        return stage_names.get(stage, str(stage))
    
    def complete(self):
        """파이프라인 완료"""
        self.set_stage(PipelineStage.COMPLETE)
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info(
            f"[{self.trace_id}] Pipeline completed in {elapsed:.2f}s",
            extra={
                "trace_id": self.trace_id,
                "elapsed_sec": elapsed,
                "stages": len(self.stage_history)
            }
        )
