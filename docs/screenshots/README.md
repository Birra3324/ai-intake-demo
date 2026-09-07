# Screenshots still needed

This folder is a capture checklist. **No screenshot image files are in the repo yet** (no png/gif/jpg placeholders). Capture these locally, then drop real files here and link them from the root README.

Do not commit admin panels, `.env` values, API keys, or private Slack workspaces. Redact `X-API-Key` and webhook URLs if they appear.

## Capture list

1. **Health JSON** — `GET http://127.0.0.1:8787/health` in a terminal or browser, showing `ok`, `db`, `ai_provider`, and `model`.
2. **High-score intake response** — HTTP 201 body from posting `examples/demo_requests.json` index 0 (`Amina Hassan` / Northwind). Show `lead_score`, `urgency`, and `assigned_department`.
3. **Slack log or Slack line** — uvicorn log line `slack skipped (SLACK_WEBHOOK_URL unset)` (default demo), **or** a redacted Slack message if you configured an incoming webhook.
4. **n8n workflow canvas** — after importing `n8n/workflow.json`: validate → FastAPI → score routing → Slack/queues.
5. **`docker compose up`** — compose output with `api` and `postgres` healthy (or the equivalent `docker compose ps`).

## After you capture them

Suggested filenames (when real images exist):

- `health-json.png`
- `high-score-intake.png`
- `slack-log-or-message.png`
- `n8n-workflow-canvas.png`
- `docker-compose-up.png`

Until those files exist, this README is the only content in this directory on purpose.
