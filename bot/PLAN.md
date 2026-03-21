# Task 4: Containerize and Document - Implementation Plan

## Overview

This task containerizes the Telegram bot so it runs alongside the backend as a proper Docker service, replacing the fragile `nohup` background process.

## Deliverables

### 1. Bot Dockerfile (`bot/Dockerfile`)

Multi-stage build using `uv` and `pyproject.toml`:

**Stage 1 (Builder):**
- Base: `astral/uv:python3.14-bookworm-slim`
- Copy `bot/pyproject.toml`
- Run `uv sync --frozen --no-install-project`
- Copy bot source code

**Stage 2 (Runtime):**
- Base: `python:3.14.2-slim-bookworm`
- Create non-root user `nonroot`
- Copy application from builder
- Set PATH to include virtualenv
- Run `bot.py` as entry point

**Key decisions:**
- No `requirements.txt` — uses `pyproject.toml` exclusively
- Non-root user for security
- Bytecode compilation for faster startup

### 2. Docker Compose Service (`docker-compose.yml`)

Add `bot` service with:

```yaml
bot:
  build:
    context: .
    dockerfile: bot/Dockerfile
  restart: unless-stopped
  networks:
    - lms-network
  environment:
    - BOT_TOKEN=${BOT_TOKEN}
    - LMS_API_BASE_URL=http://backend:8000  # Service name, not localhost
    - LMS_API_KEY=${LMS_API_KEY}
    - LLM_API_MODEL=${LLM_API_MODEL}
    - LLM_API_KEY=${LLM_API_KEY}
    - LLM_API_BASE_URL=${LLM_API_BASE_URL}
  depends_on:
    - backend
```

**Key networking change:**
- Bot uses `http://backend:8000` not `http://localhost:42002`
- Inside Docker, `localhost` is the container itself
- Service names resolve via Docker's internal DNS

### 3. README Deploy Section

Add "Deploy" section documenting:
- Required environment variables
- Docker Compose commands
- Verification steps
- Common troubleshooting

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | Yes | — | Telegram bot token from @BotFather |
| `LMS_API_BASE_URL` | No | `http://backend:8000` | Backend URL (use service name in Docker) |
| `LMS_API_KEY` | Yes | — | API key for Bearer auth |
| `LLM_API_MODEL` | No | `coder-model` | LLM model name |
| `LLM_API_KEY` | Yes | — | LLM API key |
| `LLM_API_BASE_URL` | Yes | — | LLM API endpoint |

## Docker Networking

The bot needs to reach:
1. **Backend** → `http://backend:8000` (same `lms-network`)
2. **LLM proxy** → `http://host.docker.internal:42005` (different network)

For the LLM, we use `host.docker.internal` because the Qwen proxy runs on a separate Docker network.

## Build Process

1. Docker reads `bot/Dockerfile`
2. Builder stage installs deps via `uv sync`
3. Runtime stage copies application
4. Compose starts bot with env vars
5. Bot connects to backend via `lms-network`

## Verification

```bash
# Check bot is running
docker compose ps bot

# View logs
docker compose logs bot --tail 20

# Test in Telegram
# Send: /start, /health, "what labs are available?"
```

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Container restarts | Missing env var | Check `.env.docker.secret` has all required vars |
| Backend connection refused | Using `localhost` | Change to `http://backend:8000` |
| LLM fails | Wrong URL | Use `host.docker.internal` for cross-network |
| Build fails at `uv sync` | Missing `pyproject.toml` | Check COPY paths in Dockerfile |

## Success Criteria

1. `bot/Dockerfile` exists and builds
2. `docker-compose.yml` has `bot` service
3. Bot container runs (`docker ps`)
4. Backend still healthy
5. Bot responds in Telegram
6. README has deploy section
