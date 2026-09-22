// Small API client.
//
// EVENT_CODE is baked into the QR URL as `?e=CODE`. We keep it in
// sessionStorage after the first hit so the code survives navigating between
// routes without needing to keep the query string on every URL.

const EVENT_CODE_KEY = 'cap_event_code'

export function rememberEventCode () {
  const u = new URL(window.location.href)
  const code = u.searchParams.get('e')
  if (code) sessionStorage.setItem(EVENT_CODE_KEY, code)
}

function eventCode () {
  return sessionStorage.getItem(EVENT_CODE_KEY) || ''
}

function apiError (status, text) {
  try {
    const j = JSON.parse(text)
    return new Error(j.error || `HTTP ${status}`)
  } catch {
    return new Error(`HTTP ${status}`)
  }
}

export async function uploadPhoto ({ full, thumb, caption, capturedBy, onProgress }) {
  const fd = new FormData()
  fd.append('photo', full, 'photo.jpg')
  fd.append('thumb', thumb, 'thumb.jpg')
  fd.append('caption', caption || '')
  fd.append('captured_by', capturedBy || '')

  const codeParam = eventCode() ? `?e=${encodeURIComponent(eventCode())}` : ''

  return await new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `/api/upload${codeParam}`)
    xhr.responseType = 'text'
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try { resolve(JSON.parse(xhr.responseText)) }
        catch { resolve(null) }
      } else {
        reject(apiError(xhr.status, xhr.responseText))
      }
    }
    xhr.onerror = () => reject(new Error('Network error. Check your connection?'))
    xhr.send(fd)
  })
}

export async function listPhotos ({ before, limit = 24 } = {}) {
  const params = new URLSearchParams()
  params.set('limit', String(limit))
  if (before) params.set('before', before)
  const r = await fetch(`/api/photos?${params}`, { cache: 'no-store' })
  const text = await r.text()
  if (!r.ok) throw apiError(r.status, text)
  return JSON.parse(text)
}

export async function adminLogin (password) {
  const r = await fetch('/api/admin/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  })
  const text = await r.text()
  if (!r.ok) throw apiError(r.status, text)
  return JSON.parse(text)
}

export async function adminList ({ before, limit = 50 } = {}) {
  const params = new URLSearchParams()
  params.set('limit', String(limit))
  if (before) params.set('before', before)
  const r = await fetch(`/api/admin/photos?${params}`, { cache: 'no-store' })
  const text = await r.text()
  if (!r.ok) throw apiError(r.status, text)
  return JSON.parse(text)
}

export async function adminHide (id, hidden) {
  const r = await fetch('/api/admin/hide', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, hidden }),
  })
  const text = await r.text()
  if (!r.ok) throw apiError(r.status, text)
  return JSON.parse(text)
}

export async function adminDelete (id) {
  const r = await fetch('/api/admin/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id }),
  })
  const text = await r.text()
  if (!r.ok) throw apiError(r.status, text)
  return JSON.parse(text)
}
