# Screenshots

Real captures from a local run of this repo. No placeholder or generated images of fake UI.

Do not commit admin panels, `.env` values, API keys, or private Slack workspaces. The demo key is referenced only as `$API_KEY`.

## Captured

| File | What it shows |
| --- | --- |
| [health-json.png](health-json.png) | `GET /health` — `ok`, `db: true`, `ai_provider: ollama`, `model: llama3.2`, `ollama: false` |
| [high-score-intake.png](high-score-intake.png) | Live `POST /api/v1/intake` HTTP 201 — `lead_score` 100, `urgency: critical`, `assigned_department: enterprise_sales` |
| [slack-log-or-message.png](slack-log-or-message.png) | uvicorn log: `slack skipped (SLACK_WEBHOOK_URL unset)` plus the logged payload stub |
| [docker-compose-up.png](docker-compose-up.png) | Live `docker compose up --build -d` on OrbStack — `api` + `postgres` healthy, `/health` returns `db: true` |
| [n8n-workflow-canvas.png](n8n-workflow-canvas.png) | Imported `n8n/workflow.json` canvas — Webhook → validate → FastAPI → score routing → Slack/queues |

Capture notes:

- Ollama may be down in some captures (`ollama: false` on `/health`). High-score shots then use the heuristic high-value path (`status=needs_review`) so routing and Slack logging still fire. With `llama3.2` up, the same endpoint returns `status=processed` and a model summary.
- Docker shot was taken on the Mac with OrbStack after `docker compose up --build -d`.
- n8n canvas was taken after importing `n8n/workflow.json` into a local n8n instance (see [`n8n/README.md`](../../n8n/README.md)). No production credentials are in the image.
