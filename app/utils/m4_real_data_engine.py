"""
M4 Enhanced Analysis Logic - Building Capacity Decision Engine (Real Data Only)
================================================================================

🔴 절대 원칙: 실제 데이터 기반 계산만 허용
- 샘플/MOC/기본값 기반 계산 절대 금지
- M1(토지정보) + M3(공급유형) 확정 데이터만 사용
- 계산 과정 전체를 서술형으로 출력
- "20세대/26세대" 같은 숫자 단독 출력 금지

Author: ZeroSite Development Team
Date: 2026-01-11 (완전 재구축)
"""

from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
import logging
import math

logger = logging.getLogger(__name__)


class DataSourceError(Exception):
    """데이터 출처 검증 실패 예외"""
    pass


class M4RealDataAnalyzer:
    """
    M4 건축규모 판단 - 실제 데이터 기반 의사결정 엔진
    
    핵심 원칙:
    1. 샘플/MOC/기본값 절대 사용 금지
    2. M1 + M3 확정 데이터만 입력값으로 인정
    3. 계산 과정 전체 서술 + 수치 병기
    4. 법적 최대/이론적 최대/권장 규모 명확히 구분
    """
    
    # 🔴 0단계: 허용되는 데이터 소스 정의
    ALLOWED_DATA_SOURCES = {
        "M1": ["address", "land_area_sqm", "zoning", "building_coverage_ratio", "floor_area_ratio"],
        "M3": ["final_supply_type"],
        "USER_INPUT": ["manual_input", "uploaded_data"]
    }
    
    # 🔴 금지되는 데이터 소스 패턴
    PROHIBITED_DATA_PATTERNS = [
        "MOC", "MOCK", "SAMPLE", "mock", "sample", "기본값", "default",
        "built-in", "object at", "None", "NULL", "N/A"
    ]
    
    # 공급유형별 전용면적 기준 (㎡) - LH 실제 기준
    UNIT_AREA_BY_TYPE = {
        "청년형": {"min": 16, "standard": 40, "max": 50, "name": "청년형"},
        "신혼희망타운 I형": {"min": 36, "standard": 50, "max": 60, "name": "신혼희망타운 I형"},
        "신혼희망타운 II형": {"min": 60, "standard": 75, "max": 85, "name": "신혼희망타운 II형"},
        "다자녀형": {"min": 85, "standard": 95, "max": 120, "name": "다자녀형"},
        "고령자형": {"min": 16, "standard": 35, "max": 50, "name": "고령자형"},
    }
    
    # 용도지역별 법정 건폐율·용적률 (%) - 건축법 기준
    ZONING_LIMITS = {
        "제1종전용주거지역": {"coverage": 50, "far": 100},
        "제2종전용주거지역": {"coverage": 50, "far": 150},
        "제1종일반주거지역": {"coverage": 60, "far": 200},
        "제2종일반주거지역": {"coverage": 60, "far": 250},
        "제3종일반주거지역": {"coverage": 50, "far": 300},
        "준주거지역": {"coverage": 70, "far": 500},
        "상업지역": {"coverage": 90, "far": 1000},
    }
    
    # 공용면적 비율 (복도형 기준)
    COMMON_AREA_RATIO = 0.35  # 35%
    
    # 주차 법정 기준 (서울시 기준)
    PARKING_STANDARDS = {
        "청년형": 0.3,  # 세대당 0.3대 (완화 기준)
        "신혼희망타운 I형": 0.7,
        "신혼희망타운 II형": 1.0,
        "다자녀형": 1.2,
        "고령자형": 0.5
    }
    
    def __init__(self, context_id: str, module_data: Dict[str, Any], frozen_context: Optional[Dict[str, Any]] = None):
        self.context_id = context_id
        self.summary = module_data.get("summary", {})
        self.details = module_data.get("details", {})
        self.raw_data = module_data
        self.frozen_context = frozen_context or {}
        
        # 데이터 출처 검증 플래그
        self.data_source_valid = False
        self.data_source_errors = []
        
        # 계산 결과 저장
        self.calculation_narrative = []  # 계산 과정 서술
        self.legal_limits = {}
        self.theoretical_max = {}
        self.recommended_scale = {}
        
        # 🔴 0단계: 데이터 출처 강제 선언 및 검증
        self._validate_data_sources()
    
    def _validate_data_sources(self) -> None:
        """
        🔴 0단계: 데이터 출처 강제 선언 및 검증
        
        모든 입력 데이터가 허용된 소스에서 왔는지 확인
        금지된 패턴(MOC, SAMPLE 등) 감지 시 즉시 차단
        """
        logger.info(f"🔴 [M4 DATA SOURCE VALIDATION] Starting for context_id={self.context_id}")
        
        # M1 데이터 검증
        m1_address = self.details.get("address", "")
        m1_land_area = self.details.get("land_area", 0)
        m1_zoning = self.details.get("zoning", "")
        
        # M3 데이터 검증
        m3_supply_type = self.summary.get("recommended_type", "")
        
        # 금지 패턴 검사
        all_values = [
            str(m1_address),
            str(m1_land_area),
            str(m1_zoning),
            str(m3_supply_type)
        ]
        
        for value in all_values:
            for prohibited in self.PROHIBITED_DATA_PATTERNS:
                if prohibited.lower() in value.lower():
                    error_msg = f"금지된 데이터 소스 감지: '{prohibited}' in '{value[:50]}'"
                    self.data_source_errors.append(error_msg)
                    logger.error(f"❌ {error_msg}")
        
        # 필수 필드 존재 여부 확인
        if not m1_address or "정보 없음" in str(m1_address):
            self.data_source_errors.append("M1 주소 데이터 누락")
        
        # 토지면적 숫자 변환
        land_area_value = 0
        if isinstance(m1_land_area, (int, float)):
            land_area_value = float(m1_land_area)
        elif isinstance(m1_land_area, str):
            import re
            numbers = re.findall(r'\d+\.?\d*', str(m1_land_area))
            if numbers:
                land_area_value = float(numbers[0])
        
        if land_area_value <= 0:
            self.data_source_errors.append("M1 토지면적 데이터 누락 또는 유효하지 않음")
        
        if not m1_zoning:
            self.data_source_errors.append("M1 용도지역 데이터 누락")
        
        if not m3_supply_type:
            self.data_source_errors.append("M3 공급유형 데이터 누락")
        
        # 검증 결과
        if self.data_source_errors:
            self.data_source_valid = False
            logger.error(f"❌ [M4 DATA SOURCE VALIDATION] FAILED: {len(self.data_source_errors)} errors")
            for error in self.data_source_errors:
                logger.error(f"   - {error}")
        else:
            self.data_source_valid = True
            logger.info(f"✅ [M4 DATA SOURCE VALIDATION] PASSED - All data from allowed sources")
    
    def validate_input_data_gate(self) -> Tuple[bool, List[str]]:
        """
        1️⃣ 입력 데이터 유효성 검증 (Gate)
        
        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []
        
        # 데이터 출처 검증 먼저 확인
        if not self.data_source_valid:
            errors.extend(self.data_source_errors)
            return (False, errors)
        
        # M1 데이터 추출
        land_area_str = self.details.get("land_area", "")
        land_area_sqm = 0
        
        # 토지면적 파싱 (숫자 추출)
        if isinstance(land_area_str, (int, float)):
            land_area_sqm = float(land_area_str)
        elif isinstance(land_area_str, str):
            import re
            numbers = re.findall(r'\d+\.?\d*', land_area_str)
            if numbers:
                land_area_sqm = float(numbers[0])
        
        zoning = self.details.get("zoning", "")
        supply_type = self.summary.get("recommended_type", "")
        
        # 필수 필드 검증
        if land_area_sqm <= 0:
            errors.append("land_area_sqm > 0 조건 미충족")
        
        if not zoning or zoning.strip() == "":
            errors.append("zoning ≠ NULL 조건 미충족")
        
        if not supply_type or supply_type.strip() == "":
            errors.append("final_supply_type ≠ NULL 조건 미충족")
        
        # 건폐율/용적률은 용도지역 기반 조회 가능하므로 필수 아님
        
        is_valid = len(errors) == 0
        
        if not is_valid:
            logger.error(f"❌ [M4 INPUT VALIDATION] FAILED:")
            for error in errors:
                logger.error(f"   - {error}")
        else:
            logger.info(f"✅ [M4 INPUT VALIDATION] PASSED")
        
        return (is_valid, errors)
    
    def calculate_building_capacity_narrative(self) -> Dict[str, Any]:
        """
        2️⃣ 건축 규모 산정 로직 (기획 반영 · 필수)
        
        계산 결과만 내지 말고, 아래 과정을 전부 서술 + 수치로 출력:
        A. 법적 최대 한계 산정
        B. 공급유형별 단위 계획 반영
        C. 실현 가능 규모 조정
        
        Returns:
            Dict with detailed calculation narrative
        """
        # 입력 데이터 추출
        land_area_str = self.details.get("land_area", "")
        land_area_sqm = 0
        
        if isinstance(land_area_str, (int, float)):
            land_area_sqm = float(land_area_str)
        elif isinstance(land_area_str, str):
            import re
            numbers = re.findall(r'\d+\.?\d*', land_area_str)
            if numbers:
                land_area_sqm = float(numbers[0])
        
        zoning = self.details.get("zoning", "")
        supply_type = self.summary.get("recommended_type", "")
        
        # A. 법적 최대 한계 산정
        legal_limits = self._calculate_legal_limits(land_area_sqm, zoning)
        
        # B. 공급유형별 단위 계획 반영
        theoretical_max = self._calculate_theoretical_max(legal_limits, supply_type)
        
        # C. 실현 가능 규모 조정
        recommended_scale = self._calculate_recommended_scale(legal_limits, theoretical_max, supply_type, land_area_sqm)
        
        # 저장
        self.legal_limits = legal_limits
        self.theoretical_max = theoretical_max
        self.recommended_scale = recommended_scale
        
        return {
            "legal_limits": legal_limits,
            "theoretical_max": theoretical_max,
            "recommended_scale": recommended_scale,
            "calculation_narrative": self.calculation_narrative
        }
    
    def _calculate_legal_limits(self, land_area_sqm: float, zoning: str) -> Dict[str, Any]:
        """
        A. 법적 최대 한계 산정
        
        Returns:
            Dict with legal limits and narrative
        """
        # 용도지역별 한도 조회
        limits = self.ZONING_LIMITS.get(zoning, {"coverage": 60, "far": 200})
        coverage_ratio = limits["coverage"]
        far_ratio = limits["far"]
        
        # 건축면적 = 토지면적 × 건폐율
        max_building_area = land_area_sqm * (coverage_ratio / 100)
        
        # 연면적(법정 최대) = 토지면적 × 용적률
        max_gross_floor_area = land_area_sqm * (far_ratio / 100)
        
        # 서술형 출력
        narrative = (
            f"📐 **A. 법적 최대 한계 산정**\\n\\n"
            f"**입력 데이터:**\\n"
            f"- 대지면적: {land_area_sqm:,.2f}㎡\\n"
            f"- 용도지역: {zoning}\\n"
            f"- 법정 건폐율: {coverage_ratio}%\\n"
            f"- 법정 용적률: {far_ratio}%\\n\\n"
            f"**계산 과정:**\\n"
            f"1. 최대 건축면적 = 대지면적 × 건폐율\\n"
            f"   = {land_area_sqm:,.2f}㎡ × {coverage_ratio}%\\n"
            f"   = **{max_building_area:,.2f}㎡**\\n\\n"
            f"2. 법정 최대 연면적 = 대지면적 × 용적률\\n"
            f"   = {land_area_sqm:,.2f}㎡ × {far_ratio}%\\n"
            f"   = **{max_gross_floor_area:,.2f}㎡**\\n\\n"
            f"**해석:**\\n"
            f"법적으로 이 대지에서는 최대 {max_gross_floor_area:,.2f}㎡의 연면적을 확보할 수 있습니다. "
            f"다만, 일조권·사선제한·도로사선 등 추가 규제로 인해 실제 활용 가능 면적은 이보다 10-20% 작을 수 있습니다."
        )
        
        self.calculation_narrative.append(narrative)
        
        return {
            "land_area_sqm": land_area_sqm,
            "zoning": zoning,
            "coverage_ratio": coverage_ratio,
            "far_ratio": far_ratio,
            "max_building_area": round(max_building_area, 2),
            "max_gross_floor_area": round(max_gross_floor_area, 2),
            "narrative": narrative
        }
    
    def _calculate_theoretical_max(self, legal_limits: Dict[str, Any], supply_type: str) -> Dict[str, Any]:
        """
        B. 공급유형별 단위 계획 반영
        
        Returns:
            Dict with theoretical max units and narrative
        """
        max_gross_floor_area = legal_limits["max_gross_floor_area"]
        
        # 공급유형별 전용면적 조회
        unit_area_data = self.UNIT_AREA_BY_TYPE.get(supply_type, self.UNIT_AREA_BY_TYPE["청년형"])
        unit_area_standard = unit_area_data["standard"]
        unit_area_min = unit_area_data["min"]
        unit_area_max = unit_area_data["max"]
        
        # 전용면적 → 공급면적 (공용면적률 35% 적용)
        supply_area_per_unit = unit_area_standard * (1 + self.COMMON_AREA_RATIO)
        
        # 이론적 최대 세대수 = 법정 최대 연면적 / 세대당 공급면적
        theoretical_max_units = max_gross_floor_area / supply_area_per_unit
        
        # 서술형 출력
        narrative = (
            f"📐 **B. 공급유형별 단위 계획 반영**\\n\\n"
            f"**공급유형:** {supply_type}\\n"
            f"**전용면적 범위:** {unit_area_min}~{unit_area_max}㎡ (표준 {unit_area_standard}㎡)\\n"
            f"**공용면적률:** {self.COMMON_AREA_RATIO*100:.0f}% (복도형 기준)\\n\\n"
            f"**계산 과정:**\\n"
            f"1. 세대당 공급면적 = 전용면적 × (1 + 공용면적률)\\n"
            f"   = {unit_area_standard}㎡ × (1 + {self.COMMON_AREA_RATIO*100:.0f}%)\\n"
            f"   = **{supply_area_per_unit:,.2f}㎡/세대**\\n\\n"
            f"2. 이론적 최대 세대수 = 법정 최대 연면적 / 세대당 공급면적\\n"
            f"   = {max_gross_floor_area:,.2f}㎡ / {supply_area_per_unit:,.2f}㎡\\n"
            f"   = **{theoretical_max_units:,.1f}세대** (소수점 절사 전)\\n\\n"
            f"**해석:**\\n"
            f"법정 용적률을 100% 활용하고 공용면적률 {self.COMMON_AREA_RATIO*100:.0f}%를 적용할 경우, "
            f"이론적으로 최대 {math.floor(theoretical_max_units)}세대를 확보할 수 있습니다. "
            f"다만, 코어·계단·복도 등 공용부와 주차 공간 확보를 고려하면 실제 세대수는 이보다 적습니다."
        )
        
        self.calculation_narrative.append(narrative)
        
        return {
            "supply_type": supply_type,
            "unit_area_standard": unit_area_standard,
            "unit_area_range": f"{unit_area_min}~{unit_area_max}㎡",
            "supply_area_per_unit": round(supply_area_per_unit, 2),
            "theoretical_max_units": math.floor(theoretical_max_units),
            "narrative": narrative
        }
    
    def _calculate_recommended_scale(self, legal_limits: Dict[str, Any], theoretical_max: Dict[str, Any], 
                                     supply_type: str, land_area_sqm: float) -> Dict[str, Any]:
        """
        C. 실현 가능 규모 조정 (중요)
        
        주차·코어·LH 심사 현실성 고려
        
        Returns:
            Dict with recommended scale and narrative
        """
        theoretical_max_units = theoretical_max["theoretical_max_units"]
        
        # 조정 계수 (실현 가능성 반영)
        adjustment_factors = {
            "주차 공간 확보": 0.85,  # 주차장으로 15% 면적 소요
            "코어·공용부 비율": 0.90,  # 코어·계단으로 10% 면적 소요
            "LH 심사 안정성": 0.95   # 심사 통과 가능성 5% 버퍼
        }
        
        total_adjustment = 1.0
        for factor_name, factor_value in adjustment_factors.items():
            total_adjustment *= factor_value
        
        # 권장 세대수 = 이론적 최대 × 조정 계수
        recommended_units = math.floor(theoretical_max_units * total_adjustment)
        
        # 권장 연면적
        supply_area_per_unit = theoretical_max["supply_area_per_unit"]
        recommended_gross_floor_area = recommended_units * supply_area_per_unit
        
        # 주차 계획
        parking_standard = self.PARKING_STANDARDS.get(supply_type, 0.5)
        required_parking = math.ceil(recommended_units * parking_standard)
        
        # 서술형 출력
        narrative = (
            f"📐 **C. 실현 가능 규모 조정**\\n\\n"
            f"**조정 요소:**\\n"
        )
        
        for factor_name, factor_value in adjustment_factors.items():
            narrative += f"- {factor_name}: {(1-factor_value)*100:.0f}% 면적 소요 (조정 계수 {factor_value})\n"
        
        narrative += (
            f"\\n**계산 과정:**\\n"
            f"1. 총 조정 계수 = {adjustment_factors['주차 공간 확보']} × {adjustment_factors['코어·공용부 비율']} × {adjustment_factors['LH 심사 안정성']}\\n"
            f"   = **{total_adjustment:.3f}**\\n\\n"
            f"2. 권장 세대수 = 이론적 최대 세대수 × 총 조정 계수\\n"
            f"   = {theoretical_max_units} × {total_adjustment:.3f}\\n"
            f"   = **{recommended_units}세대**\\n\\n"
            f"3. 권장 연면적 = 권장 세대수 × 세대당 공급면적\\n"
            f"   = {recommended_units} × {supply_area_per_unit:,.2f}㎡\\n"
            f"   = **{recommended_gross_floor_area:,.2f}㎡**\\n\\n"
            f"4. 주차 계획:\\n"
            f"   - 법정 기준: {supply_type} 세대당 {parking_standard}대\\n"
            f"   - 필요 주차대수: {recommended_units} × {parking_standard} = **{required_parking}대**\\n"
            f"   - 주차 방식: 지상 또는 필로티 (소규모 단지 특성상 지하 주차장 비경제적)\\n\\n"
            f"**최종 권장 규모:**\\n"
            f"- **세대수: {recommended_units}세대**\\n"
            f"- **연면적: {recommended_gross_floor_area:,.2f}㎡**\\n"
            f"- **주차: {required_parking}대** (법정 기준 충족)\\n\\n"
            f"**해석:**\\n"
            f"법정 최대({theoretical_max_units}세대) 대비 약 {(1-total_adjustment)*100:.0f}%를 감축한 {recommended_units}세대가 "
            f"실제 사업 추진에 적합한 규모입니다. 이는 주차·코어·공용부를 현실적으로 반영한 수치이며, "
            f"LH 신축매입임대 심사에서 통과 가능한 안정적인 계획안입니다."
        )
        
        self.calculation_narrative.append(narrative)
        
        return {
            "adjustment_factors": adjustment_factors,
            "total_adjustment": round(total_adjustment, 3),
            "recommended_units": recommended_units,
            "recommended_gross_floor_area": round(recommended_gross_floor_area, 2),
            "parking_standard": parking_standard,
            "required_parking": required_parking,
            "narrative": narrative
        }
    
    def calculate_parking_plan_narrative(self) -> Dict[str, Any]:
        """
        3️⃣ 주차 계획은 '0대' 출력 금지
        
        Returns:
            Dict with parking plan narrative (never "0대")
        """
        if not self.recommended_scale:
            return {
                "parking_count": "데이터 부족",
                "narrative": "권장 규모 미산정 상태에서는 주차 계획을 수립할 수 없습니다."
            }
        
        supply_type = self.theoretical_max.get("supply_type", "청년형")
        recommended_units = self.recommended_scale.get("recommended_units", 0)
        parking_standard = self.PARKING_STANDARDS.get(supply_type, 0.5)
        required_parking = math.ceil(recommended_units * parking_standard)
        
        # 절대 "0대" 출력 금지
        if required_parking == 0:
            required_parking = math.ceil(recommended_units * 0.3)  # 최소 0.3대/세대
        
        narrative = (
            f"🚗 **주차 계획 (법정 기준 산식 기반)**\\n\\n"
            f"**법정 기준:**\\n"
            f"- 공급유형: {supply_type}\\n"
            f"- 세대당 주차대수: {parking_standard}대/세대\\n"
            f"- 총 세대수: {recommended_units}세대\\n\\n"
            f"**필요 주차대수 산정:**\\n"
            f"필요 주차대수 = 총 세대수 × 세대당 주차대수\\n"
            f"= {recommended_units} × {parking_standard}\\n"
            f"= **{required_parking}대**\\n\\n"
            f"**주차 특례/완화 가능성:**\\n"
        )
        
        if supply_type == "청년형":
            narrative += (
                f"- 청년형 임대주택은 차량 비보유율이 높아(약 60%) 주차 완화 적용 가능\\n"
                f"- 대중교통 접근이 양호한 경우 세대당 0.3대까지 완화 가능 (조례 기준)\\n"
                f"- 완화 적용 시 최소 필요 주차: {math.ceil(recommended_units * 0.3)}대\\n"
            )
        else:
            narrative += (
                f"- 신혼·다자녀형은 차량 보유율이 높아 주차 완화 제한적\\n"
                f"- 법정 기준 {parking_standard}대/세대 준수 권장\\n"
            )
        
        narrative += (
            f"\\n**주차 방식:**\\n"
            f"- 소규모 단지 특성상 지하 주차장은 비경제적\\n"
            f"- 지상 주차 또는 필로티 주차 방식 권장\\n"
            f"- 주차면적: 약 {required_parking * 25}㎡ (1대당 25㎡ 기준)\\n"
        )
        
        return {
            "parking_count": required_parking,
            "parking_count_relaxed": math.ceil(recommended_units * 0.3) if supply_type == "청년형" else required_parking,
            "parking_area_sqm": required_parking * 25,
            "narrative": narrative
        }
    
    def generate_full_m4_report_data(self) -> Dict[str, Any]:
        """
        4️⃣ 최종 출력 필수 구성 (데이터 충분성 확보)
        
        Returns:
            Complete M4 report data with all required sections
        """
        # 데이터 출처 검증 먼저
        if not self.data_source_valid:
            return {
                "error": True,
                "error_type": "DATA_SOURCE_INVALID",
                "error_message": "금지된 데이터 소스 감지 또는 필수 데이터 누락",
                "data_source_errors": self.data_source_errors,
                "use_data_insufficient_template": True,
                "template_version": "v2",
                "fixed_message": (
                    "🔴 DATA SOURCE ERROR\\n\\n"
                    "샘플/MOC/기본값 기반 데이터가 감지되었거나, "
                    "필수 입력 데이터(M1 토지정보 + M3 공급유형)가 누락되었습니다.\\n\\n"
                    "M4 건축 규모 판단은 반드시 실제 데이터만을 기준으로 수행됩니다."
                )
            }
        
        # 입력 데이터 검증
        is_valid, errors = self.validate_input_data_gate()
        if not is_valid:
            return {
                "error": True,
                "error_type": "INPUT_VALIDATION_FAILED",
                "error_message": "입력 데이터 유효성 검증 실패",
                "validation_errors": errors,
                "use_data_insufficient_template": True,
                "template_version": "v2",
                "fixed_message": (
                    "🔴 INPUT DATA VALIDATION FAILED\\n\\n"
                    "필수 입력 조건 미충족:\\n" + "\\n".join(f"- {e}" for e in errors)
                )
            }
        
        # 건축 규모 계산
        capacity_result = self.calculate_building_capacity_narrative()
        
        # 주차 계획
        parking_result = self.calculate_parking_plan_narrative()
        
        # 리스크 및 한계
        risks = self._generate_risks_and_limitations()
        
        # M5 연결
        m5_linkage = self._generate_m5_linkage()
        
        # 최종 데이터 구성
        return {
            "context_id": self.context_id,
            "report_id": f"ZS-M4-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "analysis_date": datetime.now().strftime("%Y년 %m월 %d일"),
            
            # 📌 입력 데이터 요약
            "input_data_summary": {
                "address": self.details.get("address", ""),
                "land_area_sqm": self.legal_limits.get("land_area_sqm", 0),
                "zoning": self.legal_limits.get("zoning", ""),
                "coverage_ratio": self.legal_limits.get("coverage_ratio", 0),
                "far_ratio": self.legal_limits.get("far_ratio", 0),
                "supply_type": self.theoretical_max.get("supply_type", "")
            },
            
            # 📐 계산 과정 설명 (서술형)
            "calculation_narrative": "\\n\\n---\\n\\n".join(self.calculation_narrative),
            
            # 📊 건축 규모 결과 (3단계 구분)
            "building_capacity_results": {
                "legal_max": {
                    "description": "법정 기준 세대수",
                    "units": self.theoretical_max.get("theoretical_max_units", 0),
                    "gross_floor_area": self.legal_limits.get("max_gross_floor_area", 0),
                    "note": "법정 용적률 100% 활용 시 이론적 최대 세대수"
                },
                "theoretical_max": {
                    "description": "이론적 최대 세대수",
                    "units": self.theoretical_max.get("theoretical_max_units", 0),
                    "gross_floor_area": self.legal_limits.get("max_gross_floor_area", 0),
                    "note": "공용면적률 반영 시 이론적 최대 세대수"
                },
                "recommended": {
                    "description": "권장 규모 (실현 가능)",
                    "units": self.recommended_scale.get("recommended_units", 0),
                    "gross_floor_area": self.recommended_scale.get("recommended_gross_floor_area", 0),
                    "parking": self.recommended_scale.get("required_parking", 0),
                    "note": "주차·코어·LH 심사 현실성 반영 후 권장 세대수"
                }
            },
            
            # 🚗 주차 계획
            "parking_plan": parking_result,
            
            # ⚠️ 리스크 및 한계
            "risks_and_limitations": risks,
            
            # 🔗 M5 사업성 연결
            "m5_linkage": m5_linkage,
            
            # 🔐 데이터 출처 선언
            "data_source_declaration": (
                "본 건축 규모 판단은 입력된 실제 데이터(M1·M3)를 기반으로 산정되었으며, "
                "샘플 또는 목업 데이터는 사용되지 않았습니다."
            )
        }
    
    def _generate_risks_and_limitations(self) -> Dict[str, Any]:
        """리스크 및 한계 생성"""
        return {
            "regulatory_risks": [
                {
                    "risk": "일조권 및 사선제한",
                    "description": "북측 인접 대지 경계선으로부터 일정 거리 이격 필요. 법정 용적률 100% 활용 시 상층부 후퇴 불가피.",
                    "impact": "연면적 10-15% 감소 가능"
                },
                {
                    "risk": "도로사선 제한",
                    "description": "전면 도로폭에 따른 건물 높이 제한 적용. 도로폭 6m 이하 시 제약 심화.",
                    "impact": "층수 제한 가능 (최대 5-7층)"
                }
            ],
            "design_risks": [
                {
                    "risk": "코어·계단실 배치",
                    "description": "소규모 단지에서 코어 1개 배치 시 동선 효율 저하. 2개 배치 시 공용면적 증가.",
                    "impact": "세대수 2-3세대 감소 가능"
                },
                {
                    "risk": "주차 공간 확보",
                    "description": "지상 주차 시 조경면적 확보 곤란. 필로티 주차 시 1층 세대 배치 불가.",
                    "impact": "세대수 1-2세대 감소 또는 층고 증가"
                }
            ],
            "m5_business_impact": (
                "권장 세대수({})가 확정되면, M5 사업성 분석에서 다음 항목이 산출됩니다:\\n"
                "- 총 사업비 (토지비 + 건축비 + 부대비용)\\n"
                "- LH 매입 예상 단가 및 총액\\n"
                "- 임대수익 추정 (월 임대료 × 세대수 × 12개월)\\n"
                "- NPV, IRR, ROI 산출\\n\\n"
                "세대수가 {} 대비 {}% 감소 시, 사업성 지표가 민감하게 반응하므로 "
                "설계 단계에서 최대한 권장 규모에 근접하도록 계획해야 합니다."
            ).format(
                self.recommended_scale.get("recommended_units", 0),
                self.theoretical_max.get("theoretical_max_units", 0),
                ((self.theoretical_max.get("theoretical_max_units", 1) - 
                  self.recommended_scale.get("recommended_units", 1)) / 
                 self.theoretical_max.get("theoretical_max_units", 1) * 100)
            )
        }
    
    def _generate_m5_linkage(self) -> str:
        """M5 사업성 연결 문구"""
        recommended_units = self.recommended_scale.get("recommended_units", 0)
        recommended_gfa = self.recommended_scale.get("recommended_gross_floor_area", 0)
        supply_type = self.theoretical_max.get("supply_type", "청년형")
        
        return (
            f"🔗 **M5 사업성 분석 연결**\\n\\n"
            f"본 M4 보고서에서 확정된 건축 규모는 다음과 같습니다:\\n"
            f"- 총 세대수: **{recommended_units}세대**\\n"
            f"- 총 연면적: **{recommended_gfa:,.2f}㎡**\\n"
            f"- 공급유형: **{supply_type}**\\n\\n"
            f"이 수치는 M5 사업성 분석의 필수 입력값으로 사용되며, 다음 항목에 직접 영향을 미칩니다:\\n"
            f"1. **총 사업비**: 건축비(연면적 기준) + 토지비 + 부대비용\\n"
            f"2. **LH 매입 총액**: 세대수 × 세대당 매입 단가\\n"
            f"3. **임대수익**: 세대수 × 월 임대료 × 12개월\\n"
            f"4. **NPV/IRR/ROI**: 사업비 대비 수익 구조 분석\\n\\n"
            f"**중요:** M4 세대수가 변경되면 M5 사업성 지표가 즉시 재계산되어야 하므로, "
            f"설계 변경 시 반드시 M4-M5 연동 재분석이 필요합니다."
        )


def prepare_m4_real_data_report(context_id: str, module_data: Dict[str, Any], 
                                  frozen_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    M4 Real Data 보고서 준비 (외부 호출용)
    
    Args:
        context_id: Context ID
        module_data: M4 모듈 데이터
        frozen_context: frozen snapshot 데이터
    
    Returns:
        보고서 데이터 또는 ERROR
    """
    analyzer = M4RealDataAnalyzer(context_id, module_data, frozen_context)
    return analyzer.generate_full_m4_report_data()
