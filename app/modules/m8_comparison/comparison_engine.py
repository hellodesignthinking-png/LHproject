"""
ZeroSite v4.0 M8 Multi-Site Comparison Engine
=============================================

다중 부지 동시 분석 및 비교 엔진

Author: ZeroSite M8 Team
Date: 2025-12-26
Version: 1.0

Purpose:
    여러 후보 부지를 M1→M6 파이프라인으로 자동 분석하고
    상대 비교를 통해 최적 부지를 추천

Architecture:
    1. 다중 부지 입력 (주소 리스트)
    2. 병렬 M1→M6 파이프라인 실행
    3. 결과 수집 및 정규화
    4. 비교 매트릭스 생성
    5. 순위 결정 및 추천
    6. 비교 보고서 생성
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Python path adjustment
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.abspath(os.path.join(script_dir, '..', '..'))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app.core.context.canonical_land import CanonicalLandContext
from app.modules.m2_appraisal.service import AppraisalService
from app.modules.m3_lh_demand.service import LHDemandService
from app.modules.m4_capacity.service_v2 import CapacityServiceV2
from app.modules.m5_feasibility.service import FeasibilityService
from app.modules.m6_lh_review.service_v3 import LHReviewServiceV3
from app.modules.m6_lh_review.comprehensive_judgement import (
    M6ComprehensiveResult,
    JudgementType,
    GradeType,
    RegionWeightType
)
from app.modules.m8_comparison.comparison_models import (
    SiteComparisonResult,
    ComparisonMatrix,
    RecommendationTier,
    ComparisonReport
)


class MultiSiteComparisonEngine:
    """다중 부지 비교 분석 엔진"""
    
    def __init__(self):
        """서비스 초기화"""
        print("\n" + "="*80)
        print("  ZeroSite v4.0 M8 Multi-Site Comparison Engine")
        print("  다중 부지 비교 분석 엔진 초기화")
        print("="*80 + "\n")
        
        # M2-M6 서비스 초기화
        self.appraisal_service = AppraisalService()
        self.lh_demand_service = LHDemandService()
        self.capacity_service = CapacityServiceV2()
        self.feasibility_service = FeasibilityService()
        self.lh_review_service = LHReviewServiceV3()
        
        print("✓ M2 Appraisal Service initialized")
        print("✓ M3 LH Demand Service initialized")
        print("✓ M4 Capacity Service V2 initialized")
        print("✓ M5 Feasibility Service initialized")
        print("✓ M6 LH Review Service V3 initialized")
        print()
    
    def analyze_multiple_sites(
        self,
        sites: List[Dict[str, Any]]
    ) -> ComparisonReport:
        """
        다중 부지 분석 및 비교
        
        Args:
            sites: 부지 정보 리스트
                [
                    {
                        "site_id": "site_1",
                        "site_name": "역삼동 후보지 1",
                        "m1_context": M1Context(...)
                    },
                    ...
                ]
        
        Returns:
            ComparisonReport: 비교 분석 보고서
        """
        print("\n" + "="*80)
        print(f"  M8 다중 부지 분석 시작 - 총 {len(sites)}개 부지")
        print("="*80 + "\n")
        
        # STEP 1: 각 부지별 M1→M6 파이프라인 실행
        site_results: List[SiteComparisonResult] = []
        
        for idx, site_info in enumerate(sites, 1):
            print(f"\n{'─'*80}")
            print(f"  [{idx}/{len(sites)}] {site_info['site_name']}")
            print(f"  Site ID: {site_info['site_id']}")
            print(f"{'─'*80}\n")
            
            try:
                result = self._analyze_single_site(
                    site_id=site_info['site_id'],
                    site_name=site_info['site_name'],
                    m1_context=site_info['m1_context']
                )
                site_results.append(result)
                print(f"✓ {site_info['site_name']} 분석 완료")
                print(f"  → LH Score: {result.lh_score_total}/100")
                print(f"  → Judgement: {result.judgement}")
                print(f"  → Grade: {result.grade}")
                
            except Exception as e:
                print(f"✗ {site_info['site_name']} 분석 실패: {e}")
                continue
        
        print(f"\n{'='*80}")
        print(f"  전체 분석 완료: {len(site_results)}/{len(sites)} 성공")
        print(f"{'='*80}\n")
        
        # STEP 2: 비교 매트릭스 생성
        comparison_matrix = self._build_comparison_matrix(site_results)
        
        # STEP 3: 티어별 분류
        tier_classified = self._classify_by_tier(site_results)
        
        # STEP 4: 추천 결정
        top_recommendation, alternatives = self._determine_recommendations(site_results)
        
        # STEP 5: 전략적 인사이트 생성
        strategic_insights = self._generate_strategic_insights(site_results, comparison_matrix)
        
        # STEP 6: 지역별 분석
        regional_analysis = self._analyze_by_region(site_results)
        
        # STEP 7: 비교 보고서 생성
        report_id = f"M8-COMPARISON-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        report_title = f"다중 부지 비교 분석 보고서 ({len(site_results)}개 부지)"
        
        report = ComparisonReport(
            report_id=report_id,
            report_title=report_title,
            generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            comparison_matrix=comparison_matrix,
            tier_1_sites=tier_classified['tier_1'],
            tier_2_sites=tier_classified['tier_2'],
            tier_3_sites=tier_classified['tier_3'],
            tier_4_sites=tier_classified['tier_4'],
            tier_5_sites=tier_classified['tier_5'],
            top_recommendation=top_recommendation,
            alternative_recommendations=alternatives,
            strategic_insights=strategic_insights,
            regional_analysis=regional_analysis
        )
        
        print(f"\n{'='*80}")
        print(f"  M8 비교 보고서 생성 완료")
        print(f"  Report ID: {report_id}")
        print(f"{'='*80}\n")
        
        return report
    
    def _analyze_single_site(
        self,
        site_id: str,
        site_name: str,
        m1_context: CanonicalLandContext
    ) -> SiteComparisonResult:
        """개별 부지 M1→M6 파이프라인 실행"""
        
        # M1 컨텍스트는 이미 CanonicalLandContext
        land_ctx = m1_context
        
        # M2: 감정평가
        m2_result = self.appraisal_service.run(land_ctx, asking_price=None)
        
        # M3: 세대 유형 선정
        m3_result = self.lh_demand_service.run(land_ctx)
        
        # M4: 건축 가능 규모
        m4_result = self.capacity_service.run(land_ctx, m3_result)
        
        # M5: 사업성 분석
        m5_result = self.feasibility_service.run(m2_result, m4_result)
        
        # M6: LH 종합 심사
        m6_result = self.lh_review_service.run(
            land_ctx=land_ctx,
            appraisal_ctx=m2_result,
            housing_type_ctx=m3_result,
            capacity_ctx=m4_result,
            feasibility_ctx=m5_result
        )
        
        # 추천 등급 결정
        recommendation_tier = self._determine_recommendation_tier(m6_result)
        
        # 강점/약점 분석
        strengths, weaknesses = self._analyze_strengths_weaknesses(m6_result)
        
        # SiteComparisonResult 생성
        return SiteComparisonResult(
            site_id=site_id,
            site_name=site_name,
            address=land_ctx.address,
            parcel_id=land_ctx.parcel_id,
            lh_score_total=m6_result.lh_score_total,
            judgement=m6_result.judgement.value,
            grade=m6_result.grade.value,
            fatal_reject=m6_result.fatal_reject,
            region_weight=m6_result.region_weight.value,
            land_value=int(m2_result.land_value),
            land_area_sqm=land_ctx.area_sqm,
            price_per_sqm=m2_result.unit_price_sqm,
            price_per_py=m2_result.unit_price_pyeong,
            total_units=m4_result.incentive_capacity.total_units,
            cost_per_unit=int(m5_result.cost_breakdown.total_cost / m4_result.incentive_capacity.total_units),
            npv_public=int(m5_result.financial_metrics.npv_public),
            irr_public=m5_result.financial_metrics.irr_public,
            profitability_grade=m5_result.profitability_grade,
            section_scores={
                "A": m6_result.section_a_policy.weighted_score,
                "B": m6_result.section_b_location.weighted_score,
                "C": m6_result.section_c_construction.weighted_score,
                "D": m6_result.section_d_price.weighted_score,
                "E": m6_result.section_e_business.weighted_score
            },
            recommendation_tier=recommendation_tier,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_points=m6_result.improvement_points
        )
    
    def _determine_branch_type(self, sido: str) -> RegionWeightType:
        """지역별 지점 유형 결정"""
        capital_regions = ['서울특별시', '경기도', '인천광역시']
        return RegionWeightType.CAPITAL if sido in capital_regions else RegionWeightType.LOCAL
    
    def _determine_recommendation_tier(self, m6_result: M6ComprehensiveResult) -> RecommendationTier:
        """추천 등급 결정"""
        if m6_result.fatal_reject:
            return RecommendationTier.TIER_5_REJECT
        
        score = m6_result.lh_score_total
        
        if score >= 85:
            return RecommendationTier.TIER_1_BEST
        elif score >= 70:
            return RecommendationTier.TIER_2_STRONG
        elif score >= 60:
            return RecommendationTier.TIER_3_CONSIDER
        elif score >= 50:
            return RecommendationTier.TIER_4_WEAK
        else:
            return RecommendationTier.TIER_5_REJECT
    
    def _analyze_strengths_weaknesses(
        self,
        m6_result: M6ComprehensiveResult
    ) -> tuple[List[str], List[str]]:
        """강점/약점 분석"""
        strengths = []
        weaknesses = []
        
        # 섹션별 점수 분석
        sections = {
            "A_정책·유형": (m6_result.section_a_policy.weighted_score, m6_result.section_a_policy.max_score),
            "B_입지·환경": (m6_result.section_b_location.weighted_score, m6_result.section_b_location.max_score),
            "C_건축가능성": (m6_result.section_c_construction.weighted_score, m6_result.section_c_construction.max_score),
            "D_가격·매입": (m6_result.section_d_price.weighted_score, m6_result.section_d_price.max_score),
            "E_사업성": (m6_result.section_e_business.weighted_score, m6_result.section_e_business.max_score)
        }
        
        for section_name, (score, max_score) in sections.items():
            pct = (score / max_score) * 100
            
            if pct >= 80:
                strengths.append(f"{section_name} 우수 ({pct:.0f}%)")
            elif pct < 60:
                weaknesses.append(f"{section_name} 개선 필요 ({pct:.0f}%)")
        
        return strengths, weaknesses
    
    def _build_comparison_matrix(
        self,
        site_results: List[SiteComparisonResult]
    ) -> ComparisonMatrix:
        """비교 매트릭스 생성"""
        
        # 빈 리스트 방어
        if not site_results:
            return ComparisonMatrix(
                sites=[],
                ranking=[],
                best_by_category={},
                total_sites=0,
                go_sites=0,
                conditional_sites=0,
                no_go_sites=0,
                avg_lh_score=0.0,
                avg_npv=0,
                avg_irr=0.0
            )
        
        # LH 점수 기준 순위
        sorted_sites = sorted(site_results, key=lambda x: x.lh_score_total, reverse=True)
        ranking = [site.site_id for site in sorted_sites]
        
        # 카테고리별 최고 부지
        best_by_category = {}
        
        # 입지 (B섹션)
        best_location = max(site_results, key=lambda x: x.section_scores.get("B", 0))
        best_by_category["location"] = best_location.site_id
        
        # 가격 (D섹션)
        best_price = max(site_results, key=lambda x: x.section_scores.get("D", 0))
        best_by_category["price"] = best_price.site_id
        
        # 사업성 (E섹션)
        best_business = max(site_results, key=lambda x: x.section_scores.get("E", 0))
        best_by_category["business"] = best_business.site_id
        
        # 건축 (C섹션)
        best_construction = max(site_results, key=lambda x: x.section_scores.get("C", 0))
        best_by_category["construction"] = best_construction.site_id
        
        # 정책 (A섹션)
        best_policy = max(site_results, key=lambda x: x.section_scores.get("A", 0))
        best_by_category["policy"] = best_policy.site_id
        
        # 통계
        go_count = sum(1 for s in site_results if s.judgement == "GO")
        conditional_count = sum(1 for s in site_results if s.judgement == "CONDITIONAL")
        no_go_count = sum(1 for s in site_results if s.judgement == "NO_GO")
        
        avg_lh_score = sum(s.lh_score_total for s in site_results) / len(site_results)
        avg_npv = int(sum(s.npv_public for s in site_results) / len(site_results))
        avg_irr = sum(s.irr_public for s in site_results) / len(site_results)
        
        return ComparisonMatrix(
            sites=sorted_sites,
            ranking=ranking,
            best_by_category=best_by_category,
            total_sites=len(site_results),
            go_sites=go_count,
            conditional_sites=conditional_count,
            no_go_sites=no_go_count,
            avg_lh_score=avg_lh_score,
            avg_npv=avg_npv,
            avg_irr=avg_irr
        )
    
    def _classify_by_tier(
        self,
        site_results: List[SiteComparisonResult]
    ) -> Dict[str, List[SiteComparisonResult]]:
        """티어별 분류"""
        classified = {
            'tier_1': [],
            'tier_2': [],
            'tier_3': [],
            'tier_4': [],
            'tier_5': []
        }
        
        for site in site_results:
            if site.recommendation_tier == RecommendationTier.TIER_1_BEST:
                classified['tier_1'].append(site)
            elif site.recommendation_tier == RecommendationTier.TIER_2_STRONG:
                classified['tier_2'].append(site)
            elif site.recommendation_tier == RecommendationTier.TIER_3_CONSIDER:
                classified['tier_3'].append(site)
            elif site.recommendation_tier == RecommendationTier.TIER_4_WEAK:
                classified['tier_4'].append(site)
            else:
                classified['tier_5'].append(site)
        
        return classified
    
    def _determine_recommendations(
        self,
        site_results: List[SiteComparisonResult]
    ) -> tuple[Optional[SiteComparisonResult], List[SiteComparisonResult]]:
        """추천 부지 결정"""
        
        # LH 점수 기준 정렬
        sorted_sites = sorted(site_results, key=lambda x: x.lh_score_total, reverse=True)
        
        # Fatal Reject가 아닌 최고 점수 부지가 1순위 추천
        top_recommendation = None
        for site in sorted_sites:
            if not site.fatal_reject:
                top_recommendation = site
                break
        
        # 대안 추천 (2-4위, Fatal Reject 제외)
        alternatives = []
        for site in sorted_sites[1:]:
            if not site.fatal_reject and len(alternatives) < 3:
                alternatives.append(site)
        
        return top_recommendation, alternatives
    
    def _generate_strategic_insights(
        self,
        site_results: List[SiteComparisonResult],
        comparison_matrix: ComparisonMatrix
    ) -> List[str]:
        """전략적 인사이트 생성"""
        insights = []
        
        # 빈 리스트 방어
        if not site_results or comparison_matrix.total_sites == 0:
            insights.append("⚠ 분석된 부지가 없습니다.")
            return insights
        
        # 1. 전체 품질 평가
        if comparison_matrix.avg_lh_score >= 80:
            insights.append(f"✓ 전체 후보지 평균 점수 {comparison_matrix.avg_lh_score:.1f}점으로 우수한 품질")
        elif comparison_matrix.avg_lh_score >= 70:
            insights.append(f"→ 전체 후보지 평균 점수 {comparison_matrix.avg_lh_score:.1f}점으로 양호한 수준")
        else:
            insights.append(f"⚠ 전체 후보지 평균 점수 {comparison_matrix.avg_lh_score:.1f}점으로 개선 필요")
        
        # 2. GO 부지 비율
        go_ratio = (comparison_matrix.go_sites / comparison_matrix.total_sites) * 100
        if go_ratio >= 50:
            insights.append(f"✓ GO 판정 부지 {comparison_matrix.go_sites}개({go_ratio:.0f}%) - 즉시 추진 가능 부지 다수")
        elif go_ratio > 0:
            insights.append(f"→ GO 판정 부지 {comparison_matrix.go_sites}개({go_ratio:.0f}%) - 제한적 선택 가능")
        else:
            insights.append(f"⚠ GO 판정 부지 없음 - 조건부 추진 또는 추가 후보지 발굴 필요")
        
        # 3. 사업성 분석
        if comparison_matrix.avg_npv > 0:
            insights.append(f"✓ 평균 NPV {comparison_matrix.avg_npv:,}원 - 수익성 양호")
        else:
            insights.append(f"⚠ 평균 NPV {comparison_matrix.avg_npv:,}원 - 비용 절감 또는 수익 개선 필요")
        
        # 4. 지역 다양성
        regions = set(site.region_weight for site in site_results)
        if len(regions) > 1:
            insights.append(f"→ 수도권/지방 다지역 포트폴리오 구성 - 리스크 분산 효과")
        
        # 5. 개선 가능성
        improvable_sites = sum(1 for s in site_results if len(s.improvement_points) > 0 and not s.fatal_reject)
        if improvable_sites > 0:
            insights.append(f"→ 개선 가능 부지 {improvable_sites}개 - 협상·설계 최적화로 품질 향상 가능")
        
        return insights
    
    def _analyze_by_region(
        self,
        site_results: List[SiteComparisonResult]
    ) -> Dict[str, Any]:
        """지역별 분석"""
        
        capital_sites = [s for s in site_results if s.region_weight == "수도권"]
        local_sites = [s for s in site_results if s.region_weight == "지방"]
        
        analysis = {}
        
        if capital_sites:
            analysis['capital'] = {
                'count': len(capital_sites),
                'avg_lh_score': sum(s.lh_score_total for s in capital_sites) / len(capital_sites),
                'avg_price_per_py': sum(s.price_per_py for s in capital_sites) / len(capital_sites),
                'best_site': max(capital_sites, key=lambda x: x.lh_score_total).site_name
            }
        
        if local_sites:
            analysis['local'] = {
                'count': len(local_sites),
                'avg_lh_score': sum(s.lh_score_total for s in local_sites) / len(local_sites),
                'avg_price_per_py': sum(s.price_per_py for s in local_sites) / len(local_sites),
                'best_site': max(local_sites, key=lambda x: x.lh_score_total).site_name
            }
        
        return analysis


__all__ = ['MultiSiteComparisonEngine']
