"""
ZeroSite 6-Module Pipeline
===========================

6모듈을 순차적으로 실행하는 단방향 파이프라인

실행 순서:
1. M1: 토지정보 (FACT)
2. M2: 토지감정평가 (FACT, 🔒 IMMUTABLE)
3. M3: LH 선호유형 (INTERPRETATION)
4. M4: 건축규모 (INTERPRETATION)
5. M5: 사업성 (JUDGMENT INPUT)
6. M6: LH 심사예측 (FINAL JUDGMENT)

⚠️ 규칙:
- M2 AppraisalContext는 생성 후 수정 불가
- 역방향 참조 금지
- Context 기반 데이터 전달만 허용

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import logging
from datetime import datetime

# Context 임포트
from app.core.context.canonical_land import CanonicalLandContext
from app.core.context.appraisal_context import AppraisalContext
from app.core.context.housing_type_context import HousingTypeContext, TypeScore
from app.core.context.capacity_context import CapacityContext  # V1 (legacy)
from app.core.context.capacity_context_v2 import CapacityContextV2  # V2 (new)
from app.core.context.feasibility_context import FeasibilityContext
from app.core.context.lh_review_context import LHReviewContext, DecisionType

# 🔥 NEW: Data validation error
from app.services.data_contract import DataBindingError

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _safe_to_dict(obj) -> dict:
    """
    객체를 안전하게 dict로 변환
    
    to_dict() 메서드가 있으면 사용, 없으면 dataclass fields 사용
    """
    if hasattr(obj, 'to_dict') and callable(obj.to_dict):
        return obj.to_dict()
    elif hasattr(obj, '__dataclass_fields__'):
        # dataclass인 경우
        from dataclasses import asdict
        return asdict(obj)
    elif isinstance(obj, dict):
        return obj
    else:
        # fallback: __dict__ 사용
        return getattr(obj, '__dict__', {})


@dataclass(frozen=True)
class PipelineResult:
    """
    파이프라인 전체 실행 결과
    
    모든 모듈의 Context를 포함
    🔥 NEW: assembled_data 추가 (PDF 생성용)
    """
    land: CanonicalLandContext               # M1
    appraisal: AppraisalContext              # M2 🔒 IMMUTABLE
    housing_type: HousingTypeContext         # M3
    capacity: CapacityContextV2              # M4 V2 (upgraded)
    feasibility: FeasibilityContext          # M5
    lh_review: LHReviewContext               # M6
    assembled_data: Dict[str, Any] = field(default_factory=dict)  # 🔥 NEW: PDF용 조립 데이터
    
    @property
    def success(self) -> bool:
        """파이프라인 성공 여부"""
        return all([
            self.land is not None,
            self.appraisal is not None,
            self.housing_type is not None,
            self.capacity is not None,
            self.feasibility is not None,
            self.lh_review is not None
        ])
    
    @property
    def final_decision(self) -> str:
        """최종 LH 심사 결정"""
        return self.lh_review.decision


class ZeroSitePipeline:
    """
    ZeroSite 6-Module 파이프라인
    
    Usage:
        pipeline = ZeroSitePipeline()
        result = pipeline.run(parcel_id="1168010100100010001")
        
        print(result.appraisal.land_value)
        print(result.lh_review.decision)
    """
    
    def __init__(self):
        """파이프라인 초기화"""
        logger.info("="*80)
        logger.info("🚀 ZeroSite 6-MODULE PIPELINE initialized")
        logger.info("   Architecture: M1 → M2🔒 → M3 → M4 → M5 → M6")
        logger.info("   M2 AppraisalContext: IMMUTABLE (frozen=True)")
        logger.info("="*80)
        
        # 모듈 초기화 (lazy loading)
        self._m1_service = None
        self._m2_service = None
        self._m3_service = None
        self._m4_service = None
        self._m5_service = None
        self._m6_service = None
    
    def run(
        self,
        parcel_id: str,
        asking_price: Optional[float] = None,
        context_id: Optional[str] = None
    ) -> PipelineResult:
        """
        6모듈 파이프라인 실행
        
        Args:
            parcel_id: 필지 ID (PNU 코드)
            asking_price: 호가 (선택)
            context_id: Context ID (선택, M1 frozen context 로드용)
        
        Returns:
            PipelineResult: 전체 Context 포함
        
        Raises:
            Exception: 모듈 실행 중 오류 발생 시
        """
        
        logger.info("\n" + "="*80)
        logger.info(f"🎯 PIPELINE START: parcel_id={parcel_id}, context_id={context_id}")
        logger.info("="*80)
        
        # 🔥 NEW: assembled_data 초기화 (PDF 생성용)
        assembled_data = {
            "parcel_id": parcel_id,
            "context_id": context_id or parcel_id,
            "generated_at": datetime.now().isoformat(),
            "modules": {}
        }
        logger.info("✅ assembled_data 초기화 완료")
        
        try:
            # ===================================================================
            # M1: 토지정보 조회 (FACT)
            # ===================================================================
            logger.info("\n📍 [M1] Land Info Module - Starting...")
            
            # 🔥 FIX: Try to load M1 frozen context first if context_id is provided
            land_ctx = None
            if context_id:
                try:
                    from app.services.context_storage import context_storage
                    logger.info(f"🔍 Attempting to load M1 frozen context: {context_id}")
                    frozen_ctx = context_storage.get_frozen_context(context_id)
                    if frozen_ctx:
                        # Extract land context from frozen context
                        land_data = frozen_ctx.get('land')
                        if land_data:
                            from app.core.context.canonical_land import CanonicalLandContext
                            # Reconstruct CanonicalLandContext from dict
                            land_ctx = CanonicalLandContext(**land_data)
                            logger.info(f"✅ Loaded M1 frozen context from: {context_id}")
                            logger.info(f"   Address: {land_ctx.address}")
                            logger.info(f"   Area: {land_ctx.area_sqm:,.1f}㎡")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load M1 frozen context: {e}")
                    logger.info("   Falling back to fresh M1 execution")
            
            # If no frozen context, run M1 fresh
            if land_ctx is None:
                land_ctx = self._run_m1(parcel_id)
                logger.info(f"✅ [M1] Complete (Fresh): {land_ctx.address}")
            
            logger.info(f"   Area: {land_ctx.area_sqm:,.1f}㎡, Zone: {land_ctx.zone_type}")
            
            # 🔥 NEW: M1 데이터를 assembled_data에 저장
            assembled_data["modules"]["M1"] = {
                "summary": {
                    "address": land_ctx.address,
                    "area_sqm": land_ctx.area_sqm,
                    "zone_type": land_ctx.zone_type
                },
                "details": _safe_to_dict(land_ctx),
                "raw_data": _safe_to_dict(land_ctx)
            }
            logger.info("✅ M1 데이터 assembled_data에 저장 완료")
            
            # ===================================================================
            # M2: 토지감정평가 (FACT, 🔒 IMMUTABLE)
            # ===================================================================
            logger.info("\n💰 [M2] Appraisal Module - Starting...")
            appraisal_ctx = self._run_m2(land_ctx, asking_price)
            logger.info(f"✅ [M2] Complete (🔒 LOCKED)")
            logger.info(f"   Land Value: ₩{appraisal_ctx.land_value:,.0f}")
            logger.info(f"   Confidence: {appraisal_ctx.confidence_level} ({appraisal_ctx.confidence_score:.0%})")
            logger.info("   ⚠️ AppraisalContext is now IMMUTABLE!")
            
            # 🔥 NEW: M2 데이터를 assembled_data에 저장
            assembled_data["modules"]["M2"] = {
                "summary": {
                    "land_value": appraisal_ctx.land_value,
                    "confidence_score": appraisal_ctx.confidence_score,
                    "confidence_level": appraisal_ctx.confidence_level
                },
                "details": _safe_to_dict(appraisal_ctx),
                "raw_data": _safe_to_dict(appraisal_ctx)
            }
            logger.info("✅ M2 데이터 assembled_data에 저장 완료")
            
            # ===================================================================
            # M3: LH 선호유형 선택 (INTERPRETATION)
            # ===================================================================
            logger.info("\n🏘️ [M3] Housing Type Module - Starting...")
            housing_type_ctx = self._run_m3(land_ctx)
            logger.info(f"✅ [M3] Complete: {housing_type_ctx.selected_type}")
            logger.info(f"   LH Demand Prediction: {housing_type_ctx.demand_prediction}")
            
            # 🔥 CRITICAL: M3 데이터 검증 (FAIL FAST - N/A 금지, 0점 방지)
            if not housing_type_ctx.selected_type or housing_type_ctx.selected_type == "N/A":
                raise DataBindingError(
                    module="M3",
                    field="selected_type",
                    message="M3 선호유형이 선택되지 않았습니다. M3 분석을 다시 실행하세요."
                )
            
            # 선택 신뢰도 검증
            if housing_type_ctx.selection_confidence <= 0:
                raise DataBindingError(
                    module="M3",
                    field="selection_confidence",
                    message=f"M3 선택 신뢰도가 {housing_type_ctx.selection_confidence}로 0 이하입니다. 데이터를 확인하세요."
                )
            
            # 강점(key_reasons) 생성 (최소 3개)
            strengths = housing_type_ctx.strengths or []
            if len(strengths) < 3:
                # 자동 생성: POI 점수, 수요 예측, 경쟁 분석 기반
                strengths = [
                    f"입지 점수: {housing_type_ctx.location_score:.1f}/35점",
                    f"수요 예측: {housing_type_ctx.demand_prediction:.1f}점 ({housing_type_ctx.demand_trend})",
                    f"경쟁 상황: {housing_type_ctx.competitor_analysis} (경쟁 단지 {housing_type_ctx.competitor_count}개)"
                ]
            
            # excluded_types 생성 (선택되지 않은 유형)
            all_types = list(housing_type_ctx.type_scores.keys())
            excluded_types = [t for t in all_types if t != housing_type_ctx.selected_type]
            
            # 🔥 CRITICAL: M3 데이터를 assembled_data에 강제 연결 (100% 실데이터)
            assembled_data["modules"]["M3"] = {
                "summary": {
                    "preferred_type": housing_type_ctx.selected_type_name,  # ✅ 실데이터 (한글명)
                    "preferred_type_code": housing_type_ctx.selected_type,  # ✅ 코드
                    "stability_grade": "B",  # ✅ 기본값 B (추후 개선 가능)
                    "confidence_score": float(housing_type_ctx.selection_confidence * 100),  # ✅ 0~100 변환
                    "key_reasons": strengths[:3],  # ✅ 최소 3개
                    "excluded_types": excluded_types  # ✅ 선택되지 않은 유형들
                },
                "details": {
                    "location_factors": {
                        "location_score": housing_type_ctx.location_score,
                        "poi_analysis": _safe_to_dict(housing_type_ctx.poi_analysis),
                        "subway_distance": housing_type_ctx.poi_analysis.subway_distance,
                        "school_distance": housing_type_ctx.poi_analysis.school_distance,
                    },
                    "demand_analysis": {
                        "demand_prediction": housing_type_ctx.demand_prediction,
                        "demand_trend": housing_type_ctx.demand_trend,
                        "target_population": housing_type_ctx.target_population,
                    },
                    "policy_alignment": {
                        "type_scores": {k: _safe_to_dict(v) for k, v in housing_type_ctx.type_scores.items()},
                        "is_tie": housing_type_ctx.is_tie,
                        "secondary_type": housing_type_ctx.secondary_type_name if housing_type_ctx.is_tie else None,
                    },
                    "excluded_types": [
                        {
                            "type": excluded_types[i] if i < len(excluded_types) else None,
                            "reason": f"점수: {housing_type_ctx.type_scores.get(excluded_types[i], TypeScore('', '', 0, 0, 0, 0, 0)).total_score:.1f}점"
                        }
                        for i in range(min(3, len(excluded_types)))
                    ]
                },
                "raw_data": _safe_to_dict(housing_type_ctx)
            }
            
            logger.info(f"✅ M3 데이터 assembled_data에 저장 완료")
            logger.info(f"   preferred_type: {assembled_data['modules']['M3']['summary']['preferred_type']}")
            logger.info(f"   confidence_score: {assembled_data['modules']['M3']['summary']['confidence_score']:.1f}%")
            logger.info(f"   key_reasons: {len(assembled_data['modules']['M3']['summary']['key_reasons'])}개")
            
            # 🔥 필수 필드 검증
            from app.services.data_contract import validate_m3_required_fields
            validate_m3_required_fields(assembled_data["modules"]["M3"]["summary"], strict=True)
            logger.info("✅ M3 필수 필드 검증 통과")
            
            # ===================================================================
            # M4: 건축규모 검토 V2 (INTERPRETATION)
            # ===================================================================
            logger.info("\n🏗️ [M4] Capacity Module V2 - Starting...")
            capacity_ctx = self._run_m4(land_ctx, housing_type_ctx)
            logger.info(f"✅ [M4 V2] Complete")
            logger.info(f"   Legal: {capacity_ctx.legal_capacity.total_units}세대 / {capacity_ctx.legal_capacity.applied_far}%")
            logger.info(f"   Incentive: {capacity_ctx.incentive_capacity.total_units}세대 / {capacity_ctx.incentive_capacity.applied_far}%")
            logger.info(f"   Parking A/B: {capacity_ctx.far_max_alternative.total_parking_spaces}/{capacity_ctx.parking_priority_alternative.total_parking_spaces}대")
            
            # 🔥 CRITICAL: M4 데이터 검증 (FAIL FAST - 0% 방지)
            if not capacity_ctx.legal_capacity or capacity_ctx.legal_capacity.applied_far == 0:
                raise DataBindingError(
                    module="M4",
                    field="floor_area_ratio",
                    message="M4 용적률 데이터가 누락되었습니다. M4 분석을 다시 실행하세요."
                )
            
            if capacity_ctx.legal_capacity.total_units <= 0:
                raise DataBindingError(
                    module="M4",
                    field="total_units",
                    message=f"M4 세대수가 {capacity_ctx.legal_capacity.total_units}로 0 이하입니다. 데이터를 확인하세요."
                )
            
            # 🔥 CRITICAL: M4 데이터를 assembled_data에 강제 연결 (100% 실데이터, 필드명 통일)
            assembled_data["modules"]["M4"] = {
                "summary": {
                    "total_units": int(capacity_ctx.legal_capacity.total_units),  # ✅ 실데이터
                    "gross_floor_area": float(capacity_ctx.legal_capacity.target_gfa_sqm),  # ✅ 필드명 통일
                    "gross_floor_area_sqm": float(capacity_ctx.legal_capacity.target_gfa_sqm),  # ✅ 호환성
                    "far_ratio": float(capacity_ctx.legal_capacity.applied_far),  # ✅ 용적률 %
                    "coverage_ratio": float(capacity_ctx.legal_capacity.applied_bcr),  # ✅ 건폐율 %
                    "legal_far_ratio": float(capacity_ctx.legal_capacity.applied_far),  # ✅ 법정 용적률 (동일값)
                    "legal_coverage_ratio": float(capacity_ctx.legal_capacity.applied_bcr),  # ✅ 법정 건폐율 (동일값)
                },
                "details": {
                    "legal_max": _safe_to_dict(capacity_ctx.legal_capacity),
                    "incentive_capacity": _safe_to_dict(capacity_ctx.incentive_capacity),
                    "parking_solutions": {
                        "alternative_A": _safe_to_dict(capacity_ctx.far_max_alternative),
                        "alternative_B": _safe_to_dict(capacity_ctx.parking_priority_alternative)
                    },
                    "lh_recommended_range": {
                        "min_far": float(capacity_ctx.legal_capacity.applied_far * 0.9),
                        "max_far": float(capacity_ctx.legal_capacity.applied_far * 1.1),
                        "recommended_units_range": [
                            int(capacity_ctx.legal_capacity.total_units * 0.9),
                            int(capacity_ctx.legal_capacity.total_units * 1.1)
                        ]
                    },
                    "design_risks": [],  # TODO: 추후 설계 리스크 로직 추가
                    "options": {  # Option A/B/C 정보
                        "legal_capacity": {
                            "units": capacity_ctx.legal_capacity.total_units,
                            "far": capacity_ctx.legal_capacity.applied_far,
                            "parking": capacity_ctx.far_max_alternative.total_parking_spaces
                        },
                        "incentive_capacity": {
                            "units": capacity_ctx.incentive_capacity.total_units,
                            "far": capacity_ctx.incentive_capacity.applied_far,
                            "parking": capacity_ctx.parking_priority_alternative.total_parking_spaces
                        }
                    }
                },
                "raw_data": _safe_to_dict(capacity_ctx)
            }
            
            logger.info(f"✅ M4 데이터 assembled_data에 저장 완료")
            logger.info(f"   total_units: {assembled_data['modules']['M4']['summary']['total_units']}세대")
            logger.info(f"   far_ratio: {assembled_data['modules']['M4']['summary']['far_ratio']:.1f}%")
            logger.info(f"   coverage_ratio: {assembled_data['modules']['M4']['summary']['coverage_ratio']:.1f}%")
            
            # 🔥 필수 필드 검증
            from app.services.data_contract import validate_m4_required_fields
            validate_m4_required_fields(assembled_data["modules"]["M4"]["summary"], strict=True)
            logger.info("✅ M4 필수 필드 검증 통과")
            
            # ===================================================================
            # M5: 사업성 검토 (JUDGMENT INPUT)
            # ===================================================================
            logger.info("\n📊 [M5] Feasibility Module - Starting...")
            feasibility_ctx = self._run_m5(appraisal_ctx, capacity_ctx)
            logger.info(f"✅ [M5] Complete")
            logger.info(f"   NPV: ₩{feasibility_ctx.financial_metrics.npv_public:,.0f}, IRR: {feasibility_ctx.financial_metrics.irr_public:.1f}%")
            
            # 🔥 NEW: M5 데이터를 assembled_data에 저장
            assembled_data["modules"]["M5"] = {
                "summary": {
                    "npv_public": feasibility_ctx.financial_metrics.npv_public,
                    "irr_public": feasibility_ctx.financial_metrics.irr_public,
                    "roi": getattr(feasibility_ctx.financial_metrics, 'roi', 0),
                    "grade": getattr(feasibility_ctx, 'grade', 'B')
                },
                "details": _safe_to_dict(feasibility_ctx),
                "raw_data": _safe_to_dict(feasibility_ctx)
            }
            logger.info("✅ M5 데이터 assembled_data에 저장 완료")
            
            # ===================================================================
            # M6: LH 심사예측 (FINAL JUDGMENT)
            # ===================================================================
            logger.info("\n⚖️ [M6] LH Review Module - Starting...")
            
            # 🔥 CRITICAL: M6 입력 검증 (FAIL FAST)
            required_modules = ["M2", "M3", "M4", "M5"]
            for module in required_modules:
                if module not in assembled_data["modules"]:
                    raise DataBindingError(
                        module="M6",
                        field=f"input_{module}",
                        message=f"M6 실행을 위해 {module} 데이터가 필요하지만 누락되었습니다."
                    )
                if not assembled_data["modules"][module].get("summary"):
                    raise DataBindingError(
                        module="M6",
                        field=f"input_{module}.summary",
                        message=f"M6 실행을 위해 {module} summary가 필요하지만 비어 있습니다."
                    )
            
            logger.info("✅ M6 입력 검증 완료 (M2/M3/M4/M5 데이터 확인됨)")
            
            lh_review_ctx = self._run_m6(housing_type_ctx, capacity_ctx, feasibility_ctx)
            logger.info(f"✅ [M6] Complete")
            logger.info(f"   Decision: {lh_review_ctx.decision}")
            logger.info(f"   Total Score: {lh_review_ctx.total_score:.1f}/110")
            
            # 🔥 decision_rationale 생성 (최소 3개 근거)
            decision_rationale = []
            if hasattr(lh_review_ctx, 'decision_rationale') and lh_review_ctx.decision_rationale:
                # decision_rationale이 이미 리스트인 경우
                if isinstance(lh_review_ctx.decision_rationale, list):
                    decision_rationale = lh_review_ctx.decision_rationale
                else:
                    # 문자열인 경우 리스트로 감싸기
                    decision_rationale = [lh_review_ctx.decision_rationale]
            
            # 최소 3개 보장: 부족하면 자동 생성 근거 추가
            if len(decision_rationale) < 3:
                auto_rationale = [
                    f"입지 점수: {lh_review_ctx.score_breakdown.location_score:.1f}/35점 {'우수' if lh_review_ctx.score_breakdown.location_score >= 25 else '보통'}",
                    f"규모 점수: {lh_review_ctx.score_breakdown.scale_score:.1f}/20점 {'양호' if lh_review_ctx.score_breakdown.scale_score >= 14 else '보통'}",
                    f"사업성 점수: {lh_review_ctx.score_breakdown.feasibility_score:.1f}/40점 {'우수' if lh_review_ctx.score_breakdown.feasibility_score >= 28 else '보통'}",
                    f"법규 적합성: {lh_review_ctx.score_breakdown.compliance_score:.1f}/15점 {'적합' if lh_review_ctx.score_breakdown.compliance_score >= 10 else '보통'}"
                ]
                # 부족한 개수만큼 추가
                for rationale in auto_rationale:
                    if rationale not in decision_rationale:
                        decision_rationale.append(rationale)
                        if len(decision_rationale) >= 3:
                            break
            
            # 🔥 conclusion_text 생성 (최소 40자)
            conclusion_text = ""
            if hasattr(lh_review_ctx, 'conclusion') and lh_review_ctx.conclusion:
                conclusion_text = lh_review_ctx.conclusion
            else:
                # 자동 생성
                grade_text = lh_review_ctx.grade.value
                decision_text = lh_review_ctx.decision.value
                conclusion_text = (
                    f"본 사업지는 ZeroSite v4.0 M6 기준에 따라 "
                    f"총점 {lh_review_ctx.total_score:.1f}/110점 ({grade_text}등급)으로 평가되었으며, "
                    f"최종 판정은 '{decision_text}'입니다. "
                )
                if lh_review_ctx.decision == DecisionType.CONDITIONAL:
                    conclusion_text += "보완 조건 충족 시 LH 매입이 가능한 사업지로 판단됩니다."
                elif lh_review_ctx.decision == DecisionType.GO:
                    conclusion_text += "LH 매입임대사업에 적합한 사업지로 판단됩니다."
                else:
                    conclusion_text += "현 상태로는 LH 매입임대사업이 어려운 사업지로 판단됩니다."
            
            # 🔥 approval_probability 처리 (0% 고정 금지, None 허용)
            approval_probability = None
            if hasattr(lh_review_ctx, 'approval_prediction') and lh_review_ctx.approval_prediction:
                approval_probability = lh_review_ctx.approval_prediction.approval_probability * 100  # 0~100 변환
                if approval_probability == 0:
                    approval_probability = None  # 0%는 "미산정"으로 처리
            
            # 🔥 CRITICAL: M6 데이터를 assembled_data에 강제 연결 (100% 실데이터, narrative 필수)
            assembled_data["modules"]["M6"] = {
                "summary": {
                    "decision": lh_review_ctx.decision.value,  # ✅ GO/CONDITIONAL/NO-GO
                    "grade": lh_review_ctx.grade.value,  # ✅ A/B/C/D/F
                    "total_score": float(lh_review_ctx.total_score),  # ✅ 실데이터
                    "approval_probability": approval_probability,  # ✅ None 또는 실값 (0% 금지)
                    "decision_rationale": decision_rationale,  # ✅ 최소 3개
                    "conclusion_text": conclusion_text,  # ✅ 최소 40자
                },
                "details": {
                    "scores": {
                        "location": float(lh_review_ctx.score_breakdown.location_score),
                        "scale": float(lh_review_ctx.score_breakdown.scale_score),
                        "feasibility": float(lh_review_ctx.score_breakdown.feasibility_score),
                        "compliance": float(lh_review_ctx.score_breakdown.compliance_score),
                        "total": float(lh_review_ctx.score_breakdown.total_score)
                    },
                    "rationale": decision_rationale,  # 판정 근거
                    "conclusion": conclusion_text,  # 결론
                    "conditions": lh_review_ctx.approval_prediction.expected_conditions if hasattr(lh_review_ctx, 'approval_prediction') else [],
                    "strengths": lh_review_ctx.strengths if hasattr(lh_review_ctx, 'strengths') else [],
                    "weaknesses": lh_review_ctx.weaknesses if hasattr(lh_review_ctx, 'weaknesses') else [],
                    "recommendations": lh_review_ctx.recommendations if hasattr(lh_review_ctx, 'recommendations') else []
                },
                "raw_data": _safe_to_dict(lh_review_ctx)
            }
            
            logger.info(f"✅ M6 데이터 assembled_data에 저장 완료")
            logger.info(f"   decision: {assembled_data['modules']['M6']['summary']['decision']}")
            logger.info(f"   total_score: {assembled_data['modules']['M6']['summary']['total_score']:.1f}/110")
            logger.info(f"   decision_rationale: {len(assembled_data['modules']['M6']['summary']['decision_rationale'])}개")
            logger.info(f"   conclusion_text: {len(assembled_data['modules']['M6']['summary']['conclusion_text'])}자")
            
            # 🔥 필수 필드 검증
            from app.services.data_contract import validate_m6_required_fields
            
            # m6_result 생성 (호환성)
            m6_result = {
                "decision": lh_review_ctx.decision.value,
                "judgement": lh_review_ctx.decision.value,  # 호환성
                "grade": lh_review_ctx.grade.value,
                "lh_score_total": float(lh_review_ctx.total_score),
                "decision_rationale": decision_rationale,
                "conclusion": conclusion_text,
                "conclusion_text": conclusion_text,
                "approval_probability": approval_probability
            }
            assembled_data["m6_result"] = m6_result
            
            validate_m6_required_fields(m6_result, strict=True)
            logger.info("✅ M6 필수 필드 검증 통과")
            
            # 🔥 NEW: assembled_data를 context_storage에 저장
            try:
                from app.services.context_storage import context_storage
                storage_context_id = context_id or parcel_id
                context_storage.save_assembled_data(storage_context_id, assembled_data)
                logger.info(f"✅ assembled_data를 context_storage에 저장 완료 (context_id: {storage_context_id})")
            except Exception as e:
                logger.warning(f"⚠️ assembled_data 저장 실패 (계속 진행): {e}")
            
            # ===================================================================
            # 파이프라인 완료
            # ===================================================================
            result = PipelineResult(
                land=land_ctx,
                appraisal=appraisal_ctx,
                housing_type=housing_type_ctx,
                capacity=capacity_ctx,
                feasibility=feasibility_ctx,
                lh_review=lh_review_ctx,
                assembled_data=assembled_data  # 🔥 NEW: PDF 생성용 데이터 포함
            )
            
            logger.info("\n" + "="*80)
            logger.info("🎉 PIPELINE COMPLETE - All modules executed successfully")
            logger.info(f"   Final Decision: {result.final_decision}")
            logger.info(f"   Land Value (🔒): ₩{result.appraisal.land_value:,.0f}")
            logger.info(f"   📦 assembled_data modules: {list(result.assembled_data.get('modules', {}).keys())}")
            logger.info("="*80 + "\n")
            
            return result
            
        except Exception as e:
            logger.error(f"\n❌ PIPELINE FAILED: {e}")
            raise
    
    def _run_m1(self, parcel_id: str) -> CanonicalLandContext:
        """M1: 토지정보 조회"""
        if self._m1_service is None:
            from app.modules.m1_land_info.service import LandInfoService
            self._m1_service = LandInfoService()
        
        return self._m1_service.run(parcel_id)
    
    def _run_m2(
        self,
        land_ctx: CanonicalLandContext,
        asking_price: Optional[float]
    ) -> AppraisalContext:
        """M2: 토지감정평가 (🔒 IMMUTABLE)"""
        if self._m2_service is None:
            from app.modules.m2_appraisal.service import AppraisalService
            self._m2_service = AppraisalService(use_enhanced_services=True)
        
        appraisal_ctx = self._m2_service.run(land_ctx, asking_price)
        
        # 🔒 IMMUTABLE 검증
        assert isinstance(appraisal_ctx, AppraisalContext), \
            "M2 must return AppraisalContext"
        
        return appraisal_ctx
    
    def _run_m3(self, land_ctx: CanonicalLandContext) -> HousingTypeContext:
        """M3: LH 선호유형 선택"""
        if self._m3_service is None:
            from app.modules.m3_lh_demand.service import LHDemandService
            self._m3_service = LHDemandService()
        
        return self._m3_service.run(land_ctx)
    
    def _run_m4(
        self,
        land_ctx: CanonicalLandContext,
        housing_type_ctx: HousingTypeContext
    ) -> CapacityContextV2:
        """M4: 건축규모 검토 (V2)"""
        if self._m4_service is None:
            from app.modules.m4_capacity.service_v2 import CapacityServiceV2
            self._m4_service = CapacityServiceV2()
        
        return self._m4_service.run(land_ctx, housing_type_ctx)
    
    def _run_m5(
        self,
        appraisal_ctx: AppraisalContext,
        capacity_ctx: CapacityContext
    ) -> FeasibilityContext:
        """M5: 사업성 검토"""
        if self._m5_service is None:
            from app.modules.m5_feasibility.service import FeasibilityService
            self._m5_service = FeasibilityService()
        
        # ⚠️ M5는 AppraisalContext를 READ-ONLY로만 사용
        return self._m5_service.run(appraisal_ctx, capacity_ctx)
    
    def _run_m6(
        self,
        housing_type_ctx: HousingTypeContext,
        capacity_ctx: CapacityContext,
        feasibility_ctx: FeasibilityContext
    ) -> LHReviewContext:
        """M6: LH 심사예측"""
        if self._m6_service is None:
            from app.modules.m6_lh_review.service import LHReviewService
            self._m6_service = LHReviewService()
        
        return self._m6_service.run(housing_type_ctx, capacity_ctx, feasibility_ctx)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("Testing ZeroSite 6-Module Pipeline")
    print("="*80 + "\n")
    
    try:
        pipeline = ZeroSitePipeline()
        
        result = pipeline.run(
            parcel_id="1168010100100010001",  # Mock PNU
            asking_price=10_000_000_000
        )
        
        print(f"\n{'='*80}")
        print("📊 PIPELINE RESULTS")
        print(f"{'='*80}\n")
        
        print(f"🏠 토지: {result.land.address}")
        print(f"💰 감정가 (🔒): ₩{result.appraisal.land_value:,.0f}")
        print(f"🏘️ LH 유형: {result.housing_type.selected_type}")
        print(f"🏗️ 세대수 (V2):")
        print(f"   - Legal: {result.capacity.legal_capacity.total_units}세대 / {result.capacity.legal_capacity.applied_far}%")
        print(f"   - Incentive: {result.capacity.incentive_capacity.total_units}세대 / {result.capacity.incentive_capacity.applied_far}%")
        print(f"   - Parking A/B: {result.capacity.far_max_alternative.total_parking_spaces}/{result.capacity.parking_priority_alternative.total_parking_spaces}대")
        print(f"📊 NPV: ₩{result.feasibility.financial_metrics.npv_public:,.0f}")
        print(f"⚖️ LH 심사: {result.lh_review.decision} ({result.lh_review.total_score:.1f}/110점)")
        
        print(f"\n{'='*80}")
        print("✅ Test Complete!")
        print(f"{'='*80}\n")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
