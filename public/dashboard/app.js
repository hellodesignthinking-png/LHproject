/**
 * ZeroSite v24 Dashboard UI 1.0
 * Interactive Dashboard with Advanced Features
 * 
 * Features:
 * 1. Analysis History Management
 * 2. Auto-complete for Address/Location
 * 3. Inline PDF Viewer
 * 4. Auto-refresh for Long-running Analysis
 * 5. Multi-step Wizard for Complex Input
 * 6. User-friendly Error Messages
 */

// ==========================================
// 1. ANALYSIS HISTORY MANAGER
// ==========================================

class AnalysisHistory {
    constructor() {
        this.storageKey = 'zerosite_analysis_history';
        this.maxHistorySize = 50;
    }

    /**
     * 분석 기록 추가
     */
    addHistory(analysisData) {
        const history = this.getHistory();
        const record = {
            id: this.generateId(),
            timestamp: new Date().toISOString(),
            ...analysisData
        };
        
        history.unshift(record);
        
        // 최대 크기 제한
        if (history.length > this.maxHistorySize) {
            history.pop();
        }
        
        localStorage.setItem(this.storageKey, JSON.stringify(history));
        this.renderHistory();
        
        return record;
    }

    /**
     * 전체 기록 조회
     */
    getHistory() {
        const data = localStorage.getItem(this.storageKey);
        return data ? JSON.parse(data) : [];
    }

    /**
     * 기록 삭제
     */
    deleteHistory(id) {
        const history = this.getHistory();
        const filtered = history.filter(item => item.id !== id);
        localStorage.setItem(this.storageKey, JSON.stringify(filtered));
        this.renderHistory();
    }

    /**
     * 전체 기록 삭제
     */
    clearHistory() {
        if (confirm('모든 분석 기록을 삭제하시겠습니까?')) {
            localStorage.removeItem(this.storageKey);
            this.renderHistory();
        }
    }

