"""
M5 Enhanced Feasibility Analysis Logic - LH Public Rental Project
====================================================================

사용자 요구사항 10가지 Hard Stop 규칙:
1. 필수 데이터 없으면 분석 수행 불가
2. IRR, ROI, NPV 중 2개 이상 계산 불가 시 지표 출력 금지
3. IRR = 0.0%일 때 ROI, NPV 출력 금지
4. "N/A 등급" 상태에서 긍정/부정 평가 금지
5. 데이터 소스: M4 결과 + LH 기준만
6. 재무 구조 먼저 명시 (숫자 이전)
7. 지표별 계산 조건 충족 시에만 출력
8. 사업성 등급 산정 로직 강제
9. M6 연계 문장 필수
10. 기술 오류 제거

🔴 데이터 바인딩 복구 강화 (2026-01-11 추가):
- M4 데이터 연결 상태 진단
- Context ID 기반 M4 결과 재조회
- M5 계산 실행 조건 Gate 검증

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
import math

# 🔴 데이터 바인딩 복구 모듈 Import
try:
    from app.utils.data_binding_recovery import apply_data_binding_recovery
    DATA_BINDING_RECOVERY_AVAILABLE = True
except ImportError:
    DATA_BINDING_RECOVERY_AVAILABLE = False
    logging.warning("⚠️ data_binding_recovery module not available")

logger = logging.getLogger(__name__)


class M5EnhancedAnalyzer:
    """
    M5 사업성 분석 보고서를 위한 고도화된 재무 분석 엔진
    - LH 매입형 공공임대 사업 특화
    - 데이터 무결성 Hard Gate
    - 재무 지표 간 논리 일관성 보장
    """
    
    def __init__(
        self, 
        context_id: str, 
        m4_data: Dict[str, Any], 
        module_data: Dict[str, Any],
        frozen_context: Optional[Dict[str, Any]] = None
    ):
        self.context_id = context_id
        self.m4_data = m4_data
        self.summary = module_data.get("summary", {})
        self.details = module_data.get("details", {})
        self.raw_data = module_data
        self.frozen_context = frozen_context
        
        # 🔴 데이터 바인딩 복구 실행 (M4 데이터 연결 확인)
        if DATA_BINDING_RECOVERY_AVAILABLE and frozen_context:
            logger.info(f"🔄 M5: Checking M4 data binding for {context_id}")
            
            # M4 데이터 검증
            m4_valid = self._validate_m4_data_connection()
            
            if not m4_valid:
                logger.warning(f"⚠️ M5: M4 data connection issue detected")
                
                # M4 데이터 재조회 시도
                m4_result = frozen_context.get("M4", {})
                if m4_result:
                    self.m4_data = m4_result.get("result", {})
                    logger.info(f"✅ M5: M4 data recovered from frozen context")
                else:
                    logger.error(f"❌ M5: M4 data recovery failed")
                    self.binding_error = True
                    self.binding_error_message = "M4 건축규모 데이터가 연결되지 않았습니다."
                    return
        
        self.binding_error = False
        self.binding_error_message = None
    
    def _validate_m4_data_connection(self) -> bool:
        """M4 데이터 연결 상태 검증"""
        if not self.m4_data or len(self.m4_data) == 0:
            logger.warning(f"⚠️ M5: M4 data is empty")
            return False
        
        # 필수 필드 확인
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        
        unit_count = m4_summary.get("recommended_units") or m4_details.get("optimal_units")
        total_floor_area = m4_details.get("total_floor_area_sqm")
        
        if not unit_count or not total_floor_area:
            logger.warning(f"⚠️ M5: M4 required fields missing")
            return False
        
        return True
        
    def validate_required_data(self) -> Tuple[bool, List[str]]:
        """
        Hard Stop 규칙 1: 필수 데이터 검증 (DATA NOT LOADED 체크 포함)
        
        Returns:
            Tuple[bool, List[str]]: (검증 통과 여부, 누락 항목 리스트)
        """
        missing_items = []
        
        # 🔴 CRITICAL: M4 데이터 로딩 체크
        if not self.m4_data or len(self.m4_data) == 0:
            logger.error("🔴 M5 DATA NOT LOADED: M4 데이터가 전혀 로딩되지 않음")
            return (False, ["M4 건축규모 결과 전체"])
        
        # M4에서 가져와야 할 데이터
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        
        # 1. 총 세대수 (M4 필수 연계)
        unit_count = m4_summary.get("recommended_units") or m4_details.get("optimal_units")
        if not unit_count or unit_count == 0:
            missing_items.append("총 세대수 (M4 결과)")
            logger.warning(f"🔴 M5 DATA NOT LOADED: 총 세대수 누락")
            
        # 2. 총 연면적 (M4 필수 연계)
        total_floor_area = m4_details.get("total_floor_area_sqm") or m4_details.get("scenario_b", {}).get("total_floor_area")
        if not total_floor_area:
            missing_items.append("총 연면적 (M4 결과)")
            logger.warning(f"🔴 M5 DATA NOT LOADED: 총 연면적 누락")
            
        # 3. LH 매입 단가 또는 산정 기준
        lh_price_per_unit = self.details.get("lh_price_per_unit")
        lh_price_per_sqm = self.details.get("lh_price_per_sqm")
        if not lh_price_per_unit and not lh_price_per_sqm:
            missing_items.append("LH 매입 단가 또는 단가 산정 기준")
            logger.warning(f"🔴 M5 DATA NOT LOADED: LH 매입 단가 누락")
            
        # 4. 총 사업비
        total_cost = self.details.get("total_cost") or self.details.get("total_investment")
        if not total_cost or total_cost == 0:
            missing_items.append("총 사업비(공사비 + 기타비용)")
            logger.warning(f"🔴 M5 DATA NOT LOADED: 총 사업비 누락")
        
        # 🔴 DATA NOT LOADED: 1개라도 누락 시
        if len(missing_items) >= 1:
            logger.error(f"🔴 M5 DATA NOT LOADED: {len(missing_items)}개 필수 입력 누락 - {missing_items}")
            logger.error(f"📍 위 항목 중 1개라도 누락 시 사업성 분석은 수행되지 않는다.")
            return (False, missing_items)
            
        is_valid = len(missing_items) == 0
        return is_valid, missing_items
    
    def calculate_financial_metrics(self) -> Dict[str, Any]:
        """
        Hard Stop 규칙 2, 3: 재무 지표 계산 (조건부)
        
        Returns:
            Dict with:
            - npv: Optional[float]
            - irr: Optional[float]
            - roi: Optional[float]
            - calculable_metrics_count: int
            - calculation_notes: List[str]
        """
        metrics = {
            "npv": None,
            "irr": None,
            "roi": None,
            "calculable_metrics_count": 0,
            "calculation_notes": []
        }
        
        # M4 데이터 추출
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        
        unit_count = m4_summary.get("recommended_units") or m4_details.get("optimal_units") or 20
        total_floor_area = m4_details.get("total_floor_area_sqm") or 1000.0
        
        # 사업비 계산
        construction_cost = self.details.get("construction_cost", 0)
        other_costs = self.details.get("other_costs", 0)
        total_investment = construction_cost + other_costs
        
        if total_investment == 0:
            # Fallback: 연면적 기반 추정
            cost_per_sqm = 3500000  # 평당 약 1,155만원
            total_investment = total_floor_area * cost_per_sqm
            metrics["calculation_notes"].append(
                f"총 사업비가 명시되지 않아 연면적 기준({total_floor_area:,.0f}㎡ × {cost_per_sqm:,}원/㎡)으로 추정"
            )
        
        # LH 매입 수익 계산
        lh_price_per_unit = self.details.get("lh_price_per_unit")
        lh_price_per_sqm = self.details.get("lh_price_per_sqm")
        
        if lh_price_per_unit:
            lh_revenue = lh_price_per_unit * unit_count
        elif lh_price_per_sqm:
            lh_revenue = lh_price_per_sqm * total_floor_area
        else:
            # Fallback: 세대당 평균 매입 단가 (청년형 기준)
            avg_lh_price = 180000000  # 1.8억/세대
            lh_revenue = avg_lh_price * unit_count
            metrics["calculation_notes"].append(
                f"LH 매입 단가가 명시되지 않아 청년형 평균 단가({avg_lh_price:,}원/세대)로 추정"
            )
        
        # NPV 계산 시도
        try:
            discount_rate = self.details.get("discount_rate", 0.05)  # 5% 기본
            construction_period_years = self.details.get("construction_period", 2)  # 2년 기본
            
            # 현금흐름: 초기 투자(음수) → 완공 후 LH 매입(양수)
            cash_flows = [-total_investment]
            for _ in range(construction_period_years):
                cash_flows.append(0)
            cash_flows[-1] = lh_revenue
            
            # NPV 계산
            npv = sum(cf / ((1 + discount_rate) ** i) for i, cf in enumerate(cash_flows))
            metrics["npv"] = npv
            metrics["calculable_metrics_count"] += 1
            
        except Exception as e:
            logger.error(f"NPV 계산 실패: {e}")
            metrics["calculation_notes"].append("NPV 계산 중 오류 발생")
        
        # IRR 계산 시도
        try:
            # LH 매입형은 IRR 계산에 구조적 한계
            # (분양과 달리 단일 시점 수익이므로 IRR이 극단적으로 나옴)
            if len(cash_flows) >= 2 and cash_flows[0] < 0 and cash_flows[-1] > 0:
                # 단순 수익률로 근사 (정확한 IRR 아님)
                total_return = (lh_revenue - total_investment) / total_investment
                approx_irr = total_return / construction_period_years
                
                if approx_irr > -0.5 and approx_irr < 1.0:  # 합리적 범위
                    metrics["irr"] = approx_irr
                    metrics["calculable_metrics_count"] += 1
                    metrics["calculation_notes"].append(
                        "IRR은 LH 매입형 구조상 정확한 내부수익률이 아닌 연평균 수익률로 근사"
                    )
                else:
                    metrics["calculation_notes"].append(
                        "IRR 산정이 LH 매입형 사업 구조상 제한됨 (단일 시점 수익)"
                    )
            else:
                metrics["calculation_notes"].append(
                    "현금흐름 데이터 부족으로 IRR 산정 불가"
                )
        except Exception as e:
            logger.error(f"IRR 계산 실패: {e}")
            metrics["calculation_notes"].append("IRR 계산 중 오류 발생")
        
        # ROI 계산 시도
        try:
            if total_investment > 0:
                roi = (lh_revenue - total_investment) / total_investment
                metrics["roi"] = roi
                metrics["calculable_metrics_count"] += 1
        except Exception as e:
            logger.error(f"ROI 계산 실패: {e}")
            metrics["calculation_notes"].append("ROI 계산 중 오류 발생")
        
        # Hard Stop 규칙 2: 2개 이상 계산 불가 시 지표 전체 삭제
        if metrics["calculable_metrics_count"] < 2:
            metrics["npv"] = None
            metrics["irr"] = None
            metrics["roi"] = None
            metrics["calculation_notes"].append(
                "⚠️ 계산 가능한 재무 지표가 2개 미만이므로, 정량 분석 대신 정성 판단을 수행합니다."
            )
        
        # Hard Stop 규칙 3: IRR = 0.0% 또는 None일 때 ROI, NPV 출력 금지
        if metrics["irr"] is None or abs(metrics["irr"]) < 0.0001:
            if metrics["calculable_metrics_count"] == 3:
                # IRR만 문제인 경우: IRR만 제거
                metrics["irr"] = None
                metrics["calculable_metrics_count"] = 2
            else:
                # 전체 지표 문제: 모두 제거
                metrics["npv"] = None
                metrics["roi"] = None
                metrics["calculable_metrics_count"] = 0
        
        return metrics
    
    def determine_grade(self, metrics: Dict[str, Any]) -> str:
        """
        Hard Stop 규칙 4, 8: 사업성 등급 산정 (N/A 금지)
        
        Returns:
            str: A, B, C, D 중 하나 (N/A 금지)
        """
        npv = metrics.get("npv")
        irr = metrics.get("irr")
        discount_rate = self.details.get("discount_rate", 0.05)
        
        # N/A는 절대 반환하지 않음
        if metrics["calculable_metrics_count"] < 2:
            # 계산 불가 시: C (조건부 진행)
            return "C"
        
        # A: NPV(+) + IRR ≥ 기준수익률
        if npv and npv > 0:
            if irr and irr >= discount_rate:
                return "A"
            elif irr is None:
                # B: NPV(+) + IRR 산정 제한
                return "B"
            else:
                # C: NPV(+) but IRR < 기준
                return "C"
        
        # D: NPV(-)
        if npv and npv <= 0:
            return "D"
        
        # Fallback (should not reach here)
        return "C"
    
    def generate_business_structure_explanation(self) -> str:
        """
        Hard Stop 규칙 6: 재무 구조 먼저 명시
        """
        return """
