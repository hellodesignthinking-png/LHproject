"""
ZeroSite v9.0 - Engine Orchestrator
====================================

모든 v9.0 엔진을 통합하는 오케스트레이터

처리 흐름:
1. Raw Data 수집
2. Normalization Layer 적용
3. 5개 엔진 병렬 실행
   - GIS Engine
   - Financial Engine
   - LH Evaluation Engine
   - Risk Engine
   - Demand Engine
4. Final Recommendation 생성
5. StandardAnalysisOutput 반환

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import uuid

from app.models_v9.standard_schema_v9_0 import (
    StandardAnalysisOutput,
    SiteInfo,
    GISResult,
    FinancialResult,
    LHScores,
    RiskAssessment,
    DemandResult,
    FinalRecommendation,
    DecisionType
)
from app.schemas import Coordinates

from app.engines_v9.gis_engine_v9_0 import GISEngineV90
from app.engines_v9.financial_engine_v9_0 import FinancialEngineV90
from app.engines_v9.lh_evaluation_engine_v9_0 import LHEvaluationEngineV90
from app.engines_v9.risk_engine_v9_0 import RiskEngineV90
from app.engines_v9.demand_engine_v9_0 import DemandEngineV90
from app.services_v9.normalization_layer_v9_0 import NormalizationLayerV90

logger = logging.getLogger(__name__)


class EngineOrchestratorV90:
    """
    Engine Orchestrator v9.0
    
    모든 v9.0 엔진을 통합하여 StandardAnalysisOutput 생성
    """
    
    def __init__(self, kakao_api_key: str):
        """
        Orchestrator 초기화
        
        Args:
            kakao_api_key: Kakao REST API Key
        """
        self.normalizer = NormalizationLayerV90()
        self.gis_engine = GISEngineV90(kakao_api_key=kakao_api_key)
        self.financial_engine = FinancialEngineV90()
        self.lh_engine = LHEvaluationEngineV90()
        self.risk_engine = RiskEngineV90()
        self.demand_engine = DemandEngineV90()
        
        logger.info("🎯 Engine Orchestrator v9.0 초기화 완료")
        logger.info("   ✓ 6개 엔진 로드 완료")
    
    async def analyze_comprehensive(
        self,
        raw_data: Dict[str, Any]
    ) -> StandardAnalysisOutput:
        """
        종합 분석 수행 (v9.0 전체 파이프라인)
        
        Args:
            raw_data: 원시 입력 데이터
            
        Returns:
            StandardAnalysisOutput (정규화된 표준 출력)
        """
        start_time = datetime.now()
        analysis_id = f"anlz_{uuid.uuid4().hex[:12]}"
        
        logger.info("="*80)
        logger.info(f"🚀 ZeroSite v9.0 종합 분석 시작")
        logger.info(f"   Analysis ID: {analysis_id}")
        logger.info("="*80)
        
        # 1. Normalization Layer 적용
        logger.info("📋 Step 1: Data Normalization")
        site_info = self.normalizer.normalize_site_info(raw_data)
        coordinates = Coordinates(
            latitude=site_info.latitude or 37.5665,
            longitude=site_info.longitude or 126.9780
        )
        
        # 2. GIS Engine 실행
        logger.info("📋 Step 2: GIS Analysis")
        gis_result = await self.gis_engine.analyze_comprehensive_gis(
            coordinates=coordinates,
            address=site_info.address
        )
        
        # 3. Financial Engine 실행
        logger.info("📋 Step 3: Financial Analysis")
        unit_count = raw_data.get("unit_count", 33)
        financial_result = self.financial_engine.analyze_comprehensive_financial(
            land_area=site_info.land_area,
            total_land_price=site_info.total_land_price,
            floor_area_ratio=site_info.floor_area_ratio,
            unit_count=unit_count
        )
        
        # 4. LH Evaluation Engine 실행
        logger.info("📋 Step 4: LH Evaluation")
        lh_scores = self.lh_engine.evaluate_comprehensive(
            site_info=site_info,
            gis_result=gis_result,
            financial_result=financial_result
        )
        
        # 5. Risk Engine 실행
        logger.info("📋 Step 5: Risk Assessment")
        risk_assessment = self.risk_engine.assess_comprehensive_risk(
            site_info=site_info,
            gis_result=gis_result,
            financial_result=financial_result,
            lh_scores=lh_scores
        )
        
        # 6. Demand Engine 실행
        logger.info("📋 Step 6: Demand Analysis")
        demand_result = self.demand_engine.analyze_demand(
            address=site_info.address,
            unit_count=unit_count,
            lh_total_score=lh_scores.total_score
        )
        
        # 7. Final Recommendation 생성
        logger.info("📋 Step 7: Final Recommendation")
        final_recommendation = self._generate_final_recommendation(
            lh_scores=lh_scores,
            risk_assessment=risk_assessment,
            financial_result=financial_result,
            gis_result=gis_result
        )
        
        # 8. 처리 시간 계산
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # 9. StandardAnalysisOutput 생성
        output = StandardAnalysisOutput(
            analysis_id=analysis_id,
            version="v9.0",
            timestamp=datetime.now().isoformat(),
            site_info=site_info,
            gis_result=gis_result,
            financial_result=financial_result,
            lh_scores=lh_scores,
            risk_assessment=risk_assessment,
            demand_result=demand_result,
            final_recommendation=final_recommendation,
            processing_time_seconds=round(processing_time, 2)
        )
        
        logger.info("="*80)
        logger.info(f"✅ ZeroSite v9.0 종합 분석 완료")
        logger.info(f"   처리 시간: {processing_time:.2f}초")
        logger.info(f"   최종 결정: {final_recommendation.decision.value}")
        logger.info(f"   신뢰도: {final_recommendation.confidence_level:.1f}%")
        logger.info("="*80)
        
        return output
    
    def _generate_final_recommendation(
        self,
        lh_scores: LHScores,
        risk_assessment: RiskAssessment,
        financial_result: FinancialResult,
        gis_result: GISResult
    ) -> FinalRecommendation:
        """
        최종 의사결정 생성
        
        결정 기준:
        - LH 점수 ≥ 75 + 리스크 LOW/MEDIUM → PROCEED
        - LH 점수 60~75 + 리스크 MEDIUM → PROCEED_WITH_CONDITIONS
        - LH 점수 60~75 + 리스크 HIGH → REVISE
        - LH 점수 < 60 또는 리스크 CRITICAL → NOGO
        
        Args:
            lh_scores: LH 평가 점수
            risk_assessment: 리스크 평가
            financial_result: 재무 분석
            gis_result: GIS 분석
            
        Returns:
            FinalRecommendation
        """
        # 1. 결정 로직
        lh_score = lh_scores.total_score
        risk_level = risk_assessment.overall_risk_level
        
        if lh_score >= 75 and risk_level in ["LOW", "MEDIUM"]:
            decision = DecisionType.PROCEED
            confidence = 85.0
        elif lh_score >= 60 and risk_level == "MEDIUM":
            decision = DecisionType.PROCEED_WITH_CONDITIONS
            confidence = 70.0
        elif lh_score >= 60 and risk_level == "HIGH":
            decision = DecisionType.REVISE
            confidence = 55.0
        else:
            decision = DecisionType.NOGO
            confidence = 30.0
        
        # 2. 강점 추출
        strengths = []
        if lh_scores.location_score >= 25:  # 35점 만점의 71%
            strengths.append(f"입지 우수 ({lh_scores.location_score:.1f}/35점)")
        if lh_scores.business_score >= 30:  # 40점 만점의 75%
            strengths.append(f"사업성 양호 ({lh_scores.business_score:.1f}/40점)")
        if financial_result.irr_10yr >= 8:
            strengths.append(f"높은 IRR ({financial_result.irr_10yr:.1f}%)")
        if gis_result.overall_accessibility_score >= 70:
            strengths.append(f"우수한 접근성 ({gis_result.overall_accessibility_score:.1f}/100)")
        
        # 3. 약점 추출
        weaknesses = []
        if lh_scores.location_score < 20:
            weaknesses.append(f"입지 미흡 ({lh_scores.location_score:.1f}/35점)")
        if lh_scores.business_score < 24:
            weaknesses.append(f"사업성 부족 ({lh_scores.business_score:.1f}/40점)")
        if financial_result.roi_10yr < 40:
            weaknesses.append(f"낮은 ROI ({financial_result.roi_10yr:.1f}%)")
        if risk_assessment.fail_count > 0:
            weaknesses.append(f"리스크 실패 항목 {risk_assessment.fail_count}개")
        
        # 4. 실행 항목
        action_items = []
        if decision == DecisionType.PROCEED:
            action_items.append("LH 신축매입임대 사업 진행")
            action_items.append("설계 착수 및 인허가 준비")
            action_items.append("시공사 선정 및 공사비 협상")
        elif decision == DecisionType.PROCEED_WITH_CONDITIONS:
            action_items.append("리스크 완화 방안 수립")
            action_items.append("사업성 개선 방안 검토")
            action_items.append("조건부 사업 진행")
        elif decision == DecisionType.REVISE:
            action_items.append("설계 변경 또는 규모 조정")
            action_items.append("공사비 절감 방안 마련")
            action_items.append("재평가 후 재검토")
        else:  # NOGO
            action_items.append("사업 포기 권장")
            action_items.append("대체 부지 검토")
            action_items.append("투자 재구조화")
        
        # 5. 임원 요약
        executive_summary = (
            f"LH 평가 {lh_score:.1f}점 (등급: {lh_scores.grade.value}), "
            f"리스크 {risk_level}, "
            f"최종 결정: {decision.value} (신뢰도 {confidence:.0f}%)"
        )
        
        return FinalRecommendation(
            decision=decision,
            confidence_level=confidence,
            key_strengths=strengths,
            key_weaknesses=weaknesses,
            action_items=action_items,
            executive_summary=executive_summary
        )
