"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
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
from app.services.sheets_service import get_sheets_service
from app.services.lh_notice_loader import LHNoticeLoader
from app.services.dashboard_builder import DashboardBuilder

# ✨ v7.2: Import new Report Engine v7.2 router
from app.routers.report_v7_2 import router as report_v72_router

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
    print("🚀 LH 토지진단 시스템 시작")
    print(f"📍 환경: {'개발' if settings.debug else '운영'}")
    print(f"🔑 API Keys 로드됨")
    yield
    print("👋 시스템 종료")


app = FastAPI(
    title="LH 신축매입임대 토지진단 자동화 시스템",
    description="LH 신축매입임대주택 사업을 위한 토지 적합성 자동 진단 API",
    version="1.0.0",
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

# ✨ v7.2: Include Report Engine v7.2 router
app.include_router(report_v72_router)

# 정적 파일 서빙
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """메인 페이지 - 웹 인터페이스"""
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
    """상세 헬스 체크"""
    return {
        "status": "healthy",
        "apis": {
            "kakao": "configured" if settings.kakao_rest_api_key else "missing",
            "land_regulation": "configured" if settings.land_regulation_api_key else "missing",
            "mois": "configured" if settings.mois_api_key else "missing"
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
            all_results = []
            
            # 공통 데이터 (좌표, 용도지역 등)는 한 번만 조회
            temp_request = LandAnalysisRequest(
                address=request.address,
                land_area=request.land_area,
                unit_type=UnitType.YOUTH,
                zone_type=request.zone_type,
                land_status=request.land_status,
                land_appraisal_price=request.land_appraisal_price
            )
            first_result = await engine.analyze_land(temp_request)
            
            # 각 유형별로 수요 점수만 재계산
            for unit_type in all_types:
                print(f"  ├─ {unit_type.value} 분석중...")
                type_request = LandAnalysisRequest(
                    address=request.address,
                    land_area=request.land_area,
                    unit_type=unit_type,
                    zone_type=request.zone_type,
                    land_status=request.land_status,
                    land_appraisal_price=request.land_appraisal_price
                )
                type_result = await engine.analyze_land(type_request)
                
                # 유형별 정보 저장
                housing_info = HOUSING_TYPE_INFO.get(unit_type.value, {})
                demand_analysis = type_result["demand_analysis"]
                # DemandAnalysis 객체에서 demand_score 추출
                demand_score = demand_analysis.demand_score if hasattr(demand_analysis, 'demand_score') else demand_analysis.get("demand_score", 0)
                
                all_results.append({
                    "unit_type": unit_type.value,
                    "score": demand_score,
                    "size": housing_info.get("size", "N/A"),
                    "result": type_result
                })
            
            # 점수 순으로 정렬
            all_results.sort(key=lambda x: x["score"], reverse=True)
            
            # 최고 점수 유형 선택
            best_result = all_results[0]
            recommended_type = best_result["unit_type"]
            result = best_result["result"]
            
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
        대시보드 데이터 (chart_configs, map_data, statistics)
    """
    from app.services.dashboard_builder import get_dashboard_builder
    
    # 실제 구현에서는 analysis_id로 저장된 분석 결과를 가져와야 함
    # 현재는 예시 데이터 반환
    
    try:
        builder = get_dashboard_builder()
        
        # 예시 분석 결과 (실제로는 DB나 캐시에서 가져옴)
        example_result = {
            "type_demand_scores": {
                "청년": 88.5,
                "신혼·신생아 I": 85.2,
                "신혼·신생아 II": 83.7,
                "다자녀": 87.3,
                "고령자": 82.1
            },
            "grade_info": {
                "category_scores": {
                    "입지": 85.0,
                    "규모": 72.0,
                    "사업성": 80.0,
                    "법규": 90.0
                }
            },
            "coordinates": {
                "latitude": 37.5665,
                "longitude": 126.9780
            },
            "geo_optimization": {
                "analyzed_location": {
                    "latitude": 37.5665,
                    "longitude": 126.9780,
                    "address": "서울특별시 마포구 월드컵북로 120"
                },
                "optimization_score": 78.5,
                "recommended_sites": []
            },
            "summary": {
                "is_eligible": True
            }
        }
        
        dashboard_data = builder.build_dashboard(example_result)
        
        return {
            "status": "success",
            "dashboard_data": dashboard_data.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e)
            }
        )


@app.post("/api/generate-report")
async def generate_professional_report(request: LandAnalysisRequest):
    """
    전문가급 감정평가 보고서 생성 API (A4 10장 이상)
    
    Args:
        request: 토지 분석 요청
        
    Returns:
        HTML 형식의 전문가급 보고서 (지도 이미지 포함)
    """
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        print(f"\n📄 전문가급 감정평가 보고서 생성 요청 [ID: {analysis_id}]")
        print(f"🏠 유형: {request.unit_type}")
        
        # 분석 실행
        engine = AnalysisEngine()
        result = await engine.analyze_land(request)
        
        # 지도 이미지 생성 (여러 스케일)
        from app.services.kakao_service import KakaoService
        kakao_service = KakaoService()
        
        coords = result.get("coordinates")
        map_images = None
        if coords:
            print("🗺️ 지도 이미지 생성 중 (여러 스케일)...")
            map_images = await kakao_service.get_multiple_maps(coords)
            
            if map_images:
                generated_count = sum(1 for v in map_images.values() if v)
                print(f"✅ 지도 이미지 생성 완료 ({generated_count}개)")
            else:
                print("⚠️ 지도 이미지 생성 실패 (보고서는 계속 생성됨)")
        
        # unit_type 결정 (자동 분석인 경우 추천 유형 사용)
        final_unit_type = request.unit_type
        if not final_unit_type:
            # 자동 분석인 경우: 7개 유형 중 최고 점수 유형으로 재분석
            from app.schemas import UnitType
            all_types = list(UnitType)
            all_scores = []
            
            for unit_type in all_types:
                temp_request = LandAnalysisRequest(
                    address=request.address,
                    land_area=request.land_area,
                    unit_type=unit_type,
                    zone_type=request.zone_type,
                    land_status=request.land_status,
                    land_appraisal_price=request.land_appraisal_price
                )
                temp_result = await engine.analyze_land(temp_request)
                demand_analysis = temp_result["demand_analysis"]
                demand_score = demand_analysis.demand_score if hasattr(demand_analysis, 'demand_score') else demand_analysis.get("demand_score", 0)
                all_scores.append({
                    "unit_type": unit_type,
                    "score": demand_score,
                    "result": temp_result
                })
            
            # 최고 점수 유형 선택
            all_scores.sort(key=lambda x: x["score"], reverse=True)
            final_unit_type = all_scores[0]["unit_type"]
            result = all_scores[0]["result"]
            print(f"✅ 추천 유형 선택: {final_unit_type.value} ({all_scores[0]['score']:.1f}점)")
        
        # 분석 데이터 구성 (지도 이미지 포함)
        analysis_data = {
            "analysis_id": analysis_id,
            "address": request.address,
            "land_area": request.land_area,
            "unit_type": final_unit_type.value if hasattr(final_unit_type, 'value') else final_unit_type,  # Enum을 문자열로 변환
            "land_appraisal_price": request.land_appraisal_price,  # 사용자 입력 감정평가액
            "land_status": request.land_status,  # 종전 대지 이용상태
            "zone_type_manual": request.zone_type,  # 수동 선택 용도지역
            "coordinates": result["coordinates"],
            "zone_info": result["zone_info"],
            "building_capacity": result["building_capacity"],
            "risk_factors": result["risk_factors"],
            "demographic_info": result["demographic_info"],
            "demand_analysis": result["demand_analysis"],
            "summary": result["summary"],
            "map_images": map_images  # 여러 스케일의 지도 이미지 (overview, detail, close)
        }
        
        # LH 공식 양식 보고서 생성 (HTML)
        print("📝 LH 공식 양식 보고서 생성 중...")
        lh_generator = LHOfficialReportGenerator()
        report_html = lh_generator.generate_official_report(analysis_data)
        
        print(f"✅ 전문가급 감정평가 보고서 생성 완료 [ID: {analysis_id}]")
        print(f"📊 보고서 크기: {len(report_html):,} bytes")
        print()
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "report": report_html,
            "format": "html",
            "generated_at": datetime.now().isoformat(),
            "has_map_image": map_images is not None
        }
        
    except Exception as e:
        print(f"❌ 보고서 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "보고서 생성 중 오류가 발생했습니다.",
                "details": str(e) if settings.debug else None
            }
        )


@app.post("/api/generate-google-docs")
async def generate_google_docs_report(request: LandAnalysisRequest):
    """
    Google Docs 보고서 생성 API
    
    Args:
        request: 토지 분석 요청
        
    Returns:
        Google Docs URL 및 문서 정보
    """
    analysis_id = str(uuid.uuid4())[:8]
    
    try:
        print(f"\n📄 Google Docs 보고서 생성 요청 [ID: {analysis_id}]")
        
        # 1. 먼저 HTML 보고서 생성
        engine = AnalysisEngine()
        result = await engine.analyze_land(request)
        
        # 지도 이미지 생성
        from app.services.kakao_service import KakaoService
        kakao_service = KakaoService()
        
        coords = result.get("coordinates")
        map_images = None
        if coords:
            map_images = await kakao_service.get_multiple_maps(coords)
        
        # unit_type 결정
        final_unit_type = request.unit_type
        if not final_unit_type:
            from app.schemas import UnitType
            all_types = list(UnitType)
            all_scores = []
            
            for unit_type in all_types:
                temp_request = LandAnalysisRequest(
                    address=request.address,
                    land_area=request.land_area,
                    unit_type=unit_type,
                    zone_type=request.zone_type,
                    land_status=request.land_status,
                    land_appraisal_price=request.land_appraisal_price,
                    consultant=request.consultant
                )
                temp_result = await engine.analyze_land(temp_request)
                demand_analysis = temp_result["demand_analysis"]
                demand_score = demand_analysis.demand_score if hasattr(demand_analysis, 'demand_score') else demand_analysis.get("demand_score", 0)
                all_scores.append({
                    "unit_type": unit_type,
                    "score": demand_score,
                    "result": temp_result
                })
            
            all_scores.sort(key=lambda x: x["score"], reverse=True)
            final_unit_type = all_scores[0]["unit_type"]
            result = all_scores[0]["result"]
        
        # 분석 데이터 구성
        analysis_data = {
            "analysis_id": analysis_id,
            "address": request.address,
            "land_area": request.land_area,
            "unit_type": final_unit_type.value if hasattr(final_unit_type, 'value') else final_unit_type,
            "land_appraisal_price": request.land_appraisal_price,
            "land_status": request.land_status,
            "zone_type_manual": request.zone_type,
            "consultant": request.consultant.dict() if request.consultant else None,
            "coordinates": result["coordinates"],
            "zone_info": result["zone_info"],
            "building_capacity": result["building_capacity"],
            "risk_factors": result["risk_factors"],
            "demographic_info": result["demographic_info"],
            "demand_analysis": result["demand_analysis"],
            "summary": result["summary"],
            "map_images": map_images
        }
        
        # HTML 보고서 생성
        lh_generator = LHOfficialReportGenerator()
        report_html = lh_generator.generate_official_report(analysis_data)
        
        # 2. Google Docs로 변환
        print("📝 Google Docs 문서 생성 중...")
        from app.services.google_docs_service import get_google_docs_service
        
        docs_service = get_google_docs_service()
        
        if not docs_service.enabled:
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "error",
                    "message": "Google Docs 서비스가 활성화되지 않았습니다. credentials를 확인하세요."
                }
            )
        
        docs_result = docs_service.save_report_to_docs(
            analysis_data=analysis_data,
            html_content=report_html
        )
        
        if not docs_result:
            raise HTTPException(
                status_code=500,
                detail={
                    "status": "error",
                    "message": "Google Docs 문서 생성에 실패했습니다."
                }
            )
        
        print(f"✅ Google Docs 보고서 생성 완료")
        print(f"   URL: {docs_result['document_url']}")
        
        return {
            "status": "success",
            "analysis_id": analysis_id,
            "google_docs": docs_result,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Google Docs 생성 오류: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Google Docs 생성 중 오류가 발생했습니다.",
                "details": str(e) if settings.debug else None
            }
        )


@app.get("/api/reports/{analysis_id}")
async def get_report(analysis_id: str):
    """
    분석 보고서 조회
    
    Args:
        analysis_id: 분석 ID
        
    Returns:
        분석 보고서 정보
    """
    # TODO: 데이터베이스에서 저장된 분석 결과 조회
    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "보고서 생성 기능은 추후 구현 예정입니다."
    }


@app.post("/api/test-kakao")
async def test_kakao_api(address: str):
    """카카오 API 테스트"""
    from app.services.kakao_service import KakaoService
    
    service = KakaoService()
    coords = await service.address_to_coordinates(address)
    
    if coords:
        facilities = await service.analyze_location_accessibility(coords)
        return {
            "success": True,
            "coordinates": coords,
            "accessibility": facilities
        }
    
    return {"success": False, "message": "주소를 찾을 수 없습니다."}


@app.post("/api/test-land-regulation")
async def test_land_regulation_api(lat: float, lon: float):
    """토지규제 API 테스트"""
    from app.services.land_regulation_service import LandRegulationService
    from app.schemas import Coordinates
    
    service = LandRegulationService()
    coords = Coordinates(latitude=lat, longitude=lon)
    result = await service.get_comprehensive_land_info(coords)
    
    return {
        "success": True,
        "data": {
            "zone_info": result["zone_info"],
            "restrictions": result["restrictions"],
            "is_developable": result["is_developable"]
        }
    }


@app.post("/api/test-mois")
async def test_mois_api(address: str):
    """행정안전부 API 테스트"""
    from app.services.mois_service import MOISService
    from app.schemas import Coordinates
    
    service = MOISService()
    coords = Coordinates(latitude=37.5, longitude=127.0)  # 임시 좌표
    result = await service.analyze_demographics(address, coords)
    
    return {
        "success": True,
        "demographic_info": result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
