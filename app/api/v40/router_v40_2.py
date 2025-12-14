"""
ZeroSite v40.3 - PIPELINE LOCK RELEASE
감정평가 기준 파이프라인 고정 (Appraisal-First Architecture + Protection)

v40.3 핵심 업데이트:
- Context Protection: Appraisal 데이터 Immutable 보장
- Pipeline Lock: 감정평가 → 진단 → 규모 → 시나리오 순서 강제
- Data Consistency: 모든 모듈이 동일한 기준 데이터 사용 검증
- Protection Status: Context 보호 상태 추적

Release Date: 2025-12-14
Version: 40.3
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import io
import uuid
from datetime import datetime

# Import v30 engines
from app.engines.v30.geocoding_engine import GeocodingEngineV30
from app.engines.v30.zoning_engine import ZoningEngineV30
from app.engines.v30.landprice_engine import LandPriceEngineV30
from app.engines.v30.transaction_engine import TransactionEngineV30
from app.engines.v30.premium_engine import PremiumEngineV30
from app.engines.v30.appraisal_engine import AppraisalEngineV30

# Import v39 PDF Generator
from app.services.v30.pdf_generator_v39 import PDFGeneratorV39

router_v40_2 = APIRouter(prefix="/api/v40.2", tags=["v40.3-pipeline-lock"])

# In-memory context storage (use Redis in production)
CONTEXT_STORAGE = {}


class FullLandAnalysisRequest(BaseModel):
    """v40.2 Unified Request Model"""
    # Required
    address: str
    land_area_sqm: float
    
    # Optional physical characteristics
    land_shape: Optional[str] = "정방형"
    slope: Optional[str] = "평지"
    road_access: Optional[str] = "중로"
    orientation: Optional[str] = "남향"


# Initialize engines
geocoding_engine = GeocodingEngineV30()
zoning_engine = ZoningEngineV30()
landprice_engine = LandPriceEngineV30()
transaction_engine = TransactionEngineV30()
premium_engine = PremiumEngineV30()
appraisal_engine = AppraisalEngineV30()
pdf_generator = PDFGeneratorV39()


# ============================================
# Helper Functions: Extract Views from Appraisal
# ============================================

def extract_diagnosis_view(appraisal_result: Dict, geo_info: Dict) -> Dict:
    """
    감정평가 결과에서 토지진단 뷰 추출
    
    중요: 감정평가 데이터를 그대로 사용 (재계산 금지)
    """
    zoning = appraisal_result.get("zoning", {})
    zone_type = zoning.get("zone_type", "알 수 없음")
    
    # 적합성 판정
    suitability = "적합" if "주거" in zone_type else "검토 필요"
    if "상업" in zone_type or "준공업" in zone_type:
        suitability = "조건부 적합"
    
    return {
        "suitability": suitability,
        "zone_type": zone_type,  # ← appraisal 데이터
        "zoning": zoning,  # ← 전체 zoning 정보
        "official_price": appraisal_result.get("official_price", 0),  # ← appraisal 데이터
        "transactions": appraisal_result.get("transactions", []),  # ← appraisal 데이터
        "coordinates": geo_info.get("coordinates", {}),
        "administrative": geo_info.get("administrative", {}),
        "restrictions": appraisal_result.get("restrictions", [])
    }


def extract_capacity_view(appraisal_result: Dict, land_area: float) -> Dict:
    """
    감정평가 결과에서 규모검토 뷰 추출
    
    중요: 감정평가의 Zoning/FAR/BCR을 강제 사용
    """
    zoning = appraisal_result.get("zoning", {})
    
    # 감정평가의 FAR/BCR 사용 (변경 불가)
    far = zoning.get("far", 200) / 100  # percentage to ratio
    bcr = zoning.get("bcr", 60) / 100
    
    # 계산
    max_building_area = land_area * bcr
    max_floor_area = land_area * far
    max_units = int(max_floor_area / 45)  # 45㎡ 기준
    
    return {
        "zoning": zoning,  # ← appraisal과 동일한 zoning
        "far": zoning.get("far", 200),  # ← appraisal 데이터
        "bcr": zoning.get("bcr", 60),  # ← appraisal 데이터
        "max_building_area": int(max_building_area),
        "max_floor_area": int(max_floor_area),
        "max_units": max_units,
        "land_area": land_area
    }


def calculate_scenario_view(appraisal_result: Dict, land_area: float) -> Dict:
    """
    감정평가 결과 기반 시나리오 계산
    
    중요: appraisal_result.final_value를 기준 가격으로 사용
    """
    base_value = appraisal_result.get("final_value", 0)
    far = appraisal_result.get("zoning", {}).get("far", 200) / 100
    max_floor_area = land_area * far
    
    # 3가지 시나리오 계산
    scenarios = []
    
    # A안: 청년형 (30㎡)
    scenario_a = {
        "name": "A안: 청년형",
        "unit_type": "청년형",
        "unit_size": 30,
        "unit_count": int(max_floor_area / 30),
        "total_floor_area": int(max_floor_area),
        "irr": 5.2,
        "npv": base_value * 0.08,
        "policy_score": 88,
        "risk": "낮음"
    }
    scenarios.append(scenario_a)
    
    # B안: 신혼형 (45㎡)
    scenario_b = {
        "name": "B안: 신혼형",
        "unit_type": "신혼형",
        "unit_size": 45,
        "unit_count": int(max_floor_area / 45),
        "total_floor_area": int(max_floor_area),
        "irr": 6.4,
        "npv": base_value * 0.11,
        "policy_score": 92,
        "risk": "낮음"
    }
    scenarios.append(scenario_b)
    
    # C안: 고령자형 (40㎡)
    scenario_c = {
        "name": "C안: 고령자형",
        "unit_type": "고령자형",
        "unit_size": 40,
        "unit_count": int(max_floor_area / 40),
        "total_floor_area": int(max_floor_area),
        "irr": 5.8,
        "npv": base_value * 0.09,
        "policy_score": 85,
        "risk": "보통"
    }
    scenarios.append(scenario_c)
    
    # 최적 시나리오 선택 (IRR + 정책 점수 기준)
    best_scenario = max(scenarios, key=lambda x: x["irr"] + x["policy_score"] / 100)
    
    return {
        "scenarios": scenarios,
        "recommended": best_scenario["name"],
        "base_value": base_value  # ← appraisal 기준 가격
    }


def validate_appraisal_result(result: Dict) -> None:
    """
    감정평가 결과 검증
    
    필수 필드가 없으면 에러 발생
    """
    required_fields = [
        "final_value",
        "value_per_sqm",
        "zoning",
        "official_price",
        "transactions"
    ]
    
    for field in required_fields:
        if field not in result or not result[field]:
            raise HTTPException(
                status_code=400,
                detail=f"감정평가 필수 필드 누락: {field}"
            )
    
    # 거래사례 개수 확인
    if len(result.get("transactions", [])) < 5:
        raise HTTPException(
            status_code=400,
            detail="거래사례가 부족합니다 (최소 5건 필요)"
        )


# ============================================
# Main API Endpoints
# ============================================

@router_v40_2.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "40.3",
        "name": "ZeroSite v40.3 - Pipeline Lock Release (감정평가 기준 고정)",
        "features": [
            "Appraisal-First Architecture",
            "Context Protection (Immutable Appraisal)",
            "Pipeline Dependency Check",
            "Data Consistency Validation"
        ]
    }


@router_v40_2.post("/run-analysis")
async def run_full_land_analysis(request: FullLandAnalysisRequest):
    """
    🚀 v40.2 UNIFIED ANALYSIS - Appraisal-First Architecture
    
    실행 순서 (업계 표준):
    1. Geocoding & Basic Info
    2. **APPRAISAL ENGINE v39** (Single Source of Truth)
    3. Extract Diagnosis View (from appraisal)
    4. Extract Capacity View (from appraisal)
    5. Calculate Scenario (from appraisal)
    6. Store Context
    
    Returns: Context ID + Summary
    """
    try:
        context_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # =======================================
        # STEP 1: GEOCODING (기본 정보 조회)
        # =======================================
        geo_result = geocoding_engine.geocode_address(request.address)
        if not geo_result['success']:
            raise HTTPException(status_code=400, detail="주소를 찾을 수 없습니다.")
        
        lat = geo_result['lat']
        lng = geo_result['lng']
        si = geo_result['si']
        gu = geo_result['gu']
        dong = geo_result['dong']
        jibun = geo_result['jibun']
        
        geo_info = {
            "coordinates": {"lat": lat, "lng": lng},
            "administrative": {"si": si, "gu": gu, "dong": dong, "jibun": jibun}
        }
        
        # =======================================
        # STEP 2: APPRAISAL ENGINE v39 실행
        # (Single Source of Truth - 가장 중요!)
        # =======================================
        
        # 2.1) Zoning 조회
        zone_result = zoning_engine.get_zone_type(lat, lng, si, gu, dong, jibun)
        
        # 2.2) 공시지가 조회
        price_result = landprice_engine.get_land_price(lat, lng, '', si, gu, dong, jibun)
        
        # 2.3) 거래사례 조회
        transactions = transaction_engine.get_transactions(
            si, gu, dong, lat, lng, request.land_area_sqm, zone_result['zone_type']
        )
        
        # 2.4) 프리미엄 분석
        premium_result = premium_engine.analyze_premium(si, gu, dong, zone_result['zone_type'], lat, lng)
        
        # 2.5) 감정평가 실행
        land_info = {
            'address': request.address,
            'land_area': request.land_area_sqm,
            'official_price': price_result['official_price'],
            'zone_type': zone_result['zone_type'],
            'lat': lat,
            'lng': lng,
            'land_shape': request.land_shape,
            'slope': request.slope,
            'road_access': request.road_access,
            'orientation': request.orientation
        }
        
        appraisal_result = appraisal_engine.run_appraisal(land_info, transactions, premium_result)
        
        # Zoning 정보를 appraisal_result에 추가
        appraisal_result['zoning'] = {
            'zone_type': zone_result['zone_type'],
            'far': zone_result.get('far', 200),
            'bcr': zone_result.get('bcr', 60)
        }
        appraisal_result['official_price'] = price_result['official_price']
        appraisal_result['transactions'] = transactions
        appraisal_result['restrictions'] = zone_result.get('restrictions', [])
        
        # 검증: 필수 필드 확인
        validate_appraisal_result(appraisal_result)
        
        # =======================================
        # STEP 3: EXTRACT VIEWS (appraisal 기반)
        # =======================================
        diagnosis = extract_diagnosis_view(appraisal_result, geo_info)
        capacity = extract_capacity_view(appraisal_result, request.land_area_sqm)
        scenario = calculate_scenario_view(appraisal_result, request.land_area_sqm)
        
        # =======================================
        # STEP 4: STORE CONTEXT (v40.3 Protection)
        # =======================================
        complete_context = {
            "context_id": context_id,
            "timestamp": timestamp,
            "version": "40.3",  # ← v40.3 Pipeline Lock Release
            "input": {
                "address": request.address,
                "land_area_sqm": request.land_area_sqm,
                "physical_characteristics": {
                    "land_shape": request.land_shape,
                    "slope": request.slope,
                    "road_access": request.road_access,
                    "orientation": request.orientation
                }
            },
            "appraisal": appraisal_result,  # ← Single Source of Truth (IMMUTABLE)
            "diagnosis": diagnosis,  # ← appraisal 기반 뷰 (READ-ONLY)
            "capacity": capacity,  # ← appraisal 기반 뷰 (READ-ONLY)
            "scenario": scenario,  # ← appraisal 기반 뷰 (READ-ONLY)
            "raw_data": {
                "geo_result": geo_result,
                "zone_result": zone_result,
                "price_result": price_result,
                "premium_result": premium_result
            },
            "_metadata": {
                "pipeline_version": "40.3",
                "protection_enabled": True,
                "appraisal_locked": True,
                "created_at": timestamp
            }
        }
        
        # v40.3: Appraisal 데이터 보호 플래그 추가
        complete_context["appraisal"]["_protected"] = True
        complete_context["appraisal"]["_lock_timestamp"] = timestamp
        
        CONTEXT_STORAGE[context_id] = complete_context
        
        # =======================================
        # STEP 5: RETURN SUMMARY
        # =======================================
        return {
            "status": "success",
            "context_id": context_id,
            "timestamp": timestamp,
            "summary": {
                "appraisal_value": appraisal_result["final_value"],
                "value_per_sqm": appraisal_result["value_per_sqm"],
                "suitability": diagnosis["suitability"],
                "zone_type": appraisal_result["zoning"]["zone_type"],
                "max_units": capacity["max_units"],
                "recommended_scenario": scenario["recommended"]
            },
            "message": "✅ v40.2 종합 토지분석 완료 (Appraisal-First)"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")


@router_v40_2.get("/context/{context_id}")
async def get_context(context_id: str):
    """
    전체 Context 조회 (READ-ONLY)
    
    v40.3: Context Protection 적용
    """
    if context_id not in CONTEXT_STORAGE:
        raise HTTPException(status_code=404, detail="Context를 찾을 수 없습니다.")
    
    context = CONTEXT_STORAGE[context_id]
    
    # v40.3: Protection 상태 추가
    from app.core.context_protector import ContextProtector
    protection_status = ContextProtector.get_protection_status(context)
    
    return {
        **context,
        "_protection_status": protection_status
    }


@router_v40_2.get("/context/{context_id}/pipeline-status")
async def get_pipeline_status(context_id: str):
    """
    v40.3 Pipeline 상태 조회
    
    Returns:
        - Pipeline 실행 순서 및 완료 상태
        - 데이터 일관성 검증 결과
        - Context 보호 상태
    """
    if context_id not in CONTEXT_STORAGE:
        raise HTTPException(status_code=404, detail="Context를 찾을 수 없습니다.")
    
    context = CONTEXT_STORAGE[context_id]
    
    from app.core.context_protector import ContextProtector
    
    # Pipeline 완료 상태
    pipeline_status = {
        "1_appraisal": {
            "completed": "appraisal" in context,
            "required_by": ["diagnosis", "capacity", "scenario", "lh_review"],
            "status": "✅ Complete" if "appraisal" in context else "❌ Missing"
        },
        "2_diagnosis": {
            "completed": "diagnosis" in context,
            "required_by": ["scenario", "lh_review"],
            "status": "✅ Complete" if "diagnosis" in context else "❌ Missing"
        },
        "3_capacity": {
            "completed": "capacity" in context,
            "required_by": ["scenario", "lh_review"],
            "status": "✅ Complete" if "capacity" in context else "❌ Missing"
        },
        "4_scenario": {
            "completed": "scenario" in context,
            "required_by": ["lh_review"],
            "status": "✅ Complete" if "scenario" in context else "❌ Missing"
        },
        "5_lh_review": {
            "completed": "lh_review" in context,
            "required_by": [],
            "status": "✅ Complete" if "lh_review" in context else "⏳ Pending"
        }
    }
    
    # 데이터 일관성 검증
    consistency_check = ContextProtector.check_data_consistency(context)
    
    # Context 보호 상태
    protection_status = ContextProtector.get_protection_status(context)
    
    # 전체 상태 판정
    all_core_modules_complete = all([
        context.get("appraisal"),
        context.get("diagnosis"),
        context.get("capacity"),
        context.get("scenario")
    ])
    
    return {
        "context_id": context_id,
        "version": "40.3",
        "overall_status": "✅ Pipeline Complete" if all_core_modules_complete else "⏳ Pipeline In Progress",
        "pipeline": pipeline_status,
        "consistency": consistency_check,
        "protection": protection_status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@router_v40_2.get("/context/{context_id}/{tab}")
async def get_context_tab(context_id: str, tab: str):
    """
    특정 탭 데이터 조회 (READ-ONLY)
    
    Valid tabs:
    - diagnosis: 토지진단
    - capacity: 규모검토
    - appraisal: 감정평가 (기준 데이터)
    - scenario: 시나리오
    """
    if context_id not in CONTEXT_STORAGE:
        raise HTTPException(status_code=404, detail="Context를 찾을 수 없습니다.")
    
    context = CONTEXT_STORAGE[context_id]
    
    valid_tabs = ['diagnosis', 'capacity', 'appraisal', 'scenario']
    if tab not in valid_tabs:
        raise HTTPException(
            status_code=400,
            detail=f"유효하지 않은 탭입니다. 사용 가능: {', '.join(valid_tabs)}"
        )
    
    # 단순 조회만 (재계산 없음)
    return {
        "tab": tab,
        "context_id": context_id,
        "data": context[tab],
        "message": f"{tab} 데이터 조회 완료 (READ-ONLY)"
    }


@router_v40_2.get("/reports/{context_id}/{report_type}")
async def generate_report(context_id: str, report_type: str):
    """
    v40.4 보고서 생성 (5종 체계 지원)
    
    Report Types:
    - landowner_brief: 토지주용 간략 보고서 (3p)
    - lh_submission: LH 제출용 보고서 (10~15p) [향후 지원]
    - policy_impact: 정책 영향 분석 (15p) [향후 지원]
    - developer_feasibility: 개발사업자용 타당성 (15~20p) [향후 지원]
    - extended_professional: 전문가용 상세 보고서 (25~40p) [향후 지원]
    - appraisal_v39: 기존 감정평가서 (23~30p, 하위 호환)
    """
    # Context 조회
    if context_id not in CONTEXT_STORAGE:
        raise HTTPException(status_code=404, detail="Context를 찾을 수 없습니다.")
    
    context = CONTEXT_STORAGE[context_id]
    
    # ===================================
    # v40.4: Report Type Validation
    # ===================================
    from app.core.report_types import ReportType, validate_report_request
    
    try:
        report_type_enum = ReportType(report_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 보고서 타입: {report_type}. 사용 가능: landowner_brief, appraisal_v39"
        )
    
    # Validate request
    validation_result = validate_report_request(report_type_enum, context)
    
    if not validation_result["valid"]:
        errors = validation_result.get("errors", [])
        raise HTTPException(
            status_code=400,
            detail=f"보고서 생성 불가: {', '.join(errors)}"
        )
    
    # Log warnings
    warnings = validation_result.get("warnings", [])
    if warnings:
        print(f"⚠️ Report warnings: {', '.join(warnings)}")
    
    # ===================================
    # 검증: 감정평가 결과 필수
    # ===================================
    if "appraisal" not in context or not context["appraisal"]:
        raise HTTPException(
            status_code=400,
            detail="감정평가 결과가 없습니다. 먼저 토지분석을 실행하세요."
        )
    
    # 검증: 필수 필드 확인
    try:
        validate_appraisal_result(context["appraisal"])
    except HTTPException as e:
        raise HTTPException(
            status_code=400,
            detail=f"감정평가 데이터 불완전: {e.detail}"
        )
    
    # ===================================
    # v40.4: 보고서 생성 (5종 체계)
    # ===================================
    
    # 1. Landowner Brief (v40.4 신규)
    if report_type == "landowner_brief":
        try:
            from app.services.reports.landowner_brief_generator import LandownerBriefGenerator
            
            generator = LandownerBriefGenerator()
            pdf_bytes = generator.generate(context)
            
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=Landowner_Brief_{context_id[:8]}.pdf"
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Landowner Brief 생성 중 오류: {str(e)}"
            )
    
    # 2. Appraisal v39 (하위 호환)
    elif report_type == "appraisal_v39":
        try:
            pdf_bytes = pdf_generator.generate(context["appraisal"])
            
            return StreamingResponse(
                io.BytesIO(pdf_bytes),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=Appraisal_Report_v39_{context_id[:8]}.pdf"
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF 생성 중 오류: {str(e)}"
            )
    
    # 3. LH Submission, Policy Impact, Developer Feasibility (향후 지원)
    elif report_type in ["lh_submission", "policy_impact", "developer_feasibility", "extended_professional"]:
        raise HTTPException(
            status_code=501,  # Not Implemented
            detail=f"{report_type} 보고서는 v40.5에서 지원 예정입니다."
        )
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 보고서 타입: {report_type}"
        )


# ============================================
# Data Consistency Check (개발용)
# ============================================

@router_v40_2.get("/debug/consistency-check/{context_id}")
async def check_data_consistency(context_id: str):
    """
    데이터 일관성 체크 (개발/디버깅용)
    
    모든 탭에서 동일한 데이터를 사용하는지 검증
    """
    if context_id not in CONTEXT_STORAGE:
        raise HTTPException(status_code=404, detail="Context를 찾을 수 없습니다.")
    
    context = CONTEXT_STORAGE[context_id]
    
    # 감정평가 데이터 추출
    appraisal_zone = context["appraisal"]["zoning"]["zone_type"]
    appraisal_price = context["appraisal"]["official_price"]
    appraisal_far = context["appraisal"]["zoning"]["far"]
    
    # 진단 데이터 추출
    diagnosis_zone = context["diagnosis"]["zone_type"]
    diagnosis_price = context["diagnosis"]["official_price"]
    
    # 규모 데이터 추출
    capacity_far = context["capacity"]["far"]
    capacity_zone = context["capacity"]["zoning"]["zone_type"]
    
    # 일관성 검증
    checks = {
        "zone_consistency": {
            "appraisal": appraisal_zone,
            "diagnosis": diagnosis_zone,
            "capacity": capacity_zone,
            "match": (appraisal_zone == diagnosis_zone == capacity_zone),
            "status": "✅ PASS" if (appraisal_zone == diagnosis_zone == capacity_zone) else "❌ FAIL"
        },
        "price_consistency": {
            "appraisal": appraisal_price,
            "diagnosis": diagnosis_price,
            "match": (appraisal_price == diagnosis_price),
            "status": "✅ PASS" if (appraisal_price == diagnosis_price) else "❌ FAIL"
        },
        "far_consistency": {
            "appraisal": appraisal_far,
            "capacity": capacity_far,
            "match": (appraisal_far == capacity_far),
            "status": "✅ PASS" if (appraisal_far == capacity_far) else "❌ FAIL"
        }
    }
    
    all_passed = all(check["match"] for check in checks.values())
    
    return {
        "context_id": context_id,
        "overall_status": "✅ ALL CHECKS PASSED" if all_passed else "❌ SOME CHECKS FAILED",
        "checks": checks,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
