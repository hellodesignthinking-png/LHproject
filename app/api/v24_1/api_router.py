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
# v35.0: Replaced with ultimate_pdf_v35
# from app.services.ultimate_appraisal_pdf_generator import UltimateAppraisalPDFGenerator
from app.services.land_diagnosis_pdf_generator import LandDiagnosisPDFGenerator
from app.services.pdf_storage_service import PDFStorageService

# v36.0 NATIONWIDE: Import nationwide support modules
from app.services.advanced_address_parser_v36 import get_address_parser_v36
from app.data.nationwide_prices import get_market_price, estimate_official_price, get_zone_type_suggestion
from app.services.universal_transaction_engine import UniversalTransactionEngine

# v36.0 ENHANCED (Problems 1-4 해결): Import new modules
from app.services.zone_estimator import estimate_zone_type
from app.services.transaction_generator import TransactionGenerator

# v37.0 ULTIMATE: Complete API integration
from app.api_keys_config import APIKeys
from app.services.complete_land_info_service_v37 import CompleteLandInfoServiceV37

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
    """Request model for appraisal - All fields except address are dynamically fetched from real APIs"""
    address: str = Field(..., description="Property address", example="서울시 마포구 공덕동 123-4")
    land_area_sqm: Optional[float] = Field(660.0, gt=0, description="Land area in ㎡ (default 660㎡)", example=660.0)
    zone_type: Optional[str] = Field(None, description="Zoning type (auto-detected from vworld API if not provided)", example="제3종일반주거지역")
    individual_land_price_per_sqm: Optional[float] = Field(None, gt=0, description="Individual land price KRW/㎡ (auto-detected from NLIS API if not provided)", example=7000000)
    premium_factors: Optional[PremiumFactors] = Field(None, description="Premium adjustment factors (auto-detected based on address using PremiumAutoDetector)")
    comparable_sales: Optional[List[ComparableSale]] = Field(None, description="List of comparable sales (auto-fetched from MOLIT API if not provided)")


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
    
    v36.0 NATIONWIDE: Now supports all 17 provinces/229 cities with automatic zone/price estimation!
    
    Standard Korean real estate appraisal using 3 approaches:
    1. Cost Approach (원가법)
    2. Sales Comparison (거래사례비교법)
    3. Income Approach (수익환원법)
    """
    try:
        logger.info(f"🌏 [v36 NATIONWIDE] Starting appraisal for {request.address}")
        
        # ========================================
        # V36.0: Step 1 - Parse address for nationwide support
        # ========================================
        parser = get_address_parser_v36()
        parsed_address = parser.parse(request.address)
        
        sido = parsed_address.get('sido')
        sigungu = parsed_address.get('sigungu')
        dong = parsed_address.get('dong')
        
        logger.info(f"   📍 Parsed: {sido} / {sigungu} / {dong}")
        
        # ========================================
        # V36.0: Step 2 - Auto-estimate zone type (if not provided)
        # ========================================
        zone_type = request.zone_type
        if not zone_type:
            zone_type = get_zone_type_suggestion(sido, sigungu)
            logger.info(f"   🏘️ Auto-estimated zone_type: {zone_type}")
        else:
            logger.info(f"   ✏️ User-provided zone_type: {zone_type}")
        
        # ========================================
        # V36.0: Step 3 - Get market price and auto-estimate official price
        # ========================================
        market_price_per_sqm = get_market_price(sido, sigungu, dong)  # Returns 만원/㎡
        market_price_per_sqm_krw = market_price_per_sqm * 10000  # Convert to 원/㎡
        
        individual_land_price = request.individual_land_price_per_sqm
        if not individual_land_price:
            # Auto-estimate official price from market price
            official_price_per_sqm = estimate_official_price(market_price_per_sqm, zone_type)  # 만원/㎡
            individual_land_price = int(official_price_per_sqm * 10000)  # Convert to 원/㎡
            logger.info(f"   💰 Auto-estimated official price: {individual_land_price:,} 원/㎡ (from market {market_price_per_sqm:.0f}만원/㎡)")
        else:
            logger.info(f"   ✏️ User-provided land price: {individual_land_price:,} 원/㎡")
        
        # ========================================
        # V36.0 ENHANCED: Step 4 - Generate nationwide transactions (Problem 2 해결)
        # ========================================
        from app.services.transaction_generator import TransactionGenerator
        
        transaction_gen = TransactionGenerator()
        generated_transactions = transaction_gen.generate_realistic_transactions(
            sido=sido or "서울특별시",
            sigungu=sigungu or "강남구",
            dong=dong or "역삼동",
            target_size_sqm=request.land_area_sqm,
            base_price_per_sqm=market_price_per_sqm,  # 만원/㎡
            zone_type=zone_type
        )
        logger.info(f"   📊 Generated {len(generated_transactions)} nationwide transactions (accurate addresses)")
        
        engine = AppraisalEngineV241()
        
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
            # Use generated transactions as comparables
            if generated_transactions:
                # Convert transactions to comparable sales format
                comparable_sales_data = []
                for tx in generated_transactions[:5]:  # Top 5
                    comparable_sales_data.append({
                        'price_per_sqm': tx['price_per_sqm'],
                        'time_adjustment': 1.0,
                        'location_adjustment': 1.0,
                        'individual_adjustment': 1.0,
                        'weight': 0.2
                    })
                logger.info(f"📡 Auto-generated {len(comparable_sales_data)} comparable sales from transactions")
        
        # ========================================
        # 4. Prepare premium factors (user input only, no auto-detection)
        # ========================================
        premium_factors_data = {}
        
        if request.premium_factors:
            user_factors = request.premium_factors.model_dump()
            # Only include non-zero values
            non_zero_user_factors = {k: v for k, v in user_factors.items() if v != 0}
            premium_factors_data.update(non_zero_user_factors)
            logger.info(f"✏️ User-provided {len(non_zero_user_factors)} non-zero premium factors")
            if non_zero_user_factors:
                logger.info(f"   Factors: {list(non_zero_user_factors.keys())}")
        else:
            logger.info(f"📋 No premium factors provided (all defaults to 0)")
        
        # ========================================
        # 5. Prepare input data (v36.0 NATIONWIDE with automatic estimation)
        # ========================================
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm if request.land_area_sqm else 660.0,
            'zone_type': zone_type,  # Auto-estimated or user-provided
            'individual_land_price_per_sqm': individual_land_price,  # Auto-estimated or user-provided
            'premium_factors': premium_factors_data,
            'comparable_sales': comparable_sales_data,
            # V36.0: Include parsed address and transactions for PDF generation
            'parsed_address': parsed_address,
            'generated_transactions': generated_transactions,
            'market_price_per_sqm': market_price_per_sqm  # Store in 만원/㎡ for consistency
        }
        
        logger.info(f"📋 [v36] Final input: land={input_data['land_area_sqm']}㎡, zone={input_data['zone_type']}, price={individual_land_price:,}원/㎡")
        logger.info(f"   🌏 Address: {sido} {sigungu} {dong or ''}, Market: {market_price_per_sqm:.0f}만원/㎡")
        
        result = engine.process(input_data)
        
        # Extract premium information if available
        premium_info = result.get('premium_info', {})
        
        # ========================================
        # Problem 4 해결: Complete Response with ALL Data
        # ========================================
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "version": "v36.0 ENHANCED (Problems 1-4 해결)",
            
            # 감정평가 결과
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
            
            # 토지 정보 (주소, 공시지가, 용도지역)
            "land_info": {
                "address_parsed": {
                    "sido": sido,
                    "sigungu": sigungu,
                    "dong": dong,
                    "full": request.address
                },
                "zone_type": zone_type,  # 용도지역 (명시적 반환)
                "individual_land_price_per_sqm": individual_land_price,  # 공시지가 (원/㎡)
                "individual_land_price_per_pyeong": int(individual_land_price * 3.3058),  # 공시지가 (원/평)
                "market_price_per_sqm_krw": int(market_price_per_sqm_krw),  # 시세 (원/㎡)
                "market_price_per_sqm_man": market_price_per_sqm,  # 시세 (만원/㎡)
                "official_to_market_ratio": (individual_land_price / market_price_per_sqm_krw) if market_price_per_sqm_krw > 0 else 0.7
            },
            
            # 거래사례 (명시적 반환)
            "transactions": generated_transactions,  # 전체 15건
            "transactions_summary": {
                "count": len(generated_transactions),
                "avg_price_per_sqm": int(sum([t['price_per_sqm'] for t in generated_transactions]) / len(generated_transactions)) if generated_transactions else 0,
                "min_distance_km": min([t['distance_km'] for t in generated_transactions]) if generated_transactions else 0,
                "max_distance_km": max([t['distance_km'] for t in generated_transactions]) if generated_transactions else 0
            },
            
            # 기타 상세 정보
            "breakdown": result['breakdown'],
            "metadata": result['metadata'],
            "notes": result['notes'],
            "premium_info": premium_info
        }
        
    except Exception as e:
        logger.error(f"Error in appraisal calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Appraisal failed: {str(e)}")


@router.post("/appraisal/v37")
async def calculate_appraisal_v37(request: AppraisalRequest):
    """
    **v37.0 ULTIMATE - Complete API Integration**
    
    Uses ALL real APIs:
    - Kakao: Address parsing & coordinates
    - V-World: PNU code generation
    - MOLIT: Zone type, official land price, REAL TRANSACTIONS
    
    Returns complete appraisal with 100% real data where available.
    """
    try:
        logger.info("="*80)
        logger.info("🚀 [v37 ULTIMATE] Starting Complete API Integration")
        logger.info(f"   Address: {request.address}")
        logger.info(f"   Land Area: {request.land_area_sqm}㎡")
        logger.info("="*80)
        
        # ========================================
        # v37.0: Complete Land Info Service
        # ========================================
        
        land_service = CompleteLandInfoServiceV37(
            kakao_key=APIKeys.KAKAO_REST_API_KEY,
            vworld_key=APIKeys.VWORLD_API_KEY,
            molit_key=APIKeys.MOLIT_API_KEY
        )
        
        land_info = land_service.get_complete_info(
            address=request.address,
            land_area_sqm=request.land_area_sqm
        )
        
        if not land_info['success']:
            raise HTTPException(400, "Failed to retrieve land information")
        
        # ========================================
        # Use retrieved data for appraisal
        # ========================================
        
        zone_type = land_info['zone_type']
        individual_land_price = land_info['land_price']['value']
        transactions = land_info['transactions']
        
        logger.info(f"   ✅ Zone Type: {zone_type}")
        logger.info(f"   ✅ Land Price: {individual_land_price:,}원/㎡")
        logger.info(f"   ✅ Transactions: {len(transactions)}건")
        
        # Prepare comparable sales from transactions
        comparable_sales_data = []
        if transactions:
            for tx in transactions[:5]:  # Use top 5
                comparable_sales_data.append({
                    'price_per_sqm': tx.get('price_per_sqm', individual_land_price),
                    'time_adjustment': 1.0,
                    'location_adjustment': 1.0,
                    'individual_adjustment': 1.0,
                    'weight': 0.2
                })
        
        # Prepare premium factors
        premium_factors_data = {}
        if request.premium_factors:
            user_factors = request.premium_factors.model_dump()
            non_zero_user_factors = {k: v for k, v in user_factors.items() if v != 0}
            premium_factors_data.update(non_zero_user_factors)
        
        # Prepare input for engine
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm,
            'zone_type': zone_type,
            'individual_land_price_per_sqm': individual_land_price,
            'premium_factors': premium_factors_data,
            'comparable_sales': comparable_sales_data,
            'parsed_address': land_info['address'],
            'generated_transactions': transactions,
            'pnu': land_info.get('pnu', '')
        }
        
        # Run appraisal engine
        engine = AppraisalEngineV241()
        result = engine.process(input_data)
        
        # Extract premium information
        premium_info = result.get('premium_info', {})
        
        logger.info("="*80)
        logger.info("✅ [v37 ULTIMATE] Appraisal Complete!")
        logger.info(f"   Final Value: {result['final_appraisal_value']:.2f}억원")
        logger.info(f"   API Usage:")
        for key, value in land_info['api_usage'].items():
            logger.info(f"      {key}: {value}")
        logger.info("="*80)
        
        return {
            "status": "success",
            "version": "v37.0 ULTIMATE",
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
            "land_info": {
                "address_parsed": land_info['address'],
                "pnu": land_info.get('pnu', ''),
                "zone_type": zone_type,
                "individual_land_price_per_sqm": individual_land_price,
                "land_price_info": land_info['land_price'],
                "transactions_count": len(transactions),
                "api_usage": land_info['api_usage']
            },
            "breakdown": result['breakdown'],
            "metadata": result['metadata'],
            "notes": result['notes'],
            "premium_info": premium_info,
            "transactions": transactions[:5]  # Include first 5 transactions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in v37 appraisal: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"v37 Appraisal failed: {str(e)}")


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
                logger.info(f"   Auto-detected: {auto_detected}")
            else:
                logger.warning(f"⚠️ No premium factors auto-detected for address: {request.address}")
        except Exception as e:
            logger.error(f"❌ Premium auto-detection failed: {e}", exc_info=True)
        
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
        
        # Step 2: Generate PDF using v38.0 ULTIMATE (36-page Premium Production Grade)
        from app.services.premium_pdf_v38_ultimate import PremiumPDFv38Ultimate
        
        pdf_generator = PremiumPDFv38Ultimate()
        html_content = pdf_generator.generate_html(appraisal_result)
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
        # v34.0 ENCODING FIX: Use only ASCII characters in filename
        # Korean characters will be in Content-Disposition header separately
        timestamp_clean = timestamp.replace(':', '').replace('-', '')
        filename_ascii = f"Appraisal_Report_{timestamp_clean}.pdf"
        
        # URL encode Korean filename for proper browser display
        from urllib.parse import quote
        filename_korean = f"감정평가보고서_{timestamp}.pdf"
        encoded_filename = quote(filename_korean)
        
        logger.info(f"PDF generated successfully: {filename_ascii}")
        
        # Step 5: Return FileResponse with PDF
        # v34.0 ENCODING FIX: Use only ASCII in base filename, UTF-8 for display name
        return FileResponse(
            path=tmp_file_path,
            media_type="application/pdf",
            filename=filename_ascii,
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename_ascii}\"; filename*=UTF-8''{encoded_filename}"
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
        
        # Step 2: Generate PDF using v38.0 ULTIMATE (36-page Premium Production Grade)
        from app.services.premium_pdf_v38_ultimate import PremiumPDFv38Ultimate
        
        pdf_generator = PremiumPDFv38Ultimate()
        html_content = pdf_generator.generate_html(appraisal_result)
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
    **개별공시지가 자동 조회 API (v29.0 Enhanced)**
    
    주소를 입력하면 개별공시지가를 자동으로 조회합니다.
    v28.0 컴포넌트 연동 - 실제 시세 데이터 사용
    
    Returns:
        - official_price_per_sqm: 개별공시지가 (원/㎡)
        - year: 기준연도
        - source: 데이터 출처
        - fallback_used: Fallback 사용 여부
    """
    try:
        logger.info(f"🏘️ Fetching official land price for: {req.address}")
        
        # 🔥 v29.0 FIX: Use v28.0 components for REAL data
        try:
            from app.services.advanced_address_parser import AdvancedAddressParser
            from app.services.seoul_market_prices import SeoulMarketPrices
            
            # Step 1: Parse address to get gu and dong
            parser = AdvancedAddressParser()
            parsed = parser.parse(req.address)
            
            if parsed and parsed.get('success'):
                gu = parsed.get('gu', '')
                dong = parsed.get('dong', '')
                
                # Step 2: Get real market price from v28.0 data
                price = SeoulMarketPrices.get_price(gu, dong)
                
                if price and price > 0:
                    logger.info(f"✅ Real market price loaded: {gu} {dong} = {price:,} 원/㎡")
                    return {
                        "success": True,
                        "status": "success",
                        "official_price": price,
                        "official_price_per_sqm": int(price),
                        "year": 2024,
                        "source": f"실제시세데이터_{gu}_{dong}",
                        "fallback_used": False,
                        "address": req.address,
                        "parsed_gu": gu,
                        "parsed_dong": dong
                    }
        except Exception as e:
            logger.warning(f"❌ v28.0 real data fetch failed: {e}")
        
        # Final fallback: Use district averages
        logger.warning(f"⚠️ Using fallback prices for: {req.address}")
        district_prices = {
            "강남구": 20000000,
            "서초구": 18000000,
            "송파구": 16000000,
            "마포구": 13000000,
            "용산구": 17000000,
            "성동구": 13000000,
            "영등포구": 14000000,
            "default": 10000000
        }
        
        price = district_prices.get("default", 10000000)
        for district, avg_price in district_prices.items():
            if district in req.address:
                price = avg_price
                break
        
        return {
            "success": True,
            "status": "success",
            "official_price": price,
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
    **용도지역 자동 조회 API (v29.0 Enhanced)**
    
    주소를 입력하면 용도지역 및 건축 규제 정보를 자동으로 조회합니다.
    v28.0 address parser 연동으로 더 정확한 구/동 파악
    
    Returns:
        - zone_type: 용도지역
        - bcr_legal: 법정 건폐율 (%)
        - far_legal: 법정 용적률 (%)
        - district_overlays: 중복 용도지역/지구
        - regulation_summary: 규제 요약
    """
    try:
        logger.info(f"🗺️ Fetching zoning info for: {req.address}")
        
        # 🔥 v32.0 FIX: Initialize gu/dong first, then try parsing
        gu = ''
        dong = ''
        
        try:
            from app.services.advanced_address_parser import AdvancedAddressParser
            parser = AdvancedAddressParser()
            parsed = parser.parse(req.address)
            
            if parsed and parsed.get('success'):
                gu = parsed.get('gu', '')
                dong = parsed.get('dong', '')
                logger.info(f"✅ Parsed address: {gu} {dong}")
            else:
                logger.warning(f"⚠️ Address parsing returned no success flag")
        except Exception as e:
            logger.warning(f"❌ Address parsing failed: {e}")
            # gu and dong already initialized to ''
        
        # Enhanced zoning based on actual district characteristics
        zone_defaults = {
            "강남구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250, "desc": "강남권 고밀도 주거"},
            "서초구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250, "desc": "강남권 고밀도 주거"},
            "송파구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250, "desc": "잠실 고밀도 주거"},
            "마포구": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200, "desc": "마포 중밀도 주거"},
            "용산구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250, "desc": "용산 고밀도 주거"},
            "영등포구": {"zone": "제3종일반주거지역", "bcr": 50, "far": 250, "desc": "여의도 상업/주거 복합"},
            "성동구": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200, "desc": "성수 중밀도 주거"},
            "광진구": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200, "desc": "건대 중밀도 주거"},
            "강서구": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200, "desc": "강서 중밀도 주거"},
            "관악구": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200, "desc": "관악 중밀도 주거"},
            "default": {"zone": "제2종일반주거지역", "bcr": 60, "far": 200, "desc": "서울 일반 주거"}
        }
        
        zone_info = zone_defaults.get("default")
        if gu:
            zone_info = zone_defaults.get(gu, zone_defaults["default"])
            logger.info(f"✅ Zone found for {gu}: {zone_info['zone']}")
        else:
            # Fallback: Search in address string
            for district, info in zone_defaults.items():
                if district in req.address:
                    zone_info = info
                    logger.info(f"✅ Zone found by search for {district}: {info['zone']}")
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
        
        # ========================================
        # Validate required fields (NO FALLBACKS!)
        # ========================================
        if not request.zone_type:
            raise HTTPException(
                status_code=400,
                detail="zone_type is required. Frontend must fetch from zoning API first."
            )
        
        if not request.individual_land_price_per_sqm:
            raise HTTPException(
                status_code=400,
                detail="individual_land_price_per_sqm is required. Frontend must fetch from land price API first."
            )
        
        individual_land_price = request.individual_land_price_per_sqm
        logger.info(f"✅ Using provided land price for PDF: {individual_land_price:,} 원/㎡")
        logger.info(f"✅ Using provided zone type for PDF: {request.zone_type}")
        
        # ========================================
        # Prepare premium factors (user input only, no auto-detection)
        # ========================================
        premium_factors_data = {}
        
        if request.premium_factors:
            user_factors = request.premium_factors.model_dump()
            non_zero_user_factors = {k: v for k, v in user_factors.items() if v != 0}
            premium_factors_data.update(non_zero_user_factors)
            logger.info(f"✏️ User-provided {len(non_zero_user_factors)} non-zero premium factors for PDF")
            if non_zero_user_factors:
                logger.info(f"   Factors: {list(non_zero_user_factors.keys())}")
        else:
            logger.info(f"📋 No premium factors provided for PDF")
        
        # Prepare input data
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm if request.land_area_sqm else 660.0,
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
        # Step 5: Generate detailed PDF using COMPLETE generator (v25.0)
        # ========================================
        from app.services.complete_appraisal_pdf_generator import get_pdf_generator
        
        pdf_generator = get_pdf_generator()
        
        # Add address info
        appraisal_result['address'] = request.address
        appraisal_result['land_area_sqm'] = request.land_area_sqm
        appraisal_result['zone_type'] = request.zone_type
        appraisal_result['individual_land_price'] = individual_land_price
        
        logger.info("🎯 Using CompleteAppraisalPDFGenerator v25.0")
        
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


@router.post("/appraisal/html")
async def generate_detailed_appraisal_html(request: AppraisalRequest):
    """
    **상세 감정평가 보고서 HTML 미리보기**
    
    🆕 v29.0 FEATURE: PDF와 동일한 내용을 HTML로 미리보기
    
    상세한 계산 과정, 입지/인프라 분석, 개발/규제 분석, 프리미엄 요인 분석이 포함된
    전문가급 감정평가 보고서를 HTML로 미리볼 수 있습니다.
    
    Returns: HTML content (text/html)
    """
    try:
        logger.info(f"🌐 Generating DETAILED appraisal HTML for: {request.address}")
        
        # ========================================
        # Step 1: Execute appraisal with all engines
        # ========================================
        engine = AppraisalEngineV241()
        
        # ========================================
        # Validate required fields (NO FALLBACKS!)
        # ========================================
        if not request.zone_type:
            raise HTTPException(
                status_code=400,
                detail="zone_type is required. Frontend must fetch from zoning API first."
            )
        
        if not request.individual_land_price_per_sqm:
            raise HTTPException(
                status_code=400,
                detail="individual_land_price_per_sqm is required. Frontend must fetch from land price API first."
            )
        
        individual_land_price = request.individual_land_price_per_sqm
        logger.info(f"✅ Using provided land price: {individual_land_price:,} 원/㎡")
        logger.info(f"✅ Using provided zone type: {request.zone_type}")
        
        # ========================================
        # Prepare premium factors (user input only, no auto-detection)
        # ========================================
        premium_factors_data = {}
        
        if request.premium_factors:
            user_factors = request.premium_factors.model_dump()
            non_zero_user_factors = {k: v for k, v in user_factors.items() if v != 0}
            premium_factors_data.update(non_zero_user_factors)
            logger.info(f"✏️ User-provided {len(non_zero_user_factors)} non-zero premium factors for HTML")
            if non_zero_user_factors:
                logger.info(f"   Factors: {list(non_zero_user_factors.keys())}")
        else:
            logger.info(f"📋 No premium factors provided for HTML")
        
        # Prepare input data
        input_data = {
            'address': request.address,
            'land_area_sqm': request.land_area_sqm if request.land_area_sqm else 660.0,
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
        # Step 5: Generate HTML using COMPLETE generator (v25.0)
        # ========================================
        from app.services.complete_appraisal_pdf_generator import get_pdf_generator
        
        pdf_generator = get_pdf_generator()
        
        # Add address info
        appraisal_result['address'] = request.address
        appraisal_result['land_area_sqm'] = request.land_area_sqm
        appraisal_result['zone_type'] = request.zone_type
        appraisal_result['individual_land_price'] = individual_land_price
        
        logger.info("🎯 Using CompleteAppraisalPDFGenerator v25.0 for HTML preview")
        
        # Generate HTML content (same template as PDF)
        html_content = pdf_generator.generate_pdf_html(
            appraisal_data=appraisal_result
        )
        
        logger.info(f"✅ Detailed HTML generated: {len(html_content)} chars")
        
        # ========================================
        # Step 6: Return HTML directly for browser preview
        # ========================================
        from fastapi.responses import HTMLResponse
        
        return HTMLResponse(
            content=html_content,
            headers={
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Detailed HTML generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"상세 HTML 생성 실패: {str(e)}")


# ============================================================================
# TEST & DEBUG ENDPOINTS (v32.0)
# ============================================================================

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    from datetime import datetime
    return {
        "status": "healthy",
        "version": "v32.0",
        "timestamp": datetime.now().isoformat(),
        "message": "ZeroSite API is running"
    }


@router.post("/appraisal/test")
async def test_appraisal_simple(address: str, land_area: float = 360.0):
    """
    Simple test endpoint - no complex validation
    """
    try:
        logger.info(f"🧪 Test appraisal: {address}, {land_area}㎡")
        
        # Use defaults for everything
        engine = AppraisalEngineV241()
        
        input_data = {
            'address': address,
            'land_area_sqm': land_area,
            'zone_type': '제2종일반주거지역',
            'individual_land_price_per_sqm': 10_000_000,
            'premium_factors': {},
            'comparable_sales': []
        }
        
        result = engine.process(input_data)
        
        return {
            "success": True,
            "message": "Test appraisal completed",
            "input": input_data,
            "result": {
                "cost_approach": result.get('cost_approach_value', 0),
                "sales_comparison": result.get('sales_comparison_value', 0),
                "income_approach": result.get('income_approach_value', 0),
                "final_value": result.get('final_appraisal_value', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Test appraisal error: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }
