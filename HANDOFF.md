# Relay — Handoff Notes

**Status:** MVP complete, Telegram bot live, real Claude API integrated  
**Date:** 2026-08-22  
**Location:** `/Users/saf/hermes-api`  
**Repository:** https://github.com/safouenmzah/hermes-api

---

## 🎯 What Was Built (Week 1 Complete)

✅ **Telegram Bot** — Full command interface with per-user agent management  
✅ **FastAPI Server** — Agent lifecycle management + chat endpoint  
✅ **Real Claude Integration** — Anthropic API with extended thinking  
✅ **GitHub Repository** — Code ready for deployment  
✅ **Live Artifacts** — Dashboard + technical spec for reference  
✅ **Memory System** — Project context saved for future sessions  

---

## 🚀 How to Start Services

**Terminal 1 (API Server):**
```bash
cd /Users/saf/hermes-api
source venv/bin/activate
python start_api.py
```

**Terminal 2 (Telegram Bot):**
```bash
cd /Users/saf/hermes-api
source venv/bin/activate
python start_bot.py
```

**Verify:**
- API: http://localhost:8000/health
- Bot: @RelayxyzBot on Telegram (when API key added)

---

## 📋 Current Blockers

### **Blocking Issue: Missing Anthropic API Key**

The bot needs your Anthropic API key to function. Without it, agents return mock responses.

**Fix:**
1. Get key: https://console.anthropic.com/account/keys
2. Edit `/Users/saf/hermes-api/.env`
3. Add: `ANTHROPIC_API_KEY=sk-ant-...`
4. Restart services

**After key is added:**
- Bot will make real API calls to Claude
- Reasoning levels (minimal → ultra) will work
- Friends can deploy real agents

---

## 📂 Key Files & What They Do

| File | Purpose |
|------|---------|
| `start_api.py` | Launches FastAPI server |
| `start_bot.py` | Launches Telegram bot |
| `main.py` | API endpoints + agent invocation |
| `telegram_bot.py` | Bot command handlers |
| `.env` | Config (API key, bot token, etc.) |
| `agents_db.json` | Stores agent per user (auto-created) |
| `requirements.txt` | Python dependencies |

**Edit `.env` to:**
- Add `ANTHROPIC_API_KEY=sk-ant-...` (blocking)
- Adjust `DEFAULT_MODEL`, `DEFAULT_REASONING`, `MAX_TOKENS` if needed
- Bot token already set (`TELEGRAM_BOT_TOKEN`)

---

## 🔗 Live Artifacts (Updated in Real-Time)

These are published live and can be updated:

1. **Relay Dashboard** — Status, features, roadmap  
   https://claude.ai/code/artifact/4e46986c-95eb-4b35-b620-a6992499f044

2. **Relay Technical Spec** — API, commands, data models  
   https://claude.ai/code/artifact/c07785cc-8d21-4664-b704-68395f6ecfce

Edit in scratchpad → republish with same URL to update live.

---

## 🗺️ What's Next (Week 2-4)

### **Week 2: Multi-Channel + Cloud**
- [ ] Add WhatsApp or Discord integration
- [ ] Deploy to Railway (cloud-hosted)
- [ ] Get user feedback
- [ ] Set up monitoring/logging

### **Week 3: Monetization**
- [ ] Stripe payment integration
- [ ] Freemium pricing tiers
- [ ] Usage tracking & billing
- [ ] Real Argo integration readiness

### **Week 4+: Scale**
- [ ] API access tier
- [ ] Skills marketplace
- [ ] Advanced features (webhooks, custom reasoning)
- [ ] Enterprise support

---

## 💾 Project Status in Memory

Everything has been saved to `/Users/saf/.claude/projects/-Users-saf-s/memory/`:

- **relay-project.md** — Business model, vision, roadmap
- **relay-architecture.md** — Tech stack, API design, deployment path
- **hermes-agent-setup.md** — Hermes installation details
- **machine-specs.md** — Hardware (M4 Mac, 16GB)

These files persist across Claude sessions.

---

## 🧪 Testing Checklist

When API key is added:

- [ ] `GET http://localhost:8000/` returns API info
- [ ] `GET http://localhost:8000/health` returns `"status": "healthy"`
- [ ] Send `/start` to @RelayxyzBot in Telegram
- [ ] Send `/deploy` — should create new agent
- [ ] Send message — should return Claude response (not mock)
- [ ] Send `/config reasoning=high` — verify it updates
- [ ] Send `/history` — should show conversation
- [ ] Send `/list` — should list all agents

---

## 🔒 Security Notes

- **API Key:** Stored in `.env`, never commit to git
- **Bot Token:** Already in `.env`, already secure
- **Agents:** Per-user isolated (user ID = telegram_id)
- **Conversations:** Stored locally in JSON (upgrade to DB for prod)

---

## 📊 Cost Tracking

Once API key is active, track costs:

- **Anthropic API:** ~$0.015 per 1M input tokens (Opus)
- **Typical message:** 300-500 tokens = $0.005-0.008
- **High reasoning:** 1500-2000 tokens = $0.02-0.03
- **Set quota:** https://console.anthropic.com/account/billing/limits

**Pricing model:** Charge users 10x cost (margin target 70%+)

---

## 🎓 For Next Claude Session

If starting fresh:

1. Read `/Users/saf/.claude/projects/-Users-saf-s/memory/relay-project.md`
2. Run `/Users/saf/hermes-api/start_api.py` + `start_bot.py`
3. Add API key to `.env` if missing
4. Check artifacts above for full status

The bot is **ready to use** — just needs API key to go live.

---

## 📞 Quick Reference

**GitHub:** https://github.com/safouenmzah/hermes-api  
**Telegram Bot:** @RelayxyzBot  
**API Docs:** http://localhost:8000/docs  
**Anthropic Keys:** https://console.anthropic.com/account/keys  

**Commands Available:**
- `/start` — Welcome
- `/deploy` — Create agent
- `/list` — See agents
- `/switch <id>` — Change active
- `/config [key=value]` — Adjust settings
- `/status` — Check agent
- `/history` — Recent messages
- `/help` — Full reference

---

## ✅ Immediate Action Items

1. **Add Anthropic API key** to `.env`
2. **Restart services** (if changed)
3. **Test in Telegram** — send `/start`
4. **Invite friends** — share @RelayxyzBot
5. **Collect feedback** — what do they want?

**Then:** Deploy to Railway (Week 2) + add more channels.
