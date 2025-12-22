"""
ZeroSite Context Objects
=========================

Immutable data context objects for 6-module architecture.

All context objects are frozen (immutable) to ensure data integrity
throughout the pipeline.

Modules:
- M1: CanonicalLandContext (토지정보 FACT)
- M2: AppraisalContext (감정평가 FACT, IMMUTABLE)
- M3: HousingTypeContext (LH 유형 선택 INTERPRETATION)
- M4: CapacityContext (건축 규모 INTERPRETATION)
- M5: FeasibilityContext (사업성 JUDGMENT INPUT)
- M6: LHReviewContext (LH 심사 예측 FINAL JUDGMENT)

Author: ZeroSite Refactoring Team
Date: 2025-12-17
"""

from .canonical_land import CanonicalLandContext
from .appraisal_context import AppraisalContext
from .housing_type_context import HousingTypeContext
from .capacity_context import CapacityContext
from .feasibility_context import FeasibilityContext
from .lh_review_context import LHReviewContext

__all__ = [
    "CanonicalLandContext",
    "AppraisalContext",
    "HousingTypeContext",
    "CapacityContext",
    "FeasibilityContext",
    "LHReviewContext",
]
