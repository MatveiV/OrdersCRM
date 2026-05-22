import { defineConfig } from 'vite'

export default defineConfig({
  base: '/admin',
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://185.87.48.13',
        changeOrigin: true
      }
    }
  }
})
