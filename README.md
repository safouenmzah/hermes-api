# Hermes Agent Manager — MVP

**Per-user agent management platform** with Telegram bot interface.

Users deploy agents and chat with them via Telegram. Each user gets their own agents with customizable settings.

## Quick Start

### 1. Setup Telegram Bot
Follow the guide in `TELEGRAM_SETUP.md`:
- Get a bot token from @BotFather
- Add it to `.env`

### 2. Start the service
```bash
cd /Users/saf/hermes-api
source venv/bin/activate
python run.py
```

This starts:
- ✅ FastAPI server on `http://localhost:8000`
- ✅ Telegram bot (polling for messages)

### 3. Test with Telegram
- Find your bot on Telegram
- Send `/start`
- Send `/deploy`
- Chat with your agent!

Or test API directly: **http://localhost:8000/docs**

## API Endpoints

### Health & Status
- `GET /health` — Server status and Hermes availability
- `GET /` — API info and endpoint list

### Chat
- `POST /chat` — Send a message to Hermes agent
  - Request: `{ message, conversation_id?, config? }`
  - Response: `{ conversation_id, response, reasoning_used, model }`

### Configuration
- `GET /config` — Get default agent config
- `POST /config` — Update default config
  - Fields: `reasoning_effort`, `model`, `max_tokens`

### Conversations
- `GET /conversations` — List all conversation IDs
- `GET /conversations/{conv_id}` — Get messages in a conversation

## Example Usage

```bash
# Chat request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can you do?"}'

# Configure agent
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-5",
    "reasoning_effort": "high",
    "max_tokens": 8192
  }'
```

## MVP Limitations

- **No authentication** — use only on trusted networks
- **In-memory storage** — conversations lost on restart
- **Hermes integration** — currently using mock responses (TODO: real SDK integration)
- **Single-user** — no multi-tenancy

## Next Steps

1. **Wire up real Hermes SDK** — Replace mock responses with actual agent calls
2. **Add persistence** — Store conversations in SQLite/PostgreSQL
3. **User authentication** — JWT or API keys
4. **Rate limiting** — Usage quotas per user/tier
5. **Monitoring** — Logs, metrics, error tracking
6. **Deployment** — Render, Railway, or AWS Lambda

## Architecture

```
Telegram User
     ↓
Telegram Bot (telegram_bot.py)
     ↓
FastAPI Server (main.py) — Agent Manager
     ↓
Per-User Agent Storage (agents_db.json)
     ↓
Agent API (/chat endpoint)
     ↓
Hermes Agent (Python SDK)
     ↓
LLM Provider (Anthropic, etc)
```

**Flow:**
1. User sends message in Telegram
2. Bot routes to agent manager
3. Manager finds user's active agent
4. Calls `/chat` endpoint with agent config
5. Returns response back to user in Telegram

## Development

Run with auto-reload:
```bash
uvicorn main.py --reload --host 0.0.0.0 --port 8000
```

View interactive API docs at: **http://localhost:8000/docs**
