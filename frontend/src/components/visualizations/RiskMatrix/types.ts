/**
 * Type definitions for Risk Matrix Component
 * Phase 4 - Day 1-2: Risk Matrix 5×5 Interactive Grid
 */

export interface Risk {
  id: string;              // "R01", "R02", etc.
  name: string;            // Korean: "재무 타당성 부족"
  name_en: string;         // English: "Financial Viability Risk"
  category: string;        // "financial", "legal", "market", "construction", "operational"
  category_kr: string;     // Korean: "재무/자금"
  probability: number;     // 1-5 scale
  impact: number;          // 1-5 scale
  risk_score: number;      // probability × impact
  risk_level: string;      // "CRITICAL", "HIGH", "MEDIUM", "LOW"
  risk_level_kr: string;   // Korean: "심각", "높음", "보통", "낮음"
  description: string;     // Detailed description in Korean
  response_strategies: string[];  // Array of 3 strategies
}

export interface RiskMatrixProps {
  risks: Risk[];
  onRiskClick?: (risk: Risk) => void;
  loading?: boolean;
  error?: string | null;
}

export interface RiskModalProps {
  risk: Risk | null;
  isOpen: boolean;
  onClose: () => void;
}

export interface RiskCellData {
  x: number;           // Probability (1-5)
  y: number;           // Impact (1-5)
  z: number;           // Risk score (for bubble size)
  risk: Risk;          // Full risk object
  fill: string;        // Color based on risk level
}

export enum RiskLevel {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW'
}

export enum RiskCategory {
  FINANCIAL = 'financial',
  LEGAL = 'legal',
  MARKET = 'market',
  CONSTRUCTION = 'construction',
  OPERATIONAL = 'operational'
}

export const RISK_COLORS = {
  CRITICAL: '#EF4444',  // Red
  HIGH: '#F97316',      // Orange
  MEDIUM: '#EAB308',    // Yellow
  LOW: '#22C55E'        // Green
} as const;

export const RISK_LEVEL_THRESHOLDS = {
  CRITICAL: 20,
  HIGH: 12,
  MEDIUM: 6,
  LOW: 0
} as const;

export const CATEGORY_COLORS = {
  financial: '#3B82F6',      // Blue
  legal: '#8B5CF6',          // Purple
  market: '#10B981',         // Emerald
  construction: '#F59E0B',   // Amber
  operational: '#6366F1'     // Indigo
} as const;
