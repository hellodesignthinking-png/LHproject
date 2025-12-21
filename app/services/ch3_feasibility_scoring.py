"""
CH3.3 Business Feasibility Scoring Module
ROI-based scoring system for financial viability assessment

Version: v8.7
Date: 2025-12-15

Problem Addressed:
- Previously: Static placeholder scores (3-5 points) regardless of actual ROI
- Now: Dynamic 0-20 point scale based on actual financial performance

Scoring Factors:
- ROI: Primary driver (0-20 points)
- Gap Ratio: Purchase vs Cost efficiency
- LH Linkage: Premium for 공사비 연동제
- Construction Cost: Appropriateness check
- Risk Factors: Deductions for high-risk elements
"""

from typing import Dict, Any, Optional


class CH3FeasibilityScorer:
    """
    CH3.3 사업성 점수 생성기 (ROI 기반)
    
    재무 실적에 기반하여 동적으로 사업성 점수를 산출
    """
    
    def __init__(self):
        """Initialize CH3 feasibility scorer"""
        pass
    
    def calculate_feasibility_score(
        self,
        roi: float,
        lh_purchase_price: float,
        total_project_cost: float,
        analysis_mode: str,
        expected_units: int,
        land_appraisal: float,
        verified_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate business feasibility score (0-20 points)
        
        Args:
            roi: Return on investment (%)
            lh_purchase_price: LH purchase price (원)
            total_project_cost: Total project cost (원)
            analysis_mode: 'LH_LINKED' or 'STANDARD'
            expected_units: Number of units
            land_appraisal: Land appraisal value (원)
            verified_cost: Verified construction cost (원, for LH_LINKED)
        
        Returns:
            Dictionary with score, grade, factors, and rationale
        """
        
        # 1. Base ROI score (0-20 points)
        roi_score = self._calculate_roi_score(roi)
        
        # 2. Gap ratio bonus/penalty (-3 to +3 points)
        gap_ratio = ((lh_purchase_price - total_project_cost) / total_project_cost) * 100
        gap_score = self._calculate_gap_score(gap_ratio)
        
        # 3. LH linkage bonus (0-2 points)
        linkage_score = self._calculate_linkage_score(analysis_mode, expected_units)
        
        # 4. Construction cost appropriateness (0-2 points)
        cost_score = self._calculate_cost_appropriateness_score(
            verified_cost=verified_cost,
            total_project_cost=total_project_cost,
            land_appraisal=land_appraisal,
            expected_units=expected_units
        )
        
        # 5. Calculate total score (capped at 0-20)
        total_score = roi_score + gap_score + linkage_score + cost_score
        total_score = max(0, min(20, total_score))
        
        # 6. Determine grade
        grade = self._determine_grade(total_score)
        
        # 7. Generate rationale
        rationale = self._generate_rationale(
            roi=roi,
            gap_ratio=gap_ratio,
            analysis_mode=analysis_mode,
            total_score=total_score
        )
        
        return {
            'total_score': int(total_score),
            'grade': grade,
            'factors': {
                'roi_score': roi_score,
                'gap_score': gap_score,
                'linkage_score': linkage_score,
                'cost_score': cost_score
            },
            'metrics': {
                'roi': roi,
                'gap_ratio': gap_ratio
            },
            'rationale': rationale
        }
    
    def _calculate_roi_score(self, roi: float) -> float:
        """
        Calculate base score from ROI (0-20 points)
        
        Scoring:
        - ROI >= 10%: 20 points (Excellent)
        - ROI 8-10%: 17-19 points (Very Good)
        - ROI 5-8%: 14-16 points (Good)
        - ROI 3-5%: 10-13 points (Fair)
        - ROI 0-3%: 5-9 points (Poor)
        - ROI < 0%: 0-4 points (Very Poor)
        """
        
        if roi >= 10.0:
            return 20.0
        elif roi >= 8.0:
            # Linear interpolation: 8% → 17, 10% → 20
            return 17.0 + (roi - 8.0) / 2.0 * 3.0
        elif roi >= 5.0:
            # Linear interpolation: 5% → 14, 8% → 17
            return 14.0 + (roi - 5.0) / 3.0 * 3.0
        elif roi >= 3.0:
            # Linear interpolation: 3% → 10, 5% → 14
            return 10.0 + (roi - 3.0) / 2.0 * 4.0
        elif roi >= 0.0:
            # Linear interpolation: 0% → 5, 3% → 10
            return 5.0 + (roi / 3.0) * 5.0
        else:
            # Negative ROI: scaled penalty
            # -5% → 0 points, 0% → 5 points
            return max(0.0, 5.0 + roi)  # roi is negative, so this subtracts
    
    def _calculate_gap_score(self, gap_ratio: float) -> float:
        """
        Calculate gap ratio bonus/penalty (-3 to +3 points)
        
        Gap Ratio = (LH Purchase - Total Cost) / Total Cost * 100
        
        Scoring:
        - Gap >= 5%: +3 points (Excellent margin)
        - Gap 2-5%: +1 to +2 points (Good margin)
        - Gap 0-2%: 0 to +1 points (Breakeven)
        - Gap -2-0%: -1 to 0 points (Small loss)
        - Gap < -2%: -2 to -3 points (Significant loss)
        """
        
        if gap_ratio >= 5.0:
            return 3.0
        elif gap_ratio >= 2.0:
            return 1.0 + (gap_ratio - 2.0) / 3.0 * 2.0
        elif gap_ratio >= 0.0:
            return gap_ratio / 2.0
        elif gap_ratio >= -2.0:
            return gap_ratio / 2.0
        else:
            return max(-3.0, -2.0 + (gap_ratio + 2.0) / 3.0 * (-1.0))
    
    def _calculate_linkage_score(self, analysis_mode: str, expected_units: int) -> float:
        """
        Calculate LH linkage bonus (0-2 points)
        
        LH_LINKED mode gets bonus for:
        - Using verified construction cost
        - 50+ units qualification
        - Metro region eligibility
        """
        
        if analysis_mode == 'LH_LINKED' and expected_units >= 50:
            return 2.0
        elif analysis_mode == 'LH_LINKED':
            return 1.0
        else:
            return 0.0
    
    def _calculate_cost_appropriateness_score(
        self,
        verified_cost: Optional[float],
        total_project_cost: float,
        land_appraisal: float,
        expected_units: int
    ) -> float:
        """
        Calculate construction cost appropriateness (0-2 points)
        
        Checks if construction cost is reasonable:
        - Not too high (cost < 80% of total)
        - Not too low (quality concerns)
        - Land/construction balance appropriate
        """
        
        if expected_units == 0:
            return 0.0
        
        # Calculate construction cost portion
        if verified_cost:
            construction_cost = verified_cost
        else:
            construction_cost = total_project_cost - land_appraisal
        
        cost_ratio = construction_cost / total_project_cost
        
        # Ideal range: 50-70% construction, 30-50% land
        if 0.50 <= cost_ratio <= 0.70:
            return 2.0
        elif 0.45 <= cost_ratio < 0.50 or 0.70 < cost_ratio <= 0.75:
            return 1.5
        elif 0.40 <= cost_ratio < 0.45 or 0.75 < cost_ratio <= 0.80:
            return 1.0
        else:
            return 0.5
    
    def _determine_grade(self, total_score: float) -> str:
        """
        Determine grade from total score
        
        - S: 18-20 points (Excellent)
        - A: 15-17 points (Very Good)
        - B: 12-14 points (Good)
        - C: 9-11 points (Fair)
        - D: 6-8 points (Poor)
        - F: 0-5 points (Fail)
        """
        
        if total_score >= 18:
            return 'S'
        elif total_score >= 15:
            return 'A'
        elif total_score >= 12:
            return 'B'
        elif total_score >= 9:
            return 'C'
        elif total_score >= 6:
            return 'D'
        else:
            return 'F'
    
    def _generate_rationale(
        self,
        roi: float,
        gap_ratio: float,
        analysis_mode: str,
        total_score: float
    ) -> str:
        """
        Generate human-readable rationale
        
        Returns:
            String explaining the score
        """
        
        parts = []
        
        # ROI commentary
        if roi >= 8.0:
            parts.append(f"우수한 수익률 ({roi:.1f}%)")
        elif roi >= 5.0:
            parts.append(f"양호한 수익률 ({roi:.1f}%)")
        elif roi >= 0.0:
            parts.append(f"낮은 수익률 ({roi:.1f}%)")
        else:
            parts.append(f"마이너스 수익률 ({roi:.1f}%)")
        
        # Gap ratio commentary
        if gap_ratio >= 2.0:
            parts.append("매입가 우위")
        elif gap_ratio >= 0.0:
            parts.append("손익분기 근처")
        else:
            parts.append("사업비 초과")
        
        # LH linkage
        if analysis_mode == 'LH_LINKED':
            parts.append("LH 연동제 적용")
        
        return ', '.join(parts)
    
    def format_for_report(self, feasibility_result: Dict[str, Any]) -> str:
        """
        Format feasibility score for report display
        
        Returns:
            Formatted string for CH3.3 section
        """
        
        grade_emoji = {
            'S': '🌟',
            'A': '⭐',
            'B': '✓',
            'C': '△',
            'D': '▽',
            'F': '✗'
        }.get(feasibility_result['grade'], '•')
        
        lines = []
        lines.append("\n### 3.3 사업성 평가")
        lines.append(f"\n**종합 점수**: {grade_emoji} {feasibility_result['total_score']}/20점 (등급: {feasibility_result['grade']})\n")
        
        lines.append("**점수 구성:**")
        factors = feasibility_result['factors']
        lines.append(f"- ROI 기반 점수: {factors['roi_score']:.1f}점")
        lines.append(f"- Gap Ratio 조정: {factors['gap_score']:+.1f}점")
        lines.append(f"- LH 연동 보너스: {factors['linkage_score']:+.1f}점")
        lines.append(f"- 공사비 적정성: {factors['cost_score']:+.1f}점")
        
        lines.append(f"\n**재무 지표:**")
        metrics = feasibility_result['metrics']
        lines.append(f"- ROI: {metrics['roi']:.2f}%")
        lines.append(f"- Gap Ratio: {metrics['gap_ratio']:.2f}%")
        
        lines.append(f"\n**평가**: {feasibility_result['rationale']}")
        
        return '\n'.join(lines)


def create_feasibility_scorer() -> CH3FeasibilityScorer:
    """
    Factory function to create feasibility scorer
    
    Returns:
        CH3FeasibilityScorer instance
    """
    return CH3FeasibilityScorer()


__all__ = [
    'CH3FeasibilityScorer',
    'create_feasibility_scorer'
]
