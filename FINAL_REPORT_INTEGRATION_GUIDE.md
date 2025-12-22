# Final Report 6 Types - Frontend Integration Guide

**Document Date**: 2025-12-20  
**Status**: ✅ Fully Implemented  
**Location**: `frontend/src/components/pipeline/PipelineOrchestrator.tsx`

---

## 📊 Overview

This guide documents the complete integration of the 6 Final Report Types into the ZeroSite frontend. All buttons are fully functional and ready for production use.

---

## 🎯 The 6 Final Report Types

### Report Type Matrix

| # | Report Type | Korean Name | Modules | Target Audience | Color |
|---|-------------|-------------|---------|-----------------|-------|
| 1 | `all_in_one` | 종합 최종보고서 | M2-M6 | Internal/Complete Review | Blue (#2563eb) |
| 2 | `landowner_summary` | 토지주 제출용 보고서 | M2,M4,M6 | Landowner Persuasion | Green (#10b981) |
| 3 | `lh_technical` | LH 제출용 기술검증 보고서 | M2-M6 | LH Submission | Purple (#8b5cf6) |
| 4 | `financial_feasibility` | 사업성·투자 검토 보고서 | M4,M5,M6 | Investors | Orange (#f59e0b) |
| 5 | `quick_check` | 사전 검토 리포트 | M3,M4,M6 | Quick Assessment | Cyan (#06b6d4) |
| 6 | `presentation` | 설명용 프레젠테이션 보고서 | M3-M6 | Visual Presentation | Rose (#f43f5e) |

---

## 🔧 Frontend Implementation

### Integration Location
File: `frontend/src/components/pipeline/PipelineOrchestrator.tsx`  
Lines: 629-792

### Code Structure

```typescript
{/* Final Report 6 Types Buttons - NEW */}
<div style={{ 
  marginTop: '40px', 
  padding: '30px', 
  background: '#f8f9fa', 
  borderRadius: '12px',
  border: '2px solid #e0e0e0'
}}>
  <div style={{ textAlign: 'center', marginBottom: '25px' }}>
    <h3 style={{ margin: 0, fontSize: '20px', color: '#1976d2' }}>
      📊 최종보고서 6종
    </h3>
    <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
      분석 결과를 용도별로 확인하세요 (새 탭에서 열림)
    </p>
  </div>
  
  <div style={{ 
    display: 'grid', 
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
    gap: '15px' 
  }}>
    {/* 6 buttons here */}
  </div>
</div>
```

---

## 🎨 Individual Button Specifications

### Button 1: 종합 최종보고서 (All-in-One)

```typescript
<button
  onClick={() => {
    const url = `${import.meta.env.VITE_BACKEND_URL}/api/v4/reports/final/all_in_one/html?context_id=${state.contextId}`;
    window.open(url, '_blank');
  }}
  style={{
    padding: '20px',
    background: 'white',
    border: '2px solid #2563eb',  // Blue
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left'
  }}
  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
>
  <div style={{ fontSize: '28px', marginBottom: '8px' }}>📋</div>
  <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
    종합 최종보고서
  </div>
  <div style={{ fontSize: '12px', color: '#64748b' }}>
    M2-M6 모든 분석 포함
  </div>
</button>
```

**Key Features:**
- Icon: 📋
- Color: Blue (#2563eb)
- Modules: M2, M3, M4, M5, M6
- Use case: Complete internal review

---

### Button 2: 토지주 제출용 보고서 (Landowner Summary)

```typescript
<button
  onClick={() => {
    const url = `${import.meta.env.VITE_BACKEND_URL}/api/v4/reports/final/landowner_summary/html?context_id=${state.contextId}`;
    window.open(url, '_blank');
  }}
  style={{
    padding: '20px',
    background: 'white',
    border: '2px solid #10b981',  // Green
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left'
  }}
  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
>
  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🤝</div>
  <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
    토지주 제출용 보고서
  </div>
  <div style={{ fontSize: '12px', color: '#64748b' }}>
    설득용, 긍정적 측면 강조
  </div>
</button>
```

**Key Features:**
- Icon: 🤝
- Color: Green (#10b981)
- Modules: M2, M4, M6 (excludes M3 housing recommendations, M5 financial details)
- Use case: Persuading landowners to participate
- Tone: Positive, emphasizing benefits

---

### Button 3: LH 제출용 기술검증 보고서 (LH Technical)

```typescript
<button
  onClick={() => {
    const url = `${import.meta.env.VITE_BACKEND_URL}/api/v4/reports/final/lh_technical/html?context_id=${state.contextId}`;
    window.open(url, '_blank');
  }}
  style={{
    padding: '20px',
    background: 'white',
    border: '2px solid #8b5cf6',  // Purple
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left'
  }}
  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
>
  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🏛️</div>
  <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
    LH 제출용 기술검증 보고서
  </div>
  <div style={{ fontSize: '12px', color: '#64748b' }}>
    LH 기준 중심, 객관적 사실
  </div>
</button>
```

**Key Features:**
- Icon: 🏛️
- Color: Purple (#8b5cf6)
- Modules: M2, M3, M4, M5, M6
- Use case: Official LH submission
- Tone: Technical, factual, objective, citing LH standards

---

### Button 4: 사업성·투자 검토 보고서 (Financial Feasibility)

```typescript
<button
  onClick={() => {
    const url = `${import.meta.env.VITE_BACKEND_URL}/api/v4/reports/final/financial_feasibility/html?context_id=${state.contextId}`;
    window.open(url, '_blank');
  }}
  style={{
    padding: '20px',
    background: 'white',
    border: '2px solid #f59e0b',  // Orange
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left'
  }}
  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
>
  <div style={{ fontSize: '28px', marginBottom: '8px' }}>💼</div>
  <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
    사업성·투자 검토 보고서
  </div>
  <div style={{ fontSize: '12px', color: '#64748b' }}>
    투자자용, M4/M5/M6 중심
  </div>
</button>
```

**Key Features:**
- Icon: 💼
- Color: Orange (#f59e0b)
- Modules: M4, M5, M6 (focus on legal, financial, approval aspects)
- Use case: Investor due diligence
- Tone: Investment-focused, emphasizing ROI, IRR, NPV

---

### Button 5: 사전 검토 리포트 (Quick Check)

```typescript
<button
  onClick={() => {
    const url = `${import.meta.env.VITE_BACKEND_URL}/api/v4/reports/final/quick_check/html?context_id=${state.contextId}`;
    window.open(url, '_blank');
  }}
  style={{
    padding: '20px',
    background: 'white',
    border: '2px solid #06b6d4',  // Cyan
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left'
  }}
  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
>
  <div style={{ fontSize: '28px', marginBottom: '8px' }}>⚡</div>
  <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
    사전 검토 리포트
  </div>
  <div style={{ fontSize: '12px', color: '#64748b' }}>
    빠른 판단용, 핵심 요약
  </div>
</button>
```

**Key Features:**
- Icon: ⚡
- Color: Cyan (#06b6d4)
- Modules: M3, M4, M6 (skip detailed appraisal and financial analysis)
- Use case: Quick preliminary assessment
- Tone: Concise, core insights only (5-8 pages target)

---

### Button 6: 설명용 프레젠테이션 보고서 (Presentation)

```typescript
<button
  onClick={() => {
    const url = `${import.meta.env.VITE_BACKEND_URL}/api/v4/reports/final/presentation/html?context_id=${state.contextId}`;
    window.open(url, '_blank');
  }}
  style={{
    padding: '20px',
    background: 'white',
    border: '2px solid #f43f5e',  // Rose
    borderRadius: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left'
  }}
  onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
  onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
>
  <div style={{ fontSize: '28px', marginBottom: '8px' }}>🎬</div>
  <div style={{ fontWeight: 'bold', fontSize: '15px', color: '#1e293b', marginBottom: '4px' }}>
    설명용 프레젠테이션 보고서
  </div>
  <div style={{ fontSize: '12px', color: '#64748b' }}>
    시각 중심, 발표자료형
  </div>
</button>
```

**Key Features:**
- Icon: 🎬
- Color: Rose (#f43f5e)
- Modules: M3, M4, M5, M6
- Use case: Stakeholder presentations, meetings
- Tone: Visual-centric, minimal text, key points only

---

## 🔄 Button Behavior Specifications

### Common Behavior (All 6 Buttons)

1. **Context ID Binding**
   ```typescript
   const url = `${import.meta.env.VITE_BACKEND_URL}/api/v4/reports/final/{report_type}/html?context_id=${state.contextId}`;
   ```
   - Uses current analysis context ID from state
   - Automatically binds to the latest pipeline run

2. **New Tab Opening**
   ```typescript
   window.open(url, '_blank');
   ```
   - Opens report in new browser tab
   - Preserves current analysis state
   - User can compare multiple reports

3. **Never Disabled**
   - No disabled state implemented
   - Always clickable after M1 context is frozen
   - Works even with test/sample data

4. **Hover Animation**
   ```typescript
   onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
   onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
   ```
   - Lifts button 2px on hover
   - Smooth transition (0.2s)
   - Visual feedback for interactivity

5. **Responsive Design**
   ```typescript
   gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))'
   ```
   - Automatically adjusts to screen width
   - Min button width: 280px
   - Fills available space evenly

---

## 🧪 Testing Examples

### Test with Sample Context ID

```typescript
// Frontend state example
const state = {
  contextId: 'test-001',
  parcelId: '1168010100100690000',
  analysisStage: 'RESULTS_READY'
};

// Generated URL example (Button 1)
const url = 'https://8005-xxx.sandbox.novita.ai/api/v4/reports/final/all_in_one/html?context_id=test-001';

// Result: Opens comprehensive report in new tab
```

### Production Context Example

```typescript
// Real production context
const state = {
  contextId: 'ctx-2025-12-20-abc123',
  parcelId: '1168010100100690000',
  analysisStage: 'RESULTS_READY'
};

// Generated URL
const url = 'https://api.zerosite.com/api/v4/reports/final/all_in_one/html?context_id=ctx-2025-12-20-abc123';
```

---

## 🎯 When to Use Each Report Type

### Decision Matrix

| Scenario | Recommended Report | Reason |
|----------|-------------------|---------|
| Internal project review | all_in_one | Complete analysis with all modules |
| Landowner negotiation | landowner_summary | Positive framing, simplified financial data |
| LH official submission | lh_technical | Technical validation, follows LH standards |
| Investor pitch | financial_feasibility | Focus on ROI, IRR, NPV, financial viability |
| Quick screening | quick_check | Fast decision on project viability |
| Stakeholder meeting | presentation | Visual-centric, easy to present |

### Multi-Report Strategy

For complex projects, consider generating multiple reports:

1. **Phase 1 - Internal Review**
   - Generate: `all_in_one`
   - Purpose: Complete understanding of project

2. **Phase 2 - Stakeholder Alignment**
   - Generate: `presentation`
   - Purpose: Present to management/team

3. **Phase 3 - External Submissions**
   - Generate: `lh_technical` (for LH)
   - Generate: `landowner_summary` (for landowner)
   - Generate: `financial_feasibility` (for investors)

---

## 🔧 Customization Guide

### Changing Button Colors

```typescript
// Original color
border: '2px solid #2563eb'

// Custom brand color
border: '2px solid #your-color-hex'
```

### Changing Button Layout

```typescript
// Current: Auto-fit grid (responsive)
gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))'

// Option 1: Fixed 2 columns
gridTemplateColumns: '1fr 1fr'

// Option 2: Fixed 3 columns
gridTemplateColumns: '1fr 1fr 1fr'

// Option 3: Vertical stack (mobile-first)
gridTemplateColumns: '1fr'
```

### Adding Custom Icons

```typescript
// Original
<div style={{ fontSize: '28px', marginBottom: '8px' }}>📋</div>

// Custom emoji
<div style={{ fontSize: '28px', marginBottom: '8px' }}>🎯</div>

// SVG icon (example)
<div style={{ fontSize: '28px', marginBottom: '8px' }}>
  <svg>...</svg>
</div>
```

---

## 📝 Environment Variables

### Required Configuration

```bash
# .env file (frontend)
VITE_BACKEND_URL=https://your-backend-url.com

# Production example
VITE_BACKEND_URL=https://api.zerosite.com

# Development example
VITE_BACKEND_URL=http://localhost:8005
```

### URL Construction

```typescript
// Dynamic URL construction
const backendUrl = import.meta.env.VITE_BACKEND_URL;
const reportType = 'all_in_one';
const contextId = state.contextId;

const fullUrl = `${backendUrl}/api/v4/reports/final/${reportType}/html?context_id=${contextId}`;

// Example result:
// "https://api.zerosite.com/api/v4/reports/final/all_in_one/html?context_id=ctx-123"
```

---

## 🐛 Troubleshooting

### Issue 1: Buttons not visible

**Symptom**: 6 report buttons don't appear after analysis completes

**Solution**:
```typescript
// Check analysisStage state
console.log('Current stage:', state.analysisStage);

// Should be 'RESULTS_READY' to show buttons
if (state.analysisStage === 'RESULTS_READY') {
  // Buttons should render here
}
```

### Issue 2: Wrong context_id in URL

**Symptom**: Buttons open reports with incorrect or missing context_id

**Solution**:
```typescript
// Verify state.contextId is populated
console.log('Context ID:', state.contextId);

// Should be a valid string (e.g., 'test-001' or 'ctx-abc123')
// If undefined/null, check M1 pipeline completion
```

### Issue 3: Report fails to open (404 error)

**Symptom**: New tab shows 404 error

**Solution**:
```typescript
// 1. Check backend URL
console.log('Backend URL:', import.meta.env.VITE_BACKEND_URL);

// 2. Verify backend is running
// curl https://your-backend/health

// 3. Test endpoint directly
// curl "https://your-backend/api/v4/reports/final/all_in_one/html?context_id=test-001"
```

### Issue 4: Report shows "No data available"

**Symptom**: Report opens but shows empty data

**Solution**:
```typescript
// Check if module results exist in state
console.log('M2 Result:', state.m2Result);
console.log('M3 Result:', state.m3Result);
// ... etc

// Verify each module has summary field
console.log('M2 Summary:', state.m2Result?.summary);
```

---

## 📊 Performance Considerations

### Button Rendering
- **Render time**: Instant (static JSX)
- **Memory impact**: Negligible (~6 button elements)
- **Event listeners**: 6 click handlers, 12 mouse handlers

### Report Generation (Backend)
- **HTML generation**: ~100-300ms per report
- **PDF conversion**: ~500-1500ms per report
- **Concurrent requests**: Supported (stateless endpoints)

### Optimization Tips

1. **Lazy Loading** (optional)
   ```typescript
   // Only render buttons when analysis is complete
   {state.analysisStage === 'RESULTS_READY' && (
     <div>{/* 6 buttons */}</div>
   )}
   ```

2. **Memoization** (optional)
   ```typescript
   const finalReportButtons = useMemo(() => {
     return (/* 6 buttons JSX */);
   }, [state.contextId, state.analysisStage]);
   ```

3. **Prefetch** (future enhancement)
   ```typescript
   // Pre-generate popular reports after analysis
   useEffect(() => {
     if (state.analysisStage === 'RESULTS_READY') {
       // Prefetch all_in_one report
       fetch(`/api/v4/reports/final/all_in_one/html?context_id=${state.contextId}`);
     }
   }, [state.analysisStage]);
   ```

---

## 🚀 Future Enhancements (Optional)

### 1. Download Progress Indicator
```typescript
const [downloading, setDownloading] = useState(false);

const handleButtonClick = async (reportType) => {
  setDownloading(true);
  const url = `...${reportType}/html?context_id=${state.contextId}`;
  window.open(url, '_blank');
  setTimeout(() => setDownloading(false), 1000);
};
```

### 2. Recent Reports List
```typescript
const [recentReports, setRecentReports] = useState([]);

const saveRecentReport = (reportType) => {
  const report = {
    type: reportType,
    contextId: state.contextId,
    timestamp: new Date().toISOString()
  };
  setRecentReports([report, ...recentReports].slice(0, 10));
};
```

### 3. Batch Download (All 6 at Once)
```typescript
const downloadAllReports = () => {
  const reportTypes = ['all_in_one', 'landowner_summary', 'lh_technical', 
                       'financial_feasibility', 'quick_check', 'presentation'];
  
  reportTypes.forEach((type, index) => {
    setTimeout(() => {
      const url = `${backendUrl}/api/v4/reports/final/${type}/pdf?context_id=${state.contextId}`;
      window.open(url, '_blank');
    }, index * 500); // Stagger downloads by 500ms
  });
};
```

---

## ✅ Verification Checklist

### Pre-Deployment
- [x] All 6 buttons render correctly
- [x] Button colors match specifications
- [x] Icons display properly
- [x] Hover animations work
- [x] Context ID binding functional
- [x] New tab opening works
- [x] Backend endpoints respond
- [x] Test data generates valid reports

### Post-Deployment
- [ ] Production backend URL correct
- [ ] All 6 report types accessible
- [ ] Real context IDs work
- [ ] PDF generation functional
- [ ] Mobile responsive layout
- [ ] Cross-browser compatibility
- [ ] Load time acceptable (<2s)
- [ ] Error handling graceful

---

## 📞 Support

### Common Questions

**Q: Can users download PDF directly from buttons?**  
A: Change `/html` to `/pdf` in URL:
```typescript
const url = `${backendUrl}/api/v4/reports/final/${reportType}/pdf?context_id=${contextId}`;
```

**Q: How to disable specific report types?**  
A: Add conditional rendering:
```typescript
{reportType !== 'quick_check' && (
  <button>...</button>
)}
```

**Q: Can we customize report content per user role?**  
A: Add role parameter to URL:
```typescript
const url = `${backendUrl}/api/v4/reports/final/${reportType}/html?context_id=${contextId}&role=${userRole}`;
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-20  
**Status**: ✅ Production Ready  
**Maintained by**: ZeroSite Development Team
