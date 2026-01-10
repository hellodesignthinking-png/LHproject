"""
Phase 8: CapacityContextV2 Adapter
===================================

CapacityContextV2를 기존 코드가 기대하는 형식으로 변환하는 어댑터

작성일: 2026-01-11
"""

from typing import Any
import logging

logger = logging.getLogger(__name__)


class CapacityAdapter:
    """CapacityContextV2를 기존 구조로 변환하는 어댑터"""
    
    def __init__(self, capacity_v2: Any):
        """
        Args:
            capacity_v2: CapacityContextV2 객체
        """
        self.v2 = capacity_v2
        
        # 법정 규모
        self.legal_far = capacity_v2.legal_capacity.applied_far
        self.legal_bcr = capacity_v2.legal_capacity.applied_bcr
        self.legal_units = capacity_v2.legal_capacity.total_units
        self.legal_gfa = capacity_v2.legal_capacity.target_gfa_sqm
        
        # 인센티브 규모
        self.incentive_far = capacity_v2.incentive_capacity.applied_far
        self.incentive_bcr = capacity_v2.incentive_capacity.applied_bcr
        self.final_units = capacity_v2.incentive_capacity.total_units
        self.final_gfa = capacity_v2.incentive_capacity.target_gfa_sqm
        
        # 세대 구성
        self.unit_summary = capacity_v2.unit_summary
        
        # 주차 해결안 (Dict)
        self.parking_solutions = capacity_v2.parking_solutions
        
        # 매싱 옵션
        self.massing_options = capacity_v2.massing_options
    
    def get_parking_solution(self, solution_type: str = "alternative_B") -> Any:
        """주차 해결안 가져오기"""
        return self.parking_solutions.get(solution_type)


def adapt_capacity_context(capacity_ctx: Any) -> CapacityAdapter:
    """
    CapacityContextV2를 CapacityAdapter로 변환
    
    Args:
        capacity_ctx: CapacityContextV2 객체
        
    Returns:
        CapacityAdapter
    """
    try:
        return CapacityAdapter(capacity_ctx)
    except Exception as e:
        logger.error(f"Failed to adapt capacity context: {e}")
        raise
