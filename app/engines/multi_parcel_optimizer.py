"""
Multi-Parcel Optimization Engine v24.1
다필지 최적 조합 선택 알고리즘

Features:
- 모든 가능한 필지 조합 탐색 (Combination Search)
- 다차원 평가 점수 (Multi-criteria Scoring)
- Pareto 최적 조합 도출 (Pareto Optimal Set)
- 시너지 효과 정량화 (Synergy Quantification)
- 조합 비교 및 순위 (Ranking & Comparison)

Author: ZeroSite v24 Team
Date: 2025-12-12
"""

from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass, field
from itertools import combinations
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParcelData:
    """개별 필지 데이터"""
    id: str
    area_sqm: float
    max_far: float
    price_per_sqm: float
    latitude: float = 0.0
    longitude: float = 0.0
    zoning: str = "general_residential"
    
    # 추가 속성
    shape_regularity: float = 0.7  # 0-1, 형상 정형성
    accessibility: float = 0.8  # 0-1, 접근성
    development_difficulty: float = 0.3  # 0-1, 개발 난이도


@dataclass
class CombinationScore:
    """조합 평가 점수"""
    # 기본 점수
    area_score: float = 0.0  # 면적 적합성 (0-100)
    far_score: float = 0.0  # 용적률 효율성 (0-100)
    cost_score: float = 0.0  # 비용 효율성 (0-100)
    shape_score: float = 0.0  # 형상 개선도 (0-100)
    
    # 시너지 점수
    synergy_score: float = 0.0  # 종합 시너지 (0-100)
    
    # 종합 점수
    total_score: float = 0.0  # 가중 평균 (0-100)
    
    # 가중치
    weights: Dict[str, float] = field(default_factory=lambda: {
        'area': 0.25,
        'far': 0.25,
        'cost': 0.20,
        'shape': 0.15,
        'synergy': 0.15
    })


@dataclass
class ParcelCombination:
    """필지 조합"""
    id: str
    parcels: List[ParcelData]
    
    # 조합 특성
    total_area: float = 0.0
    avg_far: float = 0.0
    combined_far: float = 0.0
    total_cost: float = 0.0
    
    # 평가 결과
    scores: Optional[CombinationScore] = None
    rank: int = 0
    
    # 분석
    advantages: List[str] = field(default_factory=list)
    disadvantages: List[str] = field(default_factory=list)
    recommendation: str = ""
    
    # Pareto 최적성
    is_pareto_optimal: bool = False
    dominated_by: List[str] = field(default_factory=list)


