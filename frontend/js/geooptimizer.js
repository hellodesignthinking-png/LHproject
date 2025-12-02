// ZeroSite v7.0 - GeoOptimizer

class GeoOptimizer {
    constructor(mapManager, apiService) {
        this.mapManager = mapManager;
        this.apiService = apiService;
        this.recommendations = [];
    }
    
    // Generate alternative location recommendations
    async generateRecommendations(baseLocation, analysisData) {
        try {
            Utils.showLoading(true);
            
            // Generate recommendations based on base location
            this.recommendations = await this.findOptimalLocations(baseLocation, analysisData);
            
            // Sort by score
            this.recommendations.sort((a, b) => b.score - a.score);
            
            // Take top 3
            this.recommendations = this.recommendations.slice(0, CONFIG.GEO_OPTIMIZER.RECOMMENDATION_COUNT);
            
            // Add markers to map
            this.mapManager.addRecommendationMarkers(this.recommendations);
            
            Utils.showLoading(false);
            return this.recommendations;
        } catch (error) {
            console.error('Failed to generate recommendations:', error);
            Utils.showLoading(false);
            Utils.showToast('추천지 생성에 실패했습니다.', 'error');
            throw error;
        }
    }
    
    // Find optimal locations using scoring algorithm
    async findOptimalLocations(baseLocation, analysisData) {
        // Mock recommendation generation
        // In production, this would use real estate data, demographics, and ML models
        
        const searchRadius = CONFIG.GEO_OPTIMIZER.SEARCH_RADIUS;
        const candidates = this.generateCandidateLocations(baseLocation, searchRadius);
        
        const scoredCandidates = [];
        
        for (const candidate of candidates) {
            const score = await this.calculateLocationScore(candidate, analysisData);
            
            if (score >= CONFIG.GEO_OPTIMIZER.MIN_SCORE) {
                scoredCandidates.push({
                    ...candidate,
                    score: Math.round(score),
                    features: this.identifyKeyFeatures(candidate, score)
                });
            }
        }
        
        return scoredCandidates;
    }
    
    // Generate candidate locations around base location
    generateCandidateLocations(baseLocation, radius) {
        // Generate random candidates in a radius
        // In production, use real address database
        
        const candidates = [];
        const numCandidates = 10;
        
        const mockAddresses = [
            { name: '서울특별시 송파구 올림픽로 300', district: '송파구' },
            { name: '서울특별시 강남구 테헤란로 152', district: '강남구' },
            { name: '서울특별시 서초구 서초대로 74길 11', district: '서초구' },
            { name: '서울특별시 영등포구 여의대로 108', district: '영등포구' },
            { name: '서울특별시 용산구 이태원로 234', district: '용산구' },
            { name: '서울특별시 성동구 왕십리로 346', district: '성동구' },
            { name: '서울특별시 광진구 능동로 120', district: '광진구' },
            { name: '서울특별시 마포구 마포대로 122', district: '마포구' },
            { name: '서울특별시 동작구 노량진로 154', district: '동작구' },
            { name: '서울특별시 관악구 관악로 145', district: '관악구' }
        ];
        
        for (let i = 0; i < numCandidates; i++) {
            const addr = mockAddresses[i % mockAddresses.length];
            
            // Generate random offset from base location
            const offsetLat = (Math.random() - 0.5) * (radius / 111000); // rough conversion
            const offsetLng = (Math.random() - 0.5) * (radius / 111000);
            
            candidates.push({
                address: addr.name,
                district: addr.district,
                lat: baseLocation.lat + offsetLat,
                lng: baseLocation.lng + offsetLng
            });
        }
        
        return candidates;
    }
    
