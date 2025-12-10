"""
ZeroSite Phase 11: Architecture Design API

RESTful API for automated building design generation.

Author: ZeroSite Development Team + GenSpark AI
Created: 2025-12-10
Version: 11.0
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.architect import (
    DesignGenerator,
    DesignStrategy,
    SupplyType,
)
from app.architect.integration_engine import IntegrationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v11/architect", tags=["Architecture Design v11"])


# Request Models
class DesignRequest(BaseModel):
    """설계 요청"""
    address: str = Field(..., description="대지 주소", example="서울특별시 강남구 역삼동 123-45")
    land_area: float = Field(..., description="대지면적 (㎡)", gt=0, example=1000.0)
    bcr: float = Field(..., description="건폐율 (%)", gt=0, le=100, example=60.0)
    far: float = Field(..., description="용적률 (%)", gt=0, le=1000, example=200.0)
    max_floors: Optional[int] = Field(15, description="최고층수", gt=0, le=50)
    zone_type: Optional[str] = Field(None, description="용도지역", example="제2종일반주거지역")
    supply_type: Optional[str] = Field(
        None, 
        description="LH 공급유형 (Y/N/A/S/M, 미지정시 자동 추천)",
        example="N"
    )


class IntegratedDesignRequest(BaseModel):
    """통합 분석 요청 (Phase 2 + Phase 3 포함)"""
    address: str = Field(..., description="대지 주소", example="서울특별시 강남구 역삼동 123-45")
    land_area: float = Field(..., description="대지면적 (㎡)", gt=0, example=1000.0)
    land_appraisal_price: float = Field(..., description="토지 감정평가액 (원)", gt=0, example=9_000_000_000)
    bcr: float = Field(..., description="건폐율 (%)", gt=0, le=100, example=60.0)
    far: float = Field(..., description="용적률 (%)", gt=0, le=1000, example=200.0)
    max_floors: Optional[int] = Field(15, description="최고층수", gt=0, le=50)
    zone_type: Optional[str] = Field(None, description="용도지역", example="제2종일반주거지역")
    supply_type: Optional[str] = Field(
        None, 
        description="LH 공급유형 (Y/N/A/S/M, 미지정시 자동 추천)",
        example="N"
    )
    housing_type: Optional[str] = Field(
        "Newlyweds_TypeII",
        description="LH 주택 유형 (Phase C 비용 계산용)",
        example="Newlyweds_TypeII"
    )


class DesignResponse(BaseModel):
    """설계 응답"""
    status: str = Field(..., description="상태", example="success")
    address: str
    supply_type: str
    land_area: float
    design_count: int
    designs: list
    recommended: str
    comparison_table: Dict
    generated_at: str


# API Endpoints

@router.post("/design", response_model=DesignResponse)
async def generate_design(request: DesignRequest) -> DesignResponse:
    """
    건축 설계안 자동 생성 (A/B/C 3안)
    
    LH 매입임대 기준으로 3가지 설계 대안을 자동 생성합니다:
    - A안 (안정형): LH 점수 최대화
    - B안 (표준형): 균형 설계
    - C안 (수익형): ROI 최대화
    """
    try:
        logger.info(f"📐 Design request for: {request.address}")
        
        # Parse supply type
        supply_type = None
        if request.supply_type:
            try:
                supply_type = SupplyType(request.supply_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid supply_type: {request.supply_type}. "
                           f"Must be one of: Y, N, A, S, M"
                )
        
        # Create land parameters
        land_params = {
            "area": request.land_area,
            "bcr": request.bcr,
            "far": request.far,
            "max_floors": request.max_floors,
        }
        
        if request.zone_type:
            land_params["zone_type"] = request.zone_type
        
        # Generate designs
        generator = DesignGenerator(
            address=request.address,
            land_params=land_params,
            supply_type=supply_type
        )
        
        comparison = generator.generate_and_compare()
        
        # Format response
        response_data = generator.to_dict(comparison.designs)
        
        return DesignResponse(
            status="success",
            address=response_data["address"],
            supply_type=response_data["supply_type"],
            land_area=response_data["land_area"],
            design_count=response_data["design_count"],
            designs=response_data["designs"],
            recommended=comparison.recommended.value,
            comparison_table=comparison.comparison_table,
            generated_at=response_data["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"❌ Design generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supply-types")
async def get_supply_types() -> Dict[str, Any]:
    """
    LH 공급유형 목록 조회
    """
    return {
        "supply_types": [
            {"code": "Y", "name": "청년형", "description": "대학가, 역세권 청년 1인 가구"},
            {"code": "N", "name": "신혼부부형", "description": "초등학교 인근, 신혼부부 가구"},
            {"code": "A", "name": "일반형", "description": "시세 이하 일반 공급"},
            {"code": "S", "name": "고령자형", "description": "병원, 복지시설 인근"},
            {"code": "M", "name": "혼합형", "description": "지자체 특화형, 혼합 수요"},
        ],
        "unit_sizes": {
            "소형Ⅰ": "22㎡ (18~26㎡)",
            "소형Ⅱ": "30㎡ (26~36㎡)",
            "중형Ⅰ": "42㎡ (36~46㎡)",
            "중형Ⅱ": "50㎡ (46~55㎡)",
            "중형Ⅲ": "58㎡ (55~60㎡)",
        }
    }


@router.get("/strategies")
async def get_strategies() -> Dict[str, Any]:
    """
    설계 전략 목록 조회
    """
    return {
        "strategies": [
            {
                "code": "stable",
                "name": "안정형 (A안)",
                "description": "LH 점수 최대화, 낮은 밀도",
                "multiplier": 0.85,
                "goal": "LH 평가 고득점"
            },
            {
                "code": "standard",
                "name": "표준형 (B안)",
                "description": "균형 설계, 적정 세대수",
                "multiplier": 0.95,
                "goal": "점수와 수익 균형"
            },
            {
                "code": "profit",
                "name": "수익형 (C안)",
                "description": "ROI 최대화, 최대 세대수",
                "multiplier": 1.00,
                "goal": "투자 수익 극대화"
            }
        ]
    }


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    API 헬스 체크
    """
    return {
        "status": "healthy",
        "module": "Architecture Design v11",
        "version": "11.0.0"
    }


