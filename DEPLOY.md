# Deploy to Railway

Railway is a cloud platform that deploys your app in seconds. **Free tier included** (100 hours/month).

## 🚀 Quick Deploy (5 minutes)

### 1. Push to GitHub
```bash
cd /Users/saf/hermes-api
git remote add origin https://github.com/YOUR_USERNAME/hermes-api
git push -u origin main
```

### 2. Connect to Railway
1. Go to **https://railway.app**
2. Sign up (GitHub, email, or Google)
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Search for `hermes-api`, select it
5. Railway auto-detects Python + Procfile
6. Click **"Deploy"**

### 3. Set Environment Variables (Railway Dashboard)
In Railway dashboard, go to your project → Variables:

```
DEFAULT_MODEL=claude-opus-5
DEFAULT_REASONING=medium
MAX_TOKENS=4096
```

### 4. Get Your Live URL
Once deployed:
- Railway generates a URL like: `https://hermes-api-prod.railway.app`
- View at `https://hermes-api-prod.railway.app/docs` (interactive API)
- Share with friends: `https://hermes-api-prod.railway.app`

---

## 📊 Testing Deployed API

```bash
# Get health
curl https://hermes-api-prod.railway.app/health

# Send a chat
curl -X POST https://hermes-api-prod.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from the cloud!"}'
```

---

## 💡 Alternative: Use Railway CLI (Even Faster)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Deploy
cd /Users/saf/hermes-api
railway init
railway up
```

---

## 📈 Monitoring & Logs

In Railway dashboard:
- **Logs** — see real-time server output
- **Metrics** — CPU, memory, requests
- **Settings** → Enable auto-deploy on git push

---

## 🔒 Next: Add Authentication

Once deployed, add API key auth to prevent abuse:

```python
from fastapi import Header, HTTPException

@app.post("/chat")
async def chat(request: ChatRequest, x_api_key: str = Header(None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of chat logic
```

Set `API_KEY` in Railway variables, share with friends.

---

## 💰 Pricing

- **Free tier**: 100 hours/month + 5GB bandwidth (plenty for MVP)
- **Pay-as-you-go**: $5 credit/month, then $0.50/hour after that
- Databases (if you add): PostgreSQL $5/month minimum

For a low-traffic MVP, you'll likely stay in free tier.

---

## Next Steps After Deploy

1. ✅ Share the live URL with friends/family
2. ✅ Collect feedback on what they want
3. ⬜ Wire up real Hermes SDK (replace mock responses)
4. ⬜ Add user authentication + rate limiting
5. ⬜ Add pricing tiers
