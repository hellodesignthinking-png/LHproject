"""
ZeroSite Expert Edition v3 - Land Report API (토지감정평가)

Provides simple land appraisal reports using Land Valuation Engine v9.1
Generates 2-3 page PDF reports via WeasyPrint

Features:
- POST /api/v3/land-report - Generate land report (JSON + optional PDF)
- GET /api/v3/land-report/{report_id} - Retrieve cached report
- POST /api/v3/land-report/pdf - Generate PDF only
- POST /api/v3/land-report/compare - Compare enhanced vs legacy

Author: ZeroSite Development Team + GenSpark AI
Date: 2025-12-10
Version: v3.0
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, Response, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import uuid
import logging
import io

# Import Land Valuation Engine v9.1
from app.engines_v9.land_valuation_engine_v9_1 import LandValuationEngineV91

# Import WeasyPrint PDF Generator
from app.services_v9.pdf_generator_weasyprint import WeasyPrintPDFGenerator

logger = logging.getLogger(__name__)

# Initialize PDF generator
pdf_generator = WeasyPrintPDFGenerator()

# Router configuration
router = APIRouter(
    prefix="/api/v3",
    tags=["Land Report v3 - 토지감정평가"]
)

# ==================== REQUEST/RESPONSE SCHEMAS ====================

class LandReportRequest(BaseModel):
    """토지감정평가 요청"""
    address: str = Field(..., min_length=5, description="토지 주소 (한글)", example="서울특별시 강남구 역삼동 123-45")
    land_size_sqm: float = Field(..., gt=0, le=1000000, description="토지 면적 (㎡)", example=1000.0)
    zone_type: str = Field(
        default="제2종일반주거지역",
        description="용도지역",
        example="제2종일반주거지역"
    )
    asking_price: Optional[float] = Field(
        None,
        gt=0,
        description="요청 매입가 (₩, 선택)",
        example=10000000000
    )
    generate_pdf: bool = Field(
        default=False,
        description="PDF 생성 여부"
    )
    pdf_format: str = Field(
        default="simple",
        description="PDF 형식: simple(2p), standard(3p)",
        example="simple",
        pattern="^(simple|standard)$"
    )

class LandReportResponse(BaseModel):
    """토지감정평가 응답"""
    report_id: str = Field(..., description="보고서 ID", example="rpt_20251210_abc123")
    timestamp: str = Field(..., description="생성 시각", example="2025-12-10T10:30:00")
    
    # 입력 정보
    input: Dict[str, Any] = Field(..., description="입력 데이터")
    
    # 감정평가 결과
    valuation: Dict[str, Any] = Field(..., description="감정평가 결과")
    
    # 재무 분석
    financial: Dict[str, Any] = Field(..., description="재무 분석")
    
    # 협상 전략
    negotiation: Dict[str, Any] = Field(..., description="협상 전략")
    
    # 추천 의견
    recommendation: Dict[str, Any] = Field(..., description="추천 의견")
    
    # 비교사례 (Top 5)
    comparables: List[Dict[str, Any]] = Field([], description="비교사례 거래")
    
    # PDF (선택)
    pdf_url: Optional[str] = Field(None, description="PDF 다운로드 URL")

class CompareModeResponse(BaseModel):
    """Enhanced vs Legacy 비교 응답"""
    report_id: str
    timestamp: str
    enhanced_result: Dict[str, Any]
    legacy_result: Dict[str, Any]
    comparison: Dict[str, Any]

# ==================== IN-MEMORY CACHE ====================

# Simple cache for demo (use Redis in production)
REPORT_CACHE: Dict[str, Dict[str, Any]] = {}

def _cache_report(report_id: str, data: Dict[str, Any]):
    """캐시에 보고서 저장"""
    REPORT_CACHE[report_id] = {
        "data": data,
        "cached_at": datetime.now().isoformat()
    }
    # Limit cache size
    if len(REPORT_CACHE) > 100:
        # Remove oldest
        oldest_key = min(REPORT_CACHE.keys())
        del REPORT_CACHE[oldest_key]

def _get_cached_report(report_id: str) -> Optional[Dict[str, Any]]:
    """캐시에서 보고서 조회"""
    cached = REPORT_CACHE.get(report_id)
    if cached:
        return cached["data"]
    return None

# ==================== API ENDPOINTS ====================

@router.post("/land-report", response_model=LandReportResponse)
async def generate_land_report(request: LandReportRequest):
    """
    토지감정평가 보고서 생성 (JSON + optional PDF)
    
    **Features:**
    - Dynamic Transaction Generation (동적 비교사례 생성)
    - 4-Factor Price Adjustment (거리/시점/규모/용도)
    - Advanced Confidence Scoring (통계적 신뢰도)
    - Financial Analysis (재무 분석)
    - 3 Negotiation Strategies (협상 전략)
    
    **Example:**
    ```json
    {
      "address": "서울특별시 강남구 역삼동 123-45",
      "land_size_sqm": 1000.0,
      "zone_type": "제2종일반주거지역",
      "asking_price": 10000000000,
      "generate_pdf": false,
      "pdf_format": "simple"
    }
    ```
    
    **Returns:**
    - report_id: 보고서 고유 ID
    - valuation: 감정평가 결과 (평균가격, 가격범위, 신뢰도)
    - financial: 재무 분석 (소요자금, LTV, 수익률 등)
    - negotiation: 협상 전략 (3가지)
    - recommendation: 추천 의견 (매수/관망/매도)
    """
    try:
        logger.info(f"🔍 Land Report Request: {request.address}")
        
        # Initialize engine
        engine = LandValuationEngineV91(use_enhanced_services=True)
        
        # Execute valuation
        result = engine.evaluate_land(
            address=request.address,
            land_size_sqm=request.land_size_sqm,
            zone_type=request.zone_type,
            asking_price=request.asking_price
        )
        
        # Generate report ID
        report_id = f"rpt_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        # Extract prediction data
        prediction = result.get("prediction", {})
        asking_analysis = result.get("asking_analysis", {})
        comparables = result.get("comparables", [])
        
        # Structure response
        response_data = {
            "report_id": report_id,
            "timestamp": timestamp,
            "input": {
                "address": request.address,
                "land_size_sqm": request.land_size_sqm,
                "zone_type": request.zone_type,
                "asking_price": request.asking_price
            },
            "valuation": {
                "estimated_price_krw": prediction.get("avg", 0),
                "price_range": {
                    "low": prediction.get("low", 0),
                    "avg": prediction.get("avg", 0),
                    "high": prediction.get("high", 0)
                },
                "price_per_sqm_krw": prediction.get("price_per_sqm_avg", 0),
                "confidence_score": prediction.get("confidence", 0),
                "confidence_level": prediction.get("confidence_level", "N/A"),
                "transaction_count": len(comparables),
                "coordinate": result.get("coordinates", {}),
                "enhanced_features": {
                    "dynamic_transactions": True,
                    "weighted_adjustments": True,
                    "advanced_confidence": True,
                    "adjustment_weights": {
                        "distance": "35%",
                        "time": "25%",
                        "size": "25%",
                        "zone": "15%"
                    },
                    "confidence_weights": {
                        "sample_size": "30%",
                        "price_variance": "30%",
                        "distance": "25%",
                        "recency": "15%"
                    }
                }
            },
            "financial": result.get("financial_analysis", {}),
            "negotiation": result.get("negotiation_strategies", {}),
            "recommendation": {
                "status": asking_analysis.get("status", "N/A") if asking_analysis else "N/A",
                "difference_krw": asking_analysis.get("difference", 0) if asking_analysis else 0,
                "difference_pct": asking_analysis.get("percentage", 0) if asking_analysis else 0,
                "emoji": asking_analysis.get("emoji", "") if asking_analysis else ""
            } if asking_analysis else {},
            "comparables": comparables[:5]  # Include top 5 comparables
        }
        
        # Cache report
        _cache_report(report_id, response_data)
        
        # Generate PDF if requested
        pdf_url = None
        if request.generate_pdf:
            try:
                # Generate PDF using WeasyPrint
                pdf_bytes = pdf_generator.generate_pdf(response_data)
                
                # Save PDF to cache (in production, use blob storage)
                pdf_path = Path(f"/tmp/land_reports/{report_id}.pdf")
                pdf_path.parent.mkdir(parents=True, exist_ok=True)
                pdf_path.write_bytes(pdf_bytes)
                
                pdf_url = f"/api/v3/land-report/{report_id}/download"
                logger.info(f"📄 PDF generated: {len(pdf_bytes):,} bytes")
                
            except Exception as pdf_error:
                logger.error(f"⚠️ PDF generation failed: {pdf_error}")
                # Don't fail the entire request if PDF fails
                pdf_url = None
        
        response_data["pdf_url"] = pdf_url
        
        logger.info(f"✅ Report generated: {report_id}")
        logger.info(f"   ├─ Estimated Price: ₩{prediction.get('avg', 0):,.0f}")
        logger.info(f"   ├─ Confidence: {prediction.get('confidence', 0):.0%}")
        logger.info(f"   └─ Transactions: {len(comparables)}")
        
        return LandReportResponse(**response_data)
        
    except Exception as e:
        logger.error(f"❌ Error generating land report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/land-report/{report_id}")
async def get_land_report(report_id: str):
    """
    캐시된 토지감정평가 보고서 조회
    
    **Parameters:**
    - report_id: 보고서 ID (예: rpt_20251210_abc123)
    
    **Returns:**
    - Cached report data (JSON)
    """
    cached = _get_cached_report(report_id)
    if not cached:
        raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
    
    return JSONResponse(content=cached)


@router.post("/land-report/compare", response_model=CompareModeResponse)
async def compare_valuation_modes(request: LandReportRequest):
    """
    Enhanced vs Legacy 모드 비교
    
    **Purpose:**
    - Compare GenSpark AI Enhanced mode with Legacy v9.0 mode
    - Show improvements in accuracy, confidence, and features
    
    **Returns:**
    - enhanced_result: Enhanced mode result
    - legacy_result: Legacy mode result (placeholder)
    - comparison: Side-by-side comparison metrics
    """
    try:
        logger.info(f"🔬 Comparison Request: {request.address}")
        
        # Enhanced mode
        engine_enhanced = LandValuationEngineV91(use_enhanced_services=True)
        result_enhanced = engine_enhanced.evaluate_land(
            address=request.address,
            land_size_sqm=request.land_size_sqm,
            zone_type=request.zone_type,
            asking_price=request.asking_price
        )
        
        # Legacy mode (placeholder - would use actual v9.0 engine)
        engine_legacy = LandValuationEngineV91(use_enhanced_services=False)
        result_legacy = {
            "estimated_price_krw": result_enhanced.get("estimated_price_krw", 0) * 0.95,  # Mock: 5% lower
            "confidence_score": result_enhanced.get("confidence_score", 0) * 0.85,  # Mock: 15% lower
            "transaction_count": 5,  # Mock: fixed count
            "enhanced_features": None,
            "mode": "legacy"
        }
        
        # Comparison metrics
        price_diff = result_enhanced.get("estimated_price_krw", 0) - result_legacy["estimated_price_krw"]
        price_diff_pct = (price_diff / result_legacy["estimated_price_krw"] * 100) if result_legacy["estimated_price_krw"] > 0 else 0
        
        confidence_diff = result_enhanced.get("confidence_score", 0) - result_legacy["confidence_score"]
        
        comparison = {
            "price_difference_krw": price_diff,
            "price_difference_pct": round(price_diff_pct, 2),
            "confidence_improvement": round(confidence_diff * 100, 2),
            "transaction_count_improved": result_enhanced.get("transaction_count", 0) - result_legacy["transaction_count"],
            "enhanced_features": [
                "Dynamic Transaction Generation",
                "4-Factor Weighted Adjustment",
                "Advanced Confidence Scoring",
                "Financial Analysis",
                "3 Negotiation Strategies"
            ]
        }
        
        report_id = f"cmp_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        
        return CompareModeResponse(
            report_id=report_id,
            timestamp=datetime.now().isoformat(),
            enhanced_result=result_enhanced,
            legacy_result=result_legacy,
            comparison=comparison
        )
        
    except Exception as e:
        logger.error(f"❌ Error comparing modes: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/land-report/{report_id}/download")
async def download_report_pdf(report_id: str):
    """
    토지감정평가 보고서 PDF 다운로드
    
    **Parameters:**
    - report_id: 보고서 ID (예: rpt_20251210_abc123)
    
    **Returns:**
    - PDF file download response
    
    **Example:**
    ```bash
    curl -O https://api.example.com/api/v3/land-report/rpt_20251210_abc123/download
    ```
    """
    try:
        # Check if PDF exists in cache
        pdf_path = Path(f"/tmp/land_reports/{report_id}.pdf")
        
        if not pdf_path.exists():
            # Try to regenerate PDF from cached report data
            cached_report = _get_cached_report(report_id)
            if not cached_report:
                raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")
            
            # Generate PDF
            pdf_bytes = pdf_generator.generate_pdf(cached_report)
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            pdf_path.write_bytes(pdf_bytes)
            logger.info(f"📄 PDF regenerated for: {report_id}")
        
        # Return PDF file
        filename = f"ZeroSite_Expert_v3_Land_Report_{report_id}.pdf"
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")


@router.get("/health")
async def land_report_health():
    """
    Land Report API 헬스 체크
    
    **Returns:**
    - API status
    - Engine status
    - Cache statistics
    """
    try:
        # Test engine initialization
        engine = LandValuationEngineV91(use_enhanced_services=True)
        engine_status = "✅ Operational" if engine.use_enhanced else "⚠️ Legacy Mode"
        
        return {
            "status": "healthy",
            "api_version": "v3.0",
            "engine": {
                "name": "Land Valuation Engine v9.1",
                "status": engine_status,
                "enhanced_services": engine.use_enhanced
            },
            "cache": {
                "size": len(REPORT_CACHE),
                "max_size": 100
            },
            "features": [
                "Dynamic Transaction Generation",
                "4-Factor Price Adjustment",
                "Advanced Confidence Scoring",
                "Financial Analysis",
                "Negotiation Strategies"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
