# Deployment Guide

## Quick Start (Local)

### 1. Start the API Server

```bash
# Make sure you're in the project root
python3 api_server.py
```

The API will run on `http://localhost:8000`

### 2. Start the Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:3000`

## Deploy to Vercel

### Step 1: Prepare Your Repository

All code is already in your GitHub repo: `joel-arbitraasi`

### Step 2: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New Project"
3. Select your `joel-arbitraasi` repository
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

5. Add Environment Variable:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: Leave empty for now (we'll add the backend URL later)

6. Click "Deploy"

Your frontend will be live at: `https://your-project.vercel.app`

### Step 3: Deploy Backend API

The Python backend needs to run continuously to scan for opportunities. Options:

#### Option A: Railway (Recommended for 24/7 scanning)

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `joel-arbitraasi`
5. Add environment variables:
   - `ODDS_API_KEY`: your API key
   - `ODDS_API_BASE_URL`: https://api.the-odds-api.com/v4
6. Set start command: `python3 api_server.py`
7. Railway will give you a URL like: `https://your-app.railway.app`

#### Option B: Render

1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your `joel-arbitraasi` repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 api_server.py`
5. Add environment variables (same as above)

#### Option C: Keep Running Locally

If you have a computer that's always on:
1. Run the API server: `python3 api_server.py`
2. Use ngrok to expose it: `ngrok http 8000`
3. Use the ngrok URL as your `NEXT_PUBLIC_API_URL`

### Step 4: Connect Frontend to Backend

1. Go to your Vercel project settings
2. Environment Variables
3. Update `NEXT_PUBLIC_API_URL` with your backend URL:
   - Railway: `https://your-app.railway.app`
   - Render: `https://your-app.onrender.com`
   - ngrok: `https://abc123.ngrok.io`
4. Redeploy the frontend

## Done! 🎉

Your arbitrage dashboard is now live and scanning for opportunities 24/7!

## Troubleshooting

**CORS Error**: Make sure the API server allows your Vercel domain in CORS settings (it's already set to allow all origins).

**API Connection Failed**: Check that your backend is running and accessible from the internet.

**No Opportunities Showing**: The scanner needs time to find opportunities. Click "Refresh" to trigger a new scan.
