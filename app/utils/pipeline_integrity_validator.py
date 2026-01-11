"""
ZeroSite Pipeline Integrity Validator
======================================

목적: M1~M6 파이프라인이 실행 가능한 상태인지 기계적으로 판정

원칙:
- 해석 ❌
- 추정 ❌
- 미사여구 ❌
- 검증 / 판정 / 상태 코드만 출력

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """파이프라인 검증 상태"""
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAIL = "FAIL"


class PipelineIntegrityValidator:
    """
    ZeroSite 분석 파이프라인의 정합성 검증 스크립트
    
    이 클래스는 분석이나 설명이 아니라,
    M1~M6 전체가 실행 가능한 상태인지 여부를 기계적으로 판정합니다.
    """
    
    # 금지 값 목록
    PROHIBITED_VALUES = [
        "null",
        "N/A",
        "built-in",
        "object at",
        "None",
        "undefined"
    ]
    
    def __init__(self, pipeline_results: Dict[str, Any]):
        """
        Args:
            pipeline_results: Pipeline 전체 결과 (M1~M6)
        """
        self.results = pipeline_results
        self.validation_errors: List[str] = []
        self.blocked_module: Optional[str] = None
        self.missing_fields: List[str] = []
    
    def validate(self) -> Dict[str, Any]:
        """
        전체 파이프라인 정합성 검증
        
        Returns:
            Dict: {
                "status": "PASS" | "BLOCKED" | "FAIL",
                "block_module": str | None,
                "missing_fields": List[str],
                "errors": List[str]
            }
        """
        errors = []
        
        # 1. 전역 세션 검증
        if not self._validate_global_session():
            return {
                "status": ValidationStatus.FAIL.value,
                "block_module": None,
                "missing_fields": [],
                "errors": self.validation_errors
            }
        
        # 2. 모듈별 필수 필드 체크
        validation_sequence = [
            ("M1", self._validate_m1),
            ("M2", self._validate_m2),
            ("M3", self._validate_m3),
            ("M4", self._validate_m4),
            ("M5", self._validate_m5),
            ("M6", self._validate_m6)
        ]
        
        for module_name, validator_func in validation_sequence:
            is_valid, missing = validator_func()
            
            if not is_valid:
                for field in missing:
                    errors.append(f"{module_name}: Missing required field '{field}'")
                
                return {
                    "status": ValidationStatus.BLOCKED.value,
                    "block_module": module_name,
                    "missing_fields": missing,
                    "errors": errors
                }
        
        # 3. 금지 값 검사
        if not self._validate_prohibited_values():
            return {
                "status": ValidationStatus.FAIL.value,
                "block_module": None,
                "missing_fields": [],
                "errors": self.validation_errors
            }
        
        # 4. 모든 검증 통과
        return {
            "status": ValidationStatus.PASS.value,
            "block_module": None,
            "missing_fields": [],
            "errors": []
        }
    
    def _validate_global_session(self) -> bool:
        """
        전역 세션 검증: 모든 모듈이 동일 Context ID를 사용하는가?
        
        Returns:
            bool: 검증 통과 여부
        """
        context_ids = set()
        
        for module_name in ["land", "appraisal", "housing_type", "capacity", "feasibility", "lh_review"]:
            if module_name in self.results:
                module_data = self.results[module_name]
                
                # Context ID 추출
                context_id = (
                    module_data.get("context_id") or
                    module_data.get("module_context_id") or
                    module_data.get("parcel_id")
                )
                
                if context_id:
                    context_ids.add(context_id)
        
        # Context ID가 2개 이상이면 불일치
        if len(context_ids) > 1:
            self.validation_errors.append(f"Context ID mismatch: {context_ids}")
            return False
        
        return True
    
    def _validate_m1(self) -> Tuple[bool, List[str]]:
        """
        M1 (ROOT) 검증
        
        필수:
        - address
        - land_area_sqm
        - zoning
        
        Returns:
            Tuple[bool, List[str]]: (통과 여부, 누락 필드)
        """
        missing = []
        
        if "land" not in self.results:
            missing.append("land (M1 전체 누락)")
            return (False, missing)
        
        m1_data = self.results["land"]
        
        # address 검증
        address = m1_data.get("address", "")
        if not address or address.strip() == "" or "Mock Data" in str(address):
            missing.append("address")
        
        # land_area_sqm 검증
        land_area = m1_data.get("land", {}).get("area_sqm", 0)
        if not land_area or land_area <= 0:
            missing.append("land_area_sqm")
        
        # zoning 검증
        zoning = m1_data.get("zoning", {}).get("type", "")
        if not zoning or zoning.strip() == "":
            missing.append("zoning")
        
        return (len(missing) == 0, missing)
    
    def _validate_m2(self) -> Tuple[bool, List[str]]:
        """
        M2 검증
        
        필수:
        - land_value_reference OR market_index
        - analysis_text_length ≥ 300자
        
        Returns:
            Tuple[bool, List[str]]: (통과 여부, 누락 필드)
        """
        missing = []
        
        if "appraisal" not in self.results:
            missing.append("appraisal (M2 전체 누락)")
            return (False, missing)
        
        m2_data = self.results["appraisal"]
        
        # land_value 검증
        land_value = m2_data.get("summary", {}).get("land_value_total_krw", 0)
        if not land_value or land_value <= 0:
            missing.append("land_value_reference")
        
        # analysis_text 검증 (상세 분석 텍스트 길이)
        details = m2_data.get("details", {})
        analysis_text = str(details)  # 전체 details를 텍스트로 변환
        
        if len(analysis_text) < 300:
            missing.append("analysis_text_length")
        
        return (len(missing) == 0, missing)
    
    def _validate_m3(self) -> Tuple[bool, List[str]]:
        """
        M3 검증
        
        필수:
        - final_supply_type (1개)
        - rejection_reason_count ≥ 2
        
        Returns:
            Tuple[bool, List[str]]: (통과 여부, 누락 필드)
        """
        missing = []
        
        if "housing_type" not in self.results:
            missing.append("housing_type (M3 전체 누락)")
            return (False, missing)
        
        m3_data = self.results["housing_type"]
        
        # final_supply_type 검증
        selected_type = m3_data.get("details", {}).get("selected", {}).get("type", "")
        if not selected_type or selected_type.strip() == "":
            missing.append("final_supply_type")
        
        # rejection_reason (weaknesses) 검증
        weaknesses = m3_data.get("details", {}).get("insights", {}).get("weaknesses", [])
        if len(weaknesses) < 2:
            missing.append("rejection_reason_count")
        
        return (len(missing) == 0, missing)
    
    def _validate_m4(self) -> Tuple[bool, List[str]]:
        """
        M4 검증
        
        필수:
        - total_units
        - total_floor_area
        - recommended_scale (boolean = true)
        
        Returns:
            Tuple[bool, List[str]]: (통과 여부, 누락 필드)
        """
        missing = []
        
        if "capacity" not in self.results:
            missing.append("capacity (M4 전체 누락)")
            return (False, missing)
        
        m4_data = self.results["capacity"]
        
        # total_units 검증
        total_units = m4_data.get("summary", {}).get("incentive_units", 0)
        if not total_units or total_units <= 0:
            missing.append("total_units")
        
        # total_floor_area 검증
        total_floor_area = m4_data.get("details", {}).get("incentive_capacity", {}).get("target_gfa_sqm", 0)
        if not total_floor_area or total_floor_area <= 0:
            missing.append("total_floor_area")
        
        # recommended_scale 검증 (notes에 "권장 규모" 포함 여부)
        notes = str(m4_data.get("details", {}).get("metadata", {}).get("notes", []))
        if "권장 규모" not in notes and "recommended" not in notes.lower():
            missing.append("recommended_scale")
        
        return (len(missing) == 0, missing)
    
    def _validate_m5(self) -> Tuple[bool, List[str]]:
        """
        M5 검증
        
        필수:
        - total_project_cost
        - lh_purchase_price
        - npv OR feasibility_statement
        
        Returns:
            Tuple[bool, List[str]]: (통과 여부, 누락 필드)
        """
        missing = []
        
        if "feasibility" not in self.results:
            missing.append("feasibility (M5 전체 누락)")
            return (False, missing)
        
        m5_data = self.results["feasibility"]
        
        # total_project_cost 검증
        total_cost = m5_data.get("details", {}).get("costs", {}).get("total", 0)
        if not total_cost or total_cost <= 0:
            missing.append("total_project_cost")
        
        # lh_purchase_price 검증
        lh_price = m5_data.get("details", {}).get("lh_purchase", {}).get("price", 0)
        if not lh_price or lh_price <= 0:
            missing.append("lh_purchase_price")
        
        # npv 검증
        npv = m5_data.get("summary", {}).get("npv_public_krw")
        if npv is None:
            missing.append("npv")
        
        return (len(missing) == 0, missing)
    
    def _validate_m6(self) -> Tuple[bool, List[str]]:
        """
        M6 검증
        
        필수:
        - decision_basis_count ≥ 3
        - risk_count ≥ 2
        
        Returns:
            Tuple[bool, List[str]]: (통과 여부, 누락 필드)
        """
        missing = []
        
        if "lh_review" not in self.results:
            missing.append("lh_review (M6 전체 누락)")
            return (False, missing)
        
        m6_data = self.results["lh_review"]
        
        # decision_basis 검증 (strengths)
        strengths = m6_data.get("details", {}).get("swot", {}).get("strengths", [])
        if len(strengths) < 3:
            missing.append("decision_basis_count")
        
        # risk_count 검증 (weaknesses + threats)
        weaknesses = m6_data.get("details", {}).get("swot", {}).get("weaknesses", [])
        threats = m6_data.get("details", {}).get("swot", {}).get("threats", [])
        total_risks = len(weaknesses) + len(threats)
        
        if total_risks < 2:
            missing.append("risk_count")
        
        return (len(missing) == 0, missing)
    
    def _validate_prohibited_values(self) -> bool:
        """
        금지 값 검사 (GLOBAL SANITIZER)
        
        금지 값:
        - null
        - N/A
        - built-in
        - object at
        - None
        
        Returns:
            bool: 검증 통과 여부
        """
        results_str = str(self.results)
        
        for prohibited in self.PROHIBITED_VALUES:
            if prohibited in results_str:
                self.validation_errors.append(f"Prohibited value detected: {prohibited}")
                return False
        
        return True


def validate_pipeline(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    파이프라인 정합성 검증 실행
    
    Args:
        pipeline_results: Pipeline 전체 결과 (M1~M6)
    
    Returns:
        Dict: 검증 결과
    """
    validator = PipelineIntegrityValidator(pipeline_results)
    status, details = validator.validate()
    
    return {
        "validation_status": status.value,
        "details": details
    }


