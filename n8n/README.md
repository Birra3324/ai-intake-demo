# n8n intake workflow

This folder contains the orchestration layer in front of the FastAPI service.

| File | Status |
| --- | --- |
| `workflow.json` | Current: validate → FastAPI → score routing → score-based Slack routing, with retries and an error branch |
| `intake-to-agent.json` | Legacy phase-1 linear webhook (kept for reference) |

## What the current workflow does

1. **Webhook** receives `POST /webhook/intake` (n8n path `intake`).
2. **Validate Payload** (Code node) requires name, email, and a description. Throws on bad input.
3. **FastAPI Intake** `POST http://host.docker.internal:8787/api/v1/intake` with `X-API-Key`, 60s timeout, **3 retries** / 2s wait, **error output** on failure.
4. **Score >= 80** → **Slack High Priority**.
5. **Score 50-79** → **Sales Queue** Slack message.
6. **Score < 50** → **Nurture Track**.
7. **Respond OK** returns the FastAPI JSON to the original caller.
8. **Respond Error** returns HTTP 502 if FastAPI exhausts retries.

If Slack is not configured, disable the Slack nodes and connect the score branches to Respond OK after import. Do not use dummy URLs. Choose n8n as the notification owner and leave the API Slack/SMTP settings unset to avoid duplicate notifications.

## Import

1. Run the API locally (`uvicorn app.main:app --port 8787`) so n8n has something to call.
2. Open n8n → **Workflows** → **Import from File** → choose `n8n/workflow.json`.
3. Set environment variables in n8n (Settings → Variables, or `.env` for self-hosted):
   - `INTAKE_API_KEY` — same value as the API `API_KEY`
   - `SLACK_WEBHOOK_URL` — real incoming webhook; otherwise disable the Slack nodes
4. Confirm the FastAPI URL:
   - n8n on the same Mac as uvicorn: `http://127.0.0.1:8787/api/v1/intake`
   - n8n in Docker, API on the host: `http://host.docker.internal:8787/api/v1/intake`
   - both in Docker Compose on the same network: `http://api:8787/api/v1/intake`
5. Activate the workflow. Copy the production webhook URL from the Webhook node.

## Test from curl

```bash
python -c 'import json; print(json.dumps(json.load(open("examples/demo_requests.json"))[0]))' > /tmp/intake-demo-request.json
curl -sS -X POST "$N8N_WEBHOOK_URL" \
  -H 'content-type: application/json' \
  -H "Idempotency-Key: demo-event-001" \
  -d @/tmp/intake-demo-request.json
```

`demo_requests.json` is an array of three leads — post them one object at a time (see the project README).

## Error branch

The HTTP Request node uses `retryOnFail` (3 tries) and `onError: continueErrorOutput`. Failures skip routing and hit **Respond Error**. Check Executions in n8n for the error payload.

The caller should supply a stable event-specific Idempotency-Key. Without one, the workflow uses its execution ID, which protects retries within one execution but not repeated webhook deliveries.
