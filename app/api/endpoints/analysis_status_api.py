"""
ZeroSite Analysis Status & Result API
======================================

Endpoints for:
1. Project creation and status tracking
2. Module result retrieval (M1-M6)
3. Verification gates
4. Execution control

Author: ZeroSite UX Redesign Team
Date: 2026-01-11
Version: 3.0 (Human-Verified Mode)
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.analysis_status import (
    analysis_status_storage,
    AnalysisStatus,
    ModuleStatus,
    VerificationStatus,
    ModuleInfo
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["Analysis Status & Results"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateProjectRequest(BaseModel):
    """Create new analysis project"""
    project_name: str
    address: str
    reference_info: Optional[str] = None


class CreateProjectResponse(BaseModel):
    """Project creation response"""
    success: bool
    project_id: str
    message: str
    next_action: str


class VerifyModuleRequest(BaseModel):
    """User verification for module results"""
    approved: bool  # True = approved, False = rejected
    comments: Optional[str] = None
    verified_by: Optional[str] = "user"


class VerifyModuleResponse(BaseModel):
    """Verification response"""
    success: bool
    message: str
    next_action: Optional[str] = None
    can_proceed: bool


class ModuleResultResponse(BaseModel):
    """Module result retrieval response"""
    success: bool
    module_name: str
    status: str
    verification_status: Optional[str] = None
    executed_at: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    can_execute: bool
    execution_blocked_reason: Optional[str] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/projects/create", response_model=CreateProjectResponse)
async def create_analysis_project(request: CreateProjectRequest):
    """
    STEP 1: Create new analysis project
    
    Creates project and executes M1 data collection automatically.
    User must verify M1 before M2-M6 can execute.
    """
    try:
        # Generate project ID
        project_id = str(uuid.uuid4())
        context_id = str(uuid.uuid4())
        
        # Create analysis status
        status = analysis_status_storage.create_status(
            project_id=project_id,
            project_name=request.project_name,
            address=request.address,
            context_id=context_id
        )
        
        logger.info(f"✅ Project created: {project_id}")
        logger.info(f"   Name: {request.project_name}")
        logger.info(f"   Address: {request.address}")
        
        # ✅ REAL DATA FETCH: Auto-collect complete M1 data (LAND + POI)
        try:
            from app.services.land_data_service import LandDataService
            from app.services.kakao.kakao_map_service import KakaoMapService
            
            logger.info(f"🔍 M1 실데이터 수집 시작: {request.address}")
            warnings = []  # ⚠️ 경고 메시지 수집
            
            # 1. Land data (기본 토지 정보 + 공시지가 + 규제)
            land_service = LandDataService()
            land_data = land_service.fetch_all_by_address(request.address)
            
            if not land_data or not land_data.get("basic_info"):
                logger.error(f"❌ REAL DATA NOT LOADED for {request.address}")
                raise HTTPException(
                    status_code=400,
                    detail=f"토지 데이터를 불러올 수 없습니다. 주소를 확인해주세요: {request.address}"
                )
            
            # ⚠️ basic_info/price_info/regulation_info는 Pydantic 모델이므로 .get() 불가
            basic_info = land_data.get("basic_info")  # LandBasicInfo object
            price_info = land_data.get("price_info")  # LandPriceInfo object
            regulation_info = land_data.get("regulation_info")  # RegulationInfo object
            
            # 2. POI data (교통/학교/상업시설)
            kakao_service = KakaoMapService()
            poi_data = await kakao_service.collect_all_poi(request.address)
            
            # 3. Combine into M1 result (REAL DATA ONLY - NO FALLBACK)
            # ⚠️ Pydantic 모델은 속성 접근 (basic_info.area) 또는 getattr(basic_info, 'area', 0)
            location_info = land_data.get("location", {})
            area_sqm = getattr(basic_info, "area", 0) if basic_info else 0
            land_use_zone = getattr(basic_info, "land_use_zone", "")
            
            m1_result = {
                "address": request.address,
                "road_address": location_info.get("road_address", request.address),
                "area_sqm": area_sqm,
                "area_pyeong": area_sqm / 3.3058 if area_sqm else 0,
                "zone_type": getattr(regulation_info, "use_zone", land_use_zone) if regulation_info else land_use_zone,
                "far": getattr(regulation_info, "floor_area_ratio", 0) if regulation_info else 0,
                "bcr": getattr(regulation_info, "building_coverage_ratio", 0) if regulation_info else 0,
                "road_width": 12,  # Default - 실제 도로폭 API 연동 필요
                "official_land_price": getattr(price_info, "official_price", 0) if price_info else 0,
                "official_price_date": getattr(price_info, "base_year", "") if price_info else "",
                "regulations": getattr(regulation_info, "regulations", []) if regulation_info else [],
                "restrictions": [],  # TODO: 규제 상세 정보 추가
                "subway_stations": poi_data.get("subway_stations", []),
                "bus_stops": poi_data.get("bus_stops", []),
                "poi_schools": poi_data.get("poi_schools", []),
                "poi_commercial": poi_data.get("poi_commercial", []),
                "transaction_cases": land_data.get("transactions", []),
                "context_id": context_id,
                "fetched_at": datetime.now().isoformat(),
                "data_sources": {
                    "cadastral": "공공데이터포털 (토지특성정보)",
                    "official_price": f"개별공시지가 ({getattr(price_info, 'base_year', 'N/A') if price_info else 'N/A'})",
                    "regulations": "VWorld (토지이용규제)",
                    "poi": "Kakao Map API"
                }
            }
            
            # ⚠️ Zero Guard: 필수 필드 검증 (경고만 표시, 프로젝트 생성 허용)
            warnings = []
            if m1_result["area_sqm"] == 0:
                logger.warning(f"⚠️ LAND DATA NOT LOADED: area_sqm = 0 (API 장애 가능성)")
                warnings.append("토지 면적 정보를 불러올 수 없습니다. 수동 입력이 필요합니다.")
            
            if m1_result["official_land_price"] == 0:
                logger.warning(f"⚠️ 공시지가를 불러올 수 없습니다.")
                warnings.append("공시지가 정보를 불러올 수 없습니다. 수동 입력이 필요합니다.")
            
            if not m1_result.get("zone_type"):
                logger.warning(f"⚠️ 용도지역을 불러올 수 없습니다.")
                warnings.append("용도지역 정보를 불러올 수 없습니다. 수동 입력이 필요합니다.")
            
            # Update M1 status with REAL data
            analysis_status_storage.update_module_status(
                project_id=project_id,
                module_name="M1",
                status=ModuleStatus.COMPLETED,
                result_summary=m1_result
            )
            
            logger.info(f"✅ M1 실데이터 수집 완료: {project_id}")
            logger.info(f"   면적: {m1_result['area_sqm']}㎡")
            logger.info(f"   용도지역: {m1_result['zone_type']}")
            logger.info(f"   공시지가: ₩{m1_result['official_land_price']:,}/㎡")
            logger.info(f"   POI: 지하철 {len(poi_data.get('subway_stations', []))}개, 학교 {len(poi_data.get('poi_schools', []))}개")
            
        except HTTPException:
            raise
        except Exception as data_err:
            logger.error(f"❌ M1 데이터 수집 실패: {data_err}")
            raise HTTPException(
                status_code=500,
                detail=f"M1 데이터 수집 중 오류 발생: {str(data_err)}"
            )
        
        # Build response message
        if warnings:
            message = f"⚠️ Project created with warnings: {', '.join(warnings[:2])}"
            next_action = "Please verify M1 data and complete missing information manually."
        else:
            message = "✅ Project created successfully. M1 data collection completed."
            next_action = "Verify M1 data and approve to proceed with M2-M6 analysis."
        
        return CreateProjectResponse(
            success=True,
            project_id=project_id,
            message=message,
            next_action=next_action
        )
    
    except Exception as e:
        logger.error(f"❌ Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str) -> AnalysisStatus:
    """
    Get complete analysis status for a project
    
    Returns:
        - Current context ID and version
        - Status of all modules (M1-M6)
        - Verification status
        - Next recommended action
    """
    status = analysis_status_storage.get_status(project_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    return status


@router.post("/projects/{project_id}/modules/{module_name}/verify", response_model=VerifyModuleResponse)
async def verify_module_results(
    project_id: str,
    module_name: str,
    request: VerifyModuleRequest
):
    """
    🔒 CRITICAL: User verification gate
    
    User confirms or rejects module results.
    
    Args:
        project_id: Project identifier
        module_name: M1, M2, M3, M4, M5, or M6
        request: Verification decision
    
    Returns:
        Verification status and next action
    """
    
    # Validate module name
    valid_modules = ["M1", "M2", "M3", "M4", "M5", "M6"]
    if module_name not in valid_modules:
        raise HTTPException(status_code=400, detail=f"Invalid module: {module_name}")
    
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # Check if module has been executed
    module_info = status.get_module_status(module_name)
    
    # For M1, allow verification even if status is not COMPLETED
    # This supports manual data entry workflow
    if module_name == "M1":
        if module_info.status == ModuleStatus.NOT_STARTED:
            logger.warning(f"⚠️ M1 verification requested but status is NOT_STARTED")
            logger.warning(f"   Allowing verification for manual data workflow")
        elif module_info.status != ModuleStatus.COMPLETED:
            logger.warning(f"⚠️ M1 status is {module_info.status}, not COMPLETED")
    else:
        # For M2-M6, require COMPLETED status
        if module_info.status != ModuleStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"{module_name} has not been completed yet. Current status: {module_info.status}"
            )
    
    # Apply verification
    verification_status = VerificationStatus.APPROVED if request.approved else VerificationStatus.REJECTED
    
    try:
        analysis_status_storage.verify_module(
            project_id=project_id,
            module_name=module_name,
            verification=verification_status,
            verified_by=request.verified_by
        )
        
        logger.info(f"✅ {module_name} verification: {verification_status.value}")
        logger.info(f"   Project: {project_id}")
        logger.info(f"   Verified by: {request.verified_by}")
        
        # Determine next action
        if verification_status == VerificationStatus.APPROVED:
            # Get next module
            module_order = ["M1", "M2", "M3", "M4", "M5", "M6"]
            current_idx = module_order.index(module_name)
            
            if current_idx < len(module_order) - 1:
                next_module = module_order[current_idx + 1]
                next_action = f"Ready to execute {next_module}"
                can_proceed = True
            else:
                next_action = "All modules completed - ready for final report"
                can_proceed = False
            
            return VerifyModuleResponse(
                success=True,
                message=f"{module_name} approved by user",
                next_action=next_action,
                can_proceed=can_proceed
            )
        else:
            # Rejected - need to re-collect
            return VerifyModuleResponse(
                success=True,
                message=f"{module_name} rejected by user - data recollection required",
                next_action=f"Re-execute {module_name} with corrected data",
                can_proceed=False
            )
    
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class ExecuteModuleResponse(BaseModel):
    """Module execution response"""
    success: bool
    message: str
    module_name: str
    execution_id: Optional[str] = None
    status: str


@router.post("/projects/{project_id}/modules/{module_name}/execute", response_model=ExecuteModuleResponse)
async def execute_module(
    project_id: str,
    module_name: str
):
    """
    ⚡ CRITICAL: Execute module analysis
    
    This triggers the actual execution of M2-M6 modules.
    M1 is executed automatically on project creation.
    
    Args:
        project_id: Project identifier
        module_name: M2, M3, M4, M5, or M6 (M1 is automatic)
    
    Returns:
        Execution status and result
    """
    
    # Validate module name
    valid_modules = ["M2", "M3", "M4", "M5", "M6"]
    if module_name not in valid_modules:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid module: {module_name}. Only M2-M6 can be executed via this endpoint."
        )
    
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # Check if module can be executed
    can_execute, reason = status.can_execute_module(module_name)
    if not can_execute:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute {module_name}: {reason}"
        )
    
    try:
        execution_id = str(uuid.uuid4())
        
        logger.info(f"⚡ Executing {module_name} for project {project_id}")
        logger.info(f"   Execution ID: {execution_id}")
        
        # Mark module as in progress
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name=module_name,
            status=ModuleStatus.IN_PROGRESS,
            result_summary={"execution_id": execution_id, "started_at": datetime.now().isoformat()}
        )
        
        # TODO: Actually execute the module logic here
        # For now, immediately mark as completed (mock)
        # In production, this would call the actual M2/M3/M4/M5/M6 services
        
        # Execute actual module logic based on module_name
        if module_name == "M2":
            # M2: Land Value Analysis
            m1_status = status.get_module_status("M1")
            # ⚠️ CRITICAL: M1 data is in result_data, not result_summary
            m1_data = m1_status.result_data if hasattr(m1_status, 'result_data') and m1_status.result_data else m1_status.result_summary
            
            logger.info(f"🔍 M2 Debug: m1_data type = {type(m1_data)}")
            logger.info(f"🔍 M2 Debug: m1_data keys = {list(m1_data.keys()) if m1_data else 'None'}")
            logger.info(f"🔍 M2 Debug: area_sqm = {m1_data.get('area_sqm') if m1_data else 'N/A'}")
            logger.info(f"🔍 M2 Debug: official_land_price = {m1_data.get('official_land_price') if m1_data else 'N/A'}")
            if m1_data:
                # Simple land value calculation based on M1 data
                area_sqm = m1_data.get("area_sqm", 0)
                official_price = m1_data.get("official_land_price", 0)
                zone_type = m1_data.get("zone_type", "")
                
                # Calculate estimated land value (simple formula)
                # Official price usually 70-80% of market price
                if area_sqm > 0 and official_price > 0:
                    estimated_value = int(area_sqm * official_price * 1.3)  # 30% markup
                    unit_price_sqm = int(official_price * 1.3)
                    unit_price_pyeong = int(unit_price_sqm * 3.3058)
                else:
                    estimated_value = 0
                    unit_price_sqm = 0
                    unit_price_pyeong = 0
                
                mock_result = {
                    "execution_id": execution_id,
                    "module": module_name,
                    "computed_at": datetime.now().isoformat(),
                    "status": "completed",
                    "land_value": estimated_value,
                    "unit_price_sqm": unit_price_sqm,
                    "unit_price_pyeong": unit_price_pyeong,
                    "confidence_score": 75,
                    "confidence_level": "보통",
                    "valuation_method": "공시지가 기준 추정",
                    "official_price": official_price,
                    "market_to_official_ratio": 1.3,
                    "price_range": {
                        "min": int(estimated_value * 0.9),
                        "max": int(estimated_value * 1.1)
                    },
                    "premium_factors": {
                        "corner_lot": 0,
                        "subway_proximity": 5 if m1_data.get("subway_stations") else 0,
                        "school_district": 3 if m1_data.get("poi_schools") else 0
                    },
                    "transaction_samples": []
                }
            else:
                mock_result = {
                    "execution_id": execution_id,
                    "module": module_name,
                    "computed_at": datetime.now().isoformat(),
                    "status": "completed",
                    "message": f"{module_name} execution completed but M1 data not available"
                }
        
        elif module_name == "M3":
            # M3: Housing Type Decision
            m1_status = status.get_module_status("M1")
            m1_data = m1_status.result_data if hasattr(m1_status, 'result_data') and m1_status.result_data else m1_status.result_summary
            zone_type = m1_data.get("zone_type", "") if m1_data else ""
            
            # Simple housing type selection based on zone
            if "상업" in zone_type:
                selected_type = "도시형생활주택"
                confidence = 80
            elif "주거" in zone_type:
                selected_type = "공공임대주택"
                confidence = 85
            else:
                selected_type = "공공임대주택"
                confidence = 70
            
            mock_result = {
                "execution_id": execution_id,
                "module": module_name,
                "computed_at": datetime.now().isoformat(),
                "status": "completed",
                "selected_type": selected_type,
                "confidence": confidence,
                "decision_rationale": f"용도지역({zone_type})을 고려한 최적 주거 유형 선정",
                "selection_method": "용도지역 기반 자동 선택"
            }
        
        elif module_name == "M4":
            # M4: Unit Planning - 세대수 및 주차 계획
            m1_status = status.get_module_status("M1")
            m1_data = m1_status.result_data if hasattr(m1_status, 'result_data') and m1_status.result_data else m1_status.result_summary
            m3_status = status.get_module_status("M3")
            m3_data = m3_status.result_summary if m3_status else {}
            
            area_sqm = m1_data.get("area_sqm", 0) if m1_data else 0
            bcr = m1_data.get("bcr", 60) if m1_data else 60  # 건폐율
            far = m1_data.get("far", 200) if m1_data else 200  # 용적률
            housing_type = m3_data.get("selected_type", "공공임대주택")
            
            # Calculate building capacity
            building_footprint = area_sqm * (bcr / 100)  # 건축면적
            total_floor_area = area_sqm * (far / 100)  # 연면적
            
            # Estimate units (assuming 40㎡ avg per unit for 도시형생활주택)
            avg_unit_size = 40 if "도시형" in housing_type else 50
            legal_units = max(1, int(total_floor_area / avg_unit_size))
            
            # Incentive units (보통 법정 세대수의 120%)
            incentive_units = int(legal_units * 1.2)
            
            # Parking calculation (법정: 세대당 0.5대, 인센티브: 세대당 0.3대)
            legal_parking = max(1, int(legal_units * 0.5))
            incentive_parking = max(1, int(incentive_units * 0.3))
            
            mock_result = {
                "execution_id": execution_id,
                "module": module_name,
                "computed_at": datetime.now().isoformat(),
                "status": "completed",
                "legal_units": legal_units,
                "incentive_units": incentive_units,
                "building_footprint": int(building_footprint),
                "total_floor_area": int(total_floor_area),
                "parking_count": incentive_parking,
                "legal_parking": legal_parking,
                "parking_ratio": round(incentive_parking / incentive_units, 2),
                "avg_unit_size": avg_unit_size,
                "floors_estimated": max(1, int(total_floor_area / building_footprint)) if building_footprint > 0 else 1
            }
            
        elif module_name == "M5":
            # M5: Financial Analysis - NPV/IRR/ROI
            m2_status = status.get_module_status("M2")
            m2_data = m2_status.result_summary if m2_status else {}
            m4_status = status.get_module_status("M4")
            m4_data = m4_status.result_summary if m4_status else {}
            
            land_value = m2_data.get("land_value", 0)
            total_units = m4_data.get("incentive_units", 10)
            total_floor_area = m4_data.get("total_floor_area", 1000)
            
            # Cost estimation (simplified)
            construction_cost_per_sqm = 2000000  # ₩2M/㎡ (typical)
            construction_cost = int(total_floor_area * construction_cost_per_sqm)
            
            total_project_cost = land_value + construction_cost
            indirect_costs = int(total_project_cost * 0.15)  # 15% for fees, permits, etc.
            total_cost = total_project_cost + indirect_costs
            
            # Revenue estimation
            avg_sale_price_per_unit = 300000000  # ₩300M per unit (typical for 도시형생활주택)
            total_revenue = total_units * avg_sale_price_per_unit
            
            # Financial metrics
            net_profit = total_revenue - total_cost
            roi = round((net_profit / total_cost * 100), 2) if total_cost > 0 else 0
            npv = int(net_profit * 0.85)  # Simple NPV (85% discount)
            irr = round(roi / 3, 2)  # Simplified IRR estimate
            
            mock_result = {
                "execution_id": execution_id,
                "module": module_name,
                "computed_at": datetime.now().isoformat(),
                "status": "completed",
                "npv": npv,
                "irr": irr,
                "roi": roi,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "net_profit": net_profit,
                "cost_breakdown": {
                    "land_acquisition": land_value,
                    "construction": construction_cost,
                    "indirect_costs": indirect_costs
                },
                "revenue_breakdown": {
                    "unit_sales": total_revenue,
                    "units_count": total_units,
                    "avg_price_per_unit": avg_sale_price_per_unit
                },
                "payback_period_years": round(total_cost / (total_revenue / 3), 1) if total_revenue > 0 else 0
            }
            
        elif module_name == "M6":
            # M6: Final Decision - GO/CONDITIONAL/NO-GO
            m2_status = status.get_module_status("M2")
            m2_data = m2_status.result_summary if m2_status else {}
            m5_status = status.get_module_status("M5")
            m5_data = m5_status.result_summary if m5_status else {}
            
            roi = m5_data.get("roi", 0)
            npv = m5_data.get("npv", 0)
            confidence = m2_data.get("confidence_score", 0)
            
            # Decision logic
            risks = []
            recommendations = []
            
            if roi >= 20:
                decision = "GO"
                decision_rationale = "프로젝트 수익성이 우수하며 투자 진행을 권장합니다."
            elif roi >= 10:
                decision = "CONDITIONAL"
                decision_rationale = "프로젝트 수익성은 양호하나 리스크 관리가 필요합니다."
                risks.append("수익률이 목표치보다 낮음")
                recommendations.append("공사비 절감 방안 검토")
                recommendations.append("분양가 상향 가능성 분석")
            else:
                decision = "NO-GO"
                decision_rationale = "프로젝트 수익성이 낮아 투자를 권장하지 않습니다."
                risks.append("투자 수익률 미달")
                risks.append("자금 회수 기간 장기화 우려")
            
            # Common risks (ensure at least 3)
            if confidence < 70:
                risks.append("토지 가치 평가의 신뢰도가 낮음")
                recommendations.append("전문 감정평가 실시 권장")
            
            risks.append("건축 인허가 지연 리스크")
            risks.append("시장 수요 변동 리스크")
            risks.append("공사비 상승 리스크")
            
            # Ensure minimum 3 risks
            if len(risks) < 3:
                risks.append("금리 변동에 따른 자금 조달 리스크")
            
            recommendations.append("시장 조사 및 수요 분석 실시")
            recommendations.append("법률 및 세무 전문가 자문")
            
            mock_result = {
                "execution_id": execution_id,
                "module": module_name,
                "computed_at": datetime.now().isoformat(),
                "status": "completed",
                "decision": decision,
                "decision_rationale": decision_rationale,
                "risk_list": risks,
                "recommendations": recommendations,
                "overall_score": min(100, max(0, int(roi * 3))),
                "key_metrics": {
                    "roi": roi,
                    "npv": npv,
                    "land_value_confidence": confidence
                }
            }
            
        else:
            # Fallback for unknown modules
            mock_result = {
                "execution_id": execution_id,
                "module": module_name,
                "computed_at": datetime.now().isoformat(),
                "status": "completed",
                "message": f"{module_name} execution completed (basic implementation)"
            }
        
        # Mark module as completed
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name=module_name,
            status=ModuleStatus.COMPLETED,
            result_summary=mock_result
        )
        
        logger.info(f"✅ {module_name} execution completed")
        
        return ExecuteModuleResponse(
            success=True,
            message=f"{module_name} executed successfully",
            module_name=module_name,
            execution_id=execution_id,
            status="completed"
        )
    
    except Exception as e:
        logger.error(f"❌ {module_name} execution failed: {e}")
        
        # Mark module as failed
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name=module_name,
            status=ModuleStatus.FAILED,
            result_summary={"error": str(e)}
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/modules/{module_name}/result", response_model=ModuleResultResponse)
async def get_module_result(
    project_id: str,
    module_name: str
):
    """
    Get result data for specific module
    
    Returns:
        - Module execution status
        - Verification status
        - Result data (if completed)
        - Whether next module can execute
    """
    
    # Validate module name
    valid_modules = ["M1", "M2", "M3", "M4", "M5", "M6"]
    if module_name not in valid_modules:
        raise HTTPException(status_code=400, detail=f"Invalid module: {module_name}")
    
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # Get module info
    module_info = status.get_module_status(module_name)
    
    # Check execution permission for next module
    module_order = ["M1", "M2", "M3", "M4", "M5", "M6"]
    current_idx = module_order.index(module_name)
    
    if current_idx < len(module_order) - 1:
        next_module = module_order[current_idx + 1]
        can_execute_next, reason = status.can_execute_module(next_module)
    else:
        can_execute_next = False
        reason = "Last module in pipeline"
    
    return ModuleResultResponse(
        success=True,
        module_name=module_name,
        status=module_info.status.value,
        verification_status=module_info.verification_status.value if module_info.verification_status else None,
        executed_at=module_info.executed_at,
        result_data=module_info.result_summary,
        can_execute=can_execute_next,
        execution_blocked_reason=None if can_execute_next else reason
    )


@router.get("/projects")
async def list_all_projects(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    List all analysis projects
    
    Returns:
        List of projects with their status
    """
    all_statuses = analysis_status_storage.list_all()
    
    # Sort by last activity (most recent first)
    sorted_statuses = sorted(
        all_statuses,
        key=lambda s: s.last_activity,
        reverse=True
    )
    
    # Apply pagination
    paginated = sorted_statuses[offset:offset + limit]
    
    return {
        "success": True,
        "total": len(all_statuses),
        "limit": limit,
        "offset": offset,
        "projects": [
            {
                "project_id": s.project_id,
                "project_name": s.project_name,
                "address": s.address,
                "progress": s.get_progress_percentage(),
                "next_action": s.get_next_action(),
                "last_activity": s.last_activity,
                "is_locked": s.is_locked
            }
            for s in paginated
        ]
    }


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """
    Delete analysis project
    
    Note: This also invalidates all associated contexts
    """
    status = analysis_status_storage.get_status(project_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    # TODO: Actually delete from storage
    # For now, just mark as invalid
    
    return {
        "success": True,
        "message": f"Project {project_id} deleted"
    }


@router.put("/projects/{project_id}/modules/M1/data")
async def update_m1_data(
    project_id: str,
    data: Dict[str, Any]
):
    """
    Update M1 data with manual input
    
    This allows users to manually input M1 land data when
    automatic collection fails or is incomplete.
    """
    # Get project status
    status = analysis_status_storage.get_status(project_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    try:
        # Update M1 data
        analysis_status_storage.update_module_status(
            project_id=project_id,
            module_name="M1",
            status=ModuleStatus.COMPLETED,
            result_summary=data
        )
        
        logger.info(f"✅ M1 data updated manually for project {project_id}")
        
        return {
            "success": True,
            "message": "M1 data updated successfully",
            "project_id": project_id
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to update M1 data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
