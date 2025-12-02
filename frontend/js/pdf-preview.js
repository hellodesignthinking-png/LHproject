// ZeroSite v7.0 - PDF Preview Manager

class PDFPreviewManager {
    constructor(apiService) {
        this.apiService = apiService;
        this.currentReport = null;
        this.previewUrl = null;
    }
    
    // Generate and preview report
    async generateAndPreview(analysisData, format = 'PDF') {
        try {
            Utils.showLoading(true);
            
            // Generate report
            const response = await this.apiService.generateReport(analysisData, format);
            
            if (response.success && response.report_url) {
                this.previewUrl = response.report_url;
                this.currentReport = response;
                
                // Show preview modal
                this.showPreviewModal(this.previewUrl, format);
                
                Utils.showLoading(false);
                Utils.showToast(CONFIG.SUCCESS.REPORT_GENERATED, 'success');
                
                return response;
            } else {
                throw new Error('Report generation failed');
            }
        } catch (error) {
            console.error('Failed to generate and preview report:', error);
            Utils.showLoading(false);
            Utils.showToast('보고서 생성에 실패했습니다.', 'error');
            throw error;
        }
    }
    
    // Show preview modal
    showPreviewModal(url, format) {
        const modal = document.getElementById('pdfModal');
        const preview = document.getElementById('pdfPreview');
        
        if (format === 'PDF') {
            preview.src = url;
        } else if (format === 'HTML') {
            preview.src = url;
        }
        
        modal.classList.add('active');
    }
    
    // Close preview modal
    closePreviewModal() {
        const modal = document.getElementById('pdfModal');
        modal.classList.remove('active');
    }
    
    // Download report
    async downloadReport() {
        if (!this.previewUrl) {
            Utils.showToast('다운로드할 보고서가 없습니다.', 'warning');
            return;
        }
        
        try {
            // Create temporary link and trigger download
            const link = document.createElement('a');
            link.href = this.previewUrl;
            link.download = this.generateFilename();
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            Utils.showToast('보고서 다운로드가 시작되었습니다.', 'success');
        } catch (error) {
            console.error('Download failed:', error);
            Utils.showToast('다운로드에 실패했습니다.', 'error');
        }
    }
    
    // Generate filename
    generateFilename() {
        const timestamp = new Date().toISOString().split('T')[0];
        const format = this.currentReport?.format || 'PDF';
        return `ZeroSite_Report_${timestamp}.${format.toLowerCase()}`;
    }
    
    // Generate report from analysis results
    async generateFromAnalysis(analysisResults) {
        const reportData = this.prepareReportData(analysisResults);
        return await this.generateAndPreview(reportData);
    }
    
    // Prepare report data
    prepareReportData(analysisResults) {
        return {
            title: 'ZeroSite Land Analysis Report',
            subtitle: 'LH 신축매입임대 토지 진단 보고서',
            version: '7.0',
            date: new Date().toISOString(),
            
            // Executive Summary
            executive_summary: {
                address: analysisResults.address,
                area: analysisResults.area,
                unit_type: analysisResults.unit_type,
                lh_grade: analysisResults.lh_grade,
                total_score: analysisResults.total_score,
                demand_prediction: analysisResults.demand_prediction
            },
            
            // Location Analysis
            location: {
                coordinates: analysisResults.coordinates,
                district: analysisResults.district,
                zoning: analysisResults.zoning
            },
            
            // POI Analysis
            poi: analysisResults.poi_analysis,
            
            // GeoOptimizer Recommendations
            recommendations: analysisResults.geo_recommendations,
            
            // Demographics
            demographics: analysisResults.demographics,
            
            // Financial Analysis
            financial: analysisResults.financial_analysis,
            
            // Risk Analysis
            risks: analysisResults.risk_analysis,
            
            // Appendix
            appendix: {
                lh_rules: true,
                legal_references: true,
                data_sources: true
            }
        };
    }
    
    // Create real-time preview (for editing)
    createRealtimePreview(container, data) {
        // This would create an editable preview
        const preview = document.createElement('div');
        preview.className = 'realtime-preview';
        preview.innerHTML = this.generateHTMLPreview(data);
        
        container.appendChild(preview);
        
        return preview;
    }
    
