"""
한국어 에러 메시지 표준
======================

ZeroSite v11.0 - 사용자 친화적인 에러 메시지

Date: 2025-12-27
"""

from typing import Dict, Any
from enum import Enum


class ErrorCode(str, Enum):
    """표준 에러 코드"""
    
    # 일반 에러 (1xxx)
    UNKNOWN_ERROR = "E1000"
    VALIDATION_ERROR = "E1001"
    PERMISSION_DENIED = "E1002"
    NOT_FOUND = "E1003"
    ALREADY_EXISTS = "E1004"
    
    # 데이터 관련 (2xxx)
    INVALID_DATA = "E2000"
    MISSING_REQUIRED_FIELD = "E2001"
    DATA_TOO_LARGE = "E2002"
    DATA_FORMAT_ERROR = "E2003"
    
    # 파이프라인 관련 (3xxx)
    PIPELINE_TIMEOUT = "E3000"
    PIPELINE_EXECUTION_ERROR = "E3001"
    MODULE_DATA_MISSING = "E3002"
    CONTEXT_NOT_FOUND = "E3003"
    CONTEXT_EXPIRED = "E3004"
    
    # 외부 API 관련 (4xxx)
    EXTERNAL_API_TIMEOUT = "E4000"
    EXTERNAL_API_ERROR = "E4001"
    ADDRESS_NOT_FOUND = "E4002"
    PARCEL_DATA_UNAVAILABLE = "E4003"
    
    # PDF 생성 관련 (5xxx)
    PDF_GENERATION_ERROR = "E5000"
    PDF_DATA_MISSING = "E5001"
    PDF_TEMPLATE_ERROR = "E5002"
    
    # 데이터베이스 관련 (6xxx)
    DATABASE_ERROR = "E6000"
    DATABASE_CONNECTION_ERROR = "E6001"
    DATABASE_QUERY_ERROR = "E6002"
    
    # 저장소 관련 (7xxx)
    STORAGE_ERROR = "E7000"
    REDIS_ERROR = "E7001"
    FILE_SYSTEM_ERROR = "E7002"