    /**
     * ID 생성
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * 기록 렌더링
     */
    renderHistory() {
        const container = document.getElementById('historyContainer');
        if (!container) return;

        const history = this.getHistory();
        
        if (history.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <p>분석 기록이 없습니다</p>
                </div>
            `;
            return;
        }

        container.innerHTML = history.map(item => `
            <div class="bg-white p-4 rounded-lg shadow hover:shadow-md transition border-l-4 border-blue-500">
                <div class="flex justify-between items-start">
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-2">
                            <span class="text-sm font-bold text-blue-600">${item.location || '위치 정보 없음'}</span>
                            <span class="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">${item.type || 'Quick Analysis'}</span>
                        </div>
                        <div class="text-xs text-gray-500 space-y-1">
                            <div>📅 ${new Date(item.timestamp).toLocaleString('ko-KR')}</div>
                            ${item.landArea ? `<div>📏 토지면적: ${item.landArea.toLocaleString()}㎡</div>` : ''}
                            ${item.reportFile ? `<div class="mt-2"><a href="${item.reportFile}" target="_blank" class="text-blue-600 hover:underline">📄 보고서 보기</a></div>` : ''}
                        </div>
                    </div>
                    <button onclick="historyManager.deleteHistory('${item.id}')" class="text-red-500 hover:text-red-700 ml-2">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `).join('');
    }
}

// ==========================================
// 2. AUTO-COMPLETE FOR ADDRESS
// ==========================================

class AddressAutoComplete {
    constructor(inputId, suggestionsId) {
        this.input = document.getElementById(inputId);
        this.suggestionsContainer = document.getElementById(suggestionsId);
        this.debounceTimer = null;
        this.currentFocus = -1;
        
        if (this.input && this.suggestionsContainer) {
            this.init();
        }
    }

    init() {
        // 입력 이벤트
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.search(e.target.value);
            }, 300);
        });

        // 키보드 네비게이션
        this.input.addEventListener('keydown', (e) => {
            const suggestions = this.suggestionsContainer.getElementsByTagName('div');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.currentFocus++;
                this.addActive(suggestions);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.currentFocus--;
                this.addActive(suggestions);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (this.currentFocus > -1 && suggestions[this.currentFocus]) {
                    suggestions[this.currentFocus].click();
                }
            }
        });

        // 외부 클릭시 닫기
        document.addEventListener('click', (e) => {
            if (e.target !== this.input) {
                this.suggestionsContainer.innerHTML = '';
                this.suggestionsContainer.classList.add('hidden');
            }
        });
    }

    async search(query) {
        if (query.length < 2) {
            this.suggestionsContainer.innerHTML = '';
            this.suggestionsContainer.classList.add('hidden');
            return;
        }

        try {
            // Mock data - 실제로는 API 호출
            const mockResults = this.getMockAddresses(query);
            this.renderSuggestions(mockResults);
        } catch (error) {
            console.error('Address search error:', error);
        }
    }

    getMockAddresses(query) {
        const addresses = [
            { address: '서울특별시 강남구 역삼동 123-45', jibun: '역삼동 123-45', roadAddress: '강남대로 123' },
            { address: '서울특별시 강남구 삼성동 100-1', jibun: '삼성동 100-1', roadAddress: '테헤란로 100' },
            { address: '서울특별시 서초구 서초동 1234-5', jibun: '서초동 1234-5', roadAddress: '서초대로 1234' },
            { address: '서울특별시 송파구 잠실동 40-1', jibun: '잠실동 40-1', roadAddress: '올림픽로 40' },
            { address: '경기도 성남시 분당구 정자동 178-1', jibun: '정자동 178-1', roadAddress: '불정로 178' }
        ];

        return addresses.filter(addr => 
            addr.address.toLowerCase().includes(query.toLowerCase()) ||
            addr.jibun.toLowerCase().includes(query.toLowerCase())
        );
    }

    renderSuggestions(results) {
        if (results.length === 0) {
            this.suggestionsContainer.innerHTML = `
                <div class="p-3 text-gray-500 text-sm">검색 결과가 없습니다</div>
            `;
            this.suggestionsContainer.classList.remove('hidden');
            return;
        }

        this.suggestionsContainer.innerHTML = results.map((result, index) => `
            <div class="suggestion-item p-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0" data-index="${index}">
                <div class="font-medium text-sm">${result.address}</div>
                <div class="text-xs text-gray-500 mt-1">도로명: ${result.roadAddress}</div>
            </div>
        `).join('');

        this.suggestionsContainer.classList.remove('hidden');

        // 클릭 이벤트
        const items = this.suggestionsContainer.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.addEventListener('click', () => {
                this.selectSuggestion(results[index]);
            });
        });
    }

    selectSuggestion(result) {
        this.input.value = result.address;
        this.suggestionsContainer.innerHTML = '';
        this.suggestionsContainer.classList.add('hidden');
        this.currentFocus = -1;
    }

    addActive(suggestions) {
        if (!suggestions || suggestions.length === 0) return;
        
        this.removeActive(suggestions);
        
        if (this.currentFocus >= suggestions.length) this.currentFocus = 0;
        if (this.currentFocus < 0) this.currentFocus = suggestions.length - 1;
        
        suggestions[this.currentFocus].classList.add('bg-blue-100');
    }

    removeActive(suggestions) {
        for (let i = 0; i < suggestions.length; i++) {
            suggestions[i].classList.remove('bg-blue-100');
        }
    }
}

// ==========================================
// 3. INLINE PDF VIEWER
// ==========================================

class PDFViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentPdfUrl = null;
    }

    /**
     * PDF 뷰어 열기
     */
    openPDF(pdfUrl, title = 'Report Viewer') {
        this.currentPdfUrl = pdfUrl;
        
        const modal = document.createElement('div');
        modal.id = 'pdfViewerModal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center';
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-2xl w-11/12 h-5/6 flex flex-col">
                <!-- Header -->
                <div class="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
                    <h3 class="text-lg font-bold">${title}</h3>
                    <div class="flex gap-2">
                        <button onclick="pdfViewer.downloadPDF()" class="px-3 py-1 bg-blue-700 hover:bg-blue-800 rounded text-sm">
                            📥 Download
                        </button>
                        <button onclick="pdfViewer.closePDF()" class="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm">
                            ✕ Close
                        </button>
                    </div>
                </div>
                
                <!-- PDF Content -->
                <div class="flex-1 overflow-hidden">
                    <iframe 
                        src="${pdfUrl}" 
                        class="w-full h-full border-0"
                        title="PDF Viewer">
                    </iframe>
                </div>
                
                <!-- Footer -->
                <div class="bg-gray-100 p-2 rounded-b-lg text-center text-xs text-gray-600">
                    ZeroSite v24 Report Viewer
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    /**
     * PDF 뷰어 닫기
     */
    closePDF() {
        const modal = document.getElementById('pdfViewerModal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * PDF 다운로드
     */
    downloadPDF() {
        if (this.currentPdfUrl) {
            const link = document.createElement('a');
            link.href = this.currentPdfUrl;
            link.download = `zerosite_report_${Date.now()}.pdf`;
            link.click();
        }
    }
}

// ==========================================
// 4. AUTO-REFRESH FOR ANALYSIS
// ==========================================

class AnalysisPolling {
    constructor() {
        this.pollingInterval = null;
        this.pollingDelay = 2000; // 2초
        this.maxAttempts = 60; // 최대 2분
        this.currentAttempt = 0;
    }

    /**
     * 폴링 시작
     */
    startPolling(analysisId, callback) {
        this.currentAttempt = 0;
        
        const progressBar = document.getElementById('analysisProgressBar');
        const statusText = document.getElementById('analysisStatusText');
        
        if (progressBar) progressBar.style.display = 'block';

        this.pollingInterval = setInterval(async () => {
            this.currentAttempt++;
            
            // 진행률 업데이트
            const progress = Math.min((this.currentAttempt / this.maxAttempts) * 100, 95);
            if (progressBar) {
                progressBar.querySelector('.progress-fill').style.width = `${progress}%`;
            }
            
            if (statusText) {
                statusText.textContent = `분석 중... ${this.currentAttempt}/${this.maxAttempts}`;
            }

            try {
                // API 호출 (Mock)
                const result = await this.checkAnalysisStatus(analysisId);
                
                if (result.status === 'completed') {
                    this.stopPolling();
                    if (progressBar) {
                        progressBar.querySelector('.progress-fill').style.width = '100%';
                        setTimeout(() => {
                            progressBar.style.display = 'none';
                        }, 500);
                    }
                    callback(result);
                } else if (result.status === 'failed') {
                    this.stopPolling();
                    errorHandler.show('분석 중 오류가 발생했습니다', result.error);
                }
            } catch (error) {
                console.error('Polling error:', error);
            }

            // 최대 시도 횟수 초과
            if (this.currentAttempt >= this.maxAttempts) {
                this.stopPolling();
                errorHandler.show('타임아웃', '분석 시간이 초과되었습니다. 다시 시도해주세요.');
            }
        }, this.pollingDelay);
    }

    /**
     * 폴링 중지
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    /**
     * 분석 상태 확인 (Mock)
     */
    async checkAnalysisStatus(analysisId) {
        // Mock response
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // 80% 확률로 완료 (테스트용)
        if (Math.random() > 0.2 || this.currentAttempt > 5) {
            return {
                status: 'completed',
                reportUrl: '/reports/sample_report.html',
                data: {}
            };
        }
        
        return { status: 'processing' };
    }
}

// ==========================================
// 5. MULTI-STEP WIZARD
// ==========================================

class WizardManager {
    constructor(wizardId) {
        this.wizard = document.getElementById(wizardId);
        this.currentStep = 1;
        this.totalSteps = 4;
        this.formData = {};
    }

    /**
     * 다음 단계로
     */
    nextStep() {
        if (this.validateCurrentStep()) {
            this.saveStepData();
            
            if (this.currentStep < this.totalSteps) {
                this.currentStep++;
                this.renderStep();
            } else {
                this.submitForm();
            }
        }
    }

    /**
     * 이전 단계로
     */
    prevStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.renderStep();
        }
    }

    /**
     * 현재 단계 유효성 검사
     */
    validateCurrentStep() {
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (!currentStepElement) return true;

        const inputs = currentStepElement.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value) {
                input.classList.add('border-red-500');
                isValid = false;
            } else {
                input.classList.remove('border-red-500');
            }
        });

        if (!isValid) {
            errorHandler.show('입력 오류', '필수 항목을 모두 입력해주세요.');
        }

        return isValid;
    }

    /**
     * 현재 단계 데이터 저장
     */
    saveStepData() {
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (!currentStepElement) return;

        const inputs = currentStepElement.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            this.formData[input.name || input.id] = input.value;
        });
    }

    /**
     * 단계 렌더링
     */
    renderStep() {
        // 모든 단계 숨기기
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                step.classList.add('hidden');
            }
        }

        // 현재 단계 표시
        const currentStepElement = document.getElementById(`step${this.currentStep}`);
        if (currentStepElement) {
            currentStepElement.classList.remove('hidden');
        }

        // 진행률 업데이트
        this.updateProgress();
    }

    /**
     * 진행률 업데이트
     */
    updateProgress() {
        const progressBar = document.getElementById('wizardProgress');
        if (progressBar) {
            const progress = (this.currentStep / this.totalSteps) * 100;
            progressBar.style.width = `${progress}%`;
        }

        // 단계 표시기 업데이트
        for (let i = 1; i <= this.totalSteps; i++) {
            const indicator = document.getElementById(`stepIndicator${i}`);
            if (indicator) {
                if (i < this.currentStep) {
                    indicator.className = 'w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center';
                } else if (i === this.currentStep) {
                    indicator.className = 'w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center';
                } else {
                    indicator.className = 'w-8 h-8 rounded-full bg-gray-300 text-gray-600 flex items-center justify-center';
                }
            }
        }
    }

    /**
     * 폼 제출
     */
    async submitForm() {
        try {
            console.log('Form data:', this.formData);
            
            // Show loading
            const submitBtn = document.getElementById('wizardSubmitBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = '분석 중...';
            }

            // Start polling for analysis result
            analysisPolling.startPolling('mock_analysis_id', (result) => {
                successHandler.show('분석 완료!', '보고서가 생성되었습니다.');
                
                // Add to history
                historyManager.addHistory({
                    location: this.formData.location,
                    landArea: parseFloat(this.formData.landArea),
                    type: 'Wizard Analysis',
                    reportFile: result.reportUrl
                });

                // Reset wizard
                this.reset();
            });

        } catch (error) {
            errorHandler.show('제출 오류', error.message);
        }
    }

    /**
     * 위자드 리셋
     */
    reset() {
        this.currentStep = 1;
        this.formData = {};
        this.renderStep();
    }
}

// ==========================================
// 6. ERROR HANDLER
// ==========================================

class ErrorHandler {
    /**
     * 에러 메시지 표시
     */
    show(title, message, type = 'error') {
        const colors = {
            error: { bg: 'bg-red-100', border: 'border-red-500', text: 'text-red-700', icon: '❌' },
            warning: { bg: 'bg-yellow-100', border: 'border-yellow-500', text: 'text-yellow-700', icon: '⚠️' },
            info: { bg: 'bg-blue-100', border: 'border-blue-500', text: 'text-blue-700', icon: 'ℹ️' }
        };

        const color = colors[type] || colors.error;

        const errorDiv = document.createElement('div');
        errorDiv.className = `fixed top-4 right-4 z-50 ${color.bg} border-l-4 ${color.border} p-4 rounded shadow-lg max-w-md animate-slide-in`;
        errorDiv.innerHTML = `
            <div class="flex items-start">
                <div class="text-2xl mr-3">${color.icon}</div>
                <div class="flex-1">
                    <h4 class="font-bold ${color.text}">${title}</h4>
                    <p class="text-sm ${color.text} mt-1">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-gray-500 hover:text-gray-700 ml-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(errorDiv);

        // 5초 후 자동 제거
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
}

class SuccessHandler {
    /**
     * 성공 메시지 표시
     */
    show(title, message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'fixed top-4 right-4 z-50 bg-green-100 border-l-4 border-green-500 p-4 rounded shadow-lg max-w-md animate-slide-in';
        successDiv.innerHTML = `
            <div class="flex items-start">
                <div class="text-2xl mr-3">✅</div>
                <div class="flex-1">
                    <h4 class="font-bold text-green-700">${title}</h4>
                    <p class="text-sm text-green-700 mt-1">${message}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" class="text-gray-500 hover:text-gray-700 ml-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
        `;

        document.body.appendChild(successDiv);

        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }
}

// ==========================================
// GLOBAL INSTANCES
// ==========================================

let historyManager;
let addressAutoComplete;
let pdfViewer;
let analysisPolling;
let wizardManager;
let errorHandler;
let successHandler;

// ==========================================
// INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize managers
    historyManager = new AnalysisHistory();
    pdfViewer = new PDFViewer('pdfViewerContainer');
    analysisPolling = new AnalysisPolling();
    errorHandler = new ErrorHandler();
    successHandler = new SuccessHandler();

    // Render initial history
    historyManager.renderHistory();

    console.log('✅ ZeroSite v24 Dashboard UI 1.0 Initialized');
});

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

