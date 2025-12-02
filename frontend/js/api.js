// ZeroSite v7.0 - API Service

class APIService {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
        this.endpoints = CONFIG.API_ENDPOINTS;
    }
    
    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }
    
    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    // Health check
    async checkHealth() {
        try {
            const response = await this.get(this.endpoints.HEALTH);
            return response;
        } catch (error) {
            console.error('Health check failed:', error);
            return { status: 'error', message: error.message };
        }
    }
    
    // Analyze single land parcel
    async analyzeLand(data) {
        try {
            const payload = {
                address: data.address,
                area_sqm: parseFloat(data.area),
                unit_type: data.unitType || '신축매입임대',
                options: {
                    poi_analysis: data.poiAnalysis !== false,
                    geo_optimizer: data.geoOptimizer !== false,
                    demographic_analysis: data.demographicAnalysis !== false,
                    financial_analysis: data.financialAnalysis !== false
                }
            };
            
            console.log('Analyzing land:', payload);
            const response = await this.post(this.endpoints.ANALYZE_LAND, payload);
            console.log('Analysis response:', response);
            
            return response;
        } catch (error) {
            console.error('Land analysis failed:', error);
            throw error;
        }
    }
    
    // Analyze multiple parcels
    async analyzeMultiParcel(parcels) {
        try {
            const payload = {
                parcels: parcels.map(p => ({
                    address: p.address,
                    area_sqm: parseFloat(p.area),
                    unit_type: p.unitType || '신축매입임대'
                }))
            };
            
            console.log('Analyzing multiple parcels:', payload);
            const response = await this.post(this.endpoints.ANALYZE_MULTI, payload);
            console.log('Multi-parcel analysis response:', response);
            
            return response;
        } catch (error) {
            console.error('Multi-parcel analysis failed:', error);
            throw error;
        }
    }
    
    // Generate report
    async generateReport(analysisData, format = 'PDF') {
        try {
            const payload = {
                analysis_data: analysisData,
                format: format,
                options: {
                    include_maps: true,
                    include_charts: true,
                    include_appendix: true
                }
            };
            
            console.log('Generating report:', payload);
            const response = await this.post(this.endpoints.GENERATE_REPORT, payload);
            console.log('Report generation response:', response);
            
            return response;
        } catch (error) {
            console.error('Report generation failed:', error);
            throw error;
        }
    }
    
    // Get dashboard data
    async getDashboardData() {
        try {
            const response = await this.get(this.endpoints.DASHBOARD);
            return response;
        } catch (error) {
            console.error('Failed to get dashboard data:', error);
            throw error;
        }
    }
    
    // Get LH notices
    async getLHNotices() {
        try {
            const response = await this.get(this.endpoints.LH_NOTICES);
            return response;
        } catch (error) {
            console.error('Failed to get LH notices:', error);
            throw error;
        }
    }
    
    // Search address (mock for now, can integrate with Kakao/Naver API)
    async searchAddress(query) {
        try {
            // Mock address search results
            // In production, integrate with Kakao Local API or Naver Maps API
            const mockResults = [
                {
                    address: '서울특별시 마포구 월드컵북로 120',
                    name: '상암동 주거지역',
                    coordinates: { lat: 37.5799, lng: 126.8892 }
                },
                {
                    address: '서울특별시 송파구 올림픽로 300',
                    name: '롯데월드타워',
                    coordinates: { lat: 37.5125, lng: 127.1025 }
                },
                {
                    address: '서울특별시 강남구 테헤란로 152',
                    name: '강남역 인근',
                    coordinates: { lat: 37.4989, lng: 127.0276 }
                }
            ];
            
            // Filter results based on query
            const filtered = mockResults.filter(result =>
                result.address.toLowerCase().includes(query.toLowerCase()) ||
                result.name.toLowerCase().includes(query.toLowerCase())
            );
            
            return filtered;
        } catch (error) {
            console.error('Address search failed:', error);
            throw error;
        }
    }
    
    // Get POI data around location
    async getPOIData(lat, lng, radius = 1000) {
        try {
            // Mock POI data
            // In production, integrate with Kakao Local API or Naver Maps API
            const mockPOI = {
                schools: [
                    { name: '상암초등학교', lat: 37.5820, lng: 126.8910, distance: 288, type: '초등학교' },
                    { name: '상암중학교', lat: 37.5785, lng: 126.8875, distance: 420, type: '중학교' }
                ],
                hospitals: [
                    { name: '상암메디컬센터', lat: 37.5810, lng: 126.8900, distance: 179, type: '병원' },
                    { name: '마포구보건소', lat: 37.5795, lng: 126.8880, distance: 350, type: '보건소' }
                ],
                convenience: [
                    { name: 'GS25 상암점', lat: 37.5805, lng: 126.8895, distance: 95, type: '편의점' },
                    { name: '이마트24 월드컵점', lat: 37.5802, lng: 126.8888, distance: 120, type: '편의점' }
                ],
                subway: [
                    { name: '월드컵경기장역', lat: 37.5685, lng: 126.8997, distance: 450, type: '지하철', line: '6호선' }
                ]
            };
            
            return mockPOI;
        } catch (error) {
            console.error('POI data fetch failed:', error);
            throw error;
        }
    }
}

// Create global API service instance
window.apiService = new APIService();

console.log('ZeroSite v7.0 - API Service initialized');
