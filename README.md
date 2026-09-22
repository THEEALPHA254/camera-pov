# Capture the Moment

A mobile-first web app for guests to snap photos with their phones and share them to a live gallery, built for **Grace's Graduation**. Guests scan a branded QR code and upload directly from their camera — no login required.

- **Frontend:** Vue 3 + Vite (Composition API, hand-written CSS)
- **Backend:** Vercel Python serverless functions (`api/*.py`)
- **Storage:** Google Drive (server-side, private folder, OAuth refresh token)
- **Database:** Supabase (Postgres, service-role from functions only, RLS blocks browsers)
- **Hosting:** Vercel Hobby (free)

---

## Repo layout

```
api/                  # Vercel Python functions (each file = one endpoint)
  _lib/               # shared modules (Drive, DB, auth, EXIF, ...)
  admin/              # /api/admin/{login,photos,hide,delete}
  image/[id].py       # /api/image/<id>?size=thumb|full  (CDN-cached proxy)
  photos.py           # /api/photos
  upload.py           # /api/upload
  requirements.txt
frontend/             # Vue 3 + Vite app (deployed as static assets)
scripts/
  get_refresh_token.py  # one-time helper to obtain a Google Drive refresh token
  generate_qr.py        # branded print-ready QR code (PNG + SVG)
supabase/schema.sql   # run once in the Supabase SQL editor
vercel.json           # SPA rewrites + Python runtime
```

---

## First-time setup

### 1. Google Cloud project + Drive OAuth

1. Go to <https://console.cloud.google.com/> and create a new project (any name).
2. **Enable APIs → Google Drive API**.
3. **APIs & Services → OAuth consent screen**:
   - User type: **External**.
   - Add your Gmail address (the one whose Drive will store the photos) as a **test user**.
   - Scopes: add `.../auth/drive.file`.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**:
   - Application type: **Desktop app**.
   - Copy the **Client ID** and **Client secret**.
5. Get a refresh token by running the one-time helper:

   ```bash
   pip install google-auth-oauthlib
   export GOOGLE_CLIENT_ID=...  GOOGLE_CLIENT_SECRET=...
   python scripts/get_refresh_token.py
   ```

   It opens a browser, you sign in as your Drive account, and the refresh token is printed. Copy it as `GOOGLE_REFRESH_TOKEN`.
6. In your Drive, create a folder (e.g. `Capture the Moment`). Open it and copy the ID from the URL (`drive.google.com/drive/folders/<THIS>`) → `DRIVE_FOLDER_ID`. The app uses the `drive.file` scope, so it can only touch files it creates inside this folder; everything else in your Drive is invisible to it.
7. **Share the folder** so guests can view it: right-click the folder → **Share** → **General access → "Anyone with the link" → Viewer**. The "View Gallery" button on the landing page opens this folder directly, so if it's still restricted your guests will hit Google's "Request access" screen.

### 2. Supabase project

1. Create a project at <https://supabase.com/>.
2. **SQL editor** → paste `supabase/schema.sql` → run.
3. **Project settings → API**:
   - `SUPABASE_URL` = the Project URL.
   - `SUPABASE_SERVICE_ROLE_KEY` = the **service_role** key (never expose to the browser).
4. RLS is enabled with no anon policies, so browsers using the anon key see nothing — only our Vercel functions (using the service role key) can read/write.

### 3. Local `.env.local`

Copy `.env.example` → `.env.local` and fill in every value:

```bash
cp .env.example .env.local
python -c "import secrets; print(secrets.token_urlsafe(48))"   # ADMIN_SESSION_SECRET
python -c "import secrets; print(secrets.token_urlsafe(24))"   # IP_HASH_SALT
```

### 4. Install deps

Requires **Node ≥ 20** and **Python 3.12** (matches what Vercel runs).

```bash
# Frontend
cd frontend && npm install && cd ..

# Backend (for local dev with vercel CLI)
pip install -r api/requirements.txt
```

### 5. Run locally

Install the Vercel CLI once: `npm i -g vercel`. Then:

```bash
vercel dev              # runs both the /api Python functions and the Vite build
# or, running them separately:
vercel dev              # in one shell -> port 3000
cd frontend && npm run dev  # in another -> port 5173, proxies /api to 3000
```

Open <http://localhost:3000/?e=GRACEGRAD> (with your `EVENT_CODE`) and try the flow.

---

## Deploying to Vercel

