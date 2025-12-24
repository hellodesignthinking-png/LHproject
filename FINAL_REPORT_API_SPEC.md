# ZeroSite Final Report API - Official Specification

**Version**: 1.0  
**Date**: 2025-12-22  
**Status**: Production Ready  
**Base URL**: `https://api.zerosite.io` (production) / `http://localhost:8000` (development)

---

## Overview

The Final Report API provides automated generation of comprehensive LH project analysis reports in HTML and PDF formats. Six specialized report types are available, each tailored for specific stakeholders and decision-making scenarios.

### Key Features

- ✅ **6 Report Types**: Landowner, LH Technical, Quick Check, Financial Feasibility, All-in-One, Executive Summary
- ✅ **Quality Assurance**: Automated QA validation with blocking for insufficient quality
- ✅ **Freshness Protection**: Stale data blocking (>1 hour) prevents outdated reports
- ✅ **Brand Protection**: ZEROSITE watermark and copyright on all outputs
- ✅ **Transparency**: QA summary pages included in all reports

---

## Authentication

Currently no authentication required for development. Production will require API key.

```http
Authorization: Bearer {api_key}
```

---

## Endpoints

### 1. List Available Report Types

Get list of all available Final Report types with descriptions.

```http
GET /api/v4/final-report/types
```

#### Response 200 OK

```json
{
  "report_types": [
    {
      "id": "landowner_summary",
      "title": "토지주 요약 보고서",
      "description": "토지주를 위한 의사결정 지원 보고서",
      "target_audience": "토지주 (일반인)",
      "modules": ["M2", "M5", "M6"]
    },
    {
      "id": "lh_technical",
      "title": "LH 기술 검토 보고서",
      "description": "LH 심사 기준 기반 기술 검토",
      "target_audience": "LH 심사역",
      "modules": ["M2", "M3", "M4", "M6"]
    },
    {
      "id": "quick_check",
      "title": "Quick Check 보고서",
      "description": "5분 내 GO/NO-GO 판단",
      "target_audience": "의사결정권자",
      "modules": ["M5", "M6"]
    },
    {
      "id": "financial_feasibility",
      "title": "재무 타당성 보고서",
      "description": "투자 의사결정을 위한 재무 분석",
      "target_audience": "투자자 / 재무 담당자",
      "modules": ["M2", "M4", "M5"]
    },
    {
      "id": "all_in_one",
      "title": "종합 분석 보고서",
      "description": "전체 모듈 포함 완전 분석",
      "target_audience": "전체 이해관계자",
      "modules": ["M2", "M3", "M4", "M5", "M6"]
    },
    {
      "id": "executive_summary",
      "title": "경영진 요약 보고서",
      "description": "핵심 의사결정 요소만 압축",
      "target_audience": "경영진",
      "modules": ["M2", "M5", "M6"]
    }
  ]
}
```

---

### 2. Generate HTML Report

Generate Final Report in HTML format for preview.

```http
GET /api/v4/final-report/{report_type}/html?context_id={context_id}
```

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `report_type` | string | Yes | One of: `landowner_summary`, `lh_technical`, `quick_check`, `financial_feasibility`, `all_in_one`, `executive_summary` |

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context_id` | string | Yes | Frozen context ID from completed analysis |

#### Response 200 OK

```http
Content-Type: text/html; charset=utf-8

<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>토지주 요약 보고서</title>
  <style>
    /* ZEROSITE watermark CSS */
    body.final-report::before {
      content: 'ZEROSITE';
      position: fixed;
      top: 15px;
      right: 20px;
      /* ... */
    }
  </style>
</head>
<body class="final-report landowner_summary">
  <!-- Report Content -->
  
  <!-- QA Summary Page (Auto-inserted) -->
  <section class="qa-summary-page">
    <h2>Quality Assurance Summary</h2>
    <!-- QA Status, Checks, Warnings -->
  </section>
  
  <!-- Copyright Footer -->
  <footer class="report-footer zerosite-copyright">
    <div class="copyright">© ZeroSite by AntennaHoldings · nataiheum</div>
    <div class="report-metadata">
      <span>Report ID: {context_id}</span>
      <span>Type: {report_type}</span>
      <span>Created: {timestamp}</span>
    </div>
  </footer>
</body>
</html>
```

#### Error Responses

**400 Bad Request** - Invalid report type
```json
{
  "detail": "Invalid report type: invalid_type. Valid types: landowner_summary, lh_technical, quick_check, financial_feasibility, all_in_one, executive_summary"
}
```

**404 Not Found** - Context not found
```json
{
  "detail": "Context not found: abc123. Please run analysis first."
}
```

**400 Bad Request** - QA Failed (HTML generation only, does not block HTML)
```json
{
  "detail": "QA FAILED - Report does not meet quality standards. Issues: missing_executive_summary, missing_judgment_statement"
}
```

---

### 3. Generate PDF Report

Generate Final Report in PDF format for download and submission.

```http
GET /api/v4/final-report/{report_type}/pdf?context_id={context_id}
```

#### Path Parameters

Same as HTML endpoint.

#### Query Parameters

Same as HTML endpoint.

#### Response 200 OK

```http
Content-Type: application/pdf
Content-Disposition: attachment; filename="FinalReport_{report_type}_{context_id}_{timestamp}.pdf"

