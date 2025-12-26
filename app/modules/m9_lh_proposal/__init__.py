"""
ZeroSite v4.0 M9 LH Proposal Generator
======================================

LH 공식 제안서 자동 생성 시스템

Author: ZeroSite M9 Team
Date: 2025-12-26
Version: 1.0 (Initial Release)

Purpose:
    LH 매입임대주택 사업 제안서를 자동으로 생성
    - Word 문서 (.docx)
    - PDF 문서 (.pdf)
    - 첨부 서류 패키지

Features:
    1. LH 표준 양식 기반 제안서
    2. 자동 데이터 매핑
    3. 표, 차트, 이미지 삽입
    4. PDF 변환 (reportlab)
    5. 첨부 서류 번들링
"""

from .proposal_generator import LHProposalGenerator
from .document_builder import LHDocumentBuilder
from .attachment_manager import AttachmentManager
from .pdf_converter import PDFConverter

__all__ = [
    'LHProposalGenerator',
    'LHDocumentBuilder',
    'AttachmentManager',
    'PDFConverter'
]
