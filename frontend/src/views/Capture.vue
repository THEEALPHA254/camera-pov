<template>
  <main class="capture">
    <header class="top">
      <RouterLink to="/" class="back">← Back</RouterLink>
    </header>

    <div class="inner">
      <h2 class="prompt">TAKE THE SHOT</h2>
      <div class="gold-rule" />
      <p class="hint">
        Tap the button below to open your camera.
        <br />You can also choose from your library.
      </p>

      <label class="picker">
        <span class="picker-face">
          <span class="picker-emoji">📸</span>
          <span>Open camera</span>
        </span>
        <input
          ref="camRef"
          type="file"
          accept="image/*,image/heic,image/heif"
          capture="environment"
          @change="onPick"
        />
      </label>

      <label class="picker ghost">
        <span class="picker-face">
          <span class="picker-emoji">🖼️</span>
          <span>Choose from library</span>
        </span>
        <input
          type="file"
          accept="image/*,image/heic,image/heif"
          @change="onPick"
        />
      </label>

      <p v-if="working" class="working">Processing photo…</p>
      <p v-if="err" class="err">{{ err }}</p>
    </div>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { processImage } from '../lib/image.js'
import { pendingPhoto } from '../router.js'

const router = useRouter()
const working = ref(false)
const err = ref('')

async function onPick (evt) {
  err.value = ''
  const file = evt.target.files?.[0]
  if (!file) return
  working.value = true
  try {
    const { fullBlob, thumbBlob, previewUrl } = await processImage(file)
    pendingPhoto.fullBlob = fullBlob
    pendingPhoto.thumbBlob = thumbBlob
    if (pendingPhoto.previewUrl) URL.revokeObjectURL(pendingPhoto.previewUrl)
    pendingPhoto.previewUrl = previewUrl
    pendingPhoto.originalName = file.name || ''
    router.push({ name: 'preview' })
  } catch (e) {
    err.value = e.message || 'Could not read that photo. Try a different one?'
  } finally {
    working.value = false
    // reset the input so picking the same file re-fires change
    evt.target.value = ''
  }
}
</script>

<style scoped>
.capture {
  min-height: 100dvh;
  background: #000;
  color: #fff;
  padding: 1.25rem 1.25rem 3rem;
}
.top {
  display: flex;
  align-items: center;
  min-height: 3rem;
}
.back {
  color: rgba(255, 255, 255, 0.72);
  text-decoration: none;
  font-size: 0.95rem;
}
.inner {
  max-width: 28rem;
  margin: 3rem auto 0;
  text-align: center;
}
.prompt {
  font-family: var(--serif);
  font-weight: 500;
  letter-spacing: 0.06em;
  font-size: clamp(1.8rem, 6vw, 2.2rem);
  margin: 0;
}
.gold-rule {
  width: 3rem;
  height: 2px;
  background: var(--gold);
  margin: 1.25rem auto 1.5rem;
}
.hint {
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.55;
  margin: 0 0 2.5rem;
}
.picker {
  display: block;
  margin: 0 0 1rem;
  cursor: pointer;
}
.picker input {
  display: none;
}
.picker-face {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  padding: 1.1rem;
  border-radius: 999px;
  background: var(--gold);
  color: #000;
  font-weight: 600;
  font-size: 1.02rem;
}
.picker.ghost .picker-face {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(212, 175, 55, 0.55);
}
.picker-emoji {
  font-size: 1.15rem;
}
.working,
.err {
  margin-top: 1.5rem;
  color: rgba(255, 255, 255, 0.8);
}
.err {
  color: #ff9b9b;
}
</style>
