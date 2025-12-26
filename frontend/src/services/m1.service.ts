/**
 * M1 API Service
 * ==============
 * 
 * Service layer for M1 Land Information API calls
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 */

import {
  AddressSearchRequest,
  AddressSearchResponse,
  GeocodeRequest,
  GeocodeResponse,
  CadastralRequest,
  CadastralResponse,
  LandUseRequest,
  LandUseResponse,
  RoadInfoRequest,
  RoadInfoResponse,
  MarketDataRequest,
  MarketDataResponse,
  FreezeContextRequest,
  FreezeContextResponse,
  PDFParseResponse,
  ApiResponse,
  LandInfoContext,
} from '../types/m1.types';

import { BACKEND_URL } from '../config';

// 🔥 CRITICAL FIX: Use centralized backend URL config
const API_BASE = `${BACKEND_URL}/api/m1`;

/**
 * Get API keys from SessionStorage
 */
function getApiKeysFromSession(): Record<string, string> {
  try {
    const keysJson = sessionStorage.getItem('m1_api_keys');
    if (keysJson) {
      const keys = JSON.parse(keysJson);
      const headers = {
        'X-Kakao-API-Key': keys.kakao || '',
        'X-VWorld-API-Key': keys.vworld || '',
        'X-DataGoKr-API-Key': keys.dataGoKr || '',
      };
      
      // Log which keys are present (without revealing actual keys)
      console.log('🔑 API Keys Status:', {
        kakao: !!keys.kakao,
        vworld: !!keys.vworld,
        dataGoKr: !!keys.dataGoKr
      });
      
      return headers;
    }
  } catch (e) {
    console.error('Failed to parse API keys from session:', e);
  }
  
  console.warn('⚠️ No API keys found in SessionStorage - using backend .env keys');
  return {};
}

/**
 * Get API headers (alias for getApiKeysFromSession for consistency)
 */
function getApiHeaders(): Record<string, string> {
  return getApiKeysFromSession();
}

/**
 * Generic API call wrapper with error handling
 * 
 * Security: API keys are sent via headers (never in URL or .env)
 * SessionStorage keys are included automatically in all requests
 */
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    // Get API keys from SessionStorage and add to headers
    const apiKeyHeaders = getApiKeysFromSession();
    
    const fullUrl = `${API_BASE}${endpoint}`;
    console.log('🌐 API Call:', {
      url: fullUrl,
      method: options.method || 'GET',
      API_BASE,
      BACKEND_URL
    });
    
    const response = await fetch(fullUrl, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...apiKeyHeaders,
        ...options.headers,
      },
    });

    console.log('📡 Response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ API Error:', error);
      return {
        success: false,
        error: {
          detail: error.detail || 'API request failed',
          status: response.status,
        },
      };
    }

    const data = await response.json();
    console.log('✅ API Success:', data);
    return { success: true, data };
  } catch (error) {
    console.error('🔥 Fetch Error:', error);
    return {
      success: false,
      error: {
        detail: error instanceof Error ? error.message : 'Unknown error',
      },
    };
  }
}

/**
 * M1 API Service
 */
