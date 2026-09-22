import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router.js'
import { rememberEventCode } from './lib/api.js'
import './styles/global.css'

// Persist ?e=CODE (from the QR) once so it survives client-side navigation.
rememberEventCode()

// Warmup ping: fires against /api/upload while the user is still on the
// landing page, so the Python Lambda cold-starts now instead of when they
// hit SHARE. GET on /api/upload is a no-op that just triggers the imports.
// Fired via requestIdleCallback (or setTimeout as a fallback) so it doesn't
// contend with the first paint.
const warmup = () => { fetch('/api/upload', { method: 'GET', cache: 'no-store' }).catch(() => {}) }
if (typeof window !== 'undefined') {
  if ('requestIdleCallback' in window) window.requestIdleCallback(warmup, { timeout: 1500 })
  else setTimeout(warmup, 500)
}

createApp(App).use(router).mount('#app')
