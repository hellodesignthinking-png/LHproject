"""
ZeroSite v9.0 - Demand Engine
==============================

수요 분석 엔진 v9.0
인구 통계 기반 주택 수요 예측

주요 기능:
1. 인구 통계 분석
2. 가구수 예측
3. 타겟 가구 산출
4. 수요 점수 계산 (0-100)
5. 추천 주택 유형

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

from typing import Optional
from dataclasses import dataclass
import logging

from app.models_v9.standard_schema_v9_0 import (
    DemandResult
)

logger = logging.getLogger(__name__)


class DemandEngineV90:
    """
    Demand Engine v9.0
    
    인구 통계 기반 주택 수요 분석
    """
    
    # 수요 등급 기준
    DEMAND_GRADE_THRESHOLDS = {
        80: "매우 높음",
        60: "높음",
        40: "보통",
        20: "낮음",
        0: "매우 낮음"
    }
    
    # 주택 유형별 추천 기준
    UNIT_TYPE_RECOMMENDATION = {
        "원룸": {"min_target": 0, "max_target": 1000, "avg_household_size": 1.0},
        "투룸": {"min_target": 500, "max_target": 2000, "avg_household_size": 1.5},
        "쓰리룸": {"min_target": 1000, "max_target": 5000, "avg_household_size": 2.5},
        "패밀리": {"min_target": 2000, "max_target": 10000, "avg_household_size": 3.5}
    }
    
    def __init__(self):
        """Demand Engine 초기화"""
        logger.info("📊 Demand Engine v9.0 초기화 완료")
    
    def analyze_demand(
        self,
        address: str,
        unit_count: int,
        lh_total_score: float
    ) -> DemandResult:
        """
        수요 분석 수행 (간이 버전)
        
        실제로는 인구 통계 API를 호출하지만,
        현재는 LH 점수 기반 추정
        
        Args:
            address: 주소
            unit_count: 계획 세대수
            lh_total_score: LH 평가 총점
            
        Returns:
            DemandResult
        """
        logger.info(f"📊 수요 분석 시작: {address}")
        
        # 1. 인구/가구수 추정 (간이 공식)
        # 실제로는 통계청 API 호출 필요
        population_total = self._estimate_population(address)
        household_count = int(population_total / 2.3)  # 평균 가구원수 2.3명
        
        # 2. 타겟 가구수 추정
        # LH 점수가 높을수록 수요 높음
        demand_factor = lh_total_score / 110  # 0~1
        target_households = int(household_count * 0.1 * demand_factor)  # 전체 가구의 최대 10%
        
        # 3. 수요 점수 계산 (0-100)
        demand_score = self._calculate_demand_score(
            unit_count=unit_count,
            target_households=target_households,
            lh_score=lh_total_score
        )
        
        # 4. 수요 등급
        demand_grade = self._score_to_grade(demand_score)
        
        # 5. 추천 주택 유형
        recommended_type = self._recommend_unit_type(target_households)
        
        logger.info(f"✅ 수요 분석 완료: 점수 {demand_score:.1f}/100, 등급 {demand_grade}")
        
        return DemandResult(
            population_total=population_total,
            household_count=household_count,
            target_households=target_households,
            demand_score=round(demand_score, 1),
            demand_grade=demand_grade,
            recommended_unit_type=recommended_type
        )
    
    def _estimate_population(self, address: str) -> int:
        """
        주소 기반 인구 추정 (간이 버전)
        
        실제로는 통계청 API 호출 필요
        
        Args:
            address: 주소
            
        Returns:
            int: 추정 인구
        """
        # 간이 추정: 주소에서 지역 판단
        if "서울" in address:
            return 50000  # 서울 평균 동 인구
        elif any(city in address for city in ["경기", "인천"]):
            return 40000
        elif any(city in address for city in ["부산", "대구", "대전", "광주"]):
            return 35000
        else:
            return 25000
    
    def _calculate_demand_score(
        self,
        unit_count: int,
        target_households: int,
        lh_score: float
    ) -> float:
        """
        수요 점수 계산 (0-100)
        
        Args:
            unit_count: 계획 세대수
            target_households: 타겟 가구수
            lh_score: LH 평가 점수
            
        Returns:
            float (0-100)
        """
        # 1. 공급/수요 비율 (50점)
        if target_households > 0:
            supply_demand_ratio = unit_count / target_households
            
            # 0.3~0.5가 최적 (공급 과다/부족 방지)
            if 0.3 <= supply_demand_ratio <= 0.5:
                supply_score = 50
            elif 0.2 <= supply_demand_ratio < 0.3:
                supply_score = 40
            elif 0.5 < supply_demand_ratio <= 0.7:
                supply_score = 40
            else:
                supply_score = 20
        else:
            supply_score = 0
        
        # 2. LH 점수 기반 (50점)
        lh_factor = (lh_score / 110) * 50
        
        # 3. 총점
        total_score = supply_score + lh_factor
        
        return min(100, max(0, total_score))
    
    def _score_to_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        for threshold, grade in sorted(self.DEMAND_GRADE_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return grade
        return "매우 낮음"
    
    def _recommend_unit_type(self, target_households: int) -> str:
        """
        타겟 가구수 기반 추천 주택 유형
        
        Args:
            target_households: 타겟 가구수
            
        Returns:
            str: 추천 주택 유형
        """
        for unit_type, criteria in self.UNIT_TYPE_RECOMMENDATION.items():
            if criteria["min_target"] <= target_households <= criteria["max_target"]:
                return unit_type
        
        return "쓰리룸"  # 기본값
