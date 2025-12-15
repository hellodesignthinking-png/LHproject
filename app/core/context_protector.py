"""
ZeroSite v40.3 - Context Protection Module
Pipeline Lock Release: 감정평가 기준 데이터 보호

목적:
1. Appraisal Context의 Immutable 보장
2. 데이터 일관성 검증
3. 파이프라인 의존성 체크
4. 무단 수정 방지

Created: 2025-12-14
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException


class ContextProtector:
    """
    Context 보호 및 검증 클래스
    
    핵심 원칙:
    - Appraisal 데이터는 READ-ONLY (수정 불가)
    - 모든 파생 데이터는 Appraisal 기준
    - Pipeline 순서 강제: Appraisal → Diagnosis → Capacity → Scenario → LH Review
    """
    
    # Immutable 필드 정의
    IMMUTABLE_FIELDS = [
        "appraisal.final_value",
        "appraisal.value_per_sqm",
        "appraisal.zoning",
        "appraisal.official_price",
        "appraisal.transactions",
        "appraisal.premium",
        "appraisal.restrictions"
    ]
    
    # Required Appraisal 필드
    REQUIRED_APPRAISAL_FIELDS = [
        "final_value",
        "value_per_sqm",
        "zoning",
        "official_price",
        "transactions"
    ]
    
    # Pipeline 의존성 정의
    PIPELINE_DEPENDENCIES = {
        "diagnosis": ["appraisal"],
        "capacity": ["appraisal"],
        "scenario": ["appraisal", "diagnosis", "capacity"],
        "lh_review": ["appraisal", "diagnosis", "capacity", "scenario"]
    }
    
    
    @classmethod
    def validate_appraisal_complete(cls, context: Dict[str, Any]) -> None:
        """
        감정평가 완료 상태 검증
        
        Args:
            context: 검증할 Context 객체
            
        Raises:
            HTTPException: 필수 필드가 없거나 불완전한 경우
        """
        if "appraisal" not in context:
            raise HTTPException(
                status_code=400,
                detail="❌ 감정평가가 실행되지 않았습니다. 먼저 토지분석을 실행하세요."
            )
        
        appraisal = context["appraisal"]
        
        # 필수 필드 체크
        missing_fields = []
        for field in cls.REQUIRED_APPRAISAL_FIELDS:
            if field not in appraisal or not appraisal[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"❌ 감정평가 필수 필드 누락: {', '.join(missing_fields)}"
            )
        
        # 거래사례 개수 체크
        if len(appraisal.get("transactions", [])) < 5:
            raise HTTPException(
                status_code=400,
                detail="❌ 거래사례가 부족합니다 (최소 5건 필요)"
            )
    
    
    @classmethod
    def validate_pipeline_order(cls, context: Dict[str, Any], requesting_module: str) -> None:
        """
        파이프라인 순서 검증
        
        Args:
            context: 검증할 Context 객체
            requesting_module: 요청하는 모듈명 (diagnosis, capacity, scenario, lh_review)
            
        Raises:
            HTTPException: 의존성이 충족되지 않은 경우
        """
        if requesting_module not in cls.PIPELINE_DEPENDENCIES:
            return
        
        required_modules = cls.PIPELINE_DEPENDENCIES[requesting_module]
        missing_modules = []
        
        for required in required_modules:
            if required not in context or not context[required]:
                missing_modules.append(required)
        
        if missing_modules:
            raise HTTPException(
                status_code=400,
                detail=f"❌ {requesting_module} 실행 불가: 선행 모듈 누락 [{', '.join(missing_modules)}]"
            )
    
    
    @classmethod
    def check_data_consistency(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 일관성 체크
        
        모든 모듈이 동일한 기준 데이터를 사용하는지 검증
        
        Returns:
            Dict: 검증 결과
        """
        if "appraisal" not in context:
            return {
                "status": "❌ FAIL",
                "reason": "Appraisal 데이터 없음"
            }
        
        checks = []
        
        # Zone Consistency
        appraisal_zone = context.get("appraisal", {}).get("zoning", {}).get("zone_type")
        diagnosis_zone = context.get("diagnosis", {}).get("zone_type")
        capacity_zone = context.get("capacity", {}).get("zoning", {}).get("zone_type")
        
        zone_match = True
        if diagnosis_zone and diagnosis_zone != appraisal_zone:
            zone_match = False
        if capacity_zone and capacity_zone != appraisal_zone:
            zone_match = False
        
        checks.append({
            "name": "용도지역 일관성",
            "status": "✅ PASS" if zone_match else "❌ FAIL",
            "details": {
                "appraisal": appraisal_zone,
                "diagnosis": diagnosis_zone,
                "capacity": capacity_zone
            }
        })
        
        # Price Consistency
        appraisal_price = context.get("appraisal", {}).get("official_price")
        diagnosis_price = context.get("diagnosis", {}).get("official_price")
        
        price_match = True
        if diagnosis_price and diagnosis_price != appraisal_price:
            price_match = False
        
        checks.append({
            "name": "공시지가 일관성",
            "status": "✅ PASS" if price_match else "❌ FAIL",
            "details": {
                "appraisal": appraisal_price,
                "diagnosis": diagnosis_price
            }
        })
        
        # FAR Consistency
        appraisal_far = context.get("appraisal", {}).get("zoning", {}).get("far")
        capacity_far = context.get("capacity", {}).get("far")
        
        far_match = True
        if capacity_far and capacity_far != appraisal_far:
            far_match = False
        
        checks.append({
            "name": "용적률 일관성",
            "status": "✅ PASS" if far_match else "❌ FAIL",
            "details": {
                "appraisal": appraisal_far,
                "capacity": capacity_far
            }
        })
        
        # Overall
        all_passed = all(check["status"] == "✅ PASS" for check in checks)
        
        return {
            "status": "✅ ALL CONSISTENT" if all_passed else "❌ INCONSISTENT",
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
    
    
    @classmethod
    def protect_appraisal_data(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appraisal 데이터 보호
        
        Returns:
            Dict: 보호된 Context (appraisal은 deepcopy로 격리)
        """
        import copy
        
        protected_context = copy.deepcopy(context)
        
        # Appraisal 데이터에 보호 플래그 추가
        if "appraisal" in protected_context:
            protected_context["appraisal"]["_protected"] = True
            protected_context["appraisal"]["_lock_timestamp"] = datetime.now().isoformat()
        
        return protected_context
    
    
    @classmethod
    def get_protection_status(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Context 보호 상태 조회
        
        Returns:
            Dict: 보호 상태 정보
        """
        appraisal = context.get("appraisal", {})
        
        return {
            "protected": appraisal.get("_protected", False),
            "lock_timestamp": appraisal.get("_lock_timestamp"),
            "immutable_fields": cls.IMMUTABLE_FIELDS,
            "pipeline_status": {
                "appraisal": "appraisal" in context,
                "diagnosis": "diagnosis" in context,
                "capacity": "capacity" in context,
                "scenario": "scenario" in context,
                "lh_review": "lh_review" in context
            }
        }
    
    
    @classmethod
    def validate_context_structure(cls, context: Dict[str, Any]) -> List[str]:
        """
        Context 구조 검증
        
        Returns:
            List[str]: 경고/에러 메시지 목록 (빈 리스트면 정상)
        """
        issues = []
        
        # Required top-level fields
        required_top = ["context_id", "timestamp", "version"]
        for field in required_top:
            if field not in context:
                issues.append(f"필수 필드 누락: {field}")
        
        # Appraisal validation
        if "appraisal" in context:
            appraisal = context["appraisal"]
            for field in cls.REQUIRED_APPRAISAL_FIELDS:
                if field not in appraisal:
                    issues.append(f"감정평가 필수 필드 누락: {field}")
        
        return issues


# ============================================
# Helper Functions
# ============================================

def ensure_appraisal_first(context: Dict[str, Any]) -> None:
    """
    감정평가 우선 실행 보장
    
    모든 후속 엔진에서 호출해야 함
    """
    ContextProtector.validate_appraisal_complete(context)


def check_pipeline_dependency(context: Dict[str, Any], module_name: str) -> None:
    """
    파이프라인 의존성 체크
    
    Args:
        context: Context 객체
        module_name: 모듈명 (diagnosis, capacity, scenario, lh_review)
    """
    ContextProtector.validate_pipeline_order(context, module_name)


def get_appraisal_readonly(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Appraisal 데이터 읽기 전용 조회
    
    Returns:
        Dict: Appraisal 데이터 (복사본)
    """
    import copy
    
    if "appraisal" not in context:
        raise HTTPException(
            status_code=400,
            detail="❌ Appraisal 데이터가 없습니다."
        )
    
    return copy.deepcopy(context["appraisal"])
