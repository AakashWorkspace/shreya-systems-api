# Shreya Systems — Quotation Studio
## Complete Deployment Guide

---

## Project Structure

```
shreya-backend/          ← Deploy to Render
  main.py
  auth.py
  models.py
  database.py
  requirements.txt
  Procfile
  render.yaml
  .env.example

shreya-frontend/         ← Deploy to Vercel
  src/
    main.jsx
    index.css
    api.js
    App.jsx
    Auth.jsx
    components/
      CreateQuotation.jsx
      QuotePDF.jsx
      AddItem.jsx
      ViewItems.jsx
      QuoteHistory.jsx
  index.html
  vite.config.js
  tailwind.config.js
  postcss.config.js
  package.json
  vercel.json
  .env.example
```

---

## PART 1 — Database (Neon PostgreSQL — Free Tier)

### Step 1 · Create Neon database

1. Visit https://neon.tech → Sign up (free)
2. Create a new project → name it `shreya-systems`
3. Copy the **Connection String** — it looks like:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Save this — it is your `DATABASE_URL`
postgresql://neondb_owner:npg_VZDELA6cz7fB@ep-fancy-base-am4i4xt0.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require
---

## PART 2 — Backend (Render — Free Tier)

### Step 2 · Initialize backend Git repository

```bash
cd shreya-backend

git init
git add .
git commit -m "feat: initial Shreya Systems FastAPI backend"

# Create a new repo on GitHub (call it shreya-systems-api)
# Then:
git remote add origin https://github.com/YOUR_USERNAME/shreya-systems-api.git
git branch -M main
git push -u origin main
```

### Step 3 · Deploy to Render

1. Visit https://render.com → Sign up / Log in
2. Click **New → Web Service**
3. Connect your GitHub account → select `shreya-systems-api`
4. Configure:
   - **Name:** `shreya-systems-api`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free

### Step 4 · Set Environment Variables on Render

In your Render service → **Environment** tab, add:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` ← from Neon |
| `SECRET_KEY` | Any random 40+ char string (e.g. run `openssl rand -hex 32`) | 
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` (update after Vercel deploy) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` |

5. Click **Save Changes** → Render will deploy automatically
6. Wait ~2 min → Copy your Render URL: `https://shreya-systems-api.onrender.com`

> ⚠️ **Free Render Note:** The service sleeps after 15 min of inactivity. First request takes ~30s to wake. Consider using UptimeRobot (free) to ping /health every 10 min.

---

## PART 3 — Frontend (Vercel — Free Tier)

### Step 5 · Initialize frontend Git repository

```bash
cd shreya-frontend

# Install dependencies locally (optional, for testing)
npm install

# Test locally (optional)
# Create .env.local with VITE_API_BASE_URL=http://localhost:8000
# Then: npm run dev

git init
git add .
git commit -m "feat: initial Shreya Systems React frontend"

# Create a new repo on GitHub (call it shreya-systems-ui)
git remote add origin https://github.com/YOUR_USERNAME/shreya-systems-ui.git
git branch -M main
git push -u origin main
```

### Step 6 · Deploy to Vercel

**Option A — Vercel CLI (recommended):**
```bash
npm i -g vercel
vercel login
vercel --prod
```

**Option B — Vercel Dashboard:**
1. Visit https://vercel.com → Sign up / Log in
2. Click **Add New → Project**
3. Import `shreya-systems-ui` from GitHub
4. Framework Preset: **Vite**
5. Build Command: `npm run build`
6. Output Directory: `dist`

### Step 7 · Set Environment Variables on Vercel

In Vercel project → **Settings → Environment Variables**, add:

| Key | Value | Environment |
|-----|-------|-------------|
| `VITE_API_BASE_URL` | `https://shreya-systems-api.onrender.com` | Production, Preview, Development |

Click **Save** → Vercel will trigger a new deployment.

---

## PART 4 — Cross-Origin Fix (Critical)

After Vercel deployment, your frontend URL will be something like:
`https://shreya-systems-ui.vercel.app`

Go back to **Render → Environment** and update:
```
ALLOWED_ORIGINS = https://shreya-systems-ui.vercel.app
```

Or to allow all (simpler during development):
```
ALLOWED_ORIGINS = *
```

Render will auto-redeploy.

---

## PART 5 — Local Development

### Backend (terminal 1)
```bash
cd shreya-backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env
# Edit .env: set DATABASE_URL to your Neon URL

uvicorn main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### Frontend (terminal 2)
```bash
cd shreya-frontend
npm install

# .env.local already has VITE_API_BASE_URL=http://localhost:8000
npm run dev
# App: http://localhost:5173
```

---

## PART 6 — First-Use Checklist

After deployment:

- [ ] Visit `https://your-api.onrender.com/docs` — FastAPI Swagger UI should load
- [ ] Visit `https://your-app.vercel.app` — Login page should load
- [ ] Register a new account
- [ ] Add 2–3 items to the catalogue (Add Item tab)
- [ ] Create a quotation — live PDF preview should render on the right
- [ ] Download the PDF and verify it matches the Shreya Systems format
- [ ] Save the quotation — check Quotation Archive

---

## Architecture Summary

```
Browser (Vercel CDN)
    │  HTTPS
    ▼
React SPA (Vite build)
    │  Axios + JWT Bearer Token
    │  VITE_API_BASE_URL
    ▼
FastAPI (Render Web Service)
    │  SQLAlchemy ORM
    │  DATABASE_URL
    ▼
PostgreSQL (Neon Serverless)
```

---

## Environment Variables — Quick Reference

### Render (Backend)
```
DATABASE_URL         postgresql://...neon.tech/neondb?sslmode=require
SECRET_KEY           <random 40+ chars>
ALLOWED_ORIGINS      https://your-app.vercel.app
ACCESS_TOKEN_EXPIRE_MINUTES   1440
```

### Vercel (Frontend)
```
VITE_API_BASE_URL    https://shreya-systems-api.onrender.com
```

---

## Useful Commands

```bash
# Generate a secure SECRET_KEY
openssl rand -hex 32
# or
python3 -c "import secrets; print(secrets.token_hex(32))"

# Check backend logs on Render
# → Render dashboard → Your service → Logs tab

# Tail Vercel build logs
vercel logs --follow

# Force redeploy frontend
vercel --prod --force
```

---

*Built for Shreya Systems, Pune. GSTIN: 27AFFPG6521C1ZW*
