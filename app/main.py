"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uuid
from datetime import datetime

from app.config import get_settings
from app.schemas import (
    LandAnalysisRequest,
    LandAnalysisResponse,
    ErrorResponse
)
from app.services.analysis_engine import AnalysisEngine

settings = get_settings()


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


@app.get("/")
async def root():
    """헬스 체크"""
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
    - **unit_type**: 세대 유형 ("청년형", "신혼부부형", "고령자형")
    
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
        print(f"🏠 유형: {request.unit_type}")
        print()
        
        # 분석 엔진 실행
        engine = AnalysisEngine()
        result = await engine.analyze_land(request)
        
        # 응답 생성
        response = LandAnalysisResponse(
            status="success",
            analysis_id=analysis_id,
            address=request.address,
            land_area=request.land_area,
            unit_type=request.unit_type,
            coordinates=result["coordinates"],
            zone_info=result["zone_info"],
            building_capacity=result["building_capacity"],
            risk_factors=result["risk_factors"],
            demographic_info=result["demographic_info"],
            demand_analysis=result["demand_analysis"],
            summary=result["summary"],
            report_text=None,  # AI 생성은 추후 구현
            pdf_url=f"/api/reports/{analysis_id}.pdf",
            created_at=datetime.now()
        )
        
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
