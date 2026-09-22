<template>
  <main class="gallery">
    <header class="top">
      <RouterLink to="/" class="back">← Home</RouterLink>
      <h1>Gallery</h1>
      <RouterLink to="/capture" class="add" aria-label="Add photo">＋</RouterLink>
    </header>
    <div class="gold-rule" />
    <div v-if="err" class="err">{{ err }}</div>
    <div v-if="!loading && photos.length === 0" class="empty">
      <p>No photos yet — be the first to capture the moment.</p>
      <RouterLink to="/capture" class="cta">📸 SNAP IT</RouterLink>
    </div>
    <div class="grid">
      <button
        v-for="(p, i) in photos"
        :key="p.id"
        class="tile"
        @click="open(i)"
      >
        <img :src="p.thumb_url" :alt="p.caption || 'photo'" loading="lazy" />
      </button>
    </div>
    <p v-if="loading" class="loading">Loading…</p>
    <Lightbox
      v-if="lightboxIndex !== null"
      :photos="photos"
      :start-index="lightboxIndex"
      @close="lightboxIndex = null"
      @request-more="loadMore"
    />
  </main>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { listPhotos } from '../lib/api.js'
import Lightbox from '../components/Lightbox.vue'

const photos = ref([])
const nextCursor = ref(null)
const loading = ref(false)
const err = ref('')
const lightboxIndex = ref(null)
let pollTimer = null
let scrollListener = null

async function loadInitial () {
  loading.value = true
  err.value = ''
  try {
    const data = await listPhotos({})
    photos.value = data.photos
    nextCursor.value = data.next_cursor
  } catch (e) {
    err.value = e.message || 'Could not load photos.'
  } finally {
    loading.value = false
  }
}

async function loadMore () {
  if (!nextCursor.value || loading.value) return
  loading.value = true
  try {
    const data = await listPhotos({ before: nextCursor.value })
    photos.value.push(...data.photos)
    nextCursor.value = data.next_cursor
  } catch (e) {
    err.value = e.message || 'Could not load more.'
  } finally {
    loading.value = false
  }
}

async function pollNew () {
  try {
    const data = await listPhotos({})
    const known = new Set(photos.value.map((p) => p.id))
    const fresh = data.photos.filter((p) => !known.has(p.id))
    if (fresh.length) {
      photos.value = [...fresh, ...photos.value]
    }
  } catch { /* silent — will retry */ }
}

function open (idx) {
  lightboxIndex.value = idx
}

function onScroll () {
  const doc = document.documentElement
  const near = doc.scrollTop + window.innerHeight >= doc.scrollHeight - 400
  if (near) loadMore()
}

onMounted(async () => {
  await loadInitial()
  pollTimer = setInterval(pollNew, 15000)
  scrollListener = onScroll
  window.addEventListener('scroll', scrollListener, { passive: true })
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (scrollListener) window.removeEventListener('scroll', scrollListener)
})
</script>

<style scoped>
.gallery {
  min-height: 100dvh;
  background: #000;
  color: #fff;
  padding: 1rem 1rem 4rem;
}
.top {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
}
.top h1 {
  font-family: var(--serif);
  font-weight: 500;
  letter-spacing: 0.06em;
  font-size: 1.4rem;
  margin: 0;
  color: var(--gold);
}
.back {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  justify-self: start;
}
.add {
  justify-self: end;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 999px;
  border: 1px solid rgba(212, 175, 55, 0.5);
  color: var(--gold);
  display: grid;
  place-items: center;
  text-decoration: none;
  font-size: 1.4rem;
}
.gold-rule {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(212, 175, 55, 0.5),
    transparent
  );
  margin: 1rem 0 1.25rem;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(9rem, 1fr));
  gap: 4px;
}
.tile {
  background: #111;
  border: none;
  padding: 0;
  aspect-ratio: 1 / 1;
  overflow: hidden;
  border-radius: 4px;
  cursor: pointer;
}
.tile img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.loading {
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
  margin: 2rem 0 0;
}
.err {
  color: #ff9b9b;
  text-align: center;
  margin: 1rem 0;
}
.empty {
  text-align: center;
  padding: 3rem 1rem;
  color: rgba(255, 255, 255, 0.75);
}
.empty .cta {
  display: inline-block;
  margin-top: 1.25rem;
  padding: 0.9rem 1.5rem;
  background: var(--gold);
  color: #000;
  border-radius: 999px;
  text-decoration: none;
  font-weight: 600;
}
</style>
