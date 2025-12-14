"""
ZeroSite v40.5 - LH Submission Report Generator
LH 제출용 보고서 (10~15 페이지)

목적: LH 공사 사전심사 공식 제출용 보고서
대상: LH 공사 담당자
페이지: 10~15 pages
핵심 내용:
- 사업 개요
- 토지 감정평가 (상세)
- 토지 진단
- 규모 검토
- 시나리오 분석 (A/B/C)
- LH 심사예측 (AI Judge) - 핵심
- 종합 결론 및 권고사항

Created: 2025-12-14
"""

from typing import Dict, List
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from .base_report_generator import BaseReportGenerator


class LHSubmissionGenerator(BaseReportGenerator):
    """LH 제출용 보고서 생성기 (10~15p)"""
    
    def generate(self, context: Dict) -> bytes:
        """
        LH 제출용 보고서 생성
        
        Args:
            context: v40.3 full context
            
        Returns:
            bytes: PDF file bytes
        """
        buffer = io.BytesIO()
        self.pdf = canvas.Canvas(buffer, pagesize=A4)
        
        # Page 1: Cover
        self.draw_cover_page(
            "LH 공공주택 사전심사",
            "토지 분석 및 심사예측 보고서",
            context
        )
        
        # Page 2: Table of Contents
        self._page_2_toc()
        
        # Page 3: 사업 개요
        self._page_3_project_overview(context)
        
        # Page 4-5: 토지 감정평가
        self._page_4_5_appraisal(context)
        
        # Page 6: 토지 진단
        self._page_6_diagnosis(context)
        
        # Page 7: 규모 검토
        self._page_7_capacity(context)
        
        # Page 8-9: 시나리오 분석
        self._page_8_9_scenarios(context)
        
        # Page 10-11: LH 심사예측 (핵심)
        self._page_10_11_lh_review(context)
        
        # Page 12: 종합 결론
        self._page_12_conclusion(context)
        
        # Finalize
        self.pdf.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    # ============================================
    # Page 2: Table of Contents
    # ============================================
    
    def _page_2_toc(self):
        """목차"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("목차 (Table of Contents)", "Page 2")
        
        toc_items = [
            ("1. 사업 개요", "3"),
            ("2. 토지 감정평가", "4-5"),
            ("   2.1 감정가 산정", "4"),
            ("   2.2 거래사례 분석", "5"),
            ("3. 토지 진단", "6"),
            ("   3.1 용도지역 및 규제", "6"),
            ("   3.2 정책 적합성", "6"),
            ("4. 규모 검토", "7"),
            ("   4.1 건폐율/용적률", "7"),
            ("   4.2 예상 세대수", "7"),
            ("5. 시나리오 분석", "8-9"),
            ("   5.1 시나리오 A/B/C", "8"),
            ("   5.2 정책 점수 비교", "9"),
            ("6. LH 심사예측 (AI Judge)", "10-11"),
            ("   6.1 통과 확률 예측", "10"),
            ("   6.2 평가요소 분석", "11"),
            ("7. 종합 결론 및 권고사항", "12"),
        ]
        
        self.y_position -= 10*mm
        
        for item, page in toc_items:
            self.pdf.setFont(self.korean_font, 11)
            self.pdf.setFillColorRGB(0, 0, 0)
            self.pdf.drawString(self.margin + 5*mm, self.y_position, item)
            
            self.pdf.setFillColorRGB(*self.COLOR_GREY)
            self.pdf.drawRightString(self.width - self.margin - 5*mm, self.y_position, page)
            
            self.y_position -= 7*mm
        
        self.draw_page_footer("2", "12")
        self.pdf.showPage()
    
    # ============================================
    # Page 3: 사업 개요
    # ============================================
    
    def _page_3_project_overview(self, context: Dict):
        """사업 개요"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("1. 사업 개요", "Page 3/12")
        
        input_data = context.get("input", {})
        appraisal = context.get("appraisal", {})
        
        # 1.1 대상 토지
        self.draw_subsection("1.1 대상 토지")
        
        land_data = [
            ["항목", "내용"],
            ["소재지", input_data.get("address", "정보 없음")],
            ["대지면적", f"{input_data.get('land_area_sqm', 0):,.2f} ㎡"],
            ["평형", f"{input_data.get('land_area_sqm', 0) / 3.3058:,.1f} 평"],
            ["용도지역", appraisal.get("zoning", {}).get("zone_type", "정보 없음")],
            ["감정평가액", self.format_currency(appraisal.get("final_value", 0))],
        ]
        
        self.draw_simple_table(land_data, 150*mm)
        self.y_position -= 40*mm
        
        # 1.2 사업 목적
        self.draw_subsection("1.2 사업 목적")
        self.y_position -= 3*mm
        
        purpose_text = "본 사업은 LH 공공주택 사전심사를 위한 토지 분석 및 개발 타당성 검토를 목적으로 합니다. "
        purpose_text += "AI 기반 심사예측 시스템을 통해 사전심사 통과 가능성을 분석하고, "
        purpose_text += "최적의 주택 유형 및 개발 규모를 제안합니다."
        
        self.draw_text_block(purpose_text)
        
        self.y_position -= 10*mm
        
        # 1.3 분석 일시
        self.draw_subsection("1.3 분석 정보")
        self.y_position -= 3*mm
        
        analysis_data = [
            ["항목", "내용"],
            ["분석 일시", context.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M"))],
            ["분석 시스템", "ZeroSite v40.5 AI 기반 토지 분석"],
            ["Context ID", context.get("context_id", "N/A")[:24] + "..."],
            ["보고서 유형", "LH 제출용 (LH Submission)"],
        ]
        
        self.draw_simple_table(analysis_data, 150*mm)
        
        self.draw_page_footer("3", "12")
        self.pdf.showPage()
    
    # ============================================
    # Page 4-5: 토지 감정평가
    # ============================================
    
    def _page_4_5_appraisal(self, context: Dict):
        """토지 감정평가"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("2. 토지 감정평가", "Page 4/12")
        
        appraisal = context.get("appraisal", {})
        
        # 2.1 감정가 산정
        self.draw_subsection("2.1 감정가 산정 결과")
        self.y_position -= 5*mm
        
        # Key metrics
        final_value = appraisal.get("final_value", 0)
        value_per_sqm = appraisal.get("value_per_sqm", 0)
        land_area = context.get("input", {}).get("land_area_sqm", 0)
        
        metrics_y = self.y_position
        
        # Metric boxes
        self.draw_metric_box(
            self.margin,
            metrics_y,
            55*mm,
            self.format_currency(final_value),
            "총 감정가"
        )
        
        self.draw_metric_box(
            self.margin + 60*mm,
            metrics_y,
            55*mm,
            f"{value_per_sqm * 3.3058:,.0f} 원/평",
            "평당 가격"
        )
        
        self.draw_metric_box(
            self.margin + 120*mm,
            metrics_y,
            55*mm,
            f"{value_per_sqm:,.0f} 원/㎡",
            "제곱미터당"
        )
        
        self.y_position -= 25*mm
        
        # 감정평가 방식
        self.draw_subsection("2.2 감정평가 방식")
        self.y_position -= 3*mm
        
        approaches = appraisal.get("approaches", {})
        approach_text = f"본 감정평가는 "
        
        if approaches.get("comparison"):
            approach_text += "거래사례비교법, "
        if approaches.get("cost"):
            approach_text += "원가방식, "
        if approaches.get("income"):
            approach_text += "수익환원법을 "
        
        approach_text += "종합적으로 적용하여 산정하였습니다."
        
        self.draw_text_block(approach_text)
        
        self.y_position -= 10*mm
        
        # 공시지가 및 프리미엄
        self.draw_subsection("2.3 공시지가 및 프리미엄")
        self.y_position -= 3*mm
        
        premium_data = [
            ["항목", "금액/비율"],
            ["공시지가", self.format_currency(appraisal.get("official_price", 0))],
            ["프리미엄", f"{appraisal.get('premium', {}).get('score', 0):.1f}%"],
            ["최종 감정가", self.format_currency(final_value)],
        ]
        
        self.draw_simple_table(premium_data, 150*mm)
        
        self.draw_page_footer("4", "12")
        self.pdf.showPage()
        
        # Page 5: 거래사례
        self.y_position = self.height - self.margin
        self.draw_page_header("2. 토지 감정평가 (계속)", "Page 5/12")
        
        self.draw_subsection("2.4 거래사례 분석")
        self.y_position -= 5*mm
        
        transactions = appraisal.get("transactions", [])
        
        if transactions and len(transactions) >= 3:
            trans_data = [["거래일", "거리", "면적(㎡)", "거래가(억원)"]]
            
            for trans in transactions[:5]:  # Top 5
                date = trans.get("date", "N/A")
                distance = trans.get("distance", 0)
                area = trans.get("area", 0)
                price = trans.get("price", 0)
                
                trans_data.append([
                    date[:10] if len(date) > 10 else date,
                    f"{distance:.0f}m",
                    f"{area:,.0f}",
                    f"{price/100000000:,.1f}"
                ])
            
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            
            table = Table(trans_data, colWidths=[40*mm, 30*mm, 35*mm, 45*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*self.COLOR_TABLE_HEADER)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(*self.COLOR_PRIMARY)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.korean_font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            table_width, table_height = table.wrapOn(self.pdf, 150*mm, 200*mm)
            table.drawOn(self.pdf, self.margin, self.y_position - table_height)
            self.y_position -= table_height + 5*mm
        else:
            self.pdf.setFont(self.korean_font, 9)
            self.pdf.drawString(self.margin, self.y_position, "거래사례 데이터가 충분하지 않습니다.")
            self.y_position -= 10*mm
        
        self.draw_page_footer("5", "12")
        self.pdf.showPage()
    
    # ============================================
    # Page 6: 토지 진단
    # ============================================
    
    def _page_6_diagnosis(self, context: Dict):
        """토지 진단"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("3. 토지 진단", "Page 6/12")
        
        diagnosis = context.get("diagnosis", {})
        appraisal = context.get("appraisal", {})
        
        # 3.1 용도지역 및 규제
        self.draw_subsection("3.1 용도지역 및 규제사항")
        self.y_position -= 5*mm
        
        zone_type = appraisal.get("zoning", {}).get("zone_type", "정보 없음")
        far = appraisal.get("zoning", {}).get("far", 0)
        bcr = appraisal.get("zoning", {}).get("bcr", 0)
        
        zoning_data = [
            ["항목", "내용"],
            ["용도지역", zone_type],
            ["용적률", f"{far}%"],
            ["건폐율", f"{bcr}%"],
            ["개발 적합성", diagnosis.get("suitability", "검토 필요")],
        ]
        
        self.draw_simple_table(zoning_data, 150*mm)
        self.y_position -= 35*mm
        
        # 3.2 정책 적합성
        self.draw_subsection("3.2 정책 적합성 평가")
        self.y_position -= 3*mm
        
        suitability = diagnosis.get("suitability", "검토 필요")
        
        if "적합" in suitability:
            color = self.COLOR_SUCCESS
            assessment = "본 토지는 LH 공공주택 개발에 적합한 것으로 판단됩니다."
        elif "조건부" in suitability:
            color = self.COLOR_WARNING
            assessment = "일부 조건을 충족하면 개발 가능합니다."
        else:
            color = self.COLOR_DANGER
            assessment = "추가 검토가 필요합니다."
        
        self.pdf.setFillColorRGB(*color)
        self.pdf.setFont(self.korean_font_bold, 11)
        self.pdf.drawString(self.margin, self.y_position, f"평가 결과: {suitability}")
        
        self.y_position -= 8*mm
        
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.setFont(self.korean_font, 10)
        self.draw_text_block(assessment)
        
        self.draw_page_footer("6", "12")
        self.pdf.showPage()
    
    # ============================================
    # Page 7: 규모 검토
    # ============================================
    
    def _page_7_capacity(self, context: Dict):
        """규모 검토"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("4. 규모 검토", "Page 7/12")
        
        capacity = context.get("capacity", {})
        
        # 4.1 건축 규모
        self.draw_subsection("4.1 건축 규모 산정")
        self.y_position -= 5*mm
        
        capacity_data = [
            ["항목", "수치"],
            ["최대 건축면적", f"{capacity.get('max_building_area', 0):,.0f} ㎡"],
            ["최대 연면적", f"{capacity.get('max_floor_area', 0):,.0f} ㎡"],
            ["예상 세대수", f"{capacity.get('max_units', 0)} 세대"],
            ["용적률 활용", f"{capacity.get('far', 0)}%"],
            ["건폐율 활용", f"{capacity.get('bcr', 0)}%"],
        ]
        
        self.draw_simple_table(capacity_data, 150*mm)
        self.y_position -= 40*mm
        
        # 4.2 세대 구성
        self.draw_subsection("4.2 예상 세대 구성")
        self.y_position -= 3*mm
        
        max_units = capacity.get('max_units', 0)
        
        unit_text = f"본 토지의 최대 개발 가능 세대수는 약 {max_units}세대입니다. "
        unit_text += "이는 건폐율 및 용적률을 최대한 활용한 경우이며, "
        unit_text += "실제 개발 시 주차장, 공용시설 등을 고려하여 조정될 수 있습니다."
        
        self.draw_text_block(unit_text)
        
        self.draw_page_footer("7", "12")
        self.pdf.showPage()
    
    # ============================================
    # Page 8-9: 시나리오 분석
    # ============================================
    
    def _page_8_9_scenarios(self, context: Dict):
        """시나리오 분석"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("5. 시나리오 분석", "Page 8/12")
        
        scenario = context.get("scenario", {})
        scenarios = scenario.get("scenarios", [])
        
        # 5.1 시나리오 개요
        self.draw_subsection("5.1 시나리오 A/B/C 비교")
        self.y_position -= 5*mm
        
        if scenarios and len(scenarios) >= 3:
            scenario_data = [["시나리오", "유형", "세대수", "정책점수", "IRR"]]
            
            for idx, scen in enumerate(scenarios[:3]):
                name = scen.get("name", f"시나리오 {idx+1}")
                unit_type = scen.get("unit_type", "N/A")
                units = scen.get("unit_count", 0)
                policy = scen.get("policy_score", 0)
                irr = scen.get("irr", 0)
                
                scenario_data.append([
                    name[:10],
                    unit_type,
                    f"{units}세대",
                    f"{policy}점",
                    f"{irr:.1f}%"
                ])
            
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            
            table = Table(scenario_data, colWidths=[40*mm, 30*mm, 30*mm, 30*mm, 30*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*self.COLOR_TABLE_HEADER)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(*self.COLOR_PRIMARY)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.korean_font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            table_width, table_height = table.wrapOn(self.pdf, 160*mm, 200*mm)
            table.drawOn(self.pdf, self.margin, self.y_position - table_height)
            self.y_position -= table_height + 10*mm
        
        # 5.2 추천 시나리오
        recommended = scenario.get("recommended", "정보 없음")
        
        self.draw_subsection("5.2 추천 시나리오")
        self.y_position -= 3*mm
        
        self.pdf.setFillColorRGB(*self.COLOR_PRIMARY)
        self.pdf.setFont(self.korean_font_bold, 12)
        self.pdf.drawString(self.margin, self.y_position, f"✓ 추천: {recommended}")
        
        self.y_position -= 10*mm
        
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.setFont(self.korean_font, 10)
        rec_text = "정책 점수, 수익률, 리스크를 종합적으로 고려한 결과입니다."
        self.draw_text_block(rec_text)
        
        self.draw_page_footer("8", "12")
        self.pdf.showPage()
        
        # Page 9: 시나리오 상세
        self.y_position = self.height - self.margin
        self.draw_page_header("5. 시나리오 분석 (계속)", "Page 9/12")
        
        self.draw_subsection("5.3 시나리오별 상세 분석")
        self.y_position -= 5*mm
        
        for idx, scen in enumerate(scenarios[:3], 1):
            name = scen.get("name", f"시나리오 {idx}")
            
            self.pdf.setFont(self.korean_font_bold, 10)
            self.pdf.drawString(self.margin, self.y_position, f"• {name}")
            self.y_position -= 6*mm
            
            details = f"  - 세대수: {scen.get('unit_count', 0)}세대"
            details += f", 평형: {scen.get('unit_size', 0)}㎡"
            details += f", 정책점수: {scen.get('policy_score', 0)}점"
            
            self.pdf.setFont(self.korean_font, 9)
            self.pdf.drawString(self.margin + 5*mm, self.y_position, details)
            self.y_position -= 8*mm
        
        self.draw_page_footer("9", "12")
        self.pdf.showPage()
    
    # ============================================
    # Page 10-11: LH 심사예측 (핵심)
    # ============================================
    
    def _page_10_11_lh_review(self, context: Dict):
        """LH 심사예측 - 보고서의 핵심"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("6. LH 심사예측 (AI Judge)", "Page 10/12")
        
        lh_review = context.get("lh_review", {})
        
        if not lh_review:
            self.pdf.setFont(self.korean_font, 11)
            self.pdf.drawString(self.margin, self.y_position,
                              "LH 심사예측 데이터가 없습니다.")
            self.draw_page_footer("10", "12")
            self.pdf.showPage()
            return
        
        # 6.1 종합 예측 결과
        self.draw_subsection("6.1 종합 예측 결과")
        self.y_position -= 5*mm
        
        score = lh_review.get("predicted_score", 0)
        probability = lh_review.get("pass_probability", 0)
        risk_level = lh_review.get("risk_level", "MEDIUM")
        
        # Metric boxes
        metrics_y = self.y_position
        
        self.draw_metric_box(
            self.margin,
            metrics_y,
            55*mm,
            f"{score:.1f}점",
            "종합 점수",
            self.get_probability_color(score)
        )
        
        self.draw_metric_box(
            self.margin + 60*mm,
            metrics_y,
            55*mm,
            f"{probability:.1f}%",
            "통과 확률",
            self.get_probability_color(probability)
        )
        
        self.draw_metric_box(
            self.margin + 120*mm,
            metrics_y,
            55*mm,
            self.translate_risk(risk_level),
            "리스크 레벨",
            self.get_risk_color(risk_level)
        )
        
        self.y_position -= 30*mm
        
        # 종합 평가
        if probability >= 70:
            assessment = "✅ 통과 가능성이 높습니다. LH 사전심사 신청을 권장합니다."
            color = self.COLOR_SUCCESS
        elif probability >= 50:
            assessment = "⚠️ 통과 가능성이 보통입니다. 개선 후 신청을 권장합니다."
            color = self.COLOR_WARNING
        else:
            assessment = "❌ 통과 가능성이 낮습니다. 대폭적인 개선이 필요합니다."
            color = self.COLOR_DANGER
        
        self.pdf.setFillColorRGB(*color)
        self.pdf.setFont(self.korean_font_bold, 11)
        self.draw_text_block(assessment)
        
        self.y_position -= 10*mm
        
        # 6.2 평가 요소별 점수
        self.draw_subsection("6.2 평가 요소별 점수 (6개 Factor)")
        self.y_position -= 5*mm
        
        factors = lh_review.get("factors", [])
        
        if factors:
            factor_data = [["평가 요소", "점수", "상태"]]
            
            for factor in factors[:6]:
                name = factor.get("factor_name", "평가요소")
                score = factor.get("score", 0)
                
                if score >= 70:
                    status = "✅ 우수"
                elif score >= 50:
                    status = "⚠️ 보통"
                else:
                    status = "❌ 개선필요"
                
                factor_data.append([name, f"{score:.0f}점", status])
            
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            
            table = Table(factor_data, colWidths=[70*mm, 40*mm, 50*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(*self.COLOR_TABLE_HEADER)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.Color(*self.COLOR_PRIMARY)),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), self.korean_font_bold),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            
            table_width, table_height = table.wrapOn(self.pdf, 160*mm, 200*mm)
            table.drawOn(self.pdf, self.margin, self.y_position - table_height)
            self.y_position -= table_height + 5*mm
        
        self.draw_page_footer("10", "12")
        self.pdf.showPage()
        
        # Page 11: 개선 제안
        self.y_position = self.height - self.margin
        self.draw_page_header("6. LH 심사예측 (계속)", "Page 11/12")
        
        self.draw_subsection("6.3 개선 제안사항")
        self.y_position -= 5*mm
        
        suggestions = lh_review.get("suggestions", [])
        
        if suggestions:
            for idx, suggestion in enumerate(suggestions[:5], 1):
                self.pdf.setFont(self.korean_font, 9)
                self.pdf.drawString(self.margin, self.y_position, f"{idx}. {suggestion}")
                self.y_position -= 6*mm
        else:
            self.pdf.setFont(self.korean_font, 9)
            self.pdf.drawString(self.margin, self.y_position,
                              "현재 상태가 양호하여 추가 개선사항이 없습니다.")
        
        self.draw_page_footer("11", "12")
        self.pdf.showPage()
    
    # ============================================
    # Page 12: 종합 결론
    # ============================================
    
    def _page_12_conclusion(self, context: Dict):
        """종합 결론"""
        self.y_position = self.height - self.margin
        
        self.draw_page_header("7. 종합 결론 및 권고사항", "Page 12/12")
        
        lh_review = context.get("lh_review", {})
        scenario = context.get("scenario", {})
        
        # 7.1 종합 평가
        self.draw_subsection("7.1 종합 평가")
        self.y_position -= 5*mm
        
        probability = lh_review.get("pass_probability", 0) if lh_review else 0
        recommended = scenario.get("recommended", "정보 없음")
        
        conclusion_text = f"본 토지는 LH 공공주택 사전심사 통과 확률이 {probability:.1f}%로 예측됩니다. "
        
        if probability >= 70:
            conclusion_text += "통과 가능성이 높아 사전심사 신청을 적극 권장합니다. "
        elif probability >= 50:
            conclusion_text += "일부 개선 후 사전심사 신청을 권장합니다. "
        else:
            conclusion_text += "대폭적인 개선이 필요하며, 전문가 컨설팅을 권장합니다. "
        
        conclusion_text += f"추천 시나리오는 '{recommended}'입니다."
        
        self.draw_text_block(conclusion_text)
        
        self.y_position -= 15*mm
        
        # 7.2 권고사항
        self.draw_subsection("7.2 권고사항")
        self.y_position -= 5*mm
        
        recommendations = [
            "1. LH 사전심사 신청 전 전문가 검토를 받으시기 바랍니다.",
            "2. 개선 제안사항을 참고하여 보완 계획을 수립하세요.",
            "3. 시나리오별 상세 재무 분석을 추가로 진행하세요.",
            "4. 관련 법규 및 정책 변화를 지속적으로 모니터링하세요.",
        ]
        
        for rec in recommendations:
            self.pdf.setFont(self.korean_font, 9)
            self.pdf.drawString(self.margin, self.y_position, rec)
            self.y_position -= 6*mm
        
        self.y_position -= 10*mm
        
        # Disclaimer
        self.pdf.setFont(self.korean_font, 8)
        self.pdf.setFillColorRGB(*self.COLOR_GREY)
        disclaimer = "※ 본 보고서는 AI 기반 분석 결과이며, 실제 LH 심사 결과와 다를 수 있습니다."
        self.draw_text_block(disclaimer)
        
        # Final footer
        self.y_position = 30*mm
        self.pdf.setFont(self.korean_font, 9)
        self.pdf.setFillColorRGB(0, 0, 0)
        self.pdf.drawCentredString(self.width/2, self.y_position,
                                  "문의: ZeroSite AI 토지 분석 시스템")
        self.y_position -= 5*mm
        self.pdf.setFont(self.korean_font, 8)
        self.pdf.setFillColorRGB(*self.COLOR_GREY)
        self.pdf.drawCentredString(self.width/2, self.y_position,
                                  "Email: support@zerosite.ai | Web: www.zerosite.ai")
        
        self.draw_page_footer("12", "12")
        self.pdf.showPage()