    // Generate HTML preview
    generateHTMLPreview(data) {
        return `
            <div class="report-preview">
                <header class="report-header">
                    <h1>ZeroSite v7.0</h1>
                    <h2>토지 분석 보고서</h2>
                    <p class="report-date">${new Date().toLocaleDateString('ko-KR')}</p>
                </header>
                
                <section class="report-section">
                    <h3>📍 대상지 정보</h3>
                    <table class="report-table">
                        <tr>
                            <td>주소</td>
                            <td>${data.executive_summary?.address || '-'}</td>
                        </tr>
                        <tr>
                            <td>면적</td>
                            <td>${Utils.formatNumber(data.executive_summary?.area)} ㎡</td>
                        </tr>
                        <tr>
                            <td>주택유형</td>
                            <td>${data.executive_summary?.unit_type || '-'}</td>
                        </tr>
                    </table>
                </section>
                
                <section class="report-section">
                    <h3>📊 종합 평가</h3>
                    <div class="score-display">
                        <div class="score-main">
                            <span class="score-value">${data.executive_summary?.total_score || 0}</span>
                            <span class="score-label">점</span>
                        </div>
                        <div class="score-grade">
                            <span class="grade-badge">${data.executive_summary?.lh_grade || '-'}</span>
                            <span class="grade-label">등급</span>
                        </div>
                    </div>
                </section>
                
                <section class="report-section">
                    <h3>🏘️ POI 분석</h3>
                    <div class="poi-summary">
                        ${this.generatePOISummaryHTML(data.poi)}
                    </div>
                </section>
                
                <section class="report-section">
                    <h3>⭐ 추천 대체지</h3>
                    <div class="recommendations-list">
                        ${this.generateRecommendationsHTML(data.recommendations)}
                    </div>
                </section>
                
                <footer class="report-footer">
                    <p>본 보고서는 ZeroSite v7.0 시스템에 의해 자동 생성되었습니다.</p>
                    <p class="watermark">© ${new Date().getFullYear()} ZeroSite. All rights reserved.</p>
                </footer>
            </div>
        `;
    }
    
    // Generate POI summary HTML
    generatePOISummaryHTML(poiData) {
        if (!poiData) return '<p>POI 데이터 없음</p>';
        
        return `
            <div class="poi-grid">
                <div class="poi-item">
                    <i class="fas fa-school"></i>
                    <span>학교: ${poiData.schools?.count || 0}개</span>
                </div>
                <div class="poi-item">
                    <i class="fas fa-hospital"></i>
                    <span>병원: ${poiData.hospitals?.count || 0}개</span>
                </div>
                <div class="poi-item">
                    <i class="fas fa-shopping-cart"></i>
                    <span>편의시설: ${poiData.convenience?.count || 0}개</span>
                </div>
                <div class="poi-item">
                    <i class="fas fa-subway"></i>
                    <span>지하철: ${poiData.subway?.count || 0}개</span>
                </div>
            </div>
        `;
    }
    
    // Generate recommendations HTML
    generateRecommendationsHTML(recommendations) {
        if (!recommendations || recommendations.length === 0) {
            return '<p>추천 대체지 없음</p>';
        }
        
        return recommendations.map((rec, index) => `
            <div class="recommendation-item">
                <div class="rec-rank">${index + 1}</div>
                <div class="rec-content">
                    <h4>${rec.address}</h4>
                    <p class="rec-score">점수: ${rec.score}점</p>
                </div>
            </div>
        `).join('');
    }
    
    // Clear current report
    clear() {
        this.currentReport = null;
        this.previewUrl = null;
    }
}

// Global functions for modal control
function closePdfModal() {
    const modal = document.getElementById('pdfModal');
    modal.classList.remove('active');
}

function downloadPdf() {
    if (window.pdfPreviewManager) {
        window.pdfPreviewManager.downloadReport();
    }
}

// Export PDFPreviewManager
window.PDFPreviewManager = PDFPreviewManager;

console.log('ZeroSite v7.0 - PDF Preview Manager initialized');
