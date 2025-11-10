# Public Housing Strategy & Risk Management Model

## Vision

Build a sustainable consulting model that integrates public policy insights, private-sector risk management, and social-value creation for Korea Land and Housing Corporation (LH) purchase-type public rental housing programs.

## I. LH Purchase-Type Rental Housing Monitoring Framework

### Objectives

- Continuously track policy updates, guideline revisions, and program evaluation trends related to LH purchase-type rental housing.
- Automatically align consulting processes, documentation, and site-evaluation models with legal and regulatory changes.
- Maintain a persistent competitive advantage through up-to-date intelligence.

### 1. Information Collection Channels and Cadence

| Category | Source | Monitoring Method | Frequency |
| --- | --- | --- | --- |
| LH Official Announcements | Bid and purchase notices on the LH website | RSS feeds or automated crawling | Daily |
| Government Policy Changes | Ministry of Land, Infrastructure and Transport releases; National Law Information Center updates | Keyword alerts (e.g., "매입임대", "공공주택특별법") and notification services | Weekly |
| Research Reports | LH Research Institute, KRIHS, Construction Industry Institute | Curate, summarize, and analyze published studies | Monthly |
| Procurement & Evaluation Practice | Regional LH headquarters announcements | Capture snapshots from the five LH regional headquarters and compare changes | Semiannual |
| Media & Policy Trends | News coverage of public rental housing (Bizwatch, Newspim, EToday, etc.) | Automated keyword clipping (e.g., "LH 매입임대", "사전약정", "건축비 연동형") | Near real-time; weekly summaries |

### 2. Internal Analysis Architecture

| Analysis Focus | Key Content | Application |
| --- | --- | --- |
| System Changes | Track policy updates across public rental housing types, internal LH guideline revisions, and appraisal formula adjustments | Update internal manuals |
| Evaluation Criteria Evolution | Monitor changes in LH scoring matrices and weights | Update site-diagnosis models and review manuals |
| Purchase Price & Construction Cost Trends | Capture official LH purchase prices, construction cost standards, and appraisal trends | Build profitability databases |
| Regulatory Risk Forecasting | Detect exclusions and delays stemming from legal or policy changes | Manage project timelines |
| Success & Failure Archives | Build case studies of accepted and rejected LH purchases by region | Refine client consulting and response strategies |

### 3. Operational Models

| Model | Description | Advantages |
| --- | --- | --- |
| Model A: Database & Report | Maintain an internal LH policy database and publish monthly reports | Rapid deployment |
| Model B: SaaS Monitoring Tool | Automate updates for announcements, regulations, and purchase prices with alerting | Differentiated competitiveness |
| Model C: Research Lab | Establish a "Public Housing Policy Research Center" and issue an annual white paper | Branding and credibility |

**Example Initiative**: *Public Housing Intelligence Center (PHIC)* — a dedicated internal research cell delivering real-time analysis on LH policy, construction costs, appraisal metrics, and locational trends, with the capacity to advise private developers and municipalities.

## II. Social Value Creation & Private Development Risk Management Strategy

### Strategic Goal

Connect private capital with public policy to balance social impact and profitability in public rental housing projects.

### 1. Social Value Implementation

| Area | Initiative | Expected Impact |
| --- | --- | --- |
| Community Integration | Design ground-floor community zones, shared kitchens, and local brand pop-ups | Strengthen regional vitality and public interest |
| Youth & Newlywed Housing Models | Offer tailored designs for LH target demographics | Address social demand and align with policy priorities |
| Local Partner Participation | Engage regional SMEs and artisans in construction | Generate local jobs and ESG outcomes |
| Public-Oriented Branding | Promote a "Social Housing Consulting" identity | Improve positioning with LH and public institutions |
| Sustainability Certification | Provide guidance on eco-friendly and energy-efficient design | Enhance ESG credentials and LH evaluation scores |

### 2. Private-Sector Risk Management

| Risk Type | Mitigation Strategy | Consulting Stage |
| --- | --- | --- |
| Site Risk | Deploy a pre-screening algorithm linked to an exclusion database | Early project planning |
| Permitting Risk | Review zoning and urban plans; coordinate with municipalities | Project design |
| Financing Risk | Structure project financing based on LH agreements; secure bank partnerships | Pre-agreement |
| Construction Risk | Advise on contractor selection and schedule control | Construction |
| Quality Risk | Run mock inspections aligned with LH commissioning criteria | Pre-completion |
| Purchase Price Risk | Simulate appraisal outcomes and document cost evidence | Acquisition |
| Policy Risk | Respond to policy changes via real-time monitoring and guidance | Full project lifecycle |

### 3. Integrated Framework — "Public Value + Private Stability"

```
      ┌────────────────────────────┐
      │  LH Monitoring Center (PHIC) │
      │  • Policy DB / Site, Pricing, Appraisal Analysis  │
      └───────────────┬────────────┘
                      ↓
      ┌────────────────────────────┐
      │  Private Project Consulting PM Team │
      │  • Site Diagnostics / Planning / Agreements / Delivery │
      └───────────────┬────────────┘
                      ↓
      ┌────────────────────────────┐
      │  Social Value & ESG Cell │
      │  • Community Design / Impact Measurement / ESG Reporting │
      └────────────────────────────┘
```

### Firm Positioning Statement

A **Public Housing Strategy & Risk Management Firm** that leverages real-time LH policy intelligence, minimizes risks for private development partners, and delivers social value through public rental housing projects.

## Appendix: Running the Automation Platform

To put the consulting model into practice, run the accompanying land-screening automation service included in this repository. The commands below summarize the detailed instructions from the project README.

1. **Set up a Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows는 venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create a `.env` file** with API keys and service endpoints.
   ```env
   KAKAO_REST_API_KEY=...
   LAND_REGULATION_API_KEY=...
   MOIS_API_KEY=...
   OPENAI_API_KEY=...
   DATABASE_URL=postgresql://user:password@localhost/lh_analysis
   REDIS_URL=redis://localhost:6379
   ```

3. **Launch the FastAPI server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Run the Celery worker** in a separate terminal to process background tasks.
   ```bash
   celery -A app.tasks worker --loglevel=info
   ```

5. **Send a sample request** once both services are running.
   ```bash
   curl -X POST "http://localhost:8000/api/analyze-land" \
     -H "Content-Type: application/json" \
     -d '{
       "address": "서울특별시 강남구 역삼동 123-45",
       "land_area": 500,
       "unit_type": "청년형"
     }'
   ```

For more deployment options, including Docker usage and advanced configuration, see the root-level `README.md`.

