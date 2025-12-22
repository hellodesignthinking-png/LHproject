"""
LH Technical Review Report Assembler (PROMPT 6)
================================================

Target Audience: LH 심사역 (기술 검토자)
Goal: LH 정책 부합성 + 기술적 실현 가능성 검토
Modules: M3 (선호유형), M4 (건축규모), M6 (LH심사)

ASSEMBLY ONLY - NO CALCULATION
"""

from typing import Dict, List, Literal
import logging
import re

from ..base_assembler import BaseFinalReportAssembler, get_report_brand_class
from ..narrative_generator import NarrativeGeneratorFactory
from ..report_type_configs import REPORT_TYPE_CONFIGS, get_mandatory_kpi, get_critical_kpi

# [Phase 3.10 Final Lock + vPOST-FINAL] KPI Extractor with operational safety
from ..kpi_extractor import (
    KPIExtractor, 
    validate_mandatory_kpi, 
    validate_kpi_with_safe_gate,
    log_kpi_pipeline, 
    FinalReportAssemblyError
)