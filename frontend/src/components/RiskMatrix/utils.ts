/**
 * Risk Matrix Component - Utility Functions
 * Phase 4: Frontend Visualization
 * 
 * Helper functions for risk calculations and styling
 */

import { RiskLevel, RiskLevelConfig, CalculateRiskLevel, GetRiskLevelConfig } from './types';

/**
 * Risk Level Configurations
 * Defines visual styling and thresholds for each risk level
 */
export const RISK_LEVEL_CONFIGS: RiskLevelConfig[] = [
  {
    level: 'CRITICAL',
    color: '#DC2626',           // Red-600
    backgroundColor: '#FEE2E2', // Red-100
    borderColor: '#991B1B',     // Red-800
    label: '매우 높음',
    emoji: '🔴',
    threshold: { min: 20, max: 25 }
  },
  {
    level: 'HIGH',
    color: '#EA580C',           // Orange-600
    backgroundColor: '#FFEDD5', // Orange-100
    borderColor: '#9A3412',     // Orange-800
    label: '높음',
    emoji: '🟠',
    threshold: { min: 12, max: 19 }
  },
  {
    level: 'MEDIUM',
    color: '#CA8A04',           // Yellow-600
    backgroundColor: '#FEF9C3', // Yellow-100
    borderColor: '#713F12',     // Yellow-800
    label: '보통',
    emoji: '🟡',
    threshold: { min: 6, max: 11 }
  },
  {
    level: 'LOW',
    color: '#16A34A',           // Green-600
    backgroundColor: '#DCFCE7', // Green-100
    borderColor: '#14532D',     // Green-800
    label: '낮음',
    emoji: '🟢',
    threshold: { min: 1, max: 5 }
  }
];

/**
 * Calculate risk level based on probability and impact scores
 * 
 * Score Thresholds:
 * - CRITICAL: 20-25 (5×5, 5×4, 4×5)
 * - HIGH: 12-19 (4×4, 5×3, 3×5, 4×3, 3×4)
 * - MEDIUM: 6-11 (3×3, 3×2, 2×3, 4×2, 2×4, 5×1, 1×5)
 * - LOW: 1-5 (2×2, 2×1, 1×2, 1×1)
 * 
 * @param probability - Probability score (1-5)
 * @param impact - Impact score (1-5)
 * @returns Risk level
 */
export const calculateRiskLevel: CalculateRiskLevel = (probability: number, impact: number): RiskLevel => {
  const score = probability * impact;
  
  if (score >= 20) return 'CRITICAL';
  if (score >= 12) return 'HIGH';
  if (score >= 6) return 'MEDIUM';
  return 'LOW';
};

/**
 * Get risk level configuration by level
 * 
 * @param level - Risk level
 * @returns Risk level configuration
 */
export const getRiskLevelConfig: GetRiskLevelConfig = (level: RiskLevel): RiskLevelConfig => {
  const config = RISK_LEVEL_CONFIGS.find(c => c.level === level);
  if (!config) {
    throw new Error(`Invalid risk level: ${level}`);
  }
  return config;
};

/**
 * Get risk level by score
 * 
 * @param score - Risk score (probability × impact)
 * @returns Risk level
 */
export const getRiskLevelByScore = (score: number): RiskLevel => {
  if (score >= 20) return 'CRITICAL';
  if (score >= 12) return 'HIGH';
  if (score >= 6) return 'MEDIUM';
  return 'LOW';
};

/**
 * Get cell background color based on risk level
 * 
 * @param level - Risk level
 * @returns Background color (hex)
 */
export const getCellBackgroundColor = (level: RiskLevel): string => {
  const config = getRiskLevelConfig(level);
  return config.backgroundColor;
};

/**
 * Get cell border color based on risk level
 * 
 * @param level - Risk level
 * @returns Border color (hex)
 */
export const getCellBorderColor = (level: RiskLevel): string => {
  const config = getRiskLevelConfig(level);
  return config.borderColor;
};

/**
 * Get cell text color based on risk level
 * 
 * @param level - Risk level
 * @returns Text color (hex)
 */