class ErrorMessages:
    """한국어 에러 메시지"""
    
    # 사용자 친화적인 메시지
    USER_MESSAGES = {
        ErrorCode.UNKNOWN_ERROR: "알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ErrorCode.VALIDATION_ERROR: "입력하신 정보를 확인해주세요.",
        ErrorCode.PERMISSION_DENIED: "접근 권한이 없습니다.",
        ErrorCode.NOT_FOUND: "요청하신 정보를 찾을 수 없습니다.",
        ErrorCode.ALREADY_EXISTS: "이미 존재하는 데이터입니다.",
        
        ErrorCode.INVALID_DATA: "입력 데이터가 올바르지 않습니다.",
        ErrorCode.MISSING_REQUIRED_FIELD: "필수 입력 항목이 누락되었습니다.",
        ErrorCode.DATA_TOO_LARGE: "데이터 크기가 너무 큽니다.",
        ErrorCode.DATA_FORMAT_ERROR: "데이터 형식이 올바르지 않습니다.",
        
        ErrorCode.PIPELINE_TIMEOUT: "분석 처리 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.",
        ErrorCode.PIPELINE_EXECUTION_ERROR: "분석 중 오류가 발생했습니다.",
        ErrorCode.MODULE_DATA_MISSING: "필요한 분석 데이터가 누락되었습니다.",
        ErrorCode.CONTEXT_NOT_FOUND: "분석 결과를 찾을 수 없습니다. 분석을 다시 실행해주세요.",
        ErrorCode.CONTEXT_EXPIRED: "분석 결과가 만료되었습니다. 분석을 다시 실행해주세요.",
        
        ErrorCode.EXTERNAL_API_TIMEOUT: "외부 데이터 조회 중 시간이 초과되었습니다.",
        ErrorCode.EXTERNAL_API_ERROR: "외부 데이터 조회 중 오류가 발생했습니다.",
        ErrorCode.ADDRESS_NOT_FOUND: "입력하신 주소를 찾을 수 없습니다. 주소를 확인해주세요.",
        ErrorCode.PARCEL_DATA_UNAVAILABLE: "토지 정보를 조회할 수 없습니다.",
        
        ErrorCode.PDF_GENERATION_ERROR: "PDF 생성 중 오류가 발생했습니다.",
        ErrorCode.PDF_DATA_MISSING: "PDF 생성에 필요한 데이터가 없습니다.",
        ErrorCode.PDF_TEMPLATE_ERROR: "PDF 템플릿 오류가 발생했습니다.",
        
        ErrorCode.DATABASE_ERROR: "데이터베이스 오류가 발생했습니다.",
        ErrorCode.DATABASE_CONNECTION_ERROR: "데이터베이스 연결에 실패했습니다.",
        ErrorCode.DATABASE_QUERY_ERROR: "데이터 조회 중 오류가 발생했습니다.",
        
        ErrorCode.STORAGE_ERROR: "데이터 저장 중 오류가 발생했습니다.",
        ErrorCode.REDIS_ERROR: "캐시 서버 오류가 발생했습니다.",
        ErrorCode.FILE_SYSTEM_ERROR: "파일 시스템 오류가 발생했습니다.",
    }
    
    # 개발자용 상세 메시지
    DEVELOPER_MESSAGES = {
        ErrorCode.UNKNOWN_ERROR: "Unexpected error occurred",
        ErrorCode.VALIDATION_ERROR: "Validation failed",
        ErrorCode.PERMISSION_DENIED: "Permission denied",
        ErrorCode.NOT_FOUND: "Resource not found",
        ErrorCode.ALREADY_EXISTS: "Resource already exists",
        
        ErrorCode.INVALID_DATA: "Invalid data provided",
        ErrorCode.MISSING_REQUIRED_FIELD: "Required field missing",
        ErrorCode.DATA_TOO_LARGE: "Data size exceeds limit",
        ErrorCode.DATA_FORMAT_ERROR: "Data format is incorrect",
        
        ErrorCode.PIPELINE_TIMEOUT: "Pipeline execution timeout",
        ErrorCode.PIPELINE_EXECUTION_ERROR: "Pipeline execution failed",
        ErrorCode.MODULE_DATA_MISSING: "Required module data missing",
        ErrorCode.CONTEXT_NOT_FOUND: "Context not found in storage",
        ErrorCode.CONTEXT_EXPIRED: "Context has expired",
        
        ErrorCode.EXTERNAL_API_TIMEOUT: "External API call timeout",
        ErrorCode.EXTERNAL_API_ERROR: "External API call failed",
        ErrorCode.ADDRESS_NOT_FOUND: "Address not found in geocoding service",
        ErrorCode.PARCEL_DATA_UNAVAILABLE: "Parcel data unavailable from source",
        
        ErrorCode.PDF_GENERATION_ERROR: "PDF generation failed",
        ErrorCode.PDF_DATA_MISSING: "Required PDF data missing",
        ErrorCode.PDF_TEMPLATE_ERROR: "PDF template error",
        
        ErrorCode.DATABASE_ERROR: "Database operation failed",
        ErrorCode.DATABASE_CONNECTION_ERROR: "Database connection failed",
        ErrorCode.DATABASE_QUERY_ERROR: "Database query failed",
        
        ErrorCode.STORAGE_ERROR: "Storage operation failed",
        ErrorCode.REDIS_ERROR: "Redis operation failed",
        ErrorCode.FILE_SYSTEM_ERROR: "File system operation failed",
    }
    
    # 사용자 액션 제안
    ACTION_SUGGESTIONS = {
        ErrorCode.UNKNOWN_ERROR: "잠시 후 다시 시도하거나 관리자에게 문의하세요.",
        ErrorCode.VALIDATION_ERROR: "입력 값을 확인하고 다시 시도하세요.",
        ErrorCode.PERMISSION_DENIED: "접근 권한이 필요합니다. 관리자에게 문의하세요.",
        ErrorCode.NOT_FOUND: "URL을 확인하거나 처음부터 다시 시작하세요.",
        
        ErrorCode.PIPELINE_TIMEOUT: "네트워크 연결을 확인하고 다시 시도하세요.",
        ErrorCode.CONTEXT_NOT_FOUND: "'분석 시작' 버튼을 눌러 새로 분석해주세요.",
        ErrorCode.CONTEXT_EXPIRED: "24시간이 경과했습니다. 다시 분석해주세요.",
        
        ErrorCode.ADDRESS_NOT_FOUND: "도로명 주소 또는 지번 주소로 다시 검색하세요.",
        ErrorCode.PARCEL_DATA_UNAVAILABLE: "주소를 확인하거나 다른 필지를 선택하세요.",
        
        ErrorCode.PDF_GENERATION_ERROR: "관리자에게 문의하세요. (오류 ID 포함)",
        ErrorCode.PDF_DATA_MISSING: "M2-M6 모듈을 먼저 실행해주세요.",
    }
    
    @classmethod
    def get_message(cls, error_code: ErrorCode, lang: str = "ko") -> str:
        """
        에러 메시지 가져오기
        
        Args:
            error_code: 에러 코드
            lang: 언어 ('ko' 또는 'en')
        
        Returns:
            에러 메시지
        """
        if lang == "ko":
            return cls.USER_MESSAGES.get(error_code, cls.USER_MESSAGES[ErrorCode.UNKNOWN_ERROR])
        else:
            return cls.DEVELOPER_MESSAGES.get(error_code, cls.DEVELOPER_MESSAGES[ErrorCode.UNKNOWN_ERROR])
    
    @classmethod
    def get_action(cls, error_code: ErrorCode) -> str:
        """
        사용자 액션 제안 가져오기
        
        Args:
            error_code: 에러 코드
        
        Returns:
            액션 제안
        """
        return cls.ACTION_SUGGESTIONS.get(error_code, "관리자에게 문의하세요.")
    
    @classmethod
    def format_error_response(
        cls,
        error_code: ErrorCode,
        detail: str = None,
        debug_id: str = None,
        lang: str = "ko"
    ) -> Dict[str, Any]:
        """
        표준 에러 응답 포맷
        
        Args:
            error_code: 에러 코드
            detail: 상세 설명 (선택)
            debug_id: 디버그 ID (선택)
            lang: 언어
        
        Returns:
            표준 에러 응답 딕셔너리
        """
        response = {
            "ok": False,
            "error_code": error_code.value,
            "message": cls.get_message(error_code, lang),
            "action": cls.get_action(error_code),
        }
        
        if detail:
            response["detail"] = detail
        
        if debug_id:
            response["debug_id"] = debug_id
        
        return response


