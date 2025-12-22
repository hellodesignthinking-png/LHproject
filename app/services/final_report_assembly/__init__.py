"""
Final Report Assembly - Phase 3

This package contains ONLY assembly logic for final reports.
NO calculation or data processing is allowed here.

Modules are COMPLETE and LOCKED (Phase 1-2).
This phase ONLY combines their HTML outputs.
"""

from .base_assembler import (
    BaseFinalReportAssembler,
    FinalReportAssemblyError,
    FinalReportQAValidator,
    validate_phase3_compliance,
)

__all__ = [
    "BaseFinalReportAssembler",
    "FinalReportAssemblyError",
    "FinalReportQAValidator",
    "validate_phase3_compliance",
]
