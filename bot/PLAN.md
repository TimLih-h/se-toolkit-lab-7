# Bot Development Plan

## Overview

This document outlines the implementation plan for the Telegram bot that interfaces with the Learning Management System (LMS) backend. The bot provides students with access to their lab progress, scores, and health checks through natural language commands.

## Architecture

The bot follows a **layered architecture** with clear separation of concerns:

1. **Transport Layer** (`bot.py`): Handles Telegram Bot API communication. Also provides a `--test` CLI mode for offline testing without Telegram connection.

2. **Handler Layer** (`handlers/`): Contains command handlers that process user input and return text responses. These are pure functions with no Telegram dependency, making them testable in isolation.

3. **Service Layer** (`services/`): External API clients (LMS backend, LLM API). Handles HTTP requests, authentication, and error handling.

4. **Configuration** (`config.py`): Loads environment variables from `.env.bot.secret` for secrets management.

## Task Breakdown

### Task 1: Scaffold (Current)

Create the project skeleton with:
- Entry point with `--test` mode
- Placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Configuration loading from environment
- Dependencies via `pyproject.toml`

**Key decision:** Handlers are separated from Telegram from the start. This is called *separation of concerns* — the same handler function works from `--test` mode, unit tests, or Telegram.

### Task 2: Backend Integration

Implement real API calls to the LMS backend:
- `/health` → `GET /health` endpoint
- `/labs` → `GET /items/` to list available labs
- `/scores <lab>` → `GET /items/{id}/submissions` for student submissions

**Key decision:** API client uses Bearer token authentication with `LMS_API_KEY` from environment. Base URL from `LMS_API_BASE_URL` allows different environments (local, VM, production).

### Task 3: Intent Routing with LLM

Add natural language understanding:
- Use LLM to classify user intent and route to appropriate handler
- Tool descriptions tell the LLM what each handler does
- Fallback to help message when intent is unclear

**Key decision:** The LLM decides which tool to call based on descriptions — not regex or keyword matching. This is the core of tool use: the model reads descriptions and picks the right tool.

### Task 4: Deployment

Deploy the bot on the VM:
- Run as a background service
- Auto-restart on failure
- Logging for debugging

**Key decision:** Simple `nohup` deployment for now. Can upgrade to systemd or Docker later.

## Testing Strategy

1. **Test mode** (`--test`): Quick verification during development
2. **Unit tests**: Test handlers in isolation (future)
3. **Manual Telegram testing**: Verify real user experience

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token from @BotFather | `123456:ABCdef...` |
| `LMS_API_BASE_URL` | Backend API base URL | `http://localhost:42002` |
| `LMS_API_KEY` | API key for Bearer auth | `my-secret-key` |
| `LLM_API_KEY` | Qwen Code API key | `my-qwen-key` |
| `LLM_API_BASE_URL` | LLM API endpoint | `http://localhost:42005/v1` |
| `LLM_API_MODEL` | Model name for completions | `coder-model` |

## Success Criteria

- All commands work in `--test` mode
- Bot responds in Telegram
- No secrets committed to git
- Clean separation between layers
