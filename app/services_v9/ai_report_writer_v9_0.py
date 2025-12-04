"""
ZeroSite v9.0 - AI Report Writer
=================================

AI 기반 리포트 작성 엔진
GPT-4 / Claude 3.5 / Local LLM 지원

12개 섹션:
1. Executive Summary (임원 요약)
2. Site Overview (토지 개요)
3. Location Analysis (입지 분석)
4. Accessibility Assessment (접근성 평가)
5. Financial Analysis (재무 분석)
6. LH Evaluation (LH 평가)
7. Risk Assessment (리스크 평가)
8. Demand Analysis (수요 분석)
9. Construction Planning (건축 계획)
10. Investment Recommendation (투자 권고)
11. Implementation Timeline (실행 일정)
12. Appendix (부록)

Author: ZeroSite Development Team
Date: 2025-12-04
Version: v9.0
"""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
import logging
from datetime import datetime

from app.models_v9.standard_schema_v9_0 import StandardAnalysisOutput

logger = logging.getLogger(__name__)


@dataclass
class ReportSection:
    """리포트 섹션"""
    section_id: str
    title: str
    content: str
    subsections: Optional[List['ReportSection']] = None


@dataclass
class GeneratedReport:
    """생성된 리포트"""
    report_id: str
    title: str
    subtitle: str
    generated_at: str
    sections: List[ReportSection]
    metadata: Dict


