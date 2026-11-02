# AGENTS.md — AAROHI project context for AI coding agents

Read this before changing the repo. Upstream was **Javis OS**; this fork is personalized as **AAROHI (आरोही)**. Prefer surface branding and persona changes; do **not** rename internal `javis_*` tools, `JavisPet`, session keys, or API paths unless explicitly asked.

## Identity (what / why)

| Item | Value |
|------|--------|
| Product name | **AAROHI** |
| Persona | Aarohi (आरोही) — sweet, caring AI girlfriend + second brain |
| Owner nicknames | babe, darling, jaan, my love, sweetheart |
| Default UI lang | English (`locale.ui_lang`: `en`) |
| Default workspace | `WORKSPACE_NAME=AAROHI`, `USER_NAME=Babe` |
| Default Edge TTS | `en-US-AvaMultilingualNeural` (also Neerja / Swara in dashboard) |
| OpenAI TTS fallback | `shimmer` |
| Gemini live voice | `aoede` |

**Why:** Owner wants girlfriend companion branding without breaking the agentic OS (tools, MCP hub, brains, Kanban).

## Canonical files (persona & UI)

- `CLAUDE.md` — system prompt / Aarohi identity
- `server/user_profile.md` — relationship memory injected across brain engines
- `server/voice_brain.py` — short spoken replies (1–3 warm sentences)
- `dashboard/index.html` (+ `server/dashboard/` copy) — title, brand, chat placeholder
- `dashboard/i18n/en.json` — user-facing English strings
- `dashboard/manifest.json` — PWA name
- `env.example` — safe defaults (no secrets)
- `README.aarohi.md` — human setup overview
- `vercel.json` — multi-service layout (`app` public, `cli` internal + `JAVIS_URL` binding)

## Important invariants (do not casually break)

1. **Internal names stay Javis** — `javis_task`, `javis_schedule`, `window.JavisPet`, `javis.session.v1`, etc. Renaming breaks clients and engines.
2. **Dual dashboard trees** — edit both `dashboard/` and `server/dashboard/` when changing UI assets that Vercel/serverless may serve from the server bundle.
3. **Serverless filesystem** — on Vercel/`AWS_LAMBDA_*`, state goes under `/tmp` (`JAVIS_STATE_DIR`, `BRAINS_DIR`). Never assume the app root is writable.
4. **Host allowlist** — `server/web_security.py` must allow `*.vercel.app` / `VERCEL_URL` in production or you get `{"error":"host not allowed","blocked":"web_security"}`.
5. **Secrets never in git** — tokens belong in Vercel/local `.env` only. If pasted in chat, treat as compromised and rotate.

## Change log for AI agents (when / what / how / why)

Dates are local owner context (**2026-11-01**, Asia/Kolkata) unless noted.

### 2026-11-01 — Persona + branding customization

- **What:** Redefined product as AAROHI; girlfriend persona in prompts; Ava/Neerja/Swara voices; dashboard title/placeholder; `WORKSPACE_NAME` / `USER_NAME` defaults.
- **How:** Edited `CLAUDE.md`, `server/user_profile.md`, `server/voice_brain.py`, dashboard HTML/JS/i18n, `env.example`, TTS defaults in `server/main.py` / `server/voice_note.py`.
- **Why:** Owner requested loving companion UX while keeping full agent tooling.

### 2026-11-01 — GitHub + Vercel deploy path

- **What:** Public repo `https://github.com/tarikk786786/AAROHI`; Vercel app historically at `https://aarohi-theta.vercel.app/`; `vercel.json` services `app` + `cli`.
- **How:** Repo made public (Hobby collaborator block on private multi-author history); serverless `/tmp` redirects; host allowlist for Vercel domains.
- **Why:** Hobby plan blocked private multi-author deploys; Lambda read-only FS and host CSRF guards caused 500 / host-not-allowed.

### 2026-11-01 — PR: branding polish branch

