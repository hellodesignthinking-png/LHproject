// ZeroSite v7.0 - Multi-Parcel Manager

class MultiParcelManager {
    constructor(mapManager, apiService) {
        this.mapManager = mapManager;
        this.apiService = apiService;
        this.parcels = [];
        this.analysisResults = null;
    }
    
    // Add parcel to the list
    addParcel(parcelData) {
        if (this.parcels.length >= CONFIG.MULTI_PARCEL.MAX_PARCELS) {
            Utils.showToast(`최대 ${CONFIG.MULTI_PARCEL.MAX_PARCELS}개까지 추가할 수 있습니다.`, 'warning');
            return false;
        }
        
        const parcel = {
            id: Date.now(),
            address: parcelData.address,
            area: parseFloat(parcelData.area),
            unitType: parcelData.unitType,
            coordinates: parcelData.coordinates,
            timestamp: new Date().toISOString()
        };
        
        this.parcels.push(parcel);
        this.updateParcelList();
        
        Utils.showToast('필지가 추가되었습니다.', 'success');
        return true;
    }
    
    // Remove parcel from the list
    removeParcel(parcelId) {
        this.parcels = this.parcels.filter(p => p.id !== parcelId);
        this.updateParcelList();
        Utils.showToast('필지가 제거되었습니다.', 'success');
    }
    
    // Update parcel list display
    updateParcelList() {
        // This would update the UI list of parcels
        console.log('Current parcels:', this.parcels);
    }
    
    // Analyze all parcels
    async analyzeAll() {
        if (this.parcels.length === 0) {
            Utils.showToast('분석할 필지를 추가해주세요.', 'warning');
            return null;
        }
        
        try {
            Utils.showLoading(true);
            
            // Send all parcels for analysis
            this.analysisResults = await this.apiService.analyzeMultiParcel(this.parcels);
            
            // Display results on map
            this.displayResults();
            
            Utils.showLoading(false);
            Utils.showToast('다중 필지 분석이 완료되었습니다.', 'success');
            
            return this.analysisResults;
        } catch (error) {
            console.error('Multi-parcel analysis failed:', error);
            Utils.showLoading(false);
            Utils.showToast(CONFIG.ERRORS.ANALYSIS_FAILED, 'error');
            throw error;
        }
    }
    
    // Display analysis results on map
    displayResults() {
        if (!this.analysisResults || !this.analysisResults.results) {
            return;
        }
        
        // Clear existing markers
        this.mapManager.clearAll();
        
        // Add markers for each parcel with results
        const markers = [];
        
        this.analysisResults.results.forEach((result, index) => {
            if (result.coordinates) {
                const icon = L.divIcon({
                    html: `
                        <div class="custom-marker" style="background: ${this.getScoreColor(result.score)}; color: white;">
                            <span style="font-weight: bold;">${index + 1}</span>
                        </div>
                    `,
                    className: '',
                    iconSize: [32, 32],
                    iconAnchor: [16, 16],
                    popupAnchor: [0, -16]
                });
                
                const marker = L.marker([result.coordinates.lat, result.coordinates.lng], { icon })
                    .bindPopup(this.createParcelPopup(result, index + 1));
                
                markers.push(marker);
                this.mapManager.layers.clusters.addLayer(marker);
            }
        });
        
        // Fit map to show all markers
        if (markers.length > 0) {
            const group = L.featureGroup(markers);
            this.mapManager.map.fitBounds(group.getBounds().pad(0.1));
        }
    }
    
    // Get score color
    getScoreColor(score) {
        const grade = Utils.getScoreGrade(score);
        return Utils.getGradeColor(grade);
    }
    
