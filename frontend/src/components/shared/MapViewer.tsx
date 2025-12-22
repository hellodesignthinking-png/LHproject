/**
 * MapViewer Component
 * ===================
 * 
 * Map viewer for location visualization
 * Supports Kakao Map or fallback to simple marker display
 * 
 * Features:
 * - Display coordinates on map
 * - Draggable marker for manual adjustment
 * - Layer toggle (roads, parcels, zoning)
 * - Multiple markers support
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 */

import React, { useEffect, useRef, useState } from 'react';
import { MapViewerProps } from '../../types/m1.types';
import './MapViewer.css';

declare global {
  interface Window {
    kakao: any;
  }
}

export const MapViewer: React.FC<MapViewerProps> = ({
  coordinates,
  layers = [],
  markers = [],
  onCoordinatesChange,
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [mapInstance, setMapInstance] = useState<any>(null);
  const [isKakaoLoaded, setIsKakaoLoaded] = useState(false);
  const [activeLayers, setActiveLayers] = useState<string[]>(layers);

  // Load Kakao Map SDK
  useEffect(() => {
    if (window.kakao && window.kakao.maps) {
      setIsKakaoLoaded(true);
      return;
    }

    // Check if script already exists
    const existingScript = document.querySelector(
      'script[src*="dapi.kakao.com"]'
    );
    if (existingScript) {
      const checkKakao = setInterval(() => {
        if (window.kakao && window.kakao.maps) {
          setIsKakaoLoaded(true);
          clearInterval(checkKakao);
        }
      }, 100);
      return;
    }

    // Note: Kakao Map requires API key
    // For now, we'll use fallback static map
    console.warn('Kakao Map SDK not loaded. Using fallback display.');
  }, []);

  // Initialize map
  useEffect(() => {
    if (!mapRef.current || !isKakaoLoaded) return;

    const container = mapRef.current;
    const options = {
      center: new window.kakao.maps.LatLng(coordinates.lat, coordinates.lon),
      level: 3,
    };

    const map = new window.kakao.maps.Map(container, options);
    setMapInstance(map);

    // Add main marker
    const markerPosition = new window.kakao.maps.LatLng(
      coordinates.lat,
      coordinates.lon
    );
    const marker = new window.kakao.maps.Marker({
      position: markerPosition,
      draggable: !!onCoordinatesChange,
    });
    marker.setMap(map);

    // Add drag event
    if (onCoordinatesChange) {
      window.kakao.maps.event.addListener(marker, 'dragend', function () {
        const position = marker.getPosition();
        onCoordinatesChange({
          lat: position.getLat(),
          lon: position.getLng(),
        });
      });
    }

    // Add additional markers
    markers.forEach((m) => {
      const pos = new window.kakao.maps.LatLng(m.lat, m.lon);
      const additionalMarker = new window.kakao.maps.Marker({
        position: pos,
      });
      additionalMarker.setMap(map);

      if (m.label) {
        const infowindow = new window.kakao.maps.InfoWindow({
          content: `<div style="padding:5px;">${m.label}</div>`,
        });
        infowindow.open(map, additionalMarker);
      }
    });
  }, [isKakaoLoaded, mapRef.current]);

  // Update center when coordinates change
  useEffect(() => {
    if (!mapInstance) return;
    const newCenter = new window.kakao.maps.LatLng(
      coordinates.lat,
      coordinates.lon
    );
    mapInstance.setCenter(newCenter);
  }, [coordinates, mapInstance]);

  // Toggle layer
  const toggleLayer = (layer: string) => {
    setActiveLayers((prev) =>
      prev.includes(layer)
        ? prev.filter((l) => l !== layer)
        : [...prev, layer]
    );
  };

  // Fallback: Static map display
  if (!isKakaoLoaded) {
    return (
      <div className="map-viewer-fallback">
        <div className="fallback-map">
          <div className="coordinates-display">
            <div className="coord-item">
              <span className="coord-label">위도 (Lat):</span>
              <span className="coord-value">{coordinates.lat.toFixed(6)}</span>
            </div>
            <div className="coord-item">
              <span className="coord-label">경도 (Lon):</span>
              <span className="coord-value">{coordinates.lon.toFixed(6)}</span>
            </div>
          </div>
          <div className="fallback-marker">📍</div>
          <p className="fallback-note">
            지도를 표시하려면 Kakao Map API 키가 필요합니다.
          </p>
          {onCoordinatesChange && (
            <button
              className="btn-manual-input"
              onClick={() => {
                const lat = prompt('위도를 입력하세요:', String(coordinates.lat));
                const lon = prompt('경도를 입력하세요:', String(coordinates.lon));
                if (lat && lon) {
                  onCoordinatesChange({
                    lat: parseFloat(lat),
                    lon: parseFloat(lon),
                  });
                }
              }}
            >
              좌표 수동 입력
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="map-viewer">
      <div className="map-container" ref={mapRef} />
      {layers.length > 0 && (
        <div className="map-controls">
          <div className="layer-controls">
            {layers.map((layer) => (
              <button
                key={layer}
                className={`layer-btn ${
                  activeLayers.includes(layer) ? 'active' : ''
                }`}
                onClick={() => toggleLayer(layer)}
              >
                {layer === 'roads' && '🛣️ 도로'}
                {layer === 'parcels' && '🏞️ 필지'}
                {layer === 'zoning' && '📋 용도'}
              </button>
            ))}
          </div>
        </div>
      )}
      <div className="map-info">
        <span className="info-label">좌표:</span>
        <span className="info-value">
          {coordinates.lat.toFixed(6)}, {coordinates.lon.toFixed(6)}
        </span>
        {onCoordinatesChange && (
          <span className="info-hint">💡 마커를 드래그하여 위치 조정</span>
        )}
      </div>
    </div>
  );
};

export default MapViewer;
