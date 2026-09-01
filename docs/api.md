# HTTP API

Base URL locally: `http://127.0.0.1:8787`

Auth: header `X-API-Key: <API_KEY>` on all routes except `GET /health`.

Every response includes `x-request-id`. Error bodies look like:

```json
{ "error": "Invalid or missing API key", "request_id": "..." }
```

Validation errors are HTTP 422 with `details` from Pydantic.

## `GET /health`

Public. Checks the database with `SELECT 1`. Reports `ollama` reachability when `AI_PROVIDER=ollama` but does not fail the whole check if the model is down.

## `POST /api/v1/intake`

Creates a lead. HTTP 201.

```json
{
  "customer_name": "Amina Hassan",
  "company": "Northwind Logistics",
  "email": "amina@northwind.example",
  "phone": "+1-206-555-0142",
  "service_requested": "Ops reporting automation",
  "budget": "$80k",
  "project_description": "Weekly warehouse report into Slack...",
  "deadline": "2026-09-30",
  "source": "website"
}
```

Required: `customer_name`, `email`, `project_description` (3–8000 chars).

Response:

```json
{
  "id": "uuid",
  "status": "processed",
  "lead_score": 86,
  "urgency": "high",
  "assigned_department": "enterprise_sales",
  "summary": "...",
  "recommended_action": "...",
  "request_id": "..."
}
```

If the LLM is down or returns invalid JSON, the row is still stored with `status: needs_review` and a heuristic `lead_score`.

## `POST /webhook/intake`

Compatibility alias for the phase-1 payload:

```json
{ "name": "Amina", "email": "amina@example.com", "message": "...", "source": "webhook" }
```

Mapped to `customer_name` / `project_description`. Same auth and 201 response as `/api/v1/intake`.

## `GET /api/v1/leads`

Query: `status`, `limit` (1–200, default 50), `offset`.

## `GET /api/v1/leads/{id}`

HTTP 404 if missing.

## `PATCH /api/v1/leads/{id}`

Updatable: `status`, `assigned_department`, `follow_up_message`.
