// ZeroSite v7.0 - Configuration

const CONFIG = {
    // API Configuration
    API_BASE_URL: window.location.origin,
    API_ENDPOINTS: {
        ANALYZE_LAND: '/api/analyze-land',
        ANALYZE_MULTI: '/api/analyze-multi-parcel',
        GENERATE_REPORT: '/api/generate-report',
        DASHBOARD: '/api/dashboard-data',
        LH_NOTICES: '/api/lh-notices/list',
        HEALTH: '/health'
    },
    
    // Map Configuration
    MAP: {
        DEFAULT_CENTER: [37.5665, 126.9780], // Seoul
        DEFAULT_ZOOM: 13,
        MIN_ZOOM: 7,
        MAX_ZOOM: 19,
        TILE_LAYER: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        TILE_ATTRIBUTION: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    
    // POI Configuration (LH Standard-based)
    POI: {
        TYPES: {
            SCHOOL: {
                icon: 'fa-school',
                color: '#4CAF50',
                label: '학교',
                maxDistance: 1000,
                // LH Standard: <300m (Excellent), 300-600m (Good), 600-1000m (Fair), >1000m (Poor)
                thresholds: {
                    excellent: 300,  // < 300m
                    good: 600,       // 300-600m
                    fair: 1000       // 600-1000m
                    // > 1000m = poor
                }
            },
            HOSPITAL: {
                icon: 'fa-hospital',
                color: '#F44336',
                label: '병원',
                maxDistance: 2000,
                // LH Standard: <500m (Excellent), 500-1000m (Good), 1000-1500m (Fair), >1500m (Poor)
                thresholds: {
                    excellent: 500,
                    good: 1000,
                    fair: 1500
                }
            },
            CONVENIENCE: {
                icon: 'fa-shopping-cart',
                color: '#FF9800',
                label: '편의시설',
                maxDistance: 800,
                // LH Standard: <200m (Excellent), 200-400m (Good), 400-600m (Fair), >600m (Poor)
                thresholds: {
                    excellent: 200,
                    good: 400,
                    fair: 600
                }
            },
            SUBWAY: {
                icon: 'fa-subway',
                color: '#2196F3',
                label: '지하철',
                maxDistance: 1200,
                // LH Standard: <500m (Excellent), 500-800m (Good), 800-1200m (Fair), >1200m (Poor)
                thresholds: {
                    excellent: 500,
                    good: 800,
                    fair: 1200
                }
            }
        },
        // Global distance classification
        DISTANCE_THRESHOLDS: {
            CLOSE: 300,
            MEDIUM: 800,
            FAR: 1500
        }
    },
    
    // GeoOptimizer Configuration
    GEO_OPTIMIZER: {
        RECOMMENDATION_COUNT: 3,
        SEARCH_RADIUS: 5000, // meters
        MIN_SCORE: 60,
        WEIGHTS: {
            LOCATION: 0.3,
            DEMOGRAPHICS: 0.25,
            INFRASTRUCTURE: 0.25,
            PRICE: 0.2
        }
    },
    
    // Multi-Parcel Configuration
    MULTI_PARCEL: {
        MAX_PARCELS: 10,
        CLUSTER_RADIUS: 80,
        MIN_CLUSTER_SIZE: 2
    },
    
    // UI Configuration
    UI: {
        ANIMATION_DURATION: 250,
        DEBOUNCE_DELAY: 300,
        TOAST_DURATION: 3000,
        SIDEBAR_WIDTH: 380,
        INFO_PANEL_WIDTH: 400
    },
    
    // Analysis Configuration
    ANALYSIS: {
        DEFAULT_AREA: 1000,
        DEFAULT_UNIT_TYPE: '신축매입임대',
        UNIT_TYPES: [
            '매입임대',
            '전세임대',
            '신축매입임대'
        ],
        SCORE_GRADES: {
            A: { min: 85, color: '#22c55e', label: 'A (우수)' },
            B: { min: 70, color: '#3b82f6', label: 'B (양호)' },
            C: { min: 55, color: '#f59e0b', label: 'C (보통)' },
            D: { min: 0, color: '#ef4444', label: 'D (미흡)' }
        }
    },
    
    // Report Configuration
    REPORT: {
        FORMATS: ['PDF', 'HTML', 'JSON'],
        DEFAULT_FORMAT: 'PDF',
        PAGE_SIZE: 'A4',
        ORIENTATION: 'portrait'
    },
    
    // Error Messages
    ERRORS: {
        NETWORK_ERROR: '네트워크 연결에 실패했습니다.',
        SERVER_ERROR: '서버 오류가 발생했습니다.',
        VALIDATION_ERROR: '입력값을 확인해주세요.',
        NO_RESULTS: '분석 결과가 없습니다.',
        ADDRESS_NOT_FOUND: '주소를 찾을 수 없습니다.',
        ANALYSIS_FAILED: '분석에 실패했습니다.'
    },
    
    // Success Messages
    SUCCESS: {
        ANALYSIS_COMPLETE: '분석이 완료되었습니다.',
        REPORT_GENERATED: '보고서가 생성되었습니다.',
        DATA_SAVED: '데이터가 저장되었습니다.'
    }
};

// Utility Functions
const Utils = {
    // Format number with commas
    formatNumber(num) {
        if (num === null || num === undefined) return '-';
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },
    
    // Format distance
    formatDistance(meters) {
        if (meters === null || meters === undefined) return '-';
        if (meters < 1000) {
            return `${Math.round(meters)}m`;
        } else {
            return `${(meters / 1000).toFixed(1)}km`;
        }
    },
    
    // Get distance class (generic)
    getDistanceClass(meters) {
        const { CLOSE, MEDIUM } = CONFIG.POI.DISTANCE_THRESHOLDS;
        if (meters <= CLOSE) return 'close';
        if (meters <= MEDIUM) return 'medium';
        return 'far';
    },
    
    // Get POI-specific distance class (LH Standard-based)
    getPOIDistanceClass(poiType, meters) {
        const type = CONFIG.POI.TYPES[poiType];
        if (!type || !type.thresholds) {
            return this.getDistanceClass(meters);
        }
        
        const { excellent, good, fair } = type.thresholds;
        if (meters <= excellent) return 'excellent';
        if (meters <= good) return 'good';
        if (meters <= fair) return 'fair';
        return 'poor';
    },
    
    // Get POI distance color
    getPOIDistanceColor(poiType, meters) {
        const distClass = this.getPOIDistanceClass(poiType, meters);
        const colors = {
            'excellent': '#22c55e',  // Green
            'good': '#3b82f6',       // Blue
            'fair': '#f59e0b',       // Orange
            'poor': '#ef4444'        // Red
        };
        return colors[distClass] || '#94a3b8';
    },
    
    // Get POI distance label
    getPOIDistanceLabel(poiType, meters) {
        const distClass = this.getPOIDistanceClass(poiType, meters);
        const labels = {
            'excellent': '매우 가까움',
            'good': '가까움',
            'fair': '보통',
            'poor': '멀음'
        };
        return labels[distClass] || '알 수 없음';
    },
    
    // Get score grade
    getScoreGrade(score) {
        const grades = CONFIG.ANALYSIS.SCORE_GRADES;
        if (score >= grades.A.min) return 'A';
        if (score >= grades.B.min) return 'B';
        if (score >= grades.C.min) return 'C';
        return 'D';
    },
    
    // Get grade color
    getGradeColor(grade) {
        const gradeInfo = CONFIG.ANALYSIS.SCORE_GRADES[grade];
        return gradeInfo ? gradeInfo.color : '#94a3b8';
    },
    
    // Debounce function
    debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    },
    
    // Show toast notification
    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add to body
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after duration
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, CONFIG.UI.TOAST_DURATION);
    },
    
    // Show loading
    showLoading(show = true) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    },
    
    // Validate address input
    validateAddress(address) {
        if (!address || address.trim().length === 0) {
            return { valid: false, error: '주소를 입력해주세요.' };
        }
        if (address.length < 5) {
            return { valid: false, error: '주소가 너무 짧습니다.' };
        }
        return { valid: true };
    },
    
    // Validate area input
    validateArea(area) {
        const numArea = parseFloat(area);
        if (isNaN(numArea) || numArea <= 0) {
            return { valid: false, error: '유효한 면적을 입력해주세요.' };
        }
        if (numArea < 100 || numArea > 10000) {
            return { valid: false, error: '면적은 100㎡ ~ 10,000㎡ 사이여야 합니다.' };
        }
        return { valid: true };
    },
    
    // Calculate distance between two coordinates
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371e3; // Earth radius in meters
        const φ1 = lat1 * Math.PI / 180;
        const φ2 = lat2 * Math.PI / 180;
        const Δφ = (lat2 - lat1) * Math.PI / 180;
        const Δλ = (lon2 - lon1) * Math.PI / 180;
        
        const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                  Math.cos(φ1) * Math.cos(φ2) *
                  Math.sin(Δλ/2) * Math.sin(Δλ/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        
        return R * c;
    }
};

// Export configuration
window.CONFIG = CONFIG;
window.Utils = Utils;

console.log('ZeroSite v7.0 - Configuration loaded');
