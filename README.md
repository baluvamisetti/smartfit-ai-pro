# SmartFit AI Pro X — Style Dossier

An AI-powered fashion intelligence app that analyzes body shape and skin undertone from two photos, then generates a personalized style report — complete with a custom color palette and styling recommendations.

**🔗 Live App:** [smartfit-ai-pro.vercel.app](https://smartfit-ai-pro.vercel.app)
**⚙️ Backend API:** [smartfit-ai-pro-production.up.railway.app](https://smartfit-ai-pro-production.up.railway.app)

![Status](https://img.shields.io/badge/status-live-brightgreen)
![Backend](https://img.shields.io/badge/backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/frontend-Next.js-black)
![Deployment](https://img.shields.io/badge/deployed-Railway%20%2B%20Vercel-blueviolet)

---

## ✨ What It Does

Upload a full-body photo and a face close-up, and SmartFit AI Pro X returns a full **Style Dossier**:

- **Body Shape Classification** — detects your body shape (e.g. Inverted Triangle, Hourglass, Rectangle) with a confidence score, using pose landmark estimation
- **Skin Undertone Detection** — classifies your undertone (Warm / Cool / Neutral) from facial skin tone analysis
- **Personalized Color Palette** — generates a curated set of hex-coded colors that complement your specific undertone, with a plain-language explanation of *why* they work
- **Fashion Score** — an overall styling compatibility score based on your inputs and preferences (e.g. occasion)

---

## 🧠 How It Works

1. **Pose & landmark detection** — [MediaPipe](https://developers.google.com/mediapipe) extracts body landmarks from the full-body photo to classify body shape
2. **Computer vision analysis** — [OpenCV](https://opencv.org/) processes the face photo to sample skin tone and derive undertone
3. **Recommendation logic** — maps undertone + body shape to a tailored color palette and styling guidance
4. **API layer** — a FastAPI backend exposes this pipeline as REST endpoints, containerized with Docker and deployed on Railway
5. **Frontend** — a Next.js + TypeScript + Tailwind interface handles uploads and renders the dossier as an editorial-style report

---

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python 3.12)
- MediaPipe — pose/body landmark detection
- OpenCV (headless) — image & skin tone analysis
- SQLAlchemy + PostgreSQL (Supabase)
- Docker — containerized deployment
- Deployed on **Railway**

**Frontend**
- Next.js 16 (React 18, TypeScript)
- Tailwind CSS
- Axios for API communication
- Deployed on **Vercel**

---

## 📸 Preview

> Upload two photos → get body shape, undertone, a 6-color personalized palette, and a fashion score — all in seconds.

---

## 🚀 Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to point to your local or deployed backend.

---

## 📌 Notes

This project was built end-to-end — from ML pipeline to a fully deployed, publicly accessible full-stack application — as part of an ongoing portfolio of applied ML/Data Science projects.

---

## 👤 Author

**Balu Vamisetti**
[GitHub](https://github.com/baluvamisetti)
