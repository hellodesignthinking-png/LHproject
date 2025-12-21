# 🚀 ZeroSite v3.4 Upgrade Plan
## Complete Land Appraisal Input System Integration

**Status**: Ready for Implementation  
**Date**: 2025-12-15  
**Version**: v3.3 → v3.4  

---

## 📊 What's Changing?

### Current v3.3 Limitations
- ❌ No land address input functionality
- ❌ No automatic appraisal lookup
- ❌ Users must manually prepare appraisal_context
- ❌ No Premium manual override options
- ❌ Cannot select which reports to generate
- ❌ Mock API demonstration only

### New v3.4 Capabilities
- ✅ **Address Input** → Users enter land address
- ✅ **Auto Lookup** → System fetches 공시지가, 용도지역, 거리사례
- ✅ **Preview Card** → Show fetched data in beautiful UI
- ✅ **Manual Override** → Allow Premium score adjustments
- ✅ **Report Selection** → Checkboxes for report types
- ✅ **Integrated Generation** → One-click bulk report creation
- ✅ **Result Display** → Download links for all formats

---

## 🎯 Implementation Summary

### 1. Backend API (✅ COMPLETE)

**File**: `app/api/endpoints/reports_v3.py`

**New Endpoint Added**:
```python
GET /api/v3/reports/lookup?address={address}
```

**Response Structure**:
```json
{
  "success": true,
  "address": "서울특별시 강남구 테헤란로 123",
  "parcel_id": "...",
  "land_area_sqm": 660.0,
  "public_price_per_sqm": 4850000,
  "zoning_type": "제2종일반주거지역",
  "far": 250.0,
  "bcr": 50.0,
  "samples": [...],
  "premium": {
    "road_score": 8.5,
    "topography_score": 7.0,
    "overall_premium": 30.0
  }
}
```

**Status**: ✅ Implemented with mock data (ready for real API integration)

---

### 2. Frontend HTML Structure (🔄 IN PROGRESS)

**File**: `static/index.html`

**New Sections to Add** (between Hero and Canonical Flow):

#### Section A: Land Input System
```html
<section class="land-input-system" id="input">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title">토지 분석 시작하기</h2>
            <p class="section-subtitle">
                주소 입력만으로 자동 감정평가 → 보고서 생성까지
            </p>
        </div>
        
        <!-- Address Input -->
        <div class="input-card">
            <div class="input-step">
                <span class="step-number">1</span>
                <h3>토지 주소 입력</h3>
            </div>
            <div class="input-form">
                <input 
                    type="text" 
                    id="land-address" 
                    placeholder="예: 서울특별시 강남구 테헤란로 123"
                    class="address-input"
                />
                <button onclick="lookupAddress()" class="btn btn-primary">
                    <i class="fas fa-search"></i>
                    자동조회 실행
                </button>
            </div>
        </div>
        
        <!-- Lookup Result Preview (Hidden initially) -->
        <div id="lookup-result" class="lookup-result" style="display: none;">
            <!-- Will be populated by JavaScript -->
        </div>
        
        <!-- Premium Override (Collapsible) -->
        <div id="premium-override" class="premium-override" style="display: none;">
            <!-- Manual adjustment fields -->
        </div>
        
        <!-- Report Selection -->
        <div id="report-selection" class="report-selection" style="display: none;">
            <div class="input-step">
                <span class="step-number">2</span>
                <h3>생성할 보고서 선택</h3>
            </div>
            <div class="report-checkboxes">
                <label class="checkbox-card">
                    <input type="checkbox" id="select-pre-report" checked />
                    <div class="checkbox-content">
                        <i class="fas fa-bolt"></i>
                        <span>Pre-Report (2p)</span>
                    </div>
                </label>
                <label class="checkbox-card">
                    <input type="checkbox" id="select-comprehensive" checked />
                    <div class="checkbox-content">
                        <i class="fas fa-file-contract"></i>
                        <span>Comprehensive (17p)</span>
                    </div>
                </label>
                <label class="checkbox-card">
                    <input type="checkbox" id="select-lh-decision" />
                    <div class="checkbox-content">
                        <i class="fas fa-check-circle"></i>
                        <span>LH Decision</span>
                    </div>
                </label>
                <label class="checkbox-card">
                    <input type="checkbox" id="select-investor" />
                    <div class="checkbox-content">
                        <i class="fas fa-chart-line"></i>
                        <span>Investor (12p)</span>
                    </div>
                </label>
                <label class="checkbox-card">
                    <input type="checkbox" id="select-land-price" />
                    <div class="checkbox-content">
                        <i class="fas fa-coins"></i>
                        <span>Land Price</span>
                    </div>
                </label>
                <label class="checkbox-card">
                    <input type="checkbox" id="select-internal" />
                    <div class="checkbox-content">
                        <i class="fas fa-clipboard-check"></i>
                        <span>Internal (5p)</span>
                    </div>
                </label>
            </div>
        </div>
        
        <!-- Generate Button -->
        <div id="generate-section" class="generate-section" style="display: none;">
            <button onclick="generateSelectedReports()" class="btn btn-primary btn-large">
                <i class="fas fa-magic"></i>
                선택한 보고서 생성하기
            </button>
        </div>
    </div>
</section>
```

