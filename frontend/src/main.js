import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router.js'
import { rememberEventCode } from './lib/api.js'
import './styles/global.css'

// Persist ?e=CODE (from the QR) once so it survives client-side navigation.
rememberEventCode()

createApp(App).use(router).mount('#app')