class PipelineIntegrityExplainer:
    """
    UX용 설명 텍스트 자동 생성기
    
    데이터 없음 시 이유/영향/다음 행동을 사람이 읽을 수 있는 형태로 제시합니다.
    """
    
    # 모듈명 한글 매핑
    MODULE_NAMES = {
        "M1": "토지 정보",
        "M2": "토지 가치 평가",
        "M3": "공급 유형 선정",
        "M4": "건축 규모 판단",
        "M5": "사업성 분석",
        "M6": "종합 판단"
    }
    
    # 필드명 한글 매핑
    FIELD_NAMES = {
        # M1
        "address": "사업지 주소",
        "land_area_sqm": "토지 면적(㎡)",
        "zoning": "용도지역",
        
        # M2
        "land_value_reference": "토지 가치 산정 기준",
        "analysis_text_length": "상세 분석 내용",
        
        # M3
        "final_supply_type": "최종 공급 유형",
        "rejection_reason_count": "거부 사유 2개 이상",
        
        # M4
        "total_units": "총 세대수 (M4 결과)",
        "total_floor_area": "총 연면적 (㎡)",
        "recommended_scale": "권장 규모 판단",
        
        # M5
        "total_project_cost": "총 사업비 (공사비 + 기타비용)",
        "lh_purchase_price": "LH 매입 단가 또는 단가 산정 기준",
        "npv": "NPV (순현재가치)",
        
        # M6
        "decision_basis_count": "판단 근거 3개 이상",
        "risk_count": "리스크 2개 이상"
    }
    
    def generate_user_friendly_explanation(self, validation_result: Dict[str, Any]) -> str:
        """
        검증 결과를 UX 친화적 메시지로 변환
        
        Args:
            validation_result: PipelineIntegrityValidator.validate() 결과
            
        Returns:
            str: 사용자 친화적 설명 텍스트
        """
        status = validation_result.get("status", "UNKNOWN")
        block_module = validation_result.get("block_module", "")
        missing_fields = validation_result.get("missing_fields", [])
        
        # PASS 상태
        if status == "PASS":
            return self._generate_pass_message()
        
        # BLOCKED 상태
        if status == "BLOCKED":
            return self._generate_blocked_message(block_module, missing_fields)
        
        # FAIL 상태
        if status == "FAIL":
            errors = validation_result.get("errors", [])
            return self._generate_fail_message(errors)
        
        return "❌ 알 수 없는 검증 상태입니다."
    
    def _generate_pass_message(self) -> str:
        """PASS 상태 메시지"""
        return """✅ 모든 필수 데이터가 정상적으로 입력되었습니다.

🎯 다음 단계
• M1~M6 전체 분석이 완료되었습니다
• 보고서를 확인하고 최종 검토를 진행하세요

---
ZeroSite는 입력된 데이터만을 기반으로 분석하며, 누락된 정보는 자동으로 추정하지 않습니다.
ⓒ ZeroSite by AntennaHoldings | Natai Heum"""
    
    def _generate_blocked_message(self, block_module: str, missing_fields: List[str]) -> str:
        """BLOCKED 상태 메시지"""
        module_name = self.MODULE_NAMES.get(block_module, block_module)
        
        # 누락 필드를 한글로 변환
        missing_names = []
        for field in missing_fields:
            field_name = self.FIELD_NAMES.get(field, field)
            missing_names.append(f"• {field_name}")
        
        missing_text = "\n".join(missing_names)
        
        # 다음 단계 영향 분석
        next_modules = self._get_affected_modules(block_module)
        
        # Action List 생성
        action_list = self._generate_action_list(block_module, missing_fields)
        
        return f"""📍 현재 상태
현재 분석은 {block_module} ({module_name}) 단계에서 중단되었습니다.

❓ 왜 중단되었는가
다음 필수 정보가 입력되지 않았습니다:
{missing_text}

⚠️ 이 상태로는 무엇이 불가능한가
{next_modules}

✅ 지금 해야 할 일
{action_list}

🎯 입력 후 달라지는 점
• {block_module} {module_name} 분석이 완료됩니다
• 다음 단계 분석이 자동으로 시작됩니다

---
ZeroSite는 입력된 데이터만을 기반으로 분석하며, 누락된 정보는 자동으로 추정하지 않습니다.
ⓒ ZeroSite by AntennaHoldings | Natai Heum"""
    
    def _generate_fail_message(self, errors: List[str]) -> str:
        """FAIL 상태 메시지"""
        error_text = "\n".join([f"• {e}" for e in errors[:5]])  # 최대 5개만 표시
        
        return f"""❌ 데이터 품질 오류가 감지되었습니다

🔍 감지된 문제
{error_text}

✅ 해결 방법
1. 입력 데이터에서 null/N/A/undefined 값을 제거해 주세요
2. 모든 숫자 필드에 올바른 값이 입력되었는지 확인해 주세요
3. Context ID가 전체 모듈에서 일치하는지 확인해 주세요

---
ZeroSite는 입력된 데이터만을 기반으로 분석하며, 누락된 정보는 자동으로 추정하지 않습니다.
ⓒ ZeroSite by AntennaHoldings | Natai Heum"""
    
    def _get_affected_modules(self, block_module: str) -> str:
        """차단된 모듈 이후 영향받는 모듈 분석"""
        module_flow = {
            "M1": ["M2 토지 가치 평가", "M3 공급 유형 선정", "M4 건축 규모 판단", "M5 사업성 분석", "M6 종합 판단"],
            "M2": ["M3 공급 유형 선정", "M4 건축 규모 판단", "M5 사업성 분석", "M6 종합 판단"],
            "M3": ["M4 건축 규모 판단", "M5 사업성 분석", "M6 종합 판단"],
            "M4": ["M5 사업성 분석", "M6 종합 판단"],
            "M5": ["M6 종합 판단"],
            "M6": []
        }
        
        affected = module_flow.get(block_module, [])
        if not affected:
            return "• 모든 분석이 완료되었습니다"
        
        return "\n".join([f"• {m}을(를) 시작할 수 없습니다" for m in affected])
    
    def _generate_action_list(self, block_module: str, missing_fields: List[str]) -> str:
        """Action List 생성"""
        actions = []
        for i, field in enumerate(missing_fields, 1):
            field_name = self.FIELD_NAMES.get(field, field)
            actions.append(f"{i}. [{block_module} 입력] {field_name}을(를) 입력해 주세요")
        
        return "\n".join(actions)
