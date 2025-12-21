"""
M2: Appraisal Context (🔒 IMMUTABLE)
====================================

토지감정평가 모듈(M2) 출력 Context

⚠️ 절대 규칙 (CRITICAL):
1. frozen=True로 생성 후 수정 불가
2. 외부 모듈(M3-M6)에서 land_value 재계산 금지
3. 보고서에서 감정평가 로직 개입 금지
4. 이 Context는 READ-ONLY로만 사용

이 규칙을 어기면 전체 시스템 신뢰도가 무너집니다!

감정평가 프로세스:
1. 공시지가 조회
2. 거래사례 수집 (동적 생성 또는 실거래 API)
3. 4-Factor 프리미엄 계산:
   - Distance Factor (35%): 거리 기반 가격 차이
   - Time Factor (25%): 시점 보정
   - Size Factor (25%): 규모 보정
   - Zone Factor (15%): 용도지역 보정
4. Confidence Score 계산 (4-factor weighted)
5. AppraisalContext 생성 및 LOCK

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass(frozen=True)
class TransactionSample:
    """거래사례 개별 데이터"""
    address: str                        # 거래 주소
    transaction_date: str               # 거래 일자
    price_total: float                  # 거래 총액 (원)
    price_per_sqm: float                # ㎡당 단가 (원)
    area_sqm: float                     # 거래 면적 (㎡)
    distance_km: float                  # 대상지와의 거리 (km)
    zone_type: str                      # 용도지역
    adjusted_price_per_sqm: float       # 4-Factor 조정 후 단가
    adjustment_factors: Dict[str, float] = field(default_factory=dict)  # 조정 요인


@dataclass(frozen=True)
class PremiumFactors:
    """프리미엄 상세 요인"""
    road_score: float                   # 도로 점수 (0-10)
    terrain_score: float                # 지형 점수 (0-10)
    location_score: float               # 입지 점수 (0-10)
    accessibility_score: float          # 접근성 점수 (0-10)
    
    # 가중치 적용 프리미엄률
    distance_premium: float             # 거리 프리미엄 (35%)
    time_premium: float                 # 시점 프리미엄 (25%)
    size_premium: float                 # 규모 프리미엄 (25%)
    zone_premium: float                 # 용도 프리미엄 (15%)
    
    total_premium_rate: float           # 종합 프리미엄률 (%)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": {
                "road": self.road_score,
                "terrain": self.terrain_score,
                "location": self.location_score,
                "accessibility": self.accessibility_score
            },
            "premiums": {
                "distance": self.distance_premium,
                "time": self.time_premium,
                "size": self.size_premium,
                "zone": self.zone_premium,
                "total_rate": self.total_premium_rate
            }
        }


@dataclass(frozen=True)
class ConfidenceMetrics:
    """신뢰도 계산 메트릭"""
    sample_count_score: float           # 표본 수 점수 (30%)
    price_variance_score: float         # 가격 분산 점수 (30%)
    distance_score: float               # 거리 점수 (25%)
    recency_score: float                # 최신성 점수 (15%)
    
    confidence_score: float             # 종합 신뢰도 (0-1)
    confidence_level: str               # LOW/MEDIUM/HIGH
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": {
                "sample_count": self.sample_count_score,
                "price_variance": self.price_variance_score,
                "distance": self.distance_score,
                "recency": self.recency_score
            },
            "confidence": {
                "score": self.confidence_score,
                "level": self.confidence_level
            }
        }


@dataclass(frozen=True)
class AppraisalContext:
    """
    토지감정평가 Context (M2 출력)
    
    🔒 IMMUTABLE: frozen=True
    
    ⚠️ 절대 규칙:
    1. 이 Context 생성 후 어떤 모듈도 land_value 재계산 금지
    2. M3-M6은 이 Context를 READ-ONLY로만 참조
    3. 보고서는 계산 없이 값만 읽기
    """
    
    # === 핵심 감정평가 결과 (🔒 LOCKED) ===
    land_value: float                   # 감정평가액 (원) - 절대 수정 불가!
    unit_price_sqm: float               # ㎡당 단가 (원)
    unit_price_pyeong: float            # 평당 단가 (원)
    
    # === 기준가 ===
    official_price: float               # 공시지가 (원)
    official_price_per_sqm: float       # 공시지가 ㎡당 (원)
    
    # === 거래사례 ===
    transaction_samples: List[TransactionSample]  # 거래사례 목록
    transaction_count: int              # 거래사례 수
    avg_transaction_price: float        # 평균 거래가 (㎡당)
    
    # === 프리미엄 ===
    premium_factors: PremiumFactors     # 프리미엄 상세 요인
    premium_rate: float                 # 종합 프리미엄률 (%)
    
    # === 신뢰도 ===
    confidence_metrics: ConfidenceMetrics  # 신뢰도 메트릭
    confidence_score: float             # 신뢰도 점수 (0-1)
    confidence_level: str               # LOW/MEDIUM/HIGH
    
    # === 가격 범위 ===
    price_range_low: float              # 최소 예상가 (원)
    price_range_high: float             # 최대 예상가 (원)
    
    # === 메타데이터 ===
    valuation_date: str                 # 평가 기준일
    valuation_method: str               # 평가 방법 (거래사례비교법 등)
    appraiser: str                      # 평가 주체
    
    # === 협상 전략 (참고용) ===
    negotiation_strategies: List[Dict[str, Any]] = field(default_factory=list)
    
    # === 재무 분석 (추가 정보) ===
    asking_price: Optional[float] = None  # 호가 (있는 경우)
    price_gap_pct: Optional[float] = None  # 호가와의 차이 (%)
    recommendation: Optional[str] = None   # 추천 (저가/적정/고가)
    
    # === 경고 시스템 (Production Enhancement) ===
    warnings: List[Dict[str, str]] = field(default_factory=list)  # 경고 목록
    
    # === 시간적 기준 (Production Enhancement) ===
    valuation_base_year: int = field(default_factory=lambda: datetime.now().year)
    transaction_data_year: int = field(default_factory=lambda: datetime.now().year)
    
    def __post_init__(self):
        """유효성 검증"""
        assert self.land_value > 0, "감정평가액은 0보다 커야 합니다"
        assert self.unit_price_sqm > 0, "단가는 0보다 커야 합니다"
        assert 0 <= self.confidence_score <= 1, "신뢰도는 0-1 범위여야 합니다"
        assert self.confidence_level in ["LOW", "MEDIUM", "HIGH"], \
            "신뢰도 레벨은 LOW/MEDIUM/HIGH 중 하나여야 합니다"
        assert len(self.transaction_samples) == self.transaction_count, \
            "거래사례 수가 일치해야 합니다"
    
    @property
    def has_warnings(self) -> bool:
        """경고 존재 여부"""
        return len(self.warnings) > 0
    
    @property
    def is_high_confidence(self) -> bool:
        """높은 신뢰도 여부"""
        return self.confidence_level == "HIGH"
    
    @property
    def is_undervalued(self) -> bool:
        """저평가 여부 (호가 < 감정가)"""
        if self.asking_price is None:
            return False
        return self.asking_price < self.land_value
    
    @property
    def is_overvalued(self) -> bool:
        """고평가 여부 (호가 > 감정가)"""
        if self.asking_price is None:
            return False
        return self.asking_price > self.land_value
    
    @property
    def valuation_summary(self) -> str:
        """평가 요약"""
        return (
            f"감정평가액: ₩{self.land_value:,.0f}\n"
            f"㎡당 단가: ₩{self.unit_price_sqm:,.0f}\n"
            f"신뢰도: {self.confidence_level} ({self.confidence_score:.0%})\n"
            f"거래사례: {self.transaction_count}건"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            "appraisal": {
                "land_value": self.land_value,
                "unit_price_sqm": self.unit_price_sqm,
                "unit_price_pyeong": self.unit_price_pyeong
            },
            "official_price": {
                "total": self.official_price,
                "per_sqm": self.official_price_per_sqm
            },
            "transactions": {
                "count": self.transaction_count,
                "avg_price_sqm": self.avg_transaction_price,
                "samples": [
                    {
                        "address": t.address,
                        "date": t.transaction_date,
                        "price_sqm": t.price_per_sqm,
                        "adjusted_price_sqm": t.adjusted_price_per_sqm,
                        "distance_km": t.distance_km
                    }
                    for t in self.transaction_samples
                ]
            },
            "premium": self.premium_factors.to_dict(),
            "confidence": self.confidence_metrics.to_dict(),
            "price_range": {
                "low": self.price_range_low,
                "avg": self.land_value,
                "high": self.price_range_high
            },
            "metadata": {
                "date": self.valuation_date,
                "method": self.valuation_method,
                "appraiser": self.appraiser,
                "valuation_base_year": self.valuation_base_year,
                "transaction_data_year": self.transaction_data_year
            },
            "warnings": {
                "has_warnings": self.has_warnings,
                "items": self.warnings
            }
        }
    
    def __str__(self) -> str:
        """문자열 표현"""
        return self.valuation_summary
    
    def __repr__(self) -> str:
        """개발자용 표현"""
        return (
            f"AppraisalContext("
            f"land_value={self.land_value:,.0f}, "
            f"confidence={self.confidence_level}, "
            f"samples={self.transaction_count})"
        )
