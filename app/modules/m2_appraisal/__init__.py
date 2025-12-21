"""
M2 Appraisal Module
===================

토지감정평가 모듈 (🔒 IMMUTABLE)

핵심 원칙:
1. AppraisalContext는 frozen=True로 생성 후 수정 불가
2. 외부 모듈(M3-M6)에서 land_value 재계산 금지
3. 보고서에서 감정평가 로직 개입 금지

Public API:
- AppraisalService: 토지감정평가 서비스 (run 메서드만 노출)
- AppraisalContext: 감정평가 결과 (READ-ONLY)

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from app.modules.m2_appraisal.service import AppraisalService
from app.core.context.appraisal_context import (
    AppraisalContext,
    TransactionSample,
    PremiumFactors,
    ConfidenceMetrics
)

__all__ = [
    "AppraisalService",
    "AppraisalContext",
    "TransactionSample",
    "PremiumFactors",
    "ConfidenceMetrics"
]

# 🔒 M2 모듈 보호 선언
__protected__ = True
__immutable_output__ = "AppraisalContext"

# 경고: 이 모듈의 내부 로직은 수정하지 마세요
# WARNING: Do not modify the internal logic of this module
# AppraisalContext는 생성 후 수정 불가능합니다
