"""
AI Auto Corrector - ZeroSite Land Report v5.0
자동으로 입력 데이터를 검증하고 교정하는 서비스
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel


class CorrectedInput(BaseModel):
    """교정된 입력 데이터"""
    original_address: str
    corrected_address: Optional[str] = None
    address_confidence: float = 1.0
    
    original_land_area: float
    corrected_land_area: Optional[float] = None
    area_confidence: float = 1.0
    
    corrections_made: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []


class AIAutoCorrector:
    """AI 기반 자동 입력 교정기"""
    
    def __init__(self):
        """초기화"""
        self.address_patterns = {
            "번지_누락": r"\d+-$",  # 123- 형식 (뒤 번지 누락)
            "괄호_오류": r"\([^)]*$",  # 괄호가 닫히지 않음
            "중복_공백": r"\s{2,}",  # 연속 공백
        }
        
        self.area_thresholds = {
            "min_reasonable": 100,  # 최소 합리적 면적 (㎡)
            "max_reasonable": 10000,  # 최대 합리적 면적 (㎡)
            "typical_min": 300,  # 일반적 최소 면적
            "typical_max": 3000,  # 일반적 최대 면적
        }
    
    def correct_input(
        self, 
        address: str, 
        land_area: float,
        zone_type: Optional[str] = None
    ) -> CorrectedInput:
        """
        입력 데이터를 자동 교정
        
        Args:
            address: 입력 주소
            land_area: 입력 면적
            zone_type: 용도지역 (선택)
            
        Returns:
            CorrectedInput: 교정된 입력 데이터
        """
        result = CorrectedInput(
            original_address=address,
            original_land_area=land_area
        )
        
        # 1. 주소 교정
        corrected_addr, addr_corrections = self._correct_address(address)
        if corrected_addr != address:
            result.corrected_address = corrected_addr
            result.address_confidence = 0.85
            result.corrections_made.extend(addr_corrections)
        
        # 2. 면적 교정
        corrected_area, area_corrections, area_warnings = self._correct_land_area(
            land_area, zone_type
        )
        if corrected_area != land_area:
            result.corrected_land_area = corrected_area
            result.area_confidence = 0.9
            result.corrections_made.extend(area_corrections)
        
        result.warnings.extend(area_warnings)
        
        # 3. 제안사항 생성
        result.suggestions = self._generate_suggestions(
            address, land_area, zone_type, result
        )
        
        return result
    
    def _correct_address(self, address: str) -> tuple[str, List[str]]:
        """주소 자동 교정"""
        corrections = []
        corrected = address
        
        # 연속 공백 제거
        import re
        if re.search(r"\s{2,}", corrected):
            corrected = re.sub(r"\s{2,}", " ", corrected)
            corrections.append("연속 공백을 단일 공백으로 교정")
        
        # 앞뒤 공백 제거
        if corrected != corrected.strip():
            corrected = corrected.strip()
            corrections.append("앞뒤 공백 제거")
        
        # 특수문자 정리 (괄호 등)
        if "(" in corrected and ")" not in corrected:
            corrected = corrected.replace("(", "")
            corrections.append("닫히지 않은 괄호 제거")
        
        return corrected, corrections
    
    def _correct_land_area(
        self, 
        land_area: float, 
        zone_type: Optional[str]
    ) -> tuple[float, List[str], List[str]]:
        """면적 자동 교정"""
        corrections = []
        warnings = []
        corrected_area = land_area
        
        # 면적 범위 검증
        if land_area < self.area_thresholds["min_reasonable"]:
            warnings.append(f"면적이 매우 작습니다 ({land_area}㎡). 입력값을 확인하세요.")
        elif land_area > self.area_thresholds["max_reasonable"]:
            warnings.append(f"면적이 매우 큽니다 ({land_area}㎡). 입력값을 확인하세요.")
        
        # 일반적 범위 제안
        if land_area < self.area_thresholds["typical_min"]:
            warnings.append(
                f"LH 신축매입임대 사업에는 일반적으로 {self.area_thresholds['typical_min']}㎡ 이상이 권장됩니다."
            )
        elif land_area > self.area_thresholds["typical_max"]:
            warnings.append(
                f"면적이 큰 경우 다필지 분할 분석을 권장합니다."
            )
        
        # 소수점 정리 (예: 500.0000001 -> 500.0)
        rounded = round(land_area, 2)
        if abs(rounded - land_area) > 0.001:
            corrected_area = rounded
            corrections.append(f"소수점 자리 정리 ({land_area:.6f} → {rounded})")
        
        return corrected_area, corrections, warnings
    
    def _generate_suggestions(
        self,
        address: str,
        land_area: float,
        zone_type: Optional[str],
        result: CorrectedInput
    ) -> List[str]:
        """제안사항 생성"""
        suggestions = []
        
        # 주소 관련 제안
        if "동" not in address and "로" not in address:
            suggestions.append("정확한 법정동 또는 도로명 주소를 입력하면 더 정확한 분석이 가능합니다.")
        
        # 면적 관련 제안
        if land_area >= 1000:
            suggestions.append(
                "큰 필지는 다필지 분석 기능을 사용하여 최적의 분할 방안을 확인하세요."
            )
        
        # 용도지역 관련 제안
        if not zone_type:
            suggestions.append("용도지역을 지정하면 더 정확한 건축 규모 계산이 가능합니다.")
        
        return suggestions
    
    def validate_coordinates(
        self, 
        latitude: float, 
        longitude: float
    ) -> tuple[bool, Optional[str]]:
        """좌표 유효성 검증"""
        # 대한민국 범위 체크
        if not (33.0 <= latitude <= 38.5):
            return False, f"위도가 대한민국 범위를 벗어났습니다 ({latitude})"
        
        if not (124.0 <= longitude <= 132.0):
            return False, f"경도가 대한민국 범위를 벗어났습니다 ({longitude})"
        
        return True, None


# 전역 인스턴스
_auto_corrector = None

def get_auto_corrector() -> AIAutoCorrector:
    """Auto Corrector 싱글톤 인스턴스 반환"""
    global _auto_corrector
    if _auto_corrector is None:
        _auto_corrector = AIAutoCorrector()
    return _auto_corrector
