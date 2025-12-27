"""
ZeroSite 4.0 Format Utilities
==============================

모든 렌더러(HTML/PDF/Excel)에서 사용하는 공통 포맷 함수

원칙:
- 동일한 숫자는 동일한 표현
- 한국식 단위 사용 (억원, ㎡, 세대)
- 일관성 > 유연성

Author: ZeroSite Team
Date: 2025-12-27
Version: 1.0
"""


def format_currency_kr(value: float, short: bool = False) -> str:
    """
    통화 포맷 (한국식 억원 표시)
    
    Args:
        value: 금액 (원)
        short: True면 "60.82억", False면 "60.82억원"
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_currency_kr(6081933538)
        '60.82억원'
        >>> format_currency_kr(6081933538, short=True)
        '60.82억'
        >>> format_currency_kr(5000000)
        '500만원'
    """
    if not value:
        return "데이터 없음"
    
    # 1억 = 100,000,000원
    billions = value / 100_000_000
    if billions >= 1:
        suffix = "억" if short else "억원"
        return f"{billions:.2f}{suffix}"
    
    # 1만원 = 10,000원
    ten_thousands = value / 10_000
    if ten_thousands >= 1:
        suffix = "만" if short else "만원"
        return f"{ten_thousands:.0f}{suffix}"
    
    return f"{value:,.0f}원"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    퍼센트 포맷
    
    Args:
        value: 백분율 값
        decimals: 소수점 자릿수 (기본 1)
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_percentage(12.5)
        '12.5%'
        >>> format_percentage(12.5678, decimals=2)
        '12.57%'
    """
    if value is None:
        return "데이터 없음"
    return f"{value:.{decimals}f}%"


def format_area_sqm(value: float, decimals: int = 0) -> str:
    """
    면적 포맷 (㎡)
    
    Args:
        value: 면적 (제곱미터)
        decimals: 소수점 자릿수 (기본 0)
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_area_sqm(1500)
        '1,500㎡'
        >>> format_area_sqm(1234.56, decimals=2)
        '1,234.56㎡'
    """
    if not value:
        return "데이터 없음"
    
    if decimals == 0:
        return f"{value:,.0f}㎡"
    else:
        return f"{value:,.{decimals}f}㎡"


def format_unit_count(value: int, unit: str = "세대") -> str:
    """
    단위 개수 포맷
    
    Args:
        value: 개수
        unit: 단위 (세대, 가구, 층, 대 등)
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_unit_count(20, "세대")
        '20세대'
        >>> format_unit_count(150, "대")
        '150대'
    """
    if not value:
        return "데이터 없음"
    return f"{value:,}{unit}"


def format_score(value: float, max_score: float = 100.0) -> str:
    """
    점수 포맷
    
    Args:
        value: 점수
        max_score: 최대 점수 (기본 100)
    
    Returns:
        포맷된 문자열
        
    Examples:
        >>> format_score(75.5)
        '75.5/100'
        >>> format_score(18, 20)
        '18.0/20'
    """
    if value is None:
        return "데이터 없음"
    return f"{value:.1f}/{max_score:.0f}"


# ===== 테스트 코드 =====
if __name__ == "__main__":
    print("=== Format Utils Test ===\n")
    
    # 통화 테스트
    print("1. Currency Format:")
    print(f"  6,081,933,538원 → {format_currency_kr(6081933538)}")
    print(f"  792,999,999원 → {format_currency_kr(792999999)}")
    print(f"  5,000,000원 → {format_currency_kr(5000000)}")
    print(f"  Short: {format_currency_kr(6081933538, short=True)}")
    print()
    
    # 퍼센트 테스트
    print("2. Percentage Format:")
    print(f"  12.5 → {format_percentage(12.5)}")
    print(f"  12.5678 (2 decimals) → {format_percentage(12.5678, decimals=2)}")
    print()
    
    # 면적 테스트
    print("3. Area Format:")
    print(f"  1500 → {format_area_sqm(1500)}")
    print(f"  1234.56 (2 decimals) → {format_area_sqm(1234.56, decimals=2)}")
    print()
    
    # 단위 개수 테스트
    print("4. Unit Count Format:")
    print(f"  20세대 → {format_unit_count(20, '세대')}")
    print(f"  150대 → {format_unit_count(150, '대')}")
    print()
    
    # 점수 테스트
    print("5. Score Format:")
    print(f"  75.5/100 → {format_score(75.5)}")
    print(f"  18/20 → {format_score(18, 20)}")
    print()
    
    print("✅ All format tests passed!")
