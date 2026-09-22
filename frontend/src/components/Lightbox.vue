<template>
  <div class="lightbox" @click.self="close">
    <button class="close" @click="close" aria-label="Close">✕</button>
    <button
      v-if="idx > 0"
      class="nav prev"
      @click="prev"
      aria-label="Previous"
    >‹</button>
    <button
      v-if="idx < photos.length - 1"
      class="nav next"
      @click="next"
      aria-label="Next"
    >›</button>

    <figure
      class="stage"
      @touchstart="onTouchStart"
      @touchend="onTouchEnd"
    >
      <img :src="current.full_url" :alt="current.caption || 'photo'" />
      <figcaption>
        <p class="cap" v-if="current.caption">{{ current.caption }}</p>
        <p class="by">
          Captured by {{ current.captured_by || 'Anonymous' }}
          · {{ formatTime(current.created_at) }}
        </p>
      </figcaption>
    </figure>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  photos: { type: Array, required: true },
  startIndex: { type: Number, required: true },
})
const emit = defineEmits(['close', 'request-more'])

const idx = ref(props.startIndex)
const current = computed(() => props.photos[idx.value] || {})

let touchStartX = 0
let touchStartY = 0

function close () { emit('close') }
function prev () { if (idx.value > 0) idx.value-- }
function next () {
  if (idx.value < props.photos.length - 1) {
    idx.value++
    if (idx.value >= props.photos.length - 3) emit('request-more')
  }
}
function onKey (e) {
  if (e.key === 'ArrowLeft') prev()
  else if (e.key === 'ArrowRight') next()
  else if (e.key === 'Escape') close()
}
function onTouchStart (e) {
  const t = e.changedTouches[0]
  touchStartX = t.clientX
  touchStartY = t.clientY
}
function onTouchEnd (e) {
  const t = e.changedTouches[0]
  const dx = t.clientX - touchStartX
  const dy = t.clientY - touchStartY
  if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {
    dx > 0 ? prev() : next()
  }
}
function formatTime (iso) {
  try {
    return new Date(iso).toLocaleTimeString(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    })
  } catch { return iso }
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
watch(() => props.photos.length, () => {
  if (idx.value >= props.photos.length) idx.value = props.photos.length - 1
})
</script>

<style scoped>
.lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.94);
  z-index: 50;
  display: grid;
  place-items: center;
  padding: env(safe-area-inset-top) 1rem env(safe-area-inset-bottom);
}
.stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  max-height: 90dvh;
  max-width: 100%;
  margin: 0;
}
.stage img {
  max-height: 78dvh;
  max-width: 100%;
  object-fit: contain;
  border-radius: 8px;
  background: #111;
}
figcaption {
  color: #fff;
  text-align: center;
  padding: 0 1rem;
  max-width: 32rem;
}
.cap {
  margin: 0 0 0.4rem;
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
}
.by {
  margin: 0;
  color: rgba(255, 255, 255, 0.55);
  font-size: 0.85rem;
  letter-spacing: 0.04em;
}
.close {
  position: absolute;
  top: max(1rem, env(safe-area-inset-top));
  right: 1rem;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  border: 1px solid rgba(212, 175, 55, 0.5);
  color: var(--gold);
  background: transparent;
  font-size: 1.1rem;
  cursor: pointer;
}
.nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 3rem;
  height: 3rem;
  border-radius: 999px;
  border: 1px solid rgba(212, 175, 55, 0.4);
  color: var(--gold);
  background: rgba(0, 0, 0, 0.4);
  font-size: 1.9rem;
  line-height: 1;
  cursor: pointer;
  display: none;
}
.nav.prev { left: 0.75rem; }
.nav.next { right: 0.75rem; }

@media (hover: hover) {
  .nav { display: block; }
}
</style>