class MultiParcelOptimizer:
    """다필지 최적 조합 선택 엔진"""
    
    def __init__(self):
        """초기화"""
        self.min_parcels = 1
        self.max_parcels = 5  # 최대 5개 필지 조합
        self.target_area_min = 500  # 최소 목표 면적 (㎡)
        self.target_area_max = 3000  # 최대 목표 면적 (㎡)
        self.max_distance_km = 0.5  # 최대 조합 거리 (km)
    
    def optimize(
        self, 
        parcels: List[Dict],
        target_area_range: Tuple[float, float] = (500, 2000),
        max_combinations: int = 100
    ) -> Dict:
        """
        최적 필지 조합 탐색
        
        Args:
            parcels: 필지 목록
            target_area_range: 목표 면적 범위 (min, max)
            max_combinations: 최대 탐색 조합 수
            
        Returns:
            최적화 결과
        """
        logger.info(f"Starting optimization with {len(parcels)} parcels")
        
        # 1. 필지 데이터 변환
        parcel_objects = self._convert_parcels(parcels)
        
        # 2. 모든 가능한 조합 생성
        all_combinations = self._generate_combinations(
            parcel_objects, 
            target_area_range,
            max_combinations
        )
        
        logger.info(f"Generated {len(all_combinations)} valid combinations")
        
        # 3. 각 조합 평가
        evaluated_combinations = []
        for combo in all_combinations:
            evaluated = self._evaluate_combination(combo)
            evaluated_combinations.append(evaluated)
        
        # 4. 조합 순위 매기기
        ranked_combinations = self._rank_combinations(evaluated_combinations)
        
        # 5. Pareto 최적 조합 찾기
        pareto_optimal = self._find_pareto_optimal(ranked_combinations)
        
        # 6. 최종 추천
        recommendation = self._generate_final_recommendation(
            ranked_combinations, 
            pareto_optimal
        )
        
        # 7. 결과 반환
        result = {
            'success': True,
            'total_parcels': len(parcel_objects),
            'total_combinations_evaluated': len(ranked_combinations),
            'top_10_combinations': self._format_top_combinations(ranked_combinations[:10]),
            'pareto_optimal_set': self._format_pareto_optimal(pareto_optimal),
            'best_combination': self._format_combination(ranked_combinations[0]) if ranked_combinations else None,
            'recommendation': recommendation,
            'optimization_summary': self._generate_summary(ranked_combinations, pareto_optimal)
        }
        
        if ranked_combinations:
            logger.info(f"Optimization complete: best score {ranked_combinations[0].scores.total_score:.1f}")
        else:
            logger.warning("No combinations found matching criteria")
        
        return result
    
    def _convert_parcels(self, parcels: List[Dict]) -> List[ParcelData]:
        """필지 데이터 변환"""
        converted = []
        for i, p in enumerate(parcels):
            parcel = ParcelData(
                id=p.get('id', f"P{i+1:03d}"),
                area_sqm=p['area_sqm'],
                max_far=p.get('max_far', 200),
                price_per_sqm=p.get('price_per_sqm', 10000000),
                latitude=p.get('latitude', 37.5 + i * 0.001),
                longitude=p.get('longitude', 127.0 + i * 0.001),
                zoning=p.get('zoning', 'general_residential'),
                shape_regularity=p.get('shape_regularity', 0.7),
                accessibility=p.get('accessibility', 0.8),
                development_difficulty=p.get('development_difficulty', 0.3)
            )
            converted.append(parcel)
        return converted
    
    def _generate_combinations(
        self, 
        parcels: List[ParcelData],
        target_area_range: Tuple[float, float],
        max_combinations: int
    ) -> List[ParcelCombination]:
        """모든 가능한 조합 생성"""
        valid_combinations = []
        target_min, target_max = target_area_range
        
        # 1개부터 max_parcels개까지 조합
        for n in range(self.min_parcels, min(self.max_parcels + 1, len(parcels) + 1)):
            for combo_tuple in combinations(parcels, n):
                # 면적 합계 계산
                total_area = sum(p.area_sqm for p in combo_tuple)
                
                # 목표 면적 범위 체크
                if not (target_min <= total_area <= target_max):
                    continue
                
                # 거리 체크 (n >= 2인 경우)
                if n >= 2 and not self._check_distance_constraint(combo_tuple):
                    continue
                
                # 조합 생성
                combo_id = "_".join(sorted([p.id for p in combo_tuple]))
                combination = ParcelCombination(
                    id=combo_id,
                    parcels=list(combo_tuple),
                    total_area=total_area
                )
                
                valid_combinations.append(combination)
                
                # 최대 조합 수 제한
                if len(valid_combinations) >= max_combinations:
                    break
            
            if len(valid_combinations) >= max_combinations:
                break
        
        return valid_combinations
    
    def _check_distance_constraint(self, parcels: Tuple[ParcelData, ...]) -> bool:
        """거리 제약 조건 체크"""
        # 모든 쌍에 대해 거리 체크
        for i, p1 in enumerate(parcels):
            for p2 in parcels[i+1:]:
                distance = self._calculate_distance(
                    p1.latitude, p1.longitude,
                    p2.latitude, p2.longitude
                )
                if distance > self.max_distance_km:
                    return False
        return True
    
    def _calculate_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """두 지점 간 거리 계산 (km) - Haversine 공식"""
        R = 6371  # 지구 반지름 (km)
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _evaluate_combination(self, combination: ParcelCombination) -> ParcelCombination:
        """조합 평가"""
        parcels = combination.parcels
        n = len(parcels)
        
        # 기본 계산
        total_area = sum(p.area_sqm for p in parcels)
        avg_far = sum(p.max_far for p in parcels) / n
        
        # FAR 보너스 (다필지 결합시)
        far_bonus = 0.0
        if n >= 3:
            far_bonus = 20.0  # 3개 이상: 20%
        elif n == 2:
            far_bonus = 10.0  # 2개: 10%
        
        combined_far = avg_far + far_bonus
        
        # 총 비용
        total_cost = sum(p.area_sqm * p.price_per_sqm for p in parcels) / 100_000_000  # 억원
        
        # 기본 값 설정
        combination.total_area = total_area
        combination.avg_far = avg_far
        combination.combined_far = combined_far
        combination.total_cost = total_cost
        
        # 점수 계산
        scores = CombinationScore()
        
        # 1. 면적 점수 (목표: 1000-2000㎡)
        if 1000 <= total_area <= 2000:
            scores.area_score = 100
        elif 800 <= total_area < 1000:
            scores.area_score = 80 + (total_area - 800) / 200 * 20
        elif 2000 < total_area <= 2500:
            scores.area_score = 80 + (2500 - total_area) / 500 * 20
        else:
            scores.area_score = max(0, 60 - abs(total_area - 1500) / 1500 * 60)
        
        # 2. FAR 점수 (높을수록 좋음)
        max_possible_far = 300  # 최대 기대 FAR
        scores.far_score = min(combined_far / max_possible_far * 100, 100)
        
        # 3. 비용 점수 (낮을수록 좋음, 역산)
        avg_cost_per_sqm = total_cost * 100_000_000 / total_area
        max_acceptable_cost = 15_000_000  # 평당 최대 허용 비용
        if avg_cost_per_sqm <= max_acceptable_cost:
            scores.cost_score = 100 - (avg_cost_per_sqm / max_acceptable_cost * 50)
        else:
            scores.cost_score = max(0, 50 - (avg_cost_per_sqm - max_acceptable_cost) / max_acceptable_cost * 50)
        
        # 4. 형상 점수
        avg_shape = sum(p.shape_regularity for p in parcels) / n
        shape_improvement = 0.0
        if n >= 3:
            shape_improvement = 0.3  # 3개 이상: 대폭 개선
        elif n == 2:
            shape_improvement = 0.15  # 2개: 개선
        
        final_shape = min(avg_shape + shape_improvement, 1.0)
        scores.shape_score = final_shape * 100
        
        # 5. 시너지 점수
        synergy_factors = []
        
        # 다필지 조합 보너스
        if n >= 2:
            synergy_factors.append(n * 10)  # 필지 수당 10점
        
        # FAR 보너스
        synergy_factors.append(far_bonus / 20 * 30)  # 최대 30점
        
        # 접근성 평균
        avg_accessibility = sum(p.accessibility for p in parcels) / n
        synergy_factors.append(avg_accessibility * 20)  # 최대 20점
        
        # 개발 난이도 (낮을수록 좋음)
        avg_difficulty = sum(p.development_difficulty for p in parcels) / n
        synergy_factors.append((1 - avg_difficulty) * 20)  # 최대 20점
        
        scores.synergy_score = min(sum(synergy_factors), 100)
        
        # 6. 종합 점수 (가중 평균)
        weights = scores.weights
        scores.total_score = (
            scores.area_score * weights['area'] +
            scores.far_score * weights['far'] +
            scores.cost_score * weights['cost'] +
            scores.shape_score * weights['shape'] +
            scores.synergy_score * weights['synergy']
        )
        
        combination.scores = scores
        
        # 강점/약점 분석
        combination.advantages = self._analyze_advantages(combination)
        combination.disadvantages = self._analyze_disadvantages(combination)
        
        # 추천 메시지
        if scores.total_score >= 80:
            combination.recommendation = "✅ 최우선 추천 - 모든 기준 우수"
        elif scores.total_score >= 70:
            combination.recommendation = "⭐ 적극 추천 - 대부분 기준 충족"
        elif scores.total_score >= 60:
            combination.recommendation = "⚠️ 조건부 추천 - 일부 개선 필요"
        else:
            combination.recommendation = "❌ 비추천 - 다른 조합 검토"
        
        return combination
    
    def _analyze_advantages(self, combination: ParcelCombination) -> List[str]:
        """강점 분석"""
        advantages = []
        scores = combination.scores
        n = len(combination.parcels)
        
        if scores.area_score >= 90:
            advantages.append(f"최적 면적 ({combination.total_area:.0f}㎡)")
        
        if scores.far_score >= 85:
            advantages.append(f"높은 용적률 ({combination.combined_far:.1f}%)")
        
        if scores.cost_score >= 70:
            advantages.append(f"우수한 비용 효율 (총 {combination.total_cost:.1f}억원)")
        
        if n >= 3:
            advantages.append(f"다필지 조합 시너지 ({n}개 필지)")
        
        if scores.synergy_score >= 80:
            advantages.append("높은 시너지 효과")
        
        return advantages
    
    def _analyze_disadvantages(self, combination: ParcelCombination) -> List[str]:
        """약점 분석"""
        disadvantages = []
        scores = combination.scores
        n = len(combination.parcels)
        
        if scores.area_score < 60:
            disadvantages.append(f"면적 부족 또는 과다 ({combination.total_area:.0f}㎡)")
        
        if scores.cost_score < 50:
            disadvantages.append(f"높은 취득 비용 ({combination.total_cost:.1f}억원)")
        
        if n >= 3:
            disadvantages.append(f"복잡한 소유권 조정 ({n}명 소유자)")
        
        if scores.shape_score < 60:
            disadvantages.append("불규칙한 부지 형상")
        
        return disadvantages
    
    def _rank_combinations(self, combinations: List[ParcelCombination]) -> List[ParcelCombination]:
        """조합 순위 매기기"""
        # 종합 점수 기준 정렬
        sorted_combos = sorted(
            combinations, 
            key=lambda c: c.scores.total_score, 
            reverse=True
        )
        
        # 순위 부여
        for rank, combo in enumerate(sorted_combos, start=1):
            combo.rank = rank
        
        return sorted_combos
    
    def _find_pareto_optimal(self, combinations: List[ParcelCombination]) -> List[ParcelCombination]:
        """Pareto 최적 조합 찾기"""
        pareto_set = []
        
        for i, combo_i in enumerate(combinations):
            is_dominated = False
            dominated_by_list = []
            
            for j, combo_j in enumerate(combinations):
                if i == j:
                    continue
                
                # combo_j가 combo_i를 지배하는지 확인
                if self._dominates(combo_j, combo_i):
                    is_dominated = True
                    dominated_by_list.append(combo_j.id)
            
            if not is_dominated:
                combo_i.is_pareto_optimal = True
                pareto_set.append(combo_i)
            else:
                combo_i.dominated_by = dominated_by_list
        
        return pareto_set
    
    def _dominates(self, combo_a: ParcelCombination, combo_b: ParcelCombination) -> bool:
        """A가 B를 지배하는지 확인 (Pareto Dominance)"""
        scores_a = combo_a.scores
        scores_b = combo_b.scores
        
        # 모든 기준에서 A >= B이고, 적어도 하나에서 A > B
        criteria = [
            scores_a.area_score >= scores_b.area_score,
            scores_a.far_score >= scores_b.far_score,
            scores_a.cost_score >= scores_b.cost_score,
            scores_a.shape_score >= scores_b.shape_score,
            scores_a.synergy_score >= scores_b.synergy_score
        ]
        
        strict_criteria = [
            scores_a.area_score > scores_b.area_score,
            scores_a.far_score > scores_b.far_score,
            scores_a.cost_score > scores_b.cost_score,
            scores_a.shape_score > scores_b.shape_score,
            scores_a.synergy_score > scores_b.synergy_score
        ]
        
        return all(criteria) and any(strict_criteria)
    
    def _generate_final_recommendation(
        self, 
        combinations: List[ParcelCombination],
        pareto_optimal: List[ParcelCombination]
    ) -> str:
        """최종 추천 메시지 생성"""
        if not combinations:
            return "❌ 조건을 만족하는 조합을 찾을 수 없습니다."
        
        best = combinations[0]
        
        recommendation = f"""
🏆 **최적 조합 추천: {best.id}**

📊 종합 점수: {best.scores.total_score:.1f}점
- 면적: {best.scores.area_score:.1f}점
- 용적률: {best.scores.far_score:.1f}점
- 비용: {best.scores.cost_score:.1f}점
- 형상: {best.scores.shape_score:.1f}점
- 시너지: {best.scores.synergy_score:.1f}점

📌 조합 특성:
- 필지 수: {len(best.parcels)}개
- 총 면적: {best.total_area:.0f}㎡
- 결합 용적률: {best.combined_far:.1f}%
- 총 취득비용: {best.total_cost:.1f}억원

✅ 강점: {', '.join(best.advantages)}
⚠️ 약점: {', '.join(best.disadvantages) if best.disadvantages else '없음'}

💡 Pareto 최적 조합: {len(pareto_optimal)}개 (상위 {len(pareto_optimal)/len(combinations)*100:.1f}%)

{best.recommendation}
""".strip()
        
        return recommendation
    
    def _generate_summary(
        self, 
        combinations: List[ParcelCombination],
        pareto_optimal: List[ParcelCombination]
    ) -> Dict:
        """최적화 요약 생성"""
        if not combinations:
            return {}
        
        avg_score = sum(c.scores.total_score for c in combinations) / len(combinations)
        best_score = combinations[0].scores.total_score
        
        return {
            'total_evaluated': len(combinations),
            'pareto_optimal_count': len(pareto_optimal),
            'pareto_optimal_ratio': round(len(pareto_optimal) / len(combinations) * 100, 1),
            'average_score': round(avg_score, 1),
            'best_score': round(best_score, 1),
            'score_improvement_vs_avg': round(best_score - avg_score, 1),
            'single_parcel_count': sum(1 for c in combinations if len(c.parcels) == 1),
            'multi_parcel_count': sum(1 for c in combinations if len(c.parcels) > 1),
            'avg_parcels_per_combination': round(sum(len(c.parcels) for c in combinations) / len(combinations), 1)
        }
    
    def _format_combination(self, combination: ParcelCombination) -> Dict:
        """조합 정보 포맷팅"""
        return {
            'id': combination.id,
            'rank': combination.rank,
            'parcel_count': len(combination.parcels),
            'parcel_ids': [p.id for p in combination.parcels],
            'total_area_sqm': round(combination.total_area, 2),
            'combined_far_percent': round(combination.combined_far, 1),
            'total_cost_billion': round(combination.total_cost, 2),
            'scores': {
                'total': round(combination.scores.total_score, 1),
                'area': round(combination.scores.area_score, 1),
                'far': round(combination.scores.far_score, 1),
                'cost': round(combination.scores.cost_score, 1),
                'shape': round(combination.scores.shape_score, 1),
                'synergy': round(combination.scores.synergy_score, 1)
            },
            'advantages': combination.advantages,
            'disadvantages': combination.disadvantages,
            'recommendation': combination.recommendation,
            'is_pareto_optimal': combination.is_pareto_optimal
        }
    
    def _format_top_combinations(self, combinations: List[ParcelCombination]) -> List[Dict]:
        """상위 조합 리스트 포맷팅"""
        return [self._format_combination(c) for c in combinations]
    
    def _format_pareto_optimal(self, pareto_optimal: List[ParcelCombination]) -> List[Dict]:
        """Pareto 최적 조합 포맷팅"""
        return [self._format_combination(c) for c in pareto_optimal]


