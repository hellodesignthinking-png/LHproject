"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.schemas import (
    LandAnalysisRequest,
    LandAnalysisResponse,
    ErrorResponse,
    UnitType,
    UnitTypeScore,
    MultiParcelResponse,
    ParcelAnalysisResult
)
from app.services.analysis_engine import AnalysisEngine
from app.services.report_generator import ProfessionalReportGenerator
from app.services.advanced_report_generator import ExpertReportGenerator
from app.services.lh_official_report_generator import LHOfficialReportGenerator
from app.services.lh_report_generator_v7_2 import LHReportGeneratorV72
from app.services.lh_report_generator_v7_5_final import LHReportGeneratorV75Final
from app.services.report_field_mapper_v7_2_complete import ReportFieldMapperV72Complete
from app.services.sheets_service import get_sheets_service
from app.services.lh_notice_loader import LHNoticeLoader
from app.services.dashboard_builder import DashboardBuilder
# ✨ v8.5: Import new financial, visualization, and LH criteria engines
from app.services.financial_engine_v7_4 import FinancialEngine
from app.services.visualization_engine_v85 import VisualizationEngineV85
from app.services.lh_criteria_checker_v85 import LHCriteriaCheckerV85

# ✨ v7.2: Import new Report Engine v7.2 router
from app.routers.report_v7_2 import router as report_v72_router

# ✨ v9.0: Import Analysis API v9.0 router
from app.api.endpoints.analysis_v9_0 import router as analysis_v90_router

# ✨ v9.1: Import Analysis API v9.1 router
from app.api.endpoints.analysis_v9_1 import router as analysis_v91_router

# ✨ v9.1 REAL: Import REAL working version
from app.api.endpoints.analysis_v9_1_REAL import router as analysis_v91_real_router

# ✨ MVP: Import MVP Analysis router
from app.api.endpoints.mvp_analyze import router as mvp_router

# ✨ v11.0 ENHANCEMENTS: Import middleware and utilities
from app.middleware.rate_limiter import RateLimiter, RateLimitConfig
from app.middleware.cache_manager import cache_manager, start_cache_cleanup_task
from app.i18n.translator import translator
import asyncio

settings = get_settings()

