# Phase 4 Architecture Plan

**Status**: DESIGN ONLY - NO IMPLEMENTATION  
**Version**: 0.1 (Draft)  
**Date**: 2025-12-22  
**Purpose**: Roadmap for next development phase

⚠️ **IMPORTANT**: This document is for planning only. Do NOT implement until Phase 3.5 is fully deployed and validated in production.

---

## Overview

Phase 4 transforms ZeroSite from **"automated report generator"** to **"managed service platform"** with:
- Admin dashboard for operations
- Customer report history tracking
- Paid report issuance flow
- LH official submission format

**Timeline**: TBD (dependent on Phase 3.5 production deployment)  
**Priority**: Medium (after Phase 3.5 stabilization)

---

## 1. Admin Dashboard

### Purpose
Provide operations team with centralized management interface for:
- System monitoring
- Customer support
- Quality assurance oversight
- Business analytics

### Core Features

#### 1.1 Real-Time Monitoring
- **Live Generation Queue**: Active PDF generation requests
- **System Health**: Module status (M2-M6), API response times
- **Error Dashboard**: Recent failures, QA blocks, 409 errors
- **Usage Metrics**: Reports generated per hour/day/month

#### 1.2 Customer Management
- **Customer List**: Active accounts, subscription status
- **Context Explorer**: Search by context_id, view frozen snapshots
- **Report History**: Per-customer generation history
- **Support Tools**: Regenerate reports, extend snapshot TTL (admin override)

#### 1.3 Quality Oversight
- **QA Failure Analysis**: Most common blocking issues
- **Narrative Review**: Spot-check generated narrative quality
- **Module Performance**: M2-M6 success/failure rates
- **Watermark Compliance**: Verify branding on all outputs

#### 1.4 Business Analytics
- **Revenue Tracking**: Paid reports vs. free trials
- **Report Type Popularity**: Most/least requested types
- **Customer Churn**: Inactive accounts, failed payments
- **LH Submission Stats**: Success rate of LH-submitted reports

### Technology Stack (Proposed)

**Frontend**:
- React + TypeScript
- Recharts for analytics
- TanStack Table for data grids
- Real-time updates via WebSocket

**Backend**:
- New router: `/api/v4/admin/*`
- Role-based access control (RBAC)
- Audit logging for all admin actions

**Database**:
- Admin activity log table
- Customer metadata table
- Session management

### UI Mockup (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│ ZeroSite Admin Dashboard                  [User: Admin] │
├─────────────────────────────────────────────────────────┤
│ 📊 Dashboard | 👥 Customers | 📄 Reports | ⚙️ Settings   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  System Health                    Active Requests        │
│  ┌───────────────┐               ┌──────────────────┐   │
│  │ M2: ✅ 100%   │               │ PDF Gen: 3       │   │
│  │ M5: ⚠️  95%   │               │ Queue: 0         │   │
│  │ M6: ✅ 98%    │               │ Avg Time: 6.2s   │   │
│  └───────────────┘               └──────────────────┘   │
│                                                           │
│  Recent Errors (Last 1 hour)                             │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 12:45 | 409 Block | context_abc123 | Stale (65min)│  │
│  │ 12:30 | QA FAIL   | context_xyz789 | Missing exec │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Final Report History Database Schema

### Purpose
Persistent storage of all report generation events for:
- Customer history tracking
- Billing/invoicing
- Audit compliance
- Analytics

### Database Tables (Draft)

#### Table: `final_report_generations`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique generation ID |
| `context_id` | VARCHAR(255) | NOT NULL | Analysis context |
| `customer_id` | VARCHAR(255) | FOREIGN KEY | Customer account |
| `report_type` | ENUM | NOT NULL | Type of report |
| `created_at` | TIMESTAMP | NOT NULL | Generation timestamp |
| `qa_status` | ENUM | NOT NULL | PASS/WARNING/FAIL |
| `pdf_generated` | BOOLEAN | NOT NULL | Success flag |
| `pdf_url` | VARCHAR(512) | NULLABLE | S3/Cloud storage URL |
| `html_preview_url` | VARCHAR(512) | NULLABLE | HTML S3 URL |
| `error_message` | TEXT | NULLABLE | Error if failed |
| `snapshot_age_minutes` | INTEGER | NULLABLE | Age at generation |
| `generation_time_ms` | INTEGER | NULLABLE | Performance metric |
| `is_paid` | BOOLEAN | DEFAULT false | Paid vs. free |
| `billing_status` | ENUM | NULLABLE | PENDING/PAID/REFUNDED |

**Indexes**:
- `idx_customer_created` ON (customer_id, created_at DESC)
- `idx_context` ON (context_id)
- `idx_qa_status` ON (qa_status)
- `idx_billing` ON (is_paid, billing_status)

