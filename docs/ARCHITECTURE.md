# Architecture (Plumbly)

Single FastAPI service serves **customer review chat**, **plumber/business dashboard** (SvelteKit static build), **auth**, and **SMS webhooks**. Conversation state, analytics, and real-time dashboard signals live in **Redis**. The conversational agent uses **Google Gemini** (see `app/agent.py`).

## Runtime diagram

```text
Customer  →  GET /review/{session_id}  →  static chat UI  →  /api/chat (+ stream)  →  Gemini
                 ↑                              ↓
Plumber   →  SvelteKit SPA (/_app, /dashboard, …)  →  /api/* (jobs, sessions, analytics)  →  Redis
                 ↑
Auth      →  /auth/*  (WorkOS AuthKit, cookies, org context)

SMS       →  Twilio webhooks  →  `app/routes_sms.py`  →  Redis / sessions
```

Redis holds session documents, funnel/pipeline fields, FAQ vector seeds, rate limits, pub/sub for SSE, and plumber-facing notifications.

## Repository layout

| Path | Role |
|------|------|
| `app/main.py` | FastAPI app, lifespan (Redis ping, FAQ seed), mounts `/_app` + `/static`, includes routers |
| `app/config.py` | Pydantic settings / environment variables |
| `app/agent.py` | Gemini chat, streaming, prompts |
| `app/redis_client.py` | Redis keys, sessions, analytics helpers, pub/sub, vectors |
| `app/routes_chat.py` | Customer pages: `/review/{session_id}`, chat APIs, greeting, streaming |
| `app/routes_plumber.py` | Dashboard shell, legal pages, jobs, sessions, analytics, SSE `/api/notifications`, SPA fallback route |
| `app/routes_auth.py` | WorkOS login/callback, `/api/me`, org switching |
| `app/auth.py` | Session cookies, roles, org resolution |
| `app/routes_sms.py` | Twilio inbound/outbound hooks, STOP/START handling |
| `app/sms.py` | Sending review links (e.g. Twilio) |
| `static/` | `chat.html` / `chat.js` (customer), legacy `dashboard.html`, shared `style.css` |
| `dashboard-app/` | SvelteKit (adapter-static) operator UI; build output copied into `dashboard-app/build/` in Docker |
| `tests/` | Pytest |
| `docker-compose.yml` | `app` + `redis` (redis-stack) |

## Deploy / build

- **Dockerfile:** stage 1 builds `dashboard-app` with Bun; stage 2 runs Python `uvicorn app.main:app` on port 8080 and copies the SvelteKit `build/` tree beside the API.
- **Railway:** `railway.json` points at the root Dockerfile.

## Where to change behavior

| Concern | Primary files |
|---------|----------------|
| Review conversation logic | `app/agent.py`, prompts/tooling inside it |
| Session schema / expiry / keys | `app/redis_client.py`, `app/models.py` |
| Customer HTTP API | `app/routes_chat.py` |
| Dashboard REST + SSE | `app/routes_plumber.py` |
| Login / org / RBAC | `app/auth.py`, `app/routes_auth.py` |
| SMS compliance + webhooks | `app/routes_sms.py`, `app/sms.py` |
| Operator UI | `dashboard-app/src/**` (then rebuild / Docker) |
| Customer UI shell | `static/chat.html`, `static/chat.js` |

## Conventions

- Routers are included from `app/main.py` without URL prefixes; individual paths are defined on each router module.
- If `dashboard-app/build/` is missing locally, `app/routes_plumber.py` falls back to `static/dashboard.html` for `/`.