본 사업은 **분양 사업이 아닌** LH 신축매입임대 사업으로, 수익 구조가 일반 부동산 개발과 상이합니다.

**수익 구조:**
- LH(한국토지주택공사)가 준공 후 건물 전체를 일괄 매입
- 매입 단가는 LH 내부 기준(임대주택법 시행령 제12조)에 따라 산정
- 장기 임대 수익이 아닌 **단일 시점 매각 수익** 발생

**비용 구조:**
- 공사비(건축비, 토목비, 기계설비비 등)
- 설계비, 인허가비, 감리비
- 금융비용(공사 기간 중 이자)
- 간접비 및 예비비

**재무 분석 특성:**
- IRR(내부수익률)은 분양 사업 대비 산정에 제약이 있음 (현금흐름이 단순)
- NPV(순현재가치) 및 ROI(투자수익률)가 주요 판단 지표
- LH 매입 단가가 확정적이므로 수익 변동성이 낮음
        """.strip()
    
    def generate_metric_interpretation(self, metrics: Dict[str, Any], grade: str) -> str:
        """
        Hard Stop 규칙 6: 해석 문장 생성 (수치와 1:1 대응)
        """
        npv = metrics.get("npv")
        irr = metrics.get("irr")
        roi = metrics.get("roi")
        
        # Hard Stop 규칙 4: N/A 등급에서 평가 금지
        if grade == "N/A":
            return "데이터 부족으로 사업성 평가를 수행할 수 없습니다."
        
        # 계산 가능한 지표가 2개 미만인 경우
        if metrics["calculable_metrics_count"] < 2:
            return (
                "본 사업은 필수 재무 데이터 부족으로 정량 분석이 제한되어, "
                "정성적 판단 및 유사 사례 비교를 통해 사업 성립 가능성을 검토하는 것이 필요합니다."
            )
        
        # 정상 케이스
        interpretation_parts = []
        
        # NPV 해석
        if npv is not None:
            if npv > 0:
                interpretation_parts.append(
                    f"순현재가치(NPV)가 {npv:,.0f}원으로 산출되어 "
                    f"**사업비 대비 수익이 현재가치 기준으로 초과**하는 구조입니다."
                )
            elif npv == 0:
                interpretation_parts.append(
                    f"순현재가치(NPV)가 0원 수준으로, "
                    f"**사업비와 수익이 현재가치 기준 균형**을 이룹니다."
                )
            else:
                interpretation_parts.append(
                    f"순현재가치(NPV)가 {npv:,.0f}원(음수)로 산출되어 "
                    f"**사업비 대비 수익이 부족**한 것으로 분석됩니다."
                )
        
        # IRR 해석
        if irr is not None:
            irr_pct = irr * 100
            discount_rate_pct = self.details.get("discount_rate", 0.05) * 100
            if irr >= self.details.get("discount_rate", 0.05):
                interpretation_parts.append(
                    f"연평균 수익률이 약 {irr_pct:.1f}%로, "
                    f"기준 할인율({discount_rate_pct:.1f}%)을 상회하여 **재무적으로 양호**합니다."
                )
            else:
                interpretation_parts.append(
                    f"연평균 수익률이 약 {irr_pct:.1f}%로, "
                    f"기준 할인율({discount_rate_pct:.1f}%)에 미달하나, "
                    f"LH 매입 확정성을 고려하면 **손실 가능성은 낮은 구조**입니다."
                )
        else:
            interpretation_parts.append(
                "본 사업은 LH 매입형 구조 특성상 IRR 산정에 한계가 있으나, "
                "NPV 및 ROI 기준으로 사업 성립성을 판단할 수 있습니다."
            )
        
        # ROI 해석
        if roi is not None:
            roi_pct = roi * 100
            if roi > 0:
                interpretation_parts.append(
                    f"투자 대비 수익률(ROI)은 약 {roi_pct:.1f}%로, "
                    f"**투자금 대비 {roi_pct:.1f}%의 수익**이 예상됩니다."
                )
            elif roi == 0:
                interpretation_parts.append(
                    f"투자 대비 수익률(ROI)은 0%로, **손익분기점**에 위치합니다."
                )
            else:
                interpretation_parts.append(
                    f"투자 대비 수익률(ROI)은 약 {roi_pct:.1f}%(음수)로, "
                    f"**투자금 회수에 어려움**이 예상됩니다."
                )
        
        # 최종 판단
        if grade == "A":
            interpretation_parts.append(
                "**종합 판단**: 재무 지표가 모두 양호하여 사업 추진을 권장합니다."
            )
        elif grade == "B":
            interpretation_parts.append(
                "**종합 판단**: NPV가 양수이며 LH 매입 확정성이 있어, "
                "일부 재무 지표 산정 제약에도 불구하고 사업 추진이 가능합니다."
            )
        elif grade == "C":
            interpretation_parts.append(
                "**종합 판단**: 재무 지표가 손익분기점 근처이므로, "
                "사업비 절감 또는 LH 매입 단가 상향 협의가 필요합니다."
            )
        else:  # D
            interpretation_parts.append(
                "**종합 판단**: 재무 지표가 부정적이므로, "
                "사업 구조 재검토 또는 대안 검토가 필요합니다."
            )
        
        return "\n\n".join(interpretation_parts)
    
    def generate_m6_linkage(self) -> str:
        """
        Hard Stop 규칙 9: M6 연계 문장 필수
        """
        return (
            "본 사업성 분석 결과는 **M6 LH 종합 심사에서 "
            "사업 안정성 평가 항목의 기초 자료로 활용**됩니다. "
            "특히 NPV 및 ROI가 LH 내부 심사 기준을 충족하는지 여부가 "
            "매입 승인 결정에 직접적인 영향을 미칩니다."
        )
    
    def generate_risk_factors(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        리스크 요인 및 관리 방안
        """
        risks = []
        
        # 재무 지표 기반 리스크
        npv = metrics.get("npv")
        if npv and npv < 1000000000:  # 10억 미만
            risks.append({
                "risk": "순현재가치가 10억원 미만으로, 사업비 변동 시 손실 가능성 존재",
                "mitigation": "공사비 예비비 15% 이상 확보, VE(가치공학) 적용으로 사업비 절감"
            })
        
        # LH 매입 단가 리스크
        if not self.details.get("lh_price_confirmed", False):
            risks.append({
                "risk": "LH 매입 단가가 확정되지 않아, 실제 매입가 하향 가능성",
                "mitigation": "LH와 사전 협의를 통해 매입 단가 범위 확인 및 계약 조건 명시"
            })
        
        # 공사 기간 리스크
        construction_period = self.details.get("construction_period", 2)
        if construction_period > 2:
            risks.append({
                "risk": f"공사 기간이 {construction_period}년으로, 금융비용 증가 및 시장 변동 노출",
                "mitigation": "공정 관리 철저, Fast-track 공법 검토, 금리 고정 대출 활용"
            })
        
        # 기본 리스크 (항상 포함)
        risks.append({
            "risk": "인허가 지연 또는 설계 변경으로 인한 사업비 증가",
            "mitigation": "인허가 사전 협의 완료, 설계 확정 후 공사 착공, 예비비 충분 확보"
        })
        
        return risks


