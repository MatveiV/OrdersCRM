import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://185.87.48.13',
        changeOrigin: true
      },
      '/admin': {
        target: 'http://185.87.48.13',
        changeOrigin: true
      }
    }
  }
})