# 편의 함수
def error_response(
    error_code: ErrorCode,
    detail: str = None,
    debug_id: str = None,
    lang: str = "ko"
) -> Dict[str, Any]:
    """
    표준 에러 응답 생성
    
    Args:
        error_code: 에러 코드
        detail: 상세 설명
        debug_id: 디버그 ID
        lang: 언어
    
    Returns:
        에러 응답 딕셔너리
    """
    return ErrorMessages.format_error_response(error_code, detail, debug_id, lang)


# 사용 예제
if __name__ == "__main__":
    # 예제 1: 간단한 에러
    print("=" * 60)
    print("예제 1: Context 없음 에러")
    print("=" * 60)
    error = error_response(
        ErrorCode.CONTEXT_NOT_FOUND,
        debug_id="ctx_123456"
    )
    import json
    print(json.dumps(error, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("예제 2: PDF 생성 에러")
    print("=" * 60)
    error = error_response(
        ErrorCode.PDF_GENERATION_ERROR,
        detail="M4 모듈 데이터 누락",
        debug_id="pdf_789012"
    )
    print(json.dumps(error, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("예제 3: 주소 없음 에러")
    print("=" * 60)
    error = error_response(
        ErrorCode.ADDRESS_NOT_FOUND,
        detail="입력 주소: 서울시 강남구 역삼동 123-456"
    )
    print(json.dumps(error, ensure_ascii=False, indent=2))
