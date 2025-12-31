"""
Data Integrity Guard for LH Reports
보고서 데이터 정합성 보호 시스템
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DataIntegrityGuard:
    """
    데이터 정합성 가드
    
    M2-M6 데이터가 변조되지 않았는지 검증
    """
    
    @staticmethod
    def calculate_data_hash(data: Dict[str, Any], keys: list) -> str:
        """
        특정 키들의 값으로 해시 생성
        
        Args:
            data: 데이터 딕셔너리
            keys: 해시 계산에 사용할 키 리스트
            
        Returns:
            MD5 해시 (짧은 형태)
        """
        values = []
        for key in keys:
            value = data.get(key)
            if value is not None:
                # 숫자는 문자열로 변환하여 일관성 유지
                values.append(str(value))
        
        # 값들을 정렬하여 순서 무관하게 만듦
        sorted_values = sorted(values)
        combined = "|".join(sorted_values)
        
        # MD5 해시 계산 (첫 8자만 사용)
        hash_value = hashlib.md5(combined.encode()).hexdigest()[:8]
        return hash_value
    
    @staticmethod
    def verify_m2_data(m2_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        M2 토지평가 데이터 검증
        
        Returns:
            (is_valid, hash_value)
        """
        if not m2_data:
            return False, None
        
        # M2 핵심 필드
        critical_keys = [
            "appraisal.land_value",
            "appraisal.unit_price_sqm",
            "appraisal.unit_price_pyeong"
        ]
        
        # 중첩 딕셔너리 처리
        flat_data = {}
        for key in critical_keys:
            parts = key.split(".")
            value = m2_data
            try:
                for part in parts:
                    value = value.get(part, {})
                flat_data[key] = value
            except (AttributeError, TypeError):
                flat_data[key] = None
        
        hash_value = DataIntegrityGuard.calculate_data_hash(flat_data, critical_keys)
        
        # 모든 중요 필드가 있는지 확인
        is_valid = all(flat_data.get(k) is not None for k in critical_keys)
        
        if not is_valid:
            logger.warning(f"M2 data validation failed. Hash: {hash_value}")
        else:
            logger.info(f"M2 data validated. Hash: {hash_value}")
        
        return is_valid, hash_value
    
    @staticmethod
    def verify_consistency(
        source_data: Dict[str, Any],
        target_data: Dict[str, Any],
        module: str
    ) -> tuple[bool, str]:
        """
        소스 데이터와 타겟 데이터 일관성 검증
        
        Args:
            source_data: 원본 데이터 (M2-M6)
            target_data: 대상 데이터 (LH 보고서 등)
            module: 모듈 이름 (M2, M3 등)
            
        Returns:
            (is_consistent, message)
        """
        # 모듈별 중요 필드 정의
        critical_fields_map = {
            "M2": ["appraisal.land_value", "appraisal.unit_price_sqm"],
            "M3": ["recommended_type", "total_score"],
            "M4": ["selected_scenario_id", "legal_capacity.total_units"],
            "M5": ["household_count", "costs.total"],
            "M6": ["lh_score", "decision"]
        }
        
        critical_fields = critical_fields_map.get(module, [])
        
        if not critical_fields:
            return True, f"{module}: No critical fields defined"
        
        # 필드별 비교
        mismatches = []
        for field in critical_fields:
            parts = field.split(".")
            
            # 소스에서 값 추출
            source_value = source_data
            try:
                for part in parts:
                    source_value = source_value.get(part, {})
            except (AttributeError, TypeError):
                source_value = None
            
            # 타겟에서 값 추출
            target_value = target_data
            try:
                for part in parts:
                    target_value = target_value.get(part, {})
            except (AttributeError, TypeError):
                target_value = None
            
            # 비교
            if source_value != target_value:
                mismatches.append(f"{field}: {source_value} != {target_value}")
        
        if mismatches:
            message = f"DATA_INTEGRITY_VIOLATION\\nSOURCE: {module}\\nMISMATCHES:\\n" + "\\n".join(mismatches)
            logger.error(message)
            return False, message
        
        message = f"{module}: All fields consistent"
        logger.info(message)
        return True, message
    
    @staticmethod
    def generate_report_fingerprint(
        address: str,
        pnu: str,
        run_id: str,
        m2_data: Dict[str, Any]
    ) -> str:
        """
        보고서 고유 지문 생성
        
        이 지문은 동일한 입력에 대해 항상 동일한 값을 반환해야 함
        """
        components = [
            address,
            pnu,
            run_id,
            str(m2_data.get("appraisal", {}).get("land_value", "")),
            str(m2_data.get("appraisal", {}).get("unit_price_sqm", ""))
        ]
        
        combined = "|".join(components)
        fingerprint = hashlib.sha256(combined.encode()).hexdigest()[:16]
        
        logger.info(f"Report fingerprint generated: {fingerprint}")
        return fingerprint


# 전역 인스턴스
data_integrity_guard = DataIntegrityGuard()
