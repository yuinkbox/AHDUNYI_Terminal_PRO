import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },

  server: {
    host: true,
    port: 5173,
    open: false,
    cors: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    // Target modern Chromium — QtWebEngine ships a recent Blink version.
    target: 'chrome100',
    outDir: 'dist',
    // Relative asset paths so index.html works from any file:// location (exe packaging).
    assetsDir: 'assets',
    minify: 'esbuild',
    sourcemap: false,
    chunkSizeWarningLimit: 2000,
    rollupOptions: {
      output: {
        // Stable chunk names for better caching
        chunkFileNames:  'assets/js/[name]-[hash].js',
        entryFileNames:  'assets/js/[name]-[hash].js',
        assetFileNames:  'assets/[ext]/[name]-[hash].[ext]',
        // Split vendor chunks to reduce main bundle size
        manualChunks: {
          'vendor-vue':   ['vue', 'vue-router', 'pinia'],
          'vendor-arco':  ['@arco-design/web-vue'],
          'vendor-axios': ['axios'],
        },
      },
    },
  },

  // Ensure CSS is properly extracted for exe packaging
  css: {
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
      },
    },
  },
})
