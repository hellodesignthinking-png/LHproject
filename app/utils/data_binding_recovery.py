"""
ZeroSite Data Binding Recovery and Forced Recalculation Module
==============================================================

목적: M4/M5에서 상위 모듈(M1~M3) 데이터 연결 실패 시 강제 복구

핵심 원칙:
- 0단계: 데이터 연결 상태 진단 (최우선)
- 1단계: 데이터 바인딩 복구 루틴 (강제 실행)
- 2단계: M4 건축규모 계산 실행 조건 (Gate)
- 3단계: 계산 결과 출력 규칙
- 4단계: M5 사업성 분석 연결 조건
- 5단계: 리포트 렌더링 차단 규칙

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from typing import Dict, Any, List, Tuple, Optional
import logging
import re

logger = logging.getLogger(__name__)


class DataBindingError(Exception):
    """데이터 바인딩 실패 예외"""
    pass


class DataBindingRecovery:
    """
    M4/M5 데이터 바인딩 복구 엔진
    
    상위 모듈(M1~M3) 데이터가 연결되지 않은 경우
    Context ID 기반으로 데이터를 강제로 재조회하여 바인딩합니다.
    """
    
    # 금지 값 패턴 (DATA BINDING FAILURE 조건)
    PROHIBITED_PATTERNS = [
        r"built-in",
        r"object at",
        r"None",
        r"<.*?>",
        r"null",
        r"undefined",
    ]
    
    def __init__(self, context_id: str):
        self.context_id = context_id
        self.binding_status = {}
        self.recovered_data = {}
        
    def diagnose(self, module_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        0단계: 데이터 연결 상태 진단
        
        다음 중 하나라도 발견되면 DATA BINDING FAILURE:
        - 주소 / 토지면적 / 용도지역이 공란
        - 세대수 / 연면적이 NULL
        - %, ㎡, 세대 앞에 값이 없음
        - built-in, object at, None 문자열 노출
        
        Returns:
            {
                "status": "CONNECTED" | "BINDING_FAILURE",
                "missing_fields": List[str],
                "prohibited_values": List[str]
            }
        """
        missing_fields = []
        prohibited_values = []
        
        # 1️⃣ 필수 필드 검증
        required_fields = {
            "address": module_data.get("address", ""),
            "land_area_sqm": module_data.get("land_area_sqm", 0),
            "zoning": module_data.get("zoning", ""),
            "total_units": module_data.get("total_units"),
            "total_floor_area": module_data.get("total_floor_area"),
        }
        
        for field, value in required_fields.items():
            if value is None or (isinstance(value, str) and value.strip() == ""):
                missing_fields.append(field)
            elif isinstance(value, (int, float)) and value <= 0:
                missing_fields.append(f"{field} (값: {value})")
        
        # 2️⃣ 금지 값 검출
        data_str = str(module_data)
        for pattern in self.PROHIBITED_PATTERNS:
            matches = re.findall(pattern, data_str, re.IGNORECASE)
            if matches:
                prohibited_values.extend(matches)
        
        # 3️⃣ 단위 없는 숫자 검증 (%, ㎡, 세대 앞에 값 확인)
        # 예: "건폐율: %" → 실패
        unit_patterns = [
            (r"(\d+\.?\d*)\s*%", "퍼센트"),
            (r"(\d+\.?\d*)\s*㎡", "제곱미터"),
            (r"(\d+\.?\d*)\s*세대", "세대"),
        ]
        
        for pattern, unit_name in unit_patterns:
            if not re.search(pattern, data_str):
                # 단위는 있지만 숫자가 없는 경우
                if unit_name in data_str:
                    missing_fields.append(f"{unit_name} 값 누락")
        
        # 4️⃣ 상태 판정
        if missing_fields or prohibited_values:
            status = "BINDING_FAILURE"
        else:
            status = "CONNECTED"
        
        result = {
            "status": status,
            "missing_fields": missing_fields,
            "prohibited_values": list(set(prohibited_values))
        }
        
        logger.info(f"🔍 Data Binding Diagnosis for {self.context_id}: {result}")
        return result
    
    def recover_from_context(self, frozen_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        1단계: Context ID 기준 상위 모듈 재조회
        
        동일 Context ID에서:
        - M1: address, land_area_sqm, zoning
        - M3: final_supply_type
        를 명시적으로 다시 불러와 바인딩
        
        Args:
            frozen_context: Context.get_frozen_context(context_id) 결과
            
        Returns:
            {
                "m1_data": {...},
                "m3_data": {...},
                "recovery_status": "SUCCESS" | "FAILED"
            }
        """
        logger.info(f"🔄 Starting data recovery for context_id={self.context_id}")
        
        recovered = {
            "m1_data": {},
            "m3_data": {},
            "recovery_status": "FAILED"
        }
        
        if not frozen_context:
            logger.error(f"❌ Frozen context not found for {self.context_id}")
            return recovered
        
        try:
            # M1 데이터 추출
            m1_result = frozen_context.get("M1", {})
            if m1_result:
                land_data = m1_result.get("result", {})
                details = land_data.get("details", {})
                
                recovered["m1_data"] = {
                    "address": details.get("address", ""),
                    "land_area_sqm": details.get("land", {}).get("area_sqm", 0),
                    "zoning": details.get("zoning", {}).get("type", ""),
                    "far": details.get("zoning", {}).get("far", 0),
                    "bcr": details.get("zoning", {}).get("bcr", 0),
                }
                logger.info(f"✅ M1 data recovered: {recovered['m1_data']}")
            
            # M3 데이터 추출
            m3_result = frozen_context.get("M3", {})
            if m3_result:
                housing_data = m3_result.get("result", {})
                details = housing_data.get("details", {})
                selected = details.get("selected", {})
                
                recovered["m3_data"] = {
                    "final_supply_type": selected.get("type", "청년형"),
                    "recommended_units": details.get("capacity", {}).get("min_units", 0),
                }
                logger.info(f"✅ M3 data recovered: {recovered['m3_data']}")
            
            # 필수 필드 검증
            m1_valid = (
                recovered["m1_data"].get("address") and
                recovered["m1_data"].get("land_area_sqm", 0) > 0 and
                recovered["m1_data"].get("zoning")
            )
            
            m3_valid = recovered["m3_data"].get("final_supply_type")
            
            if m1_valid and m3_valid:
                recovered["recovery_status"] = "SUCCESS"
                logger.info(f"🎉 Data recovery SUCCESS for {self.context_id}")
            else:
                logger.warning(f"⚠️ Data recovery INCOMPLETE: M1={m1_valid}, M3={m3_valid}")
        
        except Exception as e:
            logger.error(f"❌ Data recovery failed: {e}")
        
        return recovered
    
    def validate_gate_conditions(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        2단계: M4 건축규모 계산 실행 조건 (Gate)
        
        아래 조건을 모두 만족할 때만 M4 계산 허용:
        - address ≠ NULL
        - land_area_sqm > 0
        - zoning ≠ NULL
        - final_supply_type ≠ NULL
        
        Returns:
            (gate_open: bool, missing_conditions: List[str])
        """
        missing = []
        
        if not data.get("address"):
            missing.append("address (사업지 주소)")
        
        if not data.get("land_area_sqm") or data.get("land_area_sqm", 0) <= 0:
            missing.append("land_area_sqm (토지 면적)")
        
        if not data.get("zoning"):
            missing.append("zoning (용도지역)")
        
        if not data.get("final_supply_type"):
            missing.append("final_supply_type (공급유형)")
        
        gate_open = len(missing) == 0
        
        if not gate_open:
            logger.warning(f"🚫 M4 Calculation GATE CLOSED: {missing}")
        else:
            logger.info(f"✅ M4 Calculation GATE OPEN")
        
        return (gate_open, missing)
    
    def generate_connection_error_message(self, missing_fields: List[str]) -> str:
        """
        STEP 2 실패 시 출력 메시지 생성
        
        Returns:
            HTML formatted error message
        """
        missing_text = "\n".join([f"• {field}" for field in missing_fields])
        
        return f"""
<div style="max-width: 800px; margin: 100px auto; padding: 40px; background: #fff3cd; border: 3px solid #ffc107; border-radius: 8px;">
    <h2 style="color: #856404; margin-bottom: 20px;">🔴 DATA CONNECTION ERROR</h2>
    
    <p style="font-size: 16px; line-height: 1.8; color: #856404;">
        상위 모듈(M1~M3) 데이터가 연결되지 않아<br>
        <strong>건축규모(M4) 및 사업성(M5) 분석을 수행할 수 없습니다.</strong>
    </p>
    
    <h3 style="color: #856404; margin-top: 30px;">누락된 필수 데이터:</h3>
    <pre style="background: white; padding: 20px; border-radius: 4px; color: #856404;">
{missing_text}
    </pre>
    
    <p style="margin-top: 30px; font-size: 14px; color: #856404;">
        <strong>ZeroSite는 상위 데이터가 연결되지 않은 상태에서<br>
        분석 결과를 생성하지 않습니다.</strong><br>
        모든 수치는 단일 Context ID 기반으로 계산됩니다.
    </p>
    
    <hr style="margin: 30px 0; border: none; border-top: 1px solid #ffc107;">
    
    <p style="text-align: center; font-size: 12px; color: #856404;">
        ⓒ ZeroSite by AntennaHoldings | Natai Heum<br>
        <strong>ZEROSITE</strong>
    </p>
</div>
"""


def apply_data_binding_recovery(
    context_id: str,
    module_data: Dict[str, Any],
    frozen_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    데이터 바인딩 복구 전체 루틴 실행
    
    Args:
        context_id: Context ID
        module_data: 현재 모듈 데이터
        frozen_context: Context.get_frozen_context(context_id) 결과
        
    Returns:
        {
            "status": "CONNECTED" | "RECOVERED" | "BINDING_ERROR",
            "data": {...},  # 복구된 데이터
            "error_message": str | None
        }
    """
    recovery = DataBindingRecovery(context_id)
    
    # 0단계: 진단
    diagnosis = recovery.diagnose(module_data)
    
    if diagnosis["status"] == "CONNECTED":
        logger.info(f"✅ Data already connected for {context_id}")
        return {
            "status": "CONNECTED",
            "data": module_data,
            "error_message": None
        }
    
    # 1단계: 복구 시도
    logger.warning(f"⚠️ DATA BINDING FAILURE detected, attempting recovery...")
    
    if not frozen_context:
        # Context 없으면 즉시 실패
        error_msg = recovery.generate_connection_error_message(
            diagnosis["missing_fields"]
        )
        return {
            "status": "BINDING_ERROR",
            "data": {},
            "error_message": error_msg
        }
    
    recovered = recovery.recover_from_context(frozen_context)
    
    if recovered["recovery_status"] == "FAILED":
        error_msg = recovery.generate_connection_error_message(
            diagnosis["missing_fields"]
        )
        return {
            "status": "BINDING_ERROR",
            "data": {},
            "error_message": error_msg
        }
    
    # 2단계: Gate 검증
    merged_data = {**module_data, **recovered["m1_data"], **recovered["m3_data"]}
    gate_open, missing_conditions = recovery.validate_gate_conditions(merged_data)
    
    if not gate_open:
        error_msg = recovery.generate_connection_error_message(missing_conditions)
        return {
            "status": "BINDING_ERROR",
            "data": {},
            "error_message": error_msg
        }
    
    # 성공
    logger.info(f"🎉 Data binding recovery SUCCESS for {context_id}")
    return {
        "status": "RECOVERED",
        "data": merged_data,
        "error_message": None
    }