    // Calculate location score
    async calculateLocationScore(location, analysisData) {
        const weights = CONFIG.GEO_OPTIMIZER.WEIGHTS;
        let totalScore = 0;
        
        // Location score (proximity to key areas)
        const locationScore = this.calculateProximityScore(location);
        totalScore += locationScore * weights.LOCATION;
        
        // Demographics score (population, age distribution)
        const demographicsScore = Math.random() * 100; // Mock
        totalScore += demographicsScore * weights.DEMOGRAPHICS;
        
        // Infrastructure score (transportation, facilities)
        const infrastructureScore = Math.random() * 100; // Mock
        totalScore += infrastructureScore * weights.INFRASTRUCTURE;
        
        // Price score (comparative value)
        const priceScore = Math.random() * 100; // Mock
        totalScore += priceScore * weights.PRICE;
        
        return totalScore;
    }
    
    // Calculate proximity score
    calculateProximityScore(location) {
        // Mock scoring based on district
        const highValueDistricts = ['강남구', '서초구', '송파구', '마포구'];
        const mediumValueDistricts = ['영등포구', '용산구', '성동구', '광진구'];
        
        if (highValueDistricts.includes(location.district)) {
            return 80 + Math.random() * 20;
        } else if (mediumValueDistricts.includes(location.district)) {
            return 60 + Math.random() * 20;
        } else {
            return 40 + Math.random() * 20;
        }
    }
    
    // Identify key features of a location
    identifyKeyFeatures(location, score) {
        const features = [];
        
        if (score >= 85) {
            features.push({ name: '최우수 입지', highlight: true });
        }
        
        if (location.district === '강남구' || location.district === '서초구') {
            features.push({ name: '강남권', highlight: true });
        }
        
        if (Math.random() > 0.5) {
            features.push({ name: '역세권', highlight: false });
        }
        
        if (Math.random() > 0.5) {
            features.push({ name: '학군 우수', highlight: false });
        }
        
        if (Math.random() > 0.5) {
            features.push({ name: '개발 호재', highlight: false });
        }
        
        if (Math.random() > 0.5) {
            features.push({ name: '편의시설 인접', highlight: false });
        }
        
        return features;
    }
    
    // Get recommendation details
    getRecommendationDetails(index) {
        if (index < 0 || index >= this.recommendations.length) {
            return null;
        }
        
        const rec = this.recommendations[index];
        
        return {
            rank: index + 1,
            address: rec.address,
            score: rec.score,
            grade: Utils.getScoreGrade(rec.score),
            features: rec.features,
            comparison: this.compareWithBase(rec),
            details: {
                location: rec.lat && rec.lng ? `${rec.lat.toFixed(6)}, ${rec.lng.toFixed(6)}` : '-',
                district: rec.district || '-'
            }
        };
    }
    
    // Compare recommendation with base location
    compareWithBase(recommendation) {
        // Mock comparison
        return {
            score_diff: Math.round((Math.random() - 0.5) * 20),
            advantages: [
                '더 나은 교통 접근성',
                '더 높은 수요 예측',
                '우수한 개발 가능성'
            ].slice(0, Math.floor(Math.random() * 3) + 1),
            disadvantages: [
                '상대적으로 높은 가격',
                '경쟁 물건 다수'
            ].slice(0, Math.floor(Math.random() * 2))
        };
    }
    
    // Generate comparison report
    generateComparisonReport() {
        if (this.recommendations.length === 0) {
            return null;
        }
        
        return {
            recommendations: this.recommendations.map((rec, index) => 
                this.getRecommendationDetails(index)
            ),
            summary: this.generateSummary()
        };
    }
    
    // Generate summary
    generateSummary() {
        if (this.recommendations.length === 0) {
            return '추천지를 찾을 수 없습니다.';
        }
        
        const topRec = this.recommendations[0];
        const avgScore = Math.round(
            this.recommendations.reduce((sum, rec) => sum + rec.score, 0) / this.recommendations.length
        );
        
        return `총 ${this.recommendations.length}개의 추천지를 발굴했습니다. ` +
               `최고 추천지는 ${topRec.address}(${topRec.score}점)이며, ` +
               `평균 점수는 ${avgScore}점입니다.`;
    }
    
    // Clear recommendations
    clear() {
        this.recommendations = [];
    }
}

// Export GeoOptimizer
window.GeoOptimizer = GeoOptimizer;

console.log('ZeroSite v7.0 - GeoOptimizer initialized');
