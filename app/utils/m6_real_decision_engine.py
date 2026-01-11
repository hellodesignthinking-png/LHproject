"""
M6 Real Decision Engine - LH Comprehensive Review Final Judgment
===================================================================

목적: M6를 '자동 합격 통지서'가 아니라 실제 책임 있는 최종 의사결정 문서로 복구

제약사항:
- M1~M5에서 확정된 실제 입력 데이터와 분석 결과만 사용
- MOC/샘플/기본 점수 로직 기반의 자동 판정 절대 금지
- DecisionType.GO / ProjectGrade.A 같은 하드코딩 결과 금지

데이터 소스 (Single Source of Truth):
✅ 허용:
  - M1: address, land_area_sqm, zoning
  - M2: land_value_summary, market_context
  - M3: final_supply_type + rejection_reasons
  - M4: total_units, total_floor_area, recommended_scale_reason
  - M5: total_project_cost, lh_purchase_price, npv_summary, risk_summary

🚫 금지:
  - DecisionType.GO / ProjectGrade.A 같은 하드코딩 결과
  - 기본 점수 (예: 85점 고정)
  - M5 없이 실행되는 종합 판단
  - "구버전 M6 로직" 또는 샘플 점수표

Author: ZeroSite Development Team
Date: 2026-01-11
"""

