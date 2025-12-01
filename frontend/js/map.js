// ZeroSite v7.0 - Map Manager

class MapManager {
    constructor() {
        this.map = null;
        this.markers = {
            target: null,
            schools: [],
            hospitals: [],
            convenience: [],
            subway: [],
            recommendations: []
        };
        this.layers = {
            poi: L.layerGroup(),
            recommendations: L.layerGroup(),
            clusters: null
        };
        this.distanceLines = [];
        this.currentLocation = null;
    }
    
    // Initialize map
    initialize(containerId = 'map') {
        const { DEFAULT_CENTER, DEFAULT_ZOOM, MIN_ZOOM, MAX_ZOOM, TILE_LAYER, TILE_ATTRIBUTION } = CONFIG.MAP;
        
        this.map = L.map(containerId, {
            center: DEFAULT_CENTER,
            zoom: DEFAULT_ZOOM,
            minZoom: MIN_ZOOM,
            maxZoom: MAX_ZOOM,
            zoomControl: false
        });
        
        // Add tile layer
        L.tileLayer(TILE_LAYER, {
            attribution: TILE_ATTRIBUTION
        }).addTo(this.map);
        
        // Add zoom control to top right
        L.control.zoom({ position: 'topright' }).addTo(this.map);
        
        // Add layers to map
        this.layers.poi.addTo(this.map);
        this.layers.recommendations.addTo(this.map);
        
        // Initialize marker cluster group
        this.layers.clusters = L.markerClusterGroup({
            maxClusterRadius: CONFIG.MULTI_PARCEL.CLUSTER_RADIUS,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true
        });
        this.map.addLayer(this.layers.clusters);
        
        console.log('Map initialized');
    }
    
    // Create custom marker icon
    createIcon(type, options = {}) {
        const poiConfig = CONFIG.POI.TYPES[type];
        const iconHtml = `
            <div class="custom-marker ${options.className || ''}">
                <i class="fas ${poiConfig ? poiConfig.icon : 'fa-map-marker-alt'}"></i>
            </div>
        `;
        
        return L.divIcon({
            html: iconHtml,
            className: '',
            iconSize: [32, 32],
            iconAnchor: [16, 16],
            popupAnchor: [0, -16]
        });
    }
    
    // Add target marker
    addTargetMarker(lat, lng, data = {}) {
        // Remove existing target marker
        if (this.markers.target) {
            this.map.removeLayer(this.markers.target);
        }
        
        const icon = L.divIcon({
            html: '<div class="custom-marker marker-target"><i class="fas fa-map-marker-alt"></i></div>',
            className: '',
            iconSize: [40, 40],
            iconAnchor: [20, 20],
            popupAnchor: [0, -20]
        });
        
        this.markers.target = L.marker([lat, lng], { icon })
            .addTo(this.map)
            .bindPopup(this.createTargetPopup(data));
        
        this.currentLocation = { lat, lng };
        this.map.setView([lat, lng], 15);
        
        return this.markers.target;
    }
    
