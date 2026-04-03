---
name: project-orientation
description: >-
  Orients to the Plumbly codebase by reading canonical docs
  in a fixed order before exploring code. Use when starting work in this
  repository, summarizing the project, onboarding, architecture questions,
  "what does this repo do", or when the user wants a high-level map instead of
  full codebase parsing.
---

# Project orientation (Plumbly)

## Goal

Produce an accurate mental model using **bounded reading** only. Do not map the entire repository before consulting the sources below.

## Read order (strict)

1. Repository root [`README.md`](../../../README.md) — product intent, features, stack, setup.
2. [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) — layout, runtime flow, key modules, where to change behavior.
3. [`docker-compose.yml`](../../../docker-compose.yml) — local topology (app + Redis).
4. [`Dockerfile`](../../../Dockerfile) — how the Python API and SvelteKit build are combined for deploy.
5. **Only if still unclear:** read [`app/main.py`](../../../app/main.py) (app composition) and [`app/config.py`](../../../app/config.py) (settings / env vars). Stop after that unless the task requires more.

## Fallback search (cap at 5 queries)

If the docs disagree with the code, **trust the code** and note the doc drift.

Otherwise, use at most five targeted searches (e.g. ripgrep) for entry points: `FastAPI`, `APIRouter`, `uvicorn`, `include_router`, route path strings. Do not enumerate all files.

## Output template

After reading, reply with:

```markdown
## One-line purpose
[Single sentence: who it helps and what it does]

## Core loop
[Bullets: business user → dashboard → job/link → customer chat → Redis/Gemini → outcomes]

## Main pieces
- **Backend:** [FastAPI modules / responsibilities]
- **Customer UI:** [static chat vs paths]
- **Operator UI:** [SvelteKit vs fallback static]
- **Data / infra:** [Redis roles; auth provider if relevant]

## Key paths
- Entry: `app/main.py`
- Agent / LLM: `app/agent.py`
- Sessions & Redis: `app/redis_client.py`
- Customer routes: `app/routes_chat.py`
- Business dashboard API + SPA shell: `app/routes_plumber.py`
- Auth: `app/routes_auth.py`, `app/auth.py`
- SMS: `app/routes_sms.py`, `app/sms.py`
- Frontend source: `dashboard-app/`
- Static customer chat: `static/chat.html`, `static/chat.js`

## Run / deploy (from README)
[Copy or paraphrase the 2–4 essential commands or deploy facts the task needs]

## Doc debt
[Note anything wrong or missing in README / ARCHITECTURE, or "None"]
```

## Optional deep dives

Use only when the task requires implementation detail:

- Redis data model & events: [`app/redis_client.py`](../../../app/redis_client.py)
- WorkOS / session rules: [`app/auth.py`](../../../app/auth.py)
