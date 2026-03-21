# Lab 7 — Build a Client with an AI Coding Agent

[Sync your fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork#syncing-a-fork-branch-from-the-command-line) regularly — the lab gets updated.

## Product brief

> Build a Telegram bot that lets users interact with the LMS backend through chat. Users should be able to check system health, browse labs and scores, and ask questions in plain language. The bot should use an LLM to understand what the user wants and fetch the right data. Deploy it alongside the existing backend on the VM.

This is what a customer might tell you. Your job is to turn it into a working product using an AI coding agent (Qwen Code) as your development partner.

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────┐     ┌──────────────────────────────────┐   │
│  │  Telegram    │────▶│  Your Bot                        │   │
│  │  User        │◀────│  (aiogram / python-telegram-bot) │   │
│  └──────────────┘     └──────┬───────────────────────────┘   │
│                              │                               │
│                              │ slash commands + plain text    │
│                              ├───────▶ /start, /help         │
│                              ├───────▶ /health, /labs        │
│                              ├───────▶ intent router ──▶ LLM │
│                              │                    │          │
│                              │                    ▼          │
│  ┌──────────────┐     ┌──────┴───────┐    tools/actions      │
│  │  Docker      │     │  LMS Backend │◀───── GET /items      │
│  │  Compose     │     │  (FastAPI)   │◀───── GET /analytics  │
│  │              │     │  + PostgreSQL│◀───── POST /sync      │
│  └──────────────┘     └──────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

## Requirements

### P0 — Must have

1. Testable handler architecture — handlers work without Telegram
2. CLI test mode: `cd bot && uv run bot.py --test "/command"` prints response to stdout
3. `/start` — welcome message
4. `/help` — lists all available commands
5. `/health` — calls backend, reports up/down status
6. `/labs` — lists available labs
7. `/scores <lab>` — per-task pass rates
8. Error handling — backend down produces a friendly message, not a crash

### P1 — Should have

1. Natural language intent routing — plain text interpreted by LLM
2. All 9 backend endpoints wrapped as LLM tools
3. Inline keyboard buttons for common actions
4. Multi-step reasoning (LLM chains multiple API calls)

### P2 — Nice to have

1. Rich formatting (tables, charts as images)
2. Response caching
3. Conversation context (multi-turn)

### P3 — Deployment

1. Bot containerized with Dockerfile
2. Added as service in `docker-compose.yml`
3. Deployed and running on VM
4. README documents deployment

## Learning advice

Notice the progression above: **product brief** (vague customer ask) → **prioritized requirements** (structured) → **task specifications** (precise deliverables + acceptance criteria). This is how engineering work flows.

You are not following step-by-step instructions — you are building a product with an AI coding agent. The learning comes from planning, building, testing, and debugging iteratively.

## Learning outcomes

By the end of this lab, you should be able to say:

1. I turned a vague product brief into a working Telegram bot.
2. I can ask it questions in plain language and it fetches the right data.
3. I used an AI coding agent to plan and build the whole thing.

## Tasks

### Prerequisites

1. Complete the [lab setup](./lab/setup/setup-simple.md#lab-setup)

> **Note**: First time in this course? Do the [full setup](./lab/setup/setup-full.md#lab-setup) instead.

### Required

1. [Plan and Scaffold](./lab/tasks/required/task-1.md) — P0: project structure + `--test` mode
2. [Backend Integration](./lab/tasks/required/task-2.md) — P0: slash commands + real data
3. [Intent-Based Natural Language Routing](./lab/tasks/required/task-3.md) — P1: LLM tool use
4. [Containerize and Document](./lab/tasks/required/task-4.md) — P3: containerize + deploy

## Deploy

### Prerequisites

Before deploying, ensure you have:

1. **Telegram Bot Token** from @BotFather
2. **LLM API credentials** (Qwen Code API or OpenRouter)
3. **LMS API Key** from `.env.docker.secret`

### Environment Variables

Create or update `.env.docker.secret` with bot credentials:

```bash
# Telegram Bot
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyz

# LLM API (Qwen Code)
LLM_API_MODEL=coder-model
LLM_API_KEY=your-qwen-api-key
LLM_API_BASE_URL=http://host.docker.internal:42005/v1

# LMS API (already set for backend)
LMS_API_KEY=your-lms-api-key
```

> **Note:** `LLM_API_BASE_URL` uses `host.docker.internal` to reach the Qwen proxy running on the host network.

### Deploy Commands

1. **Stop any running bot process** (from previous tasks):

   ```bash
   pkill -f "bot.py" 2>/dev/null || true
   ```

2. **Start all services** (backend + bot):

   ```bash
   cd ~/se-toolkit-lab-7
   docker compose --env-file .env.docker.secret up --build -d
   ```

3. **Verify services are running**:

   ```bash
   docker compose --env-file .env.docker.secret ps
   ```

   You should see:

   ```
   SERVICE    STATUS
   backend    Up
   bot        Up
   caddy      Up
   pgadmin    Up
   postgres   Up (healthy)
   ```

### Verify Deployment

1. **Check bot container logs**:

   ```bash
   docker compose --env-file .env.docker.secret logs bot --tail 20
   ```

   Look for:
   - "Application started" — bot connected successfully
   - No Python tracebacks

2. **Test in Telegram**:
   - Send `/start` — should receive welcome message
   - Send `/health` — should show backend status
   - Send "what labs are available?" — should list labs
   - Send "which lab has the lowest pass rate?" — should show comparison

3. **Verify backend is still healthy**:

   ```bash
   curl -sf http://localhost:42002/docs -H "Authorization: Bearer YOUR_LMS_API_KEY"
   ```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| Bot container keeps restarting | Check logs: `docker compose logs bot`. Usually missing env var or import error |
| `/health` fails but backend works | `LMS_API_BASE_URL` must be `http://backend:8000` (not `localhost`) |
| LLM queries fail | `LLM_API_BASE_URL` must use `host.docker.internal` for cross-network access |
| "BOT_TOKEN is required" | Add `BOT_TOKEN` to `.env.docker.secret` |
| Build fails at `uv sync` | Check `bot/pyproject.toml` exists and is copied in Dockerfile |

### Docker Networking

The bot uses Docker's internal DNS to reach services:

- **Backend**: `http://backend:8000` (same `lms-network`)
- **LLM Proxy**: `http://host.docker.internal:42005/v1` (host network)

Inside Docker, `localhost` refers to the container itself, not the host. Always use service names for inter-container communication.
