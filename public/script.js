/**
 * ZeroSite v24.1 Entry OS Screen - JavaScript Logic
 * CTA Button API Integration & Navigation
 */

// ============================================================================
// CONFIGURATION
// ============================================================================
const API_BASE_URL = '/api/v24.1';
const DASHBOARD_URL = '/public/dashboard.html';

// Navigation mappings
const NAVIGATION_MAP = {
    'diagnose': {
        title: '토지 진단',
        endpoint: `${API_BASE_URL}/diagnose-land`,
        method: 'POST',
        redirectUrl: `${DASHBOARD_URL}?tab=diagnose`
    },
    'capacity': {
        title: '건축 규모 검토',
        endpoint: `${API_BASE_URL}/capacity`,
        method: 'POST',
        redirectUrl: `${DASHBOARD_URL}?tab=capacity`
    },
    'appraisal': {
        title: '토지 감정평가',
        endpoint: `${API_BASE_URL}/diagnose-land`,
        method: 'POST',
        redirectUrl: `${DASHBOARD_URL}?tab=appraisal`
    },
    'scenario': {
        title: '시나리오 A/B/C 비교',
        endpoint: `${API_BASE_URL}/scenario/compare`,
        method: 'POST',
        redirectUrl: `${DASHBOARD_URL}?tab=scenario`
    },
    'multi-parcel': {
        title: 'Multi-Parcel 합필 분석',
        endpoint: `${API_BASE_URL}/multi-parcel`,
        method: 'POST',
        redirectUrl: `${DASHBOARD_URL}?tab=multi-parcel`
    },
    'reports': {
        title: '보고서 5종 생성',
        endpoint: `${API_BASE_URL}/report/generate`,
        method: 'POST',
        redirectUrl: `${DASHBOARD_URL}?tab=reports`
    }
};

// ============================================================================
// CORE NAVIGATION FUNCTIONS
// ============================================================================

/**
 * Navigate to specific feature
 * @param {string} feature - Feature identifier (diagnose, capacity, appraisal, etc.)
 */
function navigateTo(feature) {
    const config = NAVIGATION_MAP[feature];
    
    if (!config) {
        console.error(`Unknown feature: ${feature}`);
        showNotification('오류: 알 수 없는 기능입니다.', 'error');
        return;
    }
    
    console.log(`Navigating to: ${config.title}`);
    
    // Show loading indicator
    showLoadingModal(config.title);
    
    // For now, directly redirect to dashboard with feature tab
    // In production, you might want to validate user session or fetch initial data
    setTimeout(() => {
        window.location.href = config.redirectUrl;
    }, 800);
}

/**
 * Execute API call for specific feature
 * @param {string} feature - Feature identifier
 * @param {object} data - Request payload
 */
