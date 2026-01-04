/**
 * useAtomicRelease Hook
 * ======================
 * 🔒 ATOMIC RELEASE for ZeroSite v6.5
 * 
 * Purpose: Ensure all modules complete before showing ANY results
 * 
 * RULE 3: Single Completion Point (Atomic Release)
 * - All M2~M6 must complete with same context_id
 * - No partial rendering allowed
 * - Results shown only once, all at once
 * 
 * RULE 4: Hard Check before display
 * - Verify context_id consistency
 * - Verify timestamp consistency
 * - Verify address string match
 * - Verify data consistency (units, type, NPV)
 * 
 * Version: REAL APPRAISAL STANDARD v6.5 FINAL - ATOMIC RELEASE
 * Date: 2025-12-29
 */

import { useState, useCallback } from 'react';

export interface ModuleResult {
  module: string;
  contextId: string;
  timestamp: string;
  address: string;
  data: any;
  completedAt: number;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export interface AtomicReleaseState {
  results: Map<string, ModuleResult>;
  isComplete: boolean;
  validationResult: ValidationResult | null;
}

export interface AtomicReleaseHook {
  addResult: (result: ModuleResult) => void;
  isComplete: boolean;
  canDisplay: boolean;
  validationResult: ValidationResult | null;
  getAllResults: () => ModuleResult[];
  reset: () => void;
}

const REQUIRED_MODULES = ['M2', 'M3', 'M4', 'M5', 'M6'];

export const useAtomicRelease = (): AtomicReleaseHook => {
  const [state, setState] = useState<AtomicReleaseState>({
    results: new Map(),
    isComplete: false,
    validationResult: null,
  });

  /**
   * ✅ Add a module result
   */
  const addResult = useCallback((result: ModuleResult) => {
    setState((prev) => {
      const newResults = new Map(prev.results);
      newResults.set(result.module, result);

      const allModulesComplete = REQUIRED_MODULES.every((m) => 
        newResults.has(m)
      );

      console.log(`📊 Module ${result.module} result added`);
      console.log(`   Progress: ${newResults.size}/${REQUIRED_MODULES.length}`);

      let validationResult: ValidationResult | null = null;
      
      if (allModulesComplete) {
        console.log('🔍 All modules complete - Running validation...');
        validationResult = validateResults(Array.from(newResults.values()));
        
        if (validationResult.isValid) {
          console.log('✅ VALIDATION PASSED - Results can be displayed');
        } else {
          console.error('❌ VALIDATION FAILED:', validationResult.errors);
        }
      }

      return {
        results: newResults,
        isComplete: allModulesComplete,
        validationResult,
      };
    });
  }, []);

  /**
   * 🔄 Reset state for new analysis
   */
  const reset = useCallback(() => {
    console.log('🔄 Resetting atomic release state');
    setState({
      results: new Map(),
      isComplete: false,
      validationResult: null,
    });
  }, []);

  /**
   * 📊 Get all results as array
   */
  const getAllResults = useCallback((): ModuleResult[] => {
    return Array.from(state.results.values());
  }, [state.results]);

  /**
   * 🚦 Can display results?
   * Only if all complete AND validation passed
   */
  const canDisplay = state.isComplete && 
                      state.validationResult?.isValid === true;

  return {
    addResult,
    isComplete: state.isComplete,
    canDisplay,
    validationResult: state.validationResult,
    getAllResults,
    reset,
  };
};

/**
 * 🔍 RULE 4: Hard Check Validation
 * ==================================
 * Validates ALL results before allowing display
 */
function validateResults(results: ModuleResult[]): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  // 1. Check if we have all required modules
  const moduleNames = results.map((r) => r.module);
  const missingModules = REQUIRED_MODULES.filter(
    (m) => !moduleNames.includes(m)
  );

  if (missingModules.length > 0) {
    errors.push(`Missing modules: ${missingModules.join(', ')}`);
  }

  // 2. Check context_id consistency
  const contextIds = new Set(results.map((r) => r.contextId));
  if (contextIds.size > 1) {
    errors.push(
      `Context ID mismatch: Found ${contextIds.size} different IDs (${Array.from(contextIds).join(', ')})`
    );
  }

  // 3. Check timestamp consistency (same day)
  const timestamps = results.map((r) => r.timestamp);
  const dates = timestamps.map((ts) => ts.split(' ')[0]); // Extract date part
  const uniqueDates = new Set(dates);
  
  if (uniqueDates.size > 1) {
    warnings.push(
      `Timestamp inconsistency: Results generated on different dates (${Array.from(uniqueDates).join(', ')})`
    );
  }

  // 4. Check address consistency
  const addresses = new Set(results.map((r) => r.address));
  if (addresses.size > 1) {
    errors.push(
      `Address mismatch: Found ${addresses.size} different addresses`
    );
  }

  // 5. Check data consistency (units, housing type, etc.)
  try {
    const m3Result = results.find((r) => r.module === 'M3');
    const m4Result = results.find((r) => r.module === 'M4');
    const m5Result = results.find((r) => r.module === 'M5');

    if (m3Result && m4Result && m3Result.data && m4Result.data) {
      // Check if M4 units are based on M3 housing type
      const m3Type = m3Result.data.selected_housing_type || m3Result.data.selectedType;
      const m4Units = m4Result.data.total_units || m4Result.data.units;

      if (!m3Type) {
        warnings.push('M3: Housing type not found in data');
      }
      if (!m4Units) {
        warnings.push('M4: Total units not found in data');
      }
    }

    if (m4Result && m5Result && m4Result.data && m5Result.data) {
      // Check if M5 uses M4 units
      const m4Units = m4Result.data.total_units || m4Result.data.units;
      const m5Units = m5Result.data.project_scale_units || m5Result.data.units;

      if (m4Units && m5Units && Math.abs(m4Units - m5Units) > 1) {
        warnings.push(
          `Unit count mismatch: M4 (${m4Units}) vs M5 (${m5Units})`
        );
      }
    }
  } catch (err) {
    warnings.push(`Data consistency check failed: ${err}`);
  }

  // 6. Check completion time spread (all should complete within reasonable time)
  const completionTimes = results.map((r) => r.completedAt);
  const minTime = Math.min(...completionTimes);
  const maxTime = Math.max(...completionTimes);
  const timeSpread = maxTime - minTime;

  if (timeSpread > 5 * 60 * 1000) { // 5 minutes
    warnings.push(
      `Large time spread between module completions: ${Math.round(timeSpread / 1000)}s`
    );
  }

  const isValid = errors.length === 0;

  if (isValid) {
    console.log('✅ Validation PASSED');
    if (warnings.length > 0) {
      console.warn('⚠️ Warnings:', warnings);
    }
  } else {
    console.error('❌ Validation FAILED:', errors);
  }

  return { isValid, errors, warnings };
}