1. Push this repo to GitHub.
2. In Vercel, **Add New → Project → import the repo**. Framework preset: **Other** (Vercel will detect `vercel.json`).
3. Under **Environment Variables**, add every non-empty key from `.env.example`:

   | Var | Where it goes |
   |---|---|
   | `EVENT_NAME`, `EVENT_HEADLINE`, `EVENT_HOST`, `EVENT_DATE` | Public labels shown on the landing page |
   | `EVENT_CODE` | Baked into the QR URL; checked on every upload |
   | `SITE_URL` | Only used by `generate_qr.py` |
   | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` | Drive auth |
   | `DRIVE_FOLDER_ID` | Parent folder in your Drive. Also read at *build time* by `vite.config.js` so the landing page's "View Gallery" button links straight to this folder. |
   | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | Supabase |
   | `ADMIN_PASSWORD`, `ADMIN_SESSION_SECRET` | Admin gate |
   | `IP_HASH_SALT` | Rate limiter |

4. Deploy. Vercel will build the frontend, package `api/*.py` as serverless functions, and give you a URL like `capture-the-moment.vercel.app`.
5. Update `SITE_URL` to that URL and regenerate the QR (below).

**Notes on env vars.**
- **Client-side copy** (`VITE_EVENT_*`) is optional; Vite embeds anything with the `VITE_` prefix at build time. Landing-page copy has sensible fallbacks in `Landing.vue`.
- **`DRIVE_FOLDER_ID` is special**: it's both a server-side secret (used by the Python functions) *and* inlined into the frontend bundle at build time by `vite.config.js` (via `define`) so "View Gallery" can link to `drive.google.com/drive/folders/<id>`. One env var, both uses. Because it's baked in at build time, changing it in the Vercel dashboard requires a **new deployment** (not just a redeploy of an existing build) to take effect on the frontend.
- **Vercel scopes**: make sure each var is enabled for both **Production** and **Development** if you plan to use `vercel dev` with cloud values, or **Preview** if you use PR previews.

---

## Generate the QR code

```bash
pip install "qrcode[pil]" Pillow
export SITE_URL="https://your-deployment.vercel.app"
export EVENT_CODE="GRACEGRAD"    # matches Vercel env
python scripts/generate_qr.py
```

Outputs `scripts/out/capture_qr.png` (print-ready 1200×1600, black/gold with "SCAN → SNAP → SHARE") and `scripts/out/capture_qr.svg` (vector, best for large banners). Both encode `SITE_URL?e=EVENT_CODE`.

---

## Admin

- Navigate to `/admin` and log in with `ADMIN_PASSWORD`.
- You can hide/unhide or permanently delete photos. Delete removes both the Drive file and the Supabase row.
- **Cache note:** the image proxy sets a 24-hour edge cache. Newly hidden photos may still be reachable via direct URL at the CDN for up to a day. If you need faster expiry, drop `s-maxage` in `api/image/[id].py`.

## Design tokens

| Token | Value |
|---|---|
| `--bg` | `#000` |
| `--fg` | `#fff` |
| `--gold` | `#d4af37` |
| serif | Playfair Display |
| sans  | Inter |

Change them in `frontend/src/styles/global.css`.

---

## Trade-offs, kept small on purpose

- **Vercel Hobby** caps request bodies at 4.5 MB and function duration at 60 s (`vercel.json → functions.maxDuration`). The client always resizes to ≤2000 px on the long edge and 0.85 JPEG (target < 2 MB). If a HEIC comes in from an iPhone, `heic2any` decodes it in the browser before upload.
- **Cold starts are the enemy.** Importing `supabase` + `google-api-python-client` takes ~10–20 s on the first Lambda invocation. Mitigations already in place:
  - `main.js` fires a `GET /api/upload` warmup ping when the user lands, so the Python runtime is booting while they're still framing their photo.
  - `/api/upload` parallelizes the two Drive uploads (photo + thumb) using a `ThreadPoolExecutor` with per-thread Drive services (googleapiclient's httplib2 isn't thread-safe if shared).
- **Two files per photo** — a client-generated ~400 px thumbnail (fast gallery scrolling) and the 2000 px full size (opened in the lightbox / Drive). Both live in Drive subfolders `photos/` and `thumbs/`.
- **Storage abstraction** is a single module (`api/_lib/drive.py`). To move to Cloudinary or local disk later, replace that module and the callers keep working.
- **Rate limit** is a Supabase count-query per upload (max 20/hr per hashed IP). Fine for a graduation; you'd want Redis for anything busier.
- **CDN caching** trades near-zero Drive egress against slower moderation. Chose 24h; adjust `s-maxage` in `api/image/[id].py` if that's wrong for you.
