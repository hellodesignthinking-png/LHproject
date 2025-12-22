/**
 * M1 Land Information API Types
 * ==============================
 * 
 * TypeScript type definitions for M1 8-STEP land information collection
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 * Version: 1.0
 */

// ============================================================================
// Data Source Types
// ============================================================================

export type DataSource = 'api' | 'manual' | 'pdf' | 'mock';

export interface DataSourceInfo {
  source: DataSource;
  apiName?: string;
  timestamp: string;
  confidence?: number;
}

// ============================================================================
// STEP 1: Address Search
// ============================================================================

export interface AddressSearchRequest {
  query: string;
}

export interface AddressSuggestion {
  road_address: string;
  jibun_address: string;
  coordinates: {
    lat: number;
    lon: number;
  };
  sido: string;
  sigungu: string;
  dong: string;
  building_name?: string;
}

export interface AddressSearchResponse {
  suggestions: AddressSuggestion[];
  success: boolean;
  using_mock_data?: boolean;
}

// ============================================================================
// STEP 2: Geocoding
// ============================================================================

export interface GeocodeRequest {
  address: string;
}

export interface GeocodeResponse {
  coordinates: {
    lat: number;
    lon: number;
  };
  sido: string;
  sigungu: string;
  dong: string;
  beopjeong_dong: string;
  success: boolean;
}

// ============================================================================
// STEP 3: Cadastral Data
// ============================================================================

export interface CadastralRequest {
  coordinates: {
    lat: number;
    lon: number;
  };
}

export interface CadastralResponse {
  bonbun: string;
  bubun: string;
  jimok: string;
  area: number;
  success: boolean;
}

// ============================================================================
// STEP 4: Land Use
// ============================================================================

export interface LandUseRequest {
  coordinates: {
    lat: number;
    lon: number;
  };
  jimok: string;
}

export interface LandUseResponse {
  zone_type: string;
  zone_detail: string;
  bcr: number;
  far: number;
  land_use: string;
  regulations: string[];
  restrictions: string[];
  success: boolean;
}

// ============================================================================
// STEP 5: Road Information
// ============================================================================

export interface RoadInfoRequest {
  coordinates: {
    lat: number;
    lon: number;
  };
  radius?: number;
}

export interface RoadInfo {
  name: string;
  width: number;
  type: string;
  distance: number;
}

export interface RoadInfoResponse {
  nearby_roads: RoadInfo[];
  road_contact?: string;  // '접도', '맹지', '이격' etc. - optional for now, TODO: make required
  road_width: number;
  road_type: string;
  success: boolean;
}

// ============================================================================
// STEP 6: Market Data
// ============================================================================

export interface MarketDataRequest {
  coordinates: {
    lat: number;
    lon: number;
  };
  area: number;
  radius?: number;
}

export interface Transaction {
  date: string;
  area: number;
  amount: number;
  distance: number;
  address: string;
}

export interface MarketDataResponse {
  official_land_price: number;
  official_land_price_date: string;
  transactions: Transaction[];
  success: boolean;
}

// ============================================================================
// STEP 8: Freeze Context
// ============================================================================

export interface FreezeContextRequest {
  // STEP 1 data
  address: string;
  road_address: string;
  
  // STEP 2 data
  coordinates: {
    lat: number;
    lon: number;
  };
  sido: string;
  sigungu: string;
  dong: string;
  
  // STEP 3 data
  bonbun: string;
  bubun: string;
  jimok: string;
  area: number;
  
  // STEP 4 data
  zone_type: string;
  zone_detail: string;
  bcr: number;
  far: number;
  land_use: string;
  regulations: string[];
  restrictions: string[];
  
  // STEP 5 data
  road_width: number;
  road_type: string;
  
  // STEP 6 data (optional)
  official_land_price?: number;
  
  // Data sources tracking
  data_sources: Record<string, DataSourceInfo>;
}

export interface LandInfoContext {
  parcel_id: string;
  address: string;
  road_address?: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  location: {
    sido: string;
    sigungu: string;
    dong: string;
  };
  land: {
    area_sqm: number;
    area_pyeong: number;
    category: string;
    use: string;
  };
  zoning: {
    type: string;
    detail?: string;
    far: number;
    bcr: number;
  };
  terrain: {
    road_width: number;
    road_type: string;
    height: string;
    shape: string;
  };
  regulations: Record<string, any>;
  restrictions: string[];
  metadata: {
    source: string;
    date: string;
  };
}

export interface FreezeContextResponse {
  context_id: string;
  land_info_context: LandInfoContext;
  frozen: boolean;
  created_at: string;
  message: string;
}

// ============================================================================
// PDF Parsing
// ============================================================================

export interface PDFParseResponse {
  extracted: {
    bonbun?: string;
    bubun?: string;
    jimok?: string;
    area?: number;
  };
  confidence: {
    bonbun?: number;
    bubun?: number;
    jimok?: number;
    area?: number;
  };
  success: boolean;
  message: string;
}

// ============================================================================
// M1 State Management
// ============================================================================

export interface M1FormData {
  // STEP 1
  selectedAddress?: AddressSuggestion;
  
  // STEP 2
  geocodeData?: GeocodeResponse;
  manualCoordinates?: { lat: number; lon: number };
  
  // STEP 3
  cadastralData?: CadastralResponse;
  pdfExtractedData?: PDFParseResponse['extracted'];
  
  // STEP 4
  landUseData?: LandUseResponse;
  
  // STEP 5
  roadInfoData?: RoadInfoResponse;
  
  // STEP 6
  marketData?: MarketDataResponse;
  
  // Data sources
  dataSources: Record<string, DataSourceInfo>;
}

export interface M1State {
  currentStep: number;
  formData: M1FormData;
  loading: boolean;
  error: string | null;
  frozenContext?: FreezeContextResponse;
}

// ============================================================================
// Component Props
// ============================================================================

export interface ProgressBarProps {
  currentStep: number;
  totalSteps: number;
  stepLabels: string[];
}

export interface DataSourceBadgeProps {
  source: DataSource;
  apiName?: string;
  timestamp?: string;
  confidence?: number;
}

export interface MapViewerProps {
  coordinates: { lat: number; lon: number };
  layers?: string[];
  markers?: Array<{
    lat: number;
    lon: number;
    label: string;
  }>;
  onCoordinatesChange?: (coords: { lat: number; lon: number }) => void;
}

export interface PDFUploaderProps {
  onUpload: (file: File) => Promise<void>;
  onExtracted: (data: PDFParseResponse) => void;
  acceptedTypes?: string[];
  maxSize?: number;
  loading?: boolean;
}

// ============================================================================
// API Response Wrappers
// ============================================================================

export interface ApiError {
  detail: string;
  status?: number;
}

export type ApiResponse<T> = 
  | { success: true; data: T }
  | { success: false; error: ApiError };
