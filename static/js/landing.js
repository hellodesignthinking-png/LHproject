/**
 * ZeroSite OS v3.3 Landing Page JavaScript
 * Handles API interactions, status monitoring, and UI behaviors
 */

// Configuration
const API_BASE_URL = window.location.origin;
const HEALTH_CHECK_INTERVAL = 20000; // 20 seconds
let currentReportId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('ZeroSite OS v3.3 Landing Page Initialized');
    
    // Load initial system status
    loadSystemStatus();
    
    // Set up periodic status updates
    setInterval(loadSystemStatus, HEALTH_CHECK_INTERVAL);
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});

/**
 * Load and display system status from health check endpoint
 */
async function loadSystemStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v3/reports/health`);
        const data = await response.json();
        
        // Update status cards
        updateStatusCard('server-status', data.status, data.status === 'healthy' ? 'success' : 'error');
        updateStatusCard('version-status', data.version, 'info');
        updateStatusCard('pdf-status', data.pdf_generation || 'unknown', 'warning');
        
        // Count operational composers
        if (data.composers) {
            const operational = Object.values(data.composers).filter(s => s === 'operational').length;
            updateStatusCard('composers-status', `${operational}/6 Operational`, 'success');
        }
        
        // Update status icon
        const statusIcon = document.getElementById('status-icon');
        if (statusIcon) {
            if (data.status === 'healthy') {
                statusIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
                statusIcon.style.color = 'var(--success)';
            } else {
                statusIcon.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                statusIcon.style.color = 'var(--error)';
            }
        }
        
        // Update JSON display
        const jsonDisplay = document.getElementById('status-json');
        if (jsonDisplay) {
            jsonDisplay.textContent = JSON.stringify(data, null, 2);
        }
        
        // Update footer status
        const footerStatus = document.getElementById('footer-status');
        if (footerStatus) {
            footerStatus.textContent = `Status: ${data.status}`;
            footerStatus.style.color = data.status === 'healthy' ? 'var(--success)' : 'var(--error)';
        }
        
        const footerVersion = document.getElementById('footer-version');
        if (footerVersion) {
            footerVersion.textContent = `Version ${data.version}`;
        }
        
        console.log('System status updated:', data);
    } catch (error) {
        console.error('Failed to load system status:', error);
        updateStatusCard('server-status', 'Error', 'error');
    }
}

/**
 * Update a status card with new value
 */
function updateStatusCard(elementId, value, type) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = value;
        
        // Apply color based on type
        if (type === 'success') {
            element.style.color = 'var(--success)';
        } else if (type === 'error') {
            element.style.color = 'var(--error)';
        } else if (type === 'warning') {
            element.style.color = 'var(--warning)';
        } else {
            element.style.color = 'var(--text-primary)';
        }
    }
}

/**
 * Scroll to reports section
 */
function scrollToReports() {
    const reportsSection = document.getElementById('reports');
    if (reportsSection) {
        reportsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

/**
 * Scroll to input section (v3.4)
 */
function scrollToInput() {
    const inputSection = document.getElementById('input');
    if (inputSection) {
        inputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        // Focus on address input after scroll
        setTimeout(() => {
            const addressInput = document.getElementById('land-address');
            if (addressInput) {
                addressInput.focus();
            }
        }, 500);
    }
}

/**
 * Generate a report of specified type
 */
async function generateReport(reportType) {
    // Show modal
    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalResult = document.getElementById('modal-result');
    const modalError = document.getElementById('modal-error');
    
    if (!modal) return;
    
    // Reset modal state
    modal.style.display = 'block';
    modalTitle.textContent = 'Generating Report...';
    modalMessage.style.display = 'block';
    modalResult.style.display = 'none';
    modalError.style.display = 'none';
    document.querySelector('.loading-spinner').style.display = 'block';
    
    // Mock appraisal context for demo
    const mockContext = {
        appraisal_context: {
            calculation: {
                land_area_sqm: 660.0,
                land_area_pyeong: 199.6,
                final_appraised_total: 4154535000,
                final_appraised_per_sqm: 6300000,
                final_appraised_per_pyeong: 20820000,
                confidence_level: "MEDIUM"
            },
            zoning: {
                confirmed_type: "제2종일반주거지역",
                far: 250.0,
                bcr: 50.0,
                max_floors: 5,
                building_restrictions: []
            },
            confidence: {
                overall: "MEDIUM",
                calculation: "HIGH",
                zoning: "HIGH",
                market: "MEDIUM"
            },
            metadata: {
                appraisal_engine: "v8.7",
                appraisal_date: new Date().toISOString(),
                address: "서울특별시 강남구 테헤란로 123"
            },
            development: {
                buildable_area_sqm: 1650.0,
                estimated_units: 23,
                estimated_floors: 5
            },
            lh_analysis: {
                possibility: "HIGH",
                possibility_score: 85.0,
                pass_probability: 0.85,
                recommended_supply_type: "행복주택"
            },
            financial: {
                irr: 0.2744,
                roi: 0.2744,
                npv: 850000000
            },
            official_land_price: {
                standard_price_per_sqm: 4850000,
                reference_year: 2024,
                total_value: 3200000000
            }
        }
    };
    
    try {
        // Call API to generate report
        const response = await fetch(`${API_BASE_URL}/api/v3/reports/${reportType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(mockContext)
        });
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Hide loading
        document.querySelector('.loading-spinner').style.display = 'none';
        modalMessage.style.display = 'none';
        
        // Show success result
        modalTitle.textContent = 'Report Generated Successfully!';
        modalResult.style.display = 'block';
        
        // Fill in result details
        document.getElementById('result-id').textContent = result.report_id || 'N/A';
        document.getElementById('result-type').textContent = result.report_type || reportType;
        document.getElementById('result-time').textContent = 
            result.generation_time_ms ? `${result.generation_time_ms}ms` : 'N/A';
        
        // Store report ID for download
        currentReportId = result.report_id;
        
        console.log('Report generated:', result);
    } catch (error) {
        console.error('Failed to generate report:', error);
        
        // Hide loading
        document.querySelector('.loading-spinner').style.display = 'none';
        modalMessage.style.display = 'none';
        
        // Show error
        modalTitle.textContent = 'Generation Failed';
        modalError.style.display = 'block';
        document.getElementById('error-message').textContent = error.message;
    }
}