[PDF Binary Data]
```

#### Error Responses

**400 Bad Request** - Invalid report type (same as HTML)

**404 Not Found** - Context not found (same as HTML)

**409 Conflict** - Snapshot too old (CRITICAL BLOCKING)
```json
{
  "error": "OUTDATED_SNAPSHOT",
  "message": "Snapshot is too old (90 minutes). Maximum allowed age: 60 minutes. Please run a new analysis to generate fresh data.",
  "context_id": "abc123",
  "analyzed_at": "2025-12-22T10:00:00",
  "age_minutes": 90,
  "max_age_minutes": 60,
  "recommendation": "Run a new analysis with /api/v4/analyze endpoint"
}
```

**400 Bad Request** - QA Failed (BLOCKING)
```json
{
  "detail": "PDF generation blocked - Quality standards not met. Status: FAIL. Please check HTML version for details."
}
```

**501 Not Implemented** - PDF Library Not Available
```json
{
  "detail": "PDF generation not available - WeasyPrint library required"
}
```

**500 Internal Server Error** - Unexpected Error
```json
{
  "detail": "Internal error during PDF generation: {error_message}"
}
```

---

## Report Quality Assurance

### QA Status Levels

| Status | Description | PDF Generation |
|--------|-------------|----------------|
| **PASS** | All quality checks passed | ✅ Allowed |
| **WARNING** | Minor issues detected | ✅ Allowed (with warnings) |
| **FAIL** | Critical quality issues | ❌ **BLOCKED** |

### QA Validation Checks

1. **Executive Summary Exists**: Report must have executive summary section
2. **Narrative Sufficient**: Minimum paragraph count based on report type
3. **Judgment Statement Present**: Must contain explicit recommendation
4. **Decision Ready**: Report type-specific readiness (e.g., M5 profitability for landowner reports)

### QA Blocking Rules

PDF generation is **BLOCKED** when:
- ❌ Executive summary is missing
- ❌ Judgment statement is missing
- ❌ Status = FAIL with blocking issues

---

## Freshness Protection

### Snapshot Staleness Policy

**Maximum Snapshot Age**: 1 hour (60 minutes)

| Snapshot Age | HTML Generation | PDF Generation |
|--------------|-----------------|----------------|
| < 60 minutes | ✅ Allowed | ✅ Allowed |
| ≥ 60 minutes | ✅ Allowed | ❌ **BLOCKED (HTTP 409)** |

### Rationale

- Prevents legal liability from outdated data in formal documents
- Ensures financial/technical data reflects current conditions
- Protects brand reputation by blocking stale submissions

---

## Brand Protection

### ZEROSITE Watermark

All reports include:
- **Visual Watermark**: "ZEROSITE" in top-right corner (fixed position)
- **Opacity**: rgba(0, 123, 255, 0.3)
- **Print-safe**: Visible in both screen and PDF

### Copyright Footer

Every report footer includes:
```
© ZeroSite by AntennaHoldings · nataiheum
Report ID: {context_id} | Type: {report_type} | Created: {timestamp}

본 보고서는 ZeroSite 시스템에 의해 자동 생성되었습니다.
최종 의사결정 시 전문가 자문을 권장합니다.
```

---

## Operational Monitoring

### Generation History Logging

All generation attempts (success/failure) are logged to:
```
/logs/final_reports/generation_history.jsonl
```

**Log Format (JSONL)**:
```json
{
  "timestamp": "2025-12-22T12:47:19.888316",
  "context_id": "abc123",
  "report_type": "landowner_summary",
  "qa_status": "PASS",
  "pdf_generated": true,
  "error": null
}
```

**Logged Events**:
- ✅ Successful PDF generation
- ⚠️ QA blocking
- ❌ Snapshot staleness blocking
- ❌ Import errors (WeasyPrint)
- ❌ Unexpected exceptions

---

## Usage Examples

### Example 1: Get Available Report Types

```bash
curl -X GET "http://localhost:8000/api/v4/final-report/types"
```

### Example 2: Generate HTML Preview

```bash
curl -X GET "http://localhost:8000/api/v4/final-report/landowner_summary/html?context_id=abc123" \
  -H "Accept: text/html"
```

### Example 3: Download PDF

```bash
curl -X GET "http://localhost:8000/api/v4/final-report/landowner_summary/pdf?context_id=abc123" \
  -H "Accept: application/pdf" \
  -o "report.pdf"
```

### Example 4: Handle Stale Snapshot Error

```bash
curl -X GET "http://localhost:8000/api/v4/final-report/landowner_summary/pdf?context_id=old_abc" \
  -w "\nHTTP Status: %{http_code}\n"

# Response: HTTP 409
# Action: Run new analysis to get fresh context_id
```

---

## Best Practices

### For API Consumers

1. **Always check report types**: Use `/types` endpoint to get current list
2. **Handle 409 gracefully**: Prompt user to run new analysis for stale snapshots
3. **Preview before PDF**: Use HTML endpoint for preview, then PDF for final download
4. **Check QA warnings**: Even if PDF is allowed, review QA warnings for quality insights

### For System Integrators

1. **Cache report HTML**: HTML generation is faster, cache for preview
2. **Async PDF generation**: PDF conversion takes longer, consider async processing
3. **Monitor generation logs**: Track `/logs/final_reports/generation_history.jsonl` for operational insights
4. **Error handling**: Implement retry logic for transient errors, but respect 409 blocks

---

## Support & Contact

**Technical Support**: tech@zerosite.io  
**Sales Inquiries**: sales@zerosite.io  
**Documentation**: https://docs.zerosite.io

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-22 | Initial release with Phase 3.5 enhancements |

---

**© 2025 ZeroSite by AntennaHoldings · nataiheum**  
**This document is confidential and intended for authorized partners only.**
