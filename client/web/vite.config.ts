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
    open: true,
    cors: true,
  },

  build: {
    // Target modern Chromium - QtWebEngine ships a recent Blink version.
    target: 'chrome100',
    outDir: 'dist',
    // Use relative asset paths so index.html works from any file:// location.
    base: '',
    minify: 'esbuild',
    rollupOptions: {
      output: {
        chunkFileNames:  'assets/js/[name]-[hash].js',
        entryFileNames:  'assets/js/[name]-[hash].js',
        assetFileNames:  'assets/[ext]/[name]-[hash].[ext]',
      },
    },
  },
})