/**
 * Download generated report in specified format
 */
function downloadReport(format) {
    if (!currentReportId) {
        alert('No report ID available');
        return;
    }
    
    const url = `${API_BASE_URL}/api/v3/reports/${currentReportId}/${format}`;
    window.open(url, '_blank');
}

/**
 * Close the modal
 */
function closeModal() {
    const modal = document.getElementById('reportModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Copy code to clipboard
 */
function copyCode(codeId) {
    const codeElement = document.getElementById(codeId);
    if (!codeElement) return;
    
    const text = codeElement.textContent;
    
    // Use modern clipboard API
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showCopyFeedback(codeId);
        }).catch(err => {
            console.error('Failed to copy:', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

/**
 * Fallback copy method for older browsers
 */
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback();
    } catch (err) {
        console.error('Fallback: Could not copy text:', err);
    }
    
    document.body.removeChild(textArea);
}

/**
 * Show visual feedback when code is copied
 */
function showCopyFeedback(codeId) {
    // Find the copy button for this code block
    const codeElement = document.getElementById(codeId);
    if (!codeElement) return;
    
    const apiExample = codeElement.closest('.api-example');
    if (!apiExample) return;
    
    const copyBtn = apiExample.querySelector('.copy-btn');
    if (!copyBtn) return;
    
    // Change button text temporarily
    const originalHTML = copyBtn.innerHTML;
    copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
    copyBtn.style.color = 'var(--success)';
    copyBtn.style.borderColor = 'var(--success)';
    
    // Reset after 2 seconds
    setTimeout(() => {
        copyBtn.innerHTML = originalHTML;
        copyBtn.style.color = '';
        copyBtn.style.borderColor = '';
    }, 2000);
}

/**
 * Close modal when clicking outside of it
 */
window.onclick = function(event) {
    const modal = document.getElementById('reportModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Export functions for global access
window.loadSystemStatus = loadSystemStatus;
window.scrollToReports = scrollToReports;
window.scrollToInput = scrollToInput;
window.generateReport = generateReport;
window.downloadReport = downloadReport;
window.closeModal = closeModal;
window.copyCode = copyCode;

/* ============================================================================
   ZeroSite v3.4 - Land Input System Functions
   ============================================================================ */

// Global state for lookup data
let lookupData = null;
let premiumOverrideData = null;

/**
 * Lookup address and fetch appraisal data (v3.4)
 * Now uses the Real Land Data API (/api/v3/land/fetch)
 */
async function lookupAddress() {
    const addressInput = document.getElementById('land-address');
    const address = addressInput.value.trim();
    
    if (!address) {
        alert('주소를 입력해주세요');
        return;
    }
    
    try {
        // Get button element
        const buttons = document.querySelectorAll('.input-form button');
        const btn = buttons[0];
        
        // Show loading state
        btn.disabled = true;
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 실제 데이터 조회중...';
        
        // Call REAL Land Data API (v3.4)
        console.log('🚀 Calling REAL Land Data API for:', address);
        const response = await fetch(`${API_BASE_URL}/api/v3/land/fetch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ address: address })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `API Error: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Real Land Data Response:', data);
        
        // 데이터 검증
        if (!data.success) {
            throw new Error(data.error || '데이터 조회에 실패했습니다');
        }
        
        if (!data.land_data) {
            throw new Error('토지 데이터가 반환되지 않았습니다');
        }
        
        if (!data.appraisal_context) {
            console.warn('⚠️ appraisal_context가 없습니다. 기본값을 사용합니다.');
        }
        
        if (data.success && data.land_data) {
            // Store lookup data (convert to old format for compatibility)
            const landData = data.land_data;
            const appraisalData = data.appraisal_context;
            
            lookupData = {
                success: true,
                address: landData.basic_info.address,
                land_area_sqm: landData.basic_info.land_area_sqm,
                land_area_pyeong: landData.basic_info.land_area_pyeong,
                public_price_per_sqm: landData.price_info.official_price_per_sqm,
                public_price_total: landData.price_info.total_official_price,
                public_price_year: landData.price_info.price_year,
                zoning_type: landData.regulation_info.land_use_zone,
                far: landData.regulation_info.floor_area_ratio,
                bcr: landData.regulation_info.building_coverage_ratio,
                max_floors: 5, // Default value
                parcel_id: landData.basic_info.pnu_code,
                // Include appraisal context
                appraisal_context: appraisalData,
                // Include transaction samples if available
                samples: (landData.transactions || []).map(t => ({
                    distance_m: 250, // Default
                    price_per_sqm: Math.round(t.transaction_amount / t.land_area_sqm),
                    transaction_date: t.transaction_date
                })),
                // Premium data (default if not available)
                premium: {
                    road_score: 7,
                    topography_score: 7,
                    overall_premium: 30,
                    road_description: "도로 조건 양호",
                    topography_description: "지형 조건 평지",
                    premium_description: "일반적인 할증률 적용"
                }
            };
            
            premiumOverrideData = null; // Reset overrides
            
            // Display results
            displayLookupResult(lookupData);
            
            // Show premium override section
            document.getElementById('premium-override').style.display = 'block';
            
            // Show report selection
            document.getElementById('report-selection').style.display = 'block';
            document.getElementById('generate-section').style.display = 'block';
            
            // Scroll to results
            setTimeout(() => {
                document.getElementById('lookup-result').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
            }, 100);
        } else {
            alert('조회 실패: ' + (data.error || '알 수 없는 오류'));
        }
        
        // Reset button
        btn.disabled = false;
        btn.innerHTML = originalHTML;
        
    } catch (error) {
        console.error('❌ Land Data API failed:', error);
        
        // 에러 유형별 메시지
        let errorMessage = '조회 중 오류가 발생했습니다';
        
        if (error.message.includes('fetch') || error.message.includes('network')) {
            errorMessage = '서버에 연결할 수 없습니다. 네트워크를 확인해주세요.';
        } else if (error.message.includes('주소')) {
            errorMessage = '정확한 지번 주소를 입력해주세요. (예: 서울특별시 강남구 역삼동 858)';
        } else if (error.message.includes('API')) {
            errorMessage = 'API 호출에 실패했습니다. 잠시 후 다시 시도해주세요.';
        } else {
            errorMessage = error.message;
        }
        
        alert('❌ ' + errorMessage);
        
        // Reset button
        const buttons = document.querySelectorAll('.input-form button');
        const btn = buttons[0];
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-search"></i> 자동조회 실행';
    }
}

/**
 * Display lookup result in preview card (v3.4)
 */
function displayLookupResult(data) {
    const resultDiv = document.getElementById('lookup-result');
    
    // Calculate average sample price
    let avgSamplePrice = 0;
    if (data.samples && data.samples.length > 0) {
        const sum = data.samples.reduce((acc, s) => acc + s.price_per_sqm, 0);
        avgSamplePrice = Math.round(sum / data.samples.length);
    }
    
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
                <div class="result-value">${data.land_area_sqm?.toLocaleString()} ㎡ <span style="font-size: 0.8rem; color: var(--text-secondary);">(${data.land_area_pyeong?.toFixed(1)}평)</span></div>
            </div>
            <div class="result-item">
                <div class="result-label">공시지가 (㎡)</div>
                <div class="result-value">${data.public_price_per_sqm?.toLocaleString()}원</div>
            </div>
            <div class="result-item">
                <div class="result-label">공시지가 (총액)</div>
                <div class="result-value" style="font-size: 1rem;">${(data.public_price_total / 100000000)?.toFixed(2)}억원</div>
            </div>
            <div class="result-item">
                <div class="result-label">용도지역</div>
                <div class="result-value" style="font-size: 0.9rem;">${data.zoning_type}</div>
            </div>
            <div class="result-item">
                <div class="result-label">용적률 / 건폐율</div>
                <div class="result-value">${data.far}% / ${data.bcr}%</div>
            </div>
        </div>
        
        ${data.samples && data.samples.length > 0 ? `
        <div style="margin-top: 2rem;">
            <h4 style="margin-bottom: 1rem; color: var(--text-primary);">
                <i class="fas fa-map-marker-alt"></i> 거리사례 (${data.samples.length}건)
            </h4>
            <div class="result-grid">
                ${data.samples.map((sample, idx) => `
                    <div class="result-item">
                        <div class="result-label">사례 ${idx + 1} (${sample.distance_m}m)</div>
                        <div class="result-value" style="font-size: 1rem;">
                            ${(sample.price_per_sqm / 10000)?.toLocaleString()}만원/㎡
                        </div>
                        <div class="result-label" style="margin-top: 0.25rem;">
                            ${sample.transaction_date}
                        </div>
                    </div>
                `).join('')}
                <div class="result-item" style="border-left: 2px solid var(--accent-mint); padding-left: 1rem;">
                    <div class="result-label">평균 거래가</div>
                    <div class="result-value" style="color: var(--accent-mint);">
                        ${(avgSamplePrice / 10000)?.toLocaleString()}만원/㎡
                    </div>
                </div>
            </div>
        </div>
        ` : ''}
        
        ${data.premium ? `
        <div style="margin-top: 2rem; padding: 1.5rem; background: rgba(35, 230, 166, 0.1); border-radius: 0.75rem; border: 1px solid var(--accent-mint);">
            <h4 style="margin-bottom: 1rem; color: var(--accent-mint); display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-star"></i> Premium 분석
            </h4>
            <div class="result-grid">
                <div class="result-item">
                    <div class="result-label">도로 점수</div>
                    <div class="result-value">${data.premium.road_score}/10</div>
                    <div class="result-label" style="margin-top: 0.25rem;">${data.premium.road_description}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">지형 점수</div>
                    <div class="result-value">${data.premium.topography_score}/10</div>
                    <div class="result-label" style="margin-top: 0.25rem;">${data.premium.topography_description}</div>
                </div>
                <div class="result-item">
                    <div class="result-label">전체 할증률</div>
                    <div class="result-value" style="color: var(--accent-mint);">+${data.premium.overall_premium}%</div>
                    <div class="result-label" style="margin-top: 0.25rem;">${data.premium.premium_description}</div>
                </div>
            </div>
        </div>
        ` : ''}
    `;
    
    resultDiv.style.display = 'block';
}

/**
 * Toggle premium override panel (v3.4)
 */
function togglePremiumOverride() {
    const content = document.getElementById('override-content');
    const icon = document.querySelector('.toggle-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        icon.classList.add('open');
    } else {
        content.style.display = 'none';
        icon.classList.remove('open');
    }
}

/**
 * Apply premium override values (v3.4)
 */
function applyPremiumOverride() {
    const roadScore = document.getElementById('road-score').value;
    const topoScore = document.getElementById('topo-score').value;
    const overallPremium = document.getElementById('overall-premium').value;
    
    premiumOverrideData = {
        road_score: roadScore ? parseFloat(roadScore) : null,
        topography_score: topoScore ? parseFloat(topoScore) : null,
        overall_premium: overallPremium ? parseFloat(overallPremium) : null
    };
    
    console.log('Premium override applied:', premiumOverrideData);
    
    // Visual feedback
    alert('Premium 값이 적용되었습니다. 이제 보고서를 생성하면 수정된 값으로 계산됩니다.');
    
    // Close the panel
    togglePremiumOverride();
}

/**
 * Generate selected reports (v3.4)
 * Now uses REAL appraisal_context from land data API
 */
async function generateSelectedReports() {
    if (!lookupData) {
        alert('먼저 토지 조회를 실행해주세요');
        return;
    }
    
    // Get selected reports
    const selectedReports = [];
    const reportMapping = {
        'select-pre-report': 'pre-report',
        'select-comprehensive': 'comprehensive',
        'select-lh-decision': 'lh-decision',
        'select-investor': 'investor',
        'select-land-price': 'land-price',
        'select-internal': 'internal'
    };
    
    for (const [checkboxId, reportType] of Object.entries(reportMapping)) {
        if (document.getElementById(checkboxId)?.checked) {
            selectedReports.push(reportType);
        }
    }
    
    if (selectedReports.length === 0) {
        alert('최소 1개 이상의 보고서를 선택해주세요');
        return;
    }
    
    console.log('🎯 Generating reports:', selectedReports);
    
    // Use REAL appraisal context from land data API
    // The /api/v3/land/fetch already returns a complete appraisal_context
    let appraisalContext = lookupData.appraisal_context;
    
    // Apply premium overrides if provided
    if (premiumOverrideData && appraisalContext) {
        const premium = premiumOverrideData.overall_premium || 30;
        const premiumMultiplier = 1 + (premium / 100);
        
        // Update calculation with overrides
        const basePrice = lookupData.public_price_total / (1 + (lookupData.premium?.overall_premium || 30) / 100);
        appraisalContext.calculation.final_appraised_total = Math.round(basePrice * premiumMultiplier);
        appraisalContext.calculation.final_appraised_per_sqm = Math.round(basePrice * premiumMultiplier / lookupData.land_area_sqm);
        appraisalContext.calculation.final_appraised_per_pyeong = Math.round(appraisalContext.calculation.final_appraised_per_sqm * 3.3058);
        
        console.log('✨ Applied premium overrides:', premiumOverrideData);
    }
    
    console.log('📋 Using REAL appraisal context from API:', appraisalContext);
    
    // Show generation modal
    showGenerationModal(selectedReports);
    
    // Generate reports sequentially
    const results = [];
    for (const reportType of selectedReports) {
        try {
            updateModalProgress(`Generating ${reportType}...`);
            
            const response = await fetch(`${API_BASE_URL}/api/v3/reports/${reportType}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ appraisal_context: appraisalContext })
            });
            
            const result = await response.json();
            console.log(`✅ ${reportType} result:`, result);
            
            results.push({ 
                type: reportType, 
                data: result, 
                success: response.ok 
            });
        } catch (error) {
            console.error(`❌ Failed to generate ${reportType}:`, error);
            results.push({ 
                type: reportType, 
                error: error.message, 
                success: false 
            });
        }
    }
    
    // Show results
    displayGenerationResults(results);
}