#### Table: `customers`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `customer_id` | VARCHAR(255) | PRIMARY KEY | Unique customer ID |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| `name` | VARCHAR(255) | NOT NULL | Full name |
| `organization` | VARCHAR(255) | NULLABLE | Company name |
| `subscription_tier` | ENUM | NOT NULL | FREE/PRO/ENTERPRISE |
| `created_at` | TIMESTAMP | NOT NULL | Account creation |
| `last_login` | TIMESTAMP | NULLABLE | Last activity |
| `reports_quota` | INTEGER | DEFAULT 10 | Monthly limit |
| `reports_used` | INTEGER | DEFAULT 0 | Current usage |
| `stripe_customer_id` | VARCHAR(255) | NULLABLE | Payment integration |

#### Table: `admin_audit_log`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Log entry ID |
| `admin_user_id` | VARCHAR(255) | NOT NULL | Admin who acted |
| `action_type` | VARCHAR(100) | NOT NULL | e.g., "regenerate_pdf" |
| `target_entity` | VARCHAR(255) | NULLABLE | context_id or customer_id |
| `details` | JSONB | NULLABLE | Action details |
| `timestamp` | TIMESTAMP | NOT NULL | When it happened |
| `ip_address` | INET | NULLABLE | Source IP |

### Migration Strategy

**Phase 1**: Create tables in staging
**Phase 2**: Backfill from JSONL logs (if possible)
**Phase 3**: Switch to DB writes (dual-write period)
**Phase 4**: Deprecate JSONL logging

---

## 3. Paid Report Issuance Flow

### Business Model

**Free Tier**:
- 10 reports/month
- HTML preview unlimited
- PDF download rate-limited
- Watermark + QA Summary (standard)

**Pro Tier** ($99/month):
- 100 reports/month
- Priority PDF generation
- Extended snapshot TTL (2 hours)
- Bulk download API

**Enterprise** (Custom):
- Unlimited reports
- White-label option (remove watermark)
- SLA guarantee (99.9% uptime)
- Dedicated support

### Payment Flow (Stripe Integration)

```
1. Customer selects report type
2. Check quota: reports_used < reports_quota?
   ├─ Yes (Free tier): Generate immediately
   └─ No (Quota exceeded): Redirect to payment
3. Stripe Checkout Session
4. Payment Success Webhook → Increase quota
5. Redirect back to report generation
6. Generate PDF
7. Increment reports_used counter
8. Store in final_report_generations (is_paid=true)
```

### API Endpoints (Proposed)

```http
POST /api/v4/billing/checkout
# Create Stripe checkout session for quota upgrade

POST /api/v4/billing/webhook
# Stripe webhook for payment events

GET /api/v4/billing/quota
# Check current usage and limits

POST /api/v4/final-report/{type}/pdf (MODIFIED)
# Add payment validation before generation
```

### Database Changes

- Add `reports_quota` and `reports_used` to customers table
- Add `is_paid` column to final_report_generations
- Add `stripe_customer_id` for payment tracking

---

## 4. LH Submission Format Compliance

### Requirements (Based on LH Guidelines)

#### 4.1 Document Structure

**LH Official Format**:
1. **Cover Page**: Project name, applicant, submission date
2. **Table of Contents**: Auto-generated with page numbers
3. **Executive Summary**: 1-2 pages maximum
4. **Module Sections**: M2, M3, M4, M5, M6 in order
5. **Appendix**: Raw data tables, calculations
6. **Certification Page**: Signature block

**Current ZeroSite Format**:
- ❌ Missing: Cover page (LH-compliant)
- ❌ Missing: Table of contents
- ✅ Has: Executive summary (but needs reformatting)
- ✅ Has: Module sections
- ❌ Missing: Appendix section
- ❌ Missing: Certification page

#### 4.2 Styling Requirements

**LH Standards**:
- Font: Malgun Gothic (맑은 고딕) or Batang (바탕)
- Size: 11pt for body, 14pt for headings
- Margins: 25mm top/bottom, 20mm left/right
- Line spacing: 1.5
- Page numbers: Bottom center
- Headers: Project name + "LH 제출용"

**ZeroSite Current**:
- Font: Noto Sans KR (similar, but not exact)
- Size: Variable (needs standardization)
- Margins: 20mm all sides
- Line spacing: 1.6
- Page numbers: Not implemented
- Headers: Not implemented

#### 4.3 Content Requirements

**LH Checklist**:
- [ ] Project overview table (standardized format)
- [ ] Land registry information (공부상 정보)
- [ ] Zoning compliance statement (도시계획 적합 여부)
- [ ] Financial feasibility summary table
- [ ] LH pre-screening criteria checklist
- [ ] Risk assessment summary
- [ ] Applicant declaration statement

**Implementation Strategy**:

**Option A: Separate LH Report Type**
```python
# New report type: "lh_official_submission"
# Inherits from BaseFinalReportAssembler
# Adds LH-specific formatting + required sections
```

