# AI Intake Automation Platform

[![CI](https://github.com/Birra3324/ai-intake-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/Birra3324/ai-intake-demo/actions/workflows/ci.yml)

> Open to remote AI automation roles. Email: birragimedi@gmail.com | GitHub: @Birra3324 | LinkedIn: linkedin.com/in/birra-gemedi

FastAPI service that turns a contact-form webhook into a structured, scored lead: n8n (optional) → API → local or cloud LLM → SQLite/Postgres → routing → Slack.

Built as a local portfolio demo you can run with Ollama (`llama3.2`) and pytest. No paid APIs required. Source: [github.com/Birra3324/ai-intake-demo](https://github.com/Birra3324/ai-intake-demo) (no hosted demo URL).

**How to demo:** [5–10 minute walkthrough](docs/demo.md) — venv, uvicorn on `:8787`, post the three [example leads](examples/demo_requests.json), then `GET /health` and `GET /api/v1/leads`.

**Status (Days 1–10):** [verified local checklist](docs/status.md) — stack, screenshots, pytest, docker compose, n8n import.

## Screenshots

Live local captures (notes: [docs/screenshots/README.md](docs/screenshots/README.md)).

**Health JSON** (`GET /health`)

![GET /health JSON](docs/screenshots/health-json.png)

**High-score intake** (`POST /api/v1/intake` → HTTP 201, `lead_score` 100)

![High-score intake 201](docs/screenshots/high-score-intake.png)

**Slack path** (`SLACK_WEBHOOK_URL` unset — payload logged, not posted)

![Slack skipped log line](docs/screenshots/slack-log-or-message.png)

**Docker Compose** (`api` + `postgres` healthy)

![docker compose up](docs/screenshots/docker-compose-up.png)

**n8n workflow canvas** (import `n8n/workflow.json`)

![n8n AI Intake Routing](docs/screenshots/n8n-workflow-canvas.png)

## Architecture

```mermaid
flowchart LR
  User[Form / curl] --> WH[Webhook]
  WH --> N8N[n8n validate + retry]
  N8N --> API[FastAPI]
  User -.-> API
  API --> LLM[Ollama llama3.2 / OpenAI]
  API --> DB[(SQLite or Postgres)]
  LLM --> Score[Lead score 0-100]
  Score -->|">= 80"| High[High-priority + Slack]
  Score -->|"50-79"| Sales[Sales queue]
  Score -->|"< 50"| Nurture[Nurture]
```

Direct `POST /api/v1/intake` works without n8n. `POST /webhook/intake` is kept as a compatibility alias for the original `{name, email, message}` payload.

## Stack

- Python 3.12+ (developed against Homebrew 3.14.6; Pydantic 2.13.5 / SQLAlchemy 2.0.52 because older pins had no 3.14 wheels)
- FastAPI, Pydantic v2, SQLAlchemy 2
- Ollama (`llama3.2`) default; OpenAI optional via env
- SQLite default; PostgreSQL via `postgresql+psycopg://`
- n8n workflow with retries and score routing
- Slack incoming webhook (logs the payload when unset)
- pytest + TestClient with mocked LLM HTTP

## Setup

```bash
git clone https://github.com/Birra3324/ai-intake-demo.git
cd ai-intake-demo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# set API_KEY to any long random string
```

Ollama should already be installed. Confirm the model:

```bash
ollama list   # llama3.2
```

Run the API:

```bash
# terminal 1
uvicorn app.main:app --reload --port 8787

# terminal 2
export API_KEY=change-me-to-a-long-random-string   # same as .env
curl -sS -X POST http://127.0.0.1:8787/api/v1/intake \
  -H "content-type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @<(jq '.[0]' examples/demo_requests.json)
```

Health (no key): `GET http://127.0.0.1:8787/health`

Legacy curl still works:

```bash
curl -sS -X POST http://127.0.0.1:8787/webhook/intake \
  -H "content-type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"name":"Amina","email":"amina@example.com","message":"Need a weekly ops report automated."}'
```

Or: `./scripts/run_dev.sh` then `API_KEY=... python scripts/post_demo.py`

## Environment variables

See `.env.example`. Important ones:

| Variable | Purpose |
| --- | --- |
| `API_KEY` | Required for POST/PATCH and GET `/api/v1/leads`. `GET /health` is public. |
| `DATABASE_URL` | `sqlite:///./data/intake.db` (default) or `postgresql+psycopg://user:pass@host:5432/intake` |
| `AI_PROVIDER` | `ollama` (default) or `openai` |
| `OLLAMA_URL` / `OLLAMA_MODEL` | Default `http://127.0.0.1:11434` / `llama3.2` |
| `OPENAI_API_KEY` | Only if `AI_PROVIDER=openai`. Never hard-coded. |
| `SLACK_WEBHOOK_URL` | Incoming webhook. If empty, notifications are logged. |
| `SMTP_*` | Optional email. Skipped when host/from/to are empty. |

## API

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/health` | public |
| POST | `/api/v1/intake` | `X-API-Key` |
| POST | `/webhook/intake` | `X-API-Key` (legacy body) |
| GET | `/api/v1/leads` | `X-API-Key` |
| GET | `/api/v1/leads/{id}` | `X-API-Key` |
| PATCH | `/api/v1/leads/{id}` | `X-API-Key` |

Full shapes: [docs/api.md](docs/api.md). Architecture notes: [docs/architecture.md](docs/architecture.md). Recruiter walkthrough: [docs/demo.md](docs/demo.md). Status: [docs/status.md](docs/status.md).

When the LLM is down or returns invalid JSON the lead is **still stored** with `status=needs_review` and a heuristic score. Rows are not dropped.

## n8n

Import [n8n/workflow.json](n8n/workflow.json). Details: [n8n/README.md](n8n/README.md).

Routing after FastAPI returns:

- score ≥ 80 → high-priority Slack
- 50–79 → sales queue
- < 50 → nurture

The HTTP node retries three times (2s apart), 60s timeout, error branch → HTTP 502 to the caller.

The phase-1 linear workflow is kept as [n8n/intake-to-agent.json](n8n/intake-to-agent.json).

## Docker

```bash
docker compose up --build
```

Compose runs **api + postgres**. Point n8n (host or another compose file) at `http://host.docker.internal:8787/api/v1/intake` if n8n is not on the same Docker network, or at `http://api:8787` if it is.

The image uses `python:3.12-slim` for a stable base even though local Python is 3.14.

This demo uses SQLAlchemy `create_all()` on boot rather than Alembic — see [docs/architecture.md](docs/architecture.md).

## Testing

```bash
cd ai-intake-demo
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -q
```

Tests use a temp SQLite file and mock the LLM. They do not call Ollama or OpenAI. The same command runs on GitHub Actions (push/PR to `main`).

## Demo data

Three realistic payloads live in [examples/demo_requests.json](examples/demo_requests.json): an urgent enterprise ops automation, a mid-size bakery form, and a vague cheap inquiry. Example HTTP 201 bodies (not live captures) are in [examples/sample_responses.json](examples/sample_responses.json).

## Future improvements

- Alembic migrations once the schema is treated as production
- Idempotency keys so duplicate webhooks do not double-insert
- Outbox table for Slack/email instead of best-effort side effects
- Human review UI for `needs_review` rows
- Optional CRM adapter (HubSpot/Salesforce) behind the same lead schema

## License

MIT © 2026 Birra Gemedi

## Reliability and deployment boundaries

The API now requires a nonempty `API_KEY` at startup and fails closed if configuration is missing. Health remains public. Use a strong private value; do not use example values on a hosted service.

Send an `Idempotency-Key` header (1–200 ASCII letters, digits, dot, underscore, colon or hyphen) for replay-safe intake. The same key and normalized payload returns the same lead; a changed payload returns HTTP 409. A separate database ledger enforces uniqueness, including concurrent inserts, without changing existing lead columns. The key is global to this single-service-key demo: namespace it by source. Keep ledger entries as long as replay protection is needed. Requests without a key retain create-on-each-request behavior. Concurrent first requests can still invoke the model twice; only one lead and notification attempt are committed.

The n8n workflow forwards a caller's `Idempotency-Key`; otherwise it uses the execution ID for retries within that execution. New webhook deliveries without a stable caller key are separate events. Do not derive a permanent key from a person's email.

Notifications remain best effort after commit. A process crash or failed Slack/SMTP request can lose delivery; this is not a durable outbox. Choose one notification owner: for n8n routing, leave the API notification settings unset. The n8n destinations labeled Sales Queue and Nurture Track are Slack messages, not CRM queues.

Operational logs omit customer payloads and provider exception bodies. Provider retries cover transport errors and selected transient HTTP statuses; permanent HTTP errors return to the review fallback without retry. Before public hosting, still add request/rate limits, a deployment-specific secret store, durable delivery if needed, and monitoring. This repository does not claim production readiness.
