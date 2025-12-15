"""
ZeroSite Canonical Flow - Appraisal Context Lock
감정평가 결과를 Single Source of Truth로 확립하는 컨텍스트 관리 시스템

Version: v8.7+
Date: 2025-12-03
"""

from typing import Any, Dict, Optional
from copy import deepcopy
from datetime import datetime
import json


class AppraisalContextLock:
    """
    감정평가 결과 잠금 메커니즘
    
    핵심 원칙:
    1. 한 번 잠기면 수정 불가
    2. 이후 모든 엔진은 읽기만 가능
    3. 감정평가 로직 자체는 절대 수정 금지
    
    Usage:
        # 1. 감정평가 실행
        appraisal_result = run_appraisal_engine(parcel)
        
        # 2. 컨텍스트 잠금
        ctx = AppraisalContextLock()
        ctx.lock(appraisal_result)
        
        # 3. 후속 엔진에서 읽기만
        zoning = ctx.get('zoning.confirmed_type')
        land_value = ctx.get('calculation.final_appraised_total')
    """
    
    def __init__(self):
        object.__setattr__(self, '_locked', False)
        object.__setattr__(self, '_appraisal_data', None)
        object.__setattr__(self, '_locked_at', None)
        object.__setattr__(self, '_hash_signature', None)
        object.__setattr__(self, '_allow_init', True)
    
    def lock(self, appraisal_result: Dict) -> None:
        """
        감정평가 결과를 잠그고 이후 수정 불가능하게 만듦
        
        Args:
            appraisal_result: 감정평가 엔진의 출력 (Canonical Schema 준수)
        
        Raises:
            ValueError: 이미 잠긴 경우 또는 유효하지 않은 데이터
        """
        if self._locked:
            raise ValueError(
                "❌ Appraisal context already locked! "
                f"Locked at: {self._locked_at}"
            )
        
        # Validate required fields
        required_fields = ['calculation', 'zoning', 'confidence']
        for field in required_fields:
            if field not in appraisal_result:
                raise ValueError(
                    f"❌ Invalid appraisal result: missing required field '{field}'"
                )
        
        # Lock the data
        object.__setattr__(self, '_appraisal_data', deepcopy(appraisal_result))
        self._appraisal_data['locked'] = True
        locked_time = datetime.now().isoformat()
        object.__setattr__(self, '_locked_at', locked_time)
        self._appraisal_data['locked_at'] = locked_time
        
        # Calculate hash signature
        hash_sig = self._calculate_hash_signature()
        object.__setattr__(self, '_hash_signature', hash_sig)
        self._appraisal_data['hash_signature'] = hash_sig
        
        # Lock the object (prevent further modifications)
        object.__setattr__(self, '_locked', True)
        object.__setattr__(self, '_allow_init', False)
        
        # Log lock event
        final_value = self._appraisal_data.get('calculation', {}).get('final_appraised_total', 0)
        print(f"🔒 Appraisal context LOCKED")
        print(f"   Locked at: {self._locked_at}")
        print(f"   Final appraised value: {final_value:,.0f}원")
        print(f"   Version: {self._appraisal_data.get('metadata', {}).get('appraisal_engine', 'N/A')}")
        print(f"   ⚠️  This data is now READ-ONLY for all subsequent engines")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        잠긴 감정평가 데이터 읽기 (수정 불가)
        
        Args:
            key_path: Dot-notation path (e.g., "zoning.confirmed_type")
            default: Default value if key not found
        
        Returns:
            Value at the key path (deep copy to prevent modification)
        
        Raises:
            ValueError: Context not yet locked
        
        Example:
            >>> ctx.get('calculation.final_appraised_total')
            3662410000
            >>> ctx.get('premium.total_premium_rate')
            0.16
        """
        if not self._locked:
            raise ValueError(
                "❌ Appraisal context not yet locked! "
                "Call lock() before accessing data."
            )
        
        keys = key_path.split('.')
        data = self._appraisal_data
        
        try:
            for key in keys:
                data = data[key]
            
            # Return deep copy to prevent external modification
            if isinstance(data, (dict, list)):
                return deepcopy(data)
            return data
            
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise KeyError(
                f"❌ Key not found in appraisal context: '{key_path}'"
            )
    
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Prevent attribute modification after locking
        
        Raises:
            RuntimeError: If attempting to modify locked context
        """
        if hasattr(self, '_locked') and self._locked and not self._allow_init:
            raise RuntimeError(
                f"❌ IMMUTABILITY VIOLATION: Cannot modify AppraisalContextLock after locking!\n"
                f"   Attempted to set: {name} = {value}\n"
                f"   Context was locked at: {self._locked_at}\n"
                f"   Hash signature: {self._hash_signature}\n"
                f"   ⚠️  Appraisal values are IMMUTABLE by design."
            )
        object.__setattr__(self, name, value)
    
    def _calculate_hash_signature(self) -> str:
        """
        Calculate cryptographic hash of critical appraisal data
        
        Returns:
            SHA-256 hash (first 16 chars) of critical fields
        """
        import hashlib
        
        critical_fields = {
            'final_appraised_total': self._appraisal_data.get('calculation', {}).get('final_appraised_total'),
            'premium_rate': self._appraisal_data.get('premium', {}).get('total_premium_rate'),
            'land_area': self._appraisal_data.get('calculation', {}).get('land_area_sqm'),
            'zoning': self._appraisal_data.get('zoning', {}).get('confirmed_type'),
            'locked_at': self._locked_at
        }
        
        # Sort to ensure consistent hashing
        data_str = json.dumps(critical_fields, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def get_hash_signature(self) -> Optional[str]:
        """Get the hash signature of locked context"""
        return self._hash_signature
    
    def verify_hash(self) -> bool:
        """
        Verify that context hash hasn't changed
        
        Returns:
            True if hash is valid, False otherwise
        """
        if not self._locked:
            return False
        
        current_hash = self._calculate_hash_signature()
        return current_hash == self._hash_signature
    
    def is_locked(self) -> bool:
        """감정평가 컨텍스트가 잠겼는지 확인"""
        return self._locked
    
    def get_locked_at(self) -> Optional[str]:
        """잠금 시간 반환"""
        return self._locked_at
    
    def get_full_context(self) -> Dict:
        """
        전체 감정평가 컨텍스트 반환 (읽기 전용)
        
        Returns:
            전체 데이터의 deep copy (수정 방지)
        
        Raises:
            ValueError: Context not yet locked
        """
        if not self._locked:
            raise ValueError(
                "❌ Appraisal context not yet locked! "
                "Call lock() before accessing data."
            )
        
        return deepcopy(self._appraisal_data)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        감정평가 요약 정보 반환
        
        Returns:
            핵심 정보만 담은 요약 딕셔너리
        """
        if not self._locked:
            return {
                'locked': False,
                'message': 'Context not yet locked'
            }
        
        return {
            'locked': True,
            'locked_at': self._locked_at,
            'final_appraised_total': self.get('calculation.final_appraised_total', 0),
            'zoning': self.get('zoning.confirmed_type', 'N/A'),
            'premium_rate': self.get('premium.total_premium_rate', 0),
            'confidence_score': self.get('confidence.score', 0),
            'appraisal_engine': self.get('metadata.appraisal_engine', 'N/A'),
            'transaction_cases_count': len(self.get('transaction_cases', []))
        }
    
    def validate_integrity(self) -> bool:
        """
        데이터 무결성 검증
        
        Returns:
            True if data is valid and consistent
        """
        if not self._locked:
            return False
        
        try:
            # Check required fields exist
            _ = self.get('calculation.final_appraised_total')
            _ = self.get('zoning.confirmed_type')
            _ = self.get('confidence.score')
            
            # Check locked flag
            if not self._appraisal_data.get('locked'):
                return False
            
            # Check confidence is reasonable (0-1)
            confidence = self.get('confidence.score')
            if not (0 <= confidence <= 1):
                return False
            
            return True
            
        except (KeyError, TypeError):
            return False
    
    def to_json(self, indent: int = 2) -> str:
        """
        JSON 문자열로 변환
        
        Args:
            indent: JSON indentation level
        
        Returns:
            JSON string of full context
        """
        if not self._locked:
            return json.dumps({'locked': False}, indent=indent, ensure_ascii=False)
        
        return json.dumps(self._appraisal_data, indent=indent, ensure_ascii=False)
    
    def __repr__(self) -> str:
        if not self._locked:
            return "<AppraisalContextLock: UNLOCKED>"
        
        summary = self.get_summary()
        return (
            f"<AppraisalContextLock: LOCKED at {self._locked_at}, "
            f"value={summary['final_appraised_total']:,.0f}원, "
            f"confidence={summary['confidence_score']:.2f}>"
        )


# Singleton instance for global use (optional)
_global_appraisal_context: Optional[AppraisalContextLock] = None


def get_global_appraisal_context() -> AppraisalContextLock:
    """
    전역 감정평가 컨텍스트 반환 (싱글톤 패턴)
    
    Returns:
        Global AppraisalContextLock instance
    """
    global _global_appraisal_context
    if _global_appraisal_context is None:
        _global_appraisal_context = AppraisalContextLock()
    return _global_appraisal_context


def reset_global_context() -> None:
    """전역 컨텍스트 리셋 (테스트용)"""
    global _global_appraisal_context
    _global_appraisal_context = None
