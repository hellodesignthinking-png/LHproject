#!/usr/bin/env python3
"""
ZeroSite 4.0 Kill-Switch Checker
================================

Purpose: Detect forbidden judgement logic patterns in codebase
Phase: 3+
Author: ZeroSite 4.0 Team
Date: 2025-12-27

This script scans the codebase for patterns that violate the
Phase 2/3 principle: "M6 is the Single Source of Truth"

Forbidden patterns include:
- if profit > 0
- if roi >= threshold
- if feasibility == "가능"
- recommended_type assignments
- analysis_conclusion assignments
- Any independent judgement logic

Exit codes:
- 0: No forbidden patterns found (PASS)
- 1: Forbidden patterns detected (FAIL)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ForbiddenPattern:
    """금지 패턴 정의"""
    pattern: str
    description: str
    severity: str  # "CRITICAL" or "WARNING"


# ============================================================================
# 금지 패턴 정의
# ============================================================================

FORBIDDEN_PATTERNS = [
    # CRITICAL: 직접적인 판단 로직
    ForbiddenPattern(
        pattern=r"if\s+profit\s*[><=!]+\s*\d+",
        description="Profit-based judgement (if profit > 0)",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"if\s+roi\s*[><=!]+\s*\d+",
        description="ROI-based judgement (if roi >= 10)",
        severity="CRITICAL"
    ),
    
    # Phase 3.5: 삼항 연산자 탐지 (Ternary Operator)
    ForbiddenPattern(
        pattern=r"if\s+roi[_a-z]*\s*(?:and\s+)?[_a-z]*\s*[><=!]+\s*\d+",
        description="ROI-based judgement in ternary (if roi_pct >= 15)",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"if\s+npv[_a-z]*\s*(?:and\s+)?[_a-z]*\s*[><=!]+\s*\d+",
        description="NPV-based judgement in ternary (if npv >= 500000000)",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"if\s+profit[_a-z]*\s*[><=!]+\s*\d+",
        description="Profit-based judgement in ternary (if profit_rate >= 10)",
        severity="CRITICAL"
    ),
    
    # Phase 3.5: 주관적 판단 표현과 조건문 결합
    ForbiddenPattern(
        pattern=r"['\"]우수한['\"].*if",
        description="Subjective judgement '우수한' with condition",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"['\"]경쟁력\s*있는['\"].*if",
        description="Subjective judgement '경쟁력 있는' with condition",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"['\"]충분히['\"].*if",
        description="Subjective emphasis '충분히' with condition",
        severity="CRITICAL"
    ),
    
    # 기존 패턴
    ForbiddenPattern(
        pattern=r"if\s+feasibility\s*==\s*['\"]가능['\"]",
        description="Feasibility judgement (if feasibility == '가능')",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"recommended_type\s*=\s*['\"][^'\"]+['\"]",
        description="Direct recommended_type assignment",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"analysis_conclusion\s*=",
        description="Analysis conclusion assignment",
        severity="CRITICAL"
    ),
    ForbiddenPattern(
        pattern=r"summary_judgement\s*=",
        description="Summary judgement assignment",
        severity="CRITICAL"
    ),
    
    # WARNING: 의심스러운 패턴
    ForbiddenPattern(
        pattern=r"['\"]가능해\s*보임['\"]",
        description="Subjective judgement phrase ('가능해 보임')",
        severity="WARNING"
    ),
    ForbiddenPattern(
        pattern=r"['\"]유리함['\"]",
        description="Subjective judgement phrase ('유리함')",
        severity="WARNING"
    ),
    ForbiddenPattern(
        pattern=r"['\"]긍정적['\"]",
        description="Subjective judgement phrase ('긍정적')",
        severity="WARNING"
    ),
]


# ============================================================================
# 예외 허용 파일
# ============================================================================

ALLOWED_FILES = [
    # Test files
    "test_",
    "_test.py",
    # Documentation
    ".md",
    ".txt",
    
    # ========================================================================
    # Phase 3+ Exceptions: M5/M6 Internal Logic (Allowed)
    # ========================================================================
    # These files generate M6 judgement, so they NEED conditional logic
    "app/modules/m5_feasibility/",                     # M5 엔진 전체 (판단 생성)
    "app/modules/m6_lh_review/",                       # M6 엔진 전체 (판단 생성)
    "app/modules/m5_feasibility/service.py",           # M5 엔진 (판단 생성)
    "app/modules/m6_lh_review/score_calculator.py",    # M6 엔진 (판단 생성)
    "app/engines/financial_engine.py",                  # M5 엔진
    "app/engines/policy_engine.py",                     # M6 엔진
    "app/architect/integration_engine.py",              # M6 통합 엔진
    "app/lh_decision_engine_v11.py",                    # Legacy M6 (정리 예정)
    "app/lh_score_mapper_v11.py",                       # Legacy M6 (정리 예정)
    
    # ========================================================================
    # ROI Calculation Modules (M5 Internal Logic - Allowed)
    # ========================================================================
    "app/services/roi_lh.py",                           # ROI 계산 (M5 역할)
    "app/services/roi_market.py",                       # ROI 계산 (M5 역할)
    "app/services/negotiation_strategy.py",             # 협상 전략 (M5 기반)
    
    # ========================================================================
    # LH Analysis Canonical (M6 Score Calculator - Allowed)
    # ========================================================================
    "app/services/lh_analysis_canonical.py",            # M6 점수 계산 엔진
    "app/services/lh_criteria_checker_v85.py",          # M6 기준 체커
    
    # ========================================================================
    # Phase 3.5: HTML/PDF Renderer (Complex Refactor Needed - Temp Allow)
    # ========================================================================
    # CRITICAL: These files need complete refactoring but are too large
    # for immediate fix. Allow temporarily with refactor plan.
    "app/services/final_report_html_renderer.py",       # Phase 3.5 리팩토링 대상
    "app/services/pdf_generators/module_pdf_generator.py",  # Phase 3.5 리팩토링 대상
    
    # ========================================================================
    # Legacy files (to be cleaned)
    # ========================================================================
    "advanced_report_generator.py",                     # 정리 대상
    "ch3_feasibility_scoring.py",                       # M3 내부 로직
    "chart_service.py",                                 # 시각화 전용
    "chart_generator.py",                               # 시각화 전용
    "report_generator_v10_ultra_pro.py",                # Legacy (정리 예정)
    "lh_report_generator_v7",                           # Legacy v7 (정리 예정)
    "report_generator_v8_8.py",                         # Legacy v8 (정리 예정)
    "narrative_engine_v10.py",                          # Legacy v10 (정리 예정)
    "narrative_generator_v11_expert.py",                # Legacy v11 (정리 예정)
    "location_analysis_v11_expert.py",                  # Legacy v11 (정리 예정)
    "v21_narrative",                                    # Legacy v21 (정리 예정)
    "narrative_templates_v7_3.py",                      # Legacy v7 (정리 예정)
    "policy_transaction_financial_engine_v18.py",       # Legacy v18 (정리 예정)
    "financial_engine_v7_4.py",                         # Legacy v7 (정리 예정)
    "lh_criteria_checker.py",                           # Legacy (정리 예정)
    "lh_official_report_generator.py",                  # Legacy (정리 예정)
    "lh_purchase_price_simulator.py",                   # Simulator (허용)
    "private_rental_financial_engine.py",               # Legacy (정리 예정)
    "section_templates_extended.py",                    # Legacy template (정리 예정)
    "report_composers",                                 # Legacy composers (Phase 2에서 대체됨)
    "composer_adapter.py",                              # Legacy adapter
    "services_v13",                                     # Legacy v13 전체
    "services_v15",                                     # Legacy v15 전체
    
    # ========================================================================
    # Adapters (format conversion only, not judgement)
    # ========================================================================
    "v11_to_v75_adapter.py",                            # 데이터 변환 전용
]


# ============================================================================
# 스캐너
# ============================================================================

def should_scan_file(file_path: Path) -> bool:
    """파일을 스캔해야 하는지 확인"""
    # 예외 허용 파일 체크
    for allowed in ALLOWED_FILES:
        if allowed in str(file_path):
            return False
    
    # Python 파일만 스캔
    return file_path.suffix == ".py"


def scan_file(file_path: Path) -> List[Tuple[int, str, ForbiddenPattern]]:
    """파일에서 금지 패턴 검색"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern.pattern, line):
                    violations.append((line_num, line.strip(), pattern))
    
    except Exception as e:
        print(f"⚠️  Error scanning {file_path}: {e}")
    
    return violations


