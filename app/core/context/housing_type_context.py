"""
M3: Housing Type Context
=========================

LH 지역·유형 선택 모듈(M3) 출력 Context

LH 신축매입임대 5가지 주거 유형:
1. 청년형 (Youth)
2. 신혼·신생아 I형 (Newlywed I)
3. 신혼·신생아 II형 (Newlywed II)
4. 다자녀형 (Multi-child)
5. 고령자형 (Senior)

이 모듈은 입지 분석을 통해 가장 적합한 유형을 선택합니다.

⚠️ 중요:
- land_value는 사용하지 않음 (M2 결과만 참조)
- 세대수는 계산하지 않음 (M4로 이동)
- 사업성은 고려하지 않음 (M5로 이동)

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TypeScore:
    """유형별 점수"""
    type_name: str                      # 유형명
    type_code: str                      # 유형 코드
    total_score: float                  # 총점 (0-100)
    location_score: float               # 입지 점수 (35점)
    accessibility_score: float          # 접근성 점수
    poi_score: float                    # POI 점수
    demand_prediction: float            # 수요 예측 점수


@dataclass(frozen=True)
class POIAnalysis:
    """POI 분석 결과"""
    subway_distance: float              # 지하철역 거리 (m)
    school_distance: float              # 학교 거리 (m)
    hospital_distance: float            # 병원 거리 (m)
    commercial_distance: float          # 상업시설 거리 (m)
    
    subway_score: float                 # 지하철 점수
    school_score: float                 # 학교 점수
    hospital_score: float               # 병원 점수
    commercial_score: float             # 상업시설 점수
    
    total_poi_count: int                # 총 POI 개수
    radius_500m_count: int              # 반경 500m 내
    radius_1km_count: int               # 반경 1km 내
    radius_2km_count: int               # 반경 2km 내


@dataclass(frozen=True)
class HousingTypeContext:
    """
    LH 유형 선택 Context (M3 출력)
    
    frozen=True: 생성 후 수정 불가
    """
    
    # === 선택된 유형 (REQUIRED FIELDS - NO DEFAULTS) ===
    selected_type: str                  # 최종 선택 유형 (youth/newlywed_1/newlywed_2/multi_child/senior)
    selected_type_name: str             # 유형명 (한글)
    selection_confidence: float         # 선택 신뢰도 (0-1)
    
    # === 5가지 유형별 점수 (REQUIRED) ===
    type_scores: Dict[str, TypeScore]   # 유형별 상세 점수
    
    # === 입지 분석 (REQUIRED) ===
    location_score: float               # 입지 총점 (35점 만점)
    poi_analysis: POIAnalysis           # POI 분석 결과
    
    # === 수요 예측 (REQUIRED) ===
    demand_prediction: float            # 수요 예측 점수 (0-100)
    demand_trend: str                   # 수요 추세 (HIGH/MEDIUM/LOW)
    target_population: int              # 예상 타겟 인구
    
    # === 경쟁 분석 (REQUIRED) ===
    competitor_count: int               # 주변 경쟁 단지 수
    competitor_analysis: str            # 경쟁 상황 (WEAK/MODERATE/STRONG)
    
    # === 메타데이터 (REQUIRED) ===
    analysis_date: str                  # 분석 일시
    
    # === 동점 처리 (Tie Handling) - OPTIONAL FIELDS WITH DEFAULTS ===
    is_tie: bool = False                # 동점 여부 (점수 차이 < 0.05)
    secondary_type: Optional[str] = None        # 2순위 유형 코드
    secondary_type_name: Optional[str] = None   # 2순위 유형명
    secondary_score: Optional[float] = None     # 2순위 점수
    score_difference: Optional[float] = None    # 1순위와 2순위 점수 차이
    
    # === 권장사항 (OPTIONAL) ===
    strengths: List[str] = field(default_factory=list)       # 강점
    weaknesses: List[str] = field(default_factory=list)      # 약점
    recommendations: List[str] = field(default_factory=list)  # 권장사항
    data_sources: List[str] = field(default_factory=list)    # 데이터 출처
    
    def __post_init__(self):
        """유효성 검증"""
        valid_types = ["youth", "newlywed_1", "newlywed_2", "multi_child", "senior"]
        assert self.selected_type in valid_types, \
            f"유형은 {valid_types} 중 하나여야 합니다"
        assert 0 <= self.selection_confidence <= 1, \
            "선택 신뢰도는 0-1 범위여야 합니다"
        assert 0 <= self.location_score <= 35, \
            "입지 점수는 0-35 범위여야 합니다"
        assert len(self.type_scores) == 5, \
            "5가지 유형별 점수가 모두 있어야 합니다"
    
    @property
    def is_youth_suitable(self) -> bool:
        """청년형 적합 여부"""
        return self.selected_type == "youth"
    
    @property
    def is_family_suitable(self) -> bool:
        """가족형 적합 여부 (신혼 또는 다자녀)"""
        return self.selected_type in ["newlywed_1", "newlywed_2", "multi_child"]
    
    @property
    def is_senior_suitable(self) -> bool:
        """고령자형 적합 여부"""
        return self.selected_type == "senior"
    
    @property
    def type_ranking(self) -> List[str]:
        """유형 순위 (점수 높은 순)"""
        sorted_types = sorted(
            self.type_scores.items(),
            key=lambda x: x[1].total_score,
            reverse=True
        )
        return [t[0] for t in sorted_types]
    
    @property
    def display_string(self) -> str:
        """보고서용 표시 문자열 (동점 시 1순위/2순위 표시)"""
        if self.is_tie and self.secondary_type_name:
            primary_score_display = f"{self.type_scores[self.selected_type].total_score:.1f}" if self.selected_type in self.type_scores else "N/A"
            secondary_score_display = f"{self.secondary_score:.1f}" if self.secondary_score else "N/A"
            return f"1순위: {self.selected_type_name} ({primary_score_display}점) / 2순위: {self.secondary_type_name} ({secondary_score_display}점)"
        return f"{self.selected_type_name}"
    
    @property
    def selection_summary(self) -> str:
        """선택 요약"""
        base_summary = (
            f"선택 유형: {self.selected_type_name}\n"
            f"입지 점수: {self.location_score:.1f}/35점\n"
            f"수요 예측: {self.demand_trend}\n"
            f"선택 신뢰도: {self.selection_confidence:.0%}"
        )
        
        if self.is_tie:
            tie_info = f"\n⚠️ 동점: {self.secondary_type_name}과 점수 차이 {self.score_difference:.2f}점"
            return base_summary + tie_info
        
        return base_summary
    
    def to_dict(self) -> Dict[str, any]:
        """딕셔너리 변환"""
        selected_dict = {
            "type": self.selected_type,
            "name": self.selected_type_name,
            "confidence": self.selection_confidence,
            "is_tie": self.is_tie,
            "display_string": self.display_string
        }
        
        # 동점 정보 추가
        if self.is_tie:
            selected_dict.update({
                "secondary_type": self.secondary_type,
                "secondary_name": self.secondary_type_name,
                "secondary_score": self.secondary_score,
                "score_difference": self.score_difference
            })
        
        return {
            "selected": selected_dict,
            "scores": {
                code: {
                    "name": score.type_name,
                    "total": score.total_score,
                    "location": score.location_score,
                    "accessibility": score.accessibility_score,
                    "poi": score.poi_score,
                    "demand": score.demand_prediction
                }
                for code, score in self.type_scores.items()
            },
            "location": {
                "score": self.location_score,
                "poi": {
                    "subway_distance": self.poi_analysis.subway_distance,
                    "school_distance": self.poi_analysis.school_distance,
                    "hospital_distance": self.poi_analysis.hospital_distance,
                    "commercial_distance": self.poi_analysis.commercial_distance,
                    "total_count": self.poi_analysis.total_poi_count
                }
            },
            "demand": {
                "prediction": self.demand_prediction,
                "trend": self.demand_trend,
                "target_population": self.target_population
            },
            "competition": {
                "count": self.competitor_count,
                "analysis": self.competitor_analysis
            },
            "insights": {
                "strengths": self.strengths,
                "weaknesses": self.weaknesses,
                "recommendations": self.recommendations
            },
            "metadata": {
                "date": self.analysis_date,
                "sources": self.data_sources
            }
        }