def prepare_m5_enhanced_report_data(
    context_id: str, 
    m4_data: Dict[str, Any], 
    module_data: Dict[str, Any],
    frozen_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    M5 Enhanced 보고서 데이터 준비 (외부 호출용)
    
    Hard Stop 규칙 10: 최종 검증
    
    Args:
        context_id: Context ID
        m4_data: M4 모듈 데이터
        module_data: M5 모듈 데이터
        frozen_context: Context.get_frozen_context(context_id) 결과 (데이터 바인딩 복구용)
    
    Returns:
        보고서 데이터 또는 에러 상태
    """
    analyzer = M5EnhancedAnalyzer(context_id, m4_data, module_data, frozen_context)
    
    # 🔴 데이터 바인딩 에러 체크
    if analyzer.binding_error:
        from datetime import datetime
        logger.error(f"❌ M5 Data Binding Error for {context_id}")
        
        return {
            "error": True,
            "error_type": "DATA_BINDING_ERROR",
            "error_message": analyzer.binding_error_message,
            "missing_items": ["M4 건축규모 데이터"],
            "context_id": context_id,
            "report_id": f"ZS-M5-BINDING-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "use_data_not_loaded_template": True,
            "template_version": "connection_error",
            "analysis_date": datetime.now().strftime("%Y년 %m월 %d일"),
            "fixed_message": "ZeroSite는 M4 건축규모 데이터가 연결되지 않은 상태에서 사업성 분석을 수행하지 않습니다."
        }
    
    # Step 1: 데이터 무결성 검증
    is_valid, missing_items = analyzer.validate_required_data()
    
    if not is_valid:
        # Hard Stop: 필수 데이터 누락 → DATA NOT LOADED 템플릿
        from datetime import datetime
        
        logger.error(f"🔴 M5 DATA NOT LOADED: {len(missing_items)}개 항목 누락")
        
        return {
            "error": True,
            "error_type": "DATA_NOT_LOADED",
            "error_message": "필수 사업성 데이터가 수집되지 않아 분석을 진행할 수 없습니다.",
            "missing_items": missing_items,
            "context_id": context_id,
            "report_id": f"ZS-M5-NOT-LOADED-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "use_data_not_loaded_template": True,
            "template_version": "v1",
            "analysis_date": datetime.now().strftime("%Y년 %m월 %d일"),
            "project_address": m4_data.get("details", {}).get("address", "주소 정보 없음"),
            "fixed_message": "ZeroSite는 필수 사업성 데이터가 수집되기 전까지 사업성 분석 및 판단을 수행하지 않습니다."
        }
    
    # Step 2: 재무 지표 계산
    metrics = analyzer.calculate_financial_metrics()
    
    # Step 3: 등급 산정
    grade = analyzer.determine_grade(metrics)
    
    # Step 4: 보고서 데이터 생성
    from datetime import datetime
    
    report_data = {
        "context_id": context_id,
        "report_id": f"ZS-M5-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "analysis_date": datetime.now().strftime("%Y년 %m월 %d일"),
        "project_address": m4_data.get("details", {}).get("address", "주소 정보 없음"),
        
        # 사업 구조 설명
        "business_structure": analyzer.generate_business_structure_explanation(),
        
        # 재무 지표
        "financial_metrics": metrics,
        
        # 사업성 등급
        "grade": grade,
        
        # 해석 문장
        "interpretation": analyzer.generate_metric_interpretation(metrics, grade),
        
        # M6 연계
        "m6_linkage": analyzer.generate_m6_linkage(),
        
        # 리스크 요인
        "risk_factors": analyzer.generate_risk_factors(metrics),
        
        # M4 연계 정보
        "m4_summary": {
            "unit_count": m4_data.get("summary", {}).get("recommended_units"),
            "total_floor_area": m4_data.get("details", {}).get("total_floor_area_sqm")
        }
    }
    
    return report_data
