// ZeroSite v7.0 - Main Application

class ZeroSiteApp {
    constructor() {
        this.initialized = false;
        this.currentView = 'map';
        this.currentAnalysis = null;
        
        // Initialize managers
        this.poiHandler = null;
        this.geoOptimizer = null;
        this.multiParcelManager = null;
        this.pdfPreviewManager = null;
    }
    
    // Initialize application
    async initialize() {
        try {
            console.log('Initializing ZeroSite v7.0...');
            
            // Check API health
            const health = await apiService.checkHealth();
            console.log('API Health:', health);
            
            // Initialize map
            mapManager.initialize('map');
            
            // Initialize managers
            this.poiHandler = new POIHandler(mapManager, apiService);
            this.geoOptimizer = new GeoOptimizer(mapManager, apiService);
            this.multiParcelManager = new MultiParcelManager(mapManager, apiService);
            this.pdfPreviewManager = new PDFPreviewManager(apiService);
            
            // Make managers globally accessible
            window.poiHandler = this.poiHandler;
            window.geoOptimizer = this.geoOptimizer;
            window.multiParcelManager = this.multiParcelManager;
            window.pdfPreviewManager = this.pdfPreviewManager;
            
            // Setup event listeners
            this.setupEventListeners();
            
            this.initialized = true;
            console.log('ZeroSite v7.0 initialized successfully');
            
            Utils.showToast('ZeroSite v7.0이 준비되었습니다.', 'success');
        } catch (error) {
            console.error('Initialization failed:', error);
            Utils.showToast('초기화에 실패했습니다.', 'error');
        }
    }
    
