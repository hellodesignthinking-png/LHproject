import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: false,
    hmr: {
      clientPort: 443,
      protocol: 'wss'
    },
    allowedHosts: [
      '.sandbox.novita.ai',
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      '.sandbox.e2b.dev'
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8091',
        changeOrigin: true,
        secure: false
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src'
    }
  }
})
