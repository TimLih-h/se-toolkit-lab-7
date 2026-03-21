# Task 3: Intent-Based Natural Language Routing - Implementation Plan

## Overview

This task adds LLM-powered intent routing to the Telegram bot. Instead of requiring users to type `/commands`, they can ask natural questions like "which lab has the lowest pass rate?" and the bot figures out what data to fetch.

## Architecture

### Tool Calling Pattern

The bot implements the same tool use pattern from Lab 6:

1. **User sends message** → Bot receives text
2. **Bot sends to LLM** → Message + tool definitions (9 backend endpoints)
3. **LLM returns tool calls** → JSON with function names and arguments
4. **Bot executes tools** → Calls LMS API endpoints
5. **Bot feeds results back** → Tool results added to conversation
6. **LLM summarizes** → Final answer based on actual data

### Tool Definitions (9 endpoints)

| Tool | Endpoint | Purpose |
|------|----------|---------|
| `get_items` | GET /items/ | List all labs and tasks |
| `get_learners` | GET /learners/ | Enrolled students and groups |
| `get_scores` | GET /analytics/scores?lab= | Score distribution (4 buckets) |
| `get_pass_rates` | GET /analytics/pass-rates?lab= | Per-task averages |
| `get_timeline` | GET /analytics/timeline?lab= | Submissions per day |
| `get_groups` | GET /analytics/groups?lab= | Per-group performance |
| `get_top_learners` | GET /analytics/top-learners?lab=&limit= | Top N learners |
| `get_completion_rate` | GET /analytics/completion-rate?lab= | Completion percentage |
| `trigger_sync` | POST /pipeline/sync | Refresh data from autochecker |

### System Prompt

The LLM receives a system prompt that:
- Explains its role as an LMS assistant
- Encourages tool use for data-driven answers
- Handles greetings, gibberish, and ambiguous queries gracefully

### Multi-Step Reasoning

The router supports a conversation loop:
- LLM calls tool(s) → Bot executes → Results fed back → LLM continues
- Maximum 5 iterations to prevent infinite loops
- Debug logging to stderr shows tool calls and results

## Files Structure

```
bot/
├── bot.py                  # Entry point with --test mode, inline buttons
├── config.py               # Environment loading
├── handlers/
│   ├── __init__.py
│   ├── command.py          # Slash command handlers
│   └── intent_router.py    # LLM-based intent routing
└── services/
    ├── __init__.py
    ├── lms_client.py       # LMS API client (9 endpoints)
    └── llm_client.py       # LLM client with tool calling
```

## Inline Keyboard Buttons

Common queries accessible via buttons:
- 📚 What labs? → Lists available labs
- 💯 Lab 4 scores → Shows pass rates for lab-04
- 📊 Lowest pass rate → Multi-step query comparing all labs
- 🏆 Top students → Shows top 5 learners

## Testing Strategy

### Single-Step Queries
- "what labs are available?" → `get_items` → List labs
- "show me scores for lab 4" → `get_pass_rates(lab="lab-04")` → Format

### Multi-Step Queries
- "which lab has the lowest pass rate?" → `get_items` → `get_pass_rates` for each → Compare
- "which group is doing best in lab 3?" → `get_groups(lab="lab-03")` → Rank

### Fallback Cases
- "hello" → Greeting + capabilities hint
- "asdfgh" → "I didn't understand. Here's what I can do..."
- "lab 4" → "What about lab 4? I can show..."

### Debug Output

Test mode prints to stderr:
```
[tool] LLM called: get_items({})
[tool] Result: 44 items
[tool] LLM called: get_pass_rates({"lab":"lab-01"})
[tool] Result: 8 tasks
[summary] Feeding 7 tool result(s) back to LLM
```

## Dependencies

- `httpx` - HTTP client for API calls
- `pydantic-settings` - Configuration loading
- `aiogram` - Telegram bot framework (prepared for Task 4)

## LLM Configuration

Uses Qwen Code API (same as Lab 6):
- Base URL: `http://localhost:42005/v1`
- Model: `coder-model`
- API Key: from `.env.bot.secret`

## Error Handling

- LLM unreachable → "LLM error: ... The AI service may be temporarily unavailable."
- Tool execution fails → Error returned in tool result, LLM can retry or explain
- Max iterations reached → Partial answer with available information

## Success Criteria

1. `--test "what labs are available"` → Non-empty answer (≥20 chars)
2. `--test "which lab has the lowest pass rate"` → Mentions specific lab
3. `--test "asdfgh"` → Helpful message, no crash
4. Debug output shows tool calls and results
5. 9 tool definitions in source code
6. Tool results fed back to LLM for final answer