---

### 3. CSS Styles (🔄 IN PROGRESS)

**File**: `static/css/landing.css`

**New Styles to Add**:

```css
/* Land Input System */
.land-input-system {
    padding: var(--spacing-2xl) 0;
    background: var(--primary-bg);
}

.input-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-lg);
}

.input-step {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    margin-bottom: var(--spacing-md);
}

.step-number {
    width: 40px;
    height: 40px;
    background: var(--accent-mint);
    color: var(--primary-bg);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: var(--font-size-lg);
}

.input-form {
    display: flex;
    gap: var(--spacing-md);
}

.address-input {
    flex: 1;
    padding: 1rem 1.5rem;
    background: var(--secondary-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-size: var(--font-size-base);
    transition: border-color 0.2s;
}

.address-input:focus {
    outline: none;
    border-color: var(--accent-mint);
}

.lookup-result {
    background: var(--card-bg);
    border: 2px solid var(--accent-mint);
    border-radius: var(--radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-lg);
}

.result-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
}

.result-item {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
}

.result-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
}

.result-value {
    font-size: var(--font-size-xl);
    font-weight: 700;
    color: var(--text-primary);
}

.report-checkboxes {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: var(--spacing-md);
}

.checkbox-card {
    cursor: pointer;
}

.checkbox-card input[type="checkbox"] {
    display: none;
}

.checkbox-content {
    background: var(--secondary-bg);
    border: 2px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-lg);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
    transition: all 0.2s;
    text-align: center;
}

.checkbox-card input:checked + .checkbox-content {
    background: rgba(35, 230, 166, 0.1);
    border-color: var(--accent-mint);
}

.checkbox-content i {
    font-size: var(--font-size-2xl);
    color: var(--accent-mint);
}

.generate-section {
    text-align: center;
    padding: var(--spacing-xl) 0;
}

.btn-large {
    padding: 1.25rem 3rem;
    font-size: var(--font-size-lg);
}
```

---

### 4. JavaScript Logic (🔄 IN PROGRESS)

**File**: `static/js/landing.js`

**New Functions to Add**:

```javascript
// Global state for lookup data
let lookupData = null;

/**
 * Lookup address and fetch appraisal data
 */
async function lookupAddress() {
    const addressInput = document.getElementById('land-address');
    const address = addressInput.value.trim();
    
    if (!address) {
        alert('주소를 입력해주세요');
        return;
    }
    
    try {
        // Show loading state
        const btn = event.target;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 조회중...';
        
        // Call lookup API
        const response = await fetch(`${API_BASE_URL}/api/v3/reports/lookup?address=${encodeURIComponent(address)}`);
        const data = await response.json();
        
        if (data.success) {
            // Store lookup data
            lookupData = data;
            
            // Display results
            displayLookupResult(data);
            
            // Show report selection
            document.getElementById('report-selection').style.display = 'block';
            document.getElementById('generate-section').style.display = 'block';
            
            // Scroll to results
            document.getElementById('lookup-result').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        } else {
            alert('조회 실패: ' + (data.error || '알 수 없는 오류'));
        }
        
        // Reset button
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-search"></i> 자동조회 실행';
        
    } catch (error) {
        console.error('Lookup failed:', error);
        alert('조회 중 오류가 발생했습니다: ' + error.message);
        
        // Reset button
        const btn = event.target;
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-search"></i> 자동조회 실행';
    }
}

/**
 * Display lookup result in preview card
 */
function displayLookupResult(data) {
    const resultDiv = document.getElementById('lookup-result');
    
    resultDiv.innerHTML = `
        <div class="input-step">
            <span class="step-number">✓</span>
            <h3>자동조회 결과</h3>
        </div>
        <div class="result-grid">
            <div class="result-item">
                <div class="result-label">주소</div>
                <div class="result-value" style="font-size: 1rem;">${data.address}</div>
            </div>
            <div class="result-item">
                <div class="result-label">면적</div>
                <div class="result-value">${data.land_area_sqm?.toLocaleString()} ㎡</div>
            </div>
            <div class="result-item">
                <div class="result-label">공시지가 (㎡)</div>
                <div class="result-value">${data.public_price_per_sqm?.toLocaleString()}원</div>
            </div>
            <div class="result-item">
                <div class="result-label">용도지역</div>
                <div class="result-value" style="font-size: 1rem;">${data.zoning_type}</div>
            </div>
            <div class="result-item">
                <div class="result-label">용적률</div>
                <div class="result-value">${data.far}%</div>
            </div>
            <div class="result-item">
                <div class="result-label">건폐율</div>
                <div class="result-value">${data.bcr}%</div>
            </div>
        </div>
        
        ${data.samples && data.samples.length > 0 ? `
        <div style="margin-top: 2rem;">
            <h4 style="margin-bottom: 1rem;">거리사례 (${data.samples.length}건)</h4>
            <div class="result-grid">
                ${data.samples.map((sample, idx) => `
                    <div class="result-item">
                        <div class="result-label">사례 ${idx + 1} (${sample.distance_m}m)</div>
                        <div class="result-value" style="font-size: 1rem;">
                            ${sample.price_per_sqm.toLocaleString()}원/㎡
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
        ` : ''}
        
        ${data.premium ? `
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(35, 230, 166, 0.1); border-radius: 0.5rem;">
            <h4 style="margin-bottom: 0.5rem; color: var(--accent-mint);">
                <i class="fas fa-star"></i> Premium 분석
            </h4>
            <p style="color: var(--text-secondary);">
                도로점수: ${data.premium.road_score}/10 | 
                지형점수: ${data.premium.topography_score}/10 | 
                전체 할증률: ${data.premium.overall_premium}%
            </p>
        </div>
        ` : ''}
    `;
    
    resultDiv.style.display = 'block';
}

/**
 * Generate selected reports
 */