- **What:** User-facing “Javis OS” → “AAROHI”; chat empty hint; Ollama connect error text with install hint; default Ava voice; `manifest.json` rename.
- **How:** Branch `cursor/aarohi-branding-customization` → draft PR #1. Commit message covers branding + Ollama guidance; internal APIs untouched.
- **Why:** Finish remaining visible Javis labels without a risky global rename.
- **Link:** https://github.com/tarikk786786/AAROHI/pull/1

### Optional / not wired in-repo

- **OpenMausBot** (`https://github.com/milind-soni/OpenMausBot`) — owner asked to treat as a companion requirement; document only unless asked to integrate.
- **Supabase / Render / extra tokens** — provided for “use if needed”; AAROHI core does **not** require `SUPABASE_*` env vars (Supabase appears only as optional MCP). Do not commit keys.
- **Ollama** — local models need Ollama running (e.g. `winget install Ollama.Ollama` / https://ollama.com/download). UI string `ol.err_connect` explains this.

### 2026-11-01 — OpenRouter fallback brain via env

- **What:** `OPENROUTER_API_KEY` / `OPENROUTER_MODEL` seed `model.openrouter_key` and append OpenRouter to the Models usage order as a fallback when other brains deny/quota-fail.
- **How:** `server/config.py` `apply_model_env()` at startup; documented in `env.example`.
- **Why:** Owner wants a reliable API brain when Claude/Codex/etc are unavailable, without only using the Models UI.
- **Never commit real keys** — set locally or in Vercel env only.

### 2026-11-02 — Mark-inspired voice ladder (no Mark-LVI code)

- **What:** Patterns only from FatihMakes Mark-LVI (CC BY-NC - do not vendor): pick STT+LLM+TTS stack, soft TTS pace, never break girlfriend Hinglish audio.
- **How:** Skip `phien_am.doc_viet` for `reply_lang=hi` / `hi-*` / `en-IN` Edge voices (was mangling Hinglish); pin voice brain to Groq; TTS Swara @ −8%; Claude SDK/voice use `find_claude_cli()` → native `claude.exe` (not `claude.CMD`).
- **Why:** User reported broken/imperfect audio and Claude batch-script refuse on Windows; Mark-style choose-your-engine fixes reliability without copying Mark source.

### 2026-11-02 — Soft Indian girlfriend voice (Kavya + Shruti)

- **What:** Persona deepened (caring romantic Hinglish girlfriend). TTS ladder: optional **Indic-Speak Kavya**, else Edge **Swara @ −8%**. STT ear: optional **Shruti** offline Hinglish in `voice_ear` ranking. Settings can pick Kavya when available.
- **How:** `server/tts_indic_speak.py`, `server/stt_shruti.py`, voice_brain/CLAUDE/user_profile prompts, `docs/aarohi/VOICE_GIRLFRIEND.md`, `scripts/install-aarohi-voice.ps1`. Heavy models stay optional.
- **Why:** Owner wants the best free Indian girlfriend sound + hearing without forcing 6.6 GB on every install.

### 2026-11-02 — Desktop presence trilogy (Mark-inspired, clean rewrite)

- **What:** Ported *ideas* from FatihMakes Mark-LVI into AAROHI without copying CC BY-NC code: (1) `system/plugins/desktop-control` screenshot/type/click/hotkey/scroll; (2) wake phrases `aarohi`/`arohi` (+ mishears) in `voice-attention.js`; (3) speaking lip cycle on `JavisPet` mouth SVG.
- **How:** New bundled plugin + tests; mirrored `dashboard/` → `server/dashboard/` for attention + pet; optional `pip install pyautogui pillow`. Existing `desktop-apps` still opens/closes apps.
- **Why:** Owner asked for computer control + wake word + avatar HUD as a phased clean rewrite into AAROHI.
- **License note:** Do not vendor Mark-LVI source (CC BY-NC). Patterns only.

### 2026-11-02 — Full surface branding + Hinglish voice fix

- **What:** Visible "JAVIS OS" / "Javis Foundation" → **AAROHI**; en.json user strings branded; `reply_lang=hi` (Hinglish); call path `basic` + Edge Swara; Edge TTS upgraded to **7.3.1** (fixes Bing 403 silence); browser TTS fallback if Edge fails; model order skips Claude until SDK ready (`groq` → `openai-compat` → `openrouter`); brain label `AAROHI`.
- **How:** `dashboard/index.html` + `server/dashboard/` mirror; `i18n/en.json`; `lang_registry` + `lexicon/hi.py`; `voice.js` `_chunkFailed` → speechSynthesis; `settings.json` order/usage_order; `Javis/brain.json` label (folder path stays `Javis/` for engines).
- **Why:** Screenshot still showed JAVIS OS rail + silent mic after Edge 403 + Groq→Claude hop with no SDK.

### 2026-11-01 — Free LLM wake (401/429 fix)

- **What:** Bad LLM7 keys caused `401 authentication_error`; daily quota caused `429`. Chat stuck.
- **How:** `universal_brain.wake_free_brain()` clears bad keys, uses anonymous LLM7 `turbo` (no Authorization header), fails over to OVH anonymous; `aux_engine.is_route_failure` hops usage order on 401/429. Docs: `docs/aarohi/FREE_LLM_WAKE.md`.
- **Why:** Free-first always-on brain without inventing API keys.
- **Vercel:** leave `OPENAI_COMPAT_KEY` empty; set `OPENAI_COMPAT_MODEL=turbo`. Optional free keys: Groq / Gemini / OpenRouter.

### 2026-11-02 — Companion OS (Mark-capability, clean-room)

- **What:** Web-first companion HUD parity with Mark-LVI *behaviors* only (no CC BY-NC source): one-click Windows setup, warm-night home, PTT + self-echo guard + Hinglish ack, hardened desktop plugins, wizard one-click Cloudflare remote, memory strip + optional clipboard plugin.
- **How:**
  - Install: `AAROHI-setup.bat` / `AAROHI-start.bat`, `install.ps1` adds `pyautogui`+`pillow`, Desktop shortcut, Swara/−8%/Hinglish pins.
  - HUD: `dashboard/companion.css` warm rose/amber night; `body.companion-home`; engine strip on orb; status strings → Aarohi.
  - Voice: `dashboard/companion-voice.js` (hold Space / hold mic PTT, echo guard vs last TTS, instant ack on long turns).
  - Desktop: `javis_app_raise`; force-close needs `confirm=true`; Docker still refused; honest `[done]/`/`[unverified]`/`[ask]`.
  - Remote: wizard step “Open AAROHI from your phone” → `/remote-access/enable` quick tunnel (password required); Settings block unchanged.
  - Polish: `companion-memory.js` facts filter; `system/plugins/clipboard-assist` (enabled:false until user turns on).
- **Why:** Owner asked for Mark-like companion OS usable from any device without forking Mark-LVI.
- **License:** Patterns only. Never vendor `FatihMakes/Mark-LVI` (`ui.py`, `actions/`, `core/`).

## Runtime cheat sheet

| Mode | URL / command |
|------|----------------|
| Local dashboard (typical) | `http://127.0.0.1:7777` (or port from start scripts) |
| One-click Windows | `AAROHI-setup.bat` then `AAROHI-start.bat` (alias: `start-javis.bat`) |
| Production (historical) | `https://aarohi-theta.vercel.app/` |
| Start (Windows) | `AAROHI-start.bat` / `server\main.py` via venv |
| Python deps | `requirements.txt` (+ optional `pyautogui pillow` for desktop control) |
| Node/turbo CI helpers | `package.json` + `turbo.json` (lint/typecheck/test stubs) |

## How other AIs should work here

1. Read this file + `CLAUDE.md` + `README.aarohi.md`.
2. Prefer **branding/persona/docs/env defaults** over engine rewrites.
3. When changing dashboard JS/CSS/HTML, mirror into `server/dashboard/` if that path exists.
4. After host/security/serverless changes, verify production URL and `/auth/status` (not only local).
5. Never commit secrets; never force-push `main` unless the owner explicitly asks.
6. For Vercel: confirm `.vercel/project.json` / project link before claiming deploy status; Hobby + private repos have collaborator limits.

## Owner intent (short)

Keep AAROHI sweet and personal on the outside; keep Javis OS power on the inside. Customize carefully; document every intentional fork change here when you make one.
