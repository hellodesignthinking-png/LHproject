/**
 * ProgressBar Component
 * =====================
 * 
 * Displays 8-step progress indicator for M1 land information collection
 * 
 * Features:
 * - Desktop: Horizontal stepper with labels
 * - Mobile: Simplified numeric indicator (e.g., "2/8")
 * - Color coding: Green (completed), Blue (current), Gray (future)
 * 
 * Author: ZeroSite Frontend Team
 * Date: 2025-12-17
 */

import React from 'react';
import { ProgressBarProps } from '../../types/m1.types';
import './ProgressBar.css';

export const ProgressBar: React.FC<ProgressBarProps> = ({
  currentStep,
  totalSteps,
  stepLabels,
}) => {
  const steps = Array.from({ length: totalSteps }, (_, i) => i);

  return (
    <div className="progress-bar-container">
      {/* Mobile View */}
      <div className="progress-bar-mobile">
        <div className="progress-indicator">
          <span className="current-step">{currentStep}</span>
          <span className="separator">/</span>
          <span className="total-steps">{totalSteps}</span>
        </div>
        <div className="step-label-mobile">{stepLabels[currentStep]}</div>
      </div>

      {/* Desktop View */}
      <div className="progress-bar-desktop">
        <div className="steps-container">
          {steps.map((step) => {
            const isCompleted = step < currentStep;
            const isCurrent = step === currentStep;
            const status = isCompleted
              ? 'completed'
              : isCurrent
              ? 'current'
              : 'future';

            return (
              <React.Fragment key={step}>
                <div className={`step step-${status}`}>
                  <div className="step-circle">
                    {isCompleted ? (
                      <svg
                        width="16"
                        height="16"
                        viewBox="0 0 16 16"
                        fill="none"
                      >
                        <path
                          d="M13.3333 4L6 11.3333L2.66667 8"
                          stroke="white"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    ) : (
                      <span className="step-number">{step + 1}</span>
                    )}
                  </div>
                  <div className="step-label">{stepLabels[step]}</div>
                </div>
                {step < totalSteps - 1 && (
                  <div className={`step-connector connector-${status}`} />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${(currentStep / (totalSteps - 1)) * 100}%` }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;