**Option B: Export Mode Flag**
```python
# Add query parameter: ?export_format=lh_official
# Modifies styling + adds required sections
# Keeps same report types
```

**Recommendation**: Option A (cleaner separation)

#### 4.4 File Naming Convention

**LH Requirement**:
```
{Project_Name}_{Applicant_Name}_{Submission_Date}_LH제출용.pdf
```

**Example**:
```
신림동123번지_토지주홍길동_20251222_LH제출용.pdf
```

#### 4.5 Metadata Embedding

**LH May Require**:
- PDF Author: Applicant name
- PDF Subject: "LH 사업 사전심사 제출용"
- PDF Keywords: Project address, housing type
- PDF Creator: "ZeroSite LH Submission Generator"

**Implementation** (via WeasyPrint):
```python
from weasyprint import HTML, CSS

pdf_bytes = HTML(string=html_content).write_pdf(
    metadata={
        'title': '신림동123번지 LH 제출용',
        'author': '홍길동',
        'subject': 'LH 사업 사전심사 제출용',
        'keywords': '신림동, 청년주택, LH',
        'creator': 'ZeroSite v1.0'
    }
)
```

---

## 5. Implementation Priorities

### Must-Have (P0)

1. **Final Report History DB**: Required for paid billing
2. **Paid Report Flow**: Revenue generation
3. **Basic Admin Dashboard**: Operations support

### Should-Have (P1)

4. **LH Submission Format**: Market requirement
5. **Customer Portal**: Self-service quota management

### Nice-to-Have (P2)

6. **Advanced Analytics**: Business intelligence
7. **White-Label Mode**: Enterprise feature
8. **Bulk Generation API**: Power users

---

## 6. Technical Considerations

### Database Selection

**Options**:
- PostgreSQL (recommended): ACID, JSONB support, mature
- MongoDB: Flexible schema, fast writes
- MySQL: Proven, wide adoption

**Recommendation**: PostgreSQL for relational integrity + JSONB for flexibility

### Storage Strategy

**Generated PDFs**:
- Store in S3 or compatible (MinIO for self-hosted)
- Retention: 90 days for free tier, 1 year for paid
- CDN for fast delivery

**File Naming**:
```
s3://zerosite-reports/{customer_id}/{year}/{month}/{generation_id}.pdf
```

### Performance Considerations

**PDF Generation**:
- Current: Synchronous (5-8 seconds)
- Phase 4: Async queue (Celery + Redis)
- Benefit: Non-blocking for large reports

**Database Queries**:
- Index on customer_id + created_at (most common query)
- Consider read replicas for analytics

---

## 7. Security & Compliance

### Data Protection

**Personal Information**:
- Encrypt customer email, name (AES-256)
- GDPR compliance: Right to deletion
- Data retention policy: 2 years

**Access Control**:
- Admin dashboard: Role-based (Admin, Support, Viewer)
- Customer data: Row-level security
- API keys: Rotate every 90 days

### Audit Requirements

**Log Everything**:
- Admin actions (with justification)
- Payment transactions
- Data access (who viewed what customer data)
- Report generation (already done)

---

## 8. Deployment Plan (When Ready)

### Prerequisites

1. Phase 3.5 in production for 30 days
2. Zero critical bugs reported
3. Operations team trained on current system

### Rollout Strategy

**Week 1-2**: Database migration + testing  
**Week 3**: Admin dashboard (read-only mode)  
**Week 4**: Paid report flow (beta customers)  
**Week 5-6**: LH format development  
**Week 7**: Full production launch

### Rollback Plan

- Keep JSONL logging active (dual-write)
- Database schema versioned with migrations
- Feature flags for gradual rollout

---

## 9. Open Questions (To Be Resolved)

1. **LH Format**: Do we have official LH template document?
2. **Pricing**: Final decision on free vs. paid tier limits?
3. **Payment**: Stripe only, or support other gateways?
4. **Compliance**: GDPR full audit needed?
5. **SLA**: What uptime guarantee for Enterprise?

---

## 10. Success Metrics (KPIs for Phase 4)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Admin Dashboard Usage | 100% ops team | Daily active users |
| Report History Queries | < 200ms p95 | DB performance |
| Paid Conversion Rate | > 5% | Free→Pro upgrades |
| LH Submission Success | > 90% | Accepted by LH |
| Customer Satisfaction | > 4.5/5 | NPS score |

---

## Conclusion

Phase 4 represents a **business maturity** upgrade, not just technical features. It's about:
- Making ZeroSite operationally sustainable
- Generating revenue to fund development
- Meeting real-world market needs (LH format)

**Do NOT start Phase 4 until**:
1. Phase 3.5 is deployed and stable
2. Business requirements are finalized
3. Resources (dev + ops) are allocated

---

**© 2025 ZeroSite by AntennaHoldings · nataiheum**  
**Internal Planning Document - Confidential**
