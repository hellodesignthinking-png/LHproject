"""
ZeroSite v42.2 - Appraisal Single Source of Truth (SSOT) Enforcer
감정평가 기준 파이프라인 전면 고정 모듈

Purpose:
- Enforce Appraisal as the ONLY source for land-related data
- Prevent any fallback, calculation, or estimation outside Appraisal
- Validate data consistency across all engines and reports

Author: ZeroSite AI Development Team
Date: 2025-12-14
Version: 42.2.0
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AppraisalSSOTViolation:
    """
    Appraisal SSOT 위반 사항
    
    Attributes:
        engine_name: 위반한 엔진 이름
        field_name: 위반한 필드명
        violation_type: 위반 유형
        description: 상세 설명
        severity: 심각도 (critical, high, medium, low)
    """
    engine_name: str
    field_name: str
    violation_type: str  # "calculation", "fallback", "estimation", "duplication"
    description: str
    severity: str = "critical"


class AppraisalSSOTEnforcer:
    """
    감정평가 SSOT 강제 적용 엔진
    
    Core Principle:
    - Appraisal is the ONLY source for:
      - land_value (토지가치)
      - unit_price (단가)
      - official_price (공시지가)
      - zoning (용도지역)
      - market_summary (시장 요약)
      - transactions (거래 사례)
    
    - All other engines MUST:
      - Read from context["appraisal"]
      - Never calculate these values
      - Never use fallback values
      - Never estimate or approximate
    """
    
    # Protected fields (can only come from Appraisal)
    PROTECTED_FIELDS = {
        "land_value": "토지가치",
        "total_value": "총 토지가치",
        "unit_price": "단가 (원/㎡)",
        "value_per_sqm": "평당 가격",
        "official_price": "공시지가",
        "zoning": "용도지역",
        "zone_type": "용도지역 유형",
        "market_summary": "시장 요약",
        "transactions": "거래 사례",
        "comparable_sales": "비교 거래",
        "premium_ratio": "프리미엄 비율",
        "market_score": "시장 점수"
    }
    
    # Engines that must depend on Appraisal
    DEPENDENT_ENGINES = [
        "land_diagnosis",
        "capacity",
        "scenario",
        "lh_judge",
        "report"
    ]
    
    def __init__(self):
        """SSOT Enforcer 초기화"""
        self.version = "42.2.0"
        self.violations: List[AppraisalSSOTViolation] = []
        logger.info(f"✅ Appraisal SSOT Enforcer v{self.version} initialized")
    
    
    def validate_context(self, context: Dict[str, Any]) -> bool:
        """
        Context가 Appraisal SSOT를 준수하는지 검증
        
        Args:
            context: ZeroSite context dictionary
            
        Returns:
            True if valid, False if violations found
        """
        self.violations = []
        
        # Step 1: Appraisal 존재 여부 확인
        if "appraisal" not in context:
            self.violations.append(AppraisalSSOTViolation(
                engine_name="context",
                field_name="appraisal",
                violation_type="missing",
                description="❌ Appraisal data missing in context",
                severity="critical"
            ))
            return False
        
        appraisal = context["appraisal"]
        
        # Step 2: Appraisal 필수 필드 확인
        required_fields = ["total_value", "unit_price", "zoning", "transactions"]
        for field in required_fields:
            if field not in appraisal or appraisal[field] is None:
                self.violations.append(AppraisalSSOTViolation(
                    engine_name="appraisal",
                    field_name=field,
                    violation_type="missing",
                    description=f"❌ Required field '{field}' missing in Appraisal",
                    severity="critical"
                ))
        
        # Step 3: 다른 엔진에서 Protected Fields 중복 생성 여부 확인
        for engine_name in self.DEPENDENT_ENGINES:
            if engine_name in context:
                engine_data = context[engine_name]
                self._check_duplicate_fields(engine_name, engine_data, appraisal)
        
        # Step 4: Report에서 일관성 확인
        if "reports" in context:
            self._validate_report_consistency(context["reports"], appraisal)
        
        if self.violations:
            logger.error(f"❌ {len(self.violations)} SSOT violations found")
            for v in self.violations:
                logger.error(f"  - [{v.engine_name}] {v.field_name}: {v.description}")
            return False
        
        logger.info("✅ Context passes Appraisal SSOT validation")
        return True
    
    
    def _check_duplicate_fields(
        self,
        engine_name: str,
        engine_data: Dict[str, Any],
        appraisal: Dict[str, Any]
    ):
        """
        엔진 데이터에 Protected Fields 중복 생성 여부 확인
        """
        for field, description in self.PROTECTED_FIELDS.items():
            if field in engine_data:
                # 엔진에서 이 필드를 생성한 경우
                engine_value = engine_data[field]
                appraisal_value = appraisal.get(field)
                
                # 값이 다르면 violation
                if engine_value != appraisal_value:
                    self.violations.append(AppraisalSSOTViolation(
                        engine_name=engine_name,
                        field_name=field,
                        violation_type="duplication",
                        description=f"❌ {engine_name} calculated '{field}' (should reference Appraisal)",
                        severity="critical"
                    ))
    
    
    def _validate_report_consistency(
        self,
        reports: Dict[str, Any],
        appraisal: Dict[str, Any]
    ):
        """
        모든 보고서 간 Protected Fields 일관성 확인
        """
        # 보고서별 토지가치 추출
        report_values = {}
        
        for report_name, report_data in reports.items():
            if isinstance(report_data, dict):
                # 토지가치 관련 필드 추출
                for field in ["land_value", "total_value", "unit_price", "official_price"]:
                    if field in report_data:
                        if report_name not in report_values:
                            report_values[report_name] = {}
                        report_values[report_name][field] = report_data[field]
        
        # 모든 보고서의 값이 Appraisal과 일치하는지 확인
        for report_name, values in report_values.items():
            for field, value in values.items():
                appraisal_value = appraisal.get(field)
                
                if appraisal_value and value != appraisal_value:
                    self.violations.append(AppraisalSSOTViolation(
                        engine_name=f"report_{report_name}",
                        field_name=field,
                        violation_type="inconsistency",
                        description=f"❌ Report '{report_name}' has inconsistent '{field}'",
                        severity="high"
                    ))
    
    
    def lock_appraisal(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appraisal 데이터를 읽기 전용으로 잠금
        
        Args:
            context: ZeroSite context
            
        Returns:
            Updated context with locked appraisal
        """
        if "appraisal" in context:
            # Appraisal에 lock 플래그 추가
            context["appraisal"]["_locked"] = True
            context["appraisal"]["_locked_at"] = "v42.2"
            context["appraisal"]["_ssot_version"] = self.version
            
            logger.info("🔒 Appraisal data locked as SSOT")
        
        return context
    
    
    def enforce_read_only(
        self,
        engine_name: str,
        operation: str,
        field_name: str
    ) -> bool:
        """
        Protected Field 수정 시도 차단
        
        Args:
            engine_name: 수정을 시도하는 엔진 이름
            operation: 작업 유형 (read, write, calculate)
            field_name: 필드명
            
        Returns:
            True if allowed, False if blocked
        """
        # Appraisal 엔진만 Protected Fields 수정 가능
        if engine_name == "appraisal":
            return True
        
        # 다른 엔진의 write/calculate 시도 차단
        if operation in ["write", "calculate"] and field_name in self.PROTECTED_FIELDS:
            logger.error(
                f"❌ BLOCKED: {engine_name} attempted to {operation} protected field '{field_name}'"
            )
            self.violations.append(AppraisalSSOTViolation(
                engine_name=engine_name,
                field_name=field_name,
                violation_type="write_attempt",
                description=f"Attempted to {operation} protected field",
                severity="critical"
            ))
            return False
        
        # read 작업은 항상 허용
        return True
    
    
    def get_violations(self) -> List[AppraisalSSOTViolation]:
        """현재까지 감지된 모든 위반 사항 반환"""
        return self.violations
    
    
    def generate_violation_report(self) -> str:
        """
        위반 사항 리포트 생성 (Markdown)
        
        Returns:
            Markdown formatted report
        """
        if not self.violations:
            return "✅ No SSOT violations detected"
        
        report = f"""# Appraisal SSOT Violation Report

**Total Violations**: {len(self.violations)}

---

## Critical Violations

"""
        
        critical = [v for v in self.violations if v.severity == "critical"]
        if critical:
            for v in critical:
                report += f"""### {v.engine_name}.{v.field_name}

- **Type**: {v.violation_type}
- **Description**: {v.description}
- **Severity**: 🔴 CRITICAL

---

"""
        else:
            report += "None\n\n"
        
        report += """## High Severity Violations

"""
        
        high = [v for v in self.violations if v.severity == "high"]
        if high:
            for v in high:
                report += f"""### {v.engine_name}.{v.field_name}

- **Type**: {v.violation_type}
- **Description**: {v.description}
- **Severity**: 🟠 HIGH

---

"""
        else:
            report += "None\n\n"
        
        report += f"""
---

**Generated by**: Appraisal SSOT Enforcer v{self.version}
"""
        
        return report
    
    
    def create_reference_guide(self) -> str:
        """
        Appraisal SSOT 참조 가이드 생성
        
        Returns:
            Markdown formatted guide
        """
        guide = """# Appraisal SSOT Reference Guide

## Core Principle

**Appraisal is the ONLY source for land-related data.**

All engines must:
- ✅ Read from `context["appraisal"]`
- ❌ Never calculate land values
- ❌ Never use fallback values
- ❌ Never estimate or approximate

---

## Protected Fields

The following fields can ONLY come from Appraisal:

| Field | Korean | Engine Permission |
|-------|--------|-------------------|
"""
        
        for field, korean in self.PROTECTED_FIELDS.items():
            guide += f"| `{field}` | {korean} | Appraisal ONLY |\n"
        
        guide += """
---

## Correct Usage Pattern

### ✅ CORRECT: Read from Appraisal

```python
def land_diagnosis(context):
    # Read from Appraisal
    land_value = context["appraisal"]["total_value"]
    unit_price = context["appraisal"]["unit_price"]
    zoning = context["appraisal"]["zoning"]
    
    # Use for diagnosis
    diagnosis = analyze_suitability(land_value, zoning)
    
    return diagnosis
```

### ❌ WRONG: Calculate independently

```python
def land_diagnosis(context):
    # ❌ WRONG: Calculating land value independently
    land_area = context["land_area"]
    estimated_price = land_area * 1000000  # ❌ VIOLATION
    
    # ❌ WRONG: Using fallback
    zoning = context.get("zoning", "일반주거")  # ❌ VIOLATION
    
    return diagnosis
```

---

## Engine-specific Rules

### Land Diagnosis Engine
- ✅ MUST depend on Appraisal
- ❌ Cannot run without Appraisal
- ❌ Cannot calculate zoning/prices

### Capacity Engine
- ✅ Can calculate building capacity
- ❌ Cannot modify land values
- ❌ Must reference Appraisal for unit prices

### Scenario Engine
- ✅ Can vary unit types, building design
- ❌ Land value MUST remain constant across A/B/C
- ❌ Cannot recalculate land prices

### LH AI Judge
- ✅ Features MUST come from Appraisal
- ❌ No fallback features
- ❌ No estimated values

### Report Generators
- ✅ All 5 reports MUST use same Appraisal values
- ❌ Cannot have different land values per report
- ❌ Cross-report consistency enforced

---

## Validation Checklist

Before deploying any engine:

- [ ] Does it read from `context["appraisal"]`?
- [ ] Does it avoid calculating land values?
- [ ] Does it avoid fallback values?
- [ ] Does it produce consistent results?
- [ ] Does it pass SSOT validation?

---

**Enforced by**: Appraisal SSOT Enforcer v42.2.0
"""
        
        return guide


# Singleton instance
appraisal_ssot_enforcer = AppraisalSSOTEnforcer()
