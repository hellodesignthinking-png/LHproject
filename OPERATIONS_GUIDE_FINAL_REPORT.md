# ZeroSite Final Report - Operations Guide

**Version**: 1.0  
**Audience**: Operations Team, Customer Support, System Administrators  
**Last Updated**: 2025-12-22

---

## 📋 Table of Contents

1. [Final Report Generation Flow](#1-final-report-generation-flow)
2. [PDF Blocking Scenarios](#2-pdf-blocking-scenarios)
3. [QA Status Interpretation](#3-qa-status-interpretation)
4. [Generation History Monitoring](#4-generation-history-monitoring)
5. [Customer Support Response Templates](#5-customer-support-response-templates)
6. [Troubleshooting Guide](#6-troubleshooting-guide)

---

## 1. Final Report Generation Flow

### Normal Flow (Success Path)

```
1. Customer completes analysis → context_id generated
2. Customer requests PDF → System validates:
   ├─ Report type valid?
   ├─ Context exists?
   ├─ Snapshot fresh (< 1 hour)?
   └─ QA validation passes?
3. HTML generated with:
   ├─ Narrative layer
   ├─ Module content
   ├─ QA Summary page
   └─ Watermark + Copyright
4. PDF conversion (WeasyPrint)
5. PDF delivered to customer
6. Generation logged for monitoring
```

**Average Generation Time**:
- HTML: ~2-3 seconds
- PDF: ~5-8 seconds

---

## 2. PDF Blocking Scenarios

### 🔴 BLOCK SCENARIO 1: Stale Snapshot (HTTP 409)

**Trigger**: Snapshot age > 60 minutes

**Error Message Customer Sees**:
```
Snapshot is too old (90 minutes). 
Maximum allowed age: 60 minutes. 
Please run a new analysis to generate fresh data.
```

**Why Blocked**:
- Legal liability protection
- Data accuracy guarantee
- Brand reputation safeguard

**Customer Action Required**:
- Run new analysis from scratch
- Use new context_id
- Cannot "refresh" old snapshot

**HTML Preview**: ✅ Still works (for reference only)

---

### 🔴 BLOCK SCENARIO 2: QA Failure (HTTP 400)

**Trigger**: QA status = FAIL with blocking issues

**Common Blocking Issues**:
- Missing executive summary
- Missing judgment statement
- Critical module data missing

**Error Message Customer Sees**:
```
PDF generation blocked - Quality standards not met.
Status: FAIL.
Please check HTML version for details.
```

**Why Blocked**:
- Report incomplete for decision-making
- Missing critical narrative elements
- Cannot certify quality

**Customer Action Required**:
- Check HTML preview for QA Summary page
- Review "Validation Checks" table
- Address missing elements

**Internal Action**:
- Log incident for product team
- Check if module generation failed
- Verify narrative generator working

---

### ⚠️ WARNING SCENARIO: QA Warning (HTTP 200 with warnings)

**Trigger**: QA status = WARNING

**Common Warnings**:
- Narrative paragraph count low
- M5 shows project unprofitable
- Missing optional elements

**Customer Experience**:
- ✅ PDF generation proceeds
- ⚠️ Warning message logged
- 📋 QA Summary page shows warnings

**Why Allowed**:
- Report is technically complete
- Decision can still be made
- Transparency via QA Summary

**Customer Action**:
- Review QA Summary page in PDF
- Evaluate warnings for decision context
- No action required unless concerned

---

## 3. QA Status Interpretation

### QA Status Levels

| Status | Color | Meaning | PDF | Customer Impact |
|--------|-------|---------|-----|-----------------|
| **PASS** | 🟢 Green | All checks passed | ✅ Generated | No action needed |
| **WARNING** | 🟡 Yellow | Minor issues detected | ✅ Generated | Review QA page |
| **FAIL** | 🔴 Red | Critical issues | ❌ **BLOCKED** | Cannot proceed |

### QA Validation Checks Explained

#### 1. Executive Summary Exists
- **What**: Checks for section with class="executive-summary"
- **Why Critical**: Every report needs high-level overview
- **If Missing**: BLOCKING - Report cannot guide decisions

#### 2. Narrative Sufficient
- **What**: Counts paragraphs in narrative sections
- **Minimum by Report Type**:
  - Landowner Summary: 3 paragraphs
  - LH Technical: 5 paragraphs
  - Quick Check: 2 paragraphs
  - Financial Feasibility: 4 paragraphs
  - All-in-One: 6 paragraphs
  - Executive Summary: 2 paragraphs
- **Why Important**: Story context needed for understanding
- **If Insufficient**: WARNING (not blocking)

#### 3. Judgment Statement Present
- **What**: Searches for decision keywords:
  - "추천합니다", "부적합", "조건부 승인"
  - "추진 가능", "추진 곤란", "승인", "불가"
  - "GO", "NO-GO", "CONDITIONAL"
- **Why Critical**: Report must guide action
- **If Missing**: BLOCKING - Cannot certify as decision tool

#### 4. Decision Ready (Report-Specific)
- **What**: Validates report-type requirements:
  - Landowner: M5 NPV > 0 (profitability)
  - Financial: M5 NPV and IRR present
  - Quick Check: M6 decision present
- **Why Important**: Type-specific decision criteria
- **If Not Ready**: WARNING (context-dependent)

---

## 4. Generation History Monitoring

### Log File Location

```
/home/user/webapp/logs/final_reports/generation_history.jsonl
```

### Log Entry Structure

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

### Monitoring Queries

#### Count Successful Generations (Last 24 hours)

```bash
cat generation_history.jsonl | \
  jq 'select(.timestamp > "'$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S)'" and .pdf_generated == true)' | \
  wc -l
```

#### Find QA Failures

```bash
cat generation_history.jsonl | \
  jq 'select(.qa_status == "FAIL")' | \
  jq -r '[.timestamp, .context_id, .report_type] | @tsv'
```

#### Most Common Errors

```bash
cat generation_history.jsonl | \
  jq -r 'select(.error != null) | .error' | \
  sort | uniq -c | sort -rn
```

#### Report Type Distribution

```bash
cat generation_history.jsonl | \
  jq -r '.report_type' | \
  sort | uniq -c | sort -rn
```

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| QA Fail Rate | > 5% | > 10% | Investigate narrative generator |
| 409 Blocks | > 20/day | > 50/day | Review customer workflow |
| 500 Errors | > 2/hour | > 5/hour | Check system health |
| PDF Generation Time | > 15s avg | > 30s avg | Check WeasyPrint performance |

---

## 5. Customer Support Response Templates

### Template 1: Stale Snapshot (409 Error)

```
안녕하세요, 고객님.

보고서 생성 시 스냅샷 만료 오류가 발생했습니다.

[상황]
분석이 완료된 지 60분이 경과하여 데이터가 오래되었습니다.
ZeroSite는 법적 책임 보호를 위해 최신 데이터만 PDF로 제공합니다.

[해결 방법]
1. 새로운 분석을 실행해 주세요
2. 새로운 context_id를 받으세요
3. 60분 이내에 PDF를 다운로드하세요

[참고]
- HTML 미리보기는 언제든지 가능합니다 (참고용)
- PDF는 공식 제출용으로 최신 데이터만 허용됩니다

도움이 더 필요하시면 말씀해 주세요.

감사합니다.
ZeroSite 고객지원팀
```

---

### Template 2: QA Failure (400 Error)

```
안녕하세요, 고객님.

보고서 품질 검증 중 문제가 발견되었습니다.

[상황]
생성된 보고서가 ZeroSite 품질 기준을 충족하지 못했습니다.
이는 시스템 보호를 위한 자동 검증입니다.

[확인 사항]
1. HTML 미리보기에서 "Quality Assurance Summary" 섹션을 확인하세요
2. "검증 항목" 테이블에서 실패한 항목을 확인하세요
3. 해당 항목이 보고서에 누락되어 있을 수 있습니다

[일반적 원인]
- 분석 모듈(M2-M6) 실행 실패
- 필수 입력 데이터 누락
- 시스템 일시적 오류

[해결 방법]
1. 분석을 다시 실행해 주세요
2. 모든 필수 입력 항목을 확인해 주세요
3. 문제가 지속되면 고객지원팀에 context_id를 알려주세요

감사합니다.
ZeroSite 고객지원팀
```

---

### Template 3: QA Warning (200 with Warnings)

```
안녕하세요, 고객님.

보고서가 성공적으로 생성되었습니다. (경고 포함)

[상황]
PDF가 정상적으로 생성되었으나 일부 경고 사항이 있습니다.
이는 의사결정에 참고하시라는 알림입니다.

[확인 방법]
PDF 마지막 페이지의 "Quality Assurance Summary"를 확인하세요.
경고 사항이 노란색으로 표시되어 있습니다.

[일반적 경고]
- "사업성이 낮음" (M5 NPV 음수)
- "서술이 짧음" (최소 단락 수 미달)

[조치]
- 경고는 참고용이며, 보고서 사용에는 문제 없습니다
- 의사결정 시 경고 내용을 고려하시면 됩니다

질문이 있으시면 언제든지 연락주세요.

감사합니다.
ZeroSite 고객지원팀
```

---

## 6. Troubleshooting Guide

### Issue 1: PDF Generation Takes Too Long

**Symptoms**: Customer reports PDF download > 30 seconds

**Diagnosis**:
```bash
# Check recent generation times
tail -100 generation_history.jsonl | \
  jq 'select(.pdf_generated == true)'
```

**Common Causes**:
1. Large report (All-in-One type)
2. Complex module HTML (many images/tables)
3. WeasyPrint CPU usage high

**Solutions**:
- Monitor server CPU/memory
- Consider async PDF generation
- Cache module HTML for faster assembly

---

### Issue 2: Sudden Spike in 409 Errors

**Symptoms**: Many customers hitting snapshot expiry

**Diagnosis**:
```bash
# Count 409 errors today
grep "OUTDATED_SNAPSHOT" logs/ -r | wc -l
```

**Common Causes**:
1. Customers doing analysis early, downloading later
2. Workflow education needed
3. Analysis-to-PDF time > 60 minutes

**Solutions**:
- Send reminder email: "Download PDF within 60 minutes"
- Add countdown timer in UI
- Consider extending to 90 minutes (business decision)

---

### Issue 3: QA Failures Increasing

**Symptoms**: More FAIL status in logs

**Diagnosis**:
```bash
# QA failure reasons
cat generation_history.jsonl | \
  jq -r 'select(.qa_status == "FAIL") | .error'
```

**Common Causes**:
1. Module generation failures (M2-M6)
2. Narrative generator issues
3. Input data quality problems

**Solutions**:
- Check module logs for M2-M6 failures
- Review narrative generator templates
- Validate input data quality

---

### Issue 4: Copyright Footer Missing

**Symptoms**: Customer reports no copyright in PDF

**Diagnosis**:
1. Check HTML preview for footer
2. Verify assembler using `get_zerosite_copyright_footer()`
3. Check CSS loading

**Fix**:
- All assemblers should call `self.get_zerosite_copyright_footer()`
- Verify in `_generate_footer()` method

---

## Escalation Procedures

### Level 1: Customer Support (Tier 1)

**Handle**:
- Stale snapshot errors (409)
- QA warnings explanation
- General questions

**Escalate If**:
- QA FAIL without clear cause
- System errors (500)
- Data accuracy concerns

---

### Level 2: Technical Support (Tier 2)

**Handle**:
- QA validation issues
- Module generation failures
- Log analysis

**Escalate If**:
- System architecture issues
- Performance degradation
- Security concerns

---

### Level 3: Engineering (Development Team)

**Handle**:
- Code bugs
- Architecture changes
- Performance optimization

---

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| Customer Support Lead | support@zerosite.io | 24/7 |
| Technical Support | tech@zerosite.io | Business hours |
| On-Call Engineer | oncall@zerosite.io | 24/7 (emergencies) |

---

## Appendix: Quick Reference

### HTTP Status Codes

- **200 OK**: Success (may have warnings)
- **400 Bad Request**: Invalid input or QA failure
- **404 Not Found**: Context not found
- **409 Conflict**: Snapshot too old
- **500 Internal Error**: System error
- **501 Not Implemented**: WeasyPrint missing

### Report Types Cheat Sheet

| Type | Modules | Pages | Target | Time |
|------|---------|-------|--------|------|
| landowner_summary | M2,M5,M6 | ~15 | 토지주 | ~5s |
| lh_technical | M2,M3,M4,M6 | ~20 | LH 심사역 | ~6s |
| quick_check | M5,M6 | ~8 | 의사결정권자 | ~3s |
| financial_feasibility | M2,M4,M5 | ~18 | 투자자 | ~6s |
| all_in_one | M2,M3,M4,M5,M6 | ~30 | 전체 | ~10s |
| executive_summary | M2,M5,M6 | ~10 | 경영진 | ~4s |

---

**© 2025 ZeroSite by AntennaHoldings · nataiheum**  
**Internal Use Only - Confidential**
