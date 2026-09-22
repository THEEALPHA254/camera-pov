// Client-side image pipeline:
//   1. If HEIC/HEIF, convert to JPEG via heic2any (loaded lazily).
//   2. Decode with createImageBitmap({ imageOrientation: 'from-image' })
//      so EXIF rotation is applied for free.
//   3. Resize to <=2000px long edge and encode at 0.85 JPEG for `full`.
//   4. Resize to <=400px long edge and encode at 0.8 JPEG for `thumb`.
//
// Returns { fullBlob, thumbBlob, previewUrl }. Caller owns the previewUrl
// and must revoke it.

const MAX_FULL = 2000
const MAX_THUMB = 400
const QUALITY_FULL = 0.85
const QUALITY_THUMB = 0.8
const MAX_UPLOAD_BYTES = 4 * 1024 * 1024

function looksLikeHeic (file) {
  const type = (file.type || '').toLowerCase()
  const name = (file.name || '').toLowerCase()
  if (type === 'image/heic' || type === 'image/heif') return true
  if (name.endsWith('.heic') || name.endsWith('.heif')) return true
  return false
}

async function convertHeic (file) {
  const { default: heic2any } = await import('heic2any')
  const out = await heic2any({ blob: file, toType: 'image/jpeg', quality: 0.92 })
  const blob = Array.isArray(out) ? out[0] : out
  return new File([blob], (file.name || 'photo').replace(/\.\w+$/, '.jpg'), {
    type: 'image/jpeg',
  })
}

async function decode (file) {
  // Modern browsers honor EXIF orientation with this option.
  try {
    return await createImageBitmap(file, { imageOrientation: 'from-image' })
  } catch {
    // Older Safari: fall back to <img> which auto-orients by default in most
    // recent versions.
    const url = URL.createObjectURL(file)
    try {
      const img = new Image()
      img.decoding = 'async'
      await new Promise((resolve, reject) => {
        img.onload = resolve
        img.onerror = () => reject(new Error('decode failed'))
        img.src = url
      })
      return img
    } finally {
      // decode is done; caller uses bitmap; revoke via GC
      URL.revokeObjectURL(url)
    }
  }
}

function fitInside (w, h, max) {
  if (w <= max && h <= max) return { w, h }
  const scale = Math.min(max / w, max / h)
  return { w: Math.round(w * scale), h: Math.round(h * scale) }
}

async function toJpeg (source, maxEdge, quality) {
  const w0 = source.width || source.naturalWidth
  const h0 = source.height || source.naturalHeight
  const { w, h } = fitInside(w0, h0, maxEdge)
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')
  ctx.imageSmoothingQuality = 'high'
  ctx.drawImage(source, 0, 0, w, h)
  return await new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error('encode failed'))),
      'image/jpeg',
      quality,
    )
  })
}

export async function processImage (fileOrBlob) {
  let file = fileOrBlob
  if (looksLikeHeic(file)) {
    file = await convertHeic(file)
  }
  const source = await decode(file)
  const fullBlob = await toJpeg(source, MAX_FULL, QUALITY_FULL)
  const thumbBlob = await toJpeg(source, MAX_THUMB, QUALITY_THUMB)
  if (fullBlob.size > MAX_UPLOAD_BYTES) {
    throw new Error(
      'That photo is too large even after resizing. Try again with a smaller image.',
    )
  }
  const previewUrl = URL.createObjectURL(fullBlob)
  // free the decoded bitmap if it exposes close()
  if (typeof source.close === 'function') source.close()
  return { fullBlob, thumbBlob, previewUrl }
}
