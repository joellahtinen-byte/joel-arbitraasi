# Deploy to Vercel - Step by Step

## ✅ Prerequisites

- GitHub account
- Vercel account (free - sign up at vercel.com)
- Your `joel-arbitraasi` repo is already pushed to GitHub

## 🚀 Deploy Frontend (5 minutes)

### 1. Go to Vercel

Visit: https://vercel.com/new

### 2. Import Repository

- Click "Add New Project"
- Find and select `joel-arbitraasi`
- Click "Import"

### 3. Configure Build Settings

- **Framework Preset**: Next.js ✅ (auto-detected)
- **Root Directory**: Click "Edit" and enter: `frontend`
- **Build Command**: `npm run build` (default, leave as is)
- **Output Directory**: `.next` (default, leave as is)

### 4. Add Environment Variable (Important!)

Click "Environment Variables" and add:

- **Name**: `NEXT_PUBLIC_API_URL`
- **Value**: `http://localhost:8000` (temporary - we'll update this)

### 5. Deploy!

Click "Deploy" button

Wait 2-3 minutes for build to complete

Your dashboard will be live at: `https://joel-arbitraasi-xxxxx.vercel.app`

## 🔧 Deploy Backend API

The frontend is now live, but it needs the backend API to fetch opportunities.

### Option A: Keep API Running Locally (Simplest for testing)

1. Make sure API is running:
   ```bash
   python3 api_server.py
   ```

2. Install ngrok: https://ngrok.com/download

3. Expose your local API:
   ```bash
   ngrok http 8000
   ```

4. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

5. Go to Vercel project → Settings → Environment Variables

6. Update `NEXT_PUBLIC_API_URL` to your ngrok URL

7. Redeploy from Vercel dashboard

### Option B: Deploy Backend to Railway (24/7 uptime)

1. Go to: https://railway.app

2. Sign in with GitHub

3. New Project → "Deploy from GitHub repo"

4. Select `joel-arbitraasi`

5. Add environment variables:
   ```
   ODDS_API_KEY=c3ae199cf23cb998578b5b0f42bf3398
   ODDS_API_BASE_URL=https://api.the-odds-api.com/v4
   ```

6. Add start command in Settings:
   ```
   python3 api_server.py
   ```

7. Railway will give you a URL like: `https://your-app.railway.app`

8. Update Vercel environment variable `NEXT_PUBLIC_API_URL` with Railway URL

9. Redeploy frontend on Vercel

### Option C: Deploy Backend to Render

1. Go to: https://render.com

2. New → Web Service

3. Connect `joel-arbitraasi` repo

4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 api_server.py`

5. Add same environment variables as Railway

6. Render will give you: `https://your-app.onrender.com`

7. Update Vercel and redeploy

## 🎉 Done!

Visit your Vercel URL and you'll see:

- 🎨 Cartoonish dashboard
- 💰 Real arbitrage opportunities
- 🎯 Direct links to place bets
- ⚡ Auto-refreshes every 10 seconds

## 🐛 Troubleshooting

**"Could not connect to API"**
- Check that your backend is running
- Verify the `NEXT_PUBLIC_API_URL` in Vercel settings
- Check CORS is enabled (it is by default in api_server.py)

**"No opportunities found"**
- Click the refresh button to trigger a new scan
- Check backend logs to see if API calls are working
- Verify your Odds API key is valid

**Build failed on Vercel**
- Check that Root Directory is set to `frontend`
- Make sure all dependencies are in package.json

## 📊 Current Status

✅ API found **13 real arbitrage opportunities**!
✅ Best opportunity: **1.23% margin (€12.33 profit)**
✅ Frontend built successfully
✅ Ready to deploy!