export const m1ApiService = {
  /**
   * STEP 1: Search addresses
   */
  searchAddress: async (
    query: string
  ): Promise<ApiResponse<AddressSearchResponse>> => {
    return apiCall<AddressSearchResponse>('/address/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  },

  /**
   * STEP 2: Geocode address
   */
  geocodeAddress: async (
    address: string
  ): Promise<ApiResponse<GeocodeResponse>> => {
    return apiCall<GeocodeResponse>('/geocode', {
      method: 'POST',
      body: JSON.stringify({ address }),
    });
  },

  /**
   * STEP 3: Get cadastral data
   */
  getCadastralData: async (
    coordinates: { lat: number; lon: number }
  ): Promise<ApiResponse<CadastralResponse>> => {
    return apiCall<CadastralResponse>('/cadastral', {
      method: 'POST',
      body: JSON.stringify({ coordinates }),
    });
  },

  /**
   * STEP 4: Get land use information
   */
  getLandUse: async (
    coordinates: { lat: number; lon: number },
    jimok: string
  ): Promise<ApiResponse<LandUseResponse>> => {
    return apiCall<LandUseResponse>('/land-use', {
      method: 'POST',
      body: JSON.stringify({ coordinates, jimok }),
    });
  },

  /**
   * STEP 5: Get road information
   */
  getRoadInfo: async (
    coordinates: { lat: number; lon: number },
    radius: number = 100
  ): Promise<ApiResponse<RoadInfoResponse>> => {
    return apiCall<RoadInfoResponse>('/road-info', {
      method: 'POST',
      body: JSON.stringify({ coordinates, radius }),
    });
  },

  /**
   * STEP 6: Get market data
   */
  getMarketData: async (
    coordinates: { lat: number; lon: number },
    area: number,
    radius: number = 1000
  ): Promise<ApiResponse<MarketDataResponse>> => {
    return apiCall<MarketDataResponse>('/market-data', {
      method: 'POST',
      body: JSON.stringify({ coordinates, area, radius }),
    });
  },

  /**
   * Parse PDF document
   */
  parsePDF: async (file: File): Promise<ApiResponse<PDFParseResponse>> => {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/parse-pdf`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        return {
          success: false,
          error: {
            detail: error.detail || 'PDF parsing failed',
            status: response.status,
          },
        };
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: {
          detail: error instanceof Error ? error.message : 'PDF parsing error',
        },
      };
    }
  },

  /**
   * STEP 8: Freeze context (create immutable CanonicalLandContext)
   */
  freezeContext: async (
    request: FreezeContextRequest
  ): Promise<ApiResponse<FreezeContextResponse>> => {
    return apiCall<FreezeContextResponse>('/freeze-context', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * Get frozen context by ID
   */
  getFrozenContext: async (
    contextId: string
  ): Promise<ApiResponse<{ context_id: string; land_info_context: LandInfoContext; frozen: boolean }>> => {
    return apiCall<{ context_id: string; land_info_context: LandInfoContext; frozen: boolean }>(
      `/context/${contextId}`,
      {
        method: 'GET',
      }
    );
  },

  /**
   * Health check
   */
  healthCheck: async (): Promise<ApiResponse<{ status: string; module: string }>> => {
    return apiCall<{ status: string; module: string }>('/health', {
      method: 'GET',
    });
  },

  /**
   * 🎯 NEW: Unified data collection (M1 v2.0)
   * 
   * Collects all land data in one operation:
   * - Cadastral (PNU, area, jimok)
   * - Legal (zone, regulations)
   * - Road (contact, width)
   * - Market (price, transactions)
   */
  collectAll: async (
    address: string,
    lat: number,
    lon: number
  ): Promise<ApiResponse<any>> => {
    return apiCall<any>('/collect-all', {
      method: 'POST',
      body: JSON.stringify({ address, lat, lon }),
    });
  },

  /**
   * Upload PDF and extract land data
   */
  uploadPDF: async (file: File): Promise<ApiResponse<any>> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/pdf/extract`, {
      method: 'POST',
      headers: {
        ...getApiHeaders(), // Include API keys
        // Do not set Content-Type for FormData (browser will set it automatically with boundary)
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`PDF upload failed: ${response.statusText}`);
    }

    return response.json();
  },
};

/**
 * Helper: Create data source info
 */
export function createDataSourceInfo(
  source: 'api' | 'manual' | 'pdf',
  apiName?: string,
  confidence?: number
): { source: 'api' | 'manual' | 'pdf'; apiName?: string; timestamp: string; confidence?: number } {
  return {
    source,
    apiName,
    timestamp: new Date().toISOString(),
    confidence,
  };
}

/**
 * Helper: Format address for display
 */
export function formatAddress(
  sido: string,
  sigungu: string,
  dong: string,
  detail?: string
): string {
  const parts = [sido, sigungu, dong, detail].filter(Boolean);
  return parts.join(' ');
}

/**
 * Helper: Format area
 */
export function formatArea(sqm: number): string {
  const pyeong = sqm / 3.3058;
  return `${sqm.toLocaleString()}㎡ (${pyeong.toFixed(1)}평)`;
}

/**
 * Helper: Validate coordinates
 */
export function isValidCoordinates(coords: { lat: number; lon: number }): boolean {
  return (
    coords.lat >= -90 &&
    coords.lat <= 90 &&
    coords.lon >= -180 &&
    coords.lon <= 180
  );
}

export default m1ApiService;
