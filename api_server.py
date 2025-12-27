"""
ZeroSite v4.0 API Server
=========================

FastAPI 기반 REST API 서버

Author: ZeroSite API Team
Date: 2025-12-27
Version: 1.0
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import sys
from pathlib import Path
import asyncio
from datetime import datetime
import uuid

# Add app to path
app_dir = Path(__file__).parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from app.core.context.canonical_land import CanonicalLandContext
from app.modules.m2_appraisal.service import AppraisalService
from app.modules.m3_lh_demand.service import LHDemandService
from app.modules.m4_capacity.service_v2 import CapacityServiceV2
from app.modules.m5_feasibility.service import FeasibilityService
from app.modules.m6_lh_review.service_v3 import LHReviewServiceV3
from app.modules.m9_lh_proposal.proposal_generator import LHProposalGenerator
from app.modules.m8_comparison.comparison_engine import MultiSiteComparisonEngine
from app.modules.visualization.chart_generator import ChartGenerator

# FastAPI 앱 초기화
app = FastAPI(
    title="ZeroSite v4.0 API",
    description="LH 매입임대주택 사업 타당성 분석 API",
    version="4.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & Templates
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 분석 작업 저장소 (메모리)
analysis_jobs = {}
comparison_jobs = {}


# ==================== Pydantic Models ====================

class LandInfoRequest(BaseModel):
    """토지 정보 입력 모델"""
    parcel_id: str
    address: str
    road_address: Optional[str] = None
    sido: str
    sigungu: str
    dong: str
    area_sqm: float
    area_pyeong: float
    zone_type: str
    far: float
    bcr: float
    road_width: float
    asking_price: Optional[float] = None


class AnalysisResponse(BaseModel):
    """분석 결과 응답 모델"""
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    progress: int  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class ComparisonRequest(BaseModel):
    """다중 부지 비교 요청"""
    sites: List[LandInfoRequest]
    comparison_name: str


# ==================== Helper Functions ====================

def create_land_context(land_info: LandInfoRequest) -> CanonicalLandContext:
    """LandInfoRequest → CanonicalLandContext 변환"""
    return CanonicalLandContext(
        parcel_id=land_info.parcel_id,
        address=land_info.address,
        road_address=land_info.road_address or land_info.address,
        coordinates=(37.5, 127.0),  # 기본값 (실제로는 주소 → 좌표 변환 필요)
        sido=land_info.sido,
        sigungu=land_info.sigungu,
        dong=land_info.dong,
        area_sqm=land_info.area_sqm,
        area_pyeong=land_info.area_pyeong,
        land_category="대",
        land_use="주거용",
        zone_type=land_info.zone_type,
        zone_detail="",
        far=land_info.far,
        bcr=land_info.bcr,
        road_width=land_info.road_width,
        road_type="중로",
        terrain_height="평지",
        terrain_shape="정형",
        regulations={},
        restrictions=[],
        data_source="API Input",
        retrieval_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


async def run_full_analysis_async(
    job_id: str,
    land_ctx: CanonicalLandContext,
    asking_price: Optional[float]
):
    """비동기 전체 분석 실행"""
    try:
        analysis_jobs[job_id]["status"] = "processing"
        analysis_jobs[job_id]["progress"] = 10
        
        # M2: 감정평가
        m2_service = AppraisalService(use_enhanced_services=True)
        m2_result = m2_service.run(land_ctx, asking_price=asking_price)
        analysis_jobs[job_id]["progress"] = 30
        
        # M3: 세대 유형
        m3_service = LHDemandService()
        m3_result = m3_service.run(land_ctx)
        analysis_jobs[job_id]["progress"] = 50
        
        # M4: 건축 규모
        m4_service = CapacityServiceV2()
        m4_result = m4_service.run(land_ctx, m3_result)
        analysis_jobs[job_id]["progress"] = 70
        
        # M5: 사업성
        m5_service = FeasibilityService()
        m5_result = m5_service.run(m2_result, m4_result)
        analysis_jobs[job_id]["progress"] = 85
        
        # M6: LH 종합 평가
        m6_service = LHReviewServiceV3()
        m6_result = m6_service.run(
            land_ctx=land_ctx,
            appraisal_ctx=m2_result,
            housing_type_ctx=m3_result,
            capacity_ctx=m4_result,
            feasibility_ctx=m5_result
        )
        analysis_jobs[job_id]["progress"] = 100
        
        # 결과 저장
        analysis_jobs[job_id]["status"] = "completed"
        analysis_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        analysis_jobs[job_id]["result"] = {
            "land_info": {
                "address": land_ctx.address,
                "parcel_id": land_ctx.parcel_id,
                "area_sqm": land_ctx.area_sqm,
                "area_pyeong": land_ctx.area_pyeong,
                "zone_type": land_ctx.zone_type
            },
            "appraisal": {
                "land_value": m2_result.land_value,
                "unit_price_sqm": m2_result.unit_price_sqm,
                "unit_price_pyeong": m2_result.unit_price_pyeong,
                "confidence_level": m2_result.confidence_level
            },
            "housing_type": {
                "selected_type": m3_result.selected_type_name,
                "confidence": m3_result.selection_confidence,
                "demand_prediction": m3_result.demand_prediction
            },
            "capacity": {
                "legal_units": m4_result.legal_capacity.total_units,
                "incentive_units": m4_result.incentive_capacity.total_units,
                "legal_far": m4_result.input_legal_far,
                "incentive_far": m4_result.input_incentive_far
            },
            "feasibility": {
                "total_cost": m5_result.cost_breakdown.total_cost,
                "total_revenue": m5_result.revenue_projection.total_revenue,
                "npv": m5_result.financial_metrics.npv_public,
                "irr": m5_result.financial_metrics.irr_public,
                "profitability_grade": m5_result.profitability_grade
            },
            "lh_review": {
                "judgement": m6_result.judgement.value,
                "lh_score_total": m6_result.lh_score_total,
                "grade": m6_result.grade.value,
                "fatal_reject": m6_result.fatal_reject,
                "section_scores": {
                    "A": m6_result.section_a_policy.weighted_score,
                    "B": m6_result.section_b_location.weighted_score,
                    "C": m6_result.section_c_construction.weighted_score,
                    "D": m6_result.section_d_price.weighted_score,
                    "E": m6_result.section_e_business.weighted_score
                },
                "improvement_points": m6_result.improvement_points
            }
        }
        
        # 차트 생성
        chart_gen = ChartGenerator(output_dir=f"output/api/charts/{job_id}")
        
        # LH 점수표 차트
        lh_chart = chart_gen.generate_lh_scorecard_chart(
            section_scores=analysis_jobs[job_id]["result"]["lh_review"]["section_scores"],
            total_score=m6_result.lh_score_total,
            file_name="lh_scorecard.png"
        )
        
        # 재무 차트
        financial_chart = chart_gen.generate_financial_chart(
            cost_breakdown={
                "토지매입": m5_result.cost_breakdown.land_acquisition_cost,
                "건축": m5_result.cost_breakdown.construction_cost,
                "설계": m5_result.cost_breakdown.design_cost,
                "간접": m5_result.cost_breakdown.indirect_cost,
                "금융": m5_result.cost_breakdown.financing_cost,
                "예비": m5_result.cost_breakdown.contingency
            },
            revenue_projection={
                "LH매입": m5_result.revenue_projection.lh_purchase_price,
                "민간분양": m5_result.revenue_projection.private_sale_revenue,
                "임대수익": m5_result.revenue_projection.rental_income_annual
            },
            npv=m5_result.financial_metrics.npv_public,
            irr=m5_result.financial_metrics.irr_public,
            file_name="financial.png"
        )
        
        analysis_jobs[job_id]["result"]["charts"] = {
            "lh_scorecard": lh_chart,
            "financial": financial_chart
        }
        
    except Exception as e:
        analysis_jobs[job_id]["status"] = "failed"
        analysis_jobs[job_id]["error"] = str(e)
        analysis_jobs[job_id]["completed_at"] = datetime.now().isoformat()


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "name": "ZeroSite v4.0 API",
        "version": "4.0.0",
        "status": "running",
        "endpoints": {
            "analyze": "POST /api/v1/analyze",
            "status": "GET /api/v1/status/{job_id}",
            "result": "GET /api/v1/result/{job_id}",
            "compare": "POST /api/v1/compare",
            "download": "GET /api/v1/download/{job_id}"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_site(
    land_info: LandInfoRequest,
    background_tasks: BackgroundTasks
):
    """
    단일 부지 분석 시작
    
    비동기로 M2→M6 파이프라인 실행
    """
    job_id = str(uuid.uuid4())
    
    # 작업 등록
    analysis_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "message": "분석 대기 중...",
        "created_at": datetime.now().isoformat(),
        "land_info": land_info.dict()
    }
    
    # 백그라운드 작업 시작
    land_ctx = create_land_context(land_info)
    background_tasks.add_task(
        run_full_analysis_async,
        job_id,
        land_ctx,
        land_info.asking_price
    )
    
    return AnalysisResponse(
        job_id=job_id,
        status="pending",
        message="분석이 시작되었습니다.",
        progress=0,
        created_at=analysis_jobs[job_id]["created_at"]
    )


@app.get("/api/v1/status/{job_id}", response_model=AnalysisResponse)
async def get_analysis_status(job_id: str):
    """
    분석 작업 상태 조회
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    job = analysis_jobs[job_id]
    
    return AnalysisResponse(
        job_id=job_id,
        status=job["status"],
        message=f"진행률: {job['progress']}%",
        progress=job["progress"],
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        error=job.get("error")
    )