/**
 * Show generation modal (v3.4)
 */
function showGenerationModal(reportTypes) {
    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalResult = document.getElementById('modal-result');
    const modalError = document.getElementById('modal-error');
    
    if (!modal) {
        console.error('Modal not found');
        return;
    }
    
    // Reset modal state
    modal.style.display = 'block';
    modalTitle.textContent = `Generating ${reportTypes.length} Reports...`;
    modalMessage.style.display = 'block';
    modalMessage.textContent = 'Preparing...';
    modalResult.style.display = 'none';
    modalError.style.display = 'none';
    
    const spinner = modal.querySelector('.loading-spinner');
    if (spinner) spinner.style.display = 'block';
}

/**
 * Update modal progress message (v3.4)
 */
function updateModalProgress(message) {
    const modalMessage = document.getElementById('modal-message');
    if (modalMessage) {
        modalMessage.textContent = message;
    }
}

/**
 * Display generation results (v3.4)
 */
function displayGenerationResults(results) {
    const modal = document.getElementById('reportModal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalResult = document.getElementById('modal-result');
    const spinner = modal.querySelector('.loading-spinner');
    
    const successCount = results.filter(r => r.success).length;
    
    // Hide loading
    if (spinner) spinner.style.display = 'none';
    modalMessage.style.display = 'none';
    
    // Update title
    modalTitle.textContent = `Generation Complete: ${successCount}/${results.length} Successful`;
    
    // Show results
    modalResult.style.display = 'block';
    modalResult.innerHTML = `
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
                        ${r.success && r.data && r.data.report_id ? `
                            <div class="result-actions">
                                <button class="btn-small" onclick="window.open('${API_BASE_URL}/api/v3/reports/${r.data.report_id}/json', '_blank')">
                                    JSON
                                </button>
                                <button class="btn-small" onclick="window.open('${API_BASE_URL}/api/v3/reports/${r.data.report_id}/pdf', '_blank')">
                                    PDF
                                </button>
                            </div>
                        ` : r.success ? `
                            <span class="error-msg">No report ID</span>
                        ` : `
                            <span class="error-msg">${r.error || 'Unknown error'}</span>
                        `}
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Export v3.4 functions for global access
window.lookupAddress = lookupAddress;
window.displayLookupResult = displayLookupResult;
window.togglePremiumOverride = togglePremiumOverride;
window.applyPremiumOverride = applyPremiumOverride;
window.generateSelectedReports = generateSelectedReports;
window.showGenerationModal = showGenerationModal;
window.updateModalProgress = updateModalProgress;
window.displayGenerationResults = displayGenerationResults;

console.log('ZeroSite OS v3.4 JavaScript loaded successfully');