async function executeAPI(feature, data = {}) {
    const config = NAVIGATION_MAP[feature];
    
    if (!config) {
        throw new Error(`Unknown feature: ${feature}`);
    }
    
    try {
        const response = await fetch(config.endpoint, {
            method: config.method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `API Error: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error(`API call failed for ${feature}:`, error);
        throw error;
    }
}

/**
 * Check API health and availability
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ API Health Check:', data);
            return true;
        } else {
            console.warn('⚠️ API Health Check Failed:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ API Health Check Error:', error);
        return false;
    }
}

// ============================================================================
// UI HELPERS
// ============================================================================

/**
 * Show loading modal with message
 * @param {string} title - Loading title
 */
function showLoadingModal(title) {
    const existingModal = document.getElementById('loading-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.id = 'loading-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    
    modal.innerHTML = `
        <div style="
            background: white;
            padding: 3rem;
            border-radius: 1rem;
            text-align: center;
            max-width: 400px;
            animation: slideUp 0.3s ease;
        ">
            <div style="
                width: 60px;
                height: 60px;
                border: 4px solid #005BAC;
                border-top-color: transparent;
                border-radius: 50%;
                margin: 0 auto 1.5rem;
                animation: spin 1s linear infinite;
            "></div>
            <h3 style="
                font-size: 1.5rem;
                font-weight: 700;
                color: #111827;
                margin-bottom: 0.5rem;
            ">${title}</h3>
            <p style="
                color: #6B7280;
                font-size: 1rem;
            ">잠시만 기다려주세요...</p>
        </div>
    `;
    
    // Add animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes slideUp {
            from { transform: translateY(30px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(modal);
}

/**
 * Hide loading modal
 */
function hideLoadingModal() {
    const modal = document.getElementById('loading-modal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    }
}

/**
 * Show notification message
 * @param {string} message - Notification message
 * @param {string} type - Notification type (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
    const colors = {
        success: '#23A860',
        error: '#DD3333',
        info: '#005BAC',
        warning: '#FF7A00'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: ${colors[type]};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        z-index: 10001;
        font-weight: 600;
        animation: slideInRight 0.3s ease;
        max-width: 400px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ============================================================================
// FEATURE-SPECIFIC FUNCTIONS
// ============================================================================

/**
 * Start land diagnosis with sample data
 */
async function startLandDiagnosis() {
    const sampleData = {
        address: "서울시 마포구 공덕동 123-4",
        land_area: 1500.0,
        appraisal_price: 5000000,
        zone_type: "제3종일반주거지역",
        legal_far: 200.0,
        legal_bcr: 60.0,
        final_far: 240.0,
        height_limit: 60.0
    };
    
    try {
        const result = await executeAPI('diagnose', sampleData);
        console.log('Land Diagnosis Result:', result);
        showNotification('토지 진단이 완료되었습니다.', 'success');
        return result;
    } catch (error) {
        showNotification('토지 진단 중 오류가 발생했습니다.', 'error');
        throw error;
    }
}

/**
 * Start capacity analysis with sample data
 */
async function startCapacityAnalysis() {
    const sampleData = {
        land_area: 1500.0,
        bcr_limit: 60.0,
        far_limit: 240.0,
        max_floors: 15
    };
    
    try {
        const result = await executeAPI('capacity', sampleData);
        console.log('Capacity Analysis Result:', result);
        showNotification('규모 검토가 완료되었습니다.', 'success');
        return result;
    } catch (error) {
        showNotification('규모 검토 중 오류가 발생했습니다.', 'error');
        throw error;
    }
}

// ============================================================================
// SCROLL ANIMATIONS
// ============================================================================

/**
 * Initialize scroll-based animations
 */
function initScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        }
    );
    
    // Observe all feature cards
    document.querySelectorAll('.feature-card').forEach((card) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
    
    // Observe process steps
    document.querySelectorAll('.process-step').forEach((step) => {
        step.style.opacity = '0';
        step.style.transform = 'translateY(30px)';
        step.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(step);
    });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Format number with thousand separators
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Format currency (KRW)
 * @param {number} amount - Amount in KRW
 * @returns {string} Formatted currency
 */
function formatCurrency(amount) {
    if (amount >= 100000000) {
        return `${(amount / 100000000).toFixed(1)}억원`;
    } else if (amount >= 10000) {
        return `${(amount / 10000).toFixed(1)}만원`;
    } else {
        return `${formatNumber(amount)}원`;
    }
}

/**
 * Format area (sqm)
 * @param {number} area - Area in square meters
 * @returns {string} Formatted area
 */
function formatArea(area) {
    return `${formatNumber(Math.round(area))}㎡`;
}

/**
 * Format percentage
 * @param {number} value - Percentage value
 * @returns {string} Formatted percentage
 */
function formatPercentage(value) {
    return `${value.toFixed(1)}%`;
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

/**
 * Initialize keyboard shortcuts
 */
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Alt + 1: Land Diagnosis
        if (e.altKey && e.key === '1') {
            e.preventDefault();
            navigateTo('diagnose');
        }
        // Alt + 2: Capacity Analysis
        else if (e.altKey && e.key === '2') {
            e.preventDefault();
            navigateTo('capacity');
        }
        // Alt + 3: Appraisal
        else if (e.altKey && e.key === '3') {
            e.preventDefault();
            navigateTo('appraisal');
        }
        // Alt + 4: Scenario
        else if (e.altKey && e.key === '4') {
            e.preventDefault();
            navigateTo('scenario');
        }
        // Alt + 5: Multi-Parcel
        else if (e.altKey && e.key === '5') {
            e.preventDefault();
            navigateTo('multi-parcel');
        }
        // Alt + 6: Reports
        else if (e.altKey && e.key === '6') {
            e.preventDefault();
            navigateTo('reports');
        }
    });
}

// ============================================================================
// ANALYTICS & TRACKING
// ============================================================================

/**
 * Track user interaction
 * @param {string} action - Action name
 * @param {object} data - Additional data
 */
function trackEvent(action, data = {}) {
    console.log('📊 Event Tracked:', action, data);
    
    // In production, send to analytics service
    // Example: Google Analytics, Mixpanel, etc.
    if (window.gtag) {
        window.gtag('event', action, data);
    }
}

/**
 * Track page view
 * @param {string} page - Page identifier
 */
function trackPageView(page) {
    console.log('📄 Page View:', page);
    
    if (window.gtag) {
        window.gtag('config', 'GA_MEASUREMENT_ID', {
            page_path: page
        });
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize application on DOM ready
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 ZeroSite v24.1 Entry OS Initialized');
    
    // Check API health
    const apiHealthy = await checkAPIHealth();
    if (!apiHealthy) {
        console.warn('⚠️ API is not responding. Some features may not work.');
    }
    
    // Initialize scroll animations
    initScrollAnimations();
    
    // Initialize keyboard shortcuts
    initKeyboardShortcuts();
    
    // Track page view
    trackPageView('/');
    
    // Log keyboard shortcuts help
    console.log(`
╔═══════════════════════════════════════╗
║   ZeroSite v24.1 Keyboard Shortcuts   ║
╠═══════════════════════════════════════╣
║   Alt + 1  →  토지 진단                ║
║   Alt + 2  →  규모 검토                ║
║   Alt + 3  →  감정평가                 ║
║   Alt + 4  →  시나리오 비교            ║
║   Alt + 5  →  Multi-Parcel 분석       ║
║   Alt + 6  →  보고서 생성              ║
╚═══════════════════════════════════════╝
    `);
    
    // Add smooth scroll behavior for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    console.log('✅ All systems ready');
});

// ============================================================================
// GLOBAL EXPORTS
// ============================================================================

// Export functions for global access
window.ZeroSite = {
    navigateTo,
    executeAPI,
    checkAPIHealth,
    showNotification,
    startLandDiagnosis,
    startCapacityAnalysis,
    formatNumber,
    formatCurrency,
    formatArea,
    formatPercentage,
    trackEvent,
    trackPageView
};

console.log('💡 ZeroSite v24.1 Entry OS Script Loaded');
