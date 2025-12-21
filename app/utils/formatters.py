"""
ZeroSite 보고서 포맷터 유틸리티

PDF와 HTML에서 동일한 포맷팅 규칙을 적용하기 위한 공통 유틸리티.
숫자, 통화, 퍼센트, None 값 등을 일관되게 처리합니다.

Author: ZeroSite Refactoring Team
Date: 2025-12-20
"""

from typing import Optional, Union


def format_krw(value: Optional[Union[int, float]], show_unit: bool = True, precision: int = 0) -> str:
    """
    한국 원화(KRW) 포맷팅
    
    Args:
        value: 숫자 값
        show_unit: ₩ 기호 표시 여부
        precision: 소수점 자리수 (기본값: 0)
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_krw(792999999)
        '₩792,999,999'
        >>> format_krw(792999999, show_unit=False)
        '792,999,999'
        >>> format_krw(None)
        'N/A'
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        if precision > 0:
            formatted = f"{value:,.{precision}f}"
        else:
            formatted = f"{int(value):,}"
        
        if show_unit:
            return f"₩{formatted}"
        return formatted
    except (ValueError, TypeError):
        return "N/A"


def format_percent(value: Optional[Union[int, float]], precision: int = 2, multiply_by_100: bool = False) -> str:
    """
    퍼센트 포맷팅
    
    Args:
        value: 숫자 값
        precision: 소수점 자리수 (기본값: 2)
        multiply_by_100: True면 0-1 범위 값을 0-100으로 변환 (기본값: False)
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_percent(7.145993802547898)
        '7.15%'
        >>> format_percent(0.0715, multiply_by_100=True)
        '7.15%'
        >>> format_percent(None)
        'N/A'
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        if multiply_by_100:
            value = value * 100
        
        return f"{value:.{precision}f}%"
    except (ValueError, TypeError):
        return "N/A"


def format_number(value: Optional[Union[int, float]], precision: int = 0, unit: str = "", 
                  show_defensive_text: bool = False) -> str:
    """
    일반 숫자 포맷팅 (데이터 방어 강화)
    
    Args:
        value: 숫자 값
        precision: 소수점 자리수 (기본값: 0)
        unit: 단위 (예: '세대', '대', 'm²') - ⚠️ 단위 누락 방지 필수
        show_defensive_text: True면 N/A 시 방어 문구 추가
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_number(26, unit='세대')
        '26세대'
        >>> format_number(85.5, precision=1)
        '85.5'
        >>> format_number(None)
        'N/A'
    """
    if value is None:
        return "N/A"
    
    try:
        value = float(value)
        if precision > 0:
            formatted = f"{value:,.{precision}f}"
        else:
            formatted = f"{int(value):,}"
        
        if unit:
            return f"{formatted}{unit}"
        return formatted
    except (ValueError, TypeError):
        return "N/A"


def format_range(min_val: Optional[Union[int, float]], 
                 max_val: Optional[Union[int, float]], 
                 formatter: callable = None,
                 separator: str = " ~ ") -> str:
    """
    범위 값 포맷팅
    
    Args:
        min_val: 최소값
        max_val: 최대값
        formatter: 개별 값 포맷 함수 (None이면 기본 숫자 포맷)
        separator: 구분자 (기본값: ' ~ ')
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_range(100000000, 120000000, formatter=format_krw)
        '₩100,000,000 ~ ₩120,000,000'
        >>> format_range(None, None)
        'N/A'
    """
    if min_val is None and max_val is None:
        return "N/A"
    
    if min_val is None:
        return formatter(max_val) if formatter else format_number(max_val)
    
    if max_val is None:
        return formatter(min_val) if formatter else format_number(min_val)
    
    if formatter:
        return f"{formatter(min_val)}{separator}{formatter(max_val)}"
    else:
        return f"{format_number(min_val)}{separator}{format_number(max_val)}"


def safe_get(data: dict, *keys, default: str = "N/A") -> str:
    """
    안전한 딕셔너리 값 추출 (중첩된 키 지원)
    
    Args:
        data: 딕셔너리
        *keys: 추출할 키들 (중첩 가능)
        default: 기본값
    
    Returns:
        추출된 값 또는 기본값
        
    Examples:
        >>> data = {'summary': {'total_score': 85}}
        >>> safe_get(data, 'summary', 'total_score', default='N/A')
        '85'
        >>> safe_get(data, 'summary', 'missing', default='N/A')
        'N/A'
    """
    try:
        result = data
        for key in keys:
            if result is None:
                return default
            result = result.get(key) if isinstance(result, dict) else None
        
        if result is None:
            return default
        
        return str(result)
    except (AttributeError, TypeError, KeyError):
        return default


