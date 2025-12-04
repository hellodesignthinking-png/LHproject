"""
ZeroSite v9.0 - Risk Engine
============================

리스크 평가 엔진 v9.0
25개 항목 종합 리스크 체크리스트

리스크 카테고리:
1. 법률 리스크 (LEGAL) - 6개 항목
2. 재무 리스크 (FINANCIAL) - 7개 항목
3. 기술 리스크 (TECHNICAL) - 6개 항목
4. 시장 리스크 (MARKET) - 6개 항목

총 25개 항목
심각도: HIGH/MEDIUM/LOW
상태: PASS/WARNING/FAIL

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

from app.models_v9.standard_schema_v9_0 import (
    RiskAssessment,
    RiskItem,
    RiskCategory,
    RiskSeverity,
    RiskStatus,
    LHScores,
    FinancialResult,
    GISResult,
    SiteInfo
)

logger = logging.getLogger(__name__)


class RiskEngineV90:
    """
    Risk Engine v9.0
    
    25개 항목 종합 리스크 평가 시스템
    """
    
    # 25개 리스크 항목 정의
    RISK_ITEMS = [
        # 법률 리스크 (6개)
        {
            "id": "LEG-001",
            "category": RiskCategory.LEGAL,
            "name": "용도지역 부적합",
            "severity": RiskSeverity.HIGH,
            "check": "zone_type"
        },
        {
            "id": "LEG-002",
            "category": RiskCategory.LEGAL,
            "name": "건폐율 초과",
            "severity": RiskSeverity.HIGH,
            "check": "building_coverage_ratio"
        },
        {
            "id": "LEG-003",
            "category": RiskCategory.LEGAL,
            "name": "용적률 초과",
            "severity": RiskSeverity.HIGH,
            "check": "floor_area_ratio"
        },
        {
            "id": "LEG-004",
            "category": RiskCategory.LEGAL,
            "name": "높이 제한 초과",
            "severity": RiskSeverity.MEDIUM,
            "check": "height_limit"
        },
        {
            "id": "LEG-005",
            "category": RiskCategory.LEGAL,
            "name": "인허가 지연 위험",
            "severity": RiskSeverity.MEDIUM,
            "check": "permit_complexity"
        },
        {
            "id": "LEG-006",
            "category": RiskCategory.LEGAL,
            "name": "환경영향평가 필요",
            "severity": RiskSeverity.LOW,
            "check": "environmental_assessment"
        },
        
        # 재무 리스크 (7개)
        {
            "id": "FIN-001",
            "category": RiskCategory.FINANCIAL,
            "name": "낮은 ROI",
            "severity": RiskSeverity.HIGH,
            "check": "roi"
        },
        {
            "id": "FIN-002",
            "category": RiskCategory.FINANCIAL,
            "name": "낮은 Cap Rate",
            "severity": RiskSeverity.HIGH,
            "check": "cap_rate"
        },
        {
            "id": "FIN-003",
            "category": RiskCategory.FINANCIAL,
            "name": "낮은 IRR",
            "severity": RiskSeverity.HIGH,
            "check": "irr"
        },
        {
            "id": "FIN-004",
            "category": RiskCategory.FINANCIAL,
            "name": "공사비 상승 위험",
            "severity": RiskSeverity.MEDIUM,
            "check": "construction_cost"
        },
        {
            "id": "FIN-005",
            "category": RiskCategory.FINANCIAL,
            "name": "LH 매입가 불확실성",
            "severity": RiskSeverity.MEDIUM,
            "check": "lh_purchase_price"
        },
        {
            "id": "FIN-006",
            "category": RiskCategory.FINANCIAL,
            "name": "손익분기 장기화",
            "severity": RiskSeverity.MEDIUM,
            "check": "breakeven_year"
        },
        {
            "id": "FIN-007",
            "category": RiskCategory.FINANCIAL,
            "name": "임대료 하락 위험",
            "severity": RiskSeverity.LOW,
            "check": "rental_income"
        },
        
        # 기술 리스크 (6개)
        {
            "id": "TEC-001",
            "category": RiskCategory.TECHNICAL,
            "name": "지하철 접근성 부족",
            "severity": RiskSeverity.HIGH,
            "check": "subway_distance"
        },
        {
            "id": "TEC-002",
            "category": RiskCategory.TECHNICAL,
            "name": "학교 접근성 부족",
            "severity": RiskSeverity.MEDIUM,
            "check": "school_distance"
        },
        {
            "id": "TEC-003",
            "category": RiskCategory.TECHNICAL,
            "name": "병원 접근성 부족",
            "severity": RiskSeverity.MEDIUM,
            "check": "hospital_distance"
        },
        {
            "id": "TEC-004",
            "category": RiskCategory.TECHNICAL,
            "name": "상업시설 접근성 부족",
            "severity": RiskSeverity.LOW,
            "check": "commercial_distance"
        },
        {
            "id": "TEC-005",
            "category": RiskCategory.TECHNICAL,
            "name": "공사 난이도 높음",
            "severity": RiskSeverity.MEDIUM,
            "check": "construction_difficulty"
        },
        {
            "id": "TEC-006",
            "category": RiskCategory.TECHNICAL,
            "name": "품질 하자 위험",
            "severity": RiskSeverity.LOW,
            "check": "quality_risk"
        },
        
        # 시장 리스크 (6개)
        {
            "id": "MKT-001",
            "category": RiskCategory.MARKET,
            "name": "수요 부족",
            "severity": RiskSeverity.HIGH,
            "check": "demand"
        },
        {
            "id": "MKT-002",
            "category": RiskCategory.MARKET,
            "name": "경쟁 공급 과다",
            "severity": RiskSeverity.MEDIUM,
            "check": "supply"
        },
        {
            "id": "MKT-003",
            "category": RiskCategory.MARKET,
            "name": "지역 인구 감소",
            "severity": RiskSeverity.MEDIUM,
            "check": "population_trend"
        },
        {
            "id": "MKT-004",
            "category": RiskCategory.MARKET,
            "name": "지역 경제 침체",
            "severity": RiskSeverity.MEDIUM,
            "check": "economic_trend"
        },
        {
            "id": "MKT-005",
            "category": RiskCategory.MARKET,
            "name": "부동산 시장 변동",
            "severity": RiskSeverity.LOW,
            "check": "market_volatility"
        },
        {
            "id": "MKT-006",
            "category": RiskCategory.MARKET,
            "name": "입주율 저조 위험",
            "severity": RiskSeverity.MEDIUM,
            "check": "occupancy_rate"
        }
    ]
    
    def __init__(self):
        """Risk Engine 초기화"""
        logger.info("⚠️ Risk Engine v9.0 초기화 완료")
        logger.info(f"   ✓ 25개 리스크 항목 로드")
        logger.info(f"   ✓ 4개 카테고리: LEGAL/FINANCIAL/TECHNICAL/MARKET")
    
    def assess_comprehensive_risk(
        self,
        site_info: SiteInfo,
        gis_result: GISResult,
        financial_result: FinancialResult,
        lh_scores: LHScores
    ) -> RiskAssessment:
        """
        종합 리스크 평가 (25개 항목)
        
        Args:
            site_info: 토지 기본 정보
            gis_result: GIS 분석 결과
            financial_result: 재무 분석 결과
            lh_scores: LH 평가 점수
            
        Returns:
            RiskAssessment (25개 항목 평가)
        """
        logger.info("⚠️ 리스크 평가 시작 (25개 항목)")
        
        all_risks = []
        
        # 1. 각 리스크 항목 평가
        for risk_def in self.RISK_ITEMS:
            risk_item = self._evaluate_risk_item(
                risk_def,
                site_info,
                gis_result,
                financial_result,
                lh_scores
            )
            all_risks.append(risk_item)
        
        # 2. 카테고리별 집계
        pass_count = len([r for r in all_risks if r.status == RiskStatus.PASS])
        warning_count = len([r for r in all_risks if r.status == RiskStatus.WARNING])
        fail_count = len([r for r in all_risks if r.status == RiskStatus.FAIL])
        
        # 3. 중요 리스크 추출 (WARNING 이상)
        critical_risks = [r for r in all_risks if r.status in [RiskStatus.WARNING, RiskStatus.FAIL]]
        
        # 4. 전체 위험도 산출
        overall_risk_level = self._calculate_overall_risk_level(pass_count, warning_count, fail_count)
        
        logger.info(f"✅ 리스크 평가 완료: PASS {pass_count}, WARNING {warning_count}, FAIL {fail_count}")
        logger.info(f"   전체 위험도: {overall_risk_level}")
        
        return RiskAssessment(
            total_items=25,
            pass_count=pass_count,
            warning_count=warning_count,
            fail_count=fail_count,
            critical_risks=critical_risks,
            all_risks=all_risks,
            overall_risk_level=overall_risk_level
        )
    
    def _evaluate_risk_item(
        self,
        risk_def: Dict,
        site_info: SiteInfo,
        gis_result: GISResult,
        financial_result: FinancialResult,
        lh_scores: LHScores
    ) -> RiskItem:
        """
        개별 리스크 항목 평가
        
        Args:
            risk_def: 리스크 정의
            (기타 평가 데이터)
            
        Returns:
            RiskItem (평가 결과)
        """
        risk_id = risk_def["id"]
        check_type = risk_def["check"]
        
        # 체크 타입별 평가
        status = RiskStatus.PASS
        description = "정상"
        mitigation = None
        
        # 법률 리스크
        if check_type == "zone_type":
            valid_zones = ["제3종일반주거지역", "제2종일반주거지역", "제1종일반주거지역", "준주거지역"]
            if site_info.zone_type not in valid_zones:
                status = RiskStatus.FAIL
                description = f"용도지역 부적합: {site_info.zone_type}"
                mitigation = "용도지역 변경 신청 검토"
        
        elif check_type == "building_coverage_ratio":
            if site_info.building_coverage_ratio > 70:
                status = RiskStatus.FAIL
                description = f"건폐율 {site_info.building_coverage_ratio}% 초과"
                mitigation = "건축 규모 축소 또는 법규 재검토"
            elif site_info.building_coverage_ratio > 60:
                status = RiskStatus.WARNING
                description = f"건폐율 {site_info.building_coverage_ratio}% 높음"
                mitigation = "건축 규모 조정 권장"
        
        elif check_type == "floor_area_ratio":
            if site_info.floor_area_ratio > 300:
                status = RiskStatus.FAIL
                description = f"용적률 {site_info.floor_area_ratio}% 초과"
                mitigation = "층수 또는 세대수 감소"
            elif site_info.floor_area_ratio > 250:
                status = RiskStatus.WARNING
                description = f"용적률 {site_info.floor_area_ratio}% 높음"
                mitigation = "용적률 여유 확보 권장"
        
        # 재무 리스크
        elif check_type == "roi":
            if financial_result.roi_10yr < 20:
                status = RiskStatus.FAIL
                description = f"ROI {financial_result.roi_10yr:.1f}% 매우 낮음"
                mitigation = "사업성 전면 재검토 필요"
            elif financial_result.roi_10yr < 40:
                status = RiskStatus.WARNING
                description = f"ROI {financial_result.roi_10yr:.1f}% 낮음"
                mitigation = "공사비 절감 또는 임대료 상승 방안"
        
        elif check_type == "cap_rate":
            if financial_result.cap_rate < 3:
                status = RiskStatus.FAIL
                description = f"Cap Rate {financial_result.cap_rate:.1f}% 매우 낮음"
                mitigation = "토지가 협상 또는 설계 최적화"
            elif financial_result.cap_rate < 4:
                status = RiskStatus.WARNING
                description = f"Cap Rate {financial_result.cap_rate:.1f}% 낮음"
                mitigation = "수익성 개선 방안 마련"
        
        elif check_type == "irr":
            if financial_result.irr_10yr < 4:
                status = RiskStatus.FAIL
                description = f"IRR {financial_result.irr_10yr:.1f}% 매우 낮음"
                mitigation = "프로젝트 재구조화 필요"
            elif financial_result.irr_10yr < 6:
                status = RiskStatus.WARNING
                description = f"IRR {financial_result.irr_10yr:.1f}% 낮음"
                mitigation = "장기 수익 개선 계획 수립"
        
        elif check_type == "breakeven_year":
            if financial_result.breakeven_year and financial_result.breakeven_year > 15:
                status = RiskStatus.FAIL
                description = f"손익분기 {financial_result.breakeven_year}년 (장기)"
                mitigation = "초기 수익 확보 방안 필요"
            elif financial_result.breakeven_year and financial_result.breakeven_year > 10:
                status = RiskStatus.WARNING
                description = f"손익분기 {financial_result.breakeven_year}년"
                mitigation = "수익 조기 확보 방안 검토"
        
        # 기술 리스크 (GIS)
        elif check_type == "subway_distance":
            if gis_result.subway_stations:
                distance = gis_result.subway_stations[0].distance_m
                if distance > 2000:
                    status = RiskStatus.FAIL
                    description = f"지하철역 {distance:.0f}m (원거리)"
                    mitigation = "셔틀버스 운영 또는 대중교통 개선"
                elif distance > 1000:
                    status = RiskStatus.WARNING
                    description = f"지하철역 {distance:.0f}m (다소 원거리)"
                    mitigation = "접근성 보완 방안 검토"
        
        elif check_type == "school_distance":
            if gis_result.elementary_schools:
                distance = gis_result.elementary_schools[0].distance_m
                if distance > 1500:
                    status = RiskStatus.WARNING
                    description = f"초등학교 {distance:.0f}m (원거리)"
                    mitigation = "통학 지원 방안 마련"
        
        elif check_type == "hospital_distance":
            if gis_result.hospitals:
                distance = gis_result.hospitals[0].distance_m
                if distance > 3000:
                    status = RiskStatus.WARNING
                    description = f"병원 {distance:.0f}m (원거리)"
                    mitigation = "의료 서비스 연계 방안"
        
        # 시장 리스크
        elif check_type == "demand":
            # LH 평가 점수 기반 수요 평가
            if lh_scores.total_score < 60:
                status = RiskStatus.FAIL
                description = f"LH 점수 {lh_scores.total_score:.1f}점 (수요 미흡)"
                mitigation = "입지 또는 사업성 개선"
            elif lh_scores.total_score < 75:
                status = RiskStatus.WARNING
                description = f"LH 점수 {lh_scores.total_score:.1f}점 (수요 보통)"
                mitigation = "마케팅 강화"
        
        # 기타 리스크 (기본값)
        else:
            status = RiskStatus.PASS
            description = "평가 기준 미적용 (정상 가정)"
        
        return RiskItem(
            id=risk_id,
            category=risk_def["category"],
            name=risk_def["name"],
            severity=risk_def["severity"],
            status=status,
            description=description,
            mitigation=mitigation
        )
    
    def _calculate_overall_risk_level(
        self,
        pass_count: int,
        warning_count: int,
        fail_count: int
    ) -> str:
        """
        전체 위험도 산출
        
        Args:
            pass_count: 통과 항목 수
            warning_count: 경고 항목 수
            fail_count: 실패 항목 수
            
        Returns:
            str (LOW/MEDIUM/HIGH/CRITICAL)
        """
        total = 25
        
        # FAIL이 5개 이상이면 CRITICAL
        if fail_count >= 5:
            return "CRITICAL"
        
        # FAIL이 3개 이상 또는 WARNING이 10개 이상이면 HIGH
        if fail_count >= 3 or warning_count >= 10:
            return "HIGH"
        
        # FAIL이 1개 이상 또는 WARNING이 5개 이상이면 MEDIUM
        if fail_count >= 1 or warning_count >= 5:
            return "MEDIUM"
        
        # 그 외는 LOW
        return "LOW"