# LH 공식 7개 유형 정보 매핑
HOUSING_TYPE_INFO = {
    "청년": {"size": "30㎡", "평": "9평"},
    "신혼·신생아 I": {"size": "45㎡", "평": "14평"},
    "신혼·신생아 II": {"size": "55㎡", "평": "17평"},
    "다자녀": {"size": "65㎡", "평": "20평"},
    "고령자": {"size": "40㎡", "평": "12평"},
    "일반": {"size": "85㎡", "평": "26평"},
    "든든전세": {"size": "85㎡", "평": "26평"}
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행"""
    print("=" * 60)
    print("🚀 ZeroSite v11.0 HYBRID v2 시스템 시작")
    print("=" * 60)
    print(f"📍 환경: {'개발' if settings.debug else '운영'}")
    print(f"🔑 API Keys 로드됨")
    print(f"🛡️  Rate Limiting: Enabled")
    print(f"💾 Cache: In-Memory (Ready)")
    print(f"🌍 Multi-language: Korean + English")
    print(f"✅ All Enhancements: Active")
    print("=" * 60)
    
    # Start background tasks
    cleanup_task = asyncio.create_task(start_cache_cleanup_task())
    
    yield
    
    # Cleanup
    cleanup_task.cancel()
    print("=" * 60)
    print("👋 시스템 종료")
    print("=" * 60)


app = FastAPI(
    title="ZeroSite v11.0 HYBRID v2 - LH 토지진단 시스템",
    description="""
    🎯 ZeroSite v11.0 HYBRID v2 Edition
    
    Features:
    - 🤖 5 AI Engines (LH Score, Decision, Unit-Type, Feasibility, Pseudo Data)
    - 📊 100-point LH Scoring System
    - 🎯 GO/REVIEW/NO-GO Decision Engine  
    - 🏘️ 5 Unit Types × 6 Criteria Analysis
    - ✍️ v7.5-style Professional Narratives
    - 🌍 Multi-language Support (Korean + English)
    - 🛡️ Rate Limiting & Caching
    - 📄 ~26-page Government-grade Reports
    
    Status: 100% Complete | Production Ready
    """,
    version="11.0-HYBRID-v2",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영 환경에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✨ v11.0: Add Rate Limiting Middleware
# Note: RateLimiter uses default configuration from its __init__
# For production, it uses strict limits; for development, lenient limits
app.add_middleware(RateLimiter)

# ✨ v7.2: Include Report Engine v7.2 router
app.include_router(report_v72_router)

# ✨ v9.0: Include Analysis API v9.0 router
app.include_router(analysis_v90_router)

# ✨ v9.1: Include Analysis API v9.1 router
app.include_router(analysis_v91_router)

# ✨ v9.1 REAL: Include REAL working version router
app.include_router(analysis_v91_real_router)

# ✨ MVP: Include MVP Analysis router
app.include_router(mvp_router)

# 정적 파일 서빙
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# ✨ v9.0: Frontend v9.0 서빙
frontend_v9_path = Path(__file__).parent.parent / "frontend_v9"
if frontend_v9_path.exists():
    app.mount("/v9", StaticFiles(directory=str(frontend_v9_path), html=True), name="frontend_v9")


@app.get("/")
async def root():
    """메인 페이지 - Admin Dashboard로 리다이렉트 (v11.0 HYBRID v2)"""
    # v11.0 HYBRID v2 Admin Dashboard로 리다이렉트
    return RedirectResponse(url="/static/admin_dashboard.html", status_code=302)


@app.get("/v11")
async def root_v11():
    """v11.0 HYBRID v2 Admin Dashboard"""
    return RedirectResponse(url="/static/admin_dashboard.html", status_code=302)


@app.get("/v9-legacy")
async def root_v9_legacy():
    """Legacy v9.1 REAL UI (구버전 호환성)"""
    # 타임스탬프를 추가하여 브라우저 캐시 우회
    timestamp = int(datetime.now().timestamp())
    return RedirectResponse(url=f"/v9/index_REAL.html?v={timestamp}", status_code=302)


@app.get("/v7")
async def root_v7():
    """v7.0 웹 인터페이스"""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # 파일이 없는 경우 기본 JSON 응답
    return {
        "service": "LH 토지진단 자동화 시스템",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """상세 헬스 체크 (v11.0 Enhanced)"""
    cache_stats = cache_manager.get_stats()
    
    return {
        "status": "healthy",
        "version": "11.0-HYBRID-v2",
        "apis": {
            "kakao": "configured" if settings.kakao_rest_api_key else "missing",
            "land_regulation": "configured" if settings.land_regulation_api_key else "missing",
            "mois": "configured" if settings.mois_api_key else "missing"
        },
        "enhancements": {
            "rate_limiting": "enabled",
            "caching": "enabled",
            "multi_language": "enabled (ko, en)",
            "admin_dashboard": "enabled"
        },
        "cache_stats": {
            "total_entries": cache_stats["total_entries"],
            "hit_rate": f"{cache_stats['hit_rate_percent']}%",
            "hits": cache_stats["hits"],
            "misses": cache_stats["misses"]
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post(
    "/api/analyze-land",
    response_model=LandAnalysisResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_land(request: LandAnalysisRequest):
    """
    토지 종합 분석 API
    
    - **address**: 분석할 토지의 주소 (예: "서울특별시 강남구 역삼동 123-45")
    - **land_area**: 토지 면적(㎡)
    - **unit_type**: (선택사항) None이면 7가지 유형 모두 자동 분석하여 추천
    
    Returns:
        LandAnalysisResponse: 종합 분석 결과
    """
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        print(f"\n{'='*60}")
        print(f"🆕 새로운 분석 요청 [ID: {analysis_id}]")
        print(f"{'='*60}")
        print(f"📍 주소: {request.address}")
        print(f"📐 면적: {request.land_area}㎡")
        print(f"🏠 유형: {request.unit_type if request.unit_type else '전체 7개 유형 자동 분석'}")
        print()
        
        # 분석 엔진
        engine = AnalysisEngine()
        
        # unit_type이 없으면 7가지 모두 분석
        if not request.unit_type:
            print("🔄 7가지 유형 전체 분석 시작...")
            all_types = list(UnitType)
            
            # ✨ 한 번만 분석하여 type_demand_scores 가져오기 (효율적)
            temp_request = LandAnalysisRequest(
                address=request.address,
                land_area=request.land_area,
                unit_type=UnitType.YOUTH,  # 임시로 청년형 사용 (전체 분석 동일)
                zone_type=request.zone_type,
                land_status=request.land_status,
                land_appraisal_price=request.land_appraisal_price
            )
            result = await engine.analyze_land(temp_request)
            
            # 🔥 type_demand_scores에서 유형별 차별화된 점수 사용
            type_demand_scores = result.get("type_demand_scores", {})
            print(f"  ✓ 유형별 수요점수:")
            for unit_type, score in type_demand_scores.items():
                print(f"    - {unit_type}: {score:.1f}점")
            
            # 유형별 점수 매핑 (영문 → 한글)
            type_mapping = {
                "청년": UnitType.YOUTH.value,
                "신혼·신생아 I": UnitType.NEWLYWED_1.value,
                "신혼·신생아 II": UnitType.NEWLYWED_2.value,
                "다자녀": UnitType.MULTI_CHILD.value,
                "고령자": UnitType.ELDERLY.value,
                "일반": UnitType.GENERAL.value,
                "든든전세": UnitType.SECURE_JEONSE.value
            }
            
            # 각 유형별 점수와 정보 구성
            all_results = []
            for kr_name, en_name in type_mapping.items():
                score = type_demand_scores.get(kr_name, 50.0)  # 기본값 50점
                housing_info = HOUSING_TYPE_INFO.get(en_name, {})
                all_results.append({
                    "unit_type": en_name,
                    "score": score,
                    "size": housing_info.get("size", "N/A")
                })
            
            # 점수 순으로 정렬
            all_results.sort(key=lambda x: x["score"], reverse=True)
            
            # 최고 점수 유형 선택
            best_result = all_results[0]
            recommended_type = best_result["unit_type"]
            
            print(f"  └─ ✅ 추천 유형: {recommended_type} ({best_result['score']:.1f}점)")
            
            # UnitTypeScore 목록 생성
            all_types_scores = [
                UnitTypeScore(
                    unit_type=r["unit_type"],
                    score=r["score"],
                    size=r["size"]
                )
                for r in all_results
            ]
            
        else:
            # 단일 유형 분석 (기존 방식)
            result = await engine.analyze_land(request)
            housing_info = HOUSING_TYPE_INFO.get(request.unit_type.value, {})
            recommended_type = request.unit_type.value
            
            demand_analysis = result["demand_analysis"]
            demand_score = demand_analysis.demand_score if hasattr(demand_analysis, 'demand_score') else demand_analysis.get("demand_score", 0)
            
            all_types_scores = [
                UnitTypeScore(
                    unit_type=request.unit_type.value,
                    score=demand_score,
                    size=housing_info.get("size", "N/A")
                )
            ]
        
        # ✨ v8.5: Calculate financial result using FinancialEngine
        print("💰 v8.5: Calculating financial metrics...")
        financial_engine = FinancialEngine()
        
        # Calculate unit type for financial analysis
        unit_type_for_financial = recommended_type if isinstance(recommended_type, str) else recommended_type.value
        
        # Run comprehensive financial analysis
        from app.services.financial_engine_v7_4 import run_full_financial_analysis
        financial_result = run_full_financial_analysis(
            land_area=request.land_area,
            address=request.address,
            unit_type=unit_type_for_financial,
            construction_type=getattr(request, 'construction_type', 'standard'),
            land_appraisal_price=request.land_appraisal_price  # 🔥 User-provided appraisal
        )
        
        print(f"  ✓ Financial analysis complete:")
        print(f"    - Total CAPEX: {financial_result.get('summary', {}).get('total_investment', 0):,.0f} KRW")
        print(f"    - Unit Count: {financial_result.get('summary', {}).get('unit_count', 0)} units")
        print(f"    - Cap Rate: {financial_result.get('summary', {}).get('cap_rate', 0):.2f}%")
        print(f"    - IRR Range: {financial_result.get('summary', {}).get('irr_range', 'N/A')}")
        
        # 🔥 v8.6: CRITICAL FIX - Override v7.5 unit count with v8.5 financial engine units
        v8_5_unit_count = financial_result.get('summary', {}).get('unit_count', 0)
        if v8_5_unit_count > 0:
            print(f"  🔄 Synchronizing unit count:")
            
            # Get v7.5 building_capacity units safely
            bc = result.get("building_capacity")
            v7_5_units = bc.units if hasattr(bc, 'units') else (bc.get('units', 0) if isinstance(bc, dict) else 0)
            print(f"    - v7.5 building_capacity: {v7_5_units} units (DISCARDING)")
            print(f"    - v8.5 financial_result: {v8_5_unit_count} units (APPLYING)")
            
            # Override all unit count references with v8.5 value
            if isinstance(bc, dict):
                result["building_capacity"]["units"] = v8_5_unit_count
            elif hasattr(bc, 'units'):
                result["building_capacity"].units = v8_5_unit_count
            
            summ = result.get("summary")
            if isinstance(summ, dict):
                result["summary"]["estimated_units"] = v8_5_unit_count
            elif hasattr(summ, 'estimated_units'):
                result["summary"].estimated_units = v8_5_unit_count
            
            result["expected_units"] = v8_5_unit_count
            
            print(f"  ✅ Unit count synchronized to {v8_5_unit_count} units across all data structures")
        
        # ✨ v8.5: Calculate LH scores using v8.5 criteria checker
        print("📊 v8.5: Evaluating LH criteria...")
        lh_checker_v85 = LHCriteriaCheckerV85()
        
        # Determine analysis mode based on unit count
        unit_count = financial_result.get('summary', {}).get('unit_count', 0)
        analysis_mode = 'LH_LINKED' if unit_count >= 50 else 'STANDARD'
        print(f"  ✓ Analysis Mode: {analysis_mode} ({unit_count} units)")
        
        lh_scores = lh_checker_v85.evaluate_financial_feasibility(
            financial_result=financial_result,
            zone_info=result["zone_info"],
            building_capacity=result["building_capacity"],
            accessibility=result.get("demand_analysis", {})
        )
        
        print(f"  ✓ LH Scores calculated:")
        print(f"    - Location: {lh_scores.get('location_score', 0):.1f}/35")
        print(f"    - Scale: {lh_scores.get('scale_score', 0):.1f}/20")
        print(f"    - Financial: {lh_scores.get('financial_score', 0):.1f}/40")
        print(f"    - Regulations: {lh_scores.get('regulations_score', 0):.1f}/15")
        print(f"    - Total: {lh_scores.get('total_score', 0):.1f}/110")
        
        # ✨ v8.5: Generate visualizations
        print("🎨 v8.5: Generating visualizations...")
        viz_engine = VisualizationEngineV85()
        visualizations = viz_engine.generate_all_visualizations(
            financial_result=financial_result,
            lh_scores=lh_scores,
            analysis_data=result
        )
        
        print(f"  ✓ Generated {len(visualizations)} visualization datasets")
        
        # 응답 생성
        response = LandAnalysisResponse(
            status="success",
            analysis_id=analysis_id,
            address=request.address,
            land_area=request.land_area,
            unit_type=recommended_type,
            recommended_unit_type=recommended_type,
            all_types_scores=all_types_scores,
            coordinates=result["coordinates"],
            zone_info=result["zone_info"],
            building_capacity=result["building_capacity"],
            risk_factors=result["risk_factors"],
            demographic_info=result["demographic_info"],
            demand_analysis=result["demand_analysis"],
            summary=result["summary"],
            report_text=None,
            pdf_url=f"/api/reports/{analysis_id}.pdf",
            grade_info=result.get("grade_info"),  # 등급 정보 추가
            checklist=result.get("checklist", []),  # 체크리스트 추가
            checklist_details=result.get("checklist_details"),  # 체크리스트 상세 정보 (PDF용)
            type_demand_scores=result.get("type_demand_scores", {}),  # ✨ v5.0: 유형별 수요점수
            corrected_input=result.get("corrected_input"),  # ✨ v5.0: AI 자동 교정
            geo_optimization=result.get("geo_optimization"),  # ✨ v5.0: 지리 최적화
            # ✨ v8.5: Add new financial, LH scores, and visualization data
            financial_result=financial_result,  # 🔥 NEW: Complete financial analysis
            lh_scores=lh_scores,  # 🔥 NEW: v8.5 LH evaluation scores
            visualizations=visualizations,  # 🔥 NEW: Chart/graph data
            analysis_mode=analysis_mode,  # 🔥 NEW: LH_LINKED or STANDARD
            created_at=datetime.now()
        )
        
        # Google Sheets에 저장 (백그라운드로 실행)
        try:
            sheets_service = get_sheets_service()
            if sheets_service.enabled:
                print("📊 Google Sheets에 분석 결과 저장 중...")
                
                # 담당자 정보 추출
                consultant_info = None
                if request.consultant:
                    consultant_info = {
                        "name": request.consultant.name,
                        "phone": request.consultant.phone,
                        "department": request.consultant.department,
                        "email": request.consultant.email
                    }
                
                # 분석 데이터 준비
                analysis_data = {
                    "address": request.address,
                    "land_area": request.land_area,
                    "zone_info": result["zone_info"].__dict__ if hasattr(result["zone_info"], '__dict__') else result["zone_info"],
                    "recommended_unit_type": recommended_type,
                    "demand_analysis": result["demand_analysis"].__dict__ if hasattr(result["demand_analysis"], '__dict__') else result["demand_analysis"],
                    "building_capacity": result["building_capacity"].__dict__ if hasattr(result["building_capacity"], '__dict__') else result["building_capacity"],
                    "risks": [r.__dict__ if hasattr(r, '__dict__') else r for r in result["risk_factors"]],
                    "report_path": f"/api/reports/{analysis_id}.pdf"
                }
                
                sheets_result = await sheets_service.save_analysis(analysis_data, consultant_info)
                
                if sheets_result.get("success"):
                    print(f"  ✅ Google Sheets 저장 완료 (행 {sheets_result.get('row_number')})")
                    if sheets_result.get("duplicate"):
                        print(f"  ⚠️ 중복 경고: 이 토지는 이전에 {sheets_result.get('duplicate_count')}회 분석되었습니다")
                        print(f"     분석 날짜: {', '.join(sheets_result.get('duplicate_dates', []))}")
                else:
                    print(f"  ⚠️ Google Sheets 저장 실패: {sheets_result.get('message')}")
        except Exception as e:
            print(f"⚠️ Google Sheets 저장 중 오류 (계속 진행): {e}")
        
        print(f"{'='*60}")
        print(f"✅ 분석 완료 [ID: {analysis_id}]")
        print(f"{'='*60}\n")
        
        return response
        
    except ValueError as e:
        print(f"❌ 요청 오류: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_code": "INVALID_REQUEST",
                "message": str(e)
            }
        )
    
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": "분석 중 오류가 발생했습니다.",
                "details": str(e) if settings.debug else None
            }
        )


@app.post(
    "/api/analyze-multi-parcel",
    response_model=LandAnalysisResponse,  # Import MultiParcelResponse at top
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def analyze_multi_parcel(request: dict):
    """
    ✨ v5.0: 다필지 분석 API
    
    여러 필지를 동시에 분석하여 각각의 적합성을 평가합니다.
    
    Request Body:
        - parcels: List[str] - 필지 주소 리스트 (최대 10개)
        - land_area: float - 총 토지 면적
        - unit_type: Optional[str] - 세대 유형
        - lh_version: str - LH 기준 버전 (기본: "2024")
        
    Returns:
        MultiParcelResponse: 다필지 분석 결과
    """
    from app.schemas import MultiParcelResponse, ParcelAnalysisResult
    
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        print(f"\n{'='*60}")
        print(f"🆕 다필지 분석 요청 [ID: {analysis_id}]")
        print(f"{'='*60}")
        
        # 요청 파라미터 파싱
        parcels = request.get("parcels", [])
        land_area = request.get("land_area", 0)
        unit_type_str = request.get("unit_type")
        lh_version = request.get("lh_version", "2024")
        
        if not parcels or not isinstance(parcels, list):
            raise ValueError("필지 주소 리스트(parcels)가 필요합니다.")
        
        if len(parcels) > 10:
            raise ValueError("최대 10개 필지까지 분석 가능합니다.")
        
        if land_area <= 0:
            raise ValueError("유효한 토지 면적이 필요합니다.")
        
        print(f"📍 필지 수: {len(parcels)}개")
        print(f"📐 총 면적: {land_area}㎡")
        print(f"🏠 유형: {unit_type_str or '전체 7개 유형 자동 분석'}")
        print()
        
        # Unit type 변환
        unit_type_obj = None
        if unit_type_str:
            unit_type_obj = UnitType(unit_type_str)
        
        # 분석 엔진
        engine = AnalysisEngine()
        
        # 각 필지별로 분석
        results = []
        successful_count = 0
        failed_count = 0
        
        for idx, parcel_address in enumerate(parcels, 1):
            print(f"🔍 필지 {idx}/{len(parcels)}: {parcel_address}")
            
            try:
                # 개별 필지 분석 요청 생성
                parcel_request = LandAnalysisRequest(
                    address=parcel_address,
                    land_area=land_area / len(parcels),  # 면적 균등 분배 (실제로는 개별 입력 필요)
                    unit_type=unit_type_obj,
                    lh_version=lh_version
                )
                
                # 분석 실행
                parcel_result = await engine.analyze_land(parcel_request)
                
                # 결과 저장
                demand_score = parcel_result["demand_analysis"].demand_score
                building_capacity = parcel_result["building_capacity"].units
                
                result_obj = ParcelAnalysisResult(
                    address=parcel_address,
                    success=True,
                    coordinates=parcel_result["coordinates"],
                    demand_score=demand_score,
                    building_capacity=building_capacity,
                    risk_factors=parcel_result["risk_factors"],
                    summary=parcel_result["summary"]
                )
                
                results.append(result_obj)
                successful_count += 1
                print(f"  ✅ 분석 완료: 수요점수 {demand_score:.1f}점, {building_capacity}세대")
                
            except Exception as e:
                # 개별 필지 분석 실패 처리
                result_obj = ParcelAnalysisResult(
                    address=parcel_address,
                    success=False,
                    error_message=str(e)
                )
                results.append(result_obj)
                failed_count += 1
                print(f"  ❌ 분석 실패: {e}")
        
        # 추천 필지 선정 (점수 기반 상위 3개)
        successful_results = [r for r in results if r.success and r.demand_score is not None]
        successful_results.sort(key=lambda x: x.demand_score, reverse=True)
        recommended_parcels = [r.address for r in successful_results[:3]]
        
        # 클러스터링 분석 (선택사항 - 여기서는 간단히 생략)
        cluster_analysis = None
        if len(successful_results) >= 2:
            # 클러스터링 분석 수행 가능
            parcel_analyzer = engine.parcel_analyzer
            parcel_data = [
                {
                    "address": r.address,
                    "latitude": r.coordinates.latitude if r.coordinates else 0,
                    "longitude": r.coordinates.longitude if r.coordinates else 0,
                    "area": land_area / len(parcels),
                    "demand_score": r.demand_score,
                    "building_capacity": r.building_capacity
                }
                for r in successful_results
            ]
            
            clustering_result = parcel_analyzer.analyze_parcels(parcel_data)
            cluster_analysis = {
                "total_parcels": clustering_result.total_parcels,
                "clusters": [c.dict() for c in clustering_result.clusters],
                "recommended_cluster_id": clustering_result.recommended_cluster_id,
                "optimization_suggestions": clustering_result.optimization_suggestions
            }
        
        # 응답 생성
        response = MultiParcelResponse(
            status="success",
            analysis_id=analysis_id,
            total_parcels=len(parcels),
            successful=successful_count,
            failed=failed_count,
            results=results,
            cluster_analysis=cluster_analysis,
            recommended_parcels=recommended_parcels,
            created_at=datetime.now()
        )
        
        print(f"\n{'='*60}")
        print(f"✅ 다필지 분석 완료 [ID: {analysis_id}]")
        print(f"   성공: {successful_count}개, 실패: {failed_count}개")
        print(f"   추천 필지: {', '.join(recommended_parcels[:2])} 외 {len(recommended_parcels)-2}개" if len(recommended_parcels) > 2 else f"   추천 필지: {', '.join(recommended_parcels)}")
        print(f"{'='*60}\n")
        
        return response
        
    except ValueError as e:
        print(f"❌ 요청 오류: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "error_code": "INVALID_REQUEST",
                "message": str(e)
            }
        )
    
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "INTERNAL_ERROR",
                "message": "다필지 분석 중 오류가 발생했습니다.",
                "details": str(e) if settings.debug else None
            }
        )


@app.post("/api/lh-notices/sync")
async def sync_lh_notices():
    """
    ✨ v5.0: LH 공고문 Google Drive 동기화 API
    
    Google Drive에서 LH 공고문 PDF를 자동으로 다운로드하고,
    PDF에서 규칙을 추출하여 JSON 파일로 저장합니다.
    
    Returns:
        동기화 결과 (synced_files, new_versions, failed_files)
    """
    from app.services.lh_notice_loader import get_notice_loader
    
    try:
        print(f"\n{'='*60}")
        print(f"📥 LH 공고문 동기화 시작")
        print(f"{'='*60}\n")
        
        loader = get_notice_loader()
        results = await loader.sync_from_drive()
        
        print(f"\n{'='*60}")
        print(f"✅ LH 공고문 동기화 완료")
        print(f"   동기화: {results.get('synced_files', 0)}개")
        print(f"   신규 버전: {len(results.get('new_versions', []))}개")
        print(f"   실패: {len(results.get('failed_files', []))}개")
        print(f"{'='*60}\n")
        
        return results
        
    except Exception as e:
        print(f"❌ LH 공고문 동기화 오류: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "error_code": "SYNC_ERROR",
                "message": "LH 공고문 동기화 중 오류가 발생했습니다.",
                "details": str(e) if settings.debug else None
            }
        )


@app.get("/api/lh-notices/list")
async def list_lh_notices():
    """
    ✨ v5.0: 처리된 LH 공고문 목록 조회 API
    
    Returns:
        처리된 공고문 목록
    """
    from app.services.lh_notice_loader import get_notice_loader
    
    try:
        loader = get_notice_loader()
        notices = loader.list_processed_notices()
        
        return {
            "status": "success",
            "total": len(notices),
            "notices": notices
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e)
            }
        )


@app.get("/api/lh-notices/{version_id}")
async def get_lh_notice_rules(version_id: str):
    """
    ✨ v5.0: 특정 버전의 LH 규칙 조회 API
    
    Args:
        version_id: 버전 ID (예: "2024_8차")
        
    Returns:
        LH 규칙 데이터
    """
    from app.services.lh_notice_loader import get_notice_loader
    
    try:
        loader = get_notice_loader()
        rules = loader.get_notice_rules(version_id)
        
        if not rules:
            raise HTTPException(
                status_code=404,
                detail={
                    "status": "error",
                    "message": f"규칙을 찾을 수 없습니다: {version_id}"
                }
            )
        
        return {
            "status": "success",
            "version_id": version_id,
            "rules": rules
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e)
            }
        )


@app.get("/api/dashboard-data")
async def get_dashboard_data(analysis_id: Optional[str] = None):
    """
    ✨ v5.0: 대시보드 데이터 API
    
    Chart.js, Leaflet, Mapbox GL JS용 대시보드 데이터를 반환합니다.
    
    Args:
        analysis_id: 분석 ID (선택사항, 현재는 사용하지 않음)
        
    Returns:
        대시보드 데이터 (chart_co