export const getCellTextColor = (level: RiskLevel): string => {
  const config = getRiskLevelConfig(level);
  return config.color;
};

/**
 * Format risk count for display in cell
 * 
 * @param count - Number of risks
 * @returns Formatted string
 */
export const formatRiskCount = (count: number): string => {
  if (count === 0) return '';
  if (count === 1) return '1';
  return `${count}`;
};

/**
 * Get cell tooltip text
 * 
 * @param probability - Probability score (1-5)
 * @param impact - Impact score (1-5)
 * @param count - Number of risks in cell
 * @param level - Risk level
 * @returns Tooltip text
 */
export const getCellTooltip = (
  probability: number,
  impact: number,
  count: number,
  level: RiskLevel
): string => {
  const config = getRiskLevelConfig(level);
  const score = probability * impact;
  
  if (count === 0) {
    return `확률: ${probability}, 영향도: ${impact}\n위험도: ${score} (${config.label})\n리스크: 없음`;
  }
  
  return `확률: ${probability}, 영향도: ${impact}\n위험도: ${score} (${config.label})\n리스크: ${count}개`;
};

/**
 * Sort risks by score (descending)
 * 
 * @param risks - Array of risks
 * @returns Sorted array
 */
export const sortRisksByScore = <T extends { risk_score: number }>(risks: T[]): T[] => {
  return [...risks].sort((a, b) => b.risk_score - a.risk_score);
};

/**
 * Group risks by level
 * 
 * @param risks - Array of risks
 * @returns Object mapping level to risks
 */
export const groupRisksByLevel = <T extends { risk_level: RiskLevel }>(
  risks: T[]
): Record<RiskLevel, T[]> => {
  const groups: Record<RiskLevel, T[]> = {
    CRITICAL: [],
    HIGH: [],
    MEDIUM: [],
    LOW: []
  };
  
  risks.forEach(risk => {
    groups[risk.risk_level].push(risk);
  });
  
  return groups;
};

/**
 * Calculate matrix statistics
 * 
 * @param risks - Array of all risks
 * @returns Statistics object
 */
export const calculateMatrixStats = <T extends { risk_level: RiskLevel; risk_score: number }>(
  risks: T[]
) => {
  const grouped = groupRisksByLevel(risks);
  const sorted = sortRisksByScore(risks);
  
  return {
    total: risks.length,
    by_level: {
      CRITICAL: grouped.CRITICAL.length,
      HIGH: grouped.HIGH.length,
      MEDIUM: grouped.MEDIUM.length,
      LOW: grouped.LOW.length
    },
    highest_risk: sorted[0] || null,
    average_score: risks.length > 0 
      ? risks.reduce((sum, r) => sum + r.risk_score, 0) / risks.length 
      : 0
  };
};

/**
 * Validate risk data
 * 
 * @param risk - Risk object to validate
 * @returns true if valid, false otherwise
 */
export const isValidRisk = (risk: any): boolean => {
  return (
    typeof risk.id === 'string' &&
    typeof risk.name === 'string' &&
    typeof risk.probability === 'number' &&
    risk.probability >= 1 && risk.probability <= 5 &&
    typeof risk.impact === 'number' &&
    risk.impact >= 1 && risk.impact <= 5 &&
    typeof risk.risk_score === 'number' &&
    typeof risk.risk_level === 'string' &&
    ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].includes(risk.risk_level)
  );
};

/**
 * Generate empty matrix data (for loading states)
 * 
 * @returns Empty matrix data structure
 */
export const generateEmptyMatrix = () => {
  const matrix = [];
  for (let impact = 5; impact >= 1; impact--) {
    const row = [];
    for (let probability = 1; probability <= 5; probability++) {
      const level = calculateRiskLevel(probability, impact);
      row.push({
        probability,
        impact,
        risks: [],
        count: 0,
        level
      });
    }
    matrix.push(row);
  }
  
  return {
    matrix,
    axis_labels: {
      x_label: '발생확률',
      y_label: '영향도',
      x_values: ['1', '2', '3', '4', '5'],
      y_values: ['5', '4', '3', '2', '1']
    },
    risk_counts: {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0
    },
    total_risks: 0
  };
};
