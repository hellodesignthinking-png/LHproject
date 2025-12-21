/**
 * Frontend Configuration
 * 
 * Centralized configuration for API endpoints
 */

// 🔥 CRITICAL: Hardcoded backend URL for sandbox environment
// This bypasses proxy issues in HTTPS sandbox
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 
  'https://8005-iytptjlm3wjktifqay52f-2b54fc91.sandbox.novita.ai';

export const API_BASE_URL = `${BACKEND_URL}/api`;

console.log('🔧 Frontend Config Loaded:', {
  BACKEND_URL,
  API_BASE_URL,
  ENV_VAR: import.meta.env.VITE_BACKEND_URL,
});
