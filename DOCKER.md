# Relay MVP — Docker Setup

## Quick Start

```bash
# 1. Build the image
docker-compose build

# 2. Run services
docker-compose up -d

# 3. Check status
docker-compose logs -f
```

## Environment Setup

Before running, set environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export TELEGRAM_BOT_TOKEN="..."
```

Or create a `.env` file in the project root:

```bash
ANTHROPIC_API_KEY=sk-ant-...
TELEGRAM_BOT_TOKEN=...
```

## Running Services

### Start in background:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f relay
```

### Stop services:
```bash
docker-compose down
```

### Restart:
```bash
docker-compose restart
```

## Verify Services

### API Health:
```bash
curl http://localhost:8000/health
```

### API Docs:
```
http://localhost:8000/docs
```

### Chat Test:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'
```

## Telegram Bot

Once running, message **@RelayxyzBot** on Telegram:
- `/start` — Welcome
- `/deploy` — Create agent
- Any message → Chat with Claude

## Volume Mounts

- `${HOME}/.hermes` — Read-only Hermes installation
- `./agents_db.json` — Persistent agent data

## Health Check

Container has automatic health checks every 30s. View status:

```bash
docker-compose ps
```

## Building for Production (Argo)

```bash
# Build image
docker build -t relay-mvp:latest .

# Push to registry
docker push your-registry/relay-mvp:latest

# Deploy to Argo
# (See Argo deployment docs)
```

## Troubleshooting

### Container exits immediately:
```bash
docker-compose logs relay
```

### API not responding:
```bash
docker-compose ps  # Check if running
curl http://localhost:8000/health  # Check health
```

### Environment variables not set:
```bash
docker-compose config  # View resolved config
```

### Hermes not found:
Ensure `${HOME}/.hermes` exists and is properly mounted.

## Next Steps

When ready to deploy to Argo:
1. Push Docker image to a registry (Docker Hub, ECR, etc.)
2. Create Argo ApplicationSet with image reference
3. Set environment variables in Argo secrets
4. Deploy!
