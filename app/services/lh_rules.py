"""
LH 신축매입임대 기준 버전 관리 서비스
- JSON 파일 기반 LH 규칙 로딩
- 버전별 캐싱 (메모리 최적화)
- 검증 및 fallback 로직
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LHRulesLoader:
    """LH 기준 규칙 로더 (Singleton 패턴)"""
    
    _instance: Optional['LHRulesLoader'] = None
    _rules_cache: Dict[str, Dict[str, Any]] = {}
    _data_dir = Path(__file__).parent.parent.parent / "data"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """초기화 (최초 1회만 실행)"""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("LH Rules Loader 초기화")
    
    def load_rules(self, version: str = "2024") -> Dict[str, Any]:
        """
        특정 버전의 LH 규칙 로드 (캐싱 적용)
        
        Args:
            version: LH 규칙 버전 ("2024", "2025", "2026")
            
        Returns:
            LH 규칙 딕셔너리
            
        Raises:
            FileNotFoundError: 해당 버전 파일이 없는 경우
            ValueError: JSON 형식이 잘못된 경우
        """
        # 캐시 확인
        if version in self._rules_cache:
            logger.debug(f"LH 규칙 캐시 히트: {version}")
            return self._rules_cache[version]
        
        # JSON 파일 경로
        rules_file = self._data_dir / f"lh_rules_{version}.json"
        
        if not rules_file.exists():
            logger.error(f"LH 규칙 파일 없음: {rules_file}")
            # Fallback to 2024
            if version != "2024":
                logger.warning(f"버전 {version} 파일 없음. 2024 기본 버전으로 fallback")
                return self.load_rules("2024")
            raise FileNotFoundError(f"LH 규칙 파일을 찾을 수 없습니다: {rules_file}")
        
        # JSON 파일 로드
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            # 기본 검증
            self._validate_rules(rules, version)
            
            # 캐시 저장
            self._rules_cache[version] = rules
            logger.info(f"LH 규칙 로드 완료: {version} ({rules_file})")
            
            return rules
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {rules_file} - {e}")
            raise ValueError(f"JSON 형식 오류: {e}")
        except Exception as e:
            logger.error(f"LH 규칙 로드 실패: {e}")
            raise
    
    def _validate_rules(self, rules: Dict[str, Any], version: str) -> None:
        """
        LH 규칙 유효성 검증
        
        Args:
            rules: 검증할 규칙 딕셔너리
            version: 버전 정보
            
        Raises:
            ValueError: 필수 키가 없거나 형식이 잘못된 경우
        """
        required_keys = [
            "version",
            "effective_date",
            "housing_types",
            "checklist_criteria",
            "grade_thresholds",
            "category_weights"
        ]
        
        for key in required_keys:
            if key not in rules:
                raise ValueError(f"LH 규칙 검증 실패: '{key}' 키 누락 (version: {version})")
        
        # 버전 일치 확인
        if rules.get("version") != version:
            logger.warning(
                f"버전 불일치: 파일명 '{version}' vs JSON 내용 '{rules.get('version')}'"
            )
        
        # 주거 유형 확인
        if not rules.get("housing_types"):
            raise ValueError(f"housing_types가 비어있습니다 (version: {version})")
        
        # 체크리스트 카테고리 확인
        checklist = rules.get("checklist_criteria", {})
        required_categories = ["location", "scale", "business", "regulation"]
        for category in required_categories:
            if category not in checklist:
                raise ValueError(
                    f"체크리스트 카테고리 '{category}' 누락 (version: {version})"
                )
    
    def get_housing_type_info(
        self,
        unit_type: str,
        version: str = "2024"
    ) -> Optional[Dict[str, Any]]:
        """
        특정 주거 유형의 정보 조회
        
        Args:
            unit_type: 주거 유형 (예: "청년", "신혼·신생아 I")
            version: LH 규칙 버전
            
        Returns:
            주거 유형 정보 딕셔너리 또는 None
        """
        rules = self.load_rules(version)
        housing_types = rules.get("housing_types", {})
        
        # 정확한 매칭
        if unit_type in housing_types:
            return housing_types[unit_type]
        
        # 유사 매칭 (청년형 → 청년)
        for key in housing_types.keys():
            if unit_type.replace("형", "") == key or key.replace("형", "") == unit_type:
                logger.debug(f"유형 매칭: '{unit_type}' -> '{key}'")
                return housing_types[key]
        
        logger.warning(f"주거 유형 '{unit_type}'을 찾을 수 없습니다 (version: {version})")
        return None
    
    def get_checklist_criteria(
        self,
        category: str,
        version: str = "2024"
    ) -> list:
        """
        특정 카테고리의 체크리스트 기준 조회
        
        Args:
            category: 카테고리 ("location", "scale", "business", "regulation")
            version: LH 규칙 버전
            
        Returns:
            체크리스트 항목 리스트
        """
        rules = self.load_rules(version)
        checklist = rules.get("checklist_criteria", {})
        return checklist.get(category, [])
    
    def get_grade_thresholds(self, version: str = "2024") -> Dict[str, float]:
        """
        등급 기준 점수 조회
        
        Args:
            version: LH 규칙 버전
            
        Returns:
            등급 기준 점수 딕셔너리 (예: {"A": 80, "B": 60, "C": 0})
        """
        rules = self.load_rules(version)
        return rules.get("grade_thresholds", {"A": 80, "B": 60, "C": 0})
    
    def get_category_weights(self, version: str = "2024") -> Dict[str, float]:
        """
        카테고리별 가중치 조회
        
        Args:
            version: LH 규칙 버전
            
        Returns:
            카테고리 가중치 딕셔너리 (예: {"입지": 30, "규모": 25, ...})
        """
        rules = self.load_rules(version)
        return rules.get("category_weights", {"입지": 30, "규모": 25, "사업성": 30, "법규": 15})
    
    def get_messages(self, version: str = "2024") -> Dict[str, str]:
        """
        버전별 메시지 조회
        
        Args:
            version: LH 규칙 버전
            
        Returns:
            메시지 딕셔너리
        """
        rules = self.load_rules(version)
        return rules.get("messages", {})
    
    def list_available_versions(self) -> list:
        """
        사용 가능한 LH 규칙 버전 목록 조회
        
        Returns:
            버전 리스트 (예: ["2024", "2025", "2026"])
        """
        versions = []
        
        if not self._data_dir.exists():
            logger.warning(f"Data 디렉토리 없음: {self._data_dir}")
            return versions
        
        for file_path in self._data_dir.glob("lh_rules_*.json"):
            # 파일명에서 버전 추출 (lh_rules_2024.json -> 2024)
            version = file_path.stem.replace("lh_rules_", "")
            versions.append(version)
        
        versions.sort()
        logger.info(f"사용 가능한 LH 규칙 버전: {versions}")
        return versions
    
    def clear_cache(self, version: Optional[str] = None) -> None:
        """
        캐시 초기화
        
        Args:
            version: 특정 버전만 초기화 (None이면 전체 초기화)
        """
        if version:
            if version in self._rules_cache:
                del self._rules_cache[version]
                logger.info(f"LH 규칙 캐시 초기화: {version}")
        else:
            self._rules_cache.clear()
            logger.info("LH 규칙 캐시 전체 초기화")
    
    def reload_rules(self, version: str) -> Dict[str, Any]:
        """
        특정 버전의 규칙 강제 재로드 (캐시 무시)
        
        Args:
            version: LH 규칙 버전
            
        Returns:
            새로 로드된 LH 규칙 딕셔너리
        """
        self.clear_cache(version)
        return self.load_rules(version)


# Singleton 인스턴스 (전역 사용)
_lh_rules_loader = LHRulesLoader()


# 편의 함수들
def get_lh_rules(version: str = "2024") -> Dict[str, Any]:
    """LH 규칙 조회 (전역 함수)"""
    return _lh_rules_loader.load_rules(version)


def get_housing_type_info(unit_type: str, version: str = "2024") -> Optional[Dict[str, Any]]:
    """주거 유형 정보 조회 (전역 함수)"""
    return _lh_rules_loader.get_housing_type_info(unit_type, version)


def get_checklist_criteria(category: str, version: str = "2024") -> list:
    """체크리스트 기준 조회 (전역 함수)"""
    return _lh_rules_loader.get_checklist_criteria(category, version)


def get_grade_thresholds(version: str = "2024") -> Dict[str, float]:
    """등급 기준 점수 조회 (전역 함수)"""
    return _lh_rules_loader.get_grade_thresholds(version)


def get_category_weights(version: str = "2024") -> Dict[str, float]:
    """카테고리 가중치 조회 (전역 함수)"""
    return _lh_rules_loader.get_category_weights(version)


def list_available_versions() -> list:
    """사용 가능한 버전 목록 조회 (전역 함수)"""
    return _lh_rules_loader.list_available_versions()


def deep_merge_rules(base_version: str = "2024", target_version: str = "2025") -> Dict[str, Any]:
    """
    두 버전의 LH 규칙을 deep merge
    
    target_version의 값이 우선하되, 누락된 키는 base_version에서 가져옴
    
    Args:
        base_version: 기준 버전 (fallback 값 제공)
        target_version: 대상 버전 (우선 적용)
        
    Returns:
        병합된 LH 규칙 딕셔너리
    """
    base_rules = get_lh_rules(base_version)
    try:
        target_rules = get_lh_rules(target_version)
    except (FileNotFoundError, ValueError):
        logger.warning(f"버전 {target_version} 로드 실패. {base_version}만 사용")
        return base_rules
    
    def _deep_merge_dict(base: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
        """재귀적으로 딕셔너리 병합"""
        merged = base.copy()
        
        for key, target_value in target.items():
            if key in merged:
                base_value = merged[key]
                
                # 둘 다 딕셔너리면 재귀 병합
                if isinstance(base_value, dict) and isinstance(target_value, dict):
                    merged[key] = _deep_merge_dict(base_value, target_value)
                # 리스트는 target 우선
                elif isinstance(target_value, list):
                    merged[key] = target_value
                # 나머지는 target 값 덮어쓰기
                else:
                    merged[key] = target_value
            else:
                # 새로운 키는 그대로 추가
                merged[key] = target_value
        
        return merged
    
    merged_rules = _deep_merge_dict(base_rules, target_rules)
    logger.info(f"LH 규칙 deep merge 완료: {base_version} + {target_version}")
    
    return merged_rules
