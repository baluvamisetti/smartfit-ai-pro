# SmartFit AI Pro X — AI Fashion Intelligence Platform (MVP)

An AI-powered platform that analyzes a user's body shape and skin undertone from
two photos, then generates a personalized clothing and color recommendation
"Style Dossier."

This repo is the **MVP core** of a larger enterprise vision (see [Roadmap](#roadmap)
below). It's scoped to be real, working, and deployable — not a mockup.

## What actually works right now

- **Body shape classification** — MediaPipe Pose landmark detection → shoulder/hip/waist
  ratio analysis → classifies Hourglass / Rectangle / Triangle / Inverted Triangle / Oval / Athletic.
- **Skin undertone & shade analysis** — MediaPipe Face Detection → samples forehead/cheek
  regions → K-Means color clustering → classifies Warm/Cool/Neutral undertone and shade group.
- **Rule-based recommendation engine** — combines body shape + undertone + occasion into
  explainable clothing and color recommendations (not a black box).
- **Database persistence** — every body analysis, skin analysis, and recommendation is
  saved to Postgres (Supabase) or SQLite (local dev, auto-fallback). No user auth yet, so
  rows are keyed by a client-generated `session_id`, not a real account.
- **Structured logging** — every request is logged as JSON to stdout (method, path, status,
  latency) and also written to a `request_logs` table, so you can debug via console or query it.
- **`/api/stats/summary`** — basic usage counters (total analyses, avg fashion score, body
  shape breakdown, error count) — the seed of the Phase 3 analytics dashboard.
- **Next.js frontend** — editorial "Style Dossier" UI with a Pantone-style personalized
  color swatch card.

## Architecture

```
smartfit-ai-pro/
├── backend/              FastAPI service
│   └── app/
│       ├── main.py
│       ├── routers/      /api/body, /api/skin, /api/recommend
│       ├── services/     body_analysis.py, skin_analysis.py, recommendation_engine.py
│       └── models/       Pydantic schemas
└── frontend/             Next.js 14 (App Router) + TypeScript + Tailwind
    ├── app/page.tsx      Upload → Analyze → Dossier flow
    └── lib/api.ts        Typed API client
```

## Running locally

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        (Windows)  |  source venv/bin/activate   (Mac/Linux)
pip install -r requirements.txt
copy .env.example .env      (Windows)  |  cp .env.example .env      (Mac/Linux)
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for interactive API docs.
Tables are auto-created in SQLite (`smartfit_dev.db`) on first run — no manual
migration step needed for local dev. Swap `SMARTFIT_DATABASE_URL` in `.env` to
your Supabase connection string when you're ready for Postgres.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```
Visit `http://localhost:3000`.

## Important accuracy note

Absolute body measurements (cm) from a single 2D photo without a calibration
reference are inherently approximate. This service computes **proportional
ratios** (the industry-standard signal for body-shape classification) and only
produces cm estimates if the user supplies their real height — clearly flagged
as an estimate in the API response, not presented as clinical measurement.

## Deployment

Same pattern as your Resume Screener project:
- **Backend** → Render or Railway (Docker or native Python buildpack). Watch
  Gunicorn/Uvicorn worker memory — MediaPipe + OpenCV are heavier than a typical
  Flask app, so start with at least a 512MB–1GB instance.
- **Frontend** → Vercel (native Next.js support) or Render static site.
- Set `NEXT_PUBLIC_API_URL` on the frontend to your deployed backend URL.

## Roadmap

The full original spec envisioned an enterprise platform. These are documented
here as the intentional next phases, not built in this MVP:

**Phase 2**
- Smart Wardrobe Management (upload wardrobe, auto-classify, daily outfit suggestions)
- Virtual Try-On (diffusion-based garment overlay)
- Learned re-ranking layer on top of the rule-based engine using real user feedback
  (collaborative filtering)
- PostgreSQL persistence (via Supabase) for user profiles and history

**Phase 3**
- Role-based access control (CEO/Admin/Manager/Staff/User) + audit logging
- Real-time analytics dashboard
- Flutter mobile app
- Multi-language AI fashion chat assistant

Scoping it this way — a working core plus an explicit, reasoned roadmap — is
usually more convincing in interviews than a partially-built version of everything.
