<template>
  <main class="preview">
    <header class="top">
      <RouterLink to="/capture" class="back">← Retake</RouterLink>
    </header>
    <div class="inner" v-if="hasPhoto">
      <h2 class="prompt">LOOKS GOOD? <span class="emoji">😍</span></h2>
      <div class="gold-rule" />
      <div class="photo-frame">
        <img :src="pendingPhoto.previewUrl" alt="Your photo preview" />
      </div>
      <label class="field">
        <span>Caption (optional)</span>
        <input
          v-model="pendingPhoto.caption"
          type="text"
          maxlength="280"
          placeholder="Say something about this shot…"
        />
      </label>
      <label class="field">
        <span>Who captured this?</span>
        <input
          v-model="pendingPhoto.capturedBy"
          type="text"
          maxlength="60"
          placeholder="Your name (blank = Anonymous)"
        />
      </label>

      <div class="row">
        <button class="ghost" @click="retake">RETAKE</button>
        <button class="cta" :disabled="uploading" @click="share">
          {{ uploading ? uploadingLabel : 'SHARE 📤' }}
        </button>
      </div>

      <div v-if="uploading" class="progress">
        <div class="bar"><div :style="{ width: pct + '%' }"></div></div>
        <p class="hint">Uploading… {{ pct }}%</p>
      </div>
      <p v-if="err" class="err">
        {{ err }} <button class="linkish" @click="share">Try again</button>
      </p>
    </div>
    <div v-else class="inner empty">
      <p>No photo selected.</p>
      <RouterLink class="ghost" to="/capture">Snap one</RouterLink>
    </div>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { pendingPhoto } from '../router.js'
import { uploadPhoto } from '../lib/api.js'

const router = useRouter()

const hasPhoto = computed(() => !!pendingPhoto.previewUrl && !!pendingPhoto.fullBlob)
const uploading = ref(false)
const pct = ref(0)
const err = ref('')
const uploadingLabel = computed(() => (pct.value >= 100 ? 'FINISHING…' : `SENDING… ${pct.value}%`))

function retake () {
  router.replace({ name: 'capture' })
}

async function share () {
  if (uploading.value) return
  err.value = ''
  pct.value = 0
  uploading.value = true
  try {
    await uploadPhoto({
      full: pendingPhoto.fullBlob,
      thumb: pendingPhoto.thumbBlob,
      caption: pendingPhoto.caption,
      capturedBy: pendingPhoto.capturedBy,
      onProgress: (p) => (pct.value = p),
    })
    router.replace({ name: 'success' })
  } catch (e) {
    err.value = e.message || 'Upload failed.'
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.preview {
  min-height: 100dvh;
  background: #000;
  color: #fff;
  padding: 1.25rem 1.25rem 3rem;
}
.top {
  min-height: 3rem;
  display: flex;
  align-items: center;
}
.back {
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font-size: 0.95rem;
}
.inner {
  max-width: 30rem;
  margin: 1rem auto 0;
}
.inner.empty {
  text-align: center;
  padding-top: 4rem;
  color: rgba(255, 255, 255, 0.7);
}
.prompt {
  text-align: center;
  font-family: var(--serif);
  font-weight: 500;
  font-size: clamp(1.7rem, 6vw, 2.2rem);
  margin: 0;
}
.emoji {
  color: var(--gold);
}
.gold-rule {
  width: 3rem;
  height: 2px;
  background: var(--gold);
  margin: 1rem auto 1.5rem;
}
.photo-frame {
  border: 1px solid rgba(212, 175, 55, 0.4);
  border-radius: 14px;
  overflow: hidden;
  background: #0a0a0a;
  margin-bottom: 1.25rem;
}
.photo-frame img {
  display: block;
  width: 100%;
  height: auto;
  max-height: 60vh;
  object-fit: contain;
}
.field {
  display: block;
  margin: 0.9rem 0;
}
.field span {
  display: block;
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  margin-bottom: 0.35rem;
  text-transform: uppercase;
}
.field input {
  width: 100%;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(212, 175, 55, 0.3);
  color: #fff;
  font-size: 1rem;
  outline: none;
}
.field input:focus {
  border-color: var(--gold);
}
.row {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
.row button {
  flex: 1;
  padding: 1rem;
  border: none;
  border-radius: 999px;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  cursor: pointer;
}
.row .ghost {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(212, 175, 55, 0.55);
}
.row .cta {
  background: var(--gold);
  color: #000;
}
.row .cta:disabled {
  opacity: 0.75;
}
.progress {
  margin-top: 1.25rem;
}
.bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  overflow: hidden;
}
.bar > div {
  height: 100%;
  background: var(--gold);
  transition: width 0.15s ease-out;
}
.hint {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: 0.5rem 0 0;
}
.err {
  margin-top: 1.25rem;
  color: #ff9b9b;
}
.linkish {
  background: transparent;
  border: none;
  color: var(--gold);
  text-decoration: underline;
  padding: 0;
  cursor: pointer;
  font: inherit;
}
</style>
