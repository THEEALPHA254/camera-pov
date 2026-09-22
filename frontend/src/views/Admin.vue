<template>
  <main class="admin">
    <header class="top">
      <RouterLink to="/" class="back">← Home</RouterLink>
      <h1>Admin</h1>
      <span />
    </header>
    <div class="gold-rule" />

    <form v-if="!authed" class="login" @submit.prevent="login">
      <label class="field">
        <span>Password</span>
        <input v-model="pw" type="password" autocomplete="off" required />
      </label>
      <button class="cta" :disabled="busy">{{ busy ? '…' : 'Enter' }}</button>
      <p v-if="err" class="err">{{ err }}</p>
    </form>

    <div v-else class="list">
      <p v-if="err" class="err">{{ err }}</p>
      <div v-if="photos.length === 0 && !busy" class="empty">
        Nothing here yet.
      </div>
      <div class="row" v-for="p in photos" :key="p.id">
        <img :src="p.thumb_url" :alt="p.caption || 'photo'" />
        <div class="meta">
          <div class="who">{{ p.captured_by || 'Anonymous' }}</div>
          <div class="cap">{{ p.caption || '—' }}</div>
          <div class="when">{{ formatDate(p.created_at) }}</div>
          <div class="actions">
            <button @click="toggleHide(p)">
              {{ p.is_hidden ? 'Unhide' : 'Hide' }}
            </button>
            <button class="danger" @click="destroy(p)">Delete</button>
          </div>
        </div>
      </div>
      <button v-if="cursor" class="more" :disabled="busy" @click="loadMore">
        Load more
      </button>
    </div>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { adminList, adminLogin, adminHide, adminDelete } from '../lib/api.js'

const authed = ref(false)
const pw = ref('')
const busy = ref(false)
const err = ref('')
const photos = ref([])
const cursor = ref(null)

async function login () {
  err.value = ''
  busy.value = true
  try {
    await adminLogin(pw.value)
    authed.value = true
    pw.value = ''
    await refresh()
  } catch (e) {
    err.value = e.message || 'Login failed.'
  } finally {
    busy.value = false
  }
}

async function refresh () {
  busy.value = true
  err.value = ''
  try {
    const data = await adminList({})
    photos.value = data.photos
    cursor.value = data.next_cursor
  } catch (e) {
    err.value = e.message || 'Failed to load.'
    if (/401/.test(err.value)) authed.value = false
  } finally {
    busy.value = false
  }
}

async function loadMore () {
  if (!cursor.value) return
  busy.value = true
  try {
    const data = await adminList({ before: cursor.value })
    photos.value.push(...data.photos)
    cursor.value = data.next_cursor
  } catch (e) {
    err.value = e.message
  } finally {
    busy.value = false
  }
}

async function toggleHide (p) {
  try {
    await adminHide(p.id, !p.is_hidden)
    p.is_hidden = !p.is_hidden
  } catch (e) {
    err.value = e.message
  }
}

async function destroy (p) {
  if (!confirm('Delete this photo permanently?')) return
  try {
    await adminDelete(p.id)
    photos.value = photos.value.filter((x) => x.id !== p.id)
  } catch (e) {
    err.value = e.message
  }
}

function formatDate (iso) {
  try {
    const d = new Date(iso)
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    })
  } catch { return iso }
}

onMounted(async () => {
  try {
    await refresh()
    authed.value = true
  } catch { /* not logged in */ }
})
</script>

<style scoped>
.admin {
  min-height: 100dvh;
  background: #000;
  color: #fff;
  padding: 1rem 1rem 4rem;
}
.top {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
}
.top h1 {
  font-family: var(--serif);
  font-weight: 500;
  letter-spacing: 0.06em;
  color: var(--gold);
  margin: 0;
}
.back {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
}
.gold-rule {
  height: 1px;
  background: linear-gradient(
    90deg, transparent, rgba(212, 175, 55, 0.5), transparent
  );
  margin: 1rem 0 1.5rem;
}
.login {
  max-width: 22rem;
  margin: 3rem auto 0;
}
.field { margin-bottom: 1rem; }
.field span {
  display: block;
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  margin-bottom: 0.35rem;
  text-transform: uppercase;
}
.field input {
  width: 100%;
  padding: 0.9rem 1rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(212, 175, 55, 0.4);
  color: #fff;
  border-radius: 12px;
  font-size: 1rem;
}
.cta {
  width: 100%;
  padding: 1rem;
  background: var(--gold);
  color: #000;
  border: none;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
}
.list { display: flex; flex-direction: column; gap: 0.75rem; }
.row {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: 0.75rem;
  padding: 0.5rem;
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.02);
}
.row img {
  width: 88px;
  height: 88px;
  object-fit: cover;
  border-radius: 8px;
}
.meta { min-width: 0; }
.who { font-weight: 600; }
.cap {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.when { color: rgba(255, 255, 255, 0.5); font-size: 0.78rem; margin: 0.2rem 0 0.4rem; }
.actions { display: flex; gap: 0.5rem; }
.actions button {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(212, 175, 55, 0.5);
  border-radius: 999px;
  padding: 0.35rem 0.8rem;
  font-size: 0.85rem;
  cursor: pointer;
}
.actions .danger {
  border-color: #ff9b9b;
  color: #ff9b9b;
}
.more {
  margin: 1.5rem auto 0;
  background: transparent;
  color: var(--gold);
  border: 1px solid rgba(212, 175, 55, 0.4);
  border-radius: 999px;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
}
.err { color: #ff9b9b; }
.empty { color: rgba(255, 255, 255, 0.6); text-align: center; padding: 2rem 0; }
</style>
