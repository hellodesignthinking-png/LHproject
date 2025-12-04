"""
LH 신축매입임대 공고문 기준 심사 로직 v8.5
v8.5 LH Linked 모델 적용:
- ROI 기반 평가
- LH Purchase / Total Cost 비율
- Verified Cost 적정성
- 세대당 상한 제거
- Gap 모델 제거
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from app.services.lh_criteria_checker import (
    CheckItem, CheckStatus, Grade, GradeResult, LHCriteriaChecker
)


class LHCriteriaCheckerV85(LHCriteriaChecker):
    """
    LH 신축매입임대 기준 검증 v8.5
    LH LINKED 모델 적용
    """
    
    def __init__(self, custom_weights: Dict[str, float] = None, lh_version: str = "2025"):
        super().__init__(custom_weights, lh_version)
        self.model_type = "LH_LINKED"  # v8.5는 LH LINKED 모델만 사용
    
    def _check_financial(
        self,
        financial_data: Dict[str, Any],
        building_data: Dict[str, Any]
    ) -> List[CheckItem]:
        """
        사업성 기준 체크 (v8.5 LH LINKED 모델)
        
        평가 기준:
        1. ROI (Return on Investment): 0~20점
        2. LH Purchase / Total Cost 비율: 0~10점
        3. Verified Cost 적정성: 0~10점
        총 40점
        """
        checks = []
        
        # 1. ROI 기반 평가 (0~20점)
        roi = financial_data.get('roi', 0)
        
        if roi >= 15:
            status = CheckStatus.PASS
            score = 20
            desc = "우수한 투자 수익성 (ROI 15% 이상)"
        elif roi >= 10:
            status = CheckStatus.PASS
            score = 15
            desc = "양호한 투자 수익성 (ROI 10~15%)"
        elif roi >= 5:
            status = CheckStatus.WARNING
            score = 10
            desc = "보통 투자 수익성 (ROI 5~10%)"
        elif roi >= 0:
            status = CheckStatus.WARNING
            score = 5
            desc = "낮은 투자 수익성 (ROI 0~5%)"
        else:
            status = CheckStatus.FAIL
            score = 0
            desc = "투자 손실 예상 (ROI < 0%)"
        
        checks.append(CheckItem(
            category="사업성",
            item="ROI (투자수익률)",
            status=status,
            value=f"{roi:.2f}%",
            standard="≥ 15% 우수, ≥ 5% 양호",
            description=desc,
            score=score
        ))
        
        # 2. LH Purchase / Total Cost 비율 (0~10점)
        lh_purchase = financial_data.get('lh_purchase_price', 0)
        total_cost = financial_data.get('total_cost', 1)
        lh_ratio = (lh_purchase / total_cost * 100) if total_cost > 0 else 0
        
        if lh_ratio <= 100:
            status = CheckStatus.PASS
            score = 10
            desc = "LH 매입가가 총 사업비 이상 (사업성 확보)"
        elif lh_ratio <= 105:
            status = CheckStatus.WARNING
            score = 5
            desc = "LH 매입가가 총 사업비의 95~100% (사업성 주의)"
        else:
            status = CheckStatus.FAIL
            score = 0
            desc = "LH 매입가가 총 사업비 미달 (사업성 부족)"
        
        checks.append(CheckItem(
            category="사업성",
            item="LH 매입가 / 총사업비 비율",
            status=status,
            value=f"{lh_ratio:.1f}%",
            standard="≥ 100% (LH 매입가 ≥ 총사업비)",
            description=desc,
            score=score
        ))
        
        # 3. Verified Construction Cost 적정성 (0~10점)
        verified_cost = financial_data.get('verified_cost', 0)
        units = building_data.get('expected_units', 1)
        verified_cost_per_unit = verified_cost / units if units > 0 else 0
        
        # LH 공사비 연동제 적정 범위: 세대당 1.2~1.5억원
        if 120_000_000 <= verified_cost_per_unit <= 150_000_000:
            status = CheckStatus.PASS
            score = 10
            desc = "Verified Cost 적정 (LH 공사비 연동제 범위 내)"
        elif 100_000_000 <= verified_cost_per_unit < 120_000_000:
            status = CheckStatus.WARNING
            score = 7
            desc = "Verified Cost 낮음 (품질 저하 우려)"
        elif 150_000_000 < verified_cost_per_unit <= 180_000_000:
            status = CheckStatus.WARNING
            score = 7
            desc = "Verified Cost 높음 (사업비 부담 증가)"
        else:
            status = CheckStatus.FAIL
            score = 3
            desc = "Verified Cost 부적정 (LH 기준 초과/미달)"
        
        checks.append(CheckItem(
            category="사업성",
            item="Verified Construction Cost",
            status=status,
            value=f"{verified_cost_per_unit/100_000_000:.2f}억원/세대",
            standard="1.2~1.5억원/세대",
            description=desc,
            score=score
        ))
        
        # 4. 토지 감정가 적정성 (참고 사항, 점수 미반영)
        land_appraisal = financial_data.get('land_appraisal', 0)
        land_area = building_data.get('land_area', 1)
        land_price_per_sqm = land_appraisal / land_area if land_area > 0 else 0
        
        # 참고: 토지 감정가는 감정평가액 기준이므로 별도 평가 없음
        if land_price_per_sqm > 0:
            status = CheckStatus.INFO
            score = 0  # 점수 미반영
            desc = f"토지 감정가: {land_price_per_sqm/10000:.0f}만원/㎡ (참고)"
        else:
            status = CheckStatus.WARNING
            score = 0
            desc = "토지 감정가 정보 없음"
        
        checks.append(CheckItem(
            category="사업성",
            item="토지 감정가 (참고)",
            status=status,
            value=f"{land_appraisal/100_000_000:.1f}억원",
            standard="감정평가액 기준",
            description=desc,
            score=score
        ))
        
        return checks
    
    def get_financial_score_breakdown(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        재무 점수 상세 분석 (v8.5 전용)
        
        Returns:
            Dict with detailed score breakdown
        """
        roi = financial_data.get('roi', 0)
        lh_purchase = financial_data.get('lh_purchase_price', 0)
        total_cost = financial_data.get('total_cost', 1)
        verified_cost = financial_data.get('verified_cost', 0)
        
        # ROI 점수
        if roi >= 15:
            roi_score = 20
        elif roi >= 10:
            roi_score = 15
        elif roi >= 5:
            roi_score = 10
        elif roi >= 0:
            roi_score = 5
        else:
            roi_score = 0
        
        # LH 매입가 비율 점수
        lh_ratio = (lh_purchase / total_cost * 100) if total_cost > 0 else 0
        if lh_ratio <= 100:
            lh_ratio_score = 10
        elif lh_ratio <= 105:
            lh_ratio_score = 5
        else:
            lh_ratio_score = 0
        
        # Verified Cost 점수
        units = financial_data.get('expected_units', 1)
        verified_cost_per_unit = verified_cost / units if units > 0 else 0
        if 120_000_000 <= verified_cost_per_unit <= 150_000_000:
            verified_cost_score = 10
        elif 100_000_000 <= verified_cost_per_unit < 120_000_000 or 150_000_000 < verified_cost_per_unit <= 180_000_000:
            verified_cost_score = 7
        else:
            verified_cost_score = 3
        
        total_financial_score = roi_score + lh_ratio_score + verified_cost_score
        
        return {
            "roi_score": roi_score,
            "roi_value": roi,
            "lh_ratio_score": lh_ratio_score,
            "lh_ratio_value": lh_ratio,
            "verified_cost_score": verified_cost_score,
            "verified_cost_per_unit": verified_cost_per_unit,
            "total_financial_score": total_financial_score,
            "max_score": 40,
            "percentage": (total_financial_score / 40 * 100) if total_financial_score > 0 else 0
        }


