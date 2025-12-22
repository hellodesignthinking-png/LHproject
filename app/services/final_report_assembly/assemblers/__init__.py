"""
Final Report Assemblers Package
================================

Contains 6 concrete assemblers for final report types.

Each assembler:
1. Inherits from BaseFinalReportAssembler
2. Uses NarrativeGenerator for story elements
3. Loads module HTML fragments (no calculation)
4. Assembles into complete final report
5. Validates with QA Validator

PROMPT 6 Implementation
"""

from .landowner_summary import LandownerSummaryAssembler
from .lh_technical import LHTechnicalAssembler
from .quick_check import QuickCheckAssembler
from .financial_feasibility import FinancialFeasibilityAssembler
from .all_in_one import AllInOneAssembler
from .executive_summary import ExecutiveSummaryAssembler

__all__ = [
    "LandownerSummaryAssembler",
    "LHTechnicalAssembler",
    "QuickCheckAssembler",
    "FinancialFeasibilityAssembler",
    "AllInOneAssembler",
    "ExecutiveSummaryAssembler",
]
