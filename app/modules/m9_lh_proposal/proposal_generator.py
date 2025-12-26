"""
ZeroSite v4.0 LH Proposal Generator
====================================

LH 공식 제안서 통합 생성기

Author: ZeroSite M9 Team
Date: 2025-12-26
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

from app.modules.m9_lh_proposal.document_builder import LHDocumentBuilder
from app.modules.m9_lh_proposal.pdf_converter import PDFConverter
from app.modules.m9_lh_proposal.attachment_manager import AttachmentManager


class LHProposalGenerator:
    """LH 제안서 통합 생성기"""
    
    def __init__(self, output_dir: str = "output/proposals"):
        """초기화"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*80)
        print("  ZeroSite v4.0 M9 LH Proposal Generator")
        print("  LH 공식 제안서 자동 생성 시스템")
        print("="*80 + "\n")
    
    def generate_full_proposal(
        self,
        land_ctx: Any,
        appraisal_ctx: Any,
        housing_type_ctx: Any,
        capacity_ctx: Any,
        feasibility_ctx: Any,
        m6_result: Any,
        format: str = "both"  # "word", "pdf", "both"
    ) -> Dict[str, str]:
        """
        전체 제안서 생성
        
        Args:
            land_ctx: M1 토지 정보
            appraisal_ctx: M2 감정평가 결과
            housing_type_ctx: M3 세대 유형
            capacity_ctx: M4 건축 규모
            feasibility_ctx: M5 사업성 분석
            m6_result: M6 종합 평가
            format: 출력 형식 ("word", "pdf", "both")
        
        Returns:
            생성된 파일 경로 딕셔너리
        """
        print("\n" + "="*80)
        print("  LH 제안서 생성 시작")
        print("="*80 + "\n")
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_name = f"LH_Proposal_{land_ctx.parcel_id}_{timestamp}"
        
        result = {
            "word_path": None,
            "pdf_path": None,
            "attachments": [],
            "package_path": None
        }
        
        # 1. Word 문서 생성
        if format in ["word", "both"]:
            print("[STEP 1] Word 문서 생성 중...")
            word_path = self._generate_word_document(
                base_name,
                land_ctx,
                appraisal_ctx,
                housing_type_ctx,
                capacity_ctx,
                feasibility_ctx,
                m6_result
            )
            result["word_path"] = word_path
            print(f"✓ Word 문서 완료: {word_path}\n")
        
        # 2. PDF 문서 생성
        if format in ["pdf", "both"]:
            print("[STEP 2] PDF 문서 생성 중...")
            pdf_path = self._generate_pdf_document(
                base_name,
                land_ctx,
                appraisal_ctx,
                housing_type_ctx,
                capacity_ctx,
                feasibility_ctx,
                m6_result
            )
            result["pdf_path"] = pdf_path
            print(f"✓ PDF 문서 완료: {pdf_path}\n")
        
        # 3. 첨부 서류 생성
        print("[STEP 3] 첨부 서류 생성 중...")
        attachments = self._generate_attachments(
            base_name,
            land_ctx,
            appraisal_ctx,
            capacity_ctx,
            feasibility_ctx,
            m6_result
        )
        result["attachments"] = attachments
        print(f"✓ 첨부 서류 {len(attachments)}개 완료\n")
        
        # 4. 제출 패키지 생성
        print("[STEP 4] 제출 패키지 번들링 중...")
        main_doc = result["word_path"] if result["word_path"] else result["pdf_path"]
        if main_doc:
            package_path = self._create_submission_package(
                base_name,
                main_doc,
                attachments
            )
            result["package_path"] = package_path
            print(f"✓ 제출 패키지 완료: {package_path}\n")
        
        print("="*80)
        print("  LH 제안서 생성 완료")
        print("="*80)
        print(f"Word 문서: {result['word_path']}")
        print(f"PDF 문서: {result['pdf_path']}")
        print(f"첨부 파일: {len(result['attachments'])}개")
        print(f"제출 패키지: {result['package_path']}")
        print("="*80 + "\n")
        
        return result
    
    def _generate_word_document(
        self,
        base_name: str,
        land_ctx: Any,
        appraisal_ctx: Any,
        housing_type_ctx: Any,
        capacity_ctx: Any,
        feasibility_ctx: Any,
        m6_result: Any
    ) -> str:
        """Word 문서 생성"""
        builder = LHDocumentBuilder()
        
        # 표지
        builder.add_cover_page(
            title="LH 매입임대주택 사업 제안서",
            address=land_ctx.address,
            parcel_id=land_ctx.parcel_id,
            submitted_by="ZeroSite",
            submission_date=datetime.now().strftime("%Y년 %m월 %d일")
        )
        
        # 1. 사업 개요
        builder.add_section_title("1. 사업 개요")
        builder.add_paragraph(
            f"본 제안서는 {land_ctx.address} 부지를 대상으로 한 "
            f"LH 매입임대주택 사업의 타당성을 검토한 결과입니다."
        )
        builder.add_paragraph(
            f"대상 부지는 {land_ctx.zone_type}에 위치하며, "
            f"총 면적 {land_ctx.area_sqm:,.2f}m² ({land_ctx.area_pyeong:,.2f}평)입니다."
        )
        
        # 부지 정보 테이블
        builder.add_section_title("2. 부지 정보", level=2)
        site_info = {
            "주소": land_ctx.address,
            "필지번호": land_ctx.parcel_id,
            "면적 (㎡)": f"{land_ctx.area_sqm:,.2f}",
            "면적 (평)": f"{land_ctx.area_pyeong:,.2f}",
            "용도지역": land_ctx.zone_type,
            "법정 용적률": f"{land_ctx.far}%",
            "법정 건폐율": f"{land_ctx.bcr}%",
            "도로 폭": f"{land_ctx.road_width}m"
        }
        builder.add_key_value_table(site_info)
        
        # 감정평가 결과
        builder.add_section_title("3. 감정평가 결과", level=2)
        appraisal_info = {
            "감정평가액": f"₩{appraisal_ctx.land_value:,}",
            "㎡당 단가": f"₩{appraisal_ctx.unit_price_sqm:,}",
            "평당 단가": f"₩{appraisal_ctx.unit_price_pyeong:,}",
            "거래사례 수": f"{appraisal_ctx.transaction_count}건",
            "신뢰도": appraisal_ctx.confidence_level
        }
        builder.add_key_value_table(appraisal_info)
        
        # 세대 유형
        builder.add_section_title("4. 선정 세대 유형", level=2)
        builder.add_paragraph(
            f"선정된 세대 유형: {housing_type_ctx.selected_type_name}",
            bold=True
        )
        builder.add_paragraph(f"선정 신뢰도: {housing_type_ctx.selection_confidence:.1%}")
        builder.add_paragraph(f"수요 예측: {housing_type_ctx.demand_prediction:.1f}점")
        builder.add_paragraph(f"수요 추세: {housing_type_ctx.demand_trend}")
        
        # 건축 규모
        builder.add_section_title("5. 건축 가능 규모", level=2)
        builder.add_capacity_table(
            legal_units=capacity_ctx.legal_capacity.total_units,
            incentive_units=capacity_ctx.incentive_capacity.total_units,
            legal_gfa=capacity_ctx.legal_capacity.target_gfa_sqm,
            incentive_gfa=capacity_ctx.incentive_capacity.target_gfa_sqm,
            legal_far=capacity_ctx.input_legal_far,
            incentive_far=capacity_ctx.input_incentive_far
        )
        
        # 재무 분석
        builder.add_section_title("6. 재무 분석", level=2)
        builder.add_financial_summary_table(
            land_value=int(appraisal_ctx.land_value),
            construction_cost=int(feasibility_ctx.cost_breakdown.construction_cost),
            total_cost=int(feasibility_ctx.cost_breakdown.total_cost),
            total_revenue=int(feasibility_ctx.revenue_projection.total_revenue),
            npv=int(feasibility_ctx.financial_metrics.npv_public),
            irr=feasibility_ctx.financial_metrics.irr_public
        )
        
        # LH 종합 평가
        builder.add_section_title("7. LH 종합 평가", level=2)
        
        section_scores = {
            "A": m6_result.section_a_policy.weighted_score,
            "B": m6_result.section_b_location.weighted_score,
            "C": m6_result.section_c_construction.weighted_score,
            "D": m6_result.section_d_price.weighted_score,
            "E": m6_result.section_e_business.weighted_score
        }
        
        builder.add_lh_scorecard_table(
            section_scores=section_scores,
            total_score=m6_result.lh_score_total,
            judgement=m6_result.judgement.value,
            grade=m6_result.grade.value
        )
        
        # 개선 방안
        if m6_result.improvement_points:
            builder.add_section_title("8. 개선 방안", level=2)
            builder.add_bullet_list(m6_result.improvement_points)
        
        # 결론
        builder.add_section_title("9. 결론 및 제안")
        
        if m6_result.judgement.value == "GO":
            conclusion = "본 부지는 LH 매입임대주택 사업에 적합한 것으로 판단됩니다. 즉시 사업 추진을 권장합니다."
        elif m6_result.judgement.value == "CONDITIONAL":
            conclusion = "본 부지는 일부 개선이 필요하나 조건부로 사업 추진이 가능한 것으로 판단됩니다."
        else:
            conclusion = "현재 상태로는 사업 추진이 어려운 것으로 판단됩니다. 근본적인 개선 또는 대안 검토가 필요합니다."
        
        builder.add_paragraph(conclusion)
        
        # 저장
        file_path = os.path.join(self.output_dir, f"{base_name}.docx")
        return builder.save(file_path)
    
    def _generate_pdf_document(
        self,
        base_name: str,
        land_ctx: Any,
        appraisal_ctx: Any,
        housing_type_ctx: Any,
        capacity_ctx: Any,
        feasibility_ctx: Any,
        m6_result: Any
    ) -> str:
        """PDF 문서 생성"""
        converter = PDFConverter()
        
        # 표지
        converter.add_cover_page(
            title="LH 매입임대주택 사업 제안서",
            address=land_ctx.address,
            parcel_id=land_ctx.parcel_id,
            submitted_by="ZeroSite",
            submission_date=datetime.now().strftime("%Y년 %m월 %d일")
        )
        
        # 1. 사업 개요
        converter.add_section_title("1. 사업 개요")
        converter.add_paragraph(
            f"본 제안서는 {land_ctx.address} 부지를 대상으로 한 "
            f"LH 매입임대주택 사업의 타당성을 검토한 결과입니다."
        )
        
        # 2. 부지 정보
        converter.add_subsection_title("2. 부지 정보")
        site_info = {
            "주소": land_ctx.address,
            "필지번호": land_ctx.parcel_id,
            "면적 (㎡)": f"{land_ctx.area_sqm:,.2f}",
            "면적 (평)": f"{land_ctx.area_pyeong:,.2f}",
            "용도지역": land_ctx.zone_type,
            "법정 용적률": f"{land_ctx.far}%",
            "법정 건폐율": f"{land_ctx.bcr}%"
        }
        converter.add_key_value_table(site_info)
        
        # 3. 감정평가
        converter.add_subsection_title("3. 감정평가 결과")
        appraisal_info = {
            "감정평가액": f"₩{appraisal_ctx.land_value:,}",
            "㎡당 단가": f"₩{appraisal_ctx.unit_price_sqm:,}",
            "평당 단가": f"₩{appraisal_ctx.unit_price_pyeong:,}",
            "신뢰도": appraisal_ctx.confidence_level
        }
        converter.add_key_value_table(appraisal_info)
        
        # 4. 재무 분석
        converter.add_financial_summary(
            land_value=int(appraisal_ctx.land_value),
            construction_cost=int(feasibility_ctx.cost_breakdown.construction_cost),
            total_cost=int(feasibility_ctx.cost_breakdown.total_cost),
            total_revenue=int(feasibility_ctx.revenue_projection.total_revenue),
            npv=int(feasibility_ctx.financial_metrics.npv_public),
            irr=feasibility_ctx.financial_metrics.irr_public
        )
        
        # 5. LH 종합 평가
        section_scores = {
            "A": m6_result.section_a_policy.weighted_score,
            "B": m6_result.section_b_location.weighted_score,
            "C": m6_result.section_c_construction.weighted_score,
            "D": m6_result.section_d_price.weighted_score,
            "E": m6_result.section_e_business.weighted_score
        }
        
        converter.add_lh_scorecard(
            section_scores=section_scores,
            total_score=m6_result.lh_score_total,
            judgement=m6_result.judgement.value,
            grade=m6_result.grade.value
        )
        
        # 6. 개선 방안
        if m6_result.improvement_points:
            converter.add_subsection_title("개선 방안")
            converter.add_bullet_list(m6_result.improvement_points)
        
        # 저장
        file_path = os.path.join(self.output_dir, f"{base_name}.pdf")
        return converter.build(file_path)
    
    def _generate_attachments(
        self,
        base_name: str,
        land_ctx: Any,
        appraisal_ctx: Any,
        capacity_ctx: Any,
        feasibility_ctx: Any,
        m6_result: Any
    ) -> list:
        """첨부 서류 생성"""
        manager = AttachmentManager(self.output_dir)
        
        attachments = []
        
        # 1. 부지 정보 시트
        site_sheet = manager.create_site_info_sheet(
            f"{base_name}_부지정보.xlsx",
            land_ctx,
            appraisal_ctx
        )
        attachments.append(site_sheet)
        
        # 2. 재무 분석 시트
        financial_sheet = manager.create_financial_sheet(
            f"{base_name}_재무분석.xlsx",
            feasibility_ctx
        )
        attachments.append(financial_sheet)
        
        # 3. 건축 규모 시트
        capacity_sheet = manager.create_capacity_sheet(
            f"{base_name}_건축규모.xlsx",
            capacity_ctx
        )
        attachments.append(capacity_sheet)
        
        # 4. M6 평가 JSON
        m6_json = manager.create_m6_report_json(
            f"{base_name}_LH평가.json",
            m6_result
        )
        attachments.append(m6_json)
        
        return attachments
    
    def _create_submission_package(
        self,
        base_name: str,
        main_doc_path: str,
        attachments: list
    ) -> str:
        """제출 패키지 생성"""
        manager = AttachmentManager(self.output_dir)
        
        # 첨부 파일 등록
        for attachment in attachments:
            manager.attachments.append(attachment)
        
        # ZIP 생성
        return manager.create_submission_package(
            f"{base_name}_제출패키지.zip",
            main_doc_path
        )


__all__ = ['LHProposalGenerator']