# 테스트 함수
def test_lh_criteria_checker_v85():
    """v8.5 LH Criteria Checker 테스트"""
    checker = LHCriteriaCheckerV85()
    
    # 테스트 데이터
    test_financial = {
        "roi": -4.49,
        "lh_purchase_price": 22_145_790_240,
        "total_cost": 23_186_642_381,
        "verified_cost": 13_483_290_240,
        "land_appraisal": 8_662_500_000,
        "expected_units": 102
    }
    
    test_building = {
        "expected_units": 102,
        "land_area": 1500
    }
    
    # 재무 점수 분석
    breakdown = checker.get_financial_score_breakdown(test_financial)
    
    print("="*80)
    print("LH Criteria Checker v8.5 Test Results")
    print("="*80)
    print(f"\n1. ROI Score: {breakdown['roi_score']}/20 (ROI: {breakdown['roi_value']:.2f}%)")
    print(f"2. LH Ratio Score: {breakdown['lh_ratio_score']}/10 (Ratio: {breakdown['lh_ratio_value']:.1f}%)")
    print(f"3. Verified Cost Score: {breakdown['verified_cost_score']}/10 (Per Unit: {breakdown['verified_cost_per_unit']/100_000_000:.2f}억원)")
    print(f"\n📊 Total Financial Score: {breakdown['total_financial_score']}/40 ({breakdown['percentage']:.1f}%)")
    
    # 체크리스트
    checks = checker._check_financial(test_financial, test_building)
    print(f"\n📋 Financial Checklist:")
    for check in checks:
        print(f"  - {check.item}: {check.value} ({check.status.value}) - {check.score}점")
    
    return breakdown


if __name__ == "__main__":
    test_lh_criteria_checker_v85()
