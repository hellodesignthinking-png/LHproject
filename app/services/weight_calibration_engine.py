"""
ZeroSite v42.1 - Weight Calibration Engine
LH Pilot 데이터 기반 자동 가중치 조정 시스템

Purpose:
- LH Pilot Program 실제 결과 기반 가중치 최적화
- Prediction error 분석 및 개선
- Automatic weight adjustment within ±5% range
- 목표 정확도: 85%+

Author: ZeroSite AI Development Team
Date: 2025-12-14
Version: 1.0.0
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging
import math
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CalibrationCase:
    """
    LH Pilot Program 단일 케이스
    
    Attributes:
        case_id: 케이스 ID
        zerosite_prediction: ZeroSite 예측 점수 (0-100)
        lh_decision: LH 실제 결정 (approved/rejected/pending)
        lh_score: LH 내부 점수 (0-100, 있는 경우)
        factors: 6개 Factor 점수 breakdown
        metadata: 추가 정보 (주소, 주택유형 등)
    """
    case_id: str
    zerosite_prediction: float
    lh_decision: str  # "approved", "rejected", "pending"
    lh_score: float = None  # LH 내부 점수 (알 수 없는 경우 None)
    factors: Dict[str, float] = None  # {"location": 85, "price": 90, ...}
    metadata: Dict[str, Any] = None


@dataclass
class CalibrationResult:
    """
    Calibration 결과
    
    Attributes:
        old_weights: 조정 전 가중치
        new_weights: 조정 후 가중치
        accuracy_improvement: 정확도 개선 (%)
        error_analysis: 오류 분석
        recommendation: 조정 권장사항
    """
    old_weights: Dict[str, float]
    new_weights: Dict[str, float]
    accuracy_improvement: float
    error_analysis: Dict[str, Any]
    recommendation: str


class WeightCalibrationEngine:
    """
    v42.1 Weight 자동 조정 엔진
    
    Based on LH pilot program feedback:
    1. Analyze prediction errors (false positives/negatives)
    2. Identify weight optimization opportunities
    3. Automatically adjust weights within ±5% range
    4. Generate calibration report
    """
    
    # Weight adjustment constraints
    MIN_WEIGHT = 0.05  # 최소 가중치 5%
    MAX_WEIGHT = 0.40  # 최대 가중치 40%
    MAX_ADJUSTMENT = 0.05  # 최대 조정폭 ±5%
    
    # v42 Base weights (initial)
    BASE_WEIGHTS_V42 = {
        "location": 0.15,
        "price_rationality": 0.35,
        "scale": 0.15,
        "structural": 0.10,
        "policy": 0.15,
        "risk": 0.10
    }
    
    def __init__(self):
        """Weight Calibration Engine 초기화"""
        self.version = "1.0.0"
        self.calibration_history = []
        logger.info(f"✅ Weight Calibration Engine v{self.version} initialized")
    
    
    def calibrate(
        self,
        cases: List[CalibrationCase],
        current_weights: Dict[str, float] = None,
        target_accuracy: float = 0.85
    ) -> CalibrationResult:
        """
        LH Pilot 데이터 기반 가중치 조정
        
        Args:
            cases: LH Pilot Program 케이스 리스트 (최소 10건 권장)
            current_weights: 현재 가중치 (None이면 v42 base 사용)
            target_accuracy: 목표 정확도 (default: 85%)
            
        Returns:
            CalibrationResult
        """
        logger.info(f"🔧 Weight Calibration Start - {len(cases)} cases")
        
        # Step 1: 현재 가중치 설정
        if current_weights is None:
            current_weights = self.BASE_WEIGHTS_V42.copy()
        
        # Step 2: Prediction Error 분석
        error_analysis = self._analyze_prediction_errors(cases, current_weights)
        
        # Step 3: Weight 최적화
        new_weights = self._optimize_weights(
            cases, 
            current_weights, 
            error_analysis,
            target_accuracy
        )
        
        # Step 4: 정확도 개선 계산
        old_accuracy = self._calculate_accuracy(cases, current_weights)
        new_accuracy = self._calculate_accuracy(cases, new_weights)
        accuracy_improvement = (new_accuracy - old_accuracy) * 100
        
        # Step 5: 조정 권장사항 생성
        recommendation = self._generate_recommendation(
            current_weights,
            new_weights,
            error_analysis,
            old_accuracy,
            new_accuracy
        )
        
        result = CalibrationResult(
            old_weights=current_weights,
            new_weights=new_weights,
            accuracy_improvement=accuracy_improvement,
            error_analysis=error_analysis,
            recommendation=recommendation
        )
        
        # Calibration history 저장
        self.calibration_history.append({
            "timestamp": datetime.now(),
            "num_cases": len(cases),
            "result": result
        })
        
        logger.info(f"✅ Weight Calibration Complete - Accuracy: {old_accuracy:.1%} → {new_accuracy:.1%} (+{accuracy_improvement:.1f}%)")
        
        return result
    
    
    def _analyze_prediction_errors(
        self,
        cases: List[CalibrationCase],
        weights: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Prediction Error 분석
        
        Returns:
            {
                'false_positives': [...],  # ZeroSite approved, LH rejected
                'false_negatives': [...],  # ZeroSite rejected, LH approved
                'accurate_predictions': [...],
                'error_patterns': {...}
            }
        """
        false_positives = []
        false_negatives = []
        accurate_predictions = []
        
        for case in cases:
            # ZeroSite prediction
            zs_approved = case.zerosite_prediction >= 70  # 70점 이상 = 승인 예측
            
            # LH actual decision
            lh_approved = (case.lh_decision == "approved")
            
            if zs_approved and not lh_approved:
                # False Positive: ZeroSite O, LH X
                false_positives.append(case)
            elif not zs_approved and lh_approved:
                # False Negative: ZeroSite X, LH O
                false_negatives.append(case)
            else:
                # Accurate prediction
                accurate_predictions.append(case)
        
        # Error pattern 분석
        error_patterns = self._identify_error_patterns(false_positives, false_negatives)
        
        return {
            'false_positives': false_positives,
            'false_negatives': false_negatives,
            'accurate_predictions': accurate_predictions,
            'false_positive_rate': len(false_positives) / len(cases),
            'false_negative_rate': len(false_negatives) / len(cases),
            'accuracy': len(accurate_predictions) / len(cases),
            'error_patterns': error_patterns
        }
    
    
    def _identify_error_patterns(
        self,
        false_positives: List[CalibrationCase],
        false_negatives: List[CalibrationCase]
    ) -> Dict[str, Any]:
        """
        Error Pattern 식별
        
        분석 항목:
        - Which factors contribute most to false positives?
        - Which factors contribute most to false negatives?
        - Are there systematic biases?
        """
        patterns = {
            'fp_factor_analysis': {},  # False Positive에서 높은 점수를 받은 factor
            'fn_factor_analysis': {},  # False Negative에서 낮은 점수를 받은 factor
            'overweighted_factors': [],  # 과대 평가된 factor
            'underweighted_factors': []  # 과소 평가된 factor
        }
        
        # False Positive 분석
        if false_positives:
            fp_factors = self._aggregate_factors(false_positives)
            patterns['fp_factor_analysis'] = fp_factors
            
            # 높은 점수를 준 factor = 과대 평가 가능성
            high_fp_factors = [f for f, score in fp_factors.items() if score >= 80]
            patterns['overweighted_factors'] = high_fp_factors
        
        # False Negative 분석
        if false_negatives:
            fn_factors = self._aggregate_factors(false_negatives)
            patterns['fn_factor_analysis'] = fn_factors
            
            # 낮은 점수를 준 factor = 과소 평가 가능성
            low_fn_factors = [f for f, score in fn_factors.items() if score < 70]
            patterns['underweighted_factors'] = low_fn_factors
        
        return patterns
    
    
    def _aggregate_factors(self, cases: List[CalibrationCase]) -> Dict[str, float]:
        """
        케이스들의 Factor 점수 평균 계산
        
        Returns:
            {"location": 85.5, "price": 72.3, ...}
        """
        if not cases:
            return {}
        
        factor_sums = {}
        factor_counts = {}
        
        for case in cases:
            if case.factors:
                for factor_name, score in case.factors.items():
                    if factor_name not in factor_sums:
                        factor_sums[factor_name] = 0
                        factor_counts[factor_name] = 0
                    
                    factor_sums[factor_name] += score
                    factor_counts[factor_name] += 1
        
        # 평균 계산
        factor_averages = {}
        for factor_name in factor_sums:
            factor_averages[factor_name] = factor_sums[factor_name] / factor_counts[factor_name]
        
        return factor_averages
    
    
    def _optimize_weights(
        self,
        cases: List[CalibrationCase],
        current_weights: Dict[str, float],
        error_analysis: Dict[str, Any],
        target_accuracy: float
    ) -> Dict[str, float]:
        """
        Weight 최적화 (Gradient Descent approach)
        
        Algorithm:
        1. Identify overweighted factors (causing false positives)
        2. Identify underweighted factors (causing false negatives)
        3. Adjust weights within ±5% constraint
        4. Ensure total weight = 1.0
        """
        new_weights = current_weights.copy()
        error_patterns = error_analysis['error_patterns']
        
        # Step 1: 과대 평가된 factor의 가중치 감소
        for factor in error_patterns.get('overweighted_factors', []):
            if factor in new_weights:
                # 최대 5% 감소
                adjustment = min(0.05, new_weights[factor] * 0.1)  # 현재 가중치의 10% 또는 5%
                new_weights[factor] = max(
                    self.MIN_WEIGHT,
                    new_weights[factor] - adjustment
                )
                logger.info(f"⬇️ Decreased {factor} weight: {current_weights[factor]:.2f} → {new_weights[factor]:.2f}")
        
        # Step 2: 과소 평가된 factor의 가중치 증가
        for factor in error_patterns.get('underweighted_factors', []):
            if factor in new_weights:
                # 최대 5% 증가
                adjustment = min(0.05, new_weights[factor] * 0.1)
                new_weights[factor] = min(
                    self.MAX_WEIGHT,
                    new_weights[factor] + adjustment
                )
                logger.info(f"⬆️ Increased {factor} weight: {current_weights[factor]:.2f} → {new_weights[factor]:.2f}")
        
        # Step 3: Normalize to ensure sum = 1.0
        new_weights = self._normalize_weights(new_weights)
        
        # Step 4: Validate constraints
        new_weights = self._validate_weight_constraints(current_weights, new_weights)
        
        return new_weights
    
    
    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        가중치 정규화 (합계 = 1.0)
        """
        total = sum(weights.values())
        
        if total == 0:
            return weights
        
        normalized = {k: v / total for k, v in weights.items()}
        
        return normalized
    
    
    def _validate_weight_constraints(
        self,
        old_weights: Dict[str, float],
        new_weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        가중치 제약 조건 검증
        
        Constraints:
        - Min weight: 5%
        - Max weight: 40%
        - Max adjustment: ±5% from old weight
        """
        validated = {}
        
        for factor, new_weight in new_weights.items():
            old_weight = old_weights[factor]
            
            # Constraint 1: Min/Max weight
            weight = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))
            
            # Constraint 2: Max adjustment ±5%
            if abs(weight - old_weight) > self.MAX_ADJUSTMENT:
                if weight > old_weight:
                    weight = old_weight + self.MAX_ADJUSTMENT
                else:
                    weight = old_weight - self.MAX_ADJUSTMENT
            
            validated[factor] = weight
        
        # Re-normalize after constraints
        validated = self._normalize_weights(validated)
        
        return validated
    
    
    def _calculate_accuracy(
        self,
        cases: List[CalibrationCase],
        weights: Dict[str, float]
    ) -> float:
        """
        특정 가중치로 예측했을 때의 정확도 계산
        
        Returns:
            Accuracy (0.0 - 1.0)
        """
        if not cases:
            return 0.0
        
        correct_predictions = 0
        
        for case in cases:
            # Recalculate score with new weights
            if case.factors:
                recalculated_score = sum(
                    case.factors.get(factor, 0) * weights.get(factor, 0)
                    for factor in weights.keys()
                )
            else:
                recalculated_score = case.zerosite_prediction
            
            # Prediction: score >= 70 → approved
            predicted_approved = (recalculated_score >= 70)
            actual_approved = (case.lh_decision == "approved")
            
            if predicted_approved == actual_approved:
                correct_predictions += 1
        
        accuracy = correct_predictions / len(cases)
        return accuracy
    
    
    def _generate_recommendation(
        self,
        old_weights: Dict[str, float],
        new_weights: Dict[str, float],
        error_analysis: Dict[str, Any],
        old_accuracy: float,
        new_accuracy: float
    ) -> str:
        """
        조정 권장사항 생성
        """
        recommendation_parts = []
        
        # Overall accuracy improvement
        if new_accuracy > old_accuracy:
            improvement = (new_accuracy - old_accuracy) * 100
            recommendation_parts.append(
                f"✅ **Accuracy Improved**: {old_accuracy:.1%} → {new_accuracy:.1%} (+{improvement:.1f}%)"
            )
        else:
            recommendation_parts.append(
                f"⚠️ **No Improvement**: Accuracy remains at {old_accuracy:.1%}"
            )
        
        # Weight changes
        recommendation_parts.append("\n**Weight Adjustments**:")
        for factor in old_weights.keys():
            old_w = old_weights[factor]
            new_w = new_weights[factor]
            
            if abs(new_w - old_w) >= 0.01:  # 1% 이상 변경된 경우만 표시
                change = (new_w - old_w) * 100
                direction = "↑" if change > 0 else "↓"
                recommendation_parts.append(
                    f"  - {factor}: {old_w:.1%} → {new_w:.1%} ({direction} {abs(change):.1f}%)"
                )
        
        # Error analysis summary
        fp_rate = error_analysis['false_positive_rate']
        fn_rate = error_analysis['false_negative_rate']
        
        recommendation_parts.append("\n**Error Analysis**:")
        recommendation_parts.append(f"  - False Positive Rate: {fp_rate:.1%}")
        recommendation_parts.append(f"  - False Negative Rate: {fn_rate:.1%}")
        
        # Next steps
        recommendation_parts.append("\n**Next Steps**:")
        if new_accuracy >= 0.85:
            recommendation_parts.append("  ✅ Target accuracy (85%) achieved!")
            recommendation_parts.append("  → Deploy new weights to production")
        elif new_accuracy >= 0.75:
            recommendation_parts.append("  🔄 Good progress (75%+)")
            recommendation_parts.append("  → Collect more LH pilot data for further calibration")
        else:
            recommendation_parts.append("  ⚠️ More data needed")
            recommendation_parts.append("  → Continue LH pilot program to collect 30+ cases")
        
        return "\n".join(recommendation_parts)
    
    
    def simulate_calibration(
        self,
        cases: List[CalibrationCase],
        weight_scenarios: List[Dict[str, float]]
    ) -> List[Tuple[Dict[str, float], float]]:
        """
        여러 가중치 시나리오 시뮬레이션
        
        Args:
            cases: LH Pilot cases
            weight_scenarios: 테스트할 가중치 시나리오들
            
        Returns:
            [(weights, accuracy), ...]
        """
        results = []
        
        for weights in weight_scenarios:
            accuracy = self._calculate_accuracy(cases, weights)
            results.append((weights, accuracy))
        
        # Sort by accuracy (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    
    def export_calibration_report(
        self,
        result: CalibrationResult,
        output_path: str = None
    ) -> str:
        """
        Calibration 리포트 생성 (Markdown)
        
        Returns:
            Markdown content
        """
        report = f"""# ZeroSite v42.1 Weight Calibration Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Engine Version**: {self.version}

---

## Summary

{result.recommendation}

---

## Weight Comparison

| Factor | Old Weight | New Weight | Change |
|--------|------------|------------|--------|
"""
        
        for factor in result.old_weights.keys():
            old_w = result.old_weights[factor]
            new_w = result.new_weights[factor]
            change = (new_w - old_w) * 100
            direction = "↑" if change > 0 else ("↓" if change < 0 else "→")
            
            report += f"| {factor} | {old_w:.1%} | {new_w:.1%} | {direction} {abs(change):.1f}% |\n"
        
        report += f"""
---

## Error Analysis

- **False Positive Rate**: {result.error_analysis['false_positive_rate']:.1%}
- **False Negatives Rate**: {result.error_analysis['false_negative_rate']:.1%}
- **Overall Accuracy**: {result.error_analysis['accuracy']:.1%}

### Overweighted Factors
{', '.join(result.error_analysis['error_patterns'].get('overweighted_factors', ['None']))}

### Underweighted Factors
{', '.join(result.error_analysis['error_patterns'].get('underweighted_factors', ['None']))}

---

## Calibration History

Total calibrations performed: {len(self.calibration_history)}

---

**Generated by**: ZeroSite Weight Calibration Engine v{self.version}
"""
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📄 Calibration report saved to {output_path}")
        
        return report


# Singleton instance
weight_calibration_engine = WeightCalibrationEngine()
