/**
 * useExecutionLock Hook
 * ======================
 * 🔒 FINAL EXECUTION LOCK for ZeroSite v6.5
 * 
 * Purpose: Prevent concurrent analysis executions
 * 
 * RULE 1: Only ONE analysis can run at a time
 * RULE 2: New address input blocked until current analysis completes
 * RULE 3: All M2~M6 must complete before showing results
 * 
 * Version: REAL APPRAISAL STANDARD v6.5 FINAL - EXECUTION LOCK
 * Date: 2025-12-29
 * Company: Antenna Holdings · Nataiheum
 */

import { useState, useCallback, useRef } from 'react';

export interface ExecutionLockState {
  isLocked: boolean;
  currentContextId: string | null;
  startTime: number | null;
  modulesCompleted: Set<string>;
}

export interface ExecutionLockHook {
  isLocked: boolean;
  currentContextId: string | null;
  progress: number;
  lockExecution: (contextId: string) => boolean;
  unlockExecution: () => void;
  markModuleComplete: (module: string) => void;
  canProceed: () => boolean;
  getElapsedTime: () => number;
}

const REQUIRED_MODULES = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6'];
const TIMEOUT_MS = 180 * 1000; // 180 seconds (3 minutes) timeout to allow pipeline completion

export const useExecutionLock = (): ExecutionLockHook => {
  const [lockState, setLockState] = useState<ExecutionLockState>({
    isLocked: false,
    currentContextId: null,
    startTime: null,
    modulesCompleted: new Set(),
  });

  const timeoutRef = useRef<number | null>(null);

  /**
   * 🔒 RULE 1: Lock execution for a new analysis
   * Returns: true if locked successfully, false if already locked
   */
  const lockExecution = useCallback((contextId: string): boolean => {
    if (lockState.isLocked) {
      console.warn('⚠️ EXECUTION LOCKED: Analysis already in progress');
      console.warn(`   Current Context: ${lockState.currentContextId}`);
      console.warn(`   Attempted Context: ${contextId}`);
      return false;
    }

    console.log('🔒 EXECUTION LOCK ACQUIRED:', contextId);
    setLockState({
      isLocked: true,
      currentContextId: contextId,
      startTime: Date.now(),
      modulesCompleted: new Set(),
    });

    // Safety timeout - auto-unlock after 180 seconds (3 minutes)
    timeoutRef.current = window.setTimeout(() => {
      console.error('⚠️ EXECUTION TIMEOUT: Auto-unlocking after 3 minutes');
      console.error('   Pipeline execution exceeded time limit. Releasing lock...');
      
      // Clear timeout ref
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      
      // Auto unlock
      setLockState({
        isLocked: false,
        currentContextId: null,
        startTime: null,
        modulesCompleted: new Set(),
      });
      
      // Show alert and reload
      alert('⚠️ 분석 시간 초과 (3분)\n\n파이프라인 실행이 3분을 초과했습니다.\n페이지를 새로고침 해주세요.');
      window.location.reload();
    }, TIMEOUT_MS);

    return true;
  }, [lockState.isLocked, lockState.currentContextId]);

  /**
   * 🔓 Unlock execution after analysis completes
   */
  const unlockExecution = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }

    console.log('🔓 EXECUTION LOCK RELEASED');
    setLockState({
      isLocked: false,
      currentContextId: null,
      startTime: null,
      modulesCompleted: new Set(),
    });
  }, []);

  /**
   * ✅ Mark a module as completed
   */
  const markModuleComplete = useCallback((module: string) => {
    setLockState((prev) => {
      const newCompleted = new Set(prev.modulesCompleted);
      newCompleted.add(module);
      
      console.log(`✅ Module ${module} completed (${newCompleted.size}/${REQUIRED_MODULES.length})`);
      
      return {
        ...prev,
        modulesCompleted: newCompleted,
      };
    });
  }, []);

  /**
   * 🚦 Check if all modules are complete and results can be shown
   */
  const canProceed = useCallback((): boolean => {
    const allComplete = REQUIRED_MODULES.every((m) => 
      lockState.modulesCompleted.has(m)
    );
    
    if (allComplete) {
      console.log('✅ ALL MODULES COMPLETE - Results can be displayed');
    }
    
    return allComplete;
  }, [lockState.modulesCompleted]);

  /**
   * ⏱️ Get elapsed time since lock acquired
   */
  const getElapsedTime = useCallback((): number => {
    if (!lockState.startTime) return 0;
    return Date.now() - lockState.startTime;
  }, [lockState.startTime]);

  /**
   * 📊 Calculate progress percentage
   */
  const progress = Math.round(
    (lockState.modulesCompleted.size / REQUIRED_MODULES.length) * 100
  );

  return {
    isLocked: lockState.isLocked,
    currentContextId: lockState.currentContextId,
    progress,
    lockExecution,
    unlockExecution,
    markModuleComplete,
    canProceed,
    getElapsedTime,
  };
};