    // Create target popup content
    createTargetPopup(data) {
        return `
            <div class="poi-popup">
                <div class="poi-popup-header">
                    <div class="poi-popup-icon" style="background: rgba(37, 99, 235, 0.1); color: #2563eb;">
                        <i class="fas fa-map-marker-alt"></i>
                    </div>
                    <div class="poi-popup-title">
                        <div class="poi-popup-name">분석 대상지</div>
                        <div class="poi-popup-category">${data.address || '주소 정보 없음'}</div>
                    </div>
                </div>
                <div class="poi-popup-info">
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">면적</span>
                        <span class="poi-popup-value">${Utils.formatNumber(data.area)} ㎡</span>
                    </div>
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">유형</span>
                        <span class="poi-popup-value">${data.unitType || '-'}</span>
                    </div>
                    ${data.score ? `
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">LH 점수</span>
                        <span class="poi-popup-value" style="color: ${Utils.getGradeColor(Utils.getScoreGrade(data.score))}">${data.score}점</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Add POI markers
    addPOIMarkers(poiData) {
        // Clear existing POI markers
        this.clearPOIMarkers();
        
        // Add school markers
        if (poiData.schools) {
            poiData.schools.forEach(school => {
                const marker = this.addPOIMarker('SCHOOL', school);
                this.markers.schools.push(marker);
            });
        }
        
        // Add hospital markers
        if (poiData.hospitals) {
            poiData.hospitals.forEach(hospital => {
                const marker = this.addPOIMarker('HOSPITAL', hospital);
                this.markers.hospitals.push(marker);
            });
        }
        
        // Add convenience markers
        if (poiData.convenience) {
            poiData.convenience.forEach(conv => {
                const marker = this.addPOIMarker('CONVENIENCE', conv);
                this.markers.convenience.push(marker);
            });
        }
        
        // Add subway markers
        if (poiData.subway) {
            poiData.subway.forEach(station => {
                const marker = this.addPOIMarker('SUBWAY', station);
                this.markers.subway.push(marker);
            });
        }
        
        // Update legend counts
        this.updateLegendCounts();
    }
    
    // Add single POI marker
    addPOIMarker(type, data) {
        const poiConfig = CONFIG.POI.TYPES[type];
        const icon = this.createIcon(type, { className: `marker-${type.toLowerCase()}` });
        
        const marker = L.marker([data.lat, data.lng], { icon })
            .addTo(this.layers.poi)
            .bindPopup(this.createPOIPopup(type, data));
        
        // Draw distance line to target
        if (this.currentLocation) {
            this.drawDistanceLine(
                this.currentLocation.lat,
                this.currentLocation.lng,
                data.lat,
                data.lng,
                data.distance
            );
        }
        
        return marker;
    }
    
    // Create POI popup content
    createPOIPopup(type, data) {
        const poiConfig = CONFIG.POI.TYPES[type];
        const distanceClass = Utils.getPOIDistanceClass(type, data.distance);
        const distanceLabel = Utils.getPOIDistanceLabel(type, data.distance);
        const distanceColor = Utils.getPOIDistanceColor(type, data.distance);
        
        return `
            <div class="poi-popup">
                <div class="poi-popup-header">
                    <div class="poi-popup-icon ${type.toLowerCase()}">
                        <i class="fas ${poiConfig.icon}"></i>
                    </div>
                    <div class="poi-popup-title">
                        <div class="poi-popup-name">${data.name}</div>
                        <div class="poi-popup-category">${data.type || poiConfig.label}</div>
                    </div>
                </div>
                <div class="poi-popup-info">
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">거리</span>
                        <span class="poi-popup-distance ${distanceClass}" style="background-color: ${distanceColor}20; color: ${distanceColor}; border: 1px solid ${distanceColor}40;">
                            <i class="fas fa-map-marked-alt"></i>
                            ${Utils.formatDistance(data.distance)} (${distanceLabel})
                        </span>
                    </div>
                    ${data.line ? `
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">노선</span>
                        <span class="poi-popup-value">${data.line}</span>
                    </div>
                    ` : ''}
                    ${poiConfig.thresholds ? `
                    <div class="poi-popup-row">
                        <span class="poi-popup-label">LH 기준</span>
                        <span class="poi-popup-value" style="font-size: 11px;">
                            우수: <${poiConfig.thresholds.excellent}m | 
                            양호: <${poiConfig.thresholds.good}m | 
                            보통: <${poiConfig.thresholds.fair}m
                        </span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Draw distance line
    drawDistanceLine(lat1, lng1, lat2, lng2, distance) {
        const line = L.polyline([[lat1, lng1], [lat2, lng2]], {
            color: '#2563eb',
            weight: 2,
            opacity: 0.6,
            dashArray: '5, 5'
        }).addTo(this.layers.poi);
        
        this.distanceLines.push(line);
    }
    
    // Clear POI markers and lines
    clearPOIMarkers() {
        this.layers.poi.clearLayers();
        this.markers.schools = [];
        this.markers.hospitals = [];
        this.markers.convenience = [];
        this.markers.subway = [];
        this.distanceLines = [];
    }
    
    // Update legend counts
    updateLegendCounts() {
        document.getElementById('schoolCount').textContent = this.markers.schools.length;
        document.getElementById('hospitalCount').textContent = this.markers.hospitals.length;
        document.getElementById('convenienceCount').textContent = this.markers.convenience.length;
        document.getElementById('subwayCount').textContent = this.markers.subway.length;
        document.getElementById('recommendationCount').textContent = this.markers.recommendations.length;
    }
    
    // Add recommendation markers (for GeoOptimizer)
    addRecommendationMarkers(recommendations) {
        // Clear existing recommendation markers
        this.clearRecommendationMarkers();
        
        recommendations.forEach((rec, index) => {
            const icon = L.divIcon({
                html: `<div class="custom-marker marker-recommendation"><i class="fas fa-star"></i></div>`,
                className: '',
                iconSize: [36, 36],
                iconAnchor: [18, 18],
                popupAnchor: [0, -18]
            });
            
            const marker = L.marker([rec.lat, rec.lng], { icon })
                .addTo(this.layers.recommendations)
                .bindPopup(this.createRecommendationPopup(rec, index + 1));
            
            this.markers.recommendations.push(marker);
        });
        
        this.updateLegendCounts();
    }
    
    // Create recommendation popup
    createRecommendationPopup(rec, rank) {
        return `
            <div class="recommendation-popup">
                <div class="recommendation-header">
                    <div class="recommendation-badge">
                        <i class="fas fa-star"></i>
                        추천 ${rank}위
                    </div>
                </div>
                <div class="poi-popup-name">${rec.address}</div>
                <div class="recommendation-score">
                    <div class="score-item">
                        <div class="score-label">종합 점수</div>
                        <div class="score-value">${rec.score}</div>
                    </div>
                </div>
                <div class="recommendation-features">
                    ${rec.features ? rec.features.map(f => `<span class="feature-tag ${f.highlight ? 'highlight' : ''}">${f.name}</span>`).join('') : ''}
                </div>
            </div>
        `;
    }
    
    // Clear recommendation markers
    clearRecommendationMarkers() {
        this.layers.recommendations.clearLayers();
        this.markers.recommendations = [];
    }
    
    // Clear all markers
    clearAll() {
        if (this.markers.target) {
            this.map.removeLayer(this.markers.target);
            this.markers.target = null;
        }
        this.clearPOIMarkers();
        this.clearRecommendationMarkers();
        this.layers.clusters.clearLayers();
        this.currentLocation = null;
        this.updateLegendCounts();
    }
    
    // Fit bounds to markers
    fitBounds() {
        const bounds = this.layers.poi.getBounds();
        if (bounds.isValid()) {
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    }
}

// Create global map manager instance
window.mapManager = new MapManager();

console.log('ZeroSite v7.0 - Map Manager initialized');
