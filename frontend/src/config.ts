/**
 * Frontend Configuration
 * 
 * Centralized configuration for API endpoints
 */

// 🔥 CRITICAL: Hardcoded backend URL for sandbox environment
// This bypasses proxy issues in HTTPS sandbox
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 
  'https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai';

export const API_BASE_URL = `${BACKEND_URL}/api`;

console.log('🔧 Frontend Config Loaded:', {
  BACKEND_URL,
  API_BASE_URL,
  ENV_VAR: import.meta.env.VITE_BACKEND_URL,
});
