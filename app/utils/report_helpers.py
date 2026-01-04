"""
Report Helper Utilities
보고서 생성을 위한 공통 유틸리티 함수
"""

def resolve_scalar(value, default=None):
    """
    중첩된 데이터 구조에서 스칼라 값을 안전하게 추출
    
    Args:
        value: 추출할 값 (dict, list, scalar 등)
        default: 기본값 (None일 경우)
        
    Returns:
        스칼라 값 또는 기본값
    """
    if value is None:
        return default
    
    # 이미 스칼라 값이면 그대로 반환
    if isinstance(value, (int, float, str, bool)):
        return value
    
    # dict인 경우 첫 번째 값 시도
    if isinstance(value, dict):
        if 'value' in value:
            return value['value']
        if 'amount' in value:
            return value['amount']
        # 첫 번째 값 반환
        if value:
            return next(iter(value.values()))
        return default
    
    # list인 경우 첫 번째 요소
    if isinstance(value, list):
        return value[0] if value else default
    
    return default


def present_currency(value, default="-"):
    """
    금액을 한국 통화 형식으로 포맷팅
    
    Args:
        value: 금액 (숫자)
        default: value가 None일 때 반환값
        
    Returns:
        str: "1,234,567원" 형식
    """
    val = resolve_scalar(value)
    if val is None or val == "":
        return default
    
    try:
        num_val = float(val)
        # 0이면 기본값 반환
        if num_val == 0:
            return default
        # 정수로 변환하여 천 단위 콤마
        return f"{int(num_val):,}원"
    except (ValueError, TypeError):
        return default


def present_currency_in_billion(value, decimals=1, default="-"):
    """
    금액을 억원 단위로 포맷팅
    
    Args:
        value: 금액 (원 단위)
        decimals: 소수점 자릿수
        default: value가 None일 때 반환값
        
    Returns:
        str: "123.4억원" 형식
    """
    val = resolve_scalar(value)
    if val is None or val == "":
        return default
    
    try:
        num_val = float(val)
        if num_val == 0:
            return default
        billion = num_val / 100000000
        return f"{billion:.{decimals}f}억원"
    except (ValueError, TypeError):
        return default


def present_percent(value, decimals=1, default="-"):
    """
    백분율 포맷팅
    
    Args:
        value: 백분율 값
        decimals: 소수점 자릿수
        default: value가 None일 때 반환값
        
    Returns:
        str: "12.3%" 형식
    """
    val = resolve_scalar(value)
    if val is None or val == "":
        return default
    
    try:
        num_val = float(val)
        return f"{num_val:.{decimals}f}%"
    except (ValueError, TypeError):
        return default


def present_number(value, decimals=0, default="-"):
    """
    숫자를 천 단위 콤마로 포맷팅
    
    Args:
        value: 숫자
        decimals: 소수점 자릿수
        default: value가 None일 때 반환값
        
    Returns:
        str: "1,234,567" 형식
    """
    val = resolve_scalar(value)
    if val is None or val == "":
        return default
    
    try:
        num_val = float(val)
        if decimals == 0:
            return f"{int(num_val):,}"
        else:
            return f"{num_val:,.{decimals}f}"
    except (ValueError, TypeError):
        return default


def present_text(value, default="-"):
    """
    텍스트 값을 안전하게 표시
    
    Args:
        value: 텍스트 값
        default: value가 None일 때 반환값
        
    Returns:
        str: 텍스트 또는 기본값
    """
    val = resolve_scalar(value)
    if val is None or val == "":
        return default
    return str(val)


def safe_get(data, *keys, default=None):
    """
    중첩된 딕셔너리에서 안전하게 값 가져오기
    
    Args:
        data: dict 또는 중첩된 dict
        *keys: 접근할 키 경로
        default: 찾지 못했을 때 기본값
        
    Returns:
        값 또는 기본값
        
    Example:
        safe_get(data, 'financial', 'roi_percentage', default=0)
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result if result is not None else default