if __name__ == "__main__":
    print("="*80)
    print("MULTI-PARCEL OPTIMIZER v24.1 - CLI TEST")
    print("="*80)
    
    optimizer = MultiParcelOptimizer()
    
    # 테스트 데이터: 5개 필지
    test_parcels = [
        {'id': 'P001', 'area_sqm': 400, 'max_far': 200, 'price_per_sqm': 10000000, 
         'latitude': 37.5000, 'longitude': 127.0000, 'shape_regularity': 0.8},
        {'id': 'P002', 'area_sqm': 600, 'max_far': 220, 'price_per_sqm': 10500000,
         'latitude': 37.5002, 'longitude': 127.0002, 'shape_regularity': 0.7},
        {'id': 'P003', 'area_sqm': 800, 'max_far': 200, 'price_per_sqm': 9800000,
         'latitude': 37.5004, 'longitude': 127.0004, 'shape_regularity': 0.9},
        {'id': 'P004', 'area_sqm': 500, 'max_far': 250, 'price_per_sqm': 11000000,
         'latitude': 37.5006, 'longitude': 127.0006, 'shape_regularity': 0.6},
        {'id': 'P005', 'area_sqm': 700, 'max_far': 230, 'price_per_sqm': 10200000,
         'latitude': 37.5008, 'longitude': 127.0008, 'shape_regularity': 0.75}
    ]
    
    result = optimizer.optimize(
        parcels=test_parcels,
        target_area_range=(1000, 2000),
        max_combinations=50
    )
    
    print(f"\n✅ Optimization Complete")
    print(f"\n📊 Summary:")
    print(f"  - Total Parcels: {result['total_parcels']}")
    print(f"  - Combinations Evaluated: {result['total_combinations_evaluated']}")
    print(f"  - Pareto Optimal Set: {len(result['pareto_optimal_set'])} combinations")
    
    print(f"\n🏆 Best Combination:")
    best = result['best_combination']
    print(f"  - ID: {best['id']}")
    print(f"  - Rank: #{best['rank']}")
    print(f"  - Parcels: {best['parcel_count']} ({', '.join(best['parcel_ids'])})")
    print(f"  - Total Area: {best['total_area_sqm']}㎡")
    print(f"  - Combined FAR: {best['combined_far_percent']}%")
    print(f"  - Total Cost: {best['total_cost_billion']}억원")
    print(f"  - Total Score: {best['scores']['total']}")
    print(f"  - Pareto Optimal: {'Yes' if best['is_pareto_optimal'] else 'No'}")
    
    print(f"\n📈 Top 5 Combinations:")
    for i, combo in enumerate(result['top_10_combinations'][:5], 1):
        print(f"  #{i}. {combo['id']}: {combo['scores']['total']:.1f}점 "
              f"({combo['parcel_count']}필지, {combo['total_area_sqm']:.0f}㎡)")
    
    print(f"\n{result['recommendation']}")
    
    print("\n" + "="*80)