async function generateSelectedReports() {
    if (!lookupData) {
        alert('먼저 토지 조회를 실행해주세요');
        return;
    }
    
    // Get selected reports
    const selectedReports = [];
    if (document.getElementById('select-pre-report').checked) selectedReports.push('pre_report');
    if (document.getElementById('select-comprehensive').checked) selectedReports.push('comprehensive');
    if (document.getElementById('select-lh-decision').checked) selectedReports.push('lh_decision');
    if (document.getElementById('select-investor').checked) selectedReports.push('investor');
    if (document.getElementById('select-land-price').checked) selectedReports.push('land_price');
    if (document.getElementById('select-internal').checked) selectedReports.push('internal');
    
    if (selectedReports.length === 0) {
        alert('최소 1개 이상의 보고서를 선택해주세요');
        return;
    }
    
    // Build appraisal context from lookup data
    const appraisalContext = {
        calculation: {
            land_area_sqm: lookupData.land_area_sqm,
            land_area_pyeong: lookupData.land_area_pyeong,
            final_appraised_total: lookupData.public_price_total * 1.3, // Apply 30% premium
            final_appraised_per_sqm: lookupData.public_price_per_sqm * 1.3,
            confidence_level: "MEDIUM"
        },
        zoning: {
            confirmed_type: lookupData.zoning_type,
            far: lookupData.far,
            bcr: lookupData.bcr,
            max_floors: lookupData.max_floors || 5
        },
        metadata: {
            address: lookupData.address,
            parcel_id: lookupData.parcel_id
        },
        official_land_price: {
            standard_price_per_sqm: lookupData.public_price_per_sqm,
            reference_year: lookupData.public_price_year || 2024,
            total_value: lookupData.public_price_total
        }
    };
    
    // Show generation modal
    showGenerationModal(selectedReports);
    
    // Generate reports sequentially
    const results = [];
    for (const reportType of selectedReports) {
        try {
            updateModalProgress(`Generating ${reportType}...`);
            
            const response = await fetch(`${API_BASE_URL}/api/v3/reports/${reportType.replace('_', '-')}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ appraisal_context: appraisalContext })
            });
            
            const result = await response.json();
            results.push({ type: reportType, data: result, success: response.ok });
        } catch (error) {
            console.error(`Failed to generate ${reportType}:`, error);
            results.push({ type: reportType, error: error.message, success: false });
        }
    }
    
    // Show results
    displayGenerationResults(results);
}

/**
 * Show generation modal
 */
function showGenerationModal(reportTypes) {
    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = modal.querySelector('.modal-body');
    
    modalTitle.textContent = `Generating ${reportTypes.length} Reports...`;
    modalBody.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-circle-notch fa-spin"></i>
        </div>
        <p id="modal-progress">Preparing...</p>
    `;
    
    modal.style.display = 'block';
}

/**
 * Update modal progress message
 */
function updateModalProgress(message) {
    const progressEl = document.getElementById('modal-progress');
    if (progressEl) {
        progressEl.textContent = message;
    }
}

/**
 * Display generation results
 */
function displayGenerationResults(results) {
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('reportModal').querySelector('.modal-body');
    
    const successCount = results.filter(r => r.success).length;
    
    modalTitle.textContent = `Generation Complete: ${successCount}/${results.length} Successful`;
    
    modalBody.innerHTML = `
        <div class="result-success">
            <i class="fas fa-check-circle"></i>
            <h3>Reports Generated!</h3>
            <div class="result-list">
                ${results.map(r => `
                    <div class="result-row ${r.success ? 'success' : 'failed'}">
                        <span class="result-icon">
                            <i class="fas fa-${r.success ? 'check' : 'times'}-circle"></i>
                        </span>
                        <span class="result-name">${r.type}</span>
                        ${r.success ? `
                            <div class="result-actions">
                                <button class="btn-small" onclick="window.open('${API_BASE_URL}/api/v3/reports/${r.data.report_id}/json', '_blank')">
                                    JSON
                                </button>
                                <button class="btn-small" onclick="window.open('${API_BASE_URL}/api/v3/reports/${r.data.report_id}/pdf', '_blank')">
                                    PDF
                                </button>
                            </div>
                        ` : `<span class="error-msg">${r.error}</span>`}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Export new functions
window.lookupAddress = lookupAddress;
window.generateSelectedReports = generateSelectedReports;
```

---

## 🎯 User Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│  1. User lands on ZeroSite v3.4                         │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  2. Enters land address in input field                   │
│     Example: "서울특별시 강남구 테헤란로 123"            │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  3. Clicks "자동조회 실행" button                         │
│     → API: GET /api/v3/reports/lookup?address=...       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  4. System displays lookup result preview card          │
│     - 면적, 공시지가, 용도지역, FAR, BCR                │
│     - 거리사례 3건                                        │
│     - Premium 분석 결과                                   │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  5. [Optional] User adjusts Premium manually            │
│     → Checkboxes reveal override input fields           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  6. User selects which reports to generate              │
│     □ Pre-Report (2p)                                   │
│     □ Comprehensive (17p)                               │
│     □ LH Decision                                       │
│     □ Investor (12p)                                    │
│     □ Land Price                                        │
│     □ Internal (5p)                                     │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  7. Clicks "선택한 보고서 생성하기" button                │
│     → Builds appraisal_context from lookup data         │
│     → Calls POST /api/v3/reports/{type} for each        │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  8. System shows generation progress modal              │
│     "Generating pre_report..."                          │
│     "Generating comprehensive..."                       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  9. Results displayed with download buttons             │
│     ✓ Pre-Report → [JSON] [PDF]                        │
│     ✓ Comprehensive → [JSON] [PDF]                     │
│     ✗ Investor → Error message                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Checklist

### Backend
- [x] Create lookup API endpoint (`/api/v3/reports/lookup`)
- [x] Add mock data response structure
- [ ] Integrate real government APIs (future)
- [x] Update health check to show v3.4

### Frontend HTML
- [ ] Add Land Input System section
- [ ] Add address input field
- [ ] Add lookup result preview card
- [ ] Add Premium override collapsible panels
- [ ] Add report selection checkboxes
- [ ] Add generation button

### Frontend CSS
- [ ] Style land-input-system section
- [ ] Style address input field
- [ ] Style lookup result card
- [ ] Style checkbox cards
- [ ] Style generation progress modal

### Frontend JS
- [ ] Implement `lookupAddress()` function
- [ ] Implement `displayLookupResult()` function
- [ ] Implement `generateSelectedReports()` function
- [ ] Update modal display logic
- [ ] Add generation progress tracking

### Testing
- [ ] Test lookup API with various addresses
- [ ] Test report generation with lookup data
- [ ] Test Premium override functionality
- [ ] Test mobile responsiveness
- [ ] Test error handling

---

## 🚀 Next Steps

1. **Complete Frontend Implementation** (2-3 hours)
   - Add new HTML sections
   - Add new CSS styles
   - Add new JavaScript logic

2. **Test Complete Workflow** (30 min)
   - Address input → lookup → preview → select → generate

3. **Integrate Real APIs** (Future Enhancement)
   - 국토교통부 공시지가 API
   - 국토정보플랫폼 용도지역 API
   - 부동산거래관리시스템 거래사례 API

4. **Deploy v3.4** (30 min)
   - Commit all changes
   - Push to repository
   - Update documentation

---

## 📊 Expected Results

### Before (v3.3)
```
User visits landing page
    ↓
Sees report cards
    ↓
Must manually prepare appraisal_context
    ↓
Clicks "API로 생성하기" with mock data
    ↓
Gets demo report
```

### After (v3.4)
```
User visits landing page
    ↓
Enters land address: "서울특별시 강남구 테헤란로 123"
    ↓
Clicks "자동조회 실행"
    ↓
Sees complete land information (면적, 공시지가, 용도지역, 거리사례)
    ↓
[Optional] Adjusts Premium scores manually
    ↓
Selects reports: ☑ Pre-Report ☑ Comprehensive ☐ Investor
    ↓
Clicks "선택한 보고서 생성하기"
    ↓
Downloads 2 PDF reports with real calculated data
```

---

## 🎯 Success Metrics

- ✅ Users can input addresses and see immediate lookup results
- ✅ Complete workflow from input to PDF download works end-to-end
- ✅ Premium manual override functionality operational
- ✅ Multi-report bulk generation working
- ✅ Mobile-responsive UI maintained
- ✅ All existing v3.3 features still functional

---

**Status**: Backend API Complete | Frontend Implementation Ready to Start  
**ETA**: 3-4 hours for complete v3.4 implementation  
**Priority**: High (Core UX improvement)  

🎉 **This upgrade transforms ZeroSite from a demo platform to a production-ready land appraisal system!**
