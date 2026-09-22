import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // during `npm run dev`, hit `vercel dev` on 3000 for /api routes
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    // heic2any is ~500KB; lazy-loaded in image.js so keep it in its own chunk
    rollupOptions: {
      output: {
        manualChunks: {
          heic2any: ['heic2any'],
        },
      },
    },
  },
})
