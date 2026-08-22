# Hermes Agent API — MVP

REST API wrapper for Hermes Agent. Exposes chat, agent configuration, and conversation history.

## Quick Start

### 1. Install dependencies
```bash
cd /Users/saf/hermes-api
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the server
```bash
python main.py
```

Server runs on `http://localhost:8000`

### 3. Test it
```bash
# In another terminal
source venv/bin/activate
python test_client.py
```

Or use the interactive docs at: **http://localhost:8000/docs**

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
User/Frontend
     ↓
 FastAPI Server (main.py)
     ↓
Hermes Agent (Python SDK)
     ↓
LLM Provider (Anthropic, etc)
```

## Development

Run with auto-reload:
```bash
uvicorn main.py --reload --host 0.0.0.0 --port 8000
```

View interactive API docs at: **http://localhost:8000/docs**