def format_m2_summary(summary: dict) -> dict:
    """
    M2 (토지감정평가) summary 전용 포맷터
    
    Args:
        summary: M2 summary 데이터
    
    Returns:
        포맷된 summary 딕셔너리 + 해석 문장 (통일된 한국어 문체)
    """
    # 기본 KPI 포맷팅
    land_value = summary.get('land_value_total_krw')
    pyeong_price = summary.get('pyeong_price_krw')
    confidence = summary.get('confidence_pct')
    transaction_count = summary.get('transaction_count', 0)
    
    formatted = {
        'land_value_total': format_krw(land_value),
        'pyeong_price': format_krw(pyeong_price),
        'confidence_pct': format_percent(confidence),
        'transaction_count': format_number(transaction_count, unit='건')
    }
    
    # 해석 문장 (한국어 문체 통일: ~입니다)
    if land_value is not None and confidence is not None:
        formatted['interpretation'] = (
            "본 감정가는 최근 실거래·입지·용도지역을 종합 반영한 추정 범위입니다. "
            "신뢰도는 비교 사례 수와 데이터 최신성을 기준으로 산정되었습니다."
        )
    else:
        # 데이터 미유입 방어 문구
        formatted['interpretation'] = (
            "※ 본 항목은 현재 기준에서 충분한 데이터가 확보되지 않아 참고용으로만 제공됩니다. "
            "추가 데이터 확보 시 결과가 변경될 수 있습니다."
        )
    
    return formatted


def format_m3_summary(summary: dict) -> dict:
    """
    M3 (LH 선호유형) summary 전용 포맷터
    
    Args:
        summary: M3 summary 데이터
    
    Returns:
        포맷된 summary 딕셔너리
    """
    return {
        'recommended_type': summary.get('recommended_type') or 'N/A',
        'total_score': format_number(summary.get('total_score'), unit='점'),
        'confidence_pct': format_percent(summary.get('confidence_pct')),
        'second_choice': summary.get('second_choice') or 'N/A'
    }


def format_m4_summary(summary: dict) -> dict:
    """
    M4 (건축규모) summary 전용 포맷터
    
    Args:
        summary: M4 summary 데이터
    
    Returns:
        포맷된 summary 딕셔너리
    """
    return {
        'legal_units': format_number(summary.get('legal_units'), unit='세대'),
        'incentive_units': format_number(summary.get('incentive_units'), unit='세대'),
        'parking_alt_a': format_number(summary.get('parking_alt_a'), unit='대'),
        'parking_alt_b': format_number(summary.get('parking_alt_b'), unit='대')
    }


def format_m5_summary(summary: dict) -> dict:
    """
    M5 (사업성) summary 전용 포맷터
    
    Args:
        summary: M5 summary 데이터
    
    Returns:
        포맷된 summary 딕셔너리 + 판단 가이드 문장 (통일된 한국어 문체)
    """
    npv = summary.get('npv_public_krw', 0)
    irr = summary.get('irr_pct', 0)
    
    # 기본 KPI 포맷팅
    formatted = {
        'npv_public_krw': format_krw(npv),
        'irr_pct': format_percent(irr),
        'roi_pct': format_percent(summary.get('roi_pct')),
        'grade': summary.get('grade') or 'N/A'
    }
    
    # 판단 가이드 문장 (한국어 문체 통일: ~입니다, ~로 판단됩니다)
    if npv is not None and irr is not None:
        if irr >= 7:
            guide = "본 분석 결과 LH 매입 기준 대비 수익성은 양호한 수준입니다."
        elif irr >= 5:
            guide = "본 분석 결과 LH 매입 기준 대비 수익성은 보수적 수준입니다."
        else:
            guide = "본 분석 결과 민간 기준에서는 제한적 수익 구조로 판단됩니다."
    else:
        # 데이터 미유입 방어 문구
        guide = "※ 본 항목은 현재 기준에서 충분한 데이터가 확보되지 않아 참고용으로만 제공됩니다."
    
    formatted['judgment_guide'] = guide
    
    return formatted


def format_m6_summary(summary: dict) -> dict:
    """
    M6 (LH 심사예측) summary 전용 포맷터
    
    Args:
        summary: M6 summary 데이터
    
    Returns:
        포맷된 summary 딕셔너리
    """
    return {
        'decision': summary.get('decision') or 'N/A',
        'total_score': f"{format_number(summary.get('total_score'))}/{format_number(summary.get('max_score', 110))}점",
        'grade': summary.get('grade') or 'N/A',
        'approval_probability_pct': format_percent(summary.get('approval_probability_pct'))
    }