@router.post("/integrated-design")
async def generate_integrated_design(request: IntegratedDesignRequest) -> Dict[str, Any]:
    """
    통합 설계 분석 (Architecture + Financial + LH Score)
    
    Phase 11 Architecture Module + Phase 2 Financial Engine + Phase 3 LH Score Engine
    
    Returns:
    - 3가지 설계안 (A/B/C)
    - 각 설계안의 재무 분석 (CAPEX, OPEX, ROI, IRR, Cap Rate)
    - 각 설계안의 LH 평가 점수 (100점 만점, A~F 등급)
    - 종합 투자 판정 및 추천
    """
    try:
        logger.info(f"🔗 Integrated design analysis for: {request.address}")
        
        # Parse supply type
        supply_type = None
        if request.supply_type:
            try:
                supply_type = SupplyType(request.supply_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid supply_type: {request.supply_type}. "
                           f"Must be one of: Y, N, A, S, M"
                )
        
        # Create land parameters
        land_params = {
            "area": request.land_area,
            "bcr": request.bcr,
            "far": request.far,
            "max_floors": request.max_floors,
        }
        
        if request.zone_type:
            land_params["zone_type"] = request.zone_type
        
        # Step 1: Generate designs
        logger.info("📐 Step 1: Generating 3 design alternatives...")
        generator = DesignGenerator(
            address=request.address,
            land_params=land_params,
            supply_type=supply_type
        )
        
        designs = generator.generate()
        
        # Step 2: Integrate with Phase 2 & Phase 3
        logger.info("🔗 Step 2: Running integrated analysis (Phase 2 + 3)...")
        integration_engine = IntegrationEngine()
        
        integrated_results = []
        for design in designs:
            analysis = integration_engine.analyze_design(
                design=design,
                land_area=request.land_area,
                land_appraisal_price=request.land_appraisal_price,
                bcr=request.bcr,
                far=request.far,
                zone_type=request.zone_type or "제2종일반주거지역",
                housing_type=request.housing_type,
                address=request.address
            )
            
            # Format result
            integrated_results.append({
                "strategy": analysis.strategy.value,
                "design_summary": {
                    "total_units": design.metrics.total_units,
                    "total_gfa": design.metrics.total_gfa,
                    "residential_gfa": design.metrics.residential_gfa,
                    "parking_spaces": design.parking.total_required,
                    "max_floors": design.buildable_volume.max_floors,
                    "unit_mix": [
                        {
                            "type_name": unit.name,
                            "area_sqm": unit.size_sqm,
                            "count": unit.count
                        }
                        for unit in design.unit_mix
                    ]
                },
                "financial_analysis": {
                    "capex": analysis.capex,
                    "opex": analysis.opex,
                    "noi": analysis.noi,
                    "roi": analysis.roi,
                    "irr": analysis.irr,
                    "cap_rate": analysis.cap_rate,
                    "project_rating": analysis.project_rating
                },
                "lh_evaluation": {
                    "total_score": analysis.lh_total_score,
                    "grade": analysis.lh_grade,
                    "breakdown": {
                        "location": analysis.lh_score_breakdown.location_total,
                        "feasibility": analysis.lh_score_breakdown.feasibility_total,
                        "policy": analysis.lh_score_breakdown.policy_total,
                        "financial": analysis.lh_score_breakdown.financial_total,
                        "risk": analysis.lh_score_breakdown.risk_total
                    },
                    "strengths": analysis.lh_score_breakdown.strengths,
                    "weaknesses": analysis.lh_score_breakdown.weaknesses,
                    "recommendations": analysis.lh_score_breakdown.recommendations
                },
                "overall_decision": {
                    "decision": analysis.overall_decision,
                    "recommendation": analysis.recommendation,
                    "confidence": analysis.confidence
                }
            })
        
        # Determine best option
        best_balanced = max(integrated_results, key=lambda x: (
            x["lh_evaluation"]["total_score"] * 0.5 + 
            x["financial_analysis"]["roi"] * 0.5
        ))
        
        best_lh = max(integrated_results, key=lambda x: x["lh_evaluation"]["total_score"])
        best_roi = max(integrated_results, key=lambda x: x["financial_analysis"]["roi"])
        
        return {
            "status": "success",
            "address": request.address,
            "land_area": request.land_area,
            "land_appraisal_price": request.land_appraisal_price,
            "designs": integrated_results,
            "recommendations": {
                "best_balanced": {
                    "strategy": best_balanced["strategy"],
                    "lh_score": best_balanced["lh_evaluation"]["total_score"],
                    "roi": best_balanced["financial_analysis"]["roi"]
                },
                "best_lh_score": {
                    "strategy": best_lh["strategy"],
                    "lh_score": best_lh["lh_evaluation"]["total_score"],
                    "roi": best_lh["financial_analysis"]["roi"]
                },
                "best_roi": {
                    "strategy": best_roi["strategy"],
                    "lh_score": best_roi["lh_evaluation"]["total_score"],
                    "roi": best_roi["financial_analysis"]["roi"]
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Integrated design analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Quick test endpoint
@router.post("/quick-test")
async def quick_test() -> Dict[str, Any]:
    """
    빠른 테스트용 엔드포인트
    """
    request = DesignRequest(
        address="서울특별시 강남구 역삼동 123-45",
        land_area=1000.0,
        bcr=60.0,
        far=200.0,
        max_floors=15,
        zone_type="제2종일반주거지역",
        supply_type="N"
    )
    
    result = await generate_design(request)
    
    return {
        "test": "success",
        "result": result.dict()
    }
