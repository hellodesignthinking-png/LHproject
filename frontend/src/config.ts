/**
 * Frontend Configuration
 * 
 * Centralized configuration for API endpoints
 */

// 🔥 CRITICAL FIX: Use relative URL for Vite proxy
// This avoids CORS issues by using Vite's built-in proxy
// Vite config has: proxy: { '/api': { target: 'http://localhost:8005' } }

const isDevelopment = import.meta.env.DEV;

// In development, use relative URL (Vite proxy)
// In production, use full URL from env or fallback
export const BACKEND_URL = isDevelopment 
  ? '' // Empty string means relative URL, which uses Vite proxy
  : (import.meta.env.VITE_BACKEND_URL || 'https://8005-iwm3znz7z15o7t0185x5u-b9b802c4.sandbox.novita.ai');

export const API_BASE_URL = `${BACKEND_URL}/api`;

console.log('🔧 Frontend Config Loaded:', {
  isDevelopment,
  BACKEND_URL: BACKEND_URL || '(using Vite proxy)',
  API_BASE_URL,
  ENV_VAR: import.meta.env.VITE_BACKEND_URL,
});