    // Setup event listeners
    setupEventListeners() {
        // Navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleNavigation(e));
        });
        
        // Search button
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.handleAddressSearch());
        }
        
        // Address input (Enter key)
        const addressInput = document.getElementById('addressInput');
        if (addressInput) {
            addressInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleAddressSearch();
                }
            });
            
            // Address suggestions
            addressInput.addEventListener('input', Utils.debounce((e) => {
                this.handleAddressSuggestions(e.target.value);
            }, CONFIG.UI.DEBOUNCE_DELAY));
        }
        
        // Analyze button
        const analyzeBtn = document.getElementById('analyzeBtn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.handleAnalyze());
        }
        
        // Reset button
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.handleReset());
        }
        
        // Sidebar collapse button
        const collapseBtn = document.getElementById('collapseBtn');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => this.toggleSidebar());
        }
        
        // Map control buttons
        const locateBtn = document.getElementById('locateBtn');
        if (locateBtn) {
            locateBtn.addEventListener('click', () => this.handleLocate());
        }
        
        const layersBtn = document.getElementById('layersBtn');
        if (layersBtn) {
            layersBtn.addEventListener('click', () => this.handleLayers());
        }
        
        const measureBtn = document.getElementById('measureBtn');
        if (measureBtn) {
            measureBtn.addEventListener('click', () => this.handleMeasure());
        }
    }
    
    // Handle navigation
    handleNavigation(event) {
        const btn = event.currentTarget;
        const view = btn.dataset.view;
        
        // Update active state
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Switch view
        this.currentView = view;
        console.log('Switched to view:', view);
        
        // Handle view-specific logic
        switch (view) {
            case 'map':
                this.showMapView();
                break;
            case 'multi':
                this.showMultiParcelView();
                break;
            case 'report':
                this.showReportView();
                break;
            case 'dashboard':
                this.showDashboardView();
                break;
        }
    }
    
    // Handle address search
    async handleAddressSearch() {
        const addressInput = document.getElementById('addressInput');
        const address = addressInput.value.trim();
        
        const validation = Utils.validateAddress(address);
        if (!validation.valid) {
            Utils.showToast(validation.error, 'warning');
            return;
        }
        
        try {
            Utils.showLoading(true);
            
            // Search for address
            const results = await apiService.searchAddress(address);
            
            if (results.length === 0) {
                Utils.showToast(CONFIG.ERRORS.ADDRESS_NOT_FOUND, 'warning');
                Utils.showLoading(false);
                return;
            }
            
            // Use first result
            const result = results[0];
            
            // Add target marker
            mapManager.addTargetMarker(
                result.coordinates.lat,
                result.coordinates.lng,
                {
                    address: result.address,
                    area: parseFloat(document.getElementById('areaInput').value),
                    unitType: document.getElementById('unitTypeInput').value
                }
            );
            
            Utils.showLoading(false);
            Utils.showToast('주소를 찾았습니다.', 'success');
        } catch (error) {
            console.error('Address search failed:', error);
            Utils.showLoading(false);
            Utils.showToast(CONFIG.ERRORS.ADDRESS_NOT_FOUND, 'error');
        }
    }
    
    // Handle address suggestions
    async handleAddressSuggestions(query) {
        if (query.length < 3) {
            document.getElementById('suggestions').classList.remove('active');
            return;
        }
        
        try {
            const results = await apiService.searchAddress(query);
            this.displaySuggestions(results);
        } catch (error) {
            console.error('Failed to get suggestions:', error);
        }
    }
    
    // Display address suggestions
    displaySuggestions(results) {
        const suggestionsDiv = document.getElementById('suggestions');
        
        if (results.length === 0) {
            suggestionsDiv.classList.remove('active');
            return;
        }
        
        suggestionsDiv.innerHTML = results.map(result => `
            <div class="suggestion-item" onclick="app.selectSuggestion('${result.address}', ${result.coordinates.lat}, ${result.coordinates.lng})">
                <div class="suggestion-name">${result.name}</div>
                <div class="suggestion-address">${result.address}</div>
            </div>
        `).join('');
        
        suggestionsDiv.classList.add('active');
    }
    
    // Select suggestion
    selectSuggestion(address, lat, lng) {
        document.getElementById('addressInput').value = address;
        document.getElementById('suggestions').classList.remove('active');
        
        // Add marker
        mapManager.addTargetMarker(lat, lng, {
            address: address,
            area: parseFloat(document.getElementById('areaInput').value),
            unitType: document.getElementById('unitTypeInput').value
        });
    }
    
    // Handle analyze button
    async handleAnalyze() {
        const address = document.getElementById('addressInput').value.trim();
        const area = document.getElementById('areaInput').value;
        const unitType = document.getElementById('unitTypeInput').value;
        
        // Validate inputs
        const addressValidation = Utils.validateAddress(address);
        if (!addressValidation.valid) {
            Utils.showToast(addressValidation.error, 'warning');
            return;
        }
        
        const areaValidation = Utils.validateArea(area);
        if (!areaValidation.valid) {
            Utils.showToast(areaValidation.error, 'warning');
            return;
        }
        
        if (!unitType) {
            Utils.showToast('주택 유형을 선택해주세요.', 'warning');
            return;
        }
        
        // Get analysis options
        const options = {
            poiAnalysis: document.getElementById('poiAnalysis').checked,
            geoOptimizer: document.getElementById('geoOptimizer').checked,
            demographicAnalysis: document.getElementById('demographicAnalysis').checked,
            financialAnalysis: document.getElementById('financialAnalysis').checked
        };
        
        try {
            Utils.showLoading(true);
            
            // Perform analysis
            this.currentAnalysis = await apiService.analyzeLand({
                address,
                area,
                unitType,
                ...options
            });
            
            console.log('Analysis completed:', this.currentAnalysis);
            
            // Display results
            await this.displayAnalysisResults(this.currentAnalysis);
            
            Utils.showLoading(false);
            Utils.showToast(CONFIG.SUCCESS.ANALYSIS_COMPLETE, 'success');
        } catch (error) {
            console.error('Analysis failed:', error);
            Utils.showLoading(false);
            Utils.showToast(CONFIG.ERRORS.ANALYSIS_FAILED, 'error');
        }
    }
    
    // Display analysis results
    async displayAnalysisResults(results) {
        // Update summary panel
        const summaryDiv = document.getElementById('resultsSummary');
        if (summaryDiv) {
            document.getElementById('lhGrade').textContent = results.lh_grade || '-';
            document.getElementById('lhGrade').className = `summary-value grade-${(results.lh_grade || 'd').toLowerCase()}`;
            document.getElementById('totalScore').textContent = `${results.total_score || 0}점`;
            document.getElementById('demandPrediction').textContent = results.demand_prediction || '-';
            document.getElementById('topRecommendation').textContent = results.top_recommendation || '-';
            summaryDiv.style.display = 'block';
        }
        
        // Load POI data if enabled
        if (results.coordinates && results.poi_analysis) {
            await this.poiHandler.loadPOIData(
                results.coordinates.lat,
                results.coordinates.lng
            );
        }
        
        // Load GeoOptimizer recommendations if enabled
        if (results.geo_recommendations && results.geo_recommendations.length > 0) {
            this.geoOptimizer.recommendations = results.geo_recommendations;
            mapManager.addRecommendationMarkers(results.geo_recommendations);
        }
    }
    
    // Handle reset
    handleReset() {
        // Clear inputs
        document.getElementById('addressInput').value = '';
        document.getElementById('areaInput').value = '1000';
        document.getElementById('unitTypeInput').value = '';
        
        // Hide results
        const summaryDiv = document.getElementById('resultsSummary');
        if (summaryDiv) {
            summaryDiv.style.display = 'none';
        }
        
        // Clear map
        mapManager.clearAll();
        
        // Clear managers
        this.poiHandler.clear();
        this.geoOptimizer.clear();
        
        this.currentAnalysis = null;
        
        Utils.showToast('초기화되었습니다.', 'success');
    }
    
    // Toggle sidebar
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('collapsed');
    }
    
    // Handle locate (user location)
    handleLocate() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    mapManager.map.setView([lat, lng], 15);
                    Utils.showToast('현재 위치로 이동했습니다.', 'success');
                },
                (error) => {
                    Utils.showToast('위치를 가져올 수 없습니다.', 'error');
                }
            );
        } else {
            Utils.showToast('이 브라우저는 위치 서비스를 지원하지 않습니다.', 'error');
        }
    }
    
    // Handle layers
    handleLayers() {
        Utils.showToast('레이어 기능은 개발 중입니다.', 'info');
    }
    
    // Handle measure
    handleMeasure() {
        Utils.showToast('거리 측정 기능은 개발 중입니다.', 'info');
    }
    
    // Show map view
    showMapView() {
        console.log('Showing map view');
    }
    
    // Show multi-parcel view
    showMultiParcelView() {
        console.log('Showing multi-parcel view');
        Utils.showToast('다중 필지 분석 모드로 전환되었습니다.', 'info');
    }
    
    // Show report view
    async showReportView() {
        if (!this.currentAnalysis) {
            Utils.showToast('먼저 분석을 실행해주세요.', 'warning');
            return;
        }
        
        try {
            await this.pdfPreviewManager.generateFromAnalysis(this.currentAnalysis);
        } catch (error) {
            console.error('Failed to show report:', error);
        }
    }
    
    // Show dashboard view
    async showDashboardView() {
        try {
            Utils.showLoading(true);
            const dashboardData = await apiService.getDashboardData();
            console.log('Dashboard data:', dashboardData);
            Utils.showLoading(false);
            Utils.showToast('대시보드 데이터를 불러왔습니다.', 'success');
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            Utils.showLoading(false);
            Utils.showToast('대시보드 로딩에 실패했습니다.', 'error');
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ZeroSiteApp();
    window.app.initialize();
});

console.log('ZeroSite v7.0 - Main application loaded');
