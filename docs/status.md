# Intake project status (Days 1–10)

Verified **local** portfolio demo. There is **no hosted live URL**. Clone and run from [github.com/Birra3324/ai-intake-demo](https://github.com/Birra3324/ai-intake-demo).

This is not a UiPath, Workato, MuleSoft, or ServiceNow project. The stack is FastAPI + n8n + Ollama/OpenAI + SQLite/Postgres + Slack.

## Verdict

Days 1–10 of the intake automation demo are **verified** as a recruiter-ready clone-and-run walkthrough: API, pytest, docker compose file, n8n import, and five live local screenshots.

## Stack

| Layer | What this repo uses |
| --- | --- |
| API | FastAPI (Python 3.12+) on port `8787` |
| Orchestration | Optional n8n (`n8n/workflow.json`) |
| LLM | Ollama `llama3.2` default; OpenAI via env |
| Data | SQLite default; Postgres via docker compose |
| Notify | Slack incoming webhook, or log-only when unset |
| Tests | pytest + TestClient, mocked LLM, temp SQLite |
| CI | GitHub Actions — `pytest` on push/PR to `main` |

## Demo path

Follow [docs/demo.md](demo.md) (about 5–10 minutes): venv → uvicorn on `:8787` → post the three [example leads](../examples/demo_requests.json) → `GET /health` and `GET /api/v1/leads`. n8n and Docker are optional extras on that same walkthrough.

## Screenshots (live local captures)

Capture notes: [screenshots/README.md](screenshots/README.md).

| File | What it shows |
| --- | --- |
| [health-json.png](screenshots/health-json.png) | `GET /health` — `ok`, `db: true` |
| [high-score-intake.png](screenshots/high-score-intake.png) | `POST /api/v1/intake` HTTP 201, `lead_score` 100 |
| [slack-log-or-message.png](screenshots/slack-log-or-message.png) | Slack skipped (`SLACK_WEBHOOK_URL` unset); payload logged |
| [docker-compose-up.png](screenshots/docker-compose-up.png) | `api` + `postgres` healthy |
| [n8n-workflow-canvas.png](screenshots/n8n-workflow-canvas.png) | Imported `n8n/workflow.json` canvas |

## Verification checklist

| Check | Status | Notes |
| --- | --- | --- |
| pytest (mocked LLM, temp SQLite) | Pass | **21 passed** on Python 3.12 (Day 9). Same command in CI. |
| GitHub Actions | Added | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) installs `requirements.txt` and runs pytest. No secrets required. |
| Docker Compose | Artifact verified | [`docker-compose.yml`](../docker-compose.yml) runs `api` + `postgres`. Live capture is `docker-compose-up.png` (Day 8). Not re-run in the Day 9 environment (no Docker daemon). |
| n8n import | Artifact verified | [`n8n/workflow.json`](../n8n/workflow.json) is valid JSON. Canvas capture is `n8n-workflow-canvas.png` (Day 8). Import steps: [n8n/README.md](../n8n/README.md). |
| Secrets | Clean | `.env` is gitignored. Demo key only in `.env.example` as `change-me-to-a-long-random-string`. No Slack tokens, OpenAI keys, or private workspace URLs in git. n8n uses `$env.INTAKE_API_KEY` / `$env.SLACK_WEBHOOK_URL`. |
| Hosted demo | None | Local-only. Docs do not claim a public URL. |

## Intentionally not built (Days 1–10)

Alembic migrations, CRM adapters, and a human-review UI are listed as future improvements in the README. They are not part of this verified demo.

Day 9 added CI and this checklist. No new product features.
