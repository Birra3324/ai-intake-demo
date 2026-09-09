# Recruiter demo (5–10 minutes)

Local walkthrough of this portfolio repo. No hosted demo URL. From the clone root, every command below is copy-pasteable.

You need Python 3.12+, `curl`, and `jq`. Ollama with `llama3.2` is optional: if the model is down, leads are still stored with `status=needs_review` and a heuristic score.

## 1. Setup (~1 min)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env.example` already sets `API_KEY=change-me-to-a-long-random-string`. Use that same value in the shell (do not commit a real `.env`).

```bash
export API_KEY=change-me-to-a-long-random-string
```

Optional: `ollama list` should show `llama3.2` if you want live LLM scoring.

## 2. Run the API (~30 s)

Terminal 1:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8787
```

Or: `./scripts/run_dev.sh`

Wait until uvicorn is listening on `127.0.0.1:8787`.

## 3. Post the three demo leads (~2–4 min)

Payloads are [examples/demo_requests.json](../examples/demo_requests.json): high (enterprise ops), mid (bakery form), low (vague cheap inquiry).

```bash
# high — index 0
curl -sS -X POST http://127.0.0.1:8787/api/v1/intake \
  -H "content-type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @<(jq '.[0]' examples/demo_requests.json)

# mid — index 1
curl -sS -X POST http://127.0.0.1:8787/api/v1/intake \
  -H "content-type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @<(jq '.[1]' examples/demo_requests.json)

# low — index 2
curl -sS -X POST http://127.0.0.1:8787/api/v1/intake \
  -H "content-type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @<(jq '.[2]' examples/demo_requests.json)
```

Without `jq`, post all three at once:

```bash
API_KEY="$API_KEY" python scripts/post_demo.py
```

Each call returns HTTP 201 with `id`, `status`, `lead_score`, `urgency`, `assigned_department`, `summary`, `recommended_action`, `request_id`. Example shapes: [examples/sample_responses.json](../examples/sample_responses.json). Live terminal captures: [docs/screenshots/README.md](screenshots/README.md).

Talking points:

- Score ≥ 80 → `enterprise_sales` (high-value Slack/log)
- 50–79 → `sales`
- < 50 → `nurture`
- If `SLACK_WEBHOOK_URL` is empty (the demo default), the API **logs** the Slack payload instead of posting it

## 4. Health + leads list (~1 min)

```bash
# public — no API key
curl -sS http://127.0.0.1:8787/health

# stored leads (newest first)
curl -sS http://127.0.0.1:8787/api/v1/leads \
  -H "X-API-Key: $API_KEY"
```

You should see `ok` / `db: true` on health, and three rows on `/api/v1/leads`.

## 5. Optional: n8n (~2 min)

n8n is not required for the API demo. To show orchestration:

1. Keep uvicorn running on port 8787.
2. Import [n8n/workflow.json](../n8n/workflow.json) (n8n → Workflows → Import from File).
3. Set n8n variable `INTAKE_API_KEY` to the same `API_KEY`, then activate.

Details: [n8n/README.md](../n8n/README.md).

## 6. Optional: Docker one-liner

```bash
docker compose up --build
```

Compose starts **api + postgres** on port 8787. Same `curl` commands work. Point n8n at `http://host.docker.internal:8787/api/v1/intake` if n8n is not on that Docker network.

## Tests (not part of the live demo)

```bash
.venv/bin/pytest -q
```

Tests mock the LLM and use a temp SQLite file. They do not call Ollama or OpenAI.
