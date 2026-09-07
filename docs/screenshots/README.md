# Screenshots

Real terminal captures from a local `uvicorn` run of this repo (`127.0.0.1:8787`). No placeholder or generated images.

Do not commit admin panels, `.env` values, API keys, or private Slack workspaces. The demo key is referenced only as `$API_KEY`.

## Captured

| File | What it shows |
| --- | --- |
| [health-json.png](health-json.png) | `GET /health` — `ok`, `db: true`, `ai_provider: ollama`, `model: llama3.2`, `ollama: false` |
| [high-score-intake.png](high-score-intake.png) | Live `POST /api/v1/intake` HTTP 201 — `lead_score` 100, `urgency: critical`, `assigned_department: enterprise_sales` |
| [slack-log-or-message.png](slack-log-or-message.png) | uvicorn log: `slack skipped (SLACK_WEBHOOK_URL unset)` plus the logged payload stub |

Capture notes (this environment):

- Ollama was not running (`ollama: false` on `/health`). The high-score 201 is the **heuristic high-value path**: `status=needs_review`, `summary=null`, score still ≥ 80 so routing and Slack logging fire. With `llama3.2` up, the same endpoint returns `status=processed` and a model summary.
- `examples/demo_requests.json[0]` (Amina / Northwind) scores **70** on the heuristic when the LLM is down, so the high-score shot used a live POST of a complete high-value payload (same `IntakeCreate` fields) to exercise score ≥ 80.

## Still blocked in this VM

| Shot | Why |
| --- | --- |
| n8n workflow canvas | n8n is not installed or runnable here. The workflow JSON is in [`n8n/workflow.json`](../../n8n/workflow.json); import it locally (see [`n8n/README.md`](../../n8n/README.md)) and drop `n8n-workflow-canvas.png` here. |
| `docker compose up` | `docker` is not installed in this environment (`command -v docker` is empty). Run `docker compose up --build` locally and add `docker-compose-up.png` (api + postgres healthy). |

Suggested filenames when those two exist: `n8n-workflow-canvas.png`, `docker-compose-up.png`.