class AIReportWriterV90:
    """
    AI Report Writer v9.0
    
    StandardAnalysisOutput을 받아 12개 섹션의 전문가 리포트 생성
    """
    
    # 12개 섹션 정의
    REPORT_SECTIONS = [
        {"id": "01_executive_summary", "title": "1. 임원 요약 (Executive Summary)"},
        {"id": "02_site_overview", "title": "2. 토지 개요 (Site Overview)"},
        {"id": "03_location_analysis", "title": "3. 입지 분석 (Location Analysis)"},
        {"id": "04_accessibility", "title": "4. 접근성 평가 (Accessibility Assessment)"},
        {"id": "05_financial", "title": "5. 재무 분석 (Financial Analysis)"},
        {"id": "06_lh_evaluation", "title": "6. LH 평가 (LH Evaluation)"},
        {"id": "07_risk_assessment", "title": "7. 리스크 평가 (Risk Assessment)"},
        {"id": "08_demand", "title": "8. 수요 분석 (Demand Analysis)"},
        {"id": "09_construction", "title": "9. 건축 계획 (Construction Planning)"},
        {"id": "10_recommendation", "title": "10. 투자 권고 (Investment Recommendation)"},
        {"id": "11_timeline", "title": "11. 실행 일정 (Implementation Timeline)"},
        {"id": "12_appendix", "title": "12. 부록 (Appendix)"}
    ]
    
    def __init__(
        self,
        ai_provider: Literal["gpt4", "claude", "local"] = "local",
        tone: Literal["professional", "technical", "executive"] = "professional"
    ):
        """
        AI Report Writer 초기화
        
        Args:
            ai_provider: AI 제공자 (gpt4/claude/local)
            tone: 리포트 톤 (professional/technical/executive)
        """
        self.ai_provider = ai_provider
        self.tone = tone
        
        logger.info(f"🤖 AI Report Writer v9.0 초기화")
        logger.info(f"   Provider: {ai_provider}")
        logger.info(f"   Tone: {tone}")
    
    def generate_report(
        self,
        analysis_output: StandardAnalysisOutput,
        report_title: Optional[str] = None
    ) -> GeneratedReport:
        """
        전체 리포트 생성
        
        Args:
            analysis_output: 분석 결과 (StandardAnalysisOutput)
            report_title: 리포트 제목 (선택사항)
            
        Returns:
            GeneratedReport: 생성된 리포트
        """
        logger.info(f"📝 리포트 생성 시작 (12개 섹션)")
        
        # 1. 리포트 메타데이터
        report_id = f"report_{analysis_output.analysis_id}"
        title = report_title or f"LH 신축매입임대 토지 진단 보고서"
        subtitle = f"{analysis_output.site_info.address}"
        
        # 2. 12개 섹션 생성
        sections = []
        for section_def in self.REPORT_SECTIONS:
            logger.info(f"   📄 생성: {section_def['title']}")
            section = self._generate_section(
                section_def["id"],
                section_def["title"],
                analysis_output
            )
            sections.append(section)
        
        # 3. 메타데이터
        metadata = {
            "analysis_id": analysis_output.analysis_id,
            "generated_at": datetime.now().isoformat(),
            "ai_provider": self.ai_provider,
            "tone": self.tone,
            "lh_score": analysis_output.lh_scores.total_score,
            "decision": analysis_output.final_recommendation.decision.value,
            "confidence": analysis_output.final_recommendation.confidence_level
        }
        
        logger.info(f"✅ 리포트 생성 완료: {report_id}")
        
        return GeneratedReport(
            report_id=report_id,
            title=title,
            subtitle=subtitle,
            generated_at=datetime.now().isoformat(),
            sections=sections,
            metadata=metadata
        )
    
    def _generate_section(
        self,
        section_id: str,
        section_title: str,
        analysis_output: StandardAnalysisOutput
    ) -> ReportSection:
        """
        개별 섹션 생성
        
        Args:
            section_id: 섹션 ID
            section_title: 섹션 제목
            analysis_output: 분석 결과
            
        Returns:
            ReportSection
        """
        # 섹션별 콘텐츠 생성
        if section_id == "01_executive_summary":
            content = self._write_executive_summary(analysis_output)
        elif section_id == "02_site_overview":
            content = self._write_site_overview(analysis_output)
        elif section_id == "03_location_analysis":
            content = self._write_location_analysis(analysis_output)
        elif section_id == "04_accessibility":
            content = self._write_accessibility(analysis_output)
        elif section_id == "05_financial":
            content = self._write_financial(analysis_output)
        elif section_id == "06_lh_evaluation":
            content = self._write_lh_evaluation(analysis_output)
        elif section_id == "07_risk_assessment":
            content = self._write_risk_assessment(analysis_output)
        elif section_id == "08_demand":
            content = self._write_demand(analysis_output)
        elif section_id == "09_construction":
            content = self._write_construction(analysis_output)
        elif section_id == "10_recommendation":
            content = self._write_recommendation(analysis_output)
        elif section_id == "11_timeline":
            content = self._write_timeline(analysis_output)
        else:  # 12_appendix
            content = self._write_appendix(analysis_output)
        
        return ReportSection(
            section_id=section_id,
            title=section_title,
            content=content
        )
    
    def _write_executive_summary(self, output: StandardAnalysisOutput) -> str:
        """1. 임원 요약"""
        decision = output.final_recommendation.decision.value
        confidence = output.final_recommendation.confidence_level
        lh_score = output.lh_scores.total_score
        lh_grade = output.lh_scores.grade.value
        
        return f"""
## 종합 의견
본 토지는 LH 신축매입임대 사업에 **{decision}** 등급으로 평가됩니다 (신뢰도: {confidence:.0f}%).

## 핵심 지표
- **LH 평가 점수**: {lh_score:.1f}/110점 (등급: {lh_grade})
- **재무 지표**: IRR {output.financial_result.irr_10yr:.1f}%, ROI {output.financial_result.roi_10yr:.1f}%
- **리스크 수준**: {output.risk_assessment.overall_risk_level}
- **수요 점수**: {output.demand_result.demand_score:.1f}/100점

## 주요 강점
{self._format_list(output.final_recommendation.key_strengths)}

## 주요 약점
{self._format_list(output.final_recommendation.key_weaknesses)}

## 실행 권고사항
{self._format_list(output.final_recommendation.action_items)}
""".strip()
    
    def _write_site_overview(self, output: StandardAnalysisOutput) -> str:
        """2. 토지 개요"""
        site = output.site_info
        
        return f"""
## 기본 정보
- **주소**: {site.address}
- **대지 면적**: {site.land_area:,.1f}㎡ ({site.land_area * 0.3025:.1f}평)
- **용도지역**: {site.zone_type}
- **토지 가격**: {site.total_land_price:,.0f}원 (평당 {site.land_appraisal_price * 0.3025:,.0f}원)

## 건축 규제
- **건폐율**: {site.building_coverage_ratio:.1f}%
- **용적률**: {site.floor_area_ratio:.1f}%
- **높이 제한**: {site.height_limit or '제한 없음'}

## 프로젝트 규모
- **계획 세대수**: {output.financial_result.unit_count}세대
- **분석 모드**: {output.financial_result.analysis_mode.value}
""".strip()
    
    def _write_location_analysis(self, output: StandardAnalysisOutput) -> str:
        """3. 입지 분석"""
        lh = output.lh_scores
        
        return f"""
## 입지 종합 평가
- **입지 점수**: {lh.location_score:.1f}/35점
- **접근성 등급**: {output.gis_result.accessibility_grade}
- **종합 접근성**: {output.gis_result.overall_accessibility_score:.1f}/100점

## 지하철 접근성
{self._format_poi_list(output.gis_result.subway_stations, "지하철역")}

## 학교 접근성
{self._format_poi_list(output.gis_result.elementary_schools, "초등학교")}

## 의료 시설
{self._format_poi_list(output.gis_result.hospitals, "병원")}

## 상업 시설
{self._format_poi_list(output.gis_result.supermarkets, "대형마트")}
""".strip()
    
    def _write_accessibility(self, output: StandardAnalysisOutput) -> str:
        """4. 접근성 평가"""
        return f"""
## 종합 접근성 평가
대상지의 전반적인 접근성은 **{output.gis_result.accessibility_grade}** 등급으로 평가됩니다.

## 교통 접근성
- 지하철역까지 최단 거리: {self._get_min_distance(output.gis_result.subway_stations)}
- 버스정류장까지 거리: {self._get_min_distance(output.gis_result.bus_stops)}

## 생활 편의 시설
- 대형마트: {self._get_min_distance(output.gis_result.supermarkets)}
- 병원: {self._get_min_distance(output.gis_result.hospitals)}
- 공원: {self._get_min_distance(output.gis_result.parks)}

## 교육 시설
- 초등학교: {self._get_min_distance(output.gis_result.elementary_schools)}
- 중학교: {self._get_min_distance(output.gis_result.middle_schools)}
- 고등학교: {self._get_min_distance(output.gis_result.high_schools)}
""".strip()
    
    def _write_financial(self, output: StandardAnalysisOutput) -> str:
        """5. 재무 분석"""
        fin = output.financial_result
        
        return f"""
## 투자 개요
- **총 투자액 (CAPEX)**: {fin.total_capex:,.0f}원
- **토지 가격**: {fin.total_land_price:,.0f}원
- **공사비**: {fin.total_construction_cost:,.0f}원 (단가: {fin.construction_cost_per_sqm:,.0f}원/㎡)

## 수익성 지표
- **연간 NOI**: {fin.annual_noi:,.0f}원
- **Cap Rate**: {fin.cap_rate:.2f}%
- **10년 ROI**: {fin.roi_10yr:.1f}%
- **10년 IRR**: {fin.irr_10yr:.1f}%
- **손익분기년도**: {fin.breakeven_year or 'N/A'}년

## LH 매입가 (50세대 이상)
{self._format_lh_purchase(fin)}

## 재무 등급
본 프로젝트의 재무 등급은 **{fin.overall_grade}**입니다.
""".strip()
    
    def _write_lh_evaluation(self, output: StandardAnalysisOutput) -> str:
        """6. LH 평가"""
        lh = output.lh_scores
        
        return f"""
## LH 신축매입임대 평가 (110점 만점)

### 종합 점수
- **총점**: {lh.total_score:.1f}/110점
- **등급**: {lh.grade.value}

### 세부 점수
- **입지 평가**: {lh.location_score:.1f}/35점
- **규모 평가**: {lh.scale_score:.1f}/20점
- **사업성 평가**: {lh.business_score:.1f}/40점
- **법규 평가**: {lh.regulation_score:.1f}/15점

### 평가 해석
{self._interpret_lh_score(lh)}
""".strip()
    
    def _write_risk_assessment(self, output: StandardAnalysisOutput) -> str:
        """7. 리스크 평가"""
        risk = output.risk_assessment
        
        return f"""
## 종합 리스크 평가
- **전체 위험도**: {risk.overall_risk_level}
- **평가 항목**: {risk.total_items}개
- **통과**: {risk.pass_count}개 | **경고**: {risk.warning_count}개 | **실패**: {risk.fail_count}개

## 중요 리스크 항목
{self._format_critical_risks(risk.critical_risks)}

## 리스크 완화 방안
{self._format_risk_mitigation(risk.critical_risks)}
""".strip()
    
    def _write_demand(self, output: StandardAnalysisOutput) -> str:
        """8. 수요 분석"""
        demand = output.demand_result
        
        return f"""
## 수요 분석 결과
- **수요 점수**: {demand.demand_score:.1f}/100점
- **수요 등급**: {demand.demand_grade}

## 인구 통계
- **총 인구**: {demand.population_total:,}명
- **가구 수**: {demand.household_count:,}가구
- **타겟 가구**: {demand.target_households:,}가구

## 추천 주택 유형
**{demand.recommended_unit_type}** 유형이 본 지역에 가장 적합합니다.
""".strip()
    
    def _write_construction(self, output: StandardAnalysisOutput) -> str:
        """9. 건축 계획"""
        site = output.site_info
        fin = output.financial_result
        
        return f"""
## 건축 개요
- **대지 면적**: {site.land_area:,.1f}㎡
- **건폐율**: {site.building_coverage_ratio:.1f}%
- **용적률**: {site.floor_area_ratio:.1f}%
- **계획 세대수**: {fin.unit_count}세대

## 건축 규모
- **연면적**: {site.land_area * site.floor_area_ratio / 100:,.1f}㎡
- **건축면적**: {site.land_area * site.building_coverage_ratio / 100:,.1f}㎡

## 세대 구성
{self._format_unit_distribution(fin.unit_type_distribution)}
""".strip()
    
    def _write_recommendation(self, output: StandardAnalysisOutput) -> str:
        """10. 투자 권고"""
        rec = output.final_recommendation
        
        return f"""
## 최종 투자 의견
**{rec.decision.value}** (신뢰도: {rec.confidence_level:.0f}%)

{rec.executive_summary}

## 투자 결정 근거
### 강점
{self._format_list(rec.key_strengths)}

### 약점
{self._format_list(rec.key_weaknesses)}

## 실행 계획
{self._format_list(rec.action_items)}
""".strip()
    
    def _write_timeline(self, output: StandardAnalysisOutput) -> str:
        """11. 실행 일정"""
        return f"""
## 프로젝트 실행 일정 (예상)

### Phase 1: 사전 준비 (1-2개월)
- 토지 매입 계약
- LH 사전 협의
- 인허가 서류 준비

### Phase 2: 설계 및 인허가 (3-6개월)
- 건축 설계
- 인허가 신청 및 승인
- 시공사 선정

### Phase 3: 건축 공사 (12-18개월)
- 착공
- 골조 공사
- 마감 공사

### Phase 4: 준공 및 입주 (2-3개월)
- 준공 검사
- LH 매입 절차
- 입주민 모집

**총 예상 기간**: 약 18-29개월
""".strip()
    
    def _write_appendix(self, output: StandardAnalysisOutput) -> str:
        """12. 부록"""
        return f"""
## 분석 정보
- **Analysis ID**: {output.analysis_id}
- **분석 버전**: {output.version}
- **분석 시간**: {output.timestamp}
- **처리 시간**: {output.processing_time_seconds:.2f}초

## 데이터 출처
- POI 데이터: Kakao Maps API
- LH 평가 기준: LH 신축매입임대 공식 기준 (2025년)
- 재무 가정: 시장 평균 기준

## 면책 사항
본 보고서는 제공된 정보를 바탕으로 작성되었으며, 실제 사업 추진 시 추가적인 실사 및 검증이 필요합니다.
""".strip()
    
    # Helper Methods
    
    def _format_list(self, items: List[str]) -> str:
        """리스트 포맷팅"""
        if not items:
            return "- 없음"
        return "\n".join(f"- {item}" for item in items)
    
    def _format_poi_list(self, pois, category_name: str) -> str:
        """POI 리스트 포맷팅"""
        if not pois:
            return f"- {category_name}: 정보 없음"
        
        poi = pois[0]  # 가장 가까운 것
        return f"- **{poi.name}**: {poi.distance_display} (도보 {poi.walk_time_min or 'N/A'}분, {poi.interpretation})"
    
    def _get_min_distance(self, pois) -> str:
        """최소 거리 추출"""
        if not pois:
            return "정보 없음"
        return pois[0].distance_display
    
    def _format_lh_purchase(self, fin) -> str:
        """LH 매입가 포맷팅"""
        if fin.lh_purchase_price:
            return f"- **LH 매입가**: {fin.lh_purchase_price:,.0f}원 (단가: {fin.lh_purchase_price_per_sqm:,.0f}원/㎡)"
        return "- LH 매입가: 50세대 미만으로 해당 없음"
    
    def _interpret_lh_score(self, lh) -> str:
        """LH 점수 해석"""
        score = lh.total_score
        if score >= 90:
            return "매우 우수한 사업지로, LH 신청 시 높은 경쟁력을 보유하고 있습니다."
        elif score >= 75:
            return "우수한 사업지로, LH 신청 시 긍정적인 평가를 받을 것으로 예상됩니다."
        elif score >= 60:
            return "양호한 수준으로, 일부 개선 후 LH 신청이 가능합니다."
        else:
            return "개선이 필요한 수준으로, 사업지 재검토 또는 대폭적인 계획 변경이 필요합니다."
    
    def _format_critical_risks(self, risks) -> str:
        """중요 리스크 포맷팅"""
        if not risks:
            return "- 중요 리스크 없음"
        
        lines = []
        for risk in risks[:5]:  # 상위 5개
            lines.append(f"- **[{risk.id}] {risk.name}** ({risk.severity.value}): {risk.description}")
        return "\n".join(lines)
    
    def _format_risk_mitigation(self, risks) -> str:
        """리스크 완화 방안 포맷팅"""
        if not risks:
            return "- 없음"
        
        lines = []
        for risk in risks[:5]:
            if risk.mitigation:
                lines.append(f"- **{risk.name}**: {risk.mitigation}")
        return "\n".join(lines) if lines else "- 없음"
    
    def _format_unit_distribution(self, distribution: Dict[str, int]) -> str:
        """세대 구성 포맷팅"""
        if not distribution:
            return "- 정보 없음"
        
        lines = []
        for unit_type, count in distribution.items():
            lines.append(f"- {unit_type}: {count}세대")
        return "\n".join(lines)
