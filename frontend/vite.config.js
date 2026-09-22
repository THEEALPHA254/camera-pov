import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'node:path'

// Read env from the repo root (one level up from frontend/) so a single
// .env.local — and a single Vercel env-var config — feeds both the Python
// functions and the frontend build.
export default defineConfig(({ mode }) => {
  const rootDir = resolve(__dirname, '..')
  const fileEnv = loadEnv(mode, rootDir, '')
  const merged = { ...fileEnv, ...process.env }

  return {
    plugins: [vue()],
    define: {
      // Inlined at build time. Used by Landing / Success to link "View Gallery"
      // straight to the shared Drive folder. Empty string falls back to /gallery.
      __DRIVE_FOLDER_ID__: JSON.stringify(merged.DRIVE_FOLDER_ID || ''),
    },
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
  }
})
