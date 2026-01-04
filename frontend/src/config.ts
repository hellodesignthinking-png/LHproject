/**
 * Frontend Configuration
 * 
 * Centralized configuration for API endpoints
 */

// 🔥 CRITICAL: Hardcoded backend URL for sandbox environment
// This bypasses proxy issues in HTTPS sandbox
export const BACKEND_URL = 'https://49999-ix27pwgxgiz4rqbhpf92x-a402f90a.sandbox.novita.ai';

export const API_BASE_URL = `${BACKEND_URL}/api`;

console.log('🔧 Frontend Config Loaded:', {
  BACKEND_URL,
  API_BASE_URL,
});
