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
        
        // 필수 필드 검증 (critical fields)
        const basicInfo = data.land_data.basic_info;
        const missingFields = [];
        
        if (!basicInfo.land_area_sqm || basicInfo.land_area_sqm === 0) missingFields.push('면적');
        if (!basicInfo.land_category) missingFields.push('지목');
        if (!basicInfo.land_use_zone) missingFields.push('용도지역');
        
        if (missingFields.length > 0) {
            console.warn('⚠️ 누락된 필수 필드:', missingFields.join(', '));
            console.warn('⚠️ 서버 응답 스키마:', data);
        }
        
        // ⚠️ Check for warnings (Mock data usage)
        if (data.warning) {
            const useAnyway = confirm(
                `${data.warning}\n\n` +
                `API 키 상태:\n` +
                `- 카카오: ${data.api_key_status?.kakao || '미확인'}\n` +
                `- 공공데이터: ${data.api_key_status?.data_go_kr || '미확인'}\n` +
                `- VWorld: ${data.api_key_status?.vworld || '미확인'}\n\n` +
                `계속하시겠습니까? (Mock 데이터로 진행)`
            );

            if (!useAnyway) {
                // Reset button
                btn.disabled = false;
                btn.innerHTML = originalHTML;
                return;
            }
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
 * Now displays detailed land data using the new HTML structure
 */
function displayLookupResult(data) {
    console.log('📊 Displaying land data:', data);
    
    // The new structure is already in HTML, just populate the fields
    displayLandData(data);
    
    // Show the lookup result section
    const resultDiv = document.getElementById('lookup-result');
    resultDiv.style.display = 'block';
}

/**
 * Helper function to set field value safely
 */
function setFieldValue(id, value, defaultValue = '-') {
    const element = document.getElementById(id);
    if (element) {
        element.value = value || defaultValue;
    }
}

/**
 * Display land data in the detailed view (v3.4 NEW)
 */
function displayLandData(data) {
    console.log('🏗️ Populating land data fields:', data);
    
    // Check if we have the nested structure from API or the flat lookupData format
    const landData = data.land_data || data;
    const basicInfo = landData.basic_info || landData;
    const priceInfo = landData.price_info || landData;
    const regulationInfo = landData.regulation_info || landData;
    const transactions = landData.transactions || data.samples || [];
    const buildingInfo = landData.building_info;
    
    // Basic Information
    setFieldValue('display-address', basicInfo.address || data.address);
    setFieldValue('display-pnu', basicInfo.pnu_code || basicInfo.pnu || data.parcel_id);
    setFieldValue('display-area', `${(basicInfo.land_area_sqm || data.land_area_sqm || 0).toLocaleString()} ㎡`);
    setFieldValue('display-area-pyeong', `${(basicInfo.land_area_pyeong || data.land_area_pyeong || 0).toFixed(1)} 평`);
    setFieldValue('display-land-category', basicInfo.land_category || '미확인');
    setFieldValue('display-land-use-zone', basicInfo.land_use_zone || regulationInfo.land_use_zone || data.zoning_type || '미확인');
    setFieldValue('display-land-use-situation', basicInfo.land_use_situation || '미확인');
    setFieldValue('display-ownership-type', basicInfo.ownership_type || '미확인');
    
    // Critical missing fields (변동일자, 도로접면, 지형높이, 지형형상)
    setFieldValue('display-change-date', basicInfo.change_date || '미확인');
    setFieldValue('display-road-side', basicInfo.road_side || '미확인');
    setFieldValue('display-terrain-height', basicInfo.terrain_height || '미확인');
    setFieldValue('display-terrain-shape', basicInfo.terrain_shape || '미확인');
    
    // Price Information
    setFieldValue('display-official-price', `${(priceInfo.official_price_per_sqm || data.public_price_per_sqm || 0).toLocaleString()} 원/㎡`);
    setFieldValue('display-price-year', priceInfo.price_year || data.public_price_year || new Date().getFullYear());
    setFieldValue('display-total-price', `${((priceInfo.total_official_price || data.public_price_total || 0) / 100000000).toFixed(2)} 억원`);
    
    // Regulation Information
    setFieldValue('display-far', `${regulationInfo.floor_area_ratio || data.far || 0}%`);
    setFieldValue('display-bcr', `${regulationInfo.building_coverage_ratio || data.bcr || 0}%`);
    setFieldValue('display-max-height', regulationInfo.max_height_m ? `${regulationInfo.max_height_m} m` : '제한없음');
    
    // Regulations list
    const regulationsList = regulationInfo.regulations || [];
    const regulationsText = regulationsList.length > 0 
        ? regulationsList.join('\n') 
        : '특별한 규제사항 없음';
    setFieldValue('display-regulations', regulationsText);
    
    // Display transactions
    displayTransactions(transactions);
    
    // Building Information (if available)
    if (buildingInfo && buildingInfo.building_name) {
        document.getElementById('building-info-section').style.display = 'block';
        setFieldValue('display-building-name', buildingInfo.building_name);
        setFieldValue('display-building-purpose', buildingInfo.main_purpose_name || buildingInfo.main_purpose || '미확인');
        setFieldValue('display-building-area', `${(buildingInfo.total_floor_area_sqm || buildingInfo.total_floor_area || 0).toLocaleString()} ㎡`);
        setFieldValue('display-floor-count', `${buildingInfo.floor_count || 0} 층`);
    } else {
        document.getElementById('building-info-section').style.display = 'none';
    }
    
    // Data source indicator
    const dataSourceText = document.getElementById('data-source-text');
    if (dataSourceText) {
        const source = data.data_source || landData.data_source || 'api';
        if (source === 'mock') {
            dataSourceText.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <strong>경고:</strong> 테스트용 Mock 데이터 사용중 (실제 API 연결 실패)
                <br>
                <small style="margin-left: 1.5rem;">
                    실제 데이터를 조회하려면 .env 파일에 API 키를 설정해주세요.
                    <a href="https://github.com/hellodesignthinking-png/LHproject#-설치-및-실행" target="_blank">설정 가이드 →</a>
                </small>
            `;
            dataSourceText.style.color = '#ff9800';
            dataSourceText.style.backgroundColor = '#fff3e0';
            dataSourceText.style.padding = '1rem';
            dataSourceText.style.borderRadius = '8px';
            dataSourceText.style.border = '2px solid #ff9800';
        } else {
            dataSourceText.innerHTML = '<i class="fas fa-database"></i> 데이터 출처: 정부 공공데이터 API (실제 데이터)';
            dataSourceText.style.color = '#4caf50';
            dataSourceText.style.backgroundColor = '#e8f5e9';
            dataSourceText.style.padding = '0.5rem';
            dataSourceText.style.borderRadius = '4px';
            dataSourceText.style.border = '1px solid #4caf50';
        }
    }
}

/**
 * Display transactions in table (v3.4 NEW)
 */
function displayTransactions(transactions) {
    const tbody = document.getElementById('transactions-tbody');
    if (!tbody) return;
    
    if (!transactions || transactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--text-secondary); padding: 2rem;">
                    최근 1년간 실거래 내역이 없습니다
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = transactions.map(t => {
        const date = t.transaction_date || t.dealDate || '-';
        const amount = t.transaction_amount || t.dealAmount || 0;
        const area = t.land_area_sqm || t.area || 0;
        const pricePerSqm = t.price_per_sqm || (amount && area ? Math.round(amount / area) : 0);
        const category = t.land_category || t.landType || '-';
        
        return `
            <tr>
                <td>${date}</td>
                <td>${(amount / 10000).toLocaleString()}</td>
                <td>${area.toLocaleString()}</td>
                <td>${pricePerSqm.toLocaleString()}</td>
                <td>${category}</td>
            </tr>
        `;
    }).join('');
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
window.displayLandData = displayLandData;
window.setFieldValue = setFieldValue;
window.displayTransactions = displayTransactions;
window.togglePremiumOverride = togglePremiumOverride;
window.applyPremiumOverride = applyPremiumOverride;
window.generateSelectedReports = generateSelectedReports;
window.showGenerationModal = showGenerationModal;
window.updateModalProgress = updateModalProgress;
window.displayGenerationResults = displayGenerationResults;

console.log('ZeroSite OS v3.4 JavaScript loaded successfully');
