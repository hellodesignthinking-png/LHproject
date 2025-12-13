"""
ZeroSite v24.1 - Complete API Router
Connects Dashboard → Engines → Reports → PDF

Author: ZeroSite Development Team
Version: 24.1.0
Created: 2025-12-12
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import tempfile
import os

# Import v24.1 engines
from app.engines.capacity_engine_v241 import CapacityEngineV241
from app.engines.market_engine_v241 import MarketEngineV241
from app.engines.financial_engine_v241 import FinancialEngineV241
from app.engines.risk_engine_v241 import RiskEngineV241
from app.engines.scenario_engine_v241 import ScenarioEngineV241
from app.engines.multi_parcel_optimizer_v241 import MultiParcelOptimizerV241
from app.engines.narrative_engine_v241 import NarrativeEngineV241
from app.engines.alias_engine_v241 import AliasEngineV241
from app.engines.appraisal_engine_v241 import AppraisalEngineV241

# Import report generator
from app.services.report_generator_v241_enhanced import ReportGeneratorV241Enhanced
from app.services.professional_appraisal_pdf_generator import ProfessionalAppraisalPDFGenerator
from app.services.final_appraisal_pdf_generator import FinalAppraisalPDFGenerator
from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
from app.services.land_diagnosis_pdf_generator import LandDiagnosisPDFGenerator
from app.services.pdf_storage_service import PDFStorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v24.1", tags=["ZeroSite v24.1"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LandDiagnosisRequest(BaseModel):
    """Request model for land diagnosis"""
    address: str = Field(..., description="Land address", example="서울시 마포구 공덕동 123-4")
    land_area: float = Field(..., gt=0, description="Land area in ㎡", example=1500.0)
    appraisal_price: float = Field(..., gt=0, description="Appraisal price KRW/㎡", example=5000000)
    zone_type: str = Field(..., description="Zoning type", example="제3종일반주거지역")
    legal_far: float = Field(..., gt=0, description="Legal FAR %", example=200.0)
    legal_bcr: float = Field(..., gt=0, description="Legal BCR %", example=60.0)
    final_far: Optional[float] = Field(None, description="Final FAR after relaxation %", example=240.0)
    height_limit: Optional[float] = Field(None, description="Height limit in meters", example=60.0)


class CapacityRequest(BaseModel):
    """Request model for capacity analysis"""
    land_area: float = Field(..., gt=0, example=1500.0)
    bcr_limit: float = Field(..., gt=0, example=60.0)
    far_limit: float = Field(..., gt=0, example=240.0)
    max_floors: int = Field(..., ge=1, example=15)


class ScenarioComparisonRequest(BaseModel):
    """Request model for scenario comparison"""
    scenario_a: Dict[str, Any] = Field(..., description="Scenario A data")
    scenario_b: Dict[str, Any] = Field(..., description="Scenario B data")
    scenario_c: Dict[str, Any] = Field(..., description="Scenario C data")


class ComparableSale(BaseModel):
    """Comparable sale data"""
    price_per_sqm: float = Field(..., description="Transaction price per sqm", example=10000000)
    time_adjustment: float = Field(default=1.0, description="Time adjustment factor", example=1.05)
    location_adjustment: float = Field(default=1.0, description="Location adjustment factor", example=0.95)
    individual_adjustment: float = Field(default=1.0, description="Individual adjustment factor", example=1.0)
    weight: float = Field(default=0.33, description="Weight in weighted average", example=0.33)


class PremiumFactors(BaseModel):
    """Premium factors for land appraisal"""
    # Physical Characteristics
    land_shape: float = Field(default=0, description="Land shape premium %", example=15)
    land_slope: float = Field(default=0, description="Land slope premium %", example=15)
    direction: float = Field(default=0, description="Direction premium %", example=12)
    road_facing: float = Field(default=0, description="Road facing premium %", example=25)
    
    # Location/Amenities
    subway_distance: float = Field(default=0, description="Subway distance premium %", example=30)
    school_district_8: float = Field(default=0, description="8th school district premium %", example=25)
    large_park: float = Field(default=0, description="Large park premium %", example=15)
    department_store: float = Field(default=0, description="Department store premium %", example=20)
    large_hospital: float = Field(default=0, description="Large hospital premium %", example=12)
    han_river_view: float = Field(default=0, description="Han River view premium %", example=25)
    
    # Development/Regulation
    redevelopment_status: float = Field(default=0, description="Redevelopment status premium %", example=60)
    gtx_station: float = Field(default=0, description="GTX station premium %", example=50)
    greenbelt: float = Field(default=0, description="Greenbelt premium %", example=-40)
    cultural_heritage_zone: float = Field(default=0, description="Cultural heritage zone premium %", example=-30)


class AppraisalRequest(BaseModel):
    """Request model for appraisal - All fields except address have safe defaults"""
    address: str = Field(..., description="Property address", example="서울시 마포구 공덕동 123-4")
    land_area_sqm: Optional[float] = Field(660.0, gt=0, description="Land area in ㎡ (default 660㎡)", example=660.0)
    zone_type: Optional[str] = Field("제2종일반주거지역", description="Zoning type (auto-detected if not provided)", example="제3종일반주거지역")
    individual_land_price_per_sqm: Optional[float] = Field(None, gt=0, description="Individual land price KRW/㎡ (auto-detected if not provided)", example=7000000)
    premium_factors: Optional[PremiumFactors] = Field(None, description="Premium adjustment factors (auto-detected based on address)")
    comparable_sales: Optional[List[ComparableSale]] = Field(None, description="List of comparable sales (auto-fetched from MOLIT if not provided)")


class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    analysis_id: str = Field(..., description="Analysis ID")
    report_type: int = Field(..., ge=1, le=5, description="Report type (1-5)")
    format: str = Field(default="pdf", description="Output format")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/")
async def root():
    """API information endpoint"""
    return {
        "name": "ZeroSite v24.1 API",
        "version": "24.1.0",
        "status": "online",
        "endpoints": {
            "diagnose": "/api/v24.1/diagnose-land",
            "capacity": "/api/v24.1/capacity",
            "appraisal": "/api/v24.1/appraisal",
            "scenario": "/api/v24.1/scenario/compare",
            "risk": "/api/v24.1/risk/assess",
            "report": "/api/v24.1/report/generate",
            "pdf": "/api/v24.1/report/pdf/{analysis_id}"
        },
        "engines": {
            "capacity": "v24.1.0",
            "market": "v24.1.0",
            "financial": "v24.1.0",
            "risk": "v24.1.0",
            "scenario": "v24.1.0",
            "multi_parcel": "v24.1.0",
            "narrative": "v24.1.0",
            "alias": "v24.1.0",
            "appraisal": "v24.1.0"
        }
    }


@router.post("/diagnose-land")
async def diagnose_land(request: LandDiagnosisRequest):
    """
    **Dashboard Button 1: 토지 진단**
    
    Comprehensive land diagnosis using all v24.1 engines
    WITH AUTO-RECOVERY FALLBACK ENGINE
    """
    try:
        logger.info(f"Starting land diagnosis for {request.address}")
        
        # 🔄 STEP 1: Fallback Engine - 입력 데이터 검증 및 복구
        from app.services.land_diagnosis_fallback_engine import get_fallback_engine
        fallback_engine = get_fallback_engine()
        
        # 원본 입력 데이터
        raw_input = {
            'address': request.address,
            'land_area_sqm': request.land_area,
            'zone_type': request.zone_type,
            'bcr': request.legal_bcr,
            'far': request.legal_far,
            'individual_land_price_per_sqm': request.appraisal_price / request.land_area if request.appraisal_price and request.land_area > 0 else 0,
            'lh_unit_cost_per_sqm': 0,  # Will be auto-filled if needed
        }
        
        # 자동 복구 적용
        fixed_input = fallback_engine.validate_and_fix_input(raw_input)
        logger.info(f"✅ Fallback applied: {fallback_engine.fallback_log}")
        
        # Initialize report generator (which initializes all engines)
        report_gen = ReportGeneratorV241Enhanced()
        
        # Prepare input data (복구된 데이터 사용)
        input_data = {
            'address': fixed_input['address'],
            'area_sqm': fixed_input['land_area_sqm'],
            'land_area': fixed_input['land_area_sqm'],
            'appraisal_price': fixed_input['individual_land_price_per_sqm'] * fixed_input['land_area_sqm'],
            'legal_far': fixed_input['far'],
            'legal_bcr': fixed_input['bcr'],
            'final_far': request.final_far or fixed_input['far'],
            'height_limit': request.height_limit,
            'zone_type': fixed_input['zone_type']
        }
        
        # Gather all engine data
        context = report_gen.gather_all_engine_data(input_data)
        
        # Generate analysis ID
        analysis_id = f"DIAG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 🔄 STEP 2: Fallback Summary 생성
        fallback_summary = fallback_engine.generate_fallback_summary()
        
        # Return comprehensive diagnosis WITH FALLBACK INFO
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "address": fixed_input['address'],
                "land_area": fixed_input['land_area_sqm'],
                "max_units": context.capacity_data.get('max_units', 0),
                "floors": context.capacity_data.get('floors', 0),
                "roi": context.financial_data.get('roi', 0),
                "risk_level": context.risk_data.get('risk_level', 'MEDIUM'),
                "recommendation": "적합" if context.financial_data.get('roi', 0) > 0.10 else "검토 필요"
            },
            "details": {
                "capacity": context.capacity_data,
                "financial": context.financial_data,
                "risk": context.risk_data,
                "market": context.market_data
            },
            "narratives": context.narratives,
            "fallback_info": fallback_summary  # ✅ 추가: Fallback 정보
        }
        
    except Exception as e:
        logger.error(f"Error in land diagnosis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diagnosis failed: {str(e)}")


@router.post("/capacity")
async def calculate_capacity(request: CapacityRequest):
    """
    **Dashboard Button 2: 건축 규모 산정**
    
    Quick capacity calculation with mass simulation
    """
    try:
        engine = CapacityEngineV241()
        
        mass_configs = engine.generate_mass_simulation(
            land_area=request.land_area,
            bcr_limit=request.bcr_limit,
            far_limit=request.far_limit,
            max_floors=request.max_floors
        )
        
        # Calculate units from best configuration
        total_area = request.land_area * (request.far_limit / 100)
        estimated_units = int(total_area / 80)  # 80㎡ per unit
        
        return {
            "status": "success",
            "capacity": {
                "land_area": request.land_area,
                "max_units": estimated_units,
                "floors": mass_configs[0].floors if mass_configs else request.max_floors,
                "total_floor_area": total_area,
                "parking_spaces": int(estimated_units * 1.2),
                "mass_configurations": len(mass_configs)
            },
            "configurations": [
                {
                    "type": config.shape_type,
                    "floors": config.floors,
                    "footprint": config.footprint,
                    "efficiency_score": config.efficiency_score,
                    "description": config.description
                }
                for config in mass_configs[:3]  # Top 3
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in capacity calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Capacity calculation failed: {str(e)}")


@router.post("/appraisal")
async def calculate_appraisal(request: AppraisalRequest):
    """
    **Dashboard Button 3: 감정평가**
    
    Standard Korean real estate appraisal using 3 approaches:
    1. Cost Approach (원가법)
    2. Sales Comparison (거래사례비교법)
    3. Income Approach (수익환원법)
    """
    try:
        logger.info(f"Starting appraisal for {request.address}")
        
        engine = AppraisalEngineV241()
        
        # ========================================
        # 1. Auto-load Individual Land Price (개별공시지가)
        # ========================================
        individual_land_price = request.individual_land_price_per_sqm
        
        if not individual_land_price:
            try:
                from app.services.individual_land_price_api import IndividualLandPriceAPI
                price_api = IndividualLandPriceAPI()
                individual_land_price = price_api.get_individual_land_price(request.address)
                logger.info(f"🏘️ Auto-loaded individual land price: {individual_land_price:,} 원/㎡")
            except Exception as e:
                logger.warning(f"Failed to auto-load land price: {e}")
                # Fallback to default based on zone
                individual_land_price = 5_000_000  # Default 500만원/㎡
                logger.info(f"⚠️ Using default land price: {individual_land_price:,} 원/㎡")
        else:
            logger.info(f"✏️ User-provided land price: {individual_land_price:,} 원/㎡")
        
        # ========================================
        # 2. Prepare comparable sales data
        # ========================================
        comparable_sales_data = []
        if request.comparable_sales:
            for comp in request.comparable_sales:
                comparable_sales_data.append({
                    'price_per_sqm': comp.price_per_sqm,
                    'time_adjustment': comp.time_adjustment,
                    'location_adjustment': comp.location_adjustment,
                    'individual_adjustment': comp.individual_adjustment,
                    'weight': comp.weight
                })
            logger.info(f"✏️ User-provided {len(comparable_sales_data)} comparable sales")
        else:
            logger.info(f"📡 Comparable sales will be auto-fetched by engine")
        
        # ========================================
        # 3. Auto-detect premium factors
        # ========================================
        premium_factors_data = {}
        
        # First, try auto-detection based on address
        try:
            from app.services.premium_auto_detector import PremiumAutoDetector
            auto_detector = PremiumAutoDetector()
            auto_detected = auto_detector.auto_detect_premium_factors(request.address)
            if auto_detected:
                premium_factors_data.update(auto_detected)
                logger.info(f"🤖 Auto-detected {len(auto_detected)} premium factors")
        except Exception as e:
            logger.warning(f"Premium auto-detection failed: {e}")
        
        # Then merge with user-provided values (user values override auto-detected)
        if request.premium_factors:
            user_factors = request.premium_factors.model_dump()
            premium_factors_data.update(user_factors)
            logger.info(f"✏️ Merged with user-provided premium factors")
        
        # ========================================
        # 4. Prepare input data with SAFE FALLBACKS
        # ========================================
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm or 660.0,  # Fallback to 660㎡
            'zone_type': request.zone_type or "제2종일반주거지역",  # Fallback to common zone
            'individual_land_price_per_sqm': individual_land_price,  # Use auto-loaded or user-provided
            'premium_factors': premium_factors_data,
            'comparable_sales': comparable_sales_data
        }
        
        logger.info(f"📋 Final input data: land={input_data['land_area_sqm']}㎡, zone={input_data['zone_type']}, price={input_data['individual_land_price_per_sqm']:,}원/㎡")
        
        result = engine.process(input_data)
        
        # Extract premium information if available
        premium_info = result.get('premium_info', {})
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "appraisal": {
                "final_value": result['final_appraisal_value'],
                "value_per_sqm": result['final_value_per_sqm'],
                "confidence": result['confidence_level'],
                "approaches": {
                    "cost": result['cost_approach'],
                    "sales_comparison": result['sales_comparison'],
                    "income": result['income_approach']
                },
                "weights": result['weights'],
                "location_factor": result['location_factor'],
                "premium_percentage": premium_info.get('premium_percentage', 0),
                "premium_details": premium_info.get('top_5_factors', [])
            },
            "breakdown": result['breakdown'],
            "metadata": result['metadata'],
            "notes": result['notes'],
            "premium_info": premium_info  # Include full premium info
        }
        
    except Exception as e:
        logger.error(f"Error in appraisal calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Appraisal failed: {str(e)}")


@router.post("/scenario/compare")
async def compare_scenarios(request: ScenarioComparisonRequest):
    """
    **Dashboard Button 4: 시나리오 비교**
    
    Compare 3 development scenarios (A/B/C)
    """
    try:
        engine = ScenarioEngineV241()
        
        comparison = engine.compare_abc_scenarios(
            scenario_a_data=request.scenario_a,
            scenario_b_data=request.scenario_b,
            scenario_c_data=request.scenario_c
        )
        
        return {
            "status": "success",
            "best_scenario": comparison.best_scenario,
            "recommendation": comparison.recommendation,
            "comparison_matrix": comparison.comparison_matrix,
            "rankings": comparison.rankings
        }
        
    except Exception as e:
        logger.error(f"Error in scenario comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scenario comparison failed: {str(e)}")


@router.post("/risk/assess")
async def assess_risk(
    land_area: float,
    floors: int,
    unit_count: int,
    floor_area_ratio: float,
    building_coverage_ratio: float
):
    """
    **Dashboard Button 4: 리스크 평가**
    
    Assess design and legal risks
    """
    try:
        engine = RiskEngineV241()
        
        risk_assessment = engine.assess_design_risks(
            land_area=land_area,
            floors=floors,
            unit_count=unit_count,
            floor_area_ratio=floor_area_ratio,
            building_coverage_ratio=building_coverage_ratio
        )
        
        return {
            "status": "success",
            "risk_level": risk_assessment.risk_level,
            "overall_risk_score": risk_assessment.overall_risk_score,
            "key_risks": risk_assessment.key_risks[:5],
            "mitigation_strategies": risk_assessment.mitigation_strategies[:5],
            "risk_breakdown": {
                "floor_plan_risk": risk_assessment.floor_plan_risk,
                "structural_risk": risk_assessment.structural_risk,
                "code_compliance_risk": risk_assessment.code_compliance_risk,
                "construction_risk": risk_assessment.construction_risk
            }
        }
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.post("/report/generate")
async def generate_report(request: ReportGenerationRequest, background_tasks: BackgroundTasks):
    """
    **Dashboard Button 5: 보고서 생성**
    
    Generate comprehensive report (Report 1-5)
    """
    try:
        logger.info(f"Generating report type {request.report_type} for {request.analysis_id}")
        
        # Placeholder for actual report generation
        # In production, this would fetch stored analysis data and generate PDF
        
        return {
            "status": "generating",
            "report_id": f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "analysis_id": request.analysis_id,
            "report_type": request.report_type,
            "format": request.format,
            "estimated_completion_seconds": 30,
            "download_url": f"/api/v24.1/report/pdf/{request.analysis_id}"
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/report/pdf/{analysis_id}")
async def download_pdf_report(analysis_id: str):
    """
    **PDF Download Endpoint**
    
    Download generated PDF report
    """
    try:
        # Placeholder for actual PDF download
        # In production, this would retrieve the generated PDF from storage
        
        return {
            "status": "ready",
            "analysis_id": analysis_id,
            "file_name": f"ZeroSite_Report_{analysis_id}.pdf",
            "file_size_kb": 2560,
            "download_url": f"https://storage.zerosite.com/reports/{analysis_id}.pdf",
            "expires_in_hours": 24
        }
        
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=404, detail=f"PDF not found: {str(e)}")


@router.post("/appraisal/pdf")
async def generate_appraisal_pdf(request: AppraisalRequest):
    """
    **감정평가 PDF 생성 및 다운로드**
    
    Execute appraisal and immediately generate PDF report with detailed calculations
    
    Returns FileResponse with PDF file for download
    """
    try:
        logger.info(f"Starting appraisal PDF generation for {request.address}")
        
        # Step 1: Execute appraisal calculation
        engine = AppraisalEngineV241()
        
        # ========================================
        # 1. Auto-load Individual Land Price (개별공시지가)
        # ========================================
        individual_land_price = request.individual_land_price_per_sqm
        
        if not individual_land_price:
            try:
                from app.services.individual_land_price_api import IndividualLandPriceAPI
                price_api = IndividualLandPriceAPI()
                individual_land_price = price_api.get_individual_land_price(request.address)
                logger.info(f"🏘️ Auto-loaded individual land price for PDF: {individual_land_price:,} 원/㎡")
            except Exception as e:
                logger.warning(f"Failed to auto-load land price: {e}")
                individual_land_price = 5_000_000  # Default
                logger.info(f"⚠️ Using default land price for PDF: {individual_land_price:,} 원/㎡")
        else:
            logger.info(f"✏️ User-provided land price for PDF: {individual_land_price:,} 원/㎡")
        
        # ========================================
        # 2. Prepare comparable sales data
        # ========================================
        comparable_sales_data = []
        if request.comparable_sales:
            for comp in request.comparable_sales:
                comparable_sales_data.append({
                    'price_per_sqm': comp.price_per_sqm,
                    'time_adjustment': comp.time_adjustment,
                    'location_adjustment': comp.location_adjustment,
                    'individual_adjustment': comp.individual_adjustment,
                    'weight': comp.weight
                })
            logger.info(f"✏️ User-provided {len(comparable_sales_data)} comparable sales for PDF")
        else:
            logger.info(f"📡 Comparable sales will be auto-fetched by engine for PDF")
        
        # ========================================
        # 3. Auto-detect premium factors
        # ========================================
        premium_factors_data = {}
        
        # First, try auto-detection based on address
        try:
            from app.services.premium_auto_detector import PremiumAutoDetector
            auto_detector = PremiumAutoDetector()
            auto_detected = auto_detector.auto_detect_premium_factors(request.address)
            if auto_detected:
                premium_factors_data.update(auto_detected)
                logger.info(f"🤖 Auto-detected {len(auto_detected)} premium factors for PDF")
        except Exception as e:
            logger.warning(f"Premium auto-detection failed: {e}")
        
        # Then merge with user-provided values (user values override auto-detected)
        if request.premium_factors:
            user_factors = request.premium_factors.model_dump()
            premium_factors_data.update(user_factors)
            logger.info(f"✏️ Merged with user-provided premium factors for PDF")
        
        # ========================================
        # 4. Prepare input data
        # ========================================
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm,
            'zone_type': request.zone_type,
            'individual_land_price_per_sqm': individual_land_price,  # Use auto-loaded or user-provided
            'premium_factors': premium_factors_data,
            'comparable_sales': comparable_sales_data
        }
        
        appraisal_result = engine.process(input_data)
        
        # 🔥 Issue #4 Fix: Add address and land_area to result for PDF template
        # Map engine keys to PDF template keys
        appraisal_result['address'] = request.address
        appraisal_result['land_area_sqm'] = request.land_area_sqm
        appraisal_result['zone_type'] = request.zone_type
        appraisal_result['individual_land_price_per_sqm'] = individual_land_price  # Use auto-loaded or user-provided
        appraisal_result['premium_factors'] = premium_factors_data
        
        # 🔥 Issue #4 Fix: Map engine keys to PDF template expected keys
        appraisal_result['cost_approach_value'] = appraisal_result.get('cost_approach', 0)
        appraisal_result['sales_comparison_value'] = appraisal_result.get('sales_comparison', 0)
        appraisal_result['income_approach_value'] = appraisal_result.get('income_approach', 0)
        appraisal_result['weight_cost'] = appraisal_result.get('weights', {}).get('cost', 0.4)
        appraisal_result['weight_sales'] = appraisal_result.get('weights', {}).get('sales', 0.4)
        appraisal_result['weight_income'] = appraisal_result.get('weights', {}).get('income', 0.2)
        
        # Step 2: Generate PDF using Ultimate Generator (실거래가 100% 정확도)
        pdf_generator = UltimateAppraisalPDFGenerator()
        html_content = pdf_generator.generate_pdf_html(appraisal_result)
        pdf_bytes = pdf_generator.generate_pdf_bytes(html_content)
        
        # Step 3: Save to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        # 🔥 Issue #5 Fix: Generate filename with lot number (지번)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Extract lot number from address (e.g., "서울시 강남구 역삼동 123-4" -> "역삼동123-4")
        import re
        def extract_jibun(address: str) -> str:
            """Extract 지번 (lot number) from address"""
            # Pattern 1: 동 + 번지 (e.g., "역삼동 123-4")
            match = re.search(r'([가-힣]+동)\s*(\d+[-]?\d*)', address)
            if match:
                dong_name = match.group(1)
                jibun = match.group(2)
                return f"{dong_name}{jibun}"
            
            # Pattern 2: 구 + 번지 (e.g., "강남구 123-4")
            match = re.search(r'([가-힣]+구)\s*(\d+[-]?\d*)', address)
            if match:
                gu_name = match.group(1)
                jibun = match.group(2)
                return f"{gu_name}{jibun}"
            
            # Pattern 3: 도로명 + 번호 (e.g., "테헤란로 123")
            match = re.search(r'([가-힣]+로)\s*(\d+)', address)
            if match:
                road_name = match.group(1)
                number = match.group(2)
                return f"{road_name}{number}"
            
            # Fallback: Use first word
            words = address.split()
            return words[-1] if words else "Unknown"
        
        jibun = extract_jibun(request.address)
        filename_ascii = f"Appraisal_Report_{jibun}_{timestamp}.pdf"
        
        # URL encode Korean filename for proper browser display
        from urllib.parse import quote
        filename_korean = f"{jibun}_감정평가보고서.pdf"
        encoded_filename = quote(filename_korean.encode('utf-8'))
        
        logger.info(f"PDF generated successfully: {filename_ascii}")
        
        # Step 5: Return FileResponse with PDF
        # Use ASCII filename in parameter, UTF-8 filename in header
        return FileResponse(
            path=tmp_file_path,
            media_type="application/pdf",
            filename=filename_ascii,
            headers={
                "Content-Disposition": f"attachment; filename={filename_ascii}; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating appraisal PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/diagnose-land/pdf")
async def generate_land_diagnosis_pdf(request: LandDiagnosisRequest):
    """
    **토지 진단 PDF 생성 및 다운로드**
    
    Execute land diagnosis and generate comprehensive PDF report
    
    Returns FileResponse with PDF file for download
    """
    try:
        logger.info(f"Starting land diagnosis PDF generation for {request.address}")
        
        # Step 1: Execute land diagnosis
        report_gen = ReportGeneratorV241Enhanced()
        
        input_data = {
            'address': request.address,
            'area_sqm': request.land_area,
            'land_area': request.land_area,
            'appraisal_price': request.appraisal_price,
            'legal_far': request.legal_far,
            'legal_bcr': request.legal_bcr,
            'final_far': request.final_far or request.legal_far,
            'height_limit': request.height_limit,
            'zone_type': request.zone_type
        }
        
        context = report_gen.gather_all_engine_data(input_data)
        
        # Generate analysis ID
        analysis_id = f"DIAG_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Prepare diagnosis data
        diagnosis_data = {
            "analysis_id": analysis_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "address": request.address,
                "land_area": request.land_area,
                "max_units": context.capacity_data.get('max_units', 0),
                "floors": context.capacity_data.get('floors', 0),
                "roi": context.financial_data.get('roi', 0),
                "risk_level": context.risk_data.get('risk_level', 'MEDIUM'),
                "recommendation": "적합" if context.financial_data.get('roi', 0) > 0.10 else "검토 필요"
            },
            "details": {
                "capacity": context.capacity_data,
                "financial": context.financial_data,
                "risk": context.risk_data,
                "market": context.market_data
            }
        }
        
        # Step 2: Generate PDF
        pdf_generator = LandDiagnosisPDFGenerator()
        pdf_bytes = pdf_generator.generate_pdf_bytes(diagnosis_data)
        
        # Step 3: Save to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        # Step 4: Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_ascii = f"Land_Diagnosis_Report_{timestamp}.pdf"
        
        from urllib.parse import quote
        filename_korean = f"토지진단보고서_{timestamp}.pdf"
        encoded_filename = quote(filename_korean.encode('utf-8'))
        
        logger.info(f"Land diagnosis PDF generated successfully: {filename_ascii}")
        
        # Step 5: Return FileResponse
        return FileResponse(
            path=tmp_file_path,
            media_type="application/pdf",
            filename=filename_ascii,
            headers={
                "Content-Disposition": f"attachment; filename={filename_ascii}; filename*=UTF-8''{encoded_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating land diagnosis PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.post("/appraisal/pdf/store")
async def generate_and_store_appraisal_pdf(request: AppraisalRequest):
    """
    **감정평가 PDF 생성 및 클라우드 저장**
    
    Generate appraisal PDF and store it in cloud storage
    Returns JSON with download URL instead of direct file download
    
    Useful for:
    - Email sending
    - Sharing links
    - Delayed downloads
    """
    try:
        logger.info(f"Starting appraisal PDF generation and storage for {request.address}")
        
        # Step 1: Execute appraisal calculation
        engine = AppraisalEngineV241()
        
        # Prepare comparable sales data
        comparable_sales_data = []
        if request.comparable_sales:
            for comp in request.comparable_sales:
                comparable_sales_data.append({
                    'price_per_sqm': comp.price_per_sqm,
                    'time_adjustment': comp.time_adjustment,
                    'location_adjustment': comp.location_adjustment,
                    'individual_adjustment': comp.individual_adjustment,
                    'weight': comp.weight
                })
        
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm,
            'building_area_sqm': request.building_area_sqm or 0,
            'construction_year': request.construction_year or datetime.now().year,
            'zone_type': request.zone_type,
            'individual_land_price_per_sqm': request.individual_land_price_per_sqm or 0,
            'annual_rental_income': request.annual_rental_income or 0,
            'comparable_sales': comparable_sales_data
        }
        
        appraisal_result = engine.process(input_data)
        appraisal_result['address'] = request.address
        appraisal_result['land_area_sqm'] = request.land_area_sqm
        appraisal_result['zone_type'] = request.zone_type
        appraisal_result['individual_land_price_per_sqm'] = request.individual_land_price_per_sqm or 7000000
        
        # Step 2: Generate PDF using Ultimate Generator (실거래가 100% 정확도)
        pdf_generator = UltimateAppraisalPDFGenerator()
        html_content = pdf_generator.generate_pdf_html(appraisal_result)
        pdf_bytes = pdf_generator.generate_pdf_bytes(html_content)
        
        # Step 3: Store PDF in cloud storage
        storage_service = PDFStorageService(storage_type="local")  # Can be "azure" or "s3" with proper config
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"감정평가보고서_{request.address}_{timestamp}.pdf"
        
        metadata = {
            "report_type": "appraisal",
            "address": request.address,
            "land_area_sqm": str(request.land_area_sqm),
            "generated_at": datetime.now().isoformat(),
            "final_value": str(appraisal_result['final_appraisal_value'])
        }
        
        storage_info = storage_service.save_pdf(pdf_bytes, filename, metadata)
        
        logger.info(f"Appraisal PDF stored successfully: {storage_info['file_id']}")
        
        # Step 4: Return storage info with download URL
        return {
            "status": "success",
            "message": "PDF generated and stored successfully",
            "file_id": storage_info['file_id'],
            "download_url": storage_info['download_url'],
            "expires_at": storage_info['expires_at'],
            "file_size_kb": storage_info['file_size_bytes'] // 1024,
            "storage_type": storage_info['storage_type'],
            "appraisal_summary": {
                "final_value": appraisal_result['final_appraisal_value'],
                "confidence": appraisal_result['confidence_level'],
                "address": request.address
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating and storing appraisal PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF generation/storage failed: {str(e)}")


@router.get("/pdf/download/{file_id}")
async def download_stored_pdf(file_id: str):
    """
    **저장된 PDF 다운로드**
    
    Download a previously stored PDF by file ID
    """
    try:
        storage_service = PDFStorageService(storage_type="local")
        pdf_bytes = storage_service.get_pdf(file_id)
        
        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Return as streaming response
        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=ZeroSite_Report_{file_id}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "24.1.0",
        "engines_loaded": 8,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# GENSPARK V4.0 - NEW AUTO-FETCH & DETAILED PDF ENDPOINTS
# ============================================================================

class LandMetaRequest(BaseModel):
    """Request model for land metadata auto-fetch"""
    address: str = Field(..., description="Property address", example="서울시 강남구 역삼동 123-4")


@router.post("/land-price/official")
async def get_official_land_price(req: LandMetaRequest):
    """
    **개별공시지가 자동 조회 API**
    
    주소를 입력하면 개별공시지가를 자동으로 조회합니다.
    
    Returns:
        - official_price_per_sqm: 개별공시지가 (원/㎡)
        - year: 기준연도
        - source: 데이터 출처
        - fallback_used: Fallback 사용 여부
    """
    try:
        logger.info(f"🏘️ Fetching official land price for: {req.address}")
        
        # Try to use existing IndividualLandPriceAPI
        try:
            from app.services.individual_land_price_api import IndividualLandPriceAPI
            price_api = IndividualLandPriceAPI()
            price = price_api.get_individual_land_price(req.address)
            
            if price and price > 0:
                return {
                    "success": True,
                    "official_price_per_sqm": int(price),
                    "year": 2024,
                    "source": "국토교통부_개별공시지가API",
                    "fallback_used": False,
                    "address": req.address
                }
        except Exception as e:
            logger.warning(f"IndividualLandPriceAPI failed: {e}")
        
        # Fallback: Use district-based averages
        district_prices = {
            "강남구": 15000000,
            "서초구": 14000000,
            "송파구": 12000000,
            "마포구": 11000000,
            "용산구": 13000000,
            "성동구": 10000000,
            "default": 8000000
        }
        
        price = district_prices.get("default", 8000000)
        for district, avg_price in district_prices.items():
            if district in req.address:
                price = avg_price
                break
        
        return {
            "success": True,
            "official_price_per_sqm": price,
            "year": 2024,
            "source": "구별_평균값_Fallback",
            "fallback_used": True,
            "address": req.address
        }
        
    except Exception as e:
        logger.error(f"❌ Official land price fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Land price fetch failed: {str(e)}")


@router.post("/zoning-info")
async def get_zoning_info(req: LandMetaRequest):
    """
    **용도지역 자동 조회 API**
    
    주소를 입력하면 용도지역 및 건축 규제 정보를 자동으로 조회합니다.
    
    Returns:
        - zone_type: 용도지역
        - bcr_legal: 법정 건폐율 (%)
        - far_legal: 법정 용적률 (%)
        - district_overlays: 중복 용도지역/지구
        - regulation_summary: 규제 요약
    """
    try:
        logger.info(f"🗺️ Fetching zoning info for: {req.address}")
        
        # TODO: Integrate with actual zoning API (국토부 토지이용규제정보 서비스)
        # For now, use address-based heuristics
        
        # Default zoning based on district
        zone_defaults = {
            "강남구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250},
            "서초구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250},
            "마포구": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200},
            "용산구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250},
            "default": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200}
        }
        
        zone_info = zone_defaults["default"]
        for district, info in zone_defaults.items():
            if district in req.address:
                zone_info = info
                break
        
        # Check for commercial keywords
        if any(kw in req.address for kw in ["역삼", "테헤란", "강남대로", "선릉"]):
            zone_info = {"zone": "준주거지역", "bcr": 70, "far": 400}
        
        return {
            "success": True,
            "zone_type": zone_info["zone"],
            "bcr_legal": zone_info["bcr"],
            "far_legal": zone_info["far"],
            "district_overlays": ["지구단위계획구역"] if "강남" in req.address else [],
            "regulation_summary": f"{zone_info['zone']} - 중층/고층 주거 개발 가능",
            "source": "주소기반_추정",
            "address": req.address
        }
        
    except Exception as e:
        logger.error(f"❌ Zoning info fetch failed: {e}")
        raise HTTPException(status_code=500, detail=f"Zoning info fetch failed: {str(e)}")


class SimpleAppraisalRequest(BaseModel):
    """Simplified request model - address only!"""
    address: str = Field(..., description="Property address", example="서울시 강남구 역삼동 123-4")
    land_area_sqm: Optional[float] = Field(None, gt=0, description="Land area (optional, will estimate if not provided)", example=660.0)


@router.post("/appraisal/auto")
async def generate_auto_appraisal_pdf(request: SimpleAppraisalRequest):
    """
    **🚀 완전 자동화 감정평가 보고서 PDF**
    
    주소만 입력하면 모든 것이 자동으로 분석됩니다:
    - ✅ 개별공시지가 자동 조회
    - ✅ 용도지역 자동 조회
    - ✅ 입지/인프라 자동 분석
    - ✅ 개발/규제 자동 분석
    - ✅ 프리미엄 자동 계산
    - ✅ 상세 PDF 자동 생성
    
    Returns: PDF 다운로드 정보
    """
    try:
        logger.info(f"🚀 AUTO APPRAISAL for: {request.address}")
        
        # ========================================
        # STEP 1: Auto-fetch land price
        # ========================================
        logger.info("📍 Step 1: Fetching official land price...")
        try:
            from app.services.individual_land_price_api import IndividualLandPriceAPI
            price_api = IndividualLandPriceAPI()
            individual_land_price = price_api.get_individual_land_price(request.address)
            logger.info(f"✅ Land price: {individual_land_price:,} 원/㎡")
        except Exception as e:
            logger.warning(f"Land price API failed, using fallback: {e}")
            # Fallback by district
            district_prices = {
                "강남구": 15000000, "서초구": 14000000, "송파구": 12000000,
                "마포구": 11000000, "용산구": 13000000, "default": 8000000
            }
            individual_land_price = district_prices.get("default", 8000000)
            for district, price in district_prices.items():
                if district in request.address:
                    individual_land_price = price
                    break
            logger.info(f"✅ Fallback land price: {individual_land_price:,} 원/㎡")
        
        # ========================================
        # STEP 2: Auto-fetch zoning info
        # ========================================
        logger.info("🗺️ Step 2: Fetching zoning information...")
        zone_defaults = {
            "강남구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250},
            "서초구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250},
            "마포구": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200},
            "default": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200}
        }
        
        zone_info = zone_defaults["default"]
        for district, info in zone_defaults.items():
            if district in request.address:
                zone_info = info
                break
        
        # Check for commercial keywords
        if any(kw in request.address for kw in ["역삼", "테헤란", "강남대로", "선릉"]):
            zone_info = {"zone": "준주거지역", "bcr": 70, "far": 400}
        
        zone_type = zone_info["zone"]
        logger.info(f"✅ Zone type: {zone_type}, FAR: {zone_info['far']}%, BCR: {zone_info['bcr']}%")
        
        # ========================================
        # STEP 3: Estimate land area if not provided
        # ========================================
        land_area_sqm = request.land_area_sqm
        if not land_area_sqm:
            # Default estimate: 500-1000 sqm for typical plots
            land_area_sqm = 660.0  # Average
            logger.info(f"⚠️ Land area not provided, using estimate: {land_area_sqm} ㎡")
        else:
            logger.info(f"✅ Land area: {land_area_sqm} ㎡")
        
        # ========================================
        # STEP 4: Run location/infra analysis
        # ========================================
        logger.info("🏙️ Step 4: Analyzing location & infrastructure...")
        from app.engines.location_infra_engine import get_location_engine
        location_engine = get_location_engine()
        location_analysis = location_engine.analyze(request.address)
        logger.info(f"✅ Location score: {location_analysis.overall_score}/100")
        
        # ========================================
        # STEP 5: Run development/regulation analysis
        # ========================================
        logger.info("🏗️ Step 5: Analyzing development & regulations...")
        from app.engines.development_regulation_engine import get_development_engine
        dev_engine = get_development_engine()
        dev_analysis = dev_engine.analyze(
            zone_type=zone_type,
            bcr_legal=zone_info["bcr"],
            far_legal=zone_info["far"],
            address=request.address
        )
        logger.info(f"✅ Development score: {dev_analysis.regulation_score}/100")
        
        # ========================================
        # STEP 6: Auto-calculate premium from scores
        # ========================================
        logger.info("💎 Step 6: Calculating premium factors...")
        
        # Premium calculation based on location & development scores
        location_premium = (location_analysis.overall_score - 70) * 0.5  # 0.5% per point above 70
        development_premium = (dev_analysis.regulation_score - 70) * 0.3  # 0.3% per point above 70
        
        # Market trend (fixed for now, can be enhanced later)
        market_premium = 10.0  # 10% base market premium for good areas
        
        # Total premium
        total_premium_pct = max(0, location_premium + development_premium + market_premium)
        
        logger.info(f"✅ Total premium: {total_premium_pct:.1f}%")
        logger.info(f"   - Location: {location_premium:.1f}%")
        logger.info(f"   - Development: {development_premium:.1f}%")
        logger.info(f"   - Market: {market_premium:.1f}%")
        
        # ========================================
        # STEP 7: Run appraisal engine
        # ========================================
        logger.info("🧮 Step 7: Running appraisal engine...")
        engine = AppraisalEngineV241()
        
        input_data = {
            'address': request.address,
            'land_area_sqm': land_area_sqm,
            'zone_type': zone_type,
            'individual_land_price_per_sqm': individual_land_price,
            'premium_factors': {},  # Will be filled with auto-calculated values
            'comparable_sales': []
        }
        
        appraisal_result = engine.process(input_data)
        logger.info(f"✅ Appraisal complete: {appraisal_result.get('final_appraised_value', 0):.2f}억원")
        
        # ========================================
        # STEP 8: Enhance appraisal result with analysis
        # ========================================
        appraisal_result['location_analysis'] = {
            'overall_score': location_analysis.overall_score,
            'transport_score': location_analysis.transport_score,
            'education_score': location_analysis.education_score,
            'convenience_score': location_analysis.convenience_score,
            'medical_score': location_analysis.medical_score,
            'narrative': location_analysis.narrative,
            'details': location_analysis.details
        }
        
        appraisal_result['development_analysis'] = {
            'regulation_score': dev_analysis.regulation_score,
            'opportunity_factors': dev_analysis.opportunity_factors,
            'constraint_factors': dev_analysis.constraint_factors,
            'narrative': dev_analysis.narrative,
            'details': dev_analysis.details
        }
        
        # Override premium_info with auto-calculated values
        appraisal_result['premium_info']['premium_factors'] = {
            'location_premium': {
                'score': location_analysis.overall_score,
                'premium_pct': location_premium,
                'description': '입지 및 교통 접근성 기반 프리미엄'
            },
            'development_potential': {
                'score': dev_analysis.regulation_score,
                'premium_pct': development_premium,
                'description': '개발 잠재력 및 규제 환경 기반 프리미엄'
            },
            'market_trend': {
                'score': 80,  # Fixed score
                'premium_pct': market_premium,
                'description': '시장 동향 및 가격 상승세 반영'
            },
            'total_premium_pct': total_premium_pct,
            'summary_narrative': (
                f"입지 점수 {location_analysis.overall_score}점, "
                f"개발 점수 {dev_analysis.regulation_score}점을 종합하여 "
                f"약 {total_premium_pct:.1f}% 수준의 프리미엄을 적용하였습니다."
            )
        }
        
        # Apply calculated premium to final value
        base_value = appraisal_result.get('base_weighted_value', 0)
        premium_multiplier = 1 + (total_premium_pct / 100)
        final_value_with_premium = base_value * premium_multiplier
        
        appraisal_result['final_appraised_value'] = final_value_with_premium
        appraisal_result['final_appraisal_value'] = final_value_with_premium
        
        logger.info(f"✅ Final value with auto-premium: {final_value_with_premium:.2f}억원")
        
        # ========================================
        # STEP 9: Generate PDF
        # ========================================
        logger.info("📄 Step 9: Generating PDF...")
        pdf_generator = UltimateAppraisalPDFGenerator()
        
        appraisal_result['address'] = request.address
        appraisal_result['land_area_sqm'] = land_area_sqm
        appraisal_result['zone_type'] = zone_type
        appraisal_result['individual_land_price'] = individual_land_price
        
        html_content = pdf_generator.generate_pdf_html(
            appraisal_data=appraisal_result,
            comparable_sales=[]
        )
        
        pdf_bytes = pdf_generator.generate_pdf_bytes(html_content)
        logger.info(f"✅ PDF generated: {len(pdf_bytes)} bytes")
        
        # ========================================
        # STEP 10: Save and return
        # ========================================
        storage_service = PDFStorageService(storage_type="local")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"자동감정평가_{request.address.replace(' ', '_')}_{timestamp}.pdf"
        
        metadata = {
            "type": "auto_appraisal",
            "address": request.address,
            "land_area_sqm": str(land_area_sqm),
            "generated_at": datetime.now().isoformat(),
            "final_value": str(final_value_with_premium),
            "premium_pct": str(total_premium_pct)
        }
        
        storage_info = storage_service.save_pdf(pdf_bytes, filename, metadata)
        
        return {
            "status": "success",
            "message": "✅ 완전 자동화 감정평가 완료",
            "file_id": storage_info['file_id'],
            "download_url": storage_info['download_url'],
            "expires_at": storage_info['expires_at'],
            "file_size_kb": storage_info['file_size_bytes'] // 1024,
            "auto_analysis": {
                "land_price_per_sqm": individual_land_price,
                "zone_type": zone_type,
                "location_score": location_analysis.overall_score,
                "development_score": dev_analysis.regulation_score,
                "total_premium_pct": round(total_premium_pct, 1),
                "final_value": round(final_value_with_premium, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Auto appraisal failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"자동 감정평가 실패: {str(e)}")


@router.post("/appraisal/detailed-pdf")
async def generate_detailed_appraisal_pdf(request: AppraisalRequest):
    """
    **상세 감정평가 보고서 PDF 생성**
    
    상세한 계산 과정, 입지/인프라 분석, 개발/규제 분석, 프리미엄 요인 분석이 포함된
    전문가급 감정평가 보고서를 생성합니다.
    
    Returns: PDF 다운로드 정보
    """
    try:
        logger.info(f"📄 Generating DETAILED appraisal PDF for: {request.address}")
        
        # ========================================
        # Step 1: Execute appraisal with all engines
        # ========================================
        engine = AppraisalEngineV241()
        
        # Auto-load land price if not provided
        individual_land_price = request.individual_land_price_per_sqm
        if not individual_land_price:
            try:
                from app.services.individual_land_price_api import IndividualLandPriceAPI
                price_api = IndividualLandPriceAPI()
                individual_land_price = price_api.get_individual_land_price(request.address)
                logger.info(f"🏘️ Auto-loaded land price: {individual_land_price:,} 원/㎡")
            except Exception as e:
                logger.warning(f"Land price auto-load failed: {e}")
                individual_land_price = 8000000
        
        # ========================================
        # Step 1.5: Auto-detect premium factors
        # ========================================
        premium_factors_data = {}
        
        # First, try auto-detection based on address
        try:
            from app.services.premium_auto_detector import PremiumAutoDetector
            auto_detector = PremiumAutoDetector()
            auto_detected = auto_detector.auto_detect_premium_factors(request.address)
            if auto_detected:
                premium_factors_data.update(auto_detected)
                logger.info(f"🤖 Auto-detected {len(auto_detected)} premium factors for PDF")
        except Exception as e:
            logger.warning(f"Premium auto-detection failed: {e}")
        
        # Then merge with user-provided values (user values override auto-detected)
        if request.premium_factors:
            user_factors = request.premium_factors.model_dump()
            premium_factors_data.update(user_factors)
            logger.info(f"✏️ Merged with user-provided premium factors")
        
        logger.info(f"📋 Total premium factors for PDF: {len(premium_factors_data)} factors")
        
        # Prepare input data
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm,
            'zone_type': request.zone_type,
            'individual_land_price_per_sqm': individual_land_price,
            'premium_factors': premium_factors_data,
            'comparable_sales': [cs.model_dump() for cs in request.comparable_sales] if request.comparable_sales else []
        }
        
        # Execute appraisal
        appraisal_result = engine.process(input_data)
        logger.info(f"✅ Appraisal complete: {appraisal_result.get('final_appraisal_value', 0)}억원")
        
        # Log premium info for debugging
        premium_info = appraisal_result.get('premium_info', {})
        logger.info(f"📊 Premium info: has_premium={premium_info.get('has_premium')}, percentage={premium_info.get('premium_percentage', 0):.1f}%")
        
        # ========================================
        # Step 2: Run location/infra analysis
        # ========================================
        from app.engines.location_infra_engine import get_location_engine
        location_engine = get_location_engine()
        location_analysis = location_engine.analyze(request.address)
        
        # ========================================
        # Step 3: Run development/regulation analysis
        # ========================================
        from app.engines.development_regulation_engine import get_development_engine
        dev_engine = get_development_engine()
        dev_analysis = dev_engine.analyze(
            zone_type=request.zone_type,
            bcr_legal=50.0,  # Default, should be from zoning API
            far_legal=200.0,  # Default, should be from zoning API
            address=request.address
        )
        
        # ========================================
        # Step 4: Merge all analysis into appraisal_result
        # ========================================
        appraisal_result['location_analysis'] = {
            'overall_score': location_analysis.overall_score,
            'transport_score': location_analysis.transport_score,
            'education_score': location_analysis.education_score,
            'convenience_score': location_analysis.convenience_score,
            'medical_score': location_analysis.medical_score,
            'narrative': location_analysis.narrative,
            'details': location_analysis.details
        }
        
        appraisal_result['development_analysis'] = {
            'regulation_score': dev_analysis.regulation_score,
            'opportunity_factors': dev_analysis.opportunity_factors,
            'constraint_factors': dev_analysis.constraint_factors,
            'narrative': dev_analysis.narrative,
            'details': dev_analysis.details
        }
        
        # ========================================
        # Step 5: Generate detailed PDF using Ultimate generator
        # ========================================
        pdf_generator = UltimateAppraisalPDFGenerator()
        
        # Add address info
        appraisal_result['address'] = request.address
        appraisal_result['land_area_sqm'] = request.land_area_sqm
        appraisal_result['zone_type'] = request.zone_type
        appraisal_result['individual_land_price'] = individual_land_price
        
        # Generate HTML first (for debugging)
        html_content = pdf_generator.generate_pdf_html(
            appraisal_data=appraisal_result
        )
        
        # Generate PDF bytes
        pdf_bytes = pdf_generator.generate_pdf_bytes(html_content)
        
        logger.info(f"✅ Detailed PDF generated: {len(pdf_bytes)} bytes")
        
        # ========================================
        # Step 6: Return PDF directly as file download
        # ========================================
        from fastapi.responses import Response
        from datetime import datetime
        from urllib.parse import quote
        
        # Generate filename with URL encoding for Korean characters
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_korean = f"상세감정평가보고서_{timestamp}.pdf"
        filename_encoded = quote(filename_korean)
        filename_ascii = f"detailed_appraisal_report_{timestamp}.pdf"
        
        # Return PDF bytes directly with proper headers
        # Use both ASCII fallback (filename) and UTF-8 encoded (filename*) for compatibility
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename_ascii}\"; filename*=UTF-8''{filename_encoded}",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Detailed PDF generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"상세 PDF 생성 실패: {str(e)}")