    // Create parcel popup
    createParcelPopup(result, rank) {
        const grade = Utils.getScoreGrade(result.score);
        const gradeColor = Utils.getGradeColor(grade);
        
        return `
            <div class="poi-popup">
                <div class="poi-popup-header">
                    <div class="poi-popup-icon" style="background: ${gradeColor}20; color: ${gradeColor};">
                        <i class="fas fa-map-marked-alt"></i>
                    </div>
                    <div class="poi-popup-title">
                        <div class="poi-popup-name">필지 #${rank}</div>
                        <div class="poi-popup-category">${result.address || '-'}</div>
                    </div>
                </div>
                <div class="poi-popup-info">
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">면적</span>
                        <span class="poi-popup-value">${Utils.formatNumber(result.area)} ㎡</span>
                    </div>
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">LH 점수</span>
                        <span class="poi-popup-value" style="color: ${gradeColor}">
                            ${result.score}점 (${grade}등급)
                        </span>
                    </div>
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">수요 예측</span>
                        <span class="poi-popup-value">${result.demand || '-'}</span>
                    </div>
                    ${result.recommendation ? `
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">추천도</span>
                        <span class="poi-popup-value">
                            ${result.recommendation === 'high' ? '⭐⭐⭐' : result.recommendation === 'medium' ? '⭐⭐' : '⭐'}
                        </span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Get ranked parcels
    getRankedParcels() {
        if (!this.analysisResults || !this.analysisResults.results) {
            return [];
        }
        
        // Sort by score descending
        const sorted = [...this.analysisResults.results].sort((a, b) => b.score - a.score);
        
        return sorted.map((result, index) => ({
            rank: index + 1,
            ...result,
            grade: Utils.getScoreGrade(result.score),
            gradeColor: this.getScoreColor(result.score)
        }));
    }
    
    // Get top recommendations
    getTopRecommendations(count = 3) {
        const ranked = this.getRankedParcels();
        return ranked.slice(0, count);
    }
    
    // Generate comparison matrix
    generateComparisonMatrix() {
        if (!this.analysisResults || !this.analysisResults.results) {
            return null;
        }
        
        const results = this.analysisResults.results;
        const criteria = ['score', 'demand', 'location', 'infrastructure', 'price'];
        
        const matrix = {
            parcels: results.map(r => r.address),
            criteria: criteria,
            data: results.map(result => ({
                address: result.address,
                values: criteria.map(c => result[c] || Math.random() * 100) // Mock values
            }))
        };
        
        return matrix;
    }
    
    // Generate summary report
    generateSummary() {
        if (!this.analysisResults || !this.analysisResults.results) {
            return null;
        }
        
        const results = this.analysisResults.results;
        const ranked = this.getRankedParcels();
        
        const summary = {
            total_parcels: results.length,
            average_score: Math.round(
                results.reduce((sum, r) => sum + r.score, 0) / results.length
            ),
            top_parcel: ranked[0],
            grade_distribution: this.getGradeDistribution(results),
            recommendations: this.getTopRecommendations(3),
            analysis_date: new Date().toISOString()
        };
        
        return summary;
    }
    
    // Get grade distribution
    getGradeDistribution(results) {
        const distribution = { A: 0, B: 0, C: 0, D: 0 };
        
        results.forEach(result => {
            const grade = Utils.getScoreGrade(result.score);
            distribution[grade]++;
        });
        
        return distribution;
    }
    
    // Export results to JSON
    exportToJSON() {
        if (!this.analysisResults) {
            return null;
        }
        
        const exportData = {
            timestamp: new Date().toISOString(),
            parcels: this.parcels,
            results: this.analysisResults,
            summary: this.generateSummary(),
            comparison: this.generateComparisonMatrix()
        };
        
        return JSON.stringify(exportData, null, 2);
    }
    
    // Clear all parcels
    clearAll() {
        this.parcels = [];
        this.analysisResults = null;
        this.updateParcelList();
        Utils.showToast('모든 필지가 제거되었습니다.', 'success');
    }
}

// Export MultiParcelManager
window.MultiParcelManager = MultiParcelManager;

console.log('ZeroSite v7.0 - Multi-Parcel Manager initialized');
