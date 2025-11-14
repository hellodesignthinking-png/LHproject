"""
사업성 시뮬레이션 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException
from app.modules.business_simulation.models import (
    CostCalculationRequest,
    CostCalculationResponse,
    PurchaseSimulationRequest,
    PurchaseSimulationResponse,
    ROIAnalysisRequest,
    ROIAnalysisResponse,
    SensitivityAnalysisRequest,
    SensitivityAnalysisResponse,
    ComprehensiveAnalysisRequest,
    ComprehensiveAnalysisResponse
)
from app.modules.business_simulation.construction_cost import calculate_construction_cost
from app.modules.business_simulation.purchase_price import calculate_lh_purchase
from app.modules.business_simulation.roi_calculator import calculate_roi_irr
from app.modules.business_simulation.sensitivity import analyze_sensitivity
from app.modules.business_simulation.service import analyze_comprehensive

router = APIRouter(prefix="/api/business", tags=["business-simulation"])


@router.get("/")
async def business_home():
    """사업성 시뮬레이션 API 정보"""
    return {
        "message": "사업성 시뮬레이션 API",
        "version": "1.0.0",
        "endpoints": {
            "건축비 계산": "POST /api/business/calculate-cost",
            "LH 매입가 시뮬레이션": "POST /api/business/simulate-purchase",
            "ROI/IRR 분석": "POST /api/business/analyze-roi",
            "민감도 분석": "POST /api/business/analyze-sensitivity",
            "종합 사업성 분석": "POST /api/business/analyze-comprehensive"
        }
    }


@router.post("/calculate-cost", response_model=CostCalculationResponse)
async def calculate_cost(request: CostCalculationRequest):
    """
    건축비 자동 산정
    
    - **unit_type**: 주택 유형 (YOUTH/NEWLYWED/PUBLIC_RENTAL)
    - **gross_area**: 연면적 (㎡)
    - **region**: 지역명 (예: 서울특별시, 경기도)
    - **num_units**: 총 세대수
    - **num_floors**: 층수 (선택, 기본값 4)
    
    Returns:
        - 총 건축비
        - 평당 건축비
        - 공사 항목별 비용
        - 부대비용
        - 총 사업비
    """
    try:
        result = calculate_construction_cost(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"건축비 계산 오류: {str(e)}")


@router.post("/simulate-purchase", response_model=PurchaseSimulationResponse)
async def simulate_purchase(request: PurchaseSimulationRequest):
    """
    LH 매입가 시뮬레이션
    
    - **unit_type**: 주택 유형
    - **land_value**: 토지 감정평가액 (원)
    - **construction_cost**: 건축비 (원)
    - **gross_area**: 연면적 (㎡)
    - **num_units**: 총 세대수
    - **region**: 지역명
    - **custom_profit_rate**: 사용자 지정 이윤율 (선택, 0~20%)
    
    Returns:
        - LH 총 매입가
        - 적정이윤
        - ROI
        - 매입 기준 충족 여부
    """
    try:
        result = calculate_lh_purchase(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LH 매입가 시뮬레이션 오류: {str(e)}")


@router.post("/analyze-roi", response_model=ROIAnalysisResponse)
async def analyze_roi(request: ROIAnalysisRequest):
    """
    ROI/IRR 분석
    
    - **project_name**: 프로젝트 명
    - **land_acquisition_cost**: 토지 매입비 (원)
    - **construction_cost**: 건축비 (원)
    - **other_costs**: 기타 비용 (원, 선택)
    - **lh_purchase_price**: LH 매입가 (원)
    - **construction_duration_years**: 건축 기간 (년)
    - **lh_purchase_year**: LH 매입 시점 (년)
    
    Returns:
        - ROI (투자수익률)
        - IRR (내부수익률)
        - NPV (순현재가치)
        - 투자 회수 기간
        - 연도별 현금흐름
    """
    try:
        result = calculate_roi_irr(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ROI/IRR 분석 오류: {str(e)}")


@router.post("/analyze-sensitivity", response_model=SensitivityAnalysisResponse)
async def analyze_sensitivity_endpoint(request: SensitivityAnalysisRequest):
    """
    민감도 분석
    
    - **base_scenario**: 기본 시나리오 (ROIAnalysisRequest)
    - **variables**: 분석할 변수 목록 (land_price, construction_cost 등)
    - **variation_percentages**: 변동 비율 목록 (%, 예: [-20, -10, 0, 10, 20])
    
    Returns:
        - 시나리오별 ROI/IRR
        - 가장 민감한 변수
        - ROI 범위 (최소/최대)
    """
    try:
        result = analyze_sensitivity(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"민감도 분석 오류: {str(e)}")


@router.post("/analyze-comprehensive", response_model=ComprehensiveAnalysisResponse)
async def analyze_comprehensive_endpoint(request: ComprehensiveAnalysisRequest):
    """
    종합 사업성 분석 (원스톱 분석)
    
    - **project_name**: 프로젝트 명
    - **address**: 주소
    - **unit_type**: 주택 유형
    - **land_area**: 토지 면적 (㎡)
    - **land_price_per_sqm**: 토지 단가 (원/㎡)
    - **gross_area**: 연면적 (㎡)
    - **num_units**: 총 세대수
    - **region**: 지역명
    
    Returns:
        - 건축비 분석
        - LH 매입가 분석
        - ROI/IRR 분석
        - 종합 평가 (우수/양호/보통/미흡)
        - 권장 사항
        - 리스크 요인
    """
    try:
        result = analyze_comprehensive(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"종합 분석 오류: {str(e)}")


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "service": "business-simulation"}
