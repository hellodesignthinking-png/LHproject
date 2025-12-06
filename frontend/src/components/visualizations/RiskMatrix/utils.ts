/**
 * Utility functions for Risk Matrix Component
 */

import { Risk, RiskCellData, RISK_COLORS, RISK_LEVEL_THRESHOLDS } from './types';

/**
 * Get color for a risk based on its score
 */
export const getRiskColor = (score: number): string => {
  if (score >= RISK_LEVEL_THRESHOLDS.CRITICAL) return RISK_COLORS.CRITICAL;
  if (score >= RISK_LEVEL_THRESHOLDS.HIGH) return RISK_COLORS.HIGH;
  if (score >= RISK_LEVEL_THRESHOLDS.MEDIUM) return RISK_COLORS.MEDIUM;
  return RISK_COLORS.LOW;
};

/**
 * Get risk level from score
 */
export const getRiskLevel = (score: number): string => {
  if (score >= RISK_LEVEL_THRESHOLDS.CRITICAL) return 'CRITICAL';
  if (score >= RISK_LEVEL_THRESHOLDS.HIGH) return 'HIGH';
  if (score >= RISK_LEVEL_THRESHOLDS.MEDIUM) return 'MEDIUM';
  return 'LOW';
};

/**
 * Transform risks array to scatter chart data
 */
export const transformRisksToChartData = (risks: Risk[]): RiskCellData[] => {
  return risks.map(risk => ({
    x: risk.probability,
    y: risk.impact,
    z: risk.risk_score,
    risk: risk,
    fill: getRiskColor(risk.risk_score)
  }));
};

/**
 * Calculate matrix cell background color based on position
 * For the background grid (not the actual risks)
 */
export const getMatrixCellColor = (probability: number, impact: number): string => {
  const score = probability * impact;
  return getRiskColor(score);
};

/**
 * Get opacity for matrix cell background
 */
export const getMatrixCellOpacity = (probability: number, impact: number): number => {
  const score = probability * impact;
  // Higher risk = higher opacity
  if (score >= 20) return 0.15;
  if (score >= 12) return 0.12;
  if (score >= 6) return 0.08;
  return 0.05;
};

/**
 * Format risk score for display
 */
export const formatRiskScore = (score: number): string => {
  return score.toFixed(0);
};

/**
 * Get emoji for risk level
 */
export const getRiskEmoji = (level: string): string => {
  const emojiMap: Record<string, string> = {
    'CRITICAL': '🔴',
    'HIGH': '🟠',
    'MEDIUM': '🟡',
    'LOW': '🟢'
  };
  return emojiMap[level] || '⚪';
};

/**
 * Sort risks by score (highest first)
 */
export const sortRisksByScore = (risks: Risk[]): Risk[] => {
  return [...risks].sort((a, b) => b.risk_score - a.risk_score);
};

/**
 * Group risks by level
 */
export const groupRisksByLevel = (risks: Risk[]): Record<string, Risk[]> => {
  return risks.reduce((acc, risk) => {
    const level = risk.risk_level;
    if (!acc[level]) {
      acc[level] = [];
    }
    acc[level].push(risk);
    return acc;
  }, {} as Record<string, Risk[]>);
};

/**
 * Calculate risk distribution
 */
export const calculateRiskDistribution = (risks: Risk[]): Record<string, number> => {
  const grouped = groupRisksByLevel(risks);
  return {
    critical: grouped['CRITICAL']?.length || 0,
    high: grouped['HIGH']?.length || 0,
    medium: grouped['MEDIUM']?.length || 0,
    low: grouped['LOW']?.length || 0,
    total: risks.length
  };
};

/**
 * Get risk statistics
 */
export const getRiskStatistics = (risks: Risk[]) => {
  const scores = risks.map(r => r.risk_score);
  const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
  const maxScore = Math.max(...scores);
  const minScore = Math.min(...scores);
  
  return {
    average: avgScore,
    max: maxScore,
    min: minScore,
    total: risks.length,
    distribution: calculateRiskDistribution(risks)
  };
};
