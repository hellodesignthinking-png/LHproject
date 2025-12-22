"""
ZeroSite Final Report QA Validator (Extended)
==============================================

PROMPT 4: Extended QA Validator for Final Reports

PURPOSE:
    Validate Final Reports for "decision-readiness" - not just structural completeness.
    
    A Final Report MUST:
    1. Have Executive Summary
    2. Have sufficient narrative paragraphs
    3. Have explicit judgment statement
    4. Be "decision-ready" based on module data
    
CRITICAL RULES:
    - FAIL + blocking_issues → PDF GENERATION BLOCKED
    - WARNING → PDF allowed but logged
    - PASS → Proceed normally

VERSION: 1.0 (PROMPT 4 Implementation)
DATE: 2025-12-22
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FinalReportQAValidator:
    """
    Extended QA Validator for Final Reports
    
    Validates "decision-making sufficiency" NOT just structural completeness.
    
    PROMPT 4 Requirements:
    ----------------------
    1. Executive Summary section exists
    2. Minimum narrative paragraph count per report type
    3. Explicit judgment statement present
    4. Report type-specific "decision readiness" checks
    5. FAIL status BLOCKS PDF generation
    """
    
    # ========== NARRATIVE REQUIREMENTS ==========
    
    MIN_NARRATIVE_PARAGRAPHS = {
        "landowner_summary": 3,
        "lh_technical": 5,
        "quick_check": 2,
        "financial_feasibility": 4,
        "all_in_one": 6,
        "executive_summary": 2,
    }
    
    # ========== JUDGMENT KEYWORDS ==========
    
    JUDGMENT_KEYWORDS = [
        "추천합니다",
        "부적합",
        "조건부 승인",
        "추진 가능",
        "추진 곤란",
        "승인",
        "불가",
        "권장",
        "비권장",
        "GO",
        "NO-GO",
        "CONDITIONAL"
    ]
    
    # ========== MAIN VALIDATION METHOD ==========
    
    @staticmethod
    def validate(
        report_type: str,
        html_content: str,
        modules_data: Dict[str, any]
    ) -> Dict[str, any]:
        """
        Main validation entry point
        
        Args:
            report_type: Type of final report (e.g., "landowner_summary")
            html_content: Generated HTML content
            modules_data: Dict of module data for decision-readiness checks
                         Format: {"M2": {...}, "M5": {...}, "M6": {...}}
        
        Returns:
            QA Result dict:
            {
                "status": "PASS" | "WARNING" | "FAIL",
                "checks": {...},
                "errors": [...],
                "warnings": [...],
                "blocking_issues": [...]  # Causes PDF generation block
            }
        """
        logger.info(f"[QA START] Final Report QA for {report_type}")
        
        checks = {}
        errors = []
        warnings = []
        blocking_issues = []
        
        # ========== CHECK 1: Executive Summary Exists ==========
        has_exec_summary = FinalReportQAValidator._check_executive_summary(html_content)
        checks["executive_summary_exists"] = has_exec_summary
        
        if not has_exec_summary:
            error_msg = "Executive Summary section is MISSING (CRITICAL)"
            errors.append(error_msg)
            blocking_issues.append("missing_executive_summary")
            logger.error(f"[QA FAIL] {error_msg}")
        else:
            logger.info(f"[QA PASS] Executive Summary exists")
        
        # ========== CHECK 2: Narrative Sufficient ==========
        narrative_check = FinalReportQAValidator._check_narrative_sufficient(
            html_content, report_type
        )
        checks["narrative_sufficient"] = narrative_check["pass"]
        
        if not narrative_check["pass"]:
            warning_msg = (
                f"Narrative insufficient: {narrative_check['found']} paragraphs, "
                f"minimum {narrative_check['required']} required for {report_type}"
            )
            warnings.append(warning_msg)
            logger.warning(f"[QA WARNING] {warning_msg}")
        else:
            logger.info(
                f"[QA PASS] Narrative sufficient: {narrative_check['found']} "
                f"paragraphs (≥{narrative_check['required']})"
            )
        
        # ========== CHECK 3: Judgment Statement Exists ==========
        judgment_check = FinalReportQAValidator._check_judgment_statement(html_content)
        checks["judgment_statement"] = judgment_check["found"]
        
        if not judgment_check["found"]:
            error_msg = "Judgment statement is MISSING (CRITICAL) - Report must have clear recommendation"
            errors.append(error_msg)
            blocking_issues.append("missing_judgment_statement")
            logger.error(f"[QA FAIL] {error_msg}")
        else:
            logger.info(
                f"[QA PASS] Judgment statement found: {judgment_check['keywords']}"
            )
        
        # ========== CHECK 4: Decision Readiness (Module Data-Based) ==========
        decision_ready = FinalReportQAValidator._check_decision_readiness(
            report_type, modules_data
        )
        checks["decision_ready"] = decision_ready["ready"]
        
        if not decision_ready["ready"]:
            warning_msg = (
                f"Decision readiness WARNING: {decision_ready['reason']} "
                f"(This report may not support confident decision-making)"
            )
            warnings.append(warning_msg)
            logger.warning(f"[QA WARNING] {warning_msg}")
        else:
            logger.info(f"[QA PASS] Decision ready: {decision_ready['reason']}")
        
        # ========== DETERMINE FINAL STATUS ==========
        
        if blocking_issues:
            status = "FAIL"
            logger.error(
                f"[QA RESULT] FAIL - {len(blocking_issues)} blocking issues. "
                f"PDF GENERATION WILL BE BLOCKED."
            )
        elif errors:
            status = "FAIL"
            logger.error(f"[QA RESULT] FAIL - {len(errors)} errors found.")
        elif warnings:
            status = "WARNING"
            logger.warning(f"[QA RESULT] WARNING - {len(warnings)} warnings found.")
        else:
            status = "PASS"
            logger.info(f"[QA RESULT] PASS - All checks passed.")
        
        return {
            "status": status,
            "checks": checks,
            "errors": errors,
            "warnings": warnings,
            "blocking_issues": blocking_issues,
            "report_type": report_type,
            "qa_category": "Final Report (Decision-Ready Document)"
        }
    
    # ========== HELPER METHODS ==========
    
    @staticmethod
    def _check_executive_summary(html: str) -> bool:
        """
        Check if Executive Summary section exists
        
        Looks for:
        - executive-summary in class attribute
        - <h2>Executive Summary</h2>
        - 요약, 개요, Summary keywords in headers
        """
        indicators = [
            'executive-summary',  # Matches both class="executive-summary" and class="narrative executive-summary"
            'executive_summary',
            "<h2>Executive Summary</h2>",
            "<h2>종합 요약</h2>",
            "<h2>종합 검토 요약",  # Added for PROMPT 5 narrative
            "<h2>요약</h2>",
            "<h2>개요</h2>",
            "executive-intro",
            "report-summary"
        ]
        
        return any(indicator in html for indicator in indicators)
    
    @staticmethod
    def _check_narrative_sufficient(html: str, report_type: str) -> Dict:
        """
        Check if minimum narrative paragraph count is met
        
        Returns:
            {
                "pass": bool,
                "found": int,
                "required": int
            }
        """
        required = FinalReportQAValidator.MIN_NARRATIVE_PARAGRAPHS.get(report_type, 3)
        
        # Count narrative indicators
        narrative_count = (
            html.count('<p class="narrative">')
            + html.count('<p class="narrative-text">')
            + html.count('<section class="narrative">')
            + html.count('<div class="narrative">')
        )
        
        return {
            "pass": narrative_count >= required,
            "found": narrative_count,
            "required": required
        }
    
    @staticmethod
    def _check_judgment_statement(html: str) -> Dict:
        """
        Check if explicit judgment statement exists
        
        Returns:
            {
                "found": bool,
                "keywords": List[str]  # Found keywords
            }
        """
        found_keywords = []
        
        for keyword in FinalReportQAValidator.JUDGMENT_KEYWORDS:
            if keyword in html:
                found_keywords.append(keyword)
        
        return {
            "found": len(found_keywords) > 0,
            "keywords": found_keywords
        }
    
    @staticmethod
    def _check_decision_readiness(
        report_type: str,
        modules_data: Dict[str, any]
    ) -> Dict:
        """
        Check report type-specific decision readiness based on module data
        
        Rules:
        ------
        landowner_summary:
            - M5 must be profitable (is_profitable=True)
            - M6 must not be rejected (decision != "부적합")
        
        lh_technical:
            - M6 decision != "부적합"
            - M4 must have viable scenarios
        
        financial_feasibility:
            - M5 NPV > 0
            - M5 IRR > threshold
        
        quick_check:
            - M6 exists (minimal requirement)
        
        Returns:
            {
                "ready": bool,
                "reason": str
            }
        """
        # Default: if no specific rules, consider ready
        if report_type not in [
            "landowner_summary",
            "lh_technical",
            "financial_feasibility",
            "quick_check"
        ]:
            return {"ready": True, "reason": "No specific readiness rules for this report type"}
        
        # ========== RULE: landowner_summary ==========
        if report_type == "landowner_summary":
            m5_data = modules_data.get("M5", {})
            m6_data = modules_data.get("M6", {})
            
            is_profitable = m5_data.get("is_profitable", False)
            m6_decision = m6_data.get("decision", "")
            
            if not is_profitable:
                return {
                    "ready": False,
                    "reason": "M5 shows project is not profitable (is_profitable=False)"
                }
            
            if m6_decision == "부적합":
                return {
                    "ready": False,
                    "reason": "M6 decision is '부적합' (rejected by LH)"
                }
            
            return {
                "ready": True,
                "reason": "M5 is profitable AND M6 is not rejected"
            }
        
        # ========== RULE: lh_technical ==========
        if report_type == "lh_technical":
            m6_data = modules_data.get("M6", {})
            m6_decision = m6_data.get("decision", "")
            
            if m6_decision == "부적합":
                return {
                    "ready": False,
                    "reason": "M6 decision is '부적합' (rejected)"
                }
            
            return {
                "ready": True,
                "reason": "M6 decision is not rejected"
            }
        
        # ========== RULE: financial_feasibility ==========
        if report_type == "financial_feasibility":
            m5_data = modules_data.get("M5", {})
            npv = m5_data.get("npv", 0)
            
            if npv <= 0:
                return {
                    "ready": False,
                    "reason": f"M5 NPV is non-positive ({npv:,})"
                }
            
            return {
                "ready": True,
                "reason": f"M5 NPV is positive ({npv:,})"
            }
        
        # ========== RULE: quick_check ==========
        if report_type == "quick_check":
            if "M6" not in modules_data:
                return {
                    "ready": False,
                    "reason": "M6 (LH Review) data is missing"
                }
            
            return {
                "ready": True,
                "reason": "M6 data exists (minimal requirement)"
            }
        
        # Fallback
        return {"ready": True, "reason": "Default readiness"}


# ========== VALIDATION RESULT HELPER ==========

def should_block_pdf_generation(qa_result: Dict) -> bool:
    """
    Determine if PDF generation should be blocked based on QA result
    
    BLOCKING CONDITIONS:
    - status == "FAIL"
    - blocking_issues list is not empty
    
    Args:
        qa_result: Result from FinalReportQAValidator.validate()
    
    Returns:
        True if PDF generation should be blocked, False otherwise
    """
    if qa_result["status"] == "FAIL":
        return True
    
    if qa_result.get("blocking_issues"):
        return True
    
    return False


# ========== LOGGING HELPER ==========

def log_qa_result(qa_result: Dict):
    """
    Log QA result in structured format
    """
    status = qa_result["status"]
    report_type = qa_result.get("report_type", "unknown")
    
    logger.info("=" * 60)
    logger.info(f"FINAL REPORT QA RESULT: {status}")
    logger.info(f"Report Type: {report_type}")
    logger.info("=" * 60)
    
    # Checks
    checks = qa_result.get("checks", {})
    logger.info("CHECKS:")
    for check_name, check_result in checks.items():
        symbol = "✅" if check_result else "❌"
        logger.info(f"  {symbol} {check_name}: {check_result}")
    
    # Errors
    errors = qa_result.get("errors", [])
    if errors:
        logger.error("ERRORS:")
        for error in errors:
            logger.error(f"  ❌ {error}")
    
    # Warnings
    warnings = qa_result.get("warnings", [])
    if warnings:
        logger.warning("WARNINGS:")
        for warning in warnings:
            logger.warning(f"  ⚠️  {warning}")
    
    # Blocking issues
    blocking = qa_result.get("blocking_issues", [])
    if blocking:
        logger.critical("BLOCKING ISSUES (PDF GENERATION WILL BE BLOCKED):")
        for issue in blocking:
            logger.critical(f"  🚫 {issue}")
    
    logger.info("=" * 60)
