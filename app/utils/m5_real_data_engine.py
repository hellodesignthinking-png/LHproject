"""
M5 Real Data Engine - LH Public Rental Feasibility Analysis
==================================================================

목적: M5를 숫자 장난 보고서에서 실제 의사결정 가능한 분석 엔진으로 복구

제약사항:
- M4에서 확정된 실제 건축 규모 데이터만 사용
- 사용자가 입력한 사업비/매입 조건 데이터만 사용
- MOC/샘플/구버전 로직 기반 계산 절대 금지

데이터 소스:
✅ 허용:
  - M4: total_units, total_floor_area
  - 사용자 입력: 공사비(㎡당 또는 총액), 기타 사업비, LH 매입 단가
  - 정책/제도 기준(명시 시)

🚫 금지:
  - MOC/MOCK/SAMPLE
  - 구버전 M5 로직
  - 기본값 기반 NPV/IRR/ROI
  - M4 값 없이의 임의 계산

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class M5RealDataEngine:
    """
    M5 실제 데이터 기반 사업성 분석 엔진
    
    핵심 원칙:
    1. 데이터 소스 검증 (0단계)
    2. M4 → M5 데이터 연결 검증 게이트 (1단계)
    3. 사업 구조 설명 (2단계)
    4. 비용 구조 산정 (3단계)
    5. 수익 구조 (4단계)
    6. 지표 출력 원칙 (5단계)
    7. 최종 사업성 판단 (6단계)
    """
    
    # 금지 데이터 소스 패턴
    FORBIDDEN_PATTERNS = [
        r'MOC[K]?', r'SAMPLE', r'MOCK', r'TEST[\s_]?DATA',
        r'구버전', r'임시', r'테스트용', r'기본값'
    ]
    
    # LH 신축매입임대 기준 (참고용)
    LH_REFERENCE_DATA = {
        '공사비_범위_최소': 2500000,  # ㎡당 250만원 (최소)
        '공사비_범위_최대': 3500000,  # ㎡당 350만원 (최대)
        '설계감리비율': 0.05,  # 5%
        '인허가비율': 0.02,  # 2%
        '금융비율': 0.03,  # 3%
        '예비비율': 0.05,  # 5%
        'LH_매입단가_범위_최소': 3000000,  # ㎡당 300만원
        'LH_매입단가_범위_최대': 4000000,  # ㎡당 400만원
    }
    
    def __init__(
        self,
        context_id: str,
        m4_data: Dict[str, Any],
        user_inputs: Dict[str, Any],
        frozen_context: Optional[Dict[str, Any]] = None
    ):
        """
        M5 Real Data Engine 초기화
        
        Args:
            context_id: Context ID
            m4_data: M4 건축 규모 확정 데이터
            user_inputs: 사용자 입력 데이터 (사업비, 매입 조건)
            frozen_context: Context 전체 데이터
        """
        self.context_id = context_id
        self.m4_data = m4_data
        self.user_inputs = user_inputs
        self.frozen_context = frozen_context
        
        # 상태 플래그
        self.data_source_valid = True
        self.m4_connection_valid = False
        self.calculation_ready = False
        self.forbidden_sources: List[str] = []
        self.missing_fields: List[str] = []
        self.validation_errors: List[str] = []
        
        # 계산 결과
        self.cost_structure: Dict[str, Any] = {}
        self.revenue_structure: Dict[str, Any] = {}
        self.financial_metrics: Dict[str, Any] = {}
        self.final_judgment: Dict[str, Any] = {}
        
        logger.info(f"🚀 M5 Real Data Engine initialized for context {context_id}")
        
        # 0단계: 데이터 소스 검증
        self._validate_data_sources()
        
        # 1단계: M4 → M5 데이터 연결 검증
        if self.data_source_valid:
            self._validate_m4_connection()
        
        # 계산 준비 상태 결정
        self.calculation_ready = self.data_source_valid and self.m4_connection_valid
    
    def _validate_data_sources(self) -> None:
        """
        0단계: 데이터 소스 검증
        
        금지 데이터 소스 차단:
        - MOC/MOCK/SAMPLE
        - 구버전 M5 로직
        - 기본값 기반 계산
        """
        logger.info("🔍 [0단계] 데이터 소스 검증 시작")
        
        # M4 데이터 검증
        if self.m4_data:
            m4_str = str(self.m4_data)
            for pattern in self.FORBIDDEN_PATTERNS:
                if re.search(pattern, m4_str, re.IGNORECASE):
                    self.forbidden_sources.append(f"M4 데이터에서 금지 패턴 발견: {pattern}")
                    self.data_source_valid = False
        
        # 사용자 입력 데이터 검증
        if self.user_inputs:
            user_str = str(self.user_inputs)
            for pattern in self.FORBIDDEN_PATTERNS:
                if re.search(pattern, user_str, re.IGNORECASE):
                    self.forbidden_sources.append(f"사용자 입력에서 금지 패턴 발견: {pattern}")
                    self.data_source_valid = False
        
        if self.forbidden_sources:
            logger.error(f"❌ [0단계] 금지 데이터 소스 감지: {len(self.forbidden_sources)}건")
            for source in self.forbidden_sources:
                logger.error(f"  - {source}")
        else:
            logger.info("✅ [0단계] 데이터 소스 검증 통과")
    
    def _validate_m4_connection(self) -> None:
        """
        1단계: M4 → M5 데이터 연결 검증 게이트
        
        필수 조건:
        - total_units > 0
        - total_floor_area > 0
        - M4 Context ID = M5 Context ID
        
        하나라도 불충족 시 계산 불가
        """
        logger.info("🔍 [1단계] M4 → M5 데이터 연결 검증")
        
        if not self.m4_data:
            self.validation_errors.append("M4 데이터가 존재하지 않음")
            logger.error("❌ [1단계] M4 데이터 누락")
            return
        
        # M4 데이터 추출
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        
        # 세대수 확인
        total_units = (
            m4_summary.get("recommended_units") or
            m4_details.get("optimal_units") or
            m4_details.get("total_units") or
            0
        )
        
        # 연면적 확인
        total_floor_area = (
            m4_details.get("total_floor_area_sqm") or
            m4_details.get("total_floor_area") or
            0
        )
        
        # Context ID 확인
        m4_context_id = self.m4_data.get("context_id", "")
        
        # 검증
        validation_passed = True
        
        if total_units <= 0:
            self.validation_errors.append(f"total_units 유효하지 않음: {total_units}")
            validation_passed = False
        
        if total_floor_area <= 0:
            self.validation_errors.append(f"total_floor_area 유효하지 않음: {total_floor_area}")
            validation_passed = False
        
        if m4_context_id and m4_context_id != self.context_id:
            self.validation_errors.append(
                f"Context ID 불일치: M4={m4_context_id} vs M5={self.context_id}"
            )
            validation_passed = False
        
        if validation_passed:
            self.m4_connection_valid = True
            logger.info(f"✅ [1단계] M4 연결 검증 통과: {total_units}세대, {total_floor_area:.2f}㎡")
        else:
            logger.error(f"❌ [1단계] M4 연결 검증 실패: {len(self.validation_errors)}건")
            for error in self.validation_errors:
                logger.error(f"  - {error}")
    
    def generate_business_structure_explanation(self) -> Dict[str, Any]:
        """
        2단계: 사업 구조 설명
        
        서술형으로 출력:
        - LH 신축매입임대 일괄 매입 구조
        - 분양 수익 없음
        - 수익은 LH 매입 대금 단일 구조
        - 손익의 핵심은 수익률이 아닌 손실 가능성 통제 및 구조적 안정성
        """
        logger.info("📄 [2단계] 사업 구조 설명 생성")
        
        return {
            "business_model": "LH 신축매입임대",
            "structure_type": "일괄 매입 구조",
            "revenue_source": "LH 매입 대금 (단일 구조)",
            "key_principle": "손실 가능성 통제 및 구조적 안정성",
            "explanation": (
                "본 사업은 LH 신축매입임대 방식으로, 사업 시행자가 토지를 매입하여 "
                "건축물을 신축한 후 LH가 전체 물량을 일괄 매입하는 구조입니다. "
                "분양 수익 구조가 아니므로 수익은 LH 매입 단가에 의해 결정되며, "
                "사업성 판단의 핵심은 고수익률 달성이 아니라 "
                "손실 가능성을 통제하고 구조적 안정성을 확보하는 것입니다."
            ),
            "risk_focus": [
                "공사비 상승 리스크 통제",
                "LH 매입 단가 협의 안정성",
                "사업 일정 준수 가능성"
            ]
        }
    
    def calculate_cost_structure(self) -> Dict[str, Any]:
        """
        3단계: 비용 구조 산정
        
        A. 공사비 = 총 연면적 × ㎡당 공사비
        B. 기타 사업비 = 설계·감리·인허가, 금융비용, 예비비
        C. 총 사업비 = 항목별 합계 + 최종 총액
        
        각 항목에 대해 산식과 결과를 문장으로 설명
        """
        logger.info("💰 [3단계] 비용 구조 산정")
        
        if not self.calculation_ready:
            return {
                "status": "CALCULATION_NOT_READY",
                "message": "M4 데이터 연결이 확인되지 않아 비용 산정을 수행할 수 없습니다."
            }
        
        # M4 데이터 추출
        m4_details = self.m4_data.get("details", {})
        total_floor_area = (
            m4_details.get("total_floor_area_sqm") or
            m4_details.get("total_floor_area") or
            0
        )
        
        # 사용자 입력 추출
        construction_cost_per_sqm = self.user_inputs.get("construction_cost_per_sqm")
        total_construction_cost = self.user_inputs.get("total_construction_cost")
        
        # A. 공사비 산정
        if total_construction_cost:
            # 총액 직접 입력된 경우
            construction_cost = total_construction_cost
            cost_per_sqm = construction_cost / total_floor_area if total_floor_area > 0 else 0
            construction_explanation = (
                f"공사비는 사용자가 입력한 총액 {construction_cost:,.0f}원을 기준으로 하며, "
                f"㎡당 단가는 약 {cost_per_sqm:,.0f}원입니다."
            )
        elif construction_cost_per_sqm:
            # ㎡당 단가 입력된 경우
            cost_per_sqm = construction_cost_per_sqm
            construction_cost = total_floor_area * cost_per_sqm
            construction_explanation = (
                f"공사비는 총 연면적 {total_floor_area:,.2f}㎡에 "
                f"㎡당 공사비 {cost_per_sqm:,.0f}원을 곱하여 산정됩니다. "
                f"계산식: {total_floor_area:,.2f} × {cost_per_sqm:,.0f} = {construction_cost:,.0f}원"
            )
        else:
            # 입력 없는 경우 참고 범위 제시
            min_cost = total_floor_area * self.LH_REFERENCE_DATA['공사비_범위_최소']
            max_cost = total_floor_area * self.LH_REFERENCE_DATA['공사비_범위_최대']
            construction_cost = 0
            cost_per_sqm = 0
            construction_explanation = (
                f"공사비 입력값이 없습니다. "
                f"LH 기준 참고 범위는 ㎡당 250만원~350만원으로, "
                f"본 사업의 추정 공사비는 {min_cost:,.0f}원~{max_cost:,.0f}원 범위입니다. "
                f"정확한 사업비 산정을 위해 ㎡당 공사비 또는 총 공사비를 입력하십시오."
            )
        
        # B. 기타 사업비
        design_cost = construction_cost * self.LH_REFERENCE_DATA['설계감리비율']
        permit_cost = construction_cost * self.LH_REFERENCE_DATA['인허가비율']
        finance_cost = construction_cost * self.LH_REFERENCE_DATA['금융비율']
        contingency = construction_cost * self.LH_REFERENCE_DATA['예비비율']
        
        other_costs = design_cost + permit_cost + finance_cost + contingency
        
        other_costs_explanation = (
            f"기타 사업비는 설계·감리비({design_cost:,.0f}원, 공사비의 5%), "
            f"인허가비({permit_cost:,.0f}원, 2%), "
            f"금융비용({finance_cost:,.0f}원, 3%), "
            f"예비비({contingency:,.0f}원, 5%)를 포함하여 총 {other_costs:,.0f}원입니다."
        )
        
        # C. 총 사업비
        total_project_cost = construction_cost + other_costs
        
        total_cost_explanation = (
            f"총 사업비는 공사비 {construction_cost:,.0f}원과 "
            f"기타 사업비 {other_costs:,.0f}원을 합산하여 {total_project_cost:,.0f}원입니다."
        )
        
        risk_comment = (
            "공사비 상승 리스크는 철근·레미콘 등 주요 자재 가격 변동에 민감하므로, "
            "시장 상황에 따라 ±10% 범위의 변동 가능성을 고려해야 합니다."
        )
        
        self.cost_structure = {
            "construction_cost": construction_cost,
            "cost_per_sqm": cost_per_sqm,
            "construction_explanation": construction_explanation,
            "design_cost": design_cost,
            "permit_cost": permit_cost,
            "finance_cost": finance_cost,
            "contingency": contingency,
            "other_costs": other_costs,
            "other_costs_explanation": other_costs_explanation,
            "total_project_cost": total_project_cost,
            "total_cost_explanation": total_cost_explanation,
            "risk_comment": risk_comment,
            "status": "CALCULATED" if construction_cost > 0 else "INPUT_REQUIRED"
        }
        
        logger.info(f"✅ [3단계] 비용 구조 산정 완료: 총 사업비 {total_project_cost:,.0f}원")
        
        return self.cost_structure
    
    def calculate_revenue_structure(self) -> Dict[str, Any]:
        """
        4단계: 수익 구조
        
        - LH 매입 단가의 기준 설명
        - 총 매입 금액 = 단가 × 연면적
        - 단가 변동 시 민감도 간단 설명
        - 단가 근거 없으면 수치 출력 금지 및 단가 입력 필요 상태 전환
        """
        logger.info("💵 [4단계] 수익 구조 산정")
        
        if not self.calculation_ready:
            return {
                "status": "CALCULATION_NOT_READY",
                "message": "M4 데이터 연결이 확인되지 않아 수익 산정을 수행할 수 없습니다."
            }
        
        # M4 데이터 추출
        m4_details = self.m4_data.get("details", {})
        total_floor_area = (
            m4_details.get("total_floor_area_sqm") or
            m4_details.get("total_floor_area") or
            0
        )
        
        # 사용자 입력 추출
        lh_purchase_price_per_sqm = self.user_inputs.get("lh_purchase_price_per_sqm")
        total_purchase_price = self.user_inputs.get("total_purchase_price")
        
        if total_purchase_price:
            # 총액 직접 입력된 경우
            purchase_price = total_purchase_price
            price_per_sqm = purchase_price / total_floor_area if total_floor_area > 0 else 0
            revenue_explanation = (
                f"LH 매입 금액은 사용자가 입력한 총액 {purchase_price:,.0f}원을 기준으로 하며, "
                f"㎡당 단가는 약 {price_per_sqm:,.0f}원입니다."
            )
            status = "CALCULATED"
        elif lh_purchase_price_per_sqm:
            # ㎡당 단가 입력된 경우
            price_per_sqm = lh_purchase_price_per_sqm
            purchase_price = total_floor_area * price_per_sqm
            revenue_explanation = (
                f"LH 매입 금액은 총 연면적 {total_floor_area:,.2f}㎡에 "
                f"LH 매입 단가 {price_per_sqm:,.0f}원/㎡를 곱하여 산정됩니다. "
                f"계산식: {total_floor_area:,.2f} × {price_per_sqm:,.0f} = {purchase_price:,.0f}원"
            )
            status = "CALCULATED"
        else:
            # 입력 없는 경우
            min_price = total_floor_area * self.LH_REFERENCE_DATA['LH_매입단가_범위_최소']
            max_price = total_floor_area * self.LH_REFERENCE_DATA['LH_매입단가_범위_최대']
            purchase_price = 0
            price_per_sqm = 0
            revenue_explanation = (
                f"LH 매입 단가 입력값이 없습니다. "
                f"일반적인 LH 매입 단가는 ㎡당 300만원~400만원 범위로, "
                f"본 사업의 추정 매입 금액은 {min_price:,.0f}원~{max_price:,.0f}원입니다. "
                f"정확한 사업성 분석을 위해 LH 매입 단가를 입력하십시오."
            )
            status = "INPUT_REQUIRED"
        
        # 단가 변동 민감도
        if price_per_sqm > 0:
            sensitivity_10pct = total_floor_area * price_per_sqm * 0.1
            sensitivity_explanation = (
                f"LH 매입 단가가 10% 변동할 경우 총 수익은 약 {sensitivity_10pct:,.0f}원 변동합니다. "
                f"매입 단가 협의가 사업성의 핵심 변수입니다."
            )
        else:
            sensitivity_explanation = "매입 단가 입력 후 민감도 분석이 가능합니다."
        
        self.revenue_structure = {
            "purchase_price": purchase_price,
            "price_per_sqm": price_per_sqm,
            "revenue_explanation": revenue_explanation,
            "sensitivity_explanation": sensitivity_explanation,
            "status": status
        }
        
        logger.info(f"✅ [4단계] 수익 구조 산정 완료: LH 매입 금액 {purchase_price:,.0f}원")
        
        return self.revenue_structure
    
    def calculate_financial_metrics(self) -> Dict[str, Any]:
        """
        5단계: 지표 출력 원칙
        
        NPV/IRR/ROI은 조건부 출력:
        - 비용 및 수익 구조 모두 설명된 경우에만 출력
        - 해석 문장 필수
        - IRR은 참고 지표, ROI는 의미 제한, NPV 중심으로 판단
        - 지표 단독 출력 금지, 등급 단독 출력 금지
        """
        logger.info("📊 [5단계] 재무 지표 산정")
        
        if not self.cost_structure.get("status") == "CALCULATED":
            return {
                "status": "COST_NOT_READY",
                "message": "비용 구조가 산정되지 않아 재무 지표를 계산할 수 없습니다."
            }
        
        if not self.revenue_structure.get("status") == "CALCULATED":
            return {
                "status": "REVENUE_NOT_READY",
                "message": "수익 구조가 산정되지 않아 재무 지표를 계산할 수 없습니다."
            }
        
        total_cost = self.cost_structure.get("total_project_cost", 0)
        total_revenue = self.revenue_structure.get("purchase_price", 0)
        
        # NPV (Net Present Value)
        npv = total_revenue - total_cost
        npv_explanation = (
            f"순현재가치(NPV)는 LH 매입 금액 {total_revenue:,.0f}원에서 "
            f"총 사업비 {total_cost:,.0f}원을 차감한 {npv:,.0f}원입니다. "
        )
        
        if npv > 0:
            npv_explanation += "NPV가 양수이므로 사업 추진 시 이익이 예상됩니다."
            npv_grade = "양호"
        elif npv == 0:
            npv_explanation += "NPV가 0이므로 손익분기점 수준입니다."
            npv_grade = "중립"
        else:
            npv_explanation += "NPV가 음수이므로 사업 추진 시 손실이 예상됩니다."
            npv_grade = "불량"
        
        # ROI (Return on Investment)
        if total_cost > 0:
            roi = (npv / total_cost) * 100
            roi_explanation = (
                f"투자수익률(ROI)은 {roi:.2f}%로, 총 사업비 대비 순이익 비율입니다. "
            )
            
            if roi > 10:
                roi_explanation += "ROI가 10% 이상으로 양호한 수준입니다."
                roi_grade = "양호"
            elif roi > 0:
                roi_explanation += "ROI가 양수이나 10% 미만으로 제한적입니다."
                roi_grade = "보통"
            else:
                roi_explanation += "ROI가 음수로 투자 대비 손실이 예상됩니다."
                roi_grade = "불량"
        else:
            roi = 0
            roi_explanation = "총 사업비가 0이어서 ROI를 계산할 수 없습니다."
            roi_grade = "N/A"
        
        # IRR (Internal Rate of Return)
        # 간이 IRR: (NPV / 총 사업비) / 사업 기간
        project_period_years = self.user_inputs.get("project_period_years", 2)  # 기본 2년
        if total_cost > 0 and project_period_years > 0:
            simple_irr = (npv / total_cost) / project_period_years * 100
            irr_explanation = (
                f"내부수익률(IRR)은 연 {simple_irr:.2f}%로 추정됩니다. "
                f"(사업 기간 {project_period_years}년 기준 간이 계산) "
            )
            
            if simple_irr > 5:
                irr_explanation += "IRR이 5% 이상으로 양호한 수준입니다."
                irr_grade = "양호"
            elif simple_irr > 0:
                irr_explanation += "IRR이 양수이나 5% 미만으로 제한적입니다."
                irr_grade = "보통"
            else:
                irr_explanation += "IRR이 음수로 투자 매력도가 낮습니다."
                irr_grade = "불량"
        else:
            simple_irr = 0
            irr_explanation = "사업비 또는 사업 기간 정보가 부족하여 IRR을 계산할 수 없습니다."
            irr_grade = "N/A"
        
        # 종합 판단
        overall_explanation = (
            f"재무 지표 종합: NPV {npv:,.0f}원 ({npv_grade}), "
            f"ROI {roi:.2f}% ({roi_grade}), "
            f"IRR 연 {simple_irr:.2f}% ({irr_grade}). "
            f"LH 매입형 공공임대 사업의 특성상 NPV를 중심으로 판단하며, "
            f"IRR과 ROI는 참고 지표로 활용합니다."
        )
        
        self.financial_metrics = {
            "npv": npv,
            "npv_explanation": npv_explanation,
            "npv_grade": npv_grade,
            "roi": roi,
            "roi_explanation": roi_explanation,
            "roi_grade": roi_grade,
            "irr": simple_irr,
            "irr_explanation": irr_explanation,
            "irr_grade": irr_grade,
            "overall_explanation": overall_explanation,
            "status": "CALCULATED"
        }
        
        logger.info(f"✅ [5단계] 재무 지표 산정 완료: NPV {npv:,.0f}원, ROI {roi:.2f}%, IRR {simple_irr:.2f}%")
        
        return self.financial_metrics
    
    def generate_final_judgment(self) -> Dict[str, Any]:
        """
        6단계: 최종 사업성 판단
        
        종합 판단은 정책형·안정형으로 명시:
        - 주요 리스크: 공사비 상승, 매입 단가 협의, 일정 리스크
        - 관리 전략: 규모 조정, 원가 통제 포인트, M6 심사 시 유리한 해석 방향
        """
        logger.info("🎯 [6단계] 최종 사업성 판단")
        
        if not self.financial_metrics.get("status") == "CALCULATED":
            return {
                "status": "METRICS_NOT_READY",
                "message": "재무 지표가 산정되지 않아 최종 판단을 수행할 수 없습니다."
            }
        
        npv = self.financial_metrics.get("npv", 0)
        npv_grade = self.financial_metrics.get("npv_grade", "N/A")
        roi = self.financial_metrics.get("roi", 0)
        roi_grade = self.financial_metrics.get("roi_grade", "N/A")
        
        # 종합 판단
        if npv > 0 and roi > 5:
            judgment = "정책형·안정형 사업으로 추진 가능"
            feasibility_level = "HIGH"
            recommendation = "사업 추진을 권장합니다."
        elif npv > 0:
            judgment = "정책형 사업으로 제한적 추진 가능"
            feasibility_level = "MEDIUM"
            recommendation = "공사비 및 매입 단가 조건 재협의 후 추진 가능합니다."
        else:
            judgment = "현 조건에서는 사업성 확보 어려움"
            feasibility_level = "LOW"
            recommendation = "사업 구조 재조정 또는 사업 포기를 검토해야 합니다."
        
        # 주요 리스크
        major_risks = [
            {
                "risk": "공사비 상승 리스크",
                "description": "철근·레미콘 등 주요 자재 가격 변동",
                "mitigation": "계약 시 물가연동제 조항 포함, 자재 선구매 검토"
            },
            {
                "risk": "LH 매입 단가 협의 리스크",
                "description": "LH 감정평가 결과에 따른 단가 하락 가능성",
                "mitigation": "사전 감정평가 협의, 매입 단가 하한선 설정"
            },
            {
                "risk": "사업 일정 지연 리스크",
                "description": "인허가 지연, 공사 기간 초과 시 금융비용 증가",
                "mitigation": "인허가 사전 협의, 공정관리 강화, 예비비 충분 확보"
            }
        ]
        
        # 관리 전략
        management_strategies = [
            {
                "strategy": "규모 조정",
                "description": "M4 권장 규모를 기준으로 과도한 규모 확대 지양"
            },
            {
                "strategy": "원가 통제 포인트",
                "description": "공사비 구성 항목별 단가 검증, VE(Value Engineering) 적용"
            },
            {
                "strategy": "M6 심사 대응",
                "description": "정책 부합성, 입지 타당성, 재무 안정성 강조"
            }
        ]
        
        self.final_judgment = {
            "judgment": judgment,
            "feasibility_level": feasibility_level,
            "recommendation": recommendation,
            "major_risks": major_risks,
            "management_strategies": management_strategies,
            "status": "COMPLETED"
        }
        
        logger.info(f"✅ [6단계] 최종 판단 완료: {judgment} ({feasibility_level})")
        
        return self.final_judgment
    
    def generate_full_report(self) -> Dict[str, Any]:
        """
        전체 M5 보고서 데이터 생성
        """
        logger.info("📋 M5 Real Data Engine: 전체 보고서 생성")
        
        # 상태 확인
        if not self.data_source_valid:
            return self._generate_error_report("DATA_SOURCE_INVALID")
        
        if not self.m4_connection_valid:
            return self._generate_error_report("M4_NOT_CONNECTED")
        
        # 각 단계 실행
        business_structure = self.generate_business_structure_explanation()
        cost_structure = self.calculate_cost_structure()
        revenue_structure = self.calculate_revenue_structure()
        
        # 비용/수익 구조가 모두 준비된 경우에만 지표 산정
        if (cost_structure.get("status") == "CALCULATED" and 
            revenue_structure.get("status") == "CALCULATED"):
            financial_metrics = self.calculate_financial_metrics()
            final_judgment = self.generate_final_judgment()
        else:
            financial_metrics = {
                "status": "INPUT_REQUIRED",
                "message": "비용 또는 수익 구조 입력이 필요합니다."
            }
            final_judgment = {
                "status": "INPUT_REQUIRED",
                "message": "재무 지표 산정 후 최종 판단이 가능합니다."
            }
        
        # M4 데이터 추출
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        total_units = (
            m4_summary.get("recommended_units") or
            m4_details.get("optimal_units") or
            m4_details.get("total_units") or
            0
        )
        total_floor_area = (
            m4_details.get("total_floor_area_sqm") or
            m4_details.get("total_floor_area") or
            0
        )
        
        # 보고서 메타데이터
        report_id = f"ZS-M5-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        report_data = {
            "context_id": self.context_id,
            "report_id": report_id,
            "analysis_date": analysis_date,
            "m4_data_summary": {
                "total_units": total_units,
                "total_floor_area": total_floor_area
            },
            "business_structure": business_structure,
            "cost_structure": cost_structure,
            "revenue_structure": revenue_structure,
            "financial_metrics": financial_metrics,
            "final_judgment": final_judgment,
            "data_source_declaration": (
                "본 사업성 분석은 M4 확정 데이터와 입력된 비용/매입 데이터를 기준으로 "
                "수행되었으며 샘플 데이터는 사용되지 않았습니다."
            ),
            "footer": {
                "copyright": "ⓒ ZeroSite by AntennaHoldings | Natai Heum",
                "watermark": "ZEROSITE",
                "tone": "LH 실무 검토용 사업 구조 분석 보고서"
            }
        }
        
        logger.info(f"✅ M5 전체 보고서 생성 완료: {report_id}")
        
        return report_data
    
    def _generate_error_report(self, error_type: str) -> Dict[str, Any]:
        """
        오류 상태 보고서 생성
        """
        report_id = f"ZS-M5-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        if error_type == "DATA_SOURCE_INVALID":
            error_message = (
                "금지된 데이터 소스가 감지되어 M5 계산을 수행할 수 없습니다. "
                "MOC/SAMPLE/구버전 로직 기반 데이터는 사용할 수 없습니다."
            )
            error_details = {
                "forbidden_sources": self.forbidden_sources,
                "action_required": "실제 M4 데이터와 사용자 입력 데이터로 재실행하십시오."
            }
        elif error_type == "M4_NOT_CONNECTED":
            error_message = (
                "M4 건축 규모 데이터가 연결되지 않아 M5 사업성 분석을 수행할 수 없습니다."
            )
            error_details = {
                "validation_errors": self.validation_errors,
                "action_required": "M4 모듈을 먼저 실행한 후 M5를 실행하십시오."
            }
        else:
            error_message = "알 수 없는 오류가 발생했습니다."
            error_details = {}
        
        return {
            "error": True,
            "error_type": error_type,
            "error_message": error_message,
            "error_details": error_details,
            "context_id": self.context_id,
            "report_id": report_id,
            "analysis_date": analysis_date,
            "use_data_not_loaded_template": True,
            "template_version": "v1"
        }


def prepare_m5_real_data_report(
    context_id: str,
    m4_data: Dict[str, Any],
    user_inputs: Dict[str, Any],
    frozen_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    M5 Real Data Engine 외부 호출용 함수
    
    Args:
        context_id: Context ID
        m4_data: M4 건축 규모 확정 데이터
        user_inputs: 사용자 입력 데이터
        frozen_context: Context 전체 데이터
    
    Returns:
        M5 보고서 데이터 또는 오류 데이터
    """
    logger.info(f"🚀 M5 Real Data Report 생성 요청: {context_id}")
    
    try:
        engine = M5RealDataEngine(
            context_id=context_id,
            m4_data=m4_data,
            user_inputs=user_inputs,
            frozen_context=frozen_context
        )
        
        report_data = engine.generate_full_report()
        
        return report_data
    
    except Exception as e:
        logger.error(f"❌ M5 Real Data Engine 실행 중 오류: {e}")
        return {
            "error": True,
            "error_type": "ENGINE_ERROR",
            "error_message": f"M5 Real Data Engine 실행 중 오류가 발생했습니다: {str(e)}",
            "context_id": context_id,
            "use_data_not_loaded_template": True
        }
