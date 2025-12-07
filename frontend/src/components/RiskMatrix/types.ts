/**
 * Risk Matrix Component - Type Definitions
 * Phase 4: Frontend Visualization
 * 
 * Defines TypeScript interfaces for Risk Matrix 5×5 Interactive Grid
 */

export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type RiskCategory = 'financial' | 'construction' | 'legal' | 'market' | 'operational';

/**
 * Individual Risk Item
 * Represents a single risk in the matrix
 */
export interface Risk {
  id: string;                    // Unique identifier (e.g., "R01", "R02")
  name: string;                  // Risk name (Korean or English)
  category: RiskCategory;        // Risk category
  probability: number;           // Probability score (1-5)
  impact: number;                // Impact score (1-5)
  risk_score: number;            // Calculated: probability × impact
  risk_level: RiskLevel;         // Risk severity level
  description: string;           // Detailed description
  response_strategies: string[]; // Array of 3+ mitigation strategies
}

/**
 * Risk Matrix Cell
 * Represents a single cell in the 5×5 matrix
 */
export interface RiskMatrixCell {
  probability: number;           // X-axis: 1-5
  impact: number;                // Y-axis: 1-5
  risks: Risk[];                 // Risks in this cell
  count: number;                 // Number of risks
  level: RiskLevel;              // Cell risk level based on score
}

/**
 * Risk Matrix Data Structure
 * Complete data for rendering the matrix
 */
export interface RiskMatrixData {
  matrix: RiskMatrixCell[][];    // 5×5 grid of cells
  axis_labels: {
    x_label: string;             // X-axis label (e.g., "발생확률")
    y_label: string;             // Y-axis label (e.g., "영향도")
    x_values: string[];          // X-axis tick labels ["1", "2", "3", "4", "5"]
    y_values: string[];          // Y-axis tick labels ["1", "2", "3", "4", "5"]
  };
  risk_counts: {
    CRITICAL: number;
    HIGH: number;
    MEDIUM: number;
    LOW: number;
  };
  total_risks: number;
}

/**
 * Risk Matrix Props
 * Props for RiskMatrixGrid component
 */
export interface RiskMatrixProps {
  data: RiskMatrixData;
  width?: number;                // Optional fixed width
  height?: number;               // Optional fixed height
  onRiskClick?: (risk: Risk) => void; // Callback for risk click
  showLegend?: boolean;          // Show/hide legend
  className?: string;            // Additional CSS classes
}

/**
 * Risk Modal Props
 * Props for RiskModal component showing risk details
 */
export interface RiskModalProps {
  risk: Risk | null;             // Risk to display (null = closed)
  isOpen: boolean;               // Modal open/closed state
  onClose: () => void;           // Close callback
}

/**
 * Risk Level Configuration
 * Visual styling for each risk level
 */
export interface RiskLevelConfig {
  level: RiskLevel;
  color: string;                 // Primary color
  backgroundColor: string;       // Background color
  borderColor: string;          // Border color
  label: string;                 // Display label (Korean)
  emoji: string;                 // Visual emoji indicator
  threshold: {
    min: number;                 // Minimum score
    max: number;                 // Maximum score
  };
}

/**
 * Risk Matrix Theme Configuration
 */
export interface RiskMatrixTheme {
  cellSize: number;              // Cell width/height in pixels
  cellPadding: number;           // Cell internal padding
  fontSize: {
    axisLabel: number;           // Axis label font size
    cellCount: number;           // Cell count font size
    legend: number;              // Legend font size
  };
  colors: {
    gridLines: string;           // Grid line color
    axisText: string;            // Axis text color
    background: string;          // Background color
  };
  animation: {
    duration: number;            // Animation duration (ms)
    easing: string;              // Easing function
  };
}

/**
 * Helper function type for calculating risk level
 */
export type CalculateRiskLevel = (probability: number, impact: number) => RiskLevel;

/**
 * Helper function type for getting risk level config
 */
export type GetRiskLevelConfig = (level: RiskLevel) => RiskLevelConfig;