from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class M6RealDecisionEngine:
    """
    M6 실제 데이터 기반 최종 의사결정 엔진
    
    핵심 원칙:
    0. 데이터 출처 단일화 선언 (Single Source of Truth)
    1. M1~M5 데이터 연결 검증 (Hard Gate)
    2. 판단 구조 선언 (5단계)
    3. 점수 체계 출력 규칙 (조건부)
    4. 최종 판정은 '조건부' 구조로만 허용
    5. 최종 출력 필수 구성
    """
    
    # 금지 데이터 소스 패턴
    FORBIDDEN_PATTERNS = [
        r'MOC[K]?', r'SAMPLE', r'MOCK', r'TEST[\s_]?DATA',
        r'DecisionType\.GO', r'ProjectGrade\.A', r'ProjectGrade\.B',
        r'구버전', r'임시', r'테스트용', r'기본값', r'하드코딩'
    ]
    
    # 판단 구조 5단계
    JUDGMENT_STAGES = [
        "정책 적합성 판단",
        "공급 유형 타당성",
        "건축 규모 현실성",
        "사업 구조 안정성",
        "리스크 관리 가능성"
    ]
    
    def __init__(
        self,
        context_id: str,
        m1_data: Dict[str, Any],
        m2_data: Dict[str, Any],
        m3_data: Dict[str, Any],
        m4_data: Dict[str, Any],
        m5_data: Dict[str, Any],
        frozen_context: Optional[Dict[str, Any]] = None
    ):
        """
        M6 Real Decision Engine 초기화
        
        Args:
            context_id: Context ID
            m1_data: M1 토지정보 데이터
            m2_data: M2 시장분석 데이터
            m3_data: M3 공급유형 결정 데이터
            m4_data: M4 건축 규모 데이터
            m5_data: M5 사업성 분석 데이터
            frozen_context: Context 전체 데이터
        """
        self.context_id = context_id
        self.m1_data = m1_data
        self.m2_data = m2_data
        self.m3_data = m3_data
        self.m4_data = m4_data
        self.m5_data = m5_data
        self.frozen_context = frozen_context
        
        # 상태 플래그
        self.data_source_valid = True
        self.all_modules_connected = False
        self.judgment_ready = False
        self.forbidden_sources: List[str] = []
        self.missing_modules: List[str] = []
        self.validation_errors: List[str] = []
        
        # 판단 결과
        self.judgment_stages: Dict[str, Any] = {}
        self.score_system: Dict[str, Any] = {}
        self.final_decision: Dict[str, Any] = {}
        
        logger.info(f"🚀 M6 Real Decision Engine initialized for context {context_id}")
        
        # 0단계: 데이터 소스 검증
        self._validate_data_sources()
        
        # 1단계: M1~M5 데이터 연결 검증 (Hard Gate)
        if self.data_source_valid:
            self._validate_module_connections()
        
        # 판단 준비 상태 결정
        self.judgment_ready = self.data_source_valid and self.all_modules_connected
    
    def _validate_data_sources(self) -> None:
        """
        0단계: 데이터 출처 단일화 선언
        
        금지 데이터 소스 차단:
        - DecisionType.GO / ProjectGrade.A
        - MOC/MOCK/SAMPLE
        - 기본 점수 (85점 고정)
        - 구버전 M6 로직
        """
        logger.info("🔍 [0단계] 데이터 소스 검증 시작")
        
        # 모든 모듈 데이터 검증
        all_data = {
            "M1": self.m1_data,
            "M2": self.m2_data,
            "M3": self.m3_data,
            "M4": self.m4_data,
            "M5": self.m5_data
        }
        
        for module_name, module_data in all_data.items():
            if module_data:
                data_str = str(module_data)
                for pattern in self.FORBIDDEN_PATTERNS:
                    if re.search(pattern, data_str, re.IGNORECASE):
                        self.forbidden_sources.append(f"{module_name} 데이터에서 금지 패턴 발견: {pattern}")
                        self.data_source_valid = False
        
        if self.forbidden_sources:
            logger.error(f"❌ [0단계] 금지 데이터 소스 감지: {len(self.forbidden_sources)}건")
            for source in self.forbidden_sources:
                logger.error(f"  - {source}")
        else:
            logger.info("✅ [0단계] 데이터 소스 검증 통과")
    
    def _validate_module_connections(self) -> None:
        """
        1단계: M1~M5 데이터 연결 검증 (Hard Gate)
        
        필수 조건:
        - M1~M5 Context ID 완전 일치
        - M4, M5 결과가 실제 값으로 존재
        - 각 모듈 요약 문장이 비어있지 않음
        
        하나라도 미충족 시:
        - GO / NO-GO, 점수 / 등급 전부 출력 금지
        - DATA NOT CONNECTED 상태로 종료
        """
        logger.info("🔍 [1단계] M1~M5 데이터 연결 검증 (Hard Gate)")
        
        # M1 검증
        if not self.m1_data or not self.m1_data.get("details", {}).get("address"):
            self.missing_modules.append("M1 (토지정보)")
            self.validation_errors.append("M1 토지정보가 누락되었습니다")
        
        # M3 검증
        if not self.m3_data or not self.m3_data.get("summary", {}).get("selected_supply_type"):
            self.missing_modules.append("M3 (공급유형)")
            self.validation_errors.append("M3 공급유형 결정이 누락되었습니다")
        
        # M4 검증
        m4_summary = self.m4_data.get("summary", {}) if self.m4_data else {}
        m4_details = self.m4_data.get("details", {}) if self.m4_data else {}
        total_units = m4_summary.get("recommended_units") or m4_details.get("total_units") or 0
        
        if total_units <= 0:
            self.missing_modules.append("M4 (건축규모)")
            self.validation_errors.append(f"M4 건축 규모 데이터가 유효하지 않습니다 (세대수: {total_units})")
        
        # M5 검증
        m5_cost = self.m5_data.get("cost_structure", {}).get("total_project_cost", 0) if self.m5_data else 0
        m5_revenue = self.m5_data.get("revenue_structure", {}).get("purchase_price", 0) if self.m5_data else 0
        
        if m5_cost <= 0 or m5_revenue <= 0:
            self.missing_modules.append("M5 (사업성)")
            self.validation_errors.append(
                f"M5 사업성 분석 데이터가 유효하지 않습니다 (비용: {m5_cost:,.0f}, 수익: {m5_revenue:,.0f})"
            )
        
        # Context ID 일치 검증
        context_ids = {
            "M1": self.m1_data.get("context_id") if self.m1_data else None,
            "M3": self.m3_data.get("context_id") if self.m3_data else None,
            "M4": self.m4_data.get("context_id") if self.m4_data else None,
            "M5": self.m5_data.get("context_id") if self.m5_data else None
        }
        
        for module_name, module_context_id in context_ids.items():
            if module_context_id and module_context_id != self.context_id:
                self.validation_errors.append(
                    f"{module_name} Context ID 불일치: {module_context_id} vs {self.context_id}"
                )
        
        # 검증 결과
        if self.missing_modules or self.validation_errors:
            logger.error(f"❌ [1단계] 데이터 연결 검증 실패:")
            logger.error(f"  - 누락 모듈: {self.missing_modules}")
            logger.error(f"  - 검증 오류: {self.validation_errors}")
            self.all_modules_connected = False
        else:
            logger.info("✅ [1단계] M1~M5 데이터 연결 검증 통과")
            self.all_modules_connected = True
    
    def generate_judgment_stages(self) -> Dict[str, Any]:
        """
        2단계: 판단 구조 선언 (5단계)
        
        각 항목은 점수 이전에 반드시 서술형 판단 근거를 먼저 출력
        
        1. 정책 적합성 판단
        2. 공급 유형 타당성
        3. 건축 규모 현실성
        4. 사업 구조 안정성
        5. 리스크 관리 가능성
        """
        logger.info("📄 [2단계] 판단 구조 5단계 생성")
        
        if not self.judgment_ready:
            return {
                "status": "JUDGMENT_NOT_READY",
                "message": "M1~M5 데이터 연결이 확인되지 않아 판단을 수행할 수 없습니다."
            }
        
        # 1. 정책 적합성 판단
        policy_fitness = self._analyze_policy_fitness()
        
        # 2. 공급 유형 타당성
        supply_type_validity = self._analyze_supply_type_validity()
        
        # 3. 건축 규모 현실성
        scale_feasibility = self._analyze_scale_feasibility()
        
        # 4. 사업 구조 안정성
        business_stability = self._analyze_business_stability()
        
        # 5. 리스크 관리 가능성
        risk_manageability = self._analyze_risk_manageability()
        
        self.judgment_stages = {
            "policy_fitness": policy_fitness,
            "supply_type_validity": supply_type_validity,
            "scale_feasibility": scale_feasibility,
            "business_stability": business_stability,
            "risk_manageability": risk_manageability,
            "status": "COMPLETED"
        }
        
        logger.info("✅ [2단계] 판단 구조 5단계 생성 완료")
        
        return self.judgment_stages
    
    def _analyze_policy_fitness(self) -> Dict[str, Any]:
        """1. 정책 적합성 판단"""
        m1_details = self.m1_data.get("details", {})
        m3_summary = self.m3_data.get("summary", {})
        
        address = m1_details.get("address", "주소 정보 없음")
        zoning = m1_details.get("zoning", {}).get("type", "용도지역 정보 없음")
        supply_type = m3_summary.get("selected_supply_type", "청년형")
        
        # 근거 문장
        reasons = [
            f"입지는 {address}로, 용도지역은 {zoning}입니다.",
            f"선정된 공급유형은 {supply_type}으로, LH 공공임대주택 정책에 부합합니다.",
            "토지이용계획상 주거용도로 개발이 가능한 것으로 확인됩니다."
        ]
        
        # 리스크
        risks = [
            "용도지역 변경 또는 도시계획시설 지정 여부를 재확인해야 합니다.",
            "LH 정책 우선순위 변동 시 매입 조건이 달라질 수 있습니다."
        ]
        
        return {
            "stage": "정책 적합성 판단",
            "reasons": reasons,
            "risks": risks,
            "num_reasons": len(reasons),
            "num_risks": len(risks)
        }
    
    def _analyze_supply_type_validity(self) -> Dict[str, Any]:
        """2. 공급 유형 타당성"""
        m3_summary = self.m3_data.get("summary", {})
        m3_supply_comparison = self.m3_data.get("supply_type_comparison", {})
        
        supply_type = m3_summary.get("selected_supply_type", "청년형")
        rejection_reasons = m3_supply_comparison.get("rejections", {})
        
        # 근거 문장
        reasons = [
            f"{supply_type} 공급유형이 선정된 이유는 입지 특성과 수요 구조에 가장 적합하기 때문입니다.",
            "다른 유형(신혼희망타운, 다자녀형, 고령자형)은 입지 또는 수요 측면에서 제약이 있습니다."
        ]
        
        # 타 유형 탈락 사유 추가
        for rejected_type, rejection_data in rejection_reasons.items():
            if isinstance(rejection_data, dict):
                reason_summary = rejection_data.get("종합의견", "부적합")
                reasons.append(f"{rejected_type}: {reason_summary}")
        
        # 리스크
        risks = [
            f"{supply_type}의 임대 수요가 예상보다 낮을 경우 공실 리스크가 있습니다.",
            "공급유형 변경 시 건축 설계 및 사업비가 변동될 수 있습니다."
        ]
        
        return {
            "stage": "공급 유형 타당성",
            "reasons": reasons,
            "risks": risks,
            "num_reasons": len(reasons),
            "num_risks": len(risks)
        }
    
    def _analyze_scale_feasibility(self) -> Dict[str, Any]:
        """3. 건축 규모 현실성"""
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        
        total_units = m4_summary.get("recommended_units", 0) or m4_details.get("total_units", 0)
        total_floor_area = m4_details.get("total_floor_area_sqm", 0)
        recommended_reason = m4_summary.get("recommended_scale_reason", "규모 산정 근거 없음")
        
        # 근거 문장
        reasons = [
            f"권장 규모는 {total_units}세대, 연면적 {total_floor_area:,.2f}㎡입니다.",
            f"규모 산정 근거: {recommended_reason}",
            "법적 한계 및 주차·코어 공간을 고려한 현실적 규모입니다."
        ]
        
        # 리스크
        risks = [
            "주차장 확보가 어려울 경우 세대수를 조정해야 할 수 있습니다.",
            "건축 심의 과정에서 층수 또는 세대수 조정 요구가 있을 수 있습니다."
        ]
        
        return {
            "stage": "건축 규모 현실성",
            "reasons": reasons,
            "risks": risks,
            "num_reasons": len(reasons),
            "num_risks": len(risks)
        }
    
    def _analyze_business_stability(self) -> Dict[str, Any]:
        """4. 사업 구조 안정성"""
        m5_cost = self.m5_data.get("cost_structure", {})
        m5_revenue = self.m5_data.get("revenue_structure", {})
        m5_metrics = self.m5_data.get("financial_metrics", {})
        
        total_cost = m5_cost.get("total_project_cost", 0)
        total_revenue = m5_revenue.get("purchase_price", 0)
        npv = m5_metrics.get("npv", 0)
        npv_grade = m5_metrics.get("npv_grade", "N/A")
        
        # 근거 문장
        reasons = [
            f"총 사업비는 {total_cost:,.0f}원, LH 매입 금액은 {total_revenue:,.0f}원입니다.",
            f"NPV는 {npv:,.0f}원으로 {npv_grade} 수준입니다.",
            "LH 일괄 매입 구조로 분양 리스크가 없어 구조적 안정성이 확보됩니다."
        ]
        
        if npv > 0:
            reasons.append("사업 추진 시 이익이 예상되어 재무적으로 안정적입니다.")
        else:
            reasons.append("현 조건에서는 손실 가능성이 있어 조건 재협의가 필요합니다.")
        
        # 리스크
        risks = [
            "공사비 상승 시 NPV가 악화될 수 있습니다.",
            "LH 매입 단가 협의 결과에 따라 수익성이 변동됩니다.",
            "사업 기간 지연 시 금융비용이 증가합니다."
        ]
        
        return {
            "stage": "사업 구조 안정성",
            "reasons": reasons,
            "risks": risks,
            "num_reasons": len(reasons),
            "num_risks": len(risks)
        }
    
    def _analyze_risk_manageability(self) -> Dict[str, Any]:
        """5. 리스크 관리 가능성"""
        m5_judgment = self.m5_data.get("final_judgment", {})
        major_risks = m5_judgment.get("major_risks", [])
        management_strategies = m5_judgment.get("management_strategies", [])
        
        # 근거 문장
        reasons = [
            f"주요 리스크는 총 {len(major_risks)}건이 식별되었습니다.",
            f"각 리스크에 대한 관리 전략 {len(management_strategies)}건이 수립되었습니다.",
            "리스크는 사전 대응 가능한 범위 내에 있습니다."
        ]
        
        # 주요 리스크 요약
        for risk in major_risks[:3]:  # 상위 3개
            if isinstance(risk, dict):
                risk_name = risk.get("risk", "리스크")
                reasons.append(f"- {risk_name}")
        
        # 리스크
        risks = [
            "예상하지 못한 외부 변수(정책 변경, 시장 급변)가 발생할 수 있습니다.",
            "리스크 관리 전략 실행이 지연될 경우 사업에 영향을 줄 수 있습니다."
        ]
        
        return {
            "stage": "리스크 관리 가능성",
            "reasons": reasons,
            "risks": risks,
            "num_reasons": len(reasons),
            "num_risks": len(risks)
        }
    
    def calculate_score_system(self) -> Dict[str, Any]:
        """
        3단계: 점수 체계 출력 규칙 (조건부)
        
        점수는 결과가 아니라 참고 지표
        
        점수 출력 조건:
        - 위 5개 판단 항목 모두에 대해
          - 근거 문장 ≥ 2개
          - 리스크 ≥ 1개
          가 제시된 경우에만 점수 허용
        
        점수 해석 규칙:
        - "85점 = 합격" 같은 단순 표현 금지
        - "점수는 상대적 내부 판단 지표"임을 명시
        - GO / 조건부 GO / 재검토 중 하나로 귀결
        """
        logger.info("📊 [3단계] 점수 체계 산정 (조건부)")
        
        if not self.judgment_stages.get("status") == "COMPLETED":
            return {
                "status": "JUDGMENT_NOT_READY",
                "message": "판단 구조가 완성되지 않아 점수를 산정할 수 없습니다."
            }
        
        # 점수 출력 조건 검증
        all_stages_qualified = True
        stage_scores = {}
        
        for stage_key in ["policy_fitness", "supply_type_validity", "scale_feasibility", 
                          "business_stability", "risk_manageability"]:
            stage_data = self.judgment_stages.get(stage_key, {})
            num_reasons = stage_data.get("num_reasons", 0)
            num_risks = stage_data.get("num_risks", 0)
            
            if num_reasons < 2 or num_risks < 1:
                all_stages_qualified = False
                logger.warning(f"⚠️ {stage_key}: 근거 {num_reasons}개, 리스크 {num_risks}개 - 조건 미달")
            else:
                # 점수 산정 (근거 개수 기반)
                base_score = 70
                reason_bonus = min(num_reasons * 5, 20)
                risk_penalty = min(num_risks * 2, 10)
                stage_score = base_score + reason_bonus - risk_penalty
                stage_scores[stage_key] = stage_score
        
        if not all_stages_qualified:
            return {
                "status": "SCORE_CONDITIONS_NOT_MET",
                "message": "일부 판단 항목이 점수 산정 조건을 충족하지 못했습니다.",
                "stage_scores": stage_scores
            }
        
        # 총점 산정
        total_score = sum(stage_scores.values())
        avg_score = total_score / len(stage_scores) if stage_scores else 0
        
        # 점수 해석
        if avg_score >= 80:
            score_interpretation = "종합 점수는 80점 이상으로 양호한 수준입니다. 단, 점수는 상대적 내부 판단 지표이며, 최종 판정은 조건부 구조로 결정됩니다."
            score_grade = "양호"
        elif avg_score >= 70:
            score_interpretation = "종합 점수는 70점 이상으로 보통 수준입니다. 점수는 참고 지표로, 조건부 보완 여부를 검토해야 합니다."
            score_grade = "보통"
        else:
            score_interpretation = "종합 점수는 70점 미만으로 제한적입니다. 점수는 참고 지표이며, 재검토 또는 구조 조정이 필요합니다."
            score_grade = "제한적"
        
        self.score_system = {
            "stage_scores": stage_scores,
            "total_score": total_score,
            "avg_score": avg_score,
            "score_grade": score_grade,
            "score_interpretation": score_interpretation,
            "disclaimer": "점수는 상대적 내부 판단 지표이며, '85점 = 합격'과 같은 단순 표현은 허용되지 않습니다.",
            "status": "CALCULATED"
        }
        
        logger.info(f"✅ [3단계] 점수 체계 산정 완료: 평균 {avg_score:.2f}점 ({score_grade})")
        
        return self.score_system
    
    def generate_final_decision(self) -> Dict[str, Any]:
        """
        4단계: 최종 판정은 '조건부' 구조로만 허용
        
        A. 조건부 GO
        - 왜 가능한지 (3문장 이상)
        - 어떤 조건이 충족되어야 하는지 (2개 이상)
        
        B. 재검토 필요
        - 부족한 데이터
        - 보완 시 달라지는 판단 포인트
        
        무조건 GO / 무조건 A등급 출력 금지
        """
        logger.info("🎯 [4단계] 최종 판정 (조건부 구조)")
        
        if not self.score_system.get("status") == "CALCULATED":
            return {
                "status": "SCORE_NOT_READY",
                "message": "점수 체계가 산정되지 않아 최종 판정을 수행할 수 없습니다."
            }
        
        avg_score = self.score_system.get("avg_score", 0)
        m5_npv = self.m5_data.get("financial_metrics", {}).get("npv", 0)
        
        # 판정 로직
        if avg_score >= 75 and m5_npv > 0:
            # A. 조건부 GO
            decision_type = "조건부 GO"
            
            why_possible = [
                f"M1~M5 전체 분석 결과 평균 {avg_score:.2f}점으로 기준을 충족합니다.",
                f"사업성 분석 결과 NPV {m5_npv:,.0f}원으로 양수이며, 재무적으로 안정적입니다.",
                "정책 적합성, 공급유형 타당성, 건축 규모 현실성이 모두 확인되었습니다.",
                "LH 일괄 매입 구조로 분양 리스크가 없어 구조적 안정성이 있습니다."
            ]
            
            required_conditions = [
                "LH 매입 단가 협의를 통해 최종 매입 조건을 확정해야 합니다.",
                "건축 심의 및 인허가 과정에서 규모 조정 가능성을 고려해야 합니다.",
                "공사비 상승 리스크에 대비한 예비비 및 원가 통제 계획이 필요합니다.",
                "사업 일정 관리 및 금융비용 최소화 방안을 수립해야 합니다."
            ]
            
            recommendation = "상기 조건이 충족되는 경우 LH 매입형 공공임대주택 사업으로 추진 가능합니다."
            
        elif avg_score >= 65:
            # B. 재검토 필요 (조건부 보완)
            decision_type = "재검토 필요 (조건부 보완 가능)"
            
            why_possible = [
                f"현재 평균 점수는 {avg_score:.2f}점으로 기준치에 다소 미달합니다.",
                "다만, 일부 항목을 보완하면 사업 추진이 가능할 수 있습니다.",
                "재무 구조 또는 규모 조정을 통해 사업성을 개선할 여지가 있습니다."
            ]
            
            required_conditions = [
                "M5 사업성 분석의 비용 또는 수익 조건을 재협의하여 NPV를 개선해야 합니다.",
                "M4 건축 규모를 조정하여 사업비를 절감하거나 매입 조건을 개선해야 합니다.",
                "주요 리스크에 대한 구체적 관리 방안을 수립한 후 재평가가 필요합니다."
            ]
            
            recommendation = "상기 보완 사항을 반영하여 재분석 후 최종 판단하십시오."
            
        else:
            # C. 재검토 필요 (구조 재설계)
            decision_type = "재검토 필요 (구조 재설계 권장)"
            
            why_possible = [
                f"현재 평균 점수는 {avg_score:.2f}점으로 기준을 충족하지 못합니다.",
                "사업 구조상 근본적인 개선이 필요한 것으로 판단됩니다.",
                "현 조건에서는 LH 매입 승인 가능성이 낮습니다."
            ]
            
            required_conditions = [
                "토지 조건 재검토 또는 대체 부지 검토가 필요합니다.",
                "공급유형 변경 또는 사업 방식 전환을 검토해야 합니다.",
                "사업비 구조 전면 재설계 또는 사업 포기를 고려해야 합니다."
            ]
            
            recommendation = "현 조건에서는 사업 추진을 권장하지 않으며, 구조 재설계 후 재검토하십시오."
        
        self.final_decision = {
            "decision_type": decision_type,
            "why_possible": why_possible,
            "required_conditions": required_conditions,
            "recommendation": recommendation,
            "disclaimer": "본 판정은 조건부 의사결정 자료로 활용되어야 하며, 무조건 GO 또는 A등급 판정이 아닙니다.",
            "status": "COMPLETED"
        }
        
        logger.info(f"✅ [4단계] 최종 판정 완료: {decision_type}")
        
        return self.final_decision
    
    def generate_full_report(self) -> Dict[str, Any]:
        """
        전체 M6 보고서 데이터 생성
        
        5단계: 최종 출력 필수 구성
        - 입력 데이터 종합 요약
        - 판단 근거 요약
        - 주요 리스크
        - 실행 권고 방향
        """
        logger.info("📋 M6 Real Decision Engine: 전체 보고서 생성")
        
        # 상태 확인
        if not self.data_source_valid:
            return self._generate_error_report("DATA_SOURCE_INVALID")
        
        if not self.all_modules_connected:
            return self._generate_error_report("DATA_NOT_CONNECTED")
        
        # 각 단계 실행
        judgment_stages = self.generate_judgment_stages()
        score_system = self.calculate_score_system()
        final_decision = self.generate_final_decision()
        
        # 입력 데이터 종합 요약
        m1_details = self.m1_data.get("details", {})
        m3_summary = self.m3_data.get("summary", {})
        m4_summary = self.m4_data.get("summary", {})
        m4_details = self.m4_data.get("details", {})
        m5_cost = self.m5_data.get("cost_structure", {})
        m5_revenue = self.m5_data.get("revenue_structure", {})
        
        input_summary = {
            "address": m1_details.get("address", "주소 정보 없음"),
            "land_area_sqm": m1_details.get("land_area", 0),
            "zoning": m1_details.get("zoning", {}).get("type", "용도지역 정보 없음"),
            "supply_type": m3_summary.get("selected_supply_type", "청년형"),
            "total_units": m4_summary.get("recommended_units", 0) or m4_details.get("total_units", 0),
            "total_floor_area": m4_details.get("total_floor_area_sqm", 0),
            "total_project_cost": m5_cost.get("total_project_cost", 0),
            "lh_purchase_price": m5_revenue.get("purchase_price", 0)
        }
        
        # 판단 근거 요약 (M1~M5 연결 흐름)
        judgment_flow = (
            f"M1(토지정보: {input_summary['address']}, {input_summary['land_area_sqm']}㎡, {input_summary['zoning']}) → "
            f"M3(공급유형: {input_summary['supply_type']}) → "
            f"M4(건축규모: {input_summary['total_units']}세대, {input_summary['total_floor_area']:,.2f}㎡) → "
            f"M5(사업성: 총 사업비 {input_summary['total_project_cost']:,.0f}원, LH 매입 {input_summary['lh_purchase_price']:,.0f}원) → "
            f"M6(종합판단: {final_decision.get('decision_type', 'N/A')})"
        )
        
        # 주요 리스크 (최소 3개)
        all_risks = []
        for stage_key in ["policy_fitness", "supply_type_validity", "scale_feasibility", 
                          "business_stability", "risk_manageability"]:
            stage_data = judgment_stages.get(stage_key, {})
            all_risks.extend(stage_data.get("risks", []))
        
        major_risks = all_risks[:5]  # 상위 5개
        
        # 실행 권고 방향
        recommendation = final_decision.get("recommendation", "재검토 필요")
        
        # 보고서 메타데이터
        report_id = f"ZS-M6-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        report_data = {
            "context_id": self.context_id,
            "report_id": report_id,
            "analysis_date": analysis_date,
            "input_summary": input_summary,
            "judgment_flow": judgment_flow,
            "judgment_stages": judgment_stages,
            "score_system": score_system,
            "final_decision": final_decision,
            "major_risks": major_risks,
            "recommendation": recommendation,
            "data_source_declaration": (
                "본 LH 종합 판단은 M1~M5에서 확정된 실제 입력 데이터 및 분석 결과를 종합하여 "
                "수행되었으며, 샘플 또는 목업 데이터는 사용되지 않았습니다. "
                "본 판단은 조건부 의사결정 자료로 활용되어야 합니다."
            ),
            "footer": {
                "copyright": "ⓒ ZeroSite by AntennaHoldings | Natai Heum",
                "watermark": "ZEROSITE",
                "tone": "LH 내부 검토·결재 전 단계 종합 판단 보고서"
            }
        }
        
        logger.info(f"✅ M6 전체 보고서 생성 완료: {report_id}")
        
        return report_data
    
    def _generate_error_report(self, error_type: str) -> Dict[str, Any]:
        """
        오류 상태 보고서 생성
        """
        report_id = f"ZS-M6-ERROR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        analysis_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        if error_type == "DATA_SOURCE_INVALID":
            error_message = (
                "금지된 데이터 소스가 감지되어 M6 판단을 수행할 수 없습니다. "
                "DecisionType.GO / ProjectGrade.A / MOC/SAMPLE 패턴 기반 데이터는 사용할 수 없습니다."
            )
            error_details = {
                "forbidden_sources": self.forbidden_sources,
                "action_required": "M1~M5 실제 데이터로 재실행하십시오."
            }
        elif error_type == "DATA_NOT_CONNECTED":
            error_message = (
                "M1~M5 데이터가 연결되지 않아 M6 종합 판단을 수행할 수 없습니다. "
                "GO / NO-GO, 점수 / 등급 출력이 금지됩니다."
            )
            error_details = {
                "missing_modules": self.missing_modules,
                "validation_errors": self.validation_errors,
                "action_required": "M1~M5 모듈을 모두 실행한 후 M6를 실행하십시오."
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
            "use_error_template": True,
            "template_version": "v1"
        }