@app.get("/api/v1/result/{job_id}")
async def get_analysis_result(job_id: str):
    """
    분석 결과 조회
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    job = analysis_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"분석이 아직 완료되지 않았습니다. 현재 상태: {job['status']}"
        )
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "result": job["result"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"]
    }


@app.get("/api/v1/chart/{job_id}/{chart_type}")
async def get_chart(job_id: str, chart_type: str):
    """
    차트 이미지 조회
    
    chart_type: "lh_scorecard", "financial", "capacity"
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    job = analysis_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="분석이 완료되지 않았습니다.")
    
    charts = job["result"].get("charts", {})
    
    if chart_type not in charts:
        raise HTTPException(status_code=404, detail="차트를 찾을 수 없습니다.")
    
    chart_path = charts[chart_type]
    
    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="차트 파일이 없습니다.")
    
    return FileResponse(
        chart_path,
        media_type="image/png",
        filename=f"{chart_type}.png"
    )


@app.get("/api/v1/jobs")
async def list_jobs():
    """
    모든 분석 작업 목록
    """
    jobs_list = []
    
    for job_id, job in analysis_jobs.items():
        jobs_list.append({
            "job_id": job_id,
            "status": job["status"],
            "progress": job["progress"],
            "address": job.get("land_info", {}).get("address", "N/A"),
            "created_at": job["created_at"],
            "completed_at": job.get("completed_at")
        })
    
    # 최신순 정렬
    jobs_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "total": len(jobs_list),
        "jobs": jobs_list
    }


