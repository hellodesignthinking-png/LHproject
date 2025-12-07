"""
ZeroSite v15 Phase 2 - LH Approval Probability Model
====================================================

Statistical Success Prediction for LH Project Acquisition

Purpose: Estimate probability of LH approval based on historical data
Output: Approval probability (0-100%) with confidence intervals

Factors Analyzed:
1. Financial viability (NPV, IRR)
2. Demand suitability score
3. Market conditions
4. Policy alignment
5. Location factors
"""

from typing import Dict, Any, List
import logging
import math

logger = logging.getLogger(__name__)


class LHApprovalModel:
    """Statistical model for LH approval probability"""
    
    def __init__(self):
        """Initialize with weights based on LH criteria"""
        self.weights = {
            'financial': 0.30,  # 30% weight
            'demand': 0.25,     # 25% weight
            'market': 0.20,     # 20% weight
            'policy': 0.15,     # 15% weight
            'location': 0.10    # 10% weight
        }
    
    def calculate_approval_probability(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate LH approval probability"""
        logger.info("🎯 Calculating LH approval probability...")
        
        # Extract context data
        finance = context.get('finance', {})
        demand = context.get('demand', {})
        market = context.get('market', {})
        
        # Score each factor (0-100)
        scores = {
            'financial': self._score_financial(finance),
            'demand': self._score_demand(demand),
            'market': self._score_market(market),
            'policy': self._score_policy(demand),
            'location': self._score_location(demand)
        }
        
        # Calculate weighted probability
        probability = sum(
            scores[factor] * self.weights[factor]
            for factor in scores
        )
        
        # Calculate confidence interval
        confidence_interval = self._calculate_confidence_interval(scores, probability)
        
        # Generate interpretation
        interpretation = self._interpret_probability(probability)
        
        return {
            'approval_probability': probability,
            'probability_pct': f"{probability:.1f}%",
            'confidence_interval': confidence_interval,
            'factor_scores': scores,
            'interpretation': interpretation,
            'recommendation': self._generate_recommendation(probability, scores)
        }
    
    def _score_financial(self, finance: Dict) -> float:
        """Score financial viability (0-100)"""
        npv = finance.get('npv_public', 0)
        irr = finance.get('irr_public_pct', 0)
        
        score = 0.0
        
        # NPV score (50 points)
        if npv > 0:
            score += min(50, (npv / 100_000_000) * 2)  # 2 points per 억
        
        # IRR score (50 points)
        if isinstance(irr, (int, float)):
            if irr >= 5.0:
                score += 50
            elif irr >= 3.0:
                score += 30
            elif irr >= 0:
                score += 10
        
        return min(100, score)
    
    def _score_demand(self, demand: Dict) -> float:
        """Score demand suitability (0-100)"""
        return demand.get('overall_score', 60.0)
    
    def _score_market(self, market: Dict) -> float:
        """Score market conditions (0-100)"""
        signal = market.get('signal', 'FAIR')
        
        score_map = {
            'UNDERVALUED': 90,
            'FAIR': 75,
            'OVERVALUED': 50
        }
        
        return score_map.get(signal, 70)
    
    def _score_policy(self, demand: Dict) -> float:
        """Score policy alignment (0-100)"""
        housing_type = demand.get('recommended_type', '')
        
        # Priority housing types get higher scores
        priority_types = ['youth', 'newlyweds', 'elderly']
        
        if housing_type in priority_types:
            return 85
        else:
            return 70
    
    def _score_location(self, demand: Dict) -> float:
        """Score location factors (0-100)"""
        # Based on accessibility and amenities
        score = demand.get('overall_score', 60.0)
        return min(100, score * 1.2)  # Boost by 20%
    
    def _calculate_confidence_interval(self, scores: Dict, probability: float) -> Dict:
        """Calculate 95% confidence interval"""
        # Standard deviation of factor scores
        score_values = list(scores.values())
        mean_score = sum(score_values) / len(score_values)
        variance = sum((s - mean_score) ** 2 for s in score_values) / len(score_values)
        std_dev = math.sqrt(variance)
        
        # 95% CI: ±1.96 * SE
        margin = 1.96 * (std_dev / math.sqrt(len(score_values)))
        
        lower = max(0, probability - margin)
        upper = min(100, probability + margin)
        
        return {
            'lower': lower,
            'upper': upper,
            'lower_pct': f"{lower:.1f}%",
            'upper_pct': f"{upper:.1f}%",
            'range': f"{lower:.1f}% - {upper:.1f}%"
        }
    
    def _interpret_probability(self, probability: float) -> Dict[str, str]:
        """Interpret approval probability"""
        if probability >= 80:
            level = "VERY HIGH"
            level_kr = "매우 높음"
            description = "LH 승인 가능성이 매우 높습니다"
            color = "#28a745"
        elif probability >= 70:
            level = "HIGH"
            level_kr = "높음"
            description = "LH 승인 가능성이 높습니다"
            color = "#5cb85c"
        elif probability >= 60:
            level = "MEDIUM"
            level_kr = "중간"
            description = "조건 보완 시 승인 가능합니다"
            color = "#ffc107"
        else:
            level = "LOW"
            level_kr = "낮음"
            description = "구조 개선이 필요합니다"
            color = "#dc3545"
        
        return {
            'level': level,
            'level_kr': level_kr,
            'description': description,
            'color': color
        }
    
    def _generate_recommendation(self, probability: float, scores: Dict) -> List[str]:
        """Generate recommendations to improve approval probability"""
        recommendations = []
        
        # Check weak factors
        for factor, score in scores.items():
            if score < 70:
                rec = self._get_factor_recommendation(factor, score)
                if rec:
                    recommendations.append(rec)
        
        if not recommendations:
            recommendations.append("현재 구조 유지 및 실행")
        
        return recommendations[:3]  # Top 3 recommendations
    
    def _get_factor_recommendation(self, factor: str, score: float) -> str:
        """Get specific recommendation for weak factor"""
        recommendations_map = {
            'financial': f"재무 구조 개선 필요 (현재: {score:.0f}점)",
            'demand': f"수요 적합성 강화 필요 (현재: {score:.0f}점)",
            'market': f"시장 조건 개선 대기 또는 전략 수정 (현재: {score:.0f}점)",
            'policy': f"정책 우선순위 주택 유형 검토 (현재: {score:.0f}점)",
            'location': f"입지 조건 재평가 필요 (현재: {score:.0f}점)"
        }
        return recommendations_map.get(factor, "")


_lh_approval_model = None

def get_lh_approval_model() -> LHApprovalModel:
    """Get singleton instance"""
    global _lh_approval_model
    if _lh_approval_model is None:
        _lh_approval_model = LHApprovalModel()
    return _lh_approval_model