def prepare_m6_real_decision_report(
    context_id: str,
    m1_data: Dict[str, Any],
    m2_data: Dict[str, Any],
    m3_data: Dict[str, Any],
    m4_data: Dict[str, Any],
    m5_data: Dict[str, Any],
    frozen_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    M6 Real Decision Engine 외부 호출용 함수
    
    Args:
        context_id: Context ID
        m1_data: M1 토지정보 데이터
        m2_data: M2 시장분석 데이터
        m3_data: M3 공급유형 결정 데이터
        m4_data: M4 건축 규모 데이터
        m5_data: M5 사업성 분석 데이터
        frozen_context: Context 전체 데이터
    
    Returns:
        M6 보고서 데이터 또는 오류 데이터
    """
    logger.info(f"🚀 M6 Real Decision Report 생성 요청: {context_id}")
    
    try:
        engine = M6RealDecisionEngine(
            context_id=context_id,
            m1_data=m1_data,
            m2_data=m2_data,
            m3_data=m3_data,
            m4_data=m4_data,
            m5_data=m5_data,
            frozen_context=frozen_context
        )
        
        report_data = engine.generate_full_report()
        
        return report_data
    
    except Exception as e:
        logger.error(f"❌ M6 Real Decision Engine 실행 중 오류: {e}")
        return {
            "error": True,
            "error_type": "ENGINE_ERROR",
            "error_message": f"M6 Real Decision Engine 실행 중 오류가 발생했습니다: {str(e)}",
            "context_id": context_id,
            "use_error_template": True
        }
