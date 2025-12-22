"""
HTML/PDF Data Parity Validator for ZeroSite v4.3

Purpose: Ensure HTML preview and PDF download display IDENTICAL data
Author: ZeroSite Backend Team
Date: 2025-12-22

CRITICAL REQUIREMENT:
- HTML and PDF must show the EXACT SAME numbers for the same context_id
- This validator provides automated verification to prevent data mismatch
"""

from typing import Dict, Any, List, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParityCheckResult:
    """Result of HTML/PDF parity check"""
    module: str
    context_id: str
    passed: bool
    mismatches: List[Tuple[str, Any, Any]]  # (field, html_value, pdf_value)
    message: str


class HTMLPDFParityValidator:
    """
    Validates that HTML and PDF contain identical data
    
    Usage:
        validator = HTMLPDFParityValidator()
        result = validator.validate_m3(html_data, pdf_data, context_id)
        if not result.passed:
            raise ValueError(result.message)
    """
    
    @staticmethod
    def validate_m2(html_data: Dict[str, Any], pdf_data: Dict[str, Any], context_id: str) -> ParityCheckResult:
        """
        Validate M2 (토지평가) data parity
        
        Critical fields:
        - land_value_total_krw
        - pyeong_price_krw
        """
        mismatches = []
        
        # Extract HTML data
        html_appraisal = html_data.get("appraisal_result", {})
        html_land_value = html_appraisal.get("total_value", 0)
        html_pyeong_price = html_appraisal.get("pyeong_price", 0)
        
        # Extract PDF data
        pdf_appraisal = pdf_data.get("appraisal", {})
        pdf_land_value = pdf_appraisal.get("land_value", 0)
        pdf_pyeong_price = pdf_appraisal.get("unit_price_pyeong", 0)
        
        # Compare
        if html_land_value != pdf_land_value:
            mismatches.append(("land_value", html_land_value, pdf_land_value))
        
        if html_pyeong_price != pdf_pyeong_price:
            mismatches.append(("pyeong_price", html_pyeong_price, pdf_pyeong_price))
        
        passed = len(mismatches) == 0
        message = "M2 parity check PASSED" if passed else f"M2 parity check FAILED: {len(mismatches)} mismatches"
        
        if not passed:
            logger.error(f"❌ M2 HTML/PDF mismatch for {context_id}:")
            for field, html_val, pdf_val in mismatches:
                logger.error(f"  - {field}: HTML={html_val}, PDF={pdf_val}")
        else:
            logger.info(f"✅ M2 HTML/PDF parity verified for {context_id}")
        
        return ParityCheckResult(
            module="M2",
            context_id=context_id,
            passed=passed,
            mismatches=mismatches,
            message=message
        )
    
    @staticmethod
    def validate_m3(html_data: Dict[str, Any], pdf_data: Dict[str, Any], context_id: str) -> ParityCheckResult:
        """
        Validate M3 (주택유형) data parity
        
        Critical fields:
        - recommended_type (name)
        - total_score
        """
        mismatches = []
        
        # Extract HTML data
        html_rec_type = html_data.get("recommended_type", {})
        html_type_name = html_rec_type.get("name", "")
        html_score = html_rec_type.get("score", 0)
        
        # Extract PDF data
        pdf_type_name = pdf_data.get("recommended_type", "")
        pdf_score = pdf_data.get("total_score", 0)
        
        # Compare
        if html_type_name != pdf_type_name:
            mismatches.append(("recommended_type", html_type_name, pdf_type_name))
        
        if html_score != pdf_score:
            mismatches.append(("total_score", html_score, pdf_score))
        
        passed = len(mismatches) == 0
        message = "M3 parity check PASSED" if passed else f"M3 parity check FAILED: {len(mismatches)} mismatches"
        
        if not passed:
            logger.error(f"❌ M3 HTML/PDF mismatch for {context_id}:")
            for field, html_val, pdf_val in mismatches:
                logger.error(f"  - {field}: HTML={html_val}, PDF={pdf_val}")
        else:
            logger.info(f"✅ M3 HTML/PDF parity verified for {context_id}")
        
        return ParityCheckResult(
            module="M3",
            context_id=context_id,
            passed=passed,
            mismatches=mismatches,
            message=message
        )
    
    @staticmethod
    def validate_m4(html_data: Dict[str, Any], pdf_data: Dict[str, Any], context_id: str) -> ParityCheckResult:
        """
        Validate M4 (건축규모) data parity
        
        Critical fields:
        - total_units
        - base_units
        - incentive_units
        """
        mismatches = []
        
        # Extract HTML data
        html_dev = html_data.get("development_summary", {})
        html_total = html_dev.get("total_units", 0)
        html_base = html_dev.get("base_units", 0)
        html_incentive = html_dev.get("incentive_units", 0)
        
        # Extract PDF data
        pdf_total = pdf_data.get("incentive_capacity", {}).get("total_units", 0)
        pdf_base = pdf_data.get("legal_capacity", {}).get("total_units", 0)
        # Incentive units = difference
        pdf_incentive = pdf_total - pdf_base
        
        # Compare
        if html_total != pdf_total:
            mismatches.append(("total_units", html_total, pdf_total))
        
        if html_base != pdf_base:
            mismatches.append(("base_units", html_base, pdf_base))
        
        if html_incentive != pdf_incentive:
            mismatches.append(("incentive_units", html_incentive, pdf_incentive))
        
        passed = len(mismatches) == 0
        message = "M4 parity check PASSED" if passed else f"M4 parity check FAILED: {len(mismatches)} mismatches"
        
        if not passed:
            logger.error(f"❌ M4 HTML/PDF mismatch for {context_id}:")
            for field, html_val, pdf_val in mismatches:
                logger.error(f"  - {field}: HTML={html_val}, PDF={pdf_val}")
        else:
            logger.info(f"✅ M4 HTML/PDF parity verified for {context_id}")
        
        return ParityCheckResult(
            module="M4",
            context_id=context_id,
            passed=passed,
            mismatches=mismatches,
            message=message
        )
    
    @staticmethod
    def validate_m5(html_data: Dict[str, Any], pdf_data: Dict[str, Any], context_id: str) -> ParityCheckResult:
        """
        Validate M5 (사업성) data parity
        
        Critical fields:
        - npv
        - irr
        - roi
        - grade
        """
        mismatches = []
        
        # Extract HTML data
        html_financial = html_data.get("financial_result", {})
        html_npv = html_financial.get("npv", 0)
        html_irr = html_financial.get("irr", 0)
        html_roi = html_financial.get("roi", 0)
        html_grade = html_financial.get("grade", "")
        
        # Extract PDF data
        pdf_npv = pdf_data.get("npv", 0)
        pdf_irr = pdf_data.get("irr", 0)
        pdf_roi = pdf_data.get("roi", 0)
        pdf_grade = pdf_data.get("grade", "")
        
        # Compare (allow small floating point differences)
        if abs(html_npv - pdf_npv) > 1:  # Allow 1원 difference
            mismatches.append(("npv", html_npv, pdf_npv))
        
        if abs(html_irr - pdf_irr) > 0.01:  # Allow 0.01% difference
            mismatches.append(("irr", html_irr, pdf_irr))
        
        if abs(html_roi - pdf_roi) > 0.01:  # Allow 0.01% difference
            mismatches.append(("roi", html_roi, pdf_roi))
        
        if html_grade != pdf_grade:
            mismatches.append(("grade", html_grade, pdf_grade))
        
        passed = len(mismatches) == 0
        message = "M5 parity check PASSED" if passed else f"M5 parity check FAILED: {len(mismatches)} mismatches"
        
        if not passed:
            logger.error(f"❌ M5 HTML/PDF mismatch for {context_id}:")
            for field, html_val, pdf_val in mismatches:
                logger.error(f"  - {field}: HTML={html_val}, PDF={pdf_val}")
        else:
            logger.info(f"✅ M5 HTML/PDF parity verified for {context_id}")
        
        return ParityCheckResult(
            module="M5",
            context_id=context_id,
            passed=passed,
            mismatches=mismatches,
            message=message
        )
    
    @staticmethod
    def validate_m6(html_data: Dict[str, Any], pdf_data: Dict[str, Any], context_id: str) -> ParityCheckResult:
        """
        Validate M6 (LH심사) data parity
        
        Critical fields:
        - decision
        - total_score
        - grade
        """
        mismatches = []
        
        # Extract HTML data
        html_review = html_data.get("review_result", {})
        html_decision = html_review.get("decision", "")
        html_score = html_review.get("total_score", 0)
        html_grade = html_review.get("grade", "")
        
        # Extract PDF data
        pdf_decision = pdf_data.get("decision", "")
        pdf_score = pdf_data.get("total_score", 0)
        pdf_grade = pdf_data.get("grade", "")
        
        # Compare
        if html_decision != pdf_decision:
            mismatches.append(("decision", html_decision, pdf_decision))
        
        if abs(html_score - pdf_score) > 0.1:  # Allow small floating point difference
            mismatches.append(("total_score", html_score, pdf_score))
        
        if html_grade != pdf_grade:
            mismatches.append(("grade", html_grade, pdf_grade))
        
        passed = len(mismatches) == 0
        message = "M6 parity check PASSED" if passed else f"M6 parity check FAILED: {len(mismatches)} mismatches"
        
        if not passed:
            logger.error(f"❌ M6 HTML/PDF mismatch for {context_id}:")
            for field, html_val, pdf_val in mismatches:
                logger.error(f"  - {field}: HTML={html_val}, PDF={pdf_val}")
        else:
            logger.info(f"✅ M6 HTML/PDF parity verified for {context_id}")
        
        return ParityCheckResult(
            module="M6",
            context_id=context_id,
            passed=passed,
            mismatches=mismatches,
            message=message
        )
    
    @staticmethod
    def validate_all(
        module: str,
        html_data: Dict[str, Any],
        pdf_data: Dict[str, Any],
        context_id: str
    ) -> ParityCheckResult:
        """
        Validate HTML/PDF parity for any module
        
        Args:
            module: Module identifier (M2, M3, M4, M5, M6)
            html_data: Normalized data from adapter
            pdf_data: PDF generator input data
            context_id: Context ID for tracking
            
        Returns:
            ParityCheckResult with validation status
        """
        if module == "M2":
            return HTMLPDFParityValidator.validate_m2(html_data, pdf_data, context_id)
        elif module == "M3":
            return HTMLPDFParityValidator.validate_m3(html_data, pdf_data, context_id)
        elif module == "M4":
            return HTMLPDFParityValidator.validate_m4(html_data, pdf_data, context_id)
        elif module == "M5":
            return HTMLPDFParityValidator.validate_m5(html_data, pdf_data, context_id)
        elif module == "M6":
            return HTMLPDFParityValidator.validate_m6(html_data, pdf_data, context_id)
        else:
            return ParityCheckResult(
                module=module,
                context_id=context_id,
                passed=False,
                mismatches=[],
                message=f"Unknown module: {module}"
            )