/**
 * Quick Analysis 실행
 */
function runQuickAnalysis() {
    const landArea = document.getElementById('quickLandArea').value;
    const location = document.getElementById('quickLocation').value;

    if (!landArea || !location) {
        errorHandler.show('입력 오류', '모든 필수 항목을 입력해주세요.');
        return;
    }

    // Start analysis with polling
    const analysisId = `quick_${Date.now()}`;
    
    analysisPolling.startPolling(analysisId, (result) => {
        successHandler.show('분석 완료!', '보고서가 생성되었습니다.');
        
        historyManager.addHistory({
            location: location,
            landArea: parseFloat(landArea),
            type: 'Quick Analysis',
            reportFile: result.reportUrl
        });

        // Open PDF viewer
        if (result.reportUrl) {
            pdfViewer.openPDF(result.reportUrl, 'Quick Analysis Report');
        }
    });
}

/**
 * 샘플 보고서 보기
 */
function viewSampleReport(reportType) {
    const sampleReports = {
        'submission': '/reports/sample_lh_submission.html',
        'brief': '/reports/sample_brief.html',
        'professional': '/reports/sample_professional.html'
    };

    const url = sampleReports[reportType] || '/reports/sample_report.html';
    pdfViewer.openPDF(url, `${reportType} Report`);
}

/**
 * 시각화 생성
 */
function generateVisualization() {
    const vizType = document.getElementById('vizTypeSelect').value;
    successHandler.show('시각화 생성', `${vizType} 차트가 생성되었습니다.`);
}

/**
 * 배치 처리 시작
 */
function startBatchProcessing() {
    const fileInput = document.getElementById('batchFileInput');
    
    if (!fileInput.files.length) {
        errorHandler.show('파일 없음', '처리할 파일을 선택해주세요.');
        return;
    }

    successHandler.show('배치 처리 시작', '파일 처리를 시작합니다.');
}
