import { createRouter, createWebHistory } from 'vue-router'

import Landing from './views/Landing.vue'
import Capture from './views/Capture.vue'
import Preview from './views/Preview.vue'
import Success from './views/Success.vue'
import Gallery from './views/Gallery.vue'
import Admin from './views/Admin.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'landing', component: Landing },
    { path: '/capture', name: 'capture', component: Capture },
    { path: '/preview', name: 'preview', component: Preview },
    { path: '/success', name: 'success', component: Success },
    { path: '/gallery', name: 'gallery', component: Gallery },
    { path: '/admin', name: 'admin', component: Admin },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

// A tiny in-memory store for the currently pending photo (blob + form
// fields), used to hand off from Capture -> Preview -> Success without
// re-reading the file from disk. Kept here so it survives route changes
// but not full reloads.
export const pendingPhoto = {
  fullBlob: null,
  thumbBlob: null,
  previewUrl: null,
  originalName: '',
  caption: '',
  capturedBy: '',
}

export function clearPending() {
  if (pendingPhoto.previewUrl) URL.revokeObjectURL(pendingPhoto.previewUrl)
  pendingPhoto.fullBlob = null
  pendingPhoto.thumbBlob = null
  pendingPhoto.previewUrl = null
  pendingPhoto.originalName = ''
  pendingPhoto.caption = ''
  pendingPhoto.capturedBy = ''
}
