"""
Quick Check Report Assembler (PROMPT 6)
========================================

Target Audience: 의사결정권자 (빠른 GO/NO-GO 판단)
Goal: 5분 내 핵심 결론 확인
Modules: M5 (사업성), M6 (LH심사)

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