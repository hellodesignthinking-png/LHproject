"""
ZeroSite v9.0 - LH Evaluation Engine
=====================================

LH 신축매입임대 공식 평가 엔진 v9.0
110점 만점 체계 완전 구현

평가 구성:
1. 입지 평가 (35점)
2. 사업 규모 (20점)
3. 사업성 평가 (40점)
4. 법규 적합성 (15점)

총점: 110점
등급: S (90+), A (80+), B (70+), C (60+), D (50+), F (<50)

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

from app.models_v9.standard_schema_v9_0 import (
    LHScores,
    ProjectGrade,
    GISResult,
    FinancialResult,
    SiteInfo
)

logger = logging.getLogger(__name__)


class LHEvaluationEngineV90:
    """
    LH Evaluation Engine v9.0
    
    LH 신축매입임대 공식 평가 기준(110점 체계) 완전 구현
    """
    
    # LH 공식 기준 (2025년)
    LOCATION_CRITERIA = {
        "subway": {
            "weight": 15,
            "thresholds": [
                (500, 15),    # ≤500m = 15점
                (1000, 12),   # ≤1km = 12점
                (2000, 8),    # ≤2km = 8점
                (3000, 4),    # ≤3km = 4점
                (999999, 0)   # >3km = 0점
            ]
        },
        "school": {
            "weight": 10,
            "thresholds": [
                (500, 10),
                (1000, 7),
                (1500, 4),
                (999999, 0)
            ]
        },
        "hospital": {
            "weight": 5,
            "thresholds": [
                (1000, 5),
                (2000, 3),
                (3000, 1),
                (999999, 0)
            ]
        },
        "commercial": {
            "weight": 5,
            "thresholds": [
                (500, 5),
                (1000, 3),
                (2000, 1),
                (999999, 0)
            ]
        }
    }
    
    SCALE_CRITERIA = {
        "unit_count": {
            "weight": 15,
            "thresholds": [
                (100, 15),  # ≥100세대 = 15점
                (70, 12),   # ≥70세대 = 12점
                (50, 10),   # ≥50세대 = 10점
                (30, 7),    # ≥30세대 = 7점
                (20, 4),    # ≥20세대 = 4점
                (10, 2),    # ≥10세대 = 2점
                (0, 0)      # <10세대 = 0점
            ]
        },
        "site_area": {
            "weight": 5,
            "thresholds": [
                (3000, 5),  # ≥3000㎡ = 5점
                (2000, 4),
                (1500, 3),
                (1000, 2),
                (500, 1),
                (0, 0)
            ]
        }
    }
    
    BUSINESS_CRITERIA = {
        "roi": {
            "weight": 20,
            "thresholds": [
                (10, 20),   # ROI ≥10% = 20점
                (8, 17),
                (6, 14),
                (4, 10),
                (2, 5),
                (0, 2),
                (-999, 0)
            ]
        },
        "cap_rate": {
            "weight": 10,
            "thresholds": [
                (6, 10),    # Cap Rate ≥6% = 10점
                (5, 8),
                (4.5, 6),
                (4, 4),
                (3, 2),
                (0, 0)
            ]
        },
        "irr": {
            "weight": 10,
            "thresholds": [
                (12, 10),   # IRR ≥12% = 10점
                (10, 8),
                (8, 6),
                (6, 4),
                (4, 2),
                (0, 0)
            ]
        }
    }
    
    REGULATION_CRITERIA = {
        "zoning": {
            "weight": 10,
            "categories": {
                "제3종일반주거지역": 10,
                "제2종일반주거지역": 9,
                "제1종일반주거지역": 7,
                "준주거지역": 8,
                "상업지역": 6,
                "준공업지역": 5,
                "기타": 3
            }
        },
        "compliance": {
            "weight": 5
        }
    }
    
    # 등급 기준
    GRADE_THRESHOLDS = {
        90: ProjectGrade.S,
        80: ProjectGrade.A,
        70: ProjectGrade.B,
        60: ProjectGrade.C,
        50: ProjectGrade.D,
        0: ProjectGrade.F
    }
    
    def __init__(self):
        """LH Evaluation Engine 초기화"""
        logger.info("🏆 LH Evaluation Engine v9.0 초기화 완료")
        logger.info("   ✓ 110점 공식 기준 로드")
        logger.info("   ✓ 등급 시스템: S (90+), A (80+), B (70+), C (60+), D (50+), F (<50)")
    
    def evaluate_comprehensive(
        self,
        site_info: SiteInfo,
        gis_result: GISResult,
        financial_result: FinancialResult
    ) -> LHScores:
        """
        종합 LH 평가 수행
        
        Args:
            site_info: 토지 기본 정보
            gis_result: GIS 분석 결과
            financial_result: 재무 분석 결과
            
        Returns:
            LHScores (110점 만점 체계)
        """
        logger.info("🏆 LH 평가 시작 (110점 만점)")
        
        # 1. 입지 평가 (35점)
        location_score = self._evaluate_location(gis_result)
        logger.info(f"  📍 입지 점수: {location_score:.1f}/35점")
        
        # 2. 규모 평가 (20점)
        scale_score = self._evaluate_scale(
            unit_count=financial_result.unit_count,
            land_area=site_info.land_area
        )
        logger.info(f"  📏 규모 점수: {scale_score:.1f}/20점")
        
        # 3. 사업성 평가 (40점)
        business_score = self._evaluate_business(financial_result)
        logger.info(f"  💰 사업성 점수: {business_score:.1f}/40점")
        
        # 4. 법규 평가 (15점)
        regulation_score = self._evaluate_regulations(site_info)
        logger.info(f"  📋 법규 점수: {regulation_score:.1f}/15점")
        
        # 5. 총점 계산
        total_score = location_score + scale_score + business_score + regulation_score
        
        # 6. 등급 산출
        grade = self._score_to_grade(total_score)
        
        logger.info(f"✅ LH 평가 완료: {total_score:.1f}/110점 (등급: {grade.value})")
        
        return LHScores(
            location_score=round(location_score, 1),
            scale_score=round(scale_score, 1),
            business_score=round(business_score, 1),
            regulation_score=round(regulation_score, 1),
            total_score=round(total_score, 1),
            grade=grade
        )
    
    def _evaluate_location(self, gis_result: GISResult) -> float:
        """
        입지 평가 (35점 만점)
        
        세부 항목:
        - 지하철 접근성 (15점)
        - 학교 접근성 (10점)
        - 의료시설 접근성 (5점)
        - 상업시설 접근성 (5점)
        
        Args:
            gis_result: GIS 분석 결과
            
        Returns:
            float (0-35)
        """
        total = 0.0
        
        # 1. 지하철 접근성 (15점)
        if gis_result.subway_stations:
            nearest_subway = gis_result.subway_stations[0].distance_m
            subway_score = self._score_by_threshold(
                nearest_subway,
                self.LOCATION_CRITERIA["subway"]["thresholds"]
            )
            total += subway_score
        
        # 2. 학교 접근성 (10점) - 초등학교 우선
        if gis_result.elementary_schools:
            nearest_school = gis_result.elementary_schools[0].distance_m
            school_score = self._score_by_threshold(
                nearest_school,
                self.LOCATION_CRITERIA["school"]["thresholds"]
            )
            total += school_score
        
        # 3. 의료시설 접근성 (5점)
        if gis_result.hospitals:
            nearest_hospital = gis_result.hospitals[0].distance_m
            hospital_score = self._score_by_threshold(
                nearest_hospital,
                self.LOCATION_CRITERIA["hospital"]["thresholds"]
            )
            total += hospital_score
        
        # 4. 상업시설 접근성 (5점) - 대형마트 우선
        if gis_result.supermarkets:
            nearest_commercial = gis_result.supermarkets[0].distance_m
            commercial_score = self._score_by_threshold(
                nearest_commercial,
                self.LOCATION_CRITERIA["commercial"]["thresholds"]
            )
            total += commercial_score
        
        return min(35.0, total)
    
    def _evaluate_scale(self, unit_count: int, land_area: float) -> float:
        """
        규모 평가 (20점 만점)
        
        세부 항목:
        - 세대수 (15점)
        - 대지 면적 (5점)
        
        Args:
            unit_count: 세대수
            land_area: 대지 면적 (m²)
            
        Returns:
            float (0-20)
        """
        total = 0.0
        
        # 1. 세대수 점수 (15점) - 역방향 (값이 클수록 높은 점수)
        unit_score = self._score_by_threshold_reverse(
            unit_count,
            self.SCALE_CRITERIA["unit_count"]["thresholds"]
        )
        total += unit_score
        
        # 2. 대지 면적 점수 (5점) - 역방향
        area_score = self._score_by_threshold_reverse(
            land_area,
            self.SCALE_CRITERIA["site_area"]["thresholds"]
        )
        total += area_score
        
        return min(20.0, total)
    
    def _evaluate_business(self, financial_result: FinancialResult) -> float:
        """
        사업성 평가 (40점 만점)
        
        세부 항목:
        - ROI (20점)
        - Cap Rate (10점)
        - IRR (10점)
        
        Args:
            financial_result: 재무 분석 결과
            
        Returns:
            float (0-40)
        """
        total = 0.0
        
        # 1. ROI 점수 (20점)
        roi_score = self._score_by_threshold_reverse(
            financial_result.roi_10yr,
            self.BUSINESS_CRITERIA["roi"]["thresholds"]
        )
        total += roi_score
        
        # 2. Cap Rate 점수 (10점)
        cap_score = self._score_by_threshold_reverse(
            financial_result.cap_rate,
            self.BUSINESS_CRITERIA["cap_rate"]["thresholds"]
        )
        total += cap_score
        
        # 3. IRR 점수 (10점)
        irr_score = self._score_by_threshold_reverse(
            financial_result.irr_10yr,
            self.BUSINESS_CRITERIA["irr"]["thresholds"]
        )
        total += irr_score
        
        return min(40.0, total)
    
    def _evaluate_regulations(self, site_info: SiteInfo) -> float:
        """
        법규 평가 (15점 만점)
        
        세부 항목:
        - 용도지역 적합성 (10점)
        - 법규 준수 (5점)
        
        Args:
            site_info: 토지 기본 정보
            
        Returns:
            float (0-15)
        """
        total = 0.0
        
        # 1. 용도지역 점수 (10점)
        zone_type = site_info.zone_type
        zoning_categories = self.REGULATION_CRITERIA["zoning"]["categories"]
        
        zoning_score = zoning_categories.get(zone_type, zoning_categories["기타"])
        total += zoning_score
        
        # 2. 법규 준수 점수 (5점)
        # 건폐율/용적률 준수 여부
        compliance_score = 5.0  # 기본값 (법규 위반 없음 가정)
        
        # 건폐율 초과 확인
        if site_info.building_coverage_ratio > 80:  # 80% 초과는 위험
            compliance_score -= 2.0
        
        # 용적률 초과 확인
        if site_info.floor_area_ratio > 300:  # 300% 초과는 위험
            compliance_score -= 2.0
        
        total += max(0, compliance_score)
        
        return min(15.0, total)
    
    def _score_by_threshold(self, value: float, thresholds: List[Tuple[float, float]]) -> float:
        """
        Threshold 기반 점수 계산 (일반)
        
        값이 작을수록 높은 점수 (예: 거리)
        
        Args:
            value: 평가 값
            thresholds: [(threshold, score), ...] (오름차순)
            
        Returns:
            float: 점수
        """
        for threshold, score in thresholds:
            if value <= threshold:
                return score
        return 0.0
    
    def _score_by_threshold_reverse(self, value: float, thresholds: List[Tuple[float, float]]) -> float:
        """
        Threshold 기반 점수 계산 (역방향)
        
        값이 클수록 높은 점수 (예: 세대수, ROI)
        
        Args:
            value: 평가 값
            thresholds: [(threshold, score), ...] (내림차순)
            
        Returns:
            float: 점수
        """
        for threshold, score in thresholds:
            if value >= threshold:
                return score
        return 0.0
    
    def _score_to_grade(self, total_score: float) -> ProjectGrade:
        """
        총점을 등급으로 변환
        
        Args:
            total_score: 총점 (0-110)
            
        Returns:
            ProjectGrade
        """
        for threshold, grade in sorted(self.GRADE_THRESHOLDS.items(), reverse=True):
            if total_score >= threshold:
                return grade
        return ProjectGrade.F