@app.delete("/api/v1/job/{job_id}")
async def delete_job(job_id: str):
    """
    분석 작업 삭제
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    del analysis_jobs[job_id]
    
    return {"message": "작업이 삭제되었습니다.", "job_id": job_id}


# ==================== HTML Routes ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """대시보드 페이지"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "active_page": "dashboard"
    })


@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    """단일 분석 페이지"""
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "active_page": "analysis"
    })


@app.get("/result/{job_id}", response_class=HTMLResponse)
async def result_page(request: Request, job_id: str):
    """분석 결과 페이지"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    
    return templates.TemplateResponse("result.html", {
        "request": request,
        "job_id": job_id
    })


@app.get("/comparison", response_class=HTMLResponse)
async def comparison_page(request: Request):
    """다중 부지 비교 페이지"""
    return templates.TemplateResponse("comparison.html", {
        "request": request,
        "active_page": "comparison"
    })


@app.get("/map", response_class=HTMLResponse)
async def map_page(request: Request):
    """지도 보기 페이지"""
    return templates.TemplateResponse("map.html", {
        "request": request,
        "active_page": "map"
    })


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """보고서 목록 페이지"""
    return templates.TemplateResponse("reports.html", {
        "request": request,
        "active_page": "reports"
    })


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*80)
    print("  ZeroSite v4.0 API Server Starting...")
    print("  http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
