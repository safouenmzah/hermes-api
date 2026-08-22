# Getting Your Anthropic API Key

Your Hermes is already configured to use Anthropic models. Now wire up the API key:

## Step 1: Get Your API Key

1. Go to **https://console.anthropic.com/account/keys**
2. Click **"Create Key"**
3. Copy the key (starts with `sk-ant-...`)

## Step 2: Add to .env

Edit `/Users/saf/hermes-api/.env`:

```
ANTHROPIC_API_KEY=sk-ant-... (paste your key here)
```

Save and restart the services:

```bash
pkill -f "python start"
source venv/bin/activate
python start_api.py &
python start_bot.py &
```

## Step 3: Test

Send a message in Telegram:

```
/deploy
Hello, can you explain quantum computing?
```

The agent should now respond with real Claude reasoning! 🚀

---

## Billing

- Claude API charges per token
- ~$0.015 per 1M input tokens (Opus)
- Typical chat: $0.01-0.05 per message
- Add quota alerts: https://console.anthropic.com/account/billing/limits
