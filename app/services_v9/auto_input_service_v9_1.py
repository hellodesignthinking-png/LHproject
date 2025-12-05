"""
ZeroSite v9.1 Auto Input Service (통합 자동화 서비스)

This service integrates all three automation components:
1. AddressResolverV9 - Address → Coordinates
2. ZoningAutoMapperV9 - Zone Type → Building Standards
3. UnitEstimatorV9 - Land Area + FAR → Unit Count

User Input Minimization:
- v9.0: 10 required fields
- v9.1: 4 required fields (60% reduction)

Required Inputs (Only 4):
1. 지번 주소 (Parcel Number/Address)
2. 토지면적 (Land Area)
3. 토지가격 (Land Price per sqm)
4. 용도지역 (Zone Type)

Auto-Generated Fields:
- latitude, longitude (from address)
- building_coverage_ratio, floor_area_ratio (from zone type)
- unit_count (calculated from land area + FAR)
- height_limit (from zone type)
- parking_ratio (from zone type)

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.1
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from app.services_v9.address_resolver_sync_v9_1 import AddressResolverSyncV91 as AddressResolverV9, AddressInfo
from app.services_v9.zoning_auto_mapper_v9_0 import ZoningAutoMapperV9, ZoningStandards
from app.services_v9.unit_estimator_v9_0 import UnitEstimatorV9, UnitEstimation

logger = logging.getLogger(__name__)


@dataclass
class AutoInputResult:
    """
    자동 입력 결과
    
    Attributes:
        success: 성공 여부
        user_inputs: 사용자가 입력한 필드 (4개)
        auto_generated: 자동 생성된 필드 (6개+)
        complete_payload: API 전송용 완전한 페이로드
        warnings: 경고 목록
        confidence_score: 전체 신뢰도 (0-100)
        processing_time_ms: 처리 시간 (밀리초)
    """
    success: bool
    user_inputs: Dict[str, Any]
    auto_generated: Dict[str, Any]
    complete_payload: Dict[str, Any]
    warnings: list
    confidence_score: float
    processing_time_ms: float


class AutoInputServiceV91:
    """
    ZeroSite v9.1 통합 자동 입력 서비스
    
    Features:
    - 4개 입력으로 10개 필드 자동 생성
    - 주소 → 좌표 자동 변환
    - 용도지역 → 건축 기준 자동 설정
    - 세대수 자동 계산
    - 입력 검증 및 오류 처리
    
    Usage:
        service = AutoInputServiceV91()
        result = service.process_minimal_input({
            "address": "서울특별시 강남구 테헤란로 123",
            "land_area": 1000.0,
            "land_appraisal_price": 10000000.0,
            "zone_type": "제3종일반주거지역"
        })
        
        if result.success:
            api_payload = result.complete_payload
            # Send to /api/v9/analyze-land
    """
    
    def __init__(self):
        self.address_resolver = AddressResolverV9()
        self.zoning_mapper = ZoningAutoMapperV9()
        self.unit_estimator = UnitEstimatorV9()
        logger.info("✅ AutoInputServiceV91 initialized")
    
    def process_minimal_input(
        self,
        user_input: Dict[str, Any],
        fallback_coordinates: Optional[Dict[str, float]] = None
    ) -> AutoInputResult:
        """
        최소 입력 (4개 필드)으로 완전한 분석 페이로드 생성
        
        Args:
            user_input: 사용자 입력 (4개 필드)
                - address: str (지번 주소)
                - land_area: float (토지면적, ㎡)
                - land_appraisal_price: float (평당가 또는 ㎡당가, 원)
                - zone_type: str (용도지역)
            
            fallback_coordinates: 좌표 자동 변환 실패 시 대체 좌표
                - latitude: float
                - longitude: float
        
        Returns:
            AutoInputResult: 자동 입력 처리 결과
        
        Example:
            >>> service = AutoInputServiceV91()
            >>> result = service.process_minimal_input({
            ...     "address": "서울특별시 강남구 테헤란로 123",
            ...     "land_area": 1000.0,
            ...     "land_appraisal_price": 10000000.0,
            ...     "zone_type": "제3종일반주거지역"
            ... })
            >>> result.complete_payload["unit_count"]
            80
        """
        import time
        start_time = time.time()
        
        warnings = []
        auto_generated = {}
        
        logger.info("🚀 v9.1 Auto Input Processing started")
        logger.info(f"   User Inputs: {len(user_input)} fields")
        
        # ===== 1. 입력 검증 =====
        required_fields = ["address", "land_area", "land_appraisal_price", "zone_type"]
        missing_fields = [f for f in required_fields if f not in user_input]
        
        if missing_fields:
            return AutoInputResult(
                success=False,
                user_inputs=user_input,
                auto_generated={},
                complete_payload={},
                warnings=[f"필수 입력 누락: {', '.join(missing_fields)}"],
                confidence_score=0.0,
                processing_time_ms=0.0
            )
        
        # ===== 2. Address → Coordinates =====
        logger.info("📍 Step 1/3: Address Resolution")
        
        address_info = self.address_resolver.resolve_address(
            user_input["address"]
        )
        
        if address_info.success:
            auto_generated["latitude"] = address_info.latitude
            auto_generated["longitude"] = address_info.longitude
            logger.info(f"   ✅ Coordinates: ({address_info.latitude:.6f}, {address_info.longitude:.6f})")
        else:
            warnings.append(f"주소 변환 실패: {address_info.error_message}")
            
            if fallback_coordinates:
                auto_generated["latitude"] = fallback_coordinates["latitude"]
                auto_generated["longitude"] = fallback_coordinates["longitude"]
                logger.warning(f"   ⚠️  Fallback coordinates used")
            else:
                # 서울시청 좌표 (기본값)
                auto_generated["latitude"] = 37.5665
                auto_generated["longitude"] = 126.9780
                warnings.append("기본 좌표(서울시청) 사용 - GIS 정확도 낮음")
                logger.warning(f"   ⚠️  Default coordinates (Seoul City Hall)")
        
        # ===== 3. Zone Type → Building Standards =====
        logger.info("🏗️  Step 2/3: Zoning Standards Mapping")
        
        zone_standards = self.zoning_mapper.get_zoning_standards(
            user_input["zone_type"]
        )
        
        if zone_standards:
            auto_generated["building_coverage_ratio"] = zone_standards.building_coverage_ratio
            auto_generated["floor_area_ratio"] = zone_standards.floor_area_ratio
            
            if zone_standards.max_height:
                auto_generated["height_limit"] = zone_standards.max_height
            
            logger.info(f"   ✅ Building Coverage: {zone_standards.building_coverage_ratio}%")
            logger.info(f"   ✅ Floor Area Ratio: {zone_standards.floor_area_ratio}%")
        else:
            warnings.append(f"용도지역 '{user_input['zone_type']}' 기준 없음 - 기본값 사용")
            auto_generated["building_coverage_ratio"] = 50.0
            auto_generated["floor_area_ratio"] = 200.0
            logger.warning(f"   ⚠️  Unknown zone type - using defaults")
        
        # ===== 4. Land Area + FAR → Unit Count =====
        logger.info("🏘️  Step 3/3: Unit Count Estimation")
        
        unit_estimation = self.unit_estimator.estimate_units(
            land_area=user_input["land_area"],
            floor_area_ratio=auto_generated["floor_area_ratio"],
            building_coverage_ratio=auto_generated.get("building_coverage_ratio"),
            zone_type=user_input["zone_type"]
        )
        
        auto_generated["unit_count"] = unit_estimation.estimated_units
        auto_generated["unit_type_distribution"] = unit_estimation.unit_type_distribution
        
        logger.info(f"   ✅ Estimated Units: {unit_estimation.estimated_units}세대")
        logger.info(f"   ✅ Confidence: {unit_estimation.confidence_score:.1f}%")
        
        # Unit estimation warnings
        if unit_estimation.warnings:
            warnings.extend(unit_estimation.warnings)
        
        # ===== 5. Complete Payload 생성 =====
        complete_payload = {
            # User inputs (4 fields)
            "address": user_input["address"],
            "land_area": user_input["land_area"],
            "land_appraisal_price": user_input["land_appraisal_price"],
            "zone_type": user_input["zone_type"],
            
            # Auto-generated (6+ fields)
            **auto_generated
        }
        
        # ===== 6. Confidence Score 계산 =====
        confidence_components = []
        
        # Address resolution confidence
        if address_info.success:
            confidence_components.append(address_info.confidence_score)
        else:
            confidence_components.append(20.0)  # Low confidence for fallback
        
        # Zone mapping confidence
        if zone_standards:
            confidence_components.append(100.0)
        else:
            confidence_components.append(50.0)
        
        # Unit estimation confidence
        confidence_components.append(unit_estimation.confidence_score)
        
        overall_confidence = sum(confidence_components) / len(confidence_components)
        
        # ===== 7. Processing Time =====
        processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"✅ Auto Input Processing completed in {processing_time_ms:.2f}ms")
        logger.info(f"   Overall Confidence: {overall_confidence:.1f}%")
        logger.info(f"   Auto-Generated Fields: {len(auto_generated)}")
        
        if warnings:
            logger.warning(f"   Warnings: {len(warnings)}")
            for warning in warnings:
                logger.warning(f"     - {warning}")
        
        return AutoInputResult(
            success=True,
            user_inputs={k: v for k, v in user_input.items() if k in required_fields},
            auto_generated=auto_generated,
            complete_payload=complete_payload,
            warnings=warnings,
            confidence_score=overall_confidence,
            processing_time_ms=processing_time_ms
        )
    
    def get_auto_input_summary(self, result: AutoInputResult) -> str:
        """
        자동 입력 결과 요약 (사용자 친화적 메시지)
        
        Args:
            result: AutoInputResult
        
        Returns:
            str: 요약 메시지
        """
        if not result.success:
            return f"❌ 자동 입력 실패\n경고: {', '.join(result.warnings)}"
        
        summary_lines = [
            "✅ 자동 입력 완료",
            f"",
            f"사용자 입력: {len(result.user_inputs)}개 필드",
            f"자동 생성: {len(result.auto_generated)}개 필드",
            f"",
            f"생성된 필드:",
        ]
        
        for field, value in result.auto_generated.items():
            if field == "unit_type_distribution":
                continue  # Skip complex object
            
            if isinstance(value, float):
                summary_lines.append(f"  - {field}: {value:.2f}")
            else:
                summary_lines.append(f"  - {field}: {value}")
        
        summary_lines.append(f"")
        summary_lines.append(f"신뢰도: {result.confidence_score:.1f}%")
        summary_lines.append(f"처리 시간: {result.processing_time_ms:.2f}ms")
        
        if result.warnings:
            summary_lines.append(f"")
            summary_lines.append(f"⚠️  경고 ({len(result.warnings)}개):")
            for warning in result.warnings:
                summary_lines.append(f"  - {warning}")
        
        return "\n".join(summary_lines)


# ===== Module-Level Convenience Functions =====

def auto_process_minimal_input(
    address: str,
    land_area: float,
    land_appraisal_price: float,
    zone_type: str
) -> Dict[str, Any]:
    """
    Quick auto-input processing (편의 함수)
    
    Args:
        address: 지번 주소
        land_area: 토지면적 (㎡)
        land_appraisal_price: 평당가 또는 ㎡당가 (원)
        zone_type: 용도지역
    
    Returns:
        Dict: Complete API payload
    
    Example:
        >>> payload = auto_process_minimal_input(
        ...     "서울특별시 강남구 테헤란로 123",
        ...     1000.0,
        ...     10000000.0,
        ...     "제3종일반주거지역"
        ... )
        >>> payload["unit_count"]
        80
    """
    service = AutoInputServiceV91()
    result = service.process_minimal_input({
        "address": address,
        "land_area": land_area,
        "land_appraisal_price": land_appraisal_price,
        "zone_type": zone_type
    })
    
    if not result.success:
        raise ValueError(f"Auto input failed: {result.warnings}")
    
    return result.complete_payload
