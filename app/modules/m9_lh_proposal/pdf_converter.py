"""
ZeroSite v4.0 PDF Converter
============================

reportlab 기반 PDF 생성 및 변환

Author: ZeroSite M9 Team
Date: 2025-12-26
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFConverter:
    """ReportLab 기반 PDF 생성기"""
    
    def __init__(self):
        """PDF 생성기 초기화"""
        self.styles = getSampleStyleSheet()
        self._setup_korean_fonts()
        self._setup_custom_styles()
        
        self.elements = []
        
    def _setup_korean_fonts(self):
        """한글 폰트 설정"""
        # 시스템 한글 폰트 사용 시도
        try:
            # Linux 기본 나눔고딕
            font_paths = [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_name = 'NanumGothic' if 'Bold' not in font_path else 'NanumGothicBold'
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
            
            self.korean_font = 'NanumGothic'
            self.korean_font_bold = 'NanumGothicBold'
            
        except Exception as e:
            print(f"⚠ 한글 폰트 등록 실패: {e}")
            print("⚠ Helvetica 폰트로 대체합니다 (한글 깨짐 가능)")
            self.korean_font = 'Helvetica'
            self.korean_font_bold = 'Helvetica-Bold'
    
    def _setup_custom_styles(self):
        """커스텀 스타일 설정"""
        # 제목 스타일
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontName=self.korean_font_bold,
            fontSize=24,
            textColor=colors.HexColor('#002060'),
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        # 섹션 제목
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontName=self.korean_font_bold,
            fontSize=16,
            textColor=colors.HexColor('#0070C0'),
            spaceBefore=20,
            spaceAfter=10
        ))
        
        # 서브섹션 제목
        self.styles.add(ParagraphStyle(
            name='SubSectionTitle',
            parent=self.styles['Heading2'],
            fontName=self.korean_font_bold,
            fontSize=12,
            textColor=colors.HexColor('#0070C0'),
            spaceBefore=12,
            spaceAfter=6
        ))
        
        # 본문
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontName=self.korean_font,
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
        
        # 강조 본문
        self.styles.add(ParagraphStyle(
            name='CustomBodyBold',
            parent=self.styles['CustomBody'],
            fontName=self.korean_font_bold
        ))
    
    def add_cover_page(
        self,
        title: str = "LH 매입임대주택 사업 제안서",
        address: str = "",
        parcel_id: str = "",
        submitted_by: str = "ZeroSite",
        submission_date: str = ""
    ):
        """표지 페이지 추가"""
        # 제목
        self.elements.append(Spacer(1, 2*inch))
        self.elements.append(Paragraph(title, self.styles['CustomTitle']))
        
        # 공백
        self.elements.append(Spacer(1, 1*inch))
        
        # 대상 부지
        address_style = ParagraphStyle(
            name='AddressStyle',
            parent=self.styles['CustomBody'],
            fontSize=12,
            alignment=TA_CENTER
        )
        self.elements.append(Paragraph(f"대상 부지: {address}", address_style))
        
        if parcel_id:
            parcel_style = ParagraphStyle(
                name='ParcelStyle',
                parent=self.styles['CustomBody'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            self.elements.append(Spacer(1, 0.2*inch))
            self.elements.append(Paragraph(f"필지번호: {parcel_id}", parcel_style))
        
        # 공백
        self.elements.append(Spacer(1, 2*inch))
        
        # 제출 정보
        submit_style = ParagraphStyle(
            name='SubmitStyle',
            parent=self.styles['CustomBody'],
            fontSize=11,
            alignment=TA_CENTER
        )
        self.elements.append(Paragraph(f"제출: {submitted_by}", submit_style))
        self.elements.append(Spacer(1, 0.2*inch))
        self.elements.append(Paragraph(
            submission_date or datetime.now().strftime("%Y년 %m월 %d일"),
            submit_style
        ))
        
        # 페이지 구분
        self.elements.append(PageBreak())
    
    def add_section_title(self, title: str):
        """섹션 제목 추가"""
        self.elements.append(Paragraph(title, self.styles['SectionTitle']))
    
    def add_subsection_title(self, title: str):
        """서브섹션 제목 추가"""
        self.elements.append(Paragraph(title, self.styles['SubSectionTitle']))
    
    def add_paragraph(self, text: str, bold: bool = False):
        """일반 단락 추가"""
        style = self.styles['CustomBodyBold'] if bold else self.styles['CustomBody']
        self.elements.append(Paragraph(text, style))
        self.elements.append(Spacer(1, 0.1*inch))
    
    def add_bullet_list(self, items: List[str]):
        """불릿 리스트 추가"""
        for item in items:
            bullet_style = ParagraphStyle(
                name='BulletStyle',
                parent=self.styles['CustomBody'],
                leftIndent=20,
                bulletIndent=10
            )
            self.elements.append(Paragraph(f"• {item}", bullet_style))
        self.elements.append(Spacer(1, 0.1*inch))
    
    def add_table(
        self,
        headers: List[str],
        rows: List[List[Any]],
        col_widths: Optional[List[float]] = None
    ):
        """표 추가"""
        # 데이터 준비
        data = [headers] + [[str(cell) for cell in row] for row in rows]
        
        # 열 너비 (인치 단위)
        if col_widths:
            widths = [w * inch for w in col_widths]
        else:
            # 균등 분할
            available_width = 6.5 * inch
            widths = [available_width / len(headers)] * len(headers)
        
        # 표 생성
        table = Table(data, colWidths=widths)
        
        # 스타일 적용
        table.setStyle(TableStyle([
            # 헤더 스타일
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0070C0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.korean_font_bold),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # 데이터 스타일
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # 테두리
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#0070C0')),
            
            # 짝수 행 배경색
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')])
        ]))
        
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.2*inch))
    
    def add_key_value_table(self, data: Dict[str, Any]):
        """키-값 테이블 추가"""
        table_data = [[key, str(value)] for key, value in data.items()]
        
        table = Table(table_data, colWidths=[2*inch, 4*inch])
        
        table.setStyle(TableStyle([
            # 키 열 스타일
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7E6E6')),
            ('FONTNAME', (0, 0), (0, -1), self.korean_font_bold),
            ('FONTSIZE', (0, 0), (0, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            
            # 값 열 스타일
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('FONTNAME', (1, 0), (1, -1), self.korean_font),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            
            # 공통 스타일
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.2*inch))
    
    def add_financial_summary(
        self,
        land_value: int,
        construction_cost: int,
        total_cost: int,
        total_revenue: int,
        npv: int,
        irr: float
    ):
        """재무 요약 추가"""
        self.add_subsection_title("재무 개요")
        
        data = {
            "토지매입비": f"₩{land_value:,}",
            "건축비": f"₩{construction_cost:,}",
            "총 사업비": f"₩{total_cost:,}",
            "예상 수익": f"₩{total_revenue:,}",
            "순현재가치 (NPV)": f"₩{npv:,}",
            "내부수익률 (IRR)": f"{irr:.2f}%"
        }
        
        self.add_key_value_table(data)
    
    def add_lh_scorecard(
        self,
        section_scores: Dict[str, float],
        total_score: float,
        judgement: str,
        grade: str
    ):
        """LH 점수표 추가"""
        self.add_subsection_title("LH 종합 평가 결과")
        
        headers = ["평가 항목", "배점", "득점", "득점률"]
        
        section_names = {
            "A": "정책·유형 적합성",
            "B": "입지·환경 평가",
            "C": "건축 가능성",
            "D": "가격·매입 적정성",
            "E": "사업성"
        }
        
        max_scores = {"A": 25, "B": 20, "C": 20, "D": 15, "E": 20}
        
        rows = []
        for section_id, section_name in section_names.items():
            score = section_scores.get(section_id, 0.0)
            max_score = max_scores[section_id]
            score_pct = (score / max_score * 100) if max_score > 0 else 0
            rows.append([
                section_name,
                f"{max_score}점",
                f"{score:.1f}점",
                f"{score_pct:.1f}%"
            ])
        
        # 합계
        rows.append([
            "총점",
            "100점",
            f"{total_score:.1f}점",
            f"{total_score:.1f}%"
        ])
        
        self.add_table(headers, rows, col_widths=[2.5, 1.0, 1.0, 1.0])
        
        # 판정 결과
        judgement_text = f"<b>최종 판정: {judgement} (등급: {grade})</b>"
        
        if judgement == "GO":
            color = '#008000'  # 녹색
        elif judgement == "CONDITIONAL":
            color = '#FFA500'  # 주황
        else:
            color = '#FF0000'  # 빨강
        
        result_style = ParagraphStyle(
            name='ResultStyle',
            parent=self.styles['CustomBody'],
            fontSize=12,
            textColor=colors.HexColor(color),
            spaceBefore=10
        )
        
        self.elements.append(Paragraph(judgement_text, result_style))
        self.elements.append(Spacer(1, 0.2*inch))
    
    def build(self, file_path: str):
        """PDF 생성"""
        # 디렉토리 생성
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # 빌드
        doc.build(self.elements)
        
        print(f"✓ PDF document created: {file_path}")
        
        return file_path


__all__ = ['PDFConverter']