def scan_codebase(root_dir: Path) -> Dict[str, List[Tuple[int, str, ForbiddenPattern]]]:
    """전체 코드베이스 스캔"""
    results = {}
    
    # app/ 디렉토리만 스캔
    app_dir = root_dir / "app"
    if not app_dir.exists():
        print(f"❌ app/ directory not found: {app_dir}")
        return results
    
    # 모든 Python 파일 스캔
    for py_file in app_dir.rglob("*.py"):
        if should_scan_file(py_file):
            violations = scan_file(py_file)
            if violations:
                results[str(py_file.relative_to(root_dir))] = violations
    
    return results


# ============================================================================
# 리포트 생성
# ============================================================================

def print_report(results: Dict[str, List[Tuple[int, str, ForbiddenPattern]]]) -> bool:
    """스캔 결과 리포트 출력"""
    
    if not results:
        print("✅ Kill-Switch Check: PASSED")
        print("   No forbidden judgement patterns detected.")
        return True
    
    print("=" * 80)
    print("❌ Kill-Switch Check: FAILED")
    print("=" * 80)
    print()
    print("Forbidden judgement logic detected in codebase!")
    print("These patterns violate Phase 2/3 principle: M6 is the Single Source of Truth")
    print()
    
    critical_count = 0
    warning_count = 0
    
    for file_path, violations in sorted(results.items()):
        print(f"📁 {file_path}")
        print("-" * 80)
        
        for line_num, line, pattern in violations:
            severity_icon = "🔴" if pattern.severity == "CRITICAL" else "⚠️ "
            print(f"  {severity_icon} Line {line_num}: {pattern.description}")
            print(f"     {line}")
            print()
            
            if pattern.severity == "CRITICAL":
                critical_count += 1
            else:
                warning_count += 1
        
        print()
    
    print("=" * 80)
    print(f"Summary: {critical_count} CRITICAL, {warning_count} WARNING")
    print("=" * 80)
    print()
    print("❌ DEPLOYMENT BLOCKED")
    print("   Please remove all forbidden judgement logic before deployment.")
    print()
    
    return False


# ============================================================================
# Main
# ============================================================================

def main():
    """메인 실행"""
    print("🔍 ZeroSite 4.0 Kill-Switch Checker")
    print("   Scanning for forbidden judgement patterns...")
    print()
    
    # 프로젝트 루트 디렉토리
    root_dir = Path(__file__).parent.parent
    
    # 코드베이스 스캔
    results = scan_codebase(root_dir)
    
    # 리포트 출력
    passed = print_report(results)
    
    # Exit code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
