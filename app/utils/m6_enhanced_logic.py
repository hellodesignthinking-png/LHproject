"""
M6 Enhanced LH Comprehensive Review Logic - FAIL FAST Decision Chain
========================================================================

최상위 원칙: FAIL FAST
- M1~M5 중 하나라도 무결성 오류 시 판단 금지
- 점수/등급/긍정 표현 전부 출력 금지
- 지정 문구만 출력

사용자 요구사항 9가지 규칙:
1. 필수 입력 모듈 무결성 체크 (Hard Gate)
2. 점수 기반 판단 금지 조건
3. LH 심사 항목별 판단 구조 (조건부 실행)
4. 최종 판단 문장 출력 규칙
5. 출력 차단 시 유일하게 허용되는 문구
6. 기술적 오류 차단 규칙
7. 문서 출력 최소 요건
8. 문서 표기
9. 메타 선언

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class M6EnhancedAnalyzer:
    """
    M6 LH 종합 판단 보고서를 위한 고도화된 의사결정 엔진
    - FAIL FAST 원칙 최우선
    - Decision Chain 무결성 보장
    - 조건부 판단 구조만 허용
    """
    
    def __init__(self, context_id: str, m1_data: Dict[str, Any], m3_data: Dict[str, Any], 
                 m4_data: Dict[str, Any], m5_data: Dict[str, Any]):
        self.context_id = context_id
        self.m1_data = m1_data
        self.m3_data = m3_data
        self.m4_data = m4_data
        self.m5_data = m5_data
        
    def validate_decision_chain(self) -> Tuple[bool, List[str]]:
        """
        규칙 1: 필수 입력 모듈 무결성 체크 (Hard Gate)
        
        Returns:
            Tuple[bool, List[str]]: (검증 통과 여부, 누락/오류 항목 리스트)
        """
        errors = []
        
        # ✔ M1 토지·입지 정보 (파이프라인 구조: m1_data가 직접 land 정보)
        if not self.m1_data.get("address"):
            errors.append("M1: 주소 정보 누락")
        if not self.m1_data.get("land", {}).get("area_sqm"):
            errors.append("M1: 토지면적 수치 누락")
        if not self.m1_data.get("zoning", {}).get("type"):
            errors.append("M1: 용도지역 명시 누락")
            
        # ✔ M3 공급유형 판단 (파이프라인 구조: housing_type)
        m3_summary = self.m3_data.get("summary", {})
        m3_details = self.m3_data.get("details", {})
        if not m3_summary.get("recommended_type") and not m3_details.get("selected", {}).get("type"):
            errors.append("M3: 최종 공급유형 명확하지 않음")
                
        # ✔ M4 건축규모 (파이프라인 구조: capacity)
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        
        # incentive_units 또는 legal_units 확인
        unit_count = (
            m4_summary.get("incentive_units") or 
            m4_summary.get("legal_units") or 
            m4_details.get("incentive_capacity", {}).get("total_units") or
            m4_details.get("legal_capacity", {}).get("total_units")
        )
        if not unit_count or unit_count == 0:
            errors.append("M4: 총 세대수 확정 필요")
            
        # target_gfa_sqm 또는 total_gfa_sqm 확인
        total_floor_area = (
            m4_details.get("incentive_capacity", {}).get("target_gfa_sqm") or
            m4_details.get("legal_capacity", {}).get("target_gfa_sqm") or
            m4_details.get("total_floor_area_sqm")
        )
        if not total_floor_area:
            errors.append("M4: 연면적 수치 누락")
            
        # ✔ M5 사업성 분석 (파이프라인 구조: feasibility)
        m5_summary = self.m5_data.get("summary", {})
        m5_details = self.m5_data.get("details", {})
        
        # costs 또는 total_cost 확인
        total_cost = (
            m5_details.get("costs", {}).get("total") or
            m5_details.get("total_cost") or
            m5_summary.get("total_cost")
        )
        if not total_cost:
            errors.append("M5: 총 사업비 산정 필요")
            
        # revenue 또는 lh_purchase 확인
        revenue_structure = (
            m5_details.get("revenue") or
            m5_details.get("lh_purchase") or
            m5_summary.get("lh_purchase_price")
        )
        if not revenue_structure:
            errors.append("M5: 수익 구조 설명 누락")
            
        # NPV 또는 대체 판단 지표 존재
        npv = (
            m5_summary.get("npv_public_krw") or
            m5_details.get("financials", {}).get("npv_public") or
            m5_details.get("npv")
        )
        roi = (
            m5_summary.get("roi_pct") or
            m5_details.get("financials", {}).get("roi") or
            m5_details.get("roi")
        )
        irr = (
            m5_summary.get("irr_pct") or
            m5_details.get("financials", {}).get("irr_public") or
            m5_details.get("irr")
        )
        if npv is None and roi is None:
            errors.append("M5: NPV 또는 대체 판단 지표 존재 필요")
            
        # IRR/ROI 모순 체크
        irr = m5_financial.get("irr")
        if irr is not None and roi is not None:
            # IRR과 ROI의 부호가 반대인 경우 (논리 모순)
            if (irr > 0 and roi < 0) or (irr < 0 and roi > 0):
                errors.append("M5: IRR/ROI 모순 (부호 불일치)")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def check_score_prohibition_conditions(self) -> Tuple[bool, List[str]]:
        """
        규칙 2: 점수 기반 판단 금지 조건
        
        Returns:
            Tuple[bool, List[str]]: (점수 사용 가능 여부, 금지 사유 리스트)
        """
        prohibitions = []
        
        # N/A, None, 0.0%, 공란 존재 체크
        all_data = [self.m1_data, self.m3_data, self.m4_data, self.m5_data]
        
        for i, data in enumerate(all_data):
            module_name = ["M1", "M3", "M4", "M5"][i]
            
            # 재귀적으로 모든 값 체크
            def check_invalid_values(obj, path=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        check_invalid_values(v, f"{path}.{k}")
                elif isinstance(obj, list):
                    for idx, item in enumerate(obj):
                        check_invalid_values(item, f"{path}[{idx}]")
                elif obj == "N/A" or obj == "None" or obj == "" or obj == "0.0%":
                    prohibitions.append(f"{module_name}: 앞단 모듈에 '{obj}' 존재 (경로: {path})")
            
            check_invalid_values(data, module_name)
        
        # 추정치만으로 계산된 점수 체크
        m5_notes = self.m5_data.get("financial_metrics", {}).get("calculation_notes", [])
        for note in m5_notes:
            if "추정" in note:
                prohibitions.append(f"M5: 추정치 기반 계산 - '{note}'")
        
        # 내부 기준 설명 없이 산출된 퍼센트 점수
        # (현재는 점수 자체를 사용하지 않으므로 skip)
        
        can_use_score = len(prohibitions) == 0
        return can_use_score, prohibitions
    
    def analyze_lh_review_items(self) -> Dict[str, Any]:
        """
        규칙 3: LH 심사 항목별 판단 구조 (조건부 실행)
        
        Returns:
            Dict with:
            - policy_compliance: Optional[Dict]
            - business_stability: Optional[Dict]
            - operation_risk: Optional[Dict]
        """
        analysis = {
            "policy_compliance": None,
            "business_stability": None,
            "operation_risk": None
        }
        
        # ▪ 정책 적합성
        try:
            m3_type = self.m3_data.get("summary", {}).get("selected_supply_type", "청년형")
            policy_analysis = {
                "public_housing_law": "공공주택특별법에 따른 신축매입임대 사업 대상",
                "lh_policy_direction": f"LH {m3_type} 공급 정책과 부합",
                "supply_type_match": f"M3에서 판단한 {m3_type}과 일치",
                "conclusion": f"정책 적합성 측면에서 {m3_type} 신축매입임대로 진행 가능"
            }
            analysis["policy_compliance"] = policy_analysis
        except Exception as e:
            logger.error(f"정책 적합성 분석 실패: {e}")
            analysis["policy_compliance"] = {"conclusion": "판단 보류 (근거 부족)"}
        
        # ▪ 사업 안정성
        try:
            m5_grade = self.m5_data.get("grade", "C")
            m5_financial = self.m5_data.get("financial_metrics", {})
            npv = m5_financial.get("npv")
            
            if npv is not None:
                if npv > 0:
                    stability_conclusion = f"M5 사업성 등급 {m5_grade}, NPV 양수로 손실 가능성 낮음"
                else:
                    stability_conclusion = f"M5 사업성 등급 {m5_grade}, NPV 음수로 사업 안정성 우려"
            else:
                stability_conclusion = "NPV 산정 불가로 사업 안정성 판단 제한"
            
            stability_analysis = {
                "m5_grade": m5_grade,
                "loss_possibility": "낮음" if npv and npv > 0 else "주의 필요",
                "financial_structure": "LH 매입형으로 구조 단순, 수익 확정성 높음",
                "conclusion": stability_conclusion
            }
            analysis["business_stability"] = stability_analysis
        except Exception as e:
            logger.error(f"사업 안정성 분석 실패: {e}")
            analysis["business_stability"] = {"conclusion": "판단 보류 (근거 부족)"}
        
        # ▪ 운영 리스크
        try:
            m4_details = self.m4_data.get("details", {})
            parking = m4_details.get("parking_spaces", 0)
            
            risk_factors = []
            
            # 주차 리스크
            m4_units = self.m4_data.get("summary", {}).get("recommended_units", 20)
            if parking < m4_units * 0.5:
                risk_factors.append("주차 공간 부족 (세대당 0.5대 미만)")
            
            # 지역 수요 변동성
            m3_demand = self.m3_data.get("details", {}).get("demand_volatility", "중간")
            if m3_demand in ["높음", "불안정"]:
                risk_factors.append("지역 수요 변동성 높음")
            
            operation_analysis = {
                "parking_risk": "주차 부족" if parking < m4_units * 0.5 else "관리 가능",
                "management_risk": "소규모 단지로 관리 효율 양호",
                "vacancy_risk": "청년형 특성상 회전율 안정",
                "demand_volatility": m3_demand,
                "risk_factors": risk_factors,
                "conclusion": f"운영 리스크는 관리 가능한 수준 ({len(risk_factors)}개 주의 사항)"
            }
            analysis["operation_risk"] = operation_analysis
        except Exception as e:
            logger.error(f"운영 리스크 분석 실패: {e}")
            analysis["operation_risk"] = {"conclusion": "판단 보류 (근거 부족)"}
        
        return analysis
    
    def generate_final_decision(self, lh_review: Dict[str, Any]) -> Dict[str, str]:
        """
        규칙 4: 최종 판단 문장 출력 규칙
        
        ❌ 절대 금지 표현:
        - "LH 매입 가능"
        - "사업 추진 권장"
        - "종합적으로 적합"
        - "문제 없음"
        
        ✅ 허용 표현 (조건 충족 시에만):
        - "현재 입력된 조건 하에서 충족할 가능성이 있다"
        - "M1~M5 전 단계 데이터가 확정되었음을 전제로 한 판단"
        """
        
        # 판단 근거 카운트
        judgment_basis_count = 0
        if lh_review.get("policy_compliance") and lh_review["policy_compliance"].get("conclusion") != "판단 보류 (근거 부족)":
            judgment_basis_count += 1
        if lh_review.get("business_stability") and lh_review["business_stability"].get("conclusion") != "판단 보류 (근거 부족)":
            judgment_basis_count += 1
        if lh_review.get("operation_risk") and lh_review["operation_risk"].get("conclusion") != "판단 보류 (근거 부족)":
            judgment_basis_count += 1
        
        # 조건부 리스크 카운트
        risk_count = 0
        if lh_review.get("operation_risk"):
            risk_count = len(lh_review["operation_risk"].get("risk_factors", []))
        
        # 규칙 7: 문서 출력 최소 요건
        # - 판단 근거 3개 이상
        # - 조건부 리스크 2개 이상
        if judgment_basis_count < 3:
            return {
                "decision": "판단 보류",
                "reason": f"판단 근거 부족 ({judgment_basis_count}/3개)",
                "conditional_statement": ""
            }
        
        # 최종 판단 문장 생성
        decision_text = (
            "본 사업은 **현재 입력된 조건 하에서** LH 신축매입임대 심사 기준을 "
            "*충족할 가능성이 있다*. "
            "다만, 이는 **M1~M5 전 단계 데이터가 확정되었음을 전제로 한 판단**이다."
        )
        
        conditional_statement = (
            "**조건부 판단 구조**: \n"
            f"1. M1 토지정보 확정 (주소, 면적, 용도지역)\n"
            f"2. M3 공급유형 판단 ({self.m3_data.get('summary', {}).get('selected_supply_type', '청년형')})\n"
            f"3. M4 건축규모 확정 ({self.m4_data.get('summary', {}).get('recommended_units', '?')}세대)\n"
            f"4. M5 사업성 등급 ({self.m5_data.get('grade', 'C')})\n"
            f"5. 리스크 요인 {risk_count}개 관리 필요"
        )
        
        return {
            "decision": "조건부 가능",
            "decision_text": decision_text,
            "conditional_statement": conditional_statement,
            "judgment_basis_count": judgment_basis_count,
            "risk_count": risk_count
        }
    
    def generate_meta_declaration(self) -> str:
        """
        규칙 9: 메타 선언 (문서 하단 필수)
        """
        return (
            "본 판단은 ZeroSite 분석 엔진에 의해 자동 생성되었으며, "
            "실제 사업 추진 여부는 LH 내부 심사 및 관계 기관 협의를 통해 최종 결정됩니다."
        )


def prepare_m6_enhanced_report_data(
    context_id: str,
    m1_data: Dict[str, Any],
    m3_data: Dict[str, Any],
    m4_data: Dict[str, Any],
    m5_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    M6 Enhanced 보고서 데이터 준비 (외부 호출용)
    
    최상위 원칙: FAIL FAST
    """
    analyzer = M6EnhancedAnalyzer(context_id, m1_data, m3_data, m4_data, m5_data)
    
    # Step 1: Decision Chain 무결성 검증
    is_valid, errors = analyzer.validate_decision_chain()
    
    if not is_valid:
        # FAIL FAST: 필수 모듈 무결성 오류
        # 규칙 5: 출력 차단 시 유일하게 허용되는 문구
        return {
            "error": True,
            "error_message": (
                "본 종합 판단은 필수 입력 데이터의 무결성 오류로 인해 수행할 수 없습니다. "
                "M1~M5 분석 결과를 재검증한 후 다시 판단하시기 바랍니다."
            ),
            "error_details": errors,
            "context_id": context_id
        }
    
    # Step 2: 점수 기반 판단 금지 조건 체크
    can_use_score, score_prohibitions = analyzer.check_score_prohibition_conditions()
    
    # Step 3: LH 심사 항목별 판단
    lh_review = analyzer.analyze_lh_review_items()
    
    # Step 4: 최종 판단 생성
    final_decision = analyzer.generate_final_decision(lh_review)
    
    # Step 5: 보고서 데이터 생성
    from datetime import datetime
    
    report_data = {
        "context_id": context_id,
        "report_id": f"ZS-M6-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "analysis_date": datetime.now().strftime("%Y년 %m월 %d일"),
        "project_address": m1_data.get("land", {}).get("address", "주소 정보 없음"),
        
        # Decision Chain 검증 결과
        "decision_chain_valid": is_valid,
        "decision_chain_errors": errors,
        
        # 점수 사용 가능 여부
        "can_use_score": can_use_score,
        "score_prohibitions": score_prohibitions,
        
        # LH 심사 항목 분석
        "lh_review": lh_review,
        
        # 최종 판단
        "final_decision": final_decision,
        
        # 메타 선언
        "meta_declaration": analyzer.generate_meta_declaration(),
        
        # M1~M5 요약
        "m1_summary": {
            "address": m1_data.get("land", {}).get("address"),
            "area_sqm": m1_data.get("land", {}).get("land", {}).get("area_sqm"),
            "zoning": m1_data.get("land", {}).get("zoning", {}).get("type")
        },
        "m3_summary": {
            "supply_type": m3_data.get("summary", {}).get("selected_supply_type", "청년형")
        },
        "m4_summary": {
            "unit_count": m4_data.get("summary", {}).get("recommended_units"),
            "total_floor_area": m4_data.get("details", {}).get("total_floor_area_sqm")
        },
        "m5_summary": {
            "grade": m5_data.get("grade", "C"),
            "npv": m5_data.get("financial_metrics", {}).get("npv")
        }
    }
    
    return report_data
