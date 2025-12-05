// ZeroSite v7.0 - POI Handler

class POIHandler {
    constructor(mapManager, apiService) {
        this.mapManager = mapManager;
        this.apiService = apiService;
        this.poiData = null;
    }
    
    // Load and display POI data for a location
    async loadPOIData(lat, lng, radius = 1000) {
        try {
            Utils.showLoading(true);
            
            // Fetch POI data from API
            this.poiData = await this.apiService.getPOIData(lat, lng, radius);
            
            // Add POI markers to map
            this.mapManager.addPOIMarkers(this.poiData);
            
            // Calculate and display statistics
            this.displayStatistics();
            
            Utils.showLoading(false);
            return this.poiData;
        } catch (error) {
            console.error('Failed to load POI data:', error);
            Utils.showLoading(false);
            Utils.showToast(CONFIG.ERRORS.SERVER_ERROR, 'error');
            throw error;
        }
    }
    
    // Display POI statistics
    displayStatistics() {
        if (!this.poiData) return;
        
        const stats = this.calculateStatistics();
        console.log('POI Statistics:', stats);
        
        // You can display these stats in a UI panel if needed
        return stats;
    }
    
    // Calculate POI statistics
    calculateStatistics() {
        const stats = {
            schools: {
                count: this.poiData.schools?.length || 0,
                nearest: this.findNearest(this.poiData.schools),
                average_distance: this.calculateAverageDistance(this.poiData.schools)
            },
            hospitals: {
                count: this.poiData.hospitals?.length || 0,
                nearest: this.findNearest(this.poiData.hospitals),
                average_distance: this.calculateAverageDistance(this.poiData.hospitals)
            },
            convenience: {
                count: this.poiData.convenience?.length || 0,
                nearest: this.findNearest(this.poiData.convenience),
                average_distance: this.calculateAverageDistance(this.poiData.convenience)
            },
            subway: {
                count: this.poiData.subway?.length || 0,
                nearest: this.findNearest(this.poiData.subway),
                average_distance: this.calculateAverageDistance(this.poiData.subway)
            }
        };
        
        return stats;
    }
    
    // Find nearest POI
    findNearest(pois) {
        if (!pois || pois.length === 0) return null;
        return pois.reduce((nearest, poi) => {
            return (!nearest || poi.distance < nearest.distance) ? poi : nearest;
        }, null);
    }
    
    // Calculate average distance
    calculateAverageDistance(pois) {
        if (!pois || pois.length === 0) return 0;
        const sum = pois.reduce((total, poi) => total + (poi.distance || 0), 0);
        return Math.round(sum / pois.length);
    }
    
    // Get POI score for LH evaluation
    getPOIScore() {
        if (!this.poiData) return 0;
        
        let score = 0;
        const weights = {
            school: 30,
            hospital: 25,
            convenience: 20,
            subway: 25
        };
        
        // School score
        const schoolNearest = this.findNearest(this.poiData.schools);
        if (schoolNearest) {
            if (schoolNearest.distance <= 300) score += weights.school;
            else if (schoolNearest.distance <= 600) score += weights.school * 0.7;
            else if (schoolNearest.distance <= 1000) score += weights.school * 0.4;
        }
        
        // Hospital score
        const hospitalNearest = this.findNearest(this.poiData.hospitals);
        if (hospitalNearest) {
            if (hospitalNearest.distance <= 500) score += weights.hospital;
            else if (hospitalNearest.distance <= 1000) score += weights.hospital * 0.7;
            else if (hospitalNearest.distance <= 1500) score += weights.hospital * 0.4;
        }
        
        // Convenience score
        const convenienceNearest = this.findNearest(this.poiData.convenience);
        if (convenienceNearest) {
            if (convenienceNearest.distance <= 200) score += weights.convenience;
            else if (convenienceNearest.distance <= 400) score += weights.convenience * 0.7;
            else if (convenienceNearest.distance <= 600) score += weights.convenience * 0.4;
        }
        
        // Subway score
        const subwayNearest = this.findNearest(this.poiData.subway);
        if (subwayNearest) {
            if (subwayNearest.distance <= 500) score += weights.subway;
            else if (subwayNearest.distance <= 800) score += weights.subway * 0.7;
            else if (subwayNearest.distance <= 1200) score += weights.subway * 0.4;
        }
        
        return Math.round(score);
    }
    
    // Generate POI summary report
    generateSummary() {
        const stats = this.calculateStatistics();
        const score = this.getPOIScore();
        
        return {
            score,
            statistics: stats,
            grade: Utils.getScoreGrade(score),
            summary: this.generateTextSummary(stats, score)
        };
    }
    
    // Generate text summary
    generateTextSummary(stats, score) {
        const parts = [];
        
        if (stats.schools.nearest) {
            parts.push(`가장 가까운 학교는 ${stats.schools.nearest.name}(${Utils.formatDistance(stats.schools.nearest.distance)})`);
        }
        
        if (stats.hospitals.nearest) {
            parts.push(`가장 가까운 병원은 ${stats.hospitals.nearest.name}(${Utils.formatDistance(stats.hospitals.nearest.distance)})`);
        }
        
        if (stats.subway.nearest) {
            parts.push(`가장 가까운 지하철역은 ${stats.subway.nearest.name}(${Utils.formatDistance(stats.subway.nearest.distance)})`);
        }
        
        const grade = Utils.getScoreGrade(score);
        parts.push(`전체 POI 점수는 ${score}점(${grade}등급)입니다`);
        
        return parts.join('. ') + '.';
    }
    
    // Clear POI data
    clear() {
        this.poiData = null;
    }
}

// Export POI Handler
window.POIHandler = POIHandler;

console.log('ZeroSite v7.0 - POI Handler initialized');